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
            "Rank search-manifest rows by metadata distance to a seed subset, while optionally "
            "joining compare metrics so the nearest neighbors can be read together with alias ordering behavior."
        )
    )
    parser.add_argument("--seed-manifest", action="append", type=Path, required=True)
    parser.add_argument("--seed-sample-ids-file", type=Path, required=True)
    parser.add_argument("--search-manifest", action="append", type=Path, required=True)
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
    parser.add_argument("--top-k", type=int, default=20)
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


def build_rows_by_id(paths: list[Path]) -> dict[str, dict[str, Any]]:
    mapping: dict[str, dict[str, Any]] = {}
    for path in paths:
        for row in load_jsonl(path):
            sample_id = str(row["sample_id"])
            if sample_id in mapping:
                raise ValueError(f"Duplicate sample_id across manifests: {sample_id}")
            mapping[sample_id] = {
                **row,
                "_manifest_path": serialize_repo_path(path),
            }
    return mapping


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


def resolve_repo_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if path.is_absolute():
        return path
    return ROOT / path


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


def load_metadata_payloads(rows_by_id: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    cache: dict[Path, dict[str, Any]] = {}
    payloads: dict[str, dict[str, Any]] = {}
    for sample_id, row in rows_by_id.items():
        metadata_path = resolve_repo_path(str(row.get("metadata_path") or ""))
        if metadata_path is None:
            payloads[sample_id] = {}
            continue
        if metadata_path not in cache:
            cache[metadata_path] = load_json(metadata_path)
        payloads[sample_id] = cache[metadata_path]
    return payloads


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


def project_row(row: dict[str, Any]) -> dict[str, Any]:
    output = {
        "sample_id": str(row["sample_id"]),
        "split": row.get("split"),
        "recipe": row.get("recipe"),
        "temporal_pattern": row.get("temporal_pattern"),
        "target_present_ratio": row.get("target_present_ratio"),
        "metadata_path": row.get("metadata_path"),
        "manifest_path": row.get("_manifest_path"),
        "metadata_distance_z": float(row["metadata_distance_z"]),
        "numeric_values": dict(row["numeric_values"]),
    }
    if row.get("compare_summary") is not None:
        output["compare_summary"] = dict(row["compare_summary"])
    return output


def summarize_group(rows: list[dict[str, Any]], numeric_fields: list[str]) -> dict[str, Any]:
    numeric_means: dict[str, float] = {}
    for field in numeric_fields:
        values = [
            float(row["numeric_values"][field])
            for row in rows
            if row["numeric_values"].get(field) is not None
        ]
        if values:
            numeric_means[field] = float(mean(values))

    summary: dict[str, Any] = {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "numeric_field_means": numeric_means,
        "mean_metadata_distance_z": mean_or_none([float(row["metadata_distance_z"]) for row in rows]),
    }

    compare_rows = [row["compare_summary"] for row in rows if row.get("compare_summary") is not None]
    if compare_rows:
        summary["top_alias_counts"] = dict(
            sorted(Counter(str(row["top_alias"]) for row in compare_rows).items())
        )
        summary["failed_constraint_counts"] = dict(
            sorted(
                Counter(
                    " | ".join(str(item) for item in row["failed_constraints"])
                    for row in compare_rows
                ).items()
            )
        )
        focus_vs_reference = [
            float(row["focus_minus_reference_db"])
            for row in compare_rows
            if row.get("focus_minus_reference_db") is not None
        ]
        if focus_vs_reference:
            summary["mean_focus_minus_reference_db"] = float(mean(focus_vs_reference))
    return summary


def main() -> None:
    args = parse_args()
    if bool(args.focus_alias) != bool(args.reference_alias):
        raise ValueError("--focus-alias and --reference-alias must be provided together.")

    seed_sample_ids = load_sample_ids(args.seed_sample_ids_file)
    if not seed_sample_ids:
        raise ValueError("Seed sample id file is empty.")

    seed_rows_by_id = build_rows_by_id(args.seed_manifest)
    search_rows_by_id = build_rows_by_id(args.search_manifest)
    metadata_payloads = load_metadata_payloads({**seed_rows_by_id, **search_rows_by_id})

    compare_map = parse_compare_mapping(list(args.compare))
    ordered_constraints = [
        (args.ordered_aliases[index], args.ordered_aliases[index + 1])
        for index in range(len(args.ordered_aliases) - 1)
    ]
    extra_constraints = parse_constraints(list(args.extra_order_constraint))
    all_constraints = ordered_constraints + extra_constraints

    rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    if compare_map:
        if args.focus_alias is None or args.reference_alias is None:
            raise ValueError("Compare inputs require --focus-alias and --reference-alias.")
        for alias, compare_path in compare_map.items():
            rows_by_alias[alias] = {
                str(row["sample_id"]): row
                for row in load_jsonl(compare_path)
            }
        missing_order_aliases = [alias for alias in args.ordered_aliases if alias not in rows_by_alias]
        if missing_order_aliases:
            raise ValueError(f"Ordered aliases missing compare inputs: {missing_order_aliases}")
        missing_constraint_aliases = sorted(
            {
                alias
                for higher_alias, lower_alias in all_constraints
                for alias in (higher_alias, lower_alias)
                if alias not in rows_by_alias
            }
        )
        if missing_constraint_aliases:
            raise ValueError(f"Constraint aliases missing compare inputs: {missing_constraint_aliases}")

    def build_row(sample_id: str, manifest_row: dict[str, Any]) -> dict[str, Any]:
        metadata_payload = metadata_payloads.get(sample_id, {})
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
            missing_compare_aliases = [
                alias for alias, rows in rows_by_alias.items() if sample_id not in rows
            ]
            if missing_compare_aliases:
                raise RuntimeError(
                    f"Sample id {sample_id} missing from compare inputs: {missing_compare_aliases}"
                )
            baseline_metadata_path = None
            baseline_recipe = None
            baseline_pattern = None
            for alias, rows in rows_by_alias.items():
                compare_row = rows[sample_id]
                metadata_path = str(compare_row["metadata_path"])
                recipe = str(compare_row["recipe"])
                pattern = str(compare_row["temporal_pattern"])
                if baseline_metadata_path is None:
                    baseline_metadata_path = metadata_path
                    baseline_recipe = recipe
                    baseline_pattern = pattern
                elif (
                    metadata_path != baseline_metadata_path
                    or recipe != baseline_recipe
                    or pattern != baseline_pattern
                ):
                    raise RuntimeError(f"Compare metadata mismatch for sample_id: {sample_id}")
                scores[alias] = float(compare_row["sisdr_b_db"])
            ranking = ranking_from_scores(scores)
            constraint_rows = build_constraint_rows(scores, all_constraints)
            failed_constraints = [
                str(item["constraint"])
                for item in constraint_rows
                if not item["pass"]
            ]
            compare_summary = {
                "top_alias": str(ranking[0]["alias"]) if ranking else None,
                "ranking": ranking,
                "focus_minus_reference_db": float(scores[args.focus_alias] - scores[args.reference_alias]),
                "candidate_gap_vs_aliases_db": {
                    alias: float(scores[args.focus_alias] - score)
                    for alias, score in scores.items()
                    if alias != args.focus_alias
                },
                "failed_constraints": failed_constraints,
                "failed_constraint_gaps_db": {
                    str(item["constraint"]): float(item["gap_db"])
                    for item in constraint_rows
                    if not item["pass"]
                },
            }

        return {
            **manifest_row,
            "sample_id": sample_id,
            "numeric_values": numeric_values,
            "compare_summary": compare_summary,
        }

    seed_rows: list[dict[str, Any]] = []
    for sample_id in seed_sample_ids:
        manifest_row = seed_rows_by_id.get(sample_id)
        if manifest_row is None:
            raise RuntimeError(f"Missing seed sample_id from seed manifests: {sample_id}")
        seed_rows.append(build_row(sample_id, manifest_row))

    seed_id_set = set(seed_sample_ids)
    search_rows: list[dict[str, Any]] = [
        build_row(sample_id, manifest_row)
        for sample_id, manifest_row in search_rows_by_id.items()
        if sample_id not in seed_id_set
    ]

    numeric_fields = list(args.manifest_field) + list(args.metadata_field)
    usable_seed_rows = [
        row for row in seed_rows
        if all(row["numeric_values"].get(field) is not None for field in numeric_fields)
    ]
    usable_search_rows = [
        row for row in search_rows
        if all(row["numeric_values"].get(field) is not None for field in numeric_fields)
    ]
    if not usable_seed_rows:
        raise RuntimeError("No usable seed rows with all requested numeric fields.")
    if not usable_search_rows:
        raise RuntimeError("No usable search rows with all requested numeric fields.")

    combined_rows = usable_seed_rows + usable_search_rows
    field_means = {
        field: float(mean(float(row["numeric_values"][field]) for row in combined_rows))
        for field in numeric_fields
    }
    field_stdevs = {
        field: float(pstdev(float(row["numeric_values"][field]) for row in combined_rows)) or 1.0
        for field in numeric_fields
    }
    seed_center = {
        field: float(mean(float(row["numeric_values"][field]) for row in usable_seed_rows))
        for field in numeric_fields
    }

    for row in usable_seed_rows:
        row_values = {field: float(row["numeric_values"][field]) for field in numeric_fields}
        row["metadata_distance_z"] = z_distance(
            row_values,
            seed_center,
            field_means,
            field_stdevs,
            numeric_fields,
        )
    for row in usable_search_rows:
        row_values = {field: float(row["numeric_values"][field]) for field in numeric_fields}
        row["metadata_distance_z"] = z_distance(
            row_values,
            seed_center,
            field_means,
            field_stdevs,
            numeric_fields,
        )

    usable_search_rows.sort(
        key=lambda row: (
            float(row["metadata_distance_z"]),
            str(row["sample_id"]),
        )
    )

    output = {
        "seed_manifests": [serialize_repo_path(path) for path in args.seed_manifest],
        "seed_sample_ids_file": serialize_repo_path(args.seed_sample_ids_file),
        "seed_sample_ids": seed_sample_ids,
        "search_manifests": [serialize_repo_path(path) for path in args.search_manifest],
        "manifest_fields": list(args.manifest_field),
        "metadata_fields": list(args.metadata_field),
        "numeric_fields": numeric_fields,
        "compares": {alias: serialize_repo_path(path) for alias, path in sorted(compare_map.items())},
        "focus_alias": args.focus_alias,
        "reference_alias": args.reference_alias,
        "ordered_aliases": list(args.ordered_aliases),
        "extra_order_constraints": [f"{higher}>{lower}" for higher, lower in extra_constraints],
        "num_usable_seed_rows": len(usable_seed_rows),
        "num_usable_search_rows": len(usable_search_rows),
        "seed_center": seed_center,
        "field_means": field_means,
        "field_stdevs": field_stdevs,
        "seed_group_summary": summarize_group(usable_seed_rows, numeric_fields),
        "top_nearest_search_rows": [
            project_row(row)
            for row in usable_search_rows[: args.top_k]
        ],
        "nearest_search_group_summary": summarize_group(
            usable_search_rows[: args.top_k],
            numeric_fields,
        ),
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
                "top_nearest_search_sample_ids": [
                    str(row["sample_id"])
                    for row in usable_search_rows[: min(args.top_k, 10)]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
