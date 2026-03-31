# 2026-03-31 dedicated local writer on `branch_overlap_refine_head`: `v233` follow-up

## Summary

- Goal:
  test whether the next useful writable-path change after
  `v232`
  was to keep the safe keep path on
  `estimated_waveform_post_pre_present_controller`
  while moving the local-only objective onto an earlier and more independent writer,
  `branch_overlap_refine_head`.
- Route:
  start from
  `v224`,
  preserve the existing dual residual-correction local-window supervision,
  keep
  `extra_prediction_source = estimated_waveform_post_pre_present_controller`
  for the keep-side reconstruction terms,
  and add a separate
  `local_prediction_source = estimated_waveform_refine_base`
  with
  `branch_overlap_refine_head`
  trainable.
- Implementation:
  export
  `estimated_waveform_refine_base`,
  add a separate
  `local_prediction_source`
  config path,
  and route only the blocker-local
  `extra_local_*`
  terms through that new local prediction tensor.
- Smoke:
  `_smoke_v233_v224_refinebase_localwave05_v1`
  passed and confirmed the new local writer path was alive:
  `val_extra_local_waveform_l1 = 0.001275`.
- Full:
  `v233`
  was training-real,
  but fixed-proxy behavior showed a steep exchange surface rather than a selective regime.
- Verdict:
  the first dedicated
  `refine_base`
  local-only writer is not the next promotion path.
  It buys large blocker gain mainly by spending abstention and artifact margin.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to export
  `estimated_waveform_refine_base`.
- Updated:
  `src/tse_prefix/pipeline/runtime_helpers.py`
  to accept
  `local_prediction_source`
  and resolve
  `estimated_waveform_refine_base`.
- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  so only the blocker-local
  `extra_local_waveform`
  and
  `extra_local_sisdr`
  terms use
  `local_prediction`,
  while the keep-side reconstruction path still uses
  `extra_prediction`.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  and
  `scripts/eval/eval_stft_mask_baseline.py`
  to wire
  `--loss-local-prediction-source`
  through train and eval.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v233 = v224 + local_prediction_source estimated_waveform_refine_base + branch_overlap_refine_head`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v233_v224_refinebase_localwave05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v233_v224_refinebase_localwave05_v1_ft1`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T11:05:53`
- Training end:
  `2026-03-31T11:06:34`
- Elapsed:
  `41.429s`
- Final active metrics:
  - `val_loss = 0.279156`
  - `val_reconstruction_extra_waveform_l1 = 0.009643`
  - `val_reconstruction_extra_stft_l1 = 0.019893`
  - `val_extra_local_waveform_l1 = 0.001263`
  - `val_pre_present_applied_delta_local_waveform_l1 = 0.001263`
  - `val_extra_local_sisdr_loss = 0.490122`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.7969 / +0.0602 / +0.1109 / -0.4276 / +0.6780 dB`

### Fixed Checks relative `v224`

- `-0.7918 / +0.0617 / +0.1080 / -0.4197 / +0.6625 dB`

## Read

- This run is clearly not a no-op.
  The new local writer path is alive in both smoke and full,
  and the fixed-proxy changes are large.
- But it is also not a selective solution.
  Relative
  `v224`,
  the route buys
  `+0.6625 dB`
  on the active local blocker,
  but it gives back
  `-0.7918 dB`
  on abstention and
  `-0.4197 dB`
  on artifact.
- The shape is therefore different from the near-tie behavior of
  `v232`,
  but it is still a reject:
  a steeper mixed exchange surface,
  not a new basin.
- This also means that simply splitting keep and local supervision into different writable outputs
  is not sufficient by itself if the chosen local-only writer is
  `branch_overlap_refine_head`.

## Conclusion

- The first
  `refine_base`
  local-only writer continuation is now bounded.
- Do not keep micro-sweeping the same
  `estimated_waveform_refine_base + branch_overlap_refine_head`
  writer route by default.
- If the next branch still pursues a writable-path change,
  it should avoid both:
  - the writable pre-present family already bounded through
    `v232`
  - the first
    `refine_base`
    local-only writer route bounded here at
    `v233`
