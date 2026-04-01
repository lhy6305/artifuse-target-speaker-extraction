# 2026-04-01 hardlocalmask merged-bundle coverage control: `v253` follow-up

## Summary

- Goal:
  isolate the effect of the merged artifact-local bundle itself before adding any new booster objective on top of
  `v249`.
- Route:
  replay
  `v249`
  on the merged bundle
  `train_manifest_local_speech_leak_artifact_paired_plus_artifactlocal_bundle_v1.jsonl`
  and
  `val_manifest_local_speech_leak_artifact_paired_plus_artifactlocal_bundle_v1.jsonl`,
  with the same losses, selectors, model config, and trainable prefixes as
  `v249`.
- Smoke:
  the first smoke was not a faithful replay because the manual command omitted the original
  `reconstruction_extra`
  and
  `overlap_dual`
  focus sample-id assets.
  That made both selectors drop to
  `0 / 0`.
  A corrected smoke
  (`_fix1`)
  restored the expected replay shape:
  `reconstruction_extra train 63 / 263, val 27 / 71`
  and
  `overlap_dual train 33 / 263, val 7 / 71`.
- Full:
  `v253`
  is a real control run, not a candidate.
  Relative
  `v249`,
  synthetic fixed checks become mixed rather than uniformly worse,
  but the targeted near-real edge mostly collapses back to near-tie.
- Verdict:
  the merged bundle itself is now a material confound for the
  `v249`
  family.
  Future merged-bundle continuation runs must compare against
  `v253`,
  not directly against
  `v249`.

## `v253 = v249 replay on merged artifact-local bundle`

- Corrected smoke checkpoint:
  `experiments/checkpoints/_smoke_v253_v249_hardlocalmask_covctrl_v1_fix1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v253_v249_hardlocalmask_covctrl_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-04-01T00:44:36`
- Training end:
  `2026-04-01T00:45:42`
- Elapsed:
  `66.091s`
- Best validation checkpoint:
  epoch 4 with
  `best_val_loss = 0.307249`
- Final validation metrics at best epoch:
  - `val_reconstruction_extra_waveform_l1 = 0.009044`
  - `val_reconstruction_extra_stft_l1 = 0.018819`
  - `val_extra_local_waveform_l1 = 0.001362`
  - `val_branch_protect_teacher_overlap_l1 = 0.000415`
  - `val_overlap_dual_residual_waveform_l1 = 0.004800`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001616`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001255`
- Selector activity:
  - reconstruction extra `train 63 / 263, val 27 / 71`
  - overlap dual `train 33 / 263, val 7 / 71`
  - absent extra `train 95 / 263, val 24 / 71`
  - branch protect teacher `train 117 / 263, val 24 / 71`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## Fixed Checks relative `v249`

- `+0.2735 / +0.0599 / +0.1948 / -0.0617 / -0.0985 dB`

## Fixed Checks relative `v157`

- `-0.0103 / -0.8563 / -0.0921 / -0.9204 / +0.7577 dB`

## Targeted Near-Real Probes relative `v249`

- `near_real_speech_probe_v1 = -0.0231 dB`
- `friend_raw = -0.0363 dB`
- `guodegang_raw = +0.0164 dB`
- `friend_absent_820s = -0.0878 dB`
- `guodegang_anchor_120s = +0.0343 dB`
- `near_real_guodegang_transient_probe_v1 = +0.0164 dB`
- `near_real_target_conditioned_artifact_probe_v1 = -0.0519 dB`

## Read

- The corrected smoke matters:
  the first manual replay silently dropped the original
  `reconstruction_extra`
  and
  `overlap_dual`
  selectors,
  so it was not a valid bundle-control read.
  Only the corrected smoke and the full run count as
  `v253`.
- Once the replay is faithful,
  the merged bundle alone already changes the
  `v249`
  surface.
  Synthetic fixed checks become mixed:
  abstention,
  same-gender keep,
  and hard-present keep recover somewhat,
  but artifact and the active blocker both regress relative
  `v249`.
- Real-side the sharper result is not an improvement but a collapse to near-tie.
  The broad speech probe moves from the strong
  `v249`
  advantage back to
  `-0.0231 dB`,
  with the main damage concentrated on the
  `friend_raw`
  side and especially
  `friend_absent_820s`.
  The focused guodegang transient probe is only
  `+0.0164 dB`,
  which is also practical tie.
- The target-conditioned artifact probe also weakens slightly.
  So the merged-bundle shift is not just neutral bookkeeping.
  It materially changes the probe read of this family even before any new additive objective is applied.

## Conclusion

- `v253`
  is the required control for any future merged-bundle continuation on top of
  `v249`.
- It is not a promotion candidate.
- It is also not a simple reject,
  because its main role is methodological:
  it shows that bundle shift alone partially erases the
  `v249`
  probe edge.
- If this family continues on the merged bundle,
  compare the next run against
  `v253`,
  not directly against
  `v249`.
- Do not read a future artifact-local booster on the merged bundle as a clean gain over
  `v249`
  unless it first beats
  `v253`.
