# 2026-04-01 dual-representation artifact-side bridge on top of `v249`: `v262` follow-up

## Summary

- Goal:
  test whether the dedicated artifact-side bridge family failed mainly because it still read
  `branch_encoded`
  instead of the already-proven non-trivial
  `dual_encoded`
  representation.
- Route:
  reuse the
  `v258`
  artifact-subspan bundle and teacher-anchor objective,
  but change
  `branch_overlap_artifact_local_bridge_source_mode`
  from
  `branch_encoded`
  to
  `dual_encoded`.
- Type:
  same writer family,
  new shared-representation entry point.
- Result:
  the new point is training-real and stays strongly positive on the matched synthetic artifact-subspan asset,
  but the active real artifact probes still regress relative to
  `v249`,
  and they are slightly worse than
  `v258`.
- Verdict:
  close this first source-swap continuation on the dedicated artifact-side bridge family.
  The blocker is not best explained by
  "the bridge only needs dual_encoded instead of branch_encoded."

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add
  `branch_overlap_artifact_local_bridge_source_mode`
  with:
  - `branch_encoded`
  - `dual_encoded`
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose the new model flag in training configs.
- Validation:
  `py_compile`
  passed after the code change.

## `v262 = v249 + artifact-side bridge source swap to dual_encoded`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v262_v249_artifactdualbridge05_v1/best.pt`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v262_v249_artifactdualbridge05_v1_ft1/best.pt`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_artifact_local_bridge_head + branch_overlap_artifact_local_bridge_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-04-01T18:55:19`
- Training end:
  `2026-04-01T18:56:49`
- Elapsed:
  `89.5s`
- Best validation checkpoint:
  `best_val_loss = 0.298183`
- Final validation metric at best epoch:
  `val_artifact_local_bridge_teacher_waveform_extra_l1 = 0.000086`

## Fixed Synthetic Checks relative `v249`

- Order:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`
- Result:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`

## Interval-Aware Real Probes relative `v249`

- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.1397 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.1276 dB`

## Matched Synthetic Artifact Read relative `v249`

- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +3.1857 dB`
  with
  `7 / 7`
  improved samples

## Direct Read relative `v258`

- `near_real_interval_artifact_probe_v2 = -0.0196 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.0196 dB`
- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +0.0493 dB`

## Read

- This continuation is not a no-op.
  The matched synthetic artifact-subspan asset stays strongly positive,
  and even edges slightly upward relative to
  `v258`.
- But the active real artifact probes still move in the wrong direction relative to
  `v249`,
  and the direct
  `v258 -> v262`
  compare is also slightly negative on both real artifact probes.
- So this is not the missing representation fix for the current target-conditioned artifact confound.
  Swapping the dedicated artifact-side bridge from
  `branch_encoded`
  to
  `dual_encoded`
  still leaves the synthetic-real mismatch in place.

## Conclusion

- `v262`
  closes the first source-mode continuation on the dedicated artifact-side bridge family.
- Do not continue this family through:
  - more
    `branch_overlap_artifact_local_bridge_source_mode`
    swaps on the same bridge shape
  - more scalar retunes on the same
    teacher-anchor plus artifact-subspan
    setup
- If this line continues at all,
  the next change should leave the current dedicated artifact-side bridge shape itself,
  not only change which existing encoder representation feeds it.
