from __future__ import annotations

import json
import math
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

import librosa
import numpy as np
import soundfile as sf
import torch
import torchaudio
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[2]
MANIFEST_DIR = ROOT / "data" / "manifests"
INTERIM_DIR = ROOT / "data" / "interim"
SOURCE_MANIFEST_PATH = MANIFEST_DIR / "speech_interference_clean_pool.jsonl"
BACKUP_MANIFEST_PATH = (
    MANIFEST_DIR / "speech_interference_clean_pool.pre_embed_prune_v1_backup.jsonl"
)
REPORT_PATH = MANIFEST_DIR / "speech_interference_clean_pool.embed_prune_v1_report.json"
EMBEDDING_CACHE_PATH = INTERIM_DIR / "genshin_clean_cover_v1_acoustic_embeddings.npz"
NEW_CURATED_DIR = ROOT / "data" / "curated" / "genshin_clean_subset_cover_embed_prune_v1"

TARGET_SR = 16000
MIN_KEEP_PER_SPEAKER = 10
MAX_KEEP_PER_SPEAKER = 36
KEEP_RATIO = 0.52
SQRT_SCALE = 2.6
EMBED_VERSION = 1


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


def relative_within_curated_root(audio_path: str, source_root: str) -> Path:
    audio = Path(audio_path)
    source_parts = Path(source_root).parts
    audio_parts = audio.parts
    for idx in range(len(audio_parts) - len(source_parts) + 1):
        if tuple(audio_parts[idx : idx + len(source_parts)]) == tuple(source_parts):
            return Path(*audio_parts[idx + len(source_parts) :])
    raise ValueError(f"Cannot derive relative path for {audio_path} under {source_root}")


def load_audio(path: Path) -> tuple[np.ndarray, int]:
    try:
        audio, sr = sf.read(str(path), always_2d=False)
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        audio = np.asarray(audio, dtype=np.float32)
        return audio, sr
    except Exception:
        try:
            waveform, sr = torchaudio.load(str(path))
            if waveform.ndim > 1 and waveform.shape[0] > 1:
                waveform = torch.mean(waveform, dim=0, keepdim=True)
            audio = waveform.squeeze(0).detach().cpu().numpy().astype(np.float32)
            return audio, sr
        except Exception:
            result = subprocess.run(
                [
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-i",
                    str(path),
                    "-f",
                    "f32le",
                    "-acodec",
                    "pcm_f32le",
                    "-ac",
                    "1",
                    "-ar",
                    str(TARGET_SR),
                    "pipe:1",
                ],
                check=True,
                capture_output=True,
            )
            audio = np.frombuffer(result.stdout, dtype=np.float32)
            return audio, TARGET_SR


def acoustic_embedding_from_path(audio_path_str: str) -> np.ndarray:
    audio_path = ROOT / audio_path_str
    audio, sr = load_audio(audio_path)
    if sr != TARGET_SR:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=TARGET_SR)
        sr = TARGET_SR
    if audio.size == 0:
        audio = np.zeros(TARGET_SR, dtype=np.float32)

    peak = float(np.max(np.abs(audio))) if audio.size else 0.0
    if peak > 0:
        audio = audio / peak

    mfcc = librosa.feature.mfcc(
        y=audio,
        sr=sr,
        n_mfcc=20,
        n_fft=400,
        hop_length=160,
        n_mels=40,
    )
    delta = librosa.feature.delta(mfcc)
    delta2 = librosa.feature.delta(mfcc, order=2)
    rms = librosa.feature.rms(y=audio, frame_length=400, hop_length=160)
    zcr = librosa.feature.zero_crossing_rate(audio, frame_length=400, hop_length=160)
    centroid = librosa.feature.spectral_centroid(
        y=audio,
        sr=sr,
        n_fft=400,
        hop_length=160,
    )
    bandwidth = librosa.feature.spectral_bandwidth(
        y=audio,
        sr=sr,
        n_fft=400,
        hop_length=160,
    )
    rolloff = librosa.feature.spectral_rolloff(
        y=audio,
        sr=sr,
        n_fft=400,
        hop_length=160,
        roll_percent=0.85,
    )
    flatness = librosa.feature.spectral_flatness(
        y=audio,
        n_fft=400,
        hop_length=160,
    )

    voiced_ratio = np.array(
        [float(np.mean(rms > max(1e-4, float(np.median(rms)) * 0.5)))],
        dtype=np.float32,
    )
    duration_value = np.array([audio.shape[0] / float(sr)], dtype=np.float32)

    parts = [
        np.mean(mfcc, axis=1),
        np.std(mfcc, axis=1),
        np.mean(delta, axis=1),
        np.std(delta, axis=1),
        np.mean(delta2, axis=1),
        np.std(delta2, axis=1),
        np.mean(rms, axis=1),
        np.std(rms, axis=1),
        np.mean(zcr, axis=1),
        np.std(zcr, axis=1),
        np.mean(centroid, axis=1),
        np.std(centroid, axis=1),
        np.mean(bandwidth, axis=1),
        np.std(bandwidth, axis=1),
        np.mean(rolloff, axis=1),
        np.std(rolloff, axis=1),
        np.mean(flatness, axis=1),
        np.std(flatness, axis=1),
        voiced_ratio,
        duration_value,
    ]
    return np.concatenate([np.asarray(part, dtype=np.float32).ravel() for part in parts])


