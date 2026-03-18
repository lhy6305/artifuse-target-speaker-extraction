from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]
DATA_IN = ROOT / "data_in"
DATA_DIR = ROOT / "data"
MANIFEST_DIR = DATA_DIR / "manifests"
PROBE_DIR = DATA_DIR / "probes"

SOURCE_RAW_PATH = DATA_IN / "source_dataset_ly65_raw.wav"
FRIEND_RAW_PATH = DATA_IN / "friend_dataset_fuhuo_raw_concat.wav"
GUODEGANG_RAW_PATH = DATA_IN / "郭德纲 生肉.mp4"
SEGMENT_MANIFEST_PATH = DATA_IN / "source_segments" / "segment_manifest.jsonl"
TARGET_SPEECH_MANIFEST_PATH = MANIFEST_DIR / "target_speech_pool.jsonl"
TARGET_REFERENCE_MANIFEST_PATH = MANIFEST_DIR / "target_reference_pool.jsonl"

SAMPLE_RATE = 16000
TARGET_PRE_ROLL_SEC = 0.35
TARGET_POST_ROLL_SEC = 0.65
MAX_PEAK = 0.95


@dataclass(frozen=True)
class ProbeAnchor:
    near_real_anchor_sample_id: str
    target_index: int
    reference_index: int
    speech_family: str
    anchor_hypothesis: str
    note: str
    gain_db_values: tuple[float, ...]


@dataclass(frozen=True)
class SpeechSlice:
    clip_tag: str
    speech_family: str
    start_sec: float
    source_path: Path


ANCHORS: tuple[ProbeAnchor, ...] = (
    ProbeAnchor(
        near_real_anchor_sample_id="near_real_0003",
        target_index=2,
        reference_index=2,
        speech_family="friend_raw",
        anchor_hypothesis="residual_transient_like",
        note="0003-like target+friend speech anchor; intended to probe residual-heavy and transient-loss trade-offs.",
        gain_db_values=(-6.0, -4.5, -3.0),
    ),
    ProbeAnchor(
        near_real_anchor_sample_id="near_real_0004",
        target_index=3,
        reference_index=3,
        speech_family="friend_raw",
        anchor_hypothesis="speech_leak_like",
        note="0004-like target+friend speech anchor; intended to probe speech-leak trade-offs.",
        gain_db_values=(-7.0, -5.5, -4.0),
    ),
    ProbeAnchor(
        near_real_anchor_sample_id="near_real_0006",
        target_index=5,
        reference_index=5,
        speech_family="guodegang_raw",
        anchor_hypothesis="transient_like",
        note="0006-like target+guodegang speech anchor; intended to probe transient-loss regressions.",
        gain_db_values=(-8.0, -6.5, -5.0),
    ),
)

SPEECH_SLICES: tuple[SpeechSlice, ...] = (
    SpeechSlice(
        clip_tag="friend_anchor_45s",
        speech_family="friend_raw",
        start_sec=45.0,
        source_path=FRIEND_RAW_PATH,
    ),
    SpeechSlice(
        clip_tag="friend_anchor_215s",
        speech_family="friend_raw",
        start_sec=215.0,
        source_path=FRIEND_RAW_PATH,
    ),
    SpeechSlice(
        clip_tag="friend_absent_820s",
        speech_family="friend_raw",
        start_sec=820.0,
        source_path=FRIEND_RAW_PATH,
    ),
    SpeechSlice(
        clip_tag="guodegang_anchor_120s",
        speech_family="guodegang_raw",
        start_sec=120.0,
        source_path=GUODEGANG_RAW_PATH,
    ),
    SpeechSlice(
        clip_tag="guodegang_absent_480s",
        speech_family="guodegang_raw",
        start_sec=480.0,
        source_path=GUODEGANG_RAW_PATH,
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build a synthetic-compatible near-real speech probe manifest anchored on the "
            "three target_present__speech failure cases from near-real v1."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=PROBE_DIR / "near_real_speech_probe_v1",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        default=PROBE_DIR / "near_real_speech_probe_v1_manifest.jsonl",
    )
    parser.add_argument(
        "--force-clean",
        action="store_true",
        help="Remove existing sample directories in the output dir before rebuilding.",
    )
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


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
    *,
    start_sec: float | None,
    duration_sec: float,
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
            str(SAMPLE_RATE),
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]
    )
    run_command(command)


