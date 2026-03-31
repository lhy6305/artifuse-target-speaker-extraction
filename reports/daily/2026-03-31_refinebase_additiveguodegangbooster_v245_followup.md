# 2026-03-31 additive guodegang-anchor local booster on top of `v240`: `v245` follow-up

## Summary

- Goal:
  test whether the mixed near-real
  `v240`
  candidate was missing a small local-only booster,
  rather than a full selector replacement,
  by keeping the original
  `overlap_dual`
  local bundle alive and adding a second guodegang-anchor-like booster bucket on top.
- Route:
  start from
  `v240`,
  keep the split-route
  `refine_base`
  local writer,
  the abstention repair,
  the artifact teacher repair,
  and the full
  `overlap_dual`
  selector unchanged,
  then add an
  `overlap_dual_extra`
  booster branch with a new
  `overlap_dual_residual_correction_local_waveform_extra`
  term.
- Booster asset:
  use a small explicit ids bucket that stays close to the
  `near_real_0006 / guodegang_anchor_120s`
  synthetic neighborhood:
  bounded-peak local windows,
  speech-plus-music overlap,
  moderate or high target-interference similarity,
  and low target share.
- Smoke:
  `_smoke_v245_v240_refinebase_localbooster_guodeganganchor_v1`
  passed.
  The base selector stayed alive
  (`overlap_dual train 4 / 20, val 7 / 67`)
  and the booster selector was also real
  (`overlap_dual_extra train 1 / 20, val 3 / 67`,
  `val_overlap_dual_residual_correction_local_waveform_extra_l1 = 0.000681`).
- Full:
  `v245`
  was training-real.
  Relative
  `v157`,
  all five fixed synthetic checks stayed positive.
  Relative
  `v240`,
  the four non-blocker checks improved again,
  but the active local blocker moved backward.
- Verdict:
  this is not a promotion and not a near-real repair.
  It is a bounded additive-booster continuation:
  synthetic-safe relative
  `v157`,
  but slightly wrong-way relative
  `v240`
  on both the active blocker and the targeted near-real probes.
  Do not continue this family by weight micro-sweeps or by swapping in another extra bucket on the same objective.

## Code Change

- Added additive
  `overlap_dual_extra`
  selector support for the local-window residual-correction waveform loss.
- Files:
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
- New selector asset:
  `data/manifests/selectors/overlap_dual_extra_local_speech_leak_proxy_v1_guodeganganchor_v1_ids.txt`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v245 = v240 + additive guodegang-anchor local booster`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v245_v240_refinebase_localbooster_guodeganganchor_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v245_v240_additiveguodegangbooster_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T20:20:09`
- Training end:
  `2026-03-31T20:21:34`
- Elapsed:
  `84.931s`
- Final active metrics:
  - `val_loss = 0.300262`
  - `val_reconstruction_extra_waveform_l1 = 0.009595`
  - `val_reconstruction_extra_stft_l1 = 0.019943`
  - `val_extra_local_waveform_l1 = 0.001262`
  - `val_absent_extra_interval_l1 = 0.000185`
  - `val_branch_protect_teacher_overlap_l1 = 0.000390`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_waveform_extra_l1 = 0.000681`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.125546`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.007859`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - overlap dual extra `train 7 / 233, val 3 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+1.0704 / +0.4994 / +0.7340 / +0.5112 / +0.2766 dB`

### Fixed Checks relative `v240`

- `+0.8442 / +0.3207 / +0.4886 / +0.4350 / -0.2593 dB`

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_additiveguodegangbooster_v245_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_additiveguodegangbooster_v245_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0185`
- `improved_count = 0`
- `regressed_count = 0`
- `near_tie_count = 24`

### Probe By Anchor

- `near_real_0003`:
  `-0.0189 dB`
- `near_real_0004`:
  `-0.0218 dB`
- `near_real_0006`:
  `-0.0130 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.0203 dB`
- `guodegang_raw`:
  `-0.0130 dB`

## Guodegang Transient Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_additiveguodegangbooster_v245_on_near_real_guodegang_transient_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_additiveguodegangbooster_v245_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0130`
- `improved_count = 0`
- `regressed_count = 0`
- `near_tie_count = 6`

### Probe By Clip

- `guodegang_absent_480s`:
  `-0.0005 dB`
- `guodegang_anchor_120s`:
  `-0.0256 dB`

## Read

- The additive booster is real.
  This is not another selector-replacement mistake:
  the original
  `overlap_dual`
  bundle stays active at
  `33 / 233, 7 / 67`,
  while the extra booster adds a second active branch at
  `7 / 233, 3 / 67`.
- Relative
  `v157`,
  the result still looks strong:
  all five fixed checks stay positive,
  and the blocker remains
  `+0.2766 dB`.
- Relative
  `v240`,
  the shape is not the one we wanted.
  The booster improves the four non-blocker axes,
  but it gives back
  `-0.2593 dB`
  on the active blocker.
  So the additive bucket behaves like a keep-heavy regularizer,
  not like a targeted guodegang repair.
- The targeted near-real probes agree with that read.
  They do not collapse,
  but both stay slightly negative relative
  `v240`,
  and the actual anchor slice
  `guodegang_anchor_120s`
  is also slightly negative.
  So this is not a repair candidate for the
  `near_real_0006`
  failure.

## Conclusion

- `v245`
  is a bounded additive-booster continuation on top of
  `v240`,
  not a promotion and not a meaningful near-real repair.
- Keep
  `v240`
  as the leading mixed near-real candidate on the split-route
  `refine_base`
  family.
- Do not continue this
  additive
  `overlap_dual_extra`
  local-booster axis by default.
  It improves the four non-blocker fixed checks,
  but weakens the active blocker relative
  `v240`
  and does not move the targeted near-real probes in the right direction.
