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
            "Union multiple JSONL manifests by sample_id, keeping the last occurrence for duplicate keys "
            "and exporting a deterministic sorted result."
        )
    )
    parser.add_argument("--input-manifests", nargs="+", type=Path, required=True)
    parser.add_argument("--output-manifest", type=Path, required=True)
    parser.add_argument("--sample-ids-output", type=Path, default=None)
    parser.add_argument("--summary-json", type=Path, default=None)
    parser.add_argument("--dedupe-key", type=str, default="sample_id")
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


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    recipe_counts = Counter(str(row.get("recipe", "")) for row in rows)
    temporal_pattern_counts = Counter(str(row.get("temporal_pattern", "")) for row in rows)
    interference_pool_counts = Counter(
        str((row.get("interference_layers") or [{}])[0].get("pool", "")) for row in rows
    )
    return {
        "count": len(rows),
        "recipe_counts": dict(sorted(recipe_counts.items())),
        "temporal_pattern_counts": dict(sorted(temporal_pattern_counts.items())),
        "interference_pool_counts": dict(sorted(interference_pool_counts.items())),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_sample_ids(path: Path, sample_ids: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for sample_id in sample_ids:
            fh.write(sample_id + "\n")


def main() -> None:
    args = parse_args()

    merged_by_key: dict[str, dict[str, Any]] = {}
    duplicate_keys: set[str] = set()
    input_summaries: list[dict[str, Any]] = []

    for manifest_path in args.input_manifests:
        rows = load_jsonl(manifest_path)
        input_summaries.append(
            {
                "manifest": serialize_repo_path(manifest_path),
                "summary": summarize_rows(rows),
            }
        )
        for row in rows:
            key = str(row.get(args.dedupe_key, ""))
            if key in merged_by_key:
                duplicate_keys.add(key)
            merged_by_key[key] = row

    merged_rows = [merged_by_key[key] for key in sorted(merged_by_key)]
    sample_ids = [str(row.get(args.dedupe_key, "")) for row in merged_rows]

    write_jsonl(args.output_manifest, merged_rows)
    if args.sample_ids_output is not None:
        write_sample_ids(args.sample_ids_output, sample_ids)

    summary = {
        "input_manifests": [serialize_repo_path(path) for path in args.input_manifests],
        "output_manifest": serialize_repo_path(args.output_manifest),
        "sample_ids_output": serialize_repo_path(args.sample_ids_output),
        "dedupe_key": args.dedupe_key,
        "duplicate_key_count": len(duplicate_keys),
        "duplicate_keys": sorted(duplicate_keys),
        "input_summaries": input_summaries,
        "output_summary": summarize_rows(merged_rows),
    }

    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        with args.summary_json.open("w", encoding="utf-8", newline="\n") as fh:
            json.dump(summary, fh, ensure_ascii=False, indent=2)

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
