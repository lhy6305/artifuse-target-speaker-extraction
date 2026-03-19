# 2026-03-20 `v47 / v48` prefix-freeze decoupling follow-up

## 背景

`v46` 已经把当前冲突收紧到一条更硬的结论：

- 即便把 `proxy_v7 full`
  完全退出 absent reconstruction，
  friend-side 两条仍几乎不回收：
  - exact `target_full`
  - `speech_leak_like (0004)`
- 说明问题不像：
  - selector 上又多撞了哪几行；
- 而更像：
  - absent-side reconstruction
    通过共享参数更新，
    全局改写了 friend-side 行为。

因此本轮不再继续：

- `full / nonfull` 细拆 selector；
- 或 `wave / stft`
  的小修。

而是先补一条真正可复用的工程能力：

- 训练时只允许指定模块前缀继续更新，
  其余参数全部冻结；
- 再用它测试：
  - 如果只让更局部的参数动，
    能不能保住 `proxy_v7` 的 absent 收益，
    同时把 friend-side 两条拉回。

## 工程补充

### `scripts/train/train_stft_mask_baseline.py`

本轮新增：

- `--trainable-module-prefixes`
  - 传入模块名前缀后，
    只有这些参数继续训练；
  - 其他参数统一 `requires_grad = false`
- `train_summary.json`
  新增：
  - `trainable_config`
  - `trainable_parameter_count`
  - `trainable_parameter_fraction`
  - `trainable_parameter_names`

大白话讲：

- 现在可以正式跑：
  - “只动 reference-conditioning”
  - 或“只动 reference-conditioning + output head”
- 不需要再手改脚本或靠临时 patch 漂移。

## `v47 = proxy_v7 all ids + ref-conditioning only`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v47_v32_absent_reconstructionextra_v7_wave_refcondonly_ft1`
- init：
  - `v32`
- manifest：
  - 继续复用 `v42`
    merged manifest
- reconstruction：
  - 继续保留 `v42`
    同级定义：
    - `reconstruction_extra_waveform_weight = 0.005`
    - `reconstruction_extra_focus_sample_ids = proxy_v7 all ids`
- trainable prefixes：
  - `ref_encoder`
  - `condition_proj`
- trainable parameter count：
  - `131,968 / 2,367,617`
  - `5.57%`

解释：

- 对 `legacy_bias`
  这套模型来说，
  `v47`
  几乎就是：
  - 只允许 reference-conditioning 继续学；
  - 不再动
    `mix_proj / temporal_model / mask_head`
    这些更像共享主干行为的参数。

### 结果

relative to `v19`：

- default：
  - `+0.018882 dB`
- exact proxy overall：
  - `-0.114903 dB`
- exact `target_full`：
  - `-0.290016 dB`
- near-real speech probe overall：
  - `-0.049172 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.042893 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.059132 dB`
- near-real `guodegang_absent_480s`：
  - `-0.007238 dB`
- `proxy_v7`：
  - `-0.858876 dB`

relative to `v32` gate：

- `overall_judgement = near_tie`
- `overall_pass = false`
- 唯一 failed rule：
  - `speech_leak_like_gain_floor`
    - 但只差：
      - `-0.001213 dB`
    - 属于 `near_tie`
- 其余都 pass：
  - `default_stage2_delta_floor`
  - `speech_probe_overall_floor`
  - `exact_target_full_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

### 裁决

`v47` 不保留。

原因不是它 gate 很差，
恰恰相反：

- 它第一次把
  `exact_target_full`
  从 clear fail
  拉回了 pass；
- `speech_leak_like`
  也只剩 near-tie。

但它同时暴露出另一条更关键的新边界：

- 如果把更新范围压到
  纯 reference-conditioning，
  `proxy_v7` 本体会直接塌掉：
  - `+0.444459 dB`
    (`v42`)
  - 到
    `-0.858876 dB`
    (`v47`)
- 且 real `guodegang_anchor / absent`
  也都退回负向。

因此更准确的解释应写成：

- 纯 ref-conditioning freeze
  确实能保护 friend-side；
- 但它对 absent-side 来说
  过于保守，
  连 proxy 本体都带不起来；
- 所以它不是 keep，
  但它是一个非常有价值的边界实验：
  - 说明当前缺的不是
    “更少更新”本身；
  - 而是
    “保留一点 output-side plasticity，
    但别再改写共享时序主干”。

## `v48 = ref-conditioning + mask_head`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v48_v32_absent_reconstructionextra_v7_wave_refcond_maskhead_ft1`
- init / manifest / reconstruction：
  - 与 `v47` 相同
- trainable prefixes：
  - `ref_encoder`
  - `condition_proj`
  - `mask_head`
- trainable parameter count：
  - `329,345 / 2,367,617`
  - `13.91%`

解释：

- `v48`
  相比 `v47`
  只额外放开了 output head；
- 共享的
  `mix_proj / temporal_model`
  仍冻结。

### 结果

relative to `v19`：

- default：
  - `+0.061926 dB`
- exact proxy overall：
  - `-0.175707 dB`
- exact `target_full`：
  - `-0.347332 dB`
- near-real speech probe overall：
  - `-0.078896 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.089823 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.014192 dB`
- near-real `guodegang_absent_480s`：
  - `-0.017526 dB`
- `proxy_v7`：
  - `-0.274633 dB`

relative to `v32` gate：

- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
- `near_tie_rules`：
  - `guodegang_absent_floor`

### 裁决

`v48` 也不保留。

它给出的信息是：

1. 只比 `v47`
   多放开一个 `mask_head`，
   default 的确明显回升了：
   - `+0.018882 -> +0.061926 dB`
2. `proxy_v7`
   也比 `v47`
   回来了一些：
   - `-0.858876 -> -0.274633 dB`
3. 但这还不够：
   - `proxy_v7`
     仍是负向；
   - friend-side 两条又重新 clear fail；
   - `guodegang_absent`
     也掉成 near-tie。

因此：

- 单纯“冻结主干，只放开 `mask_head`”
  还不是真正足够的 decoupling；
- 它确实比 `v47`
  更有 absent/output-side 的可塑性；
- 但仍然会重新带回 friend-side 伤害，
  且 absent proxy 本体还没回到正向。

## 当前阶段结论

这两条 prefix-freeze follow-up
联合起来，已经把下一步方向继续收紧：

1. 纯 ref-conditioning：
   - 太保守；
   - friend-side 接近守住，
     但 absent proxy 本体直接塌掉。
2. ref-conditioning + `mask_head`：
   - 有一点 output-side plasticity；
   - 但仍不足以同时保住：
     - `proxy_v7`
     - friend-side 两条
3. 因此下一条不该再继续扫：
   - 哪些模块前缀冻结 / 解冻
     的小组合；
4. 更合理的默认下一步已经变成：
   - 真正的 absent-only residual adapter
   - 或独立 output branch / dual-head
   - 总之要给 absent-side
     一点专属 output plasticity，
     但不能再把共享主干一起拖走。

## 裁决摘要

- `v47`：
  - 不保留
  - 但记为：
    - `friend-side near-tie / exact recovered`
    - `proxy_v7 collapsed`
- `v48`：
  - 不保留
  - 但记为：
    - `mask_head unlock partially restores output plasticity`
    - `still not enough; friend-side re-breaks before proxy_v7 turns positive`
