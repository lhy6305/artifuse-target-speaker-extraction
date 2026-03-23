from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
BUCKET_ORDER = [
    "pre_entry_or_pure",
    "hinge_secondary_crossed_first",
    "post_entry_both_crossed_reference_deeper",
    "post_entry_both_crossed_secondary_deeper_or_equal",
    "reference_only_crossed_unexpected",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Classify neighbor rows from analyze_proxy_case_neighbors.py into gap-state buckets "
            "so rare same-signature rows can be separated from hinge cases and unexpected branches."
        )
    )
    parser.add_argument("--input-json", type=Path, required=True)
    parser.add_argument(
        "--secondary-alias",
        type=str,
        required=True,
        help="Alias to compare alongside the input summary's reference_alias.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=None,
        help="Optional cap on how many already-sorted neighbor rows to scan. Defaults to all rows in input.",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    return parser.parse_args()


def serialize_repo_path(path: Path | None) -> str | None:
    if path is None:
        return None
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def classify_bucket(
    focus_minus_reference_db: float,
    focus_minus_secondary_db: float,
) -> str:
    if focus_minus_reference_db > 0.0 and focus_minus_secondary_db > 0.0:
        return "pre_entry_or_pure"
    if focus_minus_reference_db > 0.0 and focus_minus_secondary_db <= 0.0:
        return "hinge_secondary_crossed_first"
    if focus_minus_reference_db <= 0.0 and focus_minus_secondary_db <= 0.0:
        if focus_minus_reference_db < focus_minus_secondary_db:
            return "post_entry_both_crossed_reference_deeper"
        return "post_entry_both_crossed_secondary_deeper_or_equal"
    return "reference_only_crossed_unexpected"


def project_row(
    row: dict[str, Any],
    focus_alias: str,
    reference_alias: str,
    secondary_alias: str,
) -> dict[str, Any]:
    compare_summary = row["compare_summary"]
    candidate_gaps = compare_summary["candidate_gap_vs_aliases_db"]
    focus_minus_reference_db = float(candidate_gaps[reference_alias])
    focus_minus_secondary_db = float(candidate_gaps[secondary_alias])
    bucket = classify_bucket(
        focus_minus_reference_db=focus_minus_reference_db,
        focus_minus_secondary_db=focus_minus_secondary_db,
    )
    ranking_aliases = [str(item["alias"]) for item in compare_summary["ranking"]]
    return {
        "sample_id": str(row["sample_id"]),
        "metadata_distance_z": float(row["metadata_distance_z"]),
        "bucket": bucket,
        "focus_minus_reference_db": focus_minus_reference_db,
        "focus_minus_secondary_db": focus_minus_secondary_db,
        "reference_minus_secondary_db": float(
            focus_minus_reference_db - focus_minus_secondary_db
        ),
        "top_alias": str(compare_summary["top_alias"]),
        "ranking_aliases": ranking_aliases,
        "failed_constraints": list(compare_summary["failed_constraints"]),
    }


def main() -> None:
    args = parse_args()
    input_payload = load_json(args.input_json)
    focus_alias = str(input_payload["focus_alias"])
    reference_alias = str(input_payload["reference_alias"])
    secondary_alias = args.secondary_alias

    top_rows = list(input_payload["top_nearest_search_rows"])
    if args.top_k is not None:
        top_rows = top_rows[: args.top_k]

    projected_rows = [
        project_row(
            row=row,
            focus_alias=focus_alias,
            reference_alias=reference_alias,
            secondary_alias=secondary_alias,
        )
        for row in top_rows
    ]

    bucket_counter = Counter(str(row["bucket"]) for row in projected_rows)
    bucket_counts = {
        bucket: int(bucket_counter.get(bucket, 0))
        for bucket in BUCKET_ORDER
    }

    bucket_rows: dict[str, list[dict[str, Any]]] = {}
    for row in projected_rows:
        bucket_rows.setdefault(str(row["bucket"]), []).append(row)
    for rows in bucket_rows.values():
        rows.sort(key=lambda item: (float(item["metadata_distance_z"]), str(item["sample_id"])))

    nearest_row_by_bucket = {
        bucket: rows[0]
        for bucket, rows in sorted(bucket_rows.items())
        if rows
    }

    output = {
        "input_json": serialize_repo_path(args.input_json),
        "source_seed_sample_ids": list(input_payload.get("seed_sample_ids", [])),
        "focus_alias": focus_alias,
        "reference_alias": reference_alias,
        "secondary_alias": secondary_alias,
        "num_scanned_rows": len(projected_rows),
        "same_signature_definition": (
            f"{focus_alias}<{reference_alias}, {focus_alias}<{secondary_alias}, "
            f"and {focus_alias}-{reference_alias} is deeper than {focus_alias}-{secondary_alias}"
        ),
        "bucket_counts": bucket_counts,
        "nearest_row_by_bucket": nearest_row_by_bucket,
        "same_signature_rows": bucket_rows.get("post_entry_both_crossed_reference_deeper", []),
        "bucket_rows": dict(sorted(bucket_rows.items())),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        json.dumps(
            {
                "output_json": serialize_repo_path(args.output_json),
                "bucket_counts": bucket_counts,
                "same_signature_sample_ids": [
                    str(row["sample_id"]) for row in output["same_signature_rows"]
                ],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
