# 2026-03-30 dual residual target-projection retune on the `v212` disjoint route: `v220 / v221` follow-up

## Summary

- Goal:
  test whether a more blocker-aligned local objective can move the safer
  `v212`
  family without reopening the large guardrail collapse seen on older local routes.
- Route:
  keep the
  `v212`
  trainable path and downstream application unchanged,
  and only add
  `overlap_dual_residual_target_projection_weight`
  on top of the existing dual residual plus residual-correction losses.
- To make this route reproducible without scraping old summaries,
  the
  `reconstruction_extra`
  selector ids were materialized as:
  `data/manifests/selectors/reconstruction_extra_gate_keep_union_v2_ids.txt`.
- `v220`
  with weight
  `0.01`
  was training-real,
  but practical tie to
  `v212`.
- `v221`
  raised the same weight to
  `0.02`,
  and remained practical tie to
  `v220`
  and near-tie to
  `v157`.
- Verdict:
  the first
  `overlap_dual_residual_target_projection_weight`
  retune on top of the
  `v212`
  disjoint route is now closed.
  This scalar is optimization-real,
  but it does not create meaningful local-blocker movement at the active fixed-proxy resolution.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v220 = v212 + overlap_dual_residual_target_projection_weight 0.01`

- Smoke:
  `_smoke_v220_v212_dualresidual_targetproj001_v1`
  passed.
  The new local-objective term was active,
  and selector coverage stayed unchanged.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v220_v212_dualresidual_targetproj001_v1_ft1`
- Trainable:
  still
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-30T22:47:33`
- Training end:
  `2026-03-30T22:48:33`
- Elapsed:
  `59.442s`
- Final active metrics:
  - `val_loss = 0.269348`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_target_projection_ratio = 0.001304`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0285 / -0.0122 / -0.0105 / -0.0024 / +0.0014 dB`

### Fixed Checks relative `v212`

- `+0.0026 / +0.0034 / +0.0034 / +0.0024 / +0.0009 dB`

### Verdict

- This run is training-real,
  but practical tie to
  `v212`.
- Adding a small dual residual target-projection term does not materially move the local blocker on this family.

## `v221 = v220 + overlap_dual_residual_target_projection_weight 0.02`

- Smoke:
  `_smoke_v221_v220_dualresidual_targetproj002_v1`
  also passed,
  and again looked nearly identical to the parent run.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v221_v220_dualresidual_targetproj002_v1_ft1`
- Trainable:
  unchanged from
  `v220`
  (`6.3043%`)
- Training start:
  `2026-03-30T22:55:01`
- Training end:
  `2026-03-30T22:55:55`
- Elapsed:
  `54.013s`
- Final active metrics:
  - `val_loss = 0.269361`
  - `val_reconstruction_extra_waveform_l1 = 0.009660`
  - `val_reconstruction_extra_stft_l1 = 0.020714`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_overlap_dual_residual_target_projection_ratio = 0.001304`
  - `val_gate_keep_mean = 0.118113`
- Selector activity:
  - reconstruction extra `train 63 / 233, val 27 / 67`
  - overlap dual `train 33 / 233, val 7 / 67`

### Fixed Checks relative `v157`

- `-0.0310 / -0.0144 / -0.0149 / -0.0025 / +0.0020 dB`

### Fixed Checks relative `v220`

- `-0.0025 / -0.0021 / -0.0043 / -0.0001 / +0.0006 dB`

### Verdict

- `v221`
  remains practical tie to
  `v220`.
- Raising the target-projection weight from
  `0.01`
  to
  `0.02`
  does not open a new regime.
  The only local gain is
  `+0.0006 dB`,
  far below any meaningful threshold.

## Conclusion

- On top of the
  `v212`
  disjoint route,
  the scalar
  `overlap_dual_residual_target_projection_weight`
  retune is now bounded at:
  - `v220 = 0.01`
  - `v221 = 0.02`
- Both runs are training-real,
  but both are practical tie at the fixed-proxy resolution.
- So this is not the local-objective breakthrough.
  It is another ineffective retune on the same route.
- If this branch continues,
  do not keep micro-sweeping the same target-projection scalar.
  The next step must change the local objective more structurally,
  or change the writable path rather than just reweighting this one term.
