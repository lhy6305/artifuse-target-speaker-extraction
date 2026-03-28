# 2026-03-28 true-absent decoupled routing `v128 / v129 / v130` follow-up

## Summary

- `v127` 已经证明：
  - true absent supervision 本体有效；
  - 但直接灌进 `present-head-only` routing 会把 whole tradeoff 拖坏。
- 这轮改成只训练 `branch_overlap_refine_head`，先验证解耦 routing：
  - `v128 = v126 + true absent anchor bundle + absent_extra 0.02 + complement-head only routing`
- 在 `v128` 基础上做一档最小 reweight：
  - `v129 = v128 + absent_extra 0.01`
- 随后又补了一个最小机制改动：
  - 给 `branch_overlap_refine_head` 增加 `gate_power / gate_floor`
  - `v130 = v129 + complement-head gate_power 2.0`
- 裁决：
  - `v128 = mechanism-positive but not promotable`
  - `v129 = best continuation inside decoupled true-absent branch, but still not enough to replace v126`
  - `v130 = reject`
  - 当前总线仍保持：
    - `v126` 是全局最佳 split-local-control automatic continuation
    - `v129` 只保留为 true-absent decoupled-routing 的最佳证据点

## `v128` Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v128_v126_trueabsentanchor_complementhead_absentextra002_v1_ft1`
- 初始化：
  - `v126`
- teacher：
  - `v109`
- trainable：
  - `branch_overlap_refine_head`
- 训练资产：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
    - train `203`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
    - val `63`
- selector 命中：
  - `absent_extra = 95 / 203` train
  - `absent_extra = 24 / 63` val

## `v128` relative `v126`

- synthetic 四条固定验收重新全线转正：
  - abstention `+0.2733 dB`
  - same-gender keep `+0.1355 dB`
  - hard-present keep `+0.2477 dB`
  - artifact proxy `+0.1029 dB`
- 这说明：
  - 同样的 true absent supervision，
    改走 complement-head routing 后，
    不再像 `v127` 那样立刻打穿 guardrail。
- 但 whole near-real 仍不能保留：
  - `more_interference_leaky = v128:2, tie:2`
  - `better_retention_minus_leak = v126:1, tie:2, not_applicable:1`
  - `near_real_0007`
    - `delta_interference_capture_db = +8.5356 dB`
    - `delta_retention_minus_leak_db = -8.3363 dB`
  - `near_real_0009`
    - `delta_interference_capture_db = +1.5064 dB`
- overlap-local 只有部分对：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = -5.6247 dB`
  - `near_real_0006`
    - `delta_speech_interference_capture_db = -1.3851 dB`
  - `near_real_0007`
    - `delta_speech_interference_capture_db = -0.8117 dB`
    - `delta_total_interference_capture_db = +2.5239 dB`
- 结论：
  - `v128` 是 routing hypothesis 的正证据，
    但不是可升格 continuation。

## `v129` relative `v128`

- 只改一个变量：
  - `absent_extra_weight 0.02 -> 0.01`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v129_v128_trueabsentanchor_complementhead_absentextra001_v1_ft1`
- synthetic 四条固定验收继续微正：
  - abstention `+0.0424 dB`
  - same-gender keep `+0.0366 dB`
  - hard-present keep `+0.0541 dB`
  - artifact proxy `+0.0063 dB`
- whole near-real relative `v128`：
  - `more_interference_leaky = tie:3, v128:1`
  - `better_retention_minus_leak = tie:2, v129:1, not_applicable:1`
  - 关键变化都在 `near_real_0007`
    - `delta_target_capture_db = +0.0410 dB`
    - `delta_interference_capture_db = -6.2120 dB`
    - `delta_retention_minus_leak_db = +6.2530 dB`
  - 但 `near_real_0009`
    - `delta_interference_capture_db = +0.2374 dB`
    - absent whole 口径反而更漏
- overlap-local relative `v128`：
  - `near_real_0007`
    - `delta_speech_interference_capture_db = -2.4872 dB`
    - `delta_total_interference_capture_db = -1.0267 dB`
    - `delta_retention_minus_speech_leak_db = +2.5202 dB`
    - `delta_retention_minus_total_leak_db = +1.0597 dB`
  - `near_real_0009`
    - `delta_speech_interference_capture_db = +4.1453 dB`
    - 把 absent local suppression 明显吐回去
- 因而 relative `v126` 的真实位置是：
  - whole near-real：
    - `more_interference_leaky = v129:2, tie:2`
    - `better_retention_minus_leak = v126:1, tie:2, not_applicable:1`
    - `near_real_0007`
      - `delta_interference_capture_db = +2.3236 dB`
      - `delta_retention_minus_leak_db = -2.0833 dB`
    - `near_real_0009`
      - `delta_interference_capture_db = +1.7438 dB`
  - overlap-local：
    - `near_real_0007`
      - `delta_speech_interference_capture_db = -3.2989 dB`
      - `delta_total_interference_capture_db = +1.4972 dB`
    - `near_real_0009`
      - `delta_speech_interference_capture_db = -1.4794 dB`
- 结论：
  - `v129` 是 `v128` 的有效回稳版，
    也是 decoupled true-absent 支线当前最佳 continuation；
  - 但它仍没把 `0007 / 0009` 的 whole 口径翻过 `v126`，
    所以不能升格为主线最佳。

## `v130` Setup

- 这轮补了一个最小机制：
  - `branch_overlap_refine_head`
    新增：
    - `branch_overlap_refine_gate_power`
    - `branch_overlap_refine_gate_floor`
  - 目的是把 complement action 压到更强 absent 区域，
    减少对 present 样本的 spillover。
- 本轮定义：
  - `v130 = v129 + complement-head gate_power 2.0`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v130_v129_trueabsentanchor_complementhead_gatepower2_absentextra001_v1_ft1`

## `v130` relative `v129`

- synthetic 四条固定验收全线明显转负：
  - abstention `-0.3591 dB`
  - same-gender keep `-0.2566 dB`
  - hard-present keep `-0.3005 dB`
  - artifact proxy `-0.1715 dB`
- 因为四条固定验收已经同时失守，
  本轮不再补 near-real 导包。
- 含义很明确：
  - complement-head gate shaping 往 `power > 1`
    这个方向推，
    会直接重新伤到 present keep / artifact guardrail；
  - 这不是值得继续扫的参数轴。

## Conclusion

- `v128`：
  - 证明 true absent supervision 的问题不在 supervision 本体，
    而在 routing；
  - decoupled complement-head route 是真实机制方向。
- `v129`：
  - 证明 decoupled route 上的 absent weight 可以把
    `0007` 的 whole/local 漂移往回收；
  - 但它仍没有越过 `v126`，
    因为 `0009` absent whole 继续偏漏，
    `0007` whole 也仍没完全翻正。
- `v130`：
  - 证明 complement-head `gate_power` shaping
    不是下一条应继续的机制线。

## Next

1. 收口：
   - `v128 / v129 / v130`
2. 保留：
   - `v129` 作为 true-absent decoupled-routing 的最佳 continuation
3. 主线状态保持：
   - `v126` 仍是全局最佳 automatic continuation
4. 不再继续扫：
   - `absent_extra_weight`
   - `complement-head gate_power / gate_floor`
5. 下一轮若继续 true absent 方向，
   默认需要新的解耦机制：
   - 更显式的 controller-only / auxiliary-only path，
   - 或只在 absent-local window 生效而不会回灌到 present whole tradeoff 的局部 apply 机制。
