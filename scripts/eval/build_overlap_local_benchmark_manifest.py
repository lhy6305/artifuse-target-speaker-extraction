from __future__ import annotations

import argparse
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
            "Build an overlap-local benchmark manifest from a near-real manifest by selecting "
            "short overlap-focused windows that are more likely to reflect human-audible failures."
        )
    )
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--window-duration-sec", type=float, default=1.0)
    parser.add_argument("--window-hop-sec", type=float, default=0.02)
    parser.add_argument("--search-pad-sec", type=float, default=0.0)
    return parser.parse_args()


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


def energy(waveform: np.ndarray) -> float:
    return float(np.dot(waveform, waveform))


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
    }


def derive_target_active_interval(original_sample_meta: dict[str, Any]) -> tuple[float | None, float | None]:
    mixture_duration_sec = float(original_sample_meta["mixture_duration_sec"])
    for component in original_sample_meta["components"]:
        if component["kind"] not in TARGET_COMPONENT_KINDS:
            continue
        segment_start_sec = component.get("segment_start_sec")
        segment_end_sec = component.get("segment_end_sec")
        clip_start_sec = component.get("clip_start_sec")
        if segment_start_sec is None or segment_end_sec is None or clip_start_sec is None:
            continue
        active_start_sec = max(0.0, float(segment_start_sec) - float(clip_start_sec))
        active_end_sec = min(mixture_duration_sec, float(segment_end_sec) - float(clip_start_sec))
        if active_end_sec > active_start_sec:
            return active_start_sec, active_end_sec
    return None, None


def window_energy(track: np.ndarray, start_sample: int, length_samples: int) -> float:
    end_sample = min(start_sample + length_samples, track.shape[0])
    if end_sample <= start_sample:
        return 0.0
    return energy(track[start_sample:end_sample])


def select_local_window(
    sample_id: str,
    target_track: np.ndarray,
    speech_track: np.ndarray,
    interference_track: np.ndarray,
    active_start_sec: float | None,
    active_end_sec: float | None,
    sample_rate: int,
    window_duration_sec: float,
    window_hop_sec: float,
    search_pad_sec: float,
) -> dict[str, Any]:
    clip_duration_sec = target_track.shape[0] / float(sample_rate)
    duration_sec = min(window_duration_sec, clip_duration_sec)
    window_samples = max(1, int(round(duration_sec * sample_rate)))
    hop_samples = max(1, int(round(window_hop_sec * sample_rate)))

    has_speech = energy(speech_track) > 1e-12
    scoring_track = speech_track if has_speech else interference_track

    if active_start_sec is not None and active_end_sec is not None:
        search_start_sec = max(0.0, active_start_sec - search_pad_sec)
        search_end_sec = min(clip_duration_sec, active_end_sec + search_pad_sec)
        benchmark_kind = "target_present_overlap_peak"
    else:
        search_start_sec = 0.0
        search_end_sec = clip_duration_sec
        benchmark_kind = "target_absent_speech_peak"

    if search_end_sec - search_start_sec < duration_sec:
        center_sec = 0.5 * (search_start_sec + search_end_sec)
        start_sec = max(0.0, min(clip_duration_sec - duration_sec, center_sec - 0.5 * duration_sec))
        start_sample = int(round(start_sec * sample_rate))
        target_e = window_energy(target_track, start_sample, window_samples)
        speech_e = window_energy(speech_track, start_sample, window_samples)
        interference_e = window_energy(interference_track, start_sample, window_samples)
        score = speech_e if active_start_sec is None else float(np.sqrt(max(target_e, 1e-12) * max(speech_e or interference_e, 1e-12)))
        return {
            "window_start_sec": start_sec,
            "window_duration_sec": duration_sec,
            "benchmark_kind": benchmark_kind,
            "target_window_energy": target_e,
            "speech_window_energy": speech_e,
            "interference_window_energy": interference_e,
            "selection_score": score,
        }

    candidate_start_sample = int(round(search_start_sec * sample_rate))
    max_start_sample = int(round((search_end_sec - duration_sec) * sample_rate))
    best: dict[str, Any] | None = None
    while candidate_start_sample <= max_start_sample:
        target_e = window_energy(target_track, candidate_start_sample, window_samples)
        speech_e = window_energy(speech_track, candidate_start_sample, window_samples)
        interference_e = window_energy(interference_track, candidate_start_sample, window_samples)
        score_base = speech_e if has_speech else interference_e
        if active_start_sec is None:
            score = score_base
        else:
            score = float(np.sqrt(max(target_e, 1e-12) * max(score_base, 1e-12)))
        candidate = {
            "window_start_sec": candidate_start_sample / float(sample_rate),
            "window_duration_sec": duration_sec,
            "benchmark_kind": benchmark_kind,
            "target_window_energy": target_e,
            "speech_window_energy": speech_e,
            "interference_window_energy": interference_e,
            "selection_score": score,
        }
        if best is None or candidate["selection_score"] > best["selection_score"]:
            best = candidate
        candidate_start_sample += hop_samples

    if best is None:
        raise RuntimeError(f"Failed to select a local window for {sample_id}")
    return best


def main() -> None:
    args = parse_args()
    rows = load_jsonl(args.input_manifest)
    output_rows: list[dict[str, Any]] = []

    cache_dir = args.output_manifest.parent / "_component_cache_local_benchmark"
    cache_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        sample_id = str(row["sample_id"])
        mixture_path = ROOT / row["mixture_audio_path"]
        mixture, mixture_sr = load_audio(mixture_path)
        if mixture_sr != args.sample_rate:
            raise ValueError(f"Unexpected sample rate for {mixture_path}: {mixture_sr}")

        original_sample_meta = load_json(mixture_path.parent / "sample_meta.json")
        tracks = reconstruct_category_tracks(
            sample_id=sample_id,
            original_sample_meta=original_sample_meta,
            pack_mixture=mixture,
            cache_dir=cache_dir,
            sample_rate=args.sample_rate,
        )
        active_start_sec, active_end_sec = derive_target_active_interval(original_sample_meta)
        selection = select_local_window(
            sample_id=sample_id,
            target_track=tracks["target_track"],
            speech_track=tracks["speech_track"],
            interference_track=tracks["interference_track"],
            active_start_sec=active_start_sec,
            active_end_sec=active_end_sec,
            sample_rate=args.sample_rate,
            window_duration_sec=args.window_duration_sec,
            window_hop_sec=args.window_hop_sec,
            search_pad_sec=args.search_pad_sec,
        )
        output_rows.append(
            {
                **row,
                "benchmark_kind": selection["benchmark_kind"],
                "window_start_sec": selection["window_start_sec"],
                "window_duration_sec": selection["window_duration_sec"],
                "target_active_start_sec": active_start_sec,
                "target_active_end_sec": active_end_sec,
                "target_window_energy": selection["target_window_energy"],
                "speech_window_energy": selection["speech_window_energy"],
                "interference_window_energy": selection["interference_window_energy"],
                "selection_score": selection["selection_score"],
            }
        )

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output_manifest.open("w", encoding="utf-8", newline="\n") as fh:
        for row in output_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
