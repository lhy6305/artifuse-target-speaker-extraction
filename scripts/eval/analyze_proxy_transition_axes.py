from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Project focused cases onto metadata-axis and margin-axis transitions between "
            "two reference groups using a positioning summary."
        )
    )
    parser.add_argument("--positioning-summary", type=Path, required=True)
    parser.add_argument("--source-group", type=str, required=True)
    parser.add_argument("--target-group", type=str, required=True)
    parser.add_argument("--focus-case", action="append", required=True)
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


def z_value(value: float, mean_value: float, stdev_value: float) -> float:
    return (value - mean_value) / stdev_value


def project_case(
    case_values: dict[str, float],
    source_center: dict[str, float],
    target_center: dict[str, float],
    field_means: dict[str, float],
    field_stdevs: dict[str, float],
    fields: list[str],
) -> tuple[float, float]:
    source_vec = [z_value(source_center[field], field_means[field], field_stdevs[field]) for field in fields]
    target_vec = [z_value(target_center[field], field_means[field], field_stdevs[field]) for field in fields]
    case_vec = [z_value(case_values[field], field_means[field], field_stdevs[field]) for field in fields]
    direction = [target_value - source_value for source_value, target_value in zip(source_vec, target_vec)]
    numerator = sum(
        (case_value - source_value) * direction_value
        for case_value, source_value, direction_value in zip(case_vec, source_vec, direction)
    )
    denominator = sum(direction_value * direction_value for direction_value in direction)
    transition_ratio = numerator / denominator if denominator else 0.0
    residual = math.sqrt(
        sum(
            (
                case_value
                - (source_value + transition_ratio * direction_value)
            )
            ** 2
            for case_value, source_value, direction_value in zip(case_vec, source_vec, direction)
        )
    )
    return float(transition_ratio), float(residual)


def build_field_progress_rows(
    case_values: dict[str, float],
    source_center: dict[str, float],
    target_center: dict[str, float],
    field_means: dict[str, float],
    field_stdevs: dict[str, float],
    fields: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in fields:
        path_z = z_value(target_center[field], field_means[field], field_stdevs[field]) - z_value(
            source_center[field],
            field_means[field],
            field_stdevs[field],
        )
        case_from_source_z = z_value(case_values[field], field_means[field], field_stdevs[field]) - z_value(
            source_center[field],
            field_means[field],
            field_stdevs[field],
        )
        transition_ratio = None if abs(path_z) < 1e-12 else float(case_from_source_z / path_z)
        rows.append(
            {
                "field": field,
                "source_value": source_center[field],
                "target_value": target_center[field],
                "case_value": case_values[field],
                "path_z": float(path_z),
                "case_from_source_z": float(case_from_source_z),
                "field_transition_ratio": transition_ratio,
                "path_direction_match": None if transition_ratio is None else bool(transition_ratio >= 0.0),
            }
        )
    return rows


def main() -> None:
    args = parse_args()
    summary = load_json(args.positioning_summary)

    reference_groups = summary["reference_groups"]
    if args.source_group not in reference_groups:
        raise KeyError(f"Unknown --source-group: {args.source_group}")
    if args.target_group not in reference_groups:
        raise KeyError(f"Unknown --target-group: {args.target_group}")

    source_center = reference_groups[args.source_group]["center"]
    target_center = reference_groups[args.target_group]["center"]
    field_means = summary["field_means"]
    field_stdevs = summary["field_stdevs"]
    metadata_fields = list(summary["metadata_fields"])
    margin_fields = list(summary["margin_fields"])

    outputs: dict[str, Any] = {}
    for sample_id in args.focus_case:
        case_position = summary["case_positioning"].get(sample_id)
        if case_position is None:
            raise KeyError(f"Focus case missing from positioning summary: {sample_id}")
        raw_values = case_position["raw_values"]

        metadata_transition_ratio, metadata_residual_z = project_case(
            raw_values,
            source_center,
            target_center,
            field_means,
            field_stdevs,
            metadata_fields,
        )
        margin_transition_ratio, margin_residual_z = project_case(
            raw_values,
            source_center,
            target_center,
            field_means,
            field_stdevs,
            margin_fields,
        )

        metadata_rows = build_field_progress_rows(
            raw_values,
            source_center,
            target_center,
            field_means,
            field_stdevs,
            metadata_fields,
        )
        margin_rows = build_field_progress_rows(
            raw_values,
            source_center,
            target_center,
            field_means,
            field_stdevs,
            margin_fields,
        )
        metadata_rows.sort(
            key=lambda row: (
                -abs(float(row["field_transition_ratio"]) - metadata_transition_ratio)
                if row["field_transition_ratio"] is not None
                else float("-inf"),
                row["field"],
            )
        )
        margin_rows.sort(
            key=lambda row: (
                -abs(float(row["field_transition_ratio"]) - margin_transition_ratio)
                if row["field_transition_ratio"] is not None
                else float("-inf"),
                row["field"],
            )
        )

        outputs[sample_id] = {
            "ranking": raw_values["ranking"],
            "scores": raw_values["scores"],
            "metadata_axis": {
                "transition_ratio": metadata_transition_ratio,
                "residual_z": metadata_residual_z,
                "top_field_progress_outliers": metadata_rows[: args.top_k_fields],
            },
            "margin_axis": {
                "transition_ratio": margin_transition_ratio,
                "residual_z": margin_residual_z,
                "top_field_progress_outliers": margin_rows[: args.top_k_fields],
            },
            "key_gaps": {
                "v66_minus_v64": raw_values["gap::v66>v64"],
                "v66_minus_v65": raw_values["gap::v66>v65"],
                "v66_minus_v67": raw_values["gap::v66>v67"],
                "v64_minus_v67": raw_values["gap::v64>v67"],
            },
        }

    payload = {
        "positioning_summary": serialize_repo_path(args.positioning_summary),
        "source_group": args.source_group,
        "target_group": args.target_group,
        "focus_cases": list(args.focus_case),
        "metadata_fields": metadata_fields,
        "margin_fields": margin_fields,
        "source_center": source_center,
        "target_center": target_center,
        "case_axes": outputs,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
