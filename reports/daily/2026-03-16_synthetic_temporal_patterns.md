# 2026-03-16 Synthetic Temporal Patterns

## 本次目标

把 synthetic 生成器从“目标全程存在”的 MVP 版本，推进到至少能覆盖核心 target temporal patterns 的版本。

这一步的重点不是再堆更多干扰池，而是先把监督目标本身做对：

- 目标缺席时，`target.wav` 就应该真的是静音；
- 不能只在 metadata 里写一句“这里目标不在”，但 target 监督音频实际上还是全程有人声。

## 本次修改

脚本：

- `scripts/data/build_synthetic_dataset.py`

新增能力：

- 目标时序模式：
  - `target_full`
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
- `target.wav` 按 pattern 实际渲染，不再总是直接导出完整 target 原片段。
- `mixture.wav` 仍与 `target.wav` 保持等长。
- metadata 新增：
  - `temporal_pattern`
  - `target_present_ratio`
  - `target_present_duration_sec`
  - `target_segments`
  - `target_absent_intervals`

## 本次验证

执行命令：

```powershell
.\python.exe scripts\data\build_synthetic_dataset.py --train-count 24 --val-count 6 --force-clean
```

已实际看到的 train split 时序模式分布：

- `target_full`: 11
- `target_intermittent`: 4
- `target_absent_tail`: 4
- `target_absent_head`: 5

已额外验证：

- 至少一个 `target_intermittent` 样本的 metadata 已正确记录两个 target segment 和中间缺席区间。
- `target.wav` 与 `mixture.wav` 时长保持一致。

## 当前结论

synthetic 生成器已经不再停留在“目标永远全程出现”的状态，至少具备了进入 baseline 前的基础时序多样性。

## 下一步建议

1. 抽听一批包含不同时序模式的样本。
2. 若听感通过，再开始 baseline inference 或最小训练闭环。
3. 后续再补更复杂的三段式 intermittent、更多 overlap 结构和 target absent 强化样本。
