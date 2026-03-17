# 初始设计评审记录

## 状态

当前为占位文档，后续用于记录对 `initial_design.md` 的评审结论、保留意见和阶段性修订建议。

## 首轮评审摘要

- 任务定义已经明确收敛到 Target Speaker Extraction，而不是泛人声分离。
- 工程边界已经明确为独立前置模块，这一点合理且有利于控制复杂度。
- 数据路线可先从合成数据启动，符合当前已有数据条件。
- 当前最需要补的不是模型讨论，而是：
  - 正式目录结构；
  - 数据桶 manifest；
  - target/reference 拆分规则；
  - baseline 验证闭环。

## 待补充评审点

- baseline 选型标准；
- synthetic mixture 元数据字段最终格式；
- `TSE -> VC` 链路的首版验收样本集；
- ambient noise 数据来源补充方案。
