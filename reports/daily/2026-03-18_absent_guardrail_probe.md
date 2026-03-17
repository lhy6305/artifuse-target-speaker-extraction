# 2026-03-18 Absent Guardrail Probe

## 背景

在 `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 之后，当前更清楚的判断已经变成：

- 只把 `interference selector` 收窄到 speech-only，并不能自动修好 speech-only near-real 回退；
- 真正还没被显式约束住的一个点，是 `target absent / intermittent` 空窗段里的误保留与伪目标泄漏。

因此这轮不再继续扫更窄 selector，而是直接把 synthetic metadata 里已有的
`target_absent_intervals` 接入训练与评估，验证一个更直接的假设：

- 如果显式惩罚目标缺席区间的输出能量，
- 是否能在不明显伤主线的前提下，
- 把 speech-only / target-absent 场景里的泄漏继续压下去。

## 工程落地

本轮已经完成 absent-guardrail 的第一版工程接入：

- `src/tse_prefix/data/synthetic_dataset.py`
  - 训练 batch 现会实际携带 `target_absent_intervals`
- `src/tse_prefix/pipeline/baseline_train.py`
  - 新增 `absent_interval_l1_loss(...)`
  - `LossBreakdown` 新增 `absent_interval_l1`
- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`
  - 已支持：
    - `--loss-absent-weight`
    - `--loss-absent-focus-recipes`
    - `--loss-absent-focus-patterns`
    - `--loss-absent-min-target-ratio`
    - `--loss-absent-max-target-ratio`

已完成的基础验证：

- `python -m compileall src scripts/train/train_stft_mask_baseline.py scripts/eval/eval_stft_mask_baseline.py`
- 两个 smoke run：
  - `baseline_stft_mask_absentguard_smoke`
  - `baseline_stft_mask_absentguard_smoke_w20`

结论：

- 工程入口已可复用；
- 后续若要继续做更保守的 absent-guard 微调，不需要再重复补基础代码。

## Probe V5: `legacy_transient_leakguard_probe_v5_absentguard_ft1`

### 配置

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v5_absentguard_ft1/`
- warm-start：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v1/best.pt`
- 训练：
  - `epochs = 2`
  - `batch_size = 16`
  - `lr = 1e-4`
- 保留 `v1` 主体：
  - `conditioning_mode = legacy_bias`
  - `transient_weight = 0.002`
  - `interference_weight = 0.01`
- 新增 absent guardrail：
  - `absent_weight = 20`
  - `absent_focus_recipes = [target_clean_speech, target_hard_speech, target_clean_plus_music, target_hard_plus_music]`
  - `absent_focus_patterns = [target_absent_head, target_absent_tail, target_intermittent]`

## Synthetic 结果

### Eval

- `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v5_absentguard_ft1_eval/`

当前指标：

- `loss = 0.025934`
- `waveform_l1 = 0.012862`
- `stft_l1 = 0.023659`
- `sisdr_db = -10.185`
- `transient_presence_l1 = 0.270673`
- `interference_projection_ratio = 0.032695`
- `absent_interval_l1 = 0.00001870`

### 相对 `v1` 的 absent 指标变化

为避免只看新分支，已额外补跑：

- `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v1_eval_with_absent_metric/`

关键对比：

- `legacy_transient_leakguard_probe_v1`
  - `absent_interval_l1 = 0.00010835`
  - `sisdr_db = -9.492`
- `legacy_transient_leakguard_probe_v5_absentguard_ft1`
  - `absent_interval_l1 = 0.00001870`
  - `sisdr_db = -10.185`

这说明：

1. absent 空窗段泄漏确实可以被显著压低；
2. 但它不是“几乎免费”的提升；
3. 代价已经反映到整体 source retention / SI-SDR 上。

### 默认 val compare

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v5_absentguard_ft1_on_default/`
- `reports/eval/compare_v1_vs_legacy_transient_leakguard_probe_v5_absentguard_ft1_on_default/`
- `reports/eval/compare_v1_vs_legacy_transient_leakguard_probe_v5_absentguard_ft1_on_absentguard_recipes/`

相对 `legacy stage2`：

- `avg_sisdr_delta_db = +0.187692`

相对 `legacy_transient_leakguard_probe_v1`：

- 默认全分布：
  - `avg_sisdr_delta_db = -0.662080`
- 只看本轮 focused absent-guard recipes：
  - `avg_sisdr_delta_db = -0.894569`

当前理解：

- `v5` 没有形成“只在 absent 场景更好、其他几乎不动”的局部修正；
- 相反，它对 `v1` 是较大面积回退。

## Near-Real 自动诊断

已导出并补跑：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v5_absentguard_ft1_blind/`

### 带宽

`bandwidth_analysis` 解码后：

