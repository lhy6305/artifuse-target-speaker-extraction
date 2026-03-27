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
  - `v87`
    - 含义：`v81 + overlap canceller v1`
    - 状态：objective 与 near-real 都更强，但基本退化成 `v86` 的近等价体，不升格
  - `v88`
    - 含义：`v87 + overlap canceller v2 target-orthogonality`
    - 状态：当前 overlap canceller 家族最强自动候选，但 `v81 vs v88` 听审结果为 `tie = 2, v81 = 2, v88 = 0`，不升格
  - `v89`
    - 含义：`v81 + overlap dual-source consistency v1`
    - 状态：relative `v81` 的 synthetic / near-real 都更强，但自动上仍落后 `v88`，不进入 focused 听审
  - `v90`
    - 含义：`v81 + overlap dual decoder v1`
    - 状态：失败，direct dual-target 输出导致大幅回退，自动与 near-real 都落到 `v54` 后面
  - `v91`
    - 含义：`v90 + dual blend cap 0.25`
    - 状态：比 `v90` 更稳定，但仍显著差于 `v81`，不进入 focused 听审
  - `v93`
    - 含义：`v88 -> auxiliary_only` prior transfer through `branch_decoder_temporal_model`
    - 状态：synthetic 明显变强，但 near-real 重新伤到 `0003 / 0007`，不升格
  - `v94`
    - 含义：`v88 -> auxiliary_only` narrower transfer through `branch_decoder_mask_head`
    - 状态：把 failure 收窄到 `0007` 单点，但仍不过 near-real guardrail，不升格
  - `v95`
    - 含义：`v94 + hard-present protect`
    - 状态：automatic suppression 更强，但 `v81 vs v95` 听审为 `tie = 3, v81 = 1, v95 = 0`，且唯一差异是 `0007` 上 `v95` 伪影更重，不升格
  - `v96`
    - 含义：`v81 + phase_preserve overlap cancel head`，但 `auxiliary_only + overlap_cancel_head-only`
    - 状态：结构性 no-op probe，不构成真实输出候选
  - `v97`
    - 含义：`v96` 的 `phase_preserve` startup/gradient 修正版复跑
    - 状态：代码正确性 probe，结果仍是结构性 no-op，不升格
  - `v98`
    - 含义：`v81 + overlap canceller v3 phase_preserve subtract`
    - 状态：首个有效的 phase-preserving subtractive pilot，但 synthetic / near-real / bandwidth 都与 `v81` 近乎全 tie，不进入 focused 听审
  - `v99`
    - 含义：`v95 + hard-present self-align veto probe`
    - 状态：在 `auxiliary_only` 家族上是结构性 no-op，不构成真实候选
  - `v100`
    - 含义：`v95 + frozen teacher hard-present overlap veto`
    - 状态：relative `v81` 三条 synthetic guardrail 全量正收益，near-real objective gate 已通过；但 `v81 vs v100` 听审结果为 `tie = 3, v81 = 1, v100 = 0`，不升格
  - `v101`
    - 含义：`v88 + overlap cancel delta blend v1`
    - 状态：relative `v81` synthetic / near-real objective 继续正收益，relative `v88` 则明显更保守；但 `v81 vs v101` 听审结果为 `tie = 3, v81 = 1, v101 = 0`，不升格
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
    - 状态：relative `v81` 仍全量 objective 改善、near-real 仍 `0` violation；但 `v81 vs v86` 听审仍未转正，不可放行
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
- `v72 / v73 / v74 / v75 / v76 / v77 / v78 / v79 / v80 / v81 / v82 / v83 / v84 / v85 / v86 / v87 / v88 / v89 / v90 / v91 / v93 / v94 / v95 / v98 / v99` 都不能替代默认线。
- `v100` 也不能替代默认线。
- `v101` 也不能替代默认线。

## 当前默认下一步

