from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]

SPEECH_RECIPES = {"target_clean_speech", "target_hard_speech"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Analyze synthetic speech-only proxy groups from an existing checkpoint-compare output "
            "to approximate current near-real speech bucket failure modes."
        )
    )
    parser.add_argument("--compare-jsonl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--n-fft", type=int, default=1024)
    parser.add_argument("--hop-length", type=int, default=256)
    parser.add_argument("--top-transient-ratio", type=float, default=0.12)
    parser.add_argument("--transient-min-count", type=int, default=8)
    parser.add_argument("--presence-low-hz", type=float, default=3000.0)
    parser.add_argument("--presence-high-hz", type=float, default=8000.0)
    parser.add_argument("--mid-low-hz", type=float, default=800.0)
    parser.add_argument("--mid-high-hz", type=float, default=3000.0)
    parser.add_argument("--top-k", type=int, default=12)
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


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


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
    return np.abs(np.stack(frames, axis=0)).astype(np.float32) ** 2


def band_energy(power: np.ndarray, freqs: np.ndarray, low: float, high: float) -> np.ndarray:
    mask = (freqs >= low) & (freqs < high)
    return power[:, mask].sum(axis=1)


def safe_log_ratio(numer: np.ndarray, denom: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    return 10.0 * np.log10((numer + eps) / (denom + eps))


def detect_transient_indices(
    power: np.ndarray,
    freqs: np.ndarray,
    low_hz: float,
    high_hz: float,
    top_ratio: float,
    min_count: int,
) -> np.ndarray:
    mask = (freqs >= low_hz) & (freqs < high_hz)
    log_power = np.log1p(power[:, mask])
    flux = np.maximum(log_power[1:] - log_power[:-1], 0.0).sum(axis=1)
    if flux.size == 0:
        return np.array([0], dtype=np.int64)
    keep = max(min_count, int(np.ceil(flux.shape[0] * top_ratio)))
    keep = min(max(keep, 1), flux.shape[0])
    return np.sort(np.argsort(flux)[-keep:] + 1).astype(np.int64)


def build_target_transient_metrics(
    target_audio_path: Path,
    *,
    n_fft: int,
    hop_length: int,
    top_transient_ratio: float,
    transient_min_count: int,
    presence_low_hz: float,
    presence_high_hz: float,
    mid_low_hz: float,
    mid_high_hz: float,
) -> dict[str, float]:
    target_waveform, sample_rate = load_audio(target_audio_path)
    power = stft_power(target_waveform, n_fft=n_fft, hop_length=hop_length)
    freqs = np.fft.rfftfreq(n_fft, d=1.0 / sample_rate).astype(np.float32)
    transient_indices = detect_transient_indices(
        power=power,
        freqs=freqs,
        low_hz=presence_low_hz,
        high_hz=min(presence_high_hz, sample_rate / 2.0),
        top_ratio=top_transient_ratio,
        min_count=transient_min_count,
    )
    transient_indices = transient_indices[transient_indices < power.shape[0]]
    if transient_indices.size == 0:
        transient_indices = np.array([0], dtype=np.int64)

    mid_energy = band_energy(power, freqs, mid_low_hz, mid_high_hz)[transient_indices]
    presence_energy = band_energy(
        power, freqs, presence_low_hz, min(presence_high_hz, sample_rate / 2.0)
    )[transient_indices]
    presence_minus_mid_db = safe_log_ratio(presence_energy, mid_energy)
    total_energy = power.sum(axis=1)[transient_indices] + 1e-12
    presence_share = presence_energy / total_energy

    return {
        "target_transient_presence_minus_mid_db_mean": float(np.mean(presence_minus_mid_db)),
        "target_transient_presence_minus_mid_db_p90": float(np.percentile(presence_minus_mid_db, 90)),
        "target_transient_presence_share_mean": float(np.mean(presence_share)),
        "target_transient_presence_share_p90": float(np.percentile(presence_share, 90)),
        "target_transient_frame_count": float(transient_indices.size),
    }


def summarize_group(rows: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(rows)
    if count == 0:
        return {
            "count": 0,
            "avg_sisdr_delta_db": 0.0,
            "avg_waveform_l1_delta": 0.0,
            "avg_overlap_ratio": 0.0,
            "avg_interference_gain_db": 0.0,
            "avg_target_transient_presence_minus_mid_db_mean": 0.0,
            "avg_target_transient_presence_share_mean": 0.0,
            "improved_count": 0,
            "regressed_count": 0,
            "near_tie_count": 0,
        }
    improved_count = sum(1 for row in rows if row["sisdr_delta_db"] > 0.1)
    regressed_count = sum(1 for row in rows if row["sisdr_delta_db"] < -0.1)
    return {
        "count": count,
        "avg_sisdr_delta_db": float(sum(row["sisdr_delta_db"] for row in rows) / count),
        "avg_waveform_l1_delta": float(sum(row["waveform_l1_delta"] for row in rows) / count),
        "avg_overlap_ratio": float(sum(row["speech_overlap_ratio"] for row in rows) / count),
        "avg_interference_gain_db": float(sum(row["speech_interference_gain_db"] for row in rows) / count),
        "avg_target_transient_presence_minus_mid_db_mean": float(
            sum(row["target_transient_presence_minus_mid_db_mean"] for row in rows) / count
        ),
        "avg_target_transient_presence_share_mean": float(
            sum(row["target_transient_presence_share_mean"] for row in rows) / count
        ),
        "improved_count": improved_count,
        "regressed_count": regressed_count,
        "near_tie_count": count - improved_count - regressed_count,
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    compare_rows = load_jsonl(args.compare_jsonl)
    speech_rows = [row for row in compare_rows if str(row["recipe"]) in SPEECH_RECIPES]

    enriched_rows: list[dict[str, Any]] = []
    transient_cache: dict[str, dict[str, float]] = {}
    for row in speech_rows:
        metadata_path = ROOT / str(row["metadata_path"])
        metadata = load_json(metadata_path)
        target_audio_path = ROOT / str(metadata["output_paths"]["target_audio_path"])
        transient_metrics = transient_cache.get(str(target_audio_path))
        if transient_metrics is None:
            transient_metrics = build_target_transient_metrics(
                target_audio_path,
                n_fft=args.n_fft,
                hop_length=args.hop_length,
                top_transient_ratio=args.top_transient_ratio,
                transient_min_count=args.transient_min_count,
                presence_low_hz=args.presence_low_hz,
                presence_high_hz=args.presence_high_hz,
                mid_low_hz=args.mid_low_hz,
                mid_high_hz=args.mid_high_hz,
            )
            transient_cache[str(target_audio_path)] = transient_metrics

        speech_layer = metadata["interference_layers"][0]
        target_duration_sec = float(metadata["target_duration_sec"])
        speech_start_offset_sec = float(speech_layer["start_offset_sec"])
        speech_overlap_ratio = max(0.0, target_duration_sec - speech_start_offset_sec) / max(target_duration_sec, 1e-9)
        enriched_rows.append(
            {
                **row,
                "speech_pool": str(speech_layer["pool"]),
                "speech_interference_gain_db": float(speech_layer["gain_db"]),
                "speech_start_offset_sec": speech_start_offset_sec,
                "speech_overlap_ratio": float(min(max(speech_overlap_ratio, 0.0), 1.0)),
                **transient_metrics,
            }
        )

    if not enriched_rows:
        raise RuntimeError("No speech-only rows found in compare jsonl.")

    gains = np.asarray([row["speech_interference_gain_db"] for row in enriched_rows], dtype=np.float32)
    transient_scores = np.asarray(
        [row["target_transient_presence_minus_mid_db_mean"] for row in enriched_rows],
        dtype=np.float32,
    )
    loud_gain_threshold = float(np.quantile(gains, 2.0 / 3.0))
    transient_rich_threshold = float(np.quantile(transient_scores, 2.0 / 3.0))

    proxy_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enriched_rows:
        is_target_full = str(row["temporal_pattern"]) == "target_full"
        is_clean = str(row["recipe"]) == "target_clean_speech"
        is_hard = str(row["recipe"]) == "target_hard_speech"
        is_full_overlap_like = is_target_full and row["speech_overlap_ratio"] >= 0.9
        is_loud_speech = row["speech_interference_gain_db"] >= loud_gain_threshold
        is_transient_rich = row["target_transient_presence_minus_mid_db_mean"] >= transient_rich_threshold

        proxy_groups["speech_only_all"].append(row)
        if is_target_full:
            proxy_groups["speech_target_full"].append(row)
        else:
            proxy_groups["speech_not_full"].append(row)
        if is_full_overlap_like:
            proxy_groups["speech_full_overlap_like"].append(row)
        if is_full_overlap_like and is_clean:
            proxy_groups["speech_full_overlap_like__clean"].append(row)
        if is_full_overlap_like and is_hard:
            proxy_groups["speech_full_overlap_like__hard"].append(row)
        if is_full_overlap_like and is_loud_speech:
            proxy_groups["speech_leak_risk_proxy"].append(row)
        if is_full_overlap_like and is_transient_rich:
            proxy_groups["speech_transient_proxy"].append(row)
        if is_full_overlap_like and is_transient_rich and is_clean:
            proxy_groups["speech_transient_proxy__clean"].append(row)
        if is_full_overlap_like and is_transient_rich and is_hard:
            proxy_groups["speech_transient_proxy__hard"].append(row)
        if is_full_overlap_like and is_loud_speech and is_transient_rich:
            proxy_groups["speech_compound_proxy"].append(row)

    summary = {
        "compare_jsonl": serialize_repo_path(args.compare_jsonl),
        "num_speech_rows": len(enriched_rows),
        "thresholds": {
            "loud_gain_threshold_db": loud_gain_threshold,
            "transient_rich_threshold_db": transient_rich_threshold,
            "full_overlap_ratio_min": 0.9,
        },
        "proxy_groups": {
            group_name: summarize_group(rows)
            for group_name, rows in sorted(proxy_groups.items())
        },
        "top_regressions_in_compound_proxy": sorted(
            proxy_groups.get("speech_compound_proxy", []),
            key=lambda row: row["sisdr_delta_db"],
        )[: args.top_k],
        "top_regressions_in_transient_proxy": sorted(
            proxy_groups.get("speech_transient_proxy", []),
            key=lambda row: row["sisdr_delta_db"],
        )[: args.top_k],
        "top_regressions_in_leak_risk_proxy": sorted(
            proxy_groups.get("speech_leak_risk_proxy", []),
            key=lambda row: row["sisdr_delta_db"],
        )[: args.top_k],
    }

    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (args.output_dir / "per_sample_proxy_rows.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in enriched_rows),
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "compare_jsonl": serialize_repo_path(args.compare_jsonl),
                "num_speech_rows": len(enriched_rows),
                "thresholds": summary["thresholds"],
                "output_dir": serialize_repo_path(args.output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
