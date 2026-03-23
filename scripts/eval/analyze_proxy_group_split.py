from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, pstdev
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare multiple focused proxy sample-id groups on manifest fields, metadata fields, "
            "and optional compare metrics, and emit pairwise deltas plus representative rows."
        )
    )
    parser.add_argument("--manifest", action="append", type=Path, required=True)
    parser.add_argument(
        "--group",
        action="append",
        required=True,
        help="Group mapping in the form name=path/to/sample_ids.txt.",
    )
    parser.add_argument("--manifest-field", action="append", default=[])
    parser.add_argument("--metadata-field", action="append", default=[])
    parser.add_argument(
        "--compare",
        action="append",
        default=[],
        help="Optional compare jsonl mapping in the form alias=path/to/per_sample_metrics.jsonl.",
    )
    parser.add_argument("--focus-alias", type=str)
    parser.add_argument("--reference-alias", type=str)
    parser.add_argument("--ordered-aliases", nargs="*", default=[])
    parser.add_argument("--extra-order-constraint", action="append", default=[])
    parser.add_argument("--top-k", type=int, default=3)
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


def load_sample_ids(path: Path) -> list[str]:
    sample_ids: list[str] = []
    with path.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            value = line.strip()
            if value:
                sample_ids.append(value)
    return sample_ids


def parse_group(values: list[str]) -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --group value: {value!r}")
        name, raw_path = value.split("=", 1)
        name = name.strip()
        path = Path(raw_path.strip())
        if not name:
            raise ValueError(f"Empty group name in --group value: {value!r}")
        if name in mappings:
            raise ValueError(f"Duplicate group name: {name}")
        mappings[name] = path
    return mappings


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


def get_nested_value(payload: Any, dotted_path: str) -> Any:
    current: Any = payload
    for token in dotted_path.split("."):
        if isinstance(current, list):
            try:
                index = int(token)
            except ValueError as exc:
                raise KeyError(f"List index token must be int, got {token!r}") from exc
            if index >= len(current):
                return None
            current = current[index]
            continue
        if isinstance(current, dict):
            if token not in current:
                return None
            current = current[token]
            continue
        return None
    return current


def resolve_repo_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT / path


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


def z_distance(
    row_values: dict[str, float],
    center_values: dict[str, float],
    field_means: dict[str, float],
    field_stdevs: dict[str, float],
    fields: list[str],
) -> float:
    total = 0.0
    for field in fields:
        stdev = field_stdevs[field]
        row_z = (row_values[field] - field_means[field]) / stdev
        center_z = (center_values[field] - field_means[field]) / stdev
        total += (row_z - center_z) ** 2
    return float(math.sqrt(total))


def mean_or_none(values: list[float]) -> float | None:
    if not values:
        return None
    return float(mean(values))


