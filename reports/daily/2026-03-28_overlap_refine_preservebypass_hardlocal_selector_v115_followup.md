# 2026-03-28 overlap-refine preserve/bypass hardlocal-selector `v115` follow-up

## 本轮目标

`v114` 已说明：

- 继续上调同语义 local push 权重，
- 会让 whole-tradeoff 继续变好，
- 但不会自动把 `near_real_0007` overlap-local `speech_only` leak 拉回正向。

因此本轮不改 refiner 表示，也不改 loss 语义，只改 selector 子域：

1. 保持 `v113 ft2` 的 preserve/bypass 机制与权重；
2. 把 `speech_only local leak` selector 从原来的 6 条 `0007-like` proxy，
   扩到更大的 hardlocal plus-music 子池；
3. 看更细但更广的 hardlocal 子域，是否能把优化重点从 whole / total-leak 拉回真正想要的 local `speech_only` leak。

## `v115` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v115_v113_overlap_refine_preservebypass_hardlocal_selector_v1_ft1`

初始化：

- `v113 ft2`

teacher：

- `v109`

新 bundle：

- train
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_bundle_v1.jsonl`
  - `reports/data/merge_local_speech_leak_artifact_paired_hardlocal_bundle_v1_train_summary.json`
  - `output_count = 99`
- val
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_bundle_v1.jsonl`
  - `reports/data/merge_local_speech_leak_artifact_paired_hardlocal_bundle_v1_val_summary.json`
  - `output_count = 37`

保持不变：

- 仍只训练 `branch_overlap_refine_head`
- `branch_overlap_refine_max_delta = 0.08`
- `branch_overlap_refine_gate_mode = complement`
- `branch_overlap_refine_source_mode = residual`
- `loss_use_branch_prerefine_as_primary_prediction = true`
- reconstruction / branch-protect / teacher backstop 与 `v113` 保持一致

唯一主动改动：

- `loss_overlap_interference_extra_focus_sample_ids`
  - 从 `local_speech_leak_0007_like_proxy_v1_all`
  - 改到 `local_speech_leak_proxy_v1_all`
- 并显式限定：
  - `recipe = target_clean_plus_music`
  - `pattern = target_full`
  - `interference_profile = speech_only`
  - `0.05 <= target_energy_ratio <= 0.11`
  - `overlap_ratio >= 0.6`
  - `interference_layer_count = 1`
  - `target_transient_presence_share_mean <= 0.04`

selector 激活：

- train
  - `reconstruction_extra = 63 / 99`
  - `overlap_interference_extra = 11 / 99`
  - `branch_protect = 3 / 99`
  - `branch_protect_teacher = 3 / 99`
- val
  - `reconstruction_extra = 0 / 37`
  - `overlap_interference_extra = 3 / 37`
  - `branch_protect = 3 / 37`
  - `branch_protect_teacher = 3 / 37`

## synthetic 增量结果

relative `v113`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.4349 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.2292 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.2703 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.1544 dB`

解释：

- hardlocal selector 本身没有把 `v113` 拉回 synthetic 回退；
- 它相对 `v113` 仍然是全绿。

## near-real 增量结果

### whole-utterance `v113 vs v115`

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `tie = 2`
  - `v113 = 2`
- `better_retention_minus_leak_candidate_counts`
  - `v115 = 1`
  - `tie = 2`
  - `not_applicable = 1`

关键样本：

- `near_real_0007`
  - whole-utterance：
    - `better_source_retention = tie`
    - `more_interference_leaky = v113`
    - `better_retention_minus_leak = v115`
    - `delta_target_capture_db = -0.0573 dB`
    - `delta_interference_capture_db = -2.1348 dB`
    - `delta_retention_minus_leak_db = +2.0775 dB`

解释：

- finer selector 仍然让 whole-tradeoff 继续往前走；
- 至少在 whole-utterance 上，它不像是坏 run。

### overlap-local `v113 vs v115`

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `tie = 1`
  - `v113 = 1`
  - `v115 = 2`
- `more_total_interference_leaky_candidate_counts`
  - `tie = 1`
  - `v113 = 2`
  - `v115 = 1`
- `better_retention_minus_speech_leak_candidate_counts`
  - `tie = 2`
  - `v113 = 1`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `tie = 4`

关键样本：

- `near_real_0007`
  - overlap-local：
    - `more_speech_interference_leaky = v115`
    - `more_total_interference_leaky = v113`
    - `better_retention_minus_speech_leak = v113`
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = tie`
    - `delta_target_capture_db = -0.0343 dB`
    - `delta_speech_interference_capture_db = +9.2226 dB`
    - `delta_total_interference_capture_db = -0.5585 dB`
    - `delta_retention_minus_speech_leak_db = -9.2569 dB`
    - `delta_retention_minus_total_leak_db = +0.5242 dB`

解释：

- 关键信息非常明确：
  - `v115` 没有把 local total-leak 拉坏；
  - artifact 也没变重；
  - 但真正想要的 `speech_only local leak` 变得更差。

### bandwidth / transients

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = tie:4`

解释：

- 这次失败也不是电话音或 transient 回归；
- 它是一个更干净的“目标错位”失败。

## 当前裁决

1. `v115` 不是坏 run。
2. 它 relative `v113` 在：
   - synthetic
   - whole-tradeoff
   - bandwidth / transient
   上都还是正向或至少不坏。
3. 但它再次没完成真正目标：
   - `near_real_0007` overlap-local `speech_only` leak 继续回退；
   - 而且回退幅度和 `v114` 同量级。

因此正式裁决是：

- `v115 = finer_selector_still_optimizes_whole_or_total_not_local_speech_leak`
- 不扩到 `v81 / v109` 全量 relative 验收
- 不导听审

## 新信息

这轮新增的信息很具体：

- 把 local proxy 子域切得更像 `0007`，
- 也不能保证优化重点从：
  - whole-tradeoff
  - total-leak
  自动切回：
  - overlap-local `speech_only` leak

换句话说：

- 当前问题已经不再只是 selector 粒度太粗。

## 下一步

默认下一步更新为：

1. 收口 `v115`；
2. 不继续 `v115+` selector-only 小步 sweep；
3. 如果继续 preserve/bypass family，
   下一轮应改：
   - loss 语义
   - 或 integration 语义
   而不是继续只换 hardlocal selector。
