from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEAK_SUFFIX = "_local_speech_leak_proxy_v1"
ARTIFACT_SUFFIX = "_hard_present_artifact_local_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Filter hard_present_artifact_local_proxy_v1 to the same base sample ids used by "
            "local_speech_leak_0007_like_proxy_v1, so speech-only leak and speech-plus-music "
            "artifact views can be paired inside one narrow 0007-like bundle."
        )
    )
    parser.add_argument("--input-train-manifest", type=Path, required=True)
    parser.add_argument("--input-val-manifest", type=Path, required=True)
    parser.add_argument("--paired-train-sample-ids", type=Path, required=True)
    parser.add_argument("--paired-val-sample-ids", type=Path, required=True)
    parser.add_argument("--output-train-manifest", type=Path, required=True)
    parser.add_argument("--output-val-manifest", type=Path, required=True)
    parser.add_argument("--output-train-sample-ids", type=Path, required=True)
    parser.add_argument("--output-val-sample-ids", type=Path, required=True)
    parser.add_argument("--output-all-sample-ids", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
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
            if line:
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


def load_sample_ids(path: Path) -> list[str]:
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def base_sample_id(sample_id: str, *, suffix: str) -> str:
    return re.sub(f"{re.escape(suffix)}$", "", sample_id)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {
            "selected_count": 0,
            "sample_ids": [],
            "recipe_counts": {},
            "selection_mode_counts": {},
        }
    energy_ratios = [float(row.get("target_energy_ratio", 0.0)) for row in rows]
    transient_shares = [float(row.get("target_transient_presence_share_mean", 0.0)) for row in rows]
    cosine_values = [float(row.get("target_interference_logspec_cosine", 0.0)) for row in rows]
    return {
        "selected_count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "recipe_counts": dict(sorted(Counter(str(row.get("recipe", "")) for row in rows).items())),
        "selection_mode_counts": dict(sorted(Counter(str(row.get("local_selection_mode", "")) for row in rows).items())),
        "target_energy_ratio_min": min(energy_ratios),
        "target_energy_ratio_max": max(energy_ratios),
        "target_transient_presence_share_mean_min": min(transient_shares),
        "target_transient_presence_share_mean_max": max(transient_shares),
        "target_interference_logspec_cosine_min": min(cosine_values),
        "target_interference_logspec_cosine_max": max(cosine_values),
    }


def filter_rows(rows: list[dict[str, Any]], paired_sample_ids: list[str]) -> list[dict[str, Any]]:
    paired_base_ids = {base_sample_id(sample_id, suffix=LEAK_SUFFIX) for sample_id in paired_sample_ids}
    output_rows = [
        row
        for row in rows
        if base_sample_id(str(row["sample_id"]), suffix=ARTIFACT_SUFFIX) in paired_base_ids
    ]
    output_rows.sort(key=lambda row: str(row["sample_id"]))
    return output_rows


def main() -> None:
    args = parse_args()

    train_rows = load_jsonl(args.input_train_manifest)
    val_rows = load_jsonl(args.input_val_manifest)
    paired_train_sample_ids = load_sample_ids(args.paired_train_sample_ids)
    paired_val_sample_ids = load_sample_ids(args.paired_val_sample_ids)

    output_train_rows = filter_rows(train_rows, paired_train_sample_ids)
    output_val_rows = filter_rows(val_rows, paired_val_sample_ids)
    output_all_rows = output_train_rows + output_val_rows

    write_jsonl(args.output_train_manifest, output_train_rows)
    write_jsonl(args.output_val_manifest, output_val_rows)
    write_sample_ids(args.output_train_sample_ids, output_train_rows)
    write_sample_ids(args.output_val_sample_ids, output_val_rows)
    write_sample_ids(args.output_all_sample_ids, output_all_rows)

    summary = {
        "input_train_manifest": serialize_repo_path(args.input_train_manifest),
        "input_val_manifest": serialize_repo_path(args.input_val_manifest),
        "paired_train_sample_ids": serialize_repo_path(args.paired_train_sample_ids),
        "paired_val_sample_ids": serialize_repo_path(args.paired_val_sample_ids),
        "output_train_manifest": serialize_repo_path(args.output_train_manifest),
        "output_val_manifest": serialize_repo_path(args.output_val_manifest),
        "output_train_sample_ids": serialize_repo_path(args.output_train_sample_ids),
        "output_val_sample_ids": serialize_repo_path(args.output_val_sample_ids),
        "output_all_sample_ids": serialize_repo_path(args.output_all_sample_ids),
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
