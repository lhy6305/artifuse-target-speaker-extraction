# 任务分支图

## 文档定位

- 本文档只保留当前仍会影响下一步决策的活跃分支地图。
- 历史长版已归档到：
  - `docs/archive/task_branch_map/task_branch_map_active_snapshot_2026-03-26.md`
- 更早分卷与长节索引见：
  - `docs/archive/task_branch_map/README.md`

## 当前主线与研究线

### 默认主线

- `legacy stage2`
- 状态：
  - 默认可用线
  - 当前不被任何研究分支替代

### 当前 overlap-abstention 研究基座

- `v72`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v72_v54_overlap_abstention_proxy_v4_audibility_v1_ft1`
- 状态：
  - objective 研究基座
  - 不能放行

### 当前 gate 机制探针

- `v76`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v76_v72_audibility_conditioned_v1_gate_v1_ft1`
  - 状态：
    - 证明 gate 机制有信号
    - 不能放行
- `v77`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v77_v72_audibility_conditioned_v1_gateonly_v1_ft1`
  - 状态：
    - gate-only isolate probe
    - 不能放行
- `v78`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v78_v72_abstention_gate_proxy_v1_supervised_ft1`
  - 状态：
    - gate supervision first safe pilot
    - 不能放行
- `v79`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v79_v78_abstention_gate_proxy_v1_supervised_tuned_ft1`
  - 状态：
    - stronger gate push
    - 不能放行
- `v80`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v80_v79_abstention_gate_keepunion_v2_ft1`
  - 状态：
    - wider keep union follow-up
    - 不能放行
- `v81`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v81_v79_audibility_gate_target_v1_ft1`
  - 状态：
    - audibility-conditioned gate target first pilot
    - 听审已完成，不能直接放行
- `v82`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v82_v81_overlap_purify_v1_ft1`
  - 状态：
    - present-overlap residual purification first pilot
    - objective 前进明显，但 focused 听审 `4 / 4 tie`
- `v83`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v83_v81_overlap_refiner_v1_ft1`
  - 状态：
    - overlap refiner first pilot
    - synthetic 大幅前进，但 near-real guardrail 明显失败
- `v84`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v84_v81_overlap_refiner_v2_prerefine_ft1_rerun2`
  - 状态：
    - overlap refiner prerefine follow-up
    - 比 `v83` 更受控，但仍未过 near-real guardrail
- `v85`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v85_v81_overlap_refiner_v3_gatecomplement_ft1`
  - 状态：
    - overlap refiner gate-complement pilot
    - 当前第一条已过 near-real guardrail 的 refiner 候选
    - 但 `v81 vs v85` 听审未转正
- `v86`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v86_v81_overlap_refiner_v4_residualsource_gatecomplement_ft1`
  - 状态：
    - overlap refiner residual-source gate-complement follow-up
    - relative `v81` 仍保持三条 synthetic 正收益
    - near-real 仍为 `0` present violation
    - `v81 vs v86` 听审已完成，但仍未转正
- `v87`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v87_v81_overlap_canceller_v1_ft1`
  - 状态：
    - overlap canceller first pilot
    - synthetic / near-real 都正向，但后验确认基本只是 `v86` 的近等价体
    - 不进入 focused 听审终裁
- `v88`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v88_v87_overlap_canceller_v2_targetorth_ft1`
  - 状态：
    - overlap canceller target-orthogonality follow-up
    - 当前 canceller 家族最强自动候选
    - `v81 vs v88` 听审已完成，但仍未转正
- `v89`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v89_v81_overlap_dualsource_consistency_v1_ft1`
  - 状态：
    - overlap dual-source consistency v1
    - relative `v81` 更强，但仍低于 `v88`
    - 不进入 focused 听审
- `v90`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v90_v81_overlap_dual_decoder_v1_ft1`
  - 状态：
    - overlap dual decoder v1
    - direct dual-target 输出导致整体大幅回退
    - 不进入 focused 听审
