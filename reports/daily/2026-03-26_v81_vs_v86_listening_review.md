# 2026-03-26 `v81 vs v86` focused 听审解盲结论

## 听审包

- pack:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind`
- decode:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind/listening_review_decoded_summary.json`

## 真实结果

- 总计：
  - `tie = 3`
  - `v81 = 1`
  - `v86 = 0`
- 唯一分出胜负的样本：
  - `near_real_0009 = v81 > v86`
- 其余三条：
  - `near_real_0003 = tie`
  - `near_real_0006 = tie`
  - `near_real_0007 = tie`

## 与自动分析的关系

- 自动分析仍认为 `v86` 相对 `v81` 更少泄漏：
  - `more_interference_leaky`
    - `v81 = 3`
    - `tie = 1`
  - `better_retention_minus_leak`
    - `v86 = 2`
    - `tie = 1`
    - `not_applicable = 1`
- near-real rank 里：
  - `v86`
    - `present_guardrail_violation_count = 0`
    - absent suppression 介于 `v81` 和 `v85` 之间
- 但这些收益没有稳定转成可听优势；
  - `0003 / 0006 / 0007` 全部主观打平
  - `0009` 反而是 `v81` 被明确听成更好

## 主观结论

- `v86` 不升格。
- `v81` 继续保留为当前最稳妥的研究基座。
- `residual-source gate-complement refiner` 这条线说明：
  - 自动指标和 guardrail 可以继续变好；
  - 但当前改动幅度仍不足以解决人耳层面的核心痛点。

## 当前阶段裁决

- `v81 vs v85`
  - `v85` 未转正
- `v81 vs v86`
  - `v86` 也未转正

因此：

- `overlap refiner` 这条当前家族已经把 objective / guardrail 潜力基本探出来了；
- 但 `present overlap residual leak` 的核心痛点仍未被推进到可听层。

## 结论后默认动作

- 不再把 `v85 / v86` 这一类同家族 refiner 变体当作默认升格候选。
- 若后续继续推进，默认不应再做 `v87+` 小步 sweep；
  而应切换到新的机制题，而不是继续在当前 refiner 家族里微调。
