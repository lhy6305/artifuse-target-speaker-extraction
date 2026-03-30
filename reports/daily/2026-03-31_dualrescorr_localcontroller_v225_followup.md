# 2026-03-31 local-window controller supervision on the writable residual-correction path: `v225` follow-up

## Summary

- Goal:
  test whether the weak-but-positive
  `v224`
  local-window waveform family was limited mainly by missing local supervision on
  `branch_overlap_dual_residual_correction_controller`.
- Route:
  keep the
  `v224`
  writable residual-correction waveform objective unchanged,
  and add a new local-window controller target:
  supervise
  `overlap_dual_residual_correction_controller`
  toward
  `1.0`
  inside
  `local_proxy_intervals`.
- Implementation:
  new loss and metric wiring were added to:
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
- Smoke:
  `_smoke_v225_v224_dualrescorr_localcontroller05_v1`
  passed and confirmed the new term was active:
  `val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`
- Full:
  `v225`
  remained training-real,
  but fixed-proxy behavior was worse than
  `v224`.
- Verdict:
  this first controller-local supervision axis is now a reject.
  It is not a no-op,
  but it does not improve the active fixed-proxy tradeoff surface.

## `v225 = v224 + overlap_dual_residual_correction_local_controller_weight 0.5`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v225_v224_dualrescorr_localcontroller05_v1_ft1`
- Trainable:
  unchanged from
  `v224`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T00:06:52`
- Training end:
  `2026-03-31T00:07:53`
- Elapsed:
  `60.941s`
- Final active metrics:
  - `val_loss = 0.339233`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020713`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`
  - `val_overlap_dual_residual_correction_local_target_projection_ratio = 7.25e-08`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

### Fixed Checks relative `v157`

- `-0.0106 / -0.0106 / -0.0024 / +0.0058 / +0.0115 dB`

### Fixed Checks relative `v224`

- `-0.0055 / -0.0091 / -0.0054 / +0.0136 / -0.0040 dB`

## Conclusion

- The new controller-local term is optimization-real,
  but it does not push the output in the desired direction.
- Relative
  `v224`,
  three guardrails regressed,
  one guardrail improved slightly,
  and the local blocker also regressed.
- So the first
  `overlap_dual_residual_correction_local_controller_weight`
  continuation can be closed after a single weight test.
- If this branch continues,
  do not keep micro-sweeping this controller-local scalar.
  The next step must change the local objective more structurally,
  or change the writable path itself.
