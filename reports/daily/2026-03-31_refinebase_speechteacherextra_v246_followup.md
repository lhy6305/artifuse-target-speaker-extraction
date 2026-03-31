# 2026-03-31 additive speech-only keep-side teacher repair on top of `v240`: `v246` follow-up

## Summary

- Goal:
  test whether the mixed near-real
  `v240`
  candidate could repair the failed
  `target_present__speech`
  whole-tradeoff bucket by keeping the existing plus-music artifact teacher branch unchanged and adding a second
  speech-only
  keep-side teacher-overlap branch.
- Route:
  start from
  `v240`,
  keep the split-route
  `refine_base`
  local writer,
  the abstention repair,
  the plus-music artifact teacher repair,
  and the full
  `overlap_dual`
  local bundle unchanged,
  then add an additive
  `branch_protect_teacher_extra`
  selector with
  `target_clean_speech + target_hard_speech`,
  `target_full`,
  speech interference required,
  music interference forbidden,
  and a new
  `branch_protect_teacher_overlap_extra`
  loss term.
- Smoke:
  `_smoke_v246_v240_refinebase_speechteacherextra002_v1`
  passed.
  The base plus-music keep-side teacher branch stayed active,
  and the new speech-only branch was also real
  (`branch_protect_teacher_extra train 6 / 40, val 23 / 67`,
  `val_branch_protect_teacher_overlap_extra_l1 = 0.000633`).
- Full:
  `v246`
  was training-real.
  Relative
  `v157`,
  all five fixed synthetic checks stayed positive and became even larger.
  Relative
  `v240`,
  the four non-blocker checks all improved,
  but the active local blocker gave back materially.
- Near-real:
  both targeted probes moved slightly negative relative
  `v240`.
  The new speech-only teacher branch did not repair the mixed candidate;
  it behaved like another keep-heavy regularizer.
- Verdict:
  this axis is a bounded reject.
  Do not continue the same additive
  speech-only
  `branch_protect_teacher_extra`
  family by weight micro-sweeps or minor subgroup swaps on the same keep-side objective.

## Code Change

- Added additive
  `branch_protect_teacher_extra`
  selector support for keep-side teacher-overlap loss.
- Files:
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v246 = v240 + additive speech-only keep-side teacher overlap 0.02`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v246_v240_refinebase_speechteacherextra002_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v246_v240_speechteacherextra002_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T20:51:37`
- Training end:
  `2026-03-31T20:52:50`
- Elapsed:
  `72.976s`
- Best val loss:
  `0.298667`
- Final active metrics:
  - `val_branch_protect_teacher_overlap_l1 = 0.000385`
  - `val_branch_protect_teacher_overlap_extra_l1 = 0.000614`
  - `val_extra_local_waveform_l1 = 0.001262`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 138 / 233, val 43 / 67`
  - branch protect teacher extra `train 51 / 233, val 23 / 67`

### Fixed Checks relative `v157`

- `+1.1681 / +0.5278 / +0.7823 / +0.5717 / +0.2474 dB`

### Fixed Checks relative `v240`

- `+0.9419 / +0.3491 / +0.5369 / +0.4956 / -0.2885 dB`

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_speechteacherextra_v246_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_speechteacherextra_v246_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0367`
- `improved_count = 0`
- `regressed_count = 2`
- `near_tie_count = 22`

### Probe By Anchor

- `near_real_0003`:
  `-0.0266 dB`
- `near_real_0004`:
  `-0.0480 dB`
- `near_real_0006`:
  `-0.0349 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.0373 dB`
- `guodegang_raw`:
  `-0.0349 dB`

### Probe By Speech Clip

- `friend_absent_820s`:
  `-0.0919 dB`
- `friend_anchor_215s`:
  `+0.0004 dB`
- `friend_anchor_45s`:
  `-0.0205 dB`
- `guodegang_absent_480s`:
  `-0.0082 dB`
- `guodegang_anchor_120s`:
  `-0.0615 dB`

## Guodegang Transient Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_speechteacherextra_v246_on_near_real_guodegang_transient_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_speechteacherextra_v246_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0349`
- `improved_count = 0`
- `regressed_count = 0`
- `near_tie_count = 6`

### Probe By Clip

- `guodegang_absent_480s`:
  `-0.0082 dB`
- `guodegang_anchor_120s`:
  `-0.0615 dB`

## Read

- The new speech-only teacher branch is real,
  not a fake continuation.
  The extra selector is active on both train and val,
  and the extra metric stays nonzero through smoke and full.
- Relative
  `v157`,
  the result still looks very strong on fixed synthetic.
  All five active checks stay positive,
  and the four non-blocker axes become much larger than
  `v240`.
- Relative
  `v240`,
  the direction is not what we needed.
  This continuation improves the four non-blocker axes
  but gives back
  `-0.2885 dB`
  on the active local blocker.
  So the additive speech-only keep-side teacher acts like another keep-heavy regularizer,
  not like a targeted
  `target_present__speech`
  repair.
- The targeted near-real probes agree with that read.
  They do not collapse,
  but both move slightly negative relative
  `v240`,
  and the anchor slice
  `guodegang_anchor_120s`
  also moves negative.
  So this is not a repair candidate for the
  mixed near-real failure.

## Conclusion

- `v246`
  is a bounded additive keep-side continuation on top of
  `v240`,
  not a promotion and not a near-real repair.
- Keep
  `v240`
  as the leading mixed near-real candidate on the split-route
  `refine_base`
  family.
- Do not continue this additive
  speech-only
  `branch_protect_teacher_extra`
  axis by default.
  It improves the four non-blocker fixed checks,
  but weakens the active blocker and both targeted near-real probes relative
  `v240`.
