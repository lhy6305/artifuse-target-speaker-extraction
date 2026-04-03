# 2026-04-01 dedicated artifact-refine writer on top of `v249`: `v263` and `v264`

## Summary

- Goal:
  leave the closed dedicated artifact-side bridge family and test a genuinely different
  artifact-specific writer on top of
  `v249`.
- Route:
  add a new
  `branch_overlap_artifact_refine`
  family that rewrites the current output in refine or mask space and only applies inside
  `artifact_local_proxy_intervals`.
- Type:
  new writer family,
  same artifact-subspan bundle and teacher-anchor target.
- Result:
  `v263`
  is a dormant first-launch point,
  while
  `v264`
  opens the same family enough to become strongly positive on the matched synthetic artifact-subspan asset
  without improving the active real artifact probes.
- Verdict:
  close this first dedicated artifact-refine family.
  It does not repair the active real target-conditioned artifact confound on top of
  `v249`.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add a new
  `branch_overlap_artifact_refine`
  writer family with:
  - `enable_branch_overlap_artifact_refine_head`
  - `branch_overlap_artifact_refine_max_delta`
  - `branch_overlap_artifact_refine_max_blend`
  - `estimated_waveform_post_artifact_refine`
- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add
  `artifact_local_refine_teacher_waveform_extra_l1`.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  and
  `scripts/eval/eval_stft_mask_baseline.py`
  to expose the new model and loss flags and log the new metric.
- Validation:
  `py_compile`
  passed after the code change.

## `v263 = v249 + artifact-refine writer, max_blend 0.05`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v263_v249_artifactrefine05_v1_ft1/best.pt`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_artifact_refine_head + branch_overlap_artifact_refine_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-04-01T19:18:06`
- Training end:
  `2026-04-01T19:20:05`
- Elapsed:
  `118.453s`
- Best validation checkpoint:
  `best_val_loss = 0.298198`
- Final validation metric at best epoch:
  `val_artifact_local_refine_teacher_waveform_extra_l1 = 0.000116`
- Selector activity:
  `overlap_dual_extra train 33 / 266, val 7 / 74`

### Read relative `v249`

- Fixed synthetic five-pack:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`
- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.0002 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.0001 dB`
- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +0.0109 dB`

### Read

- `v263`
  is training-real but practically dormant at this application scale.
- It does not move the fixed synthetic surface,
  it does not move the interval-aware leak probe,
  and its active real artifact deltas are only tiny negative near-ties.
- So this first-launch point is not yet evidence for or against the writer family by itself.
  It only says the new writer is too weak to read cleanly at
  `max_blend 0.05`.

## `v264 = v249 + artifact-refine writer, max_blend 0.2`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v264_v249_artifactrefine20_v1_ft1/best.pt`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_artifact_refine_head + branch_overlap_artifact_refine_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-04-01T19:22:41`
- Training end:
  `2026-04-01T19:24:45`
- Elapsed:
  `123.547s`
- Best validation checkpoint:
  `best_val_loss = 0.298196`
- Final validation metric at best epoch:
  `val_artifact_local_refine_teacher_waveform_extra_l1 = 0.000113`
- Selector activity:
  `overlap_dual_extra train 33 / 266, val 7 / 74`

### Read relative `v249`

- Fixed synthetic five-pack:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`
- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.0287 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.0217 dB`
- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +0.5939 dB`

### Direct read relative `v263`

- `near_real_interval_artifact_probe_v3_subspan = -0.0216 dB`
- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +0.5830 dB`

### Read

- Opening the application scale does make this family non-trivial.
  Unlike
  `v263`,
  `v264`
  is now clearly positive on the matched synthetic artifact-subspan asset.
- But the direction is still wrong on the active real target-conditioned artifact probes.
  The leak probe stays exact tie,
  the fixed synthetic five-pack stays exact tie,
  and both active real artifact probes move slightly negative.
- So the writer is no longer merely dormant.
  It now reads as another synthetic-positive and real-negative artifact family,
  not a repair path on top of
  `v249`.

## Conclusion

- `v263`
  is a dormant first-launch point on the dedicated artifact-refine family.
- `v264`
  closes the obvious
  `max_blend`
  open-up continuation.
- Do not continue this family through:
  - more
    `branch_overlap_artifact_refine_max_blend`
    sweeps
  - more small teacher-anchor scalar retunes on the same writer
- The current read is already sufficient:
  once the family becomes non-trivial,
  it again turns synthetic-positive while staying real-negative on the active target-conditioned artifact probes.
  The next change should leave this writer family,
  not keep opening the same application scale.
