from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze how a seed proxy family might expand by ranking non-seed rows according to "
            "their metadata/constraint similarity to the seed center and by evaluating seed+1 aggregate expansions."
        )
    )
    parser.add_argument(
        "--compare",
        action="append",
        required=True,
        help="Compare jsonl mapping in the form alias=path/to/per_sample_metrics.jsonl.",
    )
    parser.add_argument("--manifest-jsonl", type=Path, required=True)
    parser.add_argument("--focus-alias", type=str, required=True)
    parser.add_argument("--reference-alias", type=str, required=True)
    parser.add_argument("--ordered-aliases", nargs="+", required=True)
    parser.add_argument(
        "--extra-order-constraint",
        action="append",
        default=[],
        help="Additional ordering constraint in the form higher>lower.",
    )
    parser.add_argument("--seed-sample-ids-file", type=Path, required=True)
    parser.add_argument("--numeric-field", action="append", default=[])
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--output-json", type=Path, required=True)
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


def load_sample_ids(path: Path) -> list[str]:
    sample_ids: list[str] = []
    with path.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            value = line.strip()
            if value:
                sample_ids.append(value)
    return sample_ids


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


def parse_constraints(values: list[str]) -> list[tuple[str, str]]:
    constraints: list[tuple[str, str]] = []
    for value in values:
        if ">" not in value:
            raise ValueError(f"Invalid constraint value: {value!r}")
        higher_alias, lower_alias = value.split(">", 1)
        higher_alias = higher_alias.strip()
        lower_alias = lower_alias.strip()
        if not higher_alias or not lower_alias:
            raise ValueError(f"Invalid constraint value: {value!r}")
        constraints.append((higher_alias, lower_alias))
    return constraints


def build_constraint_rows(
    scores: dict[str, float],
    constraints: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for higher_alias, lower_alias in constraints:
        gap = float(scores[higher_alias] - scores[lower_alias])
        rows.append(
            {
                "constraint": f"{higher_alias}>{lower_alias}",
                "gap_db": gap,
                "pass": gap > 0.0,
            }
        )
    return rows


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(mean(values))


def numeric_stats(values: list[float]) -> dict[str, float] | None:
    if not values:
        return None
    return {
        "count": len(values),
        "mean": float(mean(values)),
        "min": float(min(values)),
        "max": float(max(values)),
    }


def summarize_rows(rows: list[dict[str, Any]], numeric_fields: list[str]) -> dict[str, Any]:
    numeric_field_stats: dict[str, Any] = {}
    for field in numeric_fields:
        values = [
            float(row["manifest_fields"][field])
            for row in rows
            if row["manifest_fields"].get(field) is not None
        ]
        stats = numeric_stats(values)
        if stats is not None:
            numeric_field_stats[field] = stats

    return {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "focus_vs_reference_avg_db": mean_or_none([float(row["focus_minus_reference_db"]) for row in rows]),
        "min_constraint_gap_avg_db": mean_or_none([float(row["min_constraint_gap_db"]) for row in rows]),
        "pass_count_avg": mean_or_none([float(row["pass_count"]) for row in rows]),
        "numeric_field_stats": numeric_field_stats,
    }


def project_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": str(row["sample_id"]),
        "focus_minus_reference_db": float(row["focus_minus_reference_db"]),
        "pass_count": int(row["pass_count"]),
        "fail_count": int(row["fail_count"]),
        "min_constraint_gap_db": float(row["min_constraint_gap_db"]),
        "failed_constraints": list(row["failed_constraints"]),
        "failed_constraint_gaps_db": dict(row["failed_constraint_gaps_db"]),
        "metadata_distance_z": float(row["metadata_distance_z"]),
        "constraint_distance_z": float(row["constraint_distance_z"]),
        "joint_distance_z": float(row["joint_distance_z"]),
        "manifest_fields": dict(row["manifest_fields"]),
        "recipe": row["recipe"],
        "temporal_pattern": row["temporal_pattern"],
        "target_present_ratio": row["target_present_ratio"],
        "metadata_path": row["metadata_path"],
    }


def z_distance(
    row_values: dict[str, float],
    center_values: dict[str, float],
    field_means: dict[str, float],
    field_stdevs: dict[str, float],
    fields: list[str],
) -> float:
    if not fields:
        return 0.0
    total = 0.0
    for field in fields:
        stdev = field_stdevs[field]
        row_z = (row_values[field] - field_means[field]) / stdev
        center_z = (center_values[field] - field_means[field]) / stdev
        total += (row_z - center_z) ** 2
    return float(math.sqrt(total))


