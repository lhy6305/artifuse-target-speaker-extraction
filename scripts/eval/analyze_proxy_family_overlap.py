from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze overlaps between focused proxy-family manifests and summarize the directionality of each "
            "membership subset using existing compare per-sample metrics."
        )
    )
    parser.add_argument(
        "--group",
        action="append",
        required=True,
        help="Group mapping in the form label=path/to/focused_manifest.jsonl.",
    )
    parser.add_argument(
        "--compare",
        action="append",
        required=True,
        help="Compare jsonl mapping in the form alias=path/to/per_sample_metrics.jsonl.",
    )
    parser.add_argument(
        "--baseline-alias",
        type=str,
        default="baseline",
        help="Alias name to use for the shared compare baseline reconstructed from sisdr_a_db.",
    )
    parser.add_argument("--candidate-alias", type=str, required=True)
    parser.add_argument("--reference-alias", type=str, required=True)
    parser.add_argument("--ordered-aliases", nargs="*", default=[])
    parser.add_argument(
        "--extra-order-constraint",
        action="append",
        default=[],
        help="Optional aggregate ordering constraint in the form higher>lower.",
    )
    parser.add_argument(
        "--numeric-field",
        action="append",
        default=[],
        help="Numeric manifest field to summarize for each membership subset.",
    )
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


def parse_mapping(values: list[str], expected_suffix: str) -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid mapping value: {value!r}")
        alias, raw_path = value.split("=", 1)
        alias = alias.strip()
        path = Path(raw_path.strip())
        if not alias:
            raise ValueError(f"Empty alias in mapping: {value!r}")
        if alias in mappings:
            raise ValueError(f"Duplicate alias in mappings: {alias}")
        if expected_suffix and not str(path).endswith(expected_suffix):
            raise ValueError(f"Expected path ending with {expected_suffix!r}, got: {path}")
        mappings[alias] = path
    return mappings


def parse_extra_order_constraints(values: list[str]) -> list[tuple[str, str]]:
    constraints: list[tuple[str, str]] = []
    for value in values:
        if ">" not in value:
            raise ValueError(f"Invalid --extra-order-constraint value: {value!r}")
        higher_alias, lower_alias = value.split(">", 1)
        higher_alias = higher_alias.strip()
        lower_alias = lower_alias.strip()
        if not higher_alias or not lower_alias:
            raise ValueError(f"Invalid --extra-order-constraint value: {value!r}")
        constraints.append((higher_alias, lower_alias))
    return constraints


def ranking_from_scores(scores: dict[str, float]) -> list[dict[str, Any]]:
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [
        {
            "rank": index + 1,
            "alias": alias,
            "sisdr_db": score,
        }
        for index, (alias, score) in enumerate(ordered)
    ]


def order_pass(scores: dict[str, float], ordered_aliases: list[str]) -> tuple[bool, list[dict[str, Any]]]:
    gaps: list[dict[str, Any]] = []
    for index in range(len(ordered_aliases) - 1):
        higher_alias = ordered_aliases[index]
        lower_alias = ordered_aliases[index + 1]
        gap = float(scores[higher_alias] - scores[lower_alias])
        gaps.append(
            {
                "constraint": f"{higher_alias}>{lower_alias}",
                "gap_db": gap,
                "pass": gap > 0.0,
            }
        )
        if gap <= 0.0:
            return False, gaps
    return True, gaps


def extra_constraints_pass(
    scores: dict[str, float],
    constraints: list[tuple[str, str]],
) -> tuple[bool, list[dict[str, Any]]]:
    gaps: list[dict[str, Any]] = []
    for higher_alias, lower_alias in constraints:
        gap = float(scores[higher_alias] - scores[lower_alias])
        gaps.append(
            {
                "constraint": f"{higher_alias}>{lower_alias}",
                "gap_db": gap,
                "pass": gap > 0.0,
            }
        )
        if gap <= 0.0:
            return False, gaps
    return True, gaps


