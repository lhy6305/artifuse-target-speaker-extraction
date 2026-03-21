from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze row-level subgroup behavior inside a focused proxy candidate subset by "
            "joining a direction summary with manifest metadata and reporting median-based splits."
        )
    )
    parser.add_argument("--direction-summary-json", type=Path, required=True)
    parser.add_argument("--manifest-jsonl", type=Path, required=True)
    parser.add_argument("--focus-alias", type=str, required=True)
    parser.add_argument(
        "--compare-alias",
        action="append",
        default=[],
        help="Alias to compare against the focus alias. Can be passed multiple times.",
    )
    parser.add_argument(
        "--numeric-field",
        action="append",
        default=[],
        help="Numeric manifest field to analyze via median splits. Can be passed multiple times.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="How many most-positive / most-negative rows to keep per compare alias.",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def mean(values: list[float]) -> float:
    if not values:
        raise ValueError("Cannot compute mean of empty values.")
    return float(sum(values) / len(values))


def build_row_records(
    summary: dict[str, Any],
    manifest_rows_by_id: dict[str, dict[str, Any]],
    focus_alias: str,
    compare_aliases: list[str],
    numeric_fields: list[str],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in summary["per_sample"]:
        sample_id = str(row["sample_id"])
        manifest_row = manifest_rows_by_id.get(sample_id)
        if manifest_row is None:
            raise RuntimeError(f"Sample id missing from manifest: {sample_id}")
        scores = dict(row["scores"])
        if focus_alias not in scores:
            raise RuntimeError(f"Focus alias missing from row scores: {focus_alias}")
        gaps = {
            compare_alias: float(scores[focus_alias] - scores[compare_alias])
            for compare_alias in compare_aliases
        }
        numeric_values: dict[str, float | None] = {}
        for field in numeric_fields:
            raw_value = manifest_row.get(field)
            numeric_values[field] = None if raw_value is None else float(raw_value)
        candidate_rank = next(
            int(rank_row["rank"]) for rank_row in row["ranking"] if str(rank_row["alias"]) == focus_alias
        )
        records.append(
            {
                "sample_id": sample_id,
                "scores": scores,
                "focus_rank": candidate_rank,
                "gaps_db": gaps,
                "manifest_fields": numeric_values,
                "recipe": manifest_row.get("recipe"),
                "temporal_pattern": manifest_row.get("temporal_pattern"),
                "target_present_ratio": manifest_row.get("target_present_ratio"),
                "metadata_path": manifest_row.get("metadata_path"),
            }
        )
    return records


def summarize_rows_for_alias(
    rows: list[dict[str, Any]],
    focus_alias: str,
    compare_alias: str,
) -> dict[str, Any]:
    gaps = [float(row["gaps_db"][compare_alias]) for row in rows]
    focus_scores = [float(row["scores"][focus_alias]) for row in rows]
    compare_scores = [float(row["scores"][compare_alias]) for row in rows]
    focus_ranks = [int(row["focus_rank"]) for row in rows]
    return {
        "count": len(rows),
        "focus_vs_compare_avg_db": mean(gaps),
        "focus_avg_score_db": mean(focus_scores),
        "compare_avg_score_db": mean(compare_scores),
        "focus_rank_mean": mean([float(rank) for rank in focus_ranks]),
        "improved_count": sum(1 for gap in gaps if gap > 0.0),
        "regressed_count": sum(1 for gap in gaps if gap < 0.0),
        "tied_count": sum(1 for gap in gaps if gap == 0.0),
        "sample_ids": [str(row["sample_id"]) for row in rows],
    }


def summarize_numeric_field(
    rows: list[dict[str, Any]],
    field: str,
    focus_alias: str,
    compare_aliases: list[str],
) -> dict[str, Any] | None:
    available_rows = [row for row in rows if row["manifest_fields"].get(field) is not None]
    if len(available_rows) < 2:
        return None

    values = [float(row["manifest_fields"][field]) for row in available_rows]
    median_value = float(statistics.median(values))
    low_rows = [row for row in available_rows if float(row["manifest_fields"][field]) <= median_value]
    high_rows = [row for row in available_rows if float(row["manifest_fields"][field]) > median_value]

    subgroup_summaries = {}
    for subgroup_name, subgroup_rows in (("low_or_equal_median", low_rows), ("high_median", high_rows)):
        subgroup_summaries[subgroup_name] = {
            compare_alias: summarize_rows_for_alias(subgroup_rows, focus_alias, compare_alias)
            for compare_alias in compare_aliases
        }

    return {
        "field": field,
        "median_value": median_value,
        "overall_min_value": min(values),
        "overall_max_value": max(values),
        "num_rows_with_value": len(available_rows),
        "subgroups": subgroup_summaries,
    }


def select_extreme_rows(
    rows: list[dict[str, Any]],
    focus_alias: str,
    compare_alias: str,
    top_k: int,
) -> dict[str, list[dict[str, Any]]]:
    ordered = sorted(rows, key=lambda row: (float(row["gaps_db"][compare_alias]), str(row["sample_id"])))

    def project(row: dict[str, Any]) -> dict[str, Any]:
        return {
            "sample_id": row["sample_id"],
            "focus_vs_compare_db": float(row["gaps_db"][compare_alias]),
            "focus_rank": int(row["focus_rank"]),
            "focus_score_db": float(row["scores"][focus_alias]),
            "compare_score_db": float(row["scores"][compare_alias]),
            "manifest_fields": row["manifest_fields"],
            "recipe": row["recipe"],
            "temporal_pattern": row["temporal_pattern"],
            "target_present_ratio": row["target_present_ratio"],
            "metadata_path": row["metadata_path"],
        }

    return {
        "most_regressed": [project(row) for row in ordered[:top_k]],
            "most_improved": [project(row) for row in ordered[-top_k:][::-1]],
    }

def main() -> None:
    args = parse_args()
    summary = load_json(args.direction_summary_json)
    manifest_rows_by_id = {
        str(row["sample_id"]): row
        for row in load_jsonl(args.manifest_jsonl)
    }
    available_aliases = set(summary.get("aggregate_scores_db", {}).keys())
    if args.focus_alias not in available_aliases:
        raise RuntimeError(f"Focus alias missing from summary aggregate scores: {args.focus_alias}")
    missing_compare_aliases = [alias for alias in args.compare_alias if alias not in available_aliases]
    if missing_compare_aliases:
        raise RuntimeError(f"Compare aliases missing from summary aggregate scores: {missing_compare_aliases}")

    row_records = build_row_records(
        summary=summary,
        manifest_rows_by_id=manifest_rows_by_id,
        focus_alias=args.focus_alias,
        compare_aliases=list(args.compare_alias),
        numeric_fields=list(args.numeric_field),
    )

    compare_summaries = {
        compare_alias: summarize_rows_for_alias(row_records, args.focus_alias, compare_alias)
        for compare_alias in args.compare_alias
    }
    numeric_field_summaries = [
        field_summary
        for field in args.numeric_field
        if (field_summary := summarize_numeric_field(row_records, field, args.focus_alias, list(args.compare_alias)))
        is not None
    ]
    extreme_rows = {
        compare_alias: select_extreme_rows(row_records, args.focus_alias, compare_alias, args.top_k)
        for compare_alias in args.compare_alias
    }

    output = {
        "direction_summary_json": serialize_repo_path(args.direction_summary_json),
        "manifest_jsonl": serialize_repo_path(args.manifest_jsonl),
        "focus_alias": args.focus_alias,
        "compare_aliases": list(args.compare_alias),
        "numeric_fields": list(args.numeric_field),
        "num_rows": len(row_records),
        "compare_summaries": compare_summaries,
        "numeric_field_summaries": numeric_field_summaries,
        "extreme_rows_by_compare_alias": extreme_rows,
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
                "focus_alias": args.focus_alias,
                "compare_aliases": list(args.compare_alias),
                "num_rows": len(row_records),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
