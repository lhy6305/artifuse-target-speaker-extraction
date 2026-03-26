from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torchaudio
from torch.nn.utils.rnn import pad_sequence
from torch.utils.data import Dataset


@dataclass(frozen=True)
class SyntheticSample:
    sample_id: str
    mixture_audio_path: Path
    target_audio_path: Path
    reference_audio_path: Path
    metadata_path: Path
    recipe: str
    temporal_pattern: str
    target_present_ratio: float
    target_energy_ratio: float | None
    target_transient_presence_minus_mid_db_mean: float | None
    target_transient_presence_share_mean: float | None
    interference_transient_presence_minus_mid_db_mean: float | None
    interference_transient_presence_share_mean: float | None
    target_interference_logspec_cosine: float | None


def _compute_overlap_ratio(metadata: dict[str, Any]) -> float:
    layers = list(metadata.get("interference_layers", []))
    if not layers:
        return float("nan")
    duration = float(metadata.get("target_duration_sec", 0.0))
    if duration <= 0.0:
        return float("nan")
    start_offset = min(float(layer.get("start_offset_sec", 0.0)) for layer in layers)
    overlap = max(0.0, duration - start_offset) / duration
    return float(min(max(overlap, 0.0), 1.0))


def _intervals_from_target_segments(
    target_segments: list[dict[str, Any]],
    overlap_start_sec: float,
    overlap_end_sec: float,
) -> list[dict[str, float]]:
    intervals: list[dict[str, float]] = []
    for segment in target_segments:
        segment_start = float(segment.get("output_start_sec", 0.0))
        segment_duration = float(segment.get("duration_sec", 0.0))
        segment_end = segment_start + max(segment_duration, 0.0)
        start_sec = max(overlap_start_sec, segment_start)
        end_sec = min(overlap_end_sec, segment_end)
        if end_sec <= start_sec:
            continue
        intervals.append(
            {
                "start_sec": start_sec,
                "end_sec": end_sec,
                "duration_sec": end_sec - start_sec,
            }
        )
    return intervals


def _subtract_interval(
    base_intervals: list[dict[str, float]],
    subtract_start_sec: float,
    subtract_end_sec: float,
) -> list[dict[str, float]]:
    if subtract_end_sec <= subtract_start_sec:
        return list(base_intervals)

    updated: list[dict[str, float]] = []
    for interval in base_intervals:
        base_start = float(interval["start_sec"])
        base_end = float(interval["end_sec"])
        if subtract_end_sec <= base_start or subtract_start_sec >= base_end:
            updated.append(interval)
            continue
        if subtract_start_sec > base_start:
            updated.append(
                {
                    "start_sec": base_start,
                    "end_sec": subtract_start_sec,
                    "duration_sec": subtract_start_sec - base_start,
                }
            )
        if subtract_end_sec < base_end:
            updated.append(
                {
                    "start_sec": subtract_end_sec,
                    "end_sec": base_end,
                    "duration_sec": base_end - subtract_end_sec,
                }
            )
    return updated


def _compute_target_overlap_intervals(metadata: dict[str, Any]) -> list[dict[str, float]]:
    duration_sec = float(metadata.get("target_duration_sec", 0.0))
    if duration_sec <= 0.0:
        return []

    layers = list(metadata.get("interference_layers", []))
    if not layers:
        return []
    overlap_start_sec = min(float(layer.get("start_offset_sec", 0.0)) for layer in layers)
    overlap_start_sec = min(max(overlap_start_sec, 0.0), duration_sec)
    overlap_end_sec = duration_sec
    if overlap_end_sec <= overlap_start_sec:
        return []

    target_segments = list(metadata.get("target_segments", []))
    if target_segments:
        return _intervals_from_target_segments(
            target_segments=target_segments,
            overlap_start_sec=overlap_start_sec,
            overlap_end_sec=overlap_end_sec,
        )

    overlap_intervals = [
        {
            "start_sec": overlap_start_sec,
            "end_sec": overlap_end_sec,
            "duration_sec": overlap_end_sec - overlap_start_sec,
        }
    ]
    for interval in list(metadata.get("target_absent_intervals", [])):
        overlap_intervals = _subtract_interval(
            base_intervals=overlap_intervals,
            subtract_start_sec=float(interval.get("start_sec", 0.0)),
            subtract_end_sec=float(interval.get("end_sec", 0.0)),
        )
        if not overlap_intervals:
            break
    return overlap_intervals


def _infer_interference_speaker_name(audio_path: str | None) -> str:
    if not audio_path:
        return ""
    parent_name = Path(audio_path).parent.name.strip()
    return parent_name


def _categorize_interference_pool(pool_name: str) -> str:
    normalized = pool_name.strip().lower()
    if not normalized:
        return ""
    if "speech" in normalized:
        return "speech"
    if "music" in normalized:
        return "music"
    return "other"


