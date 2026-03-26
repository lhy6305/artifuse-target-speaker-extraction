from __future__ import annotations

import argparse
import json
import math
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic metadata-focused manifest from an existing synthetic manifest."
    )
    parser.add_argument(
        "--input-manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "train_manifest.jsonl",
    )
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument(
        "--sample-ids-file",
        type=Path,
        default=None,
        help="Optional newline-delimited sample_id allowlist applied before metadata filters.",
    )
    parser.add_argument(
        "--include-derived-metrics",
        action="store_true",
        help="Compute and persist derived transient/similarity metrics even when they are not used as filters.",
    )
    parser.add_argument("--recipes", nargs="*", default=[])
    parser.add_argument("--temporal-patterns", nargs="*", default=[])
    parser.add_argument("--min-target-ratio", type=float, default=None)
    parser.add_argument("--max-target-ratio", type=float, default=None)
    parser.add_argument("--min-target-energy-ratio", type=float, default=None)
    parser.add_argument("--max-target-energy-ratio", type=float, default=None)
    parser.add_argument("--min-overlap-ratio", type=float, default=None)
    parser.add_argument("--max-overlap-ratio", type=float, default=None)
    parser.add_argument("--min-interference-gain-db", type=float, default=None)
    parser.add_argument("--max-interference-gain-db", type=float, default=None)
    parser.add_argument("--interference-pools", nargs="*", default=[])
    parser.add_argument("--interference-speaker-names", nargs="*", default=[])
    parser.add_argument(
        "--require-interference-reverb",
        action="store_true",
        help="Keep only rows whose first interference layer has a serialized reverb spec.",
    )
    parser.add_argument(
        "--forbid-interference-reverb",
        action="store_true",
        help="Keep only rows whose first interference layer has no serialized reverb spec.",
    )
    parser.add_argument(
        "--require-target-reverb",
        action="store_true",
        help="Keep only rows whose rendered target track has a serialized reverb spec.",
    )
    parser.add_argument(
        "--forbid-target-reverb",
        action="store_true",
        help="Keep only rows whose rendered target track has no serialized reverb spec.",
    )
    parser.add_argument(
        "--min-target-transient-presence-minus-mid-db-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--max-target-transient-presence-minus-mid-db-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--min-target-transient-presence-share-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--max-target-transient-presence-share-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--min-interference-transient-presence-minus-mid-db-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--max-interference-transient-presence-minus-mid-db-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--min-interference-transient-presence-share-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--max-interference-transient-presence-share-mean",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--min-target-interference-logspec-cosine",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--max-target-interference-logspec-cosine",
        type=float,
        default=None,
    )
    parser.add_argument(
        "--transient-filter-mode",
        choices=["all", "any"],
        default="all",
        help="How to combine multiple transient metric filters when more than one is provided.",
    )
    parser.add_argument(
        "--recipe-cap",
        action="append",
        default=[],
        help="Per-recipe cap in the form recipe=count. Can be passed multiple times.",
    )
    parser.add_argument("--seed", type=int, default=20260318)
    return parser.parse_args()


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


def load_sample_ids(path: Path | None) -> set[str]:
    if path is None:
        return set()
    sample_ids: set[str] = set()
    with path.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            value = line.strip()
            if not value:
                continue
            sample_ids.add(value)
    return sample_ids


def parse_recipe_caps(values: list[str]) -> dict[str, int]:
    caps: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --recipe-cap value: {value!r}")
        recipe, raw_count = value.split("=", 1)
        recipe = recipe.strip()
        count = int(raw_count)
        if not recipe:
            raise ValueError(f"Invalid empty recipe in --recipe-cap value: {value!r}")
        if count < 0:
            raise ValueError(f"Recipe cap must be non-negative: {value!r}")
        caps[recipe] = count
    return caps


