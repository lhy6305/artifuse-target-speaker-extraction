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

## 文档维护规则

- 本文档只记录：
  - 当前活跃分支
  - 当前裁决状态
  - 当前默认下一步
- 已终止分支、旧 family 的长历史，不再回填到主文档。
- 当本文件再次膨胀到不利于接班阅读时，默认处理方式是：
  1. 先把当时版本完整快照到 `docs/archive/task_branch_map/`
  2. 再重写为新的短版活跃分支图