- `v91`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v91_v81_overlap_dual_decoder_v1_blendcap025_ft1`
  - 状态：
    - `v90 + max_blend 0.25`
    - 比 `v90` 更稳定，但仍整体差于 `v81`
    - 不进入 focused 听审

## 当前活跃问题树

### A. silence-over-leak / absent frontier

目的：

- 解决弱目标或 absent 情况下“宁可闭嘴，也不要漏干扰”。

当前资产：

- `scripts/eval/score_silence_over_leak_pack.py`
- `scripts/eval/rank_checkpoints_on_silence_over_leak_manifest.py`
- `data/references/real_eval_manifest_silence_over_leak_guardrail_v2.jsonl`

当前结论：

- 这条线已经完成批量排雷作用；
- 适合筛掉明显更差的 checkpoint；
- 不再适合继续做 frontier 选美。

当前状态：

- `closed_as_selection_problem`

### B. residual speech leak floor / overlap-abstention

目的：

- 解决目标与干扰时间重合时的残余人声泄漏；
- 同时满足“弱目标可闭嘴”和“中等可辨目标不能一起被压坏”。

主 near-real 验收：

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`

关键样本：

- `near_real_0003`
  - medium-audibility keep anchor
- `near_real_0006`
  - weak-target overlap abstention anchor
- `near_real_0007`
  - hard present backstop
- `near_real_0009`
  - absent / external speech only anchor

当前状态：

- `active`

当前子方向：

- `audibility-conditioned objective`
  - `failed_as_loss_only`
- `branch abstention gate`
  - `active_mechanism_probe`
- `hard-present gate keep backstop`
  - `guardrail_materialized_but_insufficient_as_sample_union`
- `present-overlap residual purification`
  - `active`
- `overlap refiner`
  - `active_guardrail_safe_but_not_audibly_better`
- `overlap dual-source consistency`
  - `failed_to_cross_v88_plateau`
- `overlap dual decoder`
  - `failed_as_direct_output_path`

### C. same-gender present keep

目的：

- 专门约束 `near_real_0003` 风格的 same-gender keep-case；
- 防止 overlap-abstention 方向把 target-present 一起压坏。

当前资产：

- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v2_strict.jsonl`

当前结论：

- `v1` 是有效正式 guardrail；
- `v2_strict` 只适合作为更窄 probe，不适合作为主训练方向。

当前状态：

- `active_guardrail`

## 当前 active checkpoint 关系

### 1. `v72`

含义：

- overlap-abstention objective 最强研究基座

优点：

- `0009` absent suppression 比 `v54` 更强
- `proxy_v4` abstention objective 最优

问题：

- near-real 仍有：
  - `0003`
  - `0006`
  两条 present violation

裁决：

- `research_base_keep`

### 2. `v75`

含义：

- `v72 + audibility-conditioned objective v1`

结果：

- combined rank 看起来更强
- 但 synthetic abstention 回退
- keep / near-real guardrail 都更差

裁决：

- `failed_loss_only`

### 3. `v76`

含义：

- `v72 + audibility-conditioned objective v1 + branch abstention gate`

结果：

- `0009 / 0006` 有真实更静收益
- 但 `0007` 被 gate 一起压坏

裁决：

- `failed_joint_gate_drift`

### 4. `v77`

含义：

- `v72 + gate-only isolate probe`

结果：

- present guardrail 恢复安全
- abstention 收益基本消失

裁决：

- `failed_safe_noop`

### 5. `v78`

含义：

- `v72 + abstention_gate_proxy_v1 + gate-level loss`

结果：

- 恢复到 present-safe
- absent 仍不够静

裁决：

- `safe_but_absent_weak`

### 6. `v79`

含义：

- `v78 + stronger gate push`

结果：

- `0006 / 0009` 更静
- `0007` 开始回退

裁决：

- `failed_hard_present_backstop`

### 7. `v73`

含义：

- `v72 + broad same-gender keep guardrail`

结果：

- synthetic keep violation 明显下降
- 但 `near_real_0009` absent suppression 明显回退
- near-real 仍未修好 `0003 / 0006`

裁决：

- `failed_tradeoff`

### 8. `v74`

含义：

- `v72 + strict same-gender keep probe`

结果：

- absent objective 更强
- 但 near-real 变成更严重的过静音
- present violation 增加到：
  - `0003`
  - `0006`
  - `0007`

裁决：

- `failed_over_silence`

### 9. `v80`

含义：

- `v79 + keep_union_v2`

结果：

- `0006 / 0009` 更静
- `same_gender keep guardrail`
  - 仍是 `11` 条 violation
- `hard_present keep guardrail`
  - 仍是 `16` 条 violation
- `0007` 比 `v79` 更坏

裁决：

- `failed_binary_gate_target`

### 10. `v81`

含义：

- `v79 + audibility-conditioned gate target v1`

结果：

- `overlap_abstention_proxy_v4`
  - 相对 `v79` 是 `+1.9569 dB`
- `same_gender keep guardrail`
  - `11 -> 4` violations
- `hard_present keep guardrail`
  - `16 -> 12` violations
- near-real residual leak floor
  - 回到 `0` violation
  - `0007` 已明显拉回
  - `0006 / 0009` 仍保留部分更静收益
- `v54 vs v81` focused 听审
  - `4 / 4 tie`
  - 无任何可感知差异
  - 两侧都仍有明显 residual leak

裁决：

- `promising_but_not_audibly_better`

### 11. `v82`

含义：

- `v81 + overlap residual purify v1`

结果：

- `overlap_abstention_proxy_v4`
  - 相对 `v81` 是 `+2.8258 dB`
- `same_gender_present_keep_guardrail_v1`
  - `11 / 11` improve
- `hard_present_gate_keep_guardrail_v1`
  - `13` improve / `2` regress / `1` near tie
- near-real residual leak floor
  - `combined_rank = v82 > v81 > v54`
  - 但 `present_guardrail_violation_count = 1`
  - 回退样本：
    - `near_real_0007`
- focused 听审：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v82_blind`
  - 解盲结果：
    - `4 / 4 tie`
    - 无任何可感知差异