def load_audio(path: Path) -> np.ndarray:
    waveform, sample_rate = sf.read(str(path), dtype="float32", always_2d=False)
    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    if sample_rate != SAMPLE_RATE:
        raise ValueError(f"Unexpected sample rate for {path}: {sample_rate}")
    return waveform.astype(np.float32, copy=False)


def save_audio(path: Path, waveform: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), waveform, SAMPLE_RATE, subtype="PCM_16")


def db_to_scale(gain_db: float) -> float:
    return float(10.0 ** (gain_db / 20.0))


def fit_or_pad(waveform: np.ndarray, num_samples: int) -> np.ndarray:
    if waveform.shape[0] >= num_samples:
        return waveform[:num_samples]
    padded = np.zeros(num_samples, dtype=np.float32)
    padded[: waveform.shape[0]] = waveform
    return padded


def ensure_empty_output_dir(path: Path, *, force_clean: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    if not force_clean:
        return
    for child in path.iterdir():
        if child.is_dir():
            for nested in child.rglob("*"):
                if nested.is_file():
                    nested.unlink()
            for nested in sorted(child.rglob("*"), reverse=True):
                if nested.is_dir():
                    nested.rmdir()
            child.rmdir()
        elif child.is_file():
            child.unlink()


def clip_duration_from_segment(segment_row: dict[str, Any]) -> tuple[float, float]:
    start_sec = float(segment_row["start_sec"])
    end_sec = float(segment_row["end_sec"])
    clip_start_sec = max(0.0, start_sec - TARGET_PRE_ROLL_SEC)
    clip_duration_sec = (end_sec - start_sec) + TARGET_PRE_ROLL_SEC + TARGET_POST_ROLL_SEC
    return clip_start_sec, clip_duration_sec


def load_segment_rows_by_id() -> dict[str, dict[str, Any]]:
    return {row["segment_id"]: row for row in load_jsonl(SEGMENT_MANIFEST_PATH)}


def find_speech_slices(speech_family: str) -> list[SpeechSlice]:
    return [speech_slice for speech_slice in SPEECH_SLICES if speech_slice.speech_family == speech_family]


def main() -> None:
    args = parse_args()
    ensure_empty_output_dir(args.output_dir, force_clean=args.force_clean)
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)

    segment_rows = load_segment_rows_by_id()
    target_rows = load_jsonl(TARGET_SPEECH_MANIFEST_PATH)
    reference_rows = load_jsonl(TARGET_REFERENCE_MANIFEST_PATH)

    manifest_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    sample_index = 0

    for anchor in ANCHORS:
        target_row = target_rows[anchor.target_index]
        reference_row = reference_rows[anchor.reference_index]
        target_segment_id = str(target_row["segment_id"])
        segment_row = segment_rows[target_segment_id]
        target_clip_start_sec, target_clip_duration_sec = clip_duration_from_segment(segment_row)
        speech_slices = find_speech_slices(anchor.speech_family)

        for speech_slice in speech_slices:
            for gain_db in anchor.gain_db_values:
                sample_index += 1
                sample_id = f"probe_{sample_index:04d}"
                sample_dir = args.output_dir / sample_id
                sample_dir.mkdir(parents=True, exist_ok=True)

                target_output_path = sample_dir / "target.wav"
                reference_output_path = sample_dir / "reference.wav"
                speech_output_path = sample_dir / "_speech_tmp.wav"
                mixture_output_path = sample_dir / "mixture.wav"
                metadata_output_path = sample_dir / "metadata.json"

                extract_audio(
                    input_path=SOURCE_RAW_PATH,
                    output_path=target_output_path,
                    start_sec=target_clip_start_sec,
                    duration_sec=target_clip_duration_sec,
                )
                extract_audio(
                    input_path=ROOT / str(reference_row["audio_path"]),
                    output_path=reference_output_path,
                    start_sec=None,
                    duration_sec=min(float(reference_row["duration_sec"]), 8.0),
                )
                extract_audio(
                    input_path=speech_slice.source_path,
                    output_path=speech_output_path,
                    start_sec=speech_slice.start_sec,
                    duration_sec=target_clip_duration_sec,
                )

                target_waveform = load_audio(target_output_path)
                mixture_num_samples = int(round(target_clip_duration_sec * SAMPLE_RATE))
                target_waveform = fit_or_pad(target_waveform, mixture_num_samples)
                speech_waveform = fit_or_pad(load_audio(speech_output_path), mixture_num_samples)
                speech_waveform = speech_waveform * db_to_scale(gain_db)

                mixture = target_waveform + speech_waveform
                peak = float(np.max(np.abs(mixture))) if mixture.size else 0.0
                if peak > MAX_PEAK:
                    mixture = mixture * (MAX_PEAK / peak)
                save_audio(mixture_output_path, mixture)
                speech_output_path.unlink(missing_ok=True)

                recipe = (
                    "near_real_friend_speech_probe"
                    if anchor.speech_family == "friend_raw"
                    else "near_real_guodegang_speech_probe"
                )
                note = (
                    f"{anchor.note} Speech slice {speech_slice.clip_tag} at {speech_slice.start_sec:.1f}s "
                    f"with gain {gain_db:.1f} dB."
                )
                metadata = {
                    "sample_id": sample_id,
                    "probe_version": "near_real_speech_probe_v1",
                    "recipe_profile": "near_real_speech_probe_v1",
                    "recipe": recipe,
                    "temporal_pattern": "target_full",
                    "target_present_ratio": 1.0,
                    "target_duration_sec": round(target_clip_duration_sec, 6),
                    "target_present_duration_sec": round(target_clip_duration_sec, 6),
                    "reference_duration_sec": round(min(float(reference_row["duration_sec"]), 8.0), 6),
                    "near_real_anchor_sample_id": anchor.near_real_anchor_sample_id,
                    "anchor_hypothesis": anchor.anchor_hypothesis,
                    "speech_family": anchor.speech_family,
                    "speech_clip_tag": speech_slice.clip_tag,
                    "speech_clip_start_sec": speech_slice.start_sec,
                    "speech_interference_gain_db": gain_db,
                    "target_source": {
                        "segment_id": target_segment_id,
                        "audio_path": str(target_row["audio_path"]),
                        "pool": "target_speech_pool",
                        "clip_start_sec": round(target_clip_start_sec, 6),
                        "clip_duration_sec": round(target_clip_duration_sec, 6),
                    },
                    "reference_source": {
                        "segment_id": str(reference_row["segment_id"]),
                        "audio_path": str(reference_row["audio_path"]),
                        "pool": "target_reference_pool",
                    },
                    "interference_layers": [
                        {
                            "pool": anchor.speech_family,
                            "audio_path": serialize_repo_path(speech_slice.source_path),
                            "gain_db": round(gain_db, 3),
                            "start_offset_sec": 0.0,
                            "clip_start_sec": round(speech_slice.start_sec, 3),
                            "clip_tag": speech_slice.clip_tag,
                        }
                    ],
                    "target_segments": [
                        {
                            "output_start_sec": 0.0,
                            "source_start_sec": round(target_clip_start_sec, 3),
                            "duration_sec": round(target_clip_duration_sec, 3),
                        }
                    ],
                    "target_absent_intervals": [],
                    "output_paths": {
                        "mixture_audio_path": serialize_repo_path(mixture_output_path),
                        "target_audio_path": serialize_repo_path(target_output_path),
                        "reference_audio_path": serialize_repo_path(reference_output_path),
                        "metadata_path": serialize_repo_path(metadata_output_path),
                    },
                }
                metadata_output_path.write_text(
                    json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                    newline="\n",
                )

                manifest_rows.append(
                    {
                        "sample_id": sample_id,
                        "split": "probe",
                        "recipe_profile": "near_real_speech_probe_v1",
                        "recipe": recipe,
                        "temporal_pattern": "target_full",
                        "target_present_ratio": 1.0,
                        "mixture_audio_path": serialize_repo_path(mixture_output_path),
                        "target_audio_path": serialize_repo_path(target_output_path),
                        "reference_audio_path": serialize_repo_path(reference_output_path),
                        "metadata_path": serialize_repo_path(metadata_output_path),
                    }
                )
                summary_rows.append(
                    {
                        "sample_id": sample_id,
                        "near_real_anchor_sample_id": anchor.near_real_anchor_sample_id,
                        "anchor_hypothesis": anchor.anchor_hypothesis,
                        "speech_family": anchor.speech_family,
                        "speech_clip_tag": speech_slice.clip_tag,
                        "speech_interference_gain_db": gain_db,
                        "target_segment_id": target_segment_id,
                    }
                )

    with args.output_manifest.open("w", encoding="utf-8", newline="\n") as fh:
        for row in manifest_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "output_manifest": serialize_repo_path(args.output_manifest),
        "output_dir": serialize_repo_path(args.output_dir),
        "sample_rate": SAMPLE_RATE,
        "num_samples": len(manifest_rows),
        "num_anchors": len(ANCHORS),
        "samples": summary_rows,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
