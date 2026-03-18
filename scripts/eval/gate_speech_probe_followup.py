from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gate a speech-focused follow-up candidate against a reference candidate by combining "
            "the shared-stage2 default compare, near-real speech probe summaries, and optional "
            "near-real hard-gate outputs."
        )
    )
    parser.add_argument("--reference-default-summary", type=Path, required=True)
    parser.add_argument("--candidate-default-summary", type=Path, required=True)
    parser.add_argument("--reference-probe-summary", type=Path, required=True)
    parser.add_argument("--candidate-probe-summary", type=Path, required=True)
    parser.add_argument("--reference-hard-gate-json", type=Path, default=None)
    parser.add_argument("--candidate-hard-gate-json", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--max-default-regression-db", type=float, default=0.2)
    parser.add_argument("--min-anchor-0003-gain-db", type=float, default=0.0)
    parser.add_argument("--min-anchor-0004-gain-db", type=float, default=0.0)
    parser.add_argument("--max-anchor-0006-regression-db", type=float, default=0.1)
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def get_default_overall_delta(summary: dict[str, Any]) -> float:
    return float(summary["overall"]["avg_sisdr_delta_db"])


def get_probe_anchor_delta(summary: dict[str, Any], anchor_name: str) -> float:
    return float(summary["anchor_groups"][anchor_name]["avg_sisdr_delta_db"])


def get_probe_overall_delta(summary: dict[str, Any]) -> float:
    return float(summary["overall"]["avg_sisdr_delta_db"])


def get_probe_family_delta(summary: dict[str, Any], family_name: str) -> float:
    return float(summary["speech_family_groups"][family_name]["avg_sisdr_delta_db"])


def build_floor_rule(
    *,
    name: str,
    description: str,
    reference_value: float,
    candidate_value: float,
    floor_value: float,
) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "reference_value": reference_value,
        "candidate_value": candidate_value,
        "required_floor": floor_value,
        "candidate_minus_reference": candidate_value - reference_value,
        "pass": candidate_value >= floor_value,
    }


def build_hard_gate_rule(
    *,
    reference_gate: dict[str, Any] | None,
    candidate_gate: dict[str, Any] | None,
) -> dict[str, Any]:
    if reference_gate is None or candidate_gate is None:
        return {
            "name": "near_real_hard_gate_nonworse",
            "description": "candidate should not broaden hard-gate failures relative to reference",
            "present": False,
            "pass": True,
            "reason": "missing_gate_json",
        }

    reference_failed = sorted(str(value) for value in reference_gate.get("failed_buckets", []))
    candidate_failed = sorted(str(value) for value in candidate_gate.get("failed_buckets", []))
    candidate_failed_set = set(candidate_failed)
    reference_failed_set = set(reference_failed)
    return {
        "name": "near_real_hard_gate_nonworse",
        "description": "candidate should not broaden hard-gate failures relative to reference",
        "present": True,
        "reference_failed_buckets": reference_failed,
        "candidate_failed_buckets": candidate_failed,
        "pass": candidate_failed_set.issubset(reference_failed_set)
        and len(candidate_failed) <= len(reference_failed),
    }


