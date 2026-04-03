# 2026-04-01 artifact representation adapter `ref_film` smoke follow-up

## Summary

- Experiment:
  `v267-smoke = v249 + ref-conditioned shared-representation artifact adapter + split_localmasked artifact teacher anchor`
- Status:
  bounded smoke reject
- Decision:
  do not run full `v267`;
  do not continue the current artifact representation adapter family with
  `ref_bias`, `ref_film`, or same-family blend retunes

## Configuration

- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Smoke output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v267smoke_v249_artifactrepadapterfilm05_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable modules:
  `branch_overlap_artifact_rep_adapter_condition_scale`
  `branch_overlap_artifact_rep_adapter_condition_shift`
  `branch_overlap_artifact_rep_adapter_head`
  `branch_overlap_artifact_rep_adapter_controller_head`
- Key model settings:
  `enable_branch_overlap_artifact_rep_adapter_head = true`
  `branch_overlap_artifact_rep_adapter_max_delta = 0.5`
  `branch_overlap_artifact_rep_adapter_max_blend = 0.05`
  `branch_overlap_artifact_rep_adapter_conditioning_mode = ref_film`
- Key loss settings:
  `artifact_local_split_teacher_waveform_extra_weight = 0.5`
  `artifact_local_bridge_teacher_waveform_extra_weight = 0.0`
  `artifact_local_refine_teacher_waveform_extra_weight = 0.0`
  `artifact_local_mask_adapter_teacher_waveform_extra_weight = 0.0`

## Training Reality Check

- Train start:
  `2026-04-01T21:23:23`
- Train end:
  `2026-04-01T21:23:42`
- Elapsed:
  `19.062 s`
- Trainable fraction:
  `526593 / 8484494 = 0.062065`
- Selector coverage:
  `overlap_dual train 66 / 266, val 14 / 74`
  `overlap_dual_extra train 33 / 266, val 7 / 74`
- Final validation metric:
  `val_artifact_local_split_teacher_waveform_extra_l1 = 0.000116`

Interpretation:

- The new `ref_film` conditioning path is training-real.
- But it still does not open a meaningful output-facing regime.

## Smoke Readout

Relative to `v249`:

- Active real artifact probes:
  `near_real_interval_artifact_probe_v2 = -0.0002 dB`
  `near_real_interval_artifact_probe_v3_subspan = -0.0001 dB`
- Interval-aware leak probe:
  `near_real_interval_leak_probe_v1 = 0.0 dB`
- Matched synthetic artifact-subspan asset:
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan = -0.0011 dB`

## Conclusion

- This is not a useful smoke pass for a full run.
- Adding explicit reference conditioning to the current shared-representation artifact adapter
  still leaves the family output-dormant on the active real artifact probes,
  and the matched synthetic artifact-subspan asset is already slightly negative.
- The blocker is therefore not just missing explicit reference conditioning on the current
  `branch_encoded -> split_localmasked` artifact-adapter route.

## Next Step

- Do not run full `v267`.
- Do not retune `branch_overlap_artifact_rep_adapter_max_blend` on top of this
  `ref_film` continuation.
- Do not replay the same family with `ref_bias`.
- If work continues, it should leave the current artifact representation adapter family
  and switch to a different artifact-specific writer or a different target/shared
  representation family.
