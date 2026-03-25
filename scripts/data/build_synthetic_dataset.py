from __future__ import annotations

import argparse
import json
import random
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
MANIFEST_DIR = DATA_DIR / "manifests"
SYNTHETIC_DIR = DATA_DIR / "synthetic"

SAMPLE_RATE = 16000
REFERENCE_MAX_DURATION = 8.0
MIN_TARGET_ACTIVE_SEGMENT = 0.45
MIN_TARGET_SILENCE_GAP = 0.2


@dataclass(frozen=True)
class LayerSpec:
    pool_name: str
    audio_path: Path
    gain_db: float
    start_offset_sec: float
    speaker_id: str | None = None
    reverb: "ReverbSpec | None" = None


@dataclass(frozen=True)
class ReverbSpec:
    in_gain: float
    out_gain: float
    delays_ms: list[int]
    decays: list[float]


@dataclass(frozen=True)
class TargetSegment:
    output_start_sec: float
    source_start_sec: float
    duration_sec: float


@dataclass(frozen=True)
class TargetPattern:
    name: str
    segments: list[TargetSegment]

    @property
    def present_ratio(self) -> float:
        total = sum(segment.duration_sec for segment in self.segments)
        if not self.segments:
            return 0.0
        full_duration = max(
            segment.output_start_sec + segment.duration_sec for segment in self.segments
        )
        if full_duration <= 0:
            return 0.0
        return total / full_duration


RECIPE_PROFILES: dict[str, list[tuple[str, int]]] = {
    "default": [
        ("target_only", 1),
        ("target_clean_speech", 4),
        ("target_hard_speech", 3),
        ("target_music", 2),
        ("target_clean_plus_music", 3),
        ("target_hard_plus_music", 2),
        ("target_singing_vocal", 1),
    ],
    "hard_recipe_focus": [
        ("target_only", 1),
        ("target_clean_speech", 7),
        ("target_hard_speech", 3),
        ("target_music", 2),
        ("target_clean_plus_music", 7),
        ("target_hard_plus_music", 2),
        ("target_singing_vocal", 1),
    ],
    "clean_speech_only": [
        ("target_clean_speech", 1),
    ],
}

TEMPORAL_PATTERN_PROFILES: dict[str, list[tuple[str, int]]] = {
    "default": [
        ("target_full", 5),
        ("target_absent_head", 2),
        ("target_absent_tail", 2),
        ("target_intermittent", 3),
    ],
    "target_full_only": [
        ("target_full", 1),
    ],
}