- `narrower_candidate_counts`
  - `tie = 9`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1 = 1`

当前理解：

- 这版没有形成明显更广泛的“电话音 / 窄带化”新增风险；
- 但也不能把它解读成 near-real 已经转正。

### 瞬态

`transient_analysis` 候选计数：

- `tie = 2`
- `legacy_stage2 = 4`
- `legacy_transient_leakguard_probe_v5_absentguard_ft1 = 4`

关键负样本：

- `near_real_0003`
- `near_real_0005`
- `near_real_0007`
- `near_real_0010`

这些样本上，`v5` 仍反复被标成更 transient-lossy。

### Trade-Off

`tradeoff_analysis` 解码后计数：

- `better_source_retention`
  - `legacy_stage2 = 7`
  - `not_applicable = 3`
- `more_interference_leaky`
  - `legacy_stage2 = 8`
  - `not_applicable = 2`
- `more_residual_heavy`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1 = 7`
  - `tie = 3`
- `better_retention_minus_leak`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1 = 4`
  - `tie = 1`
  - `not_applicable = 5`

解码后均值：

- `legacy_stage2`
  - `target_capture_db = -12.578`
  - `interference_capture_db = -45.209`
  - `retention_minus_leak_db = 27.905`
  - `residual_output_share = 0.661`
- `legacy_transient_leakguard_probe_v5_absentguard_ft1`
  - `target_capture_db = -16.521`
  - `interference_capture_db = -63.817`
  - `retention_minus_leak_db = 36.329`
  - `residual_output_share = 0.748`

这里最容易误判的一点是：

- `retention_minus_leak_db` 数字看起来更高；
- 但这是建立在“把干扰压得更狠，同时把目标也压掉更多”的基础上；
- 它并不是更均衡，而是明显更 residual-heavy / over-suppressed。

### 关键样本

`near_real_0003`：

- `delta_target_capture_db = -2.646`
- `delta_interference_capture_db = -2.356`
- `delta_residual_output_share = +0.128`
- `delta_retention_minus_leak_db = -0.291`

`near_real_0004`：

- `delta_target_capture_db = -1.157`
- `delta_interference_capture_db = -11.251`
- `delta_residual_output_share = +0.110`
- `delta_retention_minus_leak_db = +10.094`

`near_real_0005`：

- `delta_target_capture_db = -5.968`
- `delta_interference_capture_db = -10.472`
- `delta_residual_output_share = +0.186`

`near_real_0007`：

- `delta_target_capture_db = -14.016`
- `delta_interference_capture_db = -23.744`
- `delta_residual_output_share = +0.111`

`near_real_0010`：

- target-absent 抑制确实更狠；
- 但这更像“整体继续往强 suppress 推”，不是一个可直接晋升的平衡版本。

## 当前结论

截至本轮，`legacy_transient_leakguard_probe_v5_absentguard_ft1` 的定位是：

1. 一个有价值的机制探针；
2. 它证明 `target_absent_intervals -> absent_interval_l1` 这条显式 guardrail 是有效可控的；
3. 但当前 `absent_weight = 20` 的做法明显过猛：
   - absent leakage 降下来了；
   - source retention 也被一起压伤；
   - near-real 变得更 residual-heavy。

因此当前不把它升级为新的 objective-only 候选，也不排到：

- `legacy_transient_leakguard_probe_v1`
- `legacy_transient_leakguard_probe_v3_w0005`

之前。

## Quick Gate: `legacy_transient_leakguard_probe_v6_absentguard_w5_ft1`

为避免直接停在“`w20` 太猛”这个判断上，本轮又补了一个更保守的小步 quick gate：

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v6_absentguard_w5_ft1/`
- 配置保持与 `v5` 相同；
- 只把：
  - `absent_weight = 20`
  - 调整为 `absent_weight = 5`

synthetic 结果：

- eval：
  - `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v6_absentguard_w5_ft1_eval/`
- 当前指标：
  - `sisdr_db = -9.851571`
  - `interference_projection_ratio = 0.035498`
  - `absent_interval_l1 = 0.00004554`

对比结果：

- 相对 `legacy stage2`：
  - `avg_sisdr_delta_db = +0.493601`
- 相对 `legacy_transient_leakguard_probe_v1`：
  - 默认全分布：
    - `avg_sisdr_delta_db = -0.356172`
  - focused absent-guard recipes：
    - `avg_sisdr_delta_db = -0.501773`

当前理解：

1. `w5` 确实比 `w20` 收回了一部分过抑制代价；
2. 但它仍没有回到 `v1`；
3. 连本轮最想修的 focused absent recipes 也仍然系统性落后；
4. 因此这版不再继续导出 near-real blind 包，直接止损。

## 下一步建议

若后续还要继续沿 absent-guardrail 往下走，约束应改成：

1. 保留现有 absent-loss 基础设施，不再重复补工程；
2. 当前也不继续沿 `absent_weight = 5` 这一级别直接扩训；
3. 若再开新点，只做更保守的小步版本：
   - 更低 absent weight
   - 更窄 selector
   - 继续与 `v1` 对照
4. 是否保留新候选，必须同时看：
   - `absent_interval_l1`
   - 默认 val 相对 `v1` 的退化
   - near-real `more_residual_heavy`
   - near-real `better_source_retention`
   - `near_real_0003 / 0004 / 0005 / 0007 / 0010`
