# 2026-03-28 overlap dual controller floor `0007-like` `v118` follow-up

## Summary

- 新机制试验：
  - `v118 = v109 + overlap dual controller floor 0007-like v1`
- 新增最小代码改动：
  - `branch_overlap_dual_decoder_gate_floor`
- 最终裁决：
  - fail before expansion / listening
  - `gate floor` 只止住了旧 `v90 / v91` 的 phone-artifact / bandwidth collapse
  - 但没有修正 `direct dual-target final-output path` 的核心问题
  - `v118` 仍然系统性走向：
    - source retention 更高
    - interference leak 也更高

## Setup

- init:
  - `v109`
- teacher:
  - `v109`
- train manifest:
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- val manifest:
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- output checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v118_v109_overlap_dual_controller_floor_0007like_v1_ft1`
- trainable:
  - `branch_overlap_dual_decoder_temporal_model`
  - `branch_overlap_dual_decoder_head`
- key model config:
  - `enable_branch_overlap_dual_decoder_head = true`
  - `branch_overlap_dual_decoder_source_mode = residual`
  - `branch_overlap_dual_decoder_gate_mode = gate`
  - `branch_overlap_dual_decoder_max_delta = 0.08`
  - `branch_overlap_dual_decoder_max_blend = 0.15`
  - `branch_overlap_dual_decoder_gate_floor = 0.75`
- key loss config:
  - `overlap_cancel_waveform_weight = 0.04`
  - `overlap_cancel_target_projection_weight = 0.02`
  - `overlap_dual_mix_consistency_weight = 0.02`
  - `overlap_dual_residual_target_projection_weight = 0.01`
  - `branch_protect_guard_sisdr_weight = 0.003`
  - `branch_protect_teacher_overlap_weight = 3.0`
- selector hits:
  - train:
    - `overlap_cancel = 3 / 108`
    - `overlap_dual = 3 / 108`
    - `branch_protect = 3 / 108`
    - `branch_protect_teacher = 3 / 108`
  - val:
    - `overlap_cancel = 3 / 39`
    - `overlap_dual = 3 / 39`
    - `branch_protect = 3 / 39`
    - `branch_protect_teacher = 3 / 39`

## Synthetic `v109 vs v118`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `-1.7880 dB`
  - `0 improve / 7 regress`
- `same_gender_present_keep_guardrail_v1`
  - `-2.4133 dB`
  - `0 improve / 11 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `-1.1600 dB`
  - `0 improve / 14 regress`
- `hard_present_artifact_proxy_v1`
  - `-2.1929 dB`
  - `0 improve / 7 regress`

结论：

- 四条固定验收全线回退；
- 这版不具备扩到 `v81` 的前提。

## Near-real `v109 vs v118`

### Whole-utterance

- `better_source_retention = v118:3, not_applicable:1`
- `more_interference_leaky = v118:4`
- `better_retention_minus_leak = tie:2, v109:1, not_applicable:1`
- `gate_near_real_tradeoff`
  - `overall_pass = false`
  - failed buckets:
    - `target_present__speech`
    - `target_absent__speech`

关键样本：

- `near_real_0007`
  - `better_source_retention = v118`
  - `more_interference_leaky = v118`
  - `better_retention_minus_leak = v109`
  - `delta_target_capture_db = +1.4838 dB`
  - `delta_interference_capture_db = +12.9325 dB`
  - `delta_retention_minus_leak_db = -11.4487 dB`
- `near_real_0009`
  - `more_interference_leaky = v118`
  - `delta_interference_capture_db = +2.4160 dB`

### Overlap-local

- `better_source_retention = v118:3, not_applicable:1`
- `more_speech_interference_leaky = v118:4`
- `more_total_interference_leaky = v118:4`
- `better_retention_minus_speech_leak = v109:2, v118:1, not_applicable:1`
- `better_retention_minus_total_leak = v109:3, not_applicable:1`
- `more_artifact_proxy_heavy = v109:3, tie:1`

关键样本：

- `near_real_0007`
  - `more_speech_interference_leaky = v118`
  - `more_total_interference_leaky = v118`
  - `better_retention_minus_speech_leak = v118`
  - `better_retention_minus_total_leak = v109`
  - `more_artifact_proxy_heavy = v109`
  - `delta_speech_interference_capture_db = +0.6250 dB`
  - `delta_total_interference_capture_db = +13.4918 dB`
  - `delta_retention_minus_speech_leak_db = +0.8488 dB`
  - `delta_retention_minus_total_leak_db = -12.0179 dB`
- `near_real_0003`
  - `more_speech_interference_leaky = v118`
  - `better_retention_minus_speech_leak = v109`
  - `more_artifact_proxy_heavy = v109`
- `near_real_0006`
  - `more_speech_interference_leaky = v118`
  - `better_retention_minus_speech_leak = v109`
  - `more_artifact_proxy_heavy = v109`
- `near_real_0009`
  - `more_speech_interference_leaky = v118`
  - `delta_speech_interference_capture_db = +1.1491 dB`

## Bandwidth / transient check

- bandwidth:
  - `narrower_candidate_counts = tie:4`
- transients:
  - `more_transient_lossy_candidate_counts = tie:4`

解释：

- `gate floor` 确实把这版从旧 `v90 / v91` 的 phone-artifact / narrowing failure 里拉出来了；
- 但它没有改变更本质的 integration failure：
  - final output 仍被 dual target 直接拉向“更响 / 更 leak”的方向。

补充：

- `gate_near_real_phone_artifact.py` 对这类全量 `ab_inference` pack 仍会出现 `missing_bucket`
  口径问题，不作为实质裁决；
- 当前可用结论仍以：
  - synthetic 四条固定验收
  - whole tradeoff
  - overlap-local
  - bandwidth / transient summary
  为准。

## Decision

- `v118 = dual_controller_floor_stops_phone_artifact_but_not_direct_output_leak_drift`
- 不扩到 `v81`
- 不导听审
- 不继续 `v118+`

## Next default

如果继续 dual 语义，这轮的结论是：

- `gate floor / blend cap` 只能做安全校准；
- 不能把 `direct dual-target final-output path` 变成正确 integration。

所以下一步不应继续：

- `v118+`
- direct-output dual decoder 的同构 sweep

如果还要复用 dual-source / dual-interference 语义，下一轮应改成：

- auxiliary / controller-only 接法
- 不再让 dual target 直接接管 final output
