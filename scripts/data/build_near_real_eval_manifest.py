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
REFERENCES_DIR = DATA_DIR / "references"
INTERIM_DIR = DATA_DIR / "interim"
MANIFEST_DIR = DATA_DIR / "manifests"

SOURCE_RAW_PATH = DATA_IN / "source_dataset_ly65_raw.wav"
FRIEND_RAW_PATH = DATA_IN / "friend_dataset_fuhuo_raw_concat.wav"
GUODEGANG_RAW_PATH = DATA_IN / "郭德纲 生肉.mp4"
SEGMENT_MANIFEST_PATH = DATA_IN / "source_segments" / "segment_manifest.jsonl"
TARGET_SPEECH_MANIFEST_PATH = MANIFEST_DIR / "target_speech_pool.jsonl"
TARGET_REFERENCE_MANIFEST_PATH = MANIFEST_DIR / "target_reference_pool.jsonl"
MUSIC_MANIFEST_PATH = MANIFEST_DIR / "music_interference_pool.jsonl"

SAMPLE_RATE = 16000
TARGET_PRE_ROLL_SEC = 0.35
TARGET_POST_ROLL_SEC = 0.65
DEFAULT_ABSENT_DURATION_SEC = 3.2
MAX_PEAK = 0.95


@dataclass(frozen=True)
class EvalSpec:
    sample_id: str
    scenario: str
    note: str
    reference_index: int
    target_index: int | None = None
    duration_sec: float | None = None
    friend_start_sec: float | None = None
    guodegang_start_sec: float | None = None
    music_index: int | None = None
    music_start_sec: float | None = None
    target_gain_db: float = 0.0
    friend_gain_db: float = -5.0
    guodegang_gain_db: float = -6.0
    music_gain_db: float = -12.0


