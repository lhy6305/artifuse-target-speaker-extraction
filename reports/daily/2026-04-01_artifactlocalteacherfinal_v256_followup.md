# 2026-04-01 artifact-local teacher-anchor on split-localmasked output: `v256` follow-up

## Summary

- Goal:
  test whether the merged-bundle artifact-local failure should be pulled toward an artifact-free teacher anchor,
  not toward the raw target waveform.
- Route:
  start from
  `v253`,
  keep the same model, parent, selectors, and trainable prefixes,
  keep
  `local_prediction_source = estimated_waveform_split_localmasked`,
  and replace the
  `v255`
  artifact-local raw-target extra term with a new artifact-local teacher-anchor extra term on the same
  `overlap_dual_extra`
  bucket.
- Smoke:
  passed.
  Coverage stayed correct
  (`overlap_dual_extra train 33 / 263, val 7 / 71`)
  and the new metric
  `val_extra_local_teacher_waveform_extra_l1 = 0.000139`
  was nonzero.
- Full:
  `v256`
  is training-real and materially changes the merged-bundle synthetic surface.
  Relative
  `v253`,
  abstention,
  same-gender keep,
  hard-present keep,
  and artifact all improve.
  But the active blocker regresses sharply,
  and the real-side read still does not repair broad speech or the target-conditioned artifact probe.
- Verdict:
  this first teacher-anchor artifact-local continuation on the split-localmasked writer is a bounded reject.
  It proves the route can repair synthetic artifact margin,
  but it does so by over-regularizing away local-blocker gain,
  not by producing a real-side repair.

## `v256 = v253 + artifact-local teacher-anchor on estimated_waveform_split_localmasked`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v256_v253_artifactlocalteacherfinal05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v256_v253_artifactlocalteacherfinal05_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v253_v249_hardlocalmask_covctrl_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Elapsed:
  `85.411s`
- Best validation checkpoint:
  `best_val_loss = 0.306494`
- Final validation metrics at best read:
  - `val_reconstruction_extra_waveform_l1 = 0.009026`
  - `val_reconstruction_extra_stft_l1 = 0.018954`
  - `val_extra_local_waveform_l1 = 0.001377`
  - `val_extra_local_waveform_extra_l1 = 0.001714`
  - `val_extra_local_teacher_waveform_extra_l1 = 0.000108`
  - `val_branch_protect_teacher_overlap_l1 = 0.000295`
  - `val_overlap_dual_residual_waveform_l1 = 0.004800`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001616`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001255`
  - `val_overlap_dual_residual_correction_local_waveform_extra_l1 = 0.001781`
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

- `+0.3966 / +0.2600 / +0.2249 / +0.3684 / -0.3300 dB`

## Fixed Checks relative `v157`

- `+0.3863 / -0.5963 / +0.1328 / -0.5520 / +0.4277 dB`

## Targeted Near-Real Probes relative `v253`

- `near_real_speech_probe_v1 = -0.0261 dB`
- `friend_raw = -0.0399 dB`
- `guodegang_raw = +0.0153 dB`
- `friend_absent_820s = -0.0838 dB`
- `guodegang_anchor_120s = +0.0297 dB`
- `near_real_guodegang_transient_probe_v1 = +0.0153 dB`
- `near_real_target_conditioned_artifact_probe_v1 = -0.0482 dB`

## Read

- The new teacher-anchor objective is real.
  This is not a selector miss:
  the artifact-local extra bucket stays at
  `33 / 263`
  train rows and
  `7 / 71`
  val rows,
  and the new metric
  `val_extra_local_teacher_waveform_extra_l1`
  stays nonzero.
- Synthetic this point looks strong on four axes.
  Relative
  `v253`,
  abstention,
  same-gender keep,
  hard-present keep,
  and artifact all improve materially.
- But this is not a repair.
  The active blocker turns sharply negative
  (`-0.3300 dB`),
  broad speech still turns negative,
  and the target-conditioned artifact probe also turns negative.
  So the teacher-anchor route is over-regularizing the split-localmasked writer rather than solving the mixed real-side failure.

## Conclusion

- `v256`
  does not justify continuing the same merged-bundle split-localmasked artifact-local teacher-anchor axis through scalar retunes.
- The route proves that synthetic artifact margin can be repaired on this writer,
  but only by giving back too much local-blocker margin,
  and without real-side artifact-probe repair.
- Keep
  `v253`
  as the correct merged-bundle control parent.
- If this family continues at all,
  the next move should be a different artifact-specific writer or target family,
  not another small sweep on this same teacher-anchor extra objective.