- `v81 vs v103` focused 听审已完成；
- 结果是 `4 / 4` 全部偏向 `v81`，共同原因都是 `v103` 伪影更重；
- 不继续做 `v103+` 同结构小步权重 sweep；
- `hard_present_artifact_proxy_v1` 已物化并完成 `v81 / v102 / v103` 回放；
- 它能复现“suppression 继续更强，但 hard-present artifact/backstop 重新变差”的问题模式；
- `v104 = artifactaware_anchor` 已完成：
  - synthetic 介于 `v81` 与 `v102` 之间
  - near-real 比 `v103` 安全，但 `0007` 没有形成局部 rescue
  - 不再继续
- `v105 = artifactguard` 已完成：
  - synthetic 四条固定验收都排前，`hard_present_artifact_proxy_v1` 也最强
  - 但 near-real `0003 / 0007` target capture 同时回退
  - overlap-local 上 `0007` 仍是 `v81` 更好，且 `v105` artifact 更重
  - 判定为 proxy 过拟合，不导听审
- 当前默认下一步改为：
  - 收口 `speech_only overlap residual + plus_music teacher veto` 这一小家族
  - 维持新的 artifact-first 固定诊断链
  - 收口 `v104 / v105` 这一轮 artifact-aware 粗权重 pilot
  - 基于 `v81` 改做更外科式的 local artifact veto / backstop，而不是继续 `v103+` 或 `v105+`

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
- `data/synthetic/val_manifest_hard_present_artifact_proxy_v1.jsonl`

作用：

- 这是当前最重要的新 guardrail；
- 它能复现 `near_real_0003` 风格 failure；
- `hard_present_gate_keep_guardrail_v1` 则覆盖 `near_real_0007` 风格 hard-present failure；
- `hard_present_artifact_proxy_v1` 进一步把 `0007` 的 `speech_plus_music + artifact-risk` 子域单独拆出来；
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
  - `v81 vs v86` focused 听审现已完成：
    - `3 / 4 tie`
    - `1 / 4 = v81`
    - `v86 = 0`
    - 唯一分出胜负的是 `near_real_0009`
      - `v81 > v86`
  - 结论：
    - `v86` 也没有跨过可听阈值
    - 当前核心痛点仍未解决

## 当前最可靠的阶段结论

1. `same_gender_present_keep_guardrail_v1` 已经是正式资产，后续必须保留。
2. overlap refiner 机制已经成立，当前最有效的收窄方式是：
   - 用 `gate-complement`
   - 而不是 `gate`
3. `v81` 仍是当前最健康、最稳妥的研究基座；`v85 / v86` 虽然自动与 guardrail 都更强，但两轮 focused 听审都没有转正。
4. `v87 / v88` 进一步证明 overlap canceller 机制可训练、可带来自动收益，但 `v81 vs v88` 听审仍是 `v81 >= v88`，说明这条线也还没有推进到可听层胜出。
5. `v89` 说明在现有 overlap canceller head 上继续叠 `dual-source consistency` 约束，能得到一个介于 `v81` 和 `v88` 之间的 checkpoint，但还不足以越过 `v88` 平台。
6. `v90 / v91` 说明“显式估计干扰，再直接用 `mixture - interference_est` 作为最终目标路径”这个接法不可用；问题不是 dual-source idea 本身，而是 direct final-output integration point 错了。
7. `v93 / v94 / v95` 说明 auxiliary interference decoder 作为训练辅助是可学习的，但当前收益仍停留在自动层；一旦跨到可听差异，先暴露出来的是 `near_real_0007` 上更重的伪影，而不是核心痛点的可听解决。
8. `v96 / v97 / v98` 说明“只把 overlap canceller 改成 phase-preserving”不是当前突破口：
   - `v96 / v97` 暴露了 `auxiliary_only + overlap_cancel_head-only` 的结构性 output-inactive 问题；
   - `v98` 虽然是有效 subtractive pilot，但 synthetic、near-real tradeoff、bandwidth 全都近乎与 `v81` 打平；
   - 这条 `phase-preserving overlap canceller` 线本轮可视为已自动收口，不值得进入 focused 听审。

