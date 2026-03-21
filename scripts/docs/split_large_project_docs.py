from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
ARCHIVE_DIR = DOCS_DIR / "archive"


@dataclass(frozen=True)
class NumberedDocConfig:
    source_path: Path
    archive_subdir: str
    active_start: int
    chunk_size: int
    title: str
    archive_readme_title: str
    tail_heading_pattern: str | None = None


@dataclass(frozen=True)
class PitfallDocConfig:
    source_path: Path
    archive_subdir: str
    active_start: int
    chunk_size: int
    title: str
    archive_readme_title: str


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def strip_existing_archive_note(lines: list[str]) -> list[str]:
    for index, line in enumerate(lines):
        if line == "## 归档说明\n":
            return lines[:index]
    return lines


def split_top_level_numbered_blocks(lines: list[str]) -> tuple[list[str], list[tuple[int, list[str]]], list[str]]:
    starts: list[tuple[int, int]] = []
    expected: int | None = None
    for index, line in enumerate(lines):
        match = re.match(r"^(\d+)\.\s", line)
        if not match:
            continue
        number = int(match.group(1))
        if expected is None:
            starts.append((number, index))
            expected = number + 1
            continue
        if number == expected:
            starts.append((number, index))
            expected += 1

    if not starts:
        raise RuntimeError("No top-level numbered blocks found.")

    intro = lines[: starts[0][1]]
    last_item_end = len(lines)
    for index in range(starts[-1][1] + 1, len(lines)):
        if re.match(r"^##\s", lines[index]):
            last_item_end = index
            break

    blocks: list[tuple[int, list[str]]] = []
    for block_index, (number, start_line) in enumerate(starts):
        next_start = starts[block_index + 1][1] if block_index + 1 < len(starts) else last_item_end
        blocks.append((number, lines[start_line:next_start]))

    tail = lines[last_item_end:]
    return intro, blocks, tail


def split_pitfall_blocks(lines: list[str]) -> tuple[list[str], list[tuple[int, str, list[str]]]]:
    pitfall_starts: list[tuple[int, int]] = []
    expected: int | None = None
    for index, line in enumerate(lines):
        match = re.match(r"^###\s+(\d+)\.\s", line)
        if not match:
            continue
        number = int(match.group(1))
        if expected is None:
            pitfall_starts.append((number, index))
            expected = number + 1
            continue
        if number == expected:
            pitfall_starts.append((number, index))
            expected += 1

    if not pitfall_starts:
        raise RuntimeError("No pitfall blocks found.")

    date_starts: list[tuple[int, str]] = []
    for index, line in enumerate(lines):
        match = re.match(r"^##\s+(\d{4}-\d{2}-\d{2})", line)
        if match:
            date_starts.append((index, match.group(1)))

    first_date_index = date_starts[0][0] if date_starts else pitfall_starts[0][1]
    intro = lines[:first_date_index]

    blocks: list[tuple[int, str, list[str]]] = []
    current_date = "undated"
    date_cursor = 0
    for block_index, (number, start_line) in enumerate(pitfall_starts):
        while date_cursor < len(date_starts) and date_starts[date_cursor][0] < start_line:
            current_date = date_starts[date_cursor][1]
            date_cursor += 1
        next_start = pitfall_starts[block_index + 1][1] if block_index + 1 < len(pitfall_starts) else len(lines)
        blocks.append((number, current_date, lines[start_line:next_start]))

    return intro, blocks


def chunk_ranges(numbers: list[int], chunk_size: int) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for index in range(0, len(numbers), chunk_size):
        chunk_numbers = numbers[index : index + chunk_size]
        ranges.append((chunk_numbers[0], chunk_numbers[-1]))
    return ranges


def format_range_label(start: int, end: int) -> str:
    return f"{start:03d}-{end:03d}"


def build_archive_note(title: str, active_start: int, archive_subdir: str) -> str:
    return (
        "## 归档说明\n\n"
        f"- 本文档当前只保留 `{active_start}` 及之后的活跃记录，便于接班和日常维护。\n"
        f"- 更早的历史记录已拆分归档到 `docs/archive/{archive_subdir}/`。\n"
        f"- 归档总索引见 `docs/archive/{archive_subdir}/README.md`。\n\n"
        "## 当前活跃记录\n\n"
    )