def _summarize_interference_layers(metadata: dict[str, Any]) -> dict[str, Any]:
    layers = list(metadata.get("interference_layers", []))
    categories: set[str] = set()
    pools: list[str] = []
    speaker_names: list[str] = []

    for layer in layers:
        pool_name = str(layer.get("pool", "")).strip()
        if pool_name:
            pools.append(pool_name)
            category = _categorize_interference_pool(pool_name)
            if category:
                categories.add(category)

        speaker_name = _infer_interference_speaker_name(str(layer.get("audio_path", "")))
        if speaker_name:
            speaker_names.append(speaker_name)

    ordered_categories = [name for name in ("speech", "music", "other") if name in categories]
    if not ordered_categories:
        profile = "none"
    elif len(ordered_categories) == 1:
        profile = f"{ordered_categories[0]}_only"
    else:
        profile = "_plus_".join(ordered_categories)
    return {
        "layer_count": len(layers),
        "profile": profile,
        "has_speech": "speech" in categories,
        "has_music": "music" in categories,
        "has_other": "other" in categories,
        "pools": sorted(set(pools)),
        "speaker_names": sorted(set(speaker_names)),
    }


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


def _load_audio_mono(path: Path, sample_rate: int) -> torch.Tensor:
    waveform, sr = torchaudio.load(str(path))
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != sample_rate:
        waveform = torchaudio.functional.resample(waveform, sr, sample_rate)
    return waveform.squeeze(0).contiguous()


class SyntheticTSEDataset(Dataset[dict[str, Any]]):
    def __init__(self, manifest_path: Path, sample_rate: int = 16000) -> None:
        self.manifest_path = manifest_path
        self.sample_rate = sample_rate
        self.root = manifest_path.resolve().parents[2]
        self.samples = [
            SyntheticSample(
                sample_id=row["sample_id"],
                mixture_audio_path=self.root / row["mixture_audio_path"],
                target_audio_path=self.root / row["target_audio_path"],
                reference_audio_path=self.root / row["reference_audio_path"],
                metadata_path=self.root / row["metadata_path"],
                recipe=row["recipe"],
                temporal_pattern=row.get("temporal_pattern", "target_full"),
                target_present_ratio=float(row.get("target_present_ratio", 1.0)),
                target_energy_ratio=(
                    float(row["target_energy_ratio"])
                    if row.get("target_energy_ratio") is not None
                    else None
                ),
                target_transient_presence_minus_mid_db_mean=(
                    float(row["target_transient_presence_minus_mid_db_mean"])
                    if row.get("target_transient_presence_minus_mid_db_mean") is not None
                    else None
                ),
                target_transient_presence_share_mean=(
                    float(row["target_transient_presence_share_mean"])
                    if row.get("target_transient_presence_share_mean") is not None
                    else None
                ),
                interference_transient_presence_minus_mid_db_mean=(
                    float(row["interference_transient_presence_minus_mid_db_mean"])
                    if row.get("interference_transient_presence_minus_mid_db_mean") is not None
                    else None
                ),
                interference_transient_presence_share_mean=(
                    float(row["interference_transient_presence_share_mean"])
                    if row.get("interference_transient_presence_share_mean") is not None
                    else None
                ),
                target_interference_logspec_cosine=(
                    float(row["target_interference_logspec_cosine"])
                    if row.get("target_interference_logspec_cosine") is not None
                    else None
                ),
            )
            for row in load_jsonl(manifest_path)
        ]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        sample = self.samples[index]
        metadata = load_json(sample.metadata_path)
        layers = list(metadata.get("interference_layers", []))
        first_layer = layers[0] if layers else {}
        interference_summary = _summarize_interference_layers(metadata)
        return {
            "sample_id": sample.sample_id,
            "mixture": _load_audio_mono(sample.mixture_audio_path, self.sample_rate),
            "target": _load_audio_mono(sample.target_audio_path, self.sample_rate),
            "reference": _load_audio_mono(sample.reference_audio_path, self.sample_rate),
            "recipe": sample.recipe,
            "temporal_pattern": sample.temporal_pattern,
            "target_present_ratio": sample.target_present_ratio,
            "target_energy_ratio": (
                float(sample.target_energy_ratio)
                if sample.target_energy_ratio is not None
                else float("nan")
            ),
            "target_transient_presence_minus_mid_db_mean": (
                float(sample.target_transient_presence_minus_mid_db_mean)
                if sample.target_transient_presence_minus_mid_db_mean is not None
                else float("nan")
            ),
            "target_transient_presence_share_mean": (
                float(sample.target_transient_presence_share_mean)
                if sample.target_transient_presence_share_mean is not None
                else float("nan")
            ),
            "interference_transient_presence_minus_mid_db_mean": (
                float(sample.interference_transient_presence_minus_mid_db_mean)
                if sample.interference_transient_presence_minus_mid_db_mean is not None
                else float("nan")
            ),
            "interference_transient_presence_share_mean": (
                float(sample.interference_transient_presence_share_mean)
                if sample.interference_transient_presence_share_mean is not None
                else float("nan")
            ),
            "target_interference_logspec_cosine": (
                float(sample.target_interference_logspec_cosine)
                if sample.target_interference_logspec_cosine is not None
                else float("nan")
            ),
            "overlap_ratio": _compute_overlap_ratio(metadata),
            "interference_gain_db": float(first_layer.get("gain_db", float("nan"))),
            "interference_pool": str(first_layer.get("pool", "")),
            "interference_speaker_name": _infer_interference_speaker_name(
                str(first_layer.get("audio_path", ""))
            ),
            "interference_layer_count": int(interference_summary["layer_count"]),
            "interference_profile": str(interference_summary["profile"]),
            "has_speech_interference": bool(interference_summary["has_speech"]),
            "has_music_interference": bool(interference_summary["has_music"]),
            "has_other_interference": bool(interference_summary["has_other"]),
            "interference_pools_all": list(interference_summary["pools"]),
            "interference_speaker_names_all": list(interference_summary["speaker_names"]),
            "target_absent_intervals": list(metadata.get("target_absent_intervals", [])),
            "target_overlap_intervals": _compute_target_overlap_intervals(metadata),
            "metadata_path": _serialize_repo_path(sample.metadata_path, self.root),
        }


