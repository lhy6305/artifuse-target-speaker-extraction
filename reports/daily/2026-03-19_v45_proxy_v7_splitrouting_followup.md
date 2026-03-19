# 2026-03-19 `v45` proxy_v7 split-routing follow-up

## 背景

`v42 / v43 / v44` 已经把 `proxy_v7` 路线收紧成三个事实：

1. `proxy_v7` 本体成立；
2. `guodegang_anchor / absent`
   两条 real floor
   可以稳定保持正向；
3. 但无论是：
   - `waveform_only`
   - `stft_only`
   都还 clear fail 于：
   - exact `target_full`
   - `speech_leak_like (0004)`

因此本轮继续推进的方向不再是：

- 微幅权重缩放；
- 或单一损失域切换；

而是做一次更接近 branch-level decoupling 的近似：

- 把 `proxy_v7` 内部按 `temporal_pattern`
  显式拆成：
  - `full`
  - `nonfull`
- 再给这两组挂不同 reconstruction branch。

## `v45 = split routing on proxy_v7`

### 分组

本轮先把 `proxy_v7` sample ids 拆成两组：

- full：
  - train `17`
  - val `5`
- nonfull：
  - train `16`
  - val `3`

对应文件：

- `sample_ids_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans_full_all.txt`
- `sample_ids_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans_nonfull_all.txt`

### 训练定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v45_v32_absent_reconstruction_split_v7_nonfullwave_fullstft_ft1`
- init：
  - `v32`
- manifest：
  - 继续复用 `v42` merged manifest
    - train `129`
    - val `37`
- reconstruction split：
  - base `reconstruction`：
    - selector = `proxy_v7 nonfull`
    - `reconstruction_waveform_weight = 0.005`
  - `reconstruction_extra`：
    - selector = `proxy_v7 full`
    - `reconstruction_extra_stft_weight = 0.01`

大白话讲：

- 把最可能冲到 friend-side exact 的 `target_full`
  行，
  从 `waveform_only`
  挪到相对保守一点的 `stft-only`；
- 而 `absent_head / tail / intermittent`
  这批 nonfull 行，
  继续保留 waveform reconstruction。

## 结果

### relative to `v19`

- default：
  - `+0.075720 dB`
- exact proxy overall：
  - `-0.307611 dB`
- exact `target_full`：
  - `-0.653286 dB`
- near-real speech probe overall：
  - `-0.077806 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.111924 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.119305 dB`
- near-real `guodegang_absent_480s`：
  - `+0.029907 dB`
- `proxy_v7`：
  - `+0.396169 dB`

### relative to `v32` gate

- `overall_pass = false`
- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

## 与 `v42 / v44` 的关系

`v45` 的位置大致落在：

- 比 `v44` 更保守地保住 default / `proxy_v7`；
- 但又没把 friend-side clear fail 拉回 enough。

相对 `v42`：

- friend-side 两条有一点点回收：
  - exact `target_full`
    - `-0.664459 -> -0.653286`
  - `speech_leak_like (0004)`
    - `-0.113430 -> -0.111924`
- 但回收幅度仍很小；
- 同时 default / `proxy_v7`
  也仍比 `v42` 略弱：
  - default：
    - `+0.077955 -> +0.075720`
  - `proxy_v7`：
    - `+0.444459 -> +0.396169`

相对 `v44`：

- default 更强：
  - `+0.072833 -> +0.075720`
- `proxy_v7` 更强：
  - `+0.359405 -> +0.396169`
- `guodegang_anchor / absent`
  也略强：
  - anchor：
    - `+0.113703 -> +0.119305`
  - absent：
    - `+0.029381 -> +0.029907`
- 但 friend-side 两条只比 `v44` 更差一点点：
  - exact `target_full`
    - `-0.647221 -> -0.653286`
  - `speech_leak_like (0004)`
    - `-0.110539 -> -0.111924`

结论是：

- `v45`
  确实比单纯 `stft_only`
  更平衡；
- 但它仍没有把最关键的两条 clear fail
  拉回到 near-tie。

## 裁决

`v45` 不保留。

但这条实验有一条值得记住的正面信息：

- 对 `proxy_v7`
  做 pattern-based split routing
  比单一路由更像“正确方向”；
- 它至少说明：
  - `full`
  和 `nonfull`
  这两类行，
  不应继续被当成同一种 absent-side reconstruction 入口。

## 当前阶段结论

1. `proxy_v7` 继续保留。
2. `v45` 仍 fail，
   但比 `v44`
   更接近一个合理的 split-routing primitive。
3. 下一条若继续自动推进，
   默认应继续沿：
   - `proxy_v7` 的内部语义拆分
   - 或更本质的 branch-level decoupling
   而不是回到：
   - 单一 `waveform_only`
   - 单一 `stft_only`
   - 或微幅权重缩放。
