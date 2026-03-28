# 2026-03-28 parallel pre-present total-risk selectivity on `v172`: `v174 / v175` follow-up

## Summary

- Goal:
  improve selectivity of the
  `v172`
  parallel pre-present total-risk controller without falling back to simple
  `max_blend`
  shrinkage.
- `v174 = v172 + pre_present_controller_floor 0.1`
  is a practical no-op.
- `v175 = v172 + outside-overlap abstain supervision 1.0`
  is also a practical no-op.
- So the new boundary is:
  neither post-sigmoid sparsification nor same-head
  outside-overlap negative supervision is enough to move this route.

## `v174 = v172 + pre_present_controller_floor 0.1`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v174_v172_parallel_prepresent_totalrisk_controller_floor01_v1_ft1`
- New code support:
  `branch_overlap_cancel_pre_present_controller_floor`
- Intent:
  zero low-confidence controller activity while preserving strong peaks,
  so this changes selectivity rather than global amplitude.
- Training signal does respond:
  final
  `val_gate_pre_present_keep_mean`
  drops from
  `0.0542`
  in
  `v172`
  to
  `0.0069`.

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
  `+7.92e-05 dB`

### Verdict

- `v174`
  changes controller statistics but not model output.
- Therefore
  `pre_present_controller_floor`
  is a practical no-op route and stops here.

## `v175 = v172 + outside-overlap abstain supervision 1.0`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v175_v172_parallel_prepresent_totalrisk_controller_outsideabstain1p0_v1_ft1`
- New code support:
  - `gate_pre_present_abstain_weight`
  - complement-interval builder for
    `target_overlap_intervals`
  - train/eval metrics:
    `gate_pre_present_abstain_mean`
- Intent:
  keep the same pre-present controller head,
  but explicitly punish activation outside overlap windows on the same selected samples.
- Training signal is real:
  final
  `val_gate_pre_present_keep_mean = 0.0424`
  and
  `val_gate_pre_present_abstain_mean = 0.0695`
  are both non-zero.

### Fixed Checks relative `v157`

- abstention `+0.0660 dB`
- same-gender keep `+0.0348 dB`
- hard-present keep `+0.0289 dB`
- artifact proxy `+0.0221 dB`
- local speech leak proxy `-0.0537 dB`

### Direct Comparison relative `v172`

- local speech leak proxy:
  `-2.35e-05 dB`
- abstention proxy:
  `+1.22e-04 dB`

### Verdict

- `v175`
  proves that adding same-head
  outside-overlap negative supervision
  is still not enough to move inference in a meaningful way.
- So this route is also a practical no-op and does not warrant near-real evaluation.

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

## Next Step

- Do not continue:
  - `pre_present_controller_floor`
  - same-head
    outside-overlap abstain
    reweight / sweep
- If this branch continues,
  it should stop assuming the frozen pre-present controller head alone can learn the missing selectivity.
  The next valid move is to change the decision source itself:
  either unfreeze a larger path jointly with the controller,
  or provide a more explicit total-risk target than the current same-head keep/abstain formulation.