def main() -> None:
    args = parse_args()

    reference_default = load_json(args.reference_default_summary)
    candidate_default = load_json(args.candidate_default_summary)
    reference_probe = load_json(args.reference_probe_summary)
    candidate_probe = load_json(args.candidate_probe_summary)
    reference_gate = (
        load_json(args.reference_hard_gate_json) if args.reference_hard_gate_json is not None else None
    )
    candidate_gate = (
        load_json(args.candidate_hard_gate_json) if args.candidate_hard_gate_json is not None else None
    )

    reference_label = str(reference_default["label_b"])
    candidate_label = str(candidate_default["label_b"])
    baseline_label = str(reference_default["label_a"])
    if str(candidate_default["label_a"]) != baseline_label:
        raise ValueError(
            f"Mismatched baseline labels: {baseline_label} vs {candidate_default['label_a']}"
        )

    reference_default_delta = get_default_overall_delta(reference_default)
    candidate_default_delta = get_default_overall_delta(candidate_default)
    reference_probe_overall = get_probe_overall_delta(reference_probe)
    candidate_probe_overall = get_probe_overall_delta(candidate_probe)
    reference_friend_delta = get_probe_family_delta(reference_probe, "friend_raw")
    candidate_friend_delta = get_probe_family_delta(candidate_probe, "friend_raw")
    reference_anchor_0003 = get_probe_anchor_delta(reference_probe, "near_real_0003")
    candidate_anchor_0003 = get_probe_anchor_delta(candidate_probe, "near_real_0003")
    reference_anchor_0004 = get_probe_anchor_delta(reference_probe, "near_real_0004")
    candidate_anchor_0004 = get_probe_anchor_delta(candidate_probe, "near_real_0004")
    reference_anchor_0006 = get_probe_anchor_delta(reference_probe, "near_real_0006")
    candidate_anchor_0006 = get_probe_anchor_delta(candidate_probe, "near_real_0006")

    rules = [
        build_floor_rule(
            name="default_stage2_delta_floor",
            description="candidate should keep most of the reference default-val gain over stage2",
            reference_value=reference_default_delta,
            candidate_value=candidate_default_delta,
            floor_value=reference_default_delta - args.max_default_regression_db,
        ),
        build_floor_rule(
            name="speech_probe_overall_floor",
            description="candidate should not be worse than reference on the near-real speech probe overall",
            reference_value=reference_probe_overall,
            candidate_value=candidate_probe_overall,
            floor_value=reference_probe_overall,
        ),
        build_floor_rule(
            name="speech_probe_friend_raw_floor",
            description="candidate should not be worse than reference on friend_raw speech probe cases",
            reference_value=reference_friend_delta,
            candidate_value=candidate_friend_delta,
            floor_value=reference_friend_delta,
        ),
        build_floor_rule(
            name="anchor_0003_gain_floor",
            description="candidate should improve the residual/transient-like anchor 0003 relative to reference",
            reference_value=reference_anchor_0003,
            candidate_value=candidate_anchor_0003,
            floor_value=reference_anchor_0003 + args.min_anchor_0003_gain_db,
        ),
        build_floor_rule(
            name="anchor_0004_gain_floor",
            description="candidate should improve the speech-leak-like anchor 0004 relative to reference",
            reference_value=reference_anchor_0004,
            candidate_value=candidate_anchor_0004,
            floor_value=reference_anchor_0004 + args.min_anchor_0004_gain_db,
        ),
        build_floor_rule(
            name="anchor_0006_regression_floor",
            description="candidate should not regress the transient-like anchor 0006 by more than the allowed tolerance",
            reference_value=reference_anchor_0006,
            candidate_value=candidate_anchor_0006,
            floor_value=reference_anchor_0006 - args.max_anchor_0006_regression_db,
        ),
        build_hard_gate_rule(reference_gate=reference_gate, candidate_gate=candidate_gate),
    ]

    output_json = args.output_json or args.candidate_probe_summary.with_name(
        "speech_followup_gate_summary.json"
    )
    output = {
        "baseline_label": baseline_label,
        "reference_label": reference_label,
        "candidate_label": candidate_label,
        "inputs": {
            "reference_default_summary": serialize_repo_path(args.reference_default_summary),
            "candidate_default_summary": serialize_repo_path(args.candidate_default_summary),
            "reference_probe_summary": serialize_repo_path(args.reference_probe_summary),
            "candidate_probe_summary": serialize_repo_path(args.candidate_probe_summary),
            "reference_hard_gate_json": serialize_repo_path(args.reference_hard_gate_json)
            if args.reference_hard_gate_json is not None
            else None,
            "candidate_hard_gate_json": serialize_repo_path(args.candidate_hard_gate_json)
            if args.candidate_hard_gate_json is not None
            else None,
        },
        "thresholds": {
            "max_default_regression_db": args.max_default_regression_db,
            "min_anchor_0003_gain_db": args.min_anchor_0003_gain_db,
            "min_anchor_0004_gain_db": args.min_anchor_0004_gain_db,
            "max_anchor_0006_regression_db": args.max_anchor_0006_regression_db,
        },
        "summary": {
            "reference_default_stage2_delta_db": reference_default_delta,
            "candidate_default_stage2_delta_db": candidate_default_delta,
            "reference_probe_overall_delta_db": reference_probe_overall,
            "candidate_probe_overall_delta_db": candidate_probe_overall,
            "reference_friend_raw_delta_db": reference_friend_delta,
            "candidate_friend_raw_delta_db": candidate_friend_delta,
            "reference_anchor_0003_delta_db": reference_anchor_0003,
            "candidate_anchor_0003_delta_db": candidate_anchor_0003,
            "reference_anchor_0004_delta_db": reference_anchor_0004,
            "candidate_anchor_0004_delta_db": candidate_anchor_0004,
            "reference_anchor_0006_delta_db": reference_anchor_0006,
            "candidate_anchor_0006_delta_db": candidate_anchor_0006,
        },
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
                "reference_label": reference_label,
                "candidate_label": candidate_label,
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
