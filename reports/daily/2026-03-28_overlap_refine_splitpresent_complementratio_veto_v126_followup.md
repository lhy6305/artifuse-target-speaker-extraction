# 2026-03-28 overlap-refine split-present complement-ratio veto `v126` follow-up

## Summary

- 基线继续沿：
  - `v125 = v122 + soft present gate power 2.5`
- 本轮只改一个机制变量：
  - `v126 = v125 + present-head complement-ratio veto 0.5`
- 目的不是继续扫 `gate_power`，
  而是验证：
  - split 的 complement head
    能否直接对 present head 形成 `target-absent / weak-target` veto，
    从而少走一轮纯 gate 形状微调。
- 裁决：
  - `v126 = keep as new best automatic continuation`
  - 但仍不是 listening candidate

## Mechanism

- 代码落点：
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `scripts/train/train_stft_mask_baseline.py`
- 新增模型开关：
  - `branch_overlap_refine_present_veto_mode`
  - `branch_overlap_refine_present_veto_strength`
  - `branch_overlap_refine_present_veto_power`
- 本轮实际配置：
  - `branch_overlap_refine_present_veto_mode = complement_ratio`
  - `branch_overlap_refine_present_veto_strength = 0.5`
  - `branch_overlap_refine_present_veto_power = 1.0`
- 实现语义：
  - 用 frozen complement refine head 的当前活动强度，
    去衰减 present refine head 的有效 gate；
  - 也就是让：
    - `weak-target / target-absent suppress` 语义
    对
    - `present-head extra suppress`
    形成直接 veto。

## Data Constraint

- 本轮还顺手确认了一件关键事实：
  - `train / val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1`
    里没有真正的 absent 样本；
  - 因此在这套 `0007_like` 训练资产上，
    直接靠 `absent / absent_extra` loss
    去验证 `target-absent veto`
    实际上是空转。
- 这也是为什么本轮优先落：
  - model-side complement-ratio veto
  而不是再做一轮 loss-side absent selector。

## `v126` relative `v125`

- synthetic 四条固定验收全部小幅正向：
  - abstention `+0.0235 dB`
  - same-gender keep `+0.0336 dB`
  - hard-present keep `+0.0146 dB`
  - artifact proxy `+0.0298 dB`
- whole near-real：
  - `more_interference_leaky = tie:3, v125:1`
  - `better_retention_minus_leak = tie:2, v126:1, not_applicable:1`
  - 关键增量集中在：
    - `near_real_0007`
      - `delta_target_capture_db = -0.0463 dB`
      - `delta_interference_capture_db = -1.4286 dB`
      - `delta_retention_minus_leak_db = +1.3823 dB`
  - 其余样本：
    - `near_real_0003`
      - `delta_retention_minus_leak_db = -0.0612 dB`
    - `near_real_0006`
      - `delta_retention_minus_leak_db = -0.0537 dB`
    - `near_real_0009`
      - `delta_interference_capture_db = -0.1196 dB`
  - 说明 whole-utterance 上，
    `v126` 的真实收益几乎全部来自：
    - `0007`
    的 interference / total-leak 回拉。
- overlap-local：
  - 总体计数：
    - `more_speech_interference_leaky = tie:4`
    - `more_total_interference_leaky = tie:3, v125:1`
    - `better_retention_minus_speech_leak = tie:3, not_applicable:1`
    - `better_retention_minus_total_leak = tie:3, not_applicable:1`
    - `more_artifact_proxy_heavy = tie:4`
  - `near_real_0007`
    - `delta_speech_interference_capture_db = +0.0284 dB`
    - `delta_total_interference_capture_db = -0.7020 dB`
    - `delta_retention_minus_speech_leak_db = -0.0782 dB`
    - `delta_retention_minus_total_leak_db = +0.6521 dB`
  - `near_real_0009`
    - `delta_speech_interference_capture_db = +0.1498 dB`
  - `near_real_0003 / 0006`
    - 都只有误差级微小摆动

## Conclusion

- complement-ratio veto 不是 no-op；
- 它相对 `v125` 的真实收益是：
  - 在不伤四条 synthetic 固定验收的前提下，
    再把 `0007` 的 whole / total-leak 往前推了一点。
- 但它没有做到两件更关键的事：
  - 没把 `0007 speech_only local leak`
    变成明确正向；
  - 也没把 `0009 absent local suppression`
    继续往前推。
- 因而本轮结论是：
  - `v126` 接替 `v125`
    成为 split local-control semantics 的当前最佳 automatic continuation；
  - 但还不到 listening candidate。

## Next

1. 收口：
   - `v126` 不再导 focused 听审
2. 不继续扫：
   - `gate_power`
   - `gate threshold / present_max_delta`
   - `present_veto_strength / power`
   这类同构微调
3. 下一轮若继续 split local-control semantics：
   - 要么补一套真正含 absent anchor 的训练资产；
   - 要么把 complement-ratio veto
     和新的 `0007 speech_only local leak` 机制
     结合起来，
     而不是再单独调 veto 数值。
