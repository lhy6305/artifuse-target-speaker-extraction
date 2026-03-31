# 2026-03-31 sparse controller selectivity on the writable residual-correction branch: `v235` follow-up

## Summary

- Goal:
  test whether the remaining blocker on the
  `v224`
  family was mainly controller selectivity rather than correction-estimate quality.
- Route:
  keep
  `v224`
  intact,
  preserve the existing writable residual-correction local-window waveform term,
  keep the local controller term inside
  `local_proxy_intervals`,
  and add an explicit nonlocal complement term that pushes the same controller toward
  `0`
  outside the blocker windows.
- Implementation:
  add
  `overlap_dual_residual_correction_nonlocal_controller_weight`
  and
  `overlap_dual_residual_correction_nonlocal_controller_l1`,
  where the nonlocal intervals are built as the complement of
  `local_proxy_intervals`
  over the valid target duration.
- Smoke:
  `_smoke_v235_v224_dualrescorr_sparsecontroller_v1`
  passed and confirmed both controller terms were alive:
  `val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`,
  `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.012859`.
- Full:
  `v235`
  was training-real,
  but fixed-proxy behavior was practical tie to slightly negative relative to
  `v224`.
- Verdict:
  the first sparse controller selectivity continuation does not improve the
  `v224`
  family.
  This axis can be closed.

## Code Change

- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to:
  - add complement-interval construction for local windows
  - add
    `overlap_dual_residual_correction_nonlocal_controller_weight`
  - add
    `overlap_dual_residual_correction_nonlocal_controller_l1`
  - supervise
    `branch_overlap_dual_residual_correction_controller`
    toward
    `1`
    inside blocker windows and toward
    `0`
    in the complement intervals
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose the new weight and carry the new metric through train and val aggregation.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v235 = v224 + local controller 0.5 + nonlocal controller 0.1`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v235_v224_dualrescorr_sparsecontroller_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v235_v224_dualrescorr_sparsecontroller_v1_ft1`
- Trainable:
  unchanged from
  `v224`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T11:57:30`
- Training end:
  `2026-03-31T11:58:16`
- Elapsed:
  `46.074s`
- Final active metrics:
  - `val_loss = 0.340519`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020713`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.012859`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0106 / -0.0106 / -0.0024 / +0.0058 / +0.0115 dB`

### Fixed Checks relative `v224`

- `-0.0055 / -0.0091 / -0.0054 / +0.0136 / -0.0040 dB`

## Read

- The sparse controller idea is clearly optimization-real.
  Both local and nonlocal controller terms are nonzero,
  and the intended overlap selector remains active.
- But output-side it does not sharpen selectivity.
  Relative
  `v224`,
  three non-blocker checks regress slightly,
  one improves slightly,
  and the active local blocker also regresses slightly.
- This places
  `v235`
  in the same practical-tie basin as the first local-controller continuation,
  not in a new blocker-positive regime.

## Conclusion

- The first sparse controller selectivity continuation on the writable residual-correction branch is now bounded.
- Do not keep micro-sweeping
  `overlap_dual_residual_correction_local_controller_weight`
  plus
  `overlap_dual_residual_correction_nonlocal_controller_weight`
  on top of
  `v224`
  by default.
- If this family continues,
  the next route should change the local objective or the writable path more structurally,
  not just add more controller sparsity shaping on the same branch.
