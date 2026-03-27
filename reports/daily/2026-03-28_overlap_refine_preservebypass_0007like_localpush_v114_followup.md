# 2026-03-28 overlap-refine preserve/bypass `0007-like` local-push `v114` follow-up

## 本轮目标

`v113` 已经证明：

- preserve/bypass refiner 机制本身不是 near-no-op；
- relative `v109`，`near_real_0007` 的 whole-utterance `better_retention_minus_leak` 已能转成自动正向；
- 但 overlap-local `speech_only` leak 仍未转正。

因此本轮只做一个最小 follow-up：

1. 不改 manifest / selector 语义；
2. 不改 refiner 表示；
3. 从 `v113 ft2` 继续；
4. 只把 `speech_only local leak` 压力再推一点；
5. 看它能否在不丢 whole-tradeoff 的前提下，把 `0007` overlap-local `speech_only` leak 拉回正向。

## `v114` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v114_v113_overlap_refine_preservebypass_0007like_localpush_v1_ft1`

初始化：

- `v113 ft2`

teacher：

- `v109`

保持不变：

- `branch_overlap_refine_head` 仍是唯一可训练模块
- `branch_overlap_refine_max_delta = 0.08`
- `branch_overlap_refine_gate_mode = complement`
- `branch_overlap_refine_source_mode = residual`
- `loss_use_branch_prerefine_as_primary_prediction = true`
- selector 命中集合与 `v113 ft2` 保持一致：
  - `reconstruction_extra = gate_keep_union_v2_train`
  - `overlap_interference_extra = local_speech_leak_0007_like_proxy_v1_all`
  - `branch_protect / teacher = hard_present_artifact_0007_like_proxy_v1_all`

唯一主动改动：

- `loss_overlap_interference_extra_weight`
  - `0.04 -> 0.05`

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

- 这轮没有再次出现 `v113 ft1` 那种 selector 未激活问题；
- 结论可直接视作“在 `v113` 之上单独增大 local push”的增量结果。

## synthetic 增量结果

relative `v113`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.6524 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.3698 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.4298 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.2396 dB`

解释：

- synthetic 四条固定验收 relative `v113` 全正；
- 这说明更强的 local push 并没有立即把 refiner 推回明显的 synthetic 回退区。

## near-real 增量结果

### whole-utterance `v113 vs v114`

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `tie = 2`
  - `v113 = 2`
- `more_residual_heavy_candidate_counts`
  - `tie = 4`
- `better_retention_minus_leak_candidate_counts`
  - `v114 = 1`
  - `tie = 2`
  - `not_applicable = 1`

关键样本：

- `near_real_0007`
  - whole-utterance：
    - `better_source_retention = tie`
    - `more_interference_leaky = v113`
    - `better_retention_minus_leak = v114`
    - `delta_target_capture_db = -0.0355 dB`
    - `delta_interference_capture_db = -1.8998 dB`
    - `delta_retention_minus_leak_db = +1.8643 dB`

解释：

- relative `v113`，`v114` 在 whole-utterance 上仍是正向；
- 尤其 `0007`，whole-tradeoff 还在继续往前走。

### overlap-local `v113 vs v114`

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `tie = 1`
  - `v113 = 1`
  - `v114 = 2`
- `more_total_interference_leaky_candidate_counts`
  - `tie = 2`
  - `v113 = 1`
  - `v114 = 1`
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
    - `more_speech_interference_leaky = v114`
    - `more_total_interference_leaky = tie`
    - `better_retention_minus_speech_leak = v113`
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = tie`
    - `delta_target_capture_db = -0.0144 dB`
    - `delta_speech_interference_capture_db = +6.7240 dB`
    - `delta_total_interference_capture_db = -0.4996 dB`
    - `delta_retention_minus_speech_leak_db = -6.7384 dB`
    - `delta_retention_minus_total_leak_db = +0.4852 dB`

解释：

- 这轮最关键的信息在这里：
  - `v114` 继续改善了 whole-tradeoff；
  - `v114` 也没有把 local total-leak 拉坏；
  - 但它把 `0007` overlap-local 的 `speech_only` leak 明显拉坏了。
- 也就是说，这次增重主要在优化：
  - whole-tradeoff
  - total-leak
- 但没有按预期优化：
  - local `speech_only` leak

### bandwidth / transients

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = tie:2, v113:2`
  - 也就是 relative `v113`：
    - `v114` 没有更电话音
    - `0006 / 0007` 反而比 `v113` 更不 transient-lossy

解释：

- `v114` 的失败不是电话音回归；
- 它更像是：
  - 在不引入额外 artifact 的前提下，
  - 把 suppress 压力继续朝“whole / total leak 更优”方向推，
  - 但没有命中真正需要的 `speech_only local leak` 维度。

## 当前裁决

1. `v114` 不是坏 run。
2. 它 relative `v113` 在：
   - synthetic
   - whole-tradeoff
   - bandwidth / transient
   上都还是正向或至少不坏。
3. 但它没有完成本轮唯一目标：
   - `near_real_0007` overlap-local `speech_only` leak 没有改善，
   - 反而显著变差。

因此正式裁决是：

- `v114 = whole_positive_but_local_speech_leak_regressed_vs_v113`
- 不扩到 `v81 / v109` 全量 relative 验收
- 不导 listening pack
- 不继续做同方向 `overlap_interference_extra_weight` 小步加码

## 新信息

这轮给出的新结论比“又一个失败 checkpoint”更具体：

- 在当前 preserve/bypass self-anchor family 里，
- 直接增加 `speech_only local push` 权重，
- 确实可以让：
  - synthetic 更好
  - whole-tradeoff 更好
  - total-leak 也不坏
- 但它不会自动把真正想要的：
  - overlap-local `speech_only` leak
  一起推正。

换句话说：

- whole-tradeoff / total-leak 的改善，
- 不是 local `speech_only` leak 改善的可靠代理。

## 下一步

默认下一步更新为：

1. 收口 `v114`；
2. preserve/bypass family 继续保留；
3. 不再继续做：
   - `v114+`
   - 或同语义的 `overlap_interference_extra_weight` 继续上调；
4. 如果继续 `0007` 子题，
   下一轮应改：
   - 更直接对齐 overlap-local `speech_only` leak 的目标语义
   - 或更细的 local selector / 局部监督形式
   - 而不是继续用同一个 whole-pack loss 权重去间接推动它。
