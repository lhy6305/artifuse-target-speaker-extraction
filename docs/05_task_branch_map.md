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

### 当前研究基座

- `v81`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v81_v79_audibility_gate_target_v1_ft1`
- 状态：
  - 当前最稳的 guardrail-safe 研究基座
  - 听审已完成，但未形成可听胜出
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
- `v93`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v93_v88_overlap_aux_interference_decoder_v2_priortransfer_ft1`
  - 状态：
    - overlap auxiliary decoder v2
    - synthetic 提升明显，但 near-real 重新伤到 `0003 / 0007`
    - 不进入 focused 听审终裁
- `v94`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v94_v88_overlap_aux_interference_decoder_v3_maskheadtransfer_ft1`
  - 状态：
    - overlap auxiliary decoder v3
    - failure 收窄到 `0007`
    - 仍不过 near-real guardrail
- `v95`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v95_v94_overlap_aux_interference_decoder_v4_hardpresentprotect_ft1`
  - 状态：
    - overlap auxiliary decoder v4
    - automatic suppression 更强，但 `v81 vs v95` 听审为 `tie = 3, v81 = 1, v95 = 0`
    - 唯一可感知差异是 `0007` 上 `v95` 伪影更重
- `v96`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v96_v81_overlap_aux_interference_decoder_v5_phasepreserve_ft1`
  - 状态：
    - `phase_preserve` overlap cancel head first probe
    - 但 `auxiliary_only + overlap_cancel_head-only` 结构性 output-inactive
    - 不构成真实候选
- `v97`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v97_v81_overlap_aux_interference_decoder_v5_phasepreserve_fixgrad_ft1`
  - 状态：
    - `v96` 的 startup/gradient 修正版复跑
    - 仍是结构性 no-op probe
    - 不构成真实候选
- `v98`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v98_v81_overlap_canceller_v3_phasepreserve_subtract_ft1`
  - 状态：
    - 首个有效的 `phase-preserving subtractive overlap canceller`
    - synthetic / near-real tradeoff / bandwidth 都近乎与 `v81` 全 tie
    - 不进入 focused 听审
- `v99`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v99_v95_hardpresent_artifact_veto_v1_ft1`
  - 状态：
    - self-align artifact veto probe
    - 在 `auxiliary_only` 家族上是结构性 no-op
    - 不构成真实候选
- `v100`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v100_v95_teacher_artifact_veto_v1_ft1`
  - 状态：
    - frozen teacher hard-present overlap veto
    - relative `v81` 三条 synthetic 全量正收益
    - near-real objective gate 已通过
    - `v81 vs v100` 听审结果为 `tie = 3, v81 = 1, v100 = 0`
    - 分支先收口，不升格
- `v101`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v101_v88_overlap_cancel_deltablend_v1_ft1`
  - 状态：
    - `v88 + overlap cancel delta blend v1`
    - relative `v81` synthetic / near-real objective 继续正收益
    - relative `v88` 明显更保守，是一个真正的中间解
    - `v81 vs v101` 听审结果为 `tie = 3, v81 = 1, v101 = 0`
    - 分支先收口，不升格

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
- `overlap auxiliary interference decoder`
  - `objective_positive_but_not_audibly_better`
- `teacher artifact veto`
  - `closed_as_non_audible_improvement`
- `overlap cancel delta blend`
  - `closed_as_safety_calibration_only`
- `local explicit speech leak backstop`
  - `active`
- `phone-artifact guardrail`
  - `active_diagnostic_gate`

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

### 21. `v93`

含义：

- `v88 -> auxiliary_only` prior transfer through `branch_decoder_temporal_model`

结果：

- relative `v81`
  - overlap-abstention `+2.0561 dB`
  - same-gender keep `+0.7050 dB`
  - hard-present keep `+0.9061 dB`
- near-real residual leak floor
  - `combined_rank = v88 > v93 > v81 > v54 > v92`
  - 但 `present_guardrail_violation_count = 2`
  - 回退样本：
    - `near_real_0003`
    - `near_real_0007`

裁决：

- `failed_temporal_transfer_too_wide`

### 22. `v94`

含义：

- `v88 -> auxiliary_only` narrower transfer through `branch_decoder_mask_head`

结果：

- relative `v81`
  - overlap-abstention `+2.8521 dB`
  - same-gender keep `+1.2026 dB`
  - hard-present keep `+1.0078 dB`
- near-real residual leak floor
  - `present_guardrail_violation_count = 1`
  - 唯一回退样本：
    - `near_real_0007`

裁决：

- `narrower_but_still_not_safe`

### 23. `v95`

含义：

- `v94 + hard-present protect`

结果：

- relative `v81`
  - overlap-abstention `+3.6205 dB`
  - same-gender keep `+1.6459 dB`
  - hard-present keep `+1.2283 dB`
- near-real residual leak floor
  - `present_guardrail_violation_count = 1`
  - 唯一自动黄灯仍是：
    - `near_real_0007`
- focused 包：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v95_blind`
- focused 听审结果：
  - `tie = 3`
  - `v81 = 1`
  - `v95 = 0`
  - 唯一可感知差异：
    - `near_real_0007 = v81 > v95`
    - 原因：
      - `v95` 伪影更重

裁决：

- `objective_gain_but_artifact_regression`

### 24. `v96`

含义：

- `v81 + phase_preserve overlap cancel head`
- 但接法是：
  - `auxiliary_only`
  - 只训练 `branch_overlap_cancel_head`

结果：

- 三条 synthetic 全部 exact tie
- 没有真实输出变化

裁决：

- `structurally_output_inactive_probe`

### 25. `v97`

含义：

- `v96` 的 `phase_preserve` gradient-startup 修正版复跑

结果：

- 虽然修掉了 dead-zone 风险
- 但三条 synthetic 仍然全部 exact tie
- 原因仍是结构性 output-inactive

裁决：

- `fixed_probe_but_still_noop`

### 26. `v98`

含义：

- `v81 + overlap canceller v3 phasepreserve subtract`

结果：

- relative `v81`
  - overlap-abstention `-0.0028 dB`
  - same-gender keep `+0.0005 dB`
  - hard-present keep `+0.0004 dB`
- near-real tradeoff pack：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v98_blind`
  - `better_source_retention = tie 3 + not_applicable 1`
  - `more_interference_leaky = tie 4`
  - `more_residual_heavy = tie 4`
  - `better_retention_minus_leak = tie 3 + not_applicable 1`
- bandwidth：
  - `tie = 4`

解释：

- 这是第一条真正有效的 `phase-preserving subtractive` pilot；
- 但它和 `v81` 基本是近等价体，没有形成新的行为层级；
- 因而不导 focused 听审。

裁决：

- `valid_but_near_exact_tie_to_v81`

### 27. `v107`

含义：

- `v81 + overlap_purify_v5_local_speech_leak_bundle_v1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v107_v81_overlap_purify_v5_local_speech_leak_bundle_v1_ft1`

结果：

- 新增：
  - `local_speech_leak_proxy_v1`
  - `speech_leak_local_aware_bundle_v1`
- 核心语义是：
  - 从 `speech_plus_music` 原样本切局部高 risk 窗
  - 但导出的训练视图只保留 `target + speech layer`
- relative `v81`
  - `overlap_abstention_proxy_v4_audibility_v1`
    - `+3.0895 dB`
  - `same_gender_present_keep_guardrail_v1`
    - `+1.4266 dB`
  - `hard_present_gate_keep_guardrail_v1`
    - `+1.1428 dB`
- near-real whole-utterance：
  - `overall_pass = true`
  - `0003` 的 `retention-minus-leak` 转正
  - `0009` absent suppression 基本 tie
- overlap-local：
  - `0003 / 0006`
    - `better_retention_minus_speech_leak = v107`
  - `0007`
    - `better_retention_minus_speech_leak = v81`
    - `more_artifact_proxy_heavy = v107`

裁决：

- `automatic_positive_but_artifact_lost_in_blind_review`

### 28. `v108`

含义：

- `v107 + local_speech_leak preserve backstop v1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v108_v107_local_speech_leak_preservebackstop_v1_ft1`

结果：

- 保留：
  - `speech_leak_local_aware_bundle_v1`
  - `speech_only overlap_interference_extra`
- 新增：
  - `sample_ids_local_speech_leak_proxy_v1_all.txt`
  - 在 `local_speech_leak_proxy_v1` 全量子集上打开：
    - `branch_protect_guard_sisdr`
    - `branch_protect_teacher_overlap(v81)`
- relative `v81`
  - abstention `-0.6017 dB`
  - same-gender keep `+0.3024 dB`
  - hard-present keep `+0.0170 dB`
  - hard-present artifact proxy `+0.2906 dB`
- relative `v107`
  - abstention `-3.6913 dB`
  - same-gender keep `-1.1242 dB`
  - hard-present keep `-1.1257 dB`
  - hard-present artifact proxy `-1.5016 dB`
- near-real / phone-artifact：
  - relative `v81`
    - `phone_artifact_gate_v1 = fail`
  - relative `v107`
    - `phone_artifact_gate_v1 = pass`
  - 说明这版确实止住了部分 `v107` 电话音式 artifact
  - 但代价是把 `v107` 的主收益一起抹掉

裁决：

- `artifact_relief_but_over_regularized`

### 29. `v109`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v109_v107_local_speech_leak_0007like_backstop_v1_ft1`

结果：

- 保留：
  - `speech_leak_local_aware_bundle_v1`
  - `speech_only overlap_interference_extra`
- 新增：
  - `build_local_speech_leak_0007_like_proxy.py`
  - `sample_ids_local_speech_leak_0007_like_proxy_v1_all.txt`
  - 在更窄的 `0007` 风格 `music_plus_speech hard-present` 局部窗上打开：
    - `branch_protect_guard_sisdr`
    - `branch_protect_teacher_overlap(v81)`
- relative `v81`
  - abstention `+2.5930 dB`
  - same-gender keep `+1.0756 dB`
  - hard-present keep `+0.6735 dB`
  - hard-present artifact proxy `+1.4404 dB`
  - `near-real tradeoff gate = pass`
  - `phone_artifact_gate_v1 = pass`
