# 2026-03-27 overlap-cancel split-path `0007-like` `v112` follow-up

## 本轮目标

`v110 / v111` 已证明：

- 只在 loss / backstop 上继续细调，
- 会在：
  - `over-suppressive`
  - `safe / near-no-op`
- 两个边界之间来回。

因此本轮改成首个最小 split-path pilot：

1. 继续以 `v109` 作为主输出基座；
2. 不再让主路径继续漂；
3. 新开一个 `overlap_cancel_head`，只负责 `speech_only overlap` suppress；
4. `0007-like music_plus_speech hard-present` 仍由现成：
   - `branch_protect_guard_sisdr`
   - `branch_protect_teacher_overlap(v81)`
   负责 preservation backstop；
5. 先验证这种“冻结主路径 + 独立 suppress 路径”是否至少能在 near-real 上形成可见增量。

## `v112` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v112_v109_overlap_cancel_splitpath_0007like_v1_ft1`

初始化：

- `v109`

teacher：

- `v81`

核心机制：

- 打开：
  - `enable_branch_overlap_cancel_head = true`
- 但只训练：
  - `branch_overlap_cancel_head`
- 并设置：
  - `branch_overlap_cancel_gate_mode = complement`
  - `branch_overlap_cancel_source_mode = residual`
  - `branch_overlap_cancel_apply_mode = subtract`
  - `branch_overlap_cancel_ratio_mode = complex`
  - `branch_overlap_cancel_max_delta = 0.08`
  - `loss_use_branch_prerefine_as_primary_prediction = true`

含义：

- `branch_base(v109)` 继续作为主预测基线；
- 新 `cancel head` 只在 gate-complement 子域上学习额外 suppress；
- 这版是首个真正意义上的：
  - frozen main path
  - separate suppress path
  试验。

selector 激活：

- train
  - `overlap_interference_extra = 38 / 135`
  - `overlap_cancel = 38 / 135`
  - `branch_protect = 3 / 135`
  - `branch_protect_teacher = 3 / 135`
- val
  - `overlap_interference_extra = 12 / 40`
  - `overlap_cancel = 12 / 40`
  - `branch_protect = 3 / 40`
  - `branch_protect_teacher = 3 / 40`

训练结果：

- 训练成功结束
- `elapsed_sec = 15.1`

## 自动验收结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +2.6823 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.1142 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.7098 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +1.4480 dB`

### relative `v109`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.0893 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0386 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0364 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.0076 dB`

解释：

- relative `v81` 四条 synthetic 固定验收仍全绿；
- 但 relative `v109` 已明显收成 near tie。

## near-real 结果

### `v81 vs v112`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `v81 = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v81 = 3`
  - `tie = 1`
- `more_residual_heavy_candidate_counts`
  - `tie = 4`
- `better_retention_minus_leak_candidate_counts`
  - `v112 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `tradeoff gate = pass`

关键样本：

- `near_real_0003`
  - `better_retention_minus_leak = v112`
- `near_real_0007`
  - `better_retention_minus_leak = tie`
  - 但：
    - `target_capture_db`
      - `v81 = -17.9587`
      - `v112 = -20.4645`
    - `retention_minus_leak_db`
      - `v81 = 29.5135`
      - `v112 = 28.8211`
    - `residual_output_share`
      - `v81 = 0.6818`
      - `v112 = 0.7538`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `v112 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `v112 = 1`
  - `tie = 1`
  - `v81 = 1`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v81 = 1`
  - `v112 = 2`
  - `tie = 1`

关键样本：

- `near_real_0007`
  - `better_retention_minus_speech_leak = tie`
  - `better_retention_minus_total_leak = v81`
  - `more_artifact_proxy_heavy = v112`

### `v109 vs v112`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `tie = 4`
- `more_residual_heavy_candidate_counts`
  - `tie = 4`
- `better_retention_minus_leak_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `tradeoff gate = pass`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `tie = 2`
  - `v109 = 1`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `tie = 4`

关键样本：

- `near_real_0007`
  - `better_retention_minus_speech_leak = v109`
  - `better_retention_minus_total_leak = tie`
  - `more_artifact_proxy_heavy = tie`

解释：

- relative `v109`，`v112` 在 whole-utterance 上几乎完全是 tie；
- 但在最关键的 `0007` overlap-local 上，
  它没有保住 `v109` 的 local speech-leak 优势，
  反而回退成：
  - `more_speech_interference_leaky = v112`
  - `better_retention_minus_speech_leak = v109`

### bandwidth / transients

relative `v81`：

- `narrower_candidate_counts`
  - `tie = 4`
- `more_transient_lossy_candidate_counts`
  - `tie = 3`
  - `v81 = 1`

relative `v109`：

- `narrower_candidate_counts`
  - `tie = 4`
- `more_transient_lossy_candidate_counts`
  - `tie = 4`

说明：

- 这版没有引入新的 bandwidth / transient 坏桶；
- `phone_artifact_gate_v1` 对全量 `ab_inference` pack 仍然是 `missing_bucket` 形态，
  不能当作实质失败结论使用。

### 导包结果

- `export_ab_listening_pack.py`
  - relative `v81`
    - `0 candidate sample`
  - relative `v109`
    - `0 candidate sample`

## 当前裁决

1. `v112` 证明：
   - `frozen main path + separate overlap-cancel suppress path`
   - 在当前代码里是可实现、可训练、且能保持 guardrail-safe 的；
2. 但它没有形成新的 near-real frontier；
3. relative `v109`，它基本收成了 near-no-op；
4. 更关键的是：
   - 在 `0007` overlap-local 上，
   - 它还丢掉了 `v109` 那点原本就很有限的 `speech-leak` 优势。

因此正式裁决是：

- `v112 = split_path_safe_but_no_frontier_gain`
- 不导听审
- 不继续 `v112+`

## 下一步

默认下一步再次更新为：

1. 收口 `v112`；
2. 不继续：
   - `v112+`
   - 当前这组 `frozen branch_base + overlap_cancel_head` split-path 小步 sweep；
3. 如果继续 `0007` 子题，
   - 下一轮需要的已不只是“把 suppress 路径单独分出来”，
   - 而是：
     - 更明确的 preserve / bypass 表示机制，
     - 或新的 integration point，
   - 不能继续停留在当前 multiplicative `overlap_cancel_head` 语义上。
