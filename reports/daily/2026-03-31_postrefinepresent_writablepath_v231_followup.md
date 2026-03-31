# 2026-03-31 writable-path continuation before the cancel route: `v231` follow-up

## Summary

- Goal:
  test whether the steep
  `v230`
  tradeoff was mainly caused by the local objective still backpropagating through the frozen cancel path.
- Implementation:
  export a new intermediate writable output
  `estimated_waveform_post_refine_present`
  after
  `branch_overlap_refine_present_head`
  but before
  `branch_overlap_cancel_head`,
  expose it through
  `extra_prediction_source`,
  and launch the same trainable route shape as
  `v230`.
- Code:
  updated
  `src/tse_prefix/models/stft_mask_baseline.py`,
  `src/tse_prefix/pipeline/runtime_helpers.py`,
  and
  `scripts/train/train_stft_mask_baseline.py`;
  `py_compile`
  passed before launch.
- Result:
  `v231`
  was training-real,
  but fixed-proxy behavior was even worse than
  `v230`.
- Verdict:
  the problem is not mainly the frozen cancel path.
  The
  `refine_present`
  writer itself is already on the wrong tradeoff surface for this blocker.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v231 = v226 + estimated_waveform_post_refine_present + branch_overlap_refine_present_head`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v231_v226_postrefinepresent_refineopen_v1_ft1`
- Trainable:
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_refine_present_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `790022 / 8352912`,
  `9.4580%`
- Training start:
  `2026-03-31T01:09:38`
- Training end:
  `2026-03-31T01:10:44`
- Elapsed:
  `65.904s`
- Final active metrics:
  - `val_loss = 0.279174`
  - `val_reconstruction_extra_waveform_l1 = 0.009624`
  - `val_reconstruction_extra_stft_l1 = 0.020134`
  - `val_extra_local_waveform_l1 = 0.001255`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-1.3804 / -1.1572 / -0.6196 / -0.9608 / +1.1856 dB`

### Fixed Checks relative `v226`

- `-1.3753 / -1.1365 / -0.6258 / -0.9372 / +1.1629 dB`

### Fixed Checks relative `v230`

- `-0.2026 / -0.1462 / -0.1320 / -0.1930 / +0.0673 dB`

## Read

- `v231`
  does not support the hypothesis that the frozen cancel path was the main cause of
  `v230`.
- Removing that downstream cancel stage from the local supervision target made the guardrails even worse,
  while the blocker improved a little more.
- So the bad tradeoff appears earlier:
  once the local route is writing through
  `branch_overlap_refine_present_head`,
  this blocker already lands on a strong guardrail-for-local exchange surface.

## Conclusion

- The first explicit pre-cancel writable-output experiment is now closed.
- `estimated_waveform_post_refine_present`
  is a useful debug and experimentation hook,
  but it does not rescue the family.
- If this line continues at all,
  it should not continue through the same
  `refine_present`
  writer.
  The next route should either:
  - move earlier than
    `refine_present`,
    or
  - use a different local writer entirely.
