from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply hard near-real gates on top of tradeoff_analysis summary.json. "
            "The default gates encode the current objective-only keep/drop rules."
        )
    )
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument("--baseline-label", type=str, default="legacy_stage2")
    parser.add_argument("--candidate-label", type=str, default=None)
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


def infer_candidate_label(summary: dict[str, Any], baseline_label: str) -> str:
    labels = sorted(summary.get("decoded_mean_metrics_by_label", {}).keys())
    other_labels = [label for label in labels if label != baseline_label]
    if len(other_labels) != 1:
        raise ValueError(
            f"Could not infer candidate label from decoded_mean_metrics_by_label: {labels}"
        )
    return other_labels[0]


def get_group(summary: dict[str, Any], bucket_name: str) -> dict[str, Any] | None:
    groups = summary.get("target_interference_bucket_groups", {})
    value = groups.get(bucket_name)
    if not isinstance(value, dict):
        return None
    return value


def get_count(group: dict[str, Any], metric_key: str, label: str) -> int:
    counts = group.get("decoded_label_counts", {}).get(metric_key, {})
    value = counts.get(label, 0)
    return int(value)


def build_rule_result(
    *,
    group: dict[str, Any],
    metric_key: str,
    baseline_label: str,
    candidate_label: str,
    comparator: str,
    description: str,
) -> dict[str, Any]:
    baseline_count = get_count(group, metric_key, baseline_label)
    candidate_count = get_count(group, metric_key, candidate_label)

    if comparator == "candidate_lte_baseline":
        passed = candidate_count <= baseline_count
        criterion = f"{candidate_label} <= {baseline_label}"
    elif comparator == "candidate_gte_baseline":
        passed = candidate_count >= baseline_count
        criterion = f"{candidate_label} >= {baseline_label}"
    else:
        raise ValueError(f"Unsupported comparator: {comparator}")

    return {
        "description": description,
        "metric_key": metric_key,
        "criterion": criterion,
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "baseline_count": baseline_count,
        "candidate_count": candidate_count,
        "pass": passed,
    }


def evaluate_bucket(
    *,
    summary: dict[str, Any],
    bucket_name: str,
    baseline_label: str,
    candidate_label: str,
    rules: list[dict[str, str]],
    required: bool = True,
) -> dict[str, Any]:
    group = get_group(summary, bucket_name)
    if group is None:
        return {
            "bucket_name": bucket_name,
            "present": False,
            "count": 0,
            "required": required,
            "pass": not required,
            "reason": "missing_bucket" if required else "missing_optional_bucket",
            "rules": [],
        }

    rule_results = [
        build_rule_result(
            group=group,
            metric_key=rule["metric_key"],
            baseline_label=baseline_label,
            candidate_label=candidate_label,
            comparator=rule["comparator"],
            description=rule["description"],
        )
        for rule in rules
    ]
    bucket_pass = all(rule["pass"] for rule in rule_results)
    return {
        "bucket_name": bucket_name,
        "present": True,
        "count": int(group.get("count", 0)),
        "required": required,
        "pass": bucket_pass,
        "rules": rule_results,
        "decoded_label_counts": group.get("decoded_label_counts", {}),
        "decoded_mean_metrics_by_label": group.get("decoded_mean_metrics_by_label", {}),
    }


def main() -> None:
    args = parse_args()
    summary = load_json(args.summary_json)
    candidate_label = args.candidate_label or infer_candidate_label(summary, args.baseline_label)
    output_json = args.output_json or args.summary_json.with_name("gate_summary.json")

    # These hard gates encode the current near-real keep/drop logic:
    # 1. speech-only target-present must not be worse on retention-vs-leak, leak, or residual.
    # 2. raw-only target-present must not become more residual-heavy when that bucket exists.
    # 3. target-absent speech must keep at least as much suppression signal as baseline.
    bucket_configs = [
        {
            "bucket_name": "target_present__speech",
            "required": True,
            "rules": [
                {
                    "metric_key": "better_retention_minus_leak_label",
                    "comparator": "candidate_gte_baseline",
                    "description": "speech-only target-present should not lose retention-minus-leak to baseline",
                },
                {
                    "metric_key": "more_interference_leaky_label",
                    "comparator": "candidate_lte_baseline",
                    "description": "speech-only target-present should not be more interference-leaky than baseline",
                },
                {
                    "metric_key": "more_residual_heavy_label",
                    "comparator": "candidate_lte_baseline",
                    "description": "speech-only target-present should not be more residual-heavy than baseline",
                },
            ],
        },
        {
            "bucket_name": "target_present__none",
            "required": False,
            "rules": [
                {
                    "metric_key": "more_residual_heavy_label",
                    "comparator": "candidate_lte_baseline",
                    "description": "raw-only target-present should not be pushed into a more residual-heavy regime",
                }
            ],
        },
        {
            "bucket_name": "target_absent__speech",
            "required": True,
            "rules": [
                {
                    "metric_key": "more_interference_leaky_label",
                    "comparator": "candidate_lte_baseline",
                    "description": "target-absent speech should preserve at least baseline-level suppression",
                }
            ],
        },
    ]

    bucket_results = [
        evaluate_bucket(
            summary=summary,
            bucket_name=config["bucket_name"],
            baseline_label=args.baseline_label,
            candidate_label=candidate_label,
            rules=config["rules"],
            required=bool(config.get("required", True)),
        )
        for config in bucket_configs
    ]

    overall_pass = all(bucket["pass"] for bucket in bucket_results)
    failed_buckets = [bucket["bucket_name"] for bucket in bucket_results if not bucket["pass"]]

    output = {
        "summary_json": serialize_repo_path(args.summary_json),
        "baseline_label": args.baseline_label,
        "candidate_label": candidate_label,
        "overall_pass": overall_pass,
        "failed_buckets": failed_buckets,
        "bucket_results": bucket_results,
    }
    output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "candidate_label": candidate_label,
                "overall_pass": overall_pass,
                "failed_buckets": failed_buckets,
                "output_json": serialize_repo_path(output_json),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
