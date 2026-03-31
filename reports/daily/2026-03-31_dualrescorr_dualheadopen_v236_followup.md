# 2026-03-31 upstream dual residual predictor widening on the writable residual-correction branch: `v236` follow-up

## Summary

- Goal:
  test whether the remaining ceiling on the
  `v224`
  family mainly came from a frozen upstream dual residual predictor rather than from the already-tested local objective terms.
- Route:
  keep the full
  `v224`
  loss unchanged,
  and widen only the trainable set by adding
  `branch_overlap_dual_decoder_head`
  on top of
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`.
- Implementation:
  no code change.
  This was a command-only continuation.
- Smoke:
  `_smoke_v236_v224_dualrescorr_dualheadopen_v1`
  passed and confirmed the wider trainable set launched cleanly.
- Full:
  `v236`
  was training-real,
  but fixed-proxy behavior remained the same mild guardrail-for-local tradeoff surface rather than opening a new blocker-positive regime.
- Verdict:
  simple upstream widening through
  `branch_overlap_dual_decoder_head`
  does not rescue the writable residual-correction family.
  This axis can be closed.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v236 = v224 + branch_overlap_dual_decoder_head`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v236_v224_dualrescorr_dualheadopen_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v236_v224_dualrescorr_dualheadopen_v1_ft1`
- Trainable:
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_decoder_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T12:05:10`
- Training end:
  `2026-03-31T12:05:56`
- Elapsed:
  `46.555s`
- Final active metrics:
  - `val_loss = 0.256490`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020713`
  - `val_overlap_dual_residual_waveform_l1 = 0.004751`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001554`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.111711`
  - `val_gate_keep_mean = 0.107056`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0371 / -0.0335 / -0.0133 / -0.0282 / +0.0478 dB`

### Fixed Checks relative `v224`

- `-0.0320 / -0.0320 / -0.0163 / -0.0203 / +0.0323 dB`

## Read

- The continuation is clearly optimization-real.
  The wider trainable set launches cleanly,
  overlap-dual selector activity stays unchanged,
  and the trainable fraction rises from the
  `v224`
  family to
  `9.4580%`.
- But output-side it does not change the family shape in a useful way.
  Relative
  `v224`,
  all four non-blocker checks regress slightly,
  while the active local blocker improves slightly.
- Relative
  `v157`,
  the route stays in the same near-tie basin:
  four checks are mildly negative,
  and only
  `local_speech_leak_proxy_v1`
  turns mildly positive.
- So this is not evidence that the
  `v224`
  ceiling was mainly caused by freezing the upstream dual predictor.
  It looks more like a small steepening of the same already-mapped tradeoff surface.

## Conclusion

- The first upstream dual residual predictor widening on the writable residual-correction branch is now bounded.
- Do not keep widening the same
  `v224`
  family only by unfreezing
  `branch_overlap_dual_decoder_head`
  by default.
- If this family continues,
  the next route should change the writable path or the local objective more structurally,
  not just expose a broader upstream predictor to the same residual-correction write-back.
