# 2026-03-30 pre-present keep-output plus dual residual-correction on `v212`: `v214 / v215 / v216` guard-SI-SDR follow-up

## Summary

- Goal:
  test whether the new disjoint-downstream
  `v211 / v212 / v213`
  family can recover guardrail quality with a more expressive keep-preserve objective
  than plain reconstruction-extra,
  while still keeping keep supervision on the same
  `estimated_waveform_post_pre_present_controller`
  output path.
- Route:
  keep the
  `v212`
  family structure,
  and add
  `branch_protect_guard_sisdr`
  on top of the same post-pre-present-controller output.
- This objective is training-real in all three runs:
  `branch_protect` stayed active
  (`train 63 / 233, val 27 / 67`)
  and
  `val_branch_protect_guard_sisdr_loss`
  stayed clearly nonzero
  (`~6.56`).
- But output-side the family is still practical no-op across the full tested weight sweep:
  - `v214` with weight `0.0002`
  - `v215` with weight `0.001`
  - `v216` with weight `0.003`
- Relative
  `v212`,
  `v214`
  moved the five fixed checks only
  `+0.0003 / +0.0021 / -0.0001 / +0.0027 / +0.0051 dB`.
- Relative
  `v214`,
  `v215`
  moved them only
  `-0.0062 / -0.0066 / -0.0000 / +0.0014 / -0.0005 dB`.
- Relative
  `v215`,
  `v216`
  moved them only
  `+0.0038 / +0.0086 / +0.0033 / -0.0013 / -0.0083 dB`.
- Verdict:
  this keep-objective family is now closed on the disjoint-downstream route.
  Increasing
  `branch_protect_guard_sisdr_weight`
  from
  `0.0002`
  to
  `0.003`
  mainly raises the scalar loss,
  not the actual fixed-proxy behavior.

## `v214 = v212 + branch_protect_guard_sisdr 0.0002`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v214_v212_prepresentkeepoutput_dualresidual_guardsisdr0002_v1_ft1`
- Parent:
  `v212`
- New keep selector:
  `data/synthetic/sample_ids_gate_keep_union_v2_all.txt`
- New keep loss:
  `branch_protect_guard_sisdr_weight = 0.0002`
- Trainable:
  still
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-30T21:51:23`
- Training end:
  `2026-03-30T21:52:06`
- Elapsed:
  `42.406s`
- Final active metrics:
  - `val_loss = 0.270647`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_branch_protect_guard_sisdr_loss = 6.560211`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- abstention `-0.0308 dB`
- same-gender keep `-0.0135 dB`
- hard-present keep `-0.0140 dB`
- artifact proxy `-0.0021 dB`
- local speech leak proxy `+0.0056 dB`

### Fixed Checks relative `v212`

- abstention `+0.0003 dB`
- same-gender keep `+0.0021 dB`
- hard-present keep `-0.0001 dB`
- artifact proxy `+0.0027 dB`
- local speech leak proxy `+0.0051 dB`

### Verdict

- The new keep objective is clearly active,
  but this weight is practical tie to
  `v212`
  on the five active fixed proxies.

## `v215 = v214 family + branch_protect_guard_sisdr 0.001`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v215_v214_prepresentkeepoutput_dualresidual_guardsisdr001_v1_ft1`
- Parent:
  `v214`
- New keep loss:
  `branch_protect_guard_sisdr_weight = 0.001`
- Training start:
  `2026-03-30T21:54:54`
- Training end:
  `2026-03-30T21:55:32`
- Elapsed:
  `38.240s`
- Final active metrics:
  - `val_loss = 0.275895`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_branch_protect_guard_sisdr_loss = 6.560095`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- abstention `-0.0371 dB`
- same-gender keep `-0.0201 dB`
- hard-present keep `-0.0140 dB`
- artifact proxy `-0.0007 dB`
- local speech leak proxy `+0.0051 dB`

### Fixed Checks relative `v214`

- abstention `-0.0062 dB`
- same-gender keep `-0.0066 dB`
- hard-present keep `-0.0000 dB`
- artifact proxy `+0.0014 dB`
- local speech leak proxy `-0.0005 dB`

### Verdict

- Increasing the keep weight by
  `5x`
  mostly raises
  `val_loss`,
  not fixed-proxy behavior.
- Output-side this is still practical tie to
  `v214`.

## `v216 = v215 family + branch_protect_guard_sisdr 0.003`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v216_v215_prepresentkeepoutput_dualresidual_guardsisdr003_v1_ft1`
- Parent:
  `v215`
- New keep loss:
  `branch_protect_guard_sisdr_weight = 0.003`
- Training start:
  `2026-03-30T21:57:58`
- Training end:
  `2026-03-30T21:58:40`
- Elapsed:
  `42.723s`
- Final active metrics:
  - `val_loss = 0.289015`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_branch_protect_guard_sisdr_loss = 6.560205`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- abstention `-0.0333 dB`
- same-gender keep `-0.0115 dB`
- hard-present keep `-0.0107 dB`
- artifact proxy `-0.0020 dB`
- local speech leak proxy `-0.0031 dB`

### Fixed Checks relative `v215`

- abstention `+0.0038 dB`
- same-gender keep `+0.0086 dB`
- hard-present keep `+0.0033 dB`
- artifact proxy `-0.0013 dB`
- local speech leak proxy `-0.0083 dB`

### Verdict

- Even at the old stronger weight scale,
  the family still does not leave the same practical-tie basin.
- This closes the tested
  `branch_protect_guard_sisdr_weight`
  sweep on the new disjoint-downstream route.

## Conclusion

- The pre-present keep-output plus dual residual-correction family now has one more closed axis:
  `branch_protect_guard_sisdr_weight`
  on the same
  `estimated_waveform_post_pre_present_controller`
  route.
- Across
  `0.0002 -> 0.001 -> 0.003`,
  the objective is optimization-real,
  but output-capped:
  `val_branch_protect_guard_sisdr_loss`
  stays active while the five fixed proxies stay in practical tie.
- So the next continuation should not keep sweeping this same scalar guard-SI-SDR keep objective.
- If this family continues,
  it should use:
  - a qualitatively different keep objective
  - or a more expressive keep path
  rather than another small-to-medium weight retune on the same guard-SI-SDR term
