from __future__ import annotations

import json
import math
import re
import shutil
import wave
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
GENSHIN_ROOT = ROOT / "data_in" / "genshin_voice_extract"
CURATED_ROOT = ROOT / "data" / "curated"
NEW_CURATED_DIR = CURATED_ROOT / "genshin_clean_subset_cover_v1"
MANIFEST_DIR = ROOT / "data" / "manifests"
MANIFEST_PATH = MANIFEST_DIR / "speech_interference_clean_pool.jsonl"
MANIFEST_BACKUP_PATH = (
    MANIFEST_DIR / "speech_interference_clean_pool.pre_cover_v1_backup.jsonl"
)
SUMMARY_PATH = NEW_CURATED_DIR / "selection_summary.json"
SELECTION_REPORT_PATH = MANIFEST_DIR / "speech_interference_clean_pool.cover_v1_report.json"

MIN_DURATION = 1.0
MAX_DURATION = 12.0
MIN_TEXT_LENGTH = 2
MAX_TEXT_LENGTH = 80
MIN_ITEMS_PER_SPEAKER = 8
BASE_TARGET_PER_SPEAKER = 32
MAX_TARGET_PER_SPEAKER = 96


@dataclass(frozen=True)
class Candidate:
    speaker_id: str
    current_audio_path: str
    current_text_path: str
    canonical_audio_path: str
    canonical_text_path: str
    text: str
    duration_sec: float
    category: str
    path_depth: int
    feature_values: tuple[tuple[str, str], ...]
    normalized_text: str


