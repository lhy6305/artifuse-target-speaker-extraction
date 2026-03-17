from __future__ import annotations

import json
import math
import re
import subprocess
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, TypeVar


ROOT = Path(__file__).resolve().parents[2]
DATA_IN = ROOT / "data_in"
DATA_DIR = ROOT / "data"
MANIFEST_DIR = DATA_DIR / "manifests"
INTERIM_DIR = DATA_DIR / "interim"

SOURCE_SEGMENTS_DIR = DATA_IN / "source_segments" / "segments"
SOURCE_SEGMENT_MANIFEST = DATA_IN / "source_segments" / "segment_manifest.jsonl"
GENSHIN_DIR = DATA_IN / "genshin_voice_extract"
PURE_MUSIC_DIR = DATA_IN / "pure_music_dataset"
SINGING_VOCAL_DIR = DATA_IN / "voice_music_dataset" / "uvr_voice_only"
FRIEND_RAW_PATH = DATA_IN / "friend_dataset_fuhuo_raw_concat.wav"
FRIEND_SEGMENT_DIR = INTERIM_DIR / "friend_hard_negative_segments"

TARGET_MIN_DURATION = 1.0
REFERENCE_MIN_DURATION = 1.5
REFERENCE_TARGET_COUNT = 64

CLEAN_MIN_DURATION = 1.0
CLEAN_MAX_DURATION = 12.0
CLEAN_MIN_TEXT_LENGTH = 2
CLEAN_MAX_TEXT_LENGTH = 80
CLEAN_SPEAKER_LIMIT = 32
CLEAN_ITEMS_PER_SPEAKER = 24

SINGING_ITEM_LIMIT = 96

FRIEND_MIN_DURATION = 1.2
FRIEND_MAX_DURATION = 10.0
FRIEND_MAX_SEGMENTS = 140
FRIEND_SILENCE_NOISE = "-35dB"
FRIEND_SILENCE_MIN = "0.35"
CURATED_GENSHIN_SOURCE_PREFIX = "data/curated/"

T = TypeVar("T")


@dataclass(frozen=True)
class Segment:
    start_sec: float
    end_sec: float

    @property
    def duration_sec(self) -> float:
        return max(0.0, self.end_sec - self.start_sec)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def write_jsonl(path: Path, rows: Iterable[dict]) -> int:
    ensure_parent(path)
    count = 0
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def select_evenly_spaced(items: list[T], limit: int) -> list[T]:
    if limit <= 0 or not items:
        return []
    if len(items) <= limit:
        return list(items)

    stride = len(items) / limit
    selected: list[T] = []
    for idx in range(limit):
        selected_idx = min(len(items) - 1, math.floor(idx * stride))
        selected.append(items[selected_idx])
    return selected


def wav_duration_sec(path: Path) -> float:
    with wave.open(str(path), "rb") as fh:
        frames = fh.getnframes()
        rate = fh.getframerate()
        return frames / float(rate)


