from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze whether a new checkpoint moves a focused synthetic candidate subset in the intended "
            "multi-model direction, using existing compare per-sample metrics."
        )
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
    parser.add_argument(
        "--sample-ids-path",
        type=Path,
        help="Optional text file containing the sample ids to analyze. Defaults to all shared ids.",
    )
    parser.add_argument(
        "--candidate-alias",
        type=str,
        required=True,
        help="Alias of the candidate checkpoint under diagnosis.",
    )
    parser.add_argument(
        "--reference-alias",
        type=str,
        required=True,
        help="Alias of the warm-start or reference checkpoint used to judge directionality.",
    )
    parser.add_argument(
        "--ordered-aliases",
        nargs="*",
        default=[],
        help="Optional expected best-to-worst ordering among historical aliases.",
    )
    parser.add_argument(
        "--extra-order-constraint",
        action="append",
        default=[],
        help="Optional additional aggregate ordering constraints in the form higher>lower.",
    )
    parser.add_argument("--output-json", type=Path, required=True)
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


def load_sample_ids(path: Path) -> list[str]:
    sample_ids: list[str] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            sample_id = line.strip()
            if sample_id:
                sample_ids.append(sample_id)
    return sample_ids


def parse_compare_mapping(values: list[str]) -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --compare value: {value!r}")
        alias, raw_path = value.split("=", 1)
        alias = alias.strip()
        compare_path = Path(raw_path.strip())
        if not alias:
            raise ValueError(f"Empty alias in --compare value: {value!r}")
        if alias in mappings:
            raise ValueError(f"Duplicate alias in --compare values: {alias}")
        mappings[alias] = compare_path
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


def aggregate_scores(rows: list[dict[str, Any]], aliases: list[str]) -> dict[str, float]:
    return {
        alias: float(sum(row["scores"][alias] for row in rows) / len(rows))
        for alias in aliases
    }


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


def ranking_aliases(scores: dict[str, float]) -> list[str]:
    return [item["alias"] for item in ranking_from_scores(scores)]


def order_pass(scores: dict[str, float], ordered_aliases: list[str]) -> tuple[bool, list[dict[str, Any]]]:
    gaps: list[dict[str, Any]] = []
    passed = True
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
            passed = False
    return passed, gaps


def extra_constraints_pass(
    scores: dict[str, float],
    constraints: list[tuple[str, str]],
) -> tuple[bool, list[dict[str, Any]]]:
    gaps: list[dict[str, Any]] = []
    passed = True
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
            passed = False
    return passed, gaps


