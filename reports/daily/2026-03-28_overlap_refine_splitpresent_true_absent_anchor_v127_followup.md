# 2026-03-28 overlap-refine split-present true absent anchor `v127` follow-up

## Summary

- 基线继续沿：
  - `v126 = v125 + present-head complement-ratio veto 0.5`
- 本轮只加一个新变量：
  - 把真正带 `target_absent_intervals` 的 absent anchor rows
    并进当前 `0007_like` bundle，
    然后给 `absent_extra` 一档极轻量权重。
- 本轮定义：
  - `v127 = v126 + true absent anchor bundle + absent_extra 0.02`
- 裁决：
  - `v127 = reject`
  - 不是 no-op，
    但也不是可保留的 continuation；
  - 不导听审，
    也不继续扫 `absent_extra_weight`。

## Data Clarification

- 这轮先把一个历史概念拆开了：
  - `sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap`
    只是 absent-side proxy allowlist，
    不是“真实 absent interval 训练资产”；
  - 从主 manifest 回取后可见，
    这批 rows 实际都是：
    - `target_full`
    - `target_present_ratio = 1.0`
    - `target_absent_intervals = []`
- 因此若要验证真正的 `absent_interval_l1 / absent_extra_interval_l1`，
  不能再把 `v40` 类历史 absent proxy
  当成真实 absent anchor。

## New Asset

- 本轮改用真正带 absent interval 的 rows：
  - `recipe = target_clean_speech`
  - `temporal_pattern in {target_absent_head, target_absent_tail}`
  - `speech_only`
  - `overlap >= 0.8`
- 新 manifest：
  - `data/synthetic/train_manifest_true_absent_anchor_clean_speech_highoverlap_v1.jsonl`
    - `95`
  - `data/synthetic/val_manifest_true_absent_anchor_clean_speech_highoverlap_v1.jsonl`
    - `24`
- 与当前 active bundle 合并后：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
    - `203`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
    - `63`
- selector 命中已不是空转：
  - train
    - `absent_extra = 95 / 203`
  - val
    - `absent_extra = 24 / 63`

## `v127` Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v127_v126_splitpresent_trueabsentanchor_absentextra002_v1_ft1`
- 初始化：
  - `v126`
- teacher：
  - `v109`
- 结构保持：
  - split-present present head only fine-tune
  - `present_gate_power = 2.5`
  - `present_veto_mode = complement_ratio`
  - `present_veto_strength = 0.5`
- 仅新增：
  - `absent_extra_weight = 0.02`
  - `absent_extra_focus_recipes = target_clean_speech`
  - `absent_extra_focus_patterns = target_absent_head / target_absent_tail`

## `v127` relative `v126`

- synthetic 四条固定验收全线转负：
  - abstention `-0.1881 dB`
  - same-gender keep `-0.1060 dB`
  - hard-present keep `-0.1184 dB`
  - artifact proxy `-0.0378 dB`
- 这说明：
  - 真实 absent supervision
    不是“白送的局部收益”；
  - 它一接到当前 present-head 路径上，
    就会立刻开始伤 present-side keep guardrail。

## Whole Near-Real

- 计数：
  - `more_interference_leaky = v127:3, tie:1`
  - `better_retention_minus_leak = v126:2, tie:1, not_applicable:1`
- 关键样本：
  - `near_real_0009`
    - `delta_interference_capture_db = +0.5250 dB`
    - whole 口径上没有继续改善 absent suppression
  - `near_real_0007`
    - `delta_target_capture_db = +0.2669 dB`
    - `delta_interference_capture_db = +6.3493 dB`
    - `delta_retention_minus_leak_db = -6.0824 dB`
  - `near_real_0003`
    - `delta_target_capture_db = -0.0034 dB`
    - `delta_interference_capture_db = +1.0259 dB`
    - `delta_retention_minus_leak_db = -1.0293 dB`
  - `near_real_0006`
    - `delta_target_capture_db = +0.0028 dB`
    - `delta_interference_capture_db = +0.9269 dB`
    - `delta_retention_minus_leak_db = -0.9241 dB`
- 含义：
  - 这轮不是简单的“目标也压没了”；
  - 更准确地说，
    是它把 present 样本的 overall leak / tradeoff
    明确推坏了。

## Overlap-Local

- 这里能看到本轮唯一真实正信号：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = -9.3758 dB`
    - `delta_total_interference_capture_db = -9.3758 dB`
  - 说明真正的 absent interval supervision
    确实能在 local absent window 上强力压 leak。
- 但同时也能看到为什么它不能保留：
  - `near_real_0007`
    - `delta_speech_interference_capture_db = -3.3370 dB`
    - `delta_total_interference_capture_db = +2.0839 dB`
    - `delta_retention_minus_speech_leak_db = +3.5401 dB`
    - `delta_retention_minus_total_leak_db = -1.8808 dB`
    - 即：
      - speech-only local leak 确实变干净；
      - 但 total leak / overall tradeoff 反而更差。
  - `near_real_0003`
    - `delta_speech_interference_capture_db = +0.9441 dB`
    - `delta_retention_minus_speech_leak_db = -0.9475 dB`
  - `near_real_0006`
    - `delta_speech_interference_capture_db = +1.3454 dB`
    - `delta_retention_minus_speech_leak_db = -1.3430 dB`

## Conclusion

- `v127` 证明了两件事：
  1. 真正的 absent interval supervision
     在 `0009` 这类 target-absent local window 上
     是真实有效的；
  2. 但把这条监督直接灌到当前
     `split-present present-head-only`
     路径里，
     会把 present-side whole / total-leak tradeoff
     一起拖坏。
- 因此本轮不能解释成：
  - absent 方向无效；
  - 或 `v126` 已经足够。
- 更准确的裁决是：
  - 当前错的是 routing / coupling，
    不是 absent supervision 本体。

## Next

1. 收口 `v127`
   - 不导听审
2. 不继续扫：
   - `absent_extra_weight`
   - `true absent anchor` 在当前 present-head-only 路径上的同构微调
3. 若继续打 `target-absent veto`
   - 默认需要把真实 absent supervision
     从当前 present-head update 路径里解耦；
   - 例如：
     - 单独 branch / controller path
     - 或只在 target-absent local 窗内生效、
       且不会把 present sample 的 total leak 推坏的局部目标
4. 当前主线结论保持：
   - `v126`
     仍是 split local-control semantics
     的最佳 automatic continuation；
   - `v127`
     只作为“true absent anchor supervision 有效但 current routing 错位”的机制证据保留。
