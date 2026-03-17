# 2026-03-16 Manifest Bootstrap 记录

## 今日完成

- 按 `docs/00_context_bootstrap.md` 要求，重新读取了文档恢复链路：
  - `docs/00_context_bootstrap.md`
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `initial_design.md`
  - `initial_design_judg.md`
- 读取并确认了当前唯一核心数据脚本：
  - `scripts/data/prepare_curated_pools.py`
- 使用仓库根目录 `.\python.exe` 实际执行该脚本，成功生成首批正式 manifest。
- 修正了 `target_reference_pool` 的抽样逻辑：
  - 从“排序后直接取前 64 条”
  - 改为“在符合时长条件的候选里均匀抽样”
  - 目的：避免 reference 池过度集中在时间上过于靠前的一段切片。

## 本次执行结果

命令：

```powershell
.\python.exe scripts\data\prepare_curated_pools.py
```

产物计数：

- `target_speech_pool`: 219
- `target_reference_pool`: 64
- `speech_interference_clean_pool`: 768
- `clean_speaker_count`: 32
- `speech_interference_hard_pool`: 140
- `music_interference_pool`: 12
- `singing_vocal_interference_pool`: 96

已生成的关键文件：

- `data/manifests/target_speech_pool.jsonl`
- `data/manifests/target_reference_pool.jsonl`
- `data/manifests/speech_interference_clean_pool.jsonl`
- `data/manifests/speech_interference_hard_pool.jsonl`
- `data/manifests/music_interference_pool.jsonl`
- `data/manifests/singing_vocal_interference_pool.jsonl`
- `data/manifests/curated_pool_summary.json`

中间产物：

- `data/interim/friend_hard_negative_segments/` 中已生成 140 个切片文件。

## 当前判断

- 项目已经从“只有结构和文档”进入“有正式数据入口”的状态。
- 下一步不应继续停留在目录整理，而应进入 synthetic mixture 生成器。
- 在真正开训前，建议先产出一小批可试听的 train/val 合成样本，优先验证：
  - 元数据是否够用；
  - 混合策略是否合理；
  - reference/target 隔离是否满足预期。

## 下一步建议

1. 编写 `scripts/data/build_synthetic_dataset.py`。
2. 先做最小字段：
   - `mixture_audio_path`
   - `target_audio_path`
   - `reference_audio_path`
   - `metadata.json`
3. 先生成少量样本并人工抽检，再进入 baseline 验证。
