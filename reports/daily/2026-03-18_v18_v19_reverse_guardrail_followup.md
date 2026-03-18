# 2026-03-18 v18 v19 reverse guardrail follow-up

## 背景

上一轮 `v16 / v17` 已经把问题收窄到一条更具体的 objective：

- manifest 固定为：
  - `guodegang_absent_proxy_v3_strict ∪ v16_v12_reverse_guardrail_proxy_v1`
- selector 也已明确分成两路：
  - `target_hard_speech / target_full / friend_hard_negative_segments`
  - `target_clean_speech / target_absent_head|tail|intermittent / speech_interference_clean_pool / interference_gain_db >= -0.8906667`

其中：

- `v16`
  - 已经非常接近 synthetic dual-proxy gate；
  - 但 absent `v3 / v4` 仍各差一点；
- `v17`
  - 证明简单下调 `absent_weight`
  - 会把 `anchor` 和 default 一起拉回去。

因此本轮 follow-up 不再改 manifest，也不再继续降 `absent_weight`，而只试两种更局部的预算调整：

1. `v18`
   - 同时把 transient / interference 权重各减半；
2. `v19`
   - 保持 `transient_weight = 0.002`
   - 只把 `interference_weight = 0.005 -> 0.0075`

## `v18 = legacy_transient_leakguard_probe_v18_v12_absent_proxy_v3_reverse_guardrail_v1_ti_half_ft1`

### 配置

- warm-start：
  - `v12`
- manifest：
  - `train_manifest_v16_absent_proxy_v3_plus_reverse_guardrail_v1.jsonl`
  - `val_manifest_v16_absent_proxy_v3_plus_reverse_guardrail_v1.jsonl`
- 预算：
  - `epochs = 1`
  - `lr = 1e-5`
  - `global_steps = 23`
- loss：
  - `transient_weight = 0.001`
  - `interference_weight = 0.0025`
  - `absent_weight = 1.0`

selector 命中保持与 `v16 / v17` 相同：

- train：
  - transient / interference = `51 / 90`
  - absent = `24 / 90`
- val：
  - transient / interference = `18 / 27`
  - absent = `4 / 27`

### synthetic 结果

相对 `legacy_stage2`：

- default：
  - `+0.154860 dB`
- `anchor_proxy_v1`：
  - `+2.123964 dB`
- `absent_proxy_v3_strict`：
  - `+0.023017 dB`
- `absent_proxy_v4_broad`：
  - `+0.112959 dB`

相对 `v12`：

- default：
  - `-0.016253 dB`
- reverse guardrail proxy：
  - `-0.069016 dB`
- `anchor_proxy_v1`：
  - `+0.233116 dB`
- `absent_proxy_v3_strict`：
  - `-0.065609 dB`
- `absent_proxy_v4_broad`：
  - `-0.042189 dB`

synthetic dual-proxy gate：

- `FAIL`
- failed rules：
  - `absent_proxy_v3_strict`
  - `absent_proxy_v4_broad`

### 结论

1. `v18` 不保留。
2. 把 transient / interference 一起减半，并没有把 `v16` 的最后一点 absent 缺口补回来。
3. 这一步反而说明：
   - 当前 `v16` 路线的关键矛盾
   - 不是“预算整体太重”
   - 而更像是：
     - transient / interference 侧的形状要改
     - 而不是直接一起降。

## `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`

### 配置

- warm-start：
  - `v12`
- manifest：
  - 与 `v16 / v18` 相同
- 预算：
  - `epochs = 1`
  - `lr = 1e-5`
  - `global_steps = 23`
- loss：
  - `transient_weight = 0.002`
  - `interference_weight = 0.0075`
  - `absent_weight = 1.0`

selector 命中仍与 `v16 / v18` 相同：

- train：
  - transient / interference = `51 / 90`
  - absent = `24 / 90`
- val：
  - transient / interference = `18 / 27`
  - absent = `4 / 27`

### synthetic 结果

相对 `legacy_stage2`：

- default：
  - `+0.216015 dB`
- `anchor_proxy_v1`：
  - `+2.237552 dB`
- `absent_proxy_v3_strict`：
  - `+0.142228 dB`
- `absent_proxy_v4_broad`：
  - `+0.195950 dB`

相对 `v12`：

