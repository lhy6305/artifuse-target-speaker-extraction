# 2026-03-27 overlap-refine preserve/bypass `0007-like` self-anchor `v113` follow-up

## 本轮目标

`v112` 已证明：

- 只把 suppress 路径从主路径里拆开，
- 但表示仍停留在 `overlap_cancel` 语义里，
- 会收成 safe / near-no-op。

因此本轮改成首个更接近 preserve/bypass 语义的最小 pilot：

1. 仍以 `v109` 作为冻结主路径；
2. 不继续训练 `branch_decoder_mask_head`；
3. 改开 `branch_overlap_refine_head`；
4. 让 refiner 只在 gate-complement 区域、以 `residual` 为 source 做小幅局部修正；
5. 并继续用 paired `0007-like` bundle 同时提供：
   - `speech_only` 局部 suppress 信号
   - `plus_music` hard-present preservation 信号

目标是先看：

- 这种 preserve/bypass 风格表示，
- 是否终于能比 `v109` 更明确地前进，
- 而不是再次收成 near-no-op。

## `v113` 训练配置

有效 checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v113_v109_overlap_refine_preservebypass_0007like_selfanchor_v1_ft2`

说明：

- 首个 `ft1` 试跑已忽略；
- 原因不是训练失败，而是 selector 没显式带进 CLI，导致 paired `0007-like` 子域没有被真正激活；
- 本轮有效结论只看 `ft2`。

初始化：

- `v109`

teacher：

- `v109`

核心机制：

- 打开：
  - `enable_branch_overlap_refine_head = true`
- 只训练：
  - `branch_overlap_refine_head`
- 并设置：
  - `branch_overlap_refine_max_delta = 0.08`
  - `branch_overlap_refine_gate_mode = complement`
  - `branch_overlap_refine_source_mode = residual`
  - `loss_use_branch_prerefine_as_primary_prediction = true`

含义：

- `branch_base(v109)` 继续作为主预测基线；
- refiner 只在 `(1 - gate)` 子域上，对 `mix - branch_base` 这一残余成分做小幅局部修正；
- 这是当前第一版真正带有 preserve/bypass 味道的 frozen-base refiner。

paired selector 激活：

- train
  - `reconstruction_extra = 63 / 108`
  - `overlap_interference_extra = 3 / 108`
  - `branch_protect = 3 / 108`
  - `branch_protect_teacher = 3 / 108`
- val
  - `reconstruction_extra = 0 / 39`
  - `overlap_interference_extra = 2 / 39`
  - `branch_protect = 3 / 39`
  - `branch_protect_teacher = 3 / 39`

训练结果：

- 训练成功结束
- `elapsed_sec = 11.5`

## 自动验收结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +3.6476 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.6197 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.2724 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +1.7747 dB`
  - `6 improve / 1 regress`

解释：

- relative `v81` 四条固定验收继续全绿；
- 且整体幅度已经不只是 safe / near-no-op。

### relative `v109`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +1.0546 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.5442 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.5989 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.3343 dB`

解释：

- 这是当前 preserve/bypass 方向第一次相对 `v109` 形成成体系的 synthetic 正向；
- 不再是 `v111 / v112` 那种整体近乎打平。

## near-real 结果

### 导包

- `export_ab_listening_pack.py`
  - relative `v81`
    - `0 candidate sample`
  - relative `v109`
    - `0 candidate sample`

解释：

- 这版仍然不导听审；
- 但 `0 candidate sample` 不代表它和 `v109` 完全一样，
- 只是还没有形成足够强的 listening-pack 候选差异。

### `v81 vs v113`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `v81 = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v81 = 4`
- `more_residual_heavy_candidate_counts`
  - `tie = 4`
- `better_retention_minus_leak_candidate_counts`
  - `v113 = 2`
  - `tie = 1`
  - `not_applicable = 1`
- `tradeoff gate = pass`

关键样本：