def _serialize_repo_path(path: Path, root: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def _pad_audio_batch(items: list[torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
    lengths = torch.tensor([item.shape[-1] for item in items], dtype=torch.long)
    padded = pad_sequence(items, batch_first=True)
    return padded, lengths


def synthetic_collate_fn(batch: list[dict[str, Any]]) -> dict[str, Any]:
    mixtures, mixture_lengths = _pad_audio_batch([item["mixture"] for item in batch])
    targets, target_lengths = _pad_audio_batch([item["target"] for item in batch])
    references, reference_lengths = _pad_audio_batch([item["reference"] for item in batch])

    return {
        "sample_ids": [item["sample_id"] for item in batch],
        "mixture": mixtures,
        "mixture_lengths": mixture_lengths,
        "target": targets,
        "target_lengths": target_lengths,
        "reference": references,
        "reference_lengths": reference_lengths,
        "recipes": [item["recipe"] for item in batch],
        "temporal_patterns": [item["temporal_pattern"] for item in batch],
        "target_present_ratios": torch.tensor(
            [item["target_present_ratio"] for item in batch],
            dtype=torch.float32,
        ),
        "target_energy_ratios": torch.tensor(
            [item["target_energy_ratio"] for item in batch],
            dtype=torch.float32,
        ),
        "target_transient_presence_minus_mid_db_means": torch.tensor(
            [item["target_transient_presence_minus_mid_db_mean"] for item in batch],
            dtype=torch.float32,
        ),
        "target_transient_presence_share_means": torch.tensor(
            [item["target_transient_presence_share_mean"] for item in batch],
            dtype=torch.float32,
        ),
        "interference_transient_presence_minus_mid_db_means": torch.tensor(
            [item["interference_transient_presence_minus_mid_db_mean"] for item in batch],
            dtype=torch.float32,
        ),
        "interference_transient_presence_share_means": torch.tensor(
            [item["interference_transient_presence_share_mean"] for item in batch],
            dtype=torch.float32,
        ),
        "target_interference_logspec_cosines": torch.tensor(
            [item["target_interference_logspec_cosine"] for item in batch],
            dtype=torch.float32,
        ),
        "overlap_ratios": torch.tensor(
            [item["overlap_ratio"] for item in batch],
            dtype=torch.float32,
        ),
        "interference_gain_dbs": torch.tensor(
            [item["interference_gain_db"] for item in batch],
            dtype=torch.float32,
        ),
        "interference_pools": [item["interference_pool"] for item in batch],
        "interference_speaker_names": [item["interference_speaker_name"] for item in batch],
        "interference_layer_counts": [item["interference_layer_count"] for item in batch],
        "interference_profiles": [item["interference_profile"] for item in batch],
        "has_speech_interference": [item["has_speech_interference"] for item in batch],
        "has_music_interference": [item["has_music_interference"] for item in batch],
        "has_other_interference": [item["has_other_interference"] for item in batch],
        "interference_pools_all": [item["interference_pools_all"] for item in batch],
        "interference_speaker_names_all": [item["interference_speaker_names_all"] for item in batch],
        "target_absent_intervals": [item["target_absent_intervals"] for item in batch],
        "target_overlap_intervals": [item["target_overlap_intervals"] for item in batch],
        "metadata_paths": [item["metadata_path"] for item in batch],
    }