DEFAULT_POOL_FILE_MAP = {
    "target_speech_pool": MANIFEST_DIR / "target_speech_pool.jsonl",
    "target_reference_pool": MANIFEST_DIR / "target_reference_pool.jsonl",
    "speech_interference_clean_pool": (
        MANIFEST_DIR / "speech_interference_clean_pool.jsonl"
    ),
    "speech_interference_hard_pool": (
        MANIFEST_DIR / "speech_interference_hard_pool.jsonl"
    ),
    "music_interference_pool": MANIFEST_DIR / "music_interference_pool.jsonl",
    "singing_vocal_interference_pool": (
        MANIFEST_DIR / "singing_vocal_interference_pool.jsonl"
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a minimal synthetic TSE dataset from curated manifests."
    )
    parser.add_argument("--train-count", type=int, default=32)
    parser.add_argument("--val-count", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260316)
    parser.add_argument(
        "--train-recipe-profile",
        choices=sorted(RECIPE_PROFILES),
        default="default",
    )
    parser.add_argument(
        "--val-recipe-profile",
        choices=sorted(RECIPE_PROFILES),
        default="default",
    )
    parser.add_argument(
        "--train-temporal-pattern-profile",
        choices=sorted(TEMPORAL_PATTERN_PROFILES),
        default="default",
    )
    parser.add_argument(
        "--val-temporal-pattern-profile",
        choices=sorted(TEMPORAL_PATTERN_PROFILES),
        default="default",
    )
    parser.add_argument(
        "--force-clean",
        action="store_true",
        help="Remove existing sample directories before writing new outputs.",
    )
    parser.add_argument(
        "--target-reverb-prob",
        type=float,
        default=0.0,
        help="Probability of applying light reverb to the rendered target track.",
    )
    parser.add_argument(
        "--speech-reverb-prob",
        type=float,
        default=0.0,
        help="Probability of applying light reverb to each speech-like interference layer.",
    )
    parser.add_argument(
        "--output-tag",
        type=str,
        default="",
        help="Optional tag to write split directories and manifests to isolated names under data/synthetic.",
    )
    parser.add_argument(
        "--pool-manifest-override",
        action="append",
        default=[],
        help=(
            "Override a default manifest path in the form "
            "pool_name=relative/or/absolute/path. Can be passed multiple times."
        ),
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


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def normalize_output_tag(value: str) -> str:
    cleaned = value.strip().replace("\\", "_").replace("/", "_").replace(" ", "_")
    return cleaned


def split_dir(split: str, output_tag: str) -> Path:
    if not output_tag:
        return SYNTHETIC_DIR / split
    return SYNTHETIC_DIR / f"{split}_{output_tag}"


def split_manifest_path(split: str, output_tag: str) -> Path:
    if not output_tag:
        return SYNTHETIC_DIR / f"{split}_manifest.jsonl"
    return SYNTHETIC_DIR / f"{split}_manifest_{output_tag}.jsonl"


def summary_path(output_tag: str) -> Path:
    if not output_tag:
        return SYNTHETIC_DIR / "summary.json"
    return SYNTHETIC_DIR / f"summary_{output_tag}.json"


def ensure_clean_dir(path: Path, force_clean: bool) -> None:
    if force_clean and path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


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


def run_command(cmd: list[str]) -> None:
    subprocess.run(
        cmd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def export_audio(
    input_path: Path,
    output_path: Path,
    duration_sec: float | None = None,
) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(input_path),
    ]
    if duration_sec is not None:
        cmd.extend(["-t", f"{duration_sec:.3f}"])
    cmd.extend(
        [
            "-ac",
            "1",
            "-ar",
            str(SAMPLE_RATE),
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]
    )
    run_command(cmd)


def choose_recipe(recipe_profile: str, rng: random.Random) -> str:
    recipes = RECIPE_PROFILES[recipe_profile]
    names = [name for name, _ in recipes]
    weights = [weight for _, weight in recipes]
    return rng.choices(names, weights=weights, k=1)[0]


def choose_temporal_pattern_name(
    target_duration_sec: float,
    rng: random.Random,
    temporal_pattern_profile: str,
) -> str:
    eligible: list[tuple[str, int]] = []
    for pattern_name, weight in TEMPORAL_PATTERN_PROFILES[temporal_pattern_profile]:
        if pattern_name == "target_full":
            eligible.append((pattern_name, weight))
            continue
        if pattern_name in {"target_absent_head", "target_absent_tail"}:
            if target_duration_sec >= 1.25:
                eligible.append((pattern_name, weight))
            continue
        if pattern_name == "target_intermittent":
            if target_duration_sec >= 1.4:
                eligible.append((pattern_name, weight))
            continue
        raise ValueError(f"Unsupported temporal pattern profile entry: {pattern_name}")
    names = [name for name, _ in eligible]
    weights = [weight for _, weight in eligible]
    return rng.choices(names, weights=weights, k=1)[0]


def choose_row(rng: random.Random, rows: list[dict[str, Any]]) -> dict[str, Any]:
    return rows[rng.randrange(len(rows))]


def choose_gain_db(pool_name: str, rng: random.Random) -> float:
    if pool_name == "speech_interference_clean_pool":
        return rng.uniform(-6.0, 1.0)
    if pool_name == "speech_interference_hard_pool":
        return rng.uniform(-4.0, 2.0)
    if pool_name == "music_interference_pool":
        return rng.uniform(-20.0, -9.0)
    if pool_name == "singing_vocal_interference_pool":
        return rng.uniform(-12.0, -4.0)
    raise ValueError(f"Unexpected pool name: {pool_name}")


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def choose_light_reverb_spec(rng: random.Random) -> ReverbSpec:
    first_delay = int(round(rng.uniform(18.0, 42.0)))
    second_delay = int(round(rng.uniform(55.0, 95.0)))
    third_delay = int(round(rng.uniform(105.0, 180.0)))
    return ReverbSpec(
        in_gain=round(rng.uniform(0.78, 0.88), 3),
        out_gain=round(rng.uniform(0.82, 0.92), 3),
        delays_ms=[first_delay, second_delay, third_delay],
        decays=[
            round(rng.uniform(0.18, 0.28), 3),
            round(rng.uniform(0.10, 0.18), 3),
            round(rng.uniform(0.05, 0.11), 3),
        ],
    )


def format_reverb_filter(spec: ReverbSpec) -> str:
    delays = "|".join(str(value) for value in spec.delays_ms)
    decays = "|".join(f"{value:.3f}" for value in spec.decays)
    return (
        f"aecho={spec.in_gain:.3f}:{spec.out_gain:.3f}:{delays}:{decays}"
    )


def serialize_reverb_spec(spec: ReverbSpec | None) -> dict[str, Any] | None:
    if spec is None:
        return None
    return {
        "type": "light_aecho",
        "in_gain": spec.in_gain,
        "out_gain": spec.out_gain,
        "delays_ms": spec.delays_ms,
        "decays": spec.decays,
    }


def build_target_pattern(
    total_duration_sec: float,
    rng: random.Random,
    temporal_pattern_profile: str,
) -> TargetPattern:
    pattern_name = choose_temporal_pattern_name(
        total_duration_sec,
        rng,
        temporal_pattern_profile=temporal_pattern_profile,
    )

    if pattern_name == "target_full":
        return TargetPattern(
            name="target_full",
            segments=[
                TargetSegment(
                    output_start_sec=0.0,
                    source_start_sec=0.0,
                    duration_sec=total_duration_sec,
                )
            ],
        )

    if pattern_name == "target_absent_head":
        max_head_silence = min(1.2, total_duration_sec * 0.4)
        head_silence = clamp(
            rng.uniform(total_duration_sec * 0.12, max_head_silence),
            MIN_TARGET_SILENCE_GAP,
            total_duration_sec - MIN_TARGET_ACTIVE_SEGMENT,
        )
        active_duration = total_duration_sec - head_silence
        return TargetPattern(
            name=pattern_name,
            segments=[
                TargetSegment(
                    output_start_sec=head_silence,
                    source_start_sec=0.0,
                    duration_sec=active_duration,
                )
            ],
        )

    if pattern_name == "target_absent_tail":
        max_tail_silence = min(1.2, total_duration_sec * 0.4)
        tail_silence = clamp(
            rng.uniform(total_duration_sec * 0.12, max_tail_silence),
            MIN_TARGET_SILENCE_GAP,
            total_duration_sec - MIN_TARGET_ACTIVE_SEGMENT,
        )
        active_duration = total_duration_sec - tail_silence
        return TargetPattern(
            name=pattern_name,
            segments=[
                TargetSegment(
                    output_start_sec=0.0,
                    source_start_sec=0.0,
                    duration_sec=active_duration,
                )
            ],
        )

    if pattern_name == "target_intermittent":
        keep_ratio = clamp(
            rng.uniform(0.55, 0.8),
            (2 * MIN_TARGET_ACTIVE_SEGMENT) / total_duration_sec,
            0.85,
        )
        active_total = total_duration_sec * keep_ratio
        gap_duration = total_duration_sec - active_total
        if (
            active_total < 2 * MIN_TARGET_ACTIVE_SEGMENT
            or gap_duration < MIN_TARGET_SILENCE_GAP
        ):
            return TargetPattern(
                name="target_full",
                segments=[
                    TargetSegment(
                        output_start_sec=0.0,
                        source_start_sec=0.0,
                        duration_sec=total_duration_sec,
                    )
                ],
            )

        first_segment_duration = clamp(
            rng.uniform(active_total * 0.35, active_total * 0.65),
            MIN_TARGET_ACTIVE_SEGMENT,
            active_total - MIN_TARGET_ACTIVE_SEGMENT,
        )
        second_segment_duration = active_total - first_segment_duration
        return TargetPattern(
            name=pattern_name,
            segments=[
                TargetSegment(
                    output_start_sec=0.0,
                    source_start_sec=0.0,
                    duration_sec=first_segment_duration,
                ),
                TargetSegment(
                    output_start_sec=first_segment_duration + gap_duration,
                    source_start_sec=first_segment_duration,
                    duration_sec=second_segment_duration,
                ),
            ],
        )

    raise ValueError(f"Unsupported temporal pattern: {pattern_name}")


def build_layers(
    recipe: str,
    pools: dict[str, list[dict[str, Any]]],
    target_duration_sec: float,
    rng: random.Random,
    speech_reverb_prob: float,
) -> list[LayerSpec]:
    layer_pool_names: list[str]
    if recipe == "target_only":
        layer_pool_names = []
    elif recipe == "target_clean_speech":
        layer_pool_names = ["speech_interference_clean_pool"]
    elif recipe == "target_hard_speech":
        layer_pool_names = ["speech_interference_hard_pool"]
    elif recipe == "target_music":
        layer_pool_names = ["music_interference_pool"]
    elif recipe == "target_clean_plus_music":
        layer_pool_names = [
            "speech_interference_clean_pool",
            "music_interference_pool",
        ]
    elif recipe == "target_hard_plus_music":
        layer_pool_names = [
            "speech_interference_hard_pool",
            "music_interference_pool",
        ]
    elif recipe == "target_singing_vocal":
        layer_pool_names = ["singing_vocal_interference_pool"]
    else:
        raise ValueError(f"Unsupported recipe: {recipe}")

    max_offset_sec = min(2.5, max(0.0, target_duration_sec * 0.35))
    layers: list[LayerSpec] = []
    for pool_name in layer_pool_names:
        row = choose_row(rng, pools[pool_name])
        start_offset_sec = 0.0 if recipe == "target_only" else rng.uniform(0.0, max_offset_sec)
        use_reverb = pool_name in {
            "speech_interference_clean_pool",
            "speech_interference_hard_pool",
            "singing_vocal_interference_pool",
        } and rng.random() < speech_reverb_prob
        layers.append(
            LayerSpec(
                pool_name=pool_name,
                audio_path=ROOT / row["audio_path"],
                gain_db=choose_gain_db(pool_name, rng),
                start_offset_sec=start_offset_sec,
                speaker_id=row.get("speaker_id"),
                reverb=choose_light_reverb_spec(rng) if use_reverb else None,
            )
        )
    return layers


def build_target_filter(
    pattern: TargetPattern,
    total_duration_sec: float,
    input_index: int = 0,
    output_label: str = "targetmix",
    reverb: ReverbSpec | None = None,
) -> list[str]:
    segment_labels: list[str] = []
    filter_parts: list[str] = []
    for segment_index, segment in enumerate(pattern.segments):
        delay_ms = int(round(segment.output_start_sec * 1000.0))
        segment_label = f"tg{segment_index}"
        filter_parts.append(
            (
                f"[{input_index}:a]aresample={SAMPLE_RATE},"
                f"aformat=sample_fmts=fltp:channel_layouts=mono,"
                f"atrim=start={segment.source_start_sec:.3f}:duration={segment.duration_sec:.3f},"
                "asetpts=N/SR/TB,"
                f"adelay={delay_ms}|{delay_ms}[{segment_label}]"
            )
        )
        segment_labels.append(f"[{segment_label}]")

    filter_parts.append(
        (
            "".join(segment_labels)
            + f"amix=inputs={len(segment_labels)}:normalize=0,"
            + f"apad=whole_dur={total_duration_sec:.3f},"
            + f"atrim=0:{total_duration_sec:.3f},"
            + (format_reverb_filter(reverb) + "," if reverb is not None else "")
            + f"asetpts=N/SR/TB[{output_label}]"
        )
    )
    return filter_parts


def render_target_track(
    target_audio_path: Path,
    target_duration_sec: float,
    pattern: TargetPattern,
    output_path: Path,
    reverb: ReverbSpec | None = None,
) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(target_audio_path),
        "-filter_complex",
        ";".join(
            build_target_filter(
                pattern,
                target_duration_sec,
                output_label="targetout",
                reverb=reverb,
            )
        ),
        "-map",
        "[targetout]",
        "-ar",
        str(SAMPLE_RATE),
        "-ac",
        "1",
        "-c:a",
        "pcm_s16le",
        str(output_path),
    ]
    run_command(cmd)


def render_mixture(
    target_audio_path: Path,
    target_duration_sec: float,
    pattern: TargetPattern,
    layers: list[LayerSpec],
    output_path: Path,
    target_reverb: ReverbSpec | None = None,
) -> None:
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-i",
        str(target_audio_path),
    ]
    for layer in layers:
        cmd.extend(["-stream_loop", "-1", "-i", str(layer.audio_path)])

    filter_parts = build_target_filter(
        pattern,
        target_duration_sec,
        output_label="m0",
        reverb=target_reverb,
    )
    mix_labels = ["[m0]"]

    for input_index, layer in enumerate(layers, start=1):
        delay_ms = int(round(layer.start_offset_sec * 1000.0))
        layer_filter = (
            f"[{input_index}:a]aresample={SAMPLE_RATE},"
            f"aformat=sample_fmts=fltp:channel_layouts=mono,"
            f"atrim=0:{target_duration_sec:.3f},"
            "asetpts=N/SR/TB,"
            f"adelay={delay_ms}|{delay_ms},"
            f"volume={layer.gain_db:.2f}dB"
        )
        if layer.reverb is not None:
            layer_filter += "," + format_reverb_filter(layer.reverb)
        filter_parts.append(
            layer_filter + f"[m{input_index}]"
        )
        mix_labels.append(f"[m{input_index}]")

    filter_parts.append(
        (
            "".join(mix_labels)
            + f"amix=inputs={len(mix_labels)}:normalize=0,"
            + f"alimiter=limit=0.95,apad=whole_dur={target_duration_sec:.3f},"
            + f"atrim=0:{target_duration_sec:.3f},"
            + "asetpts=N/SR/TB[out]"
        )
    )
    cmd.extend(
        [
            "-filter_complex",
            ";".join(filter_parts),
            "-map",
            "[out]",
            "-ar",
            str(SAMPLE_RATE),
            "-ac",
            "1",
            "-c:a",
            "pcm_s16le",
            str(output_path),
        ]
    )
    run_command(cmd)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_sample(
    split: str,
    sample_index: int,
    split_dir_path: Path,
    pools: dict[str, list[dict[str, Any]]],
    recipe_profile: str,
    temporal_pattern_profile: str,
    rng: random.Random,
    target_reverb_prob: float,
    speech_reverb_prob: float,
) -> dict[str, Any]:
    sample_id = f"{split}_{sample_index:06d}"
    sample_dir = split_dir_path / sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)

    target_row = choose_row(rng, pools["target_speech_pool"])
    reference_row = choose_row(rng, pools["target_reference_pool"])
    target_source_path = ROOT / target_row["audio_path"]
    reference_source_path = ROOT / reference_row["audio_path"]
    target_duration_sec = float(target_row["duration_sec"])
    reference_duration_sec = min(
        float(reference_row["duration_sec"]),
        REFERENCE_MAX_DURATION,
    )

    recipe = choose_recipe(recipe_profile, rng)
    target_pattern = build_target_pattern(
        target_duration_sec,
        rng,
        temporal_pattern_profile=temporal_pattern_profile,
    )
    layers = build_layers(
        recipe,
        pools,
        target_duration_sec,
        rng,
        speech_reverb_prob=speech_reverb_prob,
    )
    target_reverb = (
        choose_light_reverb_spec(rng)
        if rng.random() < target_reverb_prob
        else None
    )

    target_out_path = sample_dir / "target.wav"
    reference_out_path = sample_dir / "reference.wav"
    mixture_out_path = sample_dir / "mixture.wav"
    metadata_out_path = sample_dir / "metadata.json"

    render_target_track(
        target_source_path,
        target_duration_sec,
        target_pattern,
        target_out_path,
        reverb=target_reverb,
    )
    export_audio(
        reference_source_path,
        reference_out_path,
        duration_sec=reference_duration_sec,
    )
    render_mixture(
        target_source_path,
        target_duration_sec,
        target_pattern,
        layers,
        mixture_out_path,
        target_reverb=target_reverb,
    )

    target_present_duration_sec = sum(
        segment.duration_sec for segment in target_pattern.segments
    )
    absent_intervals: list[dict[str, float]] = []
    cursor = 0.0
    for segment in target_pattern.segments:
        if segment.output_start_sec > cursor:
            absent_intervals.append(
                {
                    "start_sec": round(cursor, 3),
                    "end_sec": round(segment.output_start_sec, 3),
                    "duration_sec": round(segment.output_start_sec - cursor, 3),
                }
            )
        cursor = segment.output_start_sec + segment.duration_sec
    if cursor < target_duration_sec:
        absent_intervals.append(
            {
                "start_sec": round(cursor, 3),
                "end_sec": round(target_duration_sec, 3),
                "duration_sec": round(target_duration_sec - cursor, 3),
            }
        )

    metadata = {
        "sample_id": sample_id,
        "split": split,
        "recipe_profile": recipe_profile,
        "temporal_pattern_profile": temporal_pattern_profile,
        "recipe": recipe,
        "target_present_ratio": round(
            target_present_duration_sec / target_duration_sec,
            6,
        ),
        "temporal_pattern": target_pattern.name,
        "target_duration_sec": round(target_duration_sec, 6),
        "target_present_duration_sec": round(target_present_duration_sec, 6),
        "reference_duration_sec": round(reference_duration_sec, 6),
        "target_source": {
            "segment_id": target_row.get("segment_id"),
            "audio_path": target_row["audio_path"],
            "pool": "target_speech_pool",
        },
        "reference_source": {
            "segment_id": reference_row.get("segment_id"),
            "audio_path": reference_row["audio_path"],
            "pool": "target_reference_pool",
        },
        "target_reverb": serialize_reverb_spec(target_reverb),
        "interference_layers": [
            {
                "pool": layer.pool_name,
                "audio_path": relpath(layer.audio_path),
                "speaker_id": layer.speaker_id,
                "gain_db": round(layer.gain_db, 3),
                "start_offset_sec": round(layer.start_offset_sec, 3),
                "reverb": serialize_reverb_spec(layer.reverb),
            }
            for layer in layers
        ],
        "target_segments": [
            {
                "output_start_sec": round(segment.output_start_sec, 3),
                "source_start_sec": round(segment.source_start_sec, 3),
                "duration_sec": round(segment.duration_sec, 3),
            }
            for segment in target_pattern.segments
        ],
        "target_absent_intervals": absent_intervals,
        "output_paths": {
            "mixture_audio_path": relpath(mixture_out_path),
            "target_audio_path": relpath(target_out_path),
            "reference_audio_path": relpath(reference_out_path),
            "metadata_path": relpath(metadata_out_path),
        },
    }
    write_json(metadata_out_path, metadata)

    return {
        "sample_id": sample_id,
        "split": split,
        "recipe_profile": recipe_profile,
        "temporal_pattern_profile": temporal_pattern_profile,
        "recipe": recipe,
        "temporal_pattern": target_pattern.name,
        "target_present_ratio": round(
            target_present_duration_sec / target_duration_sec,
            6,
        ),
        "mixture_audio_path": relpath(mixture_out_path),
        "target_audio_path": relpath(target_out_path),
        "reference_audio_path": relpath(reference_out_path),
        "metadata_path": relpath(metadata_out_path),
    }


