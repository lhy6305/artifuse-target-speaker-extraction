# 2026-04-01 artifact refine `ref_film` smoke follow-up

## Summary

- Experiment:
  `v268-smoke = v249 + ref-conditioned artifact-refine writer + artifact-subspan teacher anchor`
- Status:
  bounded smoke reject
- Decision:
  do not run full `v268`;
  do not continue the current artifact-refine family with same-family conditioning retunes

## Configuration

- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Smoke output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v268smoke_v249_artifactrefinefilm20_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable modules:
  `branch_overlap_artifact_refine_condition_scale`
  `branch_overlap_artifact_refine_condition_shift`
  `branch_overlap_artifact_refine_head`
  `branch_overlap_artifact_refine_controller_head`
- Key model settings:
  `enable_branch_overlap_artifact_refine_head = true`
  `branch_overlap_artifact_refine_max_delta = 0.15`
  `branch_overlap_artifact_refine_max_blend = 0.2`
  `branch_overlap_artifact_refine_conditioning_mode = ref_film`
- Key loss settings:
  `artifact_local_refine_teacher_waveform_extra_weight = 0.5`
  `artifact_local_split_teacher_waveform_extra_weight = 0.0`

## Training Reality Check

- Train start:
  `2026-04-01T21:29:21`
- Train end:
  `2026-04-01T21:30:13`
- Elapsed:
  `51.912 s`
- Trainable fraction:
  `527107 / 8485008 = 0.062122`
- Selector coverage:
  `overlap_dual train 66 / 266, val 14 / 74`
  `overlap_dual_extra train 33 / 266, val 7 / 74`
- Final validation metric:
  `val_artifact_local_refine_teacher_waveform_extra_l1 = 0.000116`

Interpretation:

- The new `ref_film` conditioning path is training-real.
- The writer is no longer purely dormant.
- But the output-facing read still does not move in the correct direction.

## Smoke Readout

Relative to `v249`:

- Active real artifact probes:
  `near_real_interval_artifact_probe_v2 = -0.0002 dB`
  `near_real_interval_artifact_probe_v3_subspan = -0.0001 dB`
- Interval-aware leak probe:
  `near_real_interval_leak_probe_v1 = 0.0 dB`
- Matched synthetic artifact-subspan asset:
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +0.0042 dB`

## Conclusion

- This is not a useful smoke pass for a full run.
- Adding explicit reference conditioning to the current artifact-refine writer
  still leaves the active real artifact probes practical tie to tiny negative,
  while the matched synthetic artifact-subspan asset only moves to a tiny positive.
- The blocker is therefore not just missing target conditioning on the current
  artifact-refine writer family.

## Next Step

- Do not run full `v268`.
- Do not retune `branch_overlap_artifact_refine_max_blend` on top of this
  `ref_film` continuation.
- If work continues, it should leave the current artifact-refine family and
  switch to a different artifact-specific writer or a different target/shared
  representation family.