### 6. overlap-local benchmark 诊断链

已完成：

- `scripts/eval/build_overlap_local_benchmark_manifest.py`
- `scripts/eval/analyze_overlap_local_benchmark.py`
- `reports/eval/overlap_local_benchmark_manifest_residual_speech_leak_floor_v1.jsonl`
- 已回放 pack：
  - `v81 vs v88`
  - `v81 vs v95`
  - `v81 vs v100`
  - `v81 vs v101`

结论：

- whole-utterance `more_interference_leaky` 在这 4 个已听 pack 的 `5` 个 decisive 样本上，全部与人耳偏好反向；
- overlap-local `better_retention_minus_speech_leak` 在 `3` 个 target-present decisive 样本上全部与人耳一致；
- overlap-local `more_artifact_proxy_heavy` 在 `5` 个 decisive 样本里对齐了 `4` 个，尤其能抓到：
  - `v95 / v100` 在 `near_real_0007` 上的人耳伪影回退；
- overlap-local `more_total_interference_leaky` 会被 `near_real_0007` 的 music 成分污染，不如 speech-only 版本稳定；
- 当前可用结论不是“local 指标完全替代全句指标”，而是：
  - 对 target-present overlap frontier，
  - 应优先看 localized `speech-leak / retention-minus-speech-leak / artifact-share`，
  - 不再把 whole-utterance leak tradeoff 当终裁依据。

### 7. speech-only selector 前置条件

已完成：

- `src/tse_prefix/data/synthetic_dataset.py`
  - 新增 interference 派生字段：
    - `interference_profile`
    - `interference_layer_count`
    - `has_speech_interference`
    - `has_music_interference`
    - `has_other_interference`
- `src/tse_prefix/pipeline/loss_selectors.py`
  - 新增 selector 键：
    - `focus_interference_profiles`
    - `require_speech_interference`
    - `require_music_interference`
    - `require_other_interference`
    - `min_interference_layer_count`
    - `max_interference_layer_count`
- `scripts/train/train_stft_mask_baseline.py`
  - 已暴露对应训练 CLI 参数

自检结论：

- 在 `data/synthetic/train_manifest_abstention_gate_bundle_v2.jsonl` 上：
  - `target_clean_speech = 34`
  - `target_hard_speech = 17`
  - 全部被标为 `speech_only`
- `target_clean_plus_music = 30`
  - `target_hard_plus_music = 21`
  - 全部被标为 `speech_plus_music`
- 用：
  - `focus_interference_profiles = speech_only`
  - `require_speech_interference = true`
  - `require_music_interference = false`
  可稳定选中纯 speech 样本 `51` 条，误选 `plus_music = 0`

结论：

- 下一步不需要先物化新的 speech-only manifest；
- 直接用现有 synthetic manifest + selector，就能定义“纯 speech overlap”训练子域；
- 后续 pilot 可以直接基于 `v81` 开做。

### 8. `v102` speech-only overlap pilot

已完成：

- `v102 = v81 + overlap_purify_v2_speechonly_selector_ft1`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v102_v81_overlap_purify_v2_speechonly_ft1`

训练口径：

- 结构、权重、trainable head 全部复用 `v82`
- 唯一实质改动：
  - 把 overlap-local loss 的 selector
  - 从“第一层 speech pool”改成真正的 `speech_only`

结果：

- synthetic 四条固定验收 relative `v81` 仍保持正收益：
  - abstention `+2.829 dB`
  - same-gender keep `+1.252 dB`
  - hard-present keep `+1.022 dB`
- near-real whole-utterance：
  - `overall_pass = true`
  - 但只在 `0003` 上给出清晰正 tradeoff
  - `0007` 仍是 hard-present 黄灯
  - `0009` absent 近乎打平
- overlap-local：
  - `0003 / 0006`
    的 `retention-minus-speech-leak` 都优于 `v81`
  - `0007` 仍明显更差

当前裁决：

- `v102` 不能自动升格；
- 但已经值得进入 focused 听审，
  因为它是第一条把 `speech_only` selector 落到实训并跑通完整验收的 pilot。

### 9. `v103` plus-music teacher veto pilot

已完成：

- `v103 = v102 + speech_only overlap residual + plus_music hard-risk teacher veto`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v103_v102_speechonly_plusmusic_teacher_veto_ft1`

