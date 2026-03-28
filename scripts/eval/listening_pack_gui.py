from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import sounddevice as sd
import soundfile as sf
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BETTER_OUTPUT_CHOICES = ["tie", "uncertain"]
DEFAULT_SOURCE_RETENTION_SCALE = ["excellent", "good", "fair", "weak", "lost"]
DEFAULT_PROBLEM_SEVERITY_SCALE = ["none", "slight", "moderate", "heavy", "extreme"]
DEFAULT_DECISION_TAG_EXAMPLES = [
    "better_source_retention",
    "less_interference_leak",
    "steadier_volume",
    "less_artifact",
    "prefer_silence_over_leak",
]
EXPORT_SUMMARY_NAME = "listening_results_summary.json"
LEGACY_PACK_FORMAT = "legacy_ab_v1"
MULTI_PACK_FORMAT = "multi_candidate_v1"
RESERVED_AUDIO_NAMES = {"mixture.wav", "reference.wav", "target.wav"}
RATING_DIMENSIONS = [
    ("source_retention", "源保留", DEFAULT_SOURCE_RETENTION_SCALE),
    ("interference_leak", "干扰泄漏", DEFAULT_PROBLEM_SEVERITY_SCALE),
    ("volume_fluctuation", "音量波动", DEFAULT_PROBLEM_SEVERITY_SCALE),
    ("artifact", "伪影", DEFAULT_PROBLEM_SEVERITY_SCALE),
]
VALUE_LABELS = {
    "excellent": "极好",
    "good": "良好",
    "fair": "一般",
    "weak": "偏弱",
    "lost": "丢失",
    "none": "无",
    "slight": "轻微",
    "moderate": "中等",
    "heavy": "明显",
    "extreme": "严重",
}


def serialize_repo_path(path: Path | None) -> str:
    if path is None:
        return ""
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return resolved.as_posix()


def write_utf8_text(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Browse, score, and export a listening pack.")
    parser.add_argument(
        "--pack-dir",
        type=Path,
        default=None,
        help="Optional listening pack directory to load on startup.",
    )
    return parser.parse_args()


def parse_json_list(raw: str, *, field_name: str) -> list[str]:
    value = raw.strip()
    if not value:
        return []
    parsed = json.loads(value)
    if not isinstance(parsed, list):
        raise ValueError(f"{field_name} must be a JSON array.")
    items: list[str] = []
    for item in parsed:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} must contain strings only.")
        normalized = item.strip()
        if normalized:
            items.append(normalized)
    return items


def parse_json_dict(raw: str, *, field_name: str) -> dict[str, Any]:
    value = raw.strip()
    if not value:
        return {}
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError(f"{field_name} must be a JSON object.")
    normalized: dict[str, Any] = {}
    for key, item in parsed.items():
        if not isinstance(key, str):
            raise ValueError(f"{field_name} keys must be strings.")
        normalized[key.strip()] = item
    return normalized


