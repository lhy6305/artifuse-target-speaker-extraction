from __future__ import annotations

import argparse
import csv
import json
import pickle
import random
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import torchaudio


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.data.synthetic_dataset import load_json, load_jsonl
from tse_prefix.models import STFTMaskBaseline
from tse_prefix.pipeline import masked_sisdr

BETTER_OUTPUT_CHOICES = ["file_a", "file_b", "tie", "uncertain"]
SOURCE_RETENTION_SCALE = ["excellent", "good", "fair", "weak", "lost"]
PROBLEM_SEVERITY_SCALE = ["none", "slight", "moderate", "heavy", "extreme"]
DECISION_TAG_EXAMPLES = [
    "better_source_retention",
    "less_interference_leak",
    "steadier_volume",
    "less_artifact",
    "prefer_silence_over_leak",
]
EXPORT_TARGET_RMS = 0.12
EXPORT_MAX_PEAK = 0.85


@dataclass(frozen=True)
class CandidateSample:
    sample_id: str
    recipe: str
    temporal_pattern: str
    target_present_ratio: float
    mixture_audio_path: Path
    target_audio_path: Path
    reference_audio_path: Path
    metadata_path: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export an A/B listening pack for two checkpoints.")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "val_manifest.jsonl",
    )
    parser.add_argument(
        "--checkpoint-a",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--checkpoint-b",
        type=Path,
        required=True,
    )
    parser.add_argument("--label-a", type=str, default="model_a")
    parser.add_argument("--label-b", type=str, default="model_b")
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
    )
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--max-samples", type=int, default=12)
    parser.add_argument(
        "--focus-recipes",
        nargs="*",
        default=["target_clean_speech", "target_clean_plus_music"],
    )
    parser.add_argument(
        "--stable-count",
        type=int,
        default=4,
        help="How many near-tie samples to keep in addition to improvements/regressions.",
    )
    parser.add_argument(
        "--blind",
        action="store_true",
        help="Export model outputs as candidate_a/candidate_b and keep the mapping in a separate file.",
    )
    parser.add_argument(
        "--blind-seed",
        type=int,
        default=20260316,
        help="Seed used when assigning blind candidate labels.",
    )
    return parser.parse_args()


