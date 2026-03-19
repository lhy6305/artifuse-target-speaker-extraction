# 2026-03-19 `v44` proxy_v7 STFT-only follow-up

## 背景

`v42 / v43` 已经把 `proxy_v7` 这条线收紧得很清楚：

- `proxy_v7` 本体成立；
- `guodegang_anchor / absent`
  两条 real floor
  也都能转正；
- 但当前 `reconstruction_extra`
  routing
  仍 clear fail 于：
  - exact `target_full`
  - `speech_leak_like (0004)`

同时 `v43` 又证明：

- 只把 `waveform-only reconstruction_extra`
  权重从 `0.005`
  缩到 `0.0025`
  基本是 no-op。

因此本轮不继续扫微幅 wave 权重，
而是改成一个更像 routing mode 变化的 quick follow-up：

- 保留 `proxy_v7`
- 改成 `reconstruction_extra_stft_only`

## `v44 = v32 + reconstruction_extra_stft_only(proxy_v7)`

### 训练定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v44_v32_absent_reconstructionextra_v7_highoverlap_lowtargettransient_lowinttrans_stft001_ft1`
- init：
  - `v32`
- manifest：
  - 继续复用 `v42` merged manifest：
    - train `129`
    - val `37`
- `reconstruction_extra`：
  - `reconstruction_extra_waveform_weight = 0.0`
  - `reconstruction_extra_stft_weight = 0.01`
  - `reconstruction_extra_focus_sample_ids = proxy_v7 all ids`
- 其他 branch：
  - 保持 `v42 / v43` 相同

## 结果

### relative to `v19`

- default：
  - `+0.072833 dB`
- exact proxy overall：
  - `-0.302238 dB`
- exact `target_full`：
  - `-0.647221 dB`
- near-real speech probe overall：
  - `-0.077362 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.110539 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.113703 dB`
- near-real `guodegang_absent_480s`：
  - `+0.029381 dB`
- `proxy_v7`：
  - `+0.359405 dB`

### relative to `v32` gate

- `overall_pass = false`
- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

## 与 `v42 / v43` 的关系

`v44` 不是完全没变化。

相对 `v42`：

- exact `target_full`
  略有回收：
  - `-0.664459 -> -0.647221`
- `speech_leak_like (0004)`
  也略有回收：
  - `-0.113430 -> -0.110539`

但代价也很明确：

- default 更弱：
  - `+0.077955 -> +0.072833`
- `proxy_v7` 本体更弱：
  - `+0.444459 -> +0.359405`
- `guodegang_anchor / absent`
  仍为正，
  但都比 `v42 / v43` 略弱：
  - anchor：
    - `+0.126568 -> +0.113703`
  - absent：
    - `+0.031863 -> +0.029381`

大白话讲：

- `stft_only`
  确实比 `waveform_only`
  稍微减轻了一点 friend-side 回退；
- 但改善幅度太小，
  还不足以把这条线从 clear fail
  拉到 near-tie；
- 同时还要付出：
  - default 变弱
  - `proxy_v7` 本体变弱
  的代价。

## 裁决

`v44` 不保留。

这条结果说明：

1. `routing mode` 变化
   确实比微幅 wave 权重缩放更有信号；
2. 但单纯改成 `reconstruction_extra_stft_only`
   还不够；
3. 当前下一条若继续沿 `proxy_v7`，
   仍应优先考虑：
   - 更强的 branch-level decoupling
   - 或更本质的 routing 重写
   而不是继续在
   `waveform_only / stft_only`
   之间做很局部的小切换。
