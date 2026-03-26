from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]

TARGET_COMPONENT_KINDS = {"target_raw"}
SPEECH_COMPONENT_TOKENS = ("speech", "friend", "guodegang", "raw")
MUSIC_COMPONENT_TOKENS = ("music",)
SINGING_COMPONENT_TOKENS = ("sing", "vocal")
NOISE_COMPONENT_TOKENS = ("noise", "ambient")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze source-retention vs interference-leak trade-offs inside a listening pack "
            "by reconstructing the original near-real components."
        )
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument(
        "--source-retention-threshold-db",
        type=float,
        default=0.75,
        help="Minimum target-capture delta to flag one candidate as more source-retentive.",
    )
    parser.add_argument(
        "--interference-leak-threshold-db",
        type=float,
        default=0.75,
        help="Minimum interference-capture delta to flag one candidate as more interference-leaky.",
    )
    parser.add_argument(
        "--residual-share-threshold",
        type=float,
        default=0.08,
        help="Minimum unexplained residual-share delta to flag one candidate as more residual-heavy.",
    )
    parser.add_argument(
        "--retention-minus-leak-threshold-db",
        type=float,
        default=1.0,
        help="Minimum retention-minus-leak delta to flag one candidate as having a better trade-off.",
    )
    parser.add_argument("--top-k", type=int, default=12)
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


def load_listening_sheet(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows[row["sample_id"]] = row
    return rows


def resolve_pair_candidate_info(
    pack_summary: dict[str, Any],
    sample_meta: dict[str, Any],
    sheet_row: dict[str, str],
    blind_mapping_row: dict[str, Any],
) -> dict[str, str]:
    file_a_name = str(sheet_row.get("file_a_name", "")).strip()
    file_b_name = str(sheet_row.get("file_b_name", "")).strip()
    exports = sample_meta.get("exports", {})
    export_names = sample_meta.get("export_names", {})
    if not exports and export_names:
        exports = export_names
    if not file_a_name:
        file_a_name = str(exports.get("estimate_a", "candidate_a.wav")).strip()
    if not file_b_name:
        file_b_name = str(exports.get("estimate_b", "candidate_b.wav")).strip()

    if blind_mapping_row:
        file_a_key = Path(file_a_name).stem
        file_b_key = Path(file_b_name).stem
        file_a_label = str(blind_mapping_row.get(file_a_key, file_a_key))
        file_b_label = str(blind_mapping_row.get(file_b_key, file_b_key))
    else:
        label_a = str(pack_summary.get("label_a", "")).strip()
        label_b = str(pack_summary.get("label_b", "")).strip()
        if label_a and label_b:
            file_a_label = label_a if file_a_name == str(exports.get("estimate_a", "")).strip() else label_b
            file_b_label = label_b if file_b_name == str(exports.get("estimate_b", "")).strip() else label_a
        else:
            file_a_label = Path(file_a_name).stem
            file_b_label = Path(file_b_name).stem

    return {
        "file_a_name": file_a_name,
        "file_b_name": file_b_name,
        "file_a_label": file_a_label,
        "file_b_label": file_b_label,
    }


def run_command(command: list[str]) -> None:
    subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def extract_audio(
    input_path: Path,
    output_path: Path,
    start_sec: float | None,
    duration_sec: float,
    sample_rate: int,
) -> None:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
    ]
    if start_sec is not None:
        command.extend(["-ss", f"{start_sec:.3f}"])
    command.extend(
        [
            "-i",
            str(input_path),
            "-t",
            f"{duration_sec:.3f}",
            "-ac",
            "1",
            "-ar",
            str(sample_rate),
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]
    )
    run_command(command)


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    waveform, sample_rate = sf.read(str(path), always_2d=False)
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    return waveform, sample_rate


def fit_or_pad(waveform: np.ndarray, num_samples: int) -> np.ndarray:
    if waveform.shape[0] >= num_samples:
        return waveform[:num_samples].astype(np.float32, copy=False)
    padded = np.zeros(num_samples, dtype=np.float32)
    padded[: waveform.shape[0]] = waveform
    return padded


