from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import soundfile as sf


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit listening-pack sample folders for channel-layout consistency and required assets."
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--require-target", action="store_true")
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def inspect_audio(path: Path) -> dict[str, Any]:
    info = sf.info(str(path))
    return {
        "path": serialize_repo_path(path),
        "samplerate": int(info.samplerate),
        "channels": int(info.channels),
        "frames": int(info.frames),
        "duration_sec": float(info.duration),
        "is_mono": int(info.channels) == 1,
    }


def main() -> None:
    args = parse_args()
    sample_dirs = sorted(
        path for path in args.pack_dir.iterdir() if path.is_dir() and (path / "sample_meta.json").exists()
    )
    if not sample_dirs:
        raise SystemExit(f"No sample directories with sample_meta.json found in {args.pack_dir}")

    sample_reports: list[dict[str, Any]] = []
    samples_without_target: list[str] = []
    non_mono_files: list[dict[str, Any]] = []

    for sample_dir in sample_dirs:
        audio_reports: dict[str, Any] = {}
        for wav_path in sorted(sample_dir.glob("*.wav")):
            report = inspect_audio(wav_path)
            audio_reports[wav_path.name] = report
            if not report["is_mono"]:
                non_mono_files.append(
                    {
                        "sample_id": sample_dir.name,
                        "file_name": wav_path.name,
                        "channels": report["channels"],
                    }
                )
        has_target = "target.wav" in audio_reports
        if not has_target:
            samples_without_target.append(sample_dir.name)
        sample_reports.append(
            {
                "sample_id": sample_dir.name,
                "has_target": has_target,
                "audio_files": audio_reports,
            }
        )

    output = {
        "pack_dir": serialize_repo_path(args.pack_dir),
        "require_target": args.require_target,
        "num_samples": len(sample_reports),
        "all_mono": len(non_mono_files) == 0,
        "all_have_target": len(samples_without_target) == 0,
        "missing_target_samples": samples_without_target,
        "non_mono_files": non_mono_files,
        "samples": sample_reports,
    }

    output_json = args.output_json or (args.pack_dir / "asset_audit_summary.json")
    output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "pack_dir": serialize_repo_path(args.pack_dir),
                "all_mono": output["all_mono"],
                "all_have_target": output["all_have_target"],
                "missing_target_count": len(samples_without_target),
                "non_mono_file_count": len(non_mono_files),
                "output_json": serialize_repo_path(output_json),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
