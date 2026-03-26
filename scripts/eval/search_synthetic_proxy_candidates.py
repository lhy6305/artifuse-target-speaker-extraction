from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]
SPEECH_RECIPES = {"target_clean_speech", "target_hard_speech"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search metadata-defined synthetic speech subsets whose stage2-relative model ordering "
            "matches a target ordering, to help rebuild near-real-aligned objective proxies."
        )
    )
    parser.add_argument(
        "--compare",
        action="append",
        required=True,
        help="Compare jsonl mapping in the form alias=path/to/per_sample_metrics.jsonl.",
    )
    parser.add_argument(
        "--ordered-aliases",
        nargs="+",
        required=True,
        help="Expected best-to-worst ordering across the provided aliases.",
    )
    parser.add_argument(
        "--extra-order-constraint",
        action="append",
        default=[],
        help=(
            "Additional aggregate ordering constraint in the form higher>lower. "
            "Useful for excluding subsets where a known-bad model still dominates."
        ),
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--min-count", type=int, default=8)
    parser.add_argument("--min-speaker-count", type=int, default=8)
    parser.add_argument("--min-order-gap-db", type=float, default=0.0)
    parser.add_argument(
        "--require-samplewise-order-pass",
        action="store_true",
        help="Only search over rows whose per-sample alias ordering already satisfies the requested ordering.",
    )
    parser.add_argument(
        "--require-samplewise-all-constraints-pass",
        action="store_true",
        help=(
            "Only search over rows whose per-sample alias ordering and every extra order constraint both pass. "
            "This is stricter than --require-samplewise-order-pass."
        ),
    )
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


def parse_compare_mapping(values: list[str]) -> dict[str, Path]:
    mappings: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --compare value: {value!r}")
        alias, raw_path = value.split("=", 1)
        alias = alias.strip()
        compare_path = Path(raw_path.strip())
        if not alias:
            raise ValueError(f"Empty alias in --compare value: {value!r}")
        if alias in mappings:
            raise ValueError(f"Duplicate alias in --compare values: {alias}")
        mappings[alias] = compare_path
    return mappings


def parse_extra_order_constraints(values: list[str]) -> list[tuple[str, str]]:
    constraints: list[tuple[str, str]] = []
    for value in values:
        if ">" not in value:
            raise ValueError(f"Invalid --extra-order-constraint value: {value!r}")
        higher_alias, lower_alias = value.split(">", 1)
        higher_alias = higher_alias.strip()
        lower_alias = lower_alias.strip()
        if not higher_alias or not lower_alias:
            raise ValueError(f"Invalid --extra-order-constraint value: {value!r}")
        constraints.append((higher_alias, lower_alias))
    return constraints


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
    presence_share = presence_energy / (power.sum(axis=1)[transient_indices] + 1e-12)
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
    presence_share = presence_energy / (power.sum(axis=1)[transient_indices] + 1e-12)
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


def infer_interference_speaker_name(audio_path: str | None) -> str | None:
    if not audio_path:
        return None
    path = Path(audio_path)
    parent_name = path.parent.name.strip()
    return parent_name or None


def quantile_thresholds(values: list[float], quantiles: list[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=np.float32)
    output: dict[str, float] = {}
    for quantile in quantiles:
        output[f"q{int(round(quantile * 100.0))}"] = float(np.quantile(array, quantile))
    return output


def strict_order_pass(
    scores: dict[str, float],
    ordered_aliases: list[str],
    *,
    min_order_gap_db: float,
) -> tuple[bool, list[float]]:
    gaps: list[float] = []
    for index in range(len(ordered_aliases) - 1):
        left_alias = ordered_aliases[index]
        right_alias = ordered_aliases[index + 1]
        gap = float(scores[left_alias] - scores[right_alias])
        gaps.append(gap)
        if gap <= min_order_gap_db:
            return False, gaps
    return True, gaps


def extra_order_constraints_pass(
    scores: dict[str, float],
    constraints: list[tuple[str, str]],
    *,
    min_order_gap_db: float,
) -> tuple[bool, list[float]]:
    gaps: list[float] = []
    for higher_alias, lower_alias in constraints:
        gap = float(scores[higher_alias] - scores[lower_alias])
        gaps.append(gap)
        if gap <= min_order_gap_db:
            return False, gaps
    return True, gaps


def main() -> None:
    args = parse_args()
    compare_map = parse_compare_mapping(args.compare)
    ordered_aliases = list(args.ordered_aliases)
    extra_order_constraints = parse_extra_order_constraints(args.extra_order_constraint)
    missing_aliases = [alias for alias in ordered_aliases if alias not in compare_map]
    missing_constraint_aliases = sorted(
        {
            alias
            for higher_alias, lower_alias in extra_order_constraints
            for alias in [higher_alias, lower_alias]
            if alias not in compare_map
        }
    )
    if missing_aliases:
        raise ValueError(f"Ordered aliases missing compare inputs: {missing_aliases}")
    if missing_constraint_aliases:
        raise ValueError(f"Extra order constraints missing compare inputs: {missing_constraint_aliases}")

    compare_rows_by_alias: dict[str, dict[str, dict[str, Any]]] = {}
    shared_sample_ids: set[str] | None = None
    for alias, compare_path in compare_map.items():
        rows = {str(row["sample_id"]): row for row in load_jsonl(compare_path)}
        compare_rows_by_alias[alias] = rows
        sample_ids = set(rows)
        shared_sample_ids = sample_ids if shared_sample_ids is None else (shared_sample_ids & sample_ids)

    if not shared_sample_ids:
        raise RuntimeError("No shared sample ids across compare inputs.")

    base_alias = ordered_aliases[0]
    target_transient_cache: dict[str, dict[str, float]] = {}
    interference_transient_cache: dict[str, dict[str, float]] = {}
    pair_metric_cache: dict[tuple[str, str], dict[str, float]] = {}
    enriched_rows: list[dict[str, Any]] = []
    samplewise_order_pass_count = 0
    samplewise_extra_constraint_pass_count = 0
    samplewise_all_constraints_pass_count = 0
    for sample_id in sorted(shared_sample_ids):
        base_row = compare_rows_by_alias[base_alias][sample_id]
        if str(base_row.get("recipe", "")) not in SPEECH_RECIPES:
            continue
        metadata = load_json(ROOT / str(base_row["metadata_path"]))
        layers = list(metadata.get("interference_layers", []))
        if not layers:
            continue
        first_layer = layers[0]
        target_audio_path = ROOT / str(metadata["output_paths"]["target_audio_path"])
        interference_audio_path = ROOT / str(first_layer["audio_path"])
        target_key = str(target_audio_path)
        interference_key = str(interference_audio_path)
        target_transient_metrics = target_transient_cache.get(target_key)
        if target_transient_metrics is None:
            target_transient_metrics = build_target_transient_metrics(target_audio_path)
            target_transient_cache[target_key] = target_transient_metrics
        interference_transient_metrics = interference_transient_cache.get(interference_key)
        if interference_transient_metrics is None:
            interference_transient_metrics = build_interference_transient_metrics(interference_audio_path)
            interference_transient_cache[interference_key] = interference_transient_metrics
        pair_key = (target_key, interference_key)
        pair_metrics = pair_metric_cache.get(pair_key)
        if pair_metrics is None:
            pair_metrics = build_target_interference_pair_metrics(target_audio_path, interference_audio_path)
            pair_metric_cache[pair_key] = pair_metrics

        alias_deltas = {
            alias: float(compare_rows_by_alias[alias][sample_id]["sisdr_delta_db"])
            for alias in compare_map
        }
        samplewise_order_pass, samplewise_pair_gaps = strict_order_pass(
            alias_deltas,
            ordered_aliases,
            min_order_gap_db=args.min_order_gap_db,
        )
        samplewise_extra_pass, samplewise_extra_gaps = extra_order_constraints_pass(
            alias_deltas,
            extra_order_constraints,
            min_order_gap_db=args.min_order_gap_db,
        )
        if samplewise_order_pass:
            samplewise_order_pass_count += 1
        if samplewise_extra_pass:
            samplewise_extra_constraint_pass_count += 1
        samplewise_all_constraints_pass = bool(samplewise_order_pass and samplewise_extra_pass)
        if samplewise_all_constraints_pass:
            samplewise_all_constraints_pass_count += 1
        if args.require_samplewise_all_constraints_pass and not samplewise_all_constraints_pass:
            continue
        if args.require_samplewise_order_pass and not samplewise_order_pass:
            continue
        enriched_rows.append(
            {
                "sample_id": sample_id,
                "recipe": str(base_row["recipe"]),
                "temporal_pattern": str(base_row.get("temporal_pattern", "target_full")),
                "target_present_ratio": float(base_row.get("target_present_ratio", 1.0)),
                "metadata_path": str(base_row["metadata_path"]),
                "interference_pool": str(first_layer.get("pool", "")),
                "interference_gain_db": float(first_layer["gain_db"]),
                "overlap_ratio": compute_overlap_ratio(metadata),
                "interference_speaker_name": infer_interference_speaker_name(str(first_layer.get("audio_path", ""))),
                "alias_deltas": alias_deltas,
                "samplewise_order_pass": samplewise_order_pass,
                "samplewise_pair_gaps_db": samplewise_pair_gaps,
                "samplewise_extra_constraints_pass": samplewise_extra_pass,
                "samplewise_extra_constraint_gaps_db": samplewise_extra_gaps,
                "samplewise_all_constraints_pass": samplewise_all_constraints_pass,
                **target_transient_metrics,
                **interference_transient_metrics,
                **pair_metrics,
            }
        )

    if not enriched_rows:
        raise RuntimeError("No shared speech-only rows found across compare inputs.")

    gain_thresholds = quantile_thresholds(
        [row["interference_gain_db"] for row in enriched_rows],
        [0.5, 2.0 / 3.0],
    )
    transient_thresholds = quantile_thresholds(
        [row["target_transient_presence_minus_mid_db_mean"] for row in enriched_rows],
        [0.5, 2.0 / 3.0],
    )
    interference_transient_thresholds = quantile_thresholds(
        [row["interference_transient_presence_minus_mid_db_mean"] for row in enriched_rows],
        [0.5, 2.0 / 3.0],
    )
    similarity_thresholds = quantile_thresholds(
        [row["target_interference_logspec_cosine"] for row in enriched_rows],
        [0.5, 2.0 / 3.0],
    )

    speaker_counts = Counter(
        row["interference_speaker_name"]
        for row in enriched_rows
        if row["interference_speaker_name"] is not None
    )

    FilterDef = tuple[str, Callable[[dict[str, Any]], bool], dict[str, Any]]
    recipe_filters: list[FilterDef] = [
        ("all_speech", lambda row: True, {}),
        ("recipe_clean", lambda row: row["recipe"] == "target_clean_speech", {"recipes": ["target_clean_speech"]}),
        ("recipe_hard", lambda row: row["recipe"] == "target_hard_speech", {"recipes": ["target_hard_speech"]}),
    ]
    pattern_filters: list[FilterDef] = [
        ("all_patterns", lambda row: True, {}),
        ("pattern_full", lambda row: row["temporal_pattern"] == "target_full", {"temporal_patterns": ["target_full"]}),
        (
            "pattern_nonfull",
            lambda row: row["temporal_pattern"] != "target_full",
            {"temporal_patterns": ["target_absent_head", "target_absent_tail", "target_intermittent"]},
        ),
    ]
    ratio_filters: list[FilterDef] = [
        ("any_ratio", lambda row: True, {}),
        ("ratio_ge_0_95", lambda row: row["target_present_ratio"] >= 0.95, {"min_target_ratio": 0.95}),
    ]
    overlap_filters: list[FilterDef] = [
        ("any_overlap", lambda row: True, {}),
        ("overlap_ge_0_75", lambda row: (row["overlap_ratio"] or 0.0) >= 0.75, {"min_overlap_ratio": 0.75}),
        ("overlap_ge_0_90", lambda row: (row["overlap_ratio"] or 0.0) >= 0.9, {"min_overlap_ratio": 0.9}),
    ]
    pool_filters: list[FilterDef] = [
        ("all_pools", lambda row: True, {}),
        (
            "pool_clean",
            lambda row: row["interference_pool"] == "speech_interference_clean_pool",
            {"interference_pools": ["speech_interference_clean_pool"]},
        ),
        (
            "pool_hard",
            lambda row: row["interference_pool"] == "speech_interference_hard_pool",
            {"interference_pools": ["speech_interference_hard_pool"]},
        ),
    ]
    gain_filters: list[FilterDef] = [
        ("all_gains", lambda row: True, {}),
        (
            "gain_le_q50",
            lambda row, threshold=gain_thresholds["q50"]: row["interference_gain_db"] <= threshold,
            {"max_interference_gain_db": gain_thresholds["q50"]},
        ),
        (
            "gain_ge_q50",
            lambda row, threshold=gain_thresholds["q50"]: row["interference_gain_db"] >= threshold,
            {"min_interference_gain_db": gain_thresholds["q50"]},
        ),
        (
            "gain_ge_q67",
            lambda row, threshold=gain_thresholds["q67"]: row["interference_gain_db"] >= threshold,
            {"min_interference_gain_db": gain_thresholds["q67"]},
        ),
    ]
    transient_filters: list[FilterDef] = [
        ("all_transient", lambda row: True, {}),
        (
            "transient_le_q50",
            lambda row, threshold=transient_thresholds["q50"]: row["target_transient_presence_minus_mid_db_mean"]
            <= threshold,
            {"max_target_transient_presence_minus_mid_db_mean": transient_thresholds["q50"]},
        ),
        (
            "transient_lt_q67",
            lambda row, threshold=transient_thresholds["q67"]: row["target_transient_presence_minus_mid_db_mean"]
            < threshold,
            {"max_target_transient_presence_minus_mid_db_mean": transient_thresholds["q67"]},
        ),
        (
            "transient_ge_q50",
            lambda row, threshold=transient_thresholds["q50"]: row["target_transient_presence_minus_mid_db_mean"] >= threshold,
            {"min_target_transient_presence_minus_mid_db_mean": transient_thresholds["q50"]},
        ),
        (
            "transient_ge_q67",
            lambda row, threshold=transient_thresholds["q67"]: row["target_transient_presence_minus_mid_db_mean"] >= threshold,
            {"min_target_transient_presence_minus_mid_db_mean": transient_thresholds["q67"]},
        ),
    ]
    interference_transient_filters: list[FilterDef] = [
        ("all_interference_transient", lambda row: True, {}),
        (
            "interference_transient_le_q50",
            lambda row, threshold=interference_transient_thresholds["q50"]: row[
                "interference_transient_presence_minus_mid_db_mean"
            ]
            <= threshold,
            {"max_interference_transient_presence_minus_mid_db_mean": interference_transient_thresholds["q50"]},
        ),
        (
            "interference_transient_lt_q67",
            lambda row, threshold=interference_transient_thresholds["q67"]: row[
                "interference_transient_presence_minus_mid_db_mean"
            ]
            < threshold,
            {"max_interference_transient_presence_minus_mid_db_mean": interference_transient_thresholds["q67"]},
        ),
        (
            "interference_transient_ge_q50",
            lambda row, threshold=interference_transient_thresholds["q50"]: row[
                "interference_transient_presence_minus_mid_db_mean"
            ]
            >= threshold,
            {"min_interference_transient_presence_minus_mid_db_mean": interference_transient_thresholds["q50"]},
        ),
    ]
    similarity_filters: list[FilterDef] = [
        ("all_similarity", lambda row: True, {}),
        (
            "similarity_ge_q50",
            lambda row, threshold=similarity_thresholds["q50"]: row["target_interference_logspec_cosine"] >= threshold,
            {"min_target_interference_logspec_cosine": similarity_thresholds["q50"]},
        ),
        (
            "similarity_ge_q67",
            lambda row, threshold=similarity_thresholds["q67"]: row["target_interference_logspec_cosine"] >= threshold,
            {"min_target_interference_logspec_cosine": similarity_thresholds["q67"]},
        ),
    ]
    speaker_filters: list[FilterDef] = [("all_speakers", lambda row: True, {})]
    for speaker_name, count in sorted(speaker_counts.items()):
        if count < args.min_speaker_count:
            continue
        speaker_filters.append(
            (
                f"speaker_{speaker_name}",
                lambda row, speaker_name=speaker_name: row["interference_speaker_name"] == speaker_name,
                {"interference_speaker_names": [speaker_name]},
            )
        )

    candidates: list[dict[str, Any]] = []
    for recipe_name, recipe_pred, recipe_builder in recipe_filters:
        for pattern_name, pattern_pred, pattern_builder in pattern_filters:
            for ratio_name, ratio_pred, ratio_builder in ratio_filters:
                for overlap_name, overlap_pred, overlap_builder in overlap_filters:
                    for pool_name, pool_pred, pool_builder in pool_filters:
                        for gain_name, gain_pred, gain_builder in gain_filters:
                            for transient_name, transient_pred, transient_builder in transient_filters:
                                for interference_transient_name, interference_transient_pred, interference_transient_builder in interference_transient_filters:
                                    for similarity_name, similarity_pred, similarity_builder in similarity_filters:
                                        for speaker_name, speaker_pred, speaker_builder in speaker_filters:
                                            selected_rows = [
                                                row
                                                for row in enriched_rows
                                                if recipe_pred(row)
                                                and pattern_pred(row)
                                                and ratio_pred(row)
                                                and overlap_pred(row)
                                                and pool_pred(row)
                                                and gain_pred(row)
                                                and transient_pred(row)
                                                and interference_transient_pred(row)
                                                and similarity_pred(row)
                                                and speaker_pred(row)
                                            ]
                                            if len(selected_rows) < args.min_count:
                                                continue

                                            alias_scores = {
                                                alias: float(
                                                    sum(row["alias_deltas"][alias] for row in selected_rows) / len(selected_rows)
                                                )
                                                for alias in compare_map
                                            }
                                            order_pass, pair_gaps = strict_order_pass(
                                                alias_scores,
                                                ordered_aliases,
                                                min_order_gap_db=args.min_order_gap_db,
                                            )
                                            extra_constraints_pass, extra_constraint_gaps = extra_order_constraints_pass(
                                                alias_scores,
                                                extra_order_constraints,
                                                min_order_gap_db=args.min_order_gap_db,
                                            )
                                            total_order_pass = bool(order_pass and extra_constraints_pass)
                                            all_gaps = pair_gaps + extra_constraint_gaps
                                            builder_filters = {
                                                **recipe_builder,
                                                **pattern_builder,
                                                **ratio_builder,
                                                **overlap_builder,
                                                **pool_builder,
                                                **gain_builder,
                                                **transient_builder,
                                                **interference_transient_builder,
                                                **similarity_builder,
                                                **speaker_builder,
                                            }
                                            candidates.append(
                                                {
                                                    "subset_name": "__".join(
                                                        [
                                                            recipe_name,
                                                            pattern_name,
                                                            ratio_name,
                                                            overlap_name,
                                                            pool_name,
                                                            gain_name,
                                                            transient_name,
                                                            interference_transient_name,
                                                            similarity_name,
                                                            speaker_name,
                                                        ]
                                                    ),
                                                    "count": len(selected_rows),
                                                    "order_pass": total_order_pass,
                                                    "ordered_aliases": ordered_aliases,
                                                    "extra_order_constraints": [
                                                        f"{higher_alias}>{lower_alias}"
                                                        for higher_alias, lower_alias in extra_order_constraints
                                                    ],
                                                    "alias_scores": alias_scores,
                                                    "pair_gaps_db": pair_gaps,
                                                    "extra_order_constraint_gaps_db": extra_constraint_gaps,
                                                    "min_pair_gap_db": float(min(all_gaps)) if all_gaps else 0.0,
                                                    "mean_overlap_ratio": float(
                                                        sum((row["overlap_ratio"] or 0.0) for row in selected_rows) / len(selected_rows)
                                                    ),
                                                    "mean_interference_gain_db": float(
                                                        sum(row["interference_gain_db"] for row in selected_rows) / len(selected_rows)
                                                    ),
                                                    "mean_target_transient_presence_minus_mid_db_mean": float(
                                                        sum(
                                                            row["target_transient_presence_minus_mid_db_mean"] for row in selected_rows
                                                        )
                                                        / len(selected_rows)
                                                    ),
                                                    "mean_interference_transient_presence_minus_mid_db_mean": float(
                                                        sum(
                                                            row["interference_transient_presence_minus_mid_db_mean"]
                                                            for row in selected_rows
                                                        )
                                                        / len(selected_rows)
                                                    ),
                                                    "mean_target_interference_logspec_cosine": float(
                                                        sum(row["target_interference_logspec_cosine"] for row in selected_rows)
                                                        / len(selected_rows)
                                                    ),
                                                    "recipe_counts": dict(
                                                        sorted(Counter(row["recipe"] for row in selected_rows).items())
                                                    ),
                                                    "pattern_counts": dict(
                                                        sorted(Counter(row["temporal_pattern"] for row in selected_rows).items())
                                                    ),
                                                    "pool_counts": dict(
                                                        sorted(Counter(row["interference_pool"] for row in selected_rows).items())
                                                    ),
                                                    "speaker_counts": dict(
                                                        sorted(
                                                            Counter(
                                                                row["interference_speaker_name"]
                                                                for row in selected_rows
                                                                if row["interference_speaker_name"] is not None
                                                            ).items()
                                                        )
                                                    ),
                                                    "sample_ids": [str(row["sample_id"]) for row in selected_rows],
                                                    "builder_filters": builder_filters,
                                                }
                                            )

    candidates.sort(
        key=lambda row: (
            1 if row["order_pass"] else 0,
            row["min_pair_gap_db"],
            row["count"],
        ),
        reverse=True,
    )

    output = {
        "compares": {
            alias: serialize_repo_path(path)
            for alias, path in compare_map.items()
        },
        "ordered_aliases": ordered_aliases,
        "extra_order_constraints": [f"{higher_alias}>{lower_alias}" for higher_alias, lower_alias in extra_order_constraints],
        "num_shared_speech_rows": len(enriched_rows),
        "num_samplewise_order_pass_rows_before_optional_filter": samplewise_order_pass_count,
        "num_samplewise_extra_constraint_pass_rows_before_optional_filter": samplewise_extra_constraint_pass_count,
        "num_samplewise_all_constraints_pass_rows_before_optional_filter": samplewise_all_constraints_pass_count,
        "require_samplewise_order_pass": bool(args.require_samplewise_order_pass),
        "require_samplewise_all_constraints_pass": bool(args.require_samplewise_all_constraints_pass),
        "thresholds": {
            "gain_thresholds_db": gain_thresholds,
            "transient_thresholds_db": transient_thresholds,
            "interference_transient_thresholds_db": interference_transient_thresholds,
            "target_interference_similarity_thresholds": similarity_thresholds,
            "min_count": args.min_count,
            "min_speaker_count": args.min_speaker_count,
            "min_order_gap_db": args.min_order_gap_db,
        },
        "top_order_pass_candidates": [row for row in candidates if row["order_pass"]][: args.top_k],
        "top_near_miss_candidates": [row for row in candidates if not row["order_pass"]][: args.top_k],
        "speaker_counts": dict(sorted(speaker_counts.items())),
        "num_candidates": len(candidates),
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "output_json": serialize_repo_path(args.output_json),
                "num_shared_speech_rows": len(enriched_rows),
                "num_samplewise_order_pass_rows_before_optional_filter": samplewise_order_pass_count,
                "num_samplewise_extra_constraint_pass_rows_before_optional_filter": samplewise_extra_constraint_pass_count,
                "num_samplewise_all_constraints_pass_rows_before_optional_filter": samplewise_all_constraints_pass_count,
                "require_samplewise_order_pass": bool(args.require_samplewise_order_pass),
                "require_samplewise_all_constraints_pass": bool(args.require_samplewise_all_constraints_pass),
                "extra_order_constraints": [
                    f"{higher_alias}>{lower_alias}" for higher_alias, lower_alias in extra_order_constraints
                ],
                "num_candidates": len(candidates),
                "top_order_pass_count": len(output["top_order_pass_candidates"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
