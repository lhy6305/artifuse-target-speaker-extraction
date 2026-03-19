from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gate a friend speech-leak follow-up by combining default-val, exact speech-leak proxy, "
            "near-real speech-leak anchor, and dedicated guodegang anchor protection."
        )
    )
    parser.add_argument("--reference-default-summary", type=Path, required=True)
    parser.add_argument("--candidate-default-summary", type=Path, required=True)
    parser.add_argument("--reference-exact-summary", type=Path, required=True)
    parser.add_argument("--candidate-exact-summary", type=Path, required=True)
    parser.add_argument("--reference-speech-probe-summary", type=Path, required=True)
    parser.add_argument("--candidate-speech-probe-summary", type=Path, required=True)
    parser.add_argument("--reference-guodegang-anchor-summary", type=Path, required=True)
    parser.add_argument("--candidate-guodegang-anchor-summary", type=Path, required=True)
    parser.add_argument("--reference-guodegang-absent-summary", type=Path, default=None)
    parser.add_argument("--candidate-guodegang-absent-summary", type=Path, default=None)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--max-default-regression-db", type=float, default=0.1)
    parser.add_argument("--max-speech-probe-overall-regression-db", type=float, default=0.05)
    parser.add_argument("--min-exact-full-gain-db", type=float, default=0.0)
    parser.add_argument("--min-speech-leak-gain-db", type=float, default=0.0)
    parser.add_argument("--max-guodegang-anchor-regression-db", type=float, default=0.0)
    parser.add_argument("--max-guodegang-absent-regression-db", type=float, default=0.0)
    parser.add_argument(
        "--near-tie-margin-db",
        type=float,
        default=0.03,
        help=(
            "Extra margin below a rule floor that still counts as near-tie rather than clear fail. "
            "Used only for judgement labeling; overall_pass remains strict."
        ),
    )
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


def build_floor_rule(
    *,
    name: str,
    description: str,
    reference_value: float,
    candidate_value: float,
    floor_value: float,
    near_tie_margin_db: float,
) -> dict[str, Any]:
    margin_to_floor = candidate_value - floor_value
    if candidate_value >= floor_value:
        judgement = "pass"
    elif margin_to_floor >= -near_tie_margin_db:
        judgement = "near_tie"
    else:
        judgement = "clear_fail"
    return {
        "name": name,
        "description": description,
        "reference_value": reference_value,
        "candidate_value": candidate_value,
        "required_floor": floor_value,
        "candidate_minus_reference": candidate_value - reference_value,
        "candidate_minus_floor": margin_to_floor,
        "near_tie_margin_db": near_tie_margin_db,
        "judgement": judgement,
        "pass": candidate_value >= floor_value,
    }


def summarize_overall_judgement(rules: list[dict[str, Any]]) -> tuple[str, list[str], list[str]]:
    near_tie_rules = [str(rule["name"]) for rule in rules if rule.get("judgement") == "near_tie"]
    clear_fail_rules = [str(rule["name"]) for rule in rules if rule.get("judgement") == "clear_fail"]
    if clear_fail_rules:
        return "fail", near_tie_rules, clear_fail_rules
    if near_tie_rules:
        return "near_tie", near_tie_rules, clear_fail_rules
    return "pass", near_tie_rules, clear_fail_rules


def get_default_delta(summary: dict[str, Any]) -> float:
    return float(summary["overall"]["avg_sisdr_delta_db"])


def get_exact_full_delta(summary: dict[str, Any]) -> float:
    return float(summary["pattern_groups"]["target_full"]["avg_sisdr_delta_db"])


def get_speech_leak_delta(summary: dict[str, Any]) -> float:
    return float(summary["hypothesis_groups"]["speech_leak_like"]["avg_sisdr_delta_db"])


def get_overall_delta(summary: dict[str, Any]) -> float:
    return float(summary["overall"]["avg_sisdr_delta_db"])


