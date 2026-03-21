from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Bucket shared compare rows according to pass/fail status on two named ordering constraints, "
            "and optionally materialize each bucket as train/val manifests plus sample-id files."
        )
    )
    parser.add_argument(
        "--compare",
        action="append",
        required=True,
        help="Compare jsonl mapping in the form alias=path/to/per_sample_metrics.jsonl.",
    )
    parser.add_argument("--manifest-jsonl", type=Path, required=True)
    parser.add_argument("--constraint-a", type=str, required=True)
    parser.add_argument("--constraint-b", type=str, required=True)
    parser.add_argument("--numeric-field", action="append", default=[])
    parser.add_argument(
        "--output-name-prefix",
        type=str,
        default=None,
        help="When set, write bucket manifests and sample-id files into data/synthetic using this name prefix.",
    )
    parser.add_argument("--output-summary-json", type=Path, required=True)
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
            fh.write(json.dumps(row, ensure_ascii=False))
            fh.write("\n")


def write_sample_ids(path: Path, sample_ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for sample_id in sample_ids:
            fh.write(sample_id)
            fh.write("\n")


def parse_mapping(values: list[str]) -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --compare value: {value!r}")
        alias, raw_path = value.split("=", 1)
        alias = alias.strip()
        path = Path(raw_path.strip())
        if not alias:
            raise ValueError(f"Empty alias in --compare value: {value!r}")
        if alias in mappings:
            raise ValueError(f"Duplicate alias in --compare values: {alias}")
        mappings[alias] = path
    return mappings


def parse_constraint(value: str) -> tuple[str, str]:
    if ">" not in value:
        raise ValueError(f"Invalid constraint value: {value!r}")
    higher_alias, lower_alias = value.split(">", 1)
    higher_alias = higher_alias.strip()
    lower_alias = lower_alias.strip()
    if not higher_alias or not lower_alias:
        raise ValueError(f"Invalid constraint value: {value!r}")
    return higher_alias, lower_alias


def summarize_numeric(rows: list[dict[str, Any]], numeric_fields: list[str]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for field in numeric_fields:
        values = [float(row[field]) for row in rows if row.get(field) is not None]
        if not values:
            continue
        output[field] = {
            "count": len(values),
            "mean": float(mean(values)),
            "min": float(min(values)),
            "max": float(max(values)),
        }
    return output


def bucket_name(constraint_a_pass: bool, constraint_b_pass: bool) -> str:
    if constraint_a_pass and constraint_b_pass:
        return "pass_both"
    if not constraint_a_pass and constraint_b_pass:
        return "fail_a_only"
    if constraint_a_pass and not constraint_b_pass:
        return "fail_b_only"
    return "fail_both"


def project_row(
    manifest_row: dict[str, Any],
    bucket: str,
    constraint_a_name: str,
    constraint_a_gap_db: float,
    constraint_a_pass: bool,
    constraint_b_name: str,
    constraint_b_gap_db: float,
    constraint_b_pass: bool,
) -> dict[str, Any]:
    return {
        "sample_id": str(manifest_row["sample_id"]),
        "split": manifest_row.get("split"),
        "recipe": manifest_row.get("recipe"),
        "temporal_pattern": manifest_row.get("temporal_pattern"),
        "target_present_ratio": manifest_row.get("target_present_ratio"),
        "metadata_path": manifest_row.get("metadata_path"),
        "bucket": bucket,
        "constraint_status": {
            constraint_a_name: {
                "gap_db": float(constraint_a_gap_db),
                "pass": bool(constraint_a_pass),
            },
            constraint_b_name: {
                "gap_db": float(constraint_b_gap_db),
                "pass": bool(constraint_b_pass),
            },
        },
    }


def main() -> None:
    args = parse_args()
    compare_map = parse_mapping(args.compare)
    constraint_a = parse_constraint(args.constraint_a)
    constraint_b = parse_constraint(args.constraint_b)

    needed_aliases = sorted(set(constraint_a + constraint_b))
    missing_aliases = [alias for alias in needed_aliases if alias not in compare_map]
    if missing_aliases:
        raise ValueError(f"Constraint aliases missing compare inputs: {missing_aliases}")

    manifest_rows = load_jsonl(args.manifest_jsonl)
    manifest_by_id = {str(row["sample_id"]): row for row in manifest_rows}

    rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    shared_sample_ids: set[str] | None = None
    for alias, path in compare_map.items():
        rows = {str(row["sample_id"]): row for row in load_jsonl(path)}
        rows_by_alias[alias] = rows
        sample_ids = set(rows)
        shared_sample_ids = sample_ids if shared_sample_ids is None else (shared_sample_ids & sample_ids)

    if not shared_sample_ids:
        raise RuntimeError("No shared sample ids across compare inputs.")

    bucket_rows: dict[str, list[dict[str, Any]]] = {
        "pass_both": [],
        "fail_a_only": [],
        "fail_b_only": [],
        "fail_both": [],
    }
    bucket_manifest_rows: dict[str, list[dict[str, Any]]] = {key: [] for key in bucket_rows}

    for sample_id in sorted(shared_sample_ids):
        manifest_row = manifest_by_id.get(sample_id)
        if manifest_row is None:
            continue

        higher_a, lower_a = constraint_a
        higher_b, lower_b = constraint_b
        gap_a = float(rows_by_alias[higher_a][sample_id]["sisdr_b_db"] - rows_by_alias[lower_a][sample_id]["sisdr_b_db"])
        gap_b = float(rows_by_alias[higher_b][sample_id]["sisdr_b_db"] - rows_by_alias[lower_b][sample_id]["sisdr_b_db"])
        pass_a = gap_a > 0.0
        pass_b = gap_b > 0.0
        bucket = bucket_name(pass_a, pass_b)

        bucket_rows[bucket].append(
            project_row(
                manifest_row=manifest_row,
                bucket=bucket,
                constraint_a_name=args.constraint_a,
                constraint_a_gap_db=gap_a,
                constraint_a_pass=pass_a,
                constraint_b_name=args.constraint_b,
                constraint_b_gap_db=gap_b,
                constraint_b_pass=pass_b,
            )
        )
        bucket_manifest_rows[bucket].append(manifest_row)

    bucket_summaries: dict[str, Any] = {}
    materialized_paths: dict[str, Any] = {}
    for bucket, rows in bucket_rows.items():
        split_counts = Counter(str(row.get("split")) for row in rows)
        recipe_counts = Counter(str(row.get("recipe")) for row in rows)
        pattern_counts = Counter(str(row.get("temporal_pattern")) for row in rows)
        sample_ids = [str(row["sample_id"]) for row in rows]
        bucket_summaries[bucket] = {
            "count": len(rows),
            "sample_ids": sample_ids,
            "split_counts": dict(sorted(split_counts.items())),
            "recipe_counts": dict(sorted(recipe_counts.items())),
            "pattern_counts": dict(sorted(pattern_counts.items())),
            "constraint_a_gap_avg_db": float(mean(row["constraint_status"][args.constraint_a]["gap_db"] for row in rows))
            if rows
            else None,
            "constraint_b_gap_avg_db": float(mean(row["constraint_status"][args.constraint_b]["gap_db"] for row in rows))
            if rows
            else None,
            "numeric_field_stats": summarize_numeric(bucket_manifest_rows[bucket], list(args.numeric_field)),
        }

        if args.output_name_prefix is None:
            continue

        train_rows = [row for row in bucket_manifest_rows[bucket] if str(row.get("split")) == "train"]
        val_rows = [row for row in bucket_manifest_rows[bucket] if str(row.get("split")) == "val"]
        all_rows = train_rows + val_rows
        train_ids = [str(row["sample_id"]) for row in train_rows]
        val_ids = [str(row["sample_id"]) for row in val_rows]
        all_ids = train_ids + val_ids

        prefix = args.output_name_prefix + "_" + bucket
        train_manifest_path = ROOT / "data" / "synthetic" / f"train_manifest_{prefix}.jsonl"
        val_manifest_path = ROOT / "data" / "synthetic" / f"val_manifest_{prefix}.jsonl"
        all_manifest_path = ROOT / "data" / "synthetic" / f"manifest_{prefix}_all.jsonl"
        train_ids_path = ROOT / "data" / "synthetic" / f"sample_ids_{prefix}_train.txt"
        val_ids_path = ROOT / "data" / "synthetic" / f"sample_ids_{prefix}_val.txt"
        all_ids_path = ROOT / "data" / "synthetic" / f"sample_ids_{prefix}_all.txt"

        write_jsonl(train_manifest_path, train_rows)
        write_jsonl(val_manifest_path, val_rows)
        write_jsonl(all_manifest_path, all_rows)
        write_sample_ids(train_ids_path, train_ids)
        write_sample_ids(val_ids_path, val_ids)
        write_sample_ids(all_ids_path, all_ids)

        materialized_paths[bucket] = {
            "train_manifest": serialize_repo_path(train_manifest_path),
            "val_manifest": serialize_repo_path(val_manifest_path),
            "all_manifest": serialize_repo_path(all_manifest_path),
            "train_sample_ids": serialize_repo_path(train_ids_path),
            "val_sample_ids": serialize_repo_path(val_ids_path),
            "all_sample_ids": serialize_repo_path(all_ids_path),
        }

    output = {
        "manifest_jsonl": serialize_repo_path(args.manifest_jsonl),
        "compares": {alias: serialize_repo_path(path) for alias, path in compare_map.items()},
        "constraint_a": args.constraint_a,
        "constraint_b": args.constraint_b,
        "numeric_fields": list(args.numeric_field),
        "output_name_prefix": args.output_name_prefix,
        "num_manifest_rows": len(manifest_rows),
        "num_shared_compare_rows": len(shared_sample_ids),
        "bucket_summaries": bucket_summaries,
        "materialized_paths": materialized_paths,
    }

    args.output_summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_summary_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output_summary_json": serialize_repo_path(args.output_summary_json),
                "bucket_counts": {bucket: summary["count"] for bucket, summary in bucket_summaries.items()},
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