def cache_is_usable(cache_path: Path, audio_paths: list[str]) -> bool:
    if not cache_path.exists():
        return False
    try:
        cache = np.load(cache_path, allow_pickle=True)
    except Exception:
        return False
    cached_version = int(cache["embed_version"])
    cached_paths = cache["audio_paths"].tolist()
    return cached_version == EMBED_VERSION and cached_paths == audio_paths


def extract_embedding_worker(audio_path: str) -> np.ndarray:
    try:
        embedding = acoustic_embedding_from_path(audio_path)
        return {
            "audio_path": audio_path,
            "ok": True,
            "embedding": embedding,
            "error": "",
        }
    except Exception as exc:
        return {
            "audio_path": audio_path,
            "ok": False,
            "embedding": None,
            "error": f"{type(exc).__name__}: {exc}",
        }


def build_embeddings(
    rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], np.ndarray, list[dict[str, str]]]:
    audio_paths = [row["audio_path"] for row in rows]
    if cache_is_usable(EMBEDDING_CACHE_PATH, audio_paths):
        cache = np.load(EMBEDDING_CACHE_PATH, allow_pickle=True)
        return rows, cache["embeddings"], []

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    workers = max(1, min(8, (os.cpu_count() or 1) - 1))
    with ProcessPoolExecutor(max_workers=workers) as executor:
        results = list(
            executor.map(
                extract_embedding_worker,
                audio_paths,
                chunksize=16,
            )
        )

    kept_rows: list[dict[str, Any]] = []
    embeddings: list[np.ndarray] = []
    failures: list[dict[str, str]] = []
    for row, result in zip(rows, results):
        if result["ok"]:
            kept_rows.append(row)
            embeddings.append(result["embedding"])
        else:
            failures.append(
                {
                    "audio_path": result["audio_path"],
                    "error": result["error"],
                }
            )

    embedding_matrix = np.vstack(embeddings).astype(np.float32)
    np.savez_compressed(
        EMBEDDING_CACHE_PATH,
        embed_version=np.array(EMBED_VERSION, dtype=np.int32),
        audio_paths=np.array([row["audio_path"] for row in kept_rows], dtype=object),
        embeddings=embedding_matrix,
    )
    return kept_rows, embedding_matrix, failures


def target_keep_count(items: list[dict[str, Any]]) -> int:
    n = len(items)
    category_count = len({item["coverage_category"] for item in items})
    target = max(
        MIN_KEEP_PER_SPEAKER,
        math.ceil(n * KEEP_RATIO),
        math.ceil(math.sqrt(n) * SQRT_SCALE),
        category_count * 3,
    )
    return min(n, MAX_KEEP_PER_SPEAKER, target)