def main() -> None:
    args = parse_args()

    reference_default = load_json(args.reference_default_summary)
    candidate_default = load_json(args.candidate_default_summary)
    reference_exact = load_json(args.reference_exact_summary)
    candidate_exact = load_json(args.candidate_exact_summary)
    reference_probe = load_json(args.reference_speech_probe_summary)
    candidate_probe = load_json(args.candidate_speech_probe_summary)
    reference_guodegang_anchor = load_json(args.reference_guodegang_anchor_summary)
    candidate_guodegang_anchor = load_json(args.candidate_guodegang_anchor_summary)
    reference_guodegang_absent = (
        load_json(args.reference_guodegang_absent_summary)
        if args.reference_guodegang_absent_summary is not None
        else None
    )
    candidate_guodegang_absent = (
        load_json(args.candidate_guodegang_absent_summary)
        if args.candidate_guodegang_absent_summary is not None
        else None
    )

    baseline_label = str(reference_default["label_a"])
    reference_label = str(reference_default["label_b"])
    candidate_label = str(candidate_default["label_b"])
    if str(candidate_default["label_a"]) != baseline_label:
        raise ValueError(
            f"Mismatched baseline labels: {baseline_label} vs {candidate_default['label_a']}"
        )

    reference_default_delta = get_default_delta(reference_default)
    candidate_default_delta = get_default_delta(candidate_default)
    reference_probe_overall = get_overall_delta(reference_probe)
    candidate_probe_overall = get_overall_delta(candidate_probe)
    reference_exact_full = get_exact_full_delta(reference_exact)
    candidate_exact_full = get_exact_full_delta(candidate_exact)
    reference_speech_leak = get_speech_leak_delta(reference_probe)
    candidate_speech_leak = get_speech_leak_delta(candidate_probe)
    reference_guodegang_anchor_delta = get_overall_delta(reference_guodegang_anchor)
    candidate_guodegang_anchor_delta = get_overall_delta(candidate_guodegang_anchor)

    rules = [
        build_floor_rule(
            name="default_stage2_delta_floor",
            description="candidate should keep most of the reference default-val gain over the shared baseline",
            reference_value=reference_default_delta,
            candidate_value=candidate_default_delta,
            floor_value=reference_default_delta - args.max_default_regression_db,
            near_tie_margin_db=args.near_tie_margin_db,
        ),
        build_floor_rule(
            name="speech_probe_overall_floor",
            description="candidate should not regress the broad near-real speech probe beyond the allowed tolerance",
            reference_value=reference_probe_overall,
            candidate_value=candidate_probe_overall,
            floor_value=reference_probe_overall - args.max_speech_probe_overall_regression_db,
            near_tie_margin_db=args.near_tie_margin_db,
        ),
        build_floor_rule(
            name="exact_target_full_gain_floor",
            description="candidate should improve the exact target_full speech-leak sample relative to reference",
            reference_value=reference_exact_full,
            candidate_value=candidate_exact_full,
            floor_value=reference_exact_full + args.min_exact_full_gain_db,
            near_tie_margin_db=args.near_tie_margin_db,
        ),
        build_floor_rule(
            name="speech_leak_like_gain_floor",
            description="candidate should improve near-real speech_leak_like / anchor 0004 relative to reference",
            reference_value=reference_speech_leak,
            candidate_value=candidate_speech_leak,
            floor_value=reference_speech_leak + args.min_speech_leak_gain_db,
            near_tie_margin_db=args.near_tie_margin_db,
        ),
        build_floor_rule(
            name="guodegang_anchor_floor",
            description="candidate should not regress the dedicated guodegang anchor probe beyond tolerance",
            reference_value=reference_guodegang_anchor_delta,
            candidate_value=candidate_guodegang_anchor_delta,
            floor_value=reference_guodegang_anchor_delta - args.max_guodegang_anchor_regression_db,
            near_tie_margin_db=args.near_tie_margin_db,
        ),
    ]

    if reference_guodegang_absent is not None and candidate_guodegang_absent is not None:
        reference_guodegang_absent_delta = get_overall_delta(reference_guodegang_absent)
        candidate_guodegang_absent_delta = get_overall_delta(candidate_guodegang_absent)
        rules.append(
            build_floor_rule(
                name="guodegang_absent_floor",
                description="candidate should not regress the dedicated guodegang absent probe beyond tolerance",
                reference_value=reference_guodegang_absent_delta,
                candidate_value=candidate_guodegang_absent_delta,
                floor_value=reference_guodegang_absent_delta - args.max_guodegang_absent_regression_db,
                near_tie_margin_db=args.near_tie_margin_db,
            )
        )

    overall_judgement, near_tie_rules, clear_fail_rules = summarize_overall_judgement(rules)

    output_json = args.output_json or args.candidate_speech_probe_summary.with_name(
        "friend_speech_leak_followup_gate_summary.json"
    )
    output = {
        "baseline_label": baseline_label,
        "reference_label": reference_label,
        "candidate_label": candidate_label,
        "inputs": {
            "reference_default_summary": serialize_repo_path(args.reference_default_summary),
            "candidate_default_summary": serialize_repo_path(args.candidate_default_summary),
            "reference_exact_summary": serialize_repo_path(args.reference_exact_summary),
            "candidate_exact_summary": serialize_repo_path(args.candidate_exact_summary),
            "reference_speech_probe_summary": serialize_repo_path(args.reference_speech_probe_summary),
            "candidate_speech_probe_summary": serialize_repo_path(args.candidate_speech_probe_summary),
            "reference_guodegang_anchor_summary": serialize_repo_path(args.reference_guodegang_anchor_summary),
            "candidate_guodegang_anchor_summary": serialize_repo_path(args.candidate_guodegang_anchor_summary),
            "reference_guodegang_absent_summary": (
                serialize_repo_path(args.reference_guodegang_absent_summary)
                if args.reference_guodegang_absent_summary is not None
                else None
            ),
            "candidate_guodegang_absent_summary": (
                serialize_repo_path(args.candidate_guodegang_absent_summary)
                if args.candidate_guodegang_absent_summary is not None
                else None
            ),
        },
        "thresholds": {
            "max_default_regression_db": args.max_default_regression_db,
            "max_speech_probe_overall_regression_db": args.max_speech_probe_overall_regression_db,
            "min_exact_full_gain_db": args.min_exact_full_gain_db,
            "min_speech_leak_gain_db": args.min_speech_leak_gain_db,
            "max_guodegang_anchor_regression_db": args.max_guodegang_anchor_regression_db,
            "max_guodegang_absent_regression_db": args.max_guodegang_absent_regression_db,
            "near_tie_margin_db": args.near_tie_margin_db,
        },
        "summary": {
            "reference_default_stage2_delta_db": reference_default_delta,
            "candidate_default_stage2_delta_db": candidate_default_delta,
            "reference_speech_probe_overall_delta_db": reference_probe_overall,
            "candidate_speech_probe_overall_delta_db": candidate_probe_overall,
            "reference_exact_target_full_delta_db": reference_exact_full,
            "candidate_exact_target_full_delta_db": candidate_exact_full,
            "reference_speech_leak_like_delta_db": reference_speech_leak,
            "candidate_speech_leak_like_delta_db": candidate_speech_leak,
            "reference_guodegang_anchor_delta_db": reference_guodegang_anchor_delta,
            "candidate_guodegang_anchor_delta_db": candidate_guodegang_anchor_delta,
        },
        "rules": rules,
        "overall_judgement": overall_judgement,
        "near_tie_rules": near_tie_rules,
        "clear_fail_rules": clear_fail_rules,
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
                "overall_judgement": output["overall_judgement"],
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