def ffprobe_duration_sec(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return float(result.stdout.strip())


def build_target_and_reference_pools() -> dict[str, int]:
    all_rows: list[dict] = []
    with SOURCE_SEGMENT_MANIFEST.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            segment_id = obj["segment_id"]
            audio_path = SOURCE_SEGMENTS_DIR / f"{segment_id}.wav"
            if not audio_path.exists():
                continue
            duration = float(obj["duration_sec"])
            if duration < TARGET_MIN_DURATION:
                continue
            all_rows.append(
                {
                    "segment_id": segment_id,
                    "audio_path": relpath(audio_path),
                    "duration_sec": round(duration, 6),
                    "noise_gated_ratio": float(obj.get("noise_gated_ratio", 0.0)),
                    "source": "data_in/source_segments/segments",
                    "selection_reason": "duration_ge_1s",
                }
            )

    all_rows.sort(key=lambda row: row["segment_id"])

    reference_candidates = [
        row for row in all_rows if row["duration_sec"] >= REFERENCE_MIN_DURATION
    ]
    reference_rows = select_evenly_spaced(
        reference_candidates,
        REFERENCE_TARGET_COUNT,
    )
    reference_ids = {row["segment_id"] for row in reference_rows}
    target_rows = [row for row in all_rows if row["segment_id"] not in reference_ids]

    for idx, row in enumerate(reference_rows, start=1):
        row["reference_rank"] = idx
        row["pool"] = "target_reference_pool"
    for row in target_rows:
        row["pool"] = "target_speech_pool"

    target_count = write_jsonl(MANIFEST_DIR / "target_speech_pool.jsonl", target_rows)
    reference_count = write_jsonl(
        MANIFEST_DIR / "target_reference_pool.jsonl", reference_rows
    )
    return {
        "target_speech_pool": target_count,
        "target_reference_pool": reference_count,
    }


def iter_genshin_speaker_dirs() -> list[Path]:
    return sorted(path for path in GENSHIN_DIR.iterdir() if path.is_dir())


def load_existing_curated_clean_pool() -> dict[str, int] | None:
    manifest_path = MANIFEST_DIR / "speech_interference_clean_pool.jsonl"
    if not manifest_path.exists():
        return None

    rows = load_jsonl(manifest_path)
    if not rows:
        return None
    if not all(
        str(row.get("source", "")).startswith(CURATED_GENSHIN_SOURCE_PREFIX)
        for row in rows
    ):
        return None

    speaker_ids = {row["speaker_id"] for row in rows}
    return {
        "speech_interference_clean_pool": len(rows),
        "clean_speaker_count": len(speaker_ids),
    }


def build_clean_interference_pool() -> dict[str, int]:
    existing_curated = load_existing_curated_clean_pool()
    if existing_curated is not None:
        return existing_curated

    speaker_entries: list[dict] = []
    for speaker_dir in iter_genshin_speaker_dirs():
        wav_files = sorted(speaker_dir.rglob("*.wav"))
        if not wav_files:
            continue
        usable_items: list[dict] = []
        for wav_path in wav_files:
            lab_path = wav_path.with_suffix(".lab")
            if not lab_path.exists():
                continue
            text = lab_path.read_text(encoding="utf-8").strip()
            if not (CLEAN_MIN_TEXT_LENGTH <= len(text) <= CLEAN_MAX_TEXT_LENGTH):
                continue
            try:
                duration_sec = wav_duration_sec(wav_path)
            except (wave.Error, EOFError):
                continue
            if not (CLEAN_MIN_DURATION <= duration_sec <= CLEAN_MAX_DURATION):
                continue
            usable_items.append(
                {
                    "speaker_id": speaker_dir.name,
                    "audio_path": relpath(wav_path),
                    "text_path": relpath(lab_path),
                    "text": text,
                    "duration_sec": round(duration_sec, 6),
                    "source": "data_in/genshin_voice_extract",
                }
            )
            if len(usable_items) >= CLEAN_ITEMS_PER_SPEAKER:
                break

        if len(usable_items) == CLEAN_ITEMS_PER_SPEAKER:
            speaker_entries.append(
                {
                    "speaker_id": speaker_dir.name,
                    "count": len(usable_items),
                    "items": usable_items,
                }
            )

    speaker_entries.sort(key=lambda row: row["speaker_id"])
    selected = speaker_entries[:CLEAN_SPEAKER_LIMIT]

    rows: list[dict] = []
    for speaker_rank, speaker in enumerate(selected, start=1):
        for item_rank, item in enumerate(speaker["items"], start=1):
            rows.append(
                {
                    **item,
                    "pool": "speech_interference_clean_pool",
                    "speaker_rank": speaker_rank,
                    "item_rank_within_speaker": item_rank,
                    "selection_reason": "matching_lab_and_duration_filtered",
                }
            )

    count = write_jsonl(MANIFEST_DIR / "speech_interference_clean_pool.jsonl", rows)
    return {
        "speech_interference_clean_pool": count,
        "clean_speaker_count": len(selected),
    }


def build_singing_vocal_pool() -> dict[str, int]:
    rows: list[dict] = []
    wav_files = sorted(SINGING_VOCAL_DIR.rglob("*.wav"))
    for wav_path in wav_files[:SINGING_ITEM_LIMIT]:
        duration_sec = wav_duration_sec(wav_path)
        rows.append(
            {
                "pool": "singing_vocal_interference_pool",
                "audio_path": relpath(wav_path),
                "duration_sec": round(duration_sec, 6),
                "source": "data_in/voice_music_dataset/uvr_voice_only",
                "selection_reason": "curated_subset_for_mvp",
            }
        )
    count = write_jsonl(MANIFEST_DIR / "singing_vocal_interference_pool.jsonl", rows)
    return {"singing_vocal_interference_pool": count}


def build_music_pool() -> dict[str, int]:
    rows: list[dict] = []
    for audio_path in sorted(PURE_MUSIC_DIR.rglob("*")):
        if not audio_path.is_file():
            continue
        if audio_path.suffix.lower() not in {".wav", ".mp3", ".m4a"}:
            continue
        duration_sec = ffprobe_duration_sec(audio_path)
        rows.append(
            {
                "pool": "music_interference_pool",
                "audio_path": relpath(audio_path),
                "duration_sec": round(duration_sec, 6),
                "source": "data_in/pure_music_dataset",
                "selection_reason": "all_available_pure_music_files",
            }
        )
    count = write_jsonl(MANIFEST_DIR / "music_interference_pool.jsonl", rows)
    return {"music_interference_pool": count}


def parse_silence_segments(stderr_text: str, total_duration_sec: float) -> list[Segment]:
    starts: list[float] = []
    intervals: list[tuple[float, float]] = []

    for line in stderr_text.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
        if start_match:
            starts.append(float(start_match.group(1)))
            continue

        end_match = re.search(r"silence_end:\s*([0-9.]+)", line)
        if end_match and starts:
            start_sec = starts.pop(0)
            intervals.append((start_sec, float(end_match.group(1))))

    speech_segments: list[Segment] = []
    cursor = 0.0
    for silence_start, silence_end in intervals:
        if silence_start > cursor:
            speech_segments.append(Segment(cursor, silence_start))
        cursor = max(cursor, silence_end)
    if cursor < total_duration_sec:
        speech_segments.append(Segment(cursor, total_duration_sec))
    return speech_segments


def select_friend_segments(segments: list[Segment]) -> list[Segment]:
    filtered = [
        seg
        for seg in segments
        if FRIEND_MIN_DURATION <= seg.duration_sec <= FRIEND_MAX_DURATION
    ]
    if len(filtered) <= FRIEND_MAX_SEGMENTS:
        return filtered

    stride = len(filtered) / FRIEND_MAX_SEGMENTS
    selected: list[Segment] = []
    for idx in range(FRIEND_MAX_SEGMENTS):
        selected_idx = min(len(filtered) - 1, math.floor(idx * stride))
        selected.append(filtered[selected_idx])
    return selected


def export_friend_segments(segments: list[Segment]) -> list[dict]:
    FRIEND_SEGMENT_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for idx, segment in enumerate(segments, start=1):
        out_path = FRIEND_SEGMENT_DIR / f"friend_hard_{idx:04d}.wav"
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-ss",
                f"{segment.start_sec:.3f}",
                "-to",
                f"{segment.end_sec:.3f}",
                "-i",
                str(FRIEND_RAW_PATH),
                "-ac",
                "1",
                "-ar",
                "16000",
                str(out_path),
            ],
            check=True,
            capture_output=True,
        )
        rows.append(
            {
                "pool": "speech_interference_hard_pool",
                "audio_path": relpath(out_path),
                "source_audio_path": relpath(FRIEND_RAW_PATH),
                "start_sec": round(segment.start_sec, 3),
                "end_sec": round(segment.end_sec, 3),
                "duration_sec": round(segment.duration_sec, 3),
                "source": "data_in/friend_dataset_fuhuo_raw_concat.wav",
                "selection_reason": "silence_based_segmentation_for_hard_negative",
            }
        )
    return rows