def db_to_scale(gain_db: float) -> float:
    return float(10.0 ** (gain_db / 20.0))


def safe_log10(value: float, eps: float = 1e-12) -> float:
    return float(10.0 * np.log10(max(value, eps)))


def energy(waveform: np.ndarray) -> float:
    return float(np.dot(waveform, waveform))


def fit_scalar(reference: np.ndarray, target: np.ndarray, eps: float = 1e-12) -> float:
    denom = float(np.dot(reference, reference))
    if denom <= eps:
        return 0.0
    return float(np.dot(reference, target) / denom)


def capture_db(output: np.ndarray, reference: np.ndarray, eps: float = 1e-12) -> tuple[float | None, float | None]:
    ref_energy = energy(reference)
    if ref_energy <= eps:
        return None, None
    scale = fit_scalar(reference, output, eps=eps)
    return safe_log10((scale * scale) + eps), scale


def joint_residual_metrics(
    output: np.ndarray,
    target_track: np.ndarray,
    interference_track: np.ndarray,
    eps: float = 1e-12,
) -> dict[str, float | list[float]]:
    basis_vectors: list[np.ndarray] = []
    if energy(target_track) > eps:
        basis_vectors.append(target_track)
    if energy(interference_track) > eps:
        basis_vectors.append(interference_track)

    output_energy = max(energy(output), eps)
    if not basis_vectors:
        return {
            "joint_fit_r2": 0.0,
            "residual_output_share": 1.0,
            "projection_coefficients": [],
        }

    basis = np.stack(basis_vectors, axis=1)
    coefficients, _, _, _ = np.linalg.lstsq(basis, output, rcond=None)
    fitted = basis @ coefficients
    residual = output - fitted
    residual_share = float(energy(residual) / output_energy)
    return {
        "joint_fit_r2": float(max(0.0, 1.0 - residual_share)),
        "residual_output_share": float(min(max(residual_share, 0.0), 1.0)),
        "projection_coefficients": [float(x) for x in coefficients.tolist()],
    }


def component_cache_key(sample_id: str, index: int, component: dict[str, Any]) -> str:
    start_sec = component.get("clip_start_sec")
    duration_sec = component["clip_duration_sec"]
    gain_db = component.get("gain_db", 0.0)
    return (
        f"{sample_id}_{index:02d}_{component['kind']}"
        f"_start{start_sec if start_sec is not None else 'none'}"
        f"_dur{duration_sec}_gain{gain_db:.2f}.wav"
    ).replace(":", "_")


def build_component_track(
    component: dict[str, Any],
    cache_dir: Path,
    sample_id: str,
    component_index: int,
    num_samples: int,
    sample_rate: int,
) -> np.ndarray:
    source_path = ROOT / component["source_path"]
    cache_path = cache_dir / component_cache_key(sample_id, component_index, component)
    if not cache_path.exists():
        extract_audio(
            input_path=source_path,
            output_path=cache_path,
            start_sec=component.get("clip_start_sec"),
            duration_sec=float(component["clip_duration_sec"]),
            sample_rate=sample_rate,
        )

    waveform, clip_sr = load_audio(cache_path)
    if clip_sr != sample_rate:
        raise ValueError(f"Unexpected sample rate for cached clip {cache_path}: {clip_sr}")
    waveform = fit_or_pad(waveform, num_samples)
    return waveform * db_to_scale(float(component.get("gain_db", 0.0)))


