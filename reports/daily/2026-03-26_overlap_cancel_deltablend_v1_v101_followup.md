# 2026-03-26 overlap cancel delta blend v1 and `v101` follow-up

## 本轮目标

- 不再继续沿 `v95 / v100` 的 `auxiliary_only` 家族做小步修正；
- 回到真正会改 final output 的 subtractive canceller 家族；
- 验证问题是否出在：
  - overlap cancel 的最终输出路径过于激进，
  - 而不是单纯 loss 不够。

## 新机制

新增模型接线：

- `branch_overlap_cancel_delta_blend_mode`
- `branch_overlap_cancel_max_blend`

接线文件：

- `src/tse_prefix/models/stft_mask_baseline.py`
- `scripts/train/train_stft_mask_baseline.py`

含义：

- overlap canceller 仍先预测 residual cancel estimate；
- 但在 `subtract` 路径上，不再直接全量减掉；
- 改成：
  - `estimated = branch_base - delta_blend * cancel_estimate`
- 本轮 active 配置：
  - `branch_overlap_cancel_gate_mode = complement`
  - `branch_overlap_cancel_delta_blend_mode = complement`

解释：

- `v88` 原来已经用 `complement` 去缩放 cancel ratio；
- `v101` 再在最终输出 delta 上补一层 `complement` blend；
- 结果上等价于：
  - hard-present 帧进一步缩小实际改变量，
  - weak-target 帧保留更多 suppress 动作。

## `v101`

Checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v101_v88_overlap_cancel_deltablend_v1_ft1`

初始化：

- `v88`

trainable：

- `branch_overlap_cancel_head`

训练设置：

- 其余 focused selector / loss 复用 `v88`
- 不引入 teacher
- 不改 branch mask / gate

## 自动结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `+2.4355 dB`
  - `8 improve / 0 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+1.0637 dB`
  - `8 improve / 0 regress / 3 near tie`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.2377 dB`
  - `14 improve / 0 regress / 2 near tie`

结论：

- `v101` 相对 `v81` 仍是全量 synthetic 正收益。

### relative `v88`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `-2.1785 dB`
  - `0 improve / 8 regress`
- `same_gender_present_keep_guardrail_v1`
  - `-1.1053 dB`
  - `0 improve / 10 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `-1.0642 dB`
  - `0 improve / 15 regress`

结论：

- `v101` 不是新自动前沿；
- 它是一个明确的“把 `v88` 往安全侧拉回”的中间解。

## near-real objective

### `v81 vs v101`

非盲包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v101`

tradeoff 结果：

- `better_source_retention`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky`
  - `v81 = 3`
  - `tie = 1`
- `better_retention_minus_leak`
  - `v101 = 2`
  - `tie = 1`
  - `not_applicable = 1`

gate 结果：

- `overall_pass = true`

bandwidth：

- `narrower_candidate_counts = tie: 4`

样本级解释：

- `0003`
  - 基本打平，`v101` 轻微更优
- `0006`
  - `v101` leak 更低，retention 近乎不变
- `0007`
  - objective 上仍比 `v81` 更强，但 target capture 已不再像 `v88` 那样明显更低
- `0009`
  - `v101` absent suppression 明显强于 `v81`

### `v88 vs v101`

非盲包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v88_vs_v101`

tradeoff 结果：

- `more_interference_leaky`
  - `v101 = 3`
  - `tie = 1`
- `better_retention-minus-leak`
  - `v88 = 2`
  - `tie = 1`
  - `not_applicable = 1`

解释：

- `v101` 确实把 `v88` 往安全侧拉回来了；
- 代价是：
  - `0006 / 0007 / 0009` 上 suppression 都弱于 `v88`
- 但它并没有退回 `v81`，而是落在：
  - `v81 < v101 < v88`
  的中间位置。

## 当前裁决

- `delta blend v1` 不是空改动；
- 它首次给 subtractive canceller 家族提供了一个：
  - 比 `v88` 更保守
  - 比 `v81` 更强
  的中间解；
- 因此 `v101` 值得进入 focused 听审。

## Focused pack

blind 包已导出：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v101_blind`

并已补齐：

- `asset_audit_summary.json`
- `tradeoff_analysis/summary.json`
- `tradeoff_analysis/decision_gate_summary.json`
- `bandwidth_analysis/summary.json`

## 下一步

直接做人耳终裁：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v101_blind
```

重点盯：

- `near_real_0007`
  - 相比 `v88`，这次 hard-present artifact / target-preservation 风险是否真的被压下来了
- `near_real_0006`
  - 相比 `v81`，更强 suppress 是否终于转化成可感知更干净
- `near_real_0009`
  - absent suppression 更强是否仍符合“宁可闭嘴”的主观偏好

## 听审解盲结果

对应解盲报告：

- `reports/daily/2026-03-26_v81_vs_v101_listening_review.md`

解盲结论：

- `tie = 3`
- `v81 = 1`
- `v101 = 0`

样本级：

- `near_real_0003`
  - `tie`
- `near_real_0006`
  - `tie`
- `near_real_0007`
  - `tie`
- `near_real_0009`
  - `v81 > v101`

解释：

- `v101` 的确把 `v88` 那种 hard-present 风险拉回来了；
- 但它没有把 objective 上更强的 suppress 转化成新的可听收益；
- 唯一分出胜负的 `near_real_0009` 仍然是 `v81` 更好。

## 最终裁决

- `v101` 不升格。
- `v81` 继续保留为当前研究基座。
- `overlap cancel delta blend v1` 这条分支先收口：
  - 它是有效的安全校准机制，
  - 但不是新的可听前沿。
