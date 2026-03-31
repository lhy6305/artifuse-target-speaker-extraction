# 2026-04-01 coverage-fixed additive artifact-local keep-side teacher continuation on top of `v240`: `v252`

## Summary

- Goal:
  close the scientific gap left by
  `v251`
  by replaying the same additive
  artifact-local
  keep-side teacher branch on top of
  `v240`,
  but with bundle coverage fixed first.
- Route:
  keep the
  `v240`
  split-route
  `refine_base`
  family unchanged,
  preserve the same
  `branch_protect_teacher_overlap_extra_weight = 0.02`,
  and replace the old active bundle with a merged bundle that appends the missing
  `hard_present_artifact_local_proxy_v1`
  rows.
- Coverage fix:
  the new merged manifests are
  `data/synthetic/train_manifest_local_speech_leak_artifact_paired_plus_artifactlocal_bundle_v1.jsonl`
  and
  `data/synthetic/val_manifest_local_speech_leak_artifact_paired_plus_artifactlocal_bundle_v1.jsonl`.
  The explicit ids list is now materialized at
  `data/manifests/selectors/hard_present_artifact_local_proxy_v1_ids.txt`.
- Smoke:
  selector activity landed at the intended scale,
  with
  `branch_protect_teacher_extra train 33 / 263`
  and
  `val 7 / 71`.
- Verdict:
  `v252`
  closes this family.
  Fixing coverage does not reveal a selective artifact repair.
  It steepens the same keep-heavy surface:
  relative
  `v240`,
  the four non-blocker fixed checks improve more strongly,
  but the active local blocker regresses further.
  Real-side the broad speech probe becomes more negative than
  `v251`,
  while the focused guodegang transient probe shrinks to near-tie.
  Do not continue this additive artifact-local
  `branch_protect_teacher_extra`
  axis by weight retune on either the old or the merged bundle.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v252 = v240 + additive artifact-local keep-side teacher overlap 0.02` on the coverage-fixed merged bundle

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v252_v240_artifactlocalteacherextra002_covfix_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v252_v240_artifactlocalteacherextra002_covfix_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-04-01T00:24:36`
- Training end:
  `2026-04-01T00:25:41`
- Elapsed:
  `64.481s`
- Best val loss:
  `0.063444`
- Final active metrics:
  - `val_branch_protect_teacher_overlap_l1 = 0.000162`
  - `val_branch_protect_teacher_overlap_extra_l1 = 0.000071`
  - `val_extra_local_waveform_l1 = 0.002129`
  - `val_overlap_dual_residual_waveform_l1 = 0.052253`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.017041`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.002112`
- Selector activity:
  - absent extra `train 95 / 263, val 24 / 71`
  - branch protect teacher `train 117 / 263, val 24 / 71`
  - branch protect teacher extra `train 33 / 263, val 7 / 71`

### Fixed Checks relative `v240`

- `+0.7618 / +0.3546 / +0.4219 / +0.3585 / -0.6538 dB`

### Fixed Checks relative `v157`

- `+0.9881 / +0.5333 / +0.6674 / +0.4347 / -0.1179 dB`

### Direction change relative `v251`

- On fixed synthetic relative
  `v240`,
  coverage fixing steepens the keep-heavy surface from
  `v251`
  by
  `+0.4077 / +0.2814 / +0.4114 / +0.2336 / -0.2665 dB`.
- The artifact-local extra branch is therefore not merely underpowered on the old bundle.
  At full coverage on the current family,
  it pulls harder in the same direction and gives back more blocker margin.

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v252_covfix_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v252_covfix_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.1269`
- `improved_count = 2`
- `regressed_count = 8`
- `near_tie_count = 14`

### Probe By Anchor

- `near_real_0003`:
  `-0.1869 dB`
- `near_real_0004`:
  `-0.1778 dB`
- `near_real_0006`:
  `+0.0395 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.1824 dB`
- `guodegang_raw`:
  `+0.0395 dB`

### Probe By Speech Clip

- `friend_absent_820s`:
  `-0.4467 dB`
- `friend_anchor_215s`:
  `-0.0057 dB`
- `friend_anchor_45s`:
  `-0.0947 dB`
- `guodegang_absent_480s`:
  `-0.0215 dB`
- `guodegang_anchor_120s`:
  `+0.1006 dB`

### Relative `v251`

- Broad speech probe relative
  `v240`
  moves from
  `-0.0239 dB`
  in
  `v251`
  to
  `-0.1269 dB`
  in
  `v252`,
  a further
  `-0.1030 dB`
  regression.

## Guodegang Transient Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v252_covfix_on_near_real_guodegang_transient_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_artifactlocalteacherextra_v252_covfix_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = +0.0395`
- `improved_count = 2`
- `regressed_count = 0`
- `near_tie_count = 4`

### Probe By Clip

- `guodegang_absent_480s`:
  `-0.0215 dB`
- `guodegang_anchor_120s`:
  `+0.1006 dB`

### Relative `v251`

- Focused guodegang transient relative
  `v240`
  shrinks from
  `+0.0863 dB`
  in
  `v251`
  to
  `+0.0395 dB`
  in
  `v252`,
  a
  `-0.0468 dB`
  weakening.

## Read

- `v252`
  is training-real and coverage-real.
  The merged bundle and explicit ids file successfully raise
  `branch_protect_teacher_extra`
  from
  `3 / 233`
  and
  `3 / 67`
  in
  `v251`
  to
  `33 / 263`
  and
  `7 / 71`.
- That coverage fix does not uncover a selective artifact-local repair regime.
  Instead it steepens the same keep-heavy continuation that
  `v251`
  already hinted at.
  Relative
  `v240`,
  the four non-blocker fixed checks all move further positive,
  while the active blocker regresses further to
  `-0.6538 dB`.
- Real-side the broader speech probe turns clearly negative,
  with the main damage concentrated in the
  `friend_raw`
  slice and especially
  `friend_absent_820s`.
  The focused guodegang transient slice stays slightly positive,
  but only at near-tie scale.
- The new scientific read is therefore stronger than
  `v251`:
  the additive artifact-local extra teacher idea is not merely under-covered on the old bundle.
  On the current
  `v240`
  family, full coverage still yields the wrong direction.

## Conclusion

- The additive artifact-local keep-side teacher family on top of
  `v240`
  is now bounded through
  `v252`.
- `v250`
  remains invalid scratch because of command drift.
- `v251`
  remains useful as the coverage-limited precursor.
- `v252`
  is the closure-quality read:
  after coverage fixing,
  it is still a keep-heavy continuation rather than an artifact repair.
- Keep
  `v157`
  as the active automatic base.
- Keep
  `v240`
  as the leading mixed near-real candidate inside the split-route
  `refine_base`
  family.
- Do not continue additive
  artifact-local
  `branch_protect_teacher_extra`
  weight retunes on either the old active bundle or the merged coverage-fixed bundle.
