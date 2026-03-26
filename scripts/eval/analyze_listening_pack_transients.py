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
        description="Analyze transient-band retention inside a listening pack."
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--n-fft", type=int, default=1024)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--top-transient-ratio", type=float, default=0.12)
    parser.add_argument("--transient-min-count", type=int, default=8)
    parser.add_argument("--presence-low-hz", type=float, default=3000.0)
    parser.add_argument("--presence-high-hz", type=float, default=8000.0)
    parser.add_argument("--mid-low-hz", type=float, default=800.0)
    parser.add_argument("--mid-high-hz", type=float, default=3000.0)
    parser.add_argument(
        "--loss-threshold-db",
        type=float,
        default=1.0,
        help="Minimum transient upper-vs-mid retention drop to flag a candidate as more transient-lossy.",
    )
    parser.add_argument(
        "--loss-frame-ratio-threshold",
        type=float,
        default=0.20,
        help="Minimum extra fraction of transient frames with strong upper-band loss.",
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


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    waveform, sample_rate = sf.read(str(path), always_2d=False)
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    return waveform, sample_rate


def stft_power(waveform: np.ndarray, n_fft: int, hop_length: int) -> np.ndarray:
    if waveform.shape[0] < n_fft:
        waveform = np.pad(waveform, (0, n_fft - waveform.shape[0]))
    window = np.hanning(n_fft).astype(np.float32)
    frames: list[np.ndarray] = []
    last_start = waveform.shape[0] - n_fft
    for start in range(0, max(last_start + 1, 1), hop_length):
        frame = waveform[start : start + n_fft]
        if frame.shape[0] < n_fft:
            frame = np.pad(frame, (0, n_fft - frame.shape[0]))
        frames.append(np.fft.rfft(frame * window))
    return (np.abs(np.stack(frames, axis=0)).astype(np.float32) ** 2)


def band_energy(power: np.ndarray, freqs: np.ndarray, low: float, high: float) -> np.ndarray:
    mask = (freqs >= low) & (freqs < high)
    return power[:, mask].sum(axis=1)


def safe_log_ratio(numer: np.ndarray, denom: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    return 10.0 * np.log10((numer + eps) / (denom + eps))


def detect_transient_indices(
    mixture_power: np.ndarray,
    freqs: np.ndarray,
    low_hz: float,
    high_hz: float,
    top_ratio: float,
    min_count: int,
) -> np.ndarray:
    mask = (freqs >= low_hz) & (freqs < high_hz)
    log_power = np.log1p(mixture_power[:, mask])
    flux = np.maximum(log_power[1:] - log_power[:-1], 0.0).sum(axis=1)
    if flux.size == 0:
        return np.array([0], dtype=np.int64)
    frame_count = flux.shape[0]
    keep = max(min_count, int(np.ceil(frame_count * top_ratio)))
    keep = min(max(keep, 1), frame_count)
    top_indices = np.argsort(flux)[-keep:]
    # +1 because flux[t] uses frames t and t+1; use the later frame as the transient frame.
    return np.sort(top_indices + 1).astype(np.int64)


def analyze_candidate_transients(
    candidate_power: np.ndarray,
    mixture_power: np.ndarray,
    freqs: np.ndarray,
    transient_indices: np.ndarray,
    mid_low_hz: float,
    mid_high_hz: float,
    presence_low_hz: float,
    presence_high_hz: float,
) -> dict[str, Any]:
    frame_count = min(candidate_power.shape[0], mixture_power.shape[0])
    transient_indices = transient_indices[transient_indices < frame_count]
    if transient_indices.size == 0:
        transient_indices = np.array([0], dtype=np.int64)

    candidate_power = candidate_power[:frame_count]
    mixture_power = mixture_power[:frame_count]

    cand_mid = band_energy(candidate_power, freqs, mid_low_hz, mid_high_hz)
    cand_presence = band_energy(candidate_power, freqs, presence_low_hz, presence_high_hz)
    mix_mid = band_energy(mixture_power, freqs, mid_low_hz, mid_high_hz)
    mix_presence = band_energy(mixture_power, freqs, presence_low_hz, presence_high_hz)

    transient_cand_mid = cand_mid[transient_indices]
    transient_cand_presence = cand_presence[transient_indices]
    transient_mix_mid = mix_mid[transient_indices]
    transient_mix_presence = mix_presence[transient_indices]

    mid_retention_db = safe_log_ratio(transient_cand_mid, transient_mix_mid)
    presence_retention_db = safe_log_ratio(transient_cand_presence, transient_mix_presence)
    upper_minus_mid_db = presence_retention_db - mid_retention_db

    strong_presence_loss = upper_minus_mid_db < -3.0
    return {
        "transient_frame_count": int(transient_indices.size),
        "transient_mid_retention_db_mean": float(np.mean(mid_retention_db)),
        "transient_presence_retention_db_mean": float(np.mean(presence_retention_db)),
        "transient_presence_minus_mid_retention_db_mean": float(np.mean(upper_minus_mid_db)),
        "transient_presence_minus_mid_retention_db_p10": float(np.percentile(upper_minus_mid_db, 10)),
        "transient_presence_minus_mid_retention_db_p50": float(np.percentile(upper_minus_mid_db, 50)),
        "transient_presence_minus_mid_retention_db_p90": float(np.percentile(upper_minus_mid_db, 90)),
        "strong_presence_loss_frame_ratio": float(np.mean(strong_presence_loss)),
    }


def compare_pair(
    metrics_a: dict[str, Any],
    metrics_b: dict[str, Any],
    loss_threshold_db: float,
    loss_frame_ratio_threshold: float,
) -> dict[str, Any]:
    delta_presence_minus_mid = float(
        metrics_b["transient_presence_minus_mid_retention_db_mean"]
        - metrics_a["transient_presence_minus_mid_retention_db_mean"]
    )
    delta_presence_p10 = float(
        metrics_b["transient_presence_minus_mid_retention_db_p10"]
        - metrics_a["transient_presence_minus_mid_retention_db_p10"]
    )
    delta_strong_loss_ratio = float(
        metrics_b["strong_presence_loss_frame_ratio"] - metrics_a["strong_presence_loss_frame_ratio"]
    )

    score_a = 0
    score_b = 0
    evidence_a: list[str] = []
    evidence_b: list[str] = []

    if delta_presence_minus_mid <= -loss_threshold_db:
        score_b += 1
        evidence_b.append("lower_presence_minus_mid_mean")
    elif delta_presence_minus_mid >= loss_threshold_db:
        score_a += 1
        evidence_a.append("lower_presence_minus_mid_mean")

    if delta_presence_p10 <= -loss_threshold_db:
        score_b += 1
        evidence_b.append("lower_presence_minus_mid_p10")
    elif delta_presence_p10 >= loss_threshold_db:
        score_a += 1
        evidence_a.append("lower_presence_minus_mid_p10")

    if delta_strong_loss_ratio >= loss_frame_ratio_threshold:
        score_b += 1
        evidence_b.append("higher_strong_presence_loss_ratio")
    elif delta_strong_loss_ratio <= -loss_frame_ratio_threshold:
        score_a += 1
        evidence_a.append("higher_strong_presence_loss_ratio")

    more_transient_lossy_candidate = "tie"
    if score_b >= 2 and score_b > score_a:
        more_transient_lossy_candidate = "file_b"
    elif score_a >= 2 and score_a > score_b:
        more_transient_lossy_candidate = "file_a"

    return {
        "delta_presence_minus_mid_retention_db_mean_b_minus_a": delta_presence_minus_mid,
        "delta_presence_minus_mid_retention_db_p10_b_minus_a": delta_presence_p10,
        "delta_strong_presence_loss_frame_ratio_b_minus_a": delta_strong_loss_ratio,
        "transient_loss_score_file_a": score_a,
        "transient_loss_score_file_b": score_b,
        "transient_loss_evidence_file_a": evidence_a,
        "transient_loss_evidence_file_b": evidence_b,
        "more_transient_lossy_candidate": more_transient_lossy_candidate,
    }


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir or (args.pack_dir / "transient_analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

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

        mixture, sample_rate = load_audio(sample_dir / "mixture.wav")
        cand_a, sr_a = load_audio(sample_dir / candidate_info["file_a_name"])
        cand_b, sr_b = load_audio(sample_dir / candidate_info["file_b_name"])
        if sample_rate != sr_a or sample_rate != sr_b:
            raise ValueError(f"Sample rate mismatch in {sample_id}")

        mixture_power = stft_power(mixture, n_fft=args.n_fft, hop_length=args.hop_length)
        cand_a_power = stft_power(cand_a, n_fft=args.n_fft, hop_length=args.hop_length)
        cand_b_power = stft_power(cand_b, n_fft=args.n_fft, hop_length=args.hop_length)
        freqs = np.fft.rfftfreq(args.n_fft, d=1.0 / sample_rate).astype(np.float32)
        transient_indices = detect_transient_indices(
            mixture_power=mixture_power,
            freqs=freqs,
            low_hz=args.presence_low_hz,
            high_hz=min(args.presence_high_hz, sample_rate / 2.0),
            top_ratio=args.top_transient_ratio,
            min_count=args.transient_min_count,
        )

        metrics_a = analyze_candidate_transients(
            candidate_power=cand_a_power,
            mixture_power=mixture_power,
            freqs=freqs,
            transient_indices=transient_indices,
            mid_low_hz=args.mid_low_hz,
            mid_high_hz=args.mid_high_hz,
            presence_low_hz=args.presence_low_hz,
            presence_high_hz=min(args.presence_high_hz, sample_rate / 2.0),
        )
        metrics_b = analyze_candidate_transients(
            candidate_power=cand_b_power,
            mixture_power=mixture_power,
            freqs=freqs,
            transient_indices=transient_indices,
            mid_low_hz=args.mid_low_hz,
            mid_high_hz=args.mid_high_hz,
            presence_low_hz=args.presence_low_hz,
            presence_high_hz=min(args.presence_high_hz, sample_rate / 2.0),
        )
        cmp_row = compare_pair(
            metrics_a=metrics_a,
            metrics_b=metrics_b,
            loss_threshold_db=args.loss_threshold_db,
            loss_frame_ratio_threshold=args.loss_frame_ratio_threshold,
        )

        row = {
            "sample_id": sample_id,
            "note": sample_meta.get("note", ""),
            "better_output": listening_sheet.get(sample_id, {}).get("better_output", ""),
            "file_a_name": candidate_info["file_a_name"],
            "file_b_name": candidate_info["file_b_name"],
            "file_a_label": candidate_info["file_a_label"],
            "file_b_label": candidate_info["file_b_label"],
            "transient_indices_count": int(transient_indices.size),
            "file_a_metrics": metrics_a,
            "file_b_metrics": metrics_b,
            **cmp_row,
        }
        pair_rows.append(row)

    loss_counts: dict[str, int] = {}
    for row in pair_rows:
        key = row["more_transient_lossy_candidate"]
        loss_counts[key] = loss_counts.get(key, 0) + 1

    label_level_rows: list[dict[str, Any]] = []
    if blind_key is not None:
        for row in pair_rows:
            loss_label = "tie"
            if row["more_transient_lossy_candidate"] == "file_a":
                loss_label = row["file_a_label"]
            elif row["more_transient_lossy_candidate"] == "file_b":
                loss_label = row["file_b_label"]
            label_level_rows.append(
                {
                    "sample_id": row["sample_id"],
                    "better_output": row["better_output"],
                    "more_transient_lossy_label": loss_label,
                    "delta_presence_minus_mid_retention_db_mean_b_minus_a": row[
                        "delta_presence_minus_mid_retention_db_mean_b_minus_a"
                    ],
                    "delta_strong_presence_loss_frame_ratio_b_minus_a": row[
                        "delta_strong_presence_loss_frame_ratio_b_minus_a"
                    ],
                }
            )

    by_abs_mean = sorted(
        pair_rows,
        key=lambda row: abs(row["delta_presence_minus_mid_retention_db_mean_b_minus_a"]),
        reverse=True,
    )
    by_abs_ratio = sorted(
        pair_rows,
        key=lambda row: abs(row["delta_strong_presence_loss_frame_ratio_b_minus_a"]),
        reverse=True,
    )

    summary = {
        "pack_dir": serialize_repo_path(args.pack_dir),
        "num_samples": len(pair_rows),
        "n_fft": args.n_fft,
        "hop_length": args.hop_length,
        "top_transient_ratio": args.top_transient_ratio,
        "transient_min_count": args.transient_min_count,
        "presence_low_hz": args.presence_low_hz,
        "presence_high_hz": args.presence_high_hz,
        "mid_low_hz": args.mid_low_hz,
        "mid_high_hz": args.mid_high_hz,
        "loss_threshold_db": args.loss_threshold_db,
        "loss_frame_ratio_threshold": args.loss_frame_ratio_threshold,
        "more_transient_lossy_candidate_counts": loss_counts,
        "top_abs_presence_minus_mid_mean_deltas": [
            {
                "sample_id": row["sample_id"],
                "file_a_label": row["file_a_label"],
                "file_b_label": row["file_b_label"],
                "delta_presence_minus_mid_retention_db_mean_b_minus_a": row[
                    "delta_presence_minus_mid_retention_db_mean_b_minus_a"
                ],
                "delta_presence_minus_mid_retention_db_p10_b_minus_a": row[
                    "delta_presence_minus_mid_retention_db_p10_b_minus_a"
                ],
                "delta_strong_presence_loss_frame_ratio_b_minus_a": row[
                    "delta_strong_presence_loss_frame_ratio_b_minus_a"
                ],
                "more_transient_lossy_candidate": row["more_transient_lossy_candidate"],
                "transient_loss_score_file_a": row["transient_loss_score_file_a"],
                "transient_loss_score_file_b": row["transient_loss_score_file_b"],
                "transient_loss_evidence_file_a": row["transient_loss_evidence_file_a"],
                "transient_loss_evidence_file_b": row["transient_loss_evidence_file_b"],
                "better_output": row["better_output"],
                "note": row["note"],
            }
            for row in by_abs_mean[: args.top_k]
        ],
        "top_abs_strong_loss_ratio_deltas": [
            {
                "sample_id": row["sample_id"],
                "file_a_label": row["file_a_label"],
                "file_b_label": row["file_b_label"],
                "delta_presence_minus_mid_retention_db_mean_b_minus_a": row[
                    "delta_presence_minus_mid_retention_db_mean_b_minus_a"
                ],
                "delta_presence_minus_mid_retention_db_p10_b_minus_a": row[
                    "delta_presence_minus_mid_retention_db_p10_b_minus_a"
                ],
                "delta_strong_presence_loss_frame_ratio_b_minus_a": row[
                    "delta_strong_presence_loss_frame_ratio_b_minus_a"
                ],
                "more_transient_lossy_candidate": row["more_transient_lossy_candidate"],
                "transient_loss_score_file_a": row["transient_loss_score_file_a"],
                "transient_loss_score_file_b": row["transient_loss_score_file_b"],
                "transient_loss_evidence_file_a": row["transient_loss_evidence_file_a"],
                "transient_loss_evidence_file_b": row["transient_loss_evidence_file_b"],
                "better_output": row["better_output"],
                "note": row["note"],
            }
            for row in by_abs_ratio[: args.top_k]
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
                "more_transient_lossy_candidate_counts": loss_counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
