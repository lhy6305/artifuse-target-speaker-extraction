from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split focused proxy manifests into matched and kept subsets using an all-of list of numeric conditions, "
            "and write both manifests plus sample-id assets."
        )
    )
    parser.add_argument("--train-manifest", type=Path, required=True)
    parser.add_argument("--val-manifest", type=Path, required=True)
    parser.add_argument(
        "--condition",
        action="append",
        required=True,
        help="Numeric condition in the form field<=value, field<value, field>=value, field>value, or field==value.",
    )
    parser.add_argument("--keep-train-manifest", type=Path, required=True)
    parser.add_argument("--keep-val-manifest", type=Path, required=True)
    parser.add_argument("--keep-sample-ids-prefix", type=Path, required=True)
    parser.add_argument("--match-train-manifest", type=Path, required=True)
    parser.add_argument("--match-val-manifest", type=Path, required=True)
    parser.add_argument("--match-sample-ids-prefix", type=Path, required=True)
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


def write_sample_ids(prefix: Path, rows: list[dict[str, Any]]) -> None:
    sample_ids = [str(row["sample_id"]) for row in rows]
    prefix.parent.mkdir(parents=True, exist_ok=True)
    output_path = prefix
    with output_path.open("w", encoding="utf-8", newline="\n") as fh:
        for sample_id in sample_ids:
            fh.write(sample_id + "\n")


def write_split_sample_id_files(prefix: Path, train_rows: list[dict[str, Any]], val_rows: list[dict[str, Any]]) -> None:
    write_sample_ids(prefix.with_name(prefix.name + "_train.txt"), train_rows)
    write_sample_ids(prefix.with_name(prefix.name + "_val.txt"), val_rows)
    write_sample_ids(prefix.with_name(prefix.name + "_all.txt"), train_rows + val_rows)


def parse_condition(text: str) -> tuple[str, str, float]:
    for operator in ("<=", ">=", "==", "<", ">"):
        if operator in text:
            field, raw_value = text.split(operator, 1)
            field = field.strip()
            raw_value = raw_value.strip()
            if not field or not raw_value:
                raise ValueError(f"Invalid --condition value: {text!r}")
            return field, operator, float(raw_value)
    raise ValueError(f"Invalid --condition value: {text!r}")


def condition_pass(value: float, operator: str, threshold: float) -> bool:
    if operator == "<=":
        return value <= threshold
    if operator == "<":
        return value < threshold
    if operator == ">=":
        return value >= threshold
    if operator == ">":
        return value > threshold
    if operator == "==":
        return value == threshold
    raise ValueError(f"Unsupported operator: {operator}")


def row_matches(row: dict[str, Any], conditions: list[tuple[str, str, float]]) -> bool:
    for field, operator, threshold in conditions:
        raw_value = row.get(field)
        if raw_value is None:
            return False
        if not condition_pass(float(raw_value), operator, threshold):
            return False
    return True


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
    }


def split_rows(
    rows: list[dict[str, Any]],
    conditions: list[tuple[str, str, float]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    matched: list[dict[str, Any]] = []
    kept: list[dict[str, Any]] = []
    for row in rows:
        if row_matches(row, conditions):
            matched.append(row)
        else:
            kept.append(row)
    matched.sort(key=lambda row: str(row["sample_id"]))
    kept.sort(key=lambda row: str(row["sample_id"]))
    return matched, kept


def main() -> None:
    args = parse_args()
    conditions = [parse_condition(text) for text in args.condition]

    train_rows = load_jsonl(args.train_manifest)
    val_rows = load_jsonl(args.val_manifest)

    matched_train_rows, kept_train_rows = split_rows(train_rows, conditions)
    matched_val_rows, kept_val_rows = split_rows(val_rows, conditions)

    write_jsonl(args.keep_train_manifest, kept_train_rows)
    write_jsonl(args.keep_val_manifest, kept_val_rows)
    write_jsonl(args.match_train_manifest, matched_train_rows)
    write_jsonl(args.match_val_manifest, matched_val_rows)
    write_split_sample_id_files(args.keep_sample_ids_prefix, kept_train_rows, kept_val_rows)
    write_split_sample_id_files(args.match_sample_ids_prefix, matched_train_rows, matched_val_rows)

    summary = {
        "train_manifest": serialize_repo_path(args.train_manifest),
        "val_manifest": serialize_repo_path(args.val_manifest),
        "conditions": [
            {
                "field": field,
                "operator": operator,
                "threshold": threshold,
            }
            for field, operator, threshold in conditions
        ],
        "keep_train_manifest": serialize_repo_path(args.keep_train_manifest),
        "keep_val_manifest": serialize_repo_path(args.keep_val_manifest),
        "keep_sample_ids_prefix": serialize_repo_path(args.keep_sample_ids_prefix),
        "match_train_manifest": serialize_repo_path(args.match_train_manifest),
        "match_val_manifest": serialize_repo_path(args.match_val_manifest),
        "match_sample_ids_prefix": serialize_repo_path(args.match_sample_ids_prefix),
        "kept_train": summarize_rows(kept_train_rows),
        "kept_val": summarize_rows(kept_val_rows),
        "matched_train": summarize_rows(matched_train_rows),
        "matched_val": summarize_rows(matched_val_rows),
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