- `near_real_0007`
  - whole-utterance：
    - `better_retention_minus_leak = v113`
    - `delta_target_capture_db = -2.5746 dB`
    - `delta_interference_capture_db = -4.0576 dB`
    - `delta_retention_minus_leak_db = +1.4830 dB`
    - `delta_residual_output_share = +0.0771`
  - overlap-local：
    - `better_retention_minus_speech_leak = v81`
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = v113`

解释：

- 相对 `v81`，`v113` 第一次把 `0007` 的 whole-tradeoff 拉成了自动正向；
- 但它还没解决 overlap-local 的核心旧痛点：
  - local speech leak tradeoff 仍未转正；
  - artifact proxy 仍更重。

### `v109 vs v113`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `tie = 2`
  - `v109 = 2`
- `more_residual_heavy_candidate_counts`
  - `tie = 4`
- `better_retention_minus_leak_candidate_counts`
  - `v113 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `tradeoff gate = pass`

关键样本：

- `near_real_0007`
  - whole-utterance：
    - `better_retention_minus_leak = v113`
    - `better_source_retention = tie`
    - `more_interference_leaky = v109`
    - `delta_target_capture_db = -0.0413 dB`
    - `delta_interference_capture_db = -2.4522 dB`
    - `delta_retention_minus_leak_db = +2.4109 dB`
  - overlap-local：
    - `more_speech_interference_leaky = v113`
    - `better_retention_minus_speech_leak = v109`
    - `better_retention_minus_total_leak = v113`
    - `more_artifact_proxy_heavy = tie`

解释：

- relative `v109`，`v113` 已不是 near-no-op；
- 它在 `0007` 上把 whole-tradeoff 明确推成正向；
- 但 local `speech_only` leak 这根线仍然没有压住，
  只是 `total leak` 已转成对 `v113` 更有利。

### bandwidth / transients

relative `v81`：

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = tie:4`

relative `v109`：

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = tie:3, v113:1`
  - 唯一坏点是：
    - `near_real_0009`

### `phone_artifact_gate_v1`

- relative `v81 / v109`
  - `overall_pass = false`
  - 但原因仍然是：
    - `raw_target_only`
    - `target_present__speech`
    - `target_absent__speech`
    三个桶全部 `missing_bucket`

解释：

- 这和 `v111 / v112` 一样，
- 仍是 full `ab_inference` pack 的元数据形态问题，
- 不是新的实质电话音失败；
- 当前可用判断仍以：
  - tradeoff
  - overlap-local
  - bandwidth
  - transient
  为准。

## 当前裁决

1. `v113` 是当前 preserve/bypass 方向第一次明确的 objective-positive 命中。
2. 相对 `v109`，它不再是：
   - `safe / near-no-op`
   - 或单纯 over-suppressive。
3. 它真正新增的信息是：
   - `0007` 的 whole-utterance tradeoff 已能被推成自动正向；
   - 说明新的 preserve/bypass 表示本身是有希望的。
4. 但它仍然没有完成解题：
   - overlap-local `speech_only` leak 仍未转正；
   - `v81 / v109` relative 都还是 `0 candidate sample`；
   - 当前还不到导 blind 听审的程度。

因此正式裁决是：

- `v113 = first_objective_positive_preservebypass_hit_but_not_listening_candidate`
- 不导听审
- 不把 `v113` 升格成新基座

## 新坑

- paired `0007-like` manifest 本身不会自动激活 selector；
- 如果 CLI 里没显式带上：
  - `reconstruction_extra_focus_sample_ids`
  - `overlap_interference_extra_focus_sample_ids`
  - `branch_protect_focus_sample_ids`
  - `branch_protect_teacher_focus_sample_ids`
  这些 selector 参数，
  就会出现：
  - 训练表面成功，
  - 但实际没打中目标子域
  的假有效 run。

## 下一步

默认下一步更新为：

1. 收口 `v113`；
2. preserve/bypass family 保持活跃，不回退到旧 `overlap_cancel` family；
3. 如果继续 `0007` 子题，
   下一轮不该再问“whole-tradeoff 能不能动”，
   而应直接问：
   - 怎样在保住 `v113` whole-tradeoff 正向的前提下，
   - 把 overlap-local `speech_only` leak 再往前推，
   - 同时不把 artifact 拉回来。
