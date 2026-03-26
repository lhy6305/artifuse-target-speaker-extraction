from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
LEGACY_PACK_FORMAT = "legacy_ab_v1"
MULTI_PACK_FORMAT = "multi_candidate_v1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Decode a listening GUI export back to real labels using blind_key.json, "
            "and produce a structured post-GUI summary."
        )
    )
    parser.add_argument("--pack-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, default=None)
    return parser.parse_args()


def serialize_repo_path(path: Path | None) -> str:
    if path is None:
        return ""
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def parse_json_list(raw: str) -> list[str]:
    value = raw.strip()
    if not value:
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError("Expected JSON list.")
    return [str(item).strip() for item in parsed if str(item).strip()]


def parse_json_dict(raw: str) -> dict[str, Any]:
    value = raw.strip()
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("Expected JSON object.")
    return {str(key).strip(): item for key, item in parsed.items()}


def split_decision_tags(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def infer_pack_format(fieldnames: list[str] | None) -> str:
    names = set(fieldnames or [])
    if "candidate_ids_json" in names:
        return MULTI_PACK_FORMAT
    return LEGACY_PACK_FORMAT


def load_rows(csv_path: Path) -> tuple[list[dict[str, str]], str]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        pack_format = infer_pack_format(reader.fieldnames)
        rows = [{str(key): str(value) for key, value in row.items()} for row in reader]
    return rows, pack_format


def build_mapping(blind_key: dict[str, Any] | None) -> dict[str, dict[str, str]]:
    if not blind_key:
        return {}
    mapping_rows = blind_key.get("mapping", [])
    output: dict[str, dict[str, str]] = {}
    for row in mapping_rows:
        sample_id = str(row["sample_id"])
        normalized: dict[str, str] = {}
        for key, value in row.items():
            if key == "sample_id":
                continue
            normalized_key = str(key)
            if normalized_key == "candidate_a":
                normalized_key = "file_a"
            elif normalized_key == "candidate_b":
                normalized_key = "file_b"
            normalized[normalized_key] = str(value)
        output[sample_id] = normalized
    return output


def decode_choice(
    raw_choice: str,
    sample_mapping: dict[str, str],
) -> str:
    choice = raw_choice.strip()
    if not choice:
        return "unscored"
    if choice in {"tie", "uncertain", "unscored"}:
        return choice
    return sample_mapping.get(choice, choice)


def build_candidate_ids(row: dict[str, str], pack_format: str) -> list[str]:
    if pack_format == MULTI_PACK_FORMAT:
        return parse_json_list(row.get("candidate_ids_json", ""))
    candidate_ids: list[str] = []
    if row.get("file_a_name", "").strip():
        candidate_ids.append("file_a")
    if row.get("file_b_name", "").strip():
        candidate_ids.append("file_b")
    return candidate_ids


def build_candidate_ratings(row: dict[str, str], pack_format: str) -> dict[str, dict[str, str]]:
    if pack_format == MULTI_PACK_FORMAT:
        parsed = parse_json_dict(row.get("candidate_ratings_json", ""))
        normalized: dict[str, dict[str, str]] = {}
        for candidate_id, ratings in parsed.items():
            if not isinstance(ratings, dict):
                continue
            normalized[candidate_id] = {
                str(metric_key).strip(): str(metric_value).strip()
                for metric_key, metric_value in ratings.items()
            }
        return normalized

    return {
        "file_a": {
            "source_retention": row.get("file_a_source_retention", "").strip(),
            "interference_leak": row.get("file_a_interference_leak", "").strip(),
            "volume_fluctuation": row.get("file_a_volume_fluctuation", "").strip(),
            "artifact": row.get("file_a_artifact", "").strip(),
        },
        "file_b": {
            "source_retention": row.get("file_b_source_retention", "").strip(),
            "interference_leak": row.get("file_b_interference_leak", "").strip(),
            "volume_fluctuation": row.get("file_b_volume_fluctuation", "").strip(),
            "artifact": row.get("file_b_artifact", "").strip(),
        },
    }


def decode_candidate_ratings(
    candidate_ids: list[str],
    candidate_ratings: dict[str, dict[str, str]],
    sample_mapping: dict[str, str],
) -> dict[str, dict[str, str]]:
    decoded: dict[str, dict[str, str]] = {}
    for candidate_id in candidate_ids:
        decoded_label = sample_mapping.get(candidate_id, candidate_id)
        decoded[decoded_label] = candidate_ratings.get(candidate_id, {})
    return decoded


def count_choices(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[key])
        counts[value] = counts.get(value, 0) + 1
    return counts


def decode_pair_choice(value: Any, row: dict[str, Any]) -> str:
    normalized = str(value)
    if normalized == "file_a":
        return str(row.get("file_a_label", "file_a"))
    if normalized == "file_b":
        return str(row.get("file_b_label", "file_b"))
    return normalized


def load_pair_analysis_by_sample(pack_dir: Path) -> dict[str, dict[str, Any]]:
    by_sample: dict[str, dict[str, Any]] = {}
    for analysis_name in ("tradeoff_analysis", "bandwidth_analysis", "transient_analysis"):
        per_sample_jsonl = pack_dir / analysis_name / "per_sample_pair_metrics.jsonl"
        if not per_sample_jsonl.exists():
            continue
        for line in per_sample_jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            sample_id = str(row.get("sample_id", "")).strip()
            if not sample_id:
                continue
            attached = by_sample.setdefault(sample_id, {})
            if analysis_name == "tradeoff_analysis":
                attached[analysis_name] = {
                    "better_source_retention_candidate": row.get("better_source_retention_candidate"),
                    "better_source_retention_label": decode_pair_choice(
                        row.get("better_source_retention_candidate"),
                        row,
                    ),
                    "more_interference_leaky_candidate": row.get("more_interference_leaky_candidate"),
                    "more_interference_leaky_label": decode_pair_choice(
                        row.get("more_interference_leaky_candidate"),
                        row,
                    ),
                    "more_residual_heavy_candidate": row.get("more_residual_heavy_candidate"),
                    "more_residual_heavy_label": decode_pair_choice(
                        row.get("more_residual_heavy_candidate"),
                        row,
                    ),
                    "better_retention_minus_leak_candidate": row.get("better_retention_minus_leak_candidate"),
                    "better_retention_minus_leak_label": decode_pair_choice(
                        row.get("better_retention_minus_leak_candidate"),
                        row,
                    ),
                    "delta_target_capture_db_b_minus_a": row.get("delta_target_capture_db_b_minus_a"),
                    "delta_interference_capture_db_b_minus_a": row.get("delta_interference_capture_db_b_minus_a"),
                    "delta_retention_minus_leak_db_b_minus_a": row.get("delta_retention_minus_leak_db_b_minus_a"),
                }
            elif analysis_name == "bandwidth_analysis":
                attached[analysis_name] = {
                    "narrower_candidate": row.get("narrower_candidate"),
                    "narrower_label": decode_pair_choice(row.get("narrower_candidate"), row),
                    "delta_rolloff_hz_b_minus_a": row.get("delta_rolloff_hz_b_minus_a"),
                    "delta_upper_vs_mid_db_b_minus_a": row.get("delta_upper_vs_mid_db_b_minus_a"),
                    "delta_frame_upper_share_p90_b_minus_a": row.get("delta_frame_upper_share_p90_b_minus_a"),
                }
            else:
                attached[analysis_name] = {
                    **row,
                    "more_transient_lossy_label": decode_pair_choice(
                        row.get("more_transient_lossy_candidate"),
                        row,
                    ),
                }
    return by_sample


def main() -> None:
    args = parse_args()
    pack_dir = args.pack_dir.resolve()
    csv_path = pack_dir / "listening_sheet.csv"
    if not csv_path.exists():
        raise SystemExit(f"Missing listening sheet: {csv_path}")

    rows, inferred_pack_format = load_rows(csv_path)
    blind_key_path = pack_dir / "blind_key.json"
    blind_key = load_json(blind_key_path) if blind_key_path.exists() else None
    mapping_by_sample = build_mapping(blind_key)
    gui_summary_path = pack_dir / "listening_results_summary.json"
    gui_summary = load_json(gui_summary_path) if gui_summary_path.exists() else None
    pair_analysis_by_sample = load_pair_analysis_by_sample(pack_dir)

    decoded_rows: list[dict[str, Any]] = []
    for row in rows:
        sample_id = row.get("sample_id", "").strip()
        sample_mapping = mapping_by_sample.get(sample_id, {})
        candidate_ids = build_candidate_ids(row, inferred_pack_format)
        candidate_ratings = build_candidate_ratings(row, inferred_pack_format)
        decoded_rows.append(
            {
                "sample_id": sample_id,
                "recipe": row.get("recipe", "").strip(),
                "temporal_pattern": row.get("temporal_pattern", "").strip(),
                "target_present_ratio": row.get("target_present_ratio", "").strip(),
                "raw_better_output": row.get("better_output", "").strip(),
                "decoded_better_output": decode_choice(row.get("better_output", ""), sample_mapping),
                "decision_tags": split_decision_tags(row.get("decision_tags", "")),
                "note": row.get("note", "").strip(),
                "candidate_ids": candidate_ids,
                "decoded_candidate_labels": {
                    candidate_id: sample_mapping.get(candidate_id, candidate_id)
                    for candidate_id in candidate_ids
                },
                "decoded_candidate_ratings": decode_candidate_ratings(candidate_ids, candidate_ratings, sample_mapping),
                "pair_analysis": pair_analysis_by_sample.get(sample_id, {}),
            }
        )

    decoded_counts = count_choices(decoded_rows, "decoded_better_output")
    recipe_breakdown: dict[str, dict[str, int]] = {}
    for row in decoded_rows:
        recipe_key = row["recipe"]
        recipe_counts = recipe_breakdown.setdefault(recipe_key, {})
        outcome = row["decoded_better_output"]
        recipe_counts[outcome] = recipe_counts.get(outcome, 0) + 1

    output = {
        "pack_dir": serialize_repo_path(pack_dir),
        "pack_format": inferred_pack_format,
        "blind_mode": blind_key is not None,
        "blind_key_path": serialize_repo_path(blind_key_path) if blind_key_path.exists() else "",
        "gui_summary_path": serialize_repo_path(gui_summary_path) if gui_summary_path.exists() else "",
        "gui_summary": gui_summary,
        "num_samples": len(decoded_rows),
        "num_scored": sum(1 for row in decoded_rows if row["decoded_better_output"] != "unscored"),
        "decoded_better_output_counts": decoded_counts,
        "decoded_recipe_breakdown": recipe_breakdown,
        "samples": decoded_rows,
    }

    output_json = args.output_json or (pack_dir / "listening_review_decoded_summary.json")
    output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        json.dumps(
            {
                "pack_dir": serialize_repo_path(pack_dir),
                "output_json": serialize_repo_path(output_json),
                "pack_format": inferred_pack_format,
                "blind_mode": blind_key is not None,
                "num_samples": len(decoded_rows),
                "decoded_better_output_counts": decoded_counts,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