def numeric_stats(rows: list[dict[str, Any]], fields: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for field in fields:
        values = [
            float(row["manifest_fields"][field])
            for row in rows
            if row["manifest_fields"].get(field) is not None
        ]
        if not values:
            continue
        summary[field] = {
            "count": len(values),
            "mean": float(mean(values)),
            "min": float(min(values)),
            "max": float(max(values)),
        }
    return summary


def summarize_subset(
    rows: list[dict[str, Any]],
    aliases: list[str],
    candidate_alias: str,
    reference_alias: str,
    ordered_aliases: list[str],
    extra_constraints: list[tuple[str, str]],
    numeric_fields: list[str],
) -> dict[str, Any]:
    aggregate_scores = {
        alias: float(sum(row["scores"][alias] for row in rows) / len(rows))
        for alias in aliases
    }
    aggregate_ranking = ranking_from_scores(aggregate_scores)
    aggregate_order_pass, aggregate_order_gaps = order_pass(aggregate_scores, ordered_aliases)
    aggregate_extra_pass, aggregate_extra_gaps = extra_constraints_pass(aggregate_scores, extra_constraints)

    candidate_ranks = [int(row["candidate_rank"]) for row in rows]
    rank_histogram: dict[str, int] = {}
    for rank in candidate_ranks:
        key = str(rank)
        rank_histogram[key] = rank_histogram.get(key, 0) + 1

    return {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "aggregate_scores_db": aggregate_scores,
        "aggregate_ranking": aggregate_ranking,
        "aggregate_order_pass": aggregate_order_pass,
        "aggregate_order_gaps_db": aggregate_order_gaps,
        "aggregate_extra_constraints_pass": aggregate_extra_pass,
        "aggregate_extra_constraint_gaps_db": aggregate_extra_gaps,
        "candidate_vs_reference_avg_db": float(aggregate_scores[candidate_alias] - aggregate_scores[reference_alias]),
        "samplewise_order_pass_count": sum(1 for row in rows if row["ordered_aliases_pass"]),
        "samplewise_extra_constraint_pass_count": sum(1 for row in rows if row["extra_constraints_pass"]),
        "candidate_rank_summary": {
            "mean_rank": float(sum(candidate_ranks) / len(candidate_ranks)),
            "best_rank": min(candidate_ranks),
            "worst_rank": max(candidate_ranks),
            "rank_histogram": rank_histogram,
        },
        "numeric_field_stats": numeric_stats(rows, numeric_fields),
        "rows": rows,
    }


def main() -> None:
    args = parse_args()
    group_map = parse_mapping(args.group, ".jsonl")
    compare_map = parse_mapping(args.compare, ".jsonl")
    extra_constraints = parse_extra_order_constraints(args.extra_order_constraint)

    if args.candidate_alias not in compare_map:
        raise ValueError(f"Candidate alias missing compare input: {args.candidate_alias}")
    if args.reference_alias not in compare_map:
        raise ValueError(f"Reference alias missing compare input: {args.reference_alias}")

    group_rows: dict[str, dict[str, dict[str, Any]]] = {}
    for label, manifest_path in group_map.items():
        rows = load_jsonl(manifest_path)
        by_sample_id: dict[str, dict[str, Any]] = {}
        for row in rows:
            sample_id = str(row["sample_id"])
            if sample_id in by_sample_id:
                raise ValueError(f"Duplicate sample_id {sample_id} in group {label}")
            by_sample_id[sample_id] = row
        group_rows[label] = by_sample_id

    rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    shared_sample_ids: set[str] | None = None
    for alias, compare_path in compare_map.items():
        rows = {str(row["sample_id"]): row for row in load_jsonl(compare_path)}
        rows_by_alias[alias] = rows
        sample_ids = set(rows)
        shared_sample_ids = sample_ids if shared_sample_ids is None else (shared_sample_ids & sample_ids)

    if not shared_sample_ids:
        raise RuntimeError("No shared sample ids across compare inputs.")

    union_sample_ids = sorted({sample_id for rows in group_rows.values() for sample_id in rows})
    missing_from_compare = [sample_id for sample_id in union_sample_ids if sample_id not in shared_sample_ids]
    if missing_from_compare:
        raise RuntimeError(f"Group sample ids missing from shared compare inputs: {missing_from_compare}")

    aliases = [args.baseline_alias] + sorted(compare_map)
    baseline_source_alias = sorted(compare_map)[0]

    row_entries: dict[str, dict[str, Any]] = {}
    for sample_id in union_sample_ids:
        memberships = sorted(label for label, rows in group_rows.items() if sample_id in rows)
        manifest_row = group_rows[memberships[0]][sample_id]
        scores = {args.baseline_alias: float(rows_by_alias[baseline_source_alias][sample_id]["sisdr_a_db"])}

        baseline_recipe = str(rows_by_alias[baseline_source_alias][sample_id]["recipe"])
        baseline_pattern = str(rows_by_alias[baseline_source_alias][sample_id]["temporal_pattern"])
        baseline_ratio = float(rows_by_alias[baseline_source_alias][sample_id]["target_present_ratio"])
        baseline_metadata_path = str(rows_by_alias[baseline_source_alias][sample_id]["metadata_path"])

        for alias, rows in rows_by_alias.items():
            row = rows[sample_id]
            if str(row["metadata_path"]) != baseline_metadata_path:
                raise RuntimeError(f"Metadata mismatch for {sample_id} between compare inputs.")
            if str(row["recipe"]) != baseline_recipe or str(row["temporal_pattern"]) != baseline_pattern:
                raise RuntimeError(f"Recipe/pattern mismatch for {sample_id} between compare inputs.")
            scores[alias] = float(row["sisdr_b_db"])

        ranking = ranking_from_scores(scores)
        ordered_pass, ordered_gaps = order_pass(scores, list(args.ordered_aliases))
        extra_pass, extra_gaps = extra_constraints_pass(scores, extra_constraints)
        candidate_rank = next(item["rank"] for item in ranking if item["alias"] == args.candidate_alias)

        manifest_fields = {field: manifest_row.get(field) for field in args.numeric_field}
        row_entries[sample_id] = {
            "sample_id": sample_id,
            "memberships": memberships,
            "recipe": baseline_recipe,
            "temporal_pattern": baseline_pattern,
            "target_present_ratio": baseline_ratio,
            "metadata_path": baseline_metadata_path,
            "manifest_fields": manifest_fields,
            "scores": scores,
            "ranking": ranking,
            "candidate_rank": candidate_rank,
            "candidate_minus_reference_db": float(scores[args.candidate_alias] - scores[args.reference_alias]),
            "ordered_aliases_pass": ordered_pass,
            "ordered_alias_pair_gaps_db": ordered_gaps,
            "extra_constraints_pass": extra_pass,
            "extra_constraint_gaps_db": extra_gaps,
        }

    group_summary: dict[str, Any] = {}
    for label, rows in group_rows.items():
        subset_rows = [row_entries[sample_id] for sample_id in sorted(rows)]
        group_summary[label] = summarize_subset(
            subset_rows,
            aliases=aliases,
            candidate_alias=args.candidate_alias,
            reference_alias=args.reference_alias,
            ordered_aliases=list(args.ordered_aliases),
            extra_constraints=extra_constraints,
            numeric_fields=args.numeric_field,
        )

    pairwise_overlaps: dict[str, Any] = {}
    pairwise_intersections: dict[str, Any] = {}
    for left_label, right_label in combinations(sorted(group_rows), 2):
        left_ids = set(group_rows[left_label])
        right_ids = set(group_rows[right_label])
        intersection_ids = sorted(left_ids & right_ids)
        overlap_key = f"{left_label}__{right_label}"
        pairwise_overlaps[overlap_key] = {
            "count": len(intersection_ids),
            "sample_ids": intersection_ids,
        }
        if intersection_ids:
            subset_rows = [row_entries[sample_id] for sample_id in intersection_ids]
            pairwise_intersections[overlap_key] = summarize_subset(
                subset_rows,
                aliases=aliases,
                candidate_alias=args.candidate_alias,
                reference_alias=args.reference_alias,
                ordered_aliases=list(args.ordered_aliases),
                extra_constraints=extra_constraints,
                numeric_fields=args.numeric_field,
            )

    membership_subsets: dict[str, Any] = {}
    subsets_by_membership: dict[tuple[str, ...], list[dict[str, Any]]] = {}
    for sample_id in union_sample_ids:
        membership_key = tuple(row_entries[sample_id]["memberships"])
        subsets_by_membership.setdefault(membership_key, []).append(row_entries[sample_id])
    for membership_key, subset_rows in sorted(subsets_by_membership.items()):
        subset_label = "__and__".join(membership_key)
        membership_subsets[subset_label] = summarize_subset(
            subset_rows,
            aliases=aliases,
            candidate_alias=args.candidate_alias,
            reference_alias=args.reference_alias,
            ordered_aliases=list(args.ordered_aliases),
            extra_constraints=extra_constraints,
            numeric_fields=args.numeric_field,
        )

    summary = {
        "groups": {label: serialize_repo_path(path) for label, path in sorted(group_map.items())},
        "compares": {alias: serialize_repo_path(path) for alias, path in sorted(compare_map.items())},
        "baseline_alias": args.baseline_alias,
        "baseline_source_alias": baseline_source_alias,
        "candidate_alias": args.candidate_alias,
        "reference_alias": args.reference_alias,
        "ordered_aliases": list(args.ordered_aliases),
        "extra_order_constraints": [f"{higher}>{lower}" for higher, lower in extra_constraints],
        "numeric_fields": list(args.numeric_field),
        "union_sample_ids": union_sample_ids,
        "group_summaries": group_summary,
        "pairwise_overlaps": pairwise_overlaps,
        "pairwise_intersection_summaries": pairwise_intersections,
        "membership_subset_summaries": membership_subsets,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output_json": serialize_repo_path(args.output_json),
                "groups": sorted(group_map),
                "union_sample_count": len(union_sample_ids),
                "membership_subsets": sorted(membership_subsets),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