def compute_overlap_ratio(metadata: dict[str, Any]) -> float | None:
    layers = list(metadata.get("interference_layers", []))
    if not layers:
        return None
    duration = float(metadata["target_duration_sec"])
    start_offset = min(float(layer.get("start_offset_sec", 0.0)) for layer in layers)
    overlap = max(0.0, duration - start_offset) / max(duration, 1e-9)
    return float(min(max(overlap, 0.0), 1.0))


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
    *,
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
    keep = max(min_count, int(math.ceil(flux.shape[0] * top_ratio)))
    keep = min(max(keep, 1), flux.shape[0])
    return np.sort(np.argsort(flux)[-keep:] + 1).astype(np.int64)


def build_target_transient_metrics(target_audio_path: Path) -> dict[str, float]:
    waveform, sample_rate = load_audio(target_audio_path)
    power = stft_power(waveform, n_fft=1024, hop_length=256)
    freqs = np.fft.rfftfreq(1024, d=1.0 / sample_rate).astype(np.float32)
    transient_indices = detect_transient_indices(
        power=power,
        freqs=freqs,
        low_hz=3000.0,
        high_hz=min(8000.0, sample_rate / 2.0),
        top_ratio=0.12,
        min_count=8,
    )
    transient_indices = transient_indices[transient_indices < power.shape[0]]
    if transient_indices.size == 0:
        transient_indices = np.array([0], dtype=np.int64)

    mid_energy = band_energy(power, freqs, 800.0, 3000.0)[transient_indices]
    presence_energy = band_energy(power, freqs, 3000.0, min(8000.0, sample_rate / 2.0))[transient_indices]
    presence_minus_mid_db = safe_log_ratio(presence_energy, mid_energy)
    total_energy = power.sum(axis=1)[transient_indices] + 1e-12
    presence_share = presence_energy / total_energy
    return {
        "target_transient_presence_minus_mid_db_mean": float(np.mean(presence_minus_mid_db)),
        "target_transient_presence_share_mean": float(np.mean(presence_share)),
    }


def build_interference_transient_metrics(interference_audio_path: Path) -> dict[str, float]:
    waveform, sample_rate = load_audio(interference_audio_path)
    power = stft_power(waveform, n_fft=1024, hop_length=256)
    freqs = np.fft.rfftfreq(1024, d=1.0 / sample_rate).astype(np.float32)
    transient_indices = detect_transient_indices(
        power=power,
        freqs=freqs,
        low_hz=3000.0,
        high_hz=min(8000.0, sample_rate / 2.0),
        top_ratio=0.12,
        min_count=8,
    )
    transient_indices = transient_indices[transient_indices < power.shape[0]]
    if transient_indices.size == 0:
        transient_indices = np.array([0], dtype=np.int64)

    mid_energy = band_energy(power, freqs, 800.0, 3000.0)[transient_indices]
    presence_energy = band_energy(power, freqs, 3000.0, min(8000.0, sample_rate / 2.0))[transient_indices]
    presence_minus_mid_db = safe_log_ratio(presence_energy, mid_energy)
    total_energy = power.sum(axis=1)[transient_indices] + 1e-12
    presence_share = presence_energy / total_energy
    return {
        "interference_transient_presence_minus_mid_db_mean": float(np.mean(presence_minus_mid_db)),
        "interference_transient_presence_share_mean": float(np.mean(presence_share)),
    }


def build_target_interference_pair_metrics(
    target_audio_path: Path,
    interference_audio_path: Path,
) -> dict[str, float]:
    target_waveform, target_sample_rate = load_audio(target_audio_path)
    interference_waveform, interference_sample_rate = load_audio(interference_audio_path)
    target_power = stft_power(target_waveform, n_fft=1024, hop_length=256)
    interference_power = stft_power(interference_waveform, n_fft=1024, hop_length=256)
    target_logspec = np.log1p(target_power.mean(axis=0))
    interference_logspec = np.log1p(interference_power.mean(axis=0))
    if target_sample_rate != interference_sample_rate:
        min_length = min(target_logspec.shape[0], interference_logspec.shape[0])
        target_logspec = target_logspec[:min_length]
        interference_logspec = interference_logspec[:min_length]
    cosine = float(
        np.dot(target_logspec, interference_logspec)
        / ((np.linalg.norm(target_logspec) * np.linalg.norm(interference_logspec)) + 1e-12)
    )
    return {
        "target_interference_logspec_cosine": cosine,
    }


