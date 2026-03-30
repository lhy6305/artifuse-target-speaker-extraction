# 2026-03-31 writable-path continuation on the pre-dual output route: `v229` and `v230` follow-up

## Summary

- Goal:
  test whether the first writable pre-present main-output route found in
  `v226`
  was mainly limited by supervising too early an output,
  and whether the later pre-dual route becomes useful once it gets its own trainable writer.
- Route:
  start from
  `v226`,
  move
  `extra_prediction_source`
  from
  `estimated_waveform_post_pre_present_controller`
  to
  `estimated_waveform_pre_dual_residual_correction`,
  then reopen
  `branch_overlap_refine_present_head`
  on top of that later route.
- Result:
  the output-position-only move in
  `v229`
  was slightly negative,
  while the added route capacity in
  `v230`
  sharply improved the blocker and sharply regressed all four guardrails.
- Verdict:
  the tested pre-dual writable-path family is now bounded through
  `v230`.
  A later writable output alone is not helpful,
  and simply opening
  `branch_overlap_refine_present_head`
  on that route only steepens the same guardrail-versus-local tradeoff.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v229 = v226 + extra_prediction_source estimated_waveform_pre_dual_residual_correction`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v229_v226_preduduallocalwave05_v1_ft1`
- Trainable:
  unchanged from
  `v226`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-31T00:51:26`
- Training end:
  `2026-03-31T00:52:04`
- Elapsed:
  `37.731s`
- Final active metrics:
  - `val_loss = 0.279235`
  - `val_reconstruction_extra_waveform_l1 = 0.009543`
  - `val_reconstruction_extra_stft_l1 = 0.020695`
  - `val_extra_local_waveform_l1 = 0.001299`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0203 / -0.0300 / -0.0105 / -0.0297 / +0.0217 dB`

### Fixed Checks relative `v226`

- `-0.0151 / -0.0092 / -0.0167 / -0.0061 / -0.0009 dB`

### Read

- Simply moving the local supervision target farther downstream,
  without opening that route's own writer,
  does not help.
- On the fixed proxy set,
  this was slightly negative almost everywhere and not worth continuing as-is.

## `v230 = v229 + branch_overlap_refine_present_head`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v230_v229_predudual_refinepresentopen_v1_ft1`
- Trainable:
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_refine_present_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `790022 / 8352912`,
  `9.4580%`
- Training start:
  `2026-03-31T00:54:36`
- Training end:
  `2026-03-31T00:55:17`
- Elapsed:
  `40.709s`
- Final active metrics:
  - `val_loss = 0.279177`
  - `val_reconstruction_extra_waveform_l1 = 0.009611`
  - `val_reconstruction_extra_stft_l1 = 0.020163`
  - `val_extra_local_waveform_l1 = 0.001261`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-1.1778 / -1.0109 / -0.4876 / -0.7678 / +1.1182 dB`

### Fixed Checks relative `v226`

- `-1.1727 / -0.9902 / -0.4938 / -0.7442 / +1.0956 dB`

### Fixed Checks relative `v229`

- `-1.1575 / -0.9810 / -0.4771 / -0.7381 / +1.0965 dB`

### Read

- This was not a no-op and not a mild exchange surface.
- Opening
  `branch_overlap_refine_present_head`
  on the later pre-dual writable route immediately spends large guardrail margin to buy blocker gain.
- So the issue is not merely that
  `v229`
  lacked route capacity.
  The first obvious capacity increase on this later route lands in a much steeper wrong tradeoff regime.

## Conclusion

- The tested pre-dual writable-path family is now bounded:
  `v229`
  shows that output-position-only retargeting is slightly negative,
  and
  `v230`
  shows that simply reopening
  `branch_overlap_refine_present_head`
  turns the route into a strong guardrail-for-local tradeoff.
- So the next continuation should not be another scalar sweep or another simple local unfreeze on this same route.
- If this direction continues,
  it should do so by exporting a cleaner intermediate writable output before the frozen cancel path,
  or by changing the local objective on a route that does not rely on the same
  `refine_present`
  writer.
