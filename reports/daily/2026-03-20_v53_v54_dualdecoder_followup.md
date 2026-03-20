# 2026-03-20 `v53 / v54` dual-head / branch-local decoder follow-up

## 背景

`v49 -> v52` 已经把 adapter 路线压到头：

- simple residual adapter 不够；
- 给 adapter 看 reference 仍不够；
- 给 adapter 自己的 temporal model 也仍不够。

因此本轮正式执行：

- `dual-head / branch-local decoder`

目标不是再补 plumbing，
而是回答两件事：

1. 如果给 absent-side 一套真正独立的 decoder，
   它能不能在保住 `proxy_v7 / guodegang` 的同时，
   把 friend-side 拉回来；
2. 如果不行，
   问题是在：
   - dual-head 方向本身，
   还是：
   - guardrail routing / objective 仍然不对。

## 工程补充一：正式接入 dual-head

### `src/tse_prefix/models/stft_mask_baseline.py`

新增：

- `enable_branch_decoder_head`
- `branch_decoder_temporal_model`
- `branch_decoder_mask_head`
- `reset_branch_decoder_from_base()`

当前语义：

- shared 主分支继续输出：
  - `estimated_waveform_base`
- 若启用 dual-head：
  - 额外复制一套 decoder：
    - `branch_decoder_temporal_model`
    - `branch_decoder_mask_head`
  - 最终推理输出：
    - `estimated_waveform`
      = branch decoder output

关键点：

- branch decoder 不是随机冷启动；
- 从旧 checkpoint 初始化时，
  会先复制 base decoder 权重，
  再只学习自己的增量。

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `--model-enable-branch-decoder-head`

并补：

- 旧 checkpoint 初始化时允许缺失：
  - `branch_decoder_temporal_model.*`
  - `branch_decoder_mask_head.*`
- 若缺失则自动：
  - `reset_branch_decoder_from_base()`

### `tmp/smoke_branch_decoder_v53`

已先完成一轮 1-step smoke，
确认：

- `v32` 旧 checkpoint 兼容；
- branch decoder 自举初始化正常；
- 只训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
  能正常反传。

## `v53 = dual-head + proxy_v7 reconstruction only`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v53_v32_absent_dualdecoder_v7_wave_ft1`
- init：
  - `v32`
- manifest：
  - 与 `v42 / v52` 相同：
    - train `129`
    - val `37`
- model：
  - `enable_branch_decoder_head = true`
- trainable prefixes：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- loss：
  - 沿用 `v42` 同级配置；
  - 但当前这版 branch decoder
    真正吃到梯度的，
    只有：
    - `reconstruction_extra(proxy_v7)`

### 结果

relative to `v19`：

- default：
  - `+0.117316 dB`
- exact proxy overall：
  - `-0.518182 dB`
- exact `target_full`：
  - `-0.875034 dB`
- near-real speech probe overall：
  - `-0.047810 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.104842 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.141729 dB`
- near-real `transient_like (0006)`：
  - `+0.178616 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.296715 dB`
- near-real `guodegang_absent_480s`：
  - `+0.060516 dB`
- `proxy_v7`：
  - `+1.465092 dB`

relative to `v32` gate：

- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

### 裁决

`v53` 不保留。

但它暴露出一个关键工程事实：

- dual-head 本身不是没学到东西；
- 相反：
  - `proxy_v7`
  - `guodegang_anchor`
  - `guodegang_absent`
  都明显强于 `v42`；
- 真正的问题是：
  - branch decoder 这时只吃到了 absent-side 的 `proxy_v7 reconstruction`；
  - friend-side 的 extra guardrail
    还没有真正回流到这条新分支。

大白话讲：

- `v53`
  不是“dual-head 没方向”；
- 而是：
  - “dual-head 现在学得太单边，
     只顾 absent / guodegang，
     没有被 friend-side 约束住”。

## 工程补充二：把 extra guardrail 真正路由到 branch decoder

### `src/tse_prefix/pipeline/baseline_train.py`

新增：

- `extra_prediction`

当前语义：

- base 分支继续用：
  - `prediction`