def main() -> None:
    args = parse_args()
    compare_map = parse_mapping(args.compare)
    ordered_constraints = [(args.ordered_aliases[i], args.ordered_aliases[i + 1]) for i in range(len(args.ordered_aliases) - 1)]
    extra_constraints = parse_constraints(args.extra_order_constraint)
    all_constraints = ordered_constraints + extra_constraints

    if args.focus_alias not in compare_map:
        raise ValueError(f"Focus alias missing compare input: {args.focus_alias}")
    if args.reference_alias not in compare_map:
        raise ValueError(f"Reference alias missing compare input: {args.reference_alias}")

    manifest_rows_by_id = {
        str(row["sample_id"]): row
        for row in load_jsonl(args.manifest_jsonl)
    }
    seed_sample_ids = load_sample_ids(args.seed_sample_ids_file)
    if not seed_sample_ids:
        raise ValueError("Seed sample id file is empty.")

    rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    shared_sample_ids: set[str] | None = None
    for alias, path in compare_map.items():
        rows = {str(row["sample_id"]): row for row in load_jsonl(path)}
        rows_by_alias[alias] = rows
        sample_ids = set(rows)
        shared_sample_ids = sample_ids if shared_sample_ids is None else (shared_sample_ids & sample_ids)

    if not shared_sample_ids:
        raise RuntimeError("No shared sample ids across compare inputs.")

    row_records: list[dict[str, Any]] = []
    for sample_id in sorted(shared_sample_ids):
        manifest_row = manifest_rows_by_id.get(sample_id)
        if manifest_row is None:
            continue

        baseline_metadata_path = str(rows_by_alias[args.focus_alias][sample_id]["metadata_path"])
        baseline_recipe = str(rows_by_alias[args.focus_alias][sample_id]["recipe"])
        baseline_pattern = str(rows_by_alias[args.focus_alias][sample_id]["temporal_pattern"])
        scores: dict[str, float] = {}
        for alias, rows in rows_by_alias.items():
            row = rows[sample_id]
            if str(row["metadata_path"]) != baseline_metadata_path:
                raise RuntimeError(f"Metadata mismatch for {sample_id} between compare inputs.")
            if str(row["recipe"]) != baseline_recipe or str(row["temporal_pattern"]) != baseline_pattern:
                raise RuntimeError(f"Recipe/pattern mismatch for {sample_id} between compare inputs.")
            scores[alias] = float(row["sisdr_b_db"])

        constraint_rows = build_constraint_rows(scores, all_constraints)
        failed_constraints = [row["constraint"] for row in constraint_rows if not row["pass"]]
        failed_constraint_gaps_db = {
            row["constraint"]: float(row["gap_db"])
            for row in constraint_rows
            if not row["pass"]
        }
        pass_count = sum(1 for row in constraint_rows if row["pass"])
        fail_count = len(constraint_rows) - pass_count
        manifest_fields = {
            field: manifest_row.get(field)
            for field in args.numeric_field
        }
        constraint_gap_map = {
            row["constraint"]: float(row["gap_db"])
            for row in constraint_rows
        }
        row_records.append(
            {
                "sample_id": sample_id,
                "focus_minus_reference_db": float(scores[args.focus_alias] - scores[args.reference_alias]),
                "pass_count": pass_count,
                "fail_count": fail_count,
                "all_constraints_pass": fail_count == 0,
                "failed_constraints": failed_constraints,
                "failed_constraint_gaps_db": failed_constraint_gaps_db,
                "constraint_gap_map": constraint_gap_map,
                "min_constraint_gap_db": float(min(row["gap_db"] for row in constraint_rows)),
                "scores": scores,
                "manifest_fields": manifest_fields,
                "recipe": manifest_row.get("recipe"),
                "temporal_pattern": manifest_row.get("temporal_pattern"),
                "target_present_ratio": manifest_row.get("target_present_ratio"),
                "metadata_path": manifest_row.get("metadata_path"),
                "is_seed": sample_id in seed_sample_ids,
            }
        )

    if not row_records:
        raise RuntimeError("No row records were built from the provided compare/manifest inputs.")

    seed_rows = [row for row in row_records if row["is_seed"]]
    if len(seed_rows) != len(seed_sample_ids):
        found_seed_ids = {str(row["sample_id"]) for row in seed_rows}
        missing_seed_ids = [sample_id for sample_id in seed_sample_ids if sample_id not in found_seed_ids]
        raise RuntimeError(f"Seed rows missing from compare/manifest inputs: {missing_seed_ids}")

    metadata_fields = [
        field
        for field in args.numeric_field
        if all(row["manifest_fields"].get(field) is not None for row in row_records)
    ]
    constraint_fields = [f"{higher}>{lower}" for higher, lower in all_constraints]

    metadata_field_means = {
        field: float(mean(float(row["manifest_fields"][field]) for row in row_records))
        for field in metadata_fields
    }
    metadata_field_stdevs = {
        field: float(pstdev(float(row["manifest_fields"][field]) for row in row_records)) or 1.0
        for field in metadata_fields
    }
    constraint_field_means = {
        field: float(mean(float(row["constraint_gap_map"][field]) for row in row_records))
        for field in constraint_fields
    }
    constraint_field_stdevs = {
        field: float(pstdev(float(row["constraint_gap_map"][field]) for row in row_records)) or 1.0
        for field in constraint_fields
    }

    seed_metadata_center = {
        field: float(mean(float(row["manifest_fields"][field]) for row in seed_rows))
        for field in metadata_fields
    }
    seed_constraint_center = {
        field: float(mean(float(row["constraint_gap_map"][field]) for row in seed_rows))
        for field in constraint_fields
    }

    for row in row_records:
        row_metadata_values = {
            field: float(row["manifest_fields"][field])
            for field in metadata_fields
        }
        row_constraint_values = {
            field: float(row["constraint_gap_map"][field])
            for field in constraint_fields
        }
        row["metadata_distance_z"] = z_distance(
            row_metadata_values,
            seed_metadata_center,
            metadata_field_means,
            metadata_field_stdevs,
            metadata_fields,
        )
        row["constraint_distance_z"] = z_distance(
            row_constraint_values,
            seed_constraint_center,
            constraint_field_means,
            constraint_field_stdevs,
            constraint_fields,
        )
        row["joint_distance_z"] = float(
            math.sqrt((row["metadata_distance_z"] ** 2) + (row["constraint_distance_z"] ** 2))
        )

    non_seed_rows = [row for row in row_records if not row["is_seed"]]
    non_seed_rows.sort(
        key=lambda row: (
            float(row["joint_distance_z"]),
            int(row["fail_count"]),
            -float(row["min_constraint_gap_db"]),
            str(row["sample_id"]),
        )
    )

    expansion_rows: list[dict[str, Any]] = []
    for row in non_seed_rows:
        family_rows = seed_rows + [row]
        family_scores = {
            alias: float(mean(float(member["scores"][alias]) for member in family_rows))
            for alias in compare_map
        }
        family_constraint_rows = build_constraint_rows(family_scores, all_constraints)
        family_failed_constraints = [item["constraint"] for item in family_constraint_rows if not item["pass"]]
        family_failed_constraint_gaps_db = {
            item["constraint"]: float(item["gap_db"])
            for item in family_constraint_rows
            if not item["pass"]
        }
        expansion_rows.append(
            {
                "candidate_sample_id": str(row["sample_id"]),
                "seed_plus_candidate_sample_ids": [str(seed_row["sample_id"]) for seed_row in seed_rows] + [str(row["sample_id"])],
                "candidate_failed_constraints": list(row["failed_constraints"]),
                "candidate_failed_constraint_gaps_db": dict(row["failed_constraint_gaps_db"]),
                "candidate_joint_distance_z": float(row["joint_distance_z"]),
                "candidate_metadata_distance_z": float(row["metadata_distance_z"]),
                "candidate_constraint_distance_z": float(row["constraint_distance_z"]),
                "candidate_focus_minus_reference_db": float(row["focus_minus_reference_db"]),
                "aggregate_all_constraints_pass": len(family_failed_constraints) == 0,
                "aggregate_failed_constraints": family_failed_constraints,
                "aggregate_failed_constraint_gaps_db": family_failed_constraint_gaps_db,
                "aggregate_alias_scores": family_scores,
                "aggregate_focus_minus_reference_db": float(
                    family_scores[args.focus_alias] - family_scores[args.reference_alias]
                ),
                "aggregate_min_constraint_gap_db": float(min(item["gap_db"] for item in family_constraint_rows)),
            }
        )

    expansion_rows.sort(
        key=lambda row: (
            1 if row["aggregate_all_constraints_pass"] else 0,
            float(row["aggregate_min_constraint_gap_db"]),
            -float(row["aggregate_focus_minus_reference_db"]),
            -float(row["candidate_joint_distance_z"]),
        ),
        reverse=True,
    )

    output = {
        "manifest_jsonl": serialize_repo_path(args.manifest_jsonl),
        "seed_sample_ids_file": serialize_repo_path(args.seed_sample_ids_file),
        "seed_sample_ids": seed_sample_ids,
        "focus_alias": args.focus_alias,
        "reference_alias": args.reference_alias,
        "compares": {alias: serialize_repo_path(path) for alias, path in sorted(compare_map.items())},
        "ordered_aliases": list(args.ordered_aliases),
        "extra_order_constraints": [f"{higher}>{lower}" for higher, lower in extra_constraints],
        "all_constraints": constraint_fields,
        "numeric_fields": list(args.numeric_field),
        "num_rows": len(row_records),
        "num_seed_rows": len(seed_rows),
        "seed_summary": summarize_rows(seed_rows, list(args.numeric_field)),
        "seed_constraint_center": seed_constraint_center,
        "seed_metadata_center": seed_metadata_center,
        "non_seed_fail_signature_counts": dict(
            sorted(
                Counter(" | ".join(row["failed_constraints"]) for row in non_seed_rows).items()
            )
        ),
        "top_nearest_rows_by_joint_distance": [project_row(row) for row in non_seed_rows[: args.top_k]],
        "top_nearest_rows_by_metadata_distance": [
            project_row(row)
            for row in sorted(non_seed_rows, key=lambda row: (float(row["metadata_distance_z"]), str(row["sample_id"])))[: args.top_k]
        ],
        "top_seed_plus_one_expansions": expansion_rows[: args.top_k],
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
                "seed_sample_ids": seed_sample_ids,
                "top_nearest_non_seed_sample_ids": [
                    str(row["sample_id"]) for row in non_seed_rows[: min(args.top_k, 5)]
                ],
                "top_seed_plus_one_candidates": [
                    str(row["candidate_sample_id"]) for row in expansion_rows[: min(args.top_k, 5)]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
