from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Filter local_speech_leak_proxy_v1 into a narrower 0007-like subset. "
            "The goal is to keep weak-target music-plus-speech hard-present windows "
            "without widening backstop coverage to the whole local proxy family."
        )
    )
    parser.add_argument("--input-train-manifest", type=Path, required=True)
    parser.add_argument("--input-val-manifest", type=Path, required=True)
    parser.add_argument("--output-train-manifest", type=Path, required=True)
    parser.add_argument("--output-val-manifest", type=Path, required=True)
    parser.add_argument("--output-train-sample-ids", type=Path, required=True)
    parser.add_argument("--output-val-sample-ids", type=Path, required=True)
    parser.add_argument("--output-all-sample-ids", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--min-local-music-share-of-interference", type=float, default=0.10)
    parser.add_argument("--max-local-fullmix-target-share", type=float, default=0.14)
    parser.add_argument("--max-target-energy-ratio", type=float, default=0.22)
    parser.add_argument("--min-target-transient-presence-share-mean", type=float, default=0.02)
    parser.add_argument("--max-target-transient-presence-share-mean", type=float, default=0.08)
    parser.add_argument("--min-target-interference-logspec-cosine", type=float, default=0.50)
    parser.add_argument(
        "--required-selection-mode",
        type=str,
        default="speech_target_share_bounded_peak",
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_sample_ids(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(f"{row['sample_id']}\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def keep_row(row: dict[str, Any], args: argparse.Namespace) -> bool:
    selection_mode = str(row.get("local_selection_mode", ""))
    if selection_mode != args.required_selection_mode:
        return False
    if float(row.get("local_music_share_of_interference", 0.0)) < args.min_local_music_share_of_interference:
        return False
    if float(row.get("local_fullmix_target_share", 1.0)) > args.max_local_fullmix_target_share:
        return False
    if float(row.get("target_energy_ratio", 1.0)) > args.max_target_energy_ratio:
        return False
    transient_share = float(row.get("target_transient_presence_share_mean", 0.0))
    if transient_share < args.min_target_transient_presence_share_mean:
        return False
    if transient_share > args.max_target_transient_presence_share_mean:
        return False
    if float(row.get("target_interference_logspec_cosine", 0.0)) < args.min_target_interference_logspec_cosine:
        return False
    return True


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "selected_count": 0,
            "sample_ids": [],
            "recipe_counts": {},
            "selection_mode_counts": {},
        }
    music_shares = [float(row["local_music_share_of_interference"]) for row in rows]
    target_shares = [float(row["local_fullmix_target_share"]) for row in rows]
    energy_ratios = [float(row["target_energy_ratio"]) for row in rows]
    transient_shares = [float(row["target_transient_presence_share_mean"]) for row in rows]
    cosine_values = [float(row["target_interference_logspec_cosine"]) for row in rows]
    return {
        "selected_count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "recipe_counts": dict(sorted(Counter(str(row.get("recipe", "")) for row in rows).items())),
        "selection_mode_counts": dict(sorted(Counter(str(row.get("local_selection_mode", "")) for row in rows).items())),
        "local_music_share_of_interference_min": min(music_shares),
        "local_music_share_of_interference_max": max(music_shares),
        "local_fullmix_target_share_min": min(target_shares),
        "local_fullmix_target_share_max": max(target_shares),
        "target_energy_ratio_min": min(energy_ratios),
        "target_energy_ratio_max": max(energy_ratios),
        "target_transient_presence_share_mean_min": min(transient_shares),
        "target_transient_presence_share_mean_max": max(transient_shares),
        "target_interference_logspec_cosine_min": min(cosine_values),
        "target_interference_logspec_cosine_max": max(cosine_values),
    }


def main() -> None:
    args = parse_args()
    train_rows = load_jsonl(args.input_train_manifest)
    val_rows = load_jsonl(args.input_val_manifest)

    output_train_rows = [row for row in train_rows if keep_row(row, args)]
    output_val_rows = [row for row in val_rows if keep_row(row, args)]
    output_all_rows = output_train_rows + output_val_rows

    write_jsonl(args.output_train_manifest, output_train_rows)
    write_jsonl(args.output_val_manifest, output_val_rows)
    write_sample_ids(args.output_train_sample_ids, output_train_rows)
    write_sample_ids(args.output_val_sample_ids, output_val_rows)
    write_sample_ids(args.output_all_sample_ids, output_all_rows)

    summary = {
        "input_train_manifest": serialize_repo_path(args.input_train_manifest),
        "input_val_manifest": serialize_repo_path(args.input_val_manifest),
        "output_train_manifest": serialize_repo_path(args.output_train_manifest),
        "output_val_manifest": serialize_repo_path(args.output_val_manifest),
        "output_train_sample_ids": serialize_repo_path(args.output_train_sample_ids),
        "output_val_sample_ids": serialize_repo_path(args.output_val_sample_ids),
        "output_all_sample_ids": serialize_repo_path(args.output_all_sample_ids),
        "criteria": {
            "required_selection_mode": args.required_selection_mode,
            "min_local_music_share_of_interference": args.min_local_music_share_of_interference,
            "max_local_fullmix_target_share": args.max_local_fullmix_target_share,
            "max_target_energy_ratio": args.max_target_energy_ratio,
            "min_target_transient_presence_share_mean": args.min_target_transient_presence_share_mean,
            "max_target_transient_presence_share_mean": args.max_target_transient_presence_share_mean,
            "min_target_interference_logspec_cosine": args.min_target_interference_logspec_cosine,
        },
        "train": summarize(output_train_rows),
        "val": summarize(output_val_rows),
        "all": summarize(output_all_rows),
    }
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
