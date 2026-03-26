# 2026-03-26 `v81 vs v82` listening review

## 解盲结果

听审包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v82_blind`

解盲结果：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v82_blind/listening_review_decoded_summary.json`

真实标签：

- `file_a = v81`
- `file_b = v82`

总体结果：

- `4 / 4 tie`
- 无任何可感知差异

## 样本级结论

### `near_real_0003`

结果：

- `tie`

备注：

- target present with domain-matched friend speech
- 当前前沿候选仍有 `moderate leakage`

解盲后：

- `v81`
  - `source_retention = good`
  - `interference_leak = moderate`
- `v82`
  - `source_retention = good`

结论：

- `v82` 虽然 objective 更强，但没有形成可听改善。

### `near_real_0006`

结果：

- `tie`

备注：

- external guodegang overlap
- 当前前沿候选仍有 `heavy leakage`

解盲后：

- `v81`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `artifact = none`
- `v82`
  - `source_retention = good`
  - `interference_leak = moderate`
  - `artifact = none`

结论：

- `v82` 没有把这条主问题推进到可听层。

### `near_real_0007`

结果：

- `tie`

备注：

- hard target-present friend-speech plus music
- 当前前沿候选仍有 `moderate leakage` 和 `moderate artifact`

解盲后：

- `v81`
  - `source_retention = excellent`
  - `interference_leak = moderate`
  - `volume_fluctuation = slight`
  - `artifact = moderate`
- `v82`
  - `source_retention = excellent`
  - `interference_leak = moderate`
  - `volume_fluctuation = slight`
  - `artifact = moderate`

结论：

- near-real guardrail 对 `v82` 的黄灯没有转成可听上更差；
- 但也没有形成任何可听收益。

### `near_real_0009`

结果：

- `tie`

备注：

- target absent with external speech only
- 当前前沿候选仍有 `moderate leakage`

解盲后：

- `v81`
  - `interference_leak = moderate`
- `v82`
  - `interference_leak = moderate`

结论：

- `v82` 的 absent 方向微弱 objective 改善同样没有转成可听收益。

## 对 `v82` 的裁决

1. `v82` 不能升格为新研究基座。
   - 它没有被听审判成更好。
2. `v82` 也没有被听审判成明显更差。
   - 这与 near-real objective 的 `0007` 黄灯并不矛盾；
   - 更准确地说，那个黄灯目前还停留在指标层，没有转成可听差异。
3. `v81 vs v82` 这道选型题可以收口。
   - 当前 objective 改善已经不足以形成主观收益；
   - 继续沿 `overlap residual purify v1` 同结构扫 `v83 / v84` 的收益预期很低。

## 当前阶段结论

这轮听审把一个关键事实钉死了：

- 当前问题已经不是“有没有更好的轻量 tradeoff 调法”；
- 而是现有 `v81 / v82` 这一代方法，对 residual speech leak 的改善幅度仍小于人耳可感知阈值。

也就是说：

- `v82` 证明机制方向并非错误；
- 但它还不足以构成下一轮同结构权重扩展的理由。

## 下一步

默认下一步不再是：

- `v83` 同结构 sweep
- 或 `v81 / v82` 再做更多 frontier 听审

而应改成新的机制层题目：

- 更强的 `present_overlap_residual_leak_purification v2`

方向应是：

- 不再只改一个 branch mask head 的局部投影约束；
- 而是考虑显式 residual canceller / overlap-only refinement 支路；
- 目标是把 `0003 / 0006 / 0009` 的 moderate / heavy leak 压到真正可听下降的幅度。
