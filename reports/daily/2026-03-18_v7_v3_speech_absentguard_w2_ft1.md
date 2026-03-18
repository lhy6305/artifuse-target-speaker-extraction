# 2026-03-18 `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`

## 本次目的

在 near-real hard gate 固化之后，当前最明确的 objective-only 缺口已经收敛为：

1. `target_present__speech`
2. `target_present__none`
3. `target_absent__speech`

此前：

- `v1` 是当前最强 objective-only 候选，但仍卡：
  - `target_present__speech`
  - `target_present__none`
- `v3_w0005` 更像副作用回收版，只卡：
  - `target_present__speech`
- `v5_absentguard_ft1` 证明了 absent suppression 机制有效，但副作用太重

因此这一步不再开大步近邻试探，而是从 `v3_w0005` 出发，做一个更保守的：

- speech-only + absent guard
- `absent_weight = 2`

小步 follow-up，看能否：

1. 保住 `v3` 的 raw-only guardrail；
2. 吸收一部分 `v5` 的 target-absent speech suppression；
3. 至少把 `v3` 的 `target_present__speech` 短板补上。

## 实验配置

实验名：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`

初始化自：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v3_w0005`

训练要点：

- `conditioning_mode = legacy_bias`
- `transient_weight = 0.002`
- `interference_weight = 0.005`
- `absent_weight = 2.0`
- `absent_focus_recipes`:
  - `target_clean_speech`
  - `target_hard_speech`
- `absent_focus_patterns`:
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
- `absent_max_target_ratio = 0.9`
- 2 epochs / batch size 16 / lr `1e-4`

训练产物：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1/`

训练摘要：

- `best_val_loss = 0.021886`
- `elapsed_sec = 41.868`

## Synthetic 结果

评估产物：

- `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_eval/`

默认 val 指标：

- `loss = 0.021886`
- `waveform_l1 = 0.012964`
- `stft_l1 = 0.014187`
- `sisdr_db = -9.807330`
- `transient_presence_l1 = 0.683048`
- `interference_projection_ratio = 0.049303`
- `absent_interval_l1 = 0.000107903`

相对 `legacy_stage2`：

- `avg_sisdr_delta_db = +0.461595`
- `improved_count = 266`
- `regressed_count = 152`

相对 `v3_w0005`：

- `avg_sisdr_delta_db = +0.077777`
- `improved_count = 240`
- `regressed_count = 122`

当前解释：

- `v7` 相对 `stage2` 仍是明显正增益；
- 相对 `v3` 只有小幅 synthetic 增益，但方向为正；
- 它更像是“在 `v3` 基础上补 absent guard 的保守升级”，不是新的大跃迁分支。

## Near-Real 结果

### 相对 `legacy_stage2`

blind 包：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_blind/`

hard gate：

- `overall_pass = false`
- failed buckets:
  - `target_present__speech`

更细结论：

1. `target_present__none`
   - pass
   - `more_residual_heavy` 没有继续劣化到 baseline 之下
2. `target_absent__speech`
   - pass
   - `interference_capture_db`:
     - `legacy_stage2 = -41.2111`
     - `v7 = -46.4035`
3. `target_present__speech`
   - 仍 fail
   - `better_retention_minus_leak`:
     - `legacy_stage2 = 2`
     - `v7 = 1`
   - `more_residual_heavy`:
     - `legacy_stage2 = 0`
     - `v7 = 1`

当前解释：

- `v7` 已经把 `v1 / v5` 那种 raw-only 副作用收回来了；
- 也保住了 absent speech suppression；
- 但还没有正面赢过 `legacy_stage2` 的 speech-only target-present。

### 相对 `v3_w0005`

blind 包：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_v3_w0005_vs_v7_v3_speech_absentguard_w2_ft1_blind/`

hard gate：

- `overall_pass = true`
- `failed_buckets = []`

更细结论：

1. `target_present__speech`
   - `better_retention_minus_leak`:
     - `v3 = 0`
     - `v7 = 3`
   - `more_interference_leaky`:
     - `v3 = 3`
     - `v7 = 0`
2. `target_present__none`
   - pass
   - `more_residual_heavy` 仍是 tie
3. `target_absent__speech`
   - pass
   - `interference_capture_db`:
     - `v3 = -41.9922`
     - `v7 = -46.4035`

当前解释：

- `v7` 对 `v3` 已经不是“风格不同”；
- 它是三类关键桶上的严格改进版。

## 当前结论

这轮最重要的更新不是“`v7` 通过了 near-real 主 gate”，而是：

1. `v7` 仍不能替换 `legacy_stage2`
   - 因为它还 fail `target_present__speech`
2. `v7` 也还不能替换 `legacy_transient_leakguard_probe_v1`
   - 因为 `v1` 仍是当前相对 `legacy_stage2` 更强的 objective-only 候选主基座
3. 但 `v7` 可以替换 `v3_w0005` 成为新的第二保留候选
   - 因为它对 `v3` 已经通过 hard gate
   - 同时保住了：
     - raw-only guardrail
     - target-absent speech suppression

因此当前 objective-only 保留顺位更新为：

1. `legacy_transient_leakguard_probe_v1`
2. `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
3. `legacy_transient_leakguard_probe_v3_w0005`
4. 诊断参考：
   - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
   - `legacy_transient_leakguard_probe_v5_absentguard_ft1`

## 对下一步的约束

后续如果还要继续 objective-only 小步推进，方向应继续收窄为：

1. 以 `v1` 为主基座；
2. 以 `v7` 为新的保守升级锚点；
3. 新候选至少同时做到：
   - 不再输 `target_present__speech`
   - 不再伤 `target_present__none`
   - 不丢 `target_absent__speech`

换句话说，`v7` 已经证明：

- “保守 absent guard + speech focus” 这条线不是死路；
- 但它目前还只够把 `v3` 升级掉，不够把 `stage2` 或 `v1` 升级掉。
