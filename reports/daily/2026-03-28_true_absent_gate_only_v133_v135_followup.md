# 2026-03-28 true-absent gate-only `v133 / v134 / v135` follow-up

## Summary

- 在 `v131 / v132` 收口了
  “dual absent-supervised branch 直接改 final output”
  之后，
  这轮转向更温和的间接约束：
  - 只动现有 `branch_decoder_frame_gate`
  - 不再新增 dual output rewrite
  - 先验证
    `target_absent_intervals -> gate=0`
    这条 gate-only supervision
    是否能安全生效
- 结果分三步：
  - `v133`
    不是正式实验，
    而是一次无效 scratch：
    初版 `gate_absent_sample_weights`
    误接到了 `absent_union_sample_weights`，
    而这套 run 并没有显式 absent selector，
    导致 `gate_absent_mean` 全程都是 `0.0`
  - `v134 = v126 + true-absent gate-absent 0.04 v1`
    是修正 sample-weight bug 后的首个真实 gate-only absent pilot；
    `gate_absent` 明确生效，
    但 relative `v126`
    四条 fixed synthetic checks
    仍然全线转负
  - `v135 = v126 + true-absent gate-absent 0.02 + gate-keep 0.02`
    试图用 sparse hard-present anchors
    把 guardrail 回拉；
    `gate_absent / gate_keep`
    都真实生效，
    但四条 fixed synthetic checks
    还是全线转负，
    而且比 `v134` 更差一点
- 裁决：
  - `v133 = invalid scratch`
  - `v134 = reject`
  - `v135 = reject`
  - `gate-head-only absent veto / keep`
    这条家族先收口；
    `v126` 继续保持全局最佳 automatic continuation，
    `v129` 继续保持 decoupled true-absent 支线最佳 continuation

## `v133` invalid scratch

- 预期定义：
  - `v133 = v126 + true-absent gate-absent 0.04 v1`
- 真实情况：
  - 初版实现里，
    `gate_absent_sample_weights`
    直接复用了
    `absent_union_sample_weights`
  - 但这轮并没有配置
    `absent_* selector`
    条件，
    所以
    `resolve_selector_sample_weights(...)`
    返回的是 `None`
  - `weighted_gate_target_loss(...)`
    在 `sample_weights is None`
    时直接回 `0.0`
- 结果：
  - `train_gate_absent_mean`
    四个 epoch 全是 `0.0`
  - `val_gate_absent_mean`
    四个 epoch 全是 `0.0`
- 处理：
  - 新增按
    `target_absent_intervals`
    直接构造的
    `absent_presence_sample_weights`
  - 后续 `v134 / v135`
    才是这条机制的正式结果

## `v134 = v126 + true-absent gate-absent 0.04 v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v134_v126_trueabsent_gateabsent004_v1_ft1`
- 初始化：
  - `v126`
- trainable：
  - `branch_decoder_gate_head`
- 训练资产：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
- loss 关键变化：
  - 新增
    `gate_absent_weight = 0.04`
  - 监督对象：
    - 对所有存在
      `target_absent_intervals`
      的样本，
      把 `branch_decoder_frame_gate`
      拉向 `0`

## Training Signal

- 这轮不是 no-op：
  - `train_gate_absent_mean`
    `0.4410 -> 0.1905`
  - `val_gate_absent_mean`
    `0.2315 -> 0.1255`
- 但同时能看到
  `gate_keep` 漂移问题：
  - `val_gate_keep_mean`
    在末轮到 `0.3477`
  - 说明 gate head
    正在把 absent push
    写回 present keep 语义

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `num_samples = 8`
  - `avg_sisdr_delta_db = -2.2058 dB`
  - `improved = 2`
  - `regressed = 6`
- `same_gender_present_keep_guardrail_v1`
  - `num_samples = 11`
  - `avg_sisdr_delta_db = -0.9064 dB`
  - `improved = 2`
  - `regressed = 9`
- `hard_present_gate_keep_guardrail_v1`
  - `num_samples = 16`
  - `avg_sisdr_delta_db = -1.7109 dB`
  - `improved = 4`
  - `regressed = 12`
