from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Apply hard near-real phone-artifact gates on top of an existing listening pack. "
            "The gate combines bandwidth narrowing and transient-loss signals."
        )
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
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


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def infer_candidate_label(rows: list[dict[str, Any]], baseline_label: str) -> str:
    labels: set[str] = set()
    for row in rows:
        labels.add(str(row["file_a_label"]))
        labels.add(str(row["file_b_label"]))
    other_labels = sorted(label for label in labels if label != baseline_label)
    if len(other_labels) != 1:
        raise ValueError(f"Could not infer candidate label from labels: {sorted(labels)}")
    return other_labels[0]


def decode_label_choice(row: dict[str, Any], key: str) -> str:
    raw_value = str(row.get(key, "tie"))
    if raw_value == "file_a":
        return str(row["file_a_label"])
    if raw_value == "file_b":
        return str(row["file_b_label"])
    return raw_value


def classify_bucket(sample_meta: dict[str, Any]) -> str:
    scenario = str(sample_meta.get("scenario", "")).strip()
    if scenario == "target_raw_only":
        return "raw_target_only"
    if scenario.startswith("target_absent_") and scenario.endswith("_only"):
        return "target_absent__speech"
    if scenario.startswith("target_plus_") and scenario.endswith("_speech"):
        return "target_present__speech"
    return scenario or "unknown"


def get_count(rows: list[dict[str, Any]], metric_key: str, label: str) -> int:
    return sum(1 for row in rows if str(row.get(metric_key, "tie")) == label)


def build_rule_result(
    *,
    rows: list[dict[str, Any]],
    metric_key: str,
    baseline_label: str,
    candidate_label: str,
    description: str,
) -> dict[str, Any]:
    baseline_count = get_count(rows, metric_key, baseline_label)
    candidate_count = get_count(rows, metric_key, candidate_label)
    passed = candidate_count <= baseline_count
    return {
        "description": description,
        "metric_key": metric_key,
        "criterion": f"{candidate_label} <= {baseline_label}",
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "baseline_count": baseline_count,
        "candidate_count": candidate_count,
        "pass": passed,
    }


def evaluate_bucket(
    *,
    bucket_name: str,
    rows: list[dict[str, Any]],
    baseline_label: str,
    candidate_label: str,
    rules: list[dict[str, str]],
    required: bool = True,
) -> dict[str, Any]:
    if not rows:
        return {
            "bucket_name": bucket_name,
            "present": False,
            "count": 0,
            "required": required,
            "pass": not required,
            "reason": "missing_bucket" if required else "missing_optional_bucket",
            "rules": [],
            "sample_ids": [],
        }

    rule_results = [
        build_rule_result(
            rows=rows,
            metric_key=rule["metric_key"],
            baseline_label=baseline_label,
            candidate_label=candidate_label,
            description=rule["description"],
        )
        for rule in rules
    ]
    return {
        "bucket_name": bucket_name,
        "present": True,
        "count": len(rows),
        "required": required,
        "pass": all(rule["pass"] for rule in rule_results),
        "rules": rule_results,
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "decoded_label_counts": {
            metric_key: {
                baseline_label: get_count(rows, metric_key, baseline_label),
                candidate_label: get_count(rows, metric_key, candidate_label),
                "tie": get_count(rows, metric_key, "tie"),
            }
            for metric_key in sorted({rule["metric_key"] for rule in rules})
        },
    }


def main() -> None:
    args = parse_args()
    output_json = args.output_json or (args.pack_dir / "phone_artifact_gate_summary.json")

    bandwidth_rows_by_id = {
        str(row["sample_id"]): row
        for row in load_jsonl(args.pack_dir / "bandwidth_analysis" / "per_sample_pair_metrics.jsonl")
    }
    transient_rows = load_jsonl(args.pack_dir / "transient_analysis" / "per_sample_pair_metrics.jsonl")
    candidate_label = args.candidate_label or infer_candidate_label(transient_rows, args.baseline_label)

    bucket_rows: dict[str, list[dict[str, Any]]] = {}
    for transient_row in transient_rows:
        sample_id = str(transient_row["sample_id"])
        sample_meta = load_json(args.pack_dir / sample_id / "sample_meta.json")
        bandwidth_row = bandwidth_rows_by_id.get(sample_id)
        combined_row = {
            "sample_id": sample_id,
            "bucket_name": classify_bucket(sample_meta),
            "scenario": str(sample_meta.get("scenario", "")),
            "note": str(sample_meta.get("note", "")),
            "more_transient_lossy_label": decode_label_choice(transient_row, "more_transient_lossy_candidate"),
            "narrower_label": (
                decode_label_choice(bandwidth_row, "narrower_candidate") if bandwidth_row is not None else "not_available"
            ),
        }
        bucket_rows.setdefault(combined_row["bucket_name"], []).append(combined_row)

    bucket_configs = [
        {
            "bucket_name": "raw_target_only",
            "required": True,
            "rules": [
                {
                    "metric_key": "narrower_label",
                    "description": "raw-target-only should not become narrower than baseline",
                },
                {
                    "metric_key": "more_transient_lossy_label",
                    "description": "raw-target-only should not become more transient-lossy than baseline",
                },
            ],
        },
        {
            "bucket_name": "target_present__speech",
            "required": True,
            "rules": [
                {
                    "metric_key": "more_transient_lossy_label",
                    "description": "target-present speech should not become more transient-lossy than baseline",
                }
            ],
        },
        {
            "bucket_name": "target_absent__speech",
            "required": True,
            "rules": [
                {
                    "metric_key": "narrower_label",
                    "description": "target-absent speech should not become narrower than baseline",
                },
                {
                    "metric_key": "more_transient_lossy_label",
                    "description": "target-absent speech should not become more transient-lossy than baseline",
                },
            ],
        },
    ]

    bucket_results = [
        evaluate_bucket(
            bucket_name=config["bucket_name"],
            rows=bucket_rows.get(config["bucket_name"], []),
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
        "pack_dir": serialize_repo_path(args.pack_dir),
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
                "pack_dir": serialize_repo_path(args.pack_dir),
                "baseline_label": args.baseline_label,
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
