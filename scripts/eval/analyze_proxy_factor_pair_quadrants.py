from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
QUADRANT_ORDER = ["both", "factor_a_only", "factor_b_only", "neither"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build target-side quadrants for two factors against a shared-shelf baseline, then report "
            "which branch states land in each quadrant and where the target / contrast anchors sit."
        )
    )
    parser.add_argument("--neighbor-json", type=Path, required=True)
    parser.add_argument("--split-json", type=Path, required=True)
    parser.add_argument("--target-group", type=str, required=True)
    parser.add_argument("--baseline-group", type=str, required=True)
    parser.add_argument("--contrast-group", type=str, required=True)
    parser.add_argument("--factor-a", type=str, required=True)
    parser.add_argument("--factor-b", type=str, required=True)
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


def classify_state(row: dict[str, Any]) -> str:
    compare_summary = row["compare_summary"]
    g64 = float(compare_summary["candidate_gap_vs_aliases_db"]["v64"])
    g65 = float(compare_summary["candidate_gap_vs_aliases_db"]["v65"])
    if g64 > 0.0 and g65 > 0.0:
        return "pre_entry_or_pure"
    if g64 > 0.0 and g65 <= 0.0:
        return "hinge_v65_crossed"
    if g64 <= 0.0 and g65 <= 0.0:
        if g65 < g64:
            return "both_crossed_v65_deeper"
        return "both_crossed_v64_deeper"
    return "v64_only_crossed"


def build_factor_spec(
    group_summaries: dict[str, Any],
    target_group: str,
    baseline_group: str,
    field: str,
) -> dict[str, Any]:
    target_value = float(group_summaries[target_group]["numeric_field_means"][field])
    baseline_value = float(group_summaries[baseline_group]["numeric_field_means"][field])
    midpoint = (target_value + baseline_value) / 2.0
    target_lower_than_baseline = target_value < baseline_value
    return {
        "field": field,
        "target_value": target_value,
        "baseline_value": baseline_value,
        "midpoint": midpoint,
        "target_direction": "lower" if target_lower_than_baseline else "higher",
    }


def on_target_side(value: float, spec: dict[str, Any]) -> bool:
    if spec["target_direction"] == "lower":
        return value < float(spec["midpoint"])
    return value > float(spec["midpoint"])


def quadrant_for(row: dict[str, Any], factor_a: dict[str, Any], factor_b: dict[str, Any]) -> str:
    a_side = on_target_side(float(row["numeric_values"][factor_a["field"]]), factor_a)
    b_side = on_target_side(float(row["numeric_values"][factor_b["field"]]), factor_b)
    if a_side and b_side:
        return "both"
    if a_side:
        return "factor_a_only"
    if b_side:
        return "factor_b_only"
    return "neither"


def anchor_quadrant(
    group_summary: dict[str, Any],
    factor_a: dict[str, Any],
    factor_b: dict[str, Any],
) -> dict[str, Any]:
    values = group_summary["numeric_field_means"]
    a_side = on_target_side(float(values[factor_a["field"]]), factor_a)
    b_side = on_target_side(float(values[factor_b["field"]]), factor_b)
    if a_side and b_side:
        quadrant = "both"
    elif a_side:
        quadrant = "factor_a_only"
    elif b_side:
        quadrant = "factor_b_only"
    else:
        quadrant = "neither"
    return {
        "sample_ids": list(group_summary["sample_ids"]),
        "quadrant": quadrant,
        "factor_a_value": float(values[factor_a["field"]]),
        "factor_b_value": float(values[factor_b["field"]]),
    }


def main() -> None:
    args = parse_args()
    neighbor_payload = load_json(args.neighbor_json)
    split_payload = load_json(args.split_json)
    group_summaries = split_payload["group_summaries"]

    factor_a = build_factor_spec(
        group_summaries=group_summaries,
        target_group=args.target_group,
        baseline_group=args.baseline_group,
        field=args.factor_a,
    )
    factor_b = build_factor_spec(
        group_summaries=group_summaries,
        target_group=args.target_group,
        baseline_group=args.baseline_group,
        field=args.factor_b,
    )

    rows_by_quadrant: dict[str, list[dict[str, Any]]] = {key: [] for key in QUADRANT_ORDER}
    for row in neighbor_payload["top_nearest_search_rows"]:
        quadrant = quadrant_for(row=row, factor_a=factor_a, factor_b=factor_b)
        rows_by_quadrant[quadrant].append(
            {
                "sample_id": str(row["sample_id"]),
                "state": classify_state(row),
                "metadata_distance_z": float(row["metadata_distance_z"]),
                "factor_a_value": float(row["numeric_values"][factor_a["field"]]),
                "factor_b_value": float(row["numeric_values"][factor_b["field"]]),
            }
        )

    quadrant_summaries: dict[str, Any] = {}
    for quadrant in QUADRANT_ORDER:
        rows = rows_by_quadrant[quadrant]
        rows.sort(key=lambda item: (float(item["metadata_distance_z"]), str(item["sample_id"])))
        quadrant_summaries[quadrant] = {
            "count": len(rows),
            "state_counts": dict(sorted(Counter(str(row["state"]) for row in rows).items())),
            "sample_ids": [row["sample_id"] for row in rows],
            "rows": rows,
        }

    anchor_quadrants = {
        "target_group": anchor_quadrant(group_summaries[args.target_group], factor_a, factor_b),
        "baseline_group": anchor_quadrant(group_summaries[args.baseline_group], factor_a, factor_b),
        "contrast_group": anchor_quadrant(group_summaries[args.contrast_group], factor_a, factor_b),
    }

    output = {
        "neighbor_json": serialize_repo_path(args.neighbor_json),
        "split_json": serialize_repo_path(args.split_json),
        "target_group": args.target_group,
        "baseline_group": args.baseline_group,
        "contrast_group": args.contrast_group,
        "factor_a": factor_a,
        "factor_b": factor_b,
        "anchor_quadrants": anchor_quadrants,
        "quadrant_summaries": quadrant_summaries,
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
                "target_quadrant": anchor_quadrants["target_group"]["quadrant"],
                "contrast_quadrant": anchor_quadrants["contrast_group"]["quadrant"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
