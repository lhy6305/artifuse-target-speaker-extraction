# 2026-03-31 local-window SI-SDR supervision on the writable pre-present main-output route: `v228` follow-up

## Summary

- Goal:
  test whether the first writable pre-present main-output route found in
  `v226`
  was mainly limited by the local objective being waveform L1,
  not by the route itself.
- Route:
  keep
  `v226`
  intact,
  preserve
  `extra_local_waveform_weight = 0.5`,
  and add a new blocker-local
  `extra_local_sisdr_weight`
  term on the same
  `estimated_waveform_post_pre_present_controller`
  output.
- Implementation:
  code was added to support interval-concatenated SI-SDR on
  `local_proxy_intervals`
  and to wire
  `extra_local_sisdr_loss`
  through train and val summaries.
- Smoke:
  `_smoke_v228_v226_extralocalsisdr001_v1`
  passed and confirmed the new term was active:
  `val_extra_local_sisdr_loss = 0.521498`.
- Full:
  `v228`
  was also training-real,
  but fixed-proxy behavior almost exactly reproduced the already-closed
  `v227`
  high-tradeoff shape.
- Verdict:
  this first local-window SI-SDR continuation is not a new regime.
  It behaves like another way to push farther along the same
  guardrail-versus-local exchange surface.

## Code Change

- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add:
  - `interval_sisdr_loss()`
  - `extra_local_sisdr_weight`
  - `extra_local_sisdr_loss`
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to add:
  - `--loss-extra-local-sisdr-weight`
  - train and val metric aggregation for
    `extra_local_sisdr_loss`
  - summary serialization for the new metric
- Validation:
  `py_compile`
  passed before launching
  `v228`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v228 = v226 + extra_local_sisdr_weight 0.001`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v228_v226_extralocalsisdr001_v1_ft1`
- Trainable:
  unchanged from
  `v226`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T00:44:10`
- Training end:
  `2026-03-31T00:44:49`
- Elapsed:
  `39.669s`
- Final active metrics:
  - `val_loss = 0.279770`
  - `val_reconstruction_extra_waveform_l1 = 0.009663`
  - `val_reconstruction_extra_stft_l1 = 0.020724`
  - `val_extra_local_waveform_l1 = 0.001274`
  - `val_extra_local_sisdr_loss = 0.520717`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0951 / -0.0614 / -0.0457 / -0.0633 / +0.0480 dB`

### Fixed Checks relative `v226`

- `-0.0900 / -0.0407 / -0.0519 / -0.0396 / +0.0253 dB`

## Conclusion

- The new local-window SI-SDR term is optimization-real.
  It does not collapse to zero,
  and it clearly changes training.
- But it does not open a new selective regime on this writable route.
  Relative
  `v226`,
  it improves the blocker and degrades all four guardrails,
  almost exactly like the already-closed
  `v227`
  higher-waveform-weight continuation.
- So this first
  `extra_local_sisdr_weight`
  continuation is now bounded:
  do not keep micro-sweeping this scalar on the same writable pre-present main-output route by default.
- If this branch continues,
  the next step should be a more structural writable-path change,
  or a local objective that is not just another stronger direct-quality term on the same output path.
