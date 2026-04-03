# 2026-04-01 dedicated artifact-mask-adapter writer on top of `v249`: `v265`

## Summary

- `v265 = v249 + dedicated artifact-mask-adapter writer, max_blend 0.05`
  is training-real but directionally wrong.
- Relative to
  `v249`,
  the fixed synthetic five-pack and `near_real_interval_leak_probe_v1` stay exact tie,
  both active real artifact probes move negative,
  and the matched synthetic artifact-subspan asset also collapses hard negative.
- This is not another dormant first-launch point like
  `v263`.
  It is a first-launch wrong-way point.
  Close the dedicated artifact-mask-adapter writer family without doing scalar or blend retunes.

## Motivation

- After
  `v263` and `v264`,
  the dedicated artifact-refine writer family was already closed as
  synthetic-positive and real-negative.
- The next structurally different writer test was to leave refine-space and instead adapt the
  `branch_decoder_mask`
  itself inside
  `artifact_local_proxy_intervals`.
- The goal was to see whether the blocker was specifically tied to current-output refine writeback,
  rather than to the broader artifact-side writer family.

## Code Path

- New model outputs:
  - `branch_overlap_artifact_mask_adapter_controller`
  - `branch_overlap_artifact_mask_adapter_estimate_waveform`
  - `estimated_waveform_post_artifact_mask_adapter`
- New loss term:
  - `artifact_local_mask_adapter_teacher_waveform_extra_l1`
- Files changed:
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`

## Experiment

### `v265 = v249 + artifact-mask-adapter writer, max_blend 0.05`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v265_v249_artifactmaskadapter05_v1_ft1/best.pt`
- Parent:
  `v249`
- Teacher:
  `v157`
- Trainable modules:
  `branch_overlap_artifact_mask_adapter_head + branch_overlap_artifact_mask_adapter_controller_head`
- Active bundle:
  `train/val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_artifactsubspan_bundle_v1`
- Trainable fraction:
  `328962 / 8681874 = 0.037891`
- Timing:
  `2026-04-01T19:47:18 -> 2026-04-01T19:48:17`
  (`58.933 s`)
- Selector coverage:
  `overlap_dual_extra train 33 / 266, val 7 / 74`
- Final validation metric:
  `val_artifact_local_mask_adapter_teacher_waveform_extra_l1 = 0.000076`

## Evaluation Relative to `v249`

### Fixed Synthetic Five-Pack

- `abstention = 0.0000 dB`
- `same_gender_keep = 0.0000 dB`
- `hard_present_keep = 0.0000 dB`
- `artifact = 0.0000 dB`
- `local_speech_leak_proxy_v1 = 0.0000 dB`

### Interval-Aware Real Probes

- `near_real_interval_leak_probe_v1 = 0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.1288 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.0859 dB`

### Matched Synthetic Artifact Probe

- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = -6.3211 dB`
- `0 / 7` improved
- `7 / 7` regressed

## Interpretation

- Unlike
  `v263`,
  this family is not dormant.
  The smoke run was already wrong-way,
  and the full run confirms the same shape.
- The critical read is not only that both active real artifact probes stay negative,
  but also that the matched synthetic artifact-subspan asset collapses hard negative.
- So this is not another
  synthetic-positive and real-negative
  writer mismatch.
  It is a stricter failure:
  the first artifact-mask-adapter launch is wrong on every asset that should activate this writer,
  while the fixed synthetic five-pack and interval leak stay exact tie.
- That shape is sufficient to close the family.
  There is no reason to do
  `max_blend`,
  teacher-anchor,
  or small-weight continuation sweeps on the same writer.

## Decision

- Close the dedicated artifact-mask-adapter writer family at
  `v265`.
- Do not treat it as a safe dormant launch.
- Do not retune
  `branch_overlap_artifact_mask_adapter_max_blend`
  on top of this point.
- Do not retune the same teacher-anchor scalar on this writer.
- The next artifact-side branch must leave this writer family entirely.
