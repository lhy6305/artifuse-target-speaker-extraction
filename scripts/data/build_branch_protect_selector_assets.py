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
            "Build branch-protect selector sample-id files from focused proxy manifests, "
            "with optional subtraction against an existing selector and optional union back into base manifests."
        )
    )
    parser.add_argument("--focus-train-manifest", type=Path, required=True)
    parser.add_argument("--focus-val-manifest", type=Path, required=True)
    parser.add_argument("--output-sample-ids-prefix", type=Path, required=True)
    parser.add_argument(
        "--subtract-sample-ids-file",
        type=Path,
        default=None,
        help="Optional newline-delimited sample_id file to subtract before writing outputs.",
    )
    parser.add_argument("--base-train-manifest", type=Path, default=None)
    parser.add_argument("--base-val-manifest", type=Path, default=None)
    parser.add_argument("--output-train-manifest", type=Path, default=None)
    parser.add_argument("--output-val-manifest", type=Path, default=None)
    parser.add_argument("--summary-json", type=Path, default=None)
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_sample_ids(path: Path | None) -> set[str]:
    if path is None:
        return set()
    sample_ids: set[str] = set()
    with path.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            value = line.strip()
            if value:
                sample_ids.add(value)
    return sample_ids


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def write_sample_ids(path: Path, sample_ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for sample_id in sample_ids:
            fh.write(sample_id + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    recipe_counts = Counter(str(row.get("recipe", "")) for row in rows)
    pattern_counts = Counter(str(row.get("temporal_pattern", "target_full")) for row in rows)
    split_counts = Counter(str(row.get("split", "")) for row in rows)
    return {
        "count": len(rows),
        "recipe_counts": dict(sorted(recipe_counts.items())),
        "temporal_pattern_counts": dict(sorted(pattern_counts.items())),
        "split_counts": dict(sorted(split_counts.items())),
    }


def filter_rows(rows: list[dict[str, Any]], subtract_ids: set[str]) -> list[dict[str, Any]]:
    filtered = [row for row in rows if str(row.get("sample_id", "")) not in subtract_ids]
    filtered.sort(key=lambda row: str(row.get("sample_id", "")))
    return filtered


def merge_rows(base_rows: list[dict[str, Any]], extra_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged_by_id: dict[str, dict[str, Any]] = {}
    for row in base_rows:
        merged_by_id[str(row.get("sample_id", ""))] = row
    for row in extra_rows:
        merged_by_id[str(row.get("sample_id", ""))] = row
    return [merged_by_id[sample_id] for sample_id in sorted(merged_by_id)]


def main() -> None:
    args = parse_args()

    if (args.base_train_manifest is None) != (args.base_val_manifest is None):
        raise ValueError("Base train/val manifests must be provided together.")
    if (args.output_train_manifest is None) != (args.output_val_manifest is None):
        raise ValueError("Output train/val manifests must be provided together.")
    if (args.base_train_manifest is None) != (args.output_train_manifest is None):
        raise ValueError("Base manifests and output manifests must either both be set or both be omitted.")

    focus_train_rows = load_jsonl(args.focus_train_manifest)
    focus_val_rows = load_jsonl(args.focus_val_manifest)
    subtract_ids = load_sample_ids(args.subtract_sample_ids_file)

    selected_train_rows = filter_rows(focus_train_rows, subtract_ids)
    selected_val_rows = filter_rows(focus_val_rows, subtract_ids)
    selected_train_ids = [str(row["sample_id"]) for row in selected_train_rows]
    selected_val_ids = [str(row["sample_id"]) for row in selected_val_rows]
    selected_all_ids = selected_train_ids + selected_val_ids

    prefix = args.output_sample_ids_prefix
    write_sample_ids(prefix.with_name(prefix.name + "_train.txt"), selected_train_ids)
    write_sample_ids(prefix.with_name(prefix.name + "_val.txt"), selected_val_ids)
    write_sample_ids(prefix.with_name(prefix.name + "_all.txt"), selected_all_ids)

    merged_train_summary: dict[str, Any] | None = None
    merged_val_summary: dict[str, Any] | None = None
    if args.base_train_manifest is not None:
        base_train_rows = load_jsonl(args.base_train_manifest)
        base_val_rows = load_jsonl(args.base_val_manifest)
        merged_train_rows = merge_rows(base_train_rows, selected_train_rows)
        merged_val_rows = merge_rows(base_val_rows, selected_val_rows)
        write_jsonl(args.output_train_manifest, merged_train_rows)
        write_jsonl(args.output_val_manifest, merged_val_rows)
        merged_train_summary = summarize_rows(merged_train_rows)
        merged_val_summary = summarize_rows(merged_val_rows)

    summary = {
        "focus_train_manifest": serialize_repo_path(args.focus_train_manifest),
        "focus_val_manifest": serialize_repo_path(args.focus_val_manifest),
        "subtract_sample_ids_file": serialize_repo_path(args.subtract_sample_ids_file),
        "output_sample_ids_prefix": serialize_repo_path(args.output_sample_ids_prefix),
        "selected_train_ids": selected_train_ids,
        "selected_val_ids": selected_val_ids,
        "selected_all_ids": selected_all_ids,
        "selected_train_summary": summarize_rows(selected_train_rows),
        "selected_val_summary": summarize_rows(selected_val_rows),
        "subtracted_ids_count": len(subtract_ids),
        "subtracted_overlap_with_focus_train": sorted(
            str(row["sample_id"]) for row in focus_train_rows if str(row.get("sample_id", "")) in subtract_ids
        ),
        "subtracted_overlap_with_focus_val": sorted(
            str(row["sample_id"]) for row in focus_val_rows if str(row.get("sample_id", "")) in subtract_ids
        ),
        "base_train_manifest": serialize_repo_path(args.base_train_manifest),
        "base_val_manifest": serialize_repo_path(args.base_val_manifest),
        "output_train_manifest": serialize_repo_path(args.output_train_manifest),
        "output_val_manifest": serialize_repo_path(args.output_val_manifest),
        "merged_train_summary": merged_train_summary,
        "merged_val_summary": merged_val_summary,
    }

    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        with args.summary_json.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
