from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]

SPEECH_POOL_TOKENS = ("speech",)
MUSIC_POOL_TOKENS = ("music",)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize a local hard-present artifact proxy by clipping short overlap-risk windows "
            "from an existing synthetic hard-present artifact proxy manifest."
        )
    )
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--summary-json", type=Path, required=True)
    parser.add_argument("--sample-ids-file", type=Path, required=True)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--window-duration-sec", type=float, default=1.0)
    parser.add_argument("--window-hop-sec", type=float, default=0.02)
    parser.add_argument(
        "--min-local-target-share",
        type=float,
        default=0.02,
        help="Reject windows whose local target energy share is below this floor.",
    )
    parser.add_argument(
        "--max-local-target-share",
        type=float,
        default=0.35,
        help="Reject windows whose local target energy share is above this ceiling.",
    )
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


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    waveform, sample_rate = sf.read(str(path), always_2d=False)
    waveform = np.asarray(waveform, dtype=np.float32)
    if waveform.ndim == 2:
        waveform = waveform.mean(axis=1)
    return waveform, sample_rate


def write_audio(path: Path, waveform: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), waveform.astype(np.float32, copy=False), sample_rate, subtype="PCM_16")


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def energy(waveform: np.ndarray) -> float:
    return float(np.dot(waveform, waveform))


def safe_log10(value: float, eps: float = 1e-12) -> float:
    return float(10.0 * np.log10(max(value, eps)))


def fit_or_pad(waveform: np.ndarray, num_samples: int) -> np.ndarray:
    if waveform.shape[0] >= num_samples:
        return waveform[:num_samples].astype(np.float32, copy=False)
    padded = np.zeros(num_samples, dtype=np.float32)
    padded[: waveform.shape[0]] = waveform
    return padded


def pool_category(pool_name: str) -> str:
    lowered = pool_name.strip().lower()
    if any(token in lowered for token in MUSIC_POOL_TOKENS):
        return "music"
    if any(token in lowered for token in SPEECH_POOL_TOKENS):
        return "speech"
    return "other"


def summarize_interference_layers(layers: list[dict[str, Any]]) -> dict[str, Any]:
    categories = {pool_category(str(layer.get("pool", ""))) for layer in layers}
    ordered = [name for name in ("speech", "music", "other") if name in categories]
    if not ordered:
        profile = "none"
    elif len(ordered) == 1:
        profile = f"{ordered[0]}_only"
    else:
        profile = "_plus_".join(ordered)
    return {
        "interference_layer_count": len(layers),
        "interference_profile": profile,
        "has_speech_interference": "speech" in categories,
        "has_music_interference": "music" in categories,
        "has_other_interference": "other" in categories,
    }


def clip_intervals(
    intervals: list[dict[str, Any]],
    *,
    window_start_sec: float,
    window_end_sec: float,
    start_key: str,
    duration_key: str | None = None,
    end_key: str | None = None,
) -> list[dict[str, float]]:
    clipped: list[dict[str, float]] = []
    for interval in intervals:
        start_sec = float(interval.get(start_key, 0.0))
        if duration_key is not None:
            end_sec_value = start_sec + float(interval.get(duration_key, 0.0))
        elif end_key is not None:
            end_sec_value = float(interval.get(end_key, 0.0))
        else:
            raise ValueError("Either duration_key or end_key must be provided")
        overlap_start_sec = max(window_start_sec, start_sec)
        overlap_end_sec = min(window_end_sec, end_sec_value)
        if overlap_end_sec <= overlap_start_sec:
            continue
        clipped.append(
            {
                "start_sec": overlap_start_sec - window_start_sec,
                "end_sec": overlap_end_sec - window_start_sec,
                "duration_sec": overlap_end_sec - overlap_start_sec,
            }
        )
    return clipped


