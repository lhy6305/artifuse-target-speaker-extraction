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
            "Place focused cases against multiple reference group centers using metadata fields "
            "and compare-derived margin fields."
        )
    )
    parser.add_argument("--manifest", action="append", type=Path, required=True)
    parser.add_argument(
        "--reference-group",
        action="append",
        required=True,
        help="Reference group mapping in the form name=path/to/sample_ids.txt.",
    )
    parser.add_argument("--focus-case", action="append", required=True)
    parser.add_argument("--manifest-field", action="append", default=[])
    parser.add_argument("--metadata-field", action="append", default=[])
    parser.add_argument(
        "--compare",
        action="append",
        default=[],
        help="Compare jsonl mapping in the form alias=path/to/per_sample_metrics.jsonl.",
    )
    parser.add_argument(
        "--derived-gap",
        action="append",
        default=[],
        help="Derived compare gap in the form higher_alias>lower_alias.",
    )
    parser.add_argument("--top-k-fields", type=int, default=6)
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


def parse_mapping(values: list[str], flag_name: str) -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid {flag_name} value: {value!r}")
        name, raw_path = value.split("=", 1)
        name = name.strip()
        path = Path(raw_path.strip())
        if not name:
            raise ValueError(f"Empty name in {flag_name} value: {value!r}")
        if name in mappings:
            raise ValueError(f"Duplicate name in {flag_name}: {name}")
        mappings[name] = path
    return mappings


def parse_gap_specs(values: list[str]) -> list[tuple[str, str]]:
    specs: list[tuple[str, str]] = []
    for value in values:
        if ">" not in value:
            raise ValueError(f"Invalid --derived-gap value: {value!r}")
        higher_alias, lower_alias = value.split(">", 1)
        higher_alias = higher_alias.strip()
        lower_alias = lower_alias.strip()
        if not higher_alias or not lower_alias:
            raise ValueError(f"Invalid --derived-gap value: {value!r}")
        specs.append((higher_alias, lower_alias))
    return specs


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


def field_label_for_gap(higher_alias: str, lower_alias: str) -> str:
    return f"gap::{higher_alias}>{lower_alias}"


