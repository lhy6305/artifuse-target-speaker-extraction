# 2026-03-20 `v55 - v58` dual-head protect-objective follow-up

## 背景

`v53 / v54` 已经把 dual-head 当前边界写清楚：

- dual-head 本身不是没方向；
- `proxy_v7 / guodegang`
  可以被明显拉强；
- 但把当前 friend-side
  `interference_extra residual_projection_ratio`
  接到 branch decoder 上，
  不会形成 keep 方向的有效对冲。

因此本轮不再继续扫：

- 同一条 residual extra
  的权重；
- 或继续机械复用同一条 friend exact objective。

而是改成更直接问两件事：

1. 如果只在 exact family 上挂更纯粹的
   target-preservation `SI-SDR guard`，
   dual-head 会不会比 `v54`
   更稳；
2. 如果直接约束 branch decoder
   在 friend exact ids 上不要偏离 `v32` base 输出，
   能不能把 dual-head 拉到
   `proxy_v7` 与 friend-side 之间的更平衡位置。

## 工程补充一：`v55` 前的 dual-head protect primitive

本轮延用上一轮已补好的：

- `extra_prediction`
  routing

即：

- branch decoder
  已经可以真正吃到：
  - `interference_extra_guard_sisdr`
  - `interference_extra`
  - 其他 extra 类约束

## `v55 = dual-head + proxy_v7 reconstruction + exact SI-SDR guard`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v55_v32_absent_dualdecoder_v7_wave_exactsisdrguard_ft1`
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
  - `interference_extra_guard_sisdr_weight = 0.0002`
  - `focus = v30 exact 10 ids`
- 不启用：
  - `interference_extra_weight`

### 结果

relative to `v19`：

- default：
  - `+0.126371 dB`
- exact proxy overall：
  - `+0.394224 dB`
- near-real speech probe overall：
  - `-0.140416 dB`
- near-real `speech_leak_like (0004)`：
  - 明显回退
- near-real `guodegang_anchor_120s`：
  - `-0.494584 dB`
- near-real `guodegang_absent_480s`：
  - `-0.157483 dB`
- `proxy_v7`：
  - `+1.859823 dB`

relative to `v32` gate：

- `overall_judgement = fail`
- failed rules：
  - `speech_probe_overall_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

### 裁决

`v55` 不保留。

解释：

- 这条线和 `v34`
  的 shared-path 现象一致：
  - exact family 被明显推正；
  - `proxy_v7` 也继续很强；
  - 但 near-real 尤其 `guodegang`
    直接明显转负。

因此：

- 对 dual-head 来说，
  只在 exact family 上挂 target-preservation `SI-SDR guard`
  仍然更像 exact-family overfit；
- 它不能作为当前默认的 branch-local protect objective。

## 工程补充二：新增 branch-to-base align protect objective

### `src/tse_prefix/pipeline/baseline_train.py`

新增：

- `interference_extra_base_align_l1`
- `interference_extra_base_align_weight`

当前语义：

- 只在 `interference_extra` selector 命中的样本上；
- 约束：
  - `extra_prediction`
    不要偏离
  - frozen base `prediction`

大白话讲：

- 这不是让 dual-head
  再去贴 target 真值；
- 而是：
  - 在 friend exact ids 上，
    先别把 `v32` base 原来相对稳的行为改坏。

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `--loss-interference-extra-base-align-weight`

### `scripts/eval/eval_stft_mask_baseline.py`

同步补：

- `interference_extra_base_align_l1`
  指标落盘。

## `v56`：无效实验，不计入结论

### 现象

首次跑 `base-align` 版本时，
训练命令虽然传了：

- `--loss-interference-extra-base-align-weight`
- `--loss-interference-extra-focus-sample-ids-file`

但 `resolve_selector_sample_weights(...)`
里，
`interference_extra`
的激活条件还没把：

- `interference_extra_base_align_weight`

算进去。

结果：

- `v56`
  这轮实际上
  `interference_extra = inactive`
  没有真正命中 exact ids。

### 处理

已在：

- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

把：

- `interference_extra_base_align_weight`

加入 `interference` 分支的 `extra_weight_keys`。

因此：

- `v56` 记为无效 plumbing 轮次；
- 不拿它做实验结论；
- 后续有效版本从 `v57` 开始编号。

## `v57 = dual-head + proxy_v7 reconstruction + strong base-align`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v57_v32_absent_dualdecoder_v7_wave_basealign_ft1`
- absent-side：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `focus = proxy_v7`
- friend-side protect：
  - `interference_extra_base_align_weight = 0.02`
  - `focus = v30 exact 10 ids`
