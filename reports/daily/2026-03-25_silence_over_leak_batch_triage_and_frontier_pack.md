# 2026-03-25 `silence-over-leak` objective batch triage v2 与 frontier pack

## 背景

`silence-over-leak guardrail v1`
已经证明：

- 在这条更窄的新子题上，
  `legacy_stage2`
  已经掉出前沿；
- 但 `v32 / v8 / v13`
  仍然没有被人耳拉开。

因此当前关键问题不再是：

- 要不要继续逐条全听；

而是：

- 能不能先用程序大筛，
  把明显不行或明显过激的候选淘汰掉，
  再只留极小 frontier 包给人耳。

## 本轮工程修正

### 1. 修正 `include-checkpoint` 被默认 glob 污染

脚本：

- `scripts/eval/rank_checkpoints_on_silence_over_leak_manifest.py`

旧行为有一个边界错误：

- 即使显式传了 `--include-checkpoint`，
  只要没再额外传 `--checkpoint-glob`，
  脚本仍会自动把默认 glob
  `baseline_stft_mask_stage2*`
  全带上。

这会让“短名单 smoke”
  实际变成“全家族大扫”，
  污染实验边界。

本轮已修正为：

- 若显式给了 `--include-checkpoint`
  且没有再给 `--checkpoint-glob`，
  则只评这批显式名单；
- 只有在两者都没给时，
  才回落到默认 glob。

### 2. 补 `raw-target-only` backstop 支持

旧版 present backstop
只看：

- `retention_minus_leak_db`

但这会在：

- `near_real_0001 / 0002`

这类 raw-target-only 样本上失效，
因为它们没有 interference 分量。

本轮已修正为：

- 有 interference 时：
  - 继续看 `retention_minus_leak_db`
- 无 interference 时：
  - 回退到 `target_capture_db`

即：

- `present_backstop_score_db`

### 3. 加入 present non-regression guardrail

只按“更静音 / 更少漏”排序，
会结构性偏爱：

- `v5_absentguard_ft1`

这种极端静音锚点。

本轮已新增：

- baseline：
  - `baseline_stft_mask_stage2`
- 违反 present guardrail 的条件：
  - `target_capture` 比 baseline 差超过 `2.0 dB`
  - 或 `residual_output_share` 比 baseline 高超过 `0.08`

新增输出字段：

- `present_guardrail_violation_count`
- `target_capture_regression_sample_ids`
- `residual_increase_sample_ids`
- `passes_present_guardrail`
- `guardrail_filtered_rank`

## 新 manifest

### 批量 triage manifest v2

- `data/references/real_eval_manifest_silence_over_leak_guardrail_v2.jsonl`

覆盖：

- target-present backstop：
  - `near_real_0001` 到 `near_real_0007`
- absent core：
  - `near_real_0008`
  - `near_real_0009`
  - `near_real_0010`

目的：

- 继续把 absent suppression 当主目标；
- 但不允许候选靠“把 target 一起压坏”
  来刷分。

### frontier 复核 manifest v1

- `data/references/real_eval_manifest_silence_over_leak_frontier_v1.jsonl`

只保留 6 条最有信息量的样本：

- target-present：
  - `near_real_0003`
  - `near_real_0006`
  - `near_real_0007`
- absent：
  - `near_real_0008`
  - `near_real_0009`
  - `near_real_0010`

## objective triage 结果

### 旧 absent-guard shortlist

结果：

- `reports/eval/rank_silence_over_leak_manifest_v2_shortlist/summary.json`

短名单：

- `legacy_stage2`
- `v32`
- `v5`
- `v6`
- `v7`
- `v8`
- `v13`

关键结论：

- raw `combined_rank`
  仍把 `v5_absentguard_ft1`
  排在第一；
- 但 `guardrail_filtered_rank`
  会把它打到最后，
  因为它有 `6` 条 present guardrail violation。

`v5` 的明确违规样本：

- target-capture regression：
  - `near_real_0003`
  - `near_real_0005`
  - `near_real_0007`
