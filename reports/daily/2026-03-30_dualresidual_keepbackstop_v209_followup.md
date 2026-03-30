# 2026-03-30 dual residual-correction keep-backstop on `v206`: `v209` follow-up

## Summary

- Goal:
  test the first command-only continuation after
  `v206 / v207 / v208`
  by adding a weak keep-preserve backstop on keep-critical samples,
  without scaling the same local blend again.
- `v209 = v206 + branch_protect overlap-base-align on gate_keep_union_v2`
  is training-real:
  both selectors stayed active,
  with
  `overlap_dual train 33 / 233, val 7 / 67`
  and
  `branch_protect train 63 / 233, val 27 / 67`,
  and final
  `val_branch_protect_overlap_base_align_l1 = 0.015515`.
- But fixed synthetic evaluation is catastrophic.
  Relative both
  `v157`
  and
  `v206`,
  all five active fixed proxies regressed strongly,
  and every sample in each fixed proxy manifest regressed.
- Verdict:
  this does not behave like a small guardrail-recovery regularizer.
  A weak keep-preserve loss applied directly to the same
  dual residual-correction heads
  is a collapse route,
  not a selective continuation.

## `v209 = v206 + weak keep backstop on gate_keep_union_v2`

- Parent:
  `v206`
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v209_v206_dualresidualcorr_keepalign001_v1_ft1/best.pt`
- Init checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v206_v190_dualresidualcorrection_blend002_v1_ft1/best.pt`
- New selector:
  `data/synthetic/sample_ids_gate_keep_union_v2_all.txt`
- New loss:
  `branch_protect_overlap_base_align_weight = 0.01`
- Trainable:
  still
  `branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`395011 / 8221327`,
  `4.8047%`)
- Training start:
  `2026-03-30T20:47:59`
- Training end:
  `2026-03-30T20:48:23`
- Elapsed:
  `24.097s`
- Best val loss:
  `0.734337`

## Smoke Validation

- Smoke output:
  `_smoke_v209_v206_dualresidualcorr_keepalign_v1`
- Smoke start:
  `2026-03-30T20:46:56`
- Smoke end:
  `2026-03-30T20:47:01`
- Smoke elapsed:
  `4.71s`
- Smoke selector evidence:
  - `overlap_dual train 13 / 80, val 7 / 67`
  - `branch_protect train 16 / 80, val 27 / 67`
- Smoke route evidence:
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.004909`
  - `val_branch_protect_overlap_base_align_l1 = 0.015515`

## Final Training Evidence

- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.015926`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.004909`
  - `val_branch_protect_overlap_base_align_l1 = 0.015515`
  - `val_gate_keep_mean = 0.351832`
- Selector coverage:
  - `overlap_dual train 33 / 233, val 7 / 67`
  - `branch_protect train 63 / 233, val 27 / 67`
- Interpretation:
  the branch-protect loss is genuinely active.
  This is not a launch failure,
  a selector omission,
  or a missing-loss no-op.

## Fixed Checks relative `v157`

- abstention `-16.4520 dB`
- same-gender keep `-9.0633 dB`
- hard-present keep `-13.4505 dB`
- artifact proxy `-15.2722 dB`
- local speech leak proxy `-5.9793 dB`

## Fixed Checks relative `v206`

- abstention `-16.4355 dB`
- same-gender keep `-9.0555 dB`
- hard-present keep `-13.4424 dB`
- artifact proxy `-15.2642 dB`
- local speech leak proxy `-5.9881 dB`

## Failure Shape

- This is not a simple guardrail-versus-local tradeoff.
- All five active fixed proxies moved the wrong way.
- Every sample in every fixed proxy manifest regressed:
  - abstention `8 / 8`
  - same-gender keep `11 / 11`
  - hard-present keep `16 / 16`
  - artifact proxy `7 / 7`
  - local speech leak proxy `7 / 7`

## Conclusion

- `v209`
  closes the first same-head keep-backstop continuation on the
  dual residual-correction family.
- Even a weak
  `branch_protect_overlap_base_align`
  term on keep-critical samples
  can destabilize the route when it backpropagates through the same
  residual-correction write-back heads.
- So the next valid continuation should not reuse this keep-backstop pattern.
  If keep preservation is added to the dual residual-correction line,
  it must be disjoint in trainable path as well as sample semantics.
