from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Score a listening pack for the silence-over-leak subproblem using objective-only "
            "metrics. Intended for batch triage, not as a full replacement for final human review."
        )
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    parser.add_argument(
        "--target-present-energy-threshold",
        type=float,
        default=1e-8,
        help="Minimum target-track energy ratio versus mixture to treat a sample as target-present.",
    )
    parser.add_argument(
        "--target-present-backstop-margin-db",
        type=float,
        default=0.75,
        help="How far a candidate may trail the best target-present retention-minus-leak score before being flagged.",
    )
    parser.add_argument(
        "--absent-near-tie-margin-db",
        type=float,
        default=0.75,
        help="Treat absent-case interference-capture differences inside this margin as near ties.",
    )
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


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    waveform, sample_rate = sf.read(str(path), always_2d=False)
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    return waveform, sample_rate


def fit_or_trim(waveform: np.ndarray, num_samples: int) -> np.ndarray:
    if waveform.shape[0] >= num_samples:
        return waveform[:num_samples].astype(np.float32, copy=False)
    padded = np.zeros(num_samples, dtype=np.float32)
    padded[: waveform.shape[0]] = waveform
    return padded


def energy(waveform: np.ndarray) -> float:
    return float(np.dot(waveform, waveform))


def safe_log10(value: float, eps: float = 1e-12) -> float:
    return float(10.0 * np.log10(max(value, eps)))


def rms_dbfs(waveform: np.ndarray) -> float:
    return safe_log10(float(np.mean(np.square(waveform), dtype=np.float64) + 1e-12))


def fit_scalar(reference: np.ndarray, target: np.ndarray, eps: float = 1e-12) -> float:
    denom = energy(reference)
    if denom <= eps:
        return 0.0
    return float(np.dot(reference, target) / denom)


def capture_db(output: np.ndarray, reference: np.ndarray, eps: float = 1e-12) -> tuple[float | None, float | None]:
    ref_energy = energy(reference)
    if ref_energy <= eps:
        return None, None
    scale = fit_scalar(reference, output, eps=eps)
    return safe_log10((scale * scale) + eps), scale


def joint_residual_share(output: np.ndarray, basis_vectors: list[np.ndarray], eps: float = 1e-12) -> float:
    usable = [vector for vector in basis_vectors if energy(vector) > eps]
    output_energy = max(energy(output), eps)
    if not usable:
        return 1.0
    basis = np.stack(usable, axis=1)
    coefficients, _, _, _ = np.linalg.lstsq(basis, output, rcond=None)
    fitted = basis @ coefficients
    residual = output - fitted
    return float(min(max(energy(residual) / output_energy, 0.0), 1.0))