def relpath(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


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


def wav_duration_sec(path: Path) -> float:
    with wave.open(str(path), "rb") as fh:
        return fh.getnframes() / float(fh.getframerate())


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", text).strip()


def duration_bin(duration_sec: float) -> str:
    if duration_sec < 2.0:
        return "dur_1_2"
    if duration_sec < 4.0:
        return "dur_2_4"
    if duration_sec < 7.0:
        return "dur_4_7"
    return "dur_7_12"


def text_length_bin(text: str) -> str:
    length = len(text)
    if length <= 8:
        return "txt_02_08"
    if length <= 16:
        return "txt_09_16"
    if length <= 32:
        return "txt_17_32"
    if length <= 48:
        return "txt_33_48"
    return "txt_49_80"


def clause_count_bin(text: str) -> str:
    parts = [seg for seg in re.split(r"[，,。！？!?；;…]+", text) if seg.strip()]
    count = len(parts)
    if count <= 1:
        return "clause_1"
    if count == 2:
        return "clause_2"
    if count == 3:
        return "clause_3"
    return "clause_4p"


def punctuation_classes(text: str) -> list[str]:
    classes: list[str] = []
    if re.search(r"[？?]", text):
        classes.append("punct_question")
    if re.search(r"[！!]", text):
        classes.append("punct_exclaim")
    if "…" in text:
        classes.append("punct_ellipsis")
    if re.search(r"[，,；;]", text):
        classes.append("punct_pause")
    if re.search(r"[“”\"『』「」]", text):
        classes.append("punct_quote")
    if re.search(r"[。.!！？?]", text):
        classes.append("punct_terminal")
    if not classes:
        classes.append("punct_none")
    return classes


def char_class(ch: str) -> str:
    if not ch:
        return "char_empty"
    if re.match(r"[\u4e00-\u9fff]", ch):
        return "char_cjk"
    if re.match(r"[A-Za-z]", ch):
        return "char_latin"
    if re.match(r"[0-9]", ch):
        return "char_digit"
    if re.match(r"[“”\"『』「」]", ch):
        return "char_quote"
    if re.match(r"[。.!！？?，,；;…]", ch):
        return "char_punct"
    return "char_other"


def make_feature_values(
    category: str,
    duration_sec: float,
    text: str,
) -> tuple[tuple[str, str], ...]:
    values: list[tuple[str, str]] = [
        ("category", category),
        ("duration_bin", duration_bin(duration_sec)),
        ("text_length_bin", text_length_bin(text)),
        ("clause_count_bin", clause_count_bin(text)),
        ("start_char_class", char_class(text[:1])),
        ("end_char_class", char_class(text[-1:])),
    ]
    for punct_class in punctuation_classes(text):
        values.append(("punct_class", punct_class))
    return tuple(values)


def category_from_canonical_path(canonical_audio_path: str, speaker_id: str) -> tuple[str, int]:
    parts = Path(canonical_audio_path).parts
    try:
        speaker_index = parts.index(speaker_id)
    except ValueError:
        return ("__unknown__", 0)
    trailing = parts[speaker_index + 1 : -1]
    if not trailing:
        return ("__root__", 0)
    return (trailing[0], len(trailing))


def relative_within_speaker(canonical_path: str, speaker_id: str) -> Path:
    parts = Path(canonical_path).parts
    speaker_index = parts.index(speaker_id)
    trailing = parts[speaker_index + 1 :]
    return Path(*trailing)


def iter_manifest_curated_candidates() -> list[Candidate]:
    if not MANIFEST_PATH.exists():
        return []
    rows = load_jsonl(MANIFEST_PATH)
    candidates: list[Candidate] = []
    for row in rows:
        source = str(row.get("source", ""))
        if not source.startswith("data/curated/"):
            continue
        canonical_audio_path = row.get("upstream_audio_path") or row["audio_path"]
        canonical_text_path = row.get("upstream_text_path") or row["text_path"]
        category, path_depth = category_from_canonical_path(
            canonical_audio_path,
            row["speaker_id"],
        )
        text = row["text"]
        duration_sec = float(row["duration_sec"])
        candidates.append(
            Candidate(
                speaker_id=row["speaker_id"],
                current_audio_path=row["audio_path"],
                current_text_path=row["text_path"],
                canonical_audio_path=canonical_audio_path,
                canonical_text_path=canonical_text_path,
                text=text,
                duration_sec=duration_sec,
                category=category,
                path_depth=path_depth,
                feature_values=make_feature_values(category, duration_sec, text),
                normalized_text=normalize_text(text),
            )
        )
    return candidates


def iter_original_candidates() -> list[Candidate]:
    candidates: list[Candidate] = []
    for speaker_dir in sorted(path for path in GENSHIN_ROOT.iterdir() if path.is_dir()):
        speaker_id = speaker_dir.name
        for wav_path in sorted(speaker_dir.rglob("*.wav")):
            lab_path = wav_path.with_suffix(".lab")
            if not lab_path.exists():
                continue
            try:
                text = lab_path.read_text(encoding="utf-8").strip()
            except UnicodeDecodeError:
                continue
            if not (MIN_TEXT_LENGTH <= len(text) <= MAX_TEXT_LENGTH):
                continue
            try:
                duration_sec = wav_duration_sec(wav_path)
            except (wave.Error, EOFError):
                continue
            if not (MIN_DURATION <= duration_sec <= MAX_DURATION):
                continue
            canonical_audio_path = relpath(wav_path)
            canonical_text_path = relpath(lab_path)
            category, path_depth = category_from_canonical_path(
                canonical_audio_path,
                speaker_id,
            )
            candidates.append(
                Candidate(
                    speaker_id=speaker_id,
                    current_audio_path=canonical_audio_path,
                    current_text_path=canonical_text_path,
                    canonical_audio_path=canonical_audio_path,
                    canonical_text_path=canonical_text_path,
                    text=text,
                    duration_sec=round(duration_sec, 6),
                    category=category,
                    path_depth=path_depth,
                    feature_values=make_feature_values(category, duration_sec, text),
                    normalized_text=normalize_text(text),
                )
            )
    return candidates


def merge_candidates() -> dict[str, list[Candidate]]:
    merged: dict[str, Candidate] = {}
    for candidate in iter_manifest_curated_candidates() + iter_original_candidates():
        merged.setdefault(candidate.canonical_audio_path, candidate)
    grouped: dict[str, list[Candidate]] = defaultdict(list)
    for candidate in merged.values():
        grouped[candidate.speaker_id].append(candidate)
    for speaker_id in grouped:
        grouped[speaker_id].sort(
            key=lambda item: (
                item.category,
                item.path_depth,
                item.normalized_text,
                item.canonical_audio_path,
            )
        )
    return grouped


def target_count_for_speaker(items: list[Candidate]) -> int:
    categories = {item.category for item in items}
    punct_classes = {
        value
        for item in items
        for feature_name, value in item.feature_values
        if feature_name == "punct_class"
    }
    target = BASE_TARGET_PER_SPEAKER + 8 * max(0, len(categories) - 1)
    target += 2 * max(0, len(punct_classes) - 1)
    target = max(BASE_TARGET_PER_SPEAKER, target)
    target = min(MAX_TARGET_PER_SPEAKER, target)
    return min(len(items), target)


def feature_frequencies(items: list[Candidate]) -> Counter[tuple[str, str]]:
    counter: Counter[tuple[str, str]] = Counter()
    for item in items:
        counter.update(item.feature_values)
    return counter


def score_candidate(
    item: Candidate,
    freq: Counter[tuple[str, str]],
    covered: Counter[tuple[str, str]],
    text_counts: Counter[str],
    category_counts: Counter[str],
) -> float:
    score = 0.0
    for feature in item.feature_values:
        feature_freq = freq[feature]
        rarity = 1.0 / math.sqrt(feature_freq)
        if covered[feature] == 0:
            score += 3.0 + rarity
        else:
            score += 0.35 / (1 + covered[feature]) + 0.15 * rarity

    if text_counts[item.normalized_text] == 0:
        score += 2.0
    else:
        score -= 4.0 * text_counts[item.normalized_text]

    score += 0.8 / (1 + category_counts[item.category])
    score += 0.12 * min(item.path_depth, 3)
    if item.category != "__root__":
        score += 0.6
    return score


def add_if_best_feature_match(
    selected: list[Candidate],
    selected_paths: set[str],
    items: list[Candidate],
    feature_key: tuple[str, str],
    freq: Counter[tuple[str, str]],
    covered: Counter[tuple[str, str]],
    text_counts: Counter[str],
    category_counts: Counter[str],
    target_count: int,
) -> None:
    if len(selected) >= target_count:
        return
    if covered[feature_key] > 0:
        return
    candidates = [
        item
        for item in items
        if item.canonical_audio_path not in selected_paths
        and feature_key in item.feature_values
    ]
    if not candidates:
        return
    best = max(
        candidates,
        key=lambda item: (
            score_candidate(item, freq, covered, text_counts, category_counts),
            item.duration_sec,
            item.canonical_audio_path,
        ),
    )
    selected.append(best)
    selected_paths.add(best.canonical_audio_path)
    covered.update(best.feature_values)
    text_counts[best.normalized_text] += 1
    category_counts[best.category] += 1


def select_for_speaker(items: list[Candidate]) -> list[Candidate]:
    if len(items) <= BASE_TARGET_PER_SPEAKER:
        return list(items)

    target_count = target_count_for_speaker(items)
    freq = feature_frequencies(items)
    selected: list[Candidate] = []
    selected_paths: set[str] = set()
    covered: Counter[tuple[str, str]] = Counter()
    text_counts: Counter[str] = Counter()
    category_counts: Counter[str] = Counter()

    category_values = sorted({item.category for item in items})
    duration_values = sorted(
        {
            value
            for item in items
            for feature_name, value in item.feature_values
            if feature_name == "duration_bin"
        }
    )
    text_length_values = sorted(
        {
            value
            for item in items
            for feature_name, value in item.feature_values
            if feature_name == "text_length_bin"
        }
    )
    punctuation_values = sorted(
        {
            value
            for item in items
            for feature_name, value in item.feature_values
            if feature_name == "punct_class"
        }
    )

    for value in category_values:
        add_if_best_feature_match(
            selected,
            selected_paths,
            items,
            ("category", value),
            freq,
            covered,
            text_counts,
            category_counts,
            target_count,
        )
    for value in duration_values:
        add_if_best_feature_match(
            selected,
            selected_paths,
            items,
            ("duration_bin", value),
            freq,
            covered,
            text_counts,
            category_counts,
            target_count,
        )
    for value in text_length_values:
        add_if_best_feature_match(
            selected,
            selected_paths,
            items,
            ("text_length_bin", value),
            freq,
            covered,
            text_counts,
            category_counts,
            target_count,
        )
    for value in punctuation_values:
        add_if_best_feature_match(
            selected,
            selected_paths,
            items,
            ("punct_class", value),
            freq,
            covered,
            text_counts,
            category_counts,
            target_count,
        )

    remaining = [
        item for item in items if item.canonical_audio_path not in selected_paths
    ]
    while len(selected) < target_count and remaining:
        best = max(
            remaining,
            key=lambda item: (
                score_candidate(item, freq, covered, text_counts, category_counts),
                item.duration_sec,
                item.canonical_audio_path,
            ),
        )
        selected.append(best)
        selected_paths.add(best.canonical_audio_path)
        covered.update(best.feature_values)
        text_counts[best.normalized_text] += 1
        category_counts[best.category] += 1
        remaining = [
            item for item in remaining if item.canonical_audio_path not in selected_paths
        ]

    selected.sort(
        key=lambda item: (
            item.speaker_id,
            item.category,
            item.duration_sec,
            item.canonical_audio_path,
        )
    )
    return selected


def materialize_selected_rows(rows: list[dict[str, Any]]) -> None:
    NEW_CURATED_DIR.mkdir(parents=True, exist_ok=True)
    for row in rows:
        src_audio = ROOT / row["upstream_audio_path"]
        src_text = ROOT / row["upstream_text_path"]
        if not src_audio.exists():
            src_audio = ROOT / row["current_audio_path"]
        if not src_text.exists():
            src_text = ROOT / row["current_text_path"]

        dst_audio = ROOT / row["audio_path"]
        dst_text = ROOT / row["text_path"]
        dst_audio.parent.mkdir(parents=True, exist_ok=True)
        dst_text.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_audio, dst_audio)
        shutil.copy2(src_text, dst_text)


