# 2026-03-28 parallel pre-present broader path and target-projection on `v172`: `v177 / v178 / v179 / v180` follow-up

## Summary

- Goal:
  continue past the
  `v176`
  joint cancel-head no-op by moving to a materially larger pre-present decision path,
  then test whether an explicit local target can recover the new route's wrong-way local tradeoff.
- `v177`
  is invalid scratch because the
  `overlap_cancel`
  selector bundle was accidentally omitted,
  so the targeted supervision never fired.
- `v178 = v172 + broader pre-present path`
  is the first strong-output continuation on this family:
  all four keep / abstention synthetic guardrails jump strongly positive,
  but the targeted local speech-leak proxy collapses hard.
- `v179 = v178 + overlap_cancel_target_projection_weight 0.02`
  is mechanism-positive:
  it pulls local speech leak partway back in the correct direction,
  but it also gives back most of the same-gender keep gain.
- `v180 = v178 + overlap_cancel_target_projection_weight 0.01`
  is practical tie to
  `v179`,
  so the
  `target_projection_weight`
  sweep is closed.

## `v177`: invalid scratch

- Intended experiment:
  jointly unfreeze
  - `branch_decoder_temporal_model`
  - `branch_decoder_gate_head`
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_pre_present_controller_head`
- Failure:
  the
  `overlap_cancel`
  selector bundle from
  `v172 / v176`
  was not restored,
  so
  `train_selector_metrics.overlap_cancel.active = false`
  and
  `gate_pre_present_keep_mean = 0.0`
  throughout.
- Verdict:
  `v177`
  is not comparable and should be treated as scratch only.

## `v178 = v172 + broader pre-present path`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v178_v172_parallel_prepresent_jointtemporalgate_cancelhead_selectorrestored_v1_ft1`
- Trainable set:
  - `branch_decoder_temporal_model`
  - `branch_decoder_gate_head`
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_pre_present_controller_head`
- Selector coverage is restored:
  `overlap_cancel train 33 / 233, val 7 / 67`
- Training signal is real:
  final
  `val_gate_pre_present_keep_mean = 4.15e-04`
  /
  `val_gate_pre_present_abstain_mean = 0.3416`
  and trainable parameter count rises to
  `2,498,820`.

### Fixed Checks relative `v157`

- abstention `+1.1643 dB`
- same-gender keep `+0.6554 dB`
- hard-present keep `+1.1836 dB`
- artifact proxy `+0.8078 dB`
- local speech leak proxy `-1.9865 dB`

### Direct Comparison relative `v172`

- abstention proxy:
  `+1.0984 dB`
- local speech leak proxy:
  `-1.9328 dB`

### Verdict

- `v178`
  proves the larger pre-present decision path is not a no-op.
- But it pushes in the wrong semantic direction for the active blocker:
  keep / abstention all improve strongly,
  while targeted local speech leak regresses on all
  `7 / 7`
  proxy samples.
- So
  `v178`
  does not warrant near-real evaluation.

## `v179 = v178 + overlap_cancel_target_projection_weight 0.02`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v179_v178_parallel_prepresent_jointtemporalgate_cancelhead_targetproj002_v1_ft1`
- New loss:
  `overlap_cancel_target_projection_weight = 0.02`
- Intent:
  keep the larger decision path from
  `v178`,
  but add an explicit selected local target so the new route stops winning only on keep / abstention proxies.

### Fixed Checks relative `v157`

- abstention `+1.3306 dB`
- same-gender keep `+0.0520 dB`
- hard-present keep `+1.1663 dB`
- artifact proxy `+0.9545 dB`
- local speech leak proxy `-1.6107 dB`

### Direct Comparison relative `v178`

- local speech leak proxy:
  `+0.3758 dB`
- same-gender keep:
  `-0.6034 dB`
- abstention proxy:
  `+0.1664 dB`

### Verdict

- `v179`
  is mechanism-positive.
- It proves the explicit
  `overlap_cancel_target_projection`
  objective can pull the local blocker back in the correct direction,
  but not enough:
  local proxy remains strongly negative,
  and the recovered local improvement is paid for mostly by losing same-gender keep margin.
- Therefore
  `v179`
  still does not clear the synthetic gate and does not warrant near-real evaluation.

## `v180 = v178 + overlap_cancel_target_projection_weight 0.01`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v180_v178_parallel_prepresent_jointtemporalgate_cancelhead_targetproj001_v1_ft1`
- Intent:
  test whether the
  `v179`
  tradeoff is just target-projection strength being too large.

### Fixed Checks relative `v157`

- abstention `+1.3406 dB`
- same-gender keep `+0.0483 dB`
- hard-present keep `+1.1776 dB`
- artifact proxy `+0.9602 dB`
- local speech leak proxy `-1.6277 dB`

### Direct Comparison relative `v179`

- local speech leak proxy:
  `-0.0170 dB`
- same-gender keep:
  `-0.0037 dB`

### Verdict

- `v180`
  is practical tie to
  `v179`.
- So this is not a meaningful strength-calibration axis,
  and
  `overlap_cancel_target_projection_weight`
  sweep stops here.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  as the mechanism-positive evidence point for the original parallel pre-present route.
- Mark:
  - `v177`:
    invalid scratch
  - `v178`:
    broader-path strong-tradeoff reject
  - `v179`:
    explicit-target mechanism-positive reject
  - `v180`:
    practical tie that closes
    `target_projection_weight`
    sweep
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - `branch_overlap_cancel_head + pre-present controller`
    joint unfreeze alone
  - `overlap_cancel_target_projection_weight`
    sweep
- If this branch continues,
  the next valid move is no longer broader-path activation or projection-weight calibration.
  It should switch to a different explicit local objective,
  such as a waveform-local overlap-cancel target
  or a paired objective that preserves same-gender keep while pulling back the local blocker.
