# 2026-03-28 overlap-refine preserve/bypass `0007-like` gate-guided `v117` follow-up

## 本轮目标

`v116` 已说明：

- selector 不够；
- overlap local loss mode 也不够；
- 当前 family 仍然会把 whole / total-leak 推正，
  但把真正关键的 `near_real_0007` overlap-local `speech_only` leak 拉坏。

因此本轮不再改 selector，也不再改 loss 语义，而是直接改 refiner integration：

1. 仍从 `v113 ft2` 出发；
2. 仍打原始 `0007-like` paired bundle；
3. 仍保持 `residual` source；
4. 只把
   - `branch_overlap_refine_gate_mode`
   从
   - `complement`
   改成
   - `gate`
5. 看 refiner 如果直接在 target-present 区域出手，
   是否终于能命中 `0007` 的核心 overlap-local 痛点。

## `v117` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v117_v113_overlap_refine_preservebypass_0007like_gateguided_v1_ft1`

初始化：

- `v113 ft2`

teacher：

- `v109`

保持不变：

- `train / val manifest = local_speech_leak_artifact_paired_0007_like_bundle_v1`
- `branch_overlap_refine_max_delta = 0.08`
- `branch_overlap_refine_source_mode = residual`
- `loss_overlap_interference_extra_mode = residual_projection_ratio`
- reconstruction / branch-protect / selector / 权重与 `v113` 保持一致

唯一主动改动：

- `branch_overlap_refine_gate_mode`
  - `complement -> gate`

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

- 这轮没有 selector 打空问题；
- 结论可直接视作“只换 gate integration”的干净增量。

## synthetic 增量结果

relative `v113`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +2.9297 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +2.4865 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +2.0962 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +1.8984 dB`

解释：

- 这是当前 preserve/bypass family relative `v113` 最强的一次 synthetic 增量；
- gate-guided integration 明显不是 near-no-op。

## near-real 增量结果

### whole-utterance `v113 vs v117`

- `better_source_retention_candidate_counts`
  - `tie = 2`
  - `v113 = 1`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v113 = 4`
- `better_retention_minus_leak_candidate_counts`
  - `v117 = 3`
  - `not_applicable = 1`

关键样本：

- `near_real_0007`
  - whole-utterance：
    - `better_source_retention = v113`
    - `more_interference_leaky = v113`
    - `better_retention_minus_leak = v117`
    - `delta_target_capture_db = -0.8580 dB`
    - `delta_interference_capture_db = -7.0435 dB`
    - `delta_retention_minus_leak_db = +6.1855 dB`

解释：

- relative `v113`，`v117` 在 whole-utterance 上前进非常大；
- 但它是以更明显的 target retention 代价换来的。

### overlap-local `v113 vs v117`

- `better_source_retention_candidate_counts`
  - `v113 = 2`
  - `tie = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `v113 = 2`
  - `v117 = 2`
- `more_total_interference_leaky_candidate_counts`
  - `v113 = 3`
  - `v117 = 1`
- `better_retention_minus_speech_leak_candidate_counts`
  - `v117 = 2`
  - `v113 = 1`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `v117 = 3`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v117 = 2`
  - `tie = 2`

关键样本：

- `near_real_0007`
  - overlap-local：
    - `better_source_retention = v113`
    - `more_speech_interference_leaky = v117`
    - `more_total_interference_leaky = v113`
    - `better_retention_minus_speech_leak = v113`
    - `better_retention_minus_total_leak = v117`
    - `more_artifact_proxy_heavy = v117`
    - `delta_target_capture_db = -0.7108 dB`
    - `delta_speech_interference_capture_db = +10.6017 dB`
    - `delta_total_interference_capture_db = -5.1151 dB`
    - `delta_retention_minus_speech_leak_db = -11.3125 dB`
    - `delta_retention_minus_total_leak_db = +4.4043 dB`

- `near_real_0009`
  - overlap-local absent peak：
    - `more_speech_interference_leaky = v117`
    - `delta_speech_interference_capture_db = +10.9446 dB`

- `near_real_0006`
  - overlap-local：
    - `more_speech_interference_leaky = v113`
    - `better_retention_minus_speech_leak = v117`
    - `delta_speech_interference_capture_db = -14.9396 dB`
    - `delta_retention_minus_speech_leak_db = +14.8148 dB`

解释：

- `v117` 不是全局坏解；
- 它确实把 `0006` 和 whole / total-leak 推得更强；
- 但它把 `0007` 的 local `speech_only` leak 与 artifact 一起拉坏，
  同时还把 `0009` absent local suppression 拉回去了。

### bandwidth / transients

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = v117:2, tie:1, v113:1`
  - `v117` 更 transient-lossy 的主要坏点：
    - `near_real_0003`
    - `near_real_0009`
  - `near_real_0007` 上反而是：
    - `v113` 更 transient-lossy

解释：

- `v117` 不是电话音回归；
- 但它开始带出新的 transient 副作用，而且副作用不只落在 `0007`。

## 当前裁决

1. `v117` 证明了：
   - 当前 preserve/bypass refiner 的 integration 改动，
   - 可以把 whole 与 total-leak 推得非常激进。
2. 但它仍没有解题：
   - `near_real_0007` overlap-local `speech_only` leak 明显更差；
   - `near_real_0007` artifact proxy 也更重；
   - `near_real_0009` absent local suppression 还出现回退。
3. 因此它不是可扩的 frontier。

正式裁决是：

- `v117 = gateguided_refiner_overpushes_total_leak_but_regresses_0007_local_speech_leak`
- 不扩到 `v81 / v109` 全量 relative 验收
- 不导听审
- 不继续 `v117+`

## 新信息

这轮给出的新结论最重要：

- 当前 `branch_overlap_refine_head` 这条 preserve/bypass family，
- 即使把 integration 从 `complement` 改到 `gate`，
- 也还是会把：
  - whole-tradeoff
  - total-leak
  当成主优化出口，
  而不是稳定解决：
  - `0007` overlap-local `speech_only` leak
  - 以及对应的 local artifact

换句话说：

- selector-only 不够；
- loss-mode-only 不够；
- gate-mode-only 也不够。

## 下一步

默认下一步更新为：

1. 收口 `v115 / v116 / v117`；
2. preserve/bypass family 暂不回退，但停止继续在当前 `branch_overlap_refine_head` 上做：
   - selector-only
   - loss-mode-only
   - gate-mode-only
   小步 sweep；
3. 如果继续 `0007` 子题，
   下一轮应直接切到：
   - 新的局部表示 / controller 机制，
   - 或显式分开的 target-present / target-absent local 控制语义，
   而不是继续在当前单一 refiner 头上塑形。
