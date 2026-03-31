# 2026-03-31 dedicated refine apply-controller on top of `v240`: `v248` follow-up

## Summary

- Goal:
  test whether the mixed near-real failure of
  `v240`
  could be repaired by adding a dedicated per-frame apply controller to the split-route
  `refine_base`
  local writer,
  instead of using another keep-side repair or another low-weight shape regularizer.
- Route:
  start from
  `v240`,
  keep the split local writer and keep-side repair unchanged,
  add
  `branch_overlap_refine_apply_controller_head`,
  and let it scale
  `branch_overlap_refine_ratio`
  before the
  `refine_base`
  writeback is applied.
- Smoke:
  `_smoke_v248_v240_refineapplycontroller_v1`
  passed,
  with no init or state-dict mismatch,
  and confirmed that the widened trainable set was active
  (`921607 / 8484497`,
  `10.8622%`).
- Full:
  `v248`
  was training-real.
  Relative
  `v240`,
  all four non-blocker fixed checks improved again,
  while the active blocker gave back a smaller amount
  than the keep-heavy
  `v245-v247`
  continuations.
  But both targeted near-real probes still moved negative.
- Verdict:
  this is not a no-op,
  but it is still a keep-lean continuation on the same split-route
  `refine_base`
  family,
  not the needed near-real repair.
  The first dedicated
  `refine_apply_controller`
  axis is bounded.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add
  `enable_branch_overlap_refine_apply_controller`,
  instantiate
  `branch_overlap_refine_apply_controller_head`,
  initialize its final bias to
  `6.0`
  so a
  `v240`
  parent starts near the original writeback behavior,
  and export
  `branch_overlap_refine_apply_controller`
  in the model outputs.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose
  `--model-enable-branch-overlap-refine-apply-controller`
  and treat
  `branch_overlap_refine_apply_controller_head.`
  as an optional init prefix so older checkpoints can still load.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v248 = v240 + dedicated branch_overlap_refine_apply_controller`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v248_v240_refineapplycontroller_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v248_v240_refineapplycontroller_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_refine_apply_controller_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`921607 / 8484497`,
  `10.8622%`)
- Training start:
  `2026-03-31T21:30:51`
- Training end:
  `2026-03-31T21:33:03`
- Elapsed:
  `132.191s`
- Best validation checkpoint:
  epoch 3 with
  `best_val_loss = 0.299766`
- Final validation metrics at best epoch:
  - `val_reconstruction_extra_waveform_l1 = 0.009613`
  - `val_reconstruction_extra_stft_l1 = 0.019930`
  - `val_extra_local_waveform_l1 = 0.001262`
  - `val_extra_local_nonlocal_waveform_l1 = 0.000003`
  - `val_pre_present_applied_delta_local_waveform_l1 = 0.001263`
  - `val_branch_protect_teacher_overlap_l1 = 0.000464`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.124413`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.007736`
  - `val_gate_keep_mean = 0.122211`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+0.3913 / +0.2955 / +0.5538 / +0.0917 / +0.4841 dB`

### Fixed Checks relative `v240`

- `+0.1651 / +0.1168 / +0.3084 / +0.0156 / -0.0518 dB`

## Targeted Near-Real Probes relative `v240`

- `near_real_speech_probe_v1 = -0.0360 dB`
- `friend_raw = -0.0315 dB`
- `guodegang_raw = -0.0497 dB`
- `near_real_0003 / 0004 / 0006 = -0.0221 / -0.0408 / -0.0497 dB`
- `near_real_guodegang_transient_probe_v1 = -0.0497 dB`
- `friend_absent_820s = -0.0779 dB`
- `guodegang_anchor_120s = -0.0922 dB`

## Read

- The new controller is clearly not a semantic no-op.
  Smoke loaded the old
  `v240`
  checkpoint cleanly into the widened model,
  and full moved the fixed synthetic surface in a coherent direction.
- But that direction is still the same family shape:
  relative
  `v240`,
  the four non-blocker checks improve
  while the active blocker gives back
  `-0.0518 dB`.
  This is milder than
  `v245-v247`,
  but it is still not a selective repair.
- The targeted near-real probes confirm that read.
  The line stays slightly negative on the overall speech probe,
  and the drag remains concentrated on the same difficult clips:
  `friend_absent_820s`
  and
  `guodegang_anchor_120s`.
- So the useful conclusion is structural:
  adding a dedicated per-frame scale head on top of the same
  `refine_base`
  writer does not change the family enough.
  It still behaves like a keep-lean continuation,
  not like a new near-real repair regime.

## Conclusion

- `v248`
  is a bounded reject on top of
  `v240`.
- Do not continue this family by micro-sweeping a new refine-apply-controller scalar or by adding another low-weight penalty on the same writer.
- If the split-route
  `refine_base`
  family continues,
  the next branch should change local-writer application structure more materially than adding a second scale head on the same
  `branch_overlap_refine_head`
  writeback.