- relative `v107`
  - abstention `-0.4966 dB`
  - same-gender keep `-0.3511 dB`
  - hard-present keep `-0.4693 dB`
  - hard-present artifact proxy `-0.3518 dB`
  - `near-real tradeoff gate = pass`
  - `phone_artifact_gate_v1 = pass`
- overlap-local：
  - relative `v81`
    - `0003 / 0007`
      - `better_retention_minus_speech_leak = v109`
    - `0007`
      - `more_artifact_proxy_heavy = v109`
  - relative `v107`
    - `0003 / 0007`
      - `better_retention_minus_speech_leak = v109`
    - `0007`
      - `more_artifact_proxy_heavy = tie`

裁决：

- `near_tie_but_painpoint_unresolved`

### 30. `v110`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v110_v109_local_speech_leak_artifact_paired_0007like_bundle_v1_ft1`

结果：

- 新增 paired 资产：
  - `build_hard_present_artifact_0007_like_proxy.py`
  - `train/val_manifest_hard_present_artifact_0007_like_proxy_v1.jsonl`
  - `train/val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- 训练口径：
  - 从 `v109` 初始化
  - leak view：
    - `sample_ids_local_speech_leak_0007_like_proxy_v1_all.txt`
    - `speech_only overlap_interference_extra`
  - artifact view：
    - `sample_ids_hard_present_artifact_0007_like_proxy_v1_all.txt`
    - `branch_protect_guard_sisdr`
    - `branch_protect_teacher_overlap(v81)`
- selector 激活：
  - train
    - `overlap_interference_extra = 3 / 108`
    - `branch_protect = 3 / 108`
    - `branch_protect_teacher = 3 / 108`
  - val
    - `overlap_interference_extra = 2 / 39`
    - `branch_protect = 3 / 39`
    - `branch_protect_teacher = 3 / 39`
- relative `v81`
  - abstention `+3.2903 dB`
  - same-gender keep `+1.2213 dB`
  - hard-present keep `+0.9344 dB`
  - hard-present artifact proxy `+1.6590 dB`
  - `near-real tradeoff gate = pass`
  - `phone_artifact_gate_v1 = pass`
- relative `v109`
  - abstention `+0.6973 dB`
  - same-gender keep `+0.1458 dB`
  - hard-present keep `+0.2610 dB`
  - hard-present artifact proxy `+0.2186 dB`
  - `near-real tradeoff gate = pass`
  - `phone_artifact_gate_v1 = pass`
- 关键 near-real：
  - relative `v81`
    - `0007`
      - overlap-local：
        - `better_retention_minus_speech_leak = v110`
        - `better_retention_minus_total_leak = v81`
        - `more_artifact_proxy_heavy = v110`
      - whole-utterance：
        - `better_retention_minus_leak = v81`
  - relative `v109`
    - `0007`
      - overlap-local：
        - `better_retention_minus_speech_leak = v110`
        - `better_retention_minus_total_leak = v109`
      - whole-utterance：
        - `better_retention_minus_leak = v109`

裁决：

- `objective_positive_but_over_suppressive`

### 31. `v111`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v111_v109_local_speech_leak_artifact_paired_0007like_selfanchor_v1_ft1`

结果：

- 与 `v110` 相比只改两点：
  - teacher：
    - `v81 -> v109`
  - 权重：
    - `branch_protect_teacher_overlap_weight: 3.0 -> 6.0`
    - `overlap_interference_extra_weight: 0.03 -> 0.015`
- relative `v81`
  - abstention `+3.0139 dB`
  - same-gender keep `+1.2233 dB`
  - hard-present keep `+0.8403 dB`
  - hard-present artifact proxy `+1.6793 dB`
  - `tradeoff gate = pass`
  - `0007`
    - overlap-local：
      - `better_retention_minus_speech_leak = v111`
      - `better_retention_minus_total_leak = v81`
      - `more_artifact_proxy_heavy = v111`
    - whole：
      - `better_retention_minus_leak = v81`
- relative `v109`
  - abstention `+0.4210 dB`
  - same-gender keep `+0.1478 dB`
  - hard-present keep `+0.1668 dB`
  - hard-present artifact proxy `+0.2389 dB`
  - near-real whole / local 基本全 `tie`
  - `0007`
    - overlap-local：
      - `better_retention_minus_speech_leak = tie`
      - `better_retention_minus_total_leak = tie`
      - `more_artifact_proxy_heavy = tie`
    - whole：
      - `better_retention_minus_leak = tie`
  - 导包：
    - relative `v81 / v109` 都是 `0 candidate sample`

裁决：

- `safe_but_no_meaningful_progress`

### 32. `v112`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v112_v109_overlap_cancel_splitpath_0007like_v1_ft1`

结果：

- 首个最小 split-path pilot：
  - 初始化：
    - `v109`
  - 只新增并训练：
    - `branch_overlap_cancel_head`
  - 同时保留：
    - `loss_use_branch_prerefine_as_primary_prediction = true`
  - 含义：
    - `branch_base(v109)` 保持主输出
    - `overlap_cancel_head` 只在 `speech_only overlap` 子域承担额外 suppress
- selector 激活：
  - train
    - `overlap_cancel = 38 / 135`
    - `branch_protect = 3 / 135`
  - val
    - `overlap_cancel = 12 / 40`
    - `branch_protect = 3 / 40`
- relative `v81`
  - abstention `+2.6823 dB`
  - same-gender keep `+1.1142 dB`
  - hard-present keep `+0.7098 dB`
  - hard-present artifact proxy `+1.4480 dB`
  - `tradeoff gate = pass`
  - `0007`
    - overlap-local：
      - `better_retention_minus_speech_leak = tie`
      - `better_retention_minus_total_leak = v81`
      - `more_artifact_proxy_heavy = v112`
- relative `v109`
  - abstention `+0.0893 dB`
  - same-gender keep `+0.0386 dB`
  - hard-present keep `+0.0364 dB`
  - hard-present artifact proxy `+0.0076 dB`
  - near-real whole 基本全 `tie`
  - `0007`
    - overlap-local：
      - `more_speech_interference_leaky = v112`
      - `better_retention_minus_speech_leak = v109`
      - `more_artifact_proxy_heavy = tie`
  - relative `v81 / v109`
    - `export_ab_listening_pack = 0 candidate sample`

裁决：

- `split_path_safe_but_no_frontier_gain`

### 33. `v113`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v113_v109_overlap_refine_preservebypass_0007like_selfanchor_v1_ft2`

结果：

- 首个 frozen-base residual-source refiner preserve/bypass pilot：
  - 初始化：
    - `v109`
  - teacher：
    - `v109`
  - 只新增并训练：
    - `branch_overlap_refine_head`
  - 同时保留：
    - `loss_use_branch_prerefine_as_primary_prediction = true`
  - 并设置：
    - `branch_overlap_refine_max_delta = 0.08`
    - `branch_overlap_refine_gate_mode = complement`
    - `branch_overlap_refine_source_mode = residual`
  - 含义：
    - `branch_base(v109)` 保持主输出
    - refiner 只在 gate-complement 子域对 `residual` source 做小幅 preserve/bypass 风格修正
- 首个 `ft1` 试跑不计入结论：
  - 原因是 selector 未显式带入 CLI，
  - paired `0007-like` 子域没有真正激活；
  - 有效 run 以 `ft2` 为准
- selector 激活：
  - train
    - `reconstruction_extra = 63 / 108`
    - `overlap_interference_extra = 3 / 108`
    - `branch_protect = 3 / 108`
    - `branch_protect_teacher = 3 / 108`
  - val
    - `reconstruction_extra = 0 / 39`
    - `overlap_interference_extra = 2 / 39`
    - `branch_protect = 3 / 39`
    - `branch_protect_teacher = 3 / 39`
- relative `v81`
  - abstention `+3.6476 dB`
  - same-gender keep `+1.6197 dB`
  - hard-present keep `+1.2724 dB`
  - hard-present artifact proxy `+1.7747 dB`
  - `tradeoff gate = pass`
  - `0007`
    - whole-utterance：
      - `better_retention_minus_leak = v113`
    - overlap-local：
      - `better_retention_minus_speech_leak = v81`
      - `better_retention_minus_total_leak = tie`
      - `more_artifact_proxy_heavy = v113`
- relative `v109`
  - abstention `+1.0546 dB`
  - same-gender keep `+0.5442 dB`
  - hard-present keep `+0.5989 dB`
  - hard-present artifact proxy `+0.3343 dB`
  - `tradeoff gate = pass`
  - `0007`
    - whole-utterance：
      - `better_retention_minus_leak = v113`
    - overlap-local：
      - `more_speech_interference_leaky = v113`
      - `better_retention_minus_speech_leak = v109`
      - `better_retention_minus_total_leak = v113`
      - `more_artifact_proxy_heavy = tie`
- bandwidth / transients：
  - relative `v81`
    - `narrower_candidate_counts = tie:4`
    - `more_transient_lossy_candidate_counts = tie:4`
  - relative `v109`
    - `narrower_candidate_counts = tie:4`
    - `more_transient_lossy_candidate_counts = tie:3, v113:1`
    - 唯一坏点是：
      - `near_real_0009`
- relative `v81 / v109`
  - `export_ab_listening_pack = 0 candidate sample`

裁决：

- `first_objective_positive_preservebypass_hit_but_not_listening_candidate`

### 34. `v114`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v114_v113_overlap_refine_preservebypass_0007like_localpush_v1_ft1`

结果：

- `v113` 的最小 local-push follow-up：
  - 初始化：
    - `v113 ft2`
  - teacher：
    - `v109`
  - 继续只训练：
    - `branch_overlap_refine_head`
  - 结构与 selector 命中保持不变：
    - train `reconstruction_extra / overlap_interference_extra / branch_protect / branch_protect_teacher = 63 / 3 / 3 / 3`
    - val `0 / 2 / 3 / 3`
  - 唯一主动改动：
    - `loss_overlap_interference_extra_weight`
      - `0.04 -> 0.05`