- `hard_present_artifact_proxy_v1`
  - `num_samples = 7`
  - `avg_sisdr_delta_db = -2.1404 dB`
  - `improved = 0`
  - `regressed = 7`

## `v135 = v126 + true-absent gate-absent 0.02 + gate-keep 0.02`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v135_v126_trueabsent_gateabsent002_gatekeep002_v1_ft1`
- 初始化：
  - `v126`
- trainable：
  - `branch_decoder_gate_head`
- 训练资产：
  - 与 `v134` 相同
- loss 关键变化：
  - `gate_absent_weight = 0.02`
  - `gate_keep_weight = 0.02`
  - `branch_protect_focus_sample_ids`
    只保留 6 个 hard-present local artifact anchors
- selector 命中：
  - `branch_protect = 3 / 203` train
  - `branch_protect = 3 / 63` val

## Training Signal

- 这轮也是实打实生效，
  不是 no-op：
  - `train_gate_absent_mean`
    `0.4271 -> 0.1807`
  - `val_gate_absent_mean`
    `0.2150 -> 0.1148`
  - `train_gate_keep_mean`
    `0.0506 -> 0.0833`
  - `val_gate_keep_mean`
    `0.3225 -> 0.3501`
- 但结果说明：
  - sparse keep anchors
    没有把 gate-only absent push
    拉回安全区；
  - 相反，
    hard-present / artifact
    仍在继续恶化

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `num_samples = 8`
  - `avg_sisdr_delta_db = -2.2891 dB`
  - `improved = 2`
  - `regressed = 6`
- `same_gender_present_keep_guardrail_v1`
  - `num_samples = 11`
  - `avg_sisdr_delta_db = -1.0121 dB`
  - `improved = 2`
  - `regressed = 9`
- `hard_present_gate_keep_guardrail_v1`
  - `num_samples = 16`
  - `avg_sisdr_delta_db = -1.8372 dB`
  - `improved = 4`
  - `regressed = 12`
- `hard_present_artifact_proxy_v1`
  - `num_samples = 7`
  - `avg_sisdr_delta_db = -2.5225 dB`
  - `improved = 0`
  - `regressed = 7`

## Interpretation

- `v134` 已经证明：
  - 只靠
    `target_absent_intervals -> gate=0`
    这条 gate-head-only supervision，
    机制是真实的，
    但当前 split-local-control 主线下
    guardrail 仍会整体转坏
- `v135` 则进一步证明：
  - 给这条 gate-only absent push
    再补 sparse hard-present keep anchors，
    也不足以修回：
    - abstention
    - same-gender keep
    - hard-present keep
    - artifact proxy
  - 而且 `v135`
    相对 `v134`
    没有出现任何 aggregate rescue，
    说明问题不只是
    `gate_absent_weight` 太强；
    更根本的是：
    当前 gate head
    本身就是过于直接的施力点

## Conclusion

- 这轮把
  `gate-head-only absent veto / keep`
  收口得更完整了：
  - `v133`
    暴露了 sample-weight 接线风险，
    真实结果必须先确认
    `gate_absent_mean != 0`
  - `v134`
    证明 gate-only absent supervision
    真实有效，
    但 fixed guardrails 全负
  - `v135`
    证明
    `gate_absent + sparse gate_keep`
    也救不回来
- 当前主结论保持：
  - `v126`
    仍是全局最佳 automatic continuation
  - `v129`
    仍是 decoupled true-absent 支线最佳 continuation
- 这条家族默认不再继续扫：
  - `gate_absent_weight`
  - `gate_keep_weight`
  - `gate-head-only absent veto / keep`

## Next

1. 收口 `v133 / v134 / v135`
2. 不补 near-real，也不给听审
3. 若继续 true-absent indirect path，
   默认改成更强解耦：
   - `auxiliary_only / monitor-only` 分支
   - absent-local supervision 不直接落在当前 `branch_decoder_frame_gate`
   - 不直接 rewrite final output，
     只允许通过共享表征间接影响主线
