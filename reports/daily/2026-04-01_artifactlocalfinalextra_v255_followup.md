# 2026-04-01 artifact-local final-output extra supervision on top of `v253`: `v255` follow-up

## Summary

- Goal:
  test a more structural artifact-specific continuation on the merged-bundle control
  `v253`
  by supervising the actual hard-masked final local output,
  not only the internal dual residual-correction estimate.
- Route:
  start from
  `v253`,
  keep the same model, parent, selectors, and trainable prefixes,
  switch
  `local_prediction_source`
  from
  `estimated_waveform_refine_base`
  to
  `estimated_waveform_split_localmasked`,
  and add a new
  `extra_local_waveform_extra_weight = 0.5`
  on the artifact-local
  `overlap_dual_extra`
  selector.
- Smoke:
  passed.
  The extra bucket stayed active at the intended coverage
  (`overlap_dual_extra train 33 / 263, val 7 / 71`)
  and the new metric
  `val_extra_local_waveform_extra_l1 = 0.001711`
  was nonzero.
- Full:
  `v255`
  is training-real,
  but it still does not repair the merged-bundle real-side read.
  Relative
  `v253`,
  abstention,
  same-gender keep,
  and hard-present keep improve,
  but artifact turns slightly negative and the active blocker also turns negative.
  The three targeted real probes all stay practical tie to mild negative.
- Verdict:
  this first direct artifact-local final-output extra-supervision point on the merged bundle is a bounded reject.
  It mildly rebalances the synthetic surface,
  but it is not an artifact repair and not a real-side recovery.

## `v255 = v253 + artifact-local extra_local waveform on split_localmasked output`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v255_v253_artifactlocalfinalextra05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v255_v253_artifactlocalfinalextra05_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v253_v249_hardlocalmask_covctrl_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Elapsed:
  `72.658s`
- Best validation checkpoint:
  `best_val_loss = 0.310179`
- Final validation metrics at best read:
  - `val_reconstruction_extra_waveform_l1 = 0.009028`
  - `val_reconstruction_extra_stft_l1 = 0.018810`
  - `val_extra_local_waveform_l1 = 0.001365`
  - `val_extra_local_waveform_extra_l1 = 0.001708`
  - `val_branch_protect_teacher_overlap_l1 = 0.000415`
  - `val_overlap_dual_residual_waveform_l1 = 0.004800`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001616`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001255`
  - `val_overlap_dual_residual_correction_local_waveform_extra_l1 = 0.001782`
- Selector activity:
  - reconstruction extra `train 63 / 263, val 27 / 71`
  - overlap dual `train 66 / 263, val 14 / 71`
  - overlap dual extra `train 33 / 263, val 7 / 71`
  - absent extra `train 95 / 263, val 24 / 71`
  - branch protect teacher `train 117 / 263, val 24 / 71`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## Fixed Checks relative `v253`

- `+0.1098 / +0.1122 / +0.0958 / -0.0167 / -0.0401 dB`

## Fixed Checks relative `v157`

- `+0.0995 / -0.7441 / +0.0037 / -0.9371 / +0.7176 dB`

## Targeted Near-Real Probes relative `v253`

- `near_real_speech_probe_v1 = -0.0199 dB`
- `friend_raw = -0.0217 dB`
- `guodegang_raw = -0.0145 dB`
- `friend_absent_820s = -0.0444 dB`
- `guodegang_anchor_120s = -0.0193 dB`
- `near_real_guodegang_transient_probe_v1 = -0.0145 dB`
- `near_real_target_conditioned_artifact_probe_v1 = -0.0312 dB`

## Read

- The new objective is real.
  This is not a selector miss:
  `overlap_dual_extra`
  keeps the same
  `33 / 263`
  train rows and
  `7 / 71`
  val rows as the merged-bundle artifact-local bucket,
  and the new metric
  `val_extra_local_waveform_extra_l1`
  stays nonzero.
- The route does alter the synthetic shape,
  but in the wrong way for promotion.
  Relative
  `v253`,
  three fixed guardrails improve
  while artifact and the active blocker both regress.
- Real-side this still does not repair the merged-bundle family.
  Broad speech,
  focused guodegang transient,
  and the target-conditioned artifact probe all stay practical tie to mild negative.
  So direct artifact-local supervision on the hard-masked final output does not recover the lost
  `v249`
  edge.

## Conclusion

- `v255`
  does not justify continuing the same merged-bundle artifact-local final-output extra-supervision axis through scalar retunes.
- The first structural point already shows the likely ceiling:
  mild synthetic rebalancing,
  but no real-side recovery and no artifact-probe repair.
- Keep
  `v253`
  as the correct merged-bundle control parent.
- If this family continues at all,
  the next move should be a different artifact-specific writer or target,
  not another small weight sweep on this same extra-local final-output objective.
