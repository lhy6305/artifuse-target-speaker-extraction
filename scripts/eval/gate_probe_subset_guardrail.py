from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gate a candidate probe summary against a reference probe summary for a focused subset "
            "such as near_real_0006 / guodegang."
        )
    )
    parser.add_argument("--reference-summary", type=Path, required=True)
    parser.add_argument("--candidate-summary", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--check-overall", action="store_true")
    parser.add_argument("--family-names", nargs="*", default=[])
    parser.add_argument("--anchor-names", nargs="*", default=[])
    parser.add_argument("--clip-tags", nargs="*", default=[])
    parser.add_argument("--required-margin-db", type=float, default=0.0)
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def get_group_delta(summary: dict[str, Any], group_name: str, key: str) -> float:
    return float(summary[key][group_name]["avg_sisdr_delta_db"])


def build_rule(
    *,
    name: str,
    description: str,
    reference_value: float,
    candidate_value: float,
    required_margin_db: float,
) -> dict[str, Any]:
    required_floor = reference_value + required_margin_db
    return {
        "name": name,
        "description": description,
        "reference_value": reference_value,
        "candidate_value": candidate_value,
        "required_floor": required_floor,
        "candidate_minus_reference": candidate_value - reference_value,
        "pass": candidate_value >= required_floor,
    }


def main() -> None:
    args = parse_args()
    reference_summary = load_json(args.reference_summary)
    candidate_summary = load_json(args.candidate_summary)

    rules: list[dict[str, Any]] = []
    if args.check_overall:
        rules.append(
            build_rule(
                name="overall_floor",
                description="candidate should not underperform the reference on the focused probe overall",
                reference_value=float(reference_summary["overall"]["avg_sisdr_delta_db"]),
                candidate_value=float(candidate_summary["overall"]["avg_sisdr_delta_db"]),
                required_margin_db=args.required_margin_db,
            )
        )

    for family_name in args.family_names:
        rules.append(
            build_rule(
                name=f"family__{family_name}",
                description=f"candidate should not underperform the reference on family {family_name}",
                reference_value=get_group_delta(reference_summary, family_name, "speech_family_groups"),
                candidate_value=get_group_delta(candidate_summary, family_name, "speech_family_groups"),
                required_margin_db=args.required_margin_db,
            )
        )

    for anchor_name in args.anchor_names:
        rules.append(
            build_rule(
                name=f"anchor__{anchor_name}",
                description=f"candidate should not underperform the reference on anchor {anchor_name}",
                reference_value=get_group_delta(reference_summary, anchor_name, "anchor_groups"),
                candidate_value=get_group_delta(candidate_summary, anchor_name, "anchor_groups"),
                required_margin_db=args.required_margin_db,
            )
        )

    for clip_tag in args.clip_tags:
        rules.append(
            build_rule(
                name=f"clip__{clip_tag}",
                description=f"candidate should not underperform the reference on clip tag {clip_tag}",
                reference_value=get_group_delta(reference_summary, clip_tag, "speech_clip_groups"),
                candidate_value=get_group_delta(candidate_summary, clip_tag, "speech_clip_groups"),
                required_margin_db=args.required_margin_db,
            )
        )

    output_json = args.output_json or args.candidate_summary.with_name("probe_subset_guardrail_summary.json")
    output = {
        "reference_summary": serialize_repo_path(args.reference_summary),
        "candidate_summary": serialize_repo_path(args.candidate_summary),
        "required_margin_db": args.required_margin_db,
        "rules": rules,
        "overall_pass": all(bool(rule["pass"]) for rule in rules),
        "failed_rules": [str(rule["name"]) for rule in rules if not rule["pass"]],
    }
    output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "overall_pass": output["overall_pass"],
                "failed_rules": output["failed_rules"],
                "output_json": serialize_repo_path(output_json),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