def split_decision_tags(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def join_decision_tags(checked_tags: list[str], extra_tags: str) -> str:
    merged = checked_tags + split_decision_tags(extra_tags)
    deduped: list[str] = []
    seen: set[str] = set()
    for item in merged:
        if item not in seen:
            deduped.append(item)
            seen.add(item)
    return ";".join(deduped)


def map_legacy_preferred_candidate(value: str) -> str:
    normalized = value.strip().lower()
    mapping = {
        "candidate_a": "file_a",
        "a": "file_a",
        "file_a": "file_a",
        "candidate_b": "file_b",
        "b": "file_b",
        "file_b": "file_b",
        "tie": "tie",
        "uncertain": "uncertain",
        "reject_both": "uncertain",
    }
    return mapping.get(normalized, "")


def infer_candidate_audio_names(sample_dir: Path) -> list[str]:
    return sorted(
        path.name
        for path in sample_dir.glob("*.wav")
        if path.name not in RESERVED_AUDIO_NAMES
    )


def build_legacy_note(row: dict[str, str]) -> str:
    parts: list[str] = []
    note_mapping = [
        ("speech_clarity_note", "语音清晰度"),
        ("interference_suppression_note", "干扰抑制"),
        ("artifact_note", "伪影"),
        ("overall_note", "总体备注"),
    ]
    for key, label in note_mapping:
        value = row.get(key, "").strip()
        if value:
            parts.append(f"{label}: {value}")
    return "\n".join(parts)


def candidate_sort_key(candidate_id: str) -> tuple[int, int | str]:
    if candidate_id == "file_a":
        return (0, 0)
    if candidate_id == "file_b":
        return (0, 1)
    match = re.fullmatch(r"candidate_(\d+)", candidate_id)
    if match:
        return (1, int(match.group(1)))
    return (2, candidate_id)


def format_candidate_display_name(candidate_id: str, blind_mode: bool) -> str:
    if candidate_id == "file_a":
        return "候选 A"
    if candidate_id == "file_b":
        return "候选 B"
    match = re.fullmatch(r"candidate_(\d+)", candidate_id)
    if match:
        return f"候选 {match.group(1)}"
    if blind_mode:
        return candidate_id.replace("_", " ").strip() or candidate_id
    return candidate_id


def parse_candidate_ratings(raw: str) -> dict[str, dict[str, str]]:
    parsed = parse_json_dict(raw, field_name="candidate_ratings_json")
    normalized: dict[str, dict[str, str]] = {}
    for candidate_id, item in parsed.items():
        if not isinstance(item, dict):
            raise ValueError("candidate_ratings_json values must be objects.")
        candidate_ratings: dict[str, str] = {}
        for key, value in item.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("candidate_ratings_json values must be string maps.")
            candidate_ratings[key.strip()] = value.strip()
        normalized[candidate_id.strip()] = candidate_ratings
    return normalized


@dataclass
class ListeningRow:
    sample_id: str
    recipe: str
    temporal_pattern: str
    target_present_ratio: str
    candidate_ids: list[str] = field(default_factory=list)
    candidate_audio_names: dict[str, str] = field(default_factory=dict)
    better_output: str = ""
    candidate_ratings: dict[str, dict[str, str]] = field(default_factory=dict)
    decision_tags: str = ""
    note: str = ""

    @classmethod
    def from_dict(cls, row: dict[str, str], sample_dir: Path) -> "ListeningRow":
        if "candidate_ids_json" in row and "candidate_audio_names_json" in row:
            candidate_ids = parse_json_list(row.get("candidate_ids_json", ""), field_name="candidate_ids_json")
            candidate_audio_names_raw = parse_json_dict(
                row.get("candidate_audio_names_json", ""),
                field_name="candidate_audio_names_json",
            )
            candidate_audio_names = {
                candidate_id: str(candidate_audio_names_raw.get(candidate_id, "")).strip()
                for candidate_id in candidate_ids
            }
            ratings = parse_candidate_ratings(row.get("candidate_ratings_json", ""))
            return cls(
                sample_id=row.get("sample_id", "").strip(),
                recipe=row.get("recipe", "").strip(),
                temporal_pattern=row.get("temporal_pattern", "").strip(),
                target_present_ratio=row.get("target_present_ratio", "").strip(),
                candidate_ids=candidate_ids,
                candidate_audio_names=candidate_audio_names,
                better_output=row.get("better_output", "").strip(),
                candidate_ratings=ratings,
                decision_tags=row.get("decision_tags", "").strip(),
                note=row.get("note", "").strip(),
            )

        if "file_a_name" in row and "file_b_name" in row:
            return cls(
                sample_id=row.get("sample_id", "").strip(),
                recipe=row.get("recipe", "").strip(),
                temporal_pattern=row.get("temporal_pattern", "").strip(),
                target_present_ratio=row.get("target_present_ratio", "").strip(),
                candidate_ids=["file_a", "file_b"],
                candidate_audio_names={
                    "file_a": row.get("file_a_name", "").strip(),
                    "file_b": row.get("file_b_name", "").strip(),
                },
                better_output=row.get("better_output", "").strip(),
                candidate_ratings={
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
                },
                decision_tags=row.get("decision_tags", "").strip(),
                note=row.get("note", "").strip(),
            )

        inferred_audio_names = infer_candidate_audio_names(sample_dir)
        candidate_ids = [f"candidate_{index + 1}" for index in range(len(inferred_audio_names))]
        candidate_audio_names = {
            candidate_id: audio_name
            for candidate_id, audio_name in zip(candidate_ids, inferred_audio_names)
        }
        return cls(
            sample_id=row.get("sample_id", "").strip(),
            recipe=row.get("recipe", "").strip(),
            temporal_pattern=row.get("temporal_pattern", "").strip(),
            target_present_ratio=row.get("target_present_ratio", "").strip(),
            candidate_ids=candidate_ids,
            candidate_audio_names=candidate_audio_names,
            better_output=map_legacy_preferred_candidate(row.get("preferred_candidate", "")),
            decision_tags="",
            note=build_legacy_note(row),
        )

    def ensure_candidate_consistency(self, sample_dir: Path) -> None:
        if self.candidate_ids and all(self.candidate_audio_names.get(candidate_id, "").strip() for candidate_id in self.candidate_ids):
            return

        inferred_audio_names = infer_candidate_audio_names(sample_dir)
        if not self.candidate_ids:
            self.candidate_ids = [f"candidate_{index + 1}" for index in range(len(inferred_audio_names))]
        for index, candidate_id in enumerate(self.candidate_ids):
            if self.candidate_audio_names.get(candidate_id, "").strip():
                continue
            if index < len(inferred_audio_names):
                self.candidate_audio_names[candidate_id] = inferred_audio_names[index]
        self.candidate_ids = [candidate_id for candidate_id in self.candidate_ids if self.candidate_audio_names.get(candidate_id, "").strip()]

    def ensure_rating_slots(self) -> None:
        for candidate_id in self.candidate_ids:
            ratings = self.candidate_ratings.setdefault(candidate_id, {})
            for metric_key, _label, _values in RATING_DIMENSIONS:
                ratings.setdefault(metric_key, "")

    def is_scored(self) -> bool:
        return bool(self.better_output.strip())

    def to_dict(self, pack_format: str) -> dict[str, str]:
        self.ensure_rating_slots()
        if pack_format == LEGACY_PACK_FORMAT and self.candidate_ids == ["file_a", "file_b"]:
            return {
                "sample_id": self.sample_id,
                "recipe": self.recipe,
                "temporal_pattern": self.temporal_pattern,
                "target_present_ratio": self.target_present_ratio,
                "file_a_name": self.candidate_audio_names.get("file_a", ""),
                "file_b_name": self.candidate_audio_names.get("file_b", ""),
                "better_output": self.better_output,
                "file_a_source_retention": self.candidate_ratings["file_a"]["source_retention"],
                "file_b_source_retention": self.candidate_ratings["file_b"]["source_retention"],
                "file_a_interference_leak": self.candidate_ratings["file_a"]["interference_leak"],
                "file_b_interference_leak": self.candidate_ratings["file_b"]["interference_leak"],
                "file_a_volume_fluctuation": self.candidate_ratings["file_a"]["volume_fluctuation"],
                "file_b_volume_fluctuation": self.candidate_ratings["file_b"]["volume_fluctuation"],
                "file_a_artifact": self.candidate_ratings["file_a"]["artifact"],
                "file_b_artifact": self.candidate_ratings["file_b"]["artifact"],
                "decision_tags": self.decision_tags,
                "note": self.note,
            }

        candidate_audio_names = {
            candidate_id: self.candidate_audio_names.get(candidate_id, "")
            for candidate_id in self.candidate_ids
        }
        candidate_ratings = {
            candidate_id: {
                metric_key: self.candidate_ratings.get(candidate_id, {}).get(metric_key, "")
                for metric_key, _label, _values in RATING_DIMENSIONS
            }
            for candidate_id in self.candidate_ids
        }
        return {
            "sample_id": self.sample_id,
            "recipe": self.recipe,
            "temporal_pattern": self.temporal_pattern,
            "target_present_ratio": self.target_present_ratio,
            "candidate_ids_json": json.dumps(self.candidate_ids, ensure_ascii=False),
            "candidate_audio_names_json": json.dumps(candidate_audio_names, ensure_ascii=False),
            "better_output": self.better_output,
            "candidate_ratings_json": json.dumps(candidate_ratings, ensure_ascii=False),
            "decision_tags": self.decision_tags,
            "note": self.note,
        }


def build_fieldnames(pack_format: str) -> list[str]:
    if pack_format == LEGACY_PACK_FORMAT:
        return [
            "sample_id",
            "recipe",
            "temporal_pattern",
            "target_present_ratio",
            "file_a_name",
            "file_b_name",
            "better_output",
            "file_a_source_retention",
            "file_b_source_retention",
            "file_a_interference_leak",
            "file_b_interference_leak",
            "file_a_volume_fluctuation",
            "file_b_volume_fluctuation",
            "file_a_artifact",
            "file_b_artifact",
            "decision_tags",
            "note",
        ]
    return [
        "sample_id",
        "recipe",
        "temporal_pattern",
        "target_present_ratio",
        "candidate_ids_json",
        "candidate_audio_names_json",
        "better_output",
        "candidate_ratings_json",
        "decision_tags",
        "note",
    ]


def load_rubric(pack_dir: Path) -> dict[str, Any]:
    rubric_path = pack_dir / "listening_rubric.json"
    if not rubric_path.exists():
        return {
            "pack_format": LEGACY_PACK_FORMAT,
            "better_output_choices": DEFAULT_BETTER_OUTPUT_CHOICES,
            "source_retention_scale": DEFAULT_SOURCE_RETENTION_SCALE,
            "problem_severity_scale": DEFAULT_PROBLEM_SEVERITY_SCALE,
            "decision_tag_examples": DEFAULT_DECISION_TAG_EXAMPLES,
        }
    data = json.loads(rubric_path.read_text(encoding="utf-8"))
    return {
        "pack_format": data.get("pack_format", LEGACY_PACK_FORMAT),
        "better_output_choices": data.get("better_output_choices", DEFAULT_BETTER_OUTPUT_CHOICES),
        "source_retention_scale": data.get("source_retention_scale", DEFAULT_SOURCE_RETENTION_SCALE),
        "problem_severity_scale": data.get("problem_severity_scale", DEFAULT_PROBLEM_SEVERITY_SCALE),
        "decision_tag_examples": data.get("decision_tag_examples", DEFAULT_DECISION_TAG_EXAMPLES),
    }


def load_listening_rows(pack_dir: Path) -> tuple[list[ListeningRow], str]:
    csv_path = pack_dir / "listening_sheet.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing listening sheet: {csv_path}")

    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        fieldnames = set(reader.fieldnames or [])
        if "candidate_ids_json" in fieldnames:
            pack_format = MULTI_PACK_FORMAT
        else:
            pack_format = LEGACY_PACK_FORMAT

        rows: list[ListeningRow] = []
        for row in reader:
            sample_id = row.get("sample_id", "").strip()
            sample_dir = pack_dir / sample_id
            listening_row = ListeningRow.from_dict(row, sample_dir)
            listening_row.ensure_candidate_consistency(sample_dir)
            listening_row.ensure_rating_slots()
            rows.append(listening_row)
        return rows, pack_format


