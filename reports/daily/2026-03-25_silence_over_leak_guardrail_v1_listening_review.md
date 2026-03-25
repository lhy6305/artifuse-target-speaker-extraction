# 2026-03-25 Silence-Over-Leak Guardrail v1 Listening Review

## 背景

本轮听审包为：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_guardrail_v1_stage2_v32_v8_v13_blind`

候选为：

- `legacy_stage2`
- `v32`
- `v8_absentguard`
- `v13_absentguard`

目标不是找“平均最强”的模型，而是专门看新标准：

- 当目标弱到几乎不可辨，谁更接近 `闭嘴而不吐干扰`
- 同时不能在 `target-present` 挡板样本上把可用目标一起压坏

## 解盲结果

GUI 表面计数：

- `tie = 4`

解盲后真实结论仍是：

- `tie = 4`

对应解盲摘要：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_guardrail_v1_stage2_v32_v8_v13_blind/listening_review_decoded_summary.json`

## 样本级结论

### 1. `near_real_0006`

- 这是 target-present 挡板样本
- 四个候选都被判为 `tie`
- 体感上没有谁为了“闭嘴”而把这条 target-present 样本压坏

当前含义：

- `v8 / v13` 这类 absent-guard 候选至少没有在这条回归挡板上立刻暴露出新的明显副作用

### 2. `near_real_0008`

- target absent / friend speech only
- 四个候选都被判为 `tie`
- `interference_leak` 全是 `none`

当前含义：

- 在这条最简单的 absent-only 场景里，四个候选主观上已经拉不开

### 3. `near_real_0009`

- target absent / external speech only
- 表面仍记为 `tie`
- 但备注明确写了：
  - `只有候选4明显不行，其他3个打平`

解盲后：

- `candidate_4 = legacy_stage2`
- 其余三个分别是：
  - `v32`
  - `v8_absentguard`
  - `v13_absentguard`

当前含义很关键：

- 在这条最贴近新子题定义的 `external speech only` 样本上，
  `legacy_stage2` 是唯一被明确点名为“显著泄漏”的候选；
- `v32 / v8 / v13` 三条线在这条样本上主观上打成一组前沿；
- 这不是“找到唯一新赢家”，而是“把 `legacy_stage2` 从这条窄题的前沿里剔除了”。

### 4. `near_real_0010`

- target absent / friend speech + music
- 四个候选都被判为 `tie`
- 备注为：
  - `4条都完美静音`

当前含义：

- 在这条更容易靠静音过关的 absent 样本上，四个候选都已经到达主观上不可区分的水平

## 当前裁决

当前不能得出的结论：

1. 不能说 `v8` 已经明显强于 `v32`
2. 不能说 `v13` 已经明显强于 `v32`
3. 不能说现在就该把研究基座从 `v32` 切回旧 absent-guard 分支

当前可以确定的结论是：

1. 在 `silence-over-leak` 这个更窄的新子题上，`legacy_stage2` 已经不是最稳的前沿候选。
2. 真正留在前沿上的，是：
   - `v32`
   - `v8_absentguard`
   - `v13_absentguard`
3. 但这三条线目前主观上仍未分出明确赢家。

## 方案判断

因此，这轮之后最合理的状态不是“直接升格 `v8` 或 `v13`”，而是：

- 默认主线仍继续保持 `legacy_stage2`
  - 因为整个大盘主线还没有被这 4 条窄题样本推翻
- `v32` 继续保留为研究基座
  - 因为它已经有完整 focused 资产链，而且这轮没有输给 `v8 / v13`
- `v8 / v13` 升格为这条新子题的并列历史锚点
  - 后续若继续推进，应把它们作为额外对照，而不是再只拿 `legacy` 和 `v32` 二选一

## 下一步建议

如果继续推进这条子题，不建议马上训练。

更合理的下一步是先补一轮更强的区分性资产：

1. 扩充 `external speech only / weak target audibility` 的 near-real 小包
   - 当前只有 `near_real_0009` 一条真正拉开了差异
2. 新包里继续保留：
   - `legacy_stage2`
   - `v32`
   - `v8_absentguard`
   - `v13_absentguard`
3. 只有当 `v32 / v8 / v13` 之间也能稳定拉开，才有意义讨论：
   - 研究基座是否切换
   - 是否值得开 focused follow-up 训练

大白话总结：

- 这轮没有找到“新王”
- 但已经确认：
  - `legacy_stage2` 在 `near_real_0009` 这类新子题核心样本上，是唯一明显掉队的那个
  - `v32 / v8 / v13` 三条线目前是并列前沿
