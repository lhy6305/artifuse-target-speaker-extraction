# -*- coding: utf-8 -*-
import os
import shutil
import sys
from typing import List, Tuple

# =========================
# 配置区
# =========================

SANDBOX_RUNTIME_ROOT = r"D:\Sandbox\TmpBox\drive\F\proj_dev\tmp\workdir4-1"
SANDBOX_SCAN_ROOT = r"D:\Sandbox\TmpBox\drive\F\proj_dev\tmp\workdir4-1"
REAL_RUNTIME_ROOT = r"F:\proj_dev\tmp\workdir4-1"

# 是否仅预演，不实际删除
DRY_RUN = False

# 是否删除命中文件后，顺带清理两侧的空目录
CLEAN_EMPTY_DIRS = True


# =========================
# 工具函数
# =========================

def norm(p: str) -> str:
    return os.path.normcase(os.path.normpath(p))


def is_under(child: str, parent: str) -> bool:
    child_n = norm(os.path.abspath(child))
    parent_n = norm(os.path.abspath(parent))
    try:
        common = os.path.commonpath([child_n, parent_n])
    except ValueError:
        return False
    return common == parent_n


def remove_path(path: str) -> Tuple[bool, str]:
    """
    删除文件或目录。
    返回: (是否做了删除动作, 描述)
    """
    if not os.path.lexists(path):
        return False, "不存在"

    if os.path.isfile(path) or os.path.islink(path):
        if DRY_RUN:
            return True, "预演删除文件"
        os.remove(path)
        return True, "已删除文件"

    if os.path.isdir(path):
        if DRY_RUN:
            return True, "预演删除目录"
        shutil.rmtree(path)
        return True, "已删除目录"

    return False, "未知类型，未删除"


def try_remove_empty_dirs_upward(start_dir: str, stop_at: str) -> List[str]:
    """
    从 start_dir 开始向上删除空目录，直到 stop_at（不删除 stop_at 本身之外的上层）。
    只删除空目录；遇到非空或异常即停止。
    返回已删除的目录列表。
    """
    removed = []

    start_dir = os.path.abspath(start_dir)
    stop_at = os.path.abspath(stop_at)

    if not is_under(start_dir, stop_at):
        return removed

    cur = start_dir
    while True:
        cur_n = norm(cur)
        stop_n = norm(stop_at)

        if cur_n == stop_n:
            # 是否删除 stop_at 自身：通常不删根目录
            break

        if not os.path.isdir(cur):
            parent = os.path.dirname(cur)
            if parent == cur:
                break
            cur = parent
            continue

        try:
            if os.listdir(cur):
                break
            if DRY_RUN:
                removed.append(cur + " [预演删除空目录]")
            else:
                os.rmdir(cur)
                removed.append(cur)
        except Exception:
            break

        parent = os.path.dirname(cur)
        if parent == cur:
            break
        if not is_under(parent, stop_at) and norm(parent) != stop_n:
            break
        cur = parent

    return removed


def collect_zero_size_files(scan_root: str) -> List[str]:
    """
    收集 scan_root 下所有大小为 0 的文件。
    """
    result = []
    for root, dirs, files in os.walk(scan_root):
        for name in files:
            p = os.path.join(root, name)
            try:
                if os.path.getsize(p) == 0:
                    result.append(p)
            except OSError as e:
                print("[WARN] 无法读取文件大小: {} | {}".format(p, e))
    return result


def mapped_real_path_from_sandbox_file(sandbox_file: str) -> str:
    """
    将沙盒中的文件路径，按 SANDBOX_RUNTIME_ROOT 的相对路径映射到 REAL_RUNTIME_ROOT。
    """
    rel = os.path.relpath(sandbox_file, SANDBOX_RUNTIME_ROOT)
    return os.path.join(REAL_RUNTIME_ROOT, rel)


def delete_pair_by_zero_file(sandbox_file: str) -> None:
    """
    针对一个沙盒中的 0 字节文件：
    - 删除沙盒侧对应路径（文件/目录）
    - 删除真实侧对应路径（文件/目录）
    - 可选清理两侧空目录
    """
    real_path = mapped_real_path_from_sandbox_file(sandbox_file)

    print("=" * 100)
    print("命中 0 字节文件:")
    print("  沙盒文件: {}".format(sandbox_file))
    print("  映射实侧: {}".format(real_path))

    # 先删两侧对应路径（按“目录或文件”处理）
    for side_name, path in [("沙盒侧", sandbox_file), ("实侧", real_path)]:
        try:
            acted, msg = remove_path(path)
            print("  [{}] {} -> {}".format(side_name, msg, path))
        except Exception as e:
            print("  [{}] 删除失败 -> {} | {}".format(side_name, path, e))

    # 清理空目录
    if CLEAN_EMPTY_DIRS:
        sandbox_parent = os.path.dirname(sandbox_file)
        real_parent = os.path.dirname(real_path)

        try:
            removed = try_remove_empty_dirs_upward(sandbox_parent, SANDBOX_RUNTIME_ROOT)
            for d in removed:
                print("  [沙盒侧] 清理空目录 -> {}".format(d))
        except Exception as e:
            print("  [沙盒侧] 清理空目录失败 -> {} | {}".format(sandbox_parent, e))

        try:
            removed = try_remove_empty_dirs_upward(real_parent, REAL_RUNTIME_ROOT)
            for d in removed:
                print("  [实侧] 清理空目录 -> {}".format(d))
        except Exception as e:
            print("  [实侧] 清理空目录失败 -> {} | {}".format(real_parent, e))


def main():
    print("SANDBOX_RUNTIME_ROOT =", SANDBOX_RUNTIME_ROOT)
    print("SANDBOX_SCAN_ROOT    =", SANDBOX_SCAN_ROOT)
    print("REAL_RUNTIME_ROOT    =", REAL_RUNTIME_ROOT)
    print("DRY_RUN              =", DRY_RUN)
    print("CLEAN_EMPTY_DIRS     =", CLEAN_EMPTY_DIRS)
    print()

    if not os.path.isdir(SANDBOX_RUNTIME_ROOT):
        print("[ERROR] 沙盒 runtime 根目录不存在:")
        print("        {}".format(SANDBOX_RUNTIME_ROOT))
        sys.exit(1)

    if not os.path.isdir(SANDBOX_SCAN_ROOT):
        print("[ERROR] 沙盒扫描目录不存在:")
        print("        {}".format(SANDBOX_SCAN_ROOT))
        sys.exit(1)

    # 实侧根目录可以不存在，但通常应该存在
    if not os.path.exists(REAL_RUNTIME_ROOT):
        print("[WARN] 实侧 runtime 根目录不存在:")
        print("       {}".format(REAL_RUNTIME_ROOT))

    zero_files = collect_zero_size_files(SANDBOX_SCAN_ROOT)

    print("发现 0 字节文件数量: {}".format(len(zero_files)))
    if not zero_files:
        print("没有需要处理的文件。")
        return

    for p in zero_files:
        delete_pair_by_zero_file(p)

    print()
    print("处理完成。")


if __name__ == "__main__":
    main()