def build_friend_hard_pool() -> dict[str, int]:
    total_duration_sec = ffprobe_duration_sec(FRIEND_RAW_PATH)
    result = subprocess.run(
        [
            "ffmpeg",
            "-hide_banner",
            "-i",
            str(FRIEND_RAW_PATH),
            "-af",
            f"silencedetect=n={FRIEND_SILENCE_NOISE}:d={FRIEND_SILENCE_MIN}",
            "-f",
            "null",
            "NUL",
        ],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    raw_segments = parse_silence_segments(result.stderr, total_duration_sec)
    selected_segments = select_friend_segments(raw_segments)
    rows = export_friend_segments(selected_segments)
    count = write_jsonl(MANIFEST_DIR / "speech_interference_hard_pool.jsonl", rows)
    return {"speech_interference_hard_pool": count}


def build_summary(stats: dict[str, int]) -> None:
    summary_path = MANIFEST_DIR / "curated_pool_summary.json"
    ensure_parent(summary_path)
    summary_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    stats: dict[str, int] = {}
    stats.update(build_target_and_reference_pools())
    stats.update(build_clean_interference_pool())
    stats.update(build_friend_hard_pool())
    stats.update(build_music_pool())
    stats.update(build_singing_vocal_pool())
    build_summary(stats)

    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
