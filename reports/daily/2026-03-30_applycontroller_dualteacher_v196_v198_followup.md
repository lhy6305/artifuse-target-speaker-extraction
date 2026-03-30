# 2026-03-30 apply-controller dual-teacher bridge on `v190`: `v196` to `v198` follow-up

## Summary

- Goal:
  test whether the proven no-write dual auxiliary evidence from
  `v190`
  can safely steer a separate output-writing route by distilling
  `branch_overlap_cancel_apply_controller`
  toward
  `branch_overlap_dual_controller`
  on the active blocker windows.
- `v196`
  first showed a semantics gap, not a scientific outcome:
  under the active
  `current_output`
  no-write dual setup,
  `branch_overlap_dual_controller`
  was not emitted,
  so the intended teacher bridge was exact no-op.
- I fixed that boundary in code by always materializing
  `branch_overlap_dual_controller`
  whenever the dual residual path exists,
  and by making optional monitor or distill losses safe when their tensors are absent.
- `v197`
  is therefore the first live version of the family.
  It is training-real:
  final
  `val_overlap_dual_controller_distill_l1 = 0.113235`.
  It also becomes the first pure apply-controller continuation on top of
  `v190`
  that moves the blocker the right way:
  `local_speech_leak_proxy_v1 +0.1082 dB`.
- But `v197`
  pays for that blocker gain by regressing all four fixed keep or abstention guardrails:
  abstention
  `-0.1949 dB`,
  same-gender keep
  `-0.0839 dB`,
  hard-present keep
  `-0.0889 dB`,
  artifact proxy
  `-0.0736 dB`.
- `v198 = v197` with
  `overlap_dual_controller_distill_weight = 0.5`
  is practical tie to
  `v197`.
  Relative `v157`,
  the same five fixed deltas stay effectively unchanged,
  and direct
  `v197 -> v198`
  local-proxy delta is only
  `-1.7e-07 dB`.
- Verdict:
  the pure apply-controller dual-teacher family is now bounded.
  It can spend auxiliary evidence on the blocker,
  but it does so through the same output-writing route that burns guardrail margin,
  and simple weight retuning does not open a better regime.

## Code Change

- `src/tse_prefix/pipeline/baseline_train.py`
  now returns exact zero for optional monitor or distill terms when the required tensors are absent,
  instead of crashing on `None`.
- `src/tse_prefix/models/stft_mask_baseline.py`
  now always emits
  `branch_overlap_dual_controller`
  whenever the dual residual path is active,
  even when
  `branch_overlap_dual_decoder_apply_mode = current_output`
  and no monitor head is enabled.
- The controller-distill plumbing added this turn remains active in:
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`

## `v196`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v196_v190_applycontroller_dualteacher_v1_ft1`
- Parent:
  `v190`
- Trainable:
  `branch_overlap_cancel_apply_controller_head`
  only
  (`131585 / 7826316`,
  `1.68%`)
- Training start:
  `2026-03-30T11:36:09`
- Training end:
  `2026-03-30T11:36:33`
- Elapsed:
  `24.170s`
- Scientific read:
  invalid no-op.
  The intended teacher tensor was absent under the active
  `v190`
  semantics.

## `v196` Fixed Checks

- Relative `v157`:
  exact
  `0.0 dB`
  on abstention, same-gender keep, hard-present keep, artifact proxy, and local speech leak proxy
- Relative `v190`:
  exact
  `0.0 dB`
  on the same five checks

## `v197`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v197_v190_applycontroller_dualteacher_livecontroller_v1_ft1`
- Parent:
  `v190`
- Trainable:
  `branch_overlap_cancel_apply_controller_head`
  only
  (`131585 / 7826316`,
  `1.68%`)
- Training start:
  `2026-03-30T11:52:03`
- Training end:
  `2026-03-30T11:52:32`
- Elapsed:
  `29.428s`
- Active new metric:
  `val_overlap_dual_controller_distill_l1 = 0.113235`
- Interpretation:
  the teacher bridge is now genuinely live.
  This is no longer a no-op family.

## `v197` Fixed Checks relative `v157`

- abstention `-0.1949 dB` (0 improved, 4 regressed of 8)
- same-gender keep `-0.0839 dB` (0 improved, 2 regressed of 11)
- hard-present keep `-0.0889 dB` (1 improved, 5 regressed of 16)
- artifact proxy `-0.0736 dB` (0 improved, 2 regressed of 7)
- local speech leak proxy `+0.1082 dB` (3 improved, 0 regressed of 7)

## `v197` Fixed Checks relative `v190`

- abstention `-0.1949 dB`
- same-gender keep `-0.0839 dB`
- hard-present keep `-0.0889 dB`
- artifact proxy `-0.0736 dB`
- local speech leak proxy `+0.1082 dB`

## `v198`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v198_v197_applycontroller_dualteacher_livecontroller_halfweight_v1_ft1`
- Parent:
  initialized from
  `v190`
  with the same live-teacher code path as
  `v197`
- Only route change relative `v197`:
  `overlap_dual_controller_distill_weight`
  from
  `1.0`
  to
  `0.5`
- Training start:
  `2026-03-30T11:54:32`
- Training end:
  `2026-03-30T11:54:56`
- Elapsed:
  `24.489s`
- Final active metric:
  `val_overlap_dual_controller_distill_l1 = 0.113236`

## `v198` Fixed Checks relative `v157`

- abstention `-0.1949 dB`
- same-gender keep `-0.0839 dB`
- hard-present keep `-0.0889 dB`
- artifact proxy `-0.0736 dB`
- local speech leak proxy `+0.1082 dB`

## `v198` Fixed Checks relative `v197`

- local speech leak proxy `-1.7e-07 dB`
- Interpretation:
  practical tie.
  The lower-weight run falls back into the same output regime.

## Verdict

- `v196`
  is not a valid negative or positive scientific result;
  it is a semantics audit that exposed a missing teacher tensor.
- `v197`
  is the first real proof that the no-write dual auxiliary evidence can steer a separate apply controller.
- But the tradeoff shape is already familiar:
  local improvement comes from spending margin on the same output-writing route that hurts keep and abstention guardrails.
- `v198`
  closes the obvious first calibration axis.
  Halving the distill weight does not recover a new balance point.
- So this pure apply-controller dual-teacher family should now be treated as bounded.

## Next Step

- Do not keep sweeping plain dual-teacher distill weight on the same
  `branch_overlap_cancel_apply_controller`
  path.
- If this branch continues,
  the next route should read the no-write dual auxiliary evidence through a path that is not just the same apply-controller head,
  or it should add an explicitly disjoint keep-preserve route before spending more runs here.
