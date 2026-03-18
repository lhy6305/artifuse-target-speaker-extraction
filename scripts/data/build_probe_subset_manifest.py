from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a filtered subset manifest from an existing probe manifest by reading per-sample metadata."
    )
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--anchor-ids", nargs="*", default=[])
    parser.add_argument("--speech-families", nargs="*", default=[])
    parser.add_argument("--speech-clip-tags", nargs="*", default=[])
    parser.add_argument("--recipes", nargs="*", default=[])
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


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def main() -> None:
    args = parse_args()
    anchor_ids = set(args.anchor_ids)
    speech_families = set(args.speech_families)
    speech_clip_tags = set(args.speech_clip_tags)
    recipes = set(args.recipes)

    input_rows = load_jsonl(args.input_manifest)
    selected_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []

    for row in input_rows:
        metadata = load_json(ROOT / str(row["metadata_path"]))
        if anchor_ids and str(metadata.get("near_real_anchor_sample_id", "")) not in anchor_ids:
            continue
        if speech_families and str(metadata.get("speech_family", "")) not in speech_families:
            continue
        if speech_clip_tags and str(metadata.get("speech_clip_tag", "")) not in speech_clip_tags:
            continue
        if recipes and str(row.get("recipe", "")) not in recipes:
            continue

        selected_rows.append(row)
        summary_rows.append(
            {
                "sample_id": str(row["sample_id"]),
                "anchor_id": str(metadata.get("near_real_anchor_sample_id", "")),
                "speech_family": str(metadata.get("speech_family", "")),
                "speech_clip_tag": str(metadata.get("speech_clip_tag", "")),
                "recipe": str(row.get("recipe", "")),
            }
        )

    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output_manifest.open("w", encoding="utf-8", newline="\n") as fh:
        for row in selected_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(
        json.dumps(
            {
                "input_manifest": serialize_repo_path(args.input_manifest),
                "output_manifest": serialize_repo_path(args.output_manifest),
                "selected_count": len(selected_rows),
                "filters": {
                    "anchor_ids": sorted(anchor_ids),
                    "speech_families": sorted(speech_families),
                    "speech_clip_tags": sorted(speech_clip_tags),
                    "recipes": sorted(recipes),
                },
                "samples": summary_rows,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
