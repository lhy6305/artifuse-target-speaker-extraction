# 2026-03-31 abstention-first keep-side repair on top of `v233`: `v239` follow-up

## Summary

- Goal:
  test whether the steep
  `v233`
  split-route
  `refine_base`
  local-only writer was a monolithic guardrail-for-local tradeoff,
  or whether at least the abstention failure could be repaired from the keep-side output
  without giving back most of the blocker gain.
- Diagnostic before launch:
  per-sample fixed-proxy comparison showed that the main
  `v233`
  abstention-bad roots
  (`val_000426`, `val_000182`, `val_000057`)
  were disjoint from the strongest local-good roots,
  so abstention-first repair had higher information gain than artifact-first repair.
- Route:
  start from
  `v233`,
  keep the split-route local writer unchanged
  (`local_prediction_source = estimated_waveform_refine_base`,
  `branch_overlap_refine_head` trainable),
  keep keep-side reconstruction on
  `estimated_waveform_post_pre_present_controller`,
  and add a focused
  `absent_extra`
  guard on
  `target_clean_speech`
  plus
  `target_absent_head/tail`
  slices.
- Smoke:
  `_smoke_v239_v233_refinebase_absentextra002_v1`
  passed and confirmed that the new guard was active rather than a fake continuation.
- Full:
  `v239`
  was training-real and meaningfully repaired the bad
  `v233`
  abstention side while keeping most of the blocker gain.
- Verdict:
  this is not a promotion point,
  because relative
  `v224`
  and
  `v157`
  the route is still materially negative on abstention and artifact.
  But it is also not a family closure result:
  it proves the
  `v233`
  split-route writer is at least partly decomposable.
  The next continuation should repair artifact on the keep-side output,
  not retune the same local writer or absent scalar.

## Code Change

- None.
  `v239`
  uses existing
  `absent_extra`
  plumbing and existing split-route local-writer plumbing.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v239 = v233 + keep-side absent_extra 0.02 on clean absent slices`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v239_v233_refinebase_absentextra002_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v239_v233_refinebase_absentextra002_v1_ft1`
- Trainable:
  `branch_overlap_refine_head + branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`790022 / 8352912`,
  `9.4580%`)
- Training start:
  `2026-03-31T13:38:10`
- Training end:
  `2026-03-31T13:39:18`
- Elapsed:
  `67.852s`
- Final active metrics:
  - `val_loss = 0.30602`
  - `val_reconstruction_extra_waveform_l1 = 0.009641`
  - `val_reconstruction_extra_stft_l1 = 0.019889`
  - `val_extra_local_waveform_l1 = 0.001261`
  - `val_extra_local_sisdr_loss = 0.490734`
  - `val_absent_extra_interval_l1 = 0.000242`
  - `val_gate_absent_mean = 0.0224`
  - `val_gate_keep_mean = 0.120344`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001159`
  - `val_overlap_dual_residual_correction_local_controller_l1 = 0.123013`
  - `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.009059`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`
  - absent extra `train 95 / 233, val 24 / 67`

### Fixed Checks relative `v157`

- `-0.5835 / +0.0551 / +0.0702 / -0.3359 / +0.6650 dB`

### Fixed Checks relative `v224`

- `-0.5784 / +0.0566 / +0.0672 / -0.3280 / +0.6495 dB`

### Fixed Checks relative `v233`

- `+0.2134 / -0.0051 / -0.0407 / +0.0917 / -0.0130 dB`

## Read

- This continuation is clearly not a no-op.
  The new keep-side
  `absent_extra`
  term is active in both smoke and full,
  and fixed-proxy behavior changed materially relative to
  `v233`.
- The direction is informative.
  Relative
  `v233`,
  abstention recovered by
  `+0.2134 dB`,
  artifact recovered by
  `+0.0917 dB`,
  same-gender keep stayed near tie,
  hard-present keep gave back only
  `-0.0407 dB`,
  and the blocker gave back only
  `-0.0130 dB`.
- The abstention repair is also sample-real, not just aggregate wash.
  The earlier main regressions
  `val_000182`
  and
  `val_000057`
  both improved strongly,
  and the previous artifact-local overlap case
  `val_000343`
  also recovered by
  `+0.5771 dB`
  on the artifact proxy.
- But the family is still not promotable.
  Relative
  `v224`,
  abstention and artifact remain materially negative
  (`-0.5784 / -0.3280 dB`)
  even though same-gender keep, hard-present keep, and the local blocker all stay positive.
- So the key read is not "failure" versus "success".
  The key read is that the
  `v233`
  split-route writer is not a single indivisible collapse.
  A keep-side abstention repair can claw back part of the bad surface without immediately erasing the local gain.

## Conclusion

- `v239` becomes the new best boundary point inside the split-route
  `refine_base`
  local-only writer family.
- It is still below promotion because abstention and artifact remain materially negative versus
  `v224`
  and
  `v157`.
- Do not retune the same
  `absent_extra`
  scalar by default.
- If this family continues,
  the next branch should be an artifact-first keep-side repair on top of
  `v239`,
  not another retune of the same local writer or the same abstention guard.
