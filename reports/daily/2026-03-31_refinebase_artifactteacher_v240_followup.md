# 2026-03-31 artifact-first teacher-overlap repair on top of `v239`: `v240` follow-up

## Summary

- Goal:
  test whether the split-route
  `refine_base`
  family could repair the remaining
  `v239`
  artifact drag from the keep-side output
  without reopening the abstention failure and without giving back the whole blocker gain.
- Route:
  start from
  `v239`,
  keep the local writer unchanged
  (`local_prediction_source = estimated_waveform_refine_base`,
  `branch_overlap_refine_head` trainable),
  keep the broad keep-side reconstruction and absent repair unchanged,
  and add a focused
  `branch_protect_teacher_overlap`
  term on
  `estimated_waveform_post_pre_present_controller`
  with
  teacher
  `v157`
  over
  `target_clean_plus_music + target_hard_plus_music`
  and
  `target_full`.
- Smoke:
  `_smoke_v240_v239_refinebase_artifactteacher004_v1`
  passed and confirmed that the new teacher-overlap branch was real:
  `branch_protect_teacher val 20 / 67`,
  `val_branch_protect_teacher_overlap_l1 = 0.00045`.
- Full:
  `v240`
  was training-real,
  and this time the route crossed an important boundary:
  relative
  `v157`,
  all five fixed synthetic checks turned positive.
- Verdict:
  `v240`
  is the strongest point so far inside the split-route
  `refine_base`
  family.
  It is not yet an active-base promotion by itself,
  because near-real and listening checks are still missing.
  But it is now the first fixed-synthetic continuation candidate on this family that is clearly worth taking to the next validation stage.

## Code Change

- None.
  `v240`
  uses existing
  `branch_protect_teacher_overlap`
  plumbing,
  existing split-route local-writer plumbing,
  and an explicit
  `v157`
  teacher checkpoint.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v240 = v239 + artifact-first keep-side teacher-overlap 0.04`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v240_v239_refinebase_artifactteacher004_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T14:02:21`
- Training end:
  `2026-03-31T14:03:45`
- Elapsed:
  `84.090s`
- Final active metrics:
  - `val_loss = 0.299307`
  - `val_reconstruction_extra_waveform_l1 = 0.009597`
  - `val_reconstruction_extra_stft_l1 = 0.019942`
  - `val_extra_local_waveform_l1 = 0.001263`
  - `val_extra_local_sisdr_loss = 0.496970`
  - `val_absent_extra_interval_l1 = 0.000188`
  - `val_branch_protect_teacher_overlap_l1 = 0.000396`
  - `val_gate_absent_mean = 0.003081`
  - `val_gate_keep_mean = 0.126639`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.127280`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.005049`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+0.2263 / +0.1787 / +0.2455 / +0.0762 / +0.5359 dB`

### Fixed Checks relative `v224`

- `+0.2314 / +0.1801 / +0.2425 / +0.0840 / +0.5204 dB`

### Fixed Checks relative `v233`

- `+1.0232 / +0.1185 / +0.1345 / +0.5037 / -0.1421 dB`

### Fixed Checks relative `v239`

- `+0.8098 / +0.1236 / +0.1752 / +0.4121 / -0.1290 dB`

## Read

- This continuation is clearly not a no-op.
  The new teacher-overlap selector is active at meaningful scale,
  and the added metric stays nonzero through smoke and full.
- The direction is much stronger than the earlier
  `v239`
  abstention-only repair.
  Relative
  `v157`,
  all five fixed checks are now positive.
  That includes the two previously stubborn dimensions on this family:
  abstention
  `+0.2263 dB`
  and artifact
  `+0.0762 dB`.
- The artifact repair is sample-real.
  Relative
  `v239`,
  the worst remaining artifact regressions both turned back:
  `val_000343`
  improved
  `+2.0726 dB`,
  and
  `val_000105`
  improved
  `+0.2123 dB`.
- The price is local give-back relative
  `v239`,
  not global collapse.
  The blocker regressed
  `-0.1290 dB`
  relative
  `v239`,
  concentrated mainly in
  `val_000343`
  and
  `val_000383`.
  But because
  `v239`
  had built a very large blocker surplus over
  `v157`,
  the new point still stays strongly positive on the blocker relative to both
  `v157`
  and
  `v224`.
- This is therefore the first real fixed-synthetic crossing point on the family:
  not "repair one axis while still failing the base",
  but "repair enough of the bad surface that all five active fixed checks are positive at once".

## Conclusion

- `v240` becomes the new leading candidate inside the split-route
  `refine_base`
  local-only writer family.
- It is the first point on this family that is positive against
  `v157`
  on all five active fixed synthetic checks.
- Keep `v157` as the active automatic base for now.
  This result still needs near-real or listening validation before any promotion decision.
- Do not start by micro-sweeping the same
  `branch_protect_teacher_overlap_weight`.
  The next action should be candidate validation,
  not another scalar retune on the same synthetic surface.
