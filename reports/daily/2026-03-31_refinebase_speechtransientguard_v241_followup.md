# 2026-03-31 speech-transient keep-side guard on top of `v240`: `v241` follow-up

## Summary

- Goal:
  test whether the split-route
  `refine_base`
  mixed near-real candidate
  `v240`
  could repair its failed
  `target_present__speech`
  whole-tradeoff path and the
  `guodegang_raw / transient_like`
  drag
  by adding a focused keep-side
  `branch_protect_guard_sisdr`
  term on speech-present transient-heavy synthetic slices.
- Route:
  start from
  `v240`,
  keep the split-route local writer and the music artifact teacher repair unchanged,
  and add
  `branch_protect_guard_sisdr_weight = 0.001`
  on
  `target_clean_speech + target_hard_speech`
  plus
  `target_full`
  with
  `min_interference_transient_presence_share_mean = 0.35`
  and
  `min_interference_transient_presence_minus_mid_db_mean = 2.0`.
- Smoke:
  `_smoke_v241_v240_refinebase_speechtransientguard001_v1`
  passed and confirmed the new guard was training-real:
  `branch_protect val 11 / 67`,
  `val_branch_protect_guard_sisdr_loss = 2.870708`.
- Full:
  `v241`
  stayed training-real,
  but it moved in the wrong direction for this branch goal.
  Relative
  `v240`,
  all four non-blocker fixed checks improved strongly,
  while the active blocker regressed sharply.
- Near-real read:
  the targeted
  `near_real_speech_probe_v1`
  follow-up versus
  `v240`
  was uniformly negative,
  not a repair:
  overall
  `-0.1754 dB`,
  with both
  `friend_raw`
  and
  `guodegang_raw`
  negative.
- Verdict:
  this axis is bounded reject.
  It is not a near-real speech repair.
  It is a keep-side over-regularization that buys more fixed guardrail margin by spending the local writer.

## Code Change

- None.
  This round used existing
  `branch_protect_guard_sisdr`
  selector plumbing and the existing split-route
  `refine_base`
  writable-path setup.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v241 = v240 + speech-transient keep-side branch_protect_guard_sisdr 0.001`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v241_v240_refinebase_speechtransientguard001_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v241_v240_refinebase_speechtransientguard001_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T14:47:01`
- Training end:
  `2026-03-31T14:47:54`
- Elapsed:
  `53.394s`
- Final active metrics:
  - `val_loss = 0.301457`
  - `val_reconstruction_extra_waveform_l1 = 0.009562`
  - `val_reconstruction_extra_stft_l1 = 0.020081`
  - `val_extra_local_waveform_l1 = 0.001279`
  - `val_absent_extra_interval_l1 = 0.000348`
  - `val_branch_protect_guard_sisdr_loss = 2.491614`
  - `val_branch_protect_teacher_overlap_l1 = 0.000400`
  - `val_gate_absent_mean = 0.009120`
  - `val_gate_keep_mean = 0.123440`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.125544`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.007855`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect `train 26 / 233, val 11 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+1.9704 / +1.0398 / +1.3298 / +0.7833 / -0.3131 dB`

### Fixed Checks relative `v240`

- `+1.7442 / +0.8611 / +1.0843 / +0.7071 / -0.8490 dB`

## Near-Real Speech Probe relative `v240`

- Compare:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_speechtransientguard_v241_on_near_real_speech_probe_v1`
- Analysis:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_refinebase_speechtransientguard_v241_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = -0.1754`
- `improved_count = 0`
- `regressed_count = 12`
- `near_tie_count = 12`

### Probe By Anchor

- `near_real_0003`:
  `-0.2041 dB`
- `near_real_0004`:
  `-0.1856 dB`
- `near_real_0006`:
  `-0.1169 dB`

### Probe By Speech Family

- `friend_raw`:
  `-0.1949 dB`
- `guodegang_raw`:
  `-0.1169 dB`

## Read

- The new branch is clearly not a fake continuation.
  The speech-transient keep-side selector is active at useful scale,
  and the new
  `branch_protect_guard_sisdr`
  metric stays strongly nonzero in smoke and full.
- But the fixed synthetic direction is the wrong one for this branch goal.
  Relative
  `v240`,
  the route buys large gains on abstention, same-gender keep, hard-present keep, and artifact
  (`+1.7442 / +0.8611 / +1.0843 / +0.7071 dB`)
  while the active blocker regresses
  `-0.8490 dB`.
- So this is not "repair the mixed near-real candidate while preserving the blocker".
  It is "push the keep-side output closer to a safer speech-preserve regime and spend local-writer leverage to do it".
- The targeted near-real probe confirms that this is not a hidden speech-side repair.
  Relative
  `v240`,
  the probe is negative overall
  (`-0.1754 dB`),
  negative on both
  `friend_raw`
  and
  `guodegang_raw`,
  and negative on all three active anchors
  `near_real_0003 / 0004 / 0006`.
- So the route does not selectively repair the
  `guodegang_raw / transient_like`
  drag.
  It broadly over-regularizes the same split-route family.

## Conclusion

- `v241` is a bounded reject on top of `v240`.
- Do not keep sweeping
  `branch_protect_guard_sisdr_weight`
  on this synthetic speech-transient keep-side selector.
- `v240` remains the leading mixed near-real candidate inside the split-route
  `refine_base`
  family.
- If this family continues,
  the next repair should not be another synthetic keep-side speech-transient guard on the same output path.