def reconstruct_tracks(
    sample_id: str,
    original_sample_meta: dict[str, Any],
    pack_mixture: np.ndarray,
    cache_dir: Path,
    sample_rate: int,
) -> dict[str, Any]:
    num_samples = pack_mixture.shape[0]
    target_sum = np.zeros(num_samples, dtype=np.float32)
    interference_sum = np.zeros(num_samples, dtype=np.float32)

    components = original_sample_meta["components"]
    for component_index, component in enumerate(components):
        component_track = build_component_track(
            component=component,
            cache_dir=cache_dir,
            sample_id=sample_id,
            component_index=component_index,
            num_samples=num_samples,
            sample_rate=sample_rate,
        )
        if component["kind"] in TARGET_COMPONENT_KINDS:
            target_sum += component_track
        else:
            interference_sum += component_track

    raw_mix = target_sum + interference_sum
    alignment_scale = fit_scalar(raw_mix, pack_mixture)
    aligned_target = target_sum * alignment_scale
    aligned_interference = interference_sum * alignment_scale
    aligned_mix = raw_mix * alignment_scale
    alignment_error = pack_mixture - aligned_mix

    return {
        "target_track": aligned_target,
        "interference_track": aligned_interference,
        "aligned_mix": aligned_mix,
        "alignment_scale": alignment_scale,
        "mixture_alignment_r2": float(max(0.0, 1.0 - (energy(alignment_error) / max(energy(pack_mixture), 1e-12)))),
        "target_present": bool(energy(aligned_target) > 1e-12),
        "interference_present": bool(energy(aligned_interference) > 1e-12),
    }


def analyze_candidate(
    waveform: np.ndarray,
    target_track: np.ndarray,
    interference_track: np.ndarray,
) -> dict[str, Any]:
    target_capture, target_scale = capture_db(waveform, target_track)
    interference_capture, interference_scale = capture_db(waveform, interference_track)
    residual_metrics = joint_residual_metrics(waveform, target_track, interference_track)

    retention_minus_leak_db = None
    if target_capture is not None and interference_capture is not None:
        retention_minus_leak_db = float(target_capture - interference_capture)

    return {
        "rms_dbfs": safe_log10((np.sqrt(np.mean(np.square(waveform)) + 1e-12)) ** 2),
        "target_capture_db": target_capture,
        "target_projection_scale": target_scale,
        "interference_capture_db": interference_capture,
        "interference_projection_scale": interference_scale,
        "retention_minus_leak_db": retention_minus_leak_db,
        **residual_metrics,
    }


def compare_optional_higher_is_better(
    value_a: float | None,
    value_b: float | None,
    threshold: float,
) -> tuple[str, float | None]:
    if value_a is None or value_b is None:
        return "not_applicable", None
    delta = float(value_b - value_a)
    if delta >= threshold:
        return "file_b", delta
    if delta <= -threshold:
        return "file_a", delta
    return "tie", delta


def compare_optional_residual_share(
    value_a: float | None,
    value_b: float | None,
    threshold: float,
) -> tuple[str, float | None]:
    if value_a is None or value_b is None:
        return "not_applicable", None
    delta = float(value_b - value_a)
    if delta >= threshold:
        return "file_b", delta
    if delta <= -threshold:
        return "file_a", delta
    return "tie", delta


def average_optional(values: list[float | None]) -> float | None:
    filtered = [float(x) for x in values if x is not None]
    if not filtered:
        return None
    return float(sum(filtered) / len(filtered))


def categorize_component_kind(kind: str) -> str:
    if kind in TARGET_COMPONENT_KINDS:
        return "target"
    lowered = kind.lower()
    if any(token in lowered for token in MUSIC_COMPONENT_TOKENS):
        return "music"
    if any(token in lowered for token in SINGING_COMPONENT_TOKENS):
        return "singing"
    if any(token in lowered for token in NOISE_COMPONENT_TOKENS):
        return "noise"
    if any(token in lowered for token in SPEECH_COMPONENT_TOKENS):
        return "speech"
    return "other"


def derive_group_labels(original_sample_meta: dict[str, Any]) -> dict[str, str]:
    kinds = [component["kind"] for component in original_sample_meta["components"]]
    categories = [categorize_component_kind(kind) for kind in kinds]
    target_present = "target" in categories
    interference_categories = sorted({category for category in categories if category != "target"})

    if not interference_categories:
        interference_profile = "none"
    else:
        interference_profile = "_plus_".join(interference_categories)

    target_status = "target_present" if target_present else "target_absent"
    target_interference_bucket = f"{target_status}__{interference_profile}"
    return {
        "scenario": str(original_sample_meta.get("scenario", "")),
        "target_status": target_status,
        "interference_profile": interference_profile,
        "target_interference_bucket": target_interference_bucket,
    }


