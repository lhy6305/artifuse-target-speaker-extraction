from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare one branch against a shared-shelf baseline while using another branch as a distractor, "
            "so sink-specific or pocket-specific factor residuals can be ranked explicitly."
        )
    )
    parser.add_argument("--split-json", type=Path, required=True)
    parser.add_argument("--scale-json", type=Path)
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


def pairwise_delta(
    group_summaries: dict[str, Any],
    left_name: str,
    right_name: str,
    field: str,
) -> float:
    left = float(group_summaries[left_name]["numeric_field_means"][field])
    right = float(group_summaries[right_name]["numeric_field_means"][field])
    return left - right


def main() -> None:
    args = parse_args()
    split_payload = load_json(args.split_json)
    scale_payload = load_json(args.scale_json) if args.scale_json else split_payload

    group_summaries = split_payload["group_summaries"]
    if args.target_group not in group_summaries:
        raise KeyError(f"Unknown target group: {args.target_group}")
    if args.baseline_group not in group_summaries:
        raise KeyError(f"Unknown baseline group: {args.baseline_group}")
    if args.contrast_group not in group_summaries:
        raise KeyError(f"Unknown contrast group: {args.contrast_group}")

    field_stdevs = scale_payload.get("field_stdevs", {})
    rows: list[dict[str, Any]] = []
    for field in args.factor_field:
        target_minus_baseline = pairwise_delta(
            group_summaries,
            left_name=args.target_group,
            right_name=args.baseline_group,
            field=field,
        )
        contrast_minus_baseline = pairwise_delta(
            group_summaries,
            left_name=args.contrast_group,
            right_name=args.baseline_group,
            field=field,
        )
        target_specific_residual = target_minus_baseline - contrast_minus_baseline
        scale = float(field_stdevs.get(field, 1.0)) or 1.0
        rows.append(
            {
                "field": field,
                "target_minus_baseline": target_minus_baseline,
                "contrast_minus_baseline": contrast_minus_baseline,
                "target_specific_residual": target_specific_residual,
                "abs_target_specific_residual": abs(target_specific_residual),
                "scale_stdev": scale,
                "target_specific_residual_z": target_specific_residual / scale,
                "abs_target_specific_residual_z": abs(target_specific_residual / scale),
            }
        )

    rows.sort(
        key=lambda item: (
            -float(item["abs_target_specific_residual_z"]),
            -float(item["abs_target_specific_residual"]),
            str(item["field"]),
        )
    )

    output = {
        "split_json": serialize_repo_path(args.split_json),
        "scale_json": serialize_repo_path(args.scale_json) if args.scale_json else None,
        "target_group": args.target_group,
        "baseline_group": args.baseline_group,
        "contrast_group": args.contrast_group,
        "factor_fields": list(args.factor_field),
        "rows_ranked_by_target_specific_residual_z": rows,
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
                "top_fields": [row["field"] for row in rows[:3]],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
