# 2026-03-30 dual-conditioned cancel-controller coupling on `v190`: `v203 / v204 / v205` follow-up

## Summary

- Goal:
  test a new coupling family that reads the proven no-write
  `v190`
  dual auxiliary evidence,
  but writes back through the existing overlap-cancel estimate instead of:
  - the old apply-controller head
  - the pre-present controller
  - direct gate rewrite
  - the small-blend monitor path
- Code change:
  added
  `branch_overlap_dual_cancel_controller_head`
  and
  `branch_overlap_dual_cancel_estimate_waveform`
  so the dual branch can drive a separate cancel-write controller on top of the fixed overlap-cancel estimate.
- This family is training-real:
  the dual selector stayed active in all runs
  (`train 33 / 233, val 7 / 67`),
  and the new controller metrics were nonzero.
- But output-side all three runs stayed practical near-no-op on the five fixed proxies.
  Relative `v157`,
  the best guardrail movement was only
  `+0.0103 dB`,
  and the local blocker stayed slightly wrong-way in every run
  (`-0.0015 / -0.0061 / -0.0021 dB`).
- Verdict:
  this new dual-conditioned cancel-controller family is now closed through
  `v205`.
  Higher blend only amplifies the same tiny
  guardrail-positive / local-negative
  direction,
  and widening to
  `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head`
  still does not open a useful regime.

## Code Change

- `src/tse_prefix/models/stft_mask_baseline.py`
  now supports:
  - `enable_branch_overlap_dual_cancel_controller`
  - `branch_overlap_dual_cancel_max_blend`
  - output
    `branch_overlap_dual_cancel_controller`
  - output
    `branch_overlap_dual_cancel_estimate_waveform`
- `scripts/train/train_stft_mask_baseline.py`
  now supports:
  - `--model-enable-branch-overlap-dual-cancel-controller`
  - `--model-branch-overlap-dual-cancel-max-blend`
  - `gate_supervision_source = overlap_dual_cancel_controller`
- `scripts/eval/eval_stft_mask_baseline.py`
  now resolves the same controller for evaluation-side gate supervision and comparison metrics.
- `py_compile`
  passed after the code change.

## `v203 = v190 + dual-cancel-controller head-only, blend 0.02`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v203_v190_dualcancelcontroller_blend002_v1_ft1`
- Trainable:
  `branch_overlap_dual_cancel_controller_head`
  only
  (`131585 / 7957901`,
  `1.6535%`)
- Training start:
  `2026-03-30T20:02:33`
- Training end:
  `2026-03-30T20:02:56`
- Elapsed:
  `22.915s`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.015926`
  - `val_overlap_dual_controller_distill_l1 = 0.281731`
  - `val_gate_keep_mean = 0.353940`

### Fixed Checks relative `v157`

- abstention `+0.0026 dB`
- same-gender keep `+0.0014 dB`
- hard-present keep `+0.0013 dB`
- artifact proxy `+0.0009 dB`
- local speech leak proxy `-0.0015 dB`

### Verdict

- Safe practical near-no-op.
- The route is real,
  but too weak to move the blocker in the correct direction.

## `v204 = v203 family, blend 0.08`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v204_v190_dualcancelcontroller_blend008_v1_ft1`
- Trainable:
  still
  `branch_overlap_dual_cancel_controller_head`
  only
  (`1.6535%`)
- Training start:
  `2026-03-30T20:06:17`
- Training end:
  `2026-03-30T20:06:47`
- Elapsed:
  `29.657s`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.015926`
  - `val_overlap_dual_controller_distill_l1 = 0.281731`
  - `val_gate_keep_mean = 0.353940`

### Fixed Checks relative `v157`

- abstention `+0.0103 dB`
- same-gender keep `+0.0056 dB`
- hard-present keep `+0.0051 dB`
- artifact proxy `+0.0035 dB`
- local speech leak proxy `-0.0061 dB`

### Fixed Checks relative `v203`

- abstention `+0.0077 dB`
- same-gender keep `+0.0042 dB`
- hard-present keep `+0.0038 dB`
- artifact proxy `+0.0026 dB`
- local speech leak proxy `-0.0046 dB`

### Verdict

- Higher blend only amplifies the same tiny
  guardrail-positive / local-negative
  direction.
- It does not open a new regime.

## `v205 = v203 family + joint dual-decoder-head widening`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v205_v190_dualcancelcontroller_jointdualhead_v1_ft1`
- Trainable:
  `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head`
  (`395011 / 7957901`,
  `4.9638%`)
- Training start:
  `2026-03-30T20:08:28`
- Training end:
  `2026-03-30T20:09:03`
- Elapsed:
  `35.458s`
- Final active metrics:
  - `val_overlap_dual_residual_waveform_l1 = 0.016116`
  - `val_overlap_dual_controller_distill_l1 = 0.256049`
  - `val_gate_keep_mean = 0.333589`

### Fixed Checks relative `v157`

- abstention `+0.0036 dB`
- same-gender keep `+0.0019 dB`
- hard-present keep `+0.0018 dB`
- artifact proxy `+0.0012 dB`
- local speech leak proxy `-0.0021 dB`

### Fixed Checks relative `v203`

- abstention `+0.0010 dB`
- same-gender keep `+0.0005 dB`
- hard-present keep `+0.0005 dB`
- artifact proxy `+0.0003 dB`
- local speech leak proxy `-0.0006 dB`

### Verdict

- Joint widening above the new controller still lands in practical tie to
  `v203`.
- So the problem is not just a frozen upstream ceiling.

## Conclusion

- The new dual-conditioned cancel-controller family is now bounded in three ways:
  - head-only small blend:
    safe near-no-op
  - head-only higher blend:
    same tiny direction, slightly amplified
  - joint dual-head widening:
    still practical tie
- The route reads non-trivial dual auxiliary evidence,
  but writing back through the existing overlap-cancel estimate still does not solve the active local blocker.
- The next continuation should therefore avoid the existing overlap-cancel estimate path itself,
  not just its old controller heads.