- relative `v113`
  - abstention `+0.6524 dB`
  - same-gender keep `+0.3698 dB`
  - hard-present keep `+0.4298 dB`
  - hard-present artifact proxy `+0.2396 dB`
  - whole-utterance：
    - `more_interference_leaky = v113` on `2 / 4`
    - `better_retention_minus_leak = v114` on `1 / 4`
    - `0007`
      - `better_retention_minus_leak = v114`
      - `delta_interference_capture_db = -1.8998 dB`
      - `delta_retention_minus_leak_db = +1.8643 dB`
  - overlap-local：
    - `more_speech_interference_leaky = tie:1, v113:1, v114:2`
    - `better_retention_minus_speech_leak = tie:2, v113:1, not_applicable:1`
    - `more_artifact_proxy_heavy = tie:4`
    - `0007`
      - `more_speech_interference_leaky = v114`
      - `better_retention_minus_speech_leak = v113`
      - `better_retention_minus_total_leak = tie`
      - `more_artifact_proxy_heavy = tie`
      - `delta_speech_interference_capture_db = +6.7240 dB`
      - `delta_retention_minus_speech_leak_db = -6.7384 dB`
      - `delta_retention_minus_total_leak_db = +0.4852 dB`
- bandwidth / transients：
  - relative `v113`
    - `narrower_candidate_counts = tie:4`
    - `more_transient_lossy_candidate_counts = tie:2, v113:2`

裁决：

- `whole_positive_but_local_speech_leak_regressed_vs_v113`

### 35. `v115`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v115_v113_overlap_refine_preservebypass_hardlocal_selector_v1_ft1`

结果：

- `v113` 的 finer hardlocal selector follow-up：
  - 初始化：
    - `v113 ft2`
  - teacher：
    - `v109`
  - 继续只训练：
    - `branch_overlap_refine_head`
  - 结构与权重保持不变
  - 唯一主动改动：
    - `speech_only local leak` selector
      从原始 `0007-like` 6 条 proxy
      改成更大的 hardlocal plus-music 子池
  - selector 命中：
    - train `63 / 11 / 3 / 3`
    - val `0 / 3 / 3 / 3`
- relative `v113`
  - abstention `+0.4349 dB`
  - same-gender keep `+0.2292 dB`
  - hard-present keep `+0.2703 dB`
  - hard-present artifact proxy `+0.1544 dB`
  - whole-utterance：
    - `more_interference_leaky = v113` on `2 / 4`
    - `better_retention_minus_leak = v115` on `1 / 4`
    - `0007`
      - `better_retention_minus_leak = v115`
      - `delta_interference_capture_db = -2.1348 dB`
      - `delta_retention_minus_leak_db = +2.0775 dB`
  - overlap-local：
    - `more_speech_interference_leaky = tie:1, v113:1, v115:2`
    - `better_retention_minus_speech_leak = tie:2, v113:1, not_applicable:1`
    - `more_artifact_proxy_heavy = tie:4`
    - `0007`
      - `more_speech_interference_leaky = v115`
      - `better_retention_minus_speech_leak = v113`
      - `delta_speech_interference_capture_db = +9.2226 dB`
      - `delta_retention_minus_speech_leak_db = -9.2569 dB`

裁决：

- `finer_selector_still_optimizes_whole_or_total_not_local_speech_leak`

### 36. `v116`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v116_v113_overlap_refine_preservebypass_0007like_predproj_v1_ft1`

结果：

- `v113` 的 overlap local pred-projection follow-up：
  - 初始化：
    - `v113 ft2`
  - teacher：
    - `v109`
  - 继续只训练：
    - `branch_overlap_refine_head`
  - 结构、selector 与权重保持不变
  - 唯一主动改动：
    - `loss_overlap_interference_extra_mode`
      - `residual_projection_ratio -> prediction_projection_ratio`
  - selector 命中保持与 `v113` 一致：
    - train `63 / 3 / 3 / 3`
    - val `0 / 2 / 3 / 3`
- relative `v113`
  - abstention `+0.8478 dB`
  - same-gender keep `+0.4624 dB`
  - hard-present keep `+0.5265 dB`
  - hard-present artifact proxy `+0.2962 dB`
  - whole-utterance：
    - `more_interference_leaky = v113` on `2 / 4`
    - `better_retention_minus_leak = v116` on `1 / 4`
    - `0007`
      - `better_retention_minus_leak = v116`
      - `delta_interference_capture_db = -2.3450 dB`
      - `delta_retention_minus_leak_db = +2.2477 dB`
  - overlap-local：
    - `more_speech_interference_leaky = tie:1, v113:1, v116:2`
    - `better_retention_minus_speech_leak = tie:1, v116:1, v113:1, not_applicable:1`
    - `more_artifact_proxy_heavy = tie:4`
    - `0007`
      - `more_speech_interference_leaky = v116`
      - `better_retention_minus_speech_leak = v113`
      - `delta_speech_interference_capture_db = +9.2733 dB`
      - `delta_retention_minus_speech_leak_db = -9.3285 dB`
  - bandwidth / transients：
    - `narrower_candidate_counts = tie:4`
    - `more_transient_lossy_candidate_counts = tie:3, v113:1`

裁决：

- `predproj_semantics_still_fails_0007_local_speech_leak`

### 37. `v117`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v117_v113_overlap_refine_preservebypass_0007like_gateguided_v1_ft1`

结果：

- `v113` 的 gate-guided integration follow-up：
  - 初始化：
    - `v113 ft2`
  - teacher：
    - `v109`
  - 继续只训练：
    - `branch_overlap_refine_head`
  - 结构、selector 与权重保持不变
  - 唯一主动改动：
    - `branch_overlap_refine_gate_mode`
      - `complement -> gate`
  - selector 命中保持与 `v113` 一致：
    - train `63 / 3 / 3 / 3`
    - val `0 / 2 / 3 / 3`
- relative `v113`
  - abstention `+2.9297 dB`
  - same-gender keep `+2.4865 dB`
  - hard-present keep `+2.0962 dB`
  - hard-present artifact proxy `+1.8984 dB`
  - whole-utterance：
    - `more_interference_leaky = v113` on `4 / 4`
    - `better_retention_minus_leak = v117` on `3 / 4`
    - `0007`
      - `better_source_retention = v113`
      - `better_retention_minus_leak = v117`
      - `delta_target_capture_db = -0.8580 dB`
      - `delta_interference_capture_db = -7.0435 dB`
      - `delta_retention_minus_leak_db = +6.1855 dB`
  - overlap-local：
    - `better_source_retention = v113:2, tie:1, not_applicable:1`
    - `more_speech_interference_leaky = v113:2, v117:2`
    - `more_total_interference_leaky = v113:3, v117:1`
    - `better_retention_minus_speech_leak = v117:2, v113:1, not_applicable:1`
    - `better_retention_minus_total_leak = v117:3, not_applicable:1`
    - `more_artifact_proxy_heavy = v117:2, tie:2`
    - `0007`
      - `more_speech_interference_leaky = v117`
      - `better_retention_minus_speech_leak = v113`
      - `better_retention_minus_total_leak = v117`
      - `more_artifact_proxy_heavy = v117`
      - `delta_speech_interference_capture_db = +10.6017 dB`
      - `delta_retention_minus_speech_leak_db = -11.3125 dB`
    - `0009`
      - `more_speech_interference_leaky = v117`
      - `delta_speech_interference_capture_db = +10.9446 dB`
  - bandwidth / transients：
    - `narrower_candidate_counts = tie:4`
    - `more_transient_lossy_candidate_counts = v117:2, tie:1, v113:1`

裁决：

- `gateguided_refiner_overpushes_total_leak_but_regresses_0007_local_speech_leak`

### 38. `v118`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v118_v109_overlap_dual_controller_floor_0007like_v1_ft1`

结果：

- 首个 dual-controller floor pilot：
  - 初始化：
    - `v109`
  - teacher：
    - `v109`
  - 新增最小 controller 参数：
    - `branch_overlap_dual_decoder_gate_floor = 0.75`
  - 同时设置：
    - `branch_overlap_dual_decoder_gate_mode = gate`
    - `branch_overlap_dual_decoder_source_mode = residual`
    - `branch_overlap_dual_decoder_max_delta = 0.08`
    - `branch_overlap_dual_decoder_max_blend = 0.15`
  - 只训练：
    - `branch_overlap_dual_decoder_temporal_model`
    - `branch_overlap_dual_decoder_head`
- selector 命中：
  - train
    - `overlap_cancel = 3 / 108`
    - `overlap_dual = 3 / 108`
    - `branch_protect = 3 / 108`
    - `branch_protect_teacher = 3 / 108`
  - val
    - `overlap_cancel = 3 / 39`
    - `overlap_dual = 3 / 39`
    - `branch_protect = 3 / 39`
    - `branch_protect_teacher = 3 / 39`
- relative `v109`
  - abstention `-1.7880 dB`
  - same-gender keep `-2.4133 dB`
  - hard-present keep `-1.1600 dB`
  - hard-present artifact proxy `-2.1929 dB`
  - whole-utterance：
    - `better_source_retention = v118:3, not_applicable:1`
    - `more_interference_leaky = v118:4`
    - `better_retention_minus_leak = tie:2, v109:1, not_applicable:1`
    - `gate_near_real_tradeoff = fail`
  - `0007`
    - whole：
      - `better_source_retention = v118`
      - `more_interference_leaky = v118`
      - `better_retention_minus_leak = v109`
      - `delta_interference_capture_db = +12.9325 dB`
    - overlap-local：
      - `more_speech_interference_leaky = v118`
      - `more_total_interference_leaky = v118`
      - `better_retention_minus_speech_leak = v118`
      - `better_retention_minus_total_leak = v109`
      - `delta_total_interference_capture_db = +13.4918 dB`
  - bandwidth / transients：
    - `narrower_candidate_counts = tie:4`
    - `more_transient_lossy_candidate_counts = tie:4`

裁决：

