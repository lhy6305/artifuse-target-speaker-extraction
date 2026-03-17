# 2026-03-18 Near-Real Trade-Off Bucketization

## 本次目的

当前 `analyze_listening_pack_tradeoff.py` 虽然已经能给出：

- `better_source_retention`
- `more_interference_leaky`
- `more_residual_heavy`
- `better_retention_minus_leak`

但此前 summary 主要还是“整包均值 + 整包计数”，还不够直接回答这几个最关键的问题：

1. `speech-only near-real` 的问题到底集中在哪些样本桶；
2. `target absent` guardrail 的收益到底落在哪个桶；
3. 哪些 candidate 看起来整体还行，但其实只是被 `music` 或 mixed bucket 拉起来。

因此本轮先不继续开新训练，而是先把 near-real trade-off 分桶能力补到现有分析脚本里。

## 工程更新

已更新：

- `scripts/eval/analyze_listening_pack_tradeoff.py`

新增输出维度：

- `scenario_groups`
- `target_status_groups`
- `interference_profile_groups`
- `target_interference_bucket_groups`

当前分桶规则来自 near-real 原始 `sample_meta.json` 的 `components`：

- `target_status`：
  - `target_present`
  - `target_absent`
- `interference_profile`：
  - `none`
  - `speech`
  - `music`
  - `music_plus_speech`
  - 以及后续可扩展的其他类别
- `target_interference_bucket`：
  - 例如 `target_present__speech`
  - `target_absent__speech`
  - `target_present__none`

这样后面看 near-real，不再需要手工从 10 条样本里肉眼拆桶。

## 本轮重跑对象

已重跑以下 near-real blind 包的 `tradeoff_analysis`：

1. `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v1_blind/`
2. `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v3_w0005_blind/`
3. `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v4_speechfocus_ft1_blind/`
4. `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v5_absentguard_ft1_blind/`

## 分桶结论

### 1. `legacy_transient_leakguard_probe_v1` 的主要正收益确实集中在带 music 的桶，不在 speech-only 桶

`v1` 相对 `legacy_stage2`：

- `target_present__music`
  - `better_retention_minus_leak = v1 1/1`
- `target_present__music_plus_speech`
  - `better_retention_minus_leak = v1 1/1`

但真正最难的 `speech-only near-real` 桶仍然没有修好：

- `target_present__speech`
  - `better_retention_minus_leak = legacy_stage2 3/3`
  - `more_interference_leaky = v1 2/3, tie 1/3`
  - `more_residual_heavy = v1 3/3`

同时 raw-only guardrail 也仍有问题：

- `target_present__none`
  - `more_residual_heavy = v1 2/2`

这把 `v1` 当前真正没修好的点钉得更清楚了：

- 不是“整体都不稳”；
- 而是：
  - `music` 相关桶有收益；
  - `speech-only` 和 `raw-only` guardrail 仍然偏弱。

### 2. `legacy_transient_leakguard_probe_v3_w0005` 更像“副作用更轻的保守对照”，不是 speech-only 修复版

`v3_w0005` 相对 `legacy_stage2`：

- `target_present__speech`
  - `better_retention_minus_leak = legacy_stage2 3/3`
  - `more_interference_leaky = v3 3/3`

说明它并没有修好 `speech-only near-real` 的主问题。

但它确实在两个 guardrail 桶上比 `v1` 更收敛：

- `target_present__none`
  - `more_residual_heavy = tie 2/2`
  - 相比 `v1` 的 `2/2 residual-heavy` 明显更温和
- `target_absent__speech`
  - `more_interference_leaky = legacy_stage2 1, tie 1`
  - 且 `more_residual_heavy = tie 2/2`

因此 `v3` 当前更适合继续保留为：

- 一个比 `v1` 更保守、更轻 residual 的 side-effect 对照锚点；
- 而不是新的主候选。

### 3. `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 没有把 speech-only near-real 真正救回来

这轮最重要的诊断结论之一是：

