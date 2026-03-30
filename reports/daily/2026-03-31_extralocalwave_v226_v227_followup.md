# 2026-03-31 local-window waveform supervision on the writable pre-present main-output route: `v226 / v227` follow-up

## Summary

- Goal:
  test whether the next writable-path change after
  `v225`
  should move the blocker-local objective off the residual-correction add-on path
  and onto the main writable
  `estimated_waveform_post_pre_present_controller`
  route.
- Implementation:
  the already-landed
  `extra_local_waveform_weight`
  plumbing was used to supervise
  `extra_prediction`
  inside
  `local_proxy_intervals`
  while keeping the
  `v224`
  residual-correction local-window waveform term active.
- `v226`
  was the first real run on this new route with
  `extra_local_waveform_weight = 0.5`.
  It was training-real and mildly positive on the blocker,
  but only by accepting small guardrail erosion.
- `v227`
  raised the same weight to
  `2.0`.
  The blocker improved further,
  but all four guardrails degraded materially.
- Verdict:
  this writable-path change is real,
  not a no-op,
  but the first
  `0.5 -> 2.0`
  sweep only steepens the same mild exchange surface.
  Do not keep micro-sweeping this scalar by default.

## Code Context

- The new local-window pre-present main-output loss was already wired before launch in:
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
- New loss and metric:
  - `extra_local_waveform_weight`
  - `extra_local_waveform_l1`
- Validation:
  `py_compile`
  had already passed before
  `v226`
  launched.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v226 = v224 + extra_local_waveform_weight 0.5`

- Smoke:
  `_smoke_v226_v224_extralocalwave05_v1`
  passed.
  The new term was active:
  `val_extra_local_waveform_l1 = 0.001275`.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v226_v224_extralocalwave05_v1_ft1`
- Trainable:
  unchanged from
  `v224`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T00:27:28`
- Training end:
  `2026-03-31T00:28:32`
- Elapsed:
  `64.381s`
- Final active metrics:
  - `val_loss = 0.279248`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020718`
  - `val_extra_local_waveform_l1 = 0.001274`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0051 / -0.0207 / +0.0062 / -0.0236 / +0.0226 dB`

### Fixed Checks relative `v224`

- `-0.0000 / -0.0193 / +0.0032 / -0.0157 / +0.0071 dB`

### Verdict

- This was the first writable-path change after
  `v225`
  that was clearly training-real on the active blocker.
- But it did not open a new regime.
  Relative
  `v224`,
  the blocker only moved slightly,
  while
  `same-gender keep`
  and
  `artifact`
  turned modestly negative.
- So this was enough to justify one larger follow-up weight jump,
  not a promotion discussion.

## `v227 = v226 + extra_local_waveform_weight 2.0`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v227_v226_extralocalwave20_v1_ft1`
- Trainable:
  unchanged from
  `v226`
  (`6.3043%`)
- Training start:
  `2026-03-31T00:32:35`
- Training end:
  `2026-03-31T00:33:19`
- Elapsed:
  `43.940s`
- Final active metrics:
  - `val_loss = 0.281160`
  - `val_reconstruction_extra_waveform_l1 = 0.009663`
  - `val_reconstruction_extra_stft_l1 = 0.020724`
  - `val_extra_local_waveform_l1 = 0.001274`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  unchanged from
  `v226`

### Fixed Checks relative `v157`

- `-0.0942 / -0.0600 / -0.0451 / -0.0621 / +0.0478 dB`

### Fixed Checks relative `v226`

- `-0.0891 / -0.0392 / -0.0513 / -0.0385 / +0.0251 dB`

### Verdict

- Raising the same scalar from
  `0.5`
  to
  `2.0`
  does not preserve the mild
  `v226`
  shape.
- The blocker improves further,
  but all four guardrails move materially negative.
- So the first follow-up weight jump is enough to bound this family:
  the new writable path is real,
  but simple scalar strengthening only steepens the guardrail-versus-local tradeoff.

## Conclusion

- The useful result here is structural:
  moving the local-window waveform supervision from the residual-correction add-on path
  to the writable pre-present main-output route does change output behavior.
- The limiting result is also clear:
  the first
  `extra_local_waveform_weight`
  sweep
  `0.5 -> 2.0`
  does not unlock selectivity.
  It only trades guardrails for more blocker movement.
- So this family should now be treated as:
  - writable-path-change evidence
  - mildly informative at
    `v226`
  - closed for default scalar micro-sweeps after
    `v227`
- If this branch continues,
  the next step should change the local objective more structurally,
  or change the writable path more substantially than direct local-window waveform supervision on
  `estimated_waveform_post_pre_present_controller`.