- `dual_controller_floor_stops_phone_artifact_but_not_direct_output_leak_drift`

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
- speech-only overlap selector 前置条件：
  - 不需要新 manifest
  - 直接复用现有 synthetic manifest
  - 通过以下派生字段筛纯 speech overlap：
    - `interference_profile`
    - `has_speech_interference`
    - `has_music_interference`
    - `interference_layer_count`
- local explicit speech-leak proxy：
  - `data/synthetic/train_manifest_local_speech_leak_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_proxy_v1.jsonl`
  - `data/synthetic/train_manifest_speech_leak_local_aware_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_speech_leak_local_aware_bundle_v1.jsonl`

### 验收侧

- near-real 主验收：
  - `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`
- near-real phone-artifact guardrail：
  - `data/references/real_eval_manifest_bandwidth_guardrail_v1.jsonl`
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
  - `scripts/eval/analyze_listening_pack_transients.py`
  - `scripts/eval/gate_near_real_phone_artifact.py`
- overlap-local near-real 诊断：
  - `reports/eval/overlap_local_benchmark_manifest_residual_speech_leak_floor_v1.jsonl`
  - `scripts/eval/build_overlap_local_benchmark_manifest.py`
  - `scripts/eval/analyze_overlap_local_benchmark.py`
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
- `v93 / v94 / v95` 也已完成当前轮探索，当前结论是：
  - auxiliary-only 线暂不继续做小步 sweep
  - `v95` 不升格
  - `v81` 继续作为研究基座
- `v96 / v97 / v98` 也已完成当前轮探索，当前结论是：
  - `phase_preserve` 代码路径保留
  - 但这条 overlap-canceller 线当前不构成新的前沿
  - `v98` 不进入 focused 听审
- `v81 vs v88 / v95 / v100 / v101` 已完成 overlap-local 回放，当前结论是：
  - localized `speech leak / retention-minus-speech-leak / artifact proxy`
    比 whole-utterance leak tradeoff 更接近已知听审裁决；
  - 这条 benchmark 现已成为后续 overlap frontier 的固定诊断链；
- `speech-only overlap` 的 selector 前置条件已完成，当前结论是：
  - `speech_only`
    可稳定筛出：
    - `target_clean_speech`
    - `target_hard_speech`
  - 不会再把：
    - `target_clean_plus_music`
    - `target_hard_plus_music`
    误选进来；
- 不再继续做 `v83` 式宽触发 refiner，也不做 `v84` 附近小权重 sweep；
- 不再继续做 `v85 / v86` 同家族小步 sweep；
- 不再继续做 `v87 / v88` 同家族小步 sweep；
- 不再继续做 `v89` 同家族小步 sweep；
- 不再继续做 `v90 / v91` 同家族小步 sweep；
- 不再继续做 `v93 / v94 / v95` 同家族小步 sweep；
- 不再继续做 `v98` 附近的 `phase_preserve` overlap-canceller ratio sweep；
- 若后续继续推进，默认应切到：
  - 新的机制子题
  - 并优先显式处理 `hard-present artifact risk`
  - 而不是继续让当前 auxiliary-only / direct dual path / phase-preserve overlap-canceller 家族扩树
- 当前最直接的下一步变成：
  - 基于 `v81`
  - 配一个 `speech_only local residual suppressor` 首个 pilot
  - 再用四条固定验收 + overlap-local benchmark 回放
- `v102` 首个 `speech_only local residual suppressor` pilot 已完成：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v102_v81_overlap_purify_v2_speechonly_ft1`
  - synthetic relative `v81` 仍保持三条主验收正收益
  - near-real `overall_pass = true`
  - 但 `0007` 仍未自动修好，`0009` 也未形成明确收益
  - 当前不自动升格，先走 focused 听审
- 当前新的默认下一步变成：
  - `v81 vs v102` focused 听审
  - 重点看：
    - `0003`
    - `0006`
    - `0007`
    - `0009`
  - 而不是立刻继续做 `v103` sweep
- `v103` plus-music teacher veto pilot 已完成：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v103_v102_speechonly_plusmusic_teacher_veto_ft1`
  - 相对 `v81`：
    - synthetic 三条主验收继续更强
    - near-real whole-utterance `overall_pass = true`
    - `0009` absent suppression 也更好
  - 但 overlap-local 仍显示：
    - `0003 / 0006`
      - `retention-minus-speech-leak = v103`
    - `0007`
      - `better_retention_minus_speech_leak = v81`
      - `more_artifact_proxy_heavy = v103`
  - blind `v81 vs v103` focused 听审已完成：
    - `v81 = 4`
    - `v103 = 0`
    - `tie = 0`
    - 四条样本全部因为 `v103` artifact 更重而偏向 `v81`
  - 当前正式裁决：
    - `v103` 不升格
    - 不继续做 `v103+` 同结构小步 sweep
    - 这条家族先收口，转去新的 artifact-first 机制题
- `hard_present_artifact_proxy_v1` 已完成物化：
  - `data/synthetic/train_manifest_hard_present_artifact_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_hard_present_artifact_proxy_v1.jsonl`
  - 口径：
    - `speech_plus_music`
    - `layer_count = 2`
    - `target_full`
    - weak-target
    - mid/high transient-share hard-present overlap
  - `v81 / v102 / v103` 回放结果：
    - train violation
      - `v81 = 0`
      - `v102 = 1`
      - `v103 = 2`
    - val violation
      - `v81 = 0`
      - `v102 = 0`
      - `v103 = 2`
  - 当前新的默认下一步：
    - 基于 `v81`
    - 设计首个 artifact-aware pilot
    - 固定同时回放五条验收：
      - `real_eval_manifest_residual_speech_leak_floor_v1`
      - `same_gender_present_keep_guardrail_v1`
      - `hard_present_gate_keep_guardrail_v1`
      - `hard_present_artifact_proxy_v1`
      - `overlap_abstention_proxy_v4_audibility_v1`
- 首轮 artifact-aware pilots 已完成：
  - `v104 = artifactaware_anchor`
    - 比 `v103` 安全
    - 但 near-real `0007` 没有形成局部 rescue
    - 不继续
  - `v105 = artifactguard`
    - synthetic 四条固定验收都排前
    - `hard_present_artifact_proxy_v1` 也排前
    - 但 near-real `0003 / 0007` target capture 同时回退
    - overlap-local `0007` 仍是 `v81` 更好，且 `v105` artifact 更重
    - 判定为 proxy 过拟合，不导听审
- 当前默认下一步再次更新为：
  - 收口 `v104 / v105` 这轮粗粒度 artifact-aware pilot
  - 不继续 `v104+ / v105+` 小步权重 sweep
  - 基于 `v81` 设计更外科式的 local artifact veto / backstop
  - 重点只打 `0007` 风格局部 artifact，而不是继续扩大整条 proxy 的全局 guard weight
- `v106 = local_artifact_veto`
  - checkpoint：
    - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v106_v81_overlap_purify_v4_local_artifact_veto_ft1`
  - 数据：
    - `hard_present_artifact_local_proxy_v1`
    - `artifact_local_aware_bundle_v1`
  - 结果：
    - synthetic 上是一个中间解，不再像 `v105` 那样 proxy 过拟合
    - `overlap_abstention_proxy_v4_audibility_v1` 排第一
    - near-real whole-utterance 上：
      - `0007` target capture 优于 `v81`
      - `0009` absent suppression 回退
    - overlap-local 上：
      - `0003` 更偏向 `v106`
      - `0006` 接近 tie
      - `0007` artifact 与 `v81` 打平，但 speech leak 仍更重
  - 裁决：
    - focused blind 听审已完成，结果为 `tie = 4`
    - 四条样本都无可感知差异
    - `0007` 核心痛点未出现主观改善
    - 不做 `v106+`
- 当前默认下一步再次更新为：
  - 收口 `v106` 这一版 local artifact veto
  - 暂停 `v106+` 小步权重 sweep
  - 如果 `0007` 仍要继续，则把下轮 local veto 改为显式 speech-leak backstop，而不再只做 teacher-overlap 对齐
- `v107 = local explicit speech-leak backstop`
  - checkpoint：
    - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v107_v81_overlap_purify_v5_local_speech_leak_bundle_v1_ft1`
  - 数据：
    - `local_speech_leak_proxy_v1`
    - `speech_leak_local_aware_bundle_v1`
  - 结果：
    - synthetic 三条固定验收 relative `v81` 全部继续更强
    - near-real whole-utterance `overall_pass = true`
    - overlap-local `0003 / 0006` 转正
    - 但 `0007` 仍是：
      - `better_retention_minus_speech_leak = v81`
      - `more_artifact_proxy_heavy = v107`
  - 裁决：
    - automatic 已证明“显式 local speech-leak supervision”是有效方向
    - 但 `0007` 仍未自动修好
    - blind `v81 vs v107` 结果为：
      - `v81 = 4`
      - `v107 = 0`
      - `tie = 0`
    - 四条样本共同原因都是：
      - `v107` artifact 更重
    - 当前不直接开 `v107+`
- 当前默认下一步再次更新为：
  - `v107` 这条 family 先收口
  - `v108` 这条 family 也先收口
  - `v109` 已完成自动验收，并已通过：
    - `near-real tradeoff gate`
    - `phone_artifact_gate_v1`
  - 不继续 `v107+ / v108+ / v109+` 小步 sweep
  - `phone_artifact_gate_v1` 已完成物化：
    - 基于 `real_eval_manifest_bandwidth_guardrail_v1`
    - 纯 bandwidth narrowing 不足以解释 `v103 / v107` 的主观失败
    - `bandwidth + transient-loss` 组合 gate 已能稳定抓住这两组已知失败 pack
  - `v108` 已进一步证明：
    - 宽打到整个 `local_speech_leak_proxy_v1` 子域的 preservation / teacher backstop 会过度回缩