def main() -> None:
    args = parse_args()
    if bool(args.focus_alias) != bool(args.reference_alias):
        raise ValueError("--focus-alias and --reference-alias must be provided together.")

    manifest_rows_by_id: dict[str, dict[str, Any]] = {}
    for manifest_path in args.manifest:
        for row in load_jsonl(manifest_path):
            sample_id = str(row["sample_id"])
            if sample_id in manifest_rows_by_id:
                raise ValueError(f"Duplicate sample_id across manifests: {sample_id}")
            manifest_rows_by_id[sample_id] = row

    metadata_cache: dict[Path, dict[str, Any]] = {}

    def metadata_payload_for(sample_id: str) -> dict[str, Any]:
        manifest_row = manifest_rows_by_id[sample_id]
        metadata_path = resolve_repo_path(str(manifest_row.get("metadata_path") or ""))
        if metadata_path is None:
            return {}
        if metadata_path not in metadata_cache:
            metadata_cache[metadata_path] = load_json(metadata_path)
        return metadata_cache[metadata_path]

    compare_map = parse_compare_mapping(list(args.compare))
    rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    for alias, compare_path in compare_map.items():
        rows_by_alias[alias] = {
            str(row["sample_id"]): row
            for row in load_jsonl(compare_path)
        }

    ordered_constraints = [
        (args.ordered_aliases[index], args.ordered_aliases[index + 1])
        for index in range(len(args.ordered_aliases) - 1)
    ]
    extra_constraints = parse_constraints(list(args.extra_order_constraint))
    all_constraints = ordered_constraints + extra_constraints

    if rows_by_alias:
        if args.focus_alias is None or args.reference_alias is None:
            raise ValueError("Compare inputs require --focus-alias and --reference-alias.")

    group_map = parse_group(list(args.group))
    group_sample_ids: dict[str, list[str]] = {}
    all_group_sample_ids: list[str] = []
    for group_name, path in group_map.items():
        sample_ids = load_sample_ids(path)
        if not sample_ids:
            raise ValueError(f"Group sample-id file is empty: {group_name}")
        missing = [sample_id for sample_id in sample_ids if sample_id not in manifest_rows_by_id]
        if missing:
            raise RuntimeError(f"Group {group_name} sample ids missing from manifests: {missing}")
        group_sample_ids[group_name] = sample_ids
        all_group_sample_ids.extend(sample_ids)

    numeric_fields = list(args.manifest_field) + list(args.metadata_field)

    def build_row(sample_id: str) -> dict[str, Any]:
        manifest_row = manifest_rows_by_id[sample_id]
        metadata_payload = metadata_payload_for(sample_id)
        numeric_values: dict[str, float | None] = {}
        for field in args.manifest_field:
            raw_value = manifest_row.get(field)
            numeric_values[field] = None if raw_value is None else float(raw_value)
        for field in args.metadata_field:
            raw_value = get_nested_value(metadata_payload, field)
            numeric_values[field] = None if raw_value is None else float(raw_value)

        compare_summary = None
        if rows_by_alias:
            scores: dict[str, float] = {}
            for alias, alias_rows in rows_by_alias.items():
                compare_row = alias_rows.get(sample_id)
                if compare_row is None:
                    raise RuntimeError(f"Sample id {sample_id} missing from compare alias: {alias}")
                scores[alias] = float(compare_row["sisdr_b_db"])
            ranking = ranking_from_scores(scores)
            constraint_rows = build_constraint_rows(scores, all_constraints)
            compare_summary = {
                "top_alias": str(ranking[0]["alias"]) if ranking else None,
                "ranking": ranking,
                "focus_minus_reference_db": float(scores[args.focus_alias] - scores[args.reference_alias]),
                "candidate_gap_vs_aliases_db": {
                    alias: float(scores[args.focus_alias] - score)
                    for alias, score in scores.items()
                    if alias != args.focus_alias
                },
                "failed_constraints": [
                    str(item["constraint"])
                    for item in constraint_rows
                    if not item["pass"]
                ],
            }

        return {
            "sample_id": sample_id,
            "split": manifest_row.get("split"),
            "recipe": manifest_row.get("recipe"),
            "temporal_pattern": manifest_row.get("temporal_pattern"),
            "target_present_ratio": manifest_row.get("target_present_ratio"),
            "metadata_path": manifest_row.get("metadata_path"),
            "numeric_values": numeric_values,
            "compare_summary": compare_summary,
        }

    all_rows = [build_row(sample_id) for sample_id in all_group_sample_ids]
    usable_rows = [
        row for row in all_rows
        if all(row["numeric_values"].get(field) is not None for field in numeric_fields)
    ]
    if len(usable_rows) != len(all_rows):
        missing_count = len(all_rows) - len(usable_rows)
        raise RuntimeError(f"{missing_count} group rows missing requested numeric fields.")

    field_means = {
        field: float(mean(float(row["numeric_values"][field]) for row in usable_rows))
        for field in numeric_fields
    }
    field_stdevs = {
        field: float(pstdev(float(row["numeric_values"][field]) for row in usable_rows)) or 1.0
        for field in numeric_fields
    }

    rows_by_group = {
        group_name: [build_row(sample_id) for sample_id in sample_ids]
        for group_name, sample_ids in group_sample_ids.items()
    }

    group_centers: dict[str, dict[str, float]] = {}
    group_summaries: dict[str, Any] = {}

    for group_name, rows in rows_by_group.items():
        group_center = {
            field: float(mean(float(row["numeric_values"][field]) for row in rows))
            for field in numeric_fields
        }
        group_centers[group_name] = group_center
        for row in rows:
            row_values = {
                field: float(row["numeric_values"][field])
                for field in numeric_fields
            }
            row["distance_to_group_center_z"] = z_distance(
                row_values,
                group_center,
                field_means,
                field_stdevs,
                numeric_fields,
            )

        representative_rows = sorted(
            rows,
            key=lambda row: (
                float(row["distance_to_group_center_z"]),
                str(row["sample_id"]),
            ),
        )[: args.top_k]

        summary: dict[str, Any] = {
            "count": len(rows),
            "sample_ids": [str(row["sample_id"]) for row in rows],
            "numeric_field_means": group_center,
            "representative_rows": [
                {
                    "sample_id": row["sample_id"],
                    "distance_to_group_center_z": float(row["distance_to_group_center_z"]),
                    "numeric_values": dict(row["numeric_values"]),
                    "compare_summary": row["compare_summary"],
                }
                for row in representative_rows
            ],
        }

        compare_rows = [row["compare_summary"] for row in rows if row["compare_summary"] is not None]
        if compare_rows:
            aggregate_scores = {
                alias: float(
                    mean(
                        float(row["ranking"][next(
                            index for index, item in enumerate(row["ranking"])
                            if item["alias"] == alias
                        )]["sisdr_db"])
                        for row in compare_rows
                    )
                )
                for alias in compare_map
            }
            summary["top_alias_counts"] = {
                key: sum(1 for row in compare_rows if row["top_alias"] == key)
                for key in sorted({str(row["top_alias"]) for row in compare_rows})
            }
            summary["failed_constraint_counts"] = {
                key: sum(1 for row in compare_rows if " | ".join(row["failed_constraints"]) == key)
                for key in sorted({" | ".join(row["failed_constraints"]) for row in compare_rows})
            }
            summary["mean_focus_minus_reference_db"] = mean_or_none(
                [float(row["focus_minus_reference_db"]) for row in compare_rows]
            )
            summary["mean_candidate_gap_vs_aliases_db"] = {
                alias: float(mean(float(row["candidate_gap_vs_aliases_db"][alias]) for row in compare_rows))
                for alias in compare_map
                if alias != args.focus_alias
            }
            summary["aggregate_scores_db"] = aggregate_scores
            summary["aggregate_ranking"] = ranking_from_scores(aggregate_scores)
        group_summaries[group_name] = summary

    pairwise_deltas: dict[str, Any] = {}
    group_names = list(group_map)
    for index, left_name in enumerate(group_names):
        for right_name in group_names[index + 1 :]:
            left_summary = group_summaries[left_name]
            right_summary = group_summaries[right_name]
            delta_key = f"{left_name}_minus_{right_name}"
            delta_summary: dict[str, Any] = {
                "numeric_field_mean_deltas": {
                    field: float(
                        left_summary["numeric_field_means"][field] - right_summary["numeric_field_means"][field]
                    )
                    for field in numeric_fields
                }
            }
            if "mean_focus_minus_reference_db" in left_summary and "mean_focus_minus_reference_db" in right_summary:
                delta_summary["mean_focus_minus_reference_db"] = float(
                    left_summary["mean_focus_minus_reference_db"] - right_summary["mean_focus_minus_reference_db"]
                )
            if "mean_candidate_gap_vs_aliases_db" in left_summary and "mean_candidate_gap_vs_aliases_db" in right_summary:
                delta_summary["mean_candidate_gap_vs_aliases_db"] = {
                    alias: float(
                        left_summary["mean_candidate_gap_vs_aliases_db"][alias]
                        - right_summary["mean_candidate_gap_vs_aliases_db"][alias]
                    )
                    for alias in left_summary["mean_candidate_gap_vs_aliases_db"]
                }
            pairwise_deltas[delta_key] = delta_summary

    output = {
        "manifests": [serialize_repo_path(path) for path in args.manifest],
        "groups": {name: serialize_repo_path(path) for name, path in group_map.items()},
        "manifest_fields": list(args.manifest_field),
        "metadata_fields": list(args.metadata_field),
        "numeric_fields": numeric_fields,
        "compares": {alias: serialize_repo_path(path) for alias, path in sorted(compare_map.items())},
        "focus_alias": args.focus_alias,
        "reference_alias": args.reference_alias,
        "ordered_aliases": list(args.ordered_aliases),
        "extra_order_constraints": [f"{higher}>{lower}" for higher, lower in extra_constraints],
        "field_means": field_means,
        "field_stdevs": field_stdevs,
        "group_summaries": group_summaries,
        "pairwise_deltas": pairwise_deltas,
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
                "groups": list(group_map),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
