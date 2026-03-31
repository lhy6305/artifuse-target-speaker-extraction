# 2026-03-31 local nonlocal shape constraint on top of `v240`: `v247` follow-up

## Summary

- Goal:
  test whether the mixed near-real failure of
  `v240`
  was mainly caused by the split-route
  `refine_base`
  local writer changing output shape outside the blocker windows.
- Route:
  start from
  `v240`,
  keep the split local writer unchanged
  (`local_prediction_source = estimated_waveform_refine_base`,
  `branch_overlap_refine_head` trainable),
  keep the keep-side teacher repair unchanged,
  and add a new
  `extra_local_nonlocal_waveform`
  term that aligns
  `local_prediction`
  back to
  `extra_prediction`
  on the complement of
  `local_proxy_intervals`.
- Smoke:
  `_smoke_v247_v240_refinebase_localnonlocal005_v1`
  passed,
  but the new term was already tiny:
  `val_extra_local_nonlocal_waveform_l1 = 0.000004`.
- Full:
  `v247`
  stayed training-real and synthetically strong versus
  `v157`,
  but it again behaved like a keep-heavy continuation relative to
  `v240`,
  not like a near-real repair.
- Verdict:
  the mixed near-real failure of
  `v240`
  is not explained by a simple nonlocal spill that can be repaired by low-weight
  local-to-keep complement alignment.
  This axis is bounded.

## Code Change

- Updated:
  `src/tse_prefix/pipeline/baseline_train.py`
  to add
  `extra_local_nonlocal_waveform_l1`
  and
  `extra_local_nonlocal_waveform_weight`,
  aligning
  `local_prediction`
  to
  `extra_prediction`
  on complement intervals.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose
  `--loss-extra-local-nonlocal-waveform-weight`
  and log the new metric in train and val summaries.
- Updated:
  `scripts/eval/eval_stft_mask_baseline.py`
  to export the new aggregate eval metric.
- Validation:
  `py_compile`
  passed before launch.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v247 = v240 + extra_local_nonlocal_waveform_weight 0.05`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v247_v240_refinebase_localnonlocal005_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v247_v240_refinebase_localnonlocal005_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T21:09:24`
- Training end:
  `2026-03-31T21:10:22`
- Elapsed:
  `57.856s`
- Final active metrics:
  - `val_loss = 0.298735`
  - `val_reconstruction_extra_waveform_l1 = 0.009594`
  - `val_reconstruction_extra_stft_l1 = 0.019927`
  - `val_extra_local_waveform_l1 = 0.001264`
  - `val_extra_local_nonlocal_waveform_l1 = 0.000003`
  - `val_pre_present_applied_delta_local_waveform_l1 = 0.001265`
  - `val_branch_protect_teacher_overlap_l1 = 0.000395`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001160`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.007318`
  - `val_gate_keep_mean = 0.124048`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`
  - branch protect teacher `train 87 / 233, val 20 / 67`

### Fixed Checks relative `v157`

- `+1.0801 / +0.5092 / +0.7440 / +0.4676 / +0.2413 dB`

### Fixed Checks relative `v240`

- `+0.8538 / +0.3305 / +0.4986 / +0.3915 / -0.2946 dB`

## Targeted Near-Real Probes relative `v240`

- `near_real_speech_probe_v1 = -0.0247 dB`
- `friend_raw = -0.0240 dB`
- `guodegang_raw = -0.0270 dB`
- `near_real_0003 / 0004 / 0006 = -0.0232 / -0.0247 / -0.0270 dB`
- `near_real_guodegang_transient_probe_v1 = -0.0270 dB`
- `guodegang_absent_480s = -0.0022 dB`
- `guodegang_anchor_120s = -0.0519 dB`

## Read

- The new term is not a plumbing no-op,
  but it is almost numerically silent.
  Even in smoke,
  `val_extra_local_nonlocal_waveform_l1`
  was only
  `0.000004`,
  and in full it stayed
  `0.000003`.
- The output shape is therefore not behaving like a branch with large nonlocal drift relative to the keep-side route.
  If it were,
  this term would have been materially larger before optimization.
- Relative
  `v240`,
  `v247`
  again buys stronger synthetic keep and abstention behavior
  while giving back active local-blocker gain.
  This is the same family shape already seen in
  `v245`
  and
  `v246`,
  not a new repair regime.
- The targeted near-real probes confirm that read.
  Both speech-family and guodegang-transient probes move slightly negative relative to
  `v240`,
  with the largest drag still on
  `guodegang_anchor_120s`.
- So the useful conclusion is structural:
  the remaining
  `v240`
  failure is not fixed by simply forcing
  `estimated_waveform_refine_base`
  to stay close to the keep-side output outside blocker windows.

## Conclusion

- `v247`
  is a bounded reject on top of
  `v240`.
- Do not continue this axis by micro-sweeping
  `extra_local_nonlocal_waveform_weight`
  by default.
- If the split-route
  `refine_base`
  family continues,
  the next branch should change local-writer application structure more materially,
  not add another low-weight complement alignment term against the same keep-side output.
