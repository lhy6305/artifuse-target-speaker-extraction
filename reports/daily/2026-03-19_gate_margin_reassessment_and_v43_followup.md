# 2026-03-19 gate margin reassessment and `v43` follow-up

## 背景

这轮用户提醒很关键：

- 当前一些分支的数值差异很小；
- 不应把所有“略低一点”的项都直接等价成
  “方向错误”；
- 至少需要把：
  - `near_tie`
  - `clear_fail`
  分开。

本轮因此做了三件事：

1. 给当前 absent / friend-side 主 gate
   补上三档 judgement；
2. 用这套 judgement
   回看最近 `v39-v42`；
3. 在确认没有漏掉 keep 分支后，
   继续做一条最直接的 `v42` follow-up：
   - `v43 = proxy_v7 + lighter reconstruction_extra waveform weight`

## 结果一：主 gate 已补成三档 judgement

更新脚本：

- `scripts/eval/gate_friend_speech_leak_followup.py`

新增规范：

- `overall_pass`
  继续保留原先的严格布尔口径，
  兼容旧流水线；
- 同时新增：
  - `overall_judgement`
  - `near_tie_rules`
  - `clear_fail_rules`
  - 每条 rule 的：
    - `candidate_minus_floor`
    - `judgement`

当前默认 `near_tie` 口径：

- `near_tie_margin_db = 0.03`

解释：

- `pass`：
  - `candidate >= required_floor`
- `near_tie`：
  - `candidate < required_floor`
  - 但只低于 floor `<= 0.03 dB`
- `clear_fail`：
  - 低于 floor `> 0.03 dB`

注意：

- 这套三档 judgement
  只改变“怎么解释 failed rule”；
- 不会自动把 `overall_pass`
  放宽成通过。

## 结果二：回看 `v39-v42` 后，没有漏掉 keep 分支

### `v39`

- `overall_judgement = fail`
- `near_tie_rules = []`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

结论：

- 不是边缘误判；
- 是 clear fail。

### `v40`

- `overall_judgement = fail`
- `near_tie_rules = []`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

结论：

- 也不是边缘误判；
- 是 clear fail。

### `v41`

- `overall_judgement = fail`
- `near_tie_rules`：
  - `speech_probe_overall_floor`
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
- `clear_fail_rules`：
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

关键差值 relative to `v32`：

- speech overall：
  - `-0.009327 dB` below floor
- exact `target_full`：
  - `-0.021816 dB` below floor
- `speech_leak_like (0004)`：
  - `-0.020855 dB` below floor
- `guodegang_anchor_120s`：
  - `-0.192590 dB`
- `guodegang_absent_480s`：
  - `-0.099666 dB`

结论：

- `v41` 的确存在“局部 near_tie、不是所有项都明显坏”的事实；
- 但它并不是被漏掉的 keep 分支，
  因为 real `guodegang` 两条仍是 clear fail。

### `v42`

- `overall_judgement = fail`
- `near_tie_rules = []`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

结论：

- `v42` 也不是“被严格比较错杀”的分支；
- 它的真正意义仍是：
  - `proxy_v7` 本体成立；
  - 但 routing clear fail 于 friend-side 两条。

## 当前回看结论

因此这轮可以明确写死：

1. 最近 `v39-v42`
   没有漏掉一个应当回收为 keep 的分支。
2. 唯一需要修正的不是结论，
   而是表述：
   - `v41`
     不该笼统写成“全线方向都错”；
   - 更准确应写成：
     - friend-side 若干 rule 只是 near-tie；
     - 但 real `guodegang` floor 仍 clear fail。

## 结果三：继续训练 `v43 = v42` 的 lighter-weight follow-up

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v43_v32_absent_reconstructionextra_v7_highoverlap_lowtargettransient_lowinttrans_wave00025_ft1`
- 与 `v42` 唯一差别：
  - `reconstruction_extra_waveform_weight`
    从 `0.005`
    降到 `0.0025`
- 其余：
  - merged manifest
  - `proxy_v7` sample ids
  - base transient / interference / absent
  - friend-side exact `interference_extra`
  全部保持不变

### `v43` relative to `v19`

- default：
  - `+0.077610 dB`
- exact proxy overall：
  - `-0.315729 dB`
- exact `target_full`：
  - `-0.663965 dB`
- near-real speech probe overall：
  - `-0.077980 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.113233 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.125676 dB`
- near-real `guodegang_absent_480s`：
  - `+0.031660 dB`
- `proxy_v7`：
  - `+0.440865 dB`

### relative to `v32` gate

- `overall_pass = false`
- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

### 与 `v42` 的对照

`v42 -> v43` 的变化量几乎可以视为不动：

- default：
  - `+0.077955 -> +0.077610`
- exact `target_full`：
  - `-0.664459 -> -0.663965`
- `speech_leak_like (0004)`：
  - `-0.113430 -> -0.113233`
- `guodegang_anchor_120s`：
  - `+0.126568 -> +0.125676`
- `guodegang_absent_480s`：
  - `+0.031863 -> +0.031660`
- `proxy_v7`：
  - `+0.444459 -> +0.440865`

## 裁决

`v43` 不保留。

这条结果说明：

- 在当前训练预算下，
  把 `proxy_v7 reconstruction_extra_waveform_weight`
  从 `0.005`
  减半到 `0.0025`
  几乎是 no-op；
- 因而下一条若继续沿 `proxy_v7`，
  不值得再做这一类微幅 weight rescale。

## 当前阶段结论

1. 三档 judgement 现在已经正式接入主 gate。
2. 最近 `v39-v42`
   没有漏掉 keep 分支。
3. `v41`
   应改写为：
   - 局部 near-tie
   - 但 real floor clear fail。
4. `v43`
   证明：
   - `proxy_v7` 路线上的微幅 waveform weight 缩放
     基本不改变结论。

## 下一步建议

若继续自动推进，默认优先级应收紧为：

1. 保留：
   - `proxy_v7`
2. 不继续：
   - `proxy_v6`
   - `proxy_v7` 的微幅 waveform weight rescale
3. 下一条默认改动方向应更像：
   - routing mode 变化
   - 或 branch-level decoupling 变化
   而不是继续扫
   `0.005 -> 0.0025 -> 0.001`
   这种小数点级缩放。
