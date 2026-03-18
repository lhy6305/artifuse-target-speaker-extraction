from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Summarize compare outputs on the near-real speech probe by anchor, speech family, "
            "speech slice, and gain."
        )
    )
    parser.add_argument("--compare-jsonl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--top-k", type=int, default=12)
    parser.add_argument("--delta-threshold-db", type=float, default=0.1)
    return parser.parse_args()


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


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


def summarize_group(rows: list[dict[str, Any]], delta_threshold_db: float) -> dict[str, Any]:
    count = len(rows)
    if count == 0:
        return {
            "count": 0,
            "avg_sisdr_delta_db": 0.0,
            "avg_waveform_l1_delta": 0.0,
            "improved_count": 0,
            "regressed_count": 0,
            "near_tie_count": 0,
        }
    improved_count = sum(1 for row in rows if row["sisdr_delta_db"] > delta_threshold_db)
    regressed_count = sum(1 for row in rows if row["sisdr_delta_db"] < -delta_threshold_db)
    return {
        "count": count,
        "avg_sisdr_delta_db": float(sum(row["sisdr_delta_db"] for row in rows) / count),
        "avg_waveform_l1_delta": float(sum(row["waveform_l1_delta"] for row in rows) / count),
        "improved_count": improved_count,
        "regressed_count": regressed_count,
        "near_tie_count": count - improved_count - regressed_count,
    }


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    compare_rows = load_jsonl(args.compare_jsonl)
    enriched_rows: list[dict[str, Any]] = []
    anchor_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    hypothesis_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    speech_family_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    speech_clip_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    gain_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    anchor_gain_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in compare_rows:
        metadata_path = ROOT / str(row["metadata_path"])
        metadata = load_json(metadata_path)
        gain_db = float(metadata["speech_interference_gain_db"])
        gain_key = f"{gain_db:.1f}dB"
        enriched_row = {
            **row,
            "near_real_anchor_sample_id": str(metadata["near_real_anchor_sample_id"]),
            "anchor_hypothesis": str(metadata["anchor_hypothesis"]),
            "speech_family": str(metadata["speech_family"]),
            "speech_clip_tag": str(metadata["speech_clip_tag"]),
            "speech_interference_gain_db": gain_db,
            "probe_version": str(metadata["probe_version"]),
        }
        enriched_rows.append(enriched_row)
        anchor_groups[enriched_row["near_real_anchor_sample_id"]].append(enriched_row)
        hypothesis_groups[enriched_row["anchor_hypothesis"]].append(enriched_row)
        speech_family_groups[enriched_row["speech_family"]].append(enriched_row)
        speech_clip_groups[enriched_row["speech_clip_tag"]].append(enriched_row)
        gain_groups[gain_key].append(enriched_row)
        anchor_gain_groups[f'{enriched_row["near_real_anchor_sample_id"]}__{gain_key}'].append(enriched_row)

    summary = {
        "compare_jsonl": serialize_repo_path(args.compare_jsonl),
        "num_samples": len(enriched_rows),
        "overall": summarize_group(enriched_rows, args.delta_threshold_db),
        "anchor_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(anchor_groups.items())
        },
        "hypothesis_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(hypothesis_groups.items())
        },
        "speech_family_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(speech_family_groups.items())
        },
        "speech_clip_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(speech_clip_groups.items())
        },
        "gain_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(gain_groups.items())
        },
        "anchor_gain_groups": {
            key: summarize_group(value, args.delta_threshold_db)
            for key, value in sorted(anchor_gain_groups.items())
        },
        "top_improvements": sorted(enriched_rows, key=lambda row: row["sisdr_delta_db"], reverse=True)[: args.top_k],
        "top_regressions": sorted(enriched_rows, key=lambda row: row["sisdr_delta_db"])[: args.top_k],
    }

    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    (args.output_dir / "per_sample_probe_rows.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in enriched_rows),
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "compare_jsonl": serialize_repo_path(args.compare_jsonl),
                "num_samples": len(enriched_rows),
                "avg_sisdr_delta_db": summary["overall"]["avg_sisdr_delta_db"],
                "output_dir": serialize_repo_path(args.output_dir),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
