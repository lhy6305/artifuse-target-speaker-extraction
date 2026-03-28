from __future__ import annotations

import argparse
import json
import math
import pickle
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import torch
import torchaudio
from torch.utils.data import DataLoader


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.data import SyntheticTSEDataset, synthetic_collate_fn
from tse_prefix.models import STFTMaskBaseline
from tse_prefix.pipeline import (
    absent_interval_l1_loss,
    compute_losses,
    interference_projection_loss,
    masked_sisdr,
    transient_presence_l1_loss,
    weighted_stft_l1_loss,
    weighted_waveform_l1_loss,
)
from tse_prefix.pipeline.baseline_train import (
    base_delta_interference_projection_loss,
    interval_projection_ratio_loss,
    interval_waveform_l1_loss,
    overlap_interval_interference_projection_loss,
    weighted_gate_target_loss,
    weighted_sisdr_loss,
)
from tse_prefix.pipeline.loss_selectors import (
    build_selector_sample_weights,
    summarize_selector_weights,
)
from tse_prefix.pipeline.runtime_helpers import (
    build_compute_loss_kwargs,
    build_gate_target_values,
    resolve_branch_extra_prediction,
    resolve_primary_prediction,
    resolve_selector_sample_weights,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate the minimal TSE baseline.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "val_manifest.jsonl",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=ROOT / "experiments" / "checkpoints" / "baseline_stft_mask_smoke" / "best.pt",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "reports" / "eval" / "baseline_stft_mask_smoke_eval",
    )
    parser.add_argument(
        "--teacher-checkpoint",
        type=Path,
        default=None,
        help=(
            "Optional frozen teacher checkpoint used for hard-present overlap teacher veto losses. "
            "When omitted, eval falls back to the teacher_checkpoint stored inside --checkpoint metadata."
        ),
    )
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--num-workers", type=int, default=0)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--save-audio-count", type=int, default=4)
    return parser.parse_args()


def move_batch_to_device(batch: dict, device: torch.device) -> dict:
    moved = dict(batch)
    for key in [
        "mixture",
        "mixture_lengths",
        "target",
        "target_lengths",
        "reference",
        "reference_lengths",
        "target_present_ratios",
        "target_energy_ratios",
        "target_transient_presence_minus_mid_db_means",
        "target_transient_presence_share_means",
        "interference_transient_presence_minus_mid_db_means",
        "interference_transient_presence_share_means",
        "target_interference_logspec_cosines",
        "overlap_ratios",
        "interference_gain_dbs",
    ]:
        moved[key] = batch[key].to(device)
    return moved


