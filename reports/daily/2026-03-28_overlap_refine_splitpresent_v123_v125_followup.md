# 2026-03-28 overlap-refine split-present `v123 / v124 / v125` follow-up

## Summary

- 基线继续沿：
  - `v122 = v120 + soft present gate power 2.0`
- 本轮连续补了三步：
  - `v123 = v122 + hardlocal speech_only selector/bundle v1`
  - `v124 = v122 + soft present gate power 3.0`
  - `v125 = v122 + soft present gate power 2.5`
- 裁决：
  - `v123 = reject`
  - `v124 = reject`
  - `v125 = keep as best automatic continuation, but focused listening tie and no promotion`

## `v123` relative `v122`

- synthetic 四条固定验收仍全绿：
  - abstention `+0.2959 dB`
  - same-gender keep `+0.2670 dB`
  - hard-present keep `+0.2258 dB`
  - artifact proxy `+0.2127 dB`
- whole near-real：
  - `tradeoff gate = pass`
  - 但 4 条样本都只落在 `tie`
- overlap-local：
  - `near_real_0007`
    - `delta_speech_interference_capture_db = +1.3089 dB`
    - `delta_retention_minus_speech_leak_db = -1.4342 dB`
  - `near_real_0009`
    - `delta_speech_interference_capture_db = +1.8143 dB`

结论：

- hardlocal `speech_only` 子域继续把优化拉向：
  - whole-tradeoff
  - total leak
- 不是当前 `0007 / 0009` blocker 的正确方向。

## `v124` relative `v122`

- 只改单变量：
  - `branch_overlap_refine_present_gate_power = 3.0`
- synthetic 已出现明确回退：
  - abstention `-0.1189 dB`
  - same-gender keep `+0.0098 dB`
  - hard-present keep `-0.0468 dB`
  - artifact proxy `+0.0466 dB`

结论：

- `3.0` 已经太硬；
- activation shaping 轴不能继续往 `3.0+` 扫；
- 直接废弃，不补 near-real。

## `v125` relative `v122`

- 只改单变量：
  - `branch_overlap_refine_present_gate_power = 2.5`
- synthetic 四条固定验收小幅全绿：
  - abstention `+0.0600 dB`
  - same-gender keep `+0.1311 dB`
  - hard-present keep `+0.0751 dB`
  - artifact proxy `+0.1221 dB`
- whole near-real：
  - `tradeoff gate = pass`
  - `more_interference_leaky = tie:3, v122:1`
  - `near_real_0007`
    - `delta_target_capture_db = -0.0637 dB`
    - `delta_interference_capture_db = -0.7946 dB`
    - `delta_retention_minus_leak_db = +0.7309 dB`
- overlap-local：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = -2.9284 dB`
  - `near_real_0007`
    - `delta_speech_interference_capture_db = -0.4983 dB`
    - `delta_total_interference_capture_db = -0.5610 dB`
    - `delta_retention_minus_speech_leak_db = +0.4330 dB`
    - `delta_retention_minus_total_leak_db = +0.4957 dB`
  - 自动阈值上这四个量仍大多落在 `tie`
    但方向已首次同时对 `0007 / 0009` 为正

结论：

- `v125` 是当前 split local-control semantics
  relative `v122` 的首个真实前进点：
  - `0009` absent local suppression 明显改善
  - `0007` local `speech_only / total leak` 也继续往前
- 但这些 automatic 增量最终没有转成可听优势；
- `v125` 只保留为该轴当前最好的自动 continuation，
  不升格为 listening winner。

## Listening Pack

- blind pack：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v122_vs_v125_blind`
- 导包结果：
  - `num_candidate_samples = 4`
  - `num_exported_samples = 4`
- 样本：
  - `near_real_0003`
  - `near_real_0006`
  - `near_real_0007`
  - `near_real_0009`

## Listening Review

- `v122 vs v125` focused 听审已完成：
  - `tie = 4`
  - `v122 = 0`
  - `v125 = 0`
- 结论：
  - 核心痛点仍未解决；
  - 没有形成“已经开始主观变好”的趋势；
  - automatic 上的正向 drift 仍低于当前人耳阈值。
- 样本备注：
  - pack 第 1 条即 `near_real_0003`
    留下备注：
    - `B样本有误差级别的伪影高于A。`

## Next

1. 收口：
   - `v123 / v124 / v125`
   - soft `gate_power` 轴 `2.0 / 2.5 / 3.0`
2. 不再继续扫：
   - `hardlocal selector`
   - `gate_power >= 3.0`
   - 或 `2.0 < gate_power < 3.0` 的同构小步 sweep
3. 下一轮直接回到机制层考虑：
   - 更软的 present-head veto
   - 或只针对 `0007 speech_only` 的新局部目标