def select_anchor_indices(items: list[dict[str, Any]]) -> list[int]:
    target = target_keep_count(items)
    if len(items) <= target:
        return list(range(len(items)))

    categories = sorted({item["coverage_category"] for item in items})
    duration_bins = sorted({duration_bin(float(item["duration_sec"])) for item in items})
    text_bins = sorted({text_length_bin(item["text"]) for item in items})
    punct_bins = sorted(
        {
            punct
            for item in items
            for punct in punctuation_classes(item["text"])
        }
    )

    selected: list[int] = []
    selected_set: set[int] = set()

    def choose_best(predicate) -> None:
        if len(selected) >= target:
            return
        candidates = [idx for idx, item in enumerate(items) if predicate(item)]
        candidates = [idx for idx in candidates if idx not in selected_set]
        if not candidates:
            return
        best_idx = max(
            candidates,
            key=lambda idx: (
                len(punctuation_classes(items[idx]["text"])),
                len(items[idx]["text"]),
                float(items[idx]["duration_sec"]),
                items[idx]["audio_path"],
            ),
        )
        selected.append(best_idx)
        selected_set.add(best_idx)

    for category in categories:
        choose_best(lambda item, category=category: item["coverage_category"] == category)
    for bucket in duration_bins:
        choose_best(lambda item, bucket=bucket: duration_bin(float(item["duration_sec"])) == bucket)
    for bucket in text_bins:
        choose_best(lambda item, bucket=bucket: text_length_bin(item["text"]) == bucket)
    for punct in punct_bins:
        choose_best(lambda item, punct=punct: punct in punctuation_classes(item["text"]))

    return selected


def medoid_indices_for_clusters(
    embeddings: np.ndarray,
    cluster_count: int,
) -> list[int]:
    if embeddings.shape[0] <= cluster_count:
        return list(range(embeddings.shape[0]))

    scaler = StandardScaler()
    scaled = scaler.fit_transform(embeddings)
    kmeans = KMeans(
        n_clusters=cluster_count,
        n_init=10,
        random_state=20260316,
    )
    labels = kmeans.fit_predict(scaled)
    centers = kmeans.cluster_centers_

    selected: list[int] = []
    for cluster_id in range(cluster_count):
        member_indices = np.where(labels == cluster_id)[0]
        if member_indices.size == 0:
            continue
        member_vectors = scaled[member_indices]
        center = centers[cluster_id]
        best_local_idx = int(
            member_indices[np.argmin(np.sum((member_vectors - center) ** 2, axis=1))]
        )
        selected.append(best_local_idx)
    return selected


def select_indices_for_speaker(items: list[dict[str, Any]], embeddings: np.ndarray) -> list[int]:
    target = target_keep_count(items)
    if len(items) <= target:
        return list(range(len(items)))

    anchor_indices = select_anchor_indices(items)
    anchor_set = set(anchor_indices)
    remaining_budget = target - len(anchor_indices)
    if remaining_budget <= 0:
        return sorted(anchor_indices)[:target]

    remaining_indices = [idx for idx in range(len(items)) if idx not in anchor_set]
    if not remaining_indices:
        return sorted(anchor_indices)

    clustered_local_indices = medoid_indices_for_clusters(
        embeddings[remaining_indices],
        min(remaining_budget, len(remaining_indices)),
    )
    cluster_indices = [remaining_indices[idx] for idx in clustered_local_indices]

    chosen = sorted(anchor_set.union(cluster_indices))
    if len(chosen) < target:
        extra_indices = [idx for idx in remaining_indices if idx not in cluster_indices]
        extra_sorted = sorted(
            extra_indices,
            key=lambda idx: (
                len(items[idx]["text"]),
                float(items[idx]["duration_sec"]),
            ),
            reverse=True,
        )
        for idx in extra_sorted:
            if len(chosen) >= target:
                break
            chosen.append(idx)
    return sorted(chosen[:target])


def materialize_rows(rows: list[dict[str, Any]]) -> None:
    NEW_CURATED_DIR.mkdir(parents=True, exist_ok=True)
    for row in rows:
        src_audio = ROOT / row["current_audio_path"]
        src_text = ROOT / row["current_text_path"]
        dst_audio = ROOT / row["audio_path"]
        dst_text = ROOT / row["text_path"]
        dst_audio.parent.mkdir(parents=True, exist_ok=True)
        dst_text.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_audio, dst_audio)
        shutil.copy2(src_text, dst_text)


