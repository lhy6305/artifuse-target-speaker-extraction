# 项目总览与阶段计划

## 文档定位

- 本文档只保留活跃摘要，不再承载长历史流水账。
- 历史总览已归档到：
  - `docs/archive/project_overview/project_overview_active_snapshot_2026-03-26.md`
- 更早分卷索引见：
  - `docs/archive/project_overview/README.md`

## 项目定位

本项目是独立于 VC 主线的前置目标说话人提取模块，目标是：

- 输入混合录音与目标说话人参考音频；
- 输出尽量只保留目标说话人的净化语音；
- 给后级 VC 提供更干净的 `source`。

当前默认不做：

- 与 VC 主模型联合训练；
- 把 objective 小幅提升直接当成训练放行依据；
- 在没有 near-real 裁决前继续放大训练规模。

## 当前默认状态

截至 `2026-03-26`，当前正式状态如下：

- 默认主线：
  - `legacy stage2`
- 研究分支：
  - `v72`
    - 含义：当前 overlap-abstention 方向里最强的 objective 研究基座
    - 状态：研究用，不可放行
- 机制层 follow-up：
  - `v75`
    - 含义：`audibility-conditioned objective v1`
    - 状态：失败，guardrail 比 `v72` 更差
  - `v76`
    - 含义：`v72 + branch abstention gate`
    - 状态：失败，但证明 gate 机制有真实行为
  - `v77`
    - 含义：`v72 + gate-only isolate probe`
    - 状态：失败，但证明 gate-only 在当前损失下会退回 safe/no-op
  - `v78`
    - 含义：`v72 + abstention_gate_proxy_v1 + gate-level loss`
    - 状态：present-safe，但 absent 收益不足
  - `v79`
    - 含义：`v78` 的 stronger gate push
    - 状态：absent 更静，但重新伤到 hard present backstop
  - `v80`
    - 含义：`v79 + keep_union_v2`
    - 状态：`0006 / 0009` 更静，但 synthetic / near-real keep 都没有修好
  - `v81`
    - 含义：`v79 + audibility-conditioned gate target v1`
    - 状态：near-real 重新回到 `0` violation，但 `v54 vs v81` 听审为 `4 / 4 tie`
- 已验证失败：
  - `v73`
    - broad keep-guardrail 修正
    - 结果：能回拉部分 keep-case，但明显破坏 absent case
  - `v74`
    - strict keep-guardrail 修正
    - 结果：进一步走向过静音

当前结论：

- `legacy stage2` 仍是默认可用线。
- `v72 / v73 / v74 / v75 / v76 / v77 / v78 / v79 / v80 / v81` 都不能替代默认线。

## 当前核心子题

当前真正未解的问题不是“谁是更强 checkpoint”，而是：

- 当目标与干扰时间重合时，模型知道哪里有目标，但输出分离仍不干净；
- 目标较弱时，理想行为应更接近：
  - 识别不清就闭嘴；
  - 不要把大量干扰残留吐出来；
- 但 medium-audibility present case 又不能一起被压死。

这条子题当前统一称为：

- `weak-target overlap abstention`
- 以及它的反向 keep 约束：
  - `medium-audibility present keep`

## 当前有效验收资产

