# 2026-03-26 `silence-over-leak frontier v1` GUI 听审解盲

## 对象

- pack：
  - `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind`
- manifest：
  - `data/references/real_eval_manifest_silence_over_leak_frontier_v1.jsonl`
- 候选：
  - `v32`
  - `v49_adaptermask`
  - `v54_dualdecoder_exactguard`
  - `v59_dualdecoder_basedeltaproj_w005`

## GUI 导出

- `listening_results_summary.json`
  - `num_samples = 6`
  - `num_scored = 6`
  - `better_output_counts`
    - `tie = 6`
    - 其余候选全为 `0`
- `listening_sheet.csv`
  - 6 条样本全部填写为 `tie`

解盲输出：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind/listening_review_decoded_summary.json`

真实结果：

- `decoded_better_output_counts`
  - `tie = 6`

## 样本级结论

全部 6 条样本都没有形成可感知差异：

- `near_real_0003`
  - `v54 / v32 / v49 / v59 = tie`
- `near_real_0006`
  - `v49 / v54 / v59 / v32 = tie`
- `near_real_0007`
  - `v49 / v54 / v59 / v32 = tie`
- `near_real_0008`
  - `v49 / v59 / v32 / v54 = tie`
- `near_real_0009`
  - `v32 / v49 / v54 / v59 = tie`
- `near_real_0010`
  - `v54 / v32 / v49 / v59 = tie`

也就是说：

- 这轮 frontier pack
  没有出现：
  - 更少漏但可听更好
  - 或更静音但明显更差
  的候选；
- 当前四个前沿候选在这 6 条边界样本上，
  主观上全部等价。

## 与 objective 的关系

同一包的 objective 摘要：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind/silence_over_leak_objective_summary.json`

objective 仍给出排序：

- absent rank：
  - `v54 > v59 > v49 > v32`
- present rank：
  - `v54 > v59 > v49 > v32`

但这轮人耳结果说明：

- 这些 objective 差异
  在当前 frontier 小包上
  没有转化成可感知差异；
- 因此 objective 现在可以用于：
  - 批量淘汰明显掉队候选
  但还不能用于：
  - 在 perceptual tie 的 frontier 里
    直接指定新研究基座。

## 裁决

1. `v49 / v54 / v59`
   目前都不能因为 objective 更优
   就替代 `v32`
2. `v32`
   也没有在这轮 frontier 复核里
   被新的 challenger 明确击败
3. 当前最准确的结论不是：
   - “找到新赢家”
   而是：
   - `v32 / v49 / v54 / v59`
     在这 6 条 `silence-over-leak` 边界样本上
     形成主观并列前沿
4. 因此当前不切研究基座，
   也不基于这轮结果启动训练

## 下一步建议

若继续推进，
优先级应为：

1. 先停在“objective 可大筛，人耳只听极小 frontier 包”的工作流；
2. 不再继续围绕这四条线开新训练；
3. 只有在能补到新的、
   比当前 6 条更能拉开差异的
   `weak-target / silence-over-leak`
   near-real 样本时，
   才值得再做下一轮 frontier 听审。

如果拿不到更有信息量的新样本，
则这条子题当前可以视为：

- 已完成有效排雷；
- 但尚未发现可听上足以替换现基座的新分支。