def select_window(
    mixture: np.ndarray,
    target: np.ndarray,
    *,
    sample_rate: int,
    window_duration_sec: float,
    window_hop_sec: float,
    min_local_target_share: float,
    max_local_target_share: float,
) -> dict[str, float | str]:
    common_length = min(mixture.shape[0], target.shape[0])
    mixture = mixture[:common_length]
    target = target[:common_length]
    interference = mixture - target

    window_samples = max(1, int(round(window_duration_sec * sample_rate)))
    hop_samples = max(1, int(round(window_hop_sec * sample_rate)))
    if common_length <= window_samples:
        target_energy = energy(target)
        interference_energy = energy(interference)
        total_energy = max(target_energy + interference_energy, 1e-12)
        return {
            "window_start_sec": 0.0,
            "window_duration_sec": common_length / float(sample_rate),
            "local_target_share": target_energy / total_energy,
            "local_target_energy": target_energy,
            "local_interference_energy": interference_energy,
            "selection_score": interference_energy / max(target_energy, 1e-12),
            "selection_mode": "full_clip_fallback",
        }

    best_valid: dict[str, float | str] | None = None
    best_fallback: dict[str, float | str] | None = None
    for start_sample in range(0, max(1, common_length - window_samples + 1), hop_samples):
        end_sample = min(common_length, start_sample + window_samples)
        target_slice = target[start_sample:end_sample]
        interference_slice = interference[start_sample:end_sample]
        target_energy = energy(target_slice)
        interference_energy = energy(interference_slice)
        total_energy = target_energy + interference_energy
        if total_energy <= 1e-12:
            continue
        local_target_share = target_energy / total_energy
        candidate = {
            "window_start_sec": start_sample / float(sample_rate),
            "window_duration_sec": (end_sample - start_sample) / float(sample_rate),
            "local_target_share": local_target_share,
            "local_target_energy": target_energy,
            "local_interference_energy": interference_energy,
            "selection_score": interference_energy / max(target_energy, 1e-12),
        }
        if best_fallback is None or float(candidate["local_interference_energy"]) > float(best_fallback["local_interference_energy"]):
            best_fallback = {**candidate, "selection_mode": "interference_peak_fallback"}
        if not (min_local_target_share <= local_target_share <= max_local_target_share):
            continue
        if best_valid is None or float(candidate["selection_score"]) > float(best_valid["selection_score"]):
            best_valid = {**candidate, "selection_mode": "target_share_bounded_peak"}

    if best_valid is not None:
        return best_valid
    if best_fallback is not None:
        return best_fallback
    return {
        "window_start_sec": 0.0,
        "window_duration_sec": common_length / float(sample_rate),
        "local_target_share": 0.0,
        "local_target_energy": 0.0,
        "local_interference_energy": 0.0,
        "selection_score": 0.0,
        "selection_mode": "empty_fallback",
    }


def build_local_metadata(
    original_metadata: dict[str, Any],
    *,
    local_sample_id: str,
    local_mixture_audio_path: Path,
    local_target_audio_path: Path,
    local_reference_audio_path: Path,
    local_metadata_path: Path,
    window_start_sec: float,
    window_duration_sec: float,
    selection: dict[str, float | str],
    source_metadata_path: Path,
) -> dict[str, Any]:
    window_end_sec = window_start_sec + window_duration_sec
    target_segments = clip_intervals(
        list(original_metadata.get("target_segments", [])),
        window_start_sec=window_start_sec,
        window_end_sec=window_end_sec,
        start_key="output_start_sec",
        duration_key="duration_sec",
    )
    if not target_segments:
        target_segments = [
            {
                "start_sec": 0.0,
                "end_sec": window_duration_sec,
                "duration_sec": window_duration_sec,
            }
        ]
    local_target_segments = [
        {
            "output_start_sec": float(interval["start_sec"]),
            "source_start_sec": float(interval["start_sec"]),
            "duration_sec": float(interval["duration_sec"]),
        }
        for interval in target_segments
    ]
    target_present_duration_sec = float(sum(interval["duration_sec"] for interval in target_segments))
    local_target_absent_intervals = clip_intervals(
        list(original_metadata.get("target_absent_intervals", [])),
        window_start_sec=window_start_sec,
        window_end_sec=window_end_sec,
        start_key="start_sec",
        end_key="end_sec",
    )

    local_layers: list[dict[str, Any]] = []
    for layer in list(original_metadata.get("interference_layers", [])):
        start_offset_sec = float(layer.get("start_offset_sec", 0.0))
        if start_offset_sec >= window_end_sec:
            continue
        updated_layer = dict(layer)
        updated_layer["start_offset_sec"] = max(0.0, start_offset_sec - window_start_sec)
        local_layers.append(updated_layer)

    return {
        "sample_id": local_sample_id,
        "split": original_metadata.get("split", ""),
        "recipe_profile": original_metadata.get("recipe_profile", ""),
        "recipe": original_metadata["recipe"],
        "target_present_ratio": 1.0 if window_duration_sec <= 0.0 else target_present_duration_sec / window_duration_sec,
        "temporal_pattern": "target_full",
        "target_duration_sec": window_duration_sec,
        "target_present_duration_sec": target_present_duration_sec,
        "reference_duration_sec": float(original_metadata.get("reference_duration_sec", 0.0)),
        "target_source": dict(original_metadata.get("target_source", {})),
        "reference_source": dict(original_metadata.get("reference_source", {})),
        "interference_layers": local_layers,
        "target_segments": local_target_segments,
        "target_absent_intervals": local_target_absent_intervals,
        "local_proxy": {
            "source_sample_id": original_metadata.get("sample_id", ""),
            "source_metadata_path": serialize_repo_path(source_metadata_path),
            "window_start_sec": float(window_start_sec),
            "window_duration_sec": float(window_duration_sec),
            "selection_mode": str(selection["selection_mode"]),
            "selection_score": float(selection["selection_score"]),
            "local_target_share": float(selection["local_target_share"]),
            "local_target_energy": float(selection["local_target_energy"]),
            "local_interference_energy": float(selection["local_interference_energy"]),
        },
        "output_paths": {
            "mixture_audio_path": serialize_repo_path(local_mixture_audio_path),
            "target_audio_path": serialize_repo_path(local_target_audio_path),
            "reference_audio_path": serialize_repo_path(local_reference_audio_path),
            "metadata_path": serialize_repo_path(local_metadata_path),
        },
    }


