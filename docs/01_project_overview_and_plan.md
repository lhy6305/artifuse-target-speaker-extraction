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
  - `v81`
    - 含义：当前 gate 机制线里最健康的 guardrail-safe 研究基座
    - 状态：研究用，不可放行
  - `v82`
    - 含义：`present_overlap_residual_leak_purification v1` 首轮 mask pilot
    - 状态：objective 前进明显，但 `v81 vs v82` 听审为 `4 / 4 tie`
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
  - `v82`
    - 含义：`v81 + overlap residual purify v1`
    - 状态：`same_gender / hard-present / abstention` 三条 synthetic 都改善，但 near-real `present_guardrail_violation_count = 1`
  - `v83`
    - 含义：`v81 + overlap refiner v1`
    - 状态：synthetic 大幅前进，但 near-real `present_guardrail_violation_count = 2`，不可放行
  - `v84`
    - 含义：`v81 + overlap refiner v2 prerefine`
    - 状态：比 `v83` 更受控，但 near-real 仍有 `present_guardrail_violation_count = 1`，不可放行
  - `v85`
    - 含义：`v81 + overlap refiner v3 gate-complement`
    - 状态：当前第一条 near-real `0` violation 的 refiner checkpoint，但 `v81 vs v85` 听审未转正，不可放行
  - `v86`
    - 含义：`v81 + overlap refiner v4 residual-source gate-complement`
    - 状态：relative `v81` 仍全量 objective 改善、near-real 仍 `0` violation；自动上弱于 `v85`，但更值得做人耳确认
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
- `v72 / v73 / v74 / v75 / v76 / v77 / v78 / v79 / v80 / v81 / v82 / v83 / v84 / v85` 都不能替代默认线。
- `v72 / v73 / v74 / v75 / v76 / v77 / v78 / v79 / v80 / v81 / v82 / v83 / v84 / v85 / v86` 都不能替代默认线。

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

### 5. present-overlap residual leak purification

已完成：

- `target_overlap_intervals`
- `overlap_interval_interference_projection_loss`
- `overlap_interference` selector 接线
- `v82`
- `branch_overlap_refine_head`
- `estimated_waveform_branch_base`
- `--loss-use-branch-prerefine-as-primary-prediction`
- `v83`
- `v84`
- `v85`

结论：

- `v82` 是第一条真正直接打 overlap residual leak 的 pilot；
- 相对 `v81`：
  - `overlap_abstention_proxy_v4`
    - `+2.8258 dB`
  - `same_gender_present_keep_guardrail_v1`
    - `11 / 11` improve
  - `hard_present_gate_keep_guardrail_v1`
    - `13` improve / `2` regress / `1` near tie
- 但 near-real residual leak floor 上：
  - `combined_rank = v82 > v81 > v54`
  - `guardrail_filtered_rank = v81 > v54 > v82`
  - 原因是 `near_real_0007` 重新形成 `1` 条 present guardrail violation
- `v81 vs v82` focused 听审现已完成：
  - `4 / 4 tie`
  - 无任何可感知改善
  - `0003 / 0006 / 0007 / 0009` 仍分别停留在 moderate / heavy leak 问题上
- `v83` 证明 overlap refiner 机制非常强，但当前 `v1` 监督会把 near-real 拉坏：
  - `overlap_abstention_proxy_v4`
    - `+8.5779 dB`
  - `same_gender_present_keep_guardrail_v1`
    - `+6.4518 dB`
  - `hard_present_gate_keep_guardrail_v1`
    - `+5.6606 dB`
  - 但 near-real：
    - `present_guardrail_violation_count = 2`
    - `target_capture_regression_sample_ids = [near_real_0007]`
    - `residual_increase_sample_ids = [near_real_0003, near_real_0007]`
- `v84` 证明 refiner-specific prerefine baseline / delta guard 有真实作用：
  - synthetic 相对 `v81` 仍全量改善：
    - abstention `+7.3566 dB`
    - same-gender keep `+5.1392 dB`
    - hard-present keep `+4.4538 dB`
  - near-real 相对 `v83` 明显回拉：
    - `present_guardrail_violation_count = 2 -> 1`
    - `residual_increase_sample_ids`
      - `[near_real_0003, near_real_0007] -> [near_real_0007]`
  - 但它仍未超过 `v81`：
    - `guardrail_filtered_rank = v81 > v54 > v84 > v82 > v83`
    - `near_real_0007` 仍是硬回退样本
