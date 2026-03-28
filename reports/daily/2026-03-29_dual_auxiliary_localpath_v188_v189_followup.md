# 2026-03-29 dual auxiliary local path on `v157`: `v188 / v189` follow-up

## Summary

- Goal:
  test a truly disjoint trainable auxiliary path on top of the active base
  `v157`
  without writing directly into the main output route.
- I enabled coexistence between
  `branch_overlap_cancel`
  and
  `branch_overlap_dual_decoder`
  so the active
  `v157`
  route can host a dual auxiliary branch.
- `v188`
  was intended as a non-writing calibration run,
  but it exposed a semantic trap:
  `branch_overlap_dual_decoder_apply_mode = final_output`
  with
  `max_blend = 0`
  is not a no-write path.
  It falls back to
  `estimated_waveform_branch_base`
  and strongly regresses all fixed keep or abstention guardrails.
- `v189`
  corrected that semantics:
  `branch_overlap_dual_decoder_apply_mode = current_output`
  with
  `max_blend = 0`
  is a true no-write auxiliary path.
  Fixed synthetic evaluation is exact tie to
  `v157`
  on all five active checks.
- But
  `v189`
  also shows the current dual auxiliary objective is trivial on the local blocker:
  the selector is active
  (`train 33 / 233, val 7 / 67`),
  yet
  `overlap_dual_mix_consistency_l1`
  and
  `overlap_dual_residual_target_projection_ratio`
  stay exact
  `0.0`
  throughout training.
- New branch boundary:
  a truly disjoint non-writing auxiliary path now exists,
  but the current
  `overlap_dual_mix_consistency + residual_target_projection`
  objective pair collapses to the zero-residual trivial solution on this local-blocker task.

## Code Preparation

- `src/tse_prefix/models/stft_mask_baseline.py`
  no longer forbids
  `branch_overlap_cancel`
  and
  `branch_overlap_dual_decoder`
  from coexisting.
- `scripts/train/train_stft_mask_baseline.py`
  now tolerates optional unexpected init-checkpoint keys
  for optional branch modules during `strict=False` load.
- `py_compile`
  passed for both modified files.

## `v188 = v157 + dual auxiliary local path, final_output, max_blend 0`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v188_v157_dualaux_maxblend0_localdual_v1_ft1`
- Intent:
  use a dual auxiliary branch with zero blend
  as a non-writing local auxiliary path.
- Result:
  this semantics is not non-writing.

### Fixed Checks relative `v157`

- abstention `-3.2585 dB`
- same-gender keep `-2.4507 dB`
- hard-present keep `-2.0340 dB`
- artifact proxy `-1.8415 dB`
- local speech leak proxy `+0.7581 dB`

### Verdict

- `v188`
  is a semantic calibration reject.
- `final_output + max_blend 0`
  rewrites output toward branch base,
  so it cannot be used as a monitor-only auxiliary route.

## `v189 = v157 + dual auxiliary local path, current_output, max_blend 0`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v189_v157_dualaux_currentoutput_maxblend0_localdual_v1_ft1`
- Intent:
  correct
  `v188`
  by switching to a true no-write application semantics.
- Trainable modules:
  - `branch_overlap_dual_decoder_temporal_model`
  - `branch_overlap_dual_decoder_head`
- Selector coverage:
  `train 33 / 233, val 7 / 67`

### Training Evidence

- Final
  `overlap_dual_mix_consistency_l1 = 0.0`
- Final
  `overlap_dual_residual_target_projection_ratio = 0.0`
- Interpretation:
  the current dual auxiliary objective pair is satisfied by the zero-residual solution,
  so the auxiliary branch becomes a trivial no-op on this task.

### Fixed Checks relative `v157`

- abstention `0.0 dB`
- same-gender keep `0.0 dB`
- hard-present keep `0.0 dB`
- artifact proxy `0.0 dB`
- local speech leak proxy `0.0 dB`

### Verdict

- `v189`
  is the first clean proof that a truly disjoint non-writing auxiliary path can be attached to
  `v157`
  without disturbing any fixed synthetic behavior.
- But it is only a structural evidence point,
  not a useful continuation,
  because the present dual objective is trivial.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  only as mechanism-positive evidence.
- Mark
  `v188`
  as:
  semantic calibration reject for
  `dual final_output + max_blend 0`.
- Mark
  `v189`
  as:
  true no-write auxiliary-path evidence point,
  but trivial-objective no-op.
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - `dual final_output + max_blend 0`
    as a supposed non-writing auxiliary path
  - `overlap_dual_mix_consistency + overlap_dual_residual_target_projection`
    as the local objective pair for a no-write auxiliary branch on this blocker
- If this branch continues,
  the next auxiliary objective must be non-trivial at zero residual,
  for example a target or teacher that cannot be minimized by predicting no interference at all.
