# 2026-03-30 pre-present keep-output plus dual residual-correction on `v206`: `v211 / v212 / v213` follow-up

## Summary

- Goal:
  test the first continuation on top of the dual residual-correction family
  where keep-preserve and local-blocker supervision are disjoint both:
  - in trainable path
  - in downstream output application
- Code change:
  exported
  `estimated_waveform_post_pre_present_controller`
  from the model,
  and taught train or eval to use it through
  `extra_prediction_source`
  so the keep-preserve path can supervise the actual pre-present-controller-written intermediate output,
  while the local blocker still uses the dual residual-correction route.
- This new family is training-real:
  the keep selector stayed active
  (`train 63 / 233, val 27 / 67`),
  the overlap-dual selector stayed active
  (`train 33 / 233, val 7 / 67`),
  and both the keep-output metrics and local residual-correction metrics stayed nonzero.
- `v211`
  is the first non-collapsing continuation on top of the dual residual-correction family:
  relative
  `v157`,
  all four non-blocker fixed proxies improved
  (`+0.0461 / +0.0227 / +0.0193 / +0.0433 dB`),
  while the local blocker moved only mildly wrong-way
  (`-0.0364 dB`).
- `v212`
  increased the local correction blend and moved onto a gentler exchange surface:
  relative
  `v157`,
  the local blocker recovered to practical tie or slight positive
  (`+0.0006 dB`),
  but the four non-blocker checks slipped slightly negative
  (`-0.0311 / -0.0156 / -0.0139 / -0.0048 dB`).
- `v213`
  doubled the keep-output weights on top of
  `v212`,
  but landed in practical tie to
  `v212`
  at the active fixed-proxy resolution.
- Verdict:
  this is the best-behaved continuation family so far on top of the dual residual-correction route,
  because disjoint downstream application avoids the catastrophic collapse seen in
  `v209` and `v210`.
  But the first tested axes still do not open a selective regime,
  and the simple keep-weight-strengthening axis is now closed.

## Code Change

- `src/tse_prefix/models/stft_mask_baseline.py`
  now exports
  `estimated_waveform_post_pre_present_controller`
  so the pre-present-controller-written intermediate waveform can be supervised directly.
- `src/tse_prefix/pipeline/runtime_helpers.py`
  now resolves
  `estimated_waveform_post_pre_present_controller`
  as a valid prediction source.
- `scripts/train/train_stft_mask_baseline.py`
  now accepts
  `--loss-extra-prediction-source estimated_waveform_post_pre_present_controller`.
- `scripts/eval/eval_stft_mask_baseline.py`
  now resolves
  `extra_prediction_source`
  in the same way during evaluation,
  with fallback to the old branch-extra behavior when needed.
- `py_compile`
  passed after the code change.

## `v211 = v206 + pre-present keep-output path + dual residual-correction`

- Smoke:
  `_smoke_v211_v206_prepresentkeepoutput_dualresidual_v1`
  validated the new route before the full run.
  The keep selectors and overlap-dual selector were active,
  and both
  `val_reconstruction_extra_waveform_l1`
  and
  `val_overlap_dual_residual_correction_waveform_l1`
  stayed nonzero.
- Additional sanity check:
  the exported
  `estimated_waveform_post_pre_present_controller`
  tensor was confirmed live and distinct from both the final output and the pre-dual output.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v211_v206_prepresentkeepoutput_dualresidual_v1_ft1`
- Trainable:
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-30T21:25:47`
- Training end:
  `2026-03-30T21:26:48`
- Elapsed:
  `60.745s`
