# 2026-03-17 Speech-Only Leak Guardrail Follow-Up

## 背景

在 `legacy_transient_leakguard_probe_v1` 与 `v3_w0005` 之后，当前最明确的未解决点仍然是：

- `near_real_0003`
- `near_real_0004`

这两条 speech-only near-real 样本。

`v1` 已经证明：

1. synthetic 默认 val 可以明显提升；
2. `interference_projection_ratio` 也能系统性压低；
3. 但 speech-only near-real 上仍存在：
   - leakage
   - residual-heavy
   - `retention_minus_leak` 回退

因此本轮没有再继续扫更小的 `interference_weight`，而是直接测试另一条更局部的假设：

- 保留 `v1` 的 leak guardrail 主体；
- 但把 `interference selector` 从“全 interference recipe”收窄到：
  - `target_clean_speech`
  - `target_hard_speech`

希望它能更直接修 speech-like interference 的 near-real 回退。

## Probe V4: `legacy_transient_leakguard_probe_v4_speechfocus_ft1`

### 配置

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v4_speechfocus_ft1/`
- warm-start：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v1/best.pt`
- 训练：
  - `epochs = 2`
  - `batch_size = 16`
  - `lr = 1e-4`
- transient 分支：
  - `transient_weight = 0.002`
  - `transient_focus_recipes = [target_clean_speech]`
  - `transient_focus_patterns = [target_full, target_absent_head, target_absent_tail]`
- interference 分支：
  - `interference_weight = 0.01`
  - `interference_focus_recipes = [target_clean_speech, target_hard_speech]`
  - `interference_focus_patterns = [target_full, target_absent_head, target_absent_tail]`

和 `v1` 的核心差异只有一条：

- `v1` 会在全 interference recipe 上施加 leak guardrail；
- `v4_speechfocus_ft1` 只盯 speech-like recipe。

## Synthetic 结果

### Eval

- eval：
  - `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v4_speechfocus_ft1_eval/`

当前指标：

- `loss = 0.024825`
- `waveform_l1 = 0.012926`
- `stft_l1 = 0.022229`
- `sisdr_db = -9.377`
- `transient_presence_l1 = 0.270545`
- `interference_projection_ratio = 0.024327`

对比 `legacy stage2`：

- `sisdr_db: -10.324 -> -9.377`
- `interference_projection_ratio: 0.0713 -> 0.0243`

### 默认 val compare

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v4_speechfocus_ft1_on_default/`

相对 `legacy stage2`：

- `avg_sisdr_delta_db = +0.969665`
- `improved_count = 369`
- `regressed_count = 88`

这说明它在 synthetic 默认 val 上，整体甚至比 `v1` 更强一小步。

### 相对 `v1`

- `reports/eval/compare_v1_vs_legacy_transient_leakguard_probe_v4_speechfocus_ft1_on_default/`
- `reports/eval/compare_v1_vs_legacy_transient_leakguard_probe_v4_speechfocus_ft1_on_speech_recipes/`

相对 `legacy_transient_leakguard_probe_v1`：

- 默认 val：
  - `avg_sisdr_delta_db = +0.119893`
- speech recipes only：
  - `avg_sisdr_delta_db = +0.166382`

但这条提升不是“全线更稳”，而是有明显 trade-off：

- 继续收益：
  - `target_clean_speech: +0.208 dB`
  - `target_hard_speech: +0.110 dB`
  - `target_clean_plus_music: +0.406 dB`
- 明显回退：
  - `target_only: -0.380 dB`
  - `target_singing_vocal: -0.301 dB`
  - `target_music: -0.023 dB`

当前理解：

- 它不是单纯“speech-only 修好了，其他不受影响”；
- 更像是：
  - 继续把有干扰的 speech-like synthetic 样本往前推了一点；
  - 同时开始吃掉 `target_only` 与非 speech 干扰边界。

## Near-Real 自动诊断

已导出并补跑：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v4_speechfocus_ft1_blind/`

### 带宽

解码后：

- `legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 3`
- `legacy_stage2 = 1`
- `tie = 6`

当前理解：

