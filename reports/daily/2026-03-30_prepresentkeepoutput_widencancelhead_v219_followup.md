# 2026-03-30 pre-present keep-output path widening with `branch_overlap_cancel_head`: `v219` follow-up

## Summary

- Goal:
  test the first true keep-path widening on top of the safer
  `v212`
  family,
  without changing losses,
  by expanding the trainable keep route from:
  - `branch_overlap_cancel_pre_present_controller_head`
  - `branch_overlap_dual_residual_correction_head`
  - `branch_overlap_dual_residual_correction_controller_head`
  to also include:
  - `branch_overlap_cancel_head`
- This run was training-real:
  the reconstruction selector stayed active
  (`train 63 / 233, val 27 / 67`),
  the overlap-dual selector stayed active
  (`train 33 / 233, val 7 / 67`),
  and several keep-route val metrics moved materially relative to
  `v212`,
  especially
  `val_overlap_cancel_target_projection_ratio`
  and
  `val_transient_extra_presence_l1`.
- Output-side the result is not selective.
  It is a steep tradeoff:
  four guardrails improve strongly,
  while the active local blocker regresses clearly.
- Verdict:
  do not continue the simple
  `+ branch_overlap_cancel_head`
  widening axis on this same disjoint-downstream family.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v219 = v212 + widen keep path with branch_overlap_cancel_head`

- Smoke:
  `_smoke_v219_v212_prepresentkeepoutput_widencancelhead_v1`
  passed.
  The widened trainable set was live and the keep-route validation metrics were no longer tied to
  `v212`.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v219_v212_prepresentkeepoutput_widencancelhead_v1_ft1`
- Trainable:
  `branch_overlap_cancel_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-30T22:34:25`
- Training end:
  `2026-03-30T22:35:03`
- Elapsed:
  `38.515s`
- Final active metrics:
  - `val_loss = 0.269321`
  - `val_reconstruction_extra_waveform_l1 = 0.009650`
  - `val_reconstruction_extra_stft_l1 = 0.020594`
  - `val_overlap_cancel_waveform_l1 = 0.059909`
  - `val_overlap_cancel_target_projection_ratio = 0.001015`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

## Fixed Checks

### Relative `v157`

- `+0.6402 / +0.2737 / +0.5885 / +0.2581 / -0.0907 dB`

### Relative `v212`

- `+0.6713 / +0.2892 / +0.6024 / +0.2629 / -0.0913 dB`

## Interpretation

- This is not a practical tie.
  The widened keep path has real output leverage.
- But it does not improve selectivity.
  It pushes strongly in the old direction:
  better keep or abstention guardrails,
  worse local blocker.
- The shape is much steeper than the milder exchange surface seen in
  `v212`,
  `v217`,
  and
  `v218`.
- So adding
  `branch_overlap_cancel_head`
  does increase expression,
  but it increases the keep-versus-local coupling rather than resolving it.

## Conclusion

- `v219`
  closes the first keep-path-widening axis on the disjoint downstream family.
- If this branch continues,
  do not keep widening the same pre-present keep path by simply adding more modules that still write through the same cancel estimate.
- The next step must either:
  - use a qualitatively different keep path on the same disjoint downstream route
  - or change the local objective rather than only increasing keep-route capacity
