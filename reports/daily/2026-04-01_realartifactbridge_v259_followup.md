# 2026-04-01 dedicated artifact-side bridge with real artifact booster on top of `v249`: `v259` follow-up

## Summary

- Goal:
  test whether the negative
  `v258`
  read was mainly caused by the synthetic artifact-subspan asset family,
  rather than by the dedicated artifact-side bridge writer itself.
- Route:
  keep the same
  `v249`
  parent,
  keep the same dedicated artifact-side bridge writer,
  but replace the extra artifact booster asset family with a tiny real booster bundle built from
  `near_real_interval_artifact_probe_v3_subspan`.
- Booster split:
  hold out one full
  `speech_clip_tag`
  family
  (`friend_absent_820s`)
  into val,
  and use the other two clip families for train.
- Smoke:
  passed.
  The first
  `20`
  steps did not sample any real booster rows on train,
  but val already showed the extra branch was alive.
- Full:
  the dedicated bridge remains training-real,
  and the real booster rows are actually seen during full training
  (`train 6 / 239, val 3 / 70`).
  But the real artifact probes move further negative relative to
  `v249`,
  not positive.
- Verdict:
  close this first real-booster continuation on the dedicated artifact-side bridge family.
  Changing the asset family from synthetic artifact-subspan to direct real artifact booster does not rescue the family.

## Real Booster Asset

- Source probe:
  `data/probes/near_real_interval_artifact_probe_v3_subspan_manifest.jsonl`
- Builder:
  `scripts/data/build_artifact_probe_v3_real_booster_bundle.py`
- Train rows:
  `6`
- Val rows:
  `3`
- Holdout policy:
  full
  `speech_clip_tag = friend_absent_820s`
  held out into val
- Merged manifests:
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_realartifactv3_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_realartifactv3_bundle_v1.jsonl`
- Selector ids:
  `data/manifests/selectors/real_artifact_probe_v3_subspan_ids.txt`

## `v259 = v249 + dedicated artifact-side bridge with real artifact booster`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v259_v249_realartifactbridge20_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v259_v249_realartifactbridge20_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_artifact_local_bridge_head + branch_overlap_artifact_local_bridge_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-04-01T18:10:59`
- Training end:
  `2026-04-01T18:12:00`
- Elapsed:
  `61.444s`
- Best validation checkpoint:
  epoch 4 with
  `best_val_loss = 0.311456`
- Final validation metrics at best epoch:
  - `val_artifact_local_bridge_teacher_waveform_extra_l1 = 0.000061`
  - `val_reconstruction_extra_waveform_l1 = 0.009181`
  - `val_reconstruction_extra_stft_l1 = 0.019073`
  - `val_extra_local_waveform_l1 = 0.001389`
  - `val_branch_protect_teacher_overlap_l1 = 0.000402`
  - `val_overlap_dual_residual_waveform_l1 = 0.004866`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001637`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001271`
  - `val_gate_keep_mean = 0.130479`
- Selector activity:
  - reconstruction extra `train 63 / 239, val 27 / 70`
  - overlap dual `train 39 / 239, val 10 / 70`
  - overlap dual extra `train 6 / 239, val 3 / 70`
  - absent extra `train 95 / 239, val 24 / 70`
  - branch protect teacher `train 87 / 239, val 20 / 70`

## Fixed Synthetic Checks relative `v249`

- Order:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`
- Result:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`

## Interval-Aware Real Probes relative `v249`

- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.2206 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.2261 dB`

## Synthetic Artifact Reads relative `v249`

- `val_manifest_hard_present_artifact_local_proxy_v1 = +0.0000 dB`
- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +0.2022 dB`

## Read

- The bridge family remains clearly trainable.
  This is not a no-op:
  the real booster selector is active during full training,
  and the extra bridge loss is non-zero on val.
- But moving from the synthetic artifact-subspan asset
  (`v258`)
  to the tiny real booster asset
  (`v259`)
  does not repair the real-side read.
  It makes it worse.
  The two active real artifact probes both regress more strongly relative to
  `v249`
  than the synthetic-booster version did.
- At the same time,
  the matched synthetic artifact-subspan improvement collapses from the strong
  `v258`
  read
  (`+3.1363 dB`)
  down to only
  `+0.2022 dB`
  here.
  So this is not a case where the real booster simply trades synthetic gains for real gains.
  It weakens both.
- The practical conclusion is tighter than after
  `v258`:
  the next blocker is probably not
  "choose a better booster asset for the same dedicated bridge writer."
  The writer or target-conditioning mechanism itself now looks like the more likely bottleneck.

## Conclusion

- `v259`
  closes the first real-booster continuation on the dedicated artifact-side bridge family.
- Do not continue this family through:
  - more weight sweeps on
    `artifact_local_bridge_teacher_waveform_extra_weight`
  - more retunes of
    `branch_overlap_artifact_local_bridge_max_blend`
  - more small train-val split variations of the same
    `artifact_probe_v3_subspan`
    real booster bundle
- If this line continues at all,
  the next step should change writer family or target-conditioning mechanism,
  not keep reusing the same dedicated bridge with another booster asset swap.
