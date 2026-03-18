from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Diagnose sample-level failure modes inside a near-real bucket by merging "
            "tradeoff, bandwidth, and transient analyses from an existing listening pack."
        )
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--bucket-name", type=str, default="target_present__speech")
    parser.add_argument("--baseline-label", type=str, default="legacy_stage2")
    parser.add_argument("--candidate-label", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
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


def get_metrics_for_label(row: dict[str, Any], label: str) -> dict[str, Any]:
    if str(row["file_a_label"]) == label:
        return dict(row["file_a_metrics"])
    if str(row["file_b_label"]) == label:
        return dict(row["file_b_metrics"])
    raise KeyError(f"Label {label} not present in row {row.get('sample_id')}")


def decode_label_choice(row: dict[str, Any], key: str) -> str:
    raw_value = str(row[key])
    if raw_value == "file_a":
        return str(row["file_a_label"])
    if raw_value == "file_b":
        return str(row["file_b_label"])
    return raw_value


def subtract_optional(candidate_value: Any, baseline_value: Any) -> float | None:
    if candidate_value is None or baseline_value is None:
        return None
    return float(candidate_value) - float(baseline_value)


def make_signature(flags: list[str]) -> str:
    if not flags:
        return "none"
    return " + ".join(flags)


def mean_optional(values: list[float | None]) -> float | None:
    filtered = [float(value) for value in values if value is not None]
    if not filtered:
        return None
    return float(sum(filtered) / len(filtered))


def count_values(values: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_row_diagnosis(
    tradeoff_row: dict[str, Any],
    bandwidth_row: dict[str, Any] | None,
    transient_row: dict[str, Any] | None,
    *,
    baseline_label: str,
    candidate_label: str,
) -> dict[str, Any]:
    baseline_tradeoff = get_metrics_for_label(tradeoff_row, baseline_label)
    candidate_tradeoff = get_metrics_for_label(tradeoff_row, candidate_label)

    better_source_retention_label = decode_label_choice(tradeoff_row, "better_source_retention_candidate")
    more_interference_leaky_label = decode_label_choice(tradeoff_row, "more_interference_leaky_candidate")
    more_residual_heavy_label = decode_label_choice(tradeoff_row, "more_residual_heavy_candidate")
    better_retention_minus_leak_label = decode_label_choice(tradeoff_row, "better_retention_minus_leak_candidate")

    normalized_bandwidth: dict[str, Any] = {}
    narrower_label = "not_available"
    if bandwidth_row is not None:
        baseline_bandwidth = get_metrics_for_label(bandwidth_row, baseline_label)
        candidate_bandwidth = get_metrics_for_label(bandwidth_row, candidate_label)
        narrower_label = decode_label_choice(bandwidth_row, "narrower_candidate")
        normalized_bandwidth = {
            "baseline_metrics": baseline_bandwidth,
            "candidate_metrics": candidate_bandwidth,
            "candidate_minus_baseline": {
                "rolloff_95_hz": subtract_optional(
                    candidate_bandwidth.get("rolloff_95_hz"), baseline_bandwidth.get("rolloff_95_hz")
                ),
                "spectral_centroid_hz": subtract_optional(
                    candidate_bandwidth.get("spectral_centroid_hz"),
                    baseline_bandwidth.get("spectral_centroid_hz"),
                ),
                "upper_vs_mid_db": subtract_optional(
                    candidate_bandwidth.get("upper_vs_mid_db"),
                    baseline_bandwidth.get("upper_vs_mid_db"),
                ),
                "band_share_3k_8k": subtract_optional(
                    candidate_bandwidth.get("band_share_3k_8k"),
                    baseline_bandwidth.get("band_share_3k_8k"),
                ),
                "frame_upper_share_p90": subtract_optional(
                    candidate_bandwidth.get("frame_upper_share_p90"),
                    baseline_bandwidth.get("frame_upper_share_p90"),
                ),
            },
            "narrower_label": narrower_label,
        }

    normalized_transient: dict[str, Any] = {}
    more_transient_lossy_label = "not_available"
    if transient_row is not None:
        baseline_transient = get_metrics_for_label(transient_row, baseline_label)
        candidate_transient = get_metrics_for_label(transient_row, candidate_label)
        more_transient_lossy_label = decode_label_choice(transient_row, "more_transient_lossy_candidate")
        normalized_transient = {
            "baseline_metrics": baseline_transient,
            "candidate_metrics": candidate_transient,
            "candidate_minus_baseline": {
                "transient_presence_minus_mid_retention_db_mean": subtract_optional(
                    candidate_transient.get("transient_presence_minus_mid_retention_db_mean"),
                    baseline_transient.get("transient_presence_minus_mid_retention_db_mean"),
                ),
                "transient_presence_minus_mid_retention_db_p10": subtract_optional(
                    candidate_transient.get("transient_presence_minus_mid_retention_db_p10"),
                    baseline_transient.get("transient_presence_minus_mid_retention_db_p10"),
                ),
                "strong_presence_loss_frame_ratio": subtract_optional(
                    candidate_transient.get("strong_presence_loss_frame_ratio"),
                    baseline_transient.get("strong_presence_loss_frame_ratio"),
                ),
            },
            "more_transient_lossy_label": more_transient_lossy_label,
        }

    active_failure_flags: list[str] = []
    if better_source_retention_label == baseline_label:
        active_failure_flags.append("lost_target_capture")
    if better_retention_minus_leak_label == baseline_label:
        active_failure_flags.append("lost_retention_minus_leak")
    if more_interference_leaky_label == candidate_label:
        active_failure_flags.append("more_interference_leaky")
    if more_residual_heavy_label == candidate_label:
        active_failure_flags.append("more_residual_heavy")
    if narrower_label == candidate_label:
        active_failure_flags.append("narrower_bandwidth")
    if more_transient_lossy_label == candidate_label:
        active_failure_flags.append("more_transient_lossy")

    primary_hypotheses: list[str] = []
    if "more_residual_heavy" in active_failure_flags and (
        "lost_target_capture" in active_failure_flags or "lost_retention_minus_leak" in active_failure_flags
    ):
        primary_hypotheses.append("over_suppression_or_residual_tradeoff")
    if "more_interference_leaky" in active_failure_flags:
        primary_hypotheses.append("speech_leak_tradeoff")
    if "more_transient_lossy" in active_failure_flags:
        primary_hypotheses.append("transient_loss")
    if "narrower_bandwidth" in active_failure_flags:
        primary_hypotheses.append("bandwidth_narrowing")
    if not primary_hypotheses and active_failure_flags:
        primary_hypotheses.append("mixed_tradeoff")

    return {
        "sample_id": tradeoff_row["sample_id"],
        "note": tradeoff_row.get("note", ""),
        "scenario": tradeoff_row.get("scenario", ""),
        "component_kinds": tradeoff_row.get("component_kinds", []),
        "bucket_name": tradeoff_row.get("target_interference_bucket", ""),
        "baseline_label": baseline_label,
        "candidate_label": candidate_label,
        "decoded_labels": {
            "better_source_retention_label": better_source_retention_label,
            "more_interference_leaky_label": more_interference_leaky_label,
            "more_residual_heavy_label": more_residual_heavy_label,
            "better_retention_minus_leak_label": better_retention_minus_leak_label,
            "narrower_label": narrower_label,
            "more_transient_lossy_label": more_transient_lossy_label,
        },
        "tradeoff": {
            "baseline_metrics": baseline_tradeoff,
            "candidate_metrics": candidate_tradeoff,
            "candidate_minus_baseline": {
                "target_capture_db": subtract_optional(
                    candidate_tradeoff.get("target_capture_db"), baseline_tradeoff.get("target_capture_db")
                ),
                "interference_capture_db": subtract_optional(
                    candidate_tradeoff.get("interference_capture_db"),
                    baseline_tradeoff.get("interference_capture_db"),
                ),
                "retention_minus_leak_db": subtract_optional(
                    candidate_tradeoff.get("retention_minus_leak_db"),
                    baseline_tradeoff.get("retention_minus_leak_db"),
                ),
                "residual_output_share": subtract_optional(
                    candidate_tradeoff.get("residual_output_share"),
                    baseline_tradeoff.get("residual_output_share"),
                ),
                "joint_fit_r2": subtract_optional(
                    candidate_tradeoff.get("joint_fit_r2"), baseline_tradeoff.get("joint_fit_r2")
                ),
            },
        },
        "bandwidth": normalized_bandwidth,
        "transient": normalized_transient,
        "active_failure_flags": active_failure_flags,
        "failure_signature": make_signature(active_failure_flags),
        "primary_hypotheses": primary_hypotheses,
    }


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or (args.pack_dir / "bucket_diagnostics" / args.bucket_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    tradeoff_rows = load_jsonl(args.pack_dir / "tradeoff_analysis" / "per_sample_pair_metrics.jsonl")
    candidate_label = args.candidate_label or infer_candidate_label(tradeoff_rows, args.baseline_label)

    bandwidth_rows = {
        row["sample_id"]: row
        for row in load_jsonl(args.pack_dir / "bandwidth_analysis" / "per_sample_pair_metrics.jsonl")
    }
    transient_rows = {
        row["sample_id"]: row
        for row in load_jsonl(args.pack_dir / "transient_analysis" / "per_sample_pair_metrics.jsonl")
    }

    filtered_tradeoff_rows = [
        row for row in tradeoff_rows if str(row.get("target_interference_bucket", "")) == args.bucket_name
    ]

    diagnosis_rows = [
        build_row_diagnosis(
            tradeoff_row=row,
            bandwidth_row=bandwidth_rows.get(str(row["sample_id"])),
            transient_row=transient_rows.get(str(row["sample_id"])),
            baseline_label=args.baseline_label,
            candidate_label=candidate_label,
        )
        for row in filtered_tradeoff_rows
    ]

    active_flag_lists = [row["active_failure_flags"] for row in diagnosis_rows]
    summary = {
        "pack_dir": serialize_repo_path(args.pack_dir),
        "bucket_name": args.bucket_name,
        "baseline_label": args.baseline_label,
        "candidate_label": candidate_label,
        "num_samples": len(diagnosis_rows),
        "sample_ids": [str(row["sample_id"]) for row in diagnosis_rows],
        "active_failure_flag_counts": count_values(
            [flag for flags in active_flag_lists for flag in flags]
        ),
        "failure_signature_counts": count_values([str(row["failure_signature"]) for row in diagnosis_rows]),
        "primary_hypothesis_counts": count_values(
            [hypothesis for row in diagnosis_rows for hypothesis in row["primary_hypotheses"]]
        ),
        "mean_candidate_minus_baseline": {
            "target_capture_db": mean_optional(
                [row["tradeoff"]["candidate_minus_baseline"]["target_capture_db"] for row in diagnosis_rows]
            ),
            "interference_capture_db": mean_optional(
                [row["tradeoff"]["candidate_minus_baseline"]["interference_capture_db"] for row in diagnosis_rows]
            ),
            "retention_minus_leak_db": mean_optional(
                [row["tradeoff"]["candidate_minus_baseline"]["retention_minus_leak_db"] for row in diagnosis_rows]
            ),
            "residual_output_share": mean_optional(
                [row["tradeoff"]["candidate_minus_baseline"]["residual_output_share"] for row in diagnosis_rows]
            ),
            "rolloff_95_hz": mean_optional(
                [
                    row.get("bandwidth", {}).get("candidate_minus_baseline", {}).get("rolloff_95_hz")
                    for row in diagnosis_rows
                ]
            ),
            "upper_vs_mid_db": mean_optional(
                [
                    row.get("bandwidth", {}).get("candidate_minus_baseline", {}).get("upper_vs_mid_db")
                    for row in diagnosis_rows
                ]
            ),
            "frame_upper_share_p90": mean_optional(
                [
                    row.get("bandwidth", {}).get("candidate_minus_baseline", {}).get("frame_upper_share_p90")
                    for row in diagnosis_rows
                ]
            ),
            "transient_presence_minus_mid_retention_db_mean": mean_optional(
                [
                    row.get("transient", {})
                    .get("candidate_minus_baseline", {})
                    .get("transient_presence_minus_mid_retention_db_mean")
                    for row in diagnosis_rows
                ]
            ),
            "strong_presence_loss_frame_ratio": mean_optional(
                [
                    row.get("transient", {})
                    .get("candidate_minus_baseline", {})
                    .get("strong_presence_loss_frame_ratio")
                    for row in diagnosis_rows
                ]
            ),
        },
        "per_sample": diagnosis_rows,
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "per_sample_diagnosis.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in diagnosis_rows),
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "pack_dir": serialize_repo_path(args.pack_dir),
                "bucket_name": args.bucket_name,
                "baseline_label": args.baseline_label,
                "candidate_label": candidate_label,
                "num_samples": len(diagnosis_rows),
                "active_failure_flag_counts": summary["active_failure_flag_counts"],
                "output_dir": serialize_repo_path(output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
