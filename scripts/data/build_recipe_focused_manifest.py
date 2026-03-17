from __future__ import annotations

import argparse
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


def serialize_repo_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deterministic recipe-focused manifest from an existing synthetic manifest."
    )
    parser.add_argument(
        "--input-manifest",
        type=Path,
        default=ROOT / "data" / "synthetic" / "train_manifest.jsonl",
    )
    parser.add_argument(
        "--output-manifest",
        type=Path,
        required=True,
    )
    parser.add_argument(
        "--recipe-cap",
        action="append",
        default=[],
        help="Per-recipe cap in the form recipe=count. Can be passed multiple times.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260316,
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


def parse_recipe_caps(values: list[str]) -> dict[str, int]:
    caps: dict[str, int] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid --recipe-cap value: {value!r}")
        recipe, raw_count = value.split("=", 1)
        recipe = recipe.strip()
        count = int(raw_count)
        if not recipe:
            raise ValueError(f"Invalid empty recipe in --recipe-cap value: {value!r}")
        if count < 0:
            raise ValueError(f"Recipe cap must be non-negative: {value!r}")
        caps[recipe] = count
    return caps


def summarize(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    recipe_counts = Counter(row["recipe"] for row in rows)
    pattern_counts = Counter(row.get("temporal_pattern", "target_full") for row in rows)
    return {
        "recipe_counts": dict(sorted(recipe_counts.items())),
        "pattern_counts": dict(sorted(pattern_counts.items())),
    }


def main() -> None:
    args = parse_args()
    recipe_caps = parse_recipe_caps(args.recipe_cap)
    rng = random.Random(args.seed)

    rows = load_jsonl(args.input_manifest)
    by_recipe: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_recipe[row["recipe"]].append(row)

    selected: list[dict[str, Any]] = []
    for recipe, cap in recipe_caps.items():
        candidates = list(by_recipe.get(recipe, []))
        rng.shuffle(candidates)
        selected.extend(candidates[:cap])

    selected.sort(key=lambda row: row["sample_id"])
    args.output_manifest.parent.mkdir(parents=True, exist_ok=True)
    with args.output_manifest.open("w", encoding="utf-8", newline="\n") as fh:
        for row in selected:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    summary = {
        "input_manifest": serialize_repo_path(args.input_manifest),
        "output_manifest": serialize_repo_path(args.output_manifest),
        "seed": args.seed,
        "recipe_caps": recipe_caps,
        "selected_count": len(selected),
        **summarize(selected),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
