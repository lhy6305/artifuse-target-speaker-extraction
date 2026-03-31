# 2026-04-01 additive artifact-local keep-side teacher continuation on top of `v240`: `v250` invalid scratch and `v251` follow-up

## Summary

- Goal:
  test whether the split-route
  `refine_base`
  mixed candidate
  `v240`
  could repair the newly isolated target-conditioned artifact slice
  by keeping the existing plus-music artifact teacher branch alive
  and adding a second additive
  artifact-local
  teacher-overlap branch built from
  `hard_present_artifact_local_proxy_v1`.
- Route:
  start from
  `v240`,
  keep the split-route local writer,
  the abstention repair,
  the plus-music artifact teacher repair,
  and the full
  `overlap_dual`
  local bundle unchanged,
  then add
  `branch_protect_teacher_extra`
  on the explicit
  `hard_present_artifact_local_proxy_v1`
  ids list with
  `branch_protect_teacher_overlap_extra_weight = 0.02`.
- Invalid scratch:
  the first launch
  `v250`
  accidentally omitted
  `--model-branch-overlap-dual-decoder-max-blend 0.0`,
  so it silently reopened the dual writer path with parser default
  `branch_overlap_dual_decoder_max_blend = 1.0`.
  That run is invalid scratch and should not be read scientifically.
- Valid follow-up:
  `v251`
  restored the correct
  `branch_overlap_dual_decoder_max_blend = 0.0`
  continuation semantics.
  The additive artifact-local branch is training-real,
  but selector coverage inside the active bundle is tiny:
  only
  `train 3 / 233`
  and
  `val 3 / 67`.
- Verdict:
  `v251`
  is a coverage-limited mixed continuation.
  Relative
  `v240`,
  it improves the four non-blocker fixed checks
  but weakens the active local blocker.
  Relative
  `v240`,
  the broad speech probe is slightly negative,
  while the focused guodegang transient probe is slightly positive.
  This is not a promotion and not a clean artifact repair.
  Do not continue the same tiny additive artifact-local teacher axis by weight retune
  unless coverage is fixed first.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v250` invalid scratch

- Intended route:
  `v240 + additive artifact-local keep-side teacher overlap 0.02`
- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v250_v240_refinebase_artifactlocalteacherextra002_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v250_v240_artifactlocalteacherextra002_v1_ft1`
- Invalid reason:
  the command omitted
  `--model-branch-overlap-dual-decoder-max-blend 0.0`.
  The run therefore used parser default
  `branch_overlap_dual_decoder_max_blend = 1.0`
  instead of preserving the
  `v240`
  no-write dual route.
- Read:
  treat
  `v250`
  only as a command-drift audit.
  Do not use its outputs as scientific evidence for or against the artifact-local teacher idea.

## `v251 = v240 + additive artifact-local keep-side teacher overlap 0.02`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v251_v240_artifactlocalteacherextra002_fixdualblend0_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v251_v240_artifactlocalteacherextra002_fixdualblend0_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T23:59:44`
- Training end:
  `2026-04-01T00:00:41`
- Elapsed:
  `57.306s`
- Best val loss:
  `0.057739`
- Final active metrics:
  - `val_branch_protect_teacher_overlap_l1 = 0.000190`
  - `val_branch_protect_teacher_overlap_extra_l1 = 0.000048`
  - `val_extra_local_waveform_l1 = 0.001465`
  - `val_overlap_dual_residual_waveform_l1 = 0.052711`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.017196`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001411`
- Selector activity:
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`
  - branch protect teacher extra `train 3 / 233, val 3 / 67`
- Bundle-overlap audit:
  the full
  `hard_present_artifact_local_proxy_v1`
  ids list contains many more rows,
  but only
  `train_001193_hard_present_artifact_local_v1`,
  `train_001316_hard_present_artifact_local_v1`,
  `train_001831_hard_present_artifact_local_v1`,
  `val_000343_hard_present_artifact_local_v1`,
  `val_000416_hard_present_artifact_local_v1`,
  and
  `val_000495_hard_present_artifact_local_v1`
  are present inside the current active bundle.

### Fixed Checks relative `v240`

- `+0.3541 / +0.0732 / +0.0105 / +0.1249 / -0.3873 dB`

### Fixed Checks relative `v157`

- `+0.5804 / +0.2518 / +0.2559 / +0.2011 / +0.1486 dB`

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v251_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v251_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0239`
- `improved_count = 3`
- `regressed_count = 5`
- `near_tie_count = 16`

### Probe By Anchor

- `near_real_0003`:
  `-0.0751 dB`
- `near_real_0004`:
  `-0.0461 dB`
- `near_real_0006`:
  `+0.0863 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.0606 dB`
- `guodegang_raw`:
  `+0.0863 dB`

### Probe By Speech Clip

- `friend_absent_820s`:
  `-0.1389 dB`
- `friend_anchor_215s`:
  `-0.0020 dB`
- `friend_anchor_45s`:
  `-0.0409 dB`
- `guodegang_absent_480s`:
  `+0.0087 dB`
- `guodegang_anchor_120s`:
  `+0.1639 dB`

## Guodegang Transient Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v251_on_near_real_guodegang_transient_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v251_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = +0.0863`
- `improved_count = 3`
- `regressed_count = 0`
- `near_tie_count = 3`

### Probe By Clip

- `guodegang_absent_480s`:
  `+0.0087 dB`
- `guodegang_anchor_120s`:
  `+0.1639 dB`

## Read

- `v251`
  is a valid continuation.
  The extra artifact-local teacher branch is not a fake no-op:
  smoke and full both keep
  `branch_protect_teacher_overlap_extra_l1`
  nonzero,
  and the corrected dual path preserves
  `branch_overlap_dual_decoder_max_blend = 0.0`.
- Relative
  `v240`,
  the surface is mixed in a very specific way.
  The four non-blocker fixed checks all improve,
  but the active local blocker gives back
  `-0.3873 dB`.
  So this continuation behaves like a keep-heavy repair with blocker cost,
  not like a selective artifact repair.
- The real-side probes show the same split.
  The broader speech probe is slightly negative overall,
  driven mainly by
  `friend_raw`
  and especially
  `friend_absent_820s`.
  But the focused guodegang transient slice is modestly positive,
  driven almost entirely by
  `guodegang_anchor_120s`.
- The most important limit is coverage.
  The additive extra branch only touches
  `3 / 233`
  training rows and
  `3 / 67`
  validation rows inside the current active bundle.
  So this experiment maps the direction of the artifact-local teacher idea,
  but it does not fully test its ceiling.

## Conclusion

- `v250`
  is invalid scratch because a preserved
  `v240`
  continuation accidentally reopened
  `branch_overlap_dual_decoder_max_blend`.
- `v251`
  is a coverage-limited mixed continuation on top of
  `v240`,
  not a promotion and not a clean artifact repair.
- Keep
  `v157`
  as the active automatic base.
- Keep
  `v240`
  as the leading mixed near-real candidate on the split-route
  `refine_base`
  family.
- Do not continue the same additive artifact-local teacher axis by weight micro-sweeps or tiny selector edits on the current bundle.
  If this idea continues,
  fix bundle coverage first so the extra artifact-local branch is not capped at
  `3 / 233`
  training hits.
