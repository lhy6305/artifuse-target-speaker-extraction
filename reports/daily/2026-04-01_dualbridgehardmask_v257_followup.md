# 2026-04-01 dual-local bridge as the hard local-mask writer: `v257` follow-up

## Summary

- Goal:
  test a structurally different hard local-mask writer on top of the merged-bundle control,
  by replacing the local interval writer inside
  `estimated_waveform_split_localmasked`
  from
  `estimated_waveform_refine_base`
  to
  `estimated_waveform_post_dual_local_bridge`.
- Route:
  start from
  `v253`,
  keep the merged-bundle selectors and keep-side objectives unchanged,
  enable the dedicated
  `branch_overlap_dual_local_bridge`
  writer,
  set
  `branch_overlap_refine_local_hard_mask_source = post_dual_local_bridge`,
  and train only the two bridge heads.
- Smoke:
  passed.
  Coverage stayed correct
  (`reconstruction extra 63 / 263, overlap dual 33 / 263, absent extra 95 / 263, branch protect teacher 117 / 263`)
  and the interval-local metric
  `val_extra_local_waveform_l1 = 0.001385`
  was nonzero.
- Full:
  `v257`
  is training-real and materially changes the interval-aware synthetic surface.
  Relative
  `v253`,
  abstention,
  same-gender keep,
  and hard-present keep stay exact tie,
  artifact improves strongly,
  and the active local blocker regresses sharply.
  All current real probes stay exact tie to
  `v253`.
- Verdict:
  this first dual-local-bridge hardlocalmask-source swap is a bounded synthetic-only branch point, not a real-side candidate.
  The exact real-probe ties should not be read as stability:
  the current near-real probe manifests do not carry the local interval metadata needed to activate this writer family.

## `v257 = v253 + hardlocalmask local writer source swap to post_dual_local_bridge`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v257_v253_dualbridgehardmask_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v257_v253_dualbridgehardmask_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v253_v249_hardlocalmask_covctrl_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_dual_local_bridge_head + branch_overlap_dual_local_bridge_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Elapsed:
  `207.990s`
- Best validation checkpoint:
  `best_val_loss = 0.307260`
- Final validation metrics at best read:
  - `val_reconstruction_extra_waveform_l1 = 0.009044`
  - `val_reconstruction_extra_stft_l1 = 0.018819`
  - `val_extra_local_waveform_l1 = 0.001384`
  - `val_branch_protect_teacher_overlap_l1 = 0.000415`
  - `val_overlap_dual_residual_waveform_l1 = 0.004800`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001616`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001255`
  - `val_branch_overlap_dual_local_bridge_nonlocal_waveform_l1 = 0.000008`
- Selector activity:
  - reconstruction extra `train 63 / 263, val 27 / 71`
  - overlap dual `train 33 / 263, val 7 / 71`
  - absent extra `train 95 / 263, val 24 / 71`
  - branch protect teacher `train 117 / 263, val 24 / 71`

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## Fixed Checks relative `v253`

- `+0.0000 / +0.0000 / +0.0000 / +0.9739 / -0.4393 dB`

## Fixed Checks relative `v157`

- `-0.0104 / -0.8563 / -0.0920 / +0.0535 / +0.3184 dB`

## Targeted Near-Real Probes relative `v253`

- `near_real_speech_probe_v1 = +0.0000 dB`
- `near_real_guodegang_transient_probe_v1 = +0.0000 dB`
- `near_real_target_conditioned_artifact_probe_v1 = +0.0000 dB`

## Read

- This point is not a no-op.
  The new hard local-mask source is active on the synthetic interval-aware route:
  artifact improves
  `+0.9739 dB`
  relative
  `v253`,
  while the active blocker regresses
  `-0.4393 dB`.
- The pattern is also structurally different from the
  `v256`
  split-localmasked objective retunes:
  abstention,
  same-gender keep,
  and hard-present keep stay exact tie,
  so the new bridge writer is mainly changing the artifact or local tradeoff inside the masked region.
- But current real probes cannot read this family.
  The near-real probe manifests expose fields such as
  `sample_id`,
  `recipe`,
  `mixture_audio_path`,
  `target_audio_path`,
  `reference_audio_path`,
  and
  `metadata_path`,
  but they do not carry
  `local_window_start_sec`,
  `local_window_duration_sec`,
  or other local-proxy interval metadata.
  By contrast,
  the synthetic local-proxy manifests do carry those interval fields.
- So the exact
  `0.0 dB`
  real-probe ties are not evidence that the new writer is harmless or ineffective on real audio.
  They show that the current real probe assets do not activate this interval-gated writer family at all.

## Conclusion

- `v257`
  does not justify continuing this same dual-local-bridge hardlocalmask-source swap as a real-side continuation.
- It is a valid synthetic-only boundary point:
  switching the hard local-mask writer source can strongly rebalance artifact versus local behavior inside interval-aware assets,
  but the current real probes cannot evaluate it.
- Do not interpret exact-tie current real-probe results on this family as evidence for stability.
  First build interval-aware real assets if this writer family is to be judged on real audio.
- Keep
  `v253`
  as the merged-bundle real-side control parent.
  If this family continues at all,
  it should continue only with interval-aware real assets,
  not with more scalar retunes against the current probe packs.
