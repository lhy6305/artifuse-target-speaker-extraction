# 2026-04-01 adapter artifact family `v271-smoke` and `v272-smoke` follow-up

## Summary

- `v271-smoke = v270-smoke + strict base fallback when no artifact-local interval exists`
- `v272-smoke = v270-smoke + 5x keep or abstention guardrail weights`
- Status:
  both are bounded smoke rejects
- Decision:
  do not continue the current adapter artifact family through
  strict-fallback semantics or simple keep or abstention scalar retunes

## `v271-smoke`

- Route:
  `v249 trunk init + adapter_mask_head + adapter ref_film + adapter temporal model + adapter artifact-local hard mask + strict base fallback + artifact-subspan teacher anchor`
- Output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v271smoke_v249_adapterartifactfilmgru_strictmask10_v1_ft1/best.pt`
- Train start:
  `2026-04-01T22:06:24`
- Train end:
  `2026-04-01T22:06:41`
- Elapsed:
  `17.269 s`
- Trainable fraction:
  `0.320937`
- Final validation metrics:
  `val_extra_local_teacher_waveform_extra_l1 = 0.000226`
  `val_branch_protect_teacher_overlap_l1 = 0.003306`

### Readout

- Relative to `v249`:
  exact replay of `v270-smoke`
  on all active reads
- Fixed synthetic five-pack:
  `-8.0302 / -2.4539 / -2.1597 / -2.9470 / +0.4976 dB`
- Interval-aware leak probe:
  `-0.0125 dB`
- Active real artifact probes:
  `+0.3988 / +0.5629 dB`
- Matched synthetic artifact-subspan:
  `-6.5503 dB`
- Relative to `v270-smoke`:
  `0.0 dB`
  on
  `overlap_abstention_proxy_v4_audibility_v1`
  and
  `near_real_interval_artifact_probe_v3_subspan`

### Interpretation

- `strict base fallback` is operationally dormant on the current smoke stack.
- This is not a new continuation point.
- Do not continue this axis with more masking or fallback semantics alone.

## `v272-smoke`

- Route:
  `v270-smoke + stronger reconstruction or teacher or absent guardrail weights`
- Output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v272smoke_v249_adapterartifactfilmgru_hardmask_guardrail5x_v1_ft1/best.pt`
- Train start:
  `2026-04-01T22:11:07`
- Train end:
  `2026-04-01T22:11:21`
- Elapsed:
  `14.561 s`
- Trainable fraction:
  `0.320937`
- Key weight changes vs `v270-smoke`:
  `reconstruction_extra_waveform_weight 0.2 -> 1.0`
  `reconstruction_extra_stft_weight 0.1 -> 0.5`
  `branch_protect_teacher_overlap_weight 0.04 -> 0.2`
  `absent_extra_weight 0.02 -> 0.1`
- Final validation metrics:
  `val_extra_local_teacher_waveform_extra_l1 = 0.000226`
  `val_branch_protect_teacher_overlap_l1 = 0.003306`

### Readout

- Relative to `v249`:
  practical tie to `v270-smoke`
- Fixed synthetic five-pack:
  `-8.0302 / -2.4539 / -2.1597 / -2.9470 / +0.4976 dB`
- Interval-aware leak probe:
  `-0.0125 dB`
- Active real artifact probes:
  `+0.3966 / +0.5626 dB`
- Matched synthetic artifact-subspan:
  `-6.5616 dB`
- Relative to `v270-smoke`:
  `0.0 dB`
  on
  `overlap_abstention_proxy_v4_audibility_v1`
  and
  `near_real_interval_leak_probe_v1`
  and
  `-0.0002 dB`
  on
  `near_real_interval_artifact_probe_v3_subspan`

### Interpretation

- Simply increasing the current synthetic keep or abstention losses does not move the current adapter family into a controlled regime.
- The current adapter family is not blocked on small guardrail scalar values.
- Do not continue this family through scalar retunes of the same
  `reconstruction_extra`
  or
  `branch_protect_teacher_overlap`
  or
  `absent_extra`
  route.

## Conclusion

- `v271-smoke` closes the strict-fallback semantic axis.
- `v272-smoke` closes the simple guardrail-weight retune axis on the current adapter family.
- If this adapter family continues,
  the next useful change must add a more explicit structural guardrail route,
  not another masking tweak and not another scalar increase on the existing losses.
