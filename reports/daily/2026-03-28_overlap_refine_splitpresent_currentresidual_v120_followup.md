# 2026-03-28 overlap-refine split-present `current_residual` `v120` follow-up

## Summary

- 新机制试验：
  - `v120 = v113 + split target-present / target-absent local control v1`
- 最小结构增量：
  - 保留 `v113` 的 complement-side `branch_overlap_refine_head`
  - 新增一个只在 `gate` 区域生效的 `branch_overlap_refine_present_head`
  - present head 的 source 改成：
    - `current_residual = mix - current_estimate`
- 最终裁决：
  - 这不是 `v119` 那种 near-no-op
  - synthetic 四条固定验收 relative `v113` 全绿
  - whole-utterance near-real tradeoff relative `v113` 也继续前进
  - 但它仍不是 listening candidate：
    - `near_real_0007` overlap-local `speech_only` leak 明显更差
    - `near_real_0009` target-absent speech peak 也明显更 leak
    - `export_ab_listening_pack.py` relative `v113` 仍是 `0 candidate sample`

## Setup

- init:
  - `v113 ft2`
- teacher:
  - `v109`
- train manifest:
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- val manifest:
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- output checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v120_v113_splitpresent_currentresidual_0007like_v1_ft1`
- 只训练：
  - `branch_overlap_refine_present_head`

关键 model config：

- `enable_branch_overlap_refine_head = true`
- `enable_branch_overlap_refine_present_head = true`
- complement head 继续保持：
  - `branch_overlap_refine_gate_mode = complement`
  - `branch_overlap_refine_source_mode = residual`
- 新增 present head：
  - `branch_overlap_refine_present_max_delta = 0.04`
  - `branch_overlap_refine_present_source_mode = current_residual`

训练结果：

- 训练成功结束
- `elapsed_sec = 13.3`
- 这轮不是结构性 no-op：
  - train / val loss 都有小幅稳定响应
  - `interference_extra_projection_ratio`
    与 `branch_protect_*`
    也不是完全冻结

## Synthetic `v113 vs v120`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `+1.2922 dB`
  - `8 improve / 0 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+0.9844 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+0.7738 dB`
  - `16 improve / 0 regress`
- `hard_present_artifact_proxy_v1`
  - `+0.7100 dB`
  - `7 improve / 0 regress`

结论：

- split present / absent local control 不是 near-no-op；
- 相对 `v113`，四条固定验收继续全绿；
- 说明“显式分开的 target-present / target-absent 语义”这条方向本身是成立的。

## Near-real `v113 vs v120`

### Whole-utterance

- `better_source_retention = tie:3, not_applicable:1`
- `more_interference_leaky = v113:4`
- `better_retention_minus_leak = v120:2, tie:1, not_applicable:1`
- `gate_near_real_tradeoff`
  - `overall_pass = true`

关键样本：

- `near_real_0007`
  - `better_retention_minus_leak = v120`
  - `delta_target_capture_db = -0.4180 dB`
  - `delta_interference_capture_db = -4.3538 dB`
  - `delta_retention_minus_leak_db = +3.9359 dB`
- `near_real_0006`
  - `better_retention_minus_leak = v120`
  - `delta_target_capture_db = -0.0532 dB`
  - `delta_interference_capture_db = -1.7353 dB`
  - `delta_retention_minus_leak_db = +1.6820 dB`
- `near_real_0009`
  - `more_interference_leaky = v113`
  - `delta_interference_capture_db = -1.6871 dB`

解释：

- whole-utterance 上，`v120` relative `v113` 明确继续向：
  - leak 更低
  - retention 基本打平
  推进；
- 所以这轮不是“保住 local 换来 whole 回退”的坏解。

### Overlap-local

- `better_source_retention = tie:3, not_applicable:1`
- `more_speech_interference_leaky = v113:2, v120:2`
- `more_total_interference_leaky = v113:3, v120:1`
- `better_retention_minus_speech_leak = tie:1, v120:1, v113:1, not_applicable:1`
- `better_retention_minus_total_leak = tie:1, v120:2, not_applicable:1`
- `more_artifact_proxy_heavy = tie:4`

关键样本：

- `near_real_0007`
  - `more_speech_interference_leaky = v120`
  - `more_total_interference_leaky = v113`
  - `better_retention_minus_speech_leak = v113`
  - `better_retention_minus_total_leak = v120`
  - `more_artifact_proxy_heavy = tie`
  - `delta_target_capture_db = -0.3448 dB`
  - `delta_speech_interference_capture_db = +8.0218 dB`
  - `delta_total_interference_capture_db = -2.4454 dB`
  - `delta_retention_minus_speech_leak_db = -8.3666 dB`
  - `delta_retention_minus_total_leak_db = +2.1006 dB`

- `near_real_0006`
  - `more_speech_interference_leaky = v113`
  - `better_retention_minus_speech_leak = v120`
  - `better_retention_minus_total_leak = v120`
  - `delta_target_capture_db = -0.0539 dB`
  - `delta_speech_interference_capture_db = -3.3553 dB`
  - `delta_retention_minus_speech_leak_db = +3.3014 dB`

- `near_real_0009`
  - `more_speech_interference_leaky = v120`
  - `more_total_interference_leaky = v120`
  - `delta_speech_interference_capture_db = +9.3707 dB`

解释：

- `v120` 不是全局坏解；
- 它在 `0006` 上的 overlap-local 已比 `v113` 更好；
- 但它仍没解掉真正的 blocker：
  - `0007` local `speech_only` leak 更差
  - `0009` absent local suppression 更差
- 这说明 split 语义本身是有效的，
  但当前 present head 仍会把优化继续拉向：
  - whole / total-leak
  而不是稳定修好：
  - `0007` local `speech_only` leak
  - `0009` absent local suppression

## Bandwidth / transients / listening export

- bandwidth
  - `narrower_candidate_counts = tie:4`
- transients
  - `more_transient_lossy_candidate_counts = v120:1, tie:3`
- `gate_near_real_phone_artifact.py`
  - `overall_pass = false`
  - 仍是：
    - `raw_target_only`
    - `target_present__speech`
    - `target_absent__speech`
    三桶 `missing_bucket`
  - 不作为实质 phone-artifact 裁决
- `export_ab_listening_pack.py`
  - relative `v113`
    - `0 candidate sample`

结论：

- 这轮没有带出新的 bandwidth collapse；
- transient 只新增了一个轻度坏点；
- 但还不到导正式听审的程度。

## Decision

- `v120 = split_present_currentresidual_is_real_progress_but_still_not_listening_candidate`
- 不导听审
- 不把 `v120` 升格成新基座

## New information

这轮新增的最重要信息是：

1. “显式分开的 target-present / target-absent local 控制语义”
   这条方向本身成立；
2. 仅靠：
   - 冻结 complement head
   - 再加一个 gate-side present head
   仍不足以自动解掉：
   - `0007` local `speech_only` leak
   - `0009` absent local suppression；
3. 当前 present head 即使吃 `current_residual`，
   也还是会把优化优先落到：
   - whole-tradeoff
   - total-leak
   - `0006` 这类更容易受益的 target-present speech case

## Next default

默认下一步更新为：

1. 收口 `v120`；
2. preserve/bypass family 保持活跃；
3. 不回退到 `v113-` 之前的旧 family；
4. 若继续 split 语义，
   下一轮不应再只是：
   - 调 `present_max_delta`
   - 或只换 source mode
   的同构 sweep；
5. 下一轮应直接补：
   - present head 的 target-absent veto / guard
   - 或更显式的 target-present activation 约束，
   否则 `0009` absent peak 与 `0007` local speech leak
   仍会一起成为 blocker。