### near-real 主验收

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`
- 锚点样本：
  - `near_real_0003`
  - `near_real_0006`
  - `near_real_0007`
  - `near_real_0009`

解释：

- `0009` 看 absent / silence-over-leak；
- `0003 / 0006 / 0007` 看 target-present 下的 keep-vs-leak tradeoff。

### abstention synthetic guardrail

- `data/synthetic/val_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`

作用：

- 看弱目标 overlap-abstention 方向是否继续成立；
- 但它不能单独代表 `0003` 风格 same-gender keep-case。

### present-keep synthetic guardrail

- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- `data/synthetic/val_manifest_hard_present_gate_keep_guardrail_v1.jsonl`

作用：

- 这是当前最重要的新 guardrail；
- 它能复现 `near_real_0003` 风格 failure；
- `hard_present_gate_keep_guardrail_v1` 则覆盖 `near_real_0007` 风格 hard-present failure；
- 后续凡是 overlap-abstention 分支继续训练，都必须同时看这条。

## 本阶段已完成事项

### 1. silence-over-leak 批量客观筛选链

已完成：

- `scripts/eval/score_silence_over_leak_pack.py`
- `scripts/eval/rank_checkpoints_on_silence_over_leak_manifest.py`

结论：

- 这条链适合批量排除明显掉队候选；
- 不适合单独裁决 frontier 间细微差异。

### 2. overlap-abstention focused 资产与 pilot

已完成：

- `proxy_v3`
  - `weakfull`
- `proxy_v4`
  - `weakfull + audibility`
- `v71`
- `v72`

结论：

- `v72` 在 abstention objective 上最强；
- 但 near-real 仍卡在 `0003 / 0006` 一起过静音。

### 3. same-gender present-keep guardrail 与 follow-up

已完成：

- `same_gender_present_keep_guardrail_v1`
- `same_gender_present_keep_guardrail_v2_strict`
- `v73`
- `v74`

结论：

- keep-guardrail 本身是有效信号；
- 但简单 branch-only reweighting 无法同时修好：
  - `0003` keep
  - `0006 / 0009` abstain

### 4. audibility-conditioned objective 与 abstention gate

已完成：

- `target_energy_ratio` selector 接线
- `v75`
- `branch abstention gate` 结构
- `v76`
- `v77`
- `abstention_gate_proxy_v1`
- `v78`
- `v79`
- `hard_present_gate_keep_guardrail_v1`
- `gate_keep_union_v2`
- `abstention_gate_bundle_v2`
- `v80`

结论：

- `v75` 证明 loss-only 仍不够；
- `v76` 证明 gate 机制有信号，能把 `0009 / 0006` 往更静方向拉；
- `v77` 证明 gate-only 若没有专属监督，会退回 safe/no-op；
- `v78 / v79` 证明 gate 专属监督有效，但 keep backstop 曾缺 `0007` 风格 hard present 覆盖；
- `v80` 进一步说明：即使补了更宽的 keep union，当前二元 gate target 仍会继续滑向 over-silence；
- `v81` 进一步证明：把 gate supervision 从二元 keep / abstain 改成 audibility-conditioned target，确实能把 `0007` 拉回，同时保留一部分 `0006 / 0009` 收益；
- `v54 vs v81` focused 听审已经完成，但结果是 `4 / 4 tie`，残余泄漏问题仍无可听改善；
- 当前下一步不再是继续选 checkpoint，而是直接转到 residual leak 机制题。

## 当前最可靠的阶段结论

1. `same_gender_present_keep_guardrail_v1` 已经是正式资产，后续必须保留。
2. 当前问题不再是“缺更好的 selector”或“缺更宽的 keep 样本”，而是：
   - keep
   - abstain
   虽然已经拆出 gate，但 gate 的监督目标仍然过于二元。
3. `v81` 已经是当前最健康的 gate 机制候选，但听审显示它还没有形成可听优势，不能放行。

## 下一步默认计划

当前默认下一步不是继续扫 checkpoint，而是继续机制层改动。

优先顺序：

1. 不再继续做 `v80` 同结构 sweep。
2. `v54 vs v81` 选型题先收口，不再继续追加同类听审。
3. 下一步优先改成新的机制子题：
   - `present_overlap_residual_leak_purification`
   - 目标直接降低重叠段 residual speech leak，而不是继续微调 gate calibration
4. 后续 gate 训练固定保留四条训练/验收约束：
   - `abstention_gate_proxy_v1`
   - `same_gender_present_keep_guardrail_v1`
   - `hard_present_gate_keep_guardrail_v1`
   - `gate_keep_union_v2`
5. 在任何新训练前，固定保留以下四条验收：
   - `real_eval_manifest_residual_speech_leak_floor_v1`
   - `same_gender_present_keep_guardrail_v1`
   - `hard_present_gate_keep_guardrail_v1`
   - `overlap_abstention_proxy_v4_audibility_v1`

## 近期关键日报入口

- `reports/daily/2026-03-26_overlap_abstention_proxy_v3_v4_and_v71_v72_followup.md`
- `reports/daily/2026-03-26_present_keep_guardrail_v1_v2_and_v73_v74_followup.md`
- `reports/daily/2026-03-26_overlap_abstention_feasibility_and_plan.md`
- `reports/daily/2026-03-26_audibility_conditioned_v1_and_abstention_gate_v1_v75_v76_v77.md`
- `reports/daily/2026-03-26_abstention_gate_proxy_v1_and_v78_v79_followup.md`
- `reports/daily/2026-03-26_hard_present_gate_keep_guardrail_v1_and_v80_followup.md`
- `reports/daily/2026-03-26_audibility_gate_target_v1_and_v81_followup.md`
- `reports/daily/2026-03-26_v54_vs_v81_listening_review.md`

## 文档维护规则

- 本文档保持“活跃摘要”定位，优先写当前状态、当前验收、下一步。
- 具体长过程、逐轮试验、样本级历史判断一律写入：
  - `reports/daily/`
  - `docs/archive/project_overview/`
- 当本文件再次超过“明显不利于接班阅读”的规模时，默认处理方式不是继续堆长，而是：
  - 先归档当前版本快照；
  - 再重写为新的短摘要。
