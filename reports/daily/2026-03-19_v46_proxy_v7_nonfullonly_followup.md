# 2026-03-19 `v46` proxy_v7 nonfull-only follow-up

## 背景

`v45` 已经说明：

- `proxy_v7 full / nonfull`
  分开 routing
  比单一路由更像正确方向；
- 但 friend-side 两条：
  - exact `target_full`
  - `speech_leak_like (0004)`
  仍 clear fail。

因此下一步最直接的排错问题是：

- 当前冲突到底主要来自：
  - `proxy_v7 full`
    这批最像 friend-side 冲突区的行；
- 还是说：
  - 即便只让 `nonfull`
    这批 absent-like 行吃 reconstruction，
    也仍会通过参数耦合把 friend-side 两条拖坏。

## `v46 = nonfull-only reconstruction on proxy_v7`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v46_v32_absent_reconstruction_nonfullonly_v7_wave_ft1`
- init：
  - `v32`
- manifest：
  - 继续复用 `v42` merged manifest
    - train `129`
    - val `37`
- reconstruction：
  - 只对 `proxy_v7 nonfull` 打开：
    - train `16`
    - val `3`
  - `reconstruction_waveform_weight = 0.005`
- 不再给 `proxy_v7 full`
  任何 absent-side reconstruction branch

大白话讲：

- `target_full`
  这批 proxy rows
  完全退出 absent reconstruction；
- 只保留
  `absent_head / tail / intermittent`
  这批更像真实 absent 语义的 nonfull 行。

## 结果

### relative to `v19`

- default：
  - `+0.077715 dB`
- exact proxy overall：
  - `-0.315450 dB`
- exact `target_full`：
  - 仍为负，
    且几乎没变：
    - `-0.315450` overall
    - exact `target_full` 仍由 gate 判为 clear fail
- near-real speech probe overall：
  - `-0.077905 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.113260 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.126034 dB`
- near-real `guodegang_absent_480s`：
  - `+0.031888 dB`
- `proxy_v7`：
  - `+0.441273 dB`

### relative to `v32` gate

- `overall_pass = false`
- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

## 当前最关键的结论

这条实验真正重要的不是它又 failed 了一次，
而是它把问题继续收紧了：

1. 当前冲突不只是
   `proxy_v7 full`
   这批样本直接撞到 friend-side exact 区。
2. 因为即便把 `full`
   全部从 absent reconstruction 里拿掉，
   friend-side 两条仍几乎保持：
   - exact `target_full`
   - `speech_leak_like (0004)`
   的 clear fail。
3. 这说明当前 absent-side reconstruction
   更像是在通过全局参数更新
   改写 shared behavior，
   而不是只在局部冲突样本上出问题。

## 与前几条的关系

相对 `v42`：

- default：
  - `+0.077955 -> +0.077715`
- `proxy_v7`：
  - `+0.444459 -> +0.441273`
- `guodegang_anchor / absent`
  仍保持几乎同级正向：
  - anchor：
    - `+0.126568 -> +0.126034`
  - absent：
    - `+0.031863 -> +0.031888`
- friend-side 两条也几乎没明显回收：
  - `speech_leak_like (0004)`：
    - `-0.113430 -> -0.113260`
  - gate 仍是同样两条 clear fail

这意味着：

- 只靠把 `full` 从 absent reconstruction
  里拿掉，
  并不能自然解耦 friend-side clear fail。

## 裁决

`v46` 不保留。

但这条实验给出了当前最关键的新边界：

- 问题不只是
  `proxy_v7 full`
  的局部 selector 冲突；
- 当前需要的已经不是
  “再换哪一组 proxy 行”
  或“再把哪一组拿掉”，
  而是更本质的：
  - branch-level parameter decoupling
  - 或更强的 objective isolation。

## 下一步建议

若继续自动推进，默认优先级应进一步收紧为：

1. 保留：
   - `proxy_v7`
2. 不继续：
   - 单纯删掉 `full`
   - 单纯切 `wave / stft`
   - 或微幅权重缩放
3. 下一条默认应转向：
   - 更强的 branch-level decoupling
   - 或真正的参数/目标隔离
   而不是继续在同一张共享训练图里做 selector 细修。
