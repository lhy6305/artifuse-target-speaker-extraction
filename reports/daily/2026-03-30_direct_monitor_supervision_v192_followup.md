# 2026-03-30 direct monitor supervision on `v191`: `v192` follow-up

## Summary

- Goal:
  test whether the existing safe monitor-coupling head from `v191`
  becomes locally selective
  if gate supervision is moved directly onto
  `branch_overlap_dual_monitor_controller`.
- `v192 = v191 + gate_supervision_source overlap_dual_monitor_controller`
  is training-real,
  but it still does not improve the active local blocker.
- Relative to `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all stayed small positive
  (`+0.0637 / +0.0241 / +0.0510 / +0.0317 dB`),
  but `local_speech_leak_proxy_v1` moved wrong-way
  `-0.0140 dB`.
- Relative to `v191`,
  the four non-blocker checks improved only
  `+0.0151 / +0.0078 / +0.0043 / +0.0039 dB`,
  while the local blocker regressed
  `-0.0149 dB`.
- Verdict:
  direct monitor supervision alone on top of `v191` is not the missing ingredient.

## Code

- No code changes were required.
- The run reused the already existing
  `branch_overlap_dual_monitor_controller`
  model output,
  `gate_supervision_source = overlap_dual_monitor_controller`
  entrypoint support,
  and the preserved `overlap_dual` selector path.

## `v192 = v191 + gate_supervision_source overlap_dual_monitor_controller`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v192_v191_monitor_directgate_v1_ft1`
- Parent:
  `v191/best.pt`
- Trainable:
  `branch_overlap_dual_monitor_controller_head` only
  (`131585` params of `7957901` total, `1.65%`)
- Selector:
  `overlap_dual train 33 / 233, val 7 / 67`
  using
  `data/manifests/selectors/overlap_dual_local_speech_leak_proxy_v1_ids.txt`
- Training start:
  `2026-03-30T01:22:12`
- Training end:
  `2026-03-30T01:22:39`
- Elapsed:
  `27.244s`

## Training Evidence

- `best_val_loss = 0.733490`
- `val_overlap_dual_residual_waveform_l1 = 0.015926`
  exactly preserved from `v190` and `v191`
- Final `val_gate_keep_mean = 0.353940`
  versus `0.400806` at the first validation epoch,
  so the monitor head did move during training
- Interpretation:
  the frozen no-write dual residual predictor stayed intact,
  and the trained object that changed was the monitor head itself

## Fixed Checks relative `v157`

- abstention `+0.0637 dB` (2 improved, 0 regressed of 8)
- same-gender keep `+0.0241 dB` (0 improved, 0 regressed of 11)
- hard-present keep `+0.0510 dB` (2 improved, 0 regressed of 16)
- artifact proxy `+0.0317 dB` (0 improved, 0 regressed of 7)
- local speech leak proxy `-0.0140 dB` (0 improved, 0 regressed of 7)

## Fixed Checks relative `v191`

- abstention `+0.0151 dB`
- same-gender keep `+0.0078 dB`
- hard-present keep `+0.0043 dB`
- artifact proxy `+0.0039 dB`
- local speech leak proxy `-0.0149 dB`

## Verdict

- `v192` is not a promotion candidate.
- It does not solve the local blocker.
- The branch result is stronger than a pure no-op:
  the monitor head moved,
  and four non-blocker checks improved slightly.
- But it moved in the wrong scientific direction for the active blocker:
  direct monitor supervision still sharpened general safe suppression
  more than local blocker selectivity.

## Next Step

- Do not replay direct monitor-controller supervision alone on top of `v191`.
- The most reasonable next options are:
  - add an audibility-style gate target on the monitor path
  - add a local-blocker-specific interval loss on the monitor controller output
  - increase `monitor_max_blend` only after deciding whether a more selective monitor target is worth testing first
