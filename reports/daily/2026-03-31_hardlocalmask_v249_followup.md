# 2026-03-31 hard local-interval application split on top of `v240`: `v249` follow-up

## Summary

- Goal:
  test whether the mixed near-real failure of
  `v240`
  was mainly caused by the split-route
  `refine_base`
  local writer still applying outside blocker windows,
  and whether a hard output split could repair that without adding new losses.
- Route:
  start from
  `v240`,
  keep all losses, selectors, and trainable prefixes unchanged,
  and replace the final output with a hard interval split:
  outside
  `local_proxy_intervals`
  the output is forced to
  `estimated_waveform_post_pre_present_controller`,
  and only inside blocker windows can
  `estimated_waveform_refine_base`
  write through.
- Smoke:
  `_smoke_v249_v240_hardlocalmask_v1`
  passed.
  A quick blocker-only compare against
  `v240`
  immediately showed the route was not a no-op:
  `local_speech_leak_proxy_v1 = +0.5999 dB`
  with
  `7 / 7`
  improved samples.
- Full:
  `v249`
  is not promotion-safe on fixed synthetic proxies:
  relative
  `v240`,
  four non-blocker checks regressed
  while the active blocker improved.
  But unlike the earlier synthetic-heavy continuations,
  both targeted near-real probes moved strongly positive,
  and every probe sample improved.
- Verdict:
  `v249`
  is not a bounded reject.
  It is the first split-route
  `refine_base`
  continuation whose fixed synthetic surface is clearly worse than
  `v240`
  while its targeted near-real blocker probes are clearly better.
  That makes it a new real-side evidence point,
  but not an automatic base candidate.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add
  `enable_branch_overlap_refine_local_hard_mask`,
  accept
  `local_proxy_intervals`
  in
  `forward`,
  build a waveform-domain hard interval mask,
  export
  `estimated_waveform_split_localmasked`,
  and replace
  `estimated_waveform`
  with the hard split output when the flag is enabled.
- Updated:
  `src/tse_prefix/data/synthetic_dataset.py`
  to expose
  `compute_local_proxy_intervals`
  for eval and export tooling.
- Updated:
  `src/tse_prefix/pipeline/runtime_helpers.py`
  to recognize
  `estimated_waveform_split_localmasked`
  as a named prediction source.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose
  `--model-enable-branch-overlap-refine-local-hard-mask`,
  wire the new config field,
  and pass
  `local_proxy_intervals`
  into model and teacher forward calls.
- Updated:
  `scripts/eval/eval_stft_mask_baseline.py`,
  `scripts/eval/compare_checkpoints_on_manifest.py`,
  `scripts/eval/export_ab_listening_pack.py`,
  `scripts/eval/export_ab_inference_from_manifest.py`,
  and
  `scripts/eval/rank_checkpoints_on_silence_over_leak_manifest.py`
  so interval-aware checkpoints actually receive
  `local_proxy_intervals`
  at inference time when available.
- Validation:
  `py_compile`
  passed after the code changes.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v249 = v240 + hard local-interval application split`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v249_v240_hardlocalmask_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T21:54:22`
- Training end:
  `2026-03-31T21:57:20`
- Elapsed:
  `177.693s`
- Best validation checkpoint:
  epoch 4 with
  `best_val_loss = 0.298731`
- Final validation metrics at best epoch:
  - `val_reconstruction_extra_waveform_l1 = 0.009592`
  - `val_reconstruction_extra_stft_l1 = 0.019927`
  - `val_extra_local_waveform_l1 = 0.001263`
  - `val_extra_local_nonlocal_waveform_l1 = 0.000004`
  - `val_pre_present_applied_delta_local_waveform_l1 = 0.001266`
  - `val_branch_protect_teacher_overlap_l1 = 0.000404`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.125960`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.007246`
  - `val_gate_keep_mean = 0.124125`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `-0.2838 / -0.9162 / -0.2869 / -0.8587 / +0.8562 dB`

### Fixed Checks relative `v240`

- `-0.5101 / -1.0948 / -0.5323 / -0.9349 / +0.3203 dB`

## Targeted Near-Real Probes relative `v240`

- `near_real_speech_probe_v1 = +0.7692 dB`
- `friend_raw = +0.9288 dB`
- `guodegang_raw = +0.2902 dB`
- `near_real_0003 / 0004 / 0006 = +0.9038 / +0.9538 / +0.2902 dB`
- `near_real_guodegang_transient_probe_v1 = +0.2902 dB`
- `friend_absent_820s = +0.8891 dB`
- `guodegang_anchor_120s = +0.2884 dB`

## Targeted Near-Real Probes relative `v157`

- `near_real_speech_probe_v1 = +0.9220 dB`
- `near_real_guodegang_transient_probe_v1 = +0.2293 dB`

## Read

- This route is neither a no-op nor a standard synthetic tradeoff continuation.
  The smoke sanity check already showed a large blocker-only move,
  and full keeps that direction.
- But the synthetic shape flips relative to
  `v240`.
  The hard output split buys blocker quality
  while clearly giving back abstention, same-gender keep, hard-present keep, and artifact.
  So by the usual fixed synthetic gate,
  this is not a promotion candidate.
- The real-side read is the opposite.
  On the targeted near-real probe family the route is uniformly positive:
  `24 / 24`
  improvements on the full speech probe and
  `6 / 6`
  improvements on the guodegang transient probe.
  Both the previously strong
  `friend_raw`
  side and the previously difficult
  `guodegang_raw / transient_like`
  side move in the correct direction.
- That contrast is important.
  The old split-route
  `v240`
  family was failing near-real because the local writer and keep route still shared downstream application.
  The hard interval split is the first evidence that this downstream application issue was real.
- But there is also a validation limit:
  the whole
  `near_real_v1`
  real-eval manifest does not carry
  `local_proxy`
  annotations.
  So for interval-masked routes like
  `v249`,
  the old whole-pack export is not a decisive gate,
  because the hard split would not be activated there in the same way.

## Conclusion

- `v249`
  is a new probe-positive real-side evidence point on top of
  `v240`,
  not a bounded reject.
- It should not replace
  `v157`
  as the active automatic base,
  because four active fixed synthetic guardrails are materially negative relative to both
  `v157`
  and
  `v240`.
- If this family continues,
  the next validation step should use interval-aware real assets
  or a probe-side listening pack,
  not the old whole
  `near_real_v1`
  pack without
  `local_proxy`
  annotations.