裁决：

- `objective_only_progress_not_audible`

### 12. `v83`

含义：

- `v81 + overlap refiner v1`

结果：

- relative `v81`
  - abstention `+8.5779 dB`
  - same-gender keep `+6.4518 dB`
  - hard-present keep `+5.6606 dB`
- near-real residual leak floor
  - `combined_rank = 1st`
  - 但 `present_guardrail_violation_count = 2`
  - 回退样本：
    - `near_real_0007`
  - residual share 增加样本：
    - `near_real_0003`
    - `near_real_0007`

裁决：

- `failed_refiner_v1_overpush`

### 13. `v84`

含义：

- `v81 + overlap refiner v2 prerefine`

结果：

- relative `v81`
  - abstention `+7.3566 dB`
  - same-gender keep `+5.1392 dB`
  - hard-present keep `+4.4538 dB`
- relative `v83`
  - near-real violation `2 -> 1`
  - residual increase 缩到：
    - `near_real_0007`
- 但 relative `v81`
  - `near_real_0007` 仍明显回退
  - `guardrail_filtered_rank = v81 > v54 > v84 > v82 > v83`

裁决：

- `partially_recovered_but_not_safe`

### 14. `v85`

含义：

- `v81 + overlap refiner v3 gate-complement`

结果：

- relative `v81`
  - abstention `+4.7489 dB`
  - same-gender keep `+2.1718 dB`
  - hard-present keep `+2.3698 dB`
- near-real residual leak floor
  - `present_guardrail_violation_count = 0`
  - `target_capture_regression_sample_ids = []`
  - `residual_increase_sample_ids = []`
  - `guardrail_filtered_rank = 1st`
- focused 包已导出：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind`
- focused 听审结果：
  - `3 / 4 tie`
  - `1 / 4 = v81`
  - `v85 = 0`
  - `near_real_0009` 被人耳明确判为 `v81` 更好

裁决：

- `objective_frontier_but_not_audibly_better`

### 15. `v86`

含义：

- `v81 + overlap refiner v4 residual-source gate-complement`

结果：

- relative `v81`
  - overlap-abstention `+3.5979 dB`
  - same-gender keep `+1.6103 dB`
  - hard-present keep `+1.7029 dB`
- relative `v85`
  - objective 会让回一部分
  - 但 absent 侧不再像 `v85` 那样激进
- near-real residual leak floor
  - `present_guardrail_violation_count = 0`
  - `near_real_0007` 未再被推过 guardrail
  - `near_real_0006 / 0009` 仍保留更静趋势
- focused 包已导出：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind`
- focused 听审结果：
  - `3 / 4 tie`
  - `1 / 4 = v81`
  - `v86 = 0`
  - 唯一分出胜负的是：
    - `near_real_0009 = v81 > v86`