def build_pruned_rows(
    rows: list[dict[str, Any]],
    embeddings: np.ndarray,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped_indices: dict[str, list[int]] = defaultdict(list)
    for idx, row in enumerate(rows):
        grouped_indices[row["speaker_id"]].append(idx)

    new_rows: list[dict[str, Any]] = []
    speaker_summaries: list[dict[str, Any]] = []
    full_category_cover = 0

    for speaker_rank, speaker_id in enumerate(sorted(grouped_indices), start=1):
        speaker_indices = grouped_indices[speaker_id]
        speaker_rows = [rows[idx] for idx in speaker_indices]
        speaker_embeddings = embeddings[speaker_indices]
        keep_local_indices = select_indices_for_speaker(speaker_rows, speaker_embeddings)
        kept_rows = [speaker_rows[idx] for idx in keep_local_indices]

        candidate_categories = {row["coverage_category"] for row in speaker_rows}
        kept_categories = {row["coverage_category"] for row in kept_rows}
        if kept_categories == candidate_categories:
            full_category_cover += 1

        speaker_summaries.append(
            {
                "speaker_id": speaker_id,
                "candidate_count": len(speaker_rows),
                "selected_count": len(kept_rows),
                "category_count": len(candidate_categories),
                "selected_category_count": len(kept_categories),
            }
        )

        source_root = speaker_rows[0]["source"]
        for item_rank, row in enumerate(kept_rows, start=1):
            relative_audio = relative_within_curated_root(row["audio_path"], source_root)
            relative_text = relative_within_curated_root(row["text_path"], source_root)
            dst_audio = NEW_CURATED_DIR / relative_audio
            dst_text = NEW_CURATED_DIR / relative_text
            new_row = dict(row)
            new_row["current_audio_path"] = row["audio_path"]
            new_row["current_text_path"] = row["text_path"]
            new_row["audio_path"] = relpath(dst_audio)
            new_row["text_path"] = relpath(dst_text)
            new_row["source"] = relpath(NEW_CURATED_DIR)
            new_row["speaker_rank"] = speaker_rank
            new_row["item_rank_within_speaker"] = item_rank
            new_row["selection_reason"] = (
                f"{row['selection_reason']};acoustic_embedding_cluster_prune_v1"
            )
            new_rows.append(new_row)

    summary = {
        "speaker_count": len(speaker_summaries),
        "item_count_before": len(rows),
        "item_count_after": len(new_rows),
        "full_category_cover_speakers": full_category_cover,
        "speaker_summaries": speaker_summaries,
    }
    return new_rows, summary


def main() -> None:
    rows = load_jsonl(SOURCE_MANIFEST_PATH)
    if not rows:
        raise RuntimeError("Source clean manifest is empty.")
    if not all(str(row.get("source", "")).startswith("data/curated/") for row in rows):
        raise RuntimeError("Source clean manifest is not using a curated clean subset.")

    if SOURCE_MANIFEST_PATH.exists() and not BACKUP_MANIFEST_PATH.exists():
        shutil.copy2(SOURCE_MANIFEST_PATH, BACKUP_MANIFEST_PATH)

    rows, embeddings, failures = build_embeddings(rows)
    new_rows, summary = build_pruned_rows(rows, embeddings)
    materialize_rows(new_rows)
    write_jsonl(SOURCE_MANIFEST_PATH, new_rows)
    write_json(
        REPORT_PATH,
        {
            "status": "rebuilt",
            "selection_reason": "acoustic_embedding_cluster_prune_v1",
            "source_manifest_backup": relpath(BACKUP_MANIFEST_PATH),
            "embedding_cache_path": relpath(EMBEDDING_CACHE_PATH),
            "curated_root": relpath(NEW_CURATED_DIR),
            "embedding_failures": failures,
            "embedding_failure_count": len(failures),
            **summary,
        },
    )

    print(
        json.dumps(
            {
                "speaker_count": summary["speaker_count"],
                "item_count_before": summary["item_count_before"],
                "item_count_after": summary["item_count_after"],
                "embedding_failure_count": len(failures),
                "curated_root": relpath(NEW_CURATED_DIR),
                "manifest_path": relpath(SOURCE_MANIFEST_PATH),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