- Final active metrics:
  - `val_loss = 0.269343`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001557`
  - `val_overlap_dual_controller_distill_l1 = 0.095253`
  - `val_gate_keep_mean = 0.118117`

### Fixed Checks relative `v157`

- abstention `+0.0461 dB`
- same-gender keep `+0.0227 dB`
- hard-present keep `+0.0193 dB`
- artifact proxy `+0.0433 dB`
- local speech leak proxy `-0.0364 dB`

### Fixed Checks relative `v206`

- abstention `+0.0626 dB`
- same-gender keep `+0.0306 dB`
- hard-present keep `+0.0274 dB`
- artifact proxy `+0.0513 dB`
- local speech leak proxy `-0.0452 dB`

### Verdict

- This is the first continuation on top of the dual residual-correction family
  that stays clearly safe on the four non-blocker guardrails.
- It proves that disjointness in both trainable path and downstream output application
  can avoid the global collapse seen in
  `v209` and `v210`.
- But it is still not promotion-worthy,
  because the active local blocker remains mildly wrong-way.

## `v212 = v211 family, local correction blend 0.08`

- Smoke:
  `_smoke_v212_v211_prepresentkeepoutput_dualresidual_blend008_v1`
  again validated selector activity before the full run.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v212_v211_prepresentkeepoutput_dualresidual_blend008_v1_ft1`
- Trainable:
  still
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`6.3043%`)
- Training start:
  `2026-03-30T21:29:42`
- Training end:
  `2026-03-30T21:30:23`
- Elapsed:
  `41.073s`
- Final active metrics:
  - `val_loss = 0.269335`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- abstention `-0.0311 dB`
- same-gender keep `-0.0156 dB`
- hard-present keep `-0.0139 dB`
- artifact proxy `-0.0048 dB`
- local speech leak proxy `+0.0006 dB`

### Fixed Checks relative `v211`

- abstention `-0.0772 dB`
- same-gender keep `-0.0383 dB`
- hard-present keep `-0.0332 dB`
- artifact proxy `-0.0482 dB`
- local speech leak proxy `+0.0370 dB`

### Verdict

- Raising the local residual-correction blend does not collapse this family.
- Instead it moves the family along a much gentler tradeoff surface:
  local blocker quality recovers toward tie,
  while the four guardrails slide only slightly below zero.
- That is scientifically better-behaved than the older dual residual-correction routes,
  but it is still not selective enough for promotion.

## `v213 = v212 family + keep-output weights x2`

- Smoke:
  `_smoke_v213_v212_prepresentkeepoutput_dualresidual_blend008_keepx2_v1`
  again looked nearly identical to the parent run.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v213_v212_prepresentkeepoutput_dualresidual_blend008_keepx2_v1_ft1`
- Trainable:
  still
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`6.3043%`)
- Training start:
  `2026-03-30T21:33:50`
- Training end:
  `2026-03-30T21:34:27`
- Elapsed:
  `37.005s`
- Final active metrics:
  - `val_loss = 0.273338`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- abstention `-0.0315 dB`
- same-gender keep `-0.0132 dB`
- hard-present keep `-0.0142 dB`
- artifact proxy `-0.0026 dB`
- local speech leak proxy `+0.0021 dB`

### Fixed Checks relative `v212`

- abstention `-0.0004 dB`
- same-gender keep `+0.0024 dB`
- hard-present keep `-0.0003 dB`
- artifact proxy `+0.0022 dB`
- local speech leak proxy `+0.0015 dB`

### Verdict

- Doubling the keep-output weights on top of
  `v212`
  is practical tie at the active fixed-proxy resolution.
- So the first simple keep-weight-strengthening axis on this family is now closed.

## Conclusion

- The new pre-present keep-output plus dual residual-correction family is now bounded in three tested forms:
  - `v211`:
    safe four-positive guardrails,
    but local blocker still mildly wrong-way
  - `v212`:
    local blocker recovers to practical tie,
    but the four guardrails slip slightly negative
  - `v213`:
    simple keep-weight strengthening is practical tie to
    `v212`
- This is the best-behaved dual residual-correction continuation family so far,
  because disjoint downstream output application avoids the catastrophic collapse seen in
  `v209` and `v210`.
- But the tested axes still look like a controlled exchange surface,
  not a selective solution.
- If this branch continues,
  do not keep scaling the same keep-output weights.
  The next step should instead use:
  - a more expressive keep path on the same disjoint downstream route
  - or another keep-specific route that stays disjoint in both trainable path and output application