def align_waveforms(
    prediction: torch.Tensor,
    target: torch.Tensor,
    lengths: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    common_length = min(prediction.shape[-1], target.shape[-1])
    clipped_lengths = torch.clamp(lengths, max=common_length)
    return (
        prediction[..., :common_length],
        target[..., :common_length],
        clipped_lengths,
    )


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def write_utf8_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_checkpoint(path: Path, device: torch.device) -> dict:
    try:
        return torch.load(path, map_location=device, weights_only=True)
    except pickle.UnpicklingError:
        return torch.load(path, map_location=device, weights_only=False)


def resolve_model_config(checkpoint: dict) -> dict[str, Any]:
    model_config = dict(checkpoint.get("model_config", {}))
    if "conditioning_mode" not in model_config:
        state_dict = checkpoint["model_state_dict"]
        if "condition_proj.weight" in state_dict:
            model_config["conditioning_mode"] = "legacy_bias"
    return model_config


def build_model_from_checkpoint(checkpoint_path: Path, device: torch.device) -> tuple[STFTMaskBaseline, dict[str, Any], dict[str, Any]]:
    checkpoint = load_checkpoint(checkpoint_path, device)
    model_config = resolve_model_config(checkpoint)
    model = STFTMaskBaseline(**model_config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, model_config, checkpoint.get("loss_config", {})


def save_audio(path: Path, waveform: torch.Tensor, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(path), waveform.detach().cpu().unsqueeze(0), sample_rate)


def load_audio_mono(path: Path, sample_rate: int) -> torch.Tensor:
    waveform, sr = torchaudio.load(str(path))
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != sample_rate:
        waveform = torchaudio.functional.resample(waveform, sr, sample_rate)
    return waveform.squeeze(0).contiguous()


def rms_value(waveform: torch.Tensor) -> float:
    return float(torch.sqrt(torch.mean(torch.square(waveform)) + 1e-12).item())


def max_abs_value(waveform: torch.Tensor) -> float:
    return float(torch.max(torch.abs(waveform)).item())


def compute_shared_export_gain(tracks: list[torch.Tensor]) -> float:
    reference_rms = max(rms_value(tracks[0]), 1e-4)
    gain = EXPORT_TARGET_RMS / reference_rms
    peak = max(max_abs_value(track) for track in tracks)
    if peak > 0.0:
        gain = min(gain, EXPORT_MAX_PEAK / peak)
    return gain


def infer_manifest_defaults(row: dict[str, Any], root: Path) -> tuple[str, str, float, Path]:
    mixture_audio_path = root / row["mixture_audio_path"]
    metadata_path = root / row.get("metadata_path", mixture_audio_path.parent / "sample_meta.json")
    recipe = row.get("recipe")
    temporal_pattern = row.get("temporal_pattern")
    target_present_ratio = row.get("target_present_ratio")

    if metadata_path.exists():
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        scenario = str(metadata.get("scenario", "near_real"))
        has_target_component = any(
            str(component.get("kind", "")).startswith("target")
            for component in metadata.get("components", [])
            if isinstance(component, dict)
        )
        if recipe is None:
            recipe = scenario
        if temporal_pattern is None:
            temporal_pattern = "target_present" if has_target_component else "target_absent"
        if target_present_ratio is None:
            target_present_ratio = 1.0 if has_target_component else 0.0

    if recipe is None:
        recipe = "near_real"
    if temporal_pattern is None:
        temporal_pattern = "unknown"
    if target_present_ratio is None:
        target_present_ratio = 0.0
    return str(recipe), str(temporal_pattern), float(target_present_ratio), metadata_path


def read_manifest_samples(manifest_path: Path) -> list[CandidateSample]:
    root = manifest_path.resolve().parents[2]
    rows = load_jsonl(manifest_path)
    samples: list[CandidateSample] = []
    for row in rows:
        recipe, temporal_pattern, target_present_ratio, metadata_path = infer_manifest_defaults(row, root)
        samples.append(
            CandidateSample(
                sample_id=row["sample_id"],
                recipe=recipe,
                temporal_pattern=temporal_pattern,
                target_present_ratio=target_present_ratio,
                mixture_audio_path=root / row["mixture_audio_path"],
                target_audio_path=root / row["target_audio_path"],
                reference_audio_path=root / row["reference_audio_path"],
                metadata_path=metadata_path,
            )
        )
    return samples


def build_listening_sheet_fieldnames() -> list[str]:
    return [
        "sample_id",
        "recipe",
        "temporal_pattern",
        "target_present_ratio",
        "file_a_name",
        "file_b_name",
        "better_output",
        "file_a_source_retention",
        "file_b_source_retention",
        "file_a_interference_leak",
        "file_b_interference_leak",
        "file_a_volume_fluctuation",
        "file_b_volume_fluctuation",
        "file_a_artifact",
        "file_b_artifact",
        "decision_tags",
        "note",
    ]


def export_sample_bundle(
    output_dir: Path,
    sample: CandidateSample,
    mixture: torch.Tensor,
    target: torch.Tensor,
    reference: torch.Tensor,
    estimate_a: torch.Tensor,
    estimate_b: torch.Tensor,
    metrics: dict[str, Any],
    sample_rate: int,
    export_name_a: str,
    export_name_b: str,
) -> None:
    sample_dir = output_dir / sample.sample_id
    sample_dir.mkdir(parents=True, exist_ok=True)
    gain = compute_shared_export_gain([mixture, target, reference, estimate_a, estimate_b])
    save_audio(sample_dir / "mixture.wav", mixture * gain, sample_rate)
    save_audio(sample_dir / "target.wav", target * gain, sample_rate)
    save_audio(sample_dir / "reference.wav", reference * gain, sample_rate)
    save_audio(sample_dir / f"{export_name_a}.wav", estimate_a * gain, sample_rate)
    save_audio(sample_dir / f"{export_name_b}.wav", estimate_b * gain, sample_rate)
    write_utf8_text(
        sample_dir / "sample_meta.json",
        json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
    )


def choose_listening_set(
    rows: list[dict[str, Any]],
    max_samples: int,
    stable_count: int,
) -> list[dict[str, Any]]:
    if len(rows) <= max_samples:
        return rows

    improvement_count = max(1, (max_samples - stable_count) // 2)
    regression_count = max(1, max_samples - stable_count - improvement_count)

    sorted_rows = sorted(rows, key=lambda row: row["sisdr_delta_db"], reverse=True)
    selected: list[dict[str, Any]] = []
    seen: set[str] = set()

    for row in sorted_rows[:improvement_count]:
        selected.append(row)
        seen.add(row["sample_id"])

    for row in sorted_rows[::-1]:
        if len([r for r in selected if r["sample_id"] == row["sample_id"]]) > 0:
            continue
        selected.append(row)
        seen.add(row["sample_id"])
        if len(selected) >= improvement_count + regression_count:
            break

    stable_rows = sorted(rows, key=lambda row: abs(row["sisdr_delta_db"]))
    for row in stable_rows:
        if row["sample_id"] in seen:
            continue
        selected.append(row)
        seen.add(row["sample_id"])
        if len(selected) >= max_samples:
            break

    return selected[:max_samples]


def main() -> None:
    args = parse_args()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    blind_rng = random.Random(args.blind_seed)

    manifest_samples = read_manifest_samples(args.manifest)
    manifest_by_id = {sample.sample_id: sample for sample in manifest_samples}
    model_a, model_config_a, loss_config_a = build_model_from_checkpoint(args.checkpoint_a, device)
    model_b, model_config_b, loss_config_b = build_model_from_checkpoint(args.checkpoint_b, device)

    focus_recipes = set(args.focus_recipes)
    candidates: list[dict[str, Any]] = []
    recipe_counter: dict[str, int] = defaultdict(int)

    with torch.no_grad():
        for sample in manifest_samples:
            if focus_recipes and sample.recipe not in focus_recipes:
                continue

            mixture_waveform = load_audio_mono(sample.mixture_audio_path, args.sample_rate)
            target_waveform = load_audio_mono(sample.target_audio_path, args.sample_rate)
            reference_waveform = load_audio_mono(sample.reference_audio_path, args.sample_rate)

            mixture = mixture_waveform.unsqueeze(0).to(device)
            target = target_waveform.unsqueeze(0).to(device)
            reference = reference_waveform.unsqueeze(0).to(device)
            target_lengths = torch.tensor([target_waveform.shape[-1]], device=device, dtype=torch.long)
            reference_lengths = torch.tensor([reference_waveform.shape[-1]], device=device, dtype=torch.long)
            mixture_lengths = torch.tensor([mixture_waveform.shape[-1]], device=device, dtype=torch.long)

            outputs_a = model_a(
                mixture=mixture,
                mixture_lengths=mixture_lengths,
                reference=reference,
                reference_lengths=reference_lengths,
            )
            outputs_b = model_b(
                mixture=mixture,
                mixture_lengths=mixture_lengths,
                reference=reference,
                reference_lengths=reference_lengths,
            )

            pred_a, tgt, lengths = align_waveforms(outputs_a["estimated_waveform"], target, target_lengths)
            pred_b, _, _ = align_waveforms(outputs_b["estimated_waveform"], target, target_lengths)

            sisdr_a = float(masked_sisdr(pred_a, tgt, lengths).item())
            sisdr_b = float(masked_sisdr(pred_b, tgt, lengths).item())
            waveform_l1_a = float(torch.mean(torch.abs(pred_a - tgt)).item())
            waveform_l1_b = float(torch.mean(torch.abs(pred_b - tgt)).item())

            candidates.append(
                {
                    "sample_id": sample.sample_id,
                    "recipe": sample.recipe,
                    "temporal_pattern": sample.temporal_pattern,
                    "target_present_ratio": sample.target_present_ratio,
                    "sisdr_a_db": sisdr_a,
                    "sisdr_b_db": sisdr_b,
                    "sisdr_delta_db": sisdr_b - sisdr_a,
                    "waveform_l1_a": waveform_l1_a,
                    "waveform_l1_b": waveform_l1_b,
                    "waveform_l1_delta": waveform_l1_b - waveform_l1_a,
                    "mixture": mixture_waveform.cpu(),
                    "target": target_waveform.cpu(),
                    "reference": reference_waveform.cpu(),
                    "estimate_a": pred_a[0, : lengths[0].item()].cpu(),
                    "estimate_b": pred_b[0, : lengths[0].item()].cpu(),
                    "metadata_path": serialize_repo_path(sample.metadata_path),
                }
            )
            recipe_counter[sample.recipe] += 1

    selected_rows = choose_listening_set(
        candidates,
        max_samples=args.max_samples,
        stable_count=args.stable_count,
    )

    summary_rows: list[dict[str, Any]] = []
    blind_rows: list[dict[str, Any]] = []
    score_sheet_rows: list[dict[str, Any]] = []
    for row in selected_rows:
        sample = manifest_by_id[row["sample_id"]]
        source_metadata = load_json(sample.metadata_path) if sample.metadata_path.exists() else {}
        if args.blind:
            if blind_rng.random() < 0.5:
                export_name_a = "candidate_a"
                export_name_b = "candidate_b"
                blind_mapping = {
                    "candidate_a": args.label_a,
                    "candidate_b": args.label_b,
                }
            else:
                export_name_a = "candidate_b"
                export_name_b = "candidate_a"
                blind_mapping = {
                    "candidate_a": args.label_b,
                    "candidate_b": args.label_a,
                }
        else:
            export_name_a = args.label_a
            export_name_b = args.label_b
            blind_mapping = {
                export_name_a: args.label_a,
                export_name_b: args.label_b,
            }
        file_a_name = "candidate_a.wav" if args.blind else f"{args.label_a}.wav"
        file_b_name = "candidate_b.wav" if args.blind else f"{args.label_b}.wav"

        export_metrics = {
            "sample_id": row["sample_id"],
            "recipe": row["recipe"],
            "temporal_pattern": row["temporal_pattern"],
            "target_present_ratio": row["target_present_ratio"],
            "scenario": str(source_metadata.get("scenario", "")),
            "note": str(source_metadata.get("note", "")),
            "audio_layout": str(source_metadata.get("audio_layout", "mono")),
            "mixture_audio_path": serialize_repo_path(sample.mixture_audio_path),
            "target_audio_path": serialize_repo_path(sample.target_audio_path),
            "reference_audio_path": serialize_repo_path(sample.reference_audio_path),
            "metadata_path": row["metadata_path"],
            "comparison": {
                args.label_a: {
                    "sisdr_db": row["sisdr_a_db"],
                    "waveform_l1": row["waveform_l1_a"],
                    "checkpoint": serialize_repo_path(args.checkpoint_a),
                    "model_config": model_config_a,
                    "loss_config": loss_config_a,
                },
                args.label_b: {
                    "sisdr_db": row["sisdr_b_db"],
                    "waveform_l1": row["waveform_l1_b"],
                    "checkpoint": serialize_repo_path(args.checkpoint_b),
                    "model_config": model_config_b,
                    "loss_config": loss_config_b,
                },
            },
            "delta": {
                "sisdr_db": row["sisdr_delta_db"],
                "waveform_l1": row["waveform_l1_delta"],
            },
            "export_names": {
                "estimate_a": f"{export_name_a}.wav",
                "estimate_b": f"{export_name_b}.wav",
            },
            "exports": {
                "estimate_a": f"{export_name_a}.wav",
                "estimate_b": f"{export_name_b}.wav",
            },
        }
        export_sample_bundle(
            output_dir=args.output_dir,
            sample=sample,
            mixture=row["mixture"],
            target=row["target"],
            reference=row["reference"],
            estimate_a=row["estimate_a"],
            estimate_b=row["estimate_b"],
            metrics=export_metrics,
            sample_rate=args.sample_rate,
            export_name_a=export_name_a,
            export_name_b=export_name_b,
        )
        summary_rows.append(export_metrics)
        blind_rows.append(
            {
                "sample_id": row["sample_id"],
                "candidate_a": blind_mapping.get("candidate_a", args.label_a),
                "candidate_b": blind_mapping.get("candidate_b", args.label_b),
            }
        )
        score_sheet_rows.append(
            {
                "sample_id": row["sample_id"],
                "recipe": row["recipe"],
                "temporal_pattern": row["temporal_pattern"],
                "target_present_ratio": row["target_present_ratio"],
                "file_a_name": file_a_name,
                "file_b_name": file_b_name,
                "better_output": "",
                "file_a_source_retention": "",
                "file_b_source_retention": "",
                "file_a_interference_leak": "",
                "file_b_interference_leak": "",
                "file_a_volume_fluctuation": "",
                "file_b_volume_fluctuation": "",
                "file_a_artifact": "",
                "file_b_artifact": "",
                "decision_tags": "",
                "note": "",
            }
        )
    score_sheet_rows.sort(key=lambda row: row["sample_id"])

    summary = {
        "manifest": serialize_repo_path(args.manifest),
        "checkpoint_a": serialize_repo_path(args.checkpoint_a),
        "checkpoint_b": serialize_repo_path(args.checkpoint_b),
        "label_a": args.label_a,
        "label_b": args.label_b,
        "focus_recipes": sorted(focus_recipes),
        "max_samples": args.max_samples,
        "stable_count": args.stable_count,
        "num_candidate_samples": len(candidates),
        "num_exported_samples": len(summary_rows),
        "exported_samples": summary_rows,
    }
    write_utf8_text(
        args.output_dir / "summary.json",
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    )
    with (args.output_dir / "listening_sheet.csv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=build_listening_sheet_fieldnames(),
        )
        writer.writeheader()
        writer.writerows(score_sheet_rows)

    write_utf8_text(
        args.output_dir / "listening_rubric.json",
        json.dumps(
            {
                "better_output_choices": BETTER_OUTPUT_CHOICES,
                "source_retention_scale": SOURCE_RETENTION_SCALE,
                "problem_severity_scale": PROBLEM_SEVERITY_SCALE,
                "decision_tag_examples": DECISION_TAG_EXAMPLES,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
    )

    if args.blind:
        write_utf8_text(
            args.output_dir / "blind_key.json",
            json.dumps(
                {
                    "label_a": args.label_a,
                    "label_b": args.label_b,
                    "blind_seed": args.blind_seed,
                    "mapping": blind_rows,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
        )

    export_file_a = args.label_a if not args.blind else "candidate_a"
    export_file_b = args.label_b if not args.blind else "candidate_b"

    readme_lines = [
        "# A/B Listening Pack",
        "",
        f"- manifest: `{serialize_repo_path(args.manifest)}`",
        f"- A: `{args.label_a}` -> `{serialize_repo_path(args.checkpoint_a)}`",
        f"- B: `{args.label_b}` -> `{serialize_repo_path(args.checkpoint_b)}`",
        f"- focus_recipes: `{', '.join(sorted(focus_recipes))}`",
        "",
        "Each sample directory contains:",
        "",
        "- `mixture.wav`",
        "- `target.wav`",
        "- `reference.wav`",
        f"- `{export_file_a}.wav`",
        f"- `{export_file_b}.wav`",
        "- `sample_meta.json`",
        "- top-level `listening_sheet.csv`",
        "- top-level `listening_rubric.json`",
        "",
        "Suggested listening order:",
        "",
        "1. `mixture.wav`",
        "2. `reference.wav`",
        f"3. `{export_file_a}.wav`",
        f"4. `{export_file_b}.wav`",
        "5. `target.wav`",
        "",
        "Use `summary.json` to see which samples are strongest improvements, regressions, or near ties.",
        "",
        "Listening sheet rubric:",
        "",
        "- `better_output`: `file_a` / `file_b` / `tie` / `uncertain`",
        "- `file_*_source_retention`: choose from `excellent, good, fair, weak, lost`",
        "- `file_*_interference_leak`: choose from `none, slight, moderate, heavy, extreme`",
        "- `file_*_volume_fluctuation`: choose from `none, slight, moderate, heavy, extreme`",
        "- `file_*_artifact`: choose from `none, slight, moderate, heavy, extreme`",
        "- `decision_tags`: optional semicolon-separated tags, e.g. `better_source_retention;less_interference_leak`",
        "- all files in one sample folder share the same safety gain, so playback is more stable while relative A/B level differences are preserved",
        "",
    ]
    if args.blind:
        readme_lines.extend(
            [
                "Blind mode is enabled:",
                "",
                "- listen using `candidate_a.wav` / `candidate_b.wav` only",
                "- record your choice in `listening_sheet.csv`",
                "- reveal model identity later via `blind_key.json`",
                "",
            ]
        )
    write_utf8_text(
        args.output_dir / "README.md",
        "\n".join(readme_lines),
    )

    print(
        json.dumps(
            {
                "num_candidate_samples": len(candidates),
                "num_exported_samples": len(summary_rows),
                "output_dir": serialize_repo_path(args.output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