def summarize_group_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "count": len(rows),
        "sample_ids": [str(row["sample_id"]) for row in rows],
        "decoded_label_counts": {
            "better_source_retention_label": count_decoded_choice(rows, "better_source_retention_candidate"),
            "more_interference_leaky_label": count_decoded_choice(rows, "more_interference_leaky_candidate"),
            "more_residual_heavy_label": count_decoded_choice(rows, "more_residual_heavy_candidate"),
            "better_retention_minus_leak_label": count_decoded_choice(rows, "better_retention_minus_leak_candidate"),
        },
        "decoded_mean_metrics_by_label": build_decoded_means(rows),
    }


def count_value(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[key])
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_decoded_means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    metric_names = (
        "target_capture_db",
        "interference_capture_db",
        "retention_minus_leak_db",
        "residual_output_share",
        "joint_fit_r2",
    )
    buckets: dict[str, dict[str, list[float | None]]] = {}
    for row in rows:
        for label_key in ("file_a_label", "file_b_label"):
            label = str(row[label_key])
            metric_key = "file_a_metrics" if label_key == "file_a_label" else "file_b_metrics"
            label_bucket = buckets.setdefault(label, {name: [] for name in metric_names})
            for metric_name in metric_names:
                label_bucket[metric_name].append(row[metric_key].get(metric_name))
    return {
        label: {metric_name: average_optional(values) for metric_name, values in metrics.items()}
        for label, metrics in buckets.items()
    }


def decode_candidate_choice(row: dict[str, Any], key: str) -> str:
    raw_value = str(row[key])
    if raw_value == "file_a":
        return str(row["file_a_label"])
    if raw_value == "file_b":
        return str(row["file_b_label"])
    return raw_value