def build_archive_readme(
    *,
    title: str,
    source_name: str,
    active_start: int,
    chunks: list[tuple[int, int]],
    filename_prefix: str,
) -> str:
    lines = [
        f"# {title}",
        "",
        "- 源文档：",
        f"  - `docs/{source_name}`",
        "- 当前主文档保留的活跃范围：",
        f"  - `{active_start}+`",
        "- 历史归档分卷：",
    ]
    for start, end in chunks:
        label = format_range_label(start, end)
        lines.append(f"  - `{filename_prefix}_{label}.md`")
        lines.append(f"    - 条目范围：`{start}-{end}`")
    lines.append("")
    return "\n".join(lines)


def discover_existing_chunk_ranges(archive_subdir: Path, filename_prefix: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    pattern = re.compile(rf"^{re.escape(filename_prefix)}_(\d{{3}})-(\d{{3}})\.md$")
    for path in sorted(archive_subdir.glob(f"{filename_prefix}_*.md")):
        match = pattern.match(path.name)
        if match:
            ranges.append((int(match.group(1)), int(match.group(2))))
    return ranges


def delete_existing_chunk_files(archive_subdir: Path, filename_prefix: str) -> None:
    for path in archive_subdir.glob(f"{filename_prefix}_*.md"):
        path.unlink()


def load_existing_numbered_archive_blocks(archive_subdir: Path) -> list[tuple[int, list[str]]]:
    blocks_by_number: dict[int, list[str]] = {}
    for path in sorted(archive_subdir.glob("items_*.md")):
        _, blocks, _ = split_top_level_numbered_blocks(read_lines(path))
        for number, block in blocks:
            blocks_by_number[number] = block
    return sorted(blocks_by_number.items())


def load_existing_pitfall_archive_blocks(archive_subdir: Path) -> list[tuple[int, str, list[str]]]:
    blocks_by_number: dict[int, tuple[int, str, list[str]]] = {}
    for path in sorted(archive_subdir.glob("pitfalls_*.md")):
        _, blocks = split_pitfall_blocks(read_lines(path))
        for number, date_label, block in blocks:
            blocks_by_number[number] = (number, date_label, block)
    return [blocks_by_number[number] for number in sorted(blocks_by_number)]


def build_task_branch_archive_readme(active_start: int, chunks: list[tuple[int, int]]) -> str:
    lines = [
        "# 任务分支图归档索引",
        "",
        "- 源文档：",
        "  - `docs/05_task_branch_map.md`",
        "- 当前主文档保留的活跃范围：",
        f"  - `{active_start}+`",
        "- 长节归档：",
        "  - `sections_03_dead_branches.md`",
        "    - 对应原 `## 3. 已判死分支`",
        "  - `sections_04_branch_state_history.md`",
        "    - 对应原 `## 4. 当前分支状态`",
        "- 历史归档分卷：",
    ]
    for start, end in chunks:
        label = format_range_label(start, end)
        lines.append(f"  - `items_{label}.md`")
        lines.append(f"    - 条目范围：`{start}-{end}`")
    lines.append("")
    return "\n".join(lines)


def serialize_numbered_blocks(blocks: list[tuple[int, list[str]]]) -> str:
    return "".join("".join(block_lines) for _, block_lines in blocks).rstrip() + "\n"


def serialize_pitfall_blocks(blocks: list[tuple[int, str, list[str]]]) -> str:
    output: list[str] = []
    current_date: str | None = None
    for _, date_label, block_lines in blocks:
        if date_label != current_date:
            if output and output[-1] != "":
                output.append("")
            output.append(f"## {date_label}")
            output.append("")
            current_date = date_label
        output.extend(line.rstrip("\n") for line in block_lines)
        if output[-1] != "":
            output.append("")
    while output and output[-1] == "":
        output.pop()
    return "\n".join(output) + "\n"


def archive_numbered_doc(config: NumberedDocConfig) -> None:
    lines = read_lines(config.source_path)
    intro, blocks, tail = split_top_level_numbered_blocks(lines)
    intro = strip_existing_archive_note(intro)

    active_blocks = [(number, block) for number, block in blocks if number >= config.active_start]
    archived_blocks = [(number, block) for number, block in blocks if number < config.active_start]
    archived_numbers = [number for number, _ in archived_blocks]
    ranges = chunk_ranges(archived_numbers, config.chunk_size) if archived_numbers else []

    archive_subdir = ARCHIVE_DIR / config.archive_subdir
    archive_subdir.mkdir(parents=True, exist_ok=True)

    if not archived_blocks:
        archived_blocks = load_existing_numbered_archive_blocks(archive_subdir)
        archived_numbers = [number for number, _ in archived_blocks]
        ranges = chunk_ranges(archived_numbers, config.chunk_size) if archived_numbers else []

    delete_existing_chunk_files(archive_subdir, "items")

    for start, end in ranges:
        selected = [(number, block) for number, block in archived_blocks if start <= number <= end]
        body = [
            f"# {config.title} 历史归档 {start}-{end}",
            "",
            "- 源文档：",
            f"  - `docs/{config.source_path.name}`",
            "- 条目范围：",
            f"  - `{start}-{end}`",
            "",
            serialize_numbered_blocks(selected).rstrip(),
            "",
        ]
        write_text(
            archive_subdir / f"items_{format_range_label(start, end)}.md",
            "\n".join(body).rstrip() + "\n",
        )

    if not ranges:
        ranges = discover_existing_chunk_ranges(archive_subdir, "items")

    write_text(
        archive_subdir / "README.md",
        build_archive_readme(
            title=config.archive_readme_title,
            source_name=config.source_path.name,
            active_start=config.active_start,
            chunks=ranges,
            filename_prefix="items",
        ),
    )

    rebuilt_main = (
        "".join(intro).rstrip()
        + "\n\n"
        + build_archive_note(config.title, config.active_start, config.archive_subdir)
        + serialize_numbered_blocks(active_blocks)
        + ("\n" + "".join(tail).lstrip("\n") if tail else "")
    )
    write_text(config.source_path, rebuilt_main.rstrip() + "\n")


def archive_pitfall_doc(config: PitfallDocConfig) -> None:
    lines = read_lines(config.source_path)
    intro, blocks = split_pitfall_blocks(lines)
    intro = strip_existing_archive_note(intro)

    active_blocks = [block for block in blocks if block[0] >= config.active_start]
    archived_blocks = [block for block in blocks if block[0] < config.active_start]
    archived_numbers = [number for number, _, _ in archived_blocks]
    ranges = chunk_ranges(archived_numbers, config.chunk_size) if archived_numbers else []

    archive_subdir = ARCHIVE_DIR / config.archive_subdir
    archive_subdir.mkdir(parents=True, exist_ok=True)

    if not archived_blocks:
        archived_blocks = load_existing_pitfall_archive_blocks(archive_subdir)
        archived_numbers = [number for number, _, _ in archived_blocks]
        ranges = chunk_ranges(archived_numbers, config.chunk_size) if archived_numbers else []

    delete_existing_chunk_files(archive_subdir, "pitfalls")

    for start, end in ranges:
        selected = [block for block in archived_blocks if start <= block[0] <= end]
        body = [
            f"# {config.title} 历史归档 {start}-{end}",
            "",
            "- 源文档：",
            f"  - `docs/{config.source_path.name}`",
            "- 条目范围：",
            f"  - `{start}-{end}`",
            "",
            serialize_pitfall_blocks(selected).rstrip(),
            "",
        ]
        write_text(
            archive_subdir / f"pitfalls_{format_range_label(start, end)}.md",
            "\n".join(body).rstrip() + "\n",
        )

    if not ranges:
        ranges = discover_existing_chunk_ranges(archive_subdir, "pitfalls")

    write_text(
        archive_subdir / "README.md",
        build_archive_readme(
            title=config.archive_readme_title,
            source_name=config.source_path.name,
            active_start=config.active_start,
            chunks=ranges,
            filename_prefix="pitfalls",
        ),
    )

    rebuilt_main = (
        "".join(intro).rstrip()
        + "\n\n"
        + build_archive_note(config.title, config.active_start, config.archive_subdir)
        + serialize_pitfall_blocks(active_blocks)
    )
    write_text(config.source_path, rebuilt_main.rstrip() + "\n")


def archive_task_branch_map_sections(source_path: Path) -> None:
    lines = read_lines(source_path)
    archive_subdir = ARCHIVE_DIR / "task_branch_map"
    archive_subdir.mkdir(parents=True, exist_ok=True)

    dead_heading = "## 3. 已判死分支\n"
    state_heading = "## 4. 当前分支状态\n"
    next_heading = "## 5. 下一条默认执行分支\n"
    archived_heading = "## 3. 历史分支归档\n"

    try:
        dead_start = lines.index(dead_heading)
        state_start = lines.index(state_heading)
        next_start = lines.index(next_heading)
    except ValueError:
        if archived_heading in lines:
            return
        raise RuntimeError("Task branch map does not contain the expected section headings.")

    write_text(
        archive_subdir / "sections_03_dead_branches.md",
        "".join(lines[dead_start:state_start]).rstrip() + "\n",
    )
    write_text(
        archive_subdir / "sections_04_branch_state_history.md",
        "".join(lines[state_start:next_start]).rstrip() + "\n",
    )

    summary = "\n".join(
        [
            "## 3. 历史分支归档",
            "",
            "- 原 `## 3. 已判死分支` 已迁移到：",
            "  - `docs/archive/task_branch_map/sections_03_dead_branches.md`",
            "- 原 `## 4. 当前分支状态` 已迁移到：",
            "  - `docs/archive/task_branch_map/sections_04_branch_state_history.md`",
            "- 主文档当前只保留：",
            "  - 当前裁决口径",
            "  - 下一条默认执行分支",
            "  - 当前活跃记录",
            "  - 忘线检查表",
            "- 需要回溯某条旧分支的失败原因或阶段状态时，先看上面两份归档。",
            "",
            "## 4. 当前维护口径",
            "",
            "- `docs/05_task_branch_map.md` 用于记录当前仍可能影响下一步决策的活跃事实。",
            "- 已终止或只具备历史参考价值的长记录，不再继续堆叠回主文档。",
            "- 条目级历史分卷见 `docs/archive/task_branch_map/README.md`。",
        ]
    )

    rebuilt = (
        "".join(lines[:dead_start]).rstrip()
        + "\n\n"
        + summary
        + "\n\n"
        + "".join(lines[next_start:]).lstrip("\n")
    )
    write_text(source_path, rebuilt.rstrip() + "\n")


def write_archive_root_readme() -> None:
    text = "\n".join(
        [
            "# 文档归档索引",
            "",
            "- 当前活跃文档仍保留在 `docs/` 根目录，优先用于接班与日常维护。",
            "- 历史长记录已按主题拆分到以下目录：",
            "  - `docs/archive/project_overview/`",
            "  - `docs/archive/pitfalls/`",
            "  - `docs/archive/task_branch_map/`",
            "    - 含条目分卷和大节历史归档",
            "",
            "建议读取顺序：",
            "",
            "1. 先读 `docs/00_context_bootstrap.md`。",
            "2. 再读 `docs/01_project_overview_and_plan.md`、`docs/02_pitfalls_log.md`、`docs/05_task_branch_map.md` 的活跃部分。",
            "3. 只有在需要更早历史时，再进入对应的 `docs/archive/*/README.md` 和分卷文件。",
            "",
        ]
    )
    write_text(ARCHIVE_DIR / "README.md", text)


def main() -> None:
    archive_numbered_doc(
        NumberedDocConfig(
            source_path=DOCS_DIR / "01_project_overview_and_plan.md",
            archive_subdir="project_overview",
            active_start=209,
            chunk_size=10,
            title="项目总览与阶段计划",
            archive_readme_title="项目总览与阶段计划归档索引",
        )
    )
    archive_pitfall_doc(
        PitfallDocConfig(
            source_path=DOCS_DIR / "02_pitfalls_log.md",
            archive_subdir="pitfalls",
            active_start=119,
            chunk_size=10,
            title="踩坑记录",
            archive_readme_title="踩坑记录归档索引",
        )
    )
    archive_numbered_doc(
        NumberedDocConfig(
            source_path=DOCS_DIR / "05_task_branch_map.md",
            archive_subdir="task_branch_map",
            active_start=31,
            chunk_size=15,
            title="任务分支图",
            archive_readme_title="任务分支图归档索引",
        )
    )
    archive_task_branch_map_sections(DOCS_DIR / "05_task_branch_map.md")
    write_text(
        ARCHIVE_DIR / "task_branch_map" / "README.md",
        build_task_branch_archive_readme(
            active_start=31,
            chunks=discover_existing_chunk_ranges(ARCHIVE_DIR / "task_branch_map", "items"),
        ),
    )
    write_archive_root_readme()


if __name__ == "__main__":
    main()
