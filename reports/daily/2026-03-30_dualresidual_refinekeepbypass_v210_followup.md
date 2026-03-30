# 2026-03-30 dual residual-correction prerefine keep-bypass on `v206`: `v210` follow-up

## Summary

- Goal:
  test the first dual residual-correction continuation whose keep-preserve loss is disjoint in trainable path,
  not only in selector semantics.
- `v210 = v206 + prerefine keep-bypass on pre-dual output`
  used a new keep path through
  `branch_overlap_refine_head`
  while local supervision still targeted the
  dual residual-correction heads.
- Smoke validation was successful:
  the new prerefine bypass output was live,
  the keep selector was active,
  and the local selector was still active.
- Full training was also real:
  reconstruction selector coverage stayed
  `train 63 / 233, val 27 / 67`,
  overlap-dual coverage stayed
  `train 33 / 233, val 7 / 67`,
  and the new pre-dual keep path produced nonzero validation metrics.
- But fixed synthetic evaluation is again catastrophic.
  Relative both
  `v157`
  and
  `v206`,
  all five active fixed proxies regressed strongly,
  and every sample in every fixed proxy manifest regressed.
- Verdict:
  disjoint trainable modules alone are not enough.
  If keep-preserve and local supervision still couple through the same downstream branch behavior,
  the route can still collapse globally.

## Code Plumbing Used By This Run

- `src/tse_prefix/models/stft_mask_baseline.py`
  now exports
  `estimated_waveform_pre_dual_residual_correction`
  so a keep loss can attach before the dual residual-correction write-back.
- `src/tse_prefix/pipeline/runtime_helpers.py`
  now supports
  `extra_prediction_source`
  and resolves
  `estimated_waveform_pre_dual_residual_correction`
  as a valid extra-supervision target.
- `scripts/train/train_stft_mask_baseline.py`
  now supports:
  - `--loss-extra-prediction-source`
  - `--loss-use-branch-prerefine-as-primary-prediction`
  and wires the selected extra prediction through both train and validation loss computation.
- `py_compile`
  passed on the changed files before launch.

## `v210 = v206 + disjoint prerefine keep-bypass`

- Parent:
  `v206`
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v210_v206_dualresidualcorr_refinekeepbypass_v1_ft1/best.pt`
- Init checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v206_v190_dualresidualcorrection_blend002_v1_ft1/best.pt`
- New keep path:
  reconstruction-extra on
  `estimated_waveform_pre_dual_residual_correction`
  with
  `loss_use_branch_prerefine_as_primary_prediction = true`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`658437 / 8221327`,
  `8.0089%`)
- Training start:
  `2026-03-30T21:08:50`
- Training end:
  `2026-03-30T21:09:30`
- Elapsed:
  `40.282s`
- Best val loss:
  `0.274057`

## Smoke Validation

- Smoke output:
  `_smoke_v210_v206_dualresidualcorr_refinekeepbypass_v1`
- Smoke start:
  `2026-03-30T21:04:57`
- Smoke end:
  `2026-03-30T21:05:01`
- Smoke elapsed:
  `4.823s`
- Smoke selector evidence:
  - reconstruction `train 16 / 80, val 27 / 67`
  - reconstruction-extra `train 16 / 80, val 27 / 67`
  - overlap-dual `train 13 / 80, val 7 / 67`
- Smoke route evidence:
  - `val_reconstruction_extra_waveform_l1 = 0.023048`
  - `val_reconstruction_extra_stft_l1 = 0.073691`
  - `val_overlap_dual_residual_waveform_l1 = 0.015926`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.005295`
  - `val_gate_keep_mean = 0.353424`

## Final Training Evidence

- Final active metrics:
  - `val_reconstruction_extra_waveform_l1 = 0.014815`
  - `val_reconstruction_extra_stft_l1 = 0.045874`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001671`
  - `val_overlap_dual_controller_distill_l1 = 0.095253`
  - `val_gate_keep_mean = 0.118114`
- Selector coverage:
  - reconstruction `train 63 / 233, val 27 / 67`
  - reconstruction-extra `train 63 / 233, val 27 / 67`
  - overlap-dual `train 33 / 233, val 7 / 67`
- Interpretation:
  the pre-dual keep-bypass path is genuinely active.
  This is not a selector omission,
  a missing-plumbing no-op,
  or a launch failure.

## Fixed Checks Relative `v157`

- abstention `-14.0317 dB`
- same-gender keep `-9.5738 dB`
- hard-present keep `-11.9342 dB`
- artifact proxy `-14.4076 dB`
- local speech leak proxy `-5.8259 dB`

## Fixed Checks Relative `v206`

- abstention `-14.0152 dB`
- same-gender keep `-9.5660 dB`
- hard-present keep `-11.9260 dB`
- artifact proxy `-14.3997 dB`
- local speech leak proxy `-5.8348 dB`

## Failure Shape

- This is not a local-versus-guardrail tradeoff.
- The local blocker also regressed heavily.
- Every sample in every fixed proxy manifest regressed:
  - abstention `8 / 8`
  - same-gender keep `11 / 11`
  - hard-present keep `16 / 16`
  - artifact proxy `7 / 7`
  - local speech leak proxy `7 / 7`

## Conclusion

- `v210`
  closes the first trainable-path-disjoint keep-bypass continuation on the
  dual residual-correction family.
- It proves a stricter boundary than
  `v209`:
  trainable-path disjointness by itself is not enough.
  If keep-preserve and local supervision still couple through the same downstream branch behavior,
  the whole route can still collapse.
- So the next valid continuation should not reuse this prerefine keep-bypass pattern.
  Any next branch must be disjoint both:
  - in trainable path
  - in downstream output application or control path
