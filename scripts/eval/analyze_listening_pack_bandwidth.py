from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze candidate bandwidth / spectral narrowing patterns inside a listening pack."
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--n-fft", type=int, default=1024)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--rolloff-percent", type=float, default=0.95)
    parser.add_argument(
        "--narrow-rolloff-threshold-hz",
        type=float,
        default=250.0,
        help="Minimum rolloff drop to flag a candidate as narrower.",
    )
    parser.add_argument(
        "--narrow-upper-vs-mid-threshold-db",
        type=float,
        default=1.0,
        help="Minimum upper-vs-mid drop in dB to flag a candidate as narrower.",
    )
    parser.add_argument(
        "--narrow-frame-upper-p90-threshold",
        type=float,
        default=0.15,
        help="Minimum frame-level upper-band p90 drop to flag a candidate as narrower.",
    )
    parser.add_argument(
        "--narrow-score-threshold",
        type=int,
        default=2,
        help="Number of narrowing indicators required to flag one candidate as narrower.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=12,
    )
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    waveform, sample_rate = sf.read(str(path), always_2d=False)
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    return waveform, sample_rate


def stft_power(
    waveform: np.ndarray,
    n_fft: int,
    hop_length: int,
) -> np.ndarray:
    if waveform.shape[0] < n_fft:
        pad_width = n_fft - waveform.shape[0]
        waveform = np.pad(waveform, (0, pad_width))
    window = np.hanning(n_fft).astype(np.float32)
    frames: list[np.ndarray] = []
    last_start = waveform.shape[0] - n_fft
    for start in range(0, max(last_start + 1, 1), hop_length):
        frame = waveform[start : start + n_fft]
        if frame.shape[0] < n_fft:
            frame = np.pad(frame, (0, n_fft - frame.shape[0]))
        frames.append(np.fft.rfft(frame * window))
    spec = np.stack(frames, axis=0)
    return np.abs(spec).astype(np.float32) ** 2


def safe_log10(value: float, eps: float = 1e-12) -> float:
    return float(10.0 * np.log10(max(value, eps)))


def band_power_ratio(power: np.ndarray, freqs: np.ndarray, low: float, high: float) -> float:
    mask = (freqs >= low) & (freqs < high)
    total = float(np.sum(power))
    if total <= 0.0:
        return 0.0
    return float(np.sum(power[..., mask]) / total)


def spectral_rolloff_hz(mean_power: np.ndarray, freqs: np.ndarray, rolloff_percent: float) -> float:
    cumulative = np.cumsum(mean_power)
    threshold = float(cumulative[-1] * rolloff_percent)
    index = int(np.searchsorted(cumulative, threshold, side="left"))
    index = min(max(index, 0), freqs.shape[0] - 1)
    return float(freqs[index])


def analyze_audio(
    path: Path,
    n_fft: int,
    hop_length: int,
    rolloff_percent: float,
) -> dict[str, Any]:
    waveform, sample_rate = load_audio(path)
    power = stft_power(waveform, n_fft=n_fft, hop_length=hop_length)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate).astype(np.float32)
    mean_power = power.mean(axis=0)

    low_share = band_power_ratio(mean_power, freqs, 0.0, 1000.0)
    body_share = band_power_ratio(mean_power, freqs, 1000.0, 3000.0)
    presence_share = band_power_ratio(mean_power, freqs, 3000.0, 6000.0)
    air_share = band_power_ratio(mean_power, freqs, 6000.0, min(8000.0, sample_rate / 2.0))
    upper_share = presence_share + air_share

    frame_totals = power.sum(axis=1) + 1e-12
    upper_mask = (freqs >= 3000.0) & (freqs < min(8000.0, sample_rate / 2.0))
    frame_upper_share = power[:, upper_mask].sum(axis=1) / frame_totals
    frame_presence_share = power[:, (freqs >= 3000.0) & (freqs < 6000.0)].sum(axis=1) / frame_totals

    rms = float(np.sqrt(np.mean(np.square(waveform)) + 1e-12))
    peak = float(np.max(np.abs(waveform)) + 1e-12)

    return {
        "path": serialize_repo_path(path),
        "sample_rate": sample_rate,
        "duration_sec": float(waveform.shape[0] / sample_rate),
        "rms_dbfs": safe_log10(rms**2),
        "peak_dbfs": safe_log10(peak**2),
        "spectral_centroid_hz": float(np.sum(freqs * mean_power) / (np.sum(mean_power) + 1e-12)),
        "rolloff_95_hz": spectral_rolloff_hz(mean_power, freqs, rolloff_percent),
        "band_share_0_1k": low_share,
        "band_share_1k_3k": body_share,
        "band_share_3k_6k": presence_share,
        "band_share_6k_8k": air_share,
        "band_share_3k_8k": upper_share,
        "upper_vs_mid_db": safe_log10(upper_share / max(body_share, 1e-12)),
        "upper_vs_low_db": safe_log10(upper_share / max(low_share, 1e-12)),
        "frame_upper_share_p10": float(np.percentile(frame_upper_share, 10)),
        "frame_upper_share_p50": float(np.percentile(frame_upper_share, 50)),
        "frame_upper_share_p90": float(np.percentile(frame_upper_share, 90)),
        "frame_presence_share_p90": float(np.percentile(frame_presence_share, 90)),
    }


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