def build_rows(grouped: dict[str, list[Candidate]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    speaker_summaries: list[dict[str, Any]] = []
    selected_speaker_ids = sorted(grouped)

    for speaker_rank, speaker_id in enumerate(selected_speaker_ids, start=1):
        items = grouped[speaker_id]
        if len(items) < MIN_ITEMS_PER_SPEAKER:
            continue
        selected_items = select_for_speaker(items)
        category_counter = Counter(item.category for item in selected_items)
        speaker_summaries.append(
            {
                "speaker_id": speaker_id,
                "candidate_count": len(items),
                "selected_count": len(selected_items),
                "category_count": len({item.category for item in items}),
                "selected_category_breakdown": dict(sorted(category_counter.items())),
            }
        )

        for item_rank, item in enumerate(selected_items, start=1):
            dst_audio_path = (
                NEW_CURATED_DIR
                / speaker_id
                / relative_within_speaker(item.canonical_audio_path, speaker_id)
            )
            dst_text_path = (
                NEW_CURATED_DIR
                / speaker_id
                / relative_within_speaker(item.canonical_text_path, speaker_id)
            )
            rows.append(
                {
                    "speaker_id": speaker_id,
                    "current_audio_path": item.current_audio_path,
                    "current_text_path": item.current_text_path,
                    "audio_path": relpath(dst_audio_path),
                    "text_path": relpath(dst_text_path),
                    "text": item.text,
                    "duration_sec": round(item.duration_sec, 6),
                    "source": relpath(NEW_CURATED_DIR),
                    "pool": "speech_interference_clean_pool",
                    "speaker_rank": speaker_rank,
                    "item_rank_within_speaker": item_rank,
                    "selection_reason": "coverage_weighted_sampling_v1",
                    "coverage_category": item.category,
                    "upstream_audio_path": item.canonical_audio_path,
                    "upstream_text_path": item.canonical_text_path,
                }
            )

    summary = {
        "speaker_count": len(speaker_summaries),
        "item_count": len(rows),
        "speaker_summaries": speaker_summaries,
    }
    return rows, summary


def main() -> None:
    if MANIFEST_PATH.exists() and not MANIFEST_BACKUP_PATH.exists():
        shutil.copy2(MANIFEST_PATH, MANIFEST_BACKUP_PATH)

    grouped = merge_candidates()
    rows, summary = build_rows(grouped)
    materialize_selected_rows(rows)
    write_jsonl(MANIFEST_PATH, rows)

    write_json(
        SUMMARY_PATH,
        {
            "status": "rebuilt",
            "selection_reason": "coverage_weighted_sampling_v1",
            **summary,
        },
    )
    write_json(
        SELECTION_REPORT_PATH,
        {
            "status": "rebuilt",
            "selection_reason": "coverage_weighted_sampling_v1",
            "curated_root": relpath(NEW_CURATED_DIR),
            "manifest_path": relpath(MANIFEST_PATH),
            "manifest_backup_path": relpath(MANIFEST_BACKUP_PATH),
            **summary,
        },
    )

    print(
        json.dumps(
            {
                "speaker_count": summary["speaker_count"],
                "item_count": summary["item_count"],
                "curated_root": relpath(NEW_CURATED_DIR),
                "manifest_path": relpath(MANIFEST_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
