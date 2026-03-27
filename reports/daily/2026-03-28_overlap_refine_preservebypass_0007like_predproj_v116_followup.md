# 2026-03-28 overlap-refine preserve/bypass `0007-like` pred-projection `v116` follow-up

## 本轮目标

`v115` 已说明：

- finer selector 本身不够；
- whole / total-leak 仍能继续变好，
- 但 `near_real_0007` overlap-local `speech_only` leak 依旧回退。

因此本轮保持 `v113` 的 bundle、selector 和 refiner 表示不变，只改 overlap local loss 语义：

1. 仍从 `v113 ft2` 出发；
2. 仍只训 `branch_overlap_refine_head`；
3. 仍打原始 `0007-like` paired bundle；
4. 把
   - `loss_overlap_interference_extra_mode`
   从
   - `residual_projection_ratio`
   改成
   - `prediction_projection_ratio`
5. 看更直接的 output-interference 对齐惩罚，是否终于能命中 local `speech_only` leak。

## `v116` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v116_v113_overlap_refine_preservebypass_0007like_predproj_v1_ft1`

初始化：

- `v113 ft2`

teacher：

- `v109`

保持不变：

- `train / val manifest = local_speech_leak_artifact_paired_0007_like_bundle_v1`
- `branch_overlap_refine_max_delta = 0.08`
- `branch_overlap_refine_gate_mode = complement`
- `branch_overlap_refine_source_mode = residual`
- reconstruction / branch-protect / selector / 权重全部与 `v113` 相同

唯一主动改动：

- `loss_overlap_interference_extra_mode`
  - `residual_projection_ratio -> prediction_projection_ratio`

selector 激活：

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

说明：

- 这轮不存在 selector 未激活问题；
- 结果可直接视作“只换 overlap local loss 语义”的干净增量。

## synthetic 增量结果

relative `v113`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.8478 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.4624 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.5265 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.2962 dB`

解释：

- 这轮 synthetic 增益比 `v115` 还更明显；
- 单看 synthetic，它比 `v113` 更强。

## near-real 增量结果

### whole-utterance `v113 vs v116`

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `tie = 2`
  - `v113 = 2`
- `better_retention_minus_leak_candidate_counts`
  - `v116 = 1`
  - `tie = 2`
  - `not_applicable = 1`

关键样本：

- `near_real_0007`
  - whole-utterance：
    - `better_source_retention = tie`
    - `more_interference_leaky = v113`
    - `better_retention_minus_leak = v116`
    - `delta_target_capture_db = -0.0973 dB`
    - `delta_interference_capture_db = -2.3450 dB`
    - `delta_retention_minus_leak_db = +2.2477 dB`

解释：

- relative `v113`，`v116` 在 whole-utterance 上继续正向；
- 并且 `0007` 的 whole-tradeoff 也比 `v115` 再多前进了一点。

### overlap-local `v113 vs v116`

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `tie = 1`
  - `v113 = 1`
  - `v116 = 2`
- `more_total_interference_leaky_candidate_counts`
  - `tie = 1`
  - `v113 = 2`
  - `v116 = 1`
- `better_retention_minus_speech_leak_candidate_counts`
  - `tie = 1`
  - `v116 = 1`
  - `v113 = 1`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `tie = 2`
  - `v116 = 1`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `tie = 4`

关键样本：

- `near_real_0007`
  - overlap-local：
    - `better_source_retention = tie`
    - `more_speech_interference_leaky = v116`
    - `more_total_interference_leaky = v113`
    - `better_retention_minus_speech_leak = v113`
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = tie`
    - `delta_target_capture_db = -0.0552 dB`
    - `delta_speech_interference_capture_db = +9.2733 dB`
    - `delta_total_interference_capture_db = -0.7665 dB`
    - `delta_retention_minus_speech_leak_db = -9.3285 dB`
    - `delta_retention_minus_total_leak_db = +0.7113 dB`

解释：

- 结果和 `v115` 的主失败模式几乎完全一致：
  - whole / total-leak 更好；
  - 但 local `speech_only` leak 仍明显更差。

### bandwidth / transients

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = tie:3, v113:1`
  - 唯一坏点是：
    - `near_real_0007` 上 `v113` 更 transient-lossy

解释：

- `v116` 没有更电话音；
- 而且在 `0007` 上 transient 反而比 `v113` 更不差；
- 但这仍然无法抵消 local `speech_only` leak 的关键回退。

## 当前裁决

1. `v116` 不是坏 run。
2. 它比 `v115` 更清楚地证明：
   - 直接换到 `prediction_projection_ratio`
   - 也能继续改善 synthetic 与 whole-tradeoff。
3. 但它仍然没有完成真正目标：
   - `near_real_0007` overlap-local `speech_only` leak 仍然显著回退；
   - 回退方向与 `v114 / v115` 保持一致。

因此正式裁决是：

- `v116 = predproj_semantics_still_fails_0007_local_speech_leak`
- 不扩到 `v81 / v109` 全量 relative 验收
- 不导听审

## 新信息

这轮新增结论是：

- 当前 preserve/bypass family 的问题，
- 已经不能简单归因于：
  - selector 太粗
  - 或 `residual_projection_ratio` 语义不对

因为：

- selector 换了，失败；
- overlap local loss mode 换了，也还是同方向失败。

## 下一步

默认下一步更新为：

1. 收口 `v116`；
2. 不继续 `v116+` loss-mode-only sweep；
3. 如果继续 preserve/bypass family，
   下一轮应优先改：
   - integration 语义
   - 或表示机制
   而不是继续围绕同一个 overlap local loss mode 调权。
