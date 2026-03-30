# 2026-03-30 higher monitor blend on `v194`: `v195` follow-up

## Summary

- Goal:
  close the last unresolved axis inside the monitor family
  by testing whether the earlier failures were simply caused by
  `branch_overlap_dual_monitor_max_blend = 0.02`
  being too small.
- `v195 = v194 + branch_overlap_dual_monitor_max_blend 0.08`
  is training-real,
  but it makes the same scientific direction stronger rather than fixing it.
- Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all improved more strongly
  (`+0.1546 / +0.0811 / +0.0887 / +0.0595 dB`),
  but `local_speech_leak_proxy_v1`
  regressed sharply to
  `-0.1134 dB`.
- Relative `v194`,
  the four non-blocker checks improved again
  (`+0.0777 / +0.0488 / +0.0309 / +0.0231 dB`),
  while the local blocker regressed another
  `-0.0872 dB`.
- Hard-present keep also stopped being all-positive relative `v157`:
  `7 improved, 1 regressed, 8 near tie`.
- Verdict:
  higher monitor blend was not the missing factor.
  It amplified the same wrong route,
  so the monitor family is now closed.

## `v195 = v194 + branch_overlap_dual_monitor_max_blend 0.08`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v195_v194_monitorblend008_v1_ft1`
- Parent:
  `v194/best.pt`
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
- Only route change relative `v194`:
  `branch_overlap_dual_monitor_max_blend`
  from
  `0.02`
  to
  `0.08`
- Training start:
  `2026-03-30T10:52:20`
- Training end:
  `2026-03-30T10:52:45`
- Elapsed:
  `25.126s`

## Training Evidence

- Final
  `val_overlap_dual_monitor_waveform_l1 = 0.004923`
- Final
  `val_gate_keep_mean = 0.321329`
- Final
  `val_overlap_dual_residual_waveform_l1 = 0.016118`
- Interpretation:
  this was not a dead run.
  The same monitor-local route stayed active,
  but stronger coupling simply produced stronger general safe suppression
  and a worse local blocker.

## Fixed Checks relative `v157`

- abstention `+0.1546 dB` (5 improved, 0 regressed of 8)
- same-gender keep `+0.0811 dB` (3 improved, 0 regressed of 11)
- hard-present keep `+0.0887 dB` (7 improved, 1 regressed of 16)
- artifact proxy `+0.0595 dB` (1 improved, 0 regressed of 7)
- local speech leak proxy `-0.1134 dB` (0 improved, 4 regressed of 7)

## Fixed Checks relative `v194`

- abstention `+0.0777 dB`
- same-gender keep `+0.0488 dB`
- hard-present keep `+0.0309 dB`
- artifact proxy `+0.0231 dB`
- local speech leak proxy `-0.0872 dB`

## Verdict

- `v195` is a closure reject.
- Higher `monitor_max_blend` was not the missing factor.
- The full monitor family now shows one coherent pattern:
  better keep or abstention behavior,
  worse active local blocker.
- The right interpretation is not
  "monitor coupling almost works if tuned harder".
  The right interpretation is
  "this family spends extra coupling freedom in the wrong direction".

## Next Step

- Do not continue the monitor family with more target variants or more blend sweeps.
- Leave this family and move to a path whose local objective is not capped or entangled by the current monitor-correction route.
- Keep local supervision and keep-preserve supervision disjoint in both trainable path and output application.