def main() -> None:
    args = parse_args()
    compare_map = parse_compare_mapping(args.compare)
    extra_constraints = parse_extra_order_constraints(args.extra_order_constraint)

    if args.candidate_alias not in compare_map:
        raise ValueError(f"Candidate alias missing compare input: {args.candidate_alias}")
    if args.reference_alias not in compare_map:
        raise ValueError(f"Reference alias missing compare input: {args.reference_alias}")

    missing_order_aliases = [
        alias for alias in args.ordered_aliases if alias not in compare_map and alias != args.baseline_alias
    ]
    if missing_order_aliases:
        raise ValueError(f"Ordered aliases missing compare inputs: {missing_order_aliases}")

    missing_constraint_aliases = sorted(
        {
            alias
            for higher_alias, lower_alias in extra_constraints
            for alias in (higher_alias, lower_alias)
            if alias not in compare_map and alias != args.baseline_alias
        }
    )
    if missing_constraint_aliases:
        raise ValueError(f"Extra order constraints missing compare inputs: {missing_constraint_aliases}")

    rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    shared_sample_ids: set[str] | None = None
    for alias, compare_path in compare_map.items():
        rows = {str(row["sample_id"]): row for row in load_jsonl(compare_path)}
        rows_by_alias[alias] = rows
        sample_ids = set(rows)
        shared_sample_ids = sample_ids if shared_sample_ids is None else (shared_sample_ids & sample_ids)

    if not shared_sample_ids:
        raise RuntimeError("No shared sample ids across compare inputs.")

    requested_sample_ids = (
        load_sample_ids(args.sample_ids_path) if args.sample_ids_path is not None else sorted(shared_sample_ids)
    )
    missing_requested = [sample_id for sample_id in requested_sample_ids if sample_id not in shared_sample_ids]
    if missing_requested:
        raise RuntimeError(f"Requested sample ids missing from shared compare inputs: {missing_requested}")

    candidate_rows: list[dict[str, Any]] = []
    aliases = [args.baseline_alias] + sorted(compare_map)
    baseline_source_alias = sorted(compare_map)[0]
    for sample_id in requested_sample_ids:
        baseline_score = float(rows_by_alias[baseline_source_alias][sample_id]["sisdr_a_db"])
        baseline_metadata_path = str(rows_by_alias[baseline_source_alias][sample_id]["metadata_path"])
        baseline_recipe = str(rows_by_alias[baseline_source_alias][sample_id]["recipe"])
        baseline_pattern = str(rows_by_alias[baseline_source_alias][sample_id]["temporal_pattern"])
        baseline_ratio = float(rows_by_alias[baseline_source_alias][sample_id]["target_present_ratio"])
        scores = {args.baseline_alias: baseline_score}
        for alias, rows in rows_by_alias.items():
            row = rows[sample_id]
            if str(row["metadata_path"]) != baseline_metadata_path:
                raise RuntimeError(f"Metadata mismatch for {sample_id} between compare inputs.")
            if str(row["recipe"]) != baseline_recipe or str(row["temporal_pattern"]) != baseline_pattern:
                raise RuntimeError(f"Recipe/pattern mismatch for {sample_id} between compare inputs.")
            if abs(float(row["sisdr_a_db"]) - baseline_score) > 1e-4:
                raise RuntimeError(f"Baseline score mismatch for {sample_id} between compare inputs.")
            scores[alias] = float(row["sisdr_b_db"])

        row_ranking = ranking_from_scores(scores)
        row_order_pass, row_pair_gaps = order_pass(scores, list(args.ordered_aliases))
        row_extra_pass, row_extra_gaps = extra_constraints_pass(scores, extra_constraints)
        candidate_rank = next(
            item["rank"] for item in row_ranking if item["alias"] == args.candidate_alias
        )
        candidate_rows.append(
            {
                "sample_id": sample_id,
                "recipe": baseline_recipe,
                "temporal_pattern": baseline_pattern,
                "target_present_ratio": baseline_ratio,
                "metadata_path": baseline_metadata_path,
                "scores": scores,
                "ranking": row_ranking,
                "candidate_rank": candidate_rank,
                "candidate_minus_reference_db": float(scores[args.candidate_alias] - scores[args.reference_alias]),
                "candidate_minus_baseline_db": float(scores[args.candidate_alias] - scores[args.baseline_alias]),
                "reference_minus_baseline_db": float(scores[args.reference_alias] - scores[args.baseline_alias]),
                "ordered_aliases_pass": row_order_pass,
                "ordered_alias_pair_gaps_db": row_pair_gaps,
                "extra_constraints_pass": row_extra_pass,
                "extra_constraint_gaps_db": row_extra_gaps,
            }
        )

    aggregate = aggregate_scores(candidate_rows, aliases)
    aggregate_ranking = ranking_from_scores(aggregate)
    aggregate_order_pass, aggregate_order_gaps = order_pass(aggregate, list(args.ordered_aliases))
    aggregate_extra_pass, aggregate_extra_gaps = extra_constraints_pass(aggregate, extra_constraints)

    candidate_rank_histogram: dict[str, int] = {}
    for row in candidate_rows:
        key = str(row["candidate_rank"])
        candidate_rank_histogram[key] = candidate_rank_histogram.get(key, 0) + 1

    summary = {
        "sample_ids_path": serialize_repo_path(args.sample_ids_path) if args.sample_ids_path is not None else None,
        "requested_sample_ids": requested_sample_ids,
        "baseline_alias": args.baseline_alias,
        "baseline_source_alias": baseline_source_alias,
        "candidate_alias": args.candidate_alias,
        "reference_alias": args.reference_alias,
        "compares": {alias: serialize_repo_path(path) for alias, path in sorted(compare_map.items())},
        "ordered_aliases": list(args.ordered_aliases),
        "extra_order_constraints": [f"{higher}>{lower}" for higher, lower in extra_constraints],
        "num_samples": len(candidate_rows),
        "aggregate_scores_db": aggregate,
        "aggregate_ranking": aggregate_ranking,
        "aggregate_order_pass": aggregate_order_pass,
        "aggregate_order_gaps_db": aggregate_order_gaps,
        "aggregate_extra_constraints_pass": aggregate_extra_pass,
        "aggregate_extra_constraint_gaps_db": aggregate_extra_gaps,
        "samplewise_order_pass_count": sum(1 for row in candidate_rows if row["ordered_aliases_pass"]),
        "samplewise_extra_constraint_pass_count": sum(1 for row in candidate_rows if row["extra_constraints_pass"]),
        "candidate_rank_summary": {
            "mean_rank": float(sum(row["candidate_rank"] for row in candidate_rows) / len(candidate_rows)),
            "best_rank": min(row["candidate_rank"] for row in candidate_rows),
            "worst_rank": max(row["candidate_rank"] for row in candidate_rows),
            "rank_histogram": candidate_rank_histogram,
        },
        "candidate_vs_reference_avg_db": float(aggregate[args.candidate_alias] - aggregate[args.reference_alias]),
        "candidate_vs_baseline_avg_db": float(aggregate[args.candidate_alias] - aggregate[args.baseline_alias]),
        "reference_vs_baseline_avg_db": float(aggregate[args.reference_alias] - aggregate[args.baseline_alias]),
        "candidate_gap_vs_aliases_db": {
            alias: float(aggregate[args.candidate_alias] - score)
            for alias, score in aggregate.items()
            if alias != args.candidate_alias
        },
        "per_sample": candidate_rows,
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
                "num_samples": len(candidate_rows),
                "candidate_alias": args.candidate_alias,
                "reference_alias": args.reference_alias,
                "candidate_vs_reference_avg_db": summary["candidate_vs_reference_avg_db"],
                "aggregate_top_alias": aggregate_ranking[0]["alias"] if aggregate_ranking else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
