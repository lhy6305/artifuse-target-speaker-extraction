# `v81` vs `v107` listening review

## blind 包

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107_blind`

映射：

- `candidate_a = v81`
- `candidate_b = v107`

## 结果

- `better_output`
  - `v81 = 4`
  - `v107 = 0`
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

- `file_a_artifact`
  - 四条都是 `slight`
- `file_b_artifact`
  - `near_real_0003 = slight`
  - `near_real_0006 = slight`
  - `near_real_0007 = moderate`
  - `near_real_0009 = slight`

解释：

- 本轮不是“局部有分歧但总体接近”；
- 而是同一侧在四条样本上都被稳定判为 artifact 更重；
- `near_real_0007` 只是其中最明显的一条，不是唯一问题。

## 与 automatic 的关系

automatic 上，`v107` 仍成立：

- synthetic 三条固定验收 relative `v81` 全部更强；
- near-real whole-utterance `overall_pass = true`；
- overlap-local `0003 / 0006` 的 `retention-minus-speech-leak` 也确实更优。

但这次 blind 听审说明：

- 显式 local speech-leak supervision 本身是有效的；
- 可它当前换来的不是可听层净收益，
  而是另一侧更明显的 artifact；
- 也就是说，这轮 blocker 已经从：
  - “loss 没有显式打到 speech leak”
  
  进一步收窄成：
  - “在 `music_plus_speech` hard-present 局部窗里，如何压 speech leak 的同时不引入可听 artifact”

## 当前裁决

1. `v107` 不升格。
2. `v107+` 同结构小步权重 sweep 不继续。
3. `local explicit speech-leak backstop` 这条线当前正式结论是：
   - automatic 已证明监督语义成立；
   - 但听审层面仍然一边倒输在 artifact。
4. 下一步如果继续 `0007` 子题，默认应改做：
   - 保留显式 local speech-leak proxy；
   - 再额外加入 `music_plus_speech` hard-present 局部 preservation / artifact backstop；
   - 而不是继续在当前同构设置上轻量调权重。