def count_decoded_choice(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = decode_candidate_choice(row, key)
        counts[value] = counts.get(value, 0) + 1
    return counts


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or (args.pack_dir / "tradeoff_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "_component_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    pack_summary_path = args.pack_dir / "summary.json"
    pack_summary = load_json(pack_summary_path) if pack_summary_path.exists() else {}
    blind_key_path = args.pack_dir / "blind_key.json"
    blind_key = load_json(blind_key_path) if blind_key_path.exists() else None
    blind_mapping = {}
    if blind_key is not None:
        blind_mapping = {row["sample_id"]: row for row in blind_key["mapping"]}

    listening_sheet_path = args.pack_dir / "listening_sheet.csv"
    listening_sheet = load_listening_sheet(listening_sheet_path) if listening_sheet_path.exists() else {}

    sample_dirs = sorted(
        path for path in args.pack_dir.iterdir() if path.is_dir() and (path / "sample_meta.json").exists()
    )

    pair_rows: list[dict[str, Any]] = []

    for sample_dir in sample_dirs:
        sample_meta = load_json(sample_dir / "sample_meta.json")
        sample_id = sample_meta["sample_id"]
        sheet_row = listening_sheet.get(sample_id, {})
        candidate_info = resolve_pair_candidate_info(
            pack_summary=pack_summary,
            sample_meta=sample_meta,
            sheet_row=sheet_row,
            blind_mapping_row=blind_mapping.get(sample_id, {}),
        )

        mixture, sr_mix = load_audio(sample_dir / "mixture.wav")
        candidate_a, sr_a = load_audio(sample_dir / candidate_info["file_a_name"])
        candidate_b, sr_b = load_audio(sample_dir / candidate_info["file_b_name"])
        if sr_mix != args.sample_rate or sr_a != args.sample_rate or sr_b != args.sample_rate:
            raise ValueError(f"Sample rate mismatch in {sample_id}")

        original_mixture_path = ROOT / sample_meta["mixture_audio_path"]
        original_sample_meta = load_json(original_mixture_path.parent / "sample_meta.json")
        group_labels = derive_group_labels(original_sample_meta)
        recon = reconstruct_tracks(
            sample_id=sample_id,
            original_sample_meta=original_sample_meta,
            pack_mixture=mixture,
            cache_dir=cache_dir,
            sample_rate=args.sample_rate,
        )

        metrics_a = analyze_candidate(
            waveform=candidate_a,
            target_track=recon["target_track"],
            interference_track=recon["interference_track"],
        )
        metrics_b = analyze_candidate(
            waveform=candidate_b,
            target_track=recon["target_track"],
            interference_track=recon["interference_track"],
        )

        better_source_retention_candidate, delta_target_capture = compare_optional_higher_is_better(
            metrics_a["target_capture_db"],
            metrics_b["target_capture_db"],
            args.source_retention_threshold_db,
        )
        more_interference_leaky_candidate, delta_interference_capture = compare_optional_higher_is_better(
            metrics_a["interference_capture_db"],
            metrics_b["interference_capture_db"],
            args.interference_leak_threshold_db,
        )
        more_residual_heavy_candidate, delta_residual_share = compare_optional_residual_share(
            metrics_a["residual_output_share"],
            metrics_b["residual_output_share"],
            args.residual_share_threshold,
        )
        better_retention_minus_leak_candidate, delta_retention_minus_leak = compare_optional_higher_is_better(
            metrics_a["retention_minus_leak_db"],
            metrics_b["retention_minus_leak_db"],
            args.retention_minus_leak_threshold_db,
        )

        row = {
            "sample_id": sample_id,
            "note": sample_meta.get("note", ""),
            "better_output": listening_sheet.get(sample_id, {}).get("better_output", ""),
            "scenario": original_sample_meta.get("scenario", ""),
            "target_status": group_labels["target_status"],
            "interference_profile": group_labels["interference_profile"],
            "target_interference_bucket": group_labels["target_interference_bucket"],
            "file_a_name": candidate_info["file_a_name"],
            "file_b_name": candidate_info["file_b_name"],
            "file_a_label": candidate_info["file_a_label"],
            "file_b_label": candidate_info["file_b_label"],
            "component_kinds": [component["kind"] for component in original_sample_meta["components"]],
            "target_present": recon["target_present"],
            "interference_present": recon["interference_present"],
            "mixture_alignment_scale": recon["alignment_scale"],
            "mixture_alignment_r2": recon["mixture_alignment_r2"],
            "file_a_metrics": metrics_a,
            "file_b_metrics": metrics_b,
            "delta_target_capture_db_b_minus_a": delta_target_capture,
            "delta_interference_capture_db_b_minus_a": delta_interference_capture,
            "delta_residual_output_share_b_minus_a": delta_residual_share,
            "delta_retention_minus_leak_db_b_minus_a": delta_retention_minus_leak,
            "better_source_retention_candidate": better_source_retention_candidate,
            "more_interference_leaky_candidate": more_interference_leaky_candidate,
            "more_residual_heavy_candidate": more_residual_heavy_candidate,
            "better_retention_minus_leak_candidate": better_retention_minus_leak_candidate,
        }
        pair_rows.append(row)
    def count_key(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
        return count_value(rows, key)

    label_level_rows: list[dict[str, Any]] = []
    if blind_key is not None:
        decode_keys = [
            "better_source_retention_candidate",
            "more_interference_leaky_candidate",
            "more_residual_heavy_candidate",
            "better_retention_minus_leak_candidate",
        ]
        for row in pair_rows:
            decoded_row = {
                "sample_id": row["sample_id"],
                "better_output": row["better_output"],
                "scenario": row["scenario"],
                "target_status": row["target_status"],
                "interference_profile": row["interference_profile"],
                "target_interference_bucket": row["target_interference_bucket"],
                "target_present": row["target_present"],
                "interference_present": row["interference_present"],
                "delta_target_capture_db_b_minus_a": row["delta_target_capture_db_b_minus_a"],
                "delta_interference_capture_db_b_minus_a": row["delta_interference_capture_db_b_minus_a"],
                "delta_residual_output_share_b_minus_a": row["delta_residual_output_share_b_minus_a"],
                "delta_retention_minus_leak_db_b_minus_a": row["delta_retention_minus_leak_db_b_minus_a"],
            }
            for key in decode_keys:
                raw_value = row[key]
                if raw_value == "file_a":
                    decoded_row[key.replace("_candidate", "_label")] = row["file_a_label"]
                elif raw_value == "file_b":
                    decoded_row[key.replace("_candidate", "_label")] = row["file_b_label"]
                else:
                    decoded_row[key.replace("_candidate", "_label")] = raw_value
            label_level_rows.append(decoded_row)
    decoded_means = build_decoded_means(pair_rows)

    def count_label_key(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
        return count_value(rows, key)

    group_summaries = {
        "scenario_groups": {},
        "target_status_groups": {},
        "interference_profile_groups": {},
        "target_interference_bucket_groups": {},
    }
    if pair_rows:
        grouped_rows: dict[str, dict[str, list[dict[str, Any]]]] = {
            "scenario_groups": {},
            "target_status_groups": {},
            "interference_profile_groups": {},
            "target_interference_bucket_groups": {},
        }
        for row in pair_rows:
            for key, field in (
                ("scenario_groups", "scenario"),
                ("target_status_groups", "target_status"),
                ("interference_profile_groups", "interference_profile"),
                ("target_interference_bucket_groups", "target_interference_bucket"),
            ):
                group_key = str(row[field])
                grouped_rows[key].setdefault(group_key, []).append(row)
        group_summaries = {
            group_name: {
                group_key: summarize_group_rows(rows)
                for group_key, rows in sorted(group_map.items())
            }
            for group_name, group_map in grouped_rows.items()
        }

    summary = {
        "pack_dir": serialize_repo_path(args.pack_dir),
        "num_samples": len(pair_rows),
        "sample_rate": args.sample_rate,
        "source_retention_threshold_db": args.source_retention_threshold_db,
        "interference_leak_threshold_db": args.interference_leak_threshold_db,
        "residual_share_threshold": args.residual_share_threshold,
        "retention_minus_leak_threshold_db": args.retention_minus_leak_threshold_db,
        "better_source_retention_candidate_counts": count_key(pair_rows, "better_source_retention_candidate"),
        "more_interference_leaky_candidate_counts": count_key(pair_rows, "more_interference_leaky_candidate"),
        "more_residual_heavy_candidate_counts": count_key(pair_rows, "more_residual_heavy_candidate"),
        "better_retention_minus_leak_candidate_counts": count_key(pair_rows, "better_retention_minus_leak_candidate"),
        "decoded_label_counts": {
            "better_source_retention_label": count_label_key(label_level_rows, "better_source_retention_label"),
            "more_interference_leaky_label": count_label_key(label_level_rows, "more_interference_leaky_label"),
            "more_residual_heavy_label": count_label_key(label_level_rows, "more_residual_heavy_label"),
            "better_retention_minus_leak_label": count_label_key(label_level_rows, "better_retention_minus_leak_label"),
        },
        "decoded_mean_metrics_by_label": decoded_means,
        **group_summaries,
        "top_abs_target_capture_deltas": sorted(
            [row for row in pair_rows if row["delta_target_capture_db_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_target_capture_db_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
        "top_abs_interference_capture_deltas": sorted(
            [row for row in pair_rows if row["delta_interference_capture_db_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_interference_capture_db_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
        "top_abs_residual_share_deltas": sorted(
            [row for row in pair_rows if row["delta_residual_output_share_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_residual_output_share_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
        "top_abs_retention_minus_leak_deltas": sorted(
            [row for row in pair_rows if row["delta_retention_minus_leak_db_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_retention_minus_leak_db_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    with (output_dir / "per_sample_pair_metrics.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for row in pair_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    with (output_dir / "label_level_view.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for row in label_level_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
