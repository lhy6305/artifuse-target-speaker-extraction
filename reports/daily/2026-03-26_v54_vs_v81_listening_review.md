# 2026-03-26 `v54 vs v81` listening review

## 结论

这轮 GUI 听审解盲后，真实结果是：

- `4 / 4 tie`
- 没有任何一条样本出现可感知优胜方

解盲文件：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v54_vs_v81_blind/listening_review_decoded_summary.json`

blind mapping：

- `file_a = v54`
- `file_b = v81`

## 样本级结论

### `near_real_0003`

- `tie`
- 备注：
  - target present with domain-matched friend speech
  - all current frontier candidates still have moderate leakage

主观评分：

- `v54`
  - source retention `good`
  - interference leak `heavy`
  - artifact `moderate`
- `v81`
  - source retention `good`
  - interference leak `heavy`
  - artifact `moderate`

### `near_real_0006`

- `tie`
- 备注：
  - target present with external guodegang speech
  - all current frontier candidates still have heavy leakage

主观评分：

- `v54`
  - source retention `good`
  - interference leak `moderate`
  - volume fluctuation `slight`
  - artifact `slight`
- `v81`
  - source retention `good`
  - interference leak `moderate`
  - volume fluctuation `slight`
  - artifact `slight`

### `near_real_0007`

- `tie`
- 备注：
  - hard target-present friend-speech plus music case
  - all current frontier candidates still show moderate leakage and moderate artifact

主观评分：

- `v54`
  - source retention `good`
  - interference leak `heavy`
  - artifact `moderate`
- `v81`
  - source retention `good`
  - interference leak `heavy`
  - artifact `moderate`

### `near_real_0009`

- `tie`
- 备注：
  - target absent with external speech only
  - all current frontier candidates still have moderate leakage

主观评分：

- `v54`
  - interference leak `moderate`
  - artifact `none`
- `v81`
  - interference leak `moderate`
  - artifact `none`

## 对 `v81` 的裁决

1. `v81` 不能升格为默认线。
   - 它相对 `v54` 没有形成任何可感知优势。
2. `v81` 也没有被听审判成明显更差。
   - 这说明上一轮 objective / guardrail 回拉不是伪信号；
   - 但它还没有把问题推进到可听层。
3. 当前 `v54 vs v81` 这道选型题可以先收口。
   - 继续在这两个 checkpoint 间做更多听审，预期收益很低。

## 当前真正未解的问题

当前主问题已经从：

- `gate` 该怎么校准 keep / abstain

转成：

- 即使校准更健康，重叠段的 residual speech leak 仍然太高；
- 也就是说，当前瓶颈已经不是 `silence calibration`；
- 而是 `overlap residual purification`。

## 下一步

默认下一步不再是继续比较 `v54 / v81`，而是：

1. 保留 `v81` 作为 gate 机制研究基座
2. 冻结 `v54 vs v81` 这道听审题
3. 单开新的机制子题：
   - `present_overlap_residual_leak_purification`
4. 优先尝试直接打 overlap residual leak，而不是继续微调 gate target 曲线
