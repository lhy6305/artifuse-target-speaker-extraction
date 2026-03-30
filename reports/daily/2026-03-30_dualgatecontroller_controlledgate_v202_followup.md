# 2026-03-30 dual gate-controller controlled-gate supervision on `v190`: `v202` follow-up

## Summary

- Goal:
  test whether the
  `v201`
  failure was only a supervision disconnect.
  In
  `v201`,
  gate supervision was still attached to the frozen
  `branch_decoder_frame_gate`,
  not to the actual rewritten gate used by
  `branch_overlap_dual_decoder_apply_mode = gate_controller`.
- I fixed that boundary in code by:
  - explicitly exporting
    `branch_overlap_dual_controlled_gate`
    from the model when
    `gate_controller`
    mode is active
  - allowing train and eval to use
    `gate_supervision_source = overlap_dual_controlled_gate`
- `v202`
  is therefore the first run where gate supervision is genuinely attached to the trainable rewritten gate on this family.
- Training-side the fix is real:
  unlike
  `v201`,
  `gate_keep_mean`
  is now nonzero during training and validation,
  so the local gate supervision is no longer disconnected.
- But the output result is still practical tie to
  `v201`.
  Relative `v157`,
  the fixed synthetic deltas are
  `-3.2586 / -2.4507 / -2.0340 / -1.8415 / +0.7581 dB`,
  and direct
  `v201 -> v202`
  compare is only
  `+0.0013 / +0.0011 / +0.0009 / +0.0000 / +0.0005 dB`.
- Verdict:
  the
  `v201`
  collapse was not caused only by supervising the wrong tensor.
  Even after supervision is connected to the true controlled gate,
  the family still falls back into the same
  `v188`
  style regime.

## Code Change

- `src/tse_prefix/models/stft_mask_baseline.py`
  now exports
  `branch_overlap_dual_controlled_gate`
  whenever
  `branch_overlap_dual_decoder_apply_mode = gate_controller`.
- `scripts/train/train_stft_mask_baseline.py`
  now accepts
  `gate_supervision_source = overlap_dual_controlled_gate`
  and routes absent or keep gate losses onto the explicit controlled gate.
- `scripts/eval/eval_stft_mask_baseline.py`
  now resolves gate supervision metrics against the same source,
  so eval and train read the same tensor.

## `v202`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v202_v190_dualgatecontroller_controlledgate_v1_ft1`
- Parent:
  initialized from
  `v190`
- Trainable:
  `branch_overlap_dual_decoder_temporal_model + branch_overlap_dual_decoder_head`
  (`2235650 / 7826316`,
  `28.5658%`)
- Training start:
  `2026-03-30T13:08:12`
- Training end:
  `2026-03-30T13:08:38`
- Elapsed:
  `26.329s`
- Active selector read:
  `overlap_dual train 33 / 233, val 7 / 67`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.018536`
  - `val_overlap_dual_controller_distill_l1 = 0.326552`
  - `val_gate_keep_mean = 0.165753`
- Interpretation:
  the gate-supervision path is now genuinely connected,
  but that connection still does not change the fixed-output regime in a useful way.

## `v202` Fixed Checks relative `v157`

- abstention `-3.2586 dB` (0 improved, 8 regressed of 8)
- same-gender keep `-2.4507 dB` (0 improved, 11 regressed of 11)
- hard-present keep `-2.0340 dB` (0 improved, 16 regressed of 16)
- artifact proxy `-1.8415 dB` (0 improved, 7 regressed of 7)
- local speech leak proxy `+0.7581 dB` (7 improved, 0 regressed of 7)

## `v202` Fixed Checks relative `v201`

- abstention `+0.0013 dB`
- same-gender keep `+0.0011 dB`
- hard-present keep `+0.0009 dB`
- artifact proxy `+0.0000 dB`
- local speech leak proxy `+0.0005 dB`
- Interpretation:
  practical tie.
  Connecting gate supervision to the correct tensor does not open a different basin.

## Verdict

- `v201`
  was not invalid.
  Its failure shape was already scientifically meaningful.
- `v202`
  removes the remaining ambiguity:
  the direct dual gate-controller family is still bad
  even when the gate loss is attached to the real controlled gate.
- So this family is now fully closed through
  `v202`.

## Next Step

- Do not continue direct dual gate rewrite through the existing
  `branch_decoder_frame_gate`
  path,
  even with explicit controlled-gate supervision.
- If this branch continues,
  the next route should avoid direct gate rewrite entirely
  and use a different output application mechanism.