def compare_pair(
    file_a_metrics: dict[str, Any],
    file_b_metrics: dict[str, Any],
    narrow_rolloff_threshold_hz: float,
    narrow_upper_vs_mid_threshold_db: float,
    narrow_frame_upper_p90_threshold: float,
    narrow_score_threshold: int,
) -> dict[str, Any]:
    delta_rolloff_hz = float(file_b_metrics["rolloff_95_hz"] - file_a_metrics["rolloff_95_hz"])
    delta_centroid_hz = float(file_b_metrics["spectral_centroid_hz"] - file_a_metrics["spectral_centroid_hz"])
    delta_upper_vs_mid_db = float(file_b_metrics["upper_vs_mid_db"] - file_a_metrics["upper_vs_mid_db"])
    delta_upper_share = float(file_b_metrics["band_share_3k_8k"] - file_a_metrics["band_share_3k_8k"])
    delta_frame_upper_p90 = float(file_b_metrics["frame_upper_share_p90"] - file_a_metrics["frame_upper_share_p90"])

    score_file_a = 0
    score_file_b = 0
    evidence_file_a: list[str] = []
    evidence_file_b: list[str] = []

    if delta_rolloff_hz <= -narrow_rolloff_threshold_hz:
        score_file_b += 1
        evidence_file_b.append("lower_rolloff")
    elif delta_rolloff_hz >= narrow_rolloff_threshold_hz:
        score_file_a += 1
        evidence_file_a.append("lower_rolloff")

    if delta_upper_vs_mid_db <= -narrow_upper_vs_mid_threshold_db:
        score_file_b += 1
        evidence_file_b.append("lower_upper_vs_mid")
    elif delta_upper_vs_mid_db >= narrow_upper_vs_mid_threshold_db:
        score_file_a += 1
        evidence_file_a.append("lower_upper_vs_mid")

    if delta_frame_upper_p90 <= -narrow_frame_upper_p90_threshold:
        score_file_b += 1
        evidence_file_b.append("lower_frame_upper_p90")
    elif delta_frame_upper_p90 >= narrow_frame_upper_p90_threshold:
        score_file_a += 1
        evidence_file_a.append("lower_frame_upper_p90")

    narrower_candidate = "tie"
    if score_file_b >= narrow_score_threshold and score_file_b > score_file_a:
        narrower_candidate = "file_b"
    elif score_file_a >= narrow_score_threshold and score_file_a > score_file_b:
        narrower_candidate = "file_a"

    return {
        "delta_rolloff_hz_b_minus_a": delta_rolloff_hz,
        "delta_centroid_hz_b_minus_a": delta_centroid_hz,
        "delta_upper_vs_mid_db_b_minus_a": delta_upper_vs_mid_db,
        "delta_upper_share_b_minus_a": delta_upper_share,
        "delta_frame_upper_share_p90_b_minus_a": delta_frame_upper_p90,
        "narrowing_score_file_a": score_file_a,
        "narrowing_score_file_b": score_file_b,
        "narrowing_evidence_file_a": evidence_file_a,
        "narrowing_evidence_file_b": evidence_file_b,
        "narrower_candidate": narrower_candidate,
    }


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or (args.pack_dir / "bandwidth_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

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
        file_a_metrics = analyze_audio(
            sample_dir / "candidate_a.wav",
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            rolloff_percent=args.rolloff_percent,
        )
        file_b_metrics = analyze_audio(
            sample_dir / "candidate_b.wav",
            n_fft=args.n_fft,
            hop_length=args.hop_length,
            rolloff_percent=args.rolloff_percent,
        )
        pair_cmp = compare_pair(
            file_a_metrics=file_a_metrics,
            file_b_metrics=file_b_metrics,
            narrow_rolloff_threshold_hz=args.narrow_rolloff_threshold_hz,
            narrow_upper_vs_mid_threshold_db=args.narrow_upper_vs_mid_threshold_db,
            narrow_frame_upper_p90_threshold=args.narrow_frame_upper_p90_threshold,
            narrow_score_threshold=args.narrow_score_threshold,
        )
        row = {
            "sample_id": sample_id,
            "note": sample_meta.get("note", ""),
            "better_output": listening_sheet.get(sample_id, {}).get("better_output", ""),
            "file_a_name": "candidate_a.wav",
            "file_b_name": "candidate_b.wav",
            "file_a_label": blind_mapping.get(sample_id, {}).get("candidate_a", "candidate_a"),
            "file_b_label": blind_mapping.get(sample_id, {}).get("candidate_b", "candidate_b"),
            "file_a_metrics": file_a_metrics,
            "file_b_metrics": file_b_metrics,
            **pair_cmp,
        }
        pair_rows.append(row)

    narrower_counts: dict[str, int] = {}
    for row in pair_rows:
        key = row["narrower_candidate"]
        narrower_counts[key] = narrower_counts.get(key, 0) + 1

    label_level_rows: list[dict[str, Any]] = []
    if blind_key is not None:
        for row in pair_rows:
            narrower_label = "tie"
            if row["narrower_candidate"] == "file_a":
                narrower_label = row["file_a_label"]
            elif row["narrower_candidate"] == "file_b":
                narrower_label = row["file_b_label"]
            label_level_rows.append(
                {
                    "sample_id": row["sample_id"],
                    "better_output": row["better_output"],
                    "narrower_label": narrower_label,
                    "delta_rolloff_hz_b_minus_a": row["delta_rolloff_hz_b_minus_a"],
                    "delta_upper_vs_mid_db_b_minus_a": row["delta_upper_vs_mid_db_b_minus_a"],
                }
            )

    by_abs_rolloff = sorted(pair_rows, key=lambda row: abs(row["delta_rolloff_hz_b_minus_a"]), reverse=True)
    by_abs_upper_vs_mid = sorted(
        pair_rows, key=lambda row: abs(row["delta_upper_vs_mid_db_b_minus_a"]), reverse=True
    )

    summary = {
        "pack_dir": serialize_repo_path(args.pack_dir),
        "num_samples": len(pair_rows),
        "n_fft": args.n_fft,
        "hop_length": args.hop_length,
        "rolloff_percent": args.rolloff_percent,
        "narrow_rolloff_threshold_hz": args.narrow_rolloff_threshold_hz,
        "narrow_upper_vs_mid_threshold_db": args.narrow_upper_vs_mid_threshold_db,
        "narrow_frame_upper_p90_threshold": args.narrow_frame_upper_p90_threshold,
        "narrow_score_threshold": args.narrow_score_threshold,
        "narrower_candidate_counts": narrower_counts,
        "top_abs_rolloff_deltas": [
            {
                "sample_id": row["sample_id"],
                "file_a_label": row["file_a_label"],
                "file_b_label": row["file_b_label"],
                "delta_rolloff_hz_b_minus_a": row["delta_rolloff_hz_b_minus_a"],
                "delta_upper_vs_mid_db_b_minus_a": row["delta_upper_vs_mid_db_b_minus_a"],
                "delta_frame_upper_share_p90_b_minus_a": row["delta_frame_upper_share_p90_b_minus_a"],
                "narrower_candidate": row["narrower_candidate"],
                "narrowing_score_file_a": row["narrowing_score_file_a"],
                "narrowing_score_file_b": row["narrowing_score_file_b"],
                "narrowing_evidence_file_a": row["narrowing_evidence_file_a"],
                "narrowing_evidence_file_b": row["narrowing_evidence_file_b"],
                "better_output": row["better_output"],
                "note": row["note"],
            }
            for row in by_abs_rolloff[: args.top_k]
        ],
        "top_abs_upper_vs_mid_deltas": [
            {
                "sample_id": row["sample_id"],
                "file_a_label": row["file_a_label"],
                "file_b_label": row["file_b_label"],
                "delta_rolloff_hz_b_minus_a": row["delta_rolloff_hz_b_minus_a"],
                "delta_upper_vs_mid_db_b_minus_a": row["delta_upper_vs_mid_db_b_minus_a"],
                "delta_frame_upper_share_p90_b_minus_a": row["delta_frame_upper_share_p90_b_minus_a"],
                "narrower_candidate": row["narrower_candidate"],
                "narrowing_score_file_a": row["narrowing_score_file_a"],
                "narrowing_score_file_b": row["narrowing_score_file_b"],
                "narrowing_evidence_file_a": row["narrowing_evidence_file_a"],
                "narrowing_evidence_file_b": row["narrowing_evidence_file_b"],
                "better_output": row["better_output"],
                "note": row["note"],
            }
            for row in by_abs_upper_vs_mid[: args.top_k]
        ],
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "per_sample_pair_metrics.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in pair_rows),
        encoding="utf-8",
        newline="\n",
    )
    if label_level_rows:
        (output_dir / "label_level_view.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in label_level_rows),
            encoding="utf-8",
            newline="\n",
        )

    print(
        json.dumps(
            {
                "pack_dir": serialize_repo_path(args.pack_dir),
                "output_dir": serialize_repo_path(output_dir),
                "num_samples": len(pair_rows),
                "narrower_candidate_counts": narrower_counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
