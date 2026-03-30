# 2026-03-30 dual gate-controller coupling on `v190`: `v201` follow-up

## Summary

- Goal:
  test whether the proven no-write dual auxiliary evidence from
  `v190`
  can safely affect output through
  `branch_overlap_dual_decoder_apply_mode = gate_controller`,
  instead of writing through either:
  - `branch_overlap_cancel_apply_controller`
  - `branch_overlap_cancel_pre_present_controller`
- I used the existing model path only.
  No new model code was needed for this run.
- `v201`
  changed the dual decoder from:
  - `apply_mode = current_output`
  - `gate_mode = complement`
  - `max_blend = 0.0`
  to:
  - `apply_mode = gate_controller`
  - `gate_mode = gate`
  - `max_blend = 0.02`
- The run was training-real on the intended local selector:
  `overlap_dual train 33 / 233, val 7 / 67`,
  and the dual residual path stayed non-trivial:
  final
  `val_overlap_dual_residual_waveform_l1 = 0.015890`.
- But the fixed synthetic outcome is immediate reject.
  Relative `v157`,
  the four non-blocker checks collapsed
  `-3.2598 / -2.4518 / -2.0349 / -1.8415 dB`,
  while
  `local_speech_leak_proxy_v1`
  improved
  `+0.7576 dB`.
- That shape is not just "similar to an older bad family".
  Direct
  `v188 -> v201`
  compare is practical tie on all five fixed proxies
  (`-0.0013 / -0.0011 / -0.0009 / -0.0000 / -0.0005 dB`).
- Verdict:
  this direct dual gate-controller route collapses into the same old
  `v188`
  family at active proxy resolution.
  So it does not provide a new disjoint selective regime.

## `v201`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v201_v190_dualgatecontroller_gateblend002_v1_ft1`
- Parent:
  initialized from
  `v190`
- Trainable:
  `branch_overlap_dual_decoder_temporal_model + branch_overlap_dual_decoder_head`
  (`2235650 / 7826316`,
  `28.5658%`)
- Training start:
  `2026-03-30T12:53:31`
- Training end:
  `2026-03-30T12:53:59`
- Elapsed:
  `28.002s`
- Active selector read:
  `overlap_dual train 33 / 233, val 7 / 67`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.015890`
  - `val_overlap_dual_residual_target_projection_ratio = 0.004111`

## `v201` Fixed Checks relative `v157`

- abstention `-3.2598 dB` (0 improved, 8 regressed of 8)
- same-gender keep `-2.4518 dB` (0 improved, 11 regressed of 11)
- hard-present keep `-2.0349 dB` (0 improved, 16 regressed of 16)
- artifact proxy `-1.8415 dB` (0 improved, 7 regressed of 7)
- local speech leak proxy `+0.7576 dB` (7 improved, 0 regressed of 7)

## `v201` Fixed Checks relative `v188`

- abstention `-0.0013 dB`
- same-gender keep `-0.0011 dB`
- hard-present keep `-0.0009 dB`
- artifact proxy `-0.0000 dB`
- local speech leak proxy `-0.0005 dB`
- Interpretation:
  practical tie.
  At the active proxy resolution,
  `v201`
  is not opening a new basin;
  it is reproducing the old
  `v188`
  failure family.

## Verdict

- The run is scientifically valid:
  selector coverage was restored,
  the dual residual route stayed non-trivial,
  and the checkpoint trained normally.
- But the direct
  `gate_controller`
  coupling route does not solve the branch boundary.
  It recreates the same old pattern:
  strong blocker gain bought by catastrophic keep or abstention regression.
- So the useful conclusion is not "gate_controller almost worked".
  The useful conclusion is:
  direct gate rewrite from the dual route is another old-family collapse.

## Next Step

- Do not keep sweeping this direct
  `gate_controller`
  family by default.
- If this branch continues,
  the next path should avoid direct gate rewrite through the existing
  `branch_decoder_frame_gate`
  output route.