裁决：

- `objective_guardrail_better_but_not_audibly_better`

### 16. `v87`

含义：

- `v81 + overlap canceller v1`

结果：

- relative `v81`
  - synthetic 三条线都是正收益
  - near-real residual leak floor 也保持 `0` violation
- 但 direct compare `v86 vs v87`
  - 几乎是完全近等价
  - 没有形成新的行为层级

裁决：

- `near_equivalent_to_v86`

### 17. `v88`

含义：

- `v87 + overlap canceller v2 target-orthogonality`

结果：

- relative `v87`
  - abstention `+1.0108 dB`
  - same-gender keep `+0.5571 dB`
  - hard-present keep `+0.5978 dB`
- near-real residual leak floor
  - `guardrail_filtered_rank = 1st`
  - `present_guardrail_violation_count = 0`
- focused 包已导出：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v88_blind`
- focused 听审结果：
  - `tie = 2`
  - `v81 = 2`
  - `v88 = 0`
  - 仅有的细微可感知差异都没有指向 `v88`

裁决：

- `objective_frontier_but_not_audibly_better`

### 18. `v89`

含义：

- `v81 + overlap dual-source consistency v1`

结果：

- relative `v81`
  - `overlap_dualsource_proxy_v1 = +3.6070 dB`
  - `same_gender_present_keep_guardrail_v1 = +1.6128 dB`
  - `hard_present_gate_keep_guardrail_v1 = +1.7024 dB`
- relative `v88`
  - overlap-abstention `-1.0070 dB`
  - same-gender keep `-0.5562 dB`
  - hard-present keep `-0.5994 dB`
- near-real residual leak floor
  - `combined_rank = v88 > v89 > v81 > v54`
  - `guardrail_filtered_rank = v88 > v89 > v81 > v54`
- 样本级上：
  - `0003 / 0006 / 0009`
    - 都是 `v81 < v89 < v88`
  - `0007`
    - 也是更接近 `v88` 的 softened 版本，而不是新行为层级
- 因此不导：
  - `v81 vs v89` focused 听审

裁决：

- `intermediate_checkpoint_not_new_frontier`

### 19. `v90`

含义：

- `v81 + overlap dual decoder v1`

结果：

- relative `v81`
  - overlap-abstention `-6.8556 dB`
  - same-gender keep `-4.7200 dB`
  - hard-present keep `-11.6327 dB`
- near-real residual leak floor
  - `v88 > v81 > v54 > v90`
- 失败模式：
  - direct dual-target 路径过度替换 `branch_base`
  - 四个 near-real 锚点一起变成更大泄漏 / 更大音量

裁决：

- `failed_direct_dual_target_takeover`

### 20. `v91`

含义：

- `v90 + overlap dual decoder blend cap 0.25`

结果：

- relative `v81`
  - overlap-abstention `-5.1942 dB`
  - same-gender keep `-5.2723 dB`
  - hard-present keep `-5.0749 dB`
- near-real residual leak floor
  - `v88 > v81 > v54 > v91`
- 比 `v90` 更稳定，但仍没有回到 `v81` 邻域

裁决：

- `stabilized_but_still_failed`

## 当前有效训练与验收入口

### 训练侧

- abstention focused proxy：
  - `data/synthetic/train_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`
  - `data/synthetic/val_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`
- keep guardrail：
  - `data/synthetic/train_manifest_same_gender_present_keep_guardrail_v1.jsonl`
  - `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- gate 机制 follow-up：
  - `data/synthetic/train_manifest_audibility_conditioned_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_audibility_conditioned_bundle_v1.jsonl`
  - `data/synthetic/train_manifest_abstention_gate_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_abstention_gate_proxy_v1.jsonl`
  - `data/synthetic/train_manifest_abstention_gate_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_abstention_gate_bundle_v1.jsonl`
  - `data/synthetic/train_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
  - `data/synthetic/val_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
  - `data/synthetic/train_manifest_gate_keep_union_v2.jsonl`
  - `data/synthetic/val_manifest_gate_keep_union_v2.jsonl`
  - `data/synthetic/train_manifest_abstention_gate_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_abstention_gate_bundle_v2.jsonl`

