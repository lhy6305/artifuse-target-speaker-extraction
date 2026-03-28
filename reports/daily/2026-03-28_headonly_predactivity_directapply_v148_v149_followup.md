# 2026-03-28 head-only predicted-activity direct-apply `v148 / v149` follow-up

## Summary

- 在
  `v143 / v144 / v145 / v146 / v147`
  之后，
  当前默认下一步已经切成：
  - 不再继续叠
    `v142` 之上的
    `overlap_refine` sibling
  - 改做新的
    output apply path
- 这轮测试的是一个更局部的想法：
  - 保留
    `v142`
    的
    `branch_overlap_cancel_head`
    与 hardlocal selector
  - 但把 direct-apply
    从原来的
    `complement blend 0.5`
    改成
    `predicted_activity`
    自限 blend
- 结果分成两段：
  - `v148`
    是无效 scratch
    因为 selector 文件复原错成了过宽 bundle，
    实际命中
    `train 105 / 203`、
    `val 36 / 63`
  - `v149`
    才是有效 rerun，
    selector 已对齐回
    `train 3 / 203`、
    `val 3 / 63`
    但四条 fixed checks
    relative `v142`
    全线重度转负
- 结论非常明确：
  - `predicted_activity`
    这条 self-bounded direct-apply
    不是安全 continuation
  - 当前不再继续扫：
    - `predicted_activity`
    - `predicted_activity + max_blend`
    - 同构的
      cancel-strength-derived
      output blend

## Code Change

- 新增了
  `branch_overlap_cancel_delta_blend_mode = predicted_activity`
- 语义是：
  - 用
    `abs(branch_overlap_cancel_ratio) / branch_overlap_cancel_max_delta`
    作为 direct-apply blend
  - 再乘
    `branch_overlap_cancel_max_blend`
- 代码位置：
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `scripts/train/train_stft_mask_baseline.py`

## `v148 = invalid scratch`

## What Went Wrong

- 这轮原本想复刻
  `v142`
  的 hardlocal selector，
  但我一开始误把 selector
  复原成了更宽的 bundle 文件
- 结果：
  - `train_overlap_cancel selector = 105 / 203`
  - `val_overlap_cancel selector = 36 / 63`
- 这已经不再是
  `v142`
  对应的
  `3 / 203`
  与
  `3 / 63`
  子域

裁决：

- `v148`
  不参与比较
- 只记为：
  selector reconstruction
  mistake scratch

## `v149 = v142 + head-only predicted-activity direct-apply v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v149_v142_headonly_predactivity_directapply_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `None`
  - 显式使用了
    `--disable-teacher-checkpoint-metadata-fallback`
- manifest：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
- overlap-cancel selector：
  - 直接从
    `v142 train_summary.json`
    导出原始 `40` 条
    `focus_sample_ids`
- 模型差异只一处：
  - `branch_overlap_cancel_delta_blend_mode = predicted_activity`
  - `branch_overlap_cancel_max_blend = 1.0`

## Training Signal

- selector 已正确回到：
  - train `3 / 203`
  - val `3 / 63`
- 末轮：
  - `train_overlap_cancel_waveform_l1 = 0.0083316`
  - `val_overlap_cancel_waveform_l1 = 0.0275487`
  - `train_overlap_cancel_target_projection_ratio = 0.0000171`
  - `val_overlap_cancel_target_projection_ratio = 0.0001295`

这说明：

- `v149`
  不是 no-op
- 新 apply path
  的训练信号
  真实生效

## Fixed Checks relative `v142`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -6.0908 dB`
  - `improved = 1`
  - `regressed = 7`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -3.0712 dB`
  - `improved = 4`
  - `regressed = 7`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -7.0467 dB`
  - `improved = 3`
  - `regressed = 13`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = -10.8147 dB`
  - `improved = 0`
  - `regressed = 6`

## Verdict

- `v149 = reject`
- 不补 near-real
- 不出听审

## New Boundary

- 在
  `v142`
  这条
  hardlocal head-only cancel
  direct-apply 子线上：
  - 把 apply blend
    改成
    `predicted_activity`
    这种
    cancel-strength-derived
    self-bounded 路由，
    不会带来更局部的安全更新；
  - 反而会系统性打坏：
    - abstention
    - keep
    - artifact guardrail

## Final Decision

- 保留：
  - `v126`
    继续作为全局最佳 automatic continuation
  - `v142`
    继续作为
    head-only bounded direct-apply
    子线最佳 continuation
- 收口：
  - `v148`
    selector-mismatch scratch
  - `v149`
    predicted-activity direct-apply
- 下一步默认不再继续：
  - `predicted_activity`
  - `predicted_activity + max_blend`
  - 同构的
    cancel-ratio-derived
    output blend
- 如果继续，
  默认应改做：
  - 不是由
    cancel head magnitude
    直接派生的 output apply path
  - 或完全换到
    非 cancel-head
    的局部作用机制