- `v109` 已进一步证明：
    - 把 backstop 缩到 `0007-like` 子域，
    - 可以避开 `v108` 式全局回缩，
    - 并保留相对 `v107` 的 artifact relief
  - blind `v81 vs v109` 已完成，结果为：
    - `tie = 3`
    - `v81 = 1`
    - `v109 = 0`
  - 唯一非 tie 样本仍是：
    - `0007`
    - 原因：
      - `less_artifact`
  - 当前默认下一步改为：
    - 收口 `v109`
    - 不继续 `v109+` 小步 sweep
    - 若继续 `0007` 子题，
      直接回到 retention / artifact 拉扯本身重新拆约束
- `v110` 已进一步证明：
    - paired dual-view 即使精确落在同一批 `0007-like` base id 上，
    - 也仍可能把 `0007` 往“局部 leak 更小，但 whole tradeoff 更差”的方向继续推
  - 当前默认下一步再次更新为：
    - 收口 `v110`
    - 不继续 `v110+`
    - 若继续 `0007` 子题，
      优先改做更保守的 self-anchor 约束，
      先保住 `v109` 的 whole-tradeoff，再看局部 leak 是否还能改善
- `v111` 已进一步证明：
    - self-anchor 确实能把 `v110` 的过抑制收回 safe 边界，
    - 但也会把这条 family 快速收成 near-no-op
  - 当前默认下一步再次更新为：
    - 收口 `v110 / v111 / v112`
    - 不继续 `v110+ / v111+ / v112+`
    - 若继续 `0007` 子题，
      这组 paired dual-view / overlap-cancel split-path family 应视为已触边，
      `v112` 又进一步证明：
      即使把 suppress 路径从主路径里拆开，
      当前 multiplicative `overlap_cancel_head` 表示也只会收成 safe / near-no-op；
      下一步改做新的约束、表示或 integration 机制
- `v113` 已进一步证明：
  - frozen-base residual-source refiner 这条 preserve/bypass 机制已经能相对 `v109` 真正前进，
  - `0007` 的 whole-tradeoff 也第一次被自动推成正向，
  - 但 overlap-local `speech_only` leak 仍未转正，且还没有 listening-pack candidate
  - 当前默认下一步再次更新为：
    - 收口 `v113`
    - preserve/bypass family 保持活跃
    - 不回退到旧 `overlap_cancel` family
    - 若继续 `0007` 子题，
      下一轮直接围绕：
      保住 `v113` 的 whole-tradeoff 正向，
      同时继续压 overlap-local `speech_only` leak
- `v114 / v115 / v116 / v117` 已进一步共同证明：
  - 当前 `branch_overlap_refine_head` 这条 preserve/bypass family
    确实不是 near-no-op；
  - 但不管改：
    - selector
    - overlap local loss mode
    - gate integration
    主优化出口仍然优先落在：
    - whole-tradeoff
    - total-leak
    而不是稳定解决：
    - `0007` overlap-local `speech_only` leak
    - 与之绑定的 local artifact / absent local suppression
  - 当前默认下一步再次更新为：
    - 收口 `v113 / v114 / v115 / v116 / v117`
    - preserve/bypass family 保持活跃
    - 不回退到旧 `overlap_cancel` family
    - 不继续当前 `branch_overlap_refine_head` 上的：
      - selector-only
      - loss-mode-only
      - gate-mode-only
      sweep
    - 若继续 `0007` 子题，
      直接切到新的局部表示 / controller 机制，
      或显式分开的 target-present / target-absent local 控制语义
- `v118` 已进一步证明：
  - direct-output dual decoder 即使补上：
    - `gate floor`
    - 小 `max_blend`
    也只能止住 phone-artifact；
  - 不能修掉：
    - `source retention ↑`
    - `interference leak ↑`
    同时发生的 integration 漂移；
  - 因而 `overlap dual decoder` 仍应保留为：
    - `failed_as_direct_output_path`
  - 当前默认下一步再次更新为：
    - 收口 `v118`
    - 不继续 `v118+`
    - 若继续 dual 语义，
      只能改做：
      - auxiliary-only
      - controller-only
      - 或其它不直接接管 final output 的 integration
- `v120` 已进一步证明：
  - 显式 split target-present / target-absent local control
    这条语义不是 near-no-op；
  - `v113 + present-only refine head + current_residual source`
    relative `v113`：
    - synthetic 四条固定验收全绿
    - whole near-real tradeoff gate 通过
    - `near_real_0006` overlap-local 已继续前进；
  - 但它仍没有把真正卡住的：
    - `near_real_0007` local `speech_only` leak
    - `near_real_0009` absent local suppression
    解掉；
- `v121` 已进一步证明：
  - hard present activation floor 的方向本身是对的，
    因为它确实动到了：
    - `0007` local `speech_only` leak
    - `0009` absent local suppression
  - 但 hard floor 本身过硬，
    会把 synthetic 与 whole-tradeoff 一起拉坏；
  - 因此不继续 `hard floor` family；
- `v122` 已进一步证明：
  - soft `gate^2` activation shaping 才是更对的 continuation；
  - relative `v120`：
    - synthetic 四条固定验收重新全绿
    - whole near-real tradeoff gate 通过
    - overlap-local total leak 继续全样本下降
    - `0006 / 0009` local speech leak 继续改善；
  - 但 `0007` local `speech_only` leak 仍未转正；
- `v123` 已进一步证明：
  - hardlocal `speech_only` 子域做额外抑制
    不是这条线的答案；
  - relative `v122` 虽然 synthetic / whole 都没坏，
    但 `0007 / 0009` 的局部 speech leak 一起回退；
