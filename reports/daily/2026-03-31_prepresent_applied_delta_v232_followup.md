# 2026-03-31 direct pre-present applied-delta supervision on the writable pre-present family: `v232` follow-up

## Summary

- Goal:
  test whether the writable pre-present family was mainly missing direct supervision on the actual delta written by
  `branch_overlap_cancel_pre_present_controller`,
  rather than another full-output quality term.
- Route:
  keep
  `v226`
  intact,
  preserve the existing mild local-window waveform supervision on
  `estimated_waveform_post_pre_present_controller`,
  and add a blocker-local waveform term on the explicit applied delta itself.
- Implementation:
  export
  `estimated_waveform_pre_pre_present_controller`
  and
  `branch_overlap_cancel_pre_present_applied_waveform`,
  then supervise the applied delta against the aligned blocker-local residual target inside
  `local_proxy_intervals`.
- Smoke:
  `_smoke_v232_v226_prepresentdelta05_v1`
  passed and confirmed the new metric was alive:
  `val_pre_present_applied_delta_local_waveform_l1 = 0.001274`.
- Full:
  `v232`
  was training-real,
  but fixed-proxy behavior was practical tie to slightly negative relative to
  `v226`.
- Verdict:
  directly supervising the actual pre-present applied delta is not enough to improve this writable family.
  It does not open a new selective regime.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to export:
  - `estimated_waveform_pre_pre_present_controller`
  - `branch_overlap_cancel_pre_present_applied_waveform`
- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add:
  - `pre_present_applied_delta_local_waveform_weight`
  - `pre_present_applied_delta_local_waveform_l1`
  - aligned local residual targeting for the new delta-loss term
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  and
  `scripts/eval/eval_stft_mask_baseline.py`
  to wire the new outputs and loss path through train and eval.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v232 = v226 + pre_present_applied_delta_local_waveform_weight 0.5`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v232_v226_prepresentdelta05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v232_v226_prepresentdelta05_v1_ft1`
- Trainable:
  unchanged from
  `v226`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T10:49:57`
- Training end:
  `2026-03-31T10:50:38`
- Elapsed:
  `40.719s`
- Final active metrics:
  - `val_loss = 0.279885`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020716`
  - `val_extra_local_waveform_l1 = 0.001274`
  - `val_pre_present_applied_delta_local_waveform_l1 = 0.001274`
  - `val_extra_local_sisdr_loss = 0.521926`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0226 / -0.0275 / -0.0167 / -0.0101 / +0.0078 dB`

### Fixed Checks relative `v226`

- `-0.0175 / -0.0068 / -0.0229 / +0.0135 / -0.0149 dB`

## Read

- The new delta-supervision term is clearly optimization-real.
  It does not collapse to zero,
  and smoke and full runs report the same nontrivial metric scale.
- But output-side it does not improve the writable pre-present family over
  `v226`.
  Relative
  `v226`,
  three fixed checks regress,
  one improves slightly,
  and the active local blocker regresses.
- Relative
  `v157`,
  the route stays near tie overall,
  with only a very small blocker-positive movement that is not large enough to matter.

## Conclusion

- The first direct pre-present applied-delta continuation is now bounded.
- Do not keep micro-sweeping
  `pre_present_applied_delta_local_waveform_weight`
  on this same writable pre-present family by default.
- If this writable line continues,
  the next route should be a more structural writer change,
  not another scalar retune or another direct local-quality term on the same
  `pre_present_controller`
  writer.
