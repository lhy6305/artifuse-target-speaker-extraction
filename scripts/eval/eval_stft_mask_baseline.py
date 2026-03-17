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


def build_selector_sample_weights(
    batch: dict,
    device: torch.device,
    loss_config: dict,
    prefix: str,
) -> torch.Tensor | None:
    recipes = set(loss_config.get(f"{prefix}_focus_recipes", []))
    patterns = set(loss_config.get(f"{prefix}_focus_patterns", []))
    min_ratio = loss_config.get(f"{prefix}_min_target_ratio")
    max_ratio = loss_config.get(f"{prefix}_max_target_ratio")
    has_selector = bool(recipes or patterns or min_ratio is not None or max_ratio is not None)
    if not has_selector:
        return None

    weights = torch.ones(len(batch["sample_ids"]), dtype=torch.float32, device=device)
    if recipes:
        recipe_mask = torch.tensor(
            [1.0 if recipe in recipes else 0.0 for recipe in batch["recipes"]],
            dtype=torch.float32,
            device=device,
        )
        weights = weights * recipe_mask
    if patterns:
        pattern_mask = torch.tensor(
            [1.0 if pattern in patterns else 0.0 for pattern in batch["temporal_patterns"]],
            dtype=torch.float32,
            device=device,
        )
        weights = weights * pattern_mask

    ratios = batch["target_present_ratios"].to(device=device, dtype=torch.float32)
    if min_ratio is not None:
        weights = weights * (ratios >= float(min_ratio)).float()
    if max_ratio is not None:
        weights = weights * (ratios <= float(max_ratio)).float()
    return weights


