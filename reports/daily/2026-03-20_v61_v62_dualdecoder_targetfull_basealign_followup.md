# 2026-03-20 `v61 / v62` dual-head `target_full`-only `base-align` follow-up

## 背景

`v57 / v58` 已说明：

- dual-head 上的 `base-align`
  protect primitive
  本身是对题的；
- 但把 protect selector
  直接挂在整组 `v30 exact 10 ids` 上，
  会把：
  - `target_full`
  - `0004-like speech leak`
  - 以及其它 exact-family 行为
  混成一个过粗的约束集合。

`v59 / v60` 又说明：

- 改成 `base-delta-interference projection`
  不是当前答案；
- 这条 primitive 在现有 exact ids 上
  的实际 loss 量级几乎为 `0`，
  不值得继续扫权重。

因此本轮不再换 primitive，
而是回到已有信号最强的 `base-align`，
只改 selector：

- 不再保护整组 exact-family ids；
- 只保护
  `target_full` 子集。

目标是先验证：

- 上一轮的冲突，
  到底是不是来自 selector 过粗，
  而不是 `base-align` primitive 本身错误。

## 选择器与实验设置

本轮共用：

- frozen base：
  - `v32`
- absent-side objective：
  - `proxy_v7 reconstruction`
- branch-local protect primitive：
  - `interference_extra_base_align_weight`
- protect selector：
  - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt`

该 `target_full`-only selector
实际命中为：

- train:
  - `4 / 129`
- val:
  - `1 / 37`

也就是：

- 这轮 protect
  不再试图同时约束整组 exact-family；
- 而是只盯住
  当前最核心的 `target_full`
  泄漏子集。

## `v61 = target_full`-only `base-align (0.02)`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v61_v32_absent_dualdecoder_v7_wave_targetfullbasealign_w02_ft1`
- dual-head：
  - `enable_branch_decoder_head = true`
- 仅训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- absent-side：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `focus = proxy_v7`
- friend-side protect：
  - `interference_extra_base_align_weight = 0.02`
  - `focus = target_full-only selector`

### selector 与 protect 项量级

- `interference_extra`
  selector 命中：
  - train `4 / 129`
  - val `1 / 37`
- `train_interference_extra_base_align_l1`
  - `3.7905751353334463e-06`
- `val_interference_extra_base_align_l1`
  - `7.261304563144222e-06`

### 结果

relative to `v19`：

- default：
  - `+0.075905 dB`
- exact `target_full`：
  - `-0.369736 dB`
- near-real speech probe overall：
  - `-0.051933 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.071034 dB`
- `guodegang_anchor_120s`：
  - `+0.069889 dB`
- `guodegang_absent_480s`：
  - `+0.043306 dB`
- `proxy_v7`：
  - `-0.029114 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- clear fail：
  - `exact_target_full_gain_floor`
- near-tie：
  - `speech_leak_like_gain_floor`
- pass：
  - default
  - speech probe overall
  - `guodegang_anchor`
  - `guodegang_absent`

### 裁决

`v61` 不保留为 keep，
但它给出了这条线目前最关键的新证据：

- `target_full`
  从 `v59 / v60` 的
  `-0.95 / -0.98 dB`
  回收到
  `-0.369736 dB`；
- `0004`
  也从 clear fail
  收到 near-tie；
- `guodegang`
  没塌；
- 代价只是：
  - `proxy_v7`
    回到近零轻微负向，
    没有出现
    `v57`
    那种大幅塌陷。

因此这轮应解释为：

- 问题确实主要出在
  protect selector 过粗；
- 只保护 `target_full` 子集
  是对的。

## `v62 = stronger target_full`-only `base-align (0.05)`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v62_v32_absent_dualdecoder_v7_wave_targetfullbasealign_w05_ft1`
- 相比 `v61`
  仅改：
  - `interference_extra_base_align_weight = 0.05`

### selector 与 protect 项量级

- `interference_extra`
  selector 命中保持不变：
  - train `4 / 129`
  - val `1 / 37`
- `train_interference_extra_base_align_l1`
  - `5.1941194857054525e-06`
- `val_interference_extra_base_align_l1`
  - `1.4201123849488795e-05`

### 结果

relative to `v19`：

- default：
  - `+0.079917 dB`
- exact `target_full`：
  - `-0.586134 dB`
- near-real speech probe overall：
  - `-0.039473 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.063768 dB`
- `guodegang_anchor_120s`：
  - `+0.118074 dB`
- `guodegang_absent_480s`：
  - `+0.042873 dB`
- `proxy_v7`：
  - `+0.861507 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- clear fail：
  - `exact_target_full_gain_floor`
- near-tie：
  - `speech_leak_like_gain_floor`

### 裁决

`v62` 也不保留。

关键不是：

- “比 `v61` 还差一点，所以只是不够稳”

而是：

- 它已经明确说明：
  - 在 `target_full`-only selector 上，
    继续把同一条 `base-align` weight 往上推，
    不是 closing gap 的正确方向。

具体表现为：

- `speech_leak_like (0004)`
  只小幅改善：
  - `-0.071034 -> -0.063768 dB`
- 但 exact `target_full`
  明显变差：
  - `-0.369736 -> -0.586134 dB`
- 同时：
  - `proxy_v7`
  - `guodegang_anchor`
  - broad speech probe overall
    都继续变强。

这说明：

- 同一条 primitive 加权变强后，
  主要被放大的不是
  “最后一点 friend-side protect”；
- 而更像是
  absent-side / broad trade-off
  继续占优。

## 当前阶段结论

`v61 / v62`
把这条 dual-head protect 线的边界进一步写清楚了：

1. `target_full`-only selector
   是正确方向。
   - `v61`
     首次把：
     - exact `target_full`
     - `0004`
     - `guodegang`
     这三者拉回到相对更平衡的状态。
2. 但在这个 selector 上，
   继续单纯增大同一条 `base-align` weight
   不是正确延伸。
   - `v62`
     没有关闭最后的 gap；
   - 反而把
     exact `target_full`
     再次推坏。
3. 因而当前最准确的工作结论应更新为：
   - 要保留：
     - dual-head plumbing
     - `proxy_v7`
     - `v32` frozen base anchor
     - `target_full`-only protect selector
   - 但下一条不再默认继续扫：
     - `interference_extra_base_align_weight`
       在这条 selector 上的近邻值。

## 下一步默认更新

当前默认下一步应改成：

1. 保留 `target_full`-only selector
   作为现有 protect 集合的一部分；
2. 但不再把：
   - “同一条 `base-align`
      再加一档权重”
   当作默认答案；
3. 下一条更合理的 protect objective
   应是：
   - 在保留 `target_full` 保护的同时，
   - 再显式补一条
     更直接面向
     `speech_leak_like (0004)`
     的 branch-local protect signal；
4. 也就是把当前问题
   从：
   - “一条粗 protect primitive
      权重调到哪”
   改写成：
   - “`target_full`
      与 `0004-like speech leak`
      两类行为分别怎么保护”。