def parse_pool_manifest_overrides(values: list[str]) -> dict[str, Path]:
    overrides: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --pool-manifest-override value: {value!r}")
        pool_name, raw_path = value.split("=", 1)
        pool_name = pool_name.strip()
        raw_path = raw_path.strip()
        if pool_name not in DEFAULT_POOL_FILE_MAP:
            raise ValueError(f"Unknown pool name in override: {pool_name!r}")
        if not raw_path:
            raise ValueError(f"Empty override path for pool: {pool_name!r}")
        path = Path(raw_path)
        if not path.is_absolute():
            path = ROOT / path
        overrides[pool_name] = path
    return overrides


def build_pool_file_map(overrides: dict[str, Path]) -> dict[str, Path]:
    pool_file_map = dict(DEFAULT_POOL_FILE_MAP)
    pool_file_map.update(overrides)
    return pool_file_map


def load_pools(pool_file_map: dict[str, Path]) -> dict[str, list[dict[str, Any]]]:
    pools = {name: load_jsonl(path) for name, path in pool_file_map.items()}
    for pool_name, rows in pools.items():
        if not rows:
            raise RuntimeError(f"Manifest is empty: {pool_name}")
    return pools


def build_split(
    split: str,
    sample_count: int,
    pools: dict[str, list[dict[str, Any]]],
    recipe_profile: str,
    temporal_pattern_profile: str,
    rng: random.Random,
    force_clean: bool,
    target_reverb_prob: float,
    speech_reverb_prob: float,
    output_tag: str,
) -> list[dict[str, Any]]:
    split_dir_path = split_dir(split, output_tag)
    ensure_clean_dir(split_dir_path, force_clean=force_clean)
    rows: list[dict[str, Any]] = []
    for sample_index in range(1, sample_count + 1):
        rows.append(
            build_sample(
                split,
                sample_index,
                split_dir_path,
                pools,
                recipe_profile,
                temporal_pattern_profile,
                rng,
                target_reverb_prob=target_reverb_prob,
                speech_reverb_prob=speech_reverb_prob,
            )
        )
    write_jsonl(split_manifest_path(split, output_tag), rows)
    return rows


