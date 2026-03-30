# 2026-03-30 monitor local interval residual on `v193`: `v194` follow-up

## Summary

- Goal:
  test whether the monitor family can become locally selective
  if the supervision is moved from plain gate targets
  to a local-blocker-specific residual interval objective
  on the actual monitor-applied correction path.
- `v193 = v192 + audibility gate target on overlap_dual_monitor_controller`
  was effectively a no-op:
  relative `v192`,
  the four non-blocker checks changed only
  `+0.0004 / +0.0004 / +0.0003 / +0.0004 dB`,
  while the local blocker regressed
  `-0.0004 dB`.
- `v194 = v193 + overlap_dual_monitor_waveform_weight 50.0`
  with
  `branch_overlap_dual_decoder_head + branch_overlap_dual_monitor_controller_head`
  trainable
  is training-real,
  but it still pushes in the wrong scientific direction.
- Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all improved further
  (`+0.0769 / +0.0323 / +0.0578 / +0.0364 dB`),
  but `local_speech_leak_proxy_v1`
  regressed to
  `-0.0262 dB`.
- Relative `v193`,
  the same four non-blocker checks improved
  `+0.0128 / +0.0078 / +0.0065 / +0.0043 dB`,
  while the local blocker regressed another
  `-0.0117 dB`.
- Verdict:
  the monitor family now has two more closed negatives:
  the audibility target is a practical no-op,
  and the local residual interval objective still sharpens general safe suppression
  more than local blocker selectivity.

## Why `v193` was a no-op

- On the active local blocker set,
  `branch_overlap_dual_monitor_controller`
  was already almost equal to the frozen
  `branch_overlap_dual_controller`
  ceiling:
  mean about
  `0.1122`
  versus
  `0.1136`.
- So a head-only monitor-target branch had almost no remaining freedom.
- This is why `v193`
  changed four non-blocker proxies by only
  `~+0.0003 to +0.0004 dB`
  and did not move the blocker.

## Code

- Model output added:
  `branch_overlap_dual_monitor_estimate_waveform`
  in
  `src/tse_prefix/models/stft_mask_baseline.py`
- Loss plumbing added:
  `overlap_dual_monitor_waveform_l1`
  and
  `overlap_dual_monitor_waveform_weight`
  in
  `src/tse_prefix/pipeline/baseline_train.py`
- Train and eval entrypoints were updated to pass through and log the new metric:
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
- Important correction:
  the monitor correction target was defined against
  the current output residual
  (`prediction - target`),
  not full interference.
  That matches the fact that
  `monitor_max_blend = 0.02`
  makes this path a small correction route,
  not a full residual decoder.

## `v194 = v193 + local monitor-applied residual interval loss`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v194_v193_monitor_localintervalresidual_v1_ft1`
- Parent:
  `v193/best.pt`
- Trainable:
  `branch_overlap_dual_decoder_head`
  and
  `branch_overlap_dual_monitor_controller_head`
  only
  (`395011` params of `7957901`,
  `4.96%`)
- Selector:
  `overlap_dual train 33 / 233, val 7 / 67`
  using
  `data/manifests/selectors/overlap_dual_local_speech_leak_proxy_v1_ids.txt`
- Training start:
  `2026-03-30T01:57:18`
- Training end:
  `2026-03-30T01:57:45`
- Elapsed:
  `27.451s`

## Training Evidence

- Final
  `val_overlap_dual_monitor_waveform_l1 = 0.004913`
- Final
  `val_gate_keep_mean = 0.322828`
- Final
  `val_overlap_dual_residual_waveform_l1 = 0.016114`
  versus
  `0.015926`
  in `v193`,
  so the dual decoder head did move slightly.
- Interpretation:
  the new monitor-local residual objective was active
  and the trainable path had real freedom,
  but that freedom still went into a broader safe-suppression direction
  instead of the active blocker direction.

## Fixed Checks relative `v157`

- abstention `+0.0769 dB` (3 improved, 0 regressed of 8)
- same-gender keep `+0.0323 dB` (1 improved, 0 regressed of 11)
- hard-present keep `+0.0578 dB` (2 improved, 0 regressed of 16)
- artifact proxy `+0.0364 dB` (0 improved, 0 regressed of 7)
- local speech leak proxy `-0.0262 dB` (0 improved, 0 regressed of 7)

## Fixed Checks relative `v193`

- abstention `+0.0128 dB`
- same-gender keep `+0.0078 dB`
- hard-present keep `+0.0065 dB`
- artifact proxy `+0.0043 dB`
- local speech leak proxy `-0.0117 dB`

## Verdict

- `v193` is closed as a practical no-op reject.
- `v194` is closed as a local-blocker reject.
- The monitor family still produces a coherent pattern:
  better general safe suppression,
  worse active local blocker.
- This is now stronger evidence than the earlier `v192` result,
  because `v194` was not head-only
  and did use a blocker-specific correction target.

## Next Step

- This next-step note is now superseded by `v195`.
- The final closure run on higher
  `branch_overlap_dual_monitor_max_blend`
  was executed as
  `v195`
  and also failed.
- So the monitor family is now closed,
  and the better use of time is to leave this family
  and move to a path whose local objective is not capped by the current monitor-correction route.
