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
            )
            for row in load_jsonl(manifest_path)
        ]

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        sample = self.samples[index]
        metadata = load_json(sample.metadata_path)
        return {
            "sample_id": sample.sample_id,
            "mixture": _load_audio_mono(sample.mixture_audio_path, self.sample_rate),
            "target": _load_audio_mono(sample.target_audio_path, self.sample_rate),
            "reference": _load_audio_mono(sample.reference_audio_path, self.sample_rate),
            "recipe": sample.recipe,
            "temporal_pattern": sample.temporal_pattern,
            "target_present_ratio": sample.target_present_ratio,
            "target_absent_intervals": list(metadata.get("target_absent_intervals", [])),
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
        "target_absent_intervals": [item["target_absent_intervals"] for item in batch],
        "metadata_paths": [item["metadata_path"] for item in batch],
    }