def write_listening_rows(pack_dir: Path, rows: list[ListeningRow], pack_format: str) -> None:
    csv_path = pack_dir / "listening_sheet.csv"
    fieldnames = build_fieldnames(pack_format)
    with csv_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.to_dict(pack_format))


class ListeningPackApp:
    def __init__(self, root: tk.Tk, initial_pack_dir: Path | None = None) -> None:
        self.root = root
        self.root.title("Listening Pack GUI")
        self.root.geometry("1760x1020")

        self.pack_dir: Path | None = None
        self.pack_format = LEGACY_PACK_FORMAT
        self.rows_by_id: dict[str, ListeningRow] = {}
        self.filtered_ids: list[str] = []
        self.current_sample_id: str | None = None
        self.current_candidate_ids: list[str] = []
        self.sample_gain_cache: dict[str, float] = {}
        self.form_loading = False
        self.blind_mode = False

        self.better_output_choices = DEFAULT_BETTER_OUTPUT_CHOICES
        self.source_retention_scale = DEFAULT_SOURCE_RETENTION_SCALE
        self.problem_severity_scale = DEFAULT_PROBLEM_SEVERITY_SCALE
        self.decision_tag_examples = DEFAULT_DECISION_TAG_EXAMPLES

        self.pack_dir_var = tk.StringVar()
        self.normalize_peaks_var = tk.BooleanVar(value=False)
        self.target_peak_var = tk.StringVar(value="0.80")
        self.playback_gain_var = tk.DoubleVar(value=80.0)
        self.recipe_filter_var = tk.StringVar(value="全部")
        self.pattern_filter_var = tk.StringVar(value="全部")
        self.status_filter_var = tk.StringVar(value="全部")
        self.better_output_var = tk.StringVar(value="")
        self.note_text: tk.Text | None = None
        self.status_text_var = tk.StringVar(value="未加载盲听包")
        self.sample_info_var = tk.StringVar(value="")
        self.progress_var = tk.StringVar(value="0 / 0 已评分")
        self.blind_mode_var = tk.StringVar(value="模式：未加载")
        self.extra_tags_var = tk.StringVar()
        self.tag_vars: dict[str, tk.BooleanVar] = {}
        self.candidate_rating_vars: dict[str, dict[str, tk.StringVar]] = {}
        self.status_filter_choice_map: dict[str, str] = {}

        self.recipe_filter_box: ttk.Combobox | None = None
        self.pattern_filter_box: ttk.Combobox | None = None
        self.status_filter_box: ttk.Combobox | None = None
        self.sample_listbox: tk.Listbox | None = None
        self.tag_container: ttk.Frame | None = None
        self.content_paned: ttk.Panedwindow | None = None
        self.right_canvas: tk.Canvas | None = None
        self.right_scrollbar: ttk.Scrollbar | None = None
        self.right_scroll_frame: ttk.Frame | None = None
        self.playback_buttons_frame: ttk.LabelFrame | None = None
        self.decision_frame: ttk.LabelFrame | None = None
        self.rating_frame: ttk.LabelFrame | None = None

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        if initial_pack_dir is not None:
            self.load_pack(initial_pack_dir)

    def _build_ui(self) -> None:
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(2, weight=1)

        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.grid(row=0, column=0, sticky="ew")
        top_frame.columnconfigure(1, weight=1)

        ttk.Label(top_frame, text="盲听包文件夹").grid(row=0, column=0, sticky="w")
        ttk.Entry(top_frame, textvariable=self.pack_dir_var).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top_frame, text="选择文件夹", command=self.choose_pack_dir).grid(row=0, column=2, padx=4)
        ttk.Button(top_frame, text="加载", command=self.load_pack_from_entry).grid(row=0, column=3, padx=4)
        ttk.Button(top_frame, text="一键导出", command=self.export_scores).grid(row=0, column=4, padx=4)

        playback_frame = ttk.LabelFrame(self.root, text="播放选项", padding=10)
        playback_frame.grid(row=1, column=0, sticky="ew", padx=10)
        playback_frame.columnconfigure(6, weight=1)

        ttk.Checkbutton(
            playback_frame,
            text="同一样本共享峰值增益",
            variable=self.normalize_peaks_var,
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(playback_frame, text="目标组峰值").grid(row=0, column=1, sticky="w", padx=(12, 4))
        ttk.Entry(playback_frame, textvariable=self.target_peak_var, width=8).grid(row=0, column=2, sticky="w")
        ttk.Label(playback_frame, text="总播放音量").grid(row=0, column=3, sticky="w", padx=(12, 4))
        ttk.Scale(
            playback_frame,
            from_=10.0,
            to=100.0,
            variable=self.playback_gain_var,
            orient="horizontal",
        ).grid(row=0, column=4, sticky="ew")
        ttk.Label(playback_frame, textvariable=self.blind_mode_var).grid(row=0, column=5, sticky="e", padx=(12, 0))
        ttk.Label(playback_frame, textvariable=self.status_text_var).grid(row=0, column=6, sticky="e")

        filter_frame = ttk.LabelFrame(self.root, text="分组与筛选", padding=10)
        filter_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))
        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)
        filter_frame.columnconfigure(5, weight=1)
        filter_frame.rowconfigure(1, weight=1)

        ttk.Label(filter_frame, text="配方分组").grid(row=0, column=0, sticky="w")
        self.recipe_filter_box = ttk.Combobox(
            filter_frame,
            textvariable=self.recipe_filter_var,
            state="readonly",
            values=["全部"],
        )
        self.recipe_filter_box.grid(row=0, column=1, sticky="ew", padx=(4, 12))
        self.recipe_filter_box.bind("<<ComboboxSelected>>", lambda _event: self.apply_filters())

        ttk.Label(filter_frame, text="时序模式").grid(row=0, column=2, sticky="w")
        self.pattern_filter_box = ttk.Combobox(
            filter_frame,
            textvariable=self.pattern_filter_var,
            state="readonly",
            values=["全部"],
        )
        self.pattern_filter_box.grid(row=0, column=3, sticky="ew", padx=(4, 12))
        self.pattern_filter_box.bind("<<ComboboxSelected>>", lambda _event: self.apply_filters())

        ttk.Label(filter_frame, text="状态").grid(row=0, column=4, sticky="w")
        self.status_filter_box = ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter_var,
            state="readonly",
            values=["全部", "未评分", "已评分", "打平", "都不行"],
        )
        self.status_filter_box.grid(row=0, column=5, sticky="ew", padx=(4, 0))
        self.status_filter_box.bind("<<ComboboxSelected>>", lambda _event: self.apply_filters())

        content = ttk.Panedwindow(filter_frame, orient="horizontal")
        content.grid(row=1, column=0, columnspan=6, sticky="nsew", pady=(10, 0))
        self.content_paned = content

        left_frame = ttk.Frame(content, padding=(0, 0, 10, 0))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        ttk.Label(left_frame, textvariable=self.progress_var).grid(row=0, column=0, sticky="w", pady=(0, 6))
        self.sample_listbox = tk.Listbox(left_frame, exportselection=False, width=56)
        self.sample_listbox.grid(row=1, column=0, sticky="nsew")
        self.sample_listbox.bind("<<ListboxSelect>>", self.on_sample_selected)
        content.add(left_frame, weight=2)

        right_container = ttk.Frame(content)
        right_container.columnconfigure(0, weight=1)
        right_container.rowconfigure(0, weight=1)
        self.right_canvas = tk.Canvas(right_container, highlightthickness=0)
        self.right_canvas.grid(row=0, column=0, sticky="nsew")
        self.right_scrollbar = ttk.Scrollbar(
            right_container,
            orient="vertical",
            command=self.right_canvas.yview,
        )
        self.right_scrollbar.grid(row=0, column=1, sticky="ns")
        self.right_canvas.configure(yscrollcommand=self.right_scrollbar.set)

        right_frame = ttk.Frame(self.right_canvas, padding=(10, 0, 0, 0))
        self.right_scroll_frame = right_frame
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(4, weight=1)
        self.right_canvas.create_window((0, 0), window=right_frame, anchor="nw")
        self.right_canvas.bind(
            "<Configure>",
            lambda event: self.right_canvas.itemconfigure("all", width=event.width),
        )
        right_frame.bind(
            "<Configure>",
            lambda _event: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all")),
        )
        self.right_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        content.add(right_container, weight=3)
        self.root.after(0, lambda: self.content_paned.sashpos(0, 500) if self.content_paned is not None else None)

        ttk.Label(right_frame, textvariable=self.sample_info_var, justify="left").grid(row=0, column=0, sticky="ew")

        self.playback_buttons_frame = ttk.LabelFrame(right_frame, text="播放", padding=10)
        self.playback_buttons_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

        self.decision_frame = ttk.LabelFrame(right_frame, text="主判定", padding=10)
        self.decision_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))

        self.rating_frame = ttk.LabelFrame(right_frame, text="标签化分档评估", padding=10)
        self.rating_frame.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        detail_frame = ttk.LabelFrame(right_frame, text="决策标签与备注", padding=10)
        detail_frame.grid(row=4, column=0, sticky="nsew", pady=(10, 0))
        detail_frame.columnconfigure(0, weight=1)
        detail_frame.rowconfigure(3, weight=1)

        ttk.Label(
            detail_frame,
            text="这块不是再选谁赢，而是补充“为什么这样选”。勾标签写共性原因，备注写这一条样本的特殊现象。",
            justify="left",
            wraplength=820,
        ).grid(row=0, column=0, sticky="ew")

        self.tag_container = ttk.Frame(detail_frame)
        self.tag_container.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self._rebuild_tag_checkboxes()

        extra_tag_frame = ttk.Frame(detail_frame)
        extra_tag_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        extra_tag_frame.columnconfigure(1, weight=1)
        ttk.Label(extra_tag_frame, text="额外标签").grid(row=0, column=0, sticky="w")
        ttk.Entry(extra_tag_frame, textvariable=self.extra_tags_var).grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.note_text = tk.Text(detail_frame, height=10, wrap="word")
        self.note_text.grid(row=3, column=0, sticky="nsew", pady=(10, 0))

        nav_frame = ttk.Frame(right_frame)
        nav_frame.grid(row=5, column=0, sticky="ew", pady=(10, 0))
        nav_frame.columnconfigure(2, weight=1)
        ttk.Button(nav_frame, text="上一条", command=self.select_previous_sample).grid(row=0, column=0, padx=4)
        ttk.Button(nav_frame, text="下一条", command=self.select_next_sample).grid(row=0, column=1, padx=4)
        ttk.Button(nav_frame, text="保存当前到内存", command=self.commit_current_form).grid(row=0, column=3, padx=4)

        self._rebuild_dynamic_sections([])

    def _rebuild_dynamic_sections(self, candidate_ids: list[str]) -> None:
        self.current_candidate_ids = list(candidate_ids)
        self.candidate_rating_vars = {
            candidate_id: {
                metric_key: tk.StringVar()
                for metric_key, _label, _values in RATING_DIMENSIONS
            }
            for candidate_id in candidate_ids
        }

        self._rebuild_playback_buttons(candidate_ids)
        self._rebuild_decision_buttons(candidate_ids)
        self._rebuild_rating_matrix(candidate_ids)

    def _rebuild_playback_buttons(self, candidate_ids: list[str]) -> None:
        if self.playback_buttons_frame is None:
            return
        for child in self.playback_buttons_frame.winfo_children():
            child.destroy()

        button_specs: list[tuple[str, str]] = [
            ("混合音频", "mixture.wav"),
            ("参考音频", "reference.wav"),
        ]
        for candidate_id in candidate_ids:
            button_specs.append((format_candidate_display_name(candidate_id, self.blind_mode), candidate_id))
        button_specs.append(("目标真值", "target.wav"))

        for index, (label, key) in enumerate(button_specs):
            ttk.Button(
                self.playback_buttons_frame,
                text=label,
                command=lambda value=key: self.play_sample_audio(value),
            ).grid(row=index // 4, column=index % 4, padx=4, pady=4, sticky="w")
        stop_index = len(button_specs)
        ttk.Button(self.playback_buttons_frame, text="停止", command=self.stop_audio).grid(
            row=stop_index // 4,
            column=stop_index % 4,
            padx=4,
            pady=4,
            sticky="w",
        )

    def _rebuild_decision_buttons(self, candidate_ids: list[str]) -> None:
        if self.decision_frame is None:
            return
        for child in self.decision_frame.winfo_children():
            child.destroy()

        choice_specs: list[tuple[str, str]] = []
        for candidate_id in candidate_ids:
            choice_specs.append((candidate_id, f"{format_candidate_display_name(candidate_id, self.blind_mode)} 更好"))
        choice_specs.extend(
            [
                ("tie", "打平"),
                ("uncertain", "都不行"),
            ]
        )

        for index, (value, label) in enumerate(choice_specs):
            ttk.Radiobutton(
                self.decision_frame,
                text=label,
                value=value,
                variable=self.better_output_var,
            ).grid(row=index // 4, column=index % 4, sticky="w", padx=4, pady=2)

    def _rebuild_rating_matrix(self, candidate_ids: list[str]) -> None:
        if self.rating_frame is None:
            return
        for child in self.rating_frame.winfo_children():
            child.destroy()

        self.rating_frame.columnconfigure(0, weight=0)
        ttk.Label(self.rating_frame, text="维度").grid(row=0, column=0, sticky="w")
        for column_index, candidate_id in enumerate(candidate_ids, start=1):
            self.rating_frame.columnconfigure(column_index, weight=1)
            ttk.Label(
                self.rating_frame,
                text=format_candidate_display_name(candidate_id, self.blind_mode),
            ).grid(row=0, column=column_index, sticky="w")

        for row_index, (metric_key, label, _values) in enumerate(RATING_DIMENSIONS, start=1):
            ttk.Label(self.rating_frame, text=label).grid(row=row_index, column=0, sticky="w", pady=2)
            for column_index, candidate_id in enumerate(candidate_ids, start=1):
                frame = ttk.Frame(self.rating_frame)
                frame.grid(row=row_index, column=column_index, sticky="w", padx=4, pady=2)
                variable = self.candidate_rating_vars[candidate_id][metric_key]
                ttk.Radiobutton(frame, text="未填", value="", variable=variable).pack(side="left", padx=(0, 6))
                values = (
                    self.source_retention_scale
                    if metric_key == "source_retention"
                    else self.problem_severity_scale
                )
                for value in values:
                    ttk.Radiobutton(
                        frame,
                        text=VALUE_LABELS.get(value, value),
                        value=value,
                        variable=variable,
                    ).pack(side="left", padx=(0, 6))

    def choose_pack_dir(self) -> None:
        selected = filedialog.askdirectory(title="选择盲听包文件夹")
        if selected:
            self.pack_dir_var.set(selected)

    def load_pack_from_entry(self) -> None:
        raw = self.pack_dir_var.get().strip()
        if not raw:
            messagebox.showwarning("未选择文件夹", "先选择一个盲听包文件夹。")
            return
        self.load_pack(Path(raw))

    def load_pack(self, pack_dir: Path) -> None:
        try:
            self.commit_current_form()
            pack_dir = pack_dir.resolve()
            rows, pack_format = load_listening_rows(pack_dir)
            rubric = load_rubric(pack_dir)
        except Exception as exc:
            messagebox.showerror("加载失败", str(exc))
            return

        self.stop_audio()
        self.pack_dir = pack_dir
        self.pack_format = pack_format
        self.pack_dir_var.set(str(pack_dir))
        self.rows_by_id = {row.sample_id: row for row in rows}
        self.sample_gain_cache = {}
        self.current_sample_id = None
        self.better_output_choices = rubric["better_output_choices"]
        self.source_retention_scale = rubric["source_retention_scale"]
        self.problem_severity_scale = rubric["problem_severity_scale"]
        self.decision_tag_examples = rubric["decision_tag_examples"]
        self.blind_mode = (pack_dir / "blind_key.json").exists()
        self.blind_mode_var.set("模式：盲听包" if self.blind_mode else "模式：普通包")

        recipes = sorted({row.recipe for row in rows if row.recipe})
        patterns = sorted({row.temporal_pattern for row in rows if row.temporal_pattern})
        if self.recipe_filter_box is not None:
            self.recipe_filter_box["values"] = ["全部"] + recipes
        if self.pattern_filter_box is not None:
            self.pattern_filter_box["values"] = ["全部"] + patterns
        self._rebuild_status_filter_choices(rows)
        self.recipe_filter_var.set("全部")
        self.pattern_filter_var.set("全部")
        self.status_filter_var.set("全部")

        self._rebuild_tag_checkboxes()
        self._rebuild_dynamic_sections(self._default_candidate_ids())
        self.apply_filters()
        self.status_text_var.set(f"已加载 {len(rows)} 条样本")

    def _default_candidate_ids(self) -> list[str]:
        if not self.rows_by_id:
            return []
        first_row = self.rows_by_id[sorted(self.rows_by_id)[0]]
        return list(first_row.candidate_ids)

    def _rebuild_status_filter_choices(self, rows: list[ListeningRow]) -> None:
        candidate_ids: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for candidate_id in row.candidate_ids:
                if candidate_id in seen:
                    continue
                candidate_ids.append(candidate_id)
                seen.add(candidate_id)
        candidate_ids.sort(key=candidate_sort_key)

        self.status_filter_choice_map = {
            format_candidate_display_name(candidate_id, self.blind_mode) + " 更好": candidate_id
            for candidate_id in candidate_ids
        }
        values = ["全部", "未评分", "已评分"] + list(self.status_filter_choice_map) + ["打平", "都不行"]
        if self.status_filter_box is not None:
            self.status_filter_box["values"] = values

    def _rebuild_tag_checkboxes(self) -> None:
        if self.tag_container is None:
            return
        for child in self.tag_container.winfo_children():
            child.destroy()
        self.tag_vars = {}
        for idx, tag_name in enumerate(self.decision_tag_examples):
            var = tk.BooleanVar(value=False)
            self.tag_vars[tag_name] = var
            ttk.Checkbutton(self.tag_container, text=tag_name, variable=var).grid(
                row=idx // 2,
                column=idx % 2,
                sticky="w",
                padx=4,
                pady=2,
            )

    def apply_filters(self) -> None:
        rows = list(self.rows_by_id.values())
        recipe_filter = self.recipe_filter_var.get()
        pattern_filter = self.pattern_filter_var.get()
        status_filter = self.status_filter_var.get()

        filtered: list[str] = []
        for row in rows:
            if recipe_filter != "全部" and row.recipe != recipe_filter:
                continue
            if pattern_filter != "全部" and row.temporal_pattern != pattern_filter:
                continue
            if status_filter == "未评分" and row.is_scored():
                continue
            if status_filter == "已评分" and not row.is_scored():
                continue
            if status_filter == "打平" and row.better_output != "tie":
                continue
            if status_filter == "都不行" and row.better_output != "uncertain":
                continue
            expected_choice = self.status_filter_choice_map.get(status_filter)
            if expected_choice is not None and row.better_output != expected_choice:
                continue
            filtered.append(row.sample_id)

        filtered.sort()
        self.filtered_ids = filtered
        self._refresh_sample_listbox()
        if self.filtered_ids:
            target_id = self.current_sample_id if self.current_sample_id in self.filtered_ids else self.filtered_ids[0]
            self.select_sample_by_id(target_id)
        else:
            self.current_sample_id = None
            self.sample_info_var.set("当前筛选结果为空")
            self.progress_var.set("0 / 0 已评分")

    def _refresh_sample_listbox(self) -> None:
        if self.sample_listbox is None:
            return
        self.sample_listbox.delete(0, tk.END)
        for sample_id in self.filtered_ids:
            row = self.rows_by_id[sample_id]
            status = self._status_symbol(row)
            self.sample_listbox.insert(
                tk.END,
                f"{status} {row.sample_id} | {row.recipe} | {row.temporal_pattern}",
            )
        scored_count = sum(1 for row in self.rows_by_id.values() if row.is_scored())
        total_count = len(self.rows_by_id)
        self.progress_var.set(f"{scored_count} / {total_count} 已评分")

    def _status_symbol(self, row: ListeningRow) -> str:
        if row.better_output == "tie":
            return "="
        if row.better_output == "uncertain":
            return "X"
        if row.better_output == "file_a":
            return "A"
        if row.better_output == "file_b":
            return "B"
        match = re.fullmatch(r"candidate_(\d+)", row.better_output or "")
        if match:
            return match.group(1)
        if row.better_output:
            return "*"
        return "·"

    def on_sample_selected(self, _event: Any) -> None:
        if self.sample_listbox is None:
            return
        selection = self.sample_listbox.curselection()
        if not selection:
            return
        sample_id = self.filtered_ids[selection[0]]
        self.select_sample_by_id(sample_id)

    def select_sample_by_id(self, sample_id: str) -> None:
        if sample_id not in self.rows_by_id:
            return
        self.commit_current_form()
        self.current_sample_id = sample_id
        if self.sample_listbox is not None and sample_id in self.filtered_ids:
            index = self.filtered_ids.index(sample_id)
            self.sample_listbox.selection_clear(0, tk.END)
            self.sample_listbox.selection_set(index)
            self.sample_listbox.see(index)
        self.render_current_sample()

    def render_current_sample(self) -> None:
        if self.current_sample_id is None:
            return
        row = self.rows_by_id[self.current_sample_id]
        sample_dir = self._current_sample_dir()
        if sample_dir is not None:
            row.ensure_candidate_consistency(sample_dir)
        row.ensure_rating_slots()

        if row.candidate_ids != self.current_candidate_ids:
            self._rebuild_dynamic_sections(row.candidate_ids)

        self.form_loading = True
        candidate_info_lines = [
            f"{format_candidate_display_name(candidate_id, self.blind_mode)} 文件: {row.candidate_audio_names.get(candidate_id, '未识别')}"
            for candidate_id in row.candidate_ids
        ]
        self.sample_info_var.set(
            "\n".join(
                [
                    f"样本 ID: {row.sample_id}",
                    f"配方分组: {row.recipe}",
                    f"时序模式: {row.temporal_pattern}",
                    f"目标出现比例: {row.target_present_ratio}",
                    *candidate_info_lines,
                    f"盲听包目录: {self.pack_dir}",
                ]
            )
        )
        self.better_output_var.set(row.better_output)
        for candidate_id in row.candidate_ids:
            ratings = row.candidate_ratings.get(candidate_id, {})
            for metric_key, _label, _values in RATING_DIMENSIONS:
                self.candidate_rating_vars[candidate_id][metric_key].set(ratings.get(metric_key, ""))

        known_tags = set(self.decision_tag_examples)
        parsed_tags = split_decision_tags(row.decision_tags)
        for tag_name, var in self.tag_vars.items():
            var.set(tag_name in parsed_tags)
        extra_tags = [tag for tag in parsed_tags if tag not in known_tags]
        self.extra_tags_var.set(";".join(extra_tags))

        if self.note_text is not None:
            self.note_text.delete("1.0", tk.END)
            self.note_text.insert("1.0", row.note)
        self.form_loading = False

    def commit_current_form(self) -> None:
        if self.form_loading or self.current_sample_id is None:
            return
        if self.current_sample_id not in self.rows_by_id:
            return
        row = self.rows_by_id[self.current_sample_id]
        row.better_output = self.better_output_var.get().strip()
        for candidate_id in row.candidate_ids:
            ratings = row.candidate_ratings.setdefault(candidate_id, {})
            for metric_key, _label, _values in RATING_DIMENSIONS:
                variable_map = self.candidate_rating_vars.get(candidate_id)
                if variable_map is None:
                    continue
                ratings[metric_key] = variable_map[metric_key].get().strip()
        checked_tags = [tag_name for tag_name, var in self.tag_vars.items() if var.get()]
        row.decision_tags = join_decision_tags(checked_tags, self.extra_tags_var.get())
        if self.note_text is not None:
            row.note = self.note_text.get("1.0", tk.END).strip()
        self._refresh_sample_listbox()

    def select_previous_sample(self) -> None:
        if self.current_sample_id is None or not self.filtered_ids:
            return
        index = self.filtered_ids.index(self.current_sample_id)
        if index > 0:
            self.select_sample_by_id(self.filtered_ids[index - 1])

    def select_next_sample(self) -> None:
        if self.current_sample_id is None or not self.filtered_ids:
            return
        index = self.filtered_ids.index(self.current_sample_id)
        if index + 1 < len(self.filtered_ids):
            self.select_sample_by_id(self.filtered_ids[index + 1])

    def _current_sample_dir(self) -> Path | None:
        if self.pack_dir is None or self.current_sample_id is None:
            return None
        return self.pack_dir / self.current_sample_id

    def _resolve_audio_path(self, key: str) -> Path | None:
        sample_dir = self._current_sample_dir()
        if sample_dir is None or self.current_sample_id is None:
            return None
        row = self.rows_by_id[self.current_sample_id]
        row.ensure_candidate_consistency(sample_dir)
        if key in row.candidate_audio_names:
            audio_name = row.candidate_audio_names.get(key, "")
            return sample_dir / audio_name if audio_name else None
        return sample_dir / key

    def _iter_sample_audio_paths(self, sample_dir: Path, row: ListeningRow) -> list[Path]:
        row.ensure_candidate_consistency(sample_dir)
        candidate_names = ["mixture.wav", "reference.wav", "target.wav"] + [
            row.candidate_audio_names.get(candidate_id, "")
            for candidate_id in row.candidate_ids
        ]
        paths: list[Path] = []
        seen: set[Path] = set()
        for name in candidate_names:
            if not name:
                continue
            path = sample_dir / name
            if not path.exists() or path in seen:
                continue
            paths.append(path)
            seen.add(path)
        return paths

    def _compute_shared_sample_gain(self, sample_dir: Path, row: ListeningRow) -> float:
        peak_values: list[float] = []
        for path in self._iter_sample_audio_paths(sample_dir, row):
            try:
                data, _ = sf.read(str(path), dtype="float32", always_2d=False)
            except Exception:
                continue
            if data.ndim == 2:
                data = data.mean(axis=1)
            peak = float(np.max(np.abs(data))) if data.size else 0.0
            if peak > 0.0:
                peak_values.append(peak)
        if not peak_values:
            return 1.0
        target_peak = self._parse_target_peak()
        return target_peak / max(peak_values)

    def _get_shared_sample_gain(self) -> float:
        if self.current_sample_id is None:
            return 1.0
        cached = self.sample_gain_cache.get(self.current_sample_id)
        if cached is not None:
            return cached
        sample_dir = self._current_sample_dir()
        if sample_dir is None:
            return 1.0
        row = self.rows_by_id[self.current_sample_id]
        gain = self._compute_shared_sample_gain(sample_dir, row)
        self.sample_gain_cache[self.current_sample_id] = gain
        return gain

    def play_sample_audio(self, key: str) -> None:
        audio_path = self._resolve_audio_path(key)
        if audio_path is None or not audio_path.exists():
            messagebox.showwarning("音频不存在", f"找不到文件：{audio_path}")
            return

        try:
            data, sample_rate = sf.read(str(audio_path), dtype="float32", always_2d=False)
            if data.ndim == 2:
                data = data.mean(axis=1)
            data = np.ascontiguousarray(data)
            data = self._prepare_playback_audio(data)
            sd.stop()
            sd.play(data, sample_rate, blocking=False)
            self.status_text_var.set(f"正在播放：{audio_path.name}")
        except Exception as exc:
            messagebox.showerror("播放失败", str(exc))

    def _prepare_playback_audio(self, data: np.ndarray) -> np.ndarray:
        if self.normalize_peaks_var.get():
            data = data * self._get_shared_sample_gain()
        gain = float(self.playback_gain_var.get()) / 100.0
        data = np.clip(data * gain, -0.99, 0.99)
        return data

    def _parse_target_peak(self) -> float:
        try:
            value = float(self.target_peak_var.get())
        except ValueError:
            return 0.8
        return min(max(value, 0.05), 0.99)

    def stop_audio(self) -> None:
        sd.stop()
        if self.pack_dir is not None:
            self.status_text_var.set("已停止播放")

    def export_scores(self) -> None:
        if self.pack_dir is None:
            messagebox.showwarning("未加载盲听包", "先加载一个盲听包，再导出结果。")
            return
        self.commit_current_form()
        rows = [self.rows_by_id[sample_id] for sample_id in sorted(self.rows_by_id)]
        try:
            write_listening_rows(self.pack_dir, rows, self.pack_format)
            summary = self._build_export_summary(rows)
            write_utf8_text(
                self.pack_dir / EXPORT_SUMMARY_NAME,
                json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            )
        except Exception as exc:
            messagebox.showerror("导出失败", str(exc))
            return

        self.status_text_var.set("导出完成")
        messagebox.showinfo(
            "导出完成",
            f"已写回 listening_sheet.csv，并生成 {EXPORT_SUMMARY_NAME}",
        )

    def _build_export_summary(self, rows: list[ListeningRow]) -> dict[str, Any]:
        candidate_ids: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for candidate_id in row.candidate_ids:
                if candidate_id in seen:
                    continue
                candidate_ids.append(candidate_id)
                seen.add(candidate_id)
        candidate_ids.sort(key=candidate_sort_key)

        better_output_counts = {candidate_id: 0 for candidate_id in candidate_ids}
        better_output_counts.update({"tie": 0, "uncertain": 0, "unscored": 0})

        recipe_breakdown: dict[str, dict[str, int]] = {}
        for row in rows:
            outcome = row.better_output if row.better_output else "unscored"
            if outcome not in better_output_counts:
                better_output_counts[outcome] = 0
            better_output_counts[outcome] += 1

            recipe_counts = recipe_breakdown.setdefault(
                row.recipe,
                {key: 0 for key in better_output_counts},
            )
            if outcome not in recipe_counts:
                recipe_counts[outcome] = 0
            recipe_counts[outcome] += 1

        return {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "pack_dir": serialize_repo_path(self.pack_dir),
            "pack_format": self.pack_format,
            "blind_mode": self.blind_mode,
            "normalize_peaks_enabled": self.normalize_peaks_var.get(),
            "normalization_mode": "sample_shared_peak_gain" if self.normalize_peaks_var.get() else "none",
            "playback_target_peak": self._parse_target_peak(),
            "playback_gain_percent": round(float(self.playback_gain_var.get()), 2),
            "num_samples": len(rows),
            "num_scored": sum(1 for row in rows if row.is_scored()),
            "candidate_labels": {
                candidate_id: format_candidate_display_name(candidate_id, self.blind_mode)
                for candidate_id in candidate_ids
            },
            "better_output_counts": better_output_counts,
            "recipe_breakdown": recipe_breakdown,
        }

    def _on_mousewheel(self, event: Any) -> None:
        if self.right_canvas is None:
            return
        delta = event.delta
        if delta == 0:
            return
        self.right_canvas.yview_scroll(int(-delta / 120), "units")

    def on_close(self) -> None:
        self.commit_current_form()
        self.stop_audio()
        self.root.destroy()


def main() -> None:
    args = parse_args()
    root = tk.Tk()
    ListeningPackApp(root=root, initial_pack_dir=args.pack_dir)
    root.mainloop()


if __name__ == "__main__":
    main()
