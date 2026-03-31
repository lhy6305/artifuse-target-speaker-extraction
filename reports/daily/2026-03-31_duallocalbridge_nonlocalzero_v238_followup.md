# 2026-03-31 dedicated dual-local bridge nonlocal-zero continuation on top of `v212`: `v238` follow-up

## Summary

- Goal:
  test whether the first dedicated dual-local bridge from
  `v237`
  was failing mainly because the new writer spilled correction outside blocker windows,
  and whether a simple complement-interval zero penalty on the bridge estimate could recover guardrail margin without giving back the blocker gain.
- Route:
  keep the same dedicated
  `branch_overlap_dual_local_bridge_head + branch_overlap_dual_local_bridge_controller_head`
  launch from
  `v237`,
  still supervise
  `estimated_waveform_post_dual_local_bridge`
  inside blocker windows with
  `extra_local_waveform_weight = 0.5`,
  and add
  `branch_overlap_dual_local_bridge_nonlocal_waveform_weight = 0.1`
  on the bridge estimate outside
  `local_proxy_intervals`.
- Implementation:
  add a complement-interval waveform loss for
  `branch_overlap_dual_local_bridge_estimate_waveform`,
  expose it in train and eval summaries,
  and launch from
  `v212`
  with the same dedicated bridge trainable set as
  `v237`.
- Smoke:
  `_smoke_v238_v212_duallocalbridge_nonlocalzero010_v1`
  passed.
- Full:
  `v238`
  was training-real,
  but the new nonlocal-zero term stayed effectively zero and fixed-proxy behavior was a practical tie to
  `v237`.
- Verdict:
  simple spill-control on the first dedicated dual-local bridge does not change the regime.
  This continuation can be closed as a practical-tie reject.

## Code Change

- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add
  `branch_overlap_dual_local_bridge_nonlocal_waveform_l1`
  and
  `branch_overlap_dual_local_bridge_nonlocal_waveform_weight`
  through complement intervals of
  `local_proxy_intervals`.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose the new loss weight and log the new metric in train and val summaries.
- Updated:
  `scripts/eval/eval_stft_mask_baseline.py`
  to carry the same bridge-estimate tensor into loss accounting.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v238 = v237 + branch_overlap_dual_local_bridge_nonlocal_waveform_weight 0.1`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v238_v212_duallocalbridge_nonlocalzero010_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v238_v212_duallocalbridge_nonlocalzero010_v1_ft1`
- Trainable:
  `branch_overlap_dual_local_bridge_head + branch_overlap_dual_local_bridge_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-03-31T13:05:23`
- Training end:
  `2026-03-31T13:06:08`
- Elapsed:
  `44.710s`
- Final active metrics:
  - `val_loss = 0.032108`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_extra_local_waveform_l1 = 0.001296`
  - `val_branch_overlap_dual_local_bridge_nonlocal_waveform_l1 = 8.06e-06`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.2527 / -0.1593 / -0.1516 / -0.1361 / +0.0718 dB`

### Fixed Checks relative `v212`

- `-0.2215 / -0.1438 / -0.1377 / -0.1313 / +0.0713 dB`

### Fixed Checks relative `v237`

- `+0.0057 / +0.0013 / +0.0016 / -0.0029 / -0.0010 dB`

## Read

- This continuation is not a crash and not a missing-plumbing case.
  The new nonlocal-zero metric is wired through train and val summaries,
  and the experiment trains normally.
- But the actual signal is tiny.
  The final
  `val_branch_overlap_dual_local_bridge_nonlocal_waveform_l1`
  is only
  `8.06e-06`,
  so the added term barely sees anything to penalize on the active validation slices.
- Fixed-proxy behavior confirms the same conclusion.
  Relative
  `v237`,
  all five fixed checks stay inside a practical-tie band.
- Relative
  `v212`
  and
  `v157`,
  the route still has the same qualitative shape as
  `v237`:
  all four non-blocker checks are clearly negative,
  while the blocker stays positive.
- So the simplest version of the nonlocal-spill hypothesis is not enough.
  A small complement-interval zero penalty on the first dedicated bridge does not rescue selectivity.

## Conclusion

- The first dedicated dual-local bridge family is now bounded through `v238`.
- Do not keep micro-sweeping the same bridge with simple nonlocal-zero penalties by default.
- If this direction continues,
  it should be through a more structural bridge application or a materially different objective,
  not another scalar spill-control retune on the same first-launch writer.
