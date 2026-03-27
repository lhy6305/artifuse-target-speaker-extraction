# `v81` vs `v103` listening review

## blind 包

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v103_blind`

映射：

- `candidate_a = v81`
- `candidate_b = v103`

## 结果

- `better_output`
  - `v81 = 4`
  - `v103 = 0`
  - `tie = 0`

逐样本：

- `near_real_0003`
  - `v81`
  - 理由：`less_artifact`
- `near_real_0006`
  - `v81`
  - 理由：`less_artifact`
- `near_real_0007`
  - `v81`
  - 理由：`less_artifact`
- `near_real_0009`
  - `v81`
  - 理由：`less_artifact`

主观打分共同点：

- `file_a_artifact = slight`
- `file_b_artifact = moderate`

因此这次听审的关键结论不是“`0007` 仍没修好”而已，而是：

- `v103` 四条样本都出现更明显伪影；
- 包括：
  - target-present speech
  - target-present speech+music
  - target-absent speech
  都没有逃掉。

## 与 automatic 的关系

automatic 上，`v103` 仍成立：

- synthetic 三条主验收继续更强；
- near-real whole-utterance `overall_pass = true`；
- overlap-local `0003 / 0006` 的 `retention-minus-speech-leak` 仍更优。

但这次 blind 听审证明：

- 这些 objective 仍不能覆盖真正会被人耳直接否掉的 artifact 退化；
- whole-utterance / localized leak 指标转正，不代表主观就会更好。

## 当前裁决

1. `v103` 不升格。
2. `speech_only overlap residual + plus_music teacher veto` 家族先收口。
3. 默认下一步不是 `v103+` sweep，而是改做新的 artifact-first 子题：
   - 物化能复现 `0007` 风格伪影的 synthetic proxy
   - 为后续训练补显式 artifact-aware backstop