def build_blind_mapping(blind_key: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if not blind_key:
        return {}
    output: dict[str, dict[str, str]] = {}
    for row in blind_key.get("mapping", []):
        sample_id = str(row["sample_id"])
        output[sample_id] = {
            str(key): str(value)
            for key, value in row.items()
            if str(key) != "sample_id"
        }
    return output


def mean_or_none(values: list[float | None]) -> float | None:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return None
    return float(sum(usable) / len(usable))


def sum_or_zero(values: list[int]) -> int:
    return int(sum(values))


def resolve_candidate_audio_map(
    sample_summary: dict[str, Any],
    sample_mapping: dict[str, str],
) -> dict[str, str]:
    exports = sample_summary.get("exports", {})
    if sample_mapping:
        return {
            real_label: str(exports[candidate_id])
            for candidate_id, real_label in sample_mapping.items()
            if candidate_id in exports
        }

    comparison = sample_summary.get("comparison", {})
    if "label_a" in sample_summary and "label_b" in sample_summary:
        label_a = str(sample_summary["label_a"])
        label_b = str(sample_summary["label_b"])
        return {
            label_a: str(exports["estimate_a"]),
            label_b: str(exports["estimate_b"]),
        }
    if comparison and exports:
        fallback: dict[str, str] = {}
        for key, value in exports.items():
            fallback[str(key)] = str(value)
        return fallback
    raise ValueError(f"Could not resolve candidate audio names for sample {sample_summary.get('sample_id')}")


def main() -> None:
    args = parse_args()
    pack_dir = args.pack_dir.resolve()
    summary = load_json(pack_dir / "summary.json")
    blind_key_path = pack_dir / "blind_key.json"
    blind_key = load_json(blind_key_path) if blind_key_path.exists() else None
    blind_mapping_by_sample = build_blind_mapping(blind_key)
    output_json = args.output_json or (pack_dir / "silence_over_leak_objective_summary.json")

    per_sample_rows: list[dict[str, Any]] = []
    per_label_absent: dict[str, list[dict[str, Any]]] = {}
    per_label_present: dict[str, list[dict[str, Any]]] = {}

    for sample_summary in summary.get("samples", []):
        sample_id = str(sample_summary["sample_id"])
        sample_dir = pack_dir / sample_id
        mixture, sample_rate = load_audio(sample_dir / "mixture.wav")
        target_path = sample_dir / "target.wav"
        if target_path.exists():
            target, target_sr = load_audio(target_path)
            if target_sr != sample_rate:
                raise ValueError(f"Sample rate mismatch for {target_path}")
        else:
            target = np.zeros_like(mixture)
        mixture = fit_or_trim(mixture, mixture.shape[0])
        target = fit_or_trim(target, mixture.shape[0])
        interference = mixture - target

        mixture_energy = max(energy(mixture), 1e-12)
        target_energy_ratio = energy(target) / mixture_energy
        target_present = target_energy_ratio > args.target_present_energy_threshold

        sample_mapping = blind_mapping_by_sample.get(sample_id, {})
        candidate_audio_map = resolve_candidate_audio_map(sample_summary, sample_mapping)
        candidate_metrics: dict[str, dict[str, Any]] = {}

        for label, audio_name in sorted(candidate_audio_map.items()):
            waveform, candidate_sr = load_audio(sample_dir / audio_name)
            if candidate_sr != sample_rate:
                raise ValueError(f"Sample rate mismatch for {sample_dir / audio_name}")
            waveform = fit_or_trim(waveform, mixture.shape[0])
            target_capture_db, _ = capture_db(waveform, target)
            interference_capture_db, _ = capture_db(waveform, interference)
            retention_minus_leak_db = None
            if target_capture_db is not None and interference_capture_db is not None:
                retention_minus_leak_db = float(target_capture_db - interference_capture_db)
            candidate_metrics[label] = {
                "rms_dbfs": rms_dbfs(waveform),
                "target_capture_db": target_capture_db,
                "interference_capture_db": interference_capture_db,
                "retention_minus_leak_db": retention_minus_leak_db,
                "residual_output_share": joint_residual_share(waveform, [target, interference]),
            }
            bucket = per_label_present if target_present else per_label_absent
            bucket.setdefault(label, []).append(candidate_metrics[label])

        absent_best_labels: list[str] = []
        present_within_margin_labels: list[str] = []
        if not target_present:
            best_interference_capture = min(
                metric["interference_capture_db"]
                for metric in candidate_metrics.values()
                if metric["interference_capture_db"] is not None
            )
            for label, metric in candidate_metrics.items():
                value = metric["interference_capture_db"]
                if value is None:
                    continue
                if float(value - best_interference_capture) <= args.absent_near_tie_margin_db:
                    absent_best_labels.append(label)
        else:
            present_scores = {
                label: metric["retention_minus_leak_db"]
                for label, metric in candidate_metrics.items()
                if metric["retention_minus_leak_db"] is not None
            }
            if present_scores:
                best_present = max(present_scores.values())
                for label, value in present_scores.items():
                    if float(best_present - value) <= args.target_present_backstop_margin_db:
                        present_within_margin_labels.append(label)

        per_sample_rows.append(
            {
                "sample_id": sample_id,
                "note": str(sample_summary.get("note", "")),
                "target_present": target_present,
                "target_energy_ratio": target_energy_ratio,
                "candidate_metrics": candidate_metrics,
                "absent_near_tie_best_labels": absent_best_labels,
                "present_within_backstop_margin_labels": present_within_margin_labels,
            }
        )

    labels = sorted(set(per_label_absent) | set(per_label_present))
    aggregate_by_label: dict[str, Any] = {}
    for label in labels:
        absent_rows = per_label_absent.get(label, [])
        present_rows = per_label_present.get(label, [])
        aggregate_by_label[label] = {
            "absent_count": len(absent_rows),
            "absent_mean_interference_capture_db": mean_or_none(
                [row["interference_capture_db"] for row in absent_rows]
            ),
            "absent_mean_rms_dbfs": mean_or_none([row["rms_dbfs"] for row in absent_rows]),
            "absent_mean_residual_output_share": mean_or_none(
                [row["residual_output_share"] for row in absent_rows]
            ),
            "present_count": len(present_rows),
            "present_mean_target_capture_db": mean_or_none(
                [row["target_capture_db"] for row in present_rows]
            ),
            "present_mean_interference_capture_db": mean_or_none(
                [row["interference_capture_db"] for row in present_rows]
            ),
            "present_mean_retention_minus_leak_db": mean_or_none(
                [row["retention_minus_leak_db"] for row in present_rows]
            ),
            "present_mean_residual_output_share": mean_or_none(
                [row["residual_output_share"] for row in present_rows]
            ),
        }

    absent_frontier_counts = {
        label: sum_or_zero(
            [
                1 if label in row["absent_near_tie_best_labels"] else 0
                for row in per_sample_rows
                if not row["target_present"]
            ]
        )
        for label in labels
    }
    present_backstop_counts = {
        label: sum_or_zero(
            [
                1 if label in row["present_within_backstop_margin_labels"] else 0
                for row in per_sample_rows
                if row["target_present"]
            ]
        )
        for label in labels
    }

    absent_rank = sorted(
        labels,
        key=lambda label: (
            -(absent_frontier_counts.get(label, 0)),
            float("inf")
            if aggregate_by_label[label]["absent_mean_interference_capture_db"] is None
            else aggregate_by_label[label]["absent_mean_interference_capture_db"],
            float("inf")
            if aggregate_by_label[label]["absent_mean_rms_dbfs"] is None
            else aggregate_by_label[label]["absent_mean_rms_dbfs"],
        ),
    )
    present_rank = sorted(
        labels,
        key=lambda label: (
            -(present_backstop_counts.get(label, 0)),
            -float("-inf")
            if aggregate_by_label[label]["present_mean_retention_minus_leak_db"] is None
            else -aggregate_by_label[label]["present_mean_retention_minus_leak_db"],
        ),
    )

    output = {
        "pack_dir": serialize_repo_path(pack_dir),
        "output_json": serialize_repo_path(output_json),
        "target_present_energy_threshold": args.target_present_energy_threshold,
        "target_present_backstop_margin_db": args.target_present_backstop_margin_db,
        "absent_near_tie_margin_db": args.absent_near_tie_margin_db,
        "aggregate_by_label": aggregate_by_label,
        "absent_frontier_counts": absent_frontier_counts,
        "present_backstop_counts": present_backstop_counts,
        "absent_rank": absent_rank,
        "present_rank": present_rank,
        "per_sample": per_sample_rows,
    }
    output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "output_json": serialize_repo_path(output_json),
                "absent_rank": absent_rank,
                "present_rank": present_rank,
                "absent_frontier_counts": absent_frontier_counts,
                "present_backstop_counts": present_backstop_counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