def build_compute_loss_kwargs(loss_config: dict) -> dict:
    return {
        key: value
        for key, value in loss_config.items()
        if key
        not in {
            "transient_focus_recipes",
            "transient_focus_patterns",
            "transient_min_target_ratio",
            "transient_max_target_ratio",
            "interference_focus_recipes",
            "interference_focus_patterns",
            "interference_min_target_ratio",
            "interference_max_target_ratio",
            "absent_focus_recipes",
            "absent_focus_patterns",
            "absent_min_target_ratio",
            "absent_max_target_ratio",
        }
    }


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


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


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

    totals = {
        "loss": 0.0,
        "waveform_l1": 0.0,
        "stft_l1": 0.0,
        "sisdr_db": 0.0,
        "transient_presence_l1": 0.0,
        "interference_projection_ratio": 0.0,
        "absent_interval_l1": 0.0,
    }
    batch_count = 0
    pattern_metrics: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "count": 0,
            "loss": 0.0,
            "sisdr_db": 0.0,
            "transient_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
        }
    )
    recipe_metrics: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "count": 0,
            "loss": 0.0,
            "sisdr_db": 0.0,
            "transient_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
        }
    )
    ratio_bucket_metrics: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {
            "count": 0,
            "loss": 0.0,
            "sisdr_db": 0.0,
            "transient_presence_l1": 0.0,
            "interference_projection_ratio": 0.0,
            "absent_interval_l1": 0.0,
        }
    )
    saved = 0
    loss_config = checkpoint.get("loss_config", {})
    compute_loss_kwargs = build_compute_loss_kwargs(loss_config)

    with torch.no_grad():
        for batch in dataloader:
            batch = move_batch_to_device(batch, device)
            outputs = model(
                mixture=batch["mixture"],
                mixture_lengths=batch["mixture_lengths"],
                reference=batch["reference"],
                reference_lengths=batch["reference_lengths"],
            )
            transient_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="transient",
            )
            interference_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="interference",
            )
            absent_sample_weights = build_selector_sample_weights(
                batch=batch,
                device=device,
                loss_config=loss_config,
                prefix="absent",
            )
            losses = compute_losses(
                prediction=outputs["estimated_waveform"],
                mixture=batch["mixture"],
                target=batch["target"],
                lengths=batch["target_lengths"],
                absent_intervals=batch["target_absent_intervals"],
                model=model,
                transient_sample_weights=transient_sample_weights,
                interference_sample_weights=interference_sample_weights,
                absent_sample_weights=absent_sample_weights,
                **compute_loss_kwargs,
            )
            sisdr = masked_sisdr(
                prediction=outputs["estimated_waveform"],
                target=batch["target"],
                lengths=batch["target_lengths"],
            )

            totals["loss"] += float(losses.total.item())
            totals["waveform_l1"] += float(losses.waveform_l1.item())
            totals["stft_l1"] += float(losses.stft_l1.item())
            totals["sisdr_db"] += float(sisdr.item())
            totals["transient_presence_l1"] += float(losses.transient_presence_l1.item())
            totals["interference_projection_ratio"] += float(losses.interference_projection_ratio.item())
            totals["absent_interval_l1"] += float(losses.absent_interval_l1.item())
            batch_count += 1

            predictions, targets, lengths = align_waveforms(
                outputs["estimated_waveform"],
                batch["target"],
                batch["target_lengths"],
            )

            for idx, pattern in enumerate(batch["temporal_patterns"]):
                length_int = int(lengths[idx].item())
                sample_loss = torch.mean(
                    torch.abs(predictions[idx, :length_int] - targets[idx, :length_int])
                )
                recipe = batch["recipes"][idx]
                ratio_bucket = target_present_ratio_bucket(
                    float(batch["target_present_ratios"][idx].item())
                )
                sample_sisdr = float(
                    masked_sisdr(
                        predictions[idx : idx + 1],
                        targets[idx : idx + 1],
                        lengths[idx : idx + 1],
                    ).item()
                )
                sample_transient = float(
                    transient_presence_l1_loss(
                        prediction=predictions[idx : idx + 1],
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
                sample_interference = float(
                    interference_projection_loss(
                        prediction=predictions[idx : idx + 1],
                        mixture=batch["mixture"][idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                    ).item()
                )
                sample_absent = float(
                    absent_interval_l1_loss(
                        prediction=predictions[idx : idx + 1],
                        target=targets[idx : idx + 1],
                        lengths=lengths[idx : idx + 1],
                        absent_intervals=[batch["target_absent_intervals"][idx]],
                        sample_rate=int(loss_config.get("sample_rate", args.sample_rate)),
                    ).item()
                )
                pattern_metrics[pattern]["count"] += 1
                pattern_metrics[pattern]["loss"] += float(sample_loss.item())
                pattern_metrics[pattern]["sisdr_db"] += sample_sisdr
                pattern_metrics[pattern]["transient_presence_l1"] += sample_transient
                pattern_metrics[pattern]["interference_projection_ratio"] += sample_interference
                pattern_metrics[pattern]["absent_interval_l1"] += sample_absent
                recipe_metrics[recipe]["count"] += 1
                recipe_metrics[recipe]["loss"] += float(sample_loss.item())
                recipe_metrics[recipe]["sisdr_db"] += sample_sisdr
                recipe_metrics[recipe]["transient_presence_l1"] += sample_transient
                recipe_metrics[recipe]["interference_projection_ratio"] += sample_interference
                recipe_metrics[recipe]["absent_interval_l1"] += sample_absent
                ratio_bucket_metrics[ratio_bucket]["count"] += 1
                ratio_bucket_metrics[ratio_bucket]["loss"] += float(sample_loss.item())
                ratio_bucket_metrics[ratio_bucket]["sisdr_db"] += sample_sisdr
                ratio_bucket_metrics[ratio_bucket]["transient_presence_l1"] += sample_transient
                ratio_bucket_metrics[ratio_bucket]["interference_projection_ratio"] += sample_interference
                ratio_bucket_metrics[ratio_bucket]["absent_interval_l1"] += sample_absent

                if saved < args.save_audio_count:
                    sample_id = batch["sample_ids"][idx]
                    sample_dir = sample_output_dir / sample_id
                    save_audio(
                        sample_dir / "estimate.wav",
                        predictions[idx, :length_int],
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
                                "transient_presence_l1": sample_transient,
                                "interference_projection_ratio": sample_interference,
                                "absent_interval_l1": sample_absent,
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
        "num_samples": len(dataset),
        "metrics": {
            key: (value / max(1, batch_count))
            for key, value in totals.items()
        },
        "pattern_metrics": {
            pattern: {
                "count": int(values["count"]),
                "avg_l1": values["loss"] / max(1, int(values["count"])),
                "avg_sisdr_db": values["sisdr_db"] / max(1, int(values["count"])),
                "avg_transient_presence_l1": values["transient_presence_l1"] / max(1, int(values["count"])),
                "avg_interference_projection_ratio": (
                    values["interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_absent_interval_l1": values["absent_interval_l1"] / max(1, int(values["count"])),
            }
            for pattern, values in sorted(pattern_metrics.items())
        },
        "recipe_metrics": {
            recipe: {
                "count": int(values["count"]),
                "avg_l1": values["loss"] / max(1, int(values["count"])),
                "avg_sisdr_db": values["sisdr_db"] / max(1, int(values["count"])),
                "avg_transient_presence_l1": values["transient_presence_l1"] / max(1, int(values["count"])),
                "avg_interference_projection_ratio": (
                    values["interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_absent_interval_l1": values["absent_interval_l1"] / max(1, int(values["count"])),
            }
            for recipe, values in sorted(recipe_metrics.items())
        },
        "target_present_ratio_bucket_metrics": {
            bucket: {
                "count": int(values["count"]),
                "avg_l1": values["loss"] / max(1, int(values["count"])),
                "avg_sisdr_db": values["sisdr_db"] / max(1, int(values["count"])),
                "avg_transient_presence_l1": values["transient_presence_l1"] / max(1, int(values["count"])),
                "avg_interference_projection_ratio": (
                    values["interference_projection_ratio"] / max(1, int(values["count"]))
                ),
                "avg_absent_interval_l1": values["absent_interval_l1"] / max(1, int(values["count"])),
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
