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
            "Rank rows in one or more search manifests by metadata distance to a seed subset drawn from "
            "one or more seed manifests."
        )
    )
    parser.add_argument("--seed-manifest", action="append", type=Path, required=True)
    parser.add_argument("--seed-sample-ids-file", type=Path, required=True)
    parser.add_argument("--search-manifest", action="append", type=Path, required=True)
    parser.add_argument("--numeric-field", action="append", required=True)
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


def project_row(row: dict[str, Any], numeric_fields: list[str]) -> dict[str, Any]:
    return {
        "sample_id": str(row["sample_id"]),
        "split": row.get("split"),
        "recipe": row.get("recipe"),
        "temporal_pattern": row.get("temporal_pattern"),
        "target_present_ratio": row.get("target_present_ratio"),
        "metadata_distance_z": float(row["metadata_distance_z"]),
        "manifest_path": row.get("_manifest_path"),
        "numeric_fields": {
            field: float(row[field])
            for field in numeric_fields
        },
    }


def main() -> None:
    args = parse_args()
    seed_sample_ids = load_sample_ids(args.seed_sample_ids_file)
    if not seed_sample_ids:
        raise ValueError("Seed sample id file is empty.")

    seed_rows_by_id = build_rows_by_id(args.seed_manifest)
    search_rows_by_id = build_rows_by_id(args.search_manifest)

    seed_rows: list[dict[str, Any]] = []
    for sample_id in seed_sample_ids:
        row = seed_rows_by_id.get(sample_id)
        if row is None:
            raise RuntimeError(f"Missing seed sample_id from seed manifests: {sample_id}")
        seed_rows.append(dict(row))

    seed_id_set = set(seed_sample_ids)
    search_rows: list[dict[str, Any]] = [
        dict(row)
        for sample_id, row in search_rows_by_id.items()
        if sample_id not in seed_id_set
    ]

    numeric_fields = list(args.numeric_field)
    usable_seed_rows = [
        row for row in seed_rows
        if all(row.get(field) is not None for field in numeric_fields)
    ]
    usable_search_rows = [
        row for row in search_rows
        if all(row.get(field) is not None for field in numeric_fields)
    ]
    if not usable_seed_rows:
        raise RuntimeError("No usable seed rows with all requested numeric fields.")
    if not usable_search_rows:
        raise RuntimeError("No usable search rows with all requested numeric fields.")

    combined_rows = usable_seed_rows + usable_search_rows
    field_means = {
        field: float(mean(float(row[field]) for row in combined_rows))
        for field in numeric_fields
    }
    field_stdevs = {
        field: float(pstdev(float(row[field]) for row in combined_rows)) or 1.0
        for field in numeric_fields
    }
    seed_center = {
        field: float(mean(float(row[field]) for row in usable_seed_rows))
        for field in numeric_fields
    }

    for row in usable_seed_rows:
        row_values = {field: float(row[field]) for field in numeric_fields}
        row["metadata_distance_z"] = z_distance(
            row_values,
            seed_center,
            field_means,
            field_stdevs,
            numeric_fields,
        )
    for row in usable_search_rows:
        row_values = {field: float(row[field]) for field in numeric_fields}
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

    split_counts = Counter(str(row.get("split")) for row in usable_search_rows)
    recipe_counts = Counter(str(row.get("recipe")) for row in usable_search_rows)
    pattern_counts = Counter(str(row.get("temporal_pattern")) for row in usable_search_rows)

    output = {
        "seed_manifests": [serialize_repo_path(path) for path in args.seed_manifest],
        "seed_sample_ids_file": serialize_repo_path(args.seed_sample_ids_file),
        "seed_sample_ids": seed_sample_ids,
        "search_manifests": [serialize_repo_path(path) for path in args.search_manifest],
        "numeric_fields": numeric_fields,
        "num_usable_seed_rows": len(usable_seed_rows),
        "num_usable_search_rows": len(usable_search_rows),
        "seed_center": seed_center,
        "field_means": field_means,
        "field_stdevs": field_stdevs,
        "seed_rows": [project_row(row, numeric_fields) for row in usable_seed_rows],
        "top_nearest_search_rows": [
            project_row(row, numeric_fields)
            for row in usable_search_rows[: args.top_k]
        ],
        "search_split_counts": dict(sorted(split_counts.items())),
        "search_recipe_counts": dict(sorted(recipe_counts.items())),
        "search_pattern_counts": dict(sorted(pattern_counts.items())),
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
                    str(row["sample_id"]) for row in usable_search_rows[: min(args.top_k, 10)]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
