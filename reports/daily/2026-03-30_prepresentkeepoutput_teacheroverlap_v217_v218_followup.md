# 2026-03-30 pre-present keep-output teacher-overlap on the disjoint downstream route: `v217 / v218` follow-up

## Summary

- Goal:
  test whether
  `branch_protect_teacher_overlap`
  can improve the already safer
  `v212`
  family
  without reopening collapse,
  by supervising
  `estimated_waveform_post_pre_present_controller`
  against the safe
  `v157`
  teacher only inside the keep union windows.
- Both runs were training-real:
  `branch_protect_teacher`
  stayed active
  (`train 63 / 233, val 27 / 67`),
  `overlap_dual`
  stayed active
  (`train 33 / 233, val 7 / 67`),
  and
  `val_branch_protect_teacher_overlap_l1`
  stayed nonzero at about
  `0.000295`.
- But output-side this family still stayed inside the same narrow tradeoff basin:
  - `v217`
    was practical tie to
    `v212`,
    but uniformly slightly worse
  - `v218`
    partially repaired the four guardrails relative to
    `v217`
    and
    `v212`,
    but gave back local blocker quality again
- Verdict:
  the
  `branch_protect_teacher_overlap_weight`
  sweep on the same pre-present keep-output plus dual residual-correction route is now closed.
  It does not collapse,
  but it also does not open a selective regime.

## Fixed-Proxy Order

- All fixed-delta vectors below follow:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`

## `v217 = v212 + branch_protect_teacher_overlap_weight 0.04`

- Smoke:
  `_smoke_v217_v212_prepresentkeepoutput_teacheroverlap004_v1`
  passed.
  The selector was active and the new keep term was not missing.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v217_v212_prepresentkeepoutput_teacheroverlap004_v1_ft1`
- Trainable:
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`526596 / 8352912`,
  `6.3043%`)
- Training start:
  `2026-03-30T22:16:11`
- Training end:
  `2026-03-30T22:17:03`
- Elapsed:
  `52.776s`
- Final active metrics:
  - `val_loss = 0.269347`
  - `val_reconstruction_extra_waveform_l1 = 0.009661`
  - `val_reconstruction_extra_stft_l1 = 0.020709`
  - `val_branch_protect_teacher_overlap_l1 = 0.000295`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- `-0.0507 / -0.0311 / -0.0262 / -0.0140 / -0.0024 dB`

### Fixed Checks relative `v212`

- `-0.0196 / -0.0156 / -0.0123 / -0.0092 / -0.0029 dB`

### Verdict

- The low-weight teacher-overlap launch is training-real,
  not no-op.
- But on the active proxy set it is practical tie to
  `v212`
  with five-way slight negative drift.
- So
  `branch_protect_teacher_overlap_weight = 0.04`
  is not a useful landing point on this family.

## `v218 = v217 family + branch_protect_teacher_overlap_weight 0.2`

- Smoke:
  `_smoke_v218_v217_prepresentkeepoutput_teacheroverlap020_v1`
  again passed and looked almost identical to the parent run.
- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v218_v217_prepresentkeepoutput_teacheroverlap020_v1_ft1`
- Trainable:
  still
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  (`6.3043%`)
- Training start:
  `2026-03-30T22:23:34`
- Training end:
  `2026-03-30T22:24:25`
- Elapsed:
  `50.807s`
- Final active metrics:
  - `val_loss = 0.269394`
  - `val_reconstruction_extra_waveform_l1 = 0.009662`
  - `val_reconstruction_extra_stft_l1 = 0.020711`
  - `val_branch_protect_teacher_overlap_l1 = 0.000294`
  - `val_overlap_dual_residual_waveform_l1 = 0.004671`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001556`
  - `val_gate_keep_mean = 0.118113`

### Fixed Checks relative `v157`

- `-0.0101 / +0.0088 / -0.0063 / +0.0023 / -0.0052 dB`

### Fixed Checks relative `v217`

- `+0.0406 / +0.0400 / +0.0199 / +0.0163 / -0.0028 dB`

### Fixed Checks relative `v212`

- `+0.0210 / +0.0244 / +0.0076 / +0.0071 / -0.0057 dB`

### Verdict

- Raising teacher-overlap weight from
  `0.04`
  to
  `0.2`
  does improve the four non-blocker checks relative to both
  `v217`
  and
  `v212`.
- But the local blocker turns slightly wrong-way again,
  and the whole result still stays inside practical-tie scale around
  `v157`.
- So the stronger teacher-overlap term only moves this route along the same mild exchange surface;
  it does not create a promotion-worthy selective regime.

## Conclusion

- `v217`
  showed that a low
  `branch_protect_teacher_overlap`
  weight on this disjoint-downstream route is real but slightly harmful across all five fixed checks.
- `v218`
  showed that a higher weight can claw back some guardrail margin,
  but only by giving back the already-fragile local blocker gain.
- Therefore the
  `branch_protect_teacher_overlap_weight`
  sweep on the pre-present keep-output plus dual residual-correction family is now closed.
- If this route continues,
  do not keep retuning the same scalar teacher-overlap weight.
  The next step must change the keep path or keep objective more qualitatively,
  or change the local objective itself.