### 验收侧

- near-real 主验收：
  - `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`
- keep synthetic guardrail：
  - `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- hard-present keep synthetic guardrail：
  - `data/synthetic/val_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
- abstention synthetic guardrail：
  - `data/synthetic/val_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`

## 当前禁止误接的旧分支

以下分支不应再被当作默认下一步：

- `v64 / v65 / v66 / v67`
- `candidate_v4 / candidate_v5 / candidate_v7`
- `same_gender_reverb_proxy_v3` 直接训
- 纯 checkpoint frontier 继续扫 `v72` 附近权重

原因：

- 它们要么已经被后续阶段覆盖；
- 要么已经证明不再回答当前核心问题。

## 默认下一步

如果没有新的用户决策，当前默认下一步是：

- `v54 vs v81` 选型题已收口；
- `v81 vs v82` 选型题也已收口；
- `v81 vs v84` 当前不导听审，因为 near-real guardrail 尚未过线；
- `v81 vs v85` 听审已完成，当前结论是：
  - `v85` 不升格
  - `v81` 继续作为研究基座
- `v81 vs v86` 听审也已完成，当前结论是：
  - `v86` 不升格
  - `v81` 继续作为研究基座
- `v87` 已确认只是 `v86` 的近等价体，不再单独推进
- `v81 vs v88` 听审也已完成，当前结论是：
  - `v88` 不升格
  - `v81` 继续作为研究基座
- `v89` 已完成自动验收，当前结论是：
  - `v89` 也不升格
  - 不进入 focused 听审
- `v90 / v91` 已完成自动验收，当前结论是：
  - direct dual-target output 线先收口
  - 不进入 focused 听审
- 不再继续做 `v83` 式宽触发 refiner，也不做 `v84` 附近小权重 sweep；
- 不再继续做 `v85 / v86` 同家族小步 sweep；
- 不再继续做 `v87 / v88` 同家族小步 sweep；
- 不再继续做 `v89` 同家族小步 sweep；
- 不再继续做 `v90 / v91` 同家族小步 sweep；
- 若后续继续推进，默认应切到：
  - `overlap interference auxiliary decoder v1`
  而不是继续让显式 dual path 直接接管最终输出

执行前必须保持四条验收同时在场：

- `real_eval_manifest_residual_speech_leak_floor_v1`
- `same_gender_present_keep_guardrail_v1`
- `hard_present_gate_keep_guardrail_v1`
- `overlap_abstention_proxy_v4_audibility_v1`

## 近期关键日报入口

- `reports/daily/2026-03-26_overlap_abstention_proxy_v3_v4_and_v71_v72_followup.md`
- `reports/daily/2026-03-26_present_keep_guardrail_v1_v2_and_v73_v74_followup.md`
- `reports/daily/2026-03-26_frontier_imperfection_taxonomy_and_next_subproblem.md`
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
- `reports/daily/2026-03-26_v81_vs_v86_listening_review.md`
- `reports/daily/2026-03-26_overlap_canceller_v1_v2_and_v87_v88_followup.md`
- `reports/daily/2026-03-26_v81_vs_v88_listening_review.md`
- `reports/daily/2026-03-26_overlap_dualsource_consistency_v1_and_v89_followup.md`
- `reports/daily/2026-03-26_overlap_dual_decoder_v1_v90_v91_followup.md`

## 文档维护规则

- 本文档只记录：
  - 当前活跃分支
  - 当前裁决状态
  - 当前默认下一步
- 已终止分支、旧 family 的长历史，不再回填到主文档。
- 当本文件再次膨胀到不利于接班阅读时，默认处理方式是：
  1. 先把当时版本完整快照到 `docs/archive/task_branch_map/`
  2. 再重写为新的短版活跃分支图
