from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze row-level near-miss rows around a strict proxy core by grouping shared compare rows "
            "according to which ordering constraints they fail."
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
    parser.add_argument(
        "--anchor-sample-ids-file",
        type=Path,
        default=None,
        help="Optional newline-delimited anchor row ids used to summarize the current strict core.",
    )
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


def load_sample_ids(path: Path | None) -> list[str]:
    if path is None:
        return []
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


def summarize_rows(rows: list[dict[str, Any]], numeric_fields: list[str]) -> dict[str, Any]:
    numeric_stats: dict[str, Any] = {}
    for field in numeric_fields:
        values = [
            float(row["manifest_fields"][field])
            for row in rows
            if row["manifest_fields"].get(field) is not None
        ]
        if not values:
            continue
        numeric_stats[field] = {
            "count": len(values),
            "mean": float(mean(values)),
            "min": float(min(values)),
            "max": float(max(values)),
        }

    return {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "focus_vs_reference_avg_db": mean_or_none([float(row["focus_minus_reference_db"]) for row in rows]),
        "min_constraint_gap_avg_db": mean_or_none([float(row["min_constraint_gap_db"]) for row in rows]),
        "pass_count_avg": mean_or_none([float(row["pass_count"]) for row in rows]),
        "numeric_field_stats": numeric_stats,
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
        "manifest_fields": dict(row["manifest_fields"]),
        "recipe": row["recipe"],
        "temporal_pattern": row["temporal_pattern"],
        "target_present_ratio": row["target_present_ratio"],
        "metadata_path": row["metadata_path"],
    }


def main() -> None:
    args = parse_args()
    compare_map = parse_mapping(args.compare)
    ordered_constraints = [(args.ordered_aliases[i], args.ordered_aliases[i + 1]) for i in range(len(args.ordered_aliases) - 1)]
    extra_constraints = parse_constraints(args.extra_order_constraint)
    all_constraints = ordered_constraints + extra_constraints

    manifest_rows_by_id = {
        str(row["sample_id"]): row
        for row in load_jsonl(args.manifest_jsonl)
    }
    anchor_sample_ids = load_sample_ids(args.anchor_sample_ids_file)

    if args.focus_alias not in compare_map:
        raise ValueError(f"Focus alias missing compare input: {args.focus_alias}")
    if args.reference_alias not in compare_map:
        raise ValueError(f"Reference alias missing compare input: {args.reference_alias}")

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
        row_records.append(
            {
                "sample_id": sample_id,
                "focus_minus_reference_db": float(scores[args.focus_alias] - scores[args.reference_alias]),
                "pass_count": pass_count,
                "fail_count": fail_count,
                "all_constraints_pass": fail_count == 0,
                "failed_constraints": failed_constraints,
                "failed_constraint_gaps_db": failed_constraint_gaps_db,
                "constraint_rows": constraint_rows,
                "min_constraint_gap_db": float(min(row["gap_db"] for row in constraint_rows)),
                "scores": scores,
                "manifest_fields": manifest_fields,
                "recipe": manifest_row.get("recipe"),
                "temporal_pattern": manifest_row.get("temporal_pattern"),
                "target_present_ratio": manifest_row.get("target_present_ratio"),
                "metadata_path": manifest_row.get("metadata_path"),
                "is_anchor_row": sample_id in anchor_sample_ids,
            }
        )

    if not row_records:
        raise RuntimeError("No row records were built from the provided compare/manifest inputs.")

    row_records.sort(
        key=lambda row: (
            int(row["fail_count"]),
            -float(row["min_constraint_gap_db"]),
            -float(row["focus_minus_reference_db"]),
            str(row["sample_id"]),
        )
    )

    anchor_rows = [row for row in row_records if row["is_anchor_row"]]
    all_pass_rows = [row for row in row_records if row["all_constraints_pass"]]
    near_miss_rows = [row for row in row_records if not row["all_constraints_pass"]]

    fail_signature_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    single_fail_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in near_miss_rows:
        signature = " | ".join(row["failed_constraints"])
        fail_signature_groups[signature].append(row)
        if int(row["fail_count"]) == 1:
            single_fail_groups[row["failed_constraints"][0]].append(row)

    signature_summary = {
        signature: summarize_rows(
            sorted(
                rows,
                key=lambda row: (-float(row["min_constraint_gap_db"]), -float(row["focus_minus_reference_db"]), str(row["sample_id"]))
            ),
            list(args.numeric_field),
        )
        for signature, rows in sorted(
            fail_signature_groups.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    }

    single_fail_summary = {
        constraint: {
            **summarize_rows(
                sorted(
                    rows,
                    key=lambda row: (-float(row["min_constraint_gap_db"]), -float(row["focus_minus_reference_db"]), str(row["sample_id"]))
                ),
                list(args.numeric_field),
            ),
            "top_rows": [
                project_row(row)
                for row in sorted(
                    rows,
                    key=lambda row: (-float(row["min_constraint_gap_db"]), -float(row["focus_minus_reference_db"]), str(row["sample_id"]))
                )[: args.top_k]
            ],
        }
        for constraint, rows in sorted(
            single_fail_groups.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    }

    output = {
        "manifest_jsonl": serialize_repo_path(args.manifest_jsonl),
        "anchor_sample_ids_file": serialize_repo_path(args.anchor_sample_ids_file),
        "anchor_sample_ids": anchor_sample_ids,
        "focus_alias": args.focus_alias,
        "reference_alias": args.reference_alias,
        "compares": {alias: serialize_repo_path(path) for alias, path in sorted(compare_map.items())},
        "ordered_aliases": list(args.ordered_aliases),
        "extra_order_constraints": [f"{higher}>{lower}" for higher, lower in extra_constraints],
        "all_constraints": [f"{higher}>{lower}" for higher, lower in all_constraints],
        "numeric_fields": list(args.numeric_field),
        "num_rows": len(row_records),
        "num_all_constraints_pass_rows": len(all_pass_rows),
        "num_near_miss_rows": len(near_miss_rows),
        "constraint_fail_counts": dict(
            sorted(
                Counter(
                    constraint
                    for row in near_miss_rows
                    for constraint in row["failed_constraints"]
                ).items()
            )
        ),
        "anchor_summary": summarize_rows(anchor_rows, list(args.numeric_field)),
        "all_constraints_pass_summary": summarize_rows(all_pass_rows, list(args.numeric_field)),
        "all_constraints_pass_rows": [project_row(row) for row in all_pass_rows],
        "top_near_miss_rows": [project_row(row) for row in near_miss_rows[: args.top_k]],
        "single_fail_constraint_summaries": single_fail_summary,
        "failed_signature_summaries": signature_summary,
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
                "num_rows": len(row_records),
                "num_all_constraints_pass_rows": len(all_pass_rows),
                "top_near_miss_sample_ids": [str(row["sample_id"]) for row in near_miss_rows[: args.top_k]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
