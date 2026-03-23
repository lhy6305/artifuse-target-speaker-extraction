from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Slice a neighbor scan by target-vs-baseline midpoint for selected factors, then report "
            "which branch states are supported on the target side and whether the contrast branch shares that side."
        )
    )
    parser.add_argument("--neighbor-json", type=Path, required=True)
    parser.add_argument("--split-json", type=Path, required=True)
    parser.add_argument("--target-group", type=str, required=True)
    parser.add_argument("--baseline-group", type=str, required=True)
    parser.add_argument("--contrast-group", type=str, required=True)
    parser.add_argument("--factor-field", action="append", default=[], required=True)
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


def main() -> None:
    args = parse_args()
    neighbor_payload = load_json(args.neighbor_json)
    split_payload = load_json(args.split_json)
    group_summaries = split_payload["group_summaries"]

    target_summary = group_summaries[args.target_group]
    baseline_summary = group_summaries[args.baseline_group]
    contrast_summary = group_summaries[args.contrast_group]

    rows = neighbor_payload["top_nearest_search_rows"]
    output_rows: list[dict[str, Any]] = []
    for field in args.factor_field:
        target_value = float(target_summary["numeric_field_means"][field])
        baseline_value = float(baseline_summary["numeric_field_means"][field])
        contrast_value = float(contrast_summary["numeric_field_means"][field])
        midpoint = (target_value + baseline_value) / 2.0
        target_lower_than_baseline = target_value < baseline_value

        def on_target_side(value: float) -> bool:
            if target_lower_than_baseline:
                return value < midpoint
            return value > midpoint

        target_side_rows = []
        target_side_counts = Counter()
        for row in rows:
            value = float(row["numeric_values"][field])
            if on_target_side(value):
                state = classify_state(row)
                target_side_counts[state] += 1
                target_side_rows.append(
                    {
                        "sample_id": str(row["sample_id"]),
                        "state": state,
                        "value": value,
                        "metadata_distance_z": float(row["metadata_distance_z"]),
                    }
                )

        target_side_rows.sort(key=lambda item: (float(item["metadata_distance_z"]), str(item["sample_id"])))
        contrast_on_target_side = on_target_side(contrast_value)
        output_rows.append(
            {
                "field": field,
                "target_value": target_value,
                "baseline_value": baseline_value,
                "contrast_value": contrast_value,
                "midpoint": midpoint,
                "target_direction": "lower" if target_lower_than_baseline else "higher",
                "contrast_on_target_side": contrast_on_target_side,
                "target_side_state_counts": dict(sorted(target_side_counts.items())),
                "target_side_sample_ids": [item["sample_id"] for item in target_side_rows],
                "target_side_rows": target_side_rows,
            }
        )

    output = {
        "neighbor_json": serialize_repo_path(args.neighbor_json),
        "split_json": serialize_repo_path(args.split_json),
        "target_group": args.target_group,
        "baseline_group": args.baseline_group,
        "contrast_group": args.contrast_group,
        "factor_fields": list(args.factor_field),
        "rows": output_rows,
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
                "fields": [row["field"] for row in output_rows],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
