# 2026-04-01 adapter artifact `ref_film + temporal` smoke follow-up

## Summary

- Experiment:
  `v269-smoke = v249 trunk init + adapter_mask_head + adapter ref_film + adapter temporal model + artifact-subspan teacher anchor`
- Status:
  bounded smoke reject
- Decision:
  do not run full `v269`;
  do not continue the current adapter-branch artifact family as a simple full-run or scalar-retune branch

## Configuration

- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Smoke output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v269smoke_v249_adapterartifactfilmgru10_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable modules:
  `adapter_condition_scale`
  `adapter_condition_shift`
  `adapter_temporal_model`
  `adapter_mask_head`
- Key model settings:
  `enable_adapter_mask_head = true`
  `enable_adapter_temporal_model = true`
  `adapter_gru_layers = 1`
  `adapter_conditioning_mode = ref_film`
  `adapter_mask_max_delta = 0.1`
- Key loss settings:
  `reconstruction_extra_waveform_weight = 0.2`
  `reconstruction_extra_stft_weight = 0.1`
  `extra_local_teacher_waveform_extra_weight = 0.5`
  `branch_protect_teacher_overlap_weight = 0.04`
  `absent_extra_weight = 0.02`
  `extra_prediction_source = estimated_waveform`
  `local_prediction_source = estimated_waveform`

## Training Reality Check

- Train start:
  `2026-04-01T21:38:59`
- Train end:
  `2026-04-01T21:39:43`
- Elapsed:
  `44.126 s`
- Trainable fraction:
  `1118977 / 3486594 = 0.320937`
- Selector coverage:
  `reconstruction_extra train 63 / 266, val 27 / 74`
  `overlap_dual_extra train 33 / 266, val 7 / 74`
- Final validation metrics:
  `val_extra_local_teacher_waveform_extra_l1 = 0.000251`
  `val_branch_protect_teacher_overlap_l1 = 0.002680`

Interpretation:

- This branch is clearly training-real.
- Unlike the recent artifact-side writer families, it does open a real output-facing effect.
- But the effect is the wrong overall tradeoff.

## Smoke Readout

Relative to `v249`:

- Active real artifact probes:
  `near_real_interval_artifact_probe_v2 = +0.5616 dB`
  `near_real_interval_artifact_probe_v3_subspan = +0.6922 dB`
- Interval-aware leak probe:
  `near_real_interval_leak_probe_v1 = -0.1445 dB`
- Matched synthetic artifact-subspan asset:
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan = -6.6013 dB`
- Fixed synthetic five-pack:
  `abstention = -5.5675 dB`
  `same_gender_keep = -2.2940 dB`
  `hard_present_keep = -2.1554 dB`
  `artifact = -2.6716 dB`
  `local_speech_leak_proxy_v1 = +0.2287 dB`

## Conclusion

- This is the first post-`v249` branch that is strongly positive on both active real artifact probes.
- But it achieves that by collapsing the fixed synthetic guardrails and weakening the interval-aware leak probe.
- So it is not a safe continuation point for a full run.
- The adapter family is therefore not an immediate repair route;
  it is a new mixed evidence point that says the current blocker is reachable from a much more independent branch,
  but the branch currently has no guardrail control.

## Next Step

- Do not run full `v269`.
- Do not treat this as a scalar-retune problem on `adapter_mask_max_delta`.
- If work continues on this family, the next change must add an explicit keep or leak control route for the adapter branch,
  rather than simply opening the same adapter family further.
