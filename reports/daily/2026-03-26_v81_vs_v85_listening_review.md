# 2026-03-26 `v81 vs v85` listening review

## 解盲结果

听审包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind`

解盲结果：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind/listening_review_decoded_summary.json`

真实标签：

- `file_a = v81`
- `file_b = v85`

总体结果：

- `3 / 4 tie`
- `1 / 4 = v81`
- `v85 = 0`

也就是：

- `v85` 虽然自动分析最强；
- 但本轮没有形成任何可听胜场；
- 反而在 `near_real_0009` 上被人耳明确判为不如 `v81`。

## 样本级结论

### `near_real_0003`

结果：

- `tie`

备注：

- target present with domain-matched friend speech
- 当前两侧仍是 `moderate leakage`

解盲后：

- `v81`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `artifact = slight`
- `v85`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `artifact = slight`

自动先验：

- tradeoff：
  - `better_retention_minus_leak = tie`
- bandwidth：
  - `tie`

结论：

- `v85` 在这条 medium-present same-gender case 上没有可听改善。

### `near_real_0006`

结果：

- `tie`

备注：

- external guodegang overlap
- 当前两侧仍是 `heavy leakage`

解盲后：

- `v81`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `volume_fluctuation = slight`
  - `artifact = none`
- `v85`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `volume_fluctuation = slight`
  - `artifact = none`

自动先验：

- tradeoff：
  - `more_interference_leaky = v81`
  - `better_retention_minus_leak = v85`
  - `delta_interference_capture_db_b_minus_a = -5.254 dB`
- bandwidth：
  - `tie`

结论：

- 自动指标认为 `v85` 更干净；
- 但这部分收益仍未推进到人耳可感知层。

### `near_real_0007`

结果：

- `tie`

备注：

- hard target-present friend-speech plus music
- 当前两侧仍有 `moderate leakage` 和 `moderate artifact`

解盲后：

- `v81`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `artifact = moderate`
- `v85`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `artifact = moderate`

自动先验：

- tradeoff：
  - `more_interference_leaky = v81`
  - `better_retention_minus_leak = v85`
  - `delta_retention_minus_leak_db_b_minus_a = +1.826 dB`
- bandwidth：
  - `tie`

结论：

- `v85` 至少没有把 `0007` 听感显著压坏；
- 但也没有形成可听优势。

### `near_real_0009`

结果：

- `v81`

备注：

- target absent with external speech only
- 决策标签：
  - `less_interference_leak`

解盲后：

- `v81`
  - `interference_leak = moderate`
- `v85`
  - `interference_leak = moderate`

自动先验：

- tradeoff：
  - `more_interference_leaky = v81`
  - `delta_interference_capture_db_b_minus_a = -11.124 dB`
- bandwidth：
  - `tie`

关键观察：

- 自动分析强烈支持 `v85` 更安静；
- 但人耳在这条最接近 absent / silence-over-leak 的样本上，反而明确更偏向 `v81`。

结论：

- 当前 objective / near-real 指标对 `0009` 的偏好，和真实听感发生了反向分歧；
- 这说明：
  - `v85` 的 suppression 可能已经进入“数值更低，但主观未必更好”的区域；
  - 也可能存在当前 tradeoff 指标尚未刻画到的听感差异。

## 本轮裁决

1. `v85` 不能升格。
   - 它没有任何可听胜场；
   - 反而在 `near_real_0009` 上输给 `v81`。

2. `v81` 仍是当前最健康、最稳妥的研究基座。
   - `v85` 证明 `gate-complement` 是有效自动方向；
   - 但这次听审说明，它还没有形成可靠的人耳收益。

3. overlap refiner 这条线当前应停在这里，不能继续自动推进。
   - `v83`
     - 客观强但不安全
   - `v84`
     - 更受控但仍不过线
   - `v85`
     - 自动上最健康，但主观仍未转正

## 阶段结论

本轮最重要的结论不是“`v85` 完全无价值”，而是：

- overlap refiner 已经把自动指标推到了新的前沿；
- 但当前前沿仍没有转化成可听层收益；
- 特别是在 `0009` 这类 absent 样本上，自动更优甚至可能与人耳偏好相反。

因此当前项目状态应回到：

- 默认研究基座：
  - `v81`
- `v85`
  - 保留为已验证过的自动前沿候选
  - 但不继续自动扩树
  - 不升格为新基座
