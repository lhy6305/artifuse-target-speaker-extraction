# 2026-03-30 local-window residual-correction objective on the `v212` disjoint route: `v222 / v223 / v224` follow-up

## Summary

- Goal:
  test a more structurally aligned local objective after the failed
  `v220 / v221`
  target-projection scalar retune.
  The key change was to supervise the writable
  `branch_overlap_dual_residual_correction_estimate_waveform`
  branch directly inside the blocker-local windows,
  instead of supervising the frozen dual residual prediction.
- Before launching the new family,
  two quick audits bounded dead options:
  - `_smoke_v222_v212_dualresidual_absentmix002_v1`:
    semantically dead on the active blocker selector because the selected
    `local_speech_leak_proxy_v1`
    samples do not expose usable `target_absent_intervals`;
    `val_overlap_dual_absent_mix_l1 = 0.0`
  - `_smoke_v222_v212_dualrescorr_localproj002_v1`:
    numerically dead on the writable residual-correction branch;
    the local target-projection term stayed effectively zero
    (`~1e-7`)
- Code was added to expose
  `local_proxy_intervals`
  from dataset metadata and to support two local-window losses on the writable residual-correction branch:
  - `overlap_dual_residual_correction_local_waveform_weight`
  - `overlap_dual_residual_correction_local_target_projection_weight`
- `v222`
  with local-window waveform weight
  `0.5`
  was the first non-trivial continuation on this new branch.
  Relative
  `v212`,
  all five fixed checks moved in the correct direction,
  but only slightly.
- `v223`
  raised the same weight to
  `2.0`.
  Relative
  `v222`,
  the local blocker improved again,
  but the four guardrails dipped slightly.
- `v224`
  raised the same weight to
  `8.0`.
  Relative
  `v212`,
  it became mildly positive on four of five fixed checks
  (`artifact` stayed a tiny negative),
  and the local blocker reached the largest gain of the family:
  `+0.0149 dB`.
- Verdict:
  this family is not a dead no-op,
  but the simple weight sweep
  `0.5 -> 2.0 -> 8.0`
  still does not open a meaningful new regime.
  Treat it as weak positive evidence that writable-branch local-window supervision is better aligned than the earlier target-projection scalar,
  not as a promotion candidate.

## Code Change

- Updated:
  `src/tse_prefix/data/synthetic_dataset.py`
  to derive
  `local_proxy_intervals`
  from `metadata["local_proxy"]`
- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to accept
  `local_proxy_intervals`
  in `compute_losses()`
  and to expose
  `overlap_dual_residual_correction_local_waveform_l1`
  plus
  `overlap_dual_residual_correction_local_target_projection_ratio`
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to wire the new batch field, CLI flags, and metrics into train and val summaries
- Validation:
  `py_compile`
  passed on all three changed files before launching the official family

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v222 = v212 + residual-correction local-window waveform loss 0.5`

- Smoke:
  `_smoke_v222_v212_dualrescorr_localwave05_v1`
  passed.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v222_v212_dualrescorr_localwave05_v1_ft1`
- Trainable:
  unchanged from
  `v212`
  (`branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`,
  `526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-30T23:22:49`
- Training end:
  `2026-03-30T23:23:45`
- Elapsed:
  `56.745s`
- Final active metrics:
  - `val_loss = 0.269915`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_overlap_dual_residual_correction_local_target_projection_ratio = 6.91e-08`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0242 / -0.0102 / -0.0101 / -0.0016 / +0.0017 dB`

### Fixed Checks relative `v212`

- `+0.0069 / +0.0054 / +0.0038 / +0.0032 / +0.0011 dB`

### Verdict

- This was the first local-objective continuation after
  `v220 / v221`
  that was clearly not a pure scalar tie to
  `v212`.
- But the magnitude stayed tiny.
  So this was only enough to justify one larger follow-up weight jump,
  not a promotion discussion.

## `v223 = v222 + residual-correction local-window waveform loss 2.0`

- Smoke:
  `_smoke_v223_v222_dualrescorr_localwave20_v1`
  passed.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v223_v222_dualrescorr_localwave20_v1_ft1`
- Trainable:
  unchanged from
  `v222`
  (`6.3043%`)
- Training start:
  `2026-03-30T23:26:19`
- Training end:
  `2026-03-30T23:27:17`
- Elapsed:
  `57.098s`
- Final active metrics:
  - `val_loss = 0.271654`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020714`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_overlap_dual_residual_correction_local_target_projection_ratio = 7.05e-08`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  unchanged from
  `v222`

### Fixed Checks relative `v157`

- `-0.0325 / -0.0147 / -0.0119 / -0.0049 / +0.0095 dB`

### Fixed Checks relative `v222`

- `-0.0083 / -0.0045 / -0.0018 / -0.0033 / +0.0078 dB`

### Fixed Checks relative `v212`

- `-0.0014 / +0.0009 / +0.0020 / -0.0001 / +0.0090 dB`

### Verdict

- Raising the local-window waveform weight from
  `0.5`
  to
  `2.0`
  still did not produce a meaningful regime change.
- The local blocker improved,
  but the four guardrails no longer moved together with it.
  This looked like a very mild exchange surface,
  not a breakthrough.

## `v224 = v223 + residual-correction local-window waveform loss 8.0`

- Smoke:
  `_smoke_v224_v223_dualrescorr_localwave80_v1`
  also passed.
  Training-side metrics already looked almost identical to
  `v223`,
  which made this a closure run rather than an exploratory branch.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v224_v223_dualrescorr_localwave80_v1_ft1`
- Trainable:
  unchanged from
  `v223`
  (`6.3043%`)
- Training start:
  `2026-03-30T23:39:04`
- Training end:
  `2026-03-30T23:40:07`
- Elapsed:
  `62.456s`
- Final active metrics:
  - `val_loss = 0.278611`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020715`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_target_projection_ratio = 7.20e-08`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  still unchanged from
  `v222 / v223`

### Fixed Checks relative `v157`

- `-0.0051 / -0.0015 / +0.0030 / -0.0079 / +0.0155 dB`

### Fixed Checks relative `v223`

- `+0.0274 / +0.0132 / +0.0149 / -0.0030 / +0.0060 dB`

### Fixed Checks relative `v212`

- `+0.0260 / +0.0141 / +0.0169 / -0.0031 / +0.0149 dB`

### Verdict

- This is the best point in the family so far,
  but still far below any meaningful threshold.
- Relative
  `v212`,
  four checks are small positive and
  `artifact`
  is a tiny negative.
  Relative
  `v157`,
  the run is still near tie overall.
- So the simple weight sweep on this objective is now bounded:
  larger weight does not collapse the family,
  but it still does not move enough to matter.

## Conclusion

- The key positive result here is structural, not absolute:
  supervising the writable residual-correction branch inside the blocker-local windows is better aligned than the earlier
  `overlap_dual_residual_target_projection_weight`
  scalar retune.
- The key negative result is also clear:
  a plain scalar sweep of
  `overlap_dual_residual_correction_local_waveform_weight`
  from
  `0.5`
  to
  `8.0`
  still does not unlock a meaningful regime.
- So this family should now be interpreted as:
  - weak mechanism-positive evidence
  - below promotion
  - not worth continued micro-sweeping by default
- If this branch continues,
  the next step should change the local objective more structurally on the same writable branch,
  or change the writable path itself.
  Do not keep nudging the same scalar weight in small steps.
