# 2026-04-01 artifact representation adapter v266 follow-up

## Summary

- Experiment:
  `v266 = v249 + branch_encoded artifact representation adapter + split_localmasked artifact teacher anchor`
- Status:
  bounded reject
- Decision:
  do not continue the `artifact representation adapter` family on top of the current
  `split_localmasked` writer and artifact-subspan teacher-anchor objective

## Configuration

- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v266_v249_artifactrepadapter05_v1_ft1/best.pt`
- Trainable modules:
  `branch_overlap_artifact_rep_adapter_head`
  `branch_overlap_artifact_rep_adapter_controller_head`
- Key model settings:
  `enable_branch_overlap_artifact_rep_adapter_head = true`
  `branch_overlap_artifact_rep_adapter_max_delta = 0.5`
  `branch_overlap_artifact_rep_adapter_max_blend = 0.05`
- Key loss settings:
  `artifact_local_split_teacher_waveform_extra_weight = 0.5`
  `artifact_local_bridge_teacher_waveform_extra_weight = 0.0`
  `artifact_local_refine_teacher_waveform_extra_weight = 0.0`
  `artifact_local_mask_adapter_teacher_waveform_extra_weight = 0.0`
- Training bundle:
  `train/val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_artifactsubspan_bundle_v1`

## Training Reality Check

- Train start:
  `2026-04-01T20:30:56`
- Train end:
  `2026-04-01T20:42:09`
- Elapsed:
  `672.252 s`
- Trainable fraction:
  `394497 / 8352398 = 0.047232`
- Selector coverage:
  `overlap_dual train 66 / 266, val 14 / 74`
  `overlap_dual_extra train 33 / 266, val 7 / 74`
- Final validation metric:
  `val_artifact_local_split_teacher_waveform_extra_l1 = 0.000108`

Interpretation:

- The new artifact-only extra term is non-zero, so the continuation is training-real.
- But the new representation adapter does not open a meaningful output-facing regime.

## Evaluation

Relative to `v249`:

- Fixed synthetic five-pack:
  `abstention = 0.0 dB`
  `same_gender_keep = 0.0 dB`
  `hard_present_keep = 0.0 dB`
  `artifact = 0.0 dB`
  `local_speech_leak_proxy_v1 = 0.0 dB`
- Interval-aware leak probe:
  `near_real_interval_leak_probe_v1 = 0.0 dB`
- Active real artifact probes:
  `near_real_interval_artifact_probe_v2 = -0.0061 dB`
  `near_real_interval_artifact_probe_v3_subspan = -0.0006 dB`
- Matched synthetic artifact-subspan asset:
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan = -1.7634 dB`
  with `1 improved / 4 regressed / 2 tie`

## Conclusion

- This family is not a real-side repair.
- It is also not a useful dormant first-launch point:
  the real artifact probes stay practical tie to tiny negative,
  while the matched synthetic artifact-subspan asset already regresses materially.
- The current bottleneck is therefore not just missing shared-representation capacity on
  `branch_encoded`.

## Next Step

- Do not retune `branch_overlap_artifact_rep_adapter_max_blend` on top of `v266`.
- Do not continue the same `split_localmasked` teacher-anchor family with a larger
  representation-only sweep.
- If work continues, it should leave the current artifact-side writer and
  artifact-representation adapter families and switch to a different
  artifact-specific writer or a different target/shared representation family.