def build_target_audibility_metrics(
    mixture_audio_path: Path,
    target_audio_path: Path,
) -> dict[str, float]:
    mixture_waveform, _ = load_audio(mixture_audio_path)
    target_waveform, _ = load_audio(target_audio_path)
    common_length = min(mixture_waveform.shape[0], target_waveform.shape[0])
    if common_length <= 0:
        return {
            "target_energy_ratio": 0.0,
            "interference_energy_ratio": 0.0,
            "target_to_interference_energy_ratio": 0.0,
            "target_to_interference_energy_db": -120.0,
        }
    mixture_waveform = mixture_waveform[:common_length]
    target_waveform = target_waveform[:common_length]
    interference_waveform = mixture_waveform - target_waveform

    target_energy = float(np.dot(target_waveform, target_waveform))
    mixture_energy = max(float(np.dot(mixture_waveform, mixture_waveform)), 1e-12)
    interference_energy = max(float(np.dot(interference_waveform, interference_waveform)), 1e-12)
    target_to_interference_ratio = target_energy / interference_energy
    target_to_interference_db = float(10.0 * np.log10(target_to_interference_ratio + 1e-12))
    return {
        "target_energy_ratio": float(target_energy / mixture_energy),
        "interference_energy_ratio": float(interference_energy / mixture_energy),
        "target_to_interference_energy_ratio": float(target_to_interference_ratio),
        "target_to_interference_energy_db": target_to_interference_db,
    }


def passes_optional_bounds(
    *,
    value: float,
    min_value: float | None,
    max_value: float | None,
) -> bool:
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def infer_interference_speaker_name(audio_path: str | None) -> str | None:
    if not audio_path:
        return None
    path = Path(audio_path)
    parent_name = path.parent.name.strip()
    return parent_name or None


def summarize(rows: list[dict[str, Any]], enriched: list[dict[str, Any]]) -> dict[str, Any]:
    recipe_counts = Counter(row["recipe"] for row in rows)
    pattern_counts = Counter(row.get("temporal_pattern", "target_full") for row in rows)
    pool_counts = Counter(row["interference_pool"] for row in enriched if row["interference_pool"] is not None)
    speaker_counts = Counter(
        row["interference_speaker_name"] for row in enriched if row["interference_speaker_name"] is not None
    )
    if enriched:
        mean_overlap = float(sum(row["overlap_ratio"] for row in enriched if row["overlap_ratio"] is not None) / len(enriched))
    else:
        mean_overlap = 0.0
    return {
        "recipe_counts": dict(sorted(recipe_counts.items())),
        "pattern_counts": dict(sorted(pattern_counts.items())),
        "interference_pool_counts": dict(sorted(pool_counts.items())),
        "interference_speaker_counts": dict(sorted(speaker_counts.items())),
        "mean_overlap_ratio": mean_overlap,
    }


