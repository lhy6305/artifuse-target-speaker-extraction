from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any

import torch
import torchaudio


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.models import STFTMaskBaseline
from tse_prefix.data.synthetic_dataset import compute_local_proxy_intervals


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Rank many checkpoints on the silence-over-leak subproblem using a near-real manifest. "
            "The scoring favors target-absent suppression while keeping target-present samples within a backstop margin."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=ROOT / "experiments" / "checkpoints",
    )
    parser.add_argument(
        "--checkpoint-glob",
        action="append",
        dest="checkpoint_globs",
        default=[],
        help="Directory name glob under --checkpoint-dir. Repeat to union multiple families.",
    )
    parser.add_argument(
        "--include-checkpoint",
        action="append",
        dest="include_checkpoints",
        default=[],
        help="Explicit checkpoint directory name under --checkpoint-dir. Repeat to pin candidates.",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=16000,
    )
    parser.add_argument(
        "--target-present-energy-threshold",
        type=float,
        default=1e-8,
    )
    parser.add_argument(
        "--target-present-backstop-margin-db",
        type=float,
        default=0.75,
    )
    parser.add_argument(
        "--absent-near-tie-margin-db",
        type=float,
        default=0.75,
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=12,
    )
    parser.add_argument(
        "--present-guardrail-baseline",
        type=str,
        default="baseline_stft_mask_stage2",
        help="Checkpoint label used as the present-sample non-regression baseline.",
    )
    parser.add_argument(
        "--max-target-capture-regression-db",
        type=float,
        default=2.0,
        help="Count a present-sample violation when target capture drops below the baseline by more than this margin.",
    )
    parser.add_argument(
        "--max-residual-share-increase",
        type=float,
        default=0.08,
        help="Count a present-sample violation when residual output share increases above the baseline by more than this margin.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        required=True,
    )
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_checkpoint(path: Path, device: torch.device) -> dict[str, Any]:
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except pickle.UnpicklingError:
        return torch.load(path, map_location=device, weights_only=False)


def resolve_model_config(checkpoint: dict[str, Any]) -> dict[str, Any]:
    model_config = dict(checkpoint.get("model_config", {}))
    if "conditioning_mode" not in model_config:
        state_dict = checkpoint["model_state_dict"]
        if "condition_proj.weight" in state_dict:
            model_config["conditioning_mode"] = "legacy_bias"
    return model_config