- residual increase：
  - `near_real_0001`
  - `near_real_0002`
  - `near_real_0003`
  - `near_real_0004`
  - `near_real_0005`
  - `near_real_0007`

因此这轮可以正式确认：

- `v5`
  只能保留为
  extreme silence anchor，
  不能直接升格为
  这条子题的研究基座。

在旧 shortlist 里，
通过 present guardrail 的前沿是：

- `v8`
- `v32`
- `v13`

### 全家族 batch triage

结果：

- `reports/eval/rank_silence_over_leak_manifest_v2_full/summary.json`

raw `combined_rank`
的 top 仍然会被：

- `v5`
- `v2_musiconly`

这类“过于偏向 suppression”的老分支占据；

但 `guardrail_filtered_rank`
把真正更稳的前沿收敛到了：

1. `v49_v32_absent_adaptermask_v7_only_ft1`
2. `v54_v32_absent_dualdecoder_v7_wave_exactguard_ft1`
3. `v51_v32_absent_adaptermask_reffilm_v7_delta005_ft1`
4. `v50_v32_absent_adaptermask_v7_only_delta005_ft1`
5. `v59_v32_absent_dualdecoder_v7_wave_basedeltaproj_w005_ft1`

其中最值得保留做 frontier 复核的三条是：

- `v49`
  - adapter-mask family 代表
- `v54`
  - dualdecoder exactguard family 代表
- `v59`
  - dualdecoder base-delta-projection family 代表

原因：

- 三条都 `0` violation；
- absent suppression 都强于 `v32`；
- present backstop 也没有被程序 guardrail 判成明显回退；
- 同时覆盖了三种不同的结构路线，
  比只留一堆近重复 adapter/dualdecoder 变体更省人耳。

## frontier blind 包

### pair packs

- `reports/eval/ab_listening_pack_silence_over_leak_frontier_v1_v32_vs_v49_blind`
- `reports/eval/ab_listening_pack_silence_over_leak_frontier_v1_v32_vs_v54_blind`
- `reports/eval/ab_listening_pack_silence_over_leak_frontier_v1_v32_vs_v59_blind`

### 合并多候选 blind 包

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind`

候选顺序：

- `v32`
- `v49_adaptermask`
- `v54_dualdecoder_exactguard`
- `v59_dualdecoder_basedeltaproj_w005`

样本数：

- `6`

资产审计：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind/asset_audit_summary.json`
- 结果：
  - `all_mono = true`
  - `all_have_target = true`

pack 内 objective 摘要：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind/silence_over_leak_objective_summary.json`

聚合结果：

- absent rank：
  - `v54 > v59 > v49 > v32`
- present rank：
  - `v54 > v59 > v49 > v32`
- absent frontier count：
  - `v54 = 3`
  - `v59 = 2`
  - `v49 = 1`
  - `v32 = 0`
- present backstop count：
  - `v54 = 3`
  - `v59 = 3`
  - `v49 = 2`
  - `v32 = 2`

这说明：

- 在“程序先筛完，再只留 6 条边界样本”的口径下，
  最值得被人耳最终复核的 challenger
  已经不是旧 `v8 / v13`，
  而是：
  - `v54`
  - `v59`
  - `v49`

## 当前裁决

1. objective batch triage
   现在已经可以承担：
   - 大批量淘汰明显更漏、
     或明显靠过度静音刷分的候选
2. 但它仍不能单独完成最终放行：
   - `v5`
     就证明了
     “raw silence score 高”
     不等于
     “是更好的实际方案”
3. 当前新的最小 frontier
   已经收敛成：
   - `v32`
   - `v49`
   - `v54`
   - `v59`
4. 下一步不该再开大包；
   而是只听：
   - `decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind`

如果这 6 条样本里：

- `v54 / v59`
  仍能在人耳上稳定优于 `v32`，
  才值得继续把这条 absent/weak-target 子题往前推进；

否则就应把本轮结论写成：

- objective 可筛，
  但当前 frontier 仍未形成人耳可裁决的新赢家。