def align_waveforms(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    common_length = min(prediction.shape[-1], target.shape[-1])
    clipped_lengths = torch.clamp(lengths, max=common_length)
    return (
        prediction[..., :common_length],
        target[..., :common_length],
        clipped_lengths,
    )


def save_audio(path: Path, waveform: torch.Tensor, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clipped = waveform.detach().cpu().unsqueeze(0)
    torchaudio.save(str(path), clipped, sample_rate)


def target_present_ratio_bucket(ratio: float) -> str:
    if ratio < 0.6:
        return "ratio_lt_0.6"
    if ratio < 0.8:
        return "ratio_0.6_0.8"
    if ratio < 0.95:
        return "ratio_0.8_0.95"
    return "ratio_ge_0.95"


def load_checkpoint(path: Path, device: torch.device) -> dict:
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except pickle.UnpicklingError:
        return torch.load(path, map_location=device, weights_only=False)


def resolve_model_config(checkpoint: dict) -> dict:
    model_config = dict(checkpoint.get("model_config", {}))
    if "conditioning_mode" not in model_config:
        state_dict = checkpoint["model_state_dict"]
        if "condition_proj.weight" in state_dict:
            model_config["conditioning_mode"] = "legacy_bias"
    return model_config


def build_model_from_checkpoint(checkpoint: dict, device: torch.device) -> tuple[STFTMaskBaseline, dict]:
    model_config = resolve_model_config(checkpoint)
    model = STFTMaskBaseline(**model_config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    return model, model_config


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def resolve_teacher_checkpoint_path(
    explicit_path: Path | None,
    checkpoint: dict,
    checkpoint_path: Path,
) -> Path | None:
    if explicit_path is not None:
        return explicit_path.resolve()

    metadata_path = checkpoint.get("teacher_checkpoint")
    if not metadata_path:
        return None

    candidate = Path(str(metadata_path))
    if candidate.is_absolute():
        return candidate.resolve()

    for base_dir in (ROOT, checkpoint_path.parent):
        resolved = (base_dir / candidate).resolve()
        if resolved.exists():
            return resolved
    return (ROOT / candidate).resolve()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    sample_output_dir = args.output_dir / "samples"
    sample_output_dir.mkdir(parents=True, exist_ok=True)

    start_ts = time.time()
    start_dt = datetime.now()
    print(f"eval_start={start_dt.isoformat(timespec='seconds')}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"device={device.type}")

    dataset = SyntheticTSEDataset(args.manifest, sample_rate=args.sample_rate)
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        collate_fn=synthetic_collate_fn,
    )

    checkpoint = load_checkpoint(args.checkpoint, device)
    model, model_config = build_model_from_checkpoint(checkpoint, device)
    model.eval()
    teacher_checkpoint_path = resolve_teacher_checkpoint_path(
        explicit_path=args.teacher_checkpoint,
        checkpoint=checkpoint,
        checkpoint_path=args.checkpoint,
    )
    teacher_model: STFTMaskBaseline | None = None
    if teacher_checkpoint_path is not None:
        teacher_checkpoint = load_checkpoint(teacher_checkpoint_path, device)
        teacher_model, _ = build_model_from_checkpoint(teacher_checkpoint, device)
        teacher_model.eval()
        for parameter in teacher_model.parameters():
            parameter.requires_grad_(False)

    totals = {
        "loss": 0.0,
        "waveform_l1": 0.0,
        "stft_l1": 0.0,
        "reconstruction_waveform_l1": 0.0,
        "reconstruction_stft_l1": 0.0,
        "reconstruction_extra_waveform_l1": 0.0,
        "reconstruction_extra_stft_l1": 0.0,
        "sisdr_loss": 0.0,
        "sisdr_db": 0.0,
        "branch_protect_guard_sisdr_loss": 0.0,
        "branch_protect_overlap_base_align_l1": 0.0,
        "branch_protect_teacher_overlap_l1": 0.0,
        "interference_extra_guard_sisdr_loss": 0.0,
        "interference_extra_base_align_l1": 0.0,
        "interference_extra_base_delta_projection_ratio": 0.0,
        "transient_presence_l1": 0.0,
        "transient_extra_presence_l1": 0.0,
        "interference_projection_ratio": 0.0,
        "interference_extra_projection_ratio": 0.0,
        "overlap_interference_projection_ratio": 0.0,
        "overlap_interference_extra_projection_ratio": 0.0,
        "overlap_cancel_waveform_l1": 0.0,
        "overlap_cancel_target_projection_ratio": 0.0,
        "overlap_dual_mix_consistency_l1": 0.0,
        "overlap_dual_residual_target_projection_ratio": 0.0,
        "absent_interval_l1": 0.0,
        "absent_extra_interval_l1": 0.0,
        "gate_abstain_mean": 0.0,
        "gate_keep_mean": 0.0,
        "gate_target_l1": 0.0,
    }
    batch_count = 0
    sample_count = 0
    pattern_metrics: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "count": 0,
            "loss": 0.0,
            "sisdr_db": 0.0,
            "reconstruction_waveform_l1": 0.0,
            "reconstruction_stft_l1": 0.0,
            "reconstruction_extra_waveform_l1": 0.0,
            "reconstruction_extra_stft_l1": 0.0,
            "transient_presence_l1": 0.0,
            "transient_extra_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "interference_extra_projection_ratio": 0.0,
            "overlap_interference_projection_ratio": 0.0,
            "overlap_interference_extra_projection_ratio": 0.0,
            "overlap_cancel_waveform_l1": 0.0,
            "overlap_cancel_target_projection_ratio": 0.0,
            "overlap_dual_mix_consistency_l1": 0.0,
            "overlap_dual_residual_target_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
            "absent_extra_interval_l1": 0.0,
            "branch_protect_guard_sisdr_loss": 0.0,
            "branch_protect_overlap_base_align_l1": 0.0,
            "branch_protect_teacher_overlap_l1": 0.0,
            "interference_extra_base_align_l1": 0.0,
            "interference_extra_base_delta_projection_ratio": 0.0,
            "gate_abstain_mean": 0.0,
            "gate_keep_mean": 0.0,
            "gate_target_l1": 0.0,
        }
    )
    recipe_metrics: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "count": 0,
            "loss": 0.0,
            "sisdr_db": 0.0,
            "reconstruction_waveform_l1": 0.0,
            "reconstruction_stft_l1": 0.0,
            "reconstruction_extra_waveform_l1": 0.0,
            "reconstruction_extra_stft_l1": 0.0,
            "transient_presence_l1": 0.0,
            "transient_extra_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "interference_extra_projection_ratio": 0.0,
            "overlap_interference_projection_ratio": 0.0,
            "overlap_interference_extra_projection_ratio": 0.0,
            "overlap_cancel_waveform_l1": 0.0,
            "overlap_cancel_target_projection_ratio": 0.0,
            "overlap_dual_mix_consistency_l1": 0.0,
            "overlap_dual_residual_target_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
            "absent_extra_interval_l1": 0.0,
            "branch_protect_guard_sisdr_loss": 0.0,
            "branch_protect_overlap_base_align_l1": 0.0,
            "branch_protect_teacher_overlap_l1": 0.0,
            "interference_extra_base_align_l1": 0.0,
            "interference_extra_base_delta_projection_ratio": 0.0,
            "gate_abstain_mean": 0.0,
            "gate_keep_mean": 0.0,
            "gate_target_l1": 0.0,
        }
    )
    ratio_bucket_metrics: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "count": 0,
            "loss": 0.0,
            "sisdr_db": 0.0,
            "reconstruction_waveform_l1": 0.0,
            "reconstruction_stft_l1": 0.0,
            "reconstruction_extra_waveform_l1": 0.0,
            "reconstruction_extra_stft_l1": 0.0,
            "transient_presence_l1": 0.0,
            "transient_extra_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "interference_extra_projection_ratio": 0.0,
            "overlap_interference_projection_ratio": 0.0,
            "overlap_interference_extra_projection_ratio": 0.0,
            "overlap_cancel_waveform_l1": 0.0,
            "overlap_cancel_target_projection_ratio": 0.0,
            "overlap_dual_mix_consistency_l1": 0.0,
            "overlap_dual_residual_target_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
            "absent_extra_interval_l1": 0.0,
            "branch_protect_guard_sisdr_loss": 0.0,
            "branch_protect_overlap_base_align_l1": 0.0,
            "branch_protect_teacher_overlap_l1": 0.0,
            "interference_extra_base_align_l1": 0.0,
            "interference_extra_base_delta_projection_ratio": 0.0,
            "gate_abstain_mean": 0.0,
            "gate_keep_mean": 0.0,
            "gate_target_l1": 0.0,
        }
    )
    saved = 0
    loss_config = checkpoint.get("loss_config", {})
    compute_loss_kwargs = build_compute_loss_kwargs(loss_config)
    selector_totals = {
        prefix: {"active": False, "selected_count": 0, "total_count": 0}
        for prefix in (
            "reconstruction",
            "reconstruction_extra",
            "transient",
            "transient_extra",
            "interference",
            "interference_extra",
            "overlap_interference",
            "overlap_interference_extra",
            "overlap_cancel",
            "overlap_dual",
            "absent",
            "absent_extra",
            "branch_protect",
            "branch_protect_teacher",
        )
    }

    with torch.no_grad():
        for batch in dataloader:
            batch = move_batch_to_device(batch, device)
            batch_size = len(batch["sample_ids"])
            outputs = model(
                mixture=batch["mixture"],
                mixture_lengths=batch["mixture_lengths"],
                reference=batch["reference"],
                reference_lengths=batch["reference_lengths"],
            )
            teacher_prediction = None
            if teacher_model is not None:
                teacher_outputs = teacher_model(
                    mixture=batch["mixture"],
                    mixture_lengths=batch["mixture_lengths"],
                    reference=batch["reference"],
                    reference_lengths=batch["reference_lengths"],
                )
                teacher_prediction = teacher_outputs["estimated_waveform"]
            reconstruction_sample_weights, reconstruction_extra_sample_weights, reconstruction_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="reconstruction",
                    extra_weight_keys=("reconstruction_extra_waveform_weight", "reconstruction_extra_stft_weight"),
                )
            )
            transient_sample_weights, transient_extra_sample_weights, transient_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="transient",
                    extra_weight_keys=("transient_extra_weight",),
                )
            )
            interference_sample_weights, interference_extra_sample_weights, interference_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="interference",
                    extra_weight_keys=(
                        "interference_extra_weight",
                        "interference_extra_guard_sisdr_weight",
                        "interference_extra_base_align_weight",
                        "interference_extra_base_delta_projection_weight",
                    ),
                )
            )
            overlap_interference_sample_weights, overlap_interference_extra_sample_weights, overlap_interference_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="overlap_interference",
                    extra_weight_keys=(
                        "overlap_interference_weight",
                        "overlap_interference_extra_weight",
                    ),
                )
            )
            overlap_cancel_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="overlap_cancel",
            )
            overlap_dual_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="overlap_dual",
            )
            absent_sample_weights, absent_extra_sample_weights, absent_union_sample_weights = (
                resolve_selector_sample_weights(
                    batch=batch,
                    device=device,
                    loss_config=loss_config,
                    prefix="absent",
                    extra_weight_keys=("absent_extra_weight",),
                )
            )
            branch_protect_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="branch_protect",
            )
            branch_protect_teacher_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="branch_protect_teacher",
            )
            gate_target_values = build_gate_target_values(batch=batch, device=device, loss_config=loss_config)
            gate_target_sample_weights = (
                torch.ones(len(batch["sample_ids"]), dtype=torch.float32, device=device)
                if gate_target_values is not None
                else None
            )
            for prefix, weights in (
                ("reconstruction", reconstruction_union_sample_weights),
                ("reconstruction_extra", reconstruction_extra_sample_weights),
                ("transient", transient_union_sample_weights),
                ("transient_extra", transient_extra_sample_weights),
                ("interference", interference_union_sample_weights),
                ("interference_extra", interference_extra_sample_weights),
                ("overlap_interference", overlap_interference_union_sample_weights),
                ("overlap_interference_extra", overlap_interference_extra_sample_weights),
                ("overlap_cancel", overlap_cancel_sample_weights),
                ("overlap_dual", overlap_dual_sample_weights),
                ("absent", absent_union_sample_weights),
                ("absent_extra", absent_extra_sample_weights),
                ("branch_protect", branch_protect_sample_weights),
                ("branch_protect_teacher", branch_protect_teacher_sample_weights),
            ):
                stats = summarize_selector_weights(weights, len(batch["sample_ids"]))
                selector_totals[prefix]["active"] = selector_totals[prefix]["active"] or bool(stats["active"])
                selector_totals[prefix]["selected_count"] += int(stats["selected_count"])
                selector_totals[prefix]["total_count"] += int(stats["total_count"])
            primary_prediction = resolve_primary_prediction(
                outputs,
                use_branch_prerefine_as_primary_prediction=bool(
                    loss_config.get("use_branch_prerefine_as_primary_prediction", False)
                ),
            )
            reconstruction_extra_prediction = outputs["estimated_waveform"]
            extra_prediction = resolve_branch_extra_prediction(outputs)
            losses = compute_losses(
                prediction=primary_prediction,
                reconstruction_extra_prediction=reconstruction_extra_prediction,
                extra_prediction=extra_prediction,
                teacher_prediction=teacher_prediction,
                mixture=batch["mixture"],
                target=batch["target"],
                lengths=batch["target_lengths"],
                absent_intervals=batch["target_absent_intervals"],
                overlap_intervals=batch["target_overlap_intervals"],
                model=model,
                gate_values=outputs.get("branch_decoder_frame_gate"),
                reconstruction_sample_weights=reconstruction_sample_weights,
                reconstruction_extra_sample_weights=reconstruction_extra_sample_weights,
                transient_sample_weights=transient_sample_weights,
                transient_extra_sample_weights=transient_extra_sample_weights,
                interference_sample_weights=interference_sample_weights,
                interference_extra_sample_weights=interference_extra_sample_weights,
                overlap_interference_sample_weights=overlap_interference_sample_weights,
                overlap_interference_extra_sample_weights=overlap_interference_extra_sample_weights,
                overlap_cancel_prediction=outputs.get("branch_overlap_cancel_estimate_waveform"),
                overlap_dual_target_prediction=outputs.get("branch_overlap_dual_target_waveform"),
                overlap_dual_residual_prediction=outputs.get("branch_overlap_dual_residual_waveform"),
                overlap_cancel_sample_weights=overlap_cancel_sample_weights,
                overlap_cancel_absent_mix_sample_weights=absent_union_sample_weights,
                overlap_dual_sample_weights=overlap_dual_sample_weights,
                branch_protect_sample_weights=branch_protect_sample_weights,
                branch_protect_teacher_sample_weights=branch_protect_teacher_sample_weights,
                absent_sample_weights=absent_sample_weights,
                absent_extra_sample_weights=absent_extra_sample_weights,
                gate_abstain_sample_weights=interference_extra_sample_weights,
                gate_keep_sample_weights=branch_protect_sample_weights,
                gate_target_sample_weights=gate_target_sample_weights,
                gate_target_values=gate_target_values,
                **compute_loss_kwargs,
            )

            totals["loss"] += float(losses.total.item()) * batch_size
            totals["waveform_l1"] += float(losses.waveform_l1.item()) * batch_size
            totals["stft_l1"] += float(losses.stft_l1.item()) * batch_size
            totals["reconstruction_waveform_l1"] += float(losses.reconstruction_waveform_l1.item()) * batch_size
            totals["reconstruction_stft_l1"] += float(losses.reconstruction_stft_l1.item()) * batch_size
            totals["reconstruction_extra_waveform_l1"] += (
                float(losses.reconstruction_extra_waveform_l1.item()) * batch_size
            )
            totals["reconstruction_extra_stft_l1"] += float(losses.reconstruction_extra_stft_l1.item()) * batch_size
            totals["sisdr_loss"] += float(losses.sisdr_loss.item()) * batch_size
            totals["sisdr_db"] += float(losses.sisdr_db.item()) * batch_size
            totals["branch_protect_guard_sisdr_loss"] += (
                float(losses.branch_protect_guard_sisdr_loss.item()) * batch_size
            )
            totals["branch_protect_overlap_base_align_l1"] += (
                float(losses.branch_protect_overlap_base_align_l1.item()) * batch_size
            )
            totals["branch_protect_teacher_overlap_l1"] += (
                float(losses.branch_protect_teacher_overlap_l1.item()) * batch_size
            )
            totals["interference_extra_guard_sisdr_loss"] += (
                float(losses.interference_extra_guard_sisdr_loss.item()) * batch_size
            )
            totals["interference_extra_base_align_l1"] += (
                float(losses.interference_extra_base_align_l1.item()) * batch_size
            )
            totals["interference_extra_base_delta_projection_ratio"] += float(
                losses.interference_extra_base_delta_projection_ratio.item()
            ) * batch_size
            totals["transient_presence_l1"] += float(losses.transient_presence_l1.item()) * batch_size
            totals["transient_extra_presence_l1"] += float(losses.transient_extra_presence_l1.item()) * batch_size
            totals["interference_projection_ratio"] += float(losses.interference_projection_ratio.item()) * batch_size
            totals["interference_extra_projection_ratio"] += float(
                losses.interference_extra_projection_ratio.item()
            ) * batch_size
            totals["overlap_interference_projection_ratio"] += float(
                losses.overlap_interference_projection_ratio.item()
            ) * batch_size
            totals["overlap_interference_extra_projection_ratio"] += float(
                losses.overlap_interference_extra_projection_ratio.item()
            ) * batch_size
            totals["overlap_cancel_waveform_l1"] += float(losses.overlap_cancel_waveform_l1.item()) * batch_size
            totals["overlap_cancel_target_projection_ratio"] += float(
                losses.overlap_cancel_target_projection_ratio.item()
            ) * batch_size
            totals["overlap_dual_mix_consistency_l1"] += (
                float(losses.overlap_dual_mix_consistency_l1.item()) * batch_size
            )
            totals["overlap_dual_residual_target_projection_ratio"] += (
                float(losses.overlap_dual_residual_target_projection_ratio.item()) * batch_size
            )
            totals["absent_interval_l1"] += float(losses.absent_interval_l1.item()) * batch_size
            totals["absent_extra_interval_l1"] += float(losses.absent_extra_interval_l1.item()) * batch_size
            totals["gate_abstain_mean"] += float(losses.gate_abstain_mean.item()) * batch_size
            totals["gate_keep_mean"] += float(losses.gate_keep_mean.item()) * batch_size
            totals["gate_target_l1"] += float(losses.gate_target_l1.item()) * batch_size
            batch_count += 1
            sample_count += batch_size

            primary_predictions, targets, lengths = align_waveforms(
                primary_prediction,
                batch["target"],
                batch["target_lengths"],
            )
            mixtures_aligned, _, _ = align_waveforms(
                batch["mixture"],
                batch["target"],
                batch["target_lengths"],
            )
            reconstruction_extra_predictions, _, _ = align_waveforms(
                reconstruction_extra_prediction,
                batch["target"],
                batch["target_lengths"],
            )
            resolved_extra_prediction = primary_prediction if extra_prediction is None else extra_prediction
            extra_predictions, _, _ = align_waveforms(
                resolved_extra_prediction,
                batch["target"],
                batch["target_lengths"],
            )
            resolved_overlap_cancel_prediction = outputs.get("branch_overlap_cancel_estimate_waveform")
            if resolved_overlap_cancel_prediction is None:
                resolved_overlap_cancel_prediction = primary_prediction
            overlap_cancel_predictions, _, _ = align_waveforms(
                resolved_overlap_cancel_prediction,
                batch["target"],
                batch["target_lengths"],
            )

            for idx, pattern in enumerate(batch["temporal_patterns"]):
                length_int = int(lengths[idx].item())
                sample_loss = torch.mean(
                    torch.abs(primary_predictions[idx, :length_int] - targets[idx, :length_int])
                )
                recipe = batch["recipes"][idx]
                ratio_bucket = target_present_ratio_bucket(
                    float(batch["target_present_ratios"][idx].item())
                )
                sample_sisdr = float(
                    masked_sisdr(
                        primary_predictions[idx : idx + 1],
                        targets[idx : idx + 1],
                        lengths[idx : idx + 1],
                    ).item()
                )
                sample_reconstruction = float(
                    weighted_waveform_l1_loss(
                        prediction=primary_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        sample_weights=(
                            reconstruction_sample_weights[idx : idx + 1]
                            if reconstruction_union_sample_weights is not None and reconstruction_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_reconstruction_stft = float(
                    weighted_stft_l1_loss(
                        prediction=primary_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        sample_weights=(
                            reconstruction_sample_weights[idx : idx + 1]
                            if reconstruction_union_sample_weights is not None and reconstruction_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_reconstruction_extra = float(
                    weighted_waveform_l1_loss(
                        prediction=reconstruction_extra_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        sample_weights=(
                            reconstruction_extra_sample_weights[idx : idx + 1]
                            if reconstruction_union_sample_weights is not None and reconstruction_extra_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_reconstruction_extra_stft = float(
                    weighted_stft_l1_loss(
                        prediction=reconstruction_extra_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        sample_weights=(
                            reconstruction_extra_sample_weights[idx : idx + 1]
                            if reconstruction_union_sample_weights is not None and reconstruction_extra_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_transient = float(
                    transient_presence_l1_loss(
                        prediction=primary_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        top_ratio=float(loss_config.get("transient_top_ratio", 0.12)),
                        min_count=int(loss_config.get("transient_min_count", 8)),
                        mid_low_hz=float(loss_config.get("transient_mid_low_hz", 800.0)),
                        mid_high_hz=float(loss_config.get("transient_mid_high_hz", 3000.0)),
                        presence_low_hz=float(loss_config.get("transient_presence_low_hz", 3000.0)),
                        presence_high_hz=float(loss_config.get("transient_presence_high_hz", 8000.0)),
                        ratio_weight=float(loss_config.get("transient_ratio_weight", 0.5)),
                    ).item()
                )
                sample_transient_extra = float(
                    transient_presence_l1_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        sample_weights=(
                            transient_extra_sample_weights[idx : idx + 1]
                            if transient_union_sample_weights is not None and transient_extra_sample_weights is not None
                            else None
                        ),
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        top_ratio=float(loss_config.get("transient_top_ratio", 0.12)),
                        min_count=int(loss_config.get("transient_min_count", 8)),
                        mid_low_hz=float(loss_config.get("transient_mid_low_hz", 800.0)),
                        mid_high_hz=float(loss_config.get("transient_mid_high_hz", 3000.0)),
                        presence_low_hz=float(loss_config.get("transient_presence_low_hz", 3000.0)),
                        presence_high_hz=float(loss_config.get("transient_presence_high_hz", 8000.0)),
                        ratio_weight=float(loss_config.get("transient_ratio_weight", 0.5)),
                    ).item()
                )
                sample_interference = float(
                    interference_projection_loss(
                        prediction=primary_predictions[idx : idx + 1],
                        mixture=batch["mixture"][idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        mode=str(loss_config.get("interference_loss_mode", "prediction_projection_ratio")),
                    ).item()
                )
                sample_interference_extra = float(
                    interference_projection_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        mixture=batch["mixture"][idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        mode=str(loss_config.get("interference_extra_loss_mode", "prediction_projection_ratio")),
                    ).item()
                )
                sample_overlap_interference = float(
                    overlap_interval_interference_projection_loss(
                        prediction=primary_predictions[idx : idx + 1],
                        mixture=batch["mixture"][idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        overlap_intervals=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            overlap_interference_sample_weights[idx : idx + 1]
                            if overlap_interference_sample_weights is not None
                            else None
                        ),
                        mode=str(loss_config.get("overlap_interference_loss_mode", "prediction_projection_ratio")),
                    ).item()
                )
                sample_overlap_interference_extra = float(
                    overlap_interval_interference_projection_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        mixture=batch["mixture"][idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        overlap_intervals=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            overlap_interference_extra_sample_weights[idx : idx + 1]
                            if overlap_interference_extra_sample_weights is not None
                            else None
                        ),
                        mode=str(loss_config.get("overlap_interference_extra_loss_mode", "prediction_projection_ratio")),
                    ).item()
                )
                sample_overlap_cancel = float(
                    interval_waveform_l1_loss(
                        prediction=overlap_cancel_predictions[idx : idx + 1],
                        target=mixtures_aligned[idx : idx + 1] - targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        intervals_batch=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            overlap_cancel_sample_weights[idx : idx + 1]
                            if overlap_cancel_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_overlap_cancel_target_projection = float(
                    interval_projection_ratio_loss(
                        prediction=overlap_cancel_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        intervals_batch=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            overlap_cancel_sample_weights[idx : idx + 1]
                            if overlap_cancel_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_absent = float(
                    absent_interval_l1_loss(
                        prediction=primary_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        absent_intervals=[batch["target_absent_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                    ).item()
                )
                sample_absent_extra = float(
                    absent_interval_l1_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        absent_intervals=[batch["target_absent_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            absent_extra_sample_weights[idx : idx + 1]
                            if absent_union_sample_weights is not None and absent_extra_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_branch_protect_guard = float(
                    weighted_sisdr_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        sample_weights=(
                            branch_protect_sample_weights[idx : idx + 1]
                            if branch_protect_sample_weights is not None
                            else None
                        ),
                        zero_mean=True,
                    ).item()
                )
                sample_branch_protect_overlap_base_align = float(
                    interval_waveform_l1_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        target=primary_predictions[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        intervals_batch=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            branch_protect_sample_weights[idx : idx + 1]
                            if branch_protect_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_branch_protect_teacher_overlap = (
                    0.0
                    if teacher_prediction is None
                    else float(
                        interval_waveform_l1_loss(
                            prediction=extra_predictions[idx : idx + 1],
                            target=teacher_prediction[idx : idx + 1],
                            lengths=lengths[idx : idx + 1],
                            intervals_batch=[batch["target_overlap_intervals"][idx]],
                            sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                            sample_weights=(
                                branch_protect_teacher_sample_weights[idx : idx + 1]
                                if branch_protect_teacher_sample_weights is not None
                                else (
                                    branch_protect_sample_weights[idx : idx + 1]
                                    if branch_protect_sample_weights is not None
                                    else None
                                )
                            ),
                        ).item()
                    )
                )
                sample_interference_extra_base_align = float(
                    weighted_waveform_l1_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        target=primary_predictions[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        sample_weights=(
                            interference_extra_sample_weights[idx : idx + 1]
                            if interference_extra_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_interference_extra_base_delta_projection = float(
                    base_delta_interference_projection_loss(
                        prediction=extra_predictions[idx : idx + 1],
                        reference_prediction=primary_predictions[idx : idx + 1],
                        mixture=batch["mixture"][idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        sample_weights=(
                            interference_extra_sample_weights[idx : idx + 1]
                            if interference_extra_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_overlap_dual_mix_consistency = float(
                    interval_waveform_l1_loss(
                        prediction=primary_predictions[idx : idx + 1] + overlap_cancel_predictions[idx : idx + 1],
                        target=batch["mixture"][idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        intervals_batch=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            overlap_dual_sample_weights[idx : idx + 1]
                            if overlap_dual_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_overlap_dual_residual_target_projection = float(
                    interval_projection_ratio_loss(
                        prediction=mixtures_aligned[idx : idx + 1] - primary_predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        intervals_batch=[batch["target_overlap_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                        sample_weights=(
                            overlap_dual_sample_weights[idx : idx + 1]
                            if overlap_dual_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_gate_abstain = float(
                    weighted_gate_target_loss(
                        gate_values=(
                            outputs["branch_decoder_frame_gate"][idx : idx + 1]
                            if outputs.get("branch_decoder_frame_gate") is not None
                            else None
                        ),
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        target_value=0.0,
                        sample_weights=(
                            interference_extra_sample_weights[idx : idx + 1]
                            if interference_extra_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_gate_keep = float(
                    weighted_gate_target_loss(
                        gate_values=(
                            outputs["branch_decoder_frame_gate"][idx : idx + 1]
                            if outputs.get("branch_decoder_frame_gate") is not None
                            else None
                        ),
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        target_value=1.0,
                        sample_weights=(
                            branch_protect_sample_weights[idx : idx + 1]
                            if branch_protect_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                sample_gate_target = float(
                    weighted_gate_target_loss(
                        gate_values=(
                            outputs["branch_decoder_frame_gate"][idx : idx + 1]
                            if outputs.get("branch_decoder_frame_gate") is not None
                            else None
                        ),
                        lengths=lengths[idx : idx + 1],
                        model=model,
                        target_values=(
                            gate_target_values[idx : idx + 1]
                            if gate_target_values is not None
                            else None
                        ),
                        target_value=0.0 if gate_target_values is None else None,
                        sample_weights=(
                            gate_target_sample_weights[idx : idx + 1]
                            if gate_target_sample_weights is not None
                            else None
                        ),
                    ).item()
                )
                pattern_metrics[pattern]["count"] += 1
                pattern_metrics[pattern]["loss"] += float(sample_loss.item())
                pattern_metrics[pattern]["sisdr_db"] += sample_sisdr
                pattern_metrics[pattern]["reconstruction_waveform_l1"] += sample_reconstruction
                pattern_metrics[pattern]["reconstruction_stft_l1"] += sample_reconstruction_stft
                pattern_metrics[pattern]["reconstruction_extra_waveform_l1"] += sample_reconstruction_extra
                pattern_metrics[pattern]["reconstruction_extra_stft_l1"] += sample_reconstruction_extra_stft
                pattern_metrics[pattern]["transient_presence_l1"] += sample_transient
                pattern_metrics[pattern]["transient_extra_presence_l1"] += sample_transient_extra
                pattern_metrics[pattern]["interference_projection_ratio"] += sample_interference
                pattern_metrics[pattern]["interference_extra_projection_ratio"] += sample_interference_extra
                pattern_metrics[pattern]["overlap_interference_projection_ratio"] += sample_overlap_interference
                pattern_metrics[pattern]["overlap_interference_extra_projection_ratio"] += (
                    sample_overlap_interference_extra
                )
                pattern_metrics[pattern]["overlap_cancel_waveform_l1"] += sample_overlap_cancel
                pattern_metrics[pattern]["overlap_cancel_target_projection_ratio"] += (
                    sample_overlap_cancel_target_projection
                )
                pattern_metrics[pattern]["overlap_dual_mix_consistency_l1"] += sample_overlap_dual_mix_consistency
                pattern_metrics[pattern]["overlap_dual_residual_target_projection_ratio"] += (
                    sample_overlap_dual_residual_target_projection
                )
                pattern_metrics[pattern]["absent_interval_l1"] += sample_absent
                pattern_metrics[pattern]["absent_extra_interval_l1"] += sample_absent_extra
                pattern_metrics[pattern]["branch_protect_guard_sisdr_loss"] += sample_branch_protect_guard
                pattern_metrics[pattern]["branch_protect_overlap_base_align_l1"] += (
                    sample_branch_protect_overlap_base_align
                )
                pattern_metrics[pattern]["branch_protect_teacher_overlap_l1"] += (
                    sample_branch_protect_teacher_overlap
                )
                pattern_metrics[pattern]["interference_extra_base_align_l1"] += sample_interference_extra_base_align
                pattern_metrics[pattern]["interference_extra_base_delta_projection_ratio"] += (
                    sample_interference_extra_base_delta_projection
                )
                pattern_metrics[pattern]["gate_abstain_mean"] += sample_gate_abstain
                pattern_metrics[pattern]["gate_keep_mean"] += sample_gate_keep
                pattern_metrics[pattern]["gate_target_l1"] += sample_gate_target
                recipe_metrics[recipe]["count"] += 1
                recipe_metrics[recipe]["loss"] += float(sample_loss.item())
                recipe_metrics[recipe]["sisdr_db"] += sample_sisdr
                recipe_metrics[recipe]["reconstruction_waveform_l1"] += sample_reconstruction
                recipe_metrics[recipe]["reconstruction_stft_l1"] += sample_reconstruction_stft
                recipe_metrics[recipe]["reconstruction_extra_waveform_l1"] += sample_reconstruction_extra
                recipe_metrics[recipe]["reconstruction_extra_stft_l1"] += sample_reconstruction_extra_stft
                recipe_metrics[recipe]["transient_presence_l1"] += sample_transient
                recipe_metrics[recipe]["transient_extra_presence_l1"] += sample_transient_extra
                recipe_metrics[recipe]["interference_projection_ratio"] += sample_interference
                recipe_metrics[recipe]["interference_extra_projection_ratio"] += sample_interference_extra
                recipe_metrics[recipe]["overlap_interference_projection_ratio"] += sample_overlap_interference
                recipe_metrics[recipe]["overlap_interference_extra_projection_ratio"] += (
                    sample_overlap_interference_extra
                )
                recipe_metrics[recipe]["overlap_cancel_waveform_l1"] += sample_overlap_cancel
                recipe_metrics[recipe]["overlap_cancel_target_projection_ratio"] += (
                    sample_overlap_cancel_target_projection
                )
                recipe_metrics[recipe]["overlap_dual_mix_consistency_l1"] += sample_overlap_dual_mix_consistency
                recipe_metrics[recipe]["overlap_dual_residual_target_projection_ratio"] += (
                    sample_overlap_dual_residual_target_projection
                )
                recipe_metrics[recipe]["absent_interval_l1"] += sample_absent
                recipe_metrics[recipe]["absent_extra_interval_l1"] += sample_absent_extra
                recipe_metrics[recipe]["branch_protect_guard_sisdr_loss"] += sample_branch_protect_guard
                recipe_metrics[recipe]["branch_protect_overlap_base_align_l1"] += (
                    sample_branch_protect_overlap_base_align
                )
                recipe_metrics[recipe]["branch_protect_teacher_overlap_l1"] += (
                    sample_branch_protect_teacher_overlap
                )
                recipe_metrics[recipe]["interference_extra_base_align_l1"] += sample_interference_extra_base_align
                recipe_metrics[recipe]["interference_extra_base_delta_projection_ratio"] += (
                    sample_interference_extra_base_delta_projection
                )
                recipe_metrics[recipe]["gate_abstain_mean"] += sample_gate_abstain
                recipe_metrics[recipe]["gate_keep_mean"] += sample_gate_keep
                recipe_metrics[recipe]["gate_target_l1"] += sample_gate_target
                ratio_bucket_metrics[ratio_bucket]["count"] += 1
                ratio_bucket_metrics[ratio_bucket]["loss"] += float(sample_loss.item())
                ratio_bucket_metrics[ratio_bucket]["sisdr_db"] += sample_sisdr
                ratio_bucket_metrics[ratio_bucket]["reconstruction_waveform_l1"] += sample_reconstruction
                ratio_bucket_metrics[ratio_bucket]["reconstruction_stft_l1"] += sample_reconstruction_stft
                ratio_bucket_metrics[ratio_bucket]["reconstruction_extra_waveform_l1"] += sample_reconstruction_extra
                ratio_bucket_metrics[ratio_bucket]["reconstruction_extra_stft_l1"] += sample_reconstruction_extra_stft
                ratio_bucket_metrics[ratio_bucket]["transient_presence_l1"] += sample_transient
                ratio_bucket_metrics[ratio_bucket]["transient_extra_presence_l1"] += sample_transient_extra
                ratio_bucket_metrics[ratio_bucket]["interference_projection_ratio"] += sample_interference
                ratio_bucket_metrics[ratio_bucket]["interference_extra_projection_ratio"] += sample_interference_extra
                ratio_bucket_metrics[ratio_bucket]["overlap_interference_projection_ratio"] += sample_overlap_interference
                ratio_bucket_metrics[ratio_bucket]["overlap_interference_extra_projection_ratio"] += (
                    sample_overlap_interference_extra
                )
                ratio_bucket_metrics[ratio_bucket]["overlap_cancel_waveform_l1"] += sample_overlap_cancel
                ratio_bucket_metrics[ratio_bucket]["overlap_cancel_target_projection_ratio"] += (
                    sample_overlap_cancel_target_projection
                )
                ratio_bucket_metrics[ratio_bucket]["overlap_dual_mix_consistency_l1"] += (
                    sample_overlap_dual_mix_consistency
                )
                ratio_bucket_metrics[ratio_bucket]["overlap_dual_residual_target_projection_ratio"] += (
                    sample_overlap_dual_residual_target_projection
                )
                ratio_bucket_metrics[ratio_bucket]["absent_interval_l1"] += sample_absent
                ratio_bucket_metrics[ratio_bucket]["absent_extra_interval_l1"] += sample_absent_extra
                ratio_bucket_metrics[ratio_bucket]["branch_protect_guard_sisdr_loss"] += sample_branch_protect_guard
                ratio_bucket_metrics[ratio_bucket]["branch_protect_overlap_base_align_l1"] += (
                    sample_branch_protect_overlap_base_align
                )
                ratio_bucket_metrics[ratio_bucket]["branch_protect_teacher_overlap_l1"] += (
                    sample_branch_protect_teacher_overlap
                )
                ratio_bucket_metrics[ratio_bucket]["interference_extra_base_align_l1"] += (
                    sample_interference_extra_base_align
                )
                ratio_bucket_metrics[ratio_bucket]["interference_extra_base_delta_projection_ratio"] += (
                    sample_interference_extra_base_delta_projection
                )
                ratio_bucket_metrics[ratio_bucket]["gate_abstain_mean"] += sample_gate_abstain
                ratio_bucket_metrics[ratio_bucket]["gate_keep_mean"] += sample_gate_keep
                ratio_bucket_metrics[ratio_bucket]["gate_target_l1"] += sample_gate_target

                if saved < args.save_audio_count:
                    sample_id = batch["sample_ids"][idx]
                    sample_dir = sample_output_dir / sample_id
                    save_audio(
                        sample_dir / "estimate.wav",
                        reconstruction_extra_predictions[idx, :length_int],
                        args.sample_rate,
                    )
                    save_audio(
                        sample_dir / "target.wav",
                        targets[idx, :length_int],
                        args.sample_rate,
                    )
                    save_audio(
                        sample_dir / "mixture.wav",
                        batch["mixture"][idx, :length_int],
                        args.sample_rate,
                    )
                    (sample_dir / "sample_meta.json").write_text(
                        json.dumps(
                            {
                                "sample_id": sample_id,
                                "temporal_pattern": pattern,
                                "recipe": batch["recipes"][idx],
                                "target_present_ratio": float(
                                    batch["target_present_ratios"][idx].item()
                                ),
                                "reconstruction_waveform_l1": sample_reconstruction,
                                "reconstruction_stft_l1": sample_reconstruction_stft,
                                "reconstruction_extra_waveform_l1": sample_reconstruction_extra,
                                "reconstruction_extra_stft_l1": sample_reconstruction_extra_stft,
                                "transient_presence_l1": sample_transient,
                                "transient_extra_presence_l1": sample_transient_extra,
                                "interference_projection_ratio": sample_interference,
                                "interference_extra_projection_ratio": sample_interference_extra,
                                "overlap_interference_projection_ratio": sample_overlap_interference,
                                "overlap_interference_extra_projection_ratio": sample_overlap_interference_extra,
                                "overlap_cancel_waveform_l1": sample_overlap_cancel,
                                "overlap_cancel_target_projection_ratio": (
                                    sample_overlap_cancel_target_projection
                                ),
                                "overlap_dual_mix_consistency_l1": sample_overlap_dual_mix_consistency,
                                "overlap_dual_residual_target_projection_ratio": (
                                    sample_overlap_dual_residual_target_projection
                                ),
                                "absent_interval_l1": sample_absent,
                                "absent_extra_interval_l1": sample_absent_extra,
                                "branch_protect_guard_sisdr_loss": sample_branch_protect_guard,
                                "branch_protect_overlap_base_align_l1": (
                                    sample_branch_protect_overlap_base_align
                                ),
                                "branch_protect_teacher_overlap_l1": (
                                    sample_branch_protect_teacher_overlap
                                ),
                                "interference_extra_base_align_l1": sample_interference_extra_base_align,
                                "interference_extra_base_delta_projection_ratio": (
                                    sample_interference_extra_base_delta_projection
                                ),
                                "gate_abstain_mean": sample_gate_abstain,
                                "gate_keep_mean": sample_gate_keep,
                                "gate_target_l1": sample_gate_target,
                                "metadata_path": batch["metadata_paths"][idx],
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                        + "\n",
                        encoding="utf-8",
                        newline="\n",
                    )
                    saved += 1

    summary = {
        "manifest": serialize_repo_path(args.manifest),
        "checkpoint": serialize_repo_path(args.checkpoint),
        "teacher_checkpoint": serialize_repo_path(teacher_checkpoint_path),
        "device": device.type,
        "batch_size": args.batch_size,
        "sample_rate": args.sample_rate,
        "save_audio_count": args.save_audio_count,
        "model_config": model_config,
        "loss_config": loss_config,
        "start_time": start_dt.isoformat(timespec="seconds"),
        "end_time": datetime.now().isoformat(timespec="seconds"),
        "elapsed_sec": round(time.time() - start_ts, 3),
        "num_batches": batch_count,
        "num_samples": sample_count,
        "metrics": {
            key: (value / max(1, sample_count))
            for key, value in totals.items()
        },
        "selector_metrics": {
            prefix: {
                "active": bool(totals["active"]),
                "selected_count": int(totals["selected_count"]),
                "total_count": int(totals["total_count"]),
                "selected_fraction": (
                    float(totals["selected_count"]) / float(totals["total_count"])
                    if int(totals["total_count"]) > 0
                    else None
                ),
            }
            for prefix, totals in selector_totals.items()
        },
        "pattern_metrics": {
            pattern: {
                "count": int(values["count"]),
                "avg_l1": values["loss"] / max(1, int(values["count"])),
                "avg_sisdr_db": values["sisdr_db"] / max(1, int(values["count"])),
                "avg_reconstruction_waveform_l1": (
                    values["reconstruction_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_reconstruction_stft_l1": values["reconstruction_stft_l1"] / max(1, int(values["count"])),
                "avg_reconstruction_extra_waveform_l1": (
                    values["reconstruction_extra_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_reconstruction_extra_stft_l1": (
                    values["reconstruction_extra_stft_l1"] / max(1, int(values["count"]))
                ),
                "avg_transient_presence_l1": values["transient_presence_l1"] / max(1, int(values["count"])),
                "avg_transient_extra_presence_l1": (
                    values["transient_extra_presence_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_projection_ratio": (
                    values["interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_projection_ratio": (
                    values["interference_extra_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_interference_projection_ratio": (
                    values["overlap_interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_interference_extra_projection_ratio": (
                    values["overlap_interference_extra_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_cancel_waveform_l1": (
                    values["overlap_cancel_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_overlap_cancel_target_projection_ratio": (
                    values["overlap_cancel_target_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_dual_mix_consistency_l1": (
                    values["overlap_dual_mix_consistency_l1"] / max(1, int(values["count"]))
                ),
                "avg_overlap_dual_residual_target_projection_ratio": (
                    values["overlap_dual_residual_target_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_guard_sisdr_loss": (
                    values["branch_protect_guard_sisdr_loss"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_overlap_base_align_l1": (
                    values["branch_protect_overlap_base_align_l1"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_teacher_overlap_l1": (
                    values["branch_protect_teacher_overlap_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_base_align_l1": (
                    values["interference_extra_base_align_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_base_delta_projection_ratio": (
                    values["interference_extra_base_delta_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_absent_interval_l1": values["absent_interval_l1"] / max(1, int(values["count"])),
                "avg_absent_extra_interval_l1": (
                    values["absent_extra_interval_l1"] / max(1, int(values["count"]))
                ),
                "avg_gate_abstain_mean": values["gate_abstain_mean"] / max(1, int(values["count"])),
                "avg_gate_keep_mean": values["gate_keep_mean"] / max(1, int(values["count"])),
                "avg_gate_target_l1": values["gate_target_l1"] / max(1, int(values["count"])),
            }
            for pattern, values in sorted(pattern_metrics.items())
        },
        "recipe_metrics": {
            recipe: {
                "count": int(values["count"]),
                "avg_l1": values["loss"] / max(1, int(values["count"])),
                "avg_sisdr_db": values["sisdr_db"] / max(1, int(values["count"])),
                "avg_reconstruction_waveform_l1": (
                    values["reconstruction_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_reconstruction_stft_l1": values["reconstruction_stft_l1"] / max(1, int(values["count"])),
                "avg_reconstruction_extra_waveform_l1": (
                    values["reconstruction_extra_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_reconstruction_extra_stft_l1": (
                    values["reconstruction_extra_stft_l1"] / max(1, int(values["count"]))
                ),
                "avg_transient_presence_l1": values["transient_presence_l1"] / max(1, int(values["count"])),
                "avg_transient_extra_presence_l1": (
                    values["transient_extra_presence_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_projection_ratio": (
                    values["interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_projection_ratio": (
                    values["interference_extra_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_interference_projection_ratio": (
                    values["overlap_interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_interference_extra_projection_ratio": (
                    values["overlap_interference_extra_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_cancel_waveform_l1": (
                    values["overlap_cancel_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_overlap_cancel_target_projection_ratio": (
                    values["overlap_cancel_target_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_dual_mix_consistency_l1": (
                    values["overlap_dual_mix_consistency_l1"] / max(1, int(values["count"]))
                ),
                "avg_overlap_dual_residual_target_projection_ratio": (
                    values["overlap_dual_residual_target_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_guard_sisdr_loss": (
                    values["branch_protect_guard_sisdr_loss"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_overlap_base_align_l1": (
                    values["branch_protect_overlap_base_align_l1"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_teacher_overlap_l1": (
                    values["branch_protect_teacher_overlap_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_base_align_l1": (
                    values["interference_extra_base_align_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_base_delta_projection_ratio": (
                    values["interference_extra_base_delta_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_absent_interval_l1": values["absent_interval_l1"] / max(1, int(values["count"])),
                "avg_absent_extra_interval_l1": (
                    values["absent_extra_interval_l1"] / max(1, int(values["count"]))
                ),
                "avg_gate_abstain_mean": values["gate_abstain_mean"] / max(1, int(values["count"])),
                "avg_gate_keep_mean": values["gate_keep_mean"] / max(1, int(values["count"])),
                "avg_gate_target_l1": values["gate_target_l1"] / max(1, int(values["count"])),
            }
            for recipe, values in sorted(recipe_metrics.items())
        },
        "target_present_ratio_bucket_metrics": {
            bucket: {
                "count": int(values["count"]),
                "avg_l1": values["loss"] / max(1, int(values["count"])),
                "avg_sisdr_db": values["sisdr_db"] / max(1, int(values["count"])),
                "avg_reconstruction_waveform_l1": (
                    values["reconstruction_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_reconstruction_stft_l1": values["reconstruction_stft_l1"] / max(1, int(values["count"])),
                "avg_reconstruction_extra_waveform_l1": (
                    values["reconstruction_extra_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_reconstruction_extra_stft_l1": (
                    values["reconstruction_extra_stft_l1"] / max(1, int(values["count"]))
                ),
                "avg_transient_presence_l1": values["transient_presence_l1"] / max(1, int(values["count"])),
                "avg_transient_extra_presence_l1": (
                    values["transient_extra_presence_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_projection_ratio": (
                    values["interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_projection_ratio": (
                    values["interference_extra_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_interference_projection_ratio": (
                    values["overlap_interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_interference_extra_projection_ratio": (
                    values["overlap_interference_extra_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_cancel_waveform_l1": (
                    values["overlap_cancel_waveform_l1"] / max(1, int(values["count"]))
                ),
                "avg_overlap_cancel_target_projection_ratio": (
                    values["overlap_cancel_target_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_overlap_dual_mix_consistency_l1": (
                    values["overlap_dual_mix_consistency_l1"] / max(1, int(values["count"]))
                ),
                "avg_overlap_dual_residual_target_projection_ratio": (
                    values["overlap_dual_residual_target_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_guard_sisdr_loss": (
                    values["branch_protect_guard_sisdr_loss"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_overlap_base_align_l1": (
                    values["branch_protect_overlap_base_align_l1"] / max(1, int(values["count"]))
                ),
                "avg_branch_protect_teacher_overlap_l1": (
                    values["branch_protect_teacher_overlap_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_base_align_l1": (
                    values["interference_extra_base_align_l1"] / max(1, int(values["count"]))
                ),
                "avg_interference_extra_base_delta_projection_ratio": (
                    values["interference_extra_base_delta_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_absent_interval_l1": values["absent_interval_l1"] / max(1, int(values["count"])),
                "avg_absent_extra_interval_l1": (
                    values["absent_extra_interval_l1"] / max(1, int(values["count"]))
                ),
                "avg_gate_abstain_mean": values["gate_abstain_mean"] / max(1, int(values["count"])),
                "avg_gate_keep_mean": values["gate_keep_mean"] / max(1, int(values["count"])),
                "avg_gate_target_l1": values["gate_target_l1"] / max(1, int(values["count"])),
            }
            for bucket, values in sorted(ratio_bucket_metrics.items())
        },
        "saved_samples_dir": serialize_repo_path(sample_output_dir),
    }
    (args.output_dir / "eval_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(json.dumps(summary["metrics"], ensure_ascii=False, indent=2))
    print(f"eval_end={summary['end_time']}")
    print(f"elapsed_sec={summary['elapsed_sec']}")

if __name__ == "__main__":
    main()
