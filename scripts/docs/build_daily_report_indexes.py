from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DAILY_DIR = ROOT / "reports" / "daily"


@dataclass(frozen=True)
class ReportEntry:
    path: Path
    date: str
    month: str
    line_count: int
    title: str


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def discover_report_entries() -> list[ReportEntry]:
    entries: list[ReportEntry] = []
    pattern = re.compile(r"^(\d{4}-\d{2}-\d{2})_(.+)\.md$")
    for path in sorted(DAILY_DIR.glob("*.md")):
        if path.name == "README.md" or path.name.startswith("index_"):
            continue
        match = pattern.match(path.name)
        if not match:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        heading = next((line[2:].strip() for line in lines if line.startswith("# ")), "")
        entries.append(
            ReportEntry(
                path=path,
                date=match.group(1),
                month=match.group(1)[:7],
                line_count=len(lines),
                title=heading or path.stem,
            )
        )
    return entries


def build_month_index(month: str, entries: list[ReportEntry]) -> str:
    by_date: dict[str, list[ReportEntry]] = defaultdict(list)
    for entry in entries:
        by_date[entry.date].append(entry)

    long_reports = [entry for entry in entries if entry.line_count >= 300]
    lines = [
        f"# 每日推进记录索引 {month}",
        "",
        "- 覆盖文件数：",
        f"  - `{len(entries)}`",
        "- 覆盖日期数：",
        f"  - `{len(by_date)}`",
        "- 建议用法：",
        "  - 先按日期定位，再进入具体日报。",
        "  - 需要快速抓主线时，优先阅读行数较长或最近更新的日报。",
    ]
    if long_reports:
        lines.extend(
            [
                "- 本月较长日报（`>=300` 行）：",
            ]
        )
        for entry in sorted(long_reports, key=lambda item: (item.date, item.path.name)):
            lines.append(f"  - `{entry.path.name}` | `{entry.line_count}` 行")
    lines.append("")

    for date in sorted(by_date):
        lines.append(f"## {date}")
        lines.append("")
        for entry in sorted(by_date[date], key=lambda item: item.path.name):
            lines.append(
                f"- `{entry.path.name}` | `{entry.line_count}` 行 | `{entry.title}`"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def build_root_readme(entries: list[ReportEntry]) -> str:
    by_month: dict[str, list[ReportEntry]] = defaultdict(list)
    for entry in entries:
        by_month[entry.month].append(entry)

    latest_entries = sorted(entries, key=lambda item: (item.date, item.path.name), reverse=True)[:10]
    lines = [
        "# 每日推进记录",
        "",
        "- 目录作用：",
        "  - 保存按日期落盘的实验推进记录。",
        "- 维护原则：",
        "  - 原始日报文件保持原路径，避免打断既有文档引用。",
        "  - 通过本目录 `README.md` 和 `index_YYYY-MM.md` 做月度索引与跳读入口。",
        "",
        "- 月度索引：",
    ]
    for month in sorted(by_month):
        lines.append(
            f"  - `index_{month}.md` | `{len(by_month[month])}` 份日报 | 日期 `{min(item.date for item in by_month[month])}` 至 `{max(item.date for item in by_month[month])}`"
        )
    lines.extend(
        [
            "",
            "- 最近新增日报：",
        ]
    )
    for entry in latest_entries:
        lines.append(f"  - `{entry.path.name}` | `{entry.line_count}` 行")
    lines.extend(
        [
            "",
            "建议读取顺序：",
            "",
            "1. 先读 `docs/00_context_bootstrap.md` 与 `docs/` 下活跃文档。",
            "2. 如需补实验时间线，再读本文件和对应 `index_YYYY-MM.md`。",
            "3. 最后再进入具体日报文件。",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    entries = discover_report_entries()
    write_text(DAILY_DIR / "README.md", build_root_readme(entries))

    by_month: dict[str, list[ReportEntry]] = defaultdict(list)
    for entry in entries:
        by_month[entry.month].append(entry)
    for month, month_entries in by_month.items():
        write_text(DAILY_DIR / f"index_{month}.md", build_month_index(month, month_entries))


if __name__ == "__main__":
    main()
