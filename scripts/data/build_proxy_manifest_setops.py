from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build focused proxy manifests by applying set operations on sample_id between two proxy manifest pairs."
        )
    )
    parser.add_argument("--left-train-manifest", type=Path, required=True)
    parser.add_argument("--left-val-manifest", type=Path, required=True)
    parser.add_argument("--right-train-manifest", type=Path, required=True)
    parser.add_argument("--right-val-manifest", type=Path, required=True)
    parser.add_argument(
        "--operation",
        choices=["intersection", "left_minus_right"],
        required=True,
    )
    parser.add_argument("--output-train-manifest", type=Path, required=True)
    parser.add_argument("--output-val-manifest", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    return parser.parse_args()


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
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


def rows_by_sample_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for row in rows:
        sample_id = str(row["sample_id"])
        if sample_id in mapping:
            raise ValueError(f"Duplicate sample_id in manifest: {sample_id}")
        mapping[sample_id] = row
    return mapping


def apply_operation(
    left_rows: list[dict[str, Any]],
    right_rows: list[dict[str, Any]],
    operation: str,
) -> tuple[list[dict[str, Any]], list[str]]:
    left_map = rows_by_sample_id(left_rows)
    right_ids = set(rows_by_sample_id(right_rows))
    if operation == "intersection":
        keep_ids = sorted(sample_id for sample_id in left_map if sample_id in right_ids)
    elif operation == "left_minus_right":
        keep_ids = sorted(sample_id for sample_id in left_map if sample_id not in right_ids)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
    return [left_map[sample_id] for sample_id in keep_ids], keep_ids


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
    }


def main() -> None:
    args = parse_args()

    left_train_rows = load_jsonl(args.left_train_manifest)
    left_val_rows = load_jsonl(args.left_val_manifest)
    right_train_rows = load_jsonl(args.right_train_manifest)
    right_val_rows = load_jsonl(args.right_val_manifest)

    output_train_rows, output_train_ids = apply_operation(left_train_rows, right_train_rows, args.operation)
    output_val_rows, output_val_ids = apply_operation(left_val_rows, right_val_rows, args.operation)

    write_jsonl(args.output_train_manifest, output_train_rows)
    write_jsonl(args.output_val_manifest, output_val_rows)

    summary = {
        "left_train_manifest": serialize_repo_path(args.left_train_manifest),
        "left_val_manifest": serialize_repo_path(args.left_val_manifest),
        "right_train_manifest": serialize_repo_path(args.right_train_manifest),
        "right_val_manifest": serialize_repo_path(args.right_val_manifest),
        "operation": args.operation,
        "output_train_manifest": serialize_repo_path(args.output_train_manifest),
        "output_val_manifest": serialize_repo_path(args.output_val_manifest),
        "output_train": summarize_rows(output_train_rows),
        "output_val": summarize_rows(output_val_rows),
        "output_all_sample_ids": output_train_ids + output_val_ids,
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