- default：
  - `+0.044902 dB`
- reverse guardrail proxy：
  - `-0.076964 dB`
- `anchor_proxy_v1`：
  - `+0.346704 dB`
- `absent_proxy_v3_strict`：
  - `+0.053602 dB`
- `absent_proxy_v4_broad`：
  - `+0.040802 dB`

synthetic dual-proxy gate：

- `PASS`

解释：

- `v19` 是当前第一条真正通过：
  - `anchor_proxy_v1`
  - `absent_proxy_v3_strict`
  - `absent_proxy_v4_broad`
  这三项 synthetic pre-screen 的 absent follow-up。

### near-real speech probe

分析产物：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- `.../speech_followup_gate_vs_v12_summary.json`

相对 `legacy_stage2`：

- overall：
  - `-0.009309 dB`
- `friend_raw`：
  - `-0.414640 dB`
- `near_real_0003`：
  - `-0.913926 dB`
- `near_real_0004`：
  - `+0.084646 dB`
- `near_real_0006`：
  - `+1.206683 dB`

相对 `v12`：

- overall：
  - `-0.011926 dB`
- `friend_raw`：
  - `-0.039734 dB`
- `near_real_0003`：
  - `-0.068178 dB`
- `near_real_0004`：
  - `-0.011290 dB`
- `near_real_0006`：
  - `+0.071497 dB`

`speech_followup_gate_vs_v12`：

- `FAIL`
- failed rules：
  - `speech_probe_overall_floor`
  - `speech_probe_friend_raw_floor`
  - `anchor_0003_gain_floor`
  - `anchor_0004_gain_floor`

解释：

- `v19` 已经把 `0006` 继续往前推；
- broad default 也优于 `v12`；
- 但 broad near-real 仍未能替掉 `v12`；
- 当前主要卡点已经不是 `0006`，而是：
  - `friend_raw`
  - `0003`
  - `0004`

### near-real `guodegang` probe

分析产物：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- `.../probe_subset_guardrail_vs_v8_with_clips.json`

相对 `legacy_stage2`：

- overall：
  - `+1.206683 dB`
- `guodegang_anchor_120s`：
  - `+0.355476 dB`
- `guodegang_absent_480s`：
  - `+2.057890 dB`

相对 `v8`：

- overall：
  - `+0.146716 dB`
- `guodegang_anchor_120s`：
  - `+0.370681 dB`
- `guodegang_absent_480s`：
  - `-0.077249 dB`

`probe_subset_guardrail_vs_v8_with_clips`：

- `FAIL`
- 唯一失败项：
  - `clip__guodegang_absent_480s`

解释：

- `v19` 已经把：
  - `overall`
  - `guodegang_raw`
  - `near_real_0006`
  - `guodegang_anchor_120s`
  都重新推到 `v8` 之上；
- 但它仍没有真正跨过：
  - `guodegang_absent_480s`

## 当前结论

1. `v18` 不保留。
2. `v19` 是当前第一条通过 synthetic dual-proxy gate 的 absent follow-up。
3. 但 `v19` 仍不应直接晋升为主候选：
   - broad near-real 相对 `v12` 仍小幅回退；
   - 失败点集中在：
     - `friend_raw`
     - `near_real_0003`
     - `near_real_0004`
4. `v19` 的价值在于：
   - 它把问题进一步压缩成：
     - `0006` 方向已基本保住并继续改善
     - `guodegang` 总体也重新超过 `v8`
     - 但 `absent_480s` 仍略低于 `v8`
     - 同时 broad friend-side 又出现了回吐

## 对下一步的影响

1. 当前不要再回到：
   - `v16 / v17 / v18` 这种 synthetic 未过线版本。
2. 若继续自动推进，默认应以 `v19` 作为新的 objective 基座，而不是再回到 `v12` 重新扫旧 absent 路线。
3. 但下一步不应继续做盲目的权重扫描；应先围绕 `v19` 明确回答：
   - 为什么：
     - `friend_raw / 0003 / 0004`
     会在 synthetic 过线后仍继续回退
4. 更具体地说，下一步更像应该补：
   - `v19 vs v12` 的 friend-side reverse guardrail / selector carve-out
   - 或新的 branch-local synthetic proxy
   而不是继续只围绕 `0006 absent` 单边加力。