def build_summary(
    train_rows: list[dict[str, Any]],
    val_rows: list[dict[str, Any]],
    train_recipe_profile: str,
    val_recipe_profile: str,
    train_temporal_pattern_profile: str,
    val_temporal_pattern_profile: str,
    target_reverb_prob: float,
    speech_reverb_prob: float,
    output_tag: str,
    pool_file_map: dict[str, Path],
) -> None:
    summary = {
        "train_count": len(train_rows),
        "val_count": len(val_rows),
        "train_recipe_profile": train_recipe_profile,
        "val_recipe_profile": val_recipe_profile,
        "train_temporal_pattern_profile": train_temporal_pattern_profile,
        "val_temporal_pattern_profile": val_temporal_pattern_profile,
        "target_reverb_prob": target_reverb_prob,
        "speech_reverb_prob": speech_reverb_prob,
        "output_tag": output_tag,
        "train_manifest": relpath(split_manifest_path("train", output_tag)),
        "val_manifest": relpath(split_manifest_path("val", output_tag)),
        "pool_manifests": {
            name: serialize_repo_path(path)
            for name, path in sorted(pool_file_map.items())
        },
    }
    write_json(summary_path(output_tag), summary)


def main() -> None:
    args = parse_args()
    output_tag = normalize_output_tag(args.output_tag)
    pool_manifest_overrides = parse_pool_manifest_overrides(
        args.pool_manifest_override
    )
    pool_file_map = build_pool_file_map(pool_manifest_overrides)
    pools = load_pools(pool_file_map)

    rng = random.Random(args.seed)
    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

    train_rows = build_split(
        split="train",
        sample_count=args.train_count,
        pools=pools,
        recipe_profile=args.train_recipe_profile,
        temporal_pattern_profile=args.train_temporal_pattern_profile,
        rng=rng,
        force_clean=args.force_clean,
        target_reverb_prob=args.target_reverb_prob,
        speech_reverb_prob=args.speech_reverb_prob,
        output_tag=output_tag,
    )
    val_rows = build_split(
        split="val",
        sample_count=args.val_count,
        pools=pools,
        recipe_profile=args.val_recipe_profile,
        temporal_pattern_profile=args.val_temporal_pattern_profile,
        rng=rng,
        force_clean=args.force_clean,
        target_reverb_prob=args.target_reverb_prob,
        speech_reverb_prob=args.speech_reverb_prob,
        output_tag=output_tag,
    )
    build_summary(
        train_rows,
        val_rows,
        train_recipe_profile=args.train_recipe_profile,
        val_recipe_profile=args.val_recipe_profile,
        train_temporal_pattern_profile=args.train_temporal_pattern_profile,
        val_temporal_pattern_profile=args.val_temporal_pattern_profile,
        target_reverb_prob=args.target_reverb_prob,
        speech_reverb_prob=args.speech_reverb_prob,
        output_tag=output_tag,
        pool_file_map=pool_file_map,
    )

    print(
        json.dumps(
            {
                "train_count": len(train_rows),
                "val_count": len(val_rows),
                "train_recipe_profile": args.train_recipe_profile,
                "val_recipe_profile": args.val_recipe_profile,
                "train_temporal_pattern_profile": (
                    args.train_temporal_pattern_profile
                ),
                "val_temporal_pattern_profile": (
                    args.val_temporal_pattern_profile
                ),
                "target_reverb_prob": args.target_reverb_prob,
                "speech_reverb_prob": args.speech_reverb_prob,
                "output_tag": output_tag,
                "pool_manifest_overrides": {
                    name: serialize_repo_path(path)
                    for name, path in sorted(pool_manifest_overrides.items())
                },
                "summary_path": relpath(summary_path(output_tag)),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
