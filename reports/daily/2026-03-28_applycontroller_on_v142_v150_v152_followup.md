# 2026-03-28 apply-controller on `v142`: `v150 / v151 / v152` follow-up

## Summary

- 在
  `v149`
  证明
  `predicted_activity`
  这类
  cancel-ratio-derived
  direct-apply
  会系统性打坏 guardrail 之后，
  这轮改测更显式的：
  - decoupled
    `apply-controller head`
- 目标是拆开两件事：
  - `branch_overlap_cancel_head`
    负责“估计减什么”
  - `apply-controller`
    负责“哪里真的写回输出”
- 结果分三段：
  - `v150`
    只训练 controller，
    practical no-op
  - `v151`
    训练 controller + cancel，
    fixed checks
    基本 near-tie，
    但 targeted local proxy
    明显更差
  - `v152`
    把 selector
    从 `3 / 203`
    扩到
    `33 / 99`
    后，
    fixed checks
    与 local proxy
    一起转负

最终结论：

- `apply-controller`
  这条 `v142`
  子线先收口
- 问题不只是
  `3 / 203`
  selector 太稀；
  即便扩到 broader hardlocal bundle，
  也仍然会开始伤：
  - abstention
  - hard-present keep
  - artifact proxy
  - local speech-leak proxy

## Code Change

- 已新增：
  `enable_branch_overlap_cancel_apply_controller`
- 语义是：
  - 用一个独立的
    sigmoid head
    去缩放
    overlap-cancel 的
    direct-apply blend
  - 不直接改
    cancel estimate
- 代码位置：
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `scripts/train/train_stft_mask_baseline.py`

## `v150 = v142 + apply-controller only`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v150_v142_applycontroller_only_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `None`
  - 显式使用
    `--disable-teacher-checkpoint-metadata-fallback`
- manifest：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
- overlap-cancel selector：
  - 精确复用
    `v142`
    的 hardlocal
    `focus_sample_ids`
  - 命中：
    - train `3 / 203`
    - val `3 / 63`
- trainable prefixes：
  - `branch_overlap_cancel_apply_controller_head`

## Fixed Checks relative `v142`

- abstention `-0.0030 dB`
- same-gender keep `-0.0016 dB`
- hard-present keep `-0.0013 dB`
- artifact proxy `-0.0010 dB`
- local speech leak proxy `+0.0024 dB`

结论：

- `v150`
  是 practical no-op
- 仅训练 controller，
  不足以把
  `v142`
  的输出真正推起来

## `v151 = v142 + apply-controller + cancel`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v151_v142_applycontroller_pluscancel_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `None`
- manifest / selector：
  - 与 `v150`
    相同
  - 仍是：
    - train `3 / 203`
    - val `3 / 63`
- trainable prefixes：
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_apply_controller_head`

## Training Signal

- 末轮：
  - `train_overlap_cancel_waveform_l1 = 0.0066462`
  - `val_overlap_cancel_waveform_l1 = 0.0283286`
  - `train_overlap_cancel_target_projection_ratio = 0.0000056`
  - `val_overlap_cancel_target_projection_ratio = 0.0000674`

这说明：

- `v151`
  不是 no-op
- controller + cancel
  的 joint route
  确实吃到了训练信号

## Fixed Checks relative `v142`

- abstention `-0.0108 dB`
- same-gender keep `+0.0261 dB`
- hard-present keep `-0.0397 dB`
- artifact proxy `-0.0215 dB`

## Targeted Local Proxy Check

- `val_manifest_local_speech_leak_proxy_v1`
  relative `v142`：
  - `avg_sisdr_delta_db = -0.1692 dB`
  - `improved = 0`
  - `regressed = 3`

结论：

- `v151`
  不是 guardrail 爆炸式失败，
  但也没有把目标 local 问题拉正
- 在最关键的
  `local_speech_leak_proxy_v1`
  上，
  它比
  `v142`
  更差，
  直接 reject

## `v152 = v142 + apply-controller + cancel on broader hardlocal bundle`

## Why Run `v152`

- `v150 / v151`
  还留了一个歧义：
  - apply-controller
    家族无效，
    可能是机制不对
  - 也可能只是
    `v142`
    的
    `3 / 203`
    selector
    太稀
- 所以
  `v152`
  只改一件事：
  - 保持
    `v151`
    的机制不变
  - 把训练域扩到
    `v145`
    用过的 broader
    hardlocal bundle

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v152_v142_applycontroller_pluscancel_hardlocalbundle_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `None`
- manifest：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_bundle_v1.jsonl`
- overlap-cancel selector：
  - 复用
    `v145`
    的 broader speech-local bundle
  - 命中：
    - train `33 / 99`
    - val `7 / 37`
- trainable prefixes：
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_apply_controller_head`

## Training Signal

- overlap-cancel selector
  已明显变宽：
  - train `33 / 99`
  - val `7 / 37`
- 末轮：
  - `train_overlap_cancel_waveform_l1 = 0.039313`
  - `val_overlap_cancel_waveform_l1 = 0.023974`
  - `train_overlap_cancel_target_projection_ratio = 0.000585`
  - `val_overlap_cancel_target_projection_ratio = 0.000098`

这说明：

- `v152`
  不是稀疏 selector
  下的 no-op
- 更宽 training subdomain
  的确把
  apply-controller
  这条 route
  推起来了

## Fixed Checks relative `v142`

- abstention `-0.1635 dB`
- same-gender keep `-0.0032 dB`
- hard-present keep `-0.1439 dB`
- artifact proxy `-0.0906 dB`

## Targeted Local Proxy Check

- `val_manifest_local_speech_leak_proxy_v1`
  relative `v142`：
  - `avg_sisdr_delta_db = -0.1433 dB`
  - `improved = 0`
  - `regressed = 3`

## Verdict

- `v152 = reject`
- 不补 near-real
- 不出听审

## New Boundary

- `apply-controller`
  这条
  `v142`
  output apply path
  当前已经补齐三种结果：
  - `v150`
    controller-only
    practical no-op
  - `v151`
    narrow selector
    下 signal-on，
    但 local proxy
    更差
  - `v152`
    broader selector
    下不再是 no-op，
    却开始稳定伤：
    - abstention
    - hard-present keep
    - artifact proxy
    - local speech-leak proxy
- 所以：
  - 这条家族的问题
    不是单纯
    selector 太稀
  - 而是当前
    `apply-controller + direct subtract`
    语义本身
    不适合作为
    `v142`
    的安全 continuation

## Final Decision

- 保留：
  - `v126`
    继续作为全局最佳 automatic continuation
  - `v142`
    继续作为
    head-only bounded direct-apply
    子线最佳 continuation
- 收口：
  - `v150`
    controller-only no-op
  - `v151`
    narrow-selector joint route
  - `v152`
    broader-selector joint route
- 当前默认不再继续扫：
  - `apply-controller` init bias
  - `apply-controller only`
  - `apply-controller + cancel`
  - `apply-controller` selector width
- 如果继续，
  默认应改做：
  - 不直接重写 final output 的
    local-window-only 机制
  - 或完全不经
    overlap-cancel direct subtract
    的
    monitor-only / auxiliary-only
    局部作用路径
