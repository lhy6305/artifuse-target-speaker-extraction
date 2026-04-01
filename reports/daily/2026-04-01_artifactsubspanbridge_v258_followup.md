# 2026-04-01 dedicated artifact-side bridge on top of `v249`: `v258` follow-up

## Summary

- Goal:
  test whether the next structural step after closing the
  `v255 / v256`
  split-localmasked artifact-objective family should be a new dedicated artifact-side writer,
  trained on the new
  `hard_present_artifact_local_proxy_v2_subspan`
  synthetic asset family.
- Route:
  start from
  `v249`,
  keep the existing hardlocalmask leak route frozen,
  add a new
  `branch_overlap_artifact_local_bridge`
  writer that only applies inside
  `artifact_local_proxy_intervals`,
  and train only the new writer heads with a teacher-anchor loss on the extra artifact-subspan selector.
- Smoke:
  the first direct launch was invalid because the command omitted
  `enable_branch_overlap_dual_decoder_head`,
  which is still required by the inherited dual residual-correction path.
  The corrected smoke passed and confirmed that:
  - the new writer is trainable and not a no-op
  - `overlap_dual_extra` is active on the new artifact-subspan rows
  - `artifact_local_bridge_teacher_waveform_extra_l1` is non-zero
- Full:
  `v258`
  is training-real on the new synthetic artifact-subspan family,
  but it does not improve the active real artifact probes relative to
  `v249`.
- Verdict:
  close this first-launch dedicated artifact-side bridge point as a bounded negative first read.
  It is not a writer no-op,
  but it currently looks like a synthetic-real asset mismatch rather than a real artifact repair.

## Code And Asset Change

- Updated:
  `src/tse_prefix/data/synthetic_dataset.py`
  to expose
  `artifact_local_proxy_intervals`
  alongside the existing
  `local_proxy_intervals`.
- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add
  `branch_overlap_artifact_local_bridge_head`,
  `branch_overlap_artifact_local_bridge_controller_head`,
  and
  `estimated_waveform_post_artifact_local_bridge`.
- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add
  `artifact_local_bridge_teacher_waveform_extra_l1`
  and the corresponding extra-loss term.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`,
  `scripts/eval/eval_stft_mask_baseline.py`,
  `scripts/eval/compare_checkpoints_on_manifest.py`,
  `scripts/eval/export_ab_inference_from_manifest.py`,
  and
  `scripts/eval/export_ab_listening_pack.py`
  so the new writer receives
  `artifact_local_proxy_intervals`
  and the new loss weight is configurable.
- Added new synthetic asset builder:
  `scripts/data/build_hard_present_artifact_local_proxy_v2_subspan.py`
- Added new synthetic asset family:
  `train_manifest_hard_present_artifact_local_proxy_v2_subspan.jsonl`
  and
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan.jsonl`
- Added merged training bundle:
  `train_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_artifactsubspan_bundle_v1.jsonl`
  and
  `val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_plus_artifactsubspan_bundle_v1.jsonl`
- Added selector asset:
  `data/manifests/selectors/hard_present_artifact_local_proxy_v2_subspan_ids.txt`
- Updated the interval-aware real artifact probe metadata so the new writer can actually activate there:
  copied
  `local_proxy`
  into
  `artifact_local_proxy`
  for the v2 and v3 artifact probe families.
- Validation:
  `py_compile`
  passed after the code changes.

## `v258 = v249 + dedicated artifact-side bridge on artifact-subspan bundle`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v258_v249_artifactsubspanbridge05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v258_v249_artifactsubspanbridge05_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_artifact_local_bridge_head + branch_overlap_artifact_local_bridge_controller_head`
  (`395011 / 8747923`,
  `4.5155%`)
- Training start:
  `2026-04-01T17:51:47`
- Training end:
  `2026-04-01T17:55:29`
- Elapsed:
  `222.034s`
- Best validation checkpoint:
  epoch 4 with
  `best_val_loss = 0.298182`
- Final validation metrics at best epoch:
  - `val_artifact_local_bridge_teacher_waveform_extra_l1 = 0.000083`
  - `val_reconstruction_extra_waveform_l1 = 0.008684`
  - `val_reconstruction_extra_stft_l1 = 0.018042`
  - `val_extra_local_waveform_l1 = 0.001307`
  - `val_branch_protect_teacher_overlap_l1 = 0.000443`
  - `val_overlap_dual_residual_waveform_l1 = 0.004605`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001550`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001204`
  - `val_gate_keep_mean = 0.124413`
- Selector activity:
  - reconstruction extra `train 63 / 266, val 27 / 74`
  - overlap dual `train 66 / 266, val 14 / 74`
  - overlap dual extra `train 33 / 266, val 7 / 74`
  - absent extra `train 95 / 266, val 24 / 74`
  - branch protect teacher `train 120 / 266, val 27 / 74`

## Fixed Synthetic Checks relative `v249`

- Order:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`
- Result:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`

## Interval-Aware Real Probes relative `v249`

- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.1201 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.1080 dB`

## Synthetic Artifact-Subspan Read relative `v249`

- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +3.1363 dB`
  with
  `7 / 7`
  improvements

## Read

- The first important read is activation scope.
  The exact ties on the existing fixed synthetic five-pack and on
  `near_real_interval_leak_probe_v1`
  are not evidence that the new writer is harmless in general.
  Those assets do not activate the new
  `artifact_local_proxy`
  path in a meaningful way,
  so they are schema-dormant checks for this family.
- The second important read is family alignment.
  On the new synthetic artifact-subspan asset that exactly matches the new training branch,
  `v258`
  is strongly positive:
  `+3.1363 dB`
  and
  `7 / 7`
  improvements.
  So the writer and the new asset family are both real.
- But the active real artifact probes move in the wrong direction.
  Both the wider interval-aware artifact probe
  and the tighter
  `v3_subspan`
  artifact probe regress relative to
  `v249`.
  That means this new bridge is not repairing the current target-conditioned real artifact confound.
- The practical interpretation is not
  "the writer failed to learn anything."
  It is
  "the current synthetic artifact-subspan asset is not aligned enough to the real artifact target."

## Conclusion

- `v258`
  is a bounded negative first-launch read for the new dedicated artifact-side bridge family.
- Do not continue this family through:
  - the same
    `artifact_local_bridge_teacher_waveform_extra_weight`
    scalar
  - the same
    `branch_overlap_artifact_local_bridge_max_blend`
    scalar
  - the same synthetic artifact-subspan asset family alone
- If this line continues,
  the next step should change the training asset family or the target-conditioning mechanism,
  not micro-retune the same bridge on the same synthetic artifact-subspan teacher-anchor setup.
