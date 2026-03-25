from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Filter a JSONL manifest by newline-delimited speaker_id allowlist and "
            "emit a summary JSON alongside the filtered manifest."
        )
    )
    parser.add_argument("--input-manifest", type=Path, required=True)
    parser.add_argument("--allowlist-file", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument(
        "--summary-json",
        type=Path,
        default=None,
        help="Optional output path for a JSON summary. Defaults to <output>.summary.json.",
    )
    return parser.parse_args()


def resolve_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    return ROOT / path


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_allowlist(path: Path) -> list[str]:
    values: list[str] = []
    with path.open("r", encoding="utf-8-sig") as fh:
        for line in fh:
            value = line.strip()
            if not value or value.startswith("#"):
                continue
            values.append(value)
    return values


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


def main() -> None:
    args = parse_args()
    input_manifest = resolve_path(args.input_manifest)
    allowlist_file = resolve_path(args.allowlist_file)
    output_manifest = resolve_path(args.output_manifest)
    summary_json = (
        resolve_path(args.summary_json)
        if args.summary_json is not None
        else output_manifest.with_suffix(".summary.json")
    )

    rows = load_jsonl(input_manifest)
    allowlist = load_allowlist(allowlist_file)
    allowset = set(allowlist)

    selected_rows = [
        row for row in rows if str(row.get("speaker_id", "")).strip() in allowset
    ]

    speaker_counts = Counter(str(row["speaker_id"]) for row in selected_rows)
    missing_speakers = [
        speaker_id for speaker_id in allowlist if speaker_id not in speaker_counts
    ]

    write_jsonl(output_manifest, selected_rows)
    summary = {
        "input_manifest": serialize_repo_path(input_manifest),
        "allowlist_file": serialize_repo_path(allowlist_file),
        "output_manifest": serialize_repo_path(output_manifest),
        "input_row_count": len(rows),
        "selected_row_count": len(selected_rows),
        "allowlist_count": len(allowlist),
        "selected_speaker_count": len(speaker_counts),
        "missing_allowlist_speakers": missing_speakers,
        "speaker_counts": dict(sorted(speaker_counts.items())),
    }
    write_json(summary_json, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
