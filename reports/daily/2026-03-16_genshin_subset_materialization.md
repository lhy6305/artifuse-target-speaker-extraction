# 2026-03-16 Genshin Clean Subset 迁移记录

## 背景

- 原始 `data_in/genshin_voice_extract/` 体量很大。
- 当前项目实际只需要其中一部分 clean speech interference。
- 在磁盘空间紧张前提下，继续长期保留整个完整包不划算。

## 本次处理

- 新增脚本：`scripts/data/materialize_genshin_clean_subset.py`
- 目标：
  - 将 `speech_interference_clean_pool.jsonl` 中已经选中的样本单独落盘；
  - 让后续训练和合成只依赖这批正式子集；
  - 避免继续把完整原神包当成 clean pool 的唯一入口。

## 方案尝试

### 方案 1：hardlink

- 目的：几乎不增加内容占用。
- 结果：失败。
- 结论：当前磁盘/文件系统环境不支持 `os.link(...)`。

### 方案 2：move

- 命令：

```powershell
.\python.exe scripts\data\materialize_genshin_clean_subset.py --mode move --force-clean
```

- 结果：成功。

## 迁移结果

- 已迁移样本数：768
- 已覆盖说话人数：32
- 新正式子集目录：
  - `data/curated/genshin_clean_subset/`
- 改写后的 clean manifest：
  - `data/manifests/speech_interference_clean_pool.jsonl`
- 上游路径快照：
  - `data/manifests/speech_interference_clean_pool.upstream_snapshot.jsonl`

子集体量：

- 音频总字节数：392850944
- 文本总字节数：57185
- 合计约：392.9 MB

文件数变化：

- 迁移前原神包文件数：214534
- 迁移后原神包文件数：212998
- 新 curated 子集文件数：1537
  - 768 个 `wav`
  - 768 个 `lab`
  - 1 个 `subset_summary.json`

## 额外处理

- 已给 `scripts/data/prepare_curated_pools.py` 增加保护逻辑。
- 若发现当前 clean manifest 已指向 `data/curated/genshin_clean_subset`，则不再重建 clean pool。
- 这样可以避免后续误扫不完整的 `data_in/genshin_voice_extract/` 后，把 clean pool 覆盖成另一批样本。

## 当前结论

- clean interference 已经从“依赖整个原神完整包”切换为“依赖一个正式散选子集”。
- 后续若继续压缩空间，优先考虑如何处理 `data_in/genshin_voice_extract/` 的剩余未使用内容，而不是回退到重新保留完整包。
