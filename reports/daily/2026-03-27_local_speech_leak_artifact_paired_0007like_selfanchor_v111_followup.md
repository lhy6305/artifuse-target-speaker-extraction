# 2026-03-27 local speech-leak / artifact paired `0007-like` self-anchor `v111` follow-up

## 本轮目标

`v110` 已证明：

- paired dual-view 虽然 synthetic 继续更强，
- 也没有重新触发明显 phone-artifact，
- 但在 `0007` 上仍是
  - `better_retention_minus_speech_leak`
  - 换
  - 更差的 whole-tradeoff / total-leak。

因此本轮改成更保守的 self-anchor：

1. 仍使用同一份 `paired 0007-like bundle`；
2. 初始化继续从 `v109` 出发；
3. artifact view 的 teacher 不再对齐 `v81`，改成对齐 `v109` 自身；
4. `speech_only overlap_interference_extra` 权重减半；
5. 看是否能：
   - 保住 `v109` 的 whole-tradeoff，
   - 同时留下哪怕很小的局部 leak 收益。

## `v111` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v111_v109_local_speech_leak_artifact_paired_0007like_selfanchor_v1_ft1`

初始化：

- `v109`

teacher：

- `v109`

相对 `v110` 的关键改动：

- `loss-branch-protect-teacher-overlap-weight`
  - `3.0 -> 6.0`
- `loss-overlap-interference-extra-weight`
  - `0.03 -> 0.015`

selector 激活：

- train
  - `overlap_interference_extra = 3 / 108`
  - `branch_protect = 3 / 108`
  - `branch_protect_teacher = 3 / 108`
- val
  - `overlap_interference_extra = 2 / 39`
  - `branch_protect = 3 / 39`
  - `branch_protect_teacher = 3 / 39`

训练结果：

- 训练成功结束
- `elapsed_sec = 14.2`

## 自动验收结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +3.0139 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.2233 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.8403 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +1.6793 dB`

### relative `v109`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.4210 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.1478 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.1668 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.2389 dB`

解释：

- synthetic 继续轻微正向；
- 但这次 near-real 的真实信号明显比 `v110` 更像“基本不动”。

## near-real 结果

说明：

- `export_ab_listening_pack.py` relative `v81 / v109` 都给出 `0 candidate sample`；
- 为了看全量数值，额外导出了全量 `ab_inference` pack 再跑：
  - `tradeoff_analysis`
  - `overlap_local_benchmark`
  - `bandwidth_analysis`
  - `transient_analysis`
- `gate_near_real_phone_artifact.py` 对这个全量导出 pack 会报 `missing_bucket`，
  这是因为它要求 listening-pack 的候选桶元数据；这里不作为实质失败结论使用。

### `v81 vs v111`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `v81 = 3`
  - `not_applicable = 1`
- `better_retention_minus_leak_candidate_counts`
  - `v111 = 1`
  - `tie = 1`
  - `v81 = 1`
  - `not_applicable = 1`
- `tradeoff gate = pass`
- 关键样本：
  - `near_real_0007`
    - `better_retention_minus_leak = v81`
    - `more_residual_heavy = v111`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `v111 = 2`
  - `tie = 1`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `v111 = 1`
  - `tie = 1`
  - `v81 = 1`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v111 = 3`
  - `tie = 1`
- 关键样本：
  - `near_real_0007`
    - `better_retention_minus_speech_leak = v111`
    - `better_retention_minus_total_leak = v81`
    - `more_artifact_proxy_heavy = v111`

结论：

- relative `v81`，`v111` 仍没有把 `0007` 从旧痛点里拉出来；
- 它只是比 `v110` 略收了一点，没有改变问题的方向。

### `v109 vs v111`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `better_retention_minus_leak_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `tradeoff gate = pass`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `better_retention_minus_total_leak_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `tie = 4`
- 关键样本：
  - `near_real_0007`
    - `better_retention_minus_speech_leak = tie`
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = tie`

bandwidth / transients：

- relative `v109`
  - `narrower_candidate_counts = tie:4`
  - `more_transient_lossy_candidate_counts = tie:4`
- relative `v81`
  - `narrower_candidate_counts = v81:3, tie:1`
  - `more_transient_lossy_candidate_counts = v81:2, tie:2`

结论：

- `v111` 成功把 `v110` 的过抑制收回到 `v109` 附近；
- 但它基本也把可感知的前进一起收没了。

## 当前裁决

1. `v111` 不是 `v110` 式 over-suppressive 候选；
2. 但它也不是一个值得继续导听审的新 candidate；
3. 它更像：
   - 一个证明 self-anchor 可以把 paired dual-view 收回 safe / near-no-op 边界的控制实验。

因此当前正式裁决是：

- `v111 = safe_but_no_meaningful_progress`
- 不导 blind 听审
- 不继续 `v111+` 同构小步 sweep

## 下一步

默认下一步改为：

1. 收口 `v110 / v111` 这一组 paired dual-view family；
2. 不再继续：
   - `v110+`
   - `v111+`
3. 如果继续 `0007` 子题，
   - 当前这组 loss family 已经给出边界：
     - 放松时会过抑制；
     - 收紧时会退成 near-no-op；
   - 因此下一步应改做新的约束或表示机制，
     而不是继续沿这组 loss 权重微调。
