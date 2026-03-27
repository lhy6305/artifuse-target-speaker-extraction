# `v81` vs `v106` listening review

## blind 包

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106_blind`

映射：

- `candidate_a = v81`
- `candidate_b = v106`

## 结果

- `better_output`
  - `v81 = 0`
  - `v106 = 0`
  - `tie = 4`

逐样本：

- `near_real_0003`
  - `tie`
  - 理由：无可感知差异
- `near_real_0006`
  - `tie`
  - 理由：无可感知差异
- `near_real_0007`
  - `tie`
  - 理由：无可感知差异，核心痛点未出现主观改善
- `near_real_0009`
  - `tie`
  - 理由：无可感知差异

## 听审口径补充

这次补充固定一条主观口径：

- 不同批次听审之间，可比性不高；
- 同一条样本，上一批可能主观记为“中等泄漏”，下一批也可能主观记为“明显泄漏”；
- 因此主观感受默认只对同批次 A/B 负责；
- 不能把不同批次的 artifact / leak 严重度标签直接串成统一量尺。

也就是说，这次 `tie = 4` 的有效含义是：

- 在这一次 `v81 vs v106` 的同批次 A/B 内，
  `v106` 没有形成可感知优势；
- 但它不等价于：
  `v106` 在绝对意义上“完全没有泄漏”或“绝对和历史某一批次同等级”。

## 与 automatic 的关系

automatic 上，`v106` 仍成立：

- synthetic 上是 `artifact-first` 家族里的中间解；
- overlap-local `0007` 已不再出现比 `v81` 更重的 artifact；
- whole-utterance `0007` target capture 还优于 `v81`。

但这次 blind 听审说明：

- 这些改动还没有转化成可感知收益；
- `artifact` 侧止血，不等于主观层面已经解决核心痛点；
- `local artifact veto` 只做 teacher-overlap 对齐，仍不足以把 `0007` 风格局部 speech leak 真正打穿。

## 当前裁决

1. `v106` 不升格。
2. `v106+` 同结构小步 sweep 不继续。
3. `local_artifact_veto` 这条线当前正式结论是：
   - 自动层面从“明显更差”收回到了“中间解”
   - 但听审层面仍未转正
4. 下一步如果还要继续 `0007` 子题，默认应改做：
   - 显式 `music_plus_speech` local speech-leak backstop
   - 而不是继续只靠 teacher-overlap 对齐
