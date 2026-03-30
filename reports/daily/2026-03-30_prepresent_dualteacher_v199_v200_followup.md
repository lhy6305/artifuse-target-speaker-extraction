# 2026-03-30 pre-present dual-teacher bridge on `v190`: `v199` to `v200` follow-up

## Summary

- Goal:
  test whether the proven no-write dual auxiliary evidence from
  `v190`
  can safely steer output through
  `branch_overlap_cancel_pre_present_controller`
  instead of the already-bounded pure apply-controller route.
- I first generalized the controller-distill plumbing so the same loss can target either:
  - `branch_overlap_cancel_apply_controller`
  - `branch_overlap_cancel_pre_present_controller`
- `v199`
  is the first live pre-present dual-teacher run.
  It is training-real:
  final
  `val_overlap_dual_controller_distill_l1 = 0.008762`.
  But relative `v157`,
  it is still practical near-no-op on the fixed proxy set:
  abstention
  `+0.0101 dB`,
  same-gender keep
  `+0.0049 dB`,
  hard-present keep
  `+0.0045 dB`,
  artifact proxy
  `+0.0034 dB`,
  local speech leak proxy
  `-0.0079 dB`.
- `v200`
  widened the trainable set by jointly unfreezing
  `branch_overlap_cancel_head`
  with the same pre-present controller.
  Training-side it stayed effectively identical to
  `v199`:
  the final
  `val_overlap_dual_controller_distill_l1`
  is again
  `0.008762`.
- Fixed synthetic checks confirm that
  `v200`
  is not just "similar" to
  `v199`;
  it is exact tie at the active proxy resolution.
  Relative `v157`,
  all five deltas are identical to
  `v199`,
  and direct
  `v199 -> v200`
  compare is
  `0.0 dB`
  on all five fixed proxies.
- Verdict:
  the pre-present dual-teacher family is now also bounded.
  It is safer than the pure apply-controller teacher-bridge family,
  but it collapses into a near-no-op regime,
  and the obvious local widening
  (`branch_overlap_cancel_head + pre-present controller`)
  does not reopen a useful basin.

## Code Change

- Added
  `overlap_dual_controller_distill_source`
  plumbing so controller distill can explicitly read either:
  - `overlap_cancel_apply_controller`
  - `overlap_cancel_pre_present_controller`
- This was implemented in:
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `src/tse_prefix/pipeline/runtime_helpers.py`
- The train and eval entries now resolve the requested prediction tensor explicitly,
  instead of hard-coding the distill target to
  `branch_overlap_cancel_apply_controller`.

## `v199`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v199_v190_prepresent_dualteacher_v1_ft1`
- Parent:
  initialized from
  `v190`
- Trainable:
  `branch_overlap_cancel_pre_present_controller_head`
  only
  (`131585 / 7957901`,
  `1.6535%`)
- Training start:
  `2026-03-30T12:14:06`
- Training end:
  `2026-03-30T12:14:29`
- Elapsed:
  `22.531s`
- Final active metric:
  `val_overlap_dual_controller_distill_l1 = 0.008762`
- Interpretation:
  the pre-present route can receive the teacher signal,
  but it collapses toward a safe almost-no-write regime instead of moving the blocker.

## `v199` Fixed Checks relative `v157`

- abstention `+0.0101 dB` (0 improved, 0 regressed of 8)
- same-gender keep `+0.0049 dB` (0 improved, 0 regressed of 11)
- hard-present keep `+0.0045 dB` (0 improved, 0 regressed of 16)
- artifact proxy `+0.0034 dB` (0 improved, 0 regressed of 7)
- local speech leak proxy `-0.0079 dB` (0 improved, 0 regressed of 7)

## `v200`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v200_v199_prepresent_dualteacher_jointcancel_v1_ft1`
- Parent:
  initialized from
  `v190`
  with the same pre-present teacher-bridge path as
  `v199`
- Trainable:
  `branch_overlap_cancel_head + branch_overlap_cancel_pre_present_controller_head`
  (`395011 / 7957901`,
  `4.9638%`)
- Training start:
  `2026-03-30T12:15:58`
- Training end:
  `2026-03-30T12:16:20`
- Elapsed:
  `22.132s`
- Final active metric:
  `val_overlap_dual_controller_distill_l1 = 0.008762`

## `v200` Fixed Checks relative `v157`

- abstention `+0.0101 dB`
- same-gender keep `+0.0049 dB`
- hard-present keep `+0.0045 dB`
- artifact proxy `+0.0034 dB`
- local speech leak proxy `-0.0079 dB`

## `v200` Fixed Checks relative `v199`

- abstention `0.0 dB`
- same-gender keep `0.0 dB`
- hard-present keep `0.0 dB`
- artifact proxy `0.0 dB`
- local speech leak proxy `0.0 dB`
- Interpretation:
  joint cancel-head unfreeze did not reopen the route at all.
  At the active proxy resolution,
  `v200`
  lands in exact tie to
  `v199`.

## Verdict

- The generalized controller-distill source plumbing works.
  The new family was not blocked by missing code.
- But the pre-present write-back location behaves differently from the pure apply-controller family:
  - apply-controller dual-teacher can move the blocker,
    but it burns guardrail margin
  - pre-present dual-teacher preserves guardrails,
    but collapses into near-no-op
- So the problem is no longer "find the safer write-back location".
  The problem is "find a coupling path that is both selective and expressive enough to move the blocker."

## Next Step

- Do not keep sweeping head-only or joint-cancel variants on this same pre-present dual-teacher family.
- If this branch continues,
  the next attempt should be a materially more disjoint coupling path,
  not another small local widening around
  `branch_overlap_cancel_pre_present_controller`
  or
  `branch_overlap_cancel_head`.
