from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=True))
            fh.write("\n")


def write_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def load_metadata(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build a tiny real artifact booster bundle by splitting "
            "near_real_interval_artifact_probe_v3_subspan by speech_clip_tag and "
            "merging the rows into the v249 base synthetic bundle."
        )
    )
    parser.add_argument(
        "--probe-manifest",
        type=Path,
        default=ROOT / "data" / "probes" / "near_real_interval_artifact_probe_v3_subspan_manifest.jsonl",
    )
    parser.add_argument(
        "--base-train-manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "train_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl",
    )
    parser.add_argument(
        "--base-val-manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl",
    )
    parser.add_argument(
        "--val-clip-tag",
        type=str,
        default="friend_absent_820s",
        help="Speech clip tag held out into val.",
    )
    parser.add_argument(
        "--output-prefix",
        type=str,
        default="local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_realartifactv3_bundle_v1",
    )
    args = parser.parse_args()

    probe_rows = read_jsonl(args.probe_manifest)
    base_train_rows = read_jsonl(args.base_train_manifest)
    base_val_rows = read_jsonl(args.base_val_manifest)

    real_train_rows: list[dict] = []
    real_val_rows: list[dict] = []
    for row in probe_rows:
        metadata = load_metadata(ROOT / row["metadata_path"])
        clip_tag = metadata.get("speech_clip_tag", "")
        if clip_tag == args.val_clip_tag:
            real_val_rows.append(row)
        else:
            real_train_rows.append(row)

    if not real_train_rows or not real_val_rows:
        raise ValueError("Both real_train_rows and real_val_rows must be non-empty.")

    merged_train_rows = base_train_rows + real_train_rows
    merged_val_rows = base_val_rows + real_val_rows

    train_manifest = ROOT / "data" / "synthetic" / f"train_manifest_{args.output_prefix}.jsonl"
    val_manifest = ROOT / "data" / "synthetic" / f"val_manifest_{args.output_prefix}.jsonl"
    write_jsonl(train_manifest, merged_train_rows)
    write_jsonl(val_manifest, merged_val_rows)

    selector_ids = [row["sample_id"] for row in real_train_rows + real_val_rows]
    selector_path = ROOT / "data" / "manifests" / "selectors" / "real_artifact_probe_v3_subspan_ids.txt"
    write_text(selector_path, "\n".join(selector_ids) + "\n")

    summary = {
        "probe_manifest": str(args.probe_manifest.relative_to(ROOT)).replace("\\", "/"),
        "base_train_manifest": str(args.base_train_manifest.relative_to(ROOT)).replace("\\", "/"),
        "base_val_manifest": str(args.base_val_manifest.relative_to(ROOT)).replace("\\", "/"),
        "train_manifest": str(train_manifest.relative_to(ROOT)).replace("\\", "/"),
        "val_manifest": str(val_manifest.relative_to(ROOT)).replace("\\", "/"),
        "selector_ids_file": str(selector_path.relative_to(ROOT)).replace("\\", "/"),
        "val_clip_tag": args.val_clip_tag,
        "real_train_count": len(real_train_rows),
        "real_val_count": len(real_val_rows),
        "merged_train_count": len(merged_train_rows),
        "merged_val_count": len(merged_val_rows),
        "real_train_sample_ids": [row["sample_id"] for row in real_train_rows],
        "real_val_sample_ids": [row["sample_id"] for row in real_val_rows],
    }
    summary_path = ROOT / "reports" / "data" / "2026-04-01_real_artifact_probe_v3_booster_bundle_summary.json"
    write_text(summary_path, json.dumps(summary, indent=2, ensure_ascii=True) + "\n")

    print(json.dumps(summary, ensure_ascii=True))


if __name__ == "__main__":
    main()
