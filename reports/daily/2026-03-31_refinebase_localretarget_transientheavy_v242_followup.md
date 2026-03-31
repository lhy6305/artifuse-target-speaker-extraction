# 2026-03-31 transient-heavy local retarget on top of `v240`: `v242` follow-up

## Summary

- Goal:
  test whether the split-route
  `refine_base`
  mixed near-real candidate
  `v240`
  could preserve its repaired keep-side surface
  while moving the remaining speech-transient blocker more selectively
  by narrowing the existing local selector
  instead of adding another keep-side guard.
- Route:
  start from
  `v240`,
  keep the split-route local writer,
  the abstention repair,
  and the music artifact teacher repair unchanged,
  and retarget the
  `overlap_dual`
  local supervision from the full
  `local_speech_leak_proxy_v1`
  bundle to a transient-heavy subset only.
- Subgroup:
  build a new selector with
  `interference_transient_presence_share_mean >= 0.35`
  and
  `interference_transient_presence_minus_mid_db_mean >= 2.0`.
  This produced
  `21`
  selector ids and
  `3`
  selected validation rows:
  `val_000105_local_speech_leak_proxy_v1`,
  `val_000400_local_speech_leak_proxy_v1`,
  and
  `val_000416_local_speech_leak_proxy_v1`.
- Cheap validation:
  the transient-heavy synthetic subset was directionally aligned with the active blocker:
  `v157 -> v240`
  on
  `val_manifest_local_speech_leak_proxy_v1_transientheavy`
  was
  `+0.3364 dB`.
- Smoke:
  `_smoke_v242_v240_refinebase_localretarget_transientheavy_v1`
  passed and confirmed this was a real local retarget:
  `overlap_dual train 3 / 40, val 3 / 67`,
  `branch_protect active = false`,
  `val_loss = 0.219081`.
- Full:
  `v242`
  stayed clearly training-real.
  Relative
  `v240`,
  it improved the four non-blocker fixed checks
  but gave back part of the blocker surplus.
- Near-real read:
  both
  `near_real_speech_probe_v1`
  and
  `near_real_guodegang_transient_probe_v1`
  were practical tie versus
  `v240`.
  So this is not the repair breakthrough yet,
  but it also does not recreate the
  `v241`
  collapse.
- Verdict:
  `v242`
  is a useful new boundary point on top of
  `v240`.
  It is not a promotion and not a meaningful near-real repair,
  but it is a safer local-side continuation than the rejected keep-side speech-transient guard.

## Code Change

- None.
  This round only changed the local selector asset and reused the existing
  split-route
  `refine_base`
  plumbing.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## New Selector Asset

- Selector ids:
  `data/manifests/selectors/overlap_dual_local_speech_leak_proxy_v1_transientheavy_ids.txt`
- Validation manifest:
  `data/synthetic/val_manifest_local_speech_leak_proxy_v1_transientheavy.jsonl`
- Validation compare:
  `reports/eval/compare_v157_vs_v240_on_local_speech_leak_proxy_v1_transientheavy`

## `v242 = v240 + transient-heavy local retarget on overlap_dual`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v242_v240_refinebase_localretarget_transientheavy_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v242_v240_refinebase_localretarget_transientheavy_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T15:34:06`
- Training end:
  `2026-03-31T15:35:33`
- Elapsed:
  `86.275s`
- Final active metrics:
  - `val_loss = 0.210935`
  - `val_reconstruction_extra_waveform_l1 = 0.009579`
  - `val_reconstruction_extra_stft_l1 = 0.019924`
  - `val_extra_local_waveform_l1 = 0.001012`
  - `val_extra_local_sisdr_loss = 0.137002`
  - `val_absent_extra_interval_l1 = 0.000180`
  - `val_branch_protect_teacher_overlap_l1 = 0.000395`
  - `val_gate_absent_mean = 0.002354`
  - `val_gate_keep_mean = 0.084106`
  - `val_overlap_dual_residual_waveform_l1 = 0.003158`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001019`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.000925`
  - `val_overlap_dual_residual_correction_local_sisdr_loss = 0.765012`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.084339`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.004518`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 18 / 233, val 3 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect `inactive`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+0.7686 / +0.3526 / +0.5072 / +0.3656 / +0.3598 dB`

### Fixed Checks relative `v224`

- `+0.7737 / +0.3541 / +0.5043 / +0.3734 / +0.3443 dB`

### Fixed Checks relative `v240`

- `+0.5423 / +0.1739 / +0.2618 / +0.2894 / -0.1761 dB`

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_transientheavy_v242_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_transientheavy_v242_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.0054`
- `improved_count = 0`
- `regressed_count = 0`
- `near_tie_count = 24`

### Probe By Anchor

- `near_real_0003`:
  `-0.0092 dB`
- `near_real_0004`:
  `-0.0059 dB`
- `near_real_0006`:
  `+0.0009 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.0075 dB`
- `guodegang_raw`:
  `+0.0009 dB`

## Guodegang Transient Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_transientheavy_v242_on_near_real_guodegang_transient_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_localretarget_transientheavy_v242_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = +0.0009`
- `improved_count = 0`
- `regressed_count = 0`
- `near_tie_count = 6`

### Probe By Clip

- `guodegang_absent_480s`:
  `-0.0003 dB`
- `guodegang_anchor_120s`:
  `+0.0020 dB`

## Read

- The new branch is not a fake continuation.
  The local selector really changed,
  the active
  `overlap_dual`
  coverage shrank from
  `33 / 233, 7 / 67`
  on
  `v240`
  to
  `18 / 233, 3 / 67`,
  and the local residual-correction terms stayed nonzero.
- Relative
  `v240`,
  the fixed synthetic surface changed in a useful direction:
  abstention,
  same-gender keep,
  hard-present keep,
  and artifact all improved
  (`+0.5423 / +0.1739 / +0.2618 / +0.2894 dB`)
  while local gave back only part of the previous surplus
  (`-0.1761 dB`).
- So this branch is materially different from
  `v241`.
  It does not over-regularize the keep-side output and destroy the active blocker.
- But the targeted near-real read stays below breakthrough.
  Relative
  `v240`,
  both targeted probes are practical tie:
  overall speech probe
  `-0.0054 dB`
  and focused
  `guodegang`
  transient probe
  `+0.0009 dB`.
  The exact
  `near_real_0006 / guodegang_raw / transient_like`
  side moves slightly positive,
  but only at tie scale.
- So the scientific read is now sharper:
  local-selector retargeting on top of
  `v240`
  is safer than adding another keep-side speech-transient guard,
  but the current transient-heavy filter is still too weak to repair the mixed near-real blocker at meaningful scale.

## Conclusion

- `v242` is not a reject and not a promotion.
- It is the first local-selector-retarget continuation on top of
  `v240`
  that preserves the mixed candidate shape,
  improves the four non-blocker fixed checks relative to
  `v240`,
  and avoids the
  `v241`
  collapse.
- But it does not repair the remaining near-real blocker at meaningful scale.
  Both targeted near-real probes stay practical tie relative to
  `v240`.
- Do not start by micro-sweeping the same transient-heavy selector thresholds.
- If this family continues,
  the next local-side retarget should use a different subgroup definition,
  likely with a stronger speech-transient discriminator such as
  `target_interference_logspec_cosine`
  or a narrower transient-anchor subset.
