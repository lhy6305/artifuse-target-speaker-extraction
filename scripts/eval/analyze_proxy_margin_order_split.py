from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Split focused cases by margin zero-cross order using a transition-axis summary."
        )
    )
    parser.add_argument("--transition-summary", type=Path, required=True)
    parser.add_argument("--focus-case", action="append", required=True)
    parser.add_argument("--gap-field", action="append", required=True)
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


def key_gap_name(field: str) -> str:
    mapping = {
        "gap::v66>v64": "v66_minus_v64",
        "gap::v66>v65": "v66_minus_v65",
        "gap::v66>v67": "v66_minus_v67",
        "gap::v64>v67": "v64_minus_v67",
    }
    if field not in mapping:
        raise KeyError(f"Unsupported gap field mapping: {field}")
    return mapping[field]


def stage_label(case_rows: list[dict[str, Any]]) -> str:
    rows_by_field = {row["field"]: row for row in case_rows}
    first = rows_by_field.get("gap::v66>v64")
    second = rows_by_field.get("gap::v66>v65")
    if first is None or second is None:
        return "custom_gap_set"
    if not first["crossed_zero"] and not second["crossed_zero"]:
        return "pre_entry_lowbuffer_edge"
    if not first["crossed_zero"] and second["crossed_zero"]:
        return "hinge_entry_v65_crossed_first"
    if first["crossed_zero"] and second["crossed_zero"]:
        if first["overshoot_vs_zero"] > second["overshoot_vs_zero"]:
            return "post_entry_v64_deeper_than_v65"
        return "post_entry_dual_cross_balanced"
    return "unexpected_order"


def main() -> None:
    args = parse_args()
    summary = load_json(args.transition_summary)
    source_center = summary["source_center"]
    target_center = summary["target_center"]
    case_axes = summary["case_axes"]

    outputs: dict[str, Any] = {}
    gap_zero_thresholds: dict[str, Any] = {}
    for field in args.gap_field:
        source_value = float(source_center[field])
        target_value = float(target_center[field])
        delta = target_value - source_value
        if abs(delta) < 1e-12:
            raise ValueError(f"Gap field has no transition delta: {field}")
        zero_cross_transition_ratio = float(-source_value / delta)
        gap_zero_thresholds[field] = {
            "source_value": source_value,
            "target_value": target_value,
            "zero_cross_transition_ratio": zero_cross_transition_ratio,
            "target_crosses_zero": bool(source_value * target_value <= 0.0),
        }

    for sample_id in args.focus_case:
        if sample_id not in case_axes:
            raise KeyError(f"Focus case missing from transition summary: {sample_id}")
        case_payload = case_axes[sample_id]
        margin_rows = case_payload["margin_axis"]["top_field_progress_outliers"]
        margin_by_field = {row["field"]: row for row in margin_rows}
        # top_field_progress_outliers may omit some fields if top_k < full set; rebuild from key_gaps.
        for field in args.gap_field:
            if field not in margin_by_field:
                raise KeyError(f"Gap field missing from transition summary outliers: {field}")

        gap_rows: list[dict[str, Any]] = []
        for field in args.gap_field:
            source_value = gap_zero_thresholds[field]["source_value"]
            target_value = gap_zero_thresholds[field]["target_value"]
            delta = target_value - source_value
            case_value = float(case_payload["key_gaps"][key_gap_name(field)])
            transition_ratio = float((case_value - source_value) / delta)
            zero_cross_transition_ratio = float(gap_zero_thresholds[field]["zero_cross_transition_ratio"])
            progress_to_zero = float(transition_ratio / zero_cross_transition_ratio)
            crossed_zero = bool(case_value <= 0.0 if source_value > 0.0 else case_value >= 0.0)
            overshoot_vs_zero = float(progress_to_zero - 1.0)
            gap_rows.append(
                {
                    "field": field,
                    "source_value": source_value,
                    "target_value": target_value,
                    "case_value": case_value,
                    "transition_ratio": transition_ratio,
                    "zero_cross_transition_ratio": zero_cross_transition_ratio,
                    "progress_to_zero": progress_to_zero,
                    "crossed_zero": crossed_zero,
                    "overshoot_vs_zero": overshoot_vs_zero,
                }
            )

        outputs[sample_id] = {
            "key_gaps": case_payload["key_gaps"],
            "gap_rows": gap_rows,
            "stage_label": stage_label(gap_rows),
        }

    payload = {
        "transition_summary": serialize_repo_path(args.transition_summary),
        "focus_cases": list(args.focus_case),
        "gap_fields": list(args.gap_field),
        "gap_zero_thresholds": gap_zero_thresholds,
        "case_summaries": outputs,
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
