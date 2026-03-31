# 2026-03-31 local-window SI-SDR on the writable residual-correction branch: `v234` follow-up

## Summary

- Goal:
  test whether the best still-open local branch after
  `v224`
  was mainly limited by waveform L1,
  and whether a more structural local-window quality term on the same writable
  `overlap_dual_residual_correction`
  branch could improve the blocker.
- Route:
  keep
  `v224`
  intact,
  preserve the existing local-window waveform term on
  `branch_overlap_dual_residual_correction_estimate_waveform`,
  and add an interval SI-SDR term on that same writable correction estimate.
- Implementation:
  add
  `overlap_dual_residual_correction_local_sisdr_weight`
  and
  `overlap_dual_residual_correction_local_sisdr_loss`
  to the train pipeline,
  using the same
  `local_proxy_intervals`
  and the same current-output residual target already used by the local waveform branch term.
- Smoke:
  `_smoke_v234_v224_dualrescorr_localsisdr001_v1`
  passed and confirmed the new term was alive:
  `val_overlap_dual_residual_correction_local_sisdr_loss = 1.472650`.
- Full:
  `v234`
  was training-real,
  but fixed-proxy behavior was slight guardrail-positive and blocker-negative relative to
  `v224`.
- Verdict:
  the first local-window SI-SDR continuation on the writable residual-correction branch is not the next promotion path.
  It behaves more like a mild regularizer than a blocker-solving local objective.

## Code Change

- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add:
  - `overlap_dual_residual_correction_local_sisdr_weight`
  - `overlap_dual_residual_correction_local_sisdr_loss`
  - interval SI-SDR supervision on
    `overlap_dual_residual_correction_prediction`
    inside
    `local_proxy_intervals`
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose the new CLI weight,
  carry the new metric through train and val aggregation,
  and store it in epoch history and
  `train_summary.json`.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v234 = v224 + overlap_dual_residual_correction_local_sisdr_weight 0.001`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v234_v224_dualrescorr_localsisdr001_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v234_v224_dualrescorr_localsisdr001_v1_ft1`
- Trainable:
  unchanged from
  `v224`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T11:21:28`
- Training end:
  `2026-03-31T11:22:13`
- Elapsed:
  `45.432s`
- Final active metrics:
  - `val_loss = 0.278937`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020710`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_overlap_dual_residual_correction_local_sisdr_loss = 0.323750`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `+0.0269 / +0.0103 / +0.0067 / +0.0363 / -0.0218 dB`

### Fixed Checks relative `v224`

- `+0.0320 / +0.0118 / +0.0037 / +0.0441 / -0.0373 dB`

## Read

- The new term is clearly optimization-real.
  Smoke and full both report a nonzero
  `overlap_dual_residual_correction_local_sisdr_loss`,
  and the branch stays selected on the intended local blocker samples.
- But output-side the direction is not what this family needs.
  Relative
  `v224`,
  all four non-blocker checks move slightly positive,
  while the active local blocker moves slightly negative.
- So this is not a new selective regime and not even a meaningful local-positive tradeoff.
  It looks more like a mild keep-side regularizer attached to the same correction branch.

## Conclusion

- The first local-window SI-SDR continuation on the writable residual-correction branch is now bounded.
- Do not keep micro-sweeping
  `overlap_dual_residual_correction_local_sisdr_weight`
  on top of
  `v224`
  by default.
- If this family continues,
  the next route should be a materially different local objective or a more structural path change,
  not another scalar retune of the same residual-correction local quality term.