训练口径：

- 初始化：
  - `v102`
- frozen teacher：
  - `v81`
- 保持 `v102` 的：
  - `speech_only overlap_interference_extra`
- 新增：
  - `branch_protect_teacher_overlap_weight = 0.04`
  - selector 只打：
    - `target_full`
    - `speech_plus_music`
    - `interference_layer_count = 2`
    - `overlap_ratio >= 0.6`
    - `0.05 <= target_energy_ratio <= 0.12`
    - `target_transient_presence_share_mean <= 0.04`

结果：

- teacher selector 确实激活：
  - train `14 / 102`
  - val `4 / 33`
- synthetic relative `v81` 三条主验收全部更强：
  - abstention `+3.774 dB`
  - same-gender keep `+1.913 dB`
  - hard-present keep `+1.354 dB`
- near-real whole-utterance：
  - `overall_pass = true`
  - `0003` 的 `retention-minus-leak` 继续转正
  - `0009` absent suppression 也优于 `v81`
- overlap-local：
  - `0003 / 0006`
    - `retention-minus-speech-leak` 仍优于 `v81`
  - `0007`
    - `better_retention_minus_speech_leak = v81`
    - `more_artifact_proxy_heavy = v103`
    - 当前痛点仍未真正修好

当前裁决：

- `v103` automatic 上确实是这一小家族里最强的一条；
- 但 blind 听审 `v81 vs v103` 结果为：
  - `v81 = 4`
  - `v103 = 0`
  - `tie = 0`
- 四条样本共同原因都是：
  - `v103` 伪影更重
- 因此本家族当前正式裁决不是“值得继续微调”，
  而是：
  - whole-utterance / localized leak objective 仍不足以约束真实可听伪影
  - `v103` 不升格
  - 这条训练方向先收口

## 下一步默认计划

当前默认状态不是继续当前 refiner 家族自动扩树。

优先顺序：

1. `v54 vs v81` 选型题已经收口，不再继续追加同类听审。
2. `v81 vs v82` 选型题已收口，不再继续追加同类听审。
3. 当前阶段结论已更新为：
   - `v85` 不升格
   - `v86` 也不升格
   - `v81` 继续保留为研究基座
4. 当前默认不再继续做：
   - `v83` 式宽触发 refiner
   - `v84` 附近轻量 sweep
   - `v85 / v86` 之后的同家族自动 checkpoint 扩树
5. 若后续继续推进，默认应改成：
   - 开新的机制子题
   - 而不是继续做当前 overlap refiner 家族的小步变体
6. 当前也不再继续做：
   - `v89` 同家族 weight sweep
   - `v81 vs v89` 听审导包
7. 当前也不再继续做：
   - `v90 / v91` direct dual-target 输出线的同家族 sweep
   - `v90 / v91` 听审导包
8. 当前也不再继续做：
   - `v93 / v94 / v95` auxiliary-only 小步 sweep
   - `v81 vs v95` 之后的同家族追加听审
9. 当前也不再继续做：
   - `v96 / v97` 这类 `auxiliary_only + overlap_cancel_head-only` probe
   - `v98` 附近的 `phase_preserve` overlap-canceller ratio mode 小步 sweep
