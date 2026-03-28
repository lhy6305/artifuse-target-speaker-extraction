# 2026-03-28 parallel pre-present joint cancel-head on `v172`: `v176` follow-up

## Summary

- Goal:
  test the first post-
  `v175`
  route that actually changes the decision source rather than only reweighting the same frozen
  pre-present controller head.
- `v176 = v172 + jointly unfreeze branch_overlap_cancel_head`
  is training-real but still practical no-op at output level.
- So the new boundary is:
  even jointly unfreezing the local overlap-cancel head with the pre-present controller is not enough to move this family in a meaningful way.

## `v176 = v172 + jointly unfreeze branch_overlap_cancel_head`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v176_v172_parallel_prepresent_jointcancelhead_v1_ft1`
- Init:
  `v172`
  best checkpoint, with teacher metadata fallback disabled
- Model / loss semantics:
  same as
  `v172`
  otherwise;
  only the trainable set is expanded
- Trainable set:
  - `branch_overlap_cancel_pre_present_controller_head`
  - `branch_overlap_cancel_head`
- Intent:
  stop assuming the frozen controller head alone can discover the missing selectivity,
  and let the overlap-cancel branch itself move jointly with the controller.
- Selector coverage stays unchanged:
  `overlap_cancel train 33 / 233, val 7 / 67`
- Training signal is real:
  final
  `train_gate_pre_present_keep_mean = 0.0118`
  /
  `val_gate_pre_present_keep_mean = 0.0063`
  and
  `train_gate_pre_present_abstain_mean = 0.3955`
  /
  `val_gate_pre_present_abstain_mean = 0.2612`,
  so this is not a training-side no-op.

### Fixed Checks relative `v157`

- abstention `+0.0660 dB`
- same-gender keep `+0.0348 dB`
- hard-present keep `+0.0289 dB`
- artifact proxy `+0.0221 dB`
- local speech leak proxy `-0.0537 dB`

### Direct Comparison relative `v172`

- local speech leak proxy:
  `-4.47e-05 dB`
- abstention proxy:
  `+7.91e-05 dB`

### Verdict

- `v176`
  is the first larger-path joint-unfreeze continuation on top of
  `v172`,
  but it still does not move inference in a meaningful way.
- Therefore
  `pre-present controller + branch_overlap_cancel_head`
  joint unfreeze is a practical no-op route and does not warrant near-real evaluation.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  only as the mechanism-positive evidence point for this family.
- Close as non-continuations:
  - `v174`:
    controller floor
  - `v175`:
    outside-overlap abstain supervision
  - `v176`:
    joint unfreeze of
    `branch_overlap_cancel_head`
    with the pre-present controller

## Next Step

- Do not continue:
  - `pre_present_controller_floor`
  - same-head
    outside-overlap abstain
    reweight / sweep
  - `branch_overlap_cancel_head + pre-present controller`
    joint unfreeze
- If this branch continues,
  it should stop assuming that modest local unfreezing around the same
  overlap-cancel branch
  will be enough.
  The next valid move is to either:
  - change the supervision target more explicitly for the total-risk path, or
  - jointly unfreeze a materially larger pre-present apply path than the current
    controller + cancel-head pair.
