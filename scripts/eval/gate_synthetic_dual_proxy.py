from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Gate a candidate against a reference on synthetic proxy summaries. "
            "Useful for cases such as 'keep anchor proxy floor while improving absent proxy'."
        )
    )
    parser.add_argument(
        "--floor-rule",
        action="append",
        default=[],
        help="Rule in the form name=reference_summary.json=candidate_summary.json.",
    )
    parser.add_argument(
        "--improvement-rule",
        action="append",
        default=[],
        help="Rule in the form name=reference_summary.json=candidate_summary.json.",
    )
    parser.add_argument("--floor-margin-db", type=float, default=0.0)
    parser.add_argument("--improvement-margin-db", type=float, default=0.0)
    parser.add_argument("--output-json", type=Path, default=None)
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


def parse_rule(value: str) -> tuple[str, Path, Path]:
    parts = value.split("=", 2)
    if len(parts) != 3:
        raise ValueError(f"Invalid rule value: {value!r}")
    name = parts[0].strip()
    reference_path = Path(parts[1].strip())
    candidate_path = Path(parts[2].strip())
    if not name:
        raise ValueError(f"Empty rule name in: {value!r}")
    return name, reference_path, candidate_path


def overall_delta(summary: dict[str, Any]) -> float:
    return float(summary["overall"]["avg_sisdr_delta_db"])


def build_rule(
    *,
    rule_type: str,
    name: str,
    reference_summary_path: Path,
    candidate_summary_path: Path,
    required_margin_db: float,
) -> dict[str, Any]:
    reference_summary = load_json(reference_summary_path)
    candidate_summary = load_json(candidate_summary_path)
    reference_value = overall_delta(reference_summary)
    candidate_value = overall_delta(candidate_summary)
    required_floor = reference_value + required_margin_db
    return {
        "type": rule_type,
        "name": name,
        "reference_summary": serialize_repo_path(reference_summary_path),
        "candidate_summary": serialize_repo_path(candidate_summary_path),
        "reference_value": reference_value,
        "candidate_value": candidate_value,
        "required_margin_db": required_margin_db,
        "required_floor": required_floor,
        "candidate_minus_reference": candidate_value - reference_value,
        "pass": candidate_value >= required_floor,
    }


def default_output_path(first_candidate_summary: Path) -> Path:
    return first_candidate_summary.with_name("synthetic_dual_proxy_gate_summary.json")


def main() -> None:
    args = parse_args()
    if not args.floor_rule and not args.improvement_rule:
        raise ValueError("At least one --floor-rule or --improvement-rule is required.")

    rules: list[dict[str, Any]] = []
    candidate_paths: list[Path] = []

    for raw_rule in args.floor_rule:
        name, reference_path, candidate_path = parse_rule(raw_rule)
        rules.append(
            build_rule(
                rule_type="floor",
                name=name,
                reference_summary_path=reference_path,
                candidate_summary_path=candidate_path,
                required_margin_db=args.floor_margin_db,
            )
        )
        candidate_paths.append(candidate_path)

    for raw_rule in args.improvement_rule:
        name, reference_path, candidate_path = parse_rule(raw_rule)
        rules.append(
            build_rule(
                rule_type="improvement",
                name=name,
                reference_summary_path=reference_path,
                candidate_summary_path=candidate_path,
                required_margin_db=args.improvement_margin_db,
            )
        )
        candidate_paths.append(candidate_path)

    output_json = args.output_json or default_output_path(candidate_paths[0])
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "floor_margin_db": args.floor_margin_db,
        "improvement_margin_db": args.improvement_margin_db,
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
