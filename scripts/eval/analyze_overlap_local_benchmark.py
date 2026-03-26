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
            "Analyze a listening pack on short overlap-local benchmark windows and summarize "
            "whether local metrics align better with human listening decisions."
        )
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--benchmark-manifest", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--source-retention-threshold-db", type=float, default=0.5)
    parser.add_argument("--interference-leak-threshold-db", type=float, default=0.5)
    parser.add_argument("--retention-minus-leak-threshold-db", type=float, default=0.75)
    parser.add_argument("--artifact-share-threshold", type=float, default=0.03)
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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_listening_sheet(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    if not path.exists():
        return rows
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows[str(row["sample_id"])] = row
    return rows


def decode_sheet_choice(sheet_row: dict[str, str], candidate_info: dict[str, str]) -> str:
    raw_value = str(sheet_row.get("better_output", "")).strip()
    if raw_value == "file_a":
        return str(candidate_info["file_a_label"])
    if raw_value == "file_b":
        return str(candidate_info["file_b_label"])
    return raw_value


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
            "artifact_proxy_db": 0.0,
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
        "artifact_proxy_db": safe_log10(residual_share + eps),
        "projection_coefficients": [float(x) for x in coefficients.tolist()],
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


def component_cache_key(sample_id: str, index: int, component: dict[str, Any]) -> str:
    start_sec = component.get("clip_start_sec")
    duration_sec = component["clip_duration_sec"]
    gain_db = component.get("gain_db", 0.0)
    return (
        f"{sample_id}_{index:02d}_{component['kind']}"
        f"_start{start_sec if start_sec is not None else 'none'}"
        f"_dur{duration_sec}_gain{gain_db:.2f}.wav"
    ).replace(":", "_")


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


def reconstruct_category_tracks(
    sample_id: str,
    original_sample_meta: dict[str, Any],
    pack_mixture: np.ndarray,
    cache_dir: Path,
    sample_rate: int,
) -> dict[str, np.ndarray]:
    num_samples = pack_mixture.shape[0]
    target_sum = np.zeros(num_samples, dtype=np.float32)
    speech_sum = np.zeros(num_samples, dtype=np.float32)
    total_interference_sum = np.zeros(num_samples, dtype=np.float32)

    for component_index, component in enumerate(original_sample_meta["components"]):
        component_track = build_component_track(
            component=component,
            cache_dir=cache_dir,
            sample_id=sample_id,
            component_index=component_index,
            num_samples=num_samples,
            sample_rate=sample_rate,
        )
        category = categorize_component_kind(component["kind"])
        if category == "target":
            target_sum += component_track
        else:
            total_interference_sum += component_track
            if category == "speech":
                speech_sum += component_track

    raw_mix = target_sum + total_interference_sum
    denom = energy(raw_mix)
    alignment_scale = float(np.dot(raw_mix, pack_mixture) / denom) if denom > 1e-12 else 1.0
    return {
        "target_track": target_sum * alignment_scale,
        "speech_track": speech_sum * alignment_scale,
        "interference_track": total_interference_sum * alignment_scale,
        "alignment_scale": alignment_scale,
    }


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


def crop_waveform(waveform: np.ndarray, start_sec: float, duration_sec: float, sample_rate: int) -> np.ndarray:
    start_sample = max(0, int(round(start_sec * sample_rate)))
    length_samples = max(1, int(round(duration_sec * sample_rate)))
    end_sample = min(waveform.shape[0], start_sample + length_samples)
    return fit_or_pad(waveform[start_sample:end_sample], length_samples)


def analyze_candidate(
    waveform: np.ndarray,
    target_track: np.ndarray,
    speech_track: np.ndarray,
    total_interference_track: np.ndarray,
) -> dict[str, Any]:
    target_capture_db, target_scale = capture_db(waveform, target_track)
    speech_capture_db, speech_scale = capture_db(waveform, speech_track)
    total_interference_capture_db, total_interference_scale = capture_db(waveform, total_interference_track)
    residual_metrics = joint_residual_metrics(waveform, target_track, total_interference_track)

    retention_minus_speech_leak_db = None
    if target_capture_db is not None and speech_capture_db is not None:
        retention_minus_speech_leak_db = float(target_capture_db - speech_capture_db)

    retention_minus_total_leak_db = None
    if target_capture_db is not None and total_interference_capture_db is not None:
        retention_minus_total_leak_db = float(target_capture_db - total_interference_capture_db)

    return {
        "rms_dbfs": safe_log10((np.sqrt(np.mean(np.square(waveform)) + 1e-12)) ** 2),
        "target_capture_db": target_capture_db,
        "target_projection_scale": target_scale,
        "speech_interference_capture_db": speech_capture_db,
        "speech_interference_projection_scale": speech_scale,
        "total_interference_capture_db": total_interference_capture_db,
        "total_interference_projection_scale": total_interference_scale,
        "retention_minus_speech_leak_db": retention_minus_speech_leak_db,
        "retention_minus_total_leak_db": retention_minus_total_leak_db,
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


def compare_optional_lower_is_better(
    value_a: float | None,
    value_b: float | None,
    threshold: float,
) -> tuple[str, float | None]:
    if value_a is None or value_b is None:
        return "not_applicable", None
    delta = float(value_b - value_a)
    if delta <= -threshold:
        return "file_b", delta
    if delta >= threshold:
        return "file_a", delta
    return "tie", delta


def average_optional(values: list[float | None]) -> float | None:
    filtered = [float(x) for x in values if x is not None]
    if not filtered:
        return None
    return float(sum(filtered) / len(filtered))


def decode_choice(row: dict[str, Any], key: str) -> str:
    raw_value = str(row[key])
    if raw_value == "file_a":
        return str(row["file_a_label"])
    if raw_value == "file_b":
        return str(row["file_b_label"])
    return raw_value


def count_values(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[key])
        counts[value] = counts.get(value, 0) + 1
    return counts


def count_decoded_values(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = decode_choice(row, key)
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_decoded_means(rows: list[dict[str, Any]]) -> dict[str, dict[str, float | None]]:
    metric_names = (
        "target_capture_db",
        "speech_interference_capture_db",
        "total_interference_capture_db",
        "retention_minus_speech_leak_db",
        "retention_minus_total_leak_db",
        "artifact_proxy_db",
        "residual_output_share",
        "joint_fit_r2",
    )
    buckets: dict[str, dict[str, list[float | None]]] = {}
    for row in rows:
        for label_key in ("file_a_label", "file_b_label"):
            label = str(row[label_key])
            metrics_key = "file_a_metrics" if label_key == "file_a_label" else "file_b_metrics"
            label_bucket = buckets.setdefault(label, {name: [] for name in metric_names})
            for metric_name in metric_names:
                label_bucket[metric_name].append(row[metrics_key].get(metric_name))
    return {
        label: {metric_name: average_optional(values) for metric_name, values in metrics.items()}
        for label, metrics in buckets.items()
    }


def expected_human_label_for_metric(row: dict[str, Any], metric_key: str) -> str:
    predicted = decode_choice(row, metric_key)
    if predicted in {"tie", "not_applicable"}:
        return predicted
    if metric_key in {
        "more_speech_interference_leaky_candidate",
        "more_total_interference_leaky_candidate",
        "more_artifact_proxy_heavy_candidate",
    }:
        if predicted == str(row["file_a_label"]):
            return str(row["file_b_label"])
        if predicted == str(row["file_b_label"]):
            return str(row["file_a_label"])
        return predicted
    return predicted


def build_human_alignment_summary(
    rows: list[dict[str, Any]],
    metric_keys: list[str],
) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {}
    for metric_key in metric_keys:
        counts = {
            "decisive_samples": 0,
            "aligned": 0,
            "contradicted": 0,
            "predicted_tie": 0,
            "not_applicable": 0,
        }
        for row in rows:
            human = str(row.get("human_decoded_better_output", ""))
            if not human or human in {"tie", "uncertain", "unscored"}:
                continue
            counts["decisive_samples"] += 1
            predicted = expected_human_label_for_metric(row, metric_key)
            if predicted == human:
                counts["aligned"] += 1
            elif predicted == "tie":
                counts["predicted_tie"] += 1
            elif predicted == "not_applicable":
                counts["not_applicable"] += 1
            else:
                counts["contradicted"] += 1
        summary[metric_key] = counts
    return summary


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or (args.pack_dir / "overlap_local_benchmark")
    output_dir.mkdir(parents=True, exist_ok=True)
    cache_dir = output_dir / "_component_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    benchmark_rows = {str(row["sample_id"]): row for row in load_jsonl(args.benchmark_manifest)}
    pack_summary = load_json(args.pack_dir / "summary.json") if (args.pack_dir / "summary.json").exists() else {}
    blind_key = load_json(args.pack_dir / "blind_key.json") if (args.pack_dir / "blind_key.json").exists() else None
    blind_mapping = {}
    if blind_key is not None:
        blind_mapping = {row["sample_id"]: row for row in blind_key["mapping"]}
    listening_sheet = load_listening_sheet(args.pack_dir / "listening_sheet.csv")

    human_decisions: dict[str, str] = {}
    decoded_path = args.pack_dir / "listening_review_decoded_summary.json"
    if decoded_path.exists():
        decoded_summary = load_json(decoded_path)
        for row in decoded_summary.get("samples", []):
            human_decisions[str(row["sample_id"])] = str(row.get("decoded_better_output", ""))

    sample_dirs = sorted(
        path for path in args.pack_dir.iterdir() if path.is_dir() and (path / "sample_meta.json").exists()
    )

    rows: list[dict[str, Any]] = []
    for sample_dir in sample_dirs:
        sample_meta = load_json(sample_dir / "sample_meta.json")
        sample_id = str(sample_meta["sample_id"])
        benchmark = benchmark_rows.get(sample_id)
        if benchmark is None:
            continue

        sheet_row = listening_sheet.get(sample_id, {})
        candidate_info = resolve_pair_candidate_info(
            pack_summary=pack_summary,
            sample_meta=sample_meta,
            sheet_row=sheet_row,
            blind_mapping_row=blind_mapping.get(sample_id, {}),
        )
        human_choice = human_decisions.get(sample_id, "")
        if not human_choice:
            human_choice = decode_sheet_choice(sheet_row, candidate_info)

        mixture, mixture_sr = load_audio(sample_dir / "mixture.wav")
        candidate_a, sr_a = load_audio(sample_dir / candidate_info["file_a_name"])
        candidate_b, sr_b = load_audio(sample_dir / candidate_info["file_b_name"])
        if mixture_sr != args.sample_rate or sr_a != args.sample_rate or sr_b != args.sample_rate:
            raise ValueError(f"Sample rate mismatch in {sample_id}")

        original_mixture_path = ROOT / sample_meta["mixture_audio_path"]
        original_sample_meta = load_json(original_mixture_path.parent / "sample_meta.json")
        tracks = reconstruct_category_tracks(
            sample_id=sample_id,
            original_sample_meta=original_sample_meta,
            pack_mixture=mixture,
            cache_dir=cache_dir,
            sample_rate=args.sample_rate,
        )

        window_start_sec = float(benchmark["window_start_sec"])
        window_duration_sec = float(benchmark["window_duration_sec"])

        target_window = crop_waveform(tracks["target_track"], window_start_sec, window_duration_sec, args.sample_rate)
        speech_window = crop_waveform(tracks["speech_track"], window_start_sec, window_duration_sec, args.sample_rate)
        total_interference_window = crop_waveform(
            tracks["interference_track"], window_start_sec, window_duration_sec, args.sample_rate
        )
        candidate_a_window = crop_waveform(candidate_a, window_start_sec, window_duration_sec, args.sample_rate)
        candidate_b_window = crop_waveform(candidate_b, window_start_sec, window_duration_sec, args.sample_rate)

        metrics_a = analyze_candidate(
            waveform=candidate_a_window,
            target_track=target_window,
            speech_track=speech_window,
            total_interference_track=total_interference_window,
        )
        metrics_b = analyze_candidate(
            waveform=candidate_b_window,
            target_track=target_window,
            speech_track=speech_window,
            total_interference_track=total_interference_window,
        )

        better_source_retention_candidate, delta_target_capture = compare_optional_higher_is_better(
            metrics_a["target_capture_db"],
            metrics_b["target_capture_db"],
            args.source_retention_threshold_db,
        )
        more_speech_interference_leaky_candidate, delta_speech_interference_capture = compare_optional_higher_is_better(
            metrics_a["speech_interference_capture_db"],
            metrics_b["speech_interference_capture_db"],
            args.interference_leak_threshold_db,
        )
        more_total_interference_leaky_candidate, delta_total_interference_capture = compare_optional_higher_is_better(
            metrics_a["total_interference_capture_db"],
            metrics_b["total_interference_capture_db"],
            args.interference_leak_threshold_db,
        )
        better_retention_minus_speech_leak_candidate, delta_retention_minus_speech_leak = (
            compare_optional_higher_is_better(
                metrics_a["retention_minus_speech_leak_db"],
                metrics_b["retention_minus_speech_leak_db"],
                args.retention_minus_leak_threshold_db,
            )
        )
        better_retention_minus_total_leak_candidate, delta_retention_minus_total_leak = (
            compare_optional_higher_is_better(
                metrics_a["retention_minus_total_leak_db"],
                metrics_b["retention_minus_total_leak_db"],
                args.retention_minus_leak_threshold_db,
            )
        )
        more_artifact_proxy_heavy_candidate, delta_artifact_proxy = compare_optional_higher_is_better(
            metrics_a["residual_output_share"],
            metrics_b["residual_output_share"],
            args.artifact_share_threshold,
        )

        rows.append(
            {
                "sample_id": sample_id,
                "note": benchmark.get("note", sample_meta.get("note", "")),
                "benchmark_kind": benchmark["benchmark_kind"],
                "window_start_sec": window_start_sec,
                "window_duration_sec": window_duration_sec,
                "target_active_start_sec": benchmark.get("target_active_start_sec"),
                "target_active_end_sec": benchmark.get("target_active_end_sec"),
                "human_decoded_better_output": human_choice,
                "file_a_name": candidate_info["file_a_name"],
                "file_b_name": candidate_info["file_b_name"],
                "file_a_label": candidate_info["file_a_label"],
                "file_b_label": candidate_info["file_b_label"],
                "file_a_metrics": metrics_a,
                "file_b_metrics": metrics_b,
                "delta_target_capture_db_b_minus_a": delta_target_capture,
                "delta_speech_interference_capture_db_b_minus_a": delta_speech_interference_capture,
                "delta_total_interference_capture_db_b_minus_a": delta_total_interference_capture,
                "delta_retention_minus_speech_leak_db_b_minus_a": delta_retention_minus_speech_leak,
                "delta_retention_minus_total_leak_db_b_minus_a": delta_retention_minus_total_leak,
                "delta_residual_output_share_b_minus_a": delta_artifact_proxy,
                "better_source_retention_candidate": better_source_retention_candidate,
                "more_speech_interference_leaky_candidate": more_speech_interference_leaky_candidate,
                "more_total_interference_leaky_candidate": more_total_interference_leaky_candidate,
                "better_retention_minus_speech_leak_candidate": better_retention_minus_speech_leak_candidate,
                "better_retention_minus_total_leak_candidate": better_retention_minus_total_leak_candidate,
                "more_artifact_proxy_heavy_candidate": more_artifact_proxy_heavy_candidate,
            }
        )

    metric_keys = [
        "better_source_retention_candidate",
        "more_speech_interference_leaky_candidate",
        "more_total_interference_leaky_candidate",
        "better_retention_minus_speech_leak_candidate",
        "better_retention_minus_total_leak_candidate",
        "more_artifact_proxy_heavy_candidate",
    ]
    summary = {
        "pack_dir": serialize_repo_path(args.pack_dir),
        "benchmark_manifest": serialize_repo_path(args.benchmark_manifest),
        "num_samples": len(rows),
        "source_retention_threshold_db": args.source_retention_threshold_db,
        "interference_leak_threshold_db": args.interference_leak_threshold_db,
        "retention_minus_leak_threshold_db": args.retention_minus_leak_threshold_db,
        "artifact_share_threshold": args.artifact_share_threshold,
        "better_source_retention_candidate_counts": count_values(rows, "better_source_retention_candidate"),
        "more_speech_interference_leaky_candidate_counts": count_values(rows, "more_speech_interference_leaky_candidate"),
        "more_total_interference_leaky_candidate_counts": count_values(rows, "more_total_interference_leaky_candidate"),
        "better_retention_minus_speech_leak_candidate_counts": count_values(
            rows, "better_retention_minus_speech_leak_candidate"
        ),
        "better_retention_minus_total_leak_candidate_counts": count_values(
            rows, "better_retention_minus_total_leak_candidate"
        ),
        "more_artifact_proxy_heavy_candidate_counts": count_values(rows, "more_artifact_proxy_heavy_candidate"),
        "decoded_label_counts": {
            "better_source_retention_label": count_decoded_values(rows, "better_source_retention_candidate"),
            "more_speech_interference_leaky_label": count_decoded_values(rows, "more_speech_interference_leaky_candidate"),
            "more_total_interference_leaky_label": count_decoded_values(rows, "more_total_interference_leaky_candidate"),
            "better_retention_minus_speech_leak_label": count_decoded_values(
                rows, "better_retention_minus_speech_leak_candidate"
            ),
            "better_retention_minus_total_leak_label": count_decoded_values(
                rows, "better_retention_minus_total_leak_candidate"
            ),
            "more_artifact_proxy_heavy_label": count_decoded_values(rows, "more_artifact_proxy_heavy_candidate"),
        },
        "decoded_mean_metrics_by_label": build_decoded_means(rows),
        "human_alignment_summary": build_human_alignment_summary(rows, metric_keys),
        "top_abs_speech_interference_capture_deltas": sorted(
            [row for row in rows if row["delta_speech_interference_capture_db_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_speech_interference_capture_db_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
        "top_abs_retention_minus_speech_leak_deltas": sorted(
            [row for row in rows if row["delta_retention_minus_speech_leak_db_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_retention_minus_speech_leak_db_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
        "top_abs_artifact_proxy_deltas": sorted(
            [row for row in rows if row["delta_residual_output_share_b_minus_a"] is not None],
            key=lambda row: abs(float(row["delta_residual_output_share_b_minus_a"])),
            reverse=True,
        )[: args.top_k],
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    with (output_dir / "per_sample_metrics.jsonl").open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
