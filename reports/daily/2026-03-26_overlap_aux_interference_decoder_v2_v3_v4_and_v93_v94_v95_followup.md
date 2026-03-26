# 2026-03-26 overlap auxiliary interference decoder `v93 / v94 / v95` follow-up

## Scope

- Continue the new line `overlap interference auxiliary decoder`.
- Start from the already-human-tested frontier context:
  - `v81` = current research base
  - `v88` = strongest objective frontier of the old subtractive overlap canceller family, but failed human listening
- Test whether the useful `v88` suppression prior can be transferred into a safer `auxiliary_only` regime.

## `v93`: prior transfer through `branch_decoder_temporal_model`

Checkpoint:
- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v93_v88_overlap_aux_interference_decoder_v2_priortransfer_ft1`

Setup:
- init: `v88`
- model:
  - `enable_branch_overlap_cancel_head = true`
  - `branch_overlap_cancel_apply_mode = auxiliary_only`
- trainable:
  - `branch_decoder_temporal_model`
  - `branch_overlap_cancel_head`

Result relative to `v81`:
- `overlap_abstention_proxy_v4_audibility_v1`
  - `+2.0561 dB`
  - `7 improve / 0 regress / 1 near tie`
- `same_gender_present_keep_guardrail_v1`
  - `+0.7050 dB`
  - `9 improve / 1 regress / 1 near tie`
- `hard_present_gate_keep_guardrail_v1`
  - `+0.9061 dB`
  - `15 improve / 1 regress / 0 near tie`

Near-real residual leak floor:
- combined rank:
  - `v88 > v93 > v81 > v54 > v92`
- guardrail-filtered rank:
  - `v88 > v81 > v54 > v92 > v93`
- `present_guardrail_violation_count = 2`

Failure mode:
- `near_real_0003` and `near_real_0007` both cross the target-capture regression guardrail.
- `near_real_0006` and `near_real_0009` do not improve enough to compensate for that regression.

Judgment:
- The `v88 -> auxiliary_only` idea is not wrong.
- But pushing the transfer through `branch_decoder_temporal_model` is too wide; it drags target capture down on hard present cases.

## `v94`: narrower transfer through `branch_decoder_mask_head`

Checkpoint:
- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v94_v88_overlap_aux_interference_decoder_v3_maskheadtransfer_ft1`

Setup:
- init: `v88`
- same auxiliary-decoder structure as `v93`
- trainable changed to:
  - `branch_decoder_mask_head`
  - `branch_overlap_cancel_head`

Result relative to `v81`:
- `overlap_abstention_proxy_v4_audibility_v1`
  - `+2.8521 dB`
  - `7 improve / 1 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+1.2026 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.0078 dB`
  - `14 improve / 1 regress`

Near-real residual leak floor:
- combined rank:
  - `v88 > v93 > v81 > v94 > v54 > v92`
- guardrail-filtered rank:
  - `v88 > v81 > v54 > v92 > v94 > v93`
- `present_guardrail_violation_count = 1`

Sample-level direction:
- `near_real_0006`
  - better suppression than `v81`
- `near_real_0009`
  - still slightly worse suppression than `v81`
- `near_real_0007`
  - remains the only present guardrail violation

Judgment:
- This is a real improvement over `v93`.
- The line now fails on a single concentrated hard-present case instead of broad present regression.

## `v95`: add active hard-present branch-protect selector

Checkpoint:
- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v95_v94_overlap_aux_interference_decoder_v4_hardpresentprotect_ft1`

Setup:
- init: `v94`
- same trainable modules:
  - `branch_decoder_mask_head`
  - `branch_overlap_cancel_head`
- newly activated `branch_protect` selector:
  - `target_full`
  - `target_energy_ratio in [0.05, 0.12]`
  - `overlap_ratio >= 0.6`
  - `target_transient_presence_share_mean <= 0.04`

Result relative to `v81`:
- `overlap_abstention_proxy_v4_audibility_v1`
  - `+3.6205 dB`
  - `7 improve / 1 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+1.6459 dB`
  - `10 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.2283 dB`
  - `15 improve / 1 regress`

Near-real residual leak floor:
- combined rank:
  - `v88 > v93 > v95 > v81 > v94 > v54 > v92`
- guardrail-filtered rank:
  - `v88 > v81 > v54 > v92 > v95 > v94 > v93`
- `present_guardrail_violation_count = 1`

Sample-level direction:
- `near_real_0009`
  - absent suppression is now clearly stronger than `v81`
- `near_real_0006`
  - suppression also improves versus `v81`
- `near_real_0007`
  - still fails the target-capture regression guardrail, and more strongly than `v94`

Judgment:
- The hard-present protect selector did not clear the `0007` guardrail.
- But `v95` is the first auxiliary-decoder variant that simultaneously:
  - keeps the failure localized to one sample
  - materially improves both `0006` and `0009`

## Decision

- `v93` stops here.
- `v94` is an improvement over `v93` but not the final frontier.
- `v95` becomes the next focused human-listening gate for this line.

Current interpretation:
- `auxiliary_only` transfer is now credible.
- The unresolved question is no longer "does this mechanism do anything useful?"
- The unresolved question is:
  - whether the `0006 / 0009` gains in `v95` are audible enough to justify the `0007` downside.

## Focused pack

Pack:
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v95_blind`

Asset audit:
- `all_mono = true`
- `all_have_target = true`

Listening focus:
- `near_real_0006`
  - whether `v95` is actually cleaner in overlap with external guodegang speech
- `near_real_0009`
  - whether the stronger absent suppression is preferable by ear
- `near_real_0007`
  - whether the extra suppression crosses into an audible target-preservation loss

## Next step

Run GUI listening on:

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v95_blind
```
