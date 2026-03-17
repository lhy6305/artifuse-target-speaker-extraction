from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = ROOT / "data" / "manifests"
CURATED_ROOT = ROOT / "data" / "curated" / "genshin_clean_subset"
SOURCE_MANIFEST_PATH = MANIFEST_DIR / "speech_interference_clean_pool.jsonl"
SNAPSHOT_MANIFEST_PATH = MANIFEST_DIR / "speech_interference_clean_pool.upstream_snapshot.jsonl"
SUMMARY_PATH = CURATED_ROOT / "subset_summary.json"
CURATED_SOURCE_LABEL = "data/curated/genshin_clean_subset"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Materialize the selected Genshin clean speech subset into a curated "
            "directory and rewrite the clean manifest to point there."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("hardlink", "copy", "move"),
        default="hardlink",
        help="How to materialize files into the curated directory.",
    )
    parser.add_argument(
        "--force-clean",
        action="store_true",
        help="Remove the existing curated subset directory before rewriting it.",
    )
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


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def materialize_file(src: Path, dst: Path, mode: str) -> None:
    ensure_parent(dst)
    if dst.exists():
        return
    if mode == "hardlink":
        os.link(src, dst)
        return
    if mode == "copy":
        shutil.copy2(src, dst)
        return
    if mode == "move":
        shutil.move(str(src), str(dst))
        return
    raise ValueError(f"Unsupported mode: {mode}")


def maybe_reset_curated_root(force_clean: bool) -> None:
    if force_clean and CURATED_ROOT.exists():
        shutil.rmtree(CURATED_ROOT)
    CURATED_ROOT.mkdir(parents=True, exist_ok=True)


def already_curated(rows: list[dict[str, Any]]) -> bool:
    return all(
        str(row.get("audio_path", "")).startswith(f"{CURATED_SOURCE_LABEL}/")
        for row in rows
    )


def byte_size(path: Path) -> int:
    return path.stat().st_size


def main() -> None:
    args = parse_args()
    rows = load_jsonl(SOURCE_MANIFEST_PATH)
    if not rows:
        raise RuntimeError("Clean interference manifest is empty.")

    if already_curated(rows) and not args.force_clean:
        print(
            json.dumps(
                {
                    "status": "already_curated",
                    "manifest_path": relpath(SOURCE_MANIFEST_PATH),
                    "curated_root": relpath(CURATED_ROOT),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    maybe_reset_curated_root(force_clean=args.force_clean)

    upstream_rows = rows
    write_jsonl(SNAPSHOT_MANIFEST_PATH, upstream_rows)

    curated_rows: list[dict[str, Any]] = []
    total_audio_bytes = 0
    total_text_bytes = 0
    speaker_ids: set[str] = set()

    for row in upstream_rows:
        speaker_id = row["speaker_id"]
        speaker_ids.add(speaker_id)

        src_audio_path = ROOT / row["audio_path"]
        src_text_path = ROOT / row["text_path"]
        dst_audio_path = CURATED_ROOT / speaker_id / src_audio_path.name
        dst_text_path = CURATED_ROOT / speaker_id / src_text_path.name

        total_audio_bytes += byte_size(src_audio_path)
        total_text_bytes += byte_size(src_text_path)

        materialize_file(src_audio_path, dst_audio_path, mode=args.mode)
        materialize_file(src_text_path, dst_text_path, mode=args.mode)

        curated_row = dict(row)
        curated_row["audio_path"] = relpath(dst_audio_path)
        curated_row["text_path"] = relpath(dst_text_path)
        curated_row["source"] = CURATED_SOURCE_LABEL
        curated_row["upstream_audio_path"] = row["audio_path"]
        curated_row["upstream_text_path"] = row["text_path"]
        curated_row["selection_reason"] = (
            f"{row['selection_reason']};materialized_scattered_subset"
        )
        curated_rows.append(curated_row)

    write_jsonl(SOURCE_MANIFEST_PATH, curated_rows)
    write_json(
        SUMMARY_PATH,
        {
            "status": "materialized",
            "mode": args.mode,
            "item_count": len(curated_rows),
            "speaker_count": len(speaker_ids),
            "curated_root": relpath(CURATED_ROOT),
            "rewritten_manifest": relpath(SOURCE_MANIFEST_PATH),
            "upstream_snapshot_manifest": relpath(SNAPSHOT_MANIFEST_PATH),
            "total_audio_bytes": total_audio_bytes,
            "total_text_bytes": total_text_bytes,
        },
    )

    print(
        json.dumps(
            {
                "status": "materialized",
                "mode": args.mode,
                "item_count": len(curated_rows),
                "speaker_count": len(speaker_ids),
                "curated_root": relpath(CURATED_ROOT),
                "rewritten_manifest": relpath(SOURCE_MANIFEST_PATH),
                "upstream_snapshot_manifest": relpath(SNAPSHOT_MANIFEST_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