def main() -> None:
    args = parse_args()
    if args.require_interference_reverb and args.forbid_interference_reverb:
        raise ValueError(
            "Cannot require and forbid interference reverb at the same time."
        )
    if args.require_target_reverb and args.forbid_target_reverb:
        raise ValueError(
            "Cannot require and forbid target reverb at the same time."
        )
    rng = random.Random(args.seed)
    recipe_caps = parse_recipe_caps(args.recipe_cap)
    allowed_sample_ids = load_sample_ids(args.sample_ids_file)
    recipes = set(args.recipes)
    temporal_patterns = set(args.temporal_patterns)
    interference_pools = set(args.interference_pools)
    interference_speaker_names = set(args.interference_speaker_names)
    use_transient_filters = any(
        value is not None
        for value in [
            args.min_target_transient_presence_minus_mid_db_mean,
            args.max_target_transient_presence_minus_mid_db_mean,
            args.min_target_transient_presence_share_mean,
            args.max_target_transient_presence_share_mean,
            args.min_target_energy_ratio,
            args.max_target_energy_ratio,
            args.min_interference_transient_presence_minus_mid_db_mean,
            args.max_interference_transient_presence_minus_mid_db_mean,
            args.min_interference_transient_presence_share_mean,
            args.max_interference_transient_presence_share_mean,
            args.min_target_interference_logspec_cosine,
            args.max_target_interference_logspec_cosine,
        ]
    )
    use_derived_metrics = bool(args.include_derived_metrics) or use_transient_filters

    rows = load_jsonl(args.input_manifest)
    enriched_candidates: list[dict[str, Any]] = []
    target_transient_cache: dict[str, dict[str, float]] = {}
    interference_transient_cache: dict[str, dict[str, float]] = {}
    pair_metric_cache: dict[tuple[str, str], dict[str, float]] = {}
    audibility_metric_cache: dict[tuple[str, str], dict[str, float]] = {}
    for row in rows:
        if allowed_sample_ids and str(row["sample_id"]) not in allowed_sample_ids:
            continue
        if recipes and str(row["recipe"]) not in recipes:
            continue
        if temporal_patterns and str(row.get("temporal_pattern", "target_full")) not in temporal_patterns:
            continue
        target_ratio = float(row.get("target_present_ratio", 1.0))
        if args.min_target_ratio is not None and target_ratio < args.min_target_ratio:
            continue
        if args.max_target_ratio is not None and target_ratio > args.max_target_ratio:
            continue

        metadata = load_json(ROOT / str(row["metadata_path"]))
        overlap_ratio = compute_overlap_ratio(metadata)
        if args.min_overlap_ratio is not None and (overlap_ratio is None or overlap_ratio < args.min_overlap_ratio):
            continue
        if args.max_overlap_ratio is not None and (overlap_ratio is None or overlap_ratio > args.max_overlap_ratio):
            continue

        layers = list(metadata.get("interference_layers", []))
        first_layer = layers[0] if layers else None
        interference_gain_db = None if first_layer is None else float(first_layer["gain_db"])
        interference_pool = None if first_layer is None else str(first_layer["pool"])
        interference_has_reverb = bool(
            first_layer is not None and first_layer.get("reverb") is not None
        )
        target_has_reverb = bool(metadata.get("target_reverb") is not None)
        interference_speaker_name = (
            None
            if first_layer is None
            else str(first_layer.get("speaker_id") or "").strip()
            or infer_interference_speaker_name(str(first_layer.get("audio_path", "")))
        )
        if args.min_interference_gain_db is not None and (
            interference_gain_db is None or interference_gain_db < args.min_interference_gain_db
        ):
            continue
        if args.max_interference_gain_db is not None and (
            interference_gain_db is None or interference_gain_db > args.max_interference_gain_db
        ):
            continue
        if interference_pools and interference_pool not in interference_pools:
            continue
        if interference_speaker_names and interference_speaker_name not in interference_speaker_names:
            continue
        if args.require_interference_reverb and not interference_has_reverb:
            continue
        if args.forbid_interference_reverb and interference_has_reverb:
            continue
        if args.require_target_reverb and not target_has_reverb:
            continue
        if args.forbid_target_reverb and target_has_reverb:
            continue

        transient_metrics: dict[str, float] = {}
        if use_derived_metrics:
            target_audio_path = ROOT / str(metadata["output_paths"]["target_audio_path"])
            target_key = str(target_audio_path)
            mixture_audio_path = ROOT / str(metadata["output_paths"]["mixture_audio_path"])
            mixture_key = str(mixture_audio_path)
            target_transient_metrics = target_transient_cache.get(target_key, {})
            if not target_transient_metrics:
                target_transient_metrics = build_target_transient_metrics(target_audio_path)
                target_transient_cache[target_key] = target_transient_metrics

            interference_transient_metrics: dict[str, float] = {}
            pair_metrics: dict[str, float] = {}
            audibility_metrics = audibility_metric_cache.get((mixture_key, target_key), {})
            if not audibility_metrics:
                audibility_metrics = build_target_audibility_metrics(
                    mixture_audio_path=mixture_audio_path,
                    target_audio_path=target_audio_path,
                )
                audibility_metric_cache[(mixture_key, target_key)] = audibility_metrics
            if first_layer is not None and first_layer.get("audio_path"):
                interference_audio_path = ROOT / str(first_layer["audio_path"])
                interference_key = str(interference_audio_path)
                interference_transient_metrics = interference_transient_cache.get(interference_key, {})
                if not interference_transient_metrics:
                    interference_transient_metrics = build_interference_transient_metrics(interference_audio_path)
                    interference_transient_cache[interference_key] = interference_transient_metrics
                pair_key = (target_key, interference_key)
                pair_metrics = pair_metric_cache.get(pair_key, {})
                if not pair_metrics:
                    pair_metrics = build_target_interference_pair_metrics(target_audio_path, interference_audio_path)
                    pair_metric_cache[pair_key] = pair_metrics

            transient_metrics = {
                **target_transient_metrics,
                **audibility_metrics,
                **interference_transient_metrics,
                **pair_metrics,
            }

            if use_transient_filters:
                transient_checks = [
                    passes_optional_bounds(
                        value=transient_metrics["target_transient_presence_minus_mid_db_mean"],
                        min_value=args.min_target_transient_presence_minus_mid_db_mean,
                        max_value=args.max_target_transient_presence_minus_mid_db_mean,
                    ),
                    passes_optional_bounds(
                        value=transient_metrics["target_transient_presence_share_mean"],
                        min_value=args.min_target_transient_presence_share_mean,
                        max_value=args.max_target_transient_presence_share_mean,
                    ),
                    passes_optional_bounds(
                        value=transient_metrics["target_energy_ratio"],
                        min_value=args.min_target_energy_ratio,
                        max_value=args.max_target_energy_ratio,
                    ),
                    passes_optional_bounds(
                        value=transient_metrics.get("interference_transient_presence_minus_mid_db_mean", float("nan")),
                        min_value=args.min_interference_transient_presence_minus_mid_db_mean,
                        max_value=args.max_interference_transient_presence_minus_mid_db_mean,
                    ),
                    passes_optional_bounds(
                        value=transient_metrics.get("interference_transient_presence_share_mean", float("nan")),
                        min_value=args.min_interference_transient_presence_share_mean,
                        max_value=args.max_interference_transient_presence_share_mean,
                    ),
                    passes_optional_bounds(
                        value=transient_metrics.get("target_interference_logspec_cosine", float("nan")),
                        min_value=args.min_target_interference_logspec_cosine,
                        max_value=args.max_target_interference_logspec_cosine,
                    ),
                ]
                active_checks = [
                    transient_checks[0]
                    for _ in [0]
                    if args.min_target_transient_presence_minus_mid_db_mean is not None
                    or args.max_target_transient_presence_minus_mid_db_mean is not None
                ] + [
                    transient_checks[1]
                    for _ in [0]
                    if args.min_target_transient_presence_share_mean is not None
                    or args.max_target_transient_presence_share_mean is not None
                ] + [
                    transient_checks[2]
                    for _ in [0]
                    if args.min_target_energy_ratio is not None
                    or args.max_target_energy_ratio is not None
                ] + [
                    transient_checks[3]
                    for _ in [0]
                    if args.min_interference_transient_presence_minus_mid_db_mean is not None
                    or args.max_interference_transient_presence_minus_mid_db_mean is not None
                ] + [
                    transient_checks[4]
                    for _ in [0]
                    if args.min_interference_transient_presence_share_mean is not None
                    or args.max_interference_transient_presence_share_mean is not None
                ] + [
                    transient_checks[5]
                    for _ in [0]
                    if args.min_target_interference_logspec_cosine is not None
                    or args.max_target_interference_logspec_cosine is not None
                ]
                if active_checks:
                    if args.transient_filter_mode == "all" and not all(active_checks):
                        continue
                    if args.transient_filter_mode == "any" and not any(active_checks):
                        continue

        enriched_candidates.append(
            {
                **row,
                "overlap_ratio": overlap_ratio,
                "interference_gain_db": interference_gain_db,
                "interference_pool": interference_pool,
                "interference_has_reverb": interference_has_reverb,
                "interference_speaker_name": interference_speaker_name,
                "target_has_reverb": target_has_reverb,
                **transient_metrics,
            }
        )

    by_recipe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enriched_candidates:
        by_recipe[str(row["recipe"])].append(row)

    selected_rows: list[dict[str, Any]] = []
    if recipe_caps:
        for recipe, cap in recipe_caps.items():
            candidates = list(by_recipe.get(recipe, []))
            rng.shuffle(candidates)
            selected_rows.extend(candidates[:cap])
    else:
        selected_rows = list(enriched_candidates)

    selected_rows.sort(key=lambda row: str(row["sample_id"]))
    plain_rows = [
        {
            key: value
            for key, value in row.items()
            if key
            not in {
                "overlap_ratio",
                "interference_gain_db",
                "interference_pool",
                "interference_has_reverb",
                "interference_speaker_name",
                "target_has_reverb",
            }
        }
        for row in selected_rows
    ]

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output_manifest.open("w", encoding="utf-8", newline="\n") as fh:
        for row in plain_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "input_manifest": serialize_repo_path(args.input_manifest),
        "output_manifest": serialize_repo_path(args.output_manifest),
        "sample_ids_file": serialize_repo_path(args.sample_ids_file) if args.sample_ids_file is not None else None,
        "seed": args.seed,
        "filters": {
            "recipes": sorted(recipes),
            "temporal_patterns": sorted(temporal_patterns),
            "min_target_ratio": args.min_target_ratio,
            "max_target_ratio": args.max_target_ratio,
            "min_target_energy_ratio": args.min_target_energy_ratio,
            "max_target_energy_ratio": args.max_target_energy_ratio,
            "min_overlap_ratio": args.min_overlap_ratio,
            "max_overlap_ratio": args.max_overlap_ratio,
            "min_interference_gain_db": args.min_interference_gain_db,
            "max_interference_gain_db": args.max_interference_gain_db,
            "interference_pools": sorted(interference_pools),
            "interference_speaker_names": sorted(interference_speaker_names),
            "require_interference_reverb": bool(args.require_interference_reverb),
            "forbid_interference_reverb": bool(args.forbid_interference_reverb),
            "require_target_reverb": bool(args.require_target_reverb),
            "forbid_target_reverb": bool(args.forbid_target_reverb),
            "min_target_transient_presence_minus_mid_db_mean": args.min_target_transient_presence_minus_mid_db_mean,
            "max_target_transient_presence_minus_mid_db_mean": args.max_target_transient_presence_minus_mid_db_mean,
            "min_target_transient_presence_share_mean": args.min_target_transient_presence_share_mean,
            "max_target_transient_presence_share_mean": args.max_target_transient_presence_share_mean,
            "min_interference_transient_presence_minus_mid_db_mean": (
                args.min_interference_transient_presence_minus_mid_db_mean
            ),
            "max_interference_transient_presence_minus_mid_db_mean": (
                args.max_interference_transient_presence_minus_mid_db_mean
            ),
            "min_interference_transient_presence_share_mean": args.min_interference_transient_presence_share_mean,
            "max_interference_transient_presence_share_mean": args.max_interference_transient_presence_share_mean,
            "min_target_interference_logspec_cosine": args.min_target_interference_logspec_cosine,
            "max_target_interference_logspec_cosine": args.max_target_interference_logspec_cosine,
            "transient_filter_mode": args.transient_filter_mode,
            "include_derived_metrics": bool(args.include_derived_metrics),
        },
        "recipe_caps": recipe_caps,
        "selected_count": len(plain_rows),
        **summarize(plain_rows, selected_rows),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
