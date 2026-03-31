from __future__ import annotations

import argparse
import csv
import json
import pickle
import random
import sys
from pathlib import Path
from typing import Any

import torch
import torchaudio


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from tse_prefix.models import STFTMaskBaseline
from tse_prefix.data.synthetic_dataset import compute_local_proxy_intervals, load_json

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export A/B inference results for arbitrary mixture/reference pairs."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--checkpoint-a", type=Path, required=True)
    parser.add_argument("--checkpoint-b", type=Path, required=True)
    parser.add_argument("--label-a", type=str, default="model_a")
    parser.add_argument("--label-b", type=str, default="model_b")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--sample-rate", type=int, default=16000)
    parser.add_argument("--blind", action="store_true")
    parser.add_argument("--blind-seed", type=int, default=20260316)
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


def build_model_from_checkpoint(path: Path, device: torch.device) -> tuple[STFTMaskBaseline, dict[str, Any], dict[str, Any]]:
    checkpoint = load_checkpoint(path, device)
    model_config = resolve_model_config(checkpoint)
    model = STFTMaskBaseline(**model_config).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, model_config, checkpoint.get("loss_config", {})


def load_audio_mono(path: Path, sample_rate: int) -> torch.Tensor:
    waveform, sr = torchaudio.load(str(path))
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    if sr != sample_rate:
        waveform = torchaudio.functional.resample(waveform, sr, sample_rate)
    return waveform.squeeze(0).contiguous()


