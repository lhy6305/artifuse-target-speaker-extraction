# 2026-03-28 parallel pre-present waveform-local objective on `v178`: `v181 / v182` follow-up

## Summary

- Goal:
  test whether the broader-path route from
  `v178`
  can recover the active local blocker by adding a more direct waveform-local
  overlap-cancel objective.
- `v181 = v178 + overlap_cancel_waveform_weight 0.02`
  is not a local-versus-keep tradeoff.
  It is a route-wide collapse:
  all fixed guardrails and the targeted local proxy fail sharply.
- `v182 = v178 + overlap_cancel_waveform_weight 0.002`
  still fails in the same global direction,
  so the issue is not just an overly large waveform-local weight.
- The new branch boundary is:
  on this broader-path route,
  direct waveform-local overlap-cancel supervision blows up the route even at a much smaller weight.

## `v181 = v178 + overlap_cancel_waveform_weight 0.02`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v181_v178_parallel_prepresent_jointtemporalgate_cancelhead_waveform002_v1_ft1`
- Init:
  `v178`
  best checkpoint, with teacher metadata fallback disabled
- Model / trainable set:
  same broader-path route as
  `v178`
  with
  - `branch_decoder_temporal_model`
  - `branch_decoder_gate_head`
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_pre_present_controller_head`
- Selector bundle:
  restored
  `local_speech_leak_proxy_v1_all`
  set
- New loss:
  `overlap_cancel_waveform_weight = 0.02`
- Intent:
  replace the weak projection-style local target from
  `v179 / v180`
  with a more direct waveform-local overlap-cancel target.

### Fixed Checks relative `v157`

- abstention `-12.5972 dB`
- same-gender keep `-7.4208 dB`
- hard-present keep `-13.6905 dB`
- artifact proxy `-17.9917 dB`
- local speech leak proxy `-7.9100 dB`

### Direct Comparison relative `v178`

- abstention proxy:
  `-13.7615 dB`
- local speech leak proxy:
  `-5.9235 dB`

### Verdict

- `v181`
  is training-real and not a no-op,
  but it is clearly not a selective local repair.
- It destroys both keep or abstention guardrails and the targeted local blocker together.
- Therefore
  `v181`
  is a global-collapse reject and does not warrant near-real evaluation.

## `v182 = v178 + overlap_cancel_waveform_weight 0.002`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v182_v178_parallel_prepresent_jointtemporalgate_cancelhead_waveform0002_v1_ft1`
- Intent:
  test whether the
  `v181`
  failure is just waveform-local strength being too large.
- New loss:
  `overlap_cancel_waveform_weight = 0.002`

### Fixed Checks relative `v157`

- abstention `-16.7680 dB`
- same-gender keep `-6.7406 dB`
- hard-present keep `-14.3340 dB`
- artifact proxy `-14.6796 dB`
- local speech leak proxy `-8.9497 dB`

### Verdict

- `v182`
  fails in the same global wrong-way direction as
  `v181`.
- Lowering the waveform-local weight by
  `10x`
  does not recover the route or restore the guardrails.
- So this is not a useful calibration axis,
  and
  `overlap_cancel_waveform_weight`
  sweep stops here.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  only as mechanism-positive evidence.
- Keep
  `v178 / v179 / v180`
  as the broader-path evidence sequence.
- Mark:
  - `v181`:
    waveform-local global-collapse reject
  - `v182`:
    lower-weight replication that closes
    `overlap_cancel_waveform_weight`
    sweep
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - `overlap_cancel_target_projection_weight`
    sweep
  - `overlap_cancel_waveform_weight`
    sweep on the broader-path route
- If this line continues,
  the next valid move must explicitly preserve keep while repairing the local blocker.
- The most reasonable next options are:
  - a paired objective with explicit same-gender keep protection
  - a different local objective that does not directly dominate the broader-path route
  - a larger route change only if it is coupled to explicit keep-preserving supervision