def main() -> None:
    args = parse_args()
    rows = load_jsonl(args.input_manifest)
    args.output_root.mkdir(parents=True, exist_ok=True)
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.sample_ids_file.parent.mkdir(parents=True, exist_ok=True)

    output_rows: list[dict[str, Any]] = []
    selection_modes: dict[str, int] = {}
    local_target_shares: list[float] = []
    local_target_db_values: list[float] = []
    local_interference_db_values: list[float] = []
    local_target_to_interference_db_values: list[float] = []

    for row in rows:
        mixture_audio_path = ROOT / row["mixture_audio_path"]
        target_audio_path = ROOT / row["target_audio_path"]
        reference_audio_path = ROOT / row["reference_audio_path"]
        metadata_path = ROOT / row["metadata_path"]

        mixture, mixture_sr = load_audio(mixture_audio_path)
        target, target_sr = load_audio(target_audio_path)
        if mixture_sr != args.sample_rate or target_sr != args.sample_rate:
            raise ValueError(
                f"Sample rate mismatch for {row['sample_id']}: mixture={mixture_sr}, target={target_sr}, expected={args.sample_rate}"
            )

        selection = select_window(
            mixture=mixture,
            target=target,
            sample_rate=args.sample_rate,
            window_duration_sec=args.window_duration_sec,
            window_hop_sec=args.window_hop_sec,
            min_local_target_share=args.min_local_target_share,
            max_local_target_share=args.max_local_target_share,
        )
        window_start_sec = float(selection["window_start_sec"])
        window_duration_sec = float(selection["window_duration_sec"])
        start_sample = int(round(window_start_sec * args.sample_rate))
        end_sample = start_sample + int(round(window_duration_sec * args.sample_rate))

        local_mixture = fit_or_pad(mixture[start_sample:end_sample], end_sample - start_sample)
        local_target = fit_or_pad(target[start_sample:end_sample], end_sample - start_sample)
        local_interference = local_mixture - local_target

        original_metadata = load_json(metadata_path)
        local_sample_id = f"{row['sample_id']}_hard_present_artifact_local_v1"
        local_sample_dir = args.output_root / str(row.get("split", "")) / local_sample_id
        local_mixture_audio_path = local_sample_dir / "mixture.wav"
        local_target_audio_path = local_sample_dir / "target.wav"
        local_metadata_path = local_sample_dir / "metadata.json"

        write_audio(local_mixture_audio_path, local_mixture, args.sample_rate)
        write_audio(local_target_audio_path, local_target, args.sample_rate)

        local_metadata = build_local_metadata(
            original_metadata=original_metadata,
            local_sample_id=local_sample_id,
            local_mixture_audio_path=local_mixture_audio_path,
            local_target_audio_path=local_target_audio_path,
            local_reference_audio_path=reference_audio_path,
            local_metadata_path=local_metadata_path,
            window_start_sec=window_start_sec,
            window_duration_sec=window_duration_sec,
            selection=selection,
            source_metadata_path=metadata_path,
        )
        local_metadata_path.write_text(
            json.dumps(local_metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        local_layers_summary = summarize_interference_layers(list(local_metadata.get("interference_layers", [])))
        local_target_energy = float(selection["local_target_energy"])
        local_interference_energy = float(selection["local_interference_energy"])
        local_target_share = float(selection["local_target_share"])
        local_target_to_interference_ratio = local_target_energy / max(local_interference_energy, 1e-12)

        output_rows.append(
            {
                "sample_id": local_sample_id,
                "split": row.get("split", ""),
                "recipe_profile": row.get("recipe_profile", ""),
                "recipe": row["recipe"],
                "temporal_pattern": "target_full",
                "target_present_ratio": 1.0,
                "mixture_audio_path": serialize_repo_path(local_mixture_audio_path),
                "target_audio_path": serialize_repo_path(local_target_audio_path),
                "reference_audio_path": serialize_repo_path(reference_audio_path),
                "metadata_path": serialize_repo_path(local_metadata_path),
                "interference_layer_count": local_layers_summary["interference_layer_count"],
                "interference_profile": local_layers_summary["interference_profile"],
                "has_speech_interference": local_layers_summary["has_speech_interference"],
                "has_music_interference": local_layers_summary["has_music_interference"],
                "has_other_interference": local_layers_summary["has_other_interference"],
                "target_transient_presence_minus_mid_db_mean": row.get("target_transient_presence_minus_mid_db_mean"),
                "target_transient_presence_share_mean": row.get("target_transient_presence_share_mean"),
                "target_energy_ratio": local_target_share,
                "interference_energy_ratio": local_interference_energy / max(local_target_energy, 1e-12),
                "target_to_interference_energy_ratio": local_target_to_interference_ratio,
                "target_to_interference_energy_db": safe_log10(local_target_to_interference_ratio),
                "interference_transient_presence_minus_mid_db_mean": row.get(
                    "interference_transient_presence_minus_mid_db_mean"
                ),
                "interference_transient_presence_share_mean": row.get(
                    "interference_transient_presence_share_mean"
                ),
                "target_interference_logspec_cosine": row.get("target_interference_logspec_cosine"),
                "local_window_start_sec": window_start_sec,
                "local_window_duration_sec": window_duration_sec,
                "local_selection_mode": selection["selection_mode"],
                "local_selection_score": float(selection["selection_score"]),
                "local_target_energy_db": safe_log10(local_target_energy),
                "local_interference_energy_db": safe_log10(local_interference_energy),
            }
        )

        selection_mode = str(selection["selection_mode"])
        selection_modes[selection_mode] = selection_modes.get(selection_mode, 0) + 1
        local_target_shares.append(local_target_share)
        local_target_db_values.append(safe_log10(local_target_energy))
        local_interference_db_values.append(safe_log10(local_interference_energy))
        local_target_to_interference_db_values.append(safe_log10(local_target_to_interference_ratio))

    with args.output_manifest.open("w", encoding="utf-8", newline="\n") as fh:
        for row in output_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    args.sample_ids_file.write_text(
        "".join(f"{row['sample_id']}\n" for row in output_rows),
        encoding="utf-8",
        newline="\n",
    )

    summary = {
        "input_manifest": serialize_repo_path(args.input_manifest),
        "output_manifest": serialize_repo_path(args.output_manifest),
        "output_root": serialize_repo_path(args.output_root),
        "sample_ids_file": serialize_repo_path(args.sample_ids_file),
        "window_duration_sec": args.window_duration_sec,
        "window_hop_sec": args.window_hop_sec,
        "min_local_target_share": args.min_local_target_share,
        "max_local_target_share": args.max_local_target_share,
        "selected_count": len(output_rows),
        "selection_mode_counts": selection_modes,
        "local_target_share_mean": (sum(local_target_shares) / len(local_target_shares)) if local_target_shares else None,
        "local_target_energy_db_mean": (
            sum(local_target_db_values) / len(local_target_db_values) if local_target_db_values else None
        ),
        "local_interference_energy_db_mean": (
            sum(local_interference_db_values) / len(local_interference_db_values)
            if local_interference_db_values
            else None
        ),
        "local_target_to_interference_energy_db_mean": (
            sum(local_target_to_interference_db_values) / len(local_target_to_interference_db_values)
            if local_target_to_interference_db_values
            else None
        ),
        "sample_ids": [row["sample_id"] for row in output_rows],
    }
    args.summary_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    main()