- 已确认 selector 命中：
  - train `7 / 129`
  - val `3 / 37`

### 结果

relative to `v19`：

- default：
  - `+0.032309 dB`
- exact proxy overall：
  - `-0.040606 dB`
- exact `target_full`：
  - `-0.218561 dB`
- near-real speech probe overall：
  - `-0.046852 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.047720 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.052475 dB`
- near-real `guodegang_absent_480s`：
  - `-0.000021 dB`
- `proxy_v7`：
  - `-1.498264 dB`

relative to `v32` gate：

- `overall_judgement = near_tie`
- 唯一 near-tie rule：
  - `speech_leak_like_gain_floor`
    - 只差：
      - `-0.006040 dB`
- 其余都 pass：
  - default
  - speech probe overall
  - exact `target_full`
  - `guodegang_anchor`
  - `guodegang_absent`

### 裁决

`v57` 不保留。

解释：

- 这条线第一次把 dual-head
  拉到了非常接近 gate 的位置；
- 但代价也很明显：
  - `proxy_v7` 直接塌成：
    - `-1.498264 dB`
- 因此它不是 keep，
  更像：
  - dual-head 版的“保护过头”。

## `v58 = dual-head + lighter base-align`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v58_v32_absent_dualdecoder_v7_wave_basealign_w005_ft1`
- 与 `v57`
  相同，
  仅改：
  - `interference_extra_base_align_weight = 0.005`

### 结果

relative to `v19`：

- default：
  - `+0.091565 dB`
- exact proxy overall：
  - `-0.104307 dB`
- exact `target_full`：
  - `-0.250669 dB`
- near-real speech probe overall：
  - `-0.053238 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.076592 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.061275 dB`
- near-real `guodegang_absent_480s`：
  - `+0.027740 dB`
- `proxy_v7`：
  - `+0.042581 dB`

relative to `v32` gate：

- `overall_judgement = fail`
- 唯一 clear fail：
  - `speech_leak_like_gain_floor`
    - `candidate_minus_floor = -0.034912 dB`

### 裁决

`v58` 也不保留。

解释：

- 把 `base-align` 放轻之后：
  - `proxy_v7`
    从 `v57` 的明显负向
    拉回到近零正向；
  - `guodegang_anchor / absent`
    也回到正向；
- 但 `speech_leak_like (0004)`
  又明显掉回 clear fail。

大白话讲：

- `v57`
  是保护过头；
- `v58`
  是一放松就又保不住 `0004`。

## 当前阶段结论

`v55 - v58`
联合起来，
已经把这条 protect-objective 线的边界写清楚：

1. exact `SI-SDR guard`
   在 dual-head 上仍然是 overfit 型信号；
   - 会把 exact / `proxy_v7`
     一起推强，
   - 但 near-real 尤其 `guodegang`
     会明显转负。
2. branch-to-base `base-align`
   是一个更对题的 protect primitive；
   - `v57`
     证明它确实能把 dual-head
     拉到接近 gate；
   - 但它会把 `proxy_v7`
     直接压塌。
3. 把 `base-align` 放轻到 `v58`
   后，
   - `proxy_v7 / guodegang`
     会回来；
   - 但 `speech_leak_like (0004)`
     又重新 clear fail。

因此当前应明确写成：

- `base-align` 这条 primitive
  有信号；
- 但继续扫同一条 weight
  已经不再是默认优先级。

下一条更合理的默认方向应更新为：

1. 不再继续扫：
   - `interference_extra_base_align_weight`
   的小数点；
2. 把当前缺口明确写成：
   - 需要一条比 exact-family base-align
     更直接面向
     `speech_leak_like (0004)`
     的 branch-local protect objective；
3. 同时继续保留：
   - `proxy_v7`
   - dual-head plumbing
   - `v32` 作为 frozen base anchor
   这三项资产。
