# 2026-04-01 additive artifact-local local booster on top of `v253`: `v254` follow-up

## Summary

- Goal:
  test whether the merged-bundle control
  `v253`
  can recover any real-side edge by adding a dedicated artifact-local
  `overlap_dual_extra`
  local booster,
  instead of another keep-side teacher branch.
- Route:
  start from
  `v253`,
  keep the same model, selectors, and trainable prefixes,
  and add
  `overlap_dual_residual_correction_local_waveform_extra_weight = 0.5`
  on
  `hard_present_artifact_local_proxy_v1_ids.txt`.
- Smoke:
  passed.
  The extra branch activated at the intended coverage:
  `overlap_dual_extra train 33 / 263, val 7 / 71`.
- Full:
  `v254`
  is training-real,
  but it does not repair the
  `v253`
  near-real tie.
  Relative
  `v253`,
  four fixed synthetic checks regress again,
  while the active blocker only recovers a small amount.
  The two targeted near-real probes and the target-conditioned artifact probe all stay practical tie.
- Verdict:
  this first additive artifact-local local booster point on the merged bundle is a bounded reject.
  It is not the needed artifact repair.

## `v254 = v253 + overlap_dual_extra artifact-local local booster 0.5`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v254_v253_artifactlocallocalextra05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v254_v253_artifactlocallocalextra05_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v253_v249_hardlocalmask_covctrl_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Training start:
  `2026-04-01T00:54:33`
- Training end:
  `2026-04-01T00:56:14`
- Elapsed:
  `100.958s`
- Best validation checkpoint:
  epoch 4 with
  `best_val_loss = 0.310497`
- Final validation metrics at best epoch:
  - `val_reconstruction_extra_waveform_l1 = 0.009041`
  - `val_reconstruction_extra_stft_l1 = 0.018818`
  - `val_extra_local_waveform_l1 = 0.001365`
  - `val_branch_protect_teacher_overlap_l1 = 0.000424`
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

- `-0.2223 / -0.0489 / -0.1296 / -0.1599 / +0.0570 dB`

## Fixed Checks relative `v249`

- `+0.0512 / +0.0110 / +0.0653 / -0.2216 / -0.0414 dB`

## Targeted Near-Real Probes relative `v253`

- `near_real_speech_probe_v1 = -0.0009 dB`
- `friend_raw = -0.0002 dB`
- `guodegang_raw = -0.0030 dB`
- `friend_absent_820s = +0.0027 dB`
- `guodegang_anchor_120s = -0.0068 dB`
- `near_real_guodegang_transient_probe_v1 = -0.0030 dB`
- `near_real_target_conditioned_artifact_probe_v1 = +0.0026 dB`

## Read

- The extra local branch is definitely active.
  This is not a selector miss:
  `overlap_dual_extra`
  reaches
  `33 / 263`
  train rows and
  `7 / 71`
  val rows,
  and the new validation metric
  `val_overlap_dual_residual_correction_local_waveform_extra_l1`
  is nonzero.
- Even so,
  the read is not a repair.
  Relative
  `v253`,
  the active blocker recovers only
  `+0.0570 dB`,
  while abstention,
  same-gender keep,
  hard-present keep,
  and artifact all move negative again.
- Real-side this point is effectively flat.
  Broad speech is
  `-0.0009 dB`,
  focused guodegang transient is
  `-0.0030 dB`,
  and the target-conditioned artifact probe is
  `+0.0026 dB`.
  All three are practical tie.
- That matters because
  `v253`
  already showed the merged bundle itself can erase most of the old
  `v249`
  probe edge.
  `v254`
  does not win that edge back.
  It only spends more synthetic margin for a real-side tie.

## Conclusion

- `v254`
  does not justify continuing the same merged-bundle
  `overlap_dual_extra`
  artifact-local booster axis through scalar retunes.
- The low-weight point already gives the wrong shape:
  small blocker recovery,
  four synthetic guardrail regressions,
  and near-real practical tie.
- Keep
  `v253`
  as the correct control parent for any future merged-bundle continuation.
- If this family continues at all,
  the next move should be a more structural artifact-specific objective or writer change,
  not another small weight sweep on the same additive local booster.