DEFAULT_SPECS = [
    EvalSpec(
        sample_id="near_real_0001",
        scenario="target_raw_only",
        note="raw target clip only; used to inspect source retention and over-suppression on target-present speech",
        target_index=0,
        reference_index=0,
    ),
    EvalSpec(
        sample_id="near_real_0002",
        scenario="target_raw_only",
        note="second raw target clip only; another target-present sanity check with different prosody",
        target_index=1,
        reference_index=1,
    ),
    EvalSpec(
        sample_id="near_real_0003",
        scenario="target_plus_friend_speech",
        note="raw target clip mixed with domain-matched friend speech",
        target_index=2,
        reference_index=2,
        friend_start_sec=45.0,
        friend_gain_db=-4.5,
    ),
    EvalSpec(
        sample_id="near_real_0004",
        scenario="target_plus_friend_speech",
        note="raw target clip mixed with another friend speech slice",
        target_index=3,
        reference_index=3,
        friend_start_sec=215.0,
        friend_gain_db=-5.5,
    ),
    EvalSpec(
        sample_id="near_real_0005",
        scenario="target_plus_music",
        note="raw target clip mixed with real music interference",
        target_index=4,
        reference_index=4,
        music_index=0,
        music_start_sec=28.0,
        music_gain_db=-12.5,
    ),
    EvalSpec(
        sample_id="near_real_0006",
        scenario="target_plus_guodegang_speech",
        note="raw target clip mixed with external speech from the Guodegang source",
        target_index=5,
        reference_index=5,
        guodegang_start_sec=120.0,
        guodegang_gain_db=-6.5,
    ),
    EvalSpec(
        sample_id="near_real_0007",
        scenario="target_plus_friend_plus_music",
        note="harder near-real case with raw target, friend speech, and music together",
        target_index=6,
        reference_index=6,
        friend_start_sec=640.0,
        friend_gain_db=-5.0,
        music_index=1,
        music_start_sec=75.0,
        music_gain_db=-13.0,
    ),
    EvalSpec(
        sample_id="near_real_0008",
        scenario="target_absent_friend_only",
        note="target absent; only friend speech is present, used to inspect hallucination and suppression behavior",
        reference_index=7,
        duration_sec=3.2,
        friend_start_sec=820.0,
        friend_gain_db=0.0,
    ),
    EvalSpec(
        sample_id="near_real_0009",
        scenario="target_absent_guodegang_only",
        note="target absent; only external speech is present",
        reference_index=8,
        duration_sec=3.2,
        guodegang_start_sec=480.0,
        guodegang_gain_db=0.0,
    ),
    EvalSpec(
        sample_id="near_real_0010",
        scenario="target_absent_friend_plus_music",
        note="target absent; friend speech and music together",
        reference_index=9,
        duration_sec=3.2,
        friend_start_sec=1020.0,
        friend_gain_db=-1.0,
        music_index=2,
        music_start_sec=44.0,
        music_gain_db=-12.5,
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic near-real evaluation manifest from local raw recordings."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REFERENCES_DIR / "real_eval_near_real_v1",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        default=REFERENCES_DIR / "real_eval_manifest_near_real_v1.jsonl",
    )
    parser.add_argument(
        "--force-clean",
        action="store_true",
        help="Remove any existing sample directories in the output dir before rebuilding.",
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


def clip_duration_from_segment(segment_row: dict[str, Any]) -> tuple[float, float]:
    start_sec = float(segment_row["start_sec"])
    end_sec = float(segment_row["end_sec"])
    clip_start_sec = max(0.0, start_sec - TARGET_PRE_ROLL_SEC)
    clip_duration_sec = (end_sec - start_sec) + TARGET_PRE_ROLL_SEC + TARGET_POST_ROLL_SEC
    return clip_start_sec, clip_duration_sec


def load_segment_rows_by_id() -> dict[str, dict[str, Any]]:
    return {
        row["segment_id"]: row
        for row in load_jsonl(SEGMENT_MANIFEST_PATH)
    }


def choose_target_rows() -> list[dict[str, Any]]:
    return load_jsonl(TARGET_SPEECH_MANIFEST_PATH)


def choose_reference_rows() -> list[dict[str, Any]]:
    return load_jsonl(TARGET_REFERENCE_MANIFEST_PATH)


def choose_music_rows() -> list[dict[str, Any]]:
    return load_jsonl(MUSIC_MANIFEST_PATH)


def ensure_empty_output_dir(path: Path, force_clean: bool) -> None:
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


def main() -> None:
    args = parse_args()
    ensure_empty_output_dir(args.output_dir, force_clean=args.force_clean)
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)

    segment_rows = load_segment_rows_by_id()
    target_rows = choose_target_rows()
    reference_rows = choose_reference_rows()
    music_rows = choose_music_rows()

    if len(target_rows) <= 6 or len(reference_rows) <= 9 or len(music_rows) <= 2:
        raise RuntimeError("Not enough target/reference/music rows to build near-real eval v1.")

    manifest_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for spec in DEFAULT_SPECS:
        sample_dir = args.output_dir / spec.sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)

        reference_row = reference_rows[spec.reference_index]
        reference_input_path = ROOT / reference_row["audio_path"]
        reference_output_path = sample_dir / "reference.wav"
        extract_audio(
            input_path=reference_input_path,
            output_path=reference_output_path,
            start_sec=None,
            duration_sec=min(float(reference_row["duration_sec"]), 8.0),
        )

        component_arrays: list[np.ndarray] = []
        component_meta: list[dict[str, Any]] = []
        target_track = np.zeros(1, dtype=np.float32)
        target_output_path = sample_dir / "target.wav"

        if spec.target_index is not None:
            target_row = target_rows[spec.target_index]
            target_segment_id = target_row["segment_id"]
            segment_row = segment_rows[target_segment_id]
            target_clip_start_sec, target_clip_duration_sec = clip_duration_from_segment(segment_row)
            target_tmp_path = sample_dir / "_target_tmp.wav"
            extract_audio(
                input_path=SOURCE_RAW_PATH,
                output_path=target_tmp_path,
                start_sec=target_clip_start_sec,
                duration_sec=target_clip_duration_sec,
            )
            target_waveform = load_audio(target_tmp_path) * db_to_scale(spec.target_gain_db)
            component_arrays.append(target_waveform)
            component_meta.append(
                {
                    "kind": "target_raw",
                    "source_path": serialize_repo_path(SOURCE_RAW_PATH),
                    "segment_id": target_segment_id,
                    "segment_start_sec": float(segment_row["start_sec"]),
                    "segment_end_sec": float(segment_row["end_sec"]),
                    "clip_start_sec": target_clip_start_sec,
                    "clip_duration_sec": target_clip_duration_sec,
                    "gain_db": spec.target_gain_db,
                }
            )
        else:
            target_clip_duration_sec = spec.duration_sec or DEFAULT_ABSENT_DURATION_SEC

        mixture_duration_sec = float(spec.duration_sec or target_clip_duration_sec)
        mixture_num_samples = int(round(mixture_duration_sec * SAMPLE_RATE))
        target_track = np.zeros(mixture_num_samples, dtype=np.float32)
        if spec.target_index is not None:
            target_track = fit_or_pad(target_waveform, mixture_num_samples)

        if spec.friend_start_sec is not None:
            friend_output_path = sample_dir / "_friend_tmp.wav"
            extract_audio(
                input_path=FRIEND_RAW_PATH,
                output_path=friend_output_path,
                start_sec=spec.friend_start_sec,
                duration_sec=mixture_duration_sec,
            )
            friend_waveform = fit_or_pad(load_audio(friend_output_path), mixture_num_samples)
            friend_waveform = friend_waveform * db_to_scale(spec.friend_gain_db)
            component_arrays.append(friend_waveform)
            component_meta.append(
                {
                    "kind": "friend_raw",
                    "source_path": serialize_repo_path(FRIEND_RAW_PATH),
                    "clip_start_sec": spec.friend_start_sec,
                    "clip_duration_sec": mixture_duration_sec,
                    "gain_db": spec.friend_gain_db,
                }
            )

        if spec.guodegang_start_sec is not None:
            guodegang_output_path = sample_dir / "_guodegang_tmp.wav"
            extract_audio(
                input_path=GUODEGANG_RAW_PATH,
                output_path=guodegang_output_path,
                start_sec=spec.guodegang_start_sec,
                duration_sec=mixture_duration_sec,
            )
            guodegang_waveform = fit_or_pad(load_audio(guodegang_output_path), mixture_num_samples)
            guodegang_waveform = guodegang_waveform * db_to_scale(spec.guodegang_gain_db)
            component_arrays.append(guodegang_waveform)
            component_meta.append(
                {
                    "kind": "guodegang_raw",
                    "source_path": serialize_repo_path(GUODEGANG_RAW_PATH),
                    "clip_start_sec": spec.guodegang_start_sec,
                    "clip_duration_sec": mixture_duration_sec,
                    "gain_db": spec.guodegang_gain_db,
                }
            )

        if spec.music_index is not None:
            music_row = music_rows[spec.music_index]
            music_input_path = ROOT / music_row["audio_path"]
            music_output_path = sample_dir / "_music_tmp.wav"
            extract_audio(
                input_path=music_input_path,
                output_path=music_output_path,
                start_sec=spec.music_start_sec or 0.0,
                duration_sec=mixture_duration_sec,
            )
            music_waveform = fit_or_pad(load_audio(music_output_path), mixture_num_samples)
            music_waveform = music_waveform * db_to_scale(spec.music_gain_db)
            component_arrays.append(music_waveform)
            component_meta.append(
                {
                    "kind": "music",
                    "source_path": serialize_repo_path(music_input_path),
                    "clip_start_sec": spec.music_start_sec or 0.0,
                    "clip_duration_sec": mixture_duration_sec,
                    "gain_db": spec.music_gain_db,
                }
            )

        if not component_arrays:
            raise RuntimeError(f"No mixture components built for {spec.sample_id}")

        mixture = np.zeros(mixture_num_samples, dtype=np.float32)
        for array in component_arrays:
            mixture += fit_or_pad(array, mixture_num_samples)

        peak = float(np.max(np.abs(mixture))) if mixture.size else 0.0
        if peak > MAX_PEAK:
            mixture = mixture * (MAX_PEAK / peak)

        mixture_output_path = sample_dir / "mixture.wav"
        save_audio(mixture_output_path, mixture)
        save_audio(target_output_path, target_track)

        for tmp_name in [
            "_target_tmp.wav",
            "_friend_tmp.wav",
            "_guodegang_tmp.wav",
            "_music_tmp.wav",
        ]:
            tmp_path = sample_dir / tmp_name
            if tmp_path.exists():
                tmp_path.unlink()

        sample_meta = {
            "sample_id": spec.sample_id,
            "scenario": spec.scenario,
            "note": spec.note,
            "mixture_duration_sec": mixture_duration_sec,
            "audio_layout": "mono",
            "reference_source_path": serialize_repo_path(reference_input_path),
            "reference_segment_id": reference_row["segment_id"],
            "target_audio_path": serialize_repo_path(target_output_path),
            "components": component_meta,
        }
        (sample_dir / "sample_meta.json").write_text(
            json.dumps(sample_meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        manifest_rows.append(
            {
                "sample_id": spec.sample_id,
                "mixture_audio_path": serialize_repo_path(mixture_output_path),
                "target_audio_path": serialize_repo_path(target_output_path),
                "reference_audio_path": serialize_repo_path(reference_output_path),
                "note": spec.note,
            }
        )
        summary_rows.append(
            {
                "sample_id": spec.sample_id,
                "scenario": spec.scenario,
                "mixture_audio_path": serialize_repo_path(mixture_output_path),
                "target_audio_path": serialize_repo_path(target_output_path),
                "reference_segment_id": reference_row["segment_id"],
                "components": [component["kind"] for component in component_meta],
                "mixture_duration_sec": round(mixture_duration_sec, 3),
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
        "samples": summary_rows,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
