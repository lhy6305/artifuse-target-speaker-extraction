from __future__ import annotations

import argparse
import json
import pickle
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import torch


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.data.synthetic_dataset import SyntheticTSEDataset
from tse_prefix.models import STFTMaskBaseline
from tse_prefix.pipeline import masked_sisdr


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compare two checkpoints on the same synthetic manifest and export grouped delta analysis."
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "val_manifest.jsonl",
    )
    parser.add_argument("--checkpoint-a", type=Path, required=True)
    parser.add_argument("--checkpoint-b", type=Path, required=True)
    parser.add_argument("--label-a", type=str, default="model_a")
    parser.add_argument("--label-b", type=str, default="model_b")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument(
        "--focus-recipes",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "--delta-threshold-db",
        type=float,
        default=0.1,
        help="Threshold above which a sample counts as a meaningful SI-SDR improvement/regression.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=12,
    )
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_checkpoint(path: Path, device: torch.device) -> dict:
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


def target_present_ratio_bucket(ratio: float) -> str:
    if ratio < 0.6:
        return "ratio_lt_0.6"
    if ratio < 0.8:
        return "ratio_0.6_0.8"
    if ratio < 0.95:
        return "ratio_0.8_0.95"
    return "ratio_ge_0.95"


def waveform_l1(prediction: torch.Tensor, target: torch.Tensor) -> float:
    return float(torch.mean(torch.abs(prediction - target)).item())


def summarize_group(rows: list[dict[str, Any]], delta_threshold_db: float) -> dict[str, Any]:
    count = len(rows)
    if count == 0:
        return {
            "count": 0,
            "avg_sisdr_db_a": 0.0,
            "avg_sisdr_db_b": 0.0,
            "avg_sisdr_delta_db": 0.0,
            "avg_waveform_l1_a": 0.0,
            "avg_waveform_l1_b": 0.0,
            "avg_waveform_l1_delta": 0.0,
            "improved_count": 0,
            "regressed_count": 0,
            "near_tie_count": 0,
        }
    improved_count = sum(1 for row in rows if row["sisdr_delta_db"] > delta_threshold_db)
    regressed_count = sum(1 for row in rows if row["sisdr_delta_db"] < -delta_threshold_db)
    return {
        "count": count,
        "avg_sisdr_db_a": sum(row["sisdr_a_db"] for row in rows) / count,
        "avg_sisdr_db_b": sum(row["sisdr_b_db"] for row in rows) / count,
        "avg_sisdr_delta_db": sum(row["sisdr_delta_db"] for row in rows) / count,
        "avg_waveform_l1_a": sum(row["waveform_l1_a"] for row in rows) / count,
        "avg_waveform_l1_b": sum(row["waveform_l1_b"] for row in rows) / count,
        "avg_waveform_l1_delta": sum(row["waveform_l1_delta"] for row in rows) / count,
        "improved_count": improved_count,
        "regressed_count": regressed_count,
        "near_tie_count": count - improved_count - regressed_count,
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    focus_recipes = set(args.focus_recipes)

    dataset = SyntheticTSEDataset(args.manifest, sample_rate=args.sample_rate)
    model_a, model_config_a, loss_config_a = build_model(args.checkpoint_a, device)
    model_b, model_config_b, loss_config_b = build_model(args.checkpoint_b, device)

    rows: list[dict[str, Any]] = []
    recipe_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    pattern_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    ratio_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    with torch.no_grad():
        for item in dataset:
            if focus_recipes and item["recipe"] not in focus_recipes:
                continue

            mixture = item["mixture"].unsqueeze(0).to(device)
            target = item["target"].unsqueeze(0).to(device)
            reference = item["reference"].unsqueeze(0).to(device)
            mixture_lengths = torch.tensor([item["mixture"].shape[-1]], dtype=torch.long, device=device)
            target_lengths = torch.tensor([item["target"].shape[-1]], dtype=torch.long, device=device)
            reference_lengths = torch.tensor([item["reference"].shape[-1]], dtype=torch.long, device=device)

            estimate_a = model_a(
                mixture=mixture,
                mixture_lengths=mixture_lengths,
                reference=reference,
                reference_lengths=reference_lengths,
            )["estimated_waveform"]
            estimate_b = model_b(
                mixture=mixture,
                mixture_lengths=mixture_lengths,
                reference=reference,
                reference_lengths=reference_lengths,
            )["estimated_waveform"]

            common_length = min(int(estimate_a.shape[-1]), int(target.shape[-1]), int(estimate_b.shape[-1]))
            clipped_length = torch.tensor([common_length], dtype=torch.long, device=device)
            clipped_target = target[..., :common_length]
            clipped_a = estimate_a[..., :common_length]
            clipped_b = estimate_b[..., :common_length]

            sisdr_a = float(masked_sisdr(clipped_a, clipped_target, clipped_length).item())
            sisdr_b = float(masked_sisdr(clipped_b, clipped_target, clipped_length).item())
            wave_l1_a = waveform_l1(clipped_a, clipped_target)
            wave_l1_b = waveform_l1(clipped_b, clipped_target)

            row = {
                "sample_id": item["sample_id"],
                "recipe": item["recipe"],
                "temporal_pattern": item["temporal_pattern"],
                "target_present_ratio": float(item["target_present_ratio"]),
                "target_present_ratio_bucket": target_present_ratio_bucket(float(item["target_present_ratio"])),
                "metadata_path": item["metadata_path"],
                "sisdr_a_db": sisdr_a,
                "sisdr_b_db": sisdr_b,
                "sisdr_delta_db": sisdr_b - sisdr_a,
                "waveform_l1_a": wave_l1_a,
                "waveform_l1_b": wave_l1_b,
                "waveform_l1_delta": wave_l1_b - wave_l1_a,
            }
            rows.append(row)
            recipe_groups[row["recipe"]].append(row)
            pattern_groups[row["temporal_pattern"]].append(row)
            ratio_groups[row["target_present_ratio_bucket"]].append(row)

    rows_sorted_improve = sorted(rows, key=lambda row: row["sisdr_delta_db"], reverse=True)
    rows_sorted_regress = list(reversed(rows_sorted_improve))
    rows_sorted_tie = sorted(rows, key=lambda row: abs(row["sisdr_delta_db"]))

    summary = {
        "manifest": serialize_repo_path(args.manifest),
        "checkpoint_a": serialize_repo_path(args.checkpoint_a),
        "checkpoint_b": serialize_repo_path(args.checkpoint_b),
        "label_a": args.label_a,
        "label_b": args.label_b,
        "focus_recipes": sorted(focus_recipes),
        "delta_threshold_db": args.delta_threshold_db,
        "num_samples": len(rows),
        "overall": summarize_group(rows, args.delta_threshold_db),
        "recipe_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(recipe_groups.items())
        },
        "pattern_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(pattern_groups.items())
        },
        "target_present_ratio_bucket_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(ratio_groups.items())
        },
        "top_improvements": rows_sorted_improve[: args.top_k],
        "top_regressions": rows_sorted_regress[: args.top_k],
        "top_near_ties": rows_sorted_tie[: args.top_k],
        "model_config_a": model_config_a,
        "model_config_b": model_config_b,
        "loss_config_a": loss_config_a,
        "loss_config_b": loss_config_b,
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (args.output_dir / "per_sample_metrics.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows_sorted_improve),
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "num_samples": len(rows),
                "avg_sisdr_delta_db": summary["overall"]["avg_sisdr_delta_db"],
                "improved_count": summary["overall"]["improved_count"],
                "regressed_count": summary["overall"]["regressed_count"],
                "output_dir": serialize_repo_path(args.output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
