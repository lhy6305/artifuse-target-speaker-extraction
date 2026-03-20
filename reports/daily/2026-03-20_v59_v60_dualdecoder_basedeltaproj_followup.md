# 2026-03-20 `v59 / v60` dual-head `base-delta-interference projection` follow-up

## 背景

`v57 / v58` 已说明：

- exact-family `base-align`
  是对题的 protect primitive；
- 但它的问题也已经很清楚：
  - weight 重了，
    `proxy_v7`
    会被直接压塌；
  - weight 轻了，
    `speech_leak_like (0004)`
    又重新 clear fail。

因此本轮正式测试：

- `interference_extra_base_delta_projection_weight`

目标不是再把整段 branch 输出往 base 拉回，
而是只压：

- branch output
  相对 frozen base output
  的增量里，
  落在 interference 方向上的那一部分。

大白话讲：

- 不是“你别动太多”；
- 而是：
  - “你可以动，
     但别把新增改动用在更像干扰泄漏的方向上”。

## 工程前提

上一轮已补好：

- `interference_extra_base_delta_projection_weight`
- `interference_extra_base_delta_projection_ratio`
- `interference_extra` selector 激活与 summary 落盘

并已在：

- `tmp/smoke_branch_decoder_base_delta_projection`

完成 1-step smoke。

因此本轮结果可以直接解释成：

- protect primitive 本身的实验边界，
而不是 plumbing 问题。

## `v59 = dual-head + proxy_v7 reconstruction + base-delta-interference projection (0.005)`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v59_v32_absent_dualdecoder_v7_wave_basedeltaproj_w005_ft1`
- init：
  - `v32`
- dual-head：
  - `enable_branch_decoder_head = true`
- 仅训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- absent-side：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `focus = proxy_v7`
- friend-side protect：
  - `interference_extra_base_delta_projection_weight = 0.005`
  - `focus = v30 exact 10 ids`

### selector 与 loss 量级

- `interference_extra`
  selector 命中：
  - train `7 / 129`
  - val `3 / 37`
- 但新 protect 项量级非常小：
  - train `interference_extra_base_delta_projection_ratio`
    = `2.0131949656154081e-07`
  - val
    = `1.8925945539649546e-07`
- 对照同批样本的：
  - train `interference_extra_projection_ratio`
    = `0.001460227579104178`
  - val
    = `0.00017132485518231988`

这说明：

- selector 的确命中了；
- 但这条新 protect primitive
  在当前 exact ids 上，
  实际惩罚到的量非常接近 `0`。

### 结果

relative to `v19`：

- default：
  - `+0.129068 dB`
- exact proxy overall：
  - `-0.582703 dB`
- exact `target_full`：
  - `-0.983311 dB`
- near-real speech probe overall：
  - `-0.049822 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.117378 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.157752 dB`
- near-real `transient_like (0006)`：
  - `+0.213407 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.356478 dB`
- near-real `guodegang_absent_480s`：
  - `+0.070337 dB`
- `proxy_v7`：
  - `+1.597651 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- clear fail：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
- pass：
  - default
  - speech probe overall
  - `guodegang_anchor`
  - `guodegang_absent`

### 裁决

`v59` 不保留。

解释：

- 这条 primitive
  没有把 dual-head 拉向
  `0004` protect；
- 它更像继续允许：
  - `proxy_v7 / guodegang`
    很强；
  - 但 friend-side `target_full / 0004`
    继续掉。

也就是说：

- 它并不像 `base-align`
  那样会“保护过头”；
- 更像：
  - 基本没有真正碰到
    当前坏掉的那部分 friend-side 行为。

## `v60 = stronger base-delta-interference projection (0.02)`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v60_v32_absent_dualdecoder_v7_wave_basedeltaproj_w02_ft1`
- 相比 `v59`
  仅改：
  - `interference_extra_base_delta_projection_weight = 0.02`

### selector 与 loss 量级

- `interference_extra`
  selector 命中仍相同：
  - train `7 / 129`
  - val `3 / 37`
- 新 protect 项量级仍然极小：
  - train `interference_extra_base_delta_projection_ratio`
    = `1.9598214456009678e-07`
  - val
    = `1.7825688871653256e-07`

### 结果

relative to `v19`：

- default：
  - `+0.129255 dB`
- exact proxy overall：
  - `-0.561410 dB`
- exact `target_full`：
  - `-0.950958 dB`
- near-real speech probe overall：
  - `-0.050620 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.116784 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.156840 dB`
- near-real `transient_like (0006)`：
  - `+0.207955 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.347640 dB`
- near-real `guodegang_absent_480s`：
  - `+0.068271 dB`
- `proxy_v7`：
  - `+1.562356 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- clear fail：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

### 裁决

`v60` 也不保留。

解释：

- `v60`
  相比 `v59`
  几乎只是微小扰动；
- 没有出现：
  - `0004`
    被明显拉回；
  - 或 `target_full`
    明显收敛。

因此：

- 继续扫这条 weight
  已没有价值。

## 当前阶段结论

`v59 / v60`
把 `base-delta-interference projection`
这条线的边界写得更清楚了：

1. 它不是 plumbing 问题。
   - selector 已真实命中：
     - train `7 / 129`
     - val `3 / 37`
2. 但它在当前 exact ids 上
   的实际惩罚量非常接近 `0`。
   - 量级只有 `~1e-7`
3. 因而它不会像 `base-align`
   那样形成强保护；
   - 也不会把 dual-head
     拉向 `speech_leak_like (0004)` 的 keep 区；
   - 更像允许：
     - `proxy_v7 / guodegang`
       继续很强，
     - friend-side `target_full / 0004`
       继续 clear fail。

当前更准确的结论应写成：

- `base-delta-interference projection`
  这条 primitive
  在当前 `v30 exact 10 ids`
  上，
  不是值得继续扫权重的方向；
- 它没有真正约束到
  现在坏掉的 `0004-like speech-leak`
  行为。

## 下一步默认更新

当前默认下一步不再继续扫：

- `interference_extra_base_delta_projection_weight`
  的近邻值。

更合理的下一步应更新为：

1. 明确放弃把：
   - “branch 相对 base 的 interference-like delta”
   当成当前 `0004` protect 的默认答案；
2. 下一条 protect objective
   需要更直接面向：
   - `target_full`
   - `speech_leak_like (0004)`
   的 target-retention / speech-leak 约束；
3. 仍继续保留：
   - dual-head plumbing
   - `proxy_v7`
   - `v32` frozen base anchor
   这三项资产。
