# 2026-03-30 dual residual-correction coupling on `v190`: `v206 / v207 / v208` follow-up

## Summary

- Goal:
  test a new coupling family that reads the proven no-write
  `v190`
  dual auxiliary evidence,
  but writes back through a new direct residual-correction head on the current output residual,
  rather than through:
  - the old apply-controller head
  - the pre-present controller
  - direct gate rewrite
  - the monitor path
  - the existing overlap-cancel estimate path
- Code change:
  added
  `branch_overlap_dual_residual_correction_head`
  plus
  `branch_overlap_dual_residual_correction_controller_head`
  so the dual branch can predict a bounded complex correction on
  `mix - current_output`
  and apply it through its own scalar controller.
- This family is training-real:
  the overlap-dual selector stayed active
  (`train 33 / 233, val 7 / 67`)
  and the new correction metric stayed nonzero in all runs
  (`val_overlap_dual_residual_correction_waveform_l1 ~= 0.00491`).
- But the family still lands in a clear local-versus-guardrail tradeoff.
  Small blend is safe practical near-no-op.
  Higher blend and joint dual-path widening both increase the local blocker in the correct direction,
  but they spend guardrail margin to do it.
- Verdict:
  the dual residual-correction family is now bounded through
  `v208`.
  It is a real new coupling path,
  but the currently tested axes
  (head-only small blend,
  higher blend,
  joint dual-path widening)
  do not open a selective regime.
  The next continuation should add a disjoint keep-preserve path,
  not keep scaling this same local-only route.

## Code Change

- `src/tse_prefix/models/stft_mask_baseline.py`
  now supports:
  - `enable_branch_overlap_dual_residual_correction_head`
  - `branch_overlap_dual_residual_correction_max_delta`
  - `branch_overlap_dual_residual_correction_max_blend`
  - output
    `branch_overlap_dual_residual_correction_controller`
  - output
    `branch_overlap_dual_residual_correction_estimate_waveform`
- `src/tse_prefix/pipeline/baseline_train.py`
  now supports:
  - `overlap_dual_residual_correction_prediction`
  - `overlap_dual_residual_correction_waveform_weight`
  - metric
    `overlap_dual_residual_correction_waveform_l1`
- `scripts/train/train_stft_mask_baseline.py`
  now supports:
  - `--model-enable-branch-overlap-dual-residual-correction-head`
  - `--model-branch-overlap-dual-residual-correction-max-delta`
  - `--model-branch-overlap-dual-residual-correction-max-blend`
  - `--loss-overlap-dual-residual-correction-waveform-weight`
  - `gate_supervision_source = overlap_dual_residual_correction_controller`
- `scripts/eval/eval_stft_mask_baseline.py`
  now resolves the same controller and correction waveform for evaluation-side metrics.
- `py_compile`
  passed after the code change.

## `v206 = v190 + dual residual-correction head-only, blend 0.02`

- Smoke:
  `_smoke_v206_v190_dualresidualcorrection_v1`
  validated the new route before the full run.
  The selector was active
  (`train 13 / 80, val 7 / 67`)
  and
  `val_overlap_dual_residual_correction_waveform_l1 = 0.004910`.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v206_v190_dualresidualcorrection_blend002_v1_ft1`
- Trainable:
  `branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`395011 / 8221327`,
  `4.8047%`)
- Training start:
  `2026-03-30T20:29:19`
- Training end:
  `2026-03-30T20:29:44`
- Elapsed:
  `24.119s`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.015926`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.004909`
  - `val_overlap_dual_controller_distill_l1 = 0.281731`
  - `val_gate_keep_mean = 0.353855`

### Fixed Checks relative `v157`

- abstention `-0.0165 dB`
- same-gender keep `-0.0079 dB`
- hard-present keep `-0.0082 dB`
- artifact proxy `-0.0045 dB`
- local speech leak proxy `+0.0088 dB`

### Verdict

- Safe practical near-no-op.
- This is the first dual auxiliary family in the repo that is both:
  - training-real
  - slightly positive on the active local blocker
- But the absolute movement is still too small to matter.

## `v207 = v206 family, blend 0.08`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v207_v206_dualresidualcorrection_blend008_v1_ft1`
- Trainable:
  still
  `branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`4.8047%`)
- Training start:
  `2026-03-30T20:31:58`
- Training end:
  `2026-03-30T20:32:21`
- Elapsed:
  `23.052s`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.015926`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.004906`
  - `val_overlap_dual_controller_distill_l1 = 0.281731`
  - `val_gate_keep_mean = 0.353855`

### Fixed Checks relative `v157`

- abstention `-0.0792 dB`
- same-gender keep `-0.0385 dB`
- hard-present keep `-0.0393 dB`
- artifact proxy `-0.0235 dB`
- local speech leak proxy `+0.0420 dB`

### Fixed Checks relative `v206`

- abstention `-0.0627 dB`
- same-gender keep `-0.0306 dB`
- hard-present keep `-0.0311 dB`
- artifact proxy `-0.0190 dB`
- local speech leak proxy `+0.0332 dB`

### Verdict

- Higher blend amplifies a real direction,
  but that direction is a straightforward local-versus-guardrail tradeoff.
- This is no longer near-no-op,
  but it is not selective enough for promotion.

## `v208 = v207 family + joint dual-path widening`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v208_v207_dualresidualcorrection_jointdualpath_v1_ft1`
- Trainable:
  `branch_overlap_dual_decoder_temporal_model + branch_overlap_dual_decoder_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`2630661 / 8221327`,
  `31.9980%`)
- Training start:
  `2026-03-30T20:33:53`
- Training end:
  `2026-03-30T20:34:29`
- Elapsed:
  `36.611s`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.016118`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.004902`
  - `val_overlap_dual_controller_distill_l1 = 0.255086`
  - `val_gate_keep_mean = 0.321264`

### Fixed Checks relative `v157`

- abstention `-0.0977 dB`
- same-gender keep `-0.0623 dB`
- hard-present keep `-0.0522 dB`
- artifact proxy `-0.0452 dB`
- local speech leak proxy `+0.0863 dB`

### Fixed Checks relative `v207`

- abstention `-0.0185 dB`
- same-gender keep `-0.0238 dB`
- hard-present keep `-0.0129 dB`
- artifact proxy `-0.0217 dB`
- local speech leak proxy `+0.0443 dB`

### Verdict

- Joint widening does not recover selectivity.
- It simply moves farther along the same tradeoff surface:
  more blocker gain,
  more guardrail loss.

## Conclusion

- The new dual residual-correction family is now bounded in three ways:
  - head-only small blend:
    safe near-no-op with slight local improvement
  - head-only higher blend:
    clearer local gain,
    but clear guardrail erosion
  - joint dual-path widening:
    even more local gain,
    but further guardrail erosion
- This is scientifically useful:
  unlike the older dual teacher,
  monitor,
  gate-rewrite,
  and cancel-estimate families,
  this route does create a monotonic blocker-positive signal.
- But it still buys that blocker gain by spending the same shared output budget.
- The next continuation should therefore stop scaling this family by itself.
  If this branch continues,
  add a disjoint keep-preserve supervision path outside the blocker windows,
  or another keep-specific route that does not share the same final correction path.
