from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parents[2]
SOURCE_RETENTION_SCALE = ["excellent", "good", "fair", "weak", "lost"]
PROBLEM_SEVERITY_SCALE = ["none", "slight", "moderate", "heavy", "extreme"]
DECISION_TAG_EXAMPLES = [
    "better_source_retention",
    "less_interference_leak",
    "steadier_volume",
    "less_artifact",
    "prefer_silence_over_leak",
]
RESERVED_AUDIO_NAMES = ["mixture.wav", "reference.wav", "target.wav"]
EXPORT_TARGET_RMS = 0.12
EXPORT_MAX_PEAK = 0.85


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Merge multiple A/B listening packs into one multi-candidate blind pack.")
    parser.add_argument(
        "--input-pack",
        action="append",
        dest="input_packs",
        type=Path,
        required=True,
        help="Existing listening pack directory. Repeat this flag for multiple packs.",
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--candidate-order",
        nargs="*",
        default=None,
        help="Optional revealed label order, e.g. legacy_stage2 v32 v64.",
    )
    parser.add_argument("--blind-seed", type=int, default=20260324)
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_sheet_rows(pack_dir: Path) -> dict[str, dict[str, str]]:
    csv_path = pack_dir / "listening_sheet.csv"
    if not csv_path.exists():
        return {}
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return {
            row.get("sample_id", "").strip(): row
            for row in reader
            if row.get("sample_id", "").strip()
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sanitize_filename(label: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "_" for char in label.strip())
    return safe.strip("_") or "candidate"


def infer_candidate_sources(summary: dict[str, Any], sample_meta: dict[str, Any]) -> dict[str, str]:
    if "label_a" in summary and "label_b" in summary and "exports" in sample_meta:
        exports = sample_meta["exports"]
        return {
            str(summary["label_a"]): str(exports["estimate_a"]),
            str(summary["label_b"]): str(exports["estimate_b"]),
        }
    if "label_a" in summary and "label_b" in summary and "export_names" in sample_meta:
        export_names = sample_meta["export_names"]
        return {
            str(summary["label_a"]): str(export_names["estimate_a"]),
            str(summary["label_b"]): str(export_names["estimate_b"]),
        }
    raise ValueError("Unsupported pack summary/sample_meta format for merge.")


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    data, sample_rate = sf.read(str(path), dtype="float32", always_2d=False)
    if data.ndim == 2:
        data = data.mean(axis=1)
    return np.ascontiguousarray(data), sample_rate


def save_audio(path: Path, waveform: np.ndarray, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), waveform, sample_rate)


def rms_value(waveform: np.ndarray) -> float:
    if waveform.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(waveform), dtype=np.float64) + 1e-12))


def max_abs_value(waveform: np.ndarray) -> float:
    if waveform.size == 0:
        return 0.0
    return float(np.max(np.abs(waveform)))


def compute_shared_export_gain(tracks: list[np.ndarray]) -> float:
    if not tracks:
        return 1.0
    reference_rms = max(rms_value(tracks[0]), 1e-4)
    gain = EXPORT_TARGET_RMS / reference_rms
    peak = max(max_abs_value(track) for track in tracks)
    if peak > 0.0:
        gain = min(gain, EXPORT_MAX_PEAK / peak)
    return gain


def waveforms_match_up_to_scale(left: np.ndarray, right: np.ndarray) -> bool:
    if left.shape != right.shape:
        return False
    left_peak = max_abs_value(left)
    right_peak = max_abs_value(right)
    if left_peak == 0.0 or right_peak == 0.0:
        return left_peak == right_peak
    return np.allclose(left / left_peak, right / right_peak, atol=1e-4)


