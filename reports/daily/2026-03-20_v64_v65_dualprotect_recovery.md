# 2026-03-20 `v64 / v65` dual-protect follow-up recovery

## 背景

本次接班恢复时发现：

- 主文档和分支图都停在 `v63`
- 但磁盘上已经实际存在：
  - `v64`
  - `v65`
  的 checkpoint、compare summary 与 gate 产物
- 说明这两条并不是“未执行的书面规格”，
  而是已经跑完、评估完、
  只是没有及时补日报

本文件只做一件事：

- 把 `v64 / v65` 的真实执行状态
  和裁决结果补回文档链

本次恢复不新增训练，
不重跑 compare / gate，
只回填事实。

## `v64`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v64_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_v23minus0002_ft1`
- init：
  - `v32`
- 结构：
  - dual-head / branch-local decoder
- absent-side：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `focus = proxy_v7`
- protect A：
  - `interference_extra_base_align_weight = 0.02`
  - `focus = exact_targetfull_all`
- protect B：
  - `branch_protect_guard_sisdr_weight = 0.0002`
  - `focus = sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_all.txt`

### 命中情况

- `branch_protect` 在当前默认 split 上命中很稀：
  - train `1 / 129`
  - val `0 / 37`

这点很关键：

- `v64` 不是“第二 selector 完全无效”
- 而是它在当前 manifest 里
  实际吃到的样本太少

### 结果

relative to `v19`：

- default：
  - `+0.079474 dB`
- near-real speech probe overall：
  - `-0.038093 dB`
- exact `target_full`：
  - `-0.212114 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.055069 dB`
- `guodegang_anchor_120s`：
  - `+0.048336 dB`
- `guodegang_absent_480s`：
  - `+0.019495 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = near_tie`
- pass：
  - `default_stage2_delta_floor`
  - `speech_probe_overall_floor`
  - `exact_target_full_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`
- 唯一未过：
  - `speech_leak_like_gain_floor`
    - judgement:
      - `near_tie`

### 裁决

`v64` 不记为 keep candidate，
但应记为：

- `closed_but_evidence_keep`

原因不是：

- 它已经过 gate

而是：

1. 它说明新的第二 selector
   比 `exact_nontargetfull`
   更接近真实 `0004-like` 问题；
2. 它在不伤 `guodegang_anchor / absent`
   的前提下，
   已把结果压到只剩一条
   `speech_leak_like_gain_floor`
   的 `near_tie`；
3. 但由于当前 hit 太稀，
   证据强度还不够，
   不能直接升级成 keep。

## `v65`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v65_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_v23minus_union0002_ft1`
- 与 `v64` 的关键差异：
  - 把第二 selector 对应 rows
    真正 union 进 train / val manifest
- train manifest：
  - `data/synthetic/train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
- val manifest：
  - `data/synthetic/val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`

### 命中情况

- `branch_protect`
  命中已补足到：
  - train `7 / 135`
  - val `2 / 39`

也就是：

- `v65` 基本就是在回答：
  - “如果把 `v64` 这条 selector
     真正吃进去，
     会不会过 gate？”

### 结果

relative to `v19`：

- default：
  - `+0.106078 dB`
- near-real speech probe overall：
  - `-0.070686 dB`
- exact `target_full`：
  - `+0.031807 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.067371 dB`
- `guodegang_anchor_120s`：
  - `-0.147071 dB`
- `guodegang_absent_480s`：
  - `-0.057623 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- pass：
  - `default_stage2_delta_floor`
  - `speech_probe_overall_floor`
  - `exact_target_full_gain_floor`
- near-tie：
  - `speech_leak_like_gain_floor`
- clear fail：
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

### 裁决

`v65` 记为：

- `closed_failed`

这条线的结论已经很明确：

1. 单纯把 `v23minus` rows
   真正并入训练集，
   并不会把 `0004-like`
   拉到正向；
2. 它反而会重新打坏：
   - `guodegang_anchor`
   - `guodegang_absent`
3. 所以这不是
   “再多给一点 budget”
   就会自然转正的 keep 候选。

## 当前更新

恢复后，
当前 dual-protect 线应改写为：

1. `v63`
   已证明：
   - `exact_nontargetfull`
     不是对题的第二 selector
2. `v64`
   已证明：
   - 直接面向
     `exact minus target_full`
     的 selector
     语义更对
   - 但当前 hit 太稀，
     还只是证据轮次
3. `v65`
   已证明：
   - 单纯 union
     这批 rows
     不是 keep 方向

因此当前默认结论应固定为：

- `v64 = closed_but_evidence_keep`
- `v65 = closed_failed`
- 若后续继续 dual-protect：
  - 不直接重跑 `v64`
  - 不直接放大 `v65`
  - 不直接扫现有
    `branch_protect_guard_sisdr_weight`
  - 先重建真正对应
    `speech_leak_like (0004)`
    的 selector / proxy