- `v85` 证明 `gate-complement` 是当前最有效的 refiner 激活语义：
  - synthetic 相对 `v81` 仍全量改善：
    - abstention `+4.7489 dB`
    - same-gender keep `+2.1718 dB`
    - hard-present keep `+2.3698 dB`
  - near-real 首次回到：
    - `present_guardrail_violation_count = 0`
    - `target_capture_regression_sample_ids = []`
    - `residual_increase_sample_ids = []`
  - `guardrail_filtered_rank`
    - `v85 > v81 > v54 > v84 > v82 > v83`
  - 当前已经导出 focused 包：
    - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind`
  - 但 `v81 vs v85` focused 听审现已完成：
    - `3 / 4 tie`
    - `1 / 4 = v81`
    - `v85 = 0`
    - `near_real_0009` 被人耳明确判为 `v81` 更好
- `v86` 进一步证明 residual-source refiner 是成立的新机制：
  - synthetic relative `v81`
    - abstention `+3.5979 dB`
    - same-gender keep `+1.6103 dB`
    - hard-present keep `+1.7029 dB`
  - near-real residual leak floor
    - 仍是 `present_guardrail_violation_count = 0`
    - absent suppression 介于 `v81` 和 `v85` 之间
    - `0007` keep-side tradeoff 相对 `v81` 继续前进
  - 当前已导出 focused 包：
    - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind`
  - 当前最合理的下一步已变成：
    - 先听 `v81 vs v86`
    - 不再继续自动扩树

## 当前最可靠的阶段结论

1. `same_gender_present_keep_guardrail_v1` 已经是正式资产，后续必须保留。
2. overlap refiner 机制已经成立，当前最有效的收窄方式是：
   - 用 `gate-complement`
   - 而不是 `gate`
3. `v81` 仍是当前最健康、最稳妥的研究基座；`v85` 虽然自动上最强，但本轮听审没有转正。

## 下一步默认计划

当前默认状态不是继续自动扩树，而是先完成 `v81 vs v86` focused 听审。

优先顺序：

1. `v54 vs v81` 选型题已经收口，不再继续追加同类听审。
2. `v81 vs v82` 选型题已收口，不再继续追加同类听审。
3. 当前阶段结论已更新为：
   - `v85` 不升格
   - `v81` 继续保留为研究基座
   - `v86` 进入下一道 focused 听审
4. 当前默认不再继续做：
   - `v83` 式宽触发 refiner
   - `v84` 附近轻量 sweep
   - `v85` 之后的自动 checkpoint 扩树
   直到 `v81 vs v86` 听审给出结果
5. 后续训练固定保留四条训练/验收约束：
   - `abstention_gate_proxy_v1`
   - `same_gender_present_keep_guardrail_v1`
   - `hard_present_gate_keep_guardrail_v1`
   - `gate_keep_union_v2`
6. 在任何新训练前，固定保留以下四条验收：
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
- `reports/daily/2026-03-26_present_overlap_residual_purify_v1_and_v82_followup.md`
- `reports/daily/2026-03-26_v81_vs_v82_listening_review.md`
- `reports/daily/2026-03-26_overlap_refiner_v1_v2_and_v83_v84_followup.md`
- `reports/daily/2026-03-26_overlap_refiner_v3_gatecomplement_and_v85_followup.md`
- `reports/daily/2026-03-26_v81_vs_v85_listening_review.md`
- `reports/daily/2026-03-26_overlap_refiner_v4_residualsource_and_v86_followup.md`

## 文档维护规则

- 本文档保持“活跃摘要”定位，优先写当前状态、当前验收、下一步。
- 具体长过程、逐轮试验、样本级历史判断一律写入：
  - `reports/daily/`
  - `docs/archive/project_overview/`
- 当本文件再次超过“明显不利于接班阅读”的规模时，默认处理方式不是继续堆长，而是：
  - 先归档当前版本快照；
  - 再重写为新的短摘要。
