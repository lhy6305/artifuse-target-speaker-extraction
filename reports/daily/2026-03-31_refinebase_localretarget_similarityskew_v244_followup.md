# 2026-03-31 similarity-skewed local retarget on top of `v240`: `v244` follow-up

## Summary

- Goal:
  test whether the split-route
  `refine_base`
  mixed near-real candidate
  `v240`
  could be repaired more selectively than
  `v242`
  or
  `v243`
  by switching away from transient-only narrowing and retargeting the local selector toward a
  high-cosine,
  low-target-share,
  bounded-peak speech subgroup.
- Route:
  keep the split-route local writer,
  keep-side abstention repair,
  and keep-side music artifact teacher repair unchanged,
  but replace the
  `v242` / `v243`
  transient-driven
  `overlap_dual`
  selector with a similarity-skewed local subset:
  `local_selection_mode = speech_target_share_bounded_peak`,
  `target_interference_logspec_cosine >= 0.5`,
  `local_fullmix_target_share <= 0.14`,
  and
  `local_music_share_of_interference >= 0.05`.
- New selector:
  `train 8 / 233, val 3 / 67`
  on the local proxy family,
  with validation rows
  `val_000343_local_speech_leak_proxy_v1`,
  `val_000416_local_speech_leak_proxy_v1`,
  and
  `val_000495_local_speech_leak_proxy_v1`.
- Cheap validation:
  `v157 -> v240`
  on this similarity-skewed validation subset was
  `+0.8275 dB`,
  so the subgroup was strongly aligned with the active blocker before launch.
- Smoke:
  `_smoke_v244_v240_refinebase_localretarget_similarityskew_v1`
  passed and confirmed the intended branch was real:
  `overlap_dual train 2 / 40, val 3 / 67`,
  `branch_protect_teacher train 12 / 40, val 20 / 67`.
- Full:
  `v244`
  stayed clearly training-real.
  Relative
  `v240`,
  all four non-blocker fixed checks improved strongly again,
  but the blocker gave back most of its surplus.
- Near-real read:
  unlike
  `v242`,
  this similarity-skewed retarget is not practical tie.
  Both targeted near-real probes turned clearly negative relative to
  `v240`:
  `near_real_speech_probe_v1 = -0.1064 dB`,
  `near_real_guodegang_transient_probe_v1 = -0.0811 dB`.
- Verdict:
  this similarity-skewed local retarget is bounded reject on top of
  `v240`.
  It improves the fixed guardrails,
  but it spends too much blocker margin and moves the targeted near-real probes the wrong way.

## Code Change

- None.
  This round only changed selector assets and reused the existing split-route
  `refine_base`
  plumbing.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## New Selector Asset

- Selector ids:
  `data/manifests/selectors/overlap_dual_local_speech_leak_proxy_v1_similarityskew_v1_ids.txt`
- Validation manifest:
  `data/synthetic/val_manifest_local_speech_leak_proxy_v1_similarityskew_v1.jsonl`
- Validation compare:
  `reports/eval/compare_v157_vs_v240_on_local_speech_leak_proxy_v1_similarityskew_v1`

## `v244 = v240 + similarity-skewed local retarget`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v244_v240_refinebase_localretarget_similarityskew_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v244_v240_refinebase_localretarget_similarityskew_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T19:23:54`
- Training end:
  `2026-03-31T19:25:05`
- Elapsed:
  `71.806s`
- Best validation loss:
  `0.208310`
- Final active metrics:
  - `val_loss = 0.208704`
  - `val_reconstruction_extra_waveform_l1 = 0.009563`
  - `val_reconstruction_extra_stft_l1 = 0.019962`
  - `val_extra_local_waveform_l1 = 0.000761`
  - `val_extra_local_sisdr_loss = 0.464108`
  - `val_absent_extra_interval_l1 = 0.000175`
  - `val_branch_protect_teacher_overlap_l1 = 0.000367`
  - `val_gate_absent_mean = 0.002103`
  - `val_gate_keep_mean = 0.084110`
  - `val_overlap_dual_residual_waveform_l1 = 0.003653`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001097`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.000681`
  - `val_overlap_dual_residual_correction_local_sisdr_loss = 0.883731`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.085525`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.004324`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 8 / 233, val 3 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect `inactive`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+1.4125 / +0.7279 / +1.0014 / +0.5115 / +0.0092 dB`

### Fixed Checks relative `v240`

- `+1.1863 / +0.5492 / +0.7559 / +0.4353 / -0.5267 dB`

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_similarityskew_v244_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_similarityskew_v244_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.1064`
- `improved_count = 0`
- `regressed_count = 9`
- `near_tie_count = 15`

### Probe By Anchor

- `near_real_0003`:
  `-0.0853 dB`
- `near_real_0004`:
  `-0.1444 dB`
- `near_real_0006`:
  `-0.0811 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.1149 dB`
- `guodegang_raw`:
  `-0.0811 dB`

## Guodegang Transient Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_similarityskew_v244_on_near_real_guodegang_transient_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_similarityskew_v244_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0811`
- `improved_count = 0`
- `regressed_count = 2`
- `near_tie_count = 4`

### Probe By Clip

- `guodegang_absent_480s`:
  `-0.0270 dB`
- `guodegang_anchor_120s`:
  `-0.1353 dB`

## Read

- This continuation is clearly real.
  The new selector stays active at the intended smaller scale:
  `overlap_dual train 8 / 233, val 3 / 67`.
- But the branch now shows the same wrong qualitative surface already exposed by
  `v243`,
  just through a different discriminator.
  Relative
  `v240`,
  all four non-blocker checks improve strongly
  (`+1.1863 / +0.5492 / +0.7559 / +0.4353 dB`),
  while the active blocker gives back
  `-0.5267 dB`.
- So this is not "repair the mixed near-real candidate more selectively".
  It is "push the split-route family toward a safer keep-dominant regime by spending most of the blocker surplus".
- The targeted near-real probes confirm that the direction is wrong.
  Relative
  `v240`,
  both
  `friend_raw`
  and
  `guodegang_raw`
  move negative on the speech probe,
  and the focused
  `guodegang`
  transient probe is also negative.
- This sharpens the contrast with
  `v242`:
  a broader transient-heavy retarget was safer but near-tie;
  a similarity-skewed bounded-peak retarget crosses into real regression,
  even though the cheap synthetic subgroup validation looked strongly aligned.

## Conclusion

- `v244` is a bounded reject on top of
  `v240`.
- Do not continue that same local-selector-retarget family by swapping transient-only thresholds
  for high-cosine bounded-peak speech filters alone.
- `v242` remains the only non-reject point on this selector-retarget line,
  and it still stayed only practical tie on the targeted near-real probes.
- If this family continues,
  the next subgroup should not be "transient-only tighter" or "similarity-skewed bounded-peak".
  It must add a different discriminator or move away from selector-only retargeting.