def main() -> None:
    args = parse_args()
    input_packs = [path.resolve() for path in args.input_packs]
    if len(input_packs) < 2:
        raise SystemExit("Provide at least two --input-pack directories.")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    blind_rng = random.Random(args.blind_seed)

    pack_summaries: list[dict[str, Any]] = []
    pack_sheet_rows: list[dict[str, dict[str, str]]] = []
    sample_ids_reference: list[str] | None = None
    discovered_labels: list[str] = []

    for pack_dir in input_packs:
        summary_path = pack_dir / "summary.json"
        if not summary_path.exists():
            raise FileNotFoundError(f"Missing summary.json in {pack_dir}")
        summary = load_json(summary_path)
        sheet_rows = load_sheet_rows(pack_dir)
        sample_dirs = sorted(path.name for path in pack_dir.iterdir() if path.is_dir() and (path / "sample_meta.json").exists())
        if sample_ids_reference is None:
            sample_ids_reference = sample_dirs
        elif sample_dirs != sample_ids_reference:
            raise ValueError("Input packs do not contain the same sample set/order.")
        for label in [summary.get("label_a"), summary.get("label_b")]:
            if isinstance(label, str) and label not in discovered_labels:
                discovered_labels.append(label)
        pack_summaries.append(summary)
        pack_sheet_rows.append(sheet_rows)

    if sample_ids_reference is None:
        raise ValueError("No samples found in input packs.")

    if args.candidate_order is not None and args.candidate_order:
        candidate_labels = list(args.candidate_order)
    else:
        candidate_labels = discovered_labels

    sample_rows: list[dict[str, str]] = []
    blind_mapping_rows: list[dict[str, str]] = []
    merged_samples_summary: list[dict[str, Any]] = []

    for sample_id in sample_ids_reference:
        sample_rate: int | None = None
        sample_reserved_audio: dict[str, np.ndarray] = {}
        merged_label_audio: dict[str, np.ndarray] = {}
        merged_label_meta: dict[str, Any] = {}
        first_note = ""
        first_recipe = ""
        first_pattern = ""
        first_target_present_ratio = ""

        for pack_dir, summary, sheet_rows in zip(input_packs, pack_summaries, pack_sheet_rows):
            sample_dir = pack_dir / sample_id
            sample_meta = load_json(sample_dir / "sample_meta.json")
            if not first_note:
                first_note = str(sample_meta.get("note", "")).strip()
            sheet_row = sheet_rows.get(sample_id, {})
            if not first_note:
                first_note = sheet_row.get("note", "").strip()
            first_recipe = first_recipe or sheet_row.get("recipe", "").strip()
            first_pattern = first_pattern or sheet_row.get("temporal_pattern", "").strip()
            first_target_present_ratio = first_target_present_ratio or sheet_row.get("target_present_ratio", "").strip()

            for reserved_name in RESERVED_AUDIO_NAMES:
                reserved_path = sample_dir / reserved_name
                if reserved_path.exists():
                    waveform, reserved_sr = load_audio(reserved_path)
                    if sample_rate is None:
                        sample_rate = reserved_sr
                    elif reserved_sr != sample_rate:
                        raise ValueError(f"Sample rate mismatch in {reserved_path}")
                    existing_waveform = sample_reserved_audio.get(reserved_name)
                    if existing_waveform is None:
                        sample_reserved_audio[reserved_name] = waveform
                    elif not waveforms_match_up_to_scale(existing_waveform, waveform):
                        raise ValueError(f"Conflicting reserved audio for sample {sample_id}: {reserved_name}")

            label_to_audio_name = infer_candidate_sources(summary, sample_meta)
            comparison = sample_meta.get("comparison", {})
            for label, audio_name in label_to_audio_name.items():
                audio_path = sample_dir / audio_name
                if not audio_path.exists():
                    raise FileNotFoundError(f"Missing candidate audio {audio_path}")
                waveform, audio_sr = load_audio(audio_path)
                if sample_rate is None:
                    sample_rate = audio_sr
                elif audio_sr != sample_rate:
                    raise ValueError(f"Sample rate mismatch in {audio_path}")
                existing = merged_label_audio.get(label)
                if existing is not None:
                    if not waveforms_match_up_to_scale(existing, waveform):
                        raise ValueError(f"Conflicting audio for sample {sample_id} label {label}")
                else:
                    merged_label_audio[label] = waveform
                    merged_label_meta[label] = comparison.get(label, {})

        if set(merged_label_audio) != set(candidate_labels):
            missing = sorted(set(candidate_labels) - set(merged_label_audio))
            extra = sorted(set(merged_label_audio) - set(candidate_labels))
            raise ValueError(
                f"Sample {sample_id} candidate mismatch. Missing={missing} Extra={extra}"
            )
        if sample_rate is None:
            raise ValueError(f"No audio found for sample {sample_id}")

        shuffled_labels = list(candidate_labels)
        blind_rng.shuffle(shuffled_labels)
        sample_blind_mapping: dict[str, str] = {"sample_id": sample_id}
        candidate_ids: list[str] = []
        candidate_audio_names: dict[str, str] = {}
        exports: dict[str, str] = {}
        sample_output_dir = args.output_dir / sample_id

        tracks_for_gain = list(sample_reserved_audio.values()) + [merged_label_audio[label] for label in shuffled_labels]
        shared_gain = compute_shared_export_gain(tracks_for_gain)
        for reserved_name, waveform in sample_reserved_audio.items():
            save_audio(sample_output_dir / reserved_name, waveform * shared_gain, sample_rate)

        for index, label in enumerate(shuffled_labels, start=1):
            candidate_id = f"candidate_{index}"
            candidate_ids.append(candidate_id)
            candidate_audio_name = f"{candidate_id}.wav"
            candidate_audio_names[candidate_id] = candidate_audio_name
            exports[candidate_id] = candidate_audio_name
            sample_blind_mapping[candidate_id] = label
            save_audio(sample_output_dir / candidate_audio_name, merged_label_audio[label] * shared_gain, sample_rate)

        sample_rows.append(
            {
                "sample_id": sample_id,
                "recipe": first_recipe,
                "temporal_pattern": first_pattern,
                "target_present_ratio": first_target_present_ratio,
                "candidate_ids_json": json.dumps(candidate_ids, ensure_ascii=False),
                "candidate_audio_names_json": json.dumps(candidate_audio_names, ensure_ascii=False),
                "better_output": "",
                "candidate_ratings_json": json.dumps(
                    {
                        candidate_id: {
                            "source_retention": "",
                            "interference_leak": "",
                            "volume_fluctuation": "",
                            "artifact": "",
                        }
                        for candidate_id in candidate_ids
                    },
                    ensure_ascii=False,
                ),
                "decision_tags": "",
                "note": first_note,
            }
        )
        blind_mapping_rows.append(sample_blind_mapping)
        merged_sample_summary = {
            "sample_id": sample_id,
            "note": first_note,
            "comparison": merged_label_meta,
            "exports": exports,
        }
        if first_recipe:
            merged_sample_summary["recipe"] = first_recipe
        if first_pattern:
            merged_sample_summary["temporal_pattern"] = first_pattern
        if first_target_present_ratio:
            merged_sample_summary["target_present_ratio"] = first_target_present_ratio
        (args.output_dir / sample_id / "sample_meta.json").write_text(
            json.dumps(merged_sample_summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        merged_samples_summary.append(merged_sample_summary)

    sample_rows.sort(key=lambda row: row["sample_id"])
    with (args.output_dir / "listening_sheet.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "sample_id",
                "recipe",
                "temporal_pattern",
                "target_present_ratio",
                "candidate_ids_json",
                "candidate_audio_names_json",
                "better_output",
                "candidate_ratings_json",
                "decision_tags",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(sample_rows)

    (args.output_dir / "blind_key.json").write_text(
        json.dumps(
            {
                "pack_format": "multi_candidate_v1",
                "blind_seed": args.blind_seed,
                "candidate_labels": candidate_labels,
                "mapping": blind_mapping_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (args.output_dir / "listening_rubric.json").write_text(
        json.dumps(
            {
                "pack_format": "multi_candidate_v1",
                "better_output_choices": [f"candidate_{index + 1}" for index in range(len(candidate_labels))] + ["tie", "uncertain"],
                "source_retention_scale": SOURCE_RETENTION_SCALE,
                "problem_severity_scale": PROBLEM_SEVERITY_SCALE,
                "decision_tag_examples": DECISION_TAG_EXAMPLES,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    (args.output_dir / "summary.json").write_text(
        json.dumps(
            {
                "pack_format": "multi_candidate_v1",
                "num_input_packs": len(input_packs),
                "input_packs": [serialize_repo_path(path) for path in input_packs],
                "candidate_labels": candidate_labels,
                "blind_seed": args.blind_seed,
                "num_exported_samples": len(sample_rows),
                "samples": merged_samples_summary,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
        newline="\n",
    )

    readme_lines = [
        "# Multi-Candidate Blind Listening Pack",
        "",
        f"- input packs: {', '.join(f'`{serialize_repo_path(path)}`' for path in input_packs)}",
        f"- candidate labels: {', '.join(f'`{label}`' for label in candidate_labels)}",
        "",
        "Use the GUI with this directory and listen to `candidate_1.wav`, `candidate_2.wav`, `candidate_3.wav`, ...",
        "Reserved files like `mixture.wav`, `reference.wav`, and `target.wav` are preserved when present in the input packs.",
        "Merged export audio is written in mono so mixture/reference/target/candidates share the same channel layout.",
        "Do not open `blind_key.json` until scoring is complete.",
        "",
    ]
    (args.output_dir / "README.md").write_text(
        "\n".join(readme_lines),
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "output_dir": serialize_repo_path(args.output_dir),
                "candidate_labels": candidate_labels,
                "num_exported_samples": len(sample_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
