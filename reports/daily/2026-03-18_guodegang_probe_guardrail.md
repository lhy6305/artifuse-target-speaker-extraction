# 2026-03-18 guodegang probe guardrail

## 背景

上一轮 `v9` 已经暴露出一个问题：

- broad near-real speech probe overall 只比 `v8` 差了
  - `-0.015875 dB`
- 但真正的 `guodegang / 0006` 子问题却回退了
  - `-0.285347 dB`

这说明当前不能继续把 `0006` guardrail 混在 broad speech probe 里看整体均值。

## 新增脚本

### 1. probe 子集构建

- `scripts/data/build_probe_subset_manifest.py`

作用：

- 从现有 probe manifest 读取每条样本的 metadata
- 按以下字段过滤：
  - `anchor_id`
  - `speech_family`
  - `speech_clip_tag`
  - `recipe`

### 2. focused probe guardrail

- `scripts/eval/gate_probe_subset_guardrail.py`

作用：

- 用 reference probe summary 与 candidate probe summary 做 focused guardrail
- 当前支持按以下层级检查：
  - overall
  - `speech_family`
  - `anchor`

## 生成的子 probe

### `near_real_guodegang_transient_probe_v1`

- manifest：
  - `data/probes/near_real_guodegang_transient_probe_v1_manifest.jsonl`
- 数量：
  - `6`
- 全部来自：
  - `near_real_0006`
  - `guodegang_raw`

### `near_real_friend_speech_probe_v1`

- manifest：
  - `data/probes/near_real_friend_speech_probe_v1_manifest.jsonl`
- 数量：
  - `18`
- 全部来自：
  - `friend_raw`

这次真正作为新 guardrail 落地的是第一条：

- `near_real_guodegang_transient_probe_v1`

## 当前客观排序

### `stage2 vs v7`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+1.159040 dB`

### `stage2 vs v8`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+1.059967 dB`

### `stage2 vs v9`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.774620 dB`

当前结论：

- `v7 > v8 > v9`

这是单调排序，不是偶然波动。

## `v8 -> v9` focused guardrail

本轮使用：

- `scripts/eval/gate_probe_subset_guardrail.py`

参考：

- `v8`

候选：

- `v9`

检查项：

- overall
- `speech_family = guodegang_raw`
- `anchor = near_real_0006`

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_summary.json`

结果：

- `FAIL`

失败项：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`

对应数值完全一致：

- reference:
  - `+1.059967 dB`
- candidate:
  - `+0.774620 dB`
- delta:
  - `-0.285347 dB`

并且：

- `6 / 6` 样本全部 regression

## 关键结论

1. `0006` 现在已经有了独立 objective guardrail，不再需要混在 broad speech probe 里口头判断。
2. `v9` 的失败已被进一步确认是：
   - `friend` 侧略好
   - `guodegang 0006` 系统性更差
3. 当前 synthetic `hard/full-overlap/transient` proxy 的真正问题不是“效果一般”，而是：
   - 它把训练信号继续导向 `friend`
   - 而没有导向 `guodegang transient recovery`

## 对下一步的影响

1. 以后任何声称“在补 `0006`”的 follow-up，都应先过：
   - `near_real_guodegang_transient_probe_v1`
2. 如果这条子 probe不过线，就不值得继续进入：
   - broad speech probe
   - 更重的 near-real 自动链
   - 或下一轮训练扩展
3. 当前最值得继续的任务，不再是训练 `v10`，而是：
   - 重做 `0006` 的 objective proxy / clip-family-aware probe

## 验证

- `.\python.exe -m compileall .\scripts\data\build_probe_subset_manifest.py .\scripts\eval\gate_probe_subset_guardrail.py`
- 已生成：
  - `near_real_guodegang_transient_probe_v1_manifest.jsonl`
  - `near_real_friend_speech_probe_v1_manifest.jsonl`
- 已完成：
  - `stage2 vs v7/v8/v9` on `near_real_guodegang_transient_probe_v1`
  - `v8 -> v9` focused guardrail