def build_model(checkpoint_path: Path, device: torch.device) -> tuple[STFTMaskBaseline, dict[str, Any], dict[str, Any]]:
    checkpoint = load_checkpoint(checkpoint_path, device)
    model_config = resolve_model_config(checkpoint)
    model = STFTMaskBaseline(**model_config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, model_config, checkpoint.get("loss_config", {})


def load_audio_mono(path: Path, sample_rate: int) -> torch.Tensor:
    waveform, sr = torchaudio.load(str(path))
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != sample_rate:
        waveform = torchaudio.functional.resample(waveform, sr, sample_rate)
    return waveform.squeeze(0).contiguous()


def energy(waveform: torch.Tensor) -> float:
    return float(torch.dot(waveform, waveform).item())


def safe_log10(value: float, eps: float = 1e-12) -> float:
    return float(10.0 * torch.log10(torch.tensor(max(value, eps), dtype=torch.float64)).item())


def rms_dbfs(waveform: torch.Tensor) -> float:
    return safe_log10(float(torch.mean(torch.square(waveform)).item() + 1e-12))


def fit_scalar(reference: torch.Tensor, target: torch.Tensor, eps: float = 1e-12) -> float:
    denom = energy(reference)
    if denom <= eps:
        return 0.0
    return float(torch.dot(reference, target).item() / denom)


def capture_db(output: torch.Tensor, reference: torch.Tensor, eps: float = 1e-12) -> tuple[float | None, float | None]:
    ref_energy = energy(reference)
    if ref_energy <= eps:
        return None, None
    scale = fit_scalar(reference, output, eps=eps)
    return safe_log10((scale * scale) + eps), scale


def joint_residual_share(output: torch.Tensor, basis_vectors: list[torch.Tensor], eps: float = 1e-12) -> float:
    usable = [vector for vector in basis_vectors if energy(vector) > eps]
    output_energy = max(energy(output), eps)
    if not usable:
        return 1.0
    basis = torch.stack(usable, dim=1)
    coefficients = torch.linalg.lstsq(basis, output.unsqueeze(1)).solution.squeeze(1)
    fitted = basis @ coefficients
    residual = output - fitted
    return float(min(max(energy(residual) / output_energy, 0.0), 1.0))


def mean_or_none(values: list[float | None]) -> float | None:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return None
    return float(sum(usable) / len(usable))


def list_candidate_checkpoints(args: argparse.Namespace) -> list[Path]:
    candidates: dict[str, Path] = {}
    for name in args.include_checkpoints:
        best_path = (args.checkpoint_dir / name / "best.pt").resolve()
        if best_path.exists():
            candidates[name] = best_path

    if args.checkpoint_globs:
        globs = list(args.checkpoint_globs)
    elif args.include_checkpoints:
        globs = []
    else:
        globs = ["baseline_stft_mask_stage2", "baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v*"]
    for pattern in globs:
        for directory in sorted(args.checkpoint_dir.glob(pattern)):
            if not directory.is_dir():
                continue
            best_path = (directory / "best.pt").resolve()
            if best_path.exists():
                candidates.setdefault(directory.name, best_path)
    return [candidates[name] for name in sorted(candidates)]


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    manifest_rows = load_jsonl(args.manifest)
    checkpoint_paths = list_candidate_checkpoints(args)
    if not checkpoint_paths:
        raise SystemExit("No checkpoints found.")

    sample_cache: list[dict[str, Any]] = []
    for row in manifest_rows:
        mixture = load_audio_mono(ROOT / row["mixture_audio_path"], args.sample_rate)
        target = load_audio_mono(ROOT / row["target_audio_path"], args.sample_rate)
        reference = load_audio_mono(ROOT / row["reference_audio_path"], args.sample_rate)
        common_length = min(mixture.shape[-1], target.shape[-1], reference.shape[-1])
        mixture = mixture[:common_length]
        target = target[:common_length]
        reference = reference[:common_length]
        interference = mixture - target
        mixture_energy = max(energy(mixture), 1e-12)
        target_energy_ratio = energy(target) / mixture_energy
        metadata_path_raw = str(row.get("metadata_path", "")).strip()
        metadata = {}
        if metadata_path_raw:
            metadata_path = ROOT / metadata_path_raw
            if metadata_path.exists():
                with metadata_path.open("r", encoding="utf-8") as fh:
                    metadata = json.load(fh)
        sample_cache.append(
            {
                "sample_id": row["sample_id"],
                "note": str(row.get("note", "")),
                "mixture": mixture,
                "target": target,
                "reference": reference,
                "interference": interference,
                "local_proxy_intervals": compute_local_proxy_intervals(metadata),
                "target_present": bool(target_energy_ratio > args.target_present_energy_threshold),
                "target_energy_ratio": target_energy_ratio,
            }
        )

    checkpoint_rows: list[dict[str, Any]] = []
    sample_scores_by_checkpoint: dict[str, dict[str, dict[str, Any]]] = {}

    with torch.no_grad():
        for checkpoint_path in checkpoint_paths:
            label = checkpoint_path.parent.name
            model, model_config, loss_config = build_model(checkpoint_path, device)
            absent_rows: list[dict[str, Any]] = []
            present_rows: list[dict[str, Any]] = []
            per_sample: dict[str, dict[str, Any]] = {}

            for sample in sample_cache:
                mixture = sample["mixture"].unsqueeze(0).to(device)
                reference = sample["reference"].unsqueeze(0).to(device)
                mixture_lengths = torch.tensor([sample["mixture"].shape[-1]], dtype=torch.long, device=device)
                reference_lengths = torch.tensor([sample["reference"].shape[-1]], dtype=torch.long, device=device)
                estimate = model(
                    mixture=mixture,
                    mixture_lengths=mixture_lengths,
                    reference=reference,
                    reference_lengths=reference_lengths,
                    local_proxy_intervals=[sample["local_proxy_intervals"]],
                )["estimated_waveform"][0, : sample["mixture"].shape[-1]].cpu()

                target_capture_db, _ = capture_db(estimate, sample["target"])
                interference_capture_db, _ = capture_db(estimate, sample["interference"])
                retention_minus_leak_db = None
                if target_capture_db is not None and interference_capture_db is not None:
                    retention_minus_leak_db = float(target_capture_db - interference_capture_db)
                present_backstop_score_db = retention_minus_leak_db
                present_backstop_mode = "retention_minus_leak"
                if sample["target_present"] and present_backstop_score_db is None:
                    present_backstop_score_db = target_capture_db
                    present_backstop_mode = "target_capture_only"
                row = {
                    "sample_id": sample["sample_id"],
                    "note": sample["note"],
                    "target_present": sample["target_present"],
                    "target_energy_ratio": sample["target_energy_ratio"],
                    "rms_dbfs": rms_dbfs(estimate),
                    "target_capture_db": target_capture_db,
                    "interference_capture_db": interference_capture_db,
                    "retention_minus_leak_db": retention_minus_leak_db,
                    "present_backstop_score_db": present_backstop_score_db,
                    "present_backstop_mode": present_backstop_mode,
                    "residual_output_share": joint_residual_share(estimate, [sample["target"], sample["interference"]]),
                }
                per_sample[sample["sample_id"]] = row
                if sample["target_present"]:
                    present_rows.append(row)
                else:
                    absent_rows.append(row)

            checkpoint_rows.append(
                {
                    "label": label,
                    "checkpoint": serialize_repo_path(checkpoint_path),
                    "model_config": model_config,
                    "loss_config": loss_config,
                    "absent_count": len(absent_rows),
                    "absent_mean_interference_capture_db": mean_or_none(
                        [row["interference_capture_db"] for row in absent_rows]
                    ),
                    "absent_mean_rms_dbfs": mean_or_none([row["rms_dbfs"] for row in absent_rows]),
                    "absent_mean_residual_output_share": mean_or_none(
                        [row["residual_output_share"] for row in absent_rows]
                    ),
                    "present_count": len(present_rows),
                    "present_mean_target_capture_db": mean_or_none(
                        [row["target_capture_db"] for row in present_rows]
                    ),
                    "present_mean_interference_capture_db": mean_or_none(
                        [row["interference_capture_db"] for row in present_rows]
                    ),
                    "present_mean_retention_minus_leak_db": mean_or_none(
                        [row["retention_minus_leak_db"] for row in present_rows]
                    ),
                    "present_mean_backstop_score_db": mean_or_none(
                        [row["present_backstop_score_db"] for row in present_rows]
                    ),
                    "present_mean_residual_output_share": mean_or_none(
                        [row["residual_output_share"] for row in present_rows]
                    ),
                }
            )
            sample_scores_by_checkpoint[label] = per_sample

    absent_sample_ids = [sample["sample_id"] for sample in sample_cache if not sample["target_present"]]
    present_sample_ids = [sample["sample_id"] for sample in sample_cache if sample["target_present"]]

    absent_best_by_sample: dict[str, list[str]] = {}
    for sample_id in absent_sample_ids:
        available = [
            (label, sample_scores_by_checkpoint[label][sample_id]["interference_capture_db"])
            for label in sample_scores_by_checkpoint
            if sample_scores_by_checkpoint[label][sample_id]["interference_capture_db"] is not None
        ]
        best_value = min(float(value) for _, value in available)
        absent_best_by_sample[sample_id] = [
            label
            for label, value in available
            if float(value - best_value) <= args.absent_near_tie_margin_db
        ]

    present_best_by_sample: dict[str, list[str]] = {}
    for sample_id in present_sample_ids:
        available = [
            (label, sample_scores_by_checkpoint[label][sample_id]["present_backstop_score_db"])
            for label in sample_scores_by_checkpoint
            if sample_scores_by_checkpoint[label][sample_id]["present_backstop_score_db"] is not None
        ]
        if not available:
            continue
        best_value = max(float(value) for _, value in available)
        present_best_by_sample[sample_id] = [
            label
            for label, value in available
            if float(best_value - value) <= args.target_present_backstop_margin_db
        ]

    for row in checkpoint_rows:
        label = row["label"]
        row["absent_frontier_count"] = sum(1 for winners in absent_best_by_sample.values() if label in winners)
        row["present_backstop_count"] = sum(1 for winners in present_best_by_sample.values() if label in winners)

    baseline_label = args.present_guardrail_baseline
    baseline_scores = sample_scores_by_checkpoint.get(baseline_label)
    if baseline_scores is None:
        raise SystemExit(
            f"Present guardrail baseline '{baseline_label}' not found among ranked checkpoints."
        )

    for row in checkpoint_rows:
        label = row["label"]
        target_capture_regression_sample_ids: list[str] = []
        residual_increase_sample_ids: list[str] = []
        for sample_id in present_sample_ids:
            baseline_sample = baseline_scores[sample_id]
            candidate_sample = sample_scores_by_checkpoint[label][sample_id]
            baseline_target_capture_db = baseline_sample["target_capture_db"]
            candidate_target_capture_db = candidate_sample["target_capture_db"]
            if baseline_target_capture_db is not None and candidate_target_capture_db is not None:
                if float(baseline_target_capture_db - candidate_target_capture_db) > args.max_target_capture_regression_db:
                    target_capture_regression_sample_ids.append(sample_id)
            baseline_residual_share = baseline_sample["residual_output_share"]
            candidate_residual_share = candidate_sample["residual_output_share"]
            if float(candidate_residual_share - baseline_residual_share) > args.max_residual_share_increase:
                residual_increase_sample_ids.append(sample_id)
        total_guardrail_violations = len(set(target_capture_regression_sample_ids + residual_increase_sample_ids))
        row["present_guardrail_baseline_label"] = baseline_label
        row["target_capture_regression_sample_ids"] = target_capture_regression_sample_ids
        row["residual_increase_sample_ids"] = residual_increase_sample_ids
        row["present_guardrail_violation_count"] = total_guardrail_violations
        row["passes_present_guardrail"] = bool(total_guardrail_violations == 0)

    absent_rank = sorted(
        checkpoint_rows,
        key=lambda row: (
            -int(row["absent_frontier_count"]),
            float("inf")
            if row["absent_mean_interference_capture_db"] is None
            else float(row["absent_mean_interference_capture_db"]),
            float("inf")
            if row["absent_mean_rms_dbfs"] is None
            else float(row["absent_mean_rms_dbfs"]),
        ),
    )
    present_rank = sorted(
        checkpoint_rows,
        key=lambda row: (
            -int(row["present_backstop_count"]),
            float("inf")
            if row["present_mean_backstop_score_db"] is None
            else -float(row["present_mean_backstop_score_db"]),
        ),
    )
    combined_rank = sorted(
        checkpoint_rows,
        key=lambda row: (
            -int(row["absent_frontier_count"]),
            -int(row["present_backstop_count"]),
            float("inf")
            if row["absent_mean_interference_capture_db"] is None
            else float(row["absent_mean_interference_capture_db"]),
            float("inf")
            if row["present_mean_backstop_score_db"] is None
            else -float(row["present_mean_backstop_score_db"]),
        ),
    )
    guardrail_filtered_rank = sorted(
        checkpoint_rows,
        key=lambda row: (
            int(row["present_guardrail_violation_count"]),
            -int(row["absent_frontier_count"]),
            -int(row["present_backstop_count"]),
            float("inf")
            if row["absent_mean_interference_capture_db"] is None
            else float(row["absent_mean_interference_capture_db"]),
            float("inf")
            if row["present_mean_backstop_score_db"] is None
            else -float(row["present_mean_backstop_score_db"]),
        ),
    )

    output = {
        "manifest": serialize_repo_path(args.manifest),
        "num_checkpoints": len(checkpoint_rows),
        "sample_ids": [sample["sample_id"] for sample in sample_cache],
        "absent_sample_ids": absent_sample_ids,
        "present_sample_ids": present_sample_ids,
        "absent_near_tie_margin_db": args.absent_near_tie_margin_db,
        "target_present_backstop_margin_db": args.target_present_backstop_margin_db,
        "present_guardrail_baseline": baseline_label,
        "max_target_capture_regression_db": args.max_target_capture_regression_db,
        "max_residual_share_increase": args.max_residual_share_increase,
        "absent_best_by_sample": absent_best_by_sample,
        "present_best_by_sample": present_best_by_sample,
        "combined_rank": combined_rank[: args.top_k],
        "guardrail_filtered_rank": guardrail_filtered_rank[: args.top_k],
        "absent_rank": absent_rank[: args.top_k],
        "present_rank": present_rank[: args.top_k],
        "all_checkpoint_rows": checkpoint_rows,
        "per_sample_scores_by_checkpoint": sample_scores_by_checkpoint,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output_json": serialize_repo_path(args.output_json),
                "num_checkpoints": len(checkpoint_rows),
                "combined_top_labels": [row["label"] for row in combined_rank[: args.top_k]],
                "guardrail_filtered_top_labels": [row["label"] for row in guardrail_filtered_rank[: args.top_k]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