- 它没有把带宽收窄风险压下去；
- 甚至比 `v1` 的 `2 / 0 / 8` 更差一点。

### 瞬态

解码后：

- `legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 7`
- `legacy_stage2 = 1`
- `tie = 2`

当前理解：

- 这项没有优于 `v1`；
- 仍处在“明显更 transient-lossy”的负面区间。

### Trade-Off

解码后计数：

- `better_source_retention`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 2`
  - `legacy_stage2 = 1`
  - `tie = 4`
  - `not_applicable = 3`
- `more_interference_leaky`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 5`
  - `legacy_stage2 = 1`
  - `tie = 2`
  - `not_applicable = 2`
- `more_residual_heavy`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 2`
  - `legacy_stage2 = 2`
  - `tie = 6`
- `better_retention_minus_leak`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 2`
  - `legacy_stage2 = 3`
  - `not_applicable = 5`

解码后均值：

- `legacy_stage2`
  - `target_capture_db = -12.578`
  - `interference_capture_db = -45.209`
  - `retention_minus_leak_db = 27.905`
  - `residual_output_share = 0.661`
- `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `target_capture_db = -9.647`
  - `interference_capture_db = -42.809`
  - `retention_minus_leak_db = 28.397`
  - `residual_output_share = 0.664`

相对 `v1` 的关键差异是：

1. `residual_output_share`
   - `0.679 -> 0.664`
   - 确实更轻了一点；
2. 但 `retention_minus_leak_db`
   - `28.938 -> 28.397`
   - 又退回了一部分；
3. `more_interference_leaky`
   - 仍然是 `5` 条；
4. 因此它不是“在 speech-only near-real 上已经修正”的版本。

### 关键 speech-only 样本

`near_real_0003`：

- `delta_target_capture_db = -1.502`
- `delta_interference_capture_db = -0.125`
- `delta_residual_output_share = +0.103`
- `delta_retention_minus_leak_db = -1.377`

`near_real_0004`：

- `delta_target_capture_db = -0.531`
- `delta_interference_capture_db = +4.188`
- `delta_residual_output_share = +0.079`
- `delta_retention_minus_leak_db = -4.718`

这两条正是当前最关心的 speech-only near-real 回退点，但 `v4_speechfocus_ft1` 都没有修好。

## 当前结论

截至本轮，`legacy_transient_leakguard_probe_v4_speechfocus_ft1` 的定位是：

1. 它不是失败实验。
2. 它在 synthetic 上确实很强：
   - 相对 `legacy stage2` 达到 `+0.970 dB`
   - 相对 `v1` 也还有 `+0.120 dB`
3. 它也证明了一条很重要的事实：
   - 把 `interference selector` 收窄到 speech-like recipe，
   - 不等于 speech-only near-real 回退就会自动修好。
4. 它当前的真实形态更像：
   - synthetic speech-like 样本继续提分；
   - residual side effect 比 `v1` 略轻；
   - 但 near-real leakage 仍高；
   - `retention_minus_leak` 仍未优于 `v1`；
   - `target_only / singing` guardrail 还开始回退。

因此当前不把它升级为：

- 新的默认主候选；
- 也不把它排到 `v3_w0005` 前面。

更准确的定位应是：

- 一条有价值的诊断性 follow-up；
- 证明“单纯收窄到 speech-only selector”不是当前真正缺的那一环。

## 下一步

如果仍然不能做人耳听评，当前更合理的继续方向不是：

- 继续把 selector 缩得更窄；
- 或继续在 speech-only selector 周围扫更多近邻。

而应优先考虑：

1. 保留 `v1` 作为第一 objective-only 候选；
2. 保留 `v3_w0005` 作为更保守 residual 对照；
3. 把 `v4_speechfocus_ft1` 作为“speech-only selector 不会自动修正 near-real speech 回退”的反例与诊断参考；
4. 下一步若还要继续做 objective-only 小步实验，应直接针对：
   - speech-only near-real 的 residual / leak 机制
   - 或 target absent / speech absent 的 guardrail
   做更贴症状的约束，而不是继续改 selector 覆盖范围。
