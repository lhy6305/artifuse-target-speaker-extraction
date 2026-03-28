# 2026-03-29 dual auxiliary residual-waveform objective on `v157`: `v190` follow-up

## Summary

- Goal:
  replace the trivial no-write dual objective from
  `v189`
  with a non-trivial explicit interference-residual target
  while keeping the auxiliary branch fully non-writing.
- I added
  `overlap_dual_residual_waveform_weight`
  so the dual residual branch can match
  `mixture - target`
  inside overlap intervals.
- `v190 = v157 + no-write dual auxiliary residual-waveform objective`
  is the first clean proof that a truly disjoint non-writing local auxiliary path can also be training-real.
- The path stays fully isolated at inference:
  relative to
  `v157`,
  all five active fixed synthetic checks are exact
  `0.0 dB`.
- But training is now clearly non-trivial:
  `overlap_dual` selector coverage is
  `train 33 / 233, val 7 / 67`,
  and final
  `val_overlap_dual_residual_waveform_l1 = 0.015926`.
- New branch boundary:
  a usable non-trivial no-write auxiliary local path now exists,
  but it is only an evidence point until a separate output-coupling mechanism is added.

## Code Change

- `src/tse_prefix/pipeline/baseline_train.py`
  now supports
  `overlap_dual_residual_waveform_weight`,
  an interval waveform L1 loss that matches
  `branch_overlap_dual_residual_prediction`
  against
  `mixture - target`
  on overlap intervals.
- `scripts/train/train_stft_mask_baseline.py`
  now exposes and records
  `overlap_dual_residual_waveform_l1`.
- `py_compile`
  passed for:
  - `scripts/train/train_stft_mask_baseline.py`
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `src/tse_prefix/models/stft_mask_baseline.py`

## `v190 = v157 + no-write dual auxiliary residual-waveform objective`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v190_v157_dualaux_currentoutput_maxblend0_residualwave002_v1_ft1`
- Parent:
  `v157`
- Non-writing auxiliary semantics:
  - `branch_overlap_dual_decoder_apply_mode = current_output`
  - `branch_overlap_dual_decoder_max_blend = 0.0`
- Trainable modules:
  - `branch_overlap_dual_decoder_temporal_model`
  - `branch_overlap_dual_decoder_head`
- New active loss:
  `overlap_dual_residual_waveform_weight = 0.02`
- Disabled old trivial pair:
  - `overlap_dual_mix_consistency_weight = 0.0`
  - `overlap_dual_residual_target_projection_weight = 0.0`

## Training Evidence

- `overlap_dual` selector coverage:
  `train 33 / 233, val 7 / 67`
- Final active metric:
  `val_overlap_dual_residual_waveform_l1 = 0.015926`
- Diagnostic metric:
  `val_overlap_dual_residual_target_projection_ratio = 0.004308`
- Interpretation:
  unlike
  `v189`,
  this auxiliary branch no longer collapses to a trivial zero-residual objective.

## Fixed Checks relative `v157`

- abstention `0.0 dB`
- same-gender keep `0.0 dB`
- hard-present keep `0.0 dB`
- artifact proxy `0.0 dB`
- local speech leak proxy `0.0 dB`

## Verdict

- `v190`
  is not a candidate continuation for listening or near-real evaluation.
- It is a structural evidence point:
  the repository now has a genuinely trainable,
  truly disjoint,
  fully non-writing auxiliary local path.
- The missing piece is no longer the local target itself.
  The missing piece is a safe coupling mechanism from this auxiliary path back to output behavior.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  only as mechanism-positive evidence.
- Keep
  `v189`
  as the first clean true no-write auxiliary-path proof.
- Mark
  `v190`
  as:
  non-trivial no-write auxiliary local-path evidence point.
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - direct output-free dual auxiliary training alone
    if the goal is immediate checkpoint promotion
- If this branch continues,
  the next step should be a separate coupling mechanism that reads the auxiliary branch
  without collapsing back into the shared main-output route.
- The most reasonable next options are:
  - a monitor-only controller that consumes auxiliary residual activity
  - a gated coupling path whose parameters are disjoint from the auxiliary residual predictor
  - a teacher-style supervision bridge from the auxiliary residual branch into a separate apply decision path