- `v124 / v125` 已一起收口 soft gate power 轴：
  - `v124 = gate_power 3.0`
    已重新伤到 fixed synthetic guardrail，直接废弃；
  - `v125 = gate_power 2.5`
    则 relative `v122`：
    - four fixed synthetic checks 全部小幅正向
    - whole near-real tradeoff gate 继续通过
    - `0009` absent local speech leak 明显下降
    - `0007` local `speech_only / total leak` 也继续下降；
  - blind listening pack：
    - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v122_vs_v125_blind`
    已完成 focused 听审，
    结果为：
    - `tie = 4`
    - `v122 = 0`
    - `v125 = 0`
  - pack 第 1 条 `near_real_0003`
    留下备注：
    - `B样本有误差级别的伪影高于A。`
  - 结论：
    - `v125` 是当前这条轴上最好的 automatic continuation；
    - 但主观上仍未形成可听胜出，
      不升格；
- `v126 = v125 + present-head complement-ratio veto 0.5`
  - relative `v125`：
    - four fixed synthetic checks 继续全线微正
    - whole near-real：
      - `more_interference_leaky = tie:3, v125:1`
      - `better_retention_minus_leak = tie:2, v126:1, not_applicable:1`
      - 关键收益集中在：
        - `near_real_0007`
          - `delta_interference_capture_db = -1.4286 dB`
          - `delta_retention_minus_leak_db = +1.3823 dB`
    - overlap-local：
      - `more_total_interference_leaky = tie:3, v125:1`
      - 但 `more_speech_interference_leaky = tie:4`
      - `0007` 只把 total leak 再往前推，
        没把 speech-only local leak 推成明确正向
      - `0009` absent local suppression 也没有继续前进
  - 结论：
    - `v126` 接替 `v125`
      成为当前最佳 split-local-control automatic continuation
    - 但仍不进 focused 听审；
- `v127 = v126 + true absent anchor bundle + absent_extra 0.02`
  - relative `v126`：
    - 首次改用真正带 absent interval 的 rows，
      不再拿历史 absent proxy allowlist
      充当真实 absent 资产
    - `absent_extra` selector 真正命中：
      - train `95 / 203`
      - val `24 / 63`
    - four fixed synthetic checks 全线转负：
      - abstention `-0.1881 dB`
      - same-gender keep `-0.1060 dB`
      - hard-present keep `-0.1184 dB`
      - artifact proxy `-0.0378 dB`
    - whole near-real：
      - `more_interference_leaky = v127:3, tie:1`
      - `better_retention_minus_leak = v126:2, tie:1, not_applicable:1`
      - `0007 / 0003 / 0006`
        的 overall leak 都更差
    - overlap-local：
      - `0009` absent local leak
        大幅下降：
        - `delta_speech_interference_capture_db = -9.3758 dB`
      - 但 `0007` 只在 speech-only local leak 上正向，
        total leak / overall tradeoff 反而更差
  - 结论：
    - true absent supervision 本体有效，
      但当前 present-head-only routing 错位；
    - `v127` 直接收口，
      不导听审，
      不继续做同构 weight sweep；
- `v128 = v126 + true absent anchor bundle + absent_extra 0.02 + complement-head only routing`
  - relative `v126`：
    - 四条 fixed synthetic checks
      重新全绿：
      - abstention `+0.2733 dB`
      - same-gender keep `+0.1355 dB`
      - hard-present keep `+0.2477 dB`
      - artifact proxy `+0.1029 dB`
    - 说明 true absent supervision
      的核心问题在 routing，
      不在 supervision 本体
    - 但 whole near-real 仍不过关：
      - `more_interference_leaky = v128:2, tie:2`
      - `0007`
        - `delta_interference_capture_db = +8.5356 dB`
      - `0009`
        - `delta_interference_capture_db = +1.5064 dB`
  - 结论：
    - `v128` 保留为 decoupled-routing 机制证据点，
      不升格
- `v129 = v128 + absent_extra 0.01`
  - relative `v128`：
    - fixed synthetic checks 继续微正
    - `0007`
      - whole `delta_interference_capture_db = -6.2120 dB`
      - local `delta_speech_interference_capture_db = -2.4872 dB`
    - 但 `0009`
      - whole `delta_interference_capture_db = +0.2374 dB`
      - local `delta_speech_interference_capture_db = +4.1453 dB`
  - 结论：
    - `v129` 接替 `v128`
      成为 decoupled true-absent 支线最佳 continuation，
      但仍未越过 `v126`
- `v130 = v129 + complement-head gate_power 2.0`
  - relative `v129`：
    - 四条 fixed synthetic checks
      全线明显转负：
      - abstention `-0.3591 dB`
      - same-gender keep `-0.2566 dB`
      - hard-present keep `-0.3005 dB`
      - artifact proxy `-0.1715 dB`
  - 结论：
    - complement-head `gate_power / gate_floor`
      shaping 轴直接收口，
      不补 near-real；
- `v131 = v126 + true-absent dual-controller absent-mix v1`
  - relative `v126`：
    - 训练 selector 命中有效：
      - `overlap_dual = 95 / 203` train
      - `overlap_dual = 24 / 63` val
    - 四条 fixed synthetic checks
      全线明显转负：
      - abstention `-3.0643 dB`
      - same-gender keep `-2.3636 dB`
      - hard-present keep `-1.9456 dB`
      - artifact proxy `-1.7674 dB`
  - 结论：
    - 即便把 true-absent supervision
      打到 dual residual/controller branch，
      只要最终仍通过
      `gate_controller`
      回灌主输出路由，
      也会系统性伤 guardrail；
    - `v131` 直接 reject，
      不补 near-real；
- `v132 = v126 + true-absent dual current-output absent-mix v1`
  - relative `v126`：
    - 训练 selector 命中有效：
      - `overlap_dual = 95 / 203` train
      - `overlap_dual = 24 / 63` val
    - 四条 fixed synthetic checks
      全线明显转负：
      - abstention `-6.6014 dB`
      - same-gender keep `-1.3396 dB`
      - hard-present keep `-2.3761 dB`
      - artifact proxy `-2.4415 dB`
  - 结论：
    - 即便把 dual absent-supervised branch
      改成 `current_output` 局部 blend，
      只要它仍直接改 final output，
      也会系统性伤 guardrail；
    - `v132` 直接 reject，
      不补 near-real；
- `v133 = v126 + true-absent gate-absent 0.04 v1` 初版 scratch
  - relative `v126`：
    - 不计入正式实验结论；
    - 初版 `gate_absent_sample_weights`
      误接到了
      `absent_union_sample_weights`
    - 在这套 run
      没有显式 absent selector
      的前提下，
      `train / val_gate_absent_mean`
      四个 epoch 全是 `0.0`
  - 结论：
    - 这是无效 scratch，
      不是负向证据也不是正向证据；
    - 修完 sample-weight 接线后，
      正式结果转入 `v134`
- `v134 = v126 + true-absent gate-absent 0.04 v1`
  - relative `v126`：
    - `gate_absent` 真实生效，
      不是 no-op：
      - `train_gate_absent_mean = 0.4410 -> 0.1905`
      - `val_gate_absent_mean = 0.2315 -> 0.1255`
    - 但四条 fixed synthetic checks
      仍全线转负：
      - abstention `-2.2058 dB`
      - same-gender keep `-0.9064 dB`
      - hard-present keep `-1.7109 dB`
      - artifact proxy `-2.1404 dB`
  - 结论：
    - gate-only absent supervision
      本体有效，
      但 current gate head
      仍会系统性伤 guardrail；
    - `v134` 直接 reject，
      不补 near-real；
- `v135 = v126 + true-absent gate-absent 0.02 + gate-keep 0.02`
  - relative `v126`：
    - 给 `v134`
      同一路线补 sparse
      `branch_protect` keep anchors：
      - selector 命中 `3 / 203` train
      - selector 命中 `3 / 63` val
    - `gate_absent / gate_keep`
      都真实生效：
      - `val_gate_absent_mean = 0.2150 -> 0.1148`
      - `val_gate_keep_mean = 0.3225 -> 0.3501`
    - 但四条 fixed synthetic checks
      还是全线转负，
      而且比 `v134` 更差：
      - abstention `-2.2891 dB`
      - same-gender keep `-1.0121 dB`
      - hard-present keep `-1.8372 dB`
      - artifact proxy `-2.5225 dB`
  - 结论：
    - `gate_absent + sparse gate_keep`
      也救不回 current gate head；
    - `v135` 直接 reject，
      不补 near-real；
- `v136 = v126 + true-absent auxiliary-only overlap-cancel absent-mix 0.02`
  - relative `v126`：
    - 首个不直接改 final output、
      改走
      `branch_overlap_cancel_head`
      `auxiliary_only`
      transfer 的 credible pilot
    - `overlap_cancel`
      selector 和 absent-mix loss
      都真实生效：
      - selector 命中 `95 / 203` train
      - selector 命中 `24 / 63` val
      - `val_overlap_cancel_absent_mix_l1 = 0.0522`
    - 四条 fixed synthetic checks
      仅轻微负向：
      - abstention `-0.1477 dB`
      - same-gender keep `-0.0324 dB`
      - hard-present keep `-0.0211 dB`
      - artifact proxy `-0.1126 dB`
    - overlap-local
      首次给出可信局部正证据：
      - `near_real_0009`
        absent local leak
        `-13.5689 dB`
      - `near_real_0007 speech_only`
        local leak
        `-1.7290 dB`
    - 但 whole near-real
      仍失败：
      - `more_interference_leaky = v136:3, tie:1`
      - `better_retention_minus_leak = v126:3, n/a:1`
      - `near_real_0007 total leak`
        仍转差
  - 结论：
    - `v136`
      是
      `auxiliary_only`
      true-absent indirect path
      的首个 credible evidence point；
    - 但它还不能升格 continuation，
      不出听审；
- `v137 = v136 + overlap_cancel_absent_mix_weight 0.01`
  - relative `v126`：
    - selector
      和 absent-mix loss
      仍真实生效，
      不是 no-op
    - 但四条 fixed synthetic checks
      比 `v136`
      全部更差：
      - abstention `-0.1718 dB`
      - same-gender keep `-0.0715 dB`
      - hard-present keep `-0.0347 dB`
      - artifact proxy `-0.2080 dB`
  - 结论：
    - `overlap_cancel_absent_mix_weight`
      的简单 reweight
      不能把这条机制
      拉回安全区；
    - `v137` 直接 reject，
      不补 near-real；
- `v138 = v126 + overlap-cancel total-leak 0007-like self-anchor blend05 v1`
  - relative `v126`：
    - 首个
      `head-only bounded subtract path`
      安全边界 probe
    - 四条 fixed synthetic checks
      近乎精确全 tie：
      - abstention `+0.0061 dB`
      - same-gender keep `+0.0027 dB`
      - hard-present keep `+0.0047 dB`
      - artifact proxy `+0.0023 dB`
    - whole / overlap-local
      也几乎全 tie，
      仅
      `near_real_0008`
      whole absent friend-only
      出现：
      - `delta_interference_capture_db = +1.3024 dB`
  - 结论：
    - `v138`
      是 safe / near-no-op reject，
      但保留为
      `head-only bounded subtract path`
      可以保持安全
      的证据点
- `v139 = v126 + split-selector auxcancel total-leak + absent-mix self-anchor v1`
  - relative `v126`：
    - 先把
      `overlap_cancel_waveform / target_projection`
      与
      `overlap_cancel_absent_mix`
      的 selector sample weights
      拆开
    - 四条 fixed synthetic checks
      仅轻微负向：
      - abstention `-0.0720 dB`
      - same-gender keep `-0.0702 dB`
      - hard-present keep `-0.0122 dB`
      - artifact proxy `-0.0565 dB`
    - local 侧给出真实正证据：
      - `0009`
        absent local
        `delta_speech_interference_capture_db = -24.4329 dB`
      - `0007 speech_only`
        local leak
        `delta_speech_interference_capture_db = -1.1327 dB`
    - 但 whole 与 total-leak
      同时转坏：
      - `more_interference_leaky = v139:4`
      - `0007`
        `delta_interference_capture_db = +6.3064 dB`
      - `0009`
        `delta_interference_capture_db = +1.4486 dB`
  - 结论：
    - split-selector 机制是真实的，
      但只要它仍共享当前
      `mask-head transfer`
      路径，
      就会把 whole leak
      和 `0007 total leak`
      推坏；
    - `v139` 直接 reject
- `v140 = v126 + head-only auxcancel hardlocaltotal absentmix self-anchor v1`
  - relative `v126`：
    - 只训练
      `branch_overlap_cancel_head`
      并保留 split selectors
    - 训练信号真实命中：
      - `overlap_cancel = 3 / 203` train，
        `3 / 63` val
      - `absent = 95 / 203` train，
        `24 / 63` val
      - `val_overlap_cancel_waveform_l1 = 0.0281501`
      - `val_overlap_cancel_absent_mix_l1 = 0.0522065`
    - 但四条 fixed synthetic checks
      全部精确 `0.0 dB`
  - 结论：
    - `v140`
      补出了明确边界：
      `head-only + auxiliary_only`
      在当前家族里
      是结构性 inference no-op
- `v141 = v126 + head-only split-selector subtract blend05 absentmix v1`
  - relative `v126`：
    - 相对 `v140`
      改成：
      - `apply_mode = subtract`
      - `delta_blend_mode = complement`
      - `max_blend = 0.5`
    - 四条 fixed synthetic checks
      全部正向：
      - abstention `+0.1037 dB`
      - same-gender keep `+0.1139 dB`
      - hard-present keep `+0.0121 dB`
      - artifact proxy `+0.0178 dB`
    - whole / local 的正证据：
      - `0009`
        whole absent
        `delta_interference_capture_db = -21.7825 dB`
      - `0003 / 0006`
        whole 都更干净
      - `0007`
        local total leak
        `delta_total_interference_capture_db = -19.5934 dB`
    - 但 absent-local
      与 speech-only
      同时翻坏：
      - `0009`
        local absent
        `delta_speech_interference_capture_db = +21.0921 dB`
      - `0007`
        local speech-only
        `delta_speech_interference_capture_db = +13.4400 dB`
  - 结论：
    - 同一个 direct-apply cancel head
      不能同时承载
      `present-total`
      与
      `absent-local`；
    - `v141`
      是 mixed mechanism-positive reject
- `v142 = v126 + head-only hardlocaltotal subtract blend05 v1`
  - relative `v126`：
    - 在 `v141`
      上完全移除 absent supervision
    - 四条 fixed synthetic checks
      给出这轮最干净的一组正向：
      - abstention `+0.1949 dB`
      - same-gender keep `+0.0894 dB`
      - hard-present keep `+0.0848 dB`
      - artifact proxy `+0.0696 dB`
    - whole 侧：
      - `0009`
        absent
        `delta_interference_capture_db = -5.1486 dB`
      - `0006`
        `delta_interference_capture_db = -1.1233 dB`
      - `0003`
        轻微正向
      - `0007`
        whole 仍更 leak：
        `delta_interference_capture_db = +3.4937 dB`
    - local 侧：
      - `0007`
        total leak
        `delta_total_interference_capture_db = -3.2201 dB`
      - `0006`
        speech / total leak
        都下降
      - 但
        `0007 speech_only`
        `+6.4977 dB`
      - 以及
        `0009 absent local`
        `+14.5135 dB`
        仍没解决
  - 结论：
    - `v142`
      接替 `v141`
      成为
      `head-only bounded direct-apply`
      子线最佳 continuation，
      但仍不能替代
      `v126`
      成为主线最佳 automatic continuation
- `v143 = v142 + refine-present speech-only 0007-like sibling v1`
  - relative `v142`：
    - 只训练
      `branch_overlap_refine_present_head`
    - `0007-like speech-only`
      selector
      只命中：
      - `3 / 203` train
      - `3 / 63` val
    - training-side
      `overlap_interference_extra_projection_ratio`
      仅：
      - train `0.0000213`
      - val `0.0000150`
    - 四条 fixed synthetic checks
      全是 near-tie：
      - abstention `-0.0030 dB`
      - same-gender keep `+0.0080 dB`
      - hard-present keep `+0.0086 dB`
      - artifact proxy `+0.0006 dB`
  - 结论：
    - `v143`
      是 practical no-op reject
- `v144 = v142 + refine-present broader speech-local-proxy hardlocal-bundle sibling v1`
  - relative `v142`：
    - speech-local selector
      扩到：
      - `33 / 99` train
      - `7 / 37` val
    - 但四条 fixed synthetic checks
      仍全部 near-tie：
      - abstention `+0.0067 dB`
      - same-gender keep `+0.0025 dB`
      - hard-present keep `+0.0019 dB`
      - artifact proxy `+0.0054 dB`
    - `local_speech_leak_proxy_v1`
      targeted compare
      也仍是：
      - `-0.0039 dB`
      - `0 improved / 0 regressed`
  - 结论：
    - `refine_present_head`
      在 `v142` 上
      即便吃到更宽 speech-local 资产，
      也推不动输出；
    - `v144` 直接 reject
- `v145 = v142 + refine-base broader speech-local-proxy hardlocal-bundle sibling v1`
  - relative `v142`：
    - 改训
      `branch_overlap_refine_head`
      本体
    - training-side
      已能看到真实机制：
      - `train_overlap_interference_projection_ratio = 0.0022900`
      - `val_overlap_interference_projection_ratio = 0.0006825`
    - 但四条 fixed synthetic checks
      仍全部 near-tie：
      - abstention `+0.0128 dB`
      - same-gender keep `+0.0075 dB`
      - hard-present keep `+0.0081 dB`
      - artifact proxy `+0.0047 dB`
    - `local_speech_leak_proxy_v1`
      targeted compare
      也仍是：
      - `-0.0064 dB`
      - `0 improved / 0 regressed`
  - 结论：
    - `v145`
      属于
      mechanism-on / output-off
      的 near-no-op reject
- `v146 = v142 + refine-base broader speech-local-proxy fallback-teacher sibling v1`
  - relative `v142`：
    - 原本意图是不传
      `teacher_checkpoint`
      去做 no-teacher
    - 但训练入口当前会对
      init checkpoint
      自动做
      `teacher_checkpoint`
      metadata fallback，
      因而实际继承到：
      - `teacher = v126`
    - 最终四条 fixed synthetic checks
      全部精确 `0.0 dB`
    - `local_speech_leak_proxy_v1`
      compare
      也精确 `0.0 dB`
  - 结论：
    - `v146`
      是 exact no-op reject；
    - 同时补出一个实现边界：
      “不传 teacher”
      当前不等于
      “真的无 teacher”
- 当前默认下一步再次更新为：
  - 收口 `v120`
  - preserve/bypass family 保持活跃
  - split local-control semantics 保持活跃
  - 收口 `v121`
  - 收口 `v123 / v124 / v125`
  - `v126` 保留为当前最佳 split-local-control automatic continuation
  - 不再继续扫：
    - `hardlocal selector`
    - `gate_power`
    - `present_veto_strength / power`
    - `absent_extra_weight`
    - `complement-head gate_power / gate_floor`
    - `overlap_dual_absent_mix_weight`
    - `current_output` 同构 sweep
    - `gate_absent_weight`
    - `gate_keep_weight`
    - `gate-head-only absent veto / keep`
    - `overlap_cancel_absent_mix_weight`
    - 同一个 direct-apply cancel head
      上的 `absent_mix`
      同构 reweight / 同头混训
    - `v142` 之上的
      `overlap_refine_present_head`
      sibling
    - `v142` 之上的
      `overlap_refine_head`
      sibling
    - `speech-local selector`
      宽窄 sweep
    - `gate threshold / present_max_delta`
  - 下一轮默认直接改机制去打：
    - 保留 `v142`
      这条 present-total direct path
    - 另开更强解耦的 absent path
      去打：
      - `0007 speech_only local leak`
      - `0009 absent local`
    - 若还想验证 no-teacher route，
      需先补一个
      `disable teacher metadata fallback`
      开关
    - `auxiliary_only / monitor-only`
      的更局部 true-absent indirect path
    - `0007 total leak`
  - 之后新增的两条收口也已确认：
    - `v147`
      true no-teacher
      `refine_base`
      rerun
      relative `v142`
      仍是 exact no-op；
      这条 `refine sibling`
      家族彻底收口
    - `v149`
      `v142 + head-only predicted-activity direct-apply`
      不是 no-op，
      但四条 fixed checks
      relative `v142`
      全线重度转负；
      `predicted_activity`
      这条 cancel-ratio-derived
      output blend
      也收口
    - `v150`
      `v142 + apply-controller only`
      relative `v142`
      五条口径全 near-tie，
      只是 practical no-op
    - `v151`
      `v142 + apply-controller + cancel`
      虽然 overlap-cancel signal
      已真实非零，
      但 fixed checks
      仍只是 near-tie，
      且
      `local_speech_leak_proxy_v1`
      relative `v142`
      变差 `-0.1692 dB`
    - `v152`
      `v142 + apply-controller + cancel`
      on broader hardlocal bundle
      进一步排除了
      “selector 太稀”：
      - selector
        已扩到
        train `33 / 99`
        / val `7 / 37`
      - 但 relative `v142`
        仍开始稳定伤：
        - abstention
        - hard-present keep
        - artifact proxy
        - local speech-leak proxy
  - 且需要记住：
    - 当前已经确认：
      - `v40` 类历史 absent proxy
        不等于真实 absent interval 资产
      - true absent supervision
        不能直接灌进当前
        `present-head-only` path
      - 即便是 dual residual/controller-side
        absent mix supervision，
        只要仍通过
        `gate_controller`
        回灌 global gate，
        也会系统性打坏
        abstention / keep / artifact guardrail
      - 即便改成
        `current_output`
        局部 direct-output rewrite，
        也仍会系统性打坏
        abstention / keep / artifact guardrail
      - 即便改做
        `branch_overlap_cancel_head`
        的
        `auxiliary_only`
        indirect path，
        broad absent-local mixture target
        也只会先改善：
        - `0009 absent local leak`
        - `0007 speech_only local leak`
        但不会自动改善：
        - `0007 total leak`
        - whole near-real tradeoff
      - 即便保留
        `v142`
        的 hardlocal head-only cancel
        子线，
        再把 direct-apply blend
        改成
        `predicted_activity`
        这种 self-bounded 路由，
        也会系统性打坏：
        - `abstention`
        - `keep`
        - `artifact guardrail`
      - 即便进一步把
        direct-apply
        拆成独立的
        `apply-controller head`，
        在
        `v142`
        这条子线上，
        也只会出现两类结果：
        - 窄 selector
          下 practical no-op
        - 宽 selector
          下开始伤
          `abstention / keep / artifact / local proxy`
      - 而 `v153 / v154 / v155 / v156 / v157 / v158`
        则把这条子线推进成了
        `interval-veto union-bundle`
        family：
        - `v153`
          是第一个可信的
          mechanism-positive evidence point
        - `v154`
          是 narrow-asset
          下的最佳 continuation，
          但 `0009 whole absent`
          仍回退
        - `v155`
          是 invalid broader-keep attempt，
          因为旧资产里
          根本没有 broader keep ids
        - `v156`
          是第一个真实的
          union-bundle broader-keep run，
          但 controller
          明显塌回 near-neutral
        - `v157`
          是当前这条 family
          的最佳 continuation：
          - fixed checks
            全 near-tie 且微正
          - `0007 speech_only`
            明显改善
          - `0009`
            维持阈值内安全
          - 但
            `0007 total leak`
            仍未收口
        - `v158`
          进一步证明
          `gate_keep_weight`
          sweep
          不是有效方向
        - `v159`
          说明固定
          speech-band apply
          也不够：
          它保留了 near-tie
          guardrail，
          但只把
          `0007 total leak`
          regression
          缩到
          `+0.1203 dB`
          这一类误差级，
          没有真正翻正
        - `v160`
          则说明
          apply-controller floor
          也只是
          稀疏写回版本的
          同一条路：
          `0007 speech_only`
          稍好，
          `0007 total leak`
          稍缩，
          但 whole 仍转差
        - `v161`
          则把
          split keep / absent
          controller
          这条路直接判掉：
          fixed checks
          仍近 tie，
          但
          `near_real_0007`
          whole / local
          尤其
          `speech_only`
          明显变差
        - `v162`
          说明：
          - absent-veto-only
            split controller
            可以保住
            `v157`
            的安全边界
          - 但 whole / local
            都会退成
            几乎 exact tie
          - 所以是
            mechanism-safe but ineffective
        - `v163`
          说明：
          - 在
            `v157`
            上直接挂
            no-teacher
            `refine_base`
            hardlocaltotal sibling
            仍是 no-op
          - 因为当前
            present-total
            local selector
            只有
            `3 / 99`
            / `3 / 37`
        - `v164`
          则把这条边界补实：
          - selector
            放宽到
            `hard_present_artifact_proxy_v1_all`
            后，
            train 也只到
            `8 / 99`
            / val `1 / 37`
          - training signal
            非零，
            但 relative `v157`
            五条 fixed checks
            仍全部
            `0.0 dB`
          - 所以
            `v157 + no-teacher refine_base sibling`
            当前也推不动输出
        - `v165`
          则把
          `present-total local asset`
          这条解释正式收掉：
          - 新的
            `hardlocal_totalrisk_bundle_v1`
            已把 selector
            扩到
            train `33 / 129`
            / val `7 / 41`
          - 训练信号持续非零
          - 但 relative `v157`
            五条 fixed checks
            仍全部精确
            `0.0 dB`
          - 说明
            `v157 + no-teacher refine_base`
            已经不是
            asset 宽度问题，
            而是结构性 no-op
        - `v166 / v167`
          则把新的
          `branch_base_blend`
          output path
          一并判掉：
          - `v166`
            relative `v157`
            四条 fixed checks
            `-2.8127 / -2.2610 / -1.8606 / -1.7204 dB`
            / local proxy `+0.6618 dB`
          - `v167`
            `max_blend = 0.1`
            后仍更差：
            `-3.1254 / -2.3924 / -1.9762 / -1.8001 dB`
            / local proxy `+0.7356 dB`
          - 两轮里
            controller head
            相对 `v157`
            权重 bitwise 不变，
            train / val
            `gate_absent_mean / gate_keep_mean`
            也始终是 `0.0`
          - 所以当前
            `branch_base_blend`
            应视为
            inference-path rewrite reject，
            不再继续扫
            `max_blend`
        - Correction:
          `v166 / v167`
          后来确认只是 selector-mismatch scratch，
          不能再作为
          `branch_base_blend`
          的正式机制证据。
          正确边界应改成：
          - `v168`
            才是 restored selectors 后的
            `branch_base_blend`
            正式 reject：
            fixed
            `-2.8097 / -2.2604 / -1.8620 / -1.7195 dB`
            / local `+0.6641 dB`
          - `v169 / v170`
            则把
            `refine_base_blend`
            一起收口：
            `v169 = -1.8759 / -1.7629 / -1.3051 / -1.4098 dB`
            / local `+0.5827 dB`
            ，
            `v170 = -2.0514 / -1.8388 / -1.3761 / -1.4598 dB`
            / local `+0.6458 dB`
          - `v171`
            再把
            `pre_present_subtract`
            timing route
            收到 mixed reject：
            fixed checks near-tie，
            local
            `near_real_0007 total leak = -1.5087 dB`
            首次转正，
            但 whole
            `near_real_0007`
            变成
            `delta_interference_capture_db = +27.3024 dB`
            / `delta_retention_minus_leak_db = -27.3334 dB`
          - `v172`
            把路线改成
            parallel pre-present total-risk controller
            后，
            relative `v157`
            四条 fixed checks
            首次同时微正
            `+0.0659 / +0.0348 / +0.0288 / +0.0221 dB`
            / local `-0.0537 dB`，
            且
            `near_real_0007 total leak = -1.4142 dB`
            与
            `near_real_0009`
            absent whole leak
            `= -3.1018 dB`
            一起给出机制正证据；
            但
            `near_real_0007`
            whole / speech-only
            仍分别回退
            `+23.1863 dB`
            /
            `+2.9102 dB`
          - `v173`
            只把
            `pre_present_max_blend`
            收到
            `0.1`
            后，
            证明这条 family
            的问题不是强度过大，
            而是 selectivity 不够：
            `0007`
            whole / speech-only
            regression
            缩到
            `+16.5421 / +1.5764 dB`
            ，
            但
            `0007 total leak`
            改善也同步缩到
            `-0.6784 dB`
          - `v174`
            改成
            `pre_present_controller_floor = 0.1`
            做 selectivity，
            但 relative
            `v172`
            只剩
            `+7.92e-05 dB`
            abstention
            /
            `-4.47e-05 dB`
            local proxy
            变化，
            是 practical no-op
          - `v175`
            再给同一个
            pre-present controller
            加
            outside-overlap abstain
            负监督，
            训练指标会动，
            但 relative
            `v172`
            输出仍只有
            `+1.22e-04 dB`
            abstention
            /
            `-2.35e-05 dB`
            local proxy
            变化，
            仍是 practical no-op
          - `v176`
            首次把
            `branch_overlap_cancel_head`
            与
            pre-present controller
            一起解冻，
            不再只是同一个 frozen head 的 loss-side 微调；
            但 relative
            `v172`
            输出仍只有
            `+7.91e-05 dB`
            abstention
            /
            `-4.47e-05 dB`
            local proxy
            变化，
            所以这条
            controller + cancel-head
            joint-unfreeze
            仍是 practical no-op
      - 当前默认下一步：
        - 保留 `v157`
          为 active base
        - 不再扫
          `gate_keep_weight`
          / `apply band`
          / `controller floor`
        - 不再扫
          split keep / absent
          controller
        - 不再扫
          `v157`
          上的 sparse
          no-teacher
          `refine_base` sibling
        - 不再扫
          `branch_base_blend`
          / `branch_base_blend + max_blend`
        - 不再扫
          `refine_base_blend`
          / `refine_base_blend + max_blend`
        - 不再扫
          plain `pre_present_subtract`
        - 不再扫
          parallel pre-present total-risk controller
          `max_blend`
        - 不再扫
          `pre_present_controller_floor`
        - 不再扫
          same-head
          outside-overlap abstain
          supervision / reweight
        - 不再扫
          `branch_overlap_cancel_head + pre-present controller`
          joint unfreeze
        - 下一步若继续，
          应放弃
          frozen single-head
          selectivity 微调，
          也不再停留在
          cancel-head
          这一层的小范围联合解冻；
          下一步应改更大的 decision source
          或联合解冻更大的 path

执行前必须保持六条验收同时在场：

- `real_eval_manifest_residual_speech_leak_floor_v1`
- `real_eval_manifest_bandwidth_guardrail_v1`
- `same_gender_present_keep_guardrail_v1`
- `hard_present_gate_keep_guardrail_v1`
- `hard_present_artifact_proxy_v1`
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
- `reports/daily/2026-03-26_overlap_aux_interference_decoder_v2_v3_v4_and_v93_v94_v95_followup.md`
- `reports/daily/2026-03-26_v81_vs_v95_listening_review.md`
- `reports/daily/2026-03-26_overlap_canceller_phasepreserve_v96_v97_v98_followup.md`
- `reports/daily/2026-03-27_speech_only_selector_profile_prework.md`
- `reports/daily/2026-03-27_overlap_purify_v2_speechonly_v102_followup.md`
- `reports/daily/2026-03-27_plusmusic_teacher_veto_v103_followup.md`
- `reports/daily/2026-03-27_v81_vs_v103_listening_review.md`
- `reports/daily/2026-03-27_hard_present_artifact_proxy_v1_materialization.md`
- `reports/daily/2026-03-27_artifactaware_pilots_v104_v105_followup.md`
- `reports/daily/2026-03-27_local_artifact_veto_v106_followup.md`
- `reports/daily/2026-03-27_v81_vs_v106_listening_review.md`
- `reports/daily/2026-03-27_local_speech_leak_proxy_v107_followup.md`
- `reports/daily/2026-03-27_v81_vs_v107_listening_review.md`
- `reports/daily/2026-03-27_phone_artifact_gate_v1_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_preservebackstop_v108_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_0007like_backstop_v109_followup.md`
- `reports/daily/2026-03-27_v81_vs_v109_listening_review.md`
- `reports/daily/2026-03-27_local_speech_leak_artifact_paired_0007like_v110_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_artifact_paired_0007like_selfanchor_v111_followup.md`
- `reports/daily/2026-03-27_overlap_cancel_splitpath_0007like_v112_followup.md`
- `reports/daily/2026-03-27_overlap_refine_preservebypass_0007like_selfanchor_v113_followup.md`
- `reports/daily/2026-03-28_true_absent_auxcancel_indirect_v136_v137_followup.md`
- `reports/daily/2026-03-28_splitselector_headonly_directapply_v138_v142_followup.md`
- `reports/daily/2026-03-28_refine_siblings_on_v142_v143_v146_followup.md`
- `reports/daily/2026-03-28_headonly_predactivity_directapply_v148_v149_followup.md`
- `reports/daily/2026-03-28_applycontroller_on_v142_v150_v152_followup.md`
- `reports/daily/2026-03-28_applycontroller_interval_veto_v153_v158_followup.md`
- `reports/daily/2026-03-28_applycontroller_interval_veto_localapply_v159_v160_followup.md`
- `reports/daily/2026-03-28_splitcontroller_and_refinebase_on_v157_v161_v164_followup.md`
- `reports/daily/2026-03-28_totalrisk_bundle_and_branchbaseblend_on_v157_v165_v167_followup.md`
- `reports/daily/2026-03-28_branchbase_refinebase_and_prepresentsubtract_on_v157_v168_v171_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_totalrisk_controller_on_v157_v172_v173_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_totalrisk_selectivity_v174_v175_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_hardlocal_selector_v115_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_0007like_predproj_v116_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_0007like_gateguided_v117_followup.md`
- `reports/daily/2026-03-28_overlap_dual_controller_floor_0007like_v118_followup.md`

## 文档维护规则

- 本文档只记录：
  - 当前活跃分支
  - 当前裁决状态
  - 当前默认下一步
- 已终止分支、旧 family 的长历史，不再回填到主文档。
- 当本文件再次膨胀到不利于接班阅读时，默认处理方式是：
  1. 先把当时版本完整快照到 `docs/archive/task_branch_map/`
  2. 再重写为新的短版活跃分支图