- 把 selector 收窄到 speech-only，并不会自动修好 `target_present__speech`

桶化结果非常直接：

- `target_present__speech`
  - `better_retention_minus_leak = legacy_stage2 3/3`
  - `more_interference_leaky = v4 2/3, tie 1/3`

也就是说：

- `v4_speechfocus_ft1` 在 synthetic 上继续提 speech-like recipe；
- 但 near-real `speech-only` 桶里，关键 trade-off 仍然输给 `legacy_stage2`。

这进一步支持当前总览中的判断：

- “继续把 selector 缩到 speech-only”不是当前真正缺的那一环。

### 4. `legacy_transient_leakguard_probe_v5_absentguard_ft1` 的收益主要落在 `target_absent__speech`，但代价分散到 raw-only 和 music 桶

这是本轮最有价值的新澄清。

`v5_absentguard_ft1` 相对 `legacy_stage2`：

- `target_absent__speech`
  - `more_interference_leaky = legacy_stage2 2/2`
  - 说明 absent guardrail 在它该工作的桶里，确实是有效的

同时在 `target_present__speech` 桶里，它也不是纯失败：

- `better_retention_minus_leak = v5 2/3, tie 1/3`
- `more_interference_leaky = legacy_stage2 3/3`

但问题是，这个收益不是“免费”的。

它在其他 guardrail 桶里付出的代价非常清楚：

- `target_present__none`
  - `more_residual_heavy = v5 2/2`
- `target_present__music`
  - `more_residual_heavy = v5 1/1`
  - `target_capture_db` 也明显更差
- `target_present__music_plus_speech`
  - `more_residual_heavy = v5 1/1`
  - `target_capture_db` 明显继续下降

这解释了为什么 `v5` 在整包上看起来像“过抑制 / residual-heavy”：

- 它不是每个桶都更差；
- 而是：
  - 在 `target_absent__speech` 这类桶里确实更强；
  - 但把 raw-only 和带 music 的 target-present 桶一起压伤了。

## 当前更新后的判断

本轮分桶后，当前仓库对几条候选的理解应更新为：

1. `legacy_transient_leakguard_probe_v1`
   - 仍是当前第一 objective-only 候选；
   - 但它的真实主缺口已被更明确地定位到：
     - `target_present__speech`
     - `target_present__none`
2. `legacy_transient_leakguard_probe_v3_w0005`
   - 继续保留为更保守的 residual side-effect 对照；
   - 它不能修 speech-only 主问题，但能帮助判断“副作用有没有收回来”
3. `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
   - 可以继续保留为“speech-only selector 不是根因解”的反例；
   - 不再适合作为继续缩 selector 的依据
4. `legacy_transient_leakguard_probe_v5_absentguard_ft1`
   - 继续保留为“absent guardrail 机制有效，但会伤其他桶”的机制参考；
   - 它证明：
     - `target_absent__speech` 确实能被显式压住；
     - 但当前形式不能直接升为候选主线

## 对下一步的直接约束

如果还要继续 objective-only 小步 follow-up，筛选标准不应再只看整包均值，而应至少同时过这三组桶：

1. `target_present__speech`
   - 不能继续稳定输给 `legacy_stage2`
2. `target_present__none`
   - 不能继续把 raw-only 压成更 residual-heavy
3. `target_absent__speech`
   - 需要保留当前 absent suppression 的部分收益

大白话讲，下一步如果还做小步实验，目标应该是：

- 尽量保住 `v5` 在 `target_absent__speech` 上那部分有效 suppression；
- 但不要再把 `raw-only` 和 `speech-only target-present` 一起压坏。

当前这也意味着：

- 不该继续沿 `v4` 这条“再收窄 selector”方向走；
- 也不该继续沿 `v5` 这条“大 absent weight”直接放大；
- 更合理的是：
  - 继续把 `v1` 当主基座；
  - 把 `v3` 当副作用锚点；
  - 若再开新点，必须显式按上述三组桶做 gate。
