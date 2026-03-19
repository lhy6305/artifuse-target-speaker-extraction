# 2026-03-19 `v40 / v41` absent-side follow-up results

## 背景

`v39` 之后，这条 absent-side follow-up 实际分成了两条很具体的收紧路线：

- `v40`：
  - 保留 `v39` 的 `v5 cleancarve` 思路；
  - 但把会与 friend-side exact family 重叠的 `reconstruction_extra` sample-id 显式剔除。
- `v41`：
  - 不再沿 `v5 cleancarve` metadata selector；
  - 改为直接使用更贴近 current-signal clean absent 假设的
    `guodegang_absent_proxy_v6_currentsignal_cleanonly`
    sample-id allowlist，
    挂轻量 `waveform-only reconstruction_extra`。

本次补文档的核心目的不是重新解释一遍“为什么失败”，
而是把这两条线最容易遗忘的裁决证据写死：

- exact `target_full`
- near-real `speech_leak_like (0004)`
- near-real `guodegang_anchor_120s`
- near-real `guodegang_absent_480s`
- `guodegang_absent_proxy_v6_currentsignal_cleanonly` 本体

避免下一次只记得“又 failed 了”，却忘了到底是哪一项、坏到了什么程度。

## `v40 = v39 selected carve-out - exact overlap`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v40_v32_absent_reconstructionextra_v6_cleancarve_noexactoverlap_wave_ft1`
- 目标：
  - 先验证 `v39` 的问题里，
    到底有多少只是 selector crossfire；
  - 即：
    去掉与 friend-side exact family 的 overlap 后，
    real gate 会不会自然回正。

### relative to `v19`

- default：
  - `+0.056136 dB`
- near-real speech probe overall：
  - `-0.090659 dB`
- exact `target_full`：
  - `-0.467909 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.086817 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.099242 dB`
- near-real `guodegang_absent_480s`：
  - `-0.057473 dB`
- `guodegang_absent_proxy_v6_currentsignal_cleanonly`：
  - `-0.424082 dB`

### relative to `v32` 的 `friend_speech_leak_followup_gate`

- `overall_pass = false`
- failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

### 裁决

- `v40` 不能保留。
- 这条结果说明：
  - 把 overlap 去掉，确实把 broad near-real overall 控在 gate 容忍区里；
  - 但 `exact target_full` 仍明显更差，
    `guodegang` 两条 real floor 也没有回正；
  - 连 `proxy_v6` 本体也仍是负增益，
    所以 `selector crossfire`
    不是当前 absent-side 失败的唯一主因。

## `v41 = v32 + reconstruction_extra(proxy_v6 current-signal clean-only allowlist)`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v41_v32_absent_reconstructionextra_v6_currentsignal_cleanonly_wave_ft1`
- init：
  - `v32`
- manifest：
  - train `139`
  - val `38`
- `reconstruction_extra` 配置：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `reconstruction_extra_stft_weight = 0.0`
  - `interference_extra_weight = 0.0075`
  - `reconstruction_extra_focus_sample_ids = proxy_v6 currentsignal cleanonly allowlist`
- selector 命中：
  - train：
    - `reconstruction_extra = 46 / 139`
    - `interference_extra = 7 / 139`
  - val：
    - `reconstruction_extra = 13 / 38`
    - `interference_extra = 3 / 38`

### relative to `v19`

- default：
  - `+0.066352 dB`
- exact proxy overall：
  - `+0.036695 dB`
- exact `target_full`：
  - `-0.325134 dB`
- near-real speech probe overall：
  - `-0.109792 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.062535 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.258474 dB`
- near-real `guodegang_absent_480s`：
  - `-0.112892 dB`
- `guodegang_absent_proxy_v6_currentsignal_cleanonly`：
  - `-0.627418 dB`

### relative to `v32` 的 `friend_speech_leak_followup_gate`

- `overall_pass = false`
- failed：
  - `speech_probe_overall_floor`
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

### 裁决

- `v41` 不能保留。
- 这条结果有两个必须记住的点：
  - exact proxy overall 虽然转成了 `+0.036695 dB`，
    但真正关键的 exact `target_full`
    仍是 `-0.325134 dB`；
  - `proxy_v6` 本体不但没转正，
    反而比 `v32 / v39 / v40` 更差：
    - `v32 = -0.172916 dB`
    - `v39 = -0.424309 dB`
    - `v40 = -0.424082 dB`
    - `v41 = -0.627418 dB`

大白话讲：

- `v41` 不是“代理看起来更贴近 current signal，所以 real absent 只差一点点没过 gate”；
- 而是这条 `proxy_v6 currentsignal cleanonly` 线本身现在就在反着走，
  同时还把：
  - `guodegang_anchor`
  - `guodegang_absent`
  一起拖得更差。

## 当前阶段裁决

- `v40`：
  - 证明“仅去掉 exact overlap”不足以救回 absent-side real gate。
- `v41`：
  - 证明“current-signal clean-only 的 `proxy_v6`”目前也不是可保留的 real absent protection proxy。

因此当前 absent-side 这轮 follow-up 更准确的结论应写成：

1. `selector crossfire` 不是唯一问题。
2. 现有 `proxy_v6` family 本体也没有给出正向保护信号。
3. 下一条若继续做 absent-side protection，
   不能只是：
   - 继续微调 `proxy_v6 currentsignal cleanonly`
   - 或继续围绕当前 allowlist / overlap 做小修小补。