10. 后续训练固定保留四条训练/验收约束：
   - `abstention_gate_proxy_v1`
   - `same_gender_present_keep_guardrail_v1`
   - `hard_present_gate_keep_guardrail_v1`
   - `gate_keep_union_v2`
11. 当前若继续推进，默认应切到：
   - 新的机制层表示或监督语义
   - 并显式处理 `hard-present artifact risk`
   - 而不是继续改同一个 multiplicative overlap-cancel head 的 ratio parameterization
12. 在任何新训练前，默认先保留一轮 overlap-local 回放：
   - 先看 `localized speech leak`
   - `localized retention-minus-speech-leak`
   - `localized artifact proxy`
   是否比 whole-utterance tradeoff 更接近已知听审样本
13. 在任何新训练前，固定保留以下四条验收：
   - `real_eval_manifest_residual_speech_leak_floor_v1`
   - `same_gender_present_keep_guardrail_v1`
   - `hard_present_gate_keep_guardrail_v1`
   - `overlap_abstention_proxy_v4_audibility_v1`
14. 当前新的默认前置条件已就绪：
    - `speech_only` vs `speech_plus_music` 已可通过 selector 稳定分离
    - 下一步可直接进入 `v81` 基座上的 speech-only local residual pilot 配置阶段
15. `v102` speech-only pilot 已完成自动验收：
   - 当前默认下一步不再是继续扫 `v102 / v103` 权重
   - 先做了 `v81 vs v102` focused 听审后，确认 `0007` 仍是唯一明确痛点
16. `v103` plus-music teacher veto pilot 已完成自动验收：
   - `v81 vs v103` 的 whole-utterance gate 已回到 `overall_pass = true`
   - 但 blind 听审结果为：
     - `v81 = 4`
     - `v103 = 0`
     - `tie = 0`
   - 四条样本全部因 `v103` 伪影更重而偏向 `v81`
   - 当前默认下一步改成：
     - 不再继续 `v103+` 小步 sweep
     - 改做 `0007` 风格 artifact proxy / 约束机制题

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
- `reports/daily/2026-03-26_v81_vs_v86_listening_review.md`
- `reports/daily/2026-03-26_overlap_canceller_v1_v2_and_v87_v88_followup.md`
- `reports/daily/2026-03-26_v81_vs_v88_listening_review.md`
- `reports/daily/2026-03-26_overlap_dualsource_consistency_v1_and_v89_followup.md`
- `reports/daily/2026-03-26_overlap_dual_decoder_v1_v90_v91_followup.md`
- `reports/daily/2026-03-26_overlap_aux_interference_decoder_v2_v3_v4_and_v93_v94_v95_followup.md`
- `reports/daily/2026-03-26_v81_vs_v95_listening_review.md`
- `reports/daily/2026-03-26_overlap_canceller_phasepreserve_v96_v97_v98_followup.md`
- `reports/daily/2026-03-26_overlap_local_benchmark_v81_v88_v95_v100_v101_followup.md`
- `reports/daily/2026-03-27_speech_only_selector_profile_prework.md`
- `reports/daily/2026-03-27_overlap_purify_v2_speechonly_v102_followup.md`
- `reports/daily/2026-03-27_plusmusic_teacher_veto_v103_followup.md`
- `reports/daily/2026-03-27_v81_vs_v103_listening_review.md`
- `reports/daily/2026-03-27_hard_present_artifact_proxy_v1_materialization.md`
- `reports/daily/2026-03-27_artifactaware_pilots_v104_v105_followup.md`

## 文档维护规则

- 本文档保持“活跃摘要”定位，优先写当前状态、当前验收、下一步。
- 具体长过程、逐轮试验、样本级历史判断一律写入：
  - `reports/daily/`
  - `docs/archive/project_overview/`
- 当本文件再次超过“明显不利于接班阅读”的规模时，默认处理方式不是继续堆长，而是：
  - 先归档当前版本快照；
  - 再重写为新的短摘要。