- extra 分支相关项改为可独立吃：
  - `extra_prediction`

已切到 `extra_prediction` 的包括：

- `interference_extra_guard_sisdr`
- `transient_extra`
- `interference_extra`
- `absent_extra`

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `resolve_branch_extra_prediction(outputs)`

当前语义：

- 若存在 `branch_decoder_mask`，
  则：
  - `extra_prediction = outputs["estimated_waveform"]`
- 否则维持旧行为。

### `scripts/eval/eval_stft_mask_baseline.py`

同步补齐相同 routing，
避免后续 eval summary
把 branch decoder 的 extra 指标算错。

## `v54 = dual-head + proxy_v7 reconstruction + friend exact interference_extra`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v54_v32_absent_dualdecoder_v7_wave_exactguard_ft1`
- init / manifest / model / trainable prefixes：
  - 与 `v53` 相同
- 相比 `v53`
  只额外补：
  - `interference_extra_focus_sample_ids`
    = `v30 exact 10 ids`
- 且这次已确认：
  - `interference_extra`
    真正命中 branch decoder：
    - train `7 / 129`
    - val `3 / 37`

### 结果

relative to `v19`：

- default：
  - `+0.123281 dB`
- exact proxy overall：
  - `-0.828377 dB`
- exact `target_full`：
  - `-1.349682 dB`
- near-real speech probe overall：
  - `-0.041588 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.128521 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.170088 dB`
- near-real `transient_like (0006)`：
  - `+0.281562 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.465969 dB`
- near-real `guodegang_absent_480s`：
  - `+0.097155 dB`
- `proxy_v7`：
  - `+2.016788 dB`

relative to `v32` gate：

- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

### 裁决

`v54` 仍不保留。

并且这次失败性质比 `v53` 更关键：

1. 不是因为 friend-side guardrail 没接到 branch decoder。
   - 这次 `interference_extra`
     已经实际命中：
     - train `7`
     - val `3`
2. 但接进去之后，
   `proxy_v7 / guodegang`
   反而更强了：
   - `proxy_v7`：
     - `+1.465092 -> +2.016788`
   - `guodegang_anchor`：
     - `+0.296715 -> +0.465969`
   - `guodegang_absent`：
     - `+0.060516 -> +0.097155`
3. 同时 friend-side 两条却更差：
   - exact `target_full`：
     - `-0.875034 -> -1.349682`
   - `speech_leak_like (0004)`：
     - `-0.104842 -> -0.128521`

这说明：

- 当前 dual-head 的问题
  已经不再是：
  - extra routing 没接上；
- 而是：
  - 现有这条 friend-side `interference_extra residual_projection_ratio`
    就算接到 branch decoder，
    也不会把它往 keep 方向推；
  - 它和 absent-side `proxy_v7 reconstruction`
    在这条新分支上，
    仍然更像同向强化，
    不是有效对冲。

## 当前阶段结论

`v53 / v54`
联合起来，
把 dual-head 这条线的边界写得更清楚：

1. dual-head 方向本身不是无效。
   - `proxy_v7`
   - `guodegang_anchor`
   - `guodegang_absent`
   都明显比 `v42` 更强。
2. `v53`
   暴露的是：
   - branch decoder 只吃 absent-side objective，
     friend-side guardrail 没接上。
3. `v54`
   暴露的是：
   - 即便把当前 friend-side residual extra
     真接上去，
     它也不会把 dual-head 拉向 keep；
   - 反而会把
     `proxy_v7 / guodegang`
     与 friend-side failure
     一起放大。

因此下一条默认不该再继续扫：

- 同一条 `interference_extra residual_projection_ratio`
  在 dual-head 上的权重；
- 或继续把这 10 条 exact sample-id
  机械叠到同一 branch decoder 上。

更合理的下一步应更新为：

- 保留 dual-head plumbing；
- 但 friend-side protect objective
  需要换成更接近：
  - `keep target_full`
  - `protect speech_leak_like`
  的 branch-local 约束；
- 而不是继续复用当前这条
  `residual_projection_ratio`
  作为默认对冲项。