def save_audio(path: Path, waveform: torch.Tensor, sample_rate: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torchaudio.save(str(path), waveform.detach().cpu().unsqueeze(0), sample_rate)


def resolve_optional_target_path(row: dict[str, Any]) -> Path | None:
    target_audio_raw = str(row.get("target_audio_path", "")).strip()
    if target_audio_raw:
        target_path = ROOT / target_audio_raw
        if target_path.exists():
            return target_path
    mixture_audio_raw = str(row.get("mixture_audio_path", "")).strip()
    if not mixture_audio_raw:
        return None
    sibling_target = (ROOT / mixture_audio_raw).parent / "target.wav"
    if sibling_target.exists():
        return sibling_target
    return None


def resolve_local_proxy_intervals(row: dict[str, Any]) -> list[dict[str, float]]:
    metadata_path_raw = str(row.get("metadata_path", "")).strip()
    if not metadata_path_raw:
        return []
    metadata_path = ROOT / metadata_path_raw
    if not metadata_path.exists():
        return []
    return compute_local_proxy_intervals(load_json(metadata_path))


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


def build_listening_sheet_fieldnames() -> list[str]:
    return [
        "sample_id",
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


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    blind_rng = random.Random(args.blind_seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model_a, model_config_a, loss_config_a = build_model_from_checkpoint(args.checkpoint_a, device)
    model_b, model_config_b, loss_config_b = build_model_from_checkpoint(args.checkpoint_b, device)

    rows = load_jsonl(args.manifest)
    exported_rows: list[dict[str, Any]] = []
    blind_rows: list[dict[str, Any]] = []
    score_sheet_rows: list[dict[str, Any]] = []

    for row in rows:
        sample_id = row["sample_id"]
        mixture_path = ROOT / row["mixture_audio_path"]
        reference_path = ROOT / row["reference_audio_path"]
        target_path = resolve_optional_target_path(row)
        note = row.get("note", "")

        mixture = load_audio_mono(mixture_path, args.sample_rate)
        reference = load_audio_mono(reference_path, args.sample_rate)
        target = load_audio_mono(target_path, args.sample_rate) if target_path is not None else None
        mixture_batch = mixture.unsqueeze(0).to(device)
        reference_batch = reference.unsqueeze(0).to(device)
        mixture_lengths = torch.tensor([mixture.shape[-1]], dtype=torch.long, device=device)
        reference_lengths = torch.tensor([reference.shape[-1]], dtype=torch.long, device=device)
        local_proxy_intervals = [resolve_local_proxy_intervals(row)]

        with torch.no_grad():
            estimate_a = model_a(
                mixture=mixture_batch,
                mixture_lengths=mixture_lengths,
                reference=reference_batch,
                reference_lengths=reference_lengths,
                local_proxy_intervals=local_proxy_intervals,
            )["estimated_waveform"][0, : mixture.shape[-1]].cpu()
            estimate_b = model_b(
                mixture=mixture_batch,
                mixture_lengths=mixture_lengths,
                reference=reference_batch,
                reference_lengths=reference_lengths,
                local_proxy_intervals=local_proxy_intervals,
            )["estimated_waveform"][0, : mixture.shape[-1]].cpu()

        if args.blind:
            if blind_rng.random() < 0.5:
                file_a = "candidate_a.wav"
                file_b = "candidate_b.wav"
                blind_mapping = {"candidate_a": args.label_a, "candidate_b": args.label_b}
            else:
                file_a = "candidate_b.wav"
                file_b = "candidate_a.wav"
                blind_mapping = {"candidate_a": args.label_b, "candidate_b": args.label_a}
        else:
            file_a = f"{args.label_a}.wav"
            file_b = f"{args.label_b}.wav"
            blind_mapping = {args.label_a: args.label_a, args.label_b: args.label_b}
        sheet_file_a = "candidate_a.wav" if args.blind else f"{args.label_a}.wav"
        sheet_file_b = "candidate_b.wav" if args.blind else f"{args.label_b}.wav"

        sample_dir = args.output_dir / sample_id
        sample_dir.mkdir(parents=True, exist_ok=True)
        tracks_for_gain = [mixture, reference, estimate_a, estimate_b]
        if target is not None:
            tracks_for_gain.insert(1, target)
        gain = compute_shared_export_gain(tracks_for_gain)
        save_audio(sample_dir / "mixture.wav", mixture * gain, args.sample_rate)
        save_audio(sample_dir / "reference.wav", reference * gain, args.sample_rate)
        if target is not None:
            save_audio(sample_dir / "target.wav", target * gain, args.sample_rate)
        save_audio(sample_dir / file_a, estimate_a * gain, args.sample_rate)
        save_audio(sample_dir / file_b, estimate_b * gain, args.sample_rate)

        sample_meta = {
            "sample_id": sample_id,
            "mixture_audio_path": row["mixture_audio_path"],
            "reference_audio_path": row["reference_audio_path"],
            "audio_layout": "mono",
            "note": note,
            "exports": {
                "estimate_a": file_a,
                "estimate_b": file_b,
            },
            "comparison": {
                args.label_a: {
                    "checkpoint": serialize_repo_path(args.checkpoint_a),
                    "model_config": model_config_a,
                    "loss_config": loss_config_a,
                },
                args.label_b: {
                    "checkpoint": serialize_repo_path(args.checkpoint_b),
                    "model_config": model_config_b,
                    "loss_config": loss_config_b,
                },
            },
        }
        if target_path is not None:
            sample_meta["target_audio_path"] = serialize_repo_path(target_path)
        write_utf8_text(
            sample_dir / "sample_meta.json",
            json.dumps(sample_meta, ensure_ascii=False, indent=2) + "\n",
        )

        exported_rows.append(sample_meta)
        blind_rows.append({"sample_id": sample_id, **blind_mapping})
        score_sheet_rows.append(
            {
                "sample_id": sample_id,
                "file_a_name": sheet_file_a,
                "file_b_name": sheet_file_b,
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
                "note": note,
            }
        )
    score_sheet_rows.sort(key=lambda row: row["sample_id"])

    summary = {
        "manifest": serialize_repo_path(args.manifest),
        "checkpoint_a": serialize_repo_path(args.checkpoint_a),
        "checkpoint_b": serialize_repo_path(args.checkpoint_b),
        "label_a": args.label_a,
        "label_b": args.label_b,
        "blind": args.blind,
        "num_exported_samples": len(exported_rows),
        "samples": exported_rows,
    }
    write_utf8_text(
        args.output_dir / "summary.json",
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
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

    template_lines = [
        "# Arbitrary Pair A/B Pack",
        "",
        "Manifest row example:",
        "",
        '{"sample_id":"real_0001","mixture_audio_path":"data/references/real_eval/real_0001/mixture.wav","target_audio_path":"data/references/real_eval/real_0001/target.wav","reference_audio_path":"data/references/real_eval/real_0001/reference.wav","note":"optional"}',
        "",
        "Each sample directory contains mono mixture/reference, optional mono target.wav, and two mono model outputs.",
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
        "- export audio is always downmixed to mono before scoring, so mixture/reference/target/candidates share the same channel layout",
        "",
    ]
    write_utf8_text(
        args.output_dir / "README.md",
        "\n".join(template_lines),
    )

    print(
        json.dumps(
            {
                "num_exported_samples": len(exported_rows),
                "output_dir": serialize_repo_path(args.output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
