# 2026-03-31 dedicated dual-local writer bridge on top of `v212`: `v237` follow-up

## Summary

- Goal:
  test whether the next useful step after
  `v236`
  was not another loss tweak on an already-closed writer,
  but a new dedicated local-only writer that reads the proven no-write dual auxiliary evidence without reusing the old writable residual-correction,
  pre-present,
  `refine_base`,
  or
  `refine_present`
  paths.
- Route:
  start from
  `v212`,
  keep the keep-side route on
  `estimated_waveform_post_pre_present_controller`,
  add a new
  `branch_overlap_dual_local_bridge_head + branch_overlap_dual_local_bridge_controller_head`,
  write a bounded correction onto the current output residual,
  and supervise only
  `estimated_waveform_post_dual_local_bridge`
  inside blocker windows through the existing
  `extra_local_waveform`
  term.
- Implementation:
  add the new dual-local bridge heads and outputs in the model,
  allow
  `estimated_waveform_post_dual_local_bridge`
  as a valid prediction source,
  and allow the new bridge heads as optional init-checkpoint mismatches.
- Smoke:
  `_smoke_v237_v212_duallocalbridge_localwave05_v1`
  passed.
  A direct forward check confirmed that
  `estimated_waveform_post_dual_local_bridge`
  is materialized under the new config.
- Full:
  `v237`
  was training-real,
  but fixed-proxy behavior became a clear guardrail-for-local tradeoff relative to both
  `v157`
  and
  `v212`.
- Verdict:
  the first dedicated dual-local writer bridge is not a new selective regime.
  It buys blocker gain by spending guardrail margin,
  so this exact first-launch point is bounded.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add:
  - `branch_overlap_dual_local_bridge_head`
  - `branch_overlap_dual_local_bridge_controller_head`
  - `branch_overlap_dual_local_bridge_controller`
  - `branch_overlap_dual_local_bridge_estimate_waveform`
  - `estimated_waveform_post_dual_local_bridge`
- Updated:
  `src/tse_prefix/pipeline/runtime_helpers.py`
  so
  `estimated_waveform_post_dual_local_bridge`
  can be selected as a prediction source.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to:
  - expose the new model flags
  - allow the new local prediction source
  - treat the new bridge heads as optional when loading from an older init checkpoint
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v237 = v212 + dedicated dual-local bridge + local waveform 0.5`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v237_v212_duallocalbridge_localwave05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v237_v212_duallocalbridge_localwave05_v1_ft1`
- Trainable:
  `branch_overlap_dual_local_bridge_head + branch_overlap_dual_local_bridge_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-03-31T12:44:31`
- Training end:
  `2026-03-31T12:45:15`
- Elapsed:
  `44.721s`
- Final active metrics:
  - `val_loss = 0.032107`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_extra_local_waveform_l1 = 0.001296`
  - `val_extra_local_sisdr_loss = 0.596853`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.2584 / -0.1607 / -0.1532 / -0.1332 / +0.0728 dB`

### Fixed Checks relative `v212`

- `-0.2272 / -0.1451 / -0.1393 / -0.1284 / +0.0722 dB`

## Read

- This route is clearly not a no-op.
  The new bridge heads train,
  the dedicated post-bridge waveform is materialized,
  and the blocker proxy moves the right way.
- But the shape is not selective.
  Relative
  `v212`,
  every fixed non-blocker check regresses materially,
  while the blocker improves only
  `+0.0722 dB`.
- Relative
  `v157`,
  the same shape remains:
  all four non-blocker checks are clearly negative,
  while the blocker is positive.
- So the first dedicated dual-local writer bridge behaves like another direct guardrail-for-local exchange surface.
  It is structurally new,
  but it does not solve the underlying selectivity problem.

## Conclusion

- The first dedicated dual-local writer bridge launch is now bounded.
- Do not keep micro-sweeping the same
  `branch_overlap_dual_local_bridge`
  writer with the same local waveform objective by default.
- If this direction continues,
  it should not be via simple scalar retune on the same first-launch point.
  The next continuation would need a materially different bridge application or a materially different objective,
  not just another small weight or blend adjustment.