def main() -> None:
    args = parse_args()

    manifest_rows_by_id: dict[str, dict[str, Any]] = {}
    for manifest_path in args.manifest:
        for row in load_jsonl(manifest_path):
            sample_id = str(row["sample_id"])
            if sample_id in manifest_rows_by_id:
                raise ValueError(f"Duplicate sample_id across manifests: {sample_id}")
            manifest_rows_by_id[sample_id] = row

    metadata_cache: dict[Path, dict[str, Any]] = {}

    def metadata_payload_for(sample_id: str) -> dict[str, Any]:
        row = manifest_rows_by_id[sample_id]
        metadata_path = resolve_repo_path(str(row.get("metadata_path") or ""))
        if metadata_path is None:
            return {}
        if metadata_path not in metadata_cache:
            metadata_cache[metadata_path] = load_json(metadata_path)
        return metadata_cache[metadata_path]

    compare_map = parse_mapping(list(args.compare), "--compare")
    compare_rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    for alias, compare_path in compare_map.items():
        compare_rows_by_alias[alias] = {
            str(row["sample_id"]): row
            for row in load_jsonl(compare_path)
        }

    gap_specs = parse_gap_specs(list(args.derived_gap))

    reference_group_map = parse_mapping(list(args.reference_group), "--reference-group")
    reference_group_ids: dict[str, list[str]] = {}
    for group_name, sample_ids_path in reference_group_map.items():
        sample_ids = load_sample_ids(sample_ids_path)
        if not sample_ids:
            raise ValueError(f"Reference group is empty: {group_name}")
        missing = [sample_id for sample_id in sample_ids if sample_id not in manifest_rows_by_id]
        if missing:
            raise RuntimeError(f"Reference group {group_name} missing sample ids from manifest: {missing}")
        reference_group_ids[group_name] = sample_ids

    focus_cases = list(dict.fromkeys(str(sample_id) for sample_id in args.focus_case))
    if not focus_cases:
        raise ValueError("At least one --focus-case is required.")
    missing_focus = [sample_id for sample_id in focus_cases if sample_id not in manifest_rows_by_id]
    if missing_focus:
        raise RuntimeError(f"Focus cases missing from manifest: {missing_focus}")

    all_case_ids = list(
        dict.fromkeys(
            [sample_id for sample_ids in reference_group_ids.values() for sample_id in sample_ids]
            + focus_cases
        )
    )

    numeric_rows: dict[str, dict[str, float]] = {}
    metadata_payloads = {sample_id: metadata_payload_for(sample_id) for sample_id in all_case_ids}

    margin_field_names = [field_label_for_gap(higher_alias, lower_alias) for higher_alias, lower_alias in gap_specs]
    metadata_field_names = list(args.manifest_field) + list(args.metadata_field)
    all_field_names = metadata_field_names + margin_field_names

    for sample_id in all_case_ids:
        row = manifest_rows_by_id[sample_id]
        payload = metadata_payloads[sample_id]
        numeric_values: dict[str, float] = {}
        for field_name in args.manifest_field:
            value = row.get(field_name)
            if value is None:
                raise RuntimeError(f"Manifest field missing for {sample_id}: {field_name}")
            numeric_values[field_name] = float(value)
        for field_name in args.metadata_field:
            value = get_nested_value(payload, field_name)
            if value is None:
                raise RuntimeError(f"Metadata field missing for {sample_id}: {field_name}")
            numeric_values[field_name] = float(value)
        for higher_alias, lower_alias in gap_specs:
            higher_rows = compare_rows_by_alias.get(higher_alias)
            lower_rows = compare_rows_by_alias.get(lower_alias)
            if higher_rows is None or lower_rows is None:
                raise RuntimeError(f"Missing compare rows for gap {higher_alias}>{lower_alias}")
            if sample_id not in higher_rows or sample_id not in lower_rows:
                raise RuntimeError(f"Sample {sample_id} missing compare rows for gap {higher_alias}>{lower_alias}")
            numeric_values[field_label_for_gap(higher_alias, lower_alias)] = float(
                higher_rows[sample_id]["sisdr_b_db"] - lower_rows[sample_id]["sisdr_b_db"]
            )
        numeric_rows[sample_id] = numeric_values

    field_means: dict[str, float] = {}
    field_stdevs: dict[str, float] = {}
    for field_name in all_field_names:
        values = [numeric_rows[sample_id][field_name] for sample_id in all_case_ids]
        field_means[field_name] = float(mean(values))
        stdev = float(pstdev(values)) if len(values) > 1 else 0.0
        if stdev == 0.0:
            stdev = 1.0
        field_stdevs[field_name] = stdev

    def center_for_group(group_sample_ids: list[str]) -> dict[str, float]:
        return {
            field_name: float(mean([numeric_rows[sample_id][field_name] for sample_id in group_sample_ids]))
            for field_name in all_field_names
        }

    reference_group_centers = {
        group_name: center_for_group(sample_ids)
        for group_name, sample_ids in reference_group_ids.items()
    }

    case_positioning: dict[str, Any] = {}
    for sample_id in focus_cases:
        row = manifest_rows_by_id[sample_id]
        scores = {
            alias: float(compare_rows_by_alias[alias][sample_id]["sisdr_b_db"])
            for alias in compare_map
        }
        ranking = [
            alias
            for alias, _score in sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        ]

        distances: list[dict[str, Any]] = []
        for group_name, base_group_ids in reference_group_ids.items():
            effective_group_ids = [value for value in base_group_ids if value != sample_id]
            leave_one_out_applied = len(effective_group_ids) != len(base_group_ids)
            if not effective_group_ids:
                raise RuntimeError(f"Reference group {group_name} became empty after leave-one-out for {sample_id}")
            group_center = center_for_group(effective_group_ids) if leave_one_out_applied else reference_group_centers[group_name]

            field_rows: list[dict[str, Any]] = []
            total_sq = 0.0
            metadata_sq = 0.0
            margin_sq = 0.0
            for field_name in all_field_names:
                stdev = field_stdevs[field_name]
                signed_delta = numeric_rows[sample_id][field_name] - group_center[field_name]
                signed_z_delta = signed_delta / stdev
                contribution = signed_z_delta**2
                total_sq += contribution
                if field_name in margin_field_names:
                    margin_sq += contribution
                    category = "margin"
                else:
                    metadata_sq += contribution
                    category = "metadata"
                field_rows.append(
                    {
                        "field": field_name,
                        "category": category,
                        "case_value": numeric_rows[sample_id][field_name],
                        "group_mean": group_center[field_name],
                        "signed_delta": signed_delta,
                        "signed_z_delta": signed_z_delta,
                        "abs_z_delta": abs(signed_z_delta),
                    }
                )

            field_rows.sort(key=lambda item: (-item["abs_z_delta"], item["field"]))
            distances.append(
                {
                    "reference_group": group_name,
                    "reference_group_size": len(effective_group_ids),
                    "leave_one_out_applied": leave_one_out_applied,
                    "distance_total_z": math.sqrt(total_sq),
                    "distance_metadata_z": math.sqrt(metadata_sq),
                    "distance_margin_z": math.sqrt(margin_sq),
                    "top_field_deviations": field_rows[: args.top_k_fields],
                }
            )

        distances.sort(key=lambda item: (item["distance_total_z"], item["reference_group"]))
        best_distance = distances[0]["distance_total_z"]
        second_distance = distances[1]["distance_total_z"] if len(distances) > 1 else None

        case_positioning[sample_id] = {
            "raw_values": {
                **numeric_rows[sample_id],
                "scores": scores,
                "ranking": ranking,
                "target_duration_sec": float(get_nested_value(metadata_payloads[sample_id], "target_duration_sec")),
                "reference_duration_sec": float(get_nested_value(metadata_payloads[sample_id], "reference_duration_sec")),
                "interference_gain_db": float(get_nested_value(metadata_payloads[sample_id], "interference_layers.0.gain_db")),
                "interference_start_offset_sec": float(
                    get_nested_value(metadata_payloads[sample_id], "interference_layers.0.start_offset_sec")
                ),
            },
            "nearest_reference_group": distances[0]["reference_group"],
            "distance_margin_vs_second_best": (
                None if second_distance is None else float(second_distance - best_distance)
            ),
            "distances": distances,
        }

    summary = {
        "manifests": [serialize_repo_path(path) for path in args.manifest],
        "reference_groups": {
            group_name: {
                "sample_ids_file": serialize_repo_path(path),
                "sample_ids": reference_group_ids[group_name],
                "center": reference_group_centers[group_name],
            }
            for group_name, path in reference_group_map.items()
        },
        "focus_cases": focus_cases,
        "metadata_fields": metadata_field_names,
        "margin_fields": margin_field_names,
        "field_means": field_means,
        "field_stdevs": field_stdevs,
        "case_positioning": case_positioning,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as fh:
        json.dump(summary, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
