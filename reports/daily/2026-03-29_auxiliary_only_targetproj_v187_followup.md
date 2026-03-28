# 2026-03-29 broader-path auxiliary-only target projection on `v179`: `v187` follow-up

## Summary

- Goal:
  test whether the broader-path
  `v179`
  local objective can stay useful
  after decoupling direct final-output rewrite through
  `branch_overlap_cancel_apply_mode = auxiliary_only`.
- `v187 = v179 + auxiliary_only overlap_cancel target projection`
  is not a no-op.
  But it does not behave like a clean orthogonal local path either.
- Relative
  `v157`,
  all four keep or abstention guardrails improved
  (`+1.4179 / +0.1285 / +1.2877 / +0.9857 dB`),
  while
  `local_speech_leak_proxy_v1`
  regressed
  `-1.9193 dB`.
- Relative
  `v179`,
  same-gender keep recovered only
  `+0.0765 dB`,
  while the local blocker regressed
  `-0.3086 dB`.
- Training evidence explains the shape:
  the auxiliary route stayed selected
  (`train 33 / 233, val 7 / 67`),
  but final
  `val_overlap_cancel_target_projection_ratio = 2.58e-09`
  and
  `val_gate_pre_present_keep_mean = 1.64e-05`
  both collapsed to near zero.
- New branch boundary:
  decoupling output application alone is not enough
  if the local objective still backpropagates through the same broader-path temporal or gate route.

## `v187 = v179 + auxiliary_only overlap_cancel target projection`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v187_v179_auxonly_targetproj002_keep2p0_v1_ft1`
- Parent:
  `v179`
- Model change:
  `branch_overlap_cancel_apply_mode = auxiliary_only`
- Kept local loss:
  `overlap_cancel_target_projection_weight = 0.02`
- Kept gate loss:
  `gate_pre_present_keep_weight = 2.0`
- Kept overlap selector:
  `data/synthetic/sample_ids_local_speech_leak_proxy_v1_all.txt`
- Intent:
  preserve the broader-path local objective,
  but stop writing the cancel estimate directly into the final output.

## Training Evidence

- Trainable modules remained:
  - `branch_decoder_temporal_model`
  - `branch_decoder_gate_head`
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_pre_present_controller_head`
- `overlap_cancel` selector coverage:
  `train 33 / 233, val 7 / 67`
- Final training metrics:
  - `val_overlap_cancel_target_projection_ratio = 2.58e-09`
  - `val_gate_pre_present_keep_mean = 1.64e-05`
  - `val_gate_pre_present_abstain_mean = 0.3432833`
- Interpretation:
  once direct output rewrite is removed,
  the intended local route itself collapses to near zero,
  but the shared branch still drifts enough to move fixed synthetic behavior.

## Fixed Checks relative `v157`

- abstention `+1.4179 dB`
- same-gender keep `+0.1285 dB`
- hard-present keep `+1.2877 dB`
- artifact proxy `+0.9857 dB`
- local speech leak proxy `-1.9193 dB`

## Direct Comparison relative `v179`

- same-gender keep `+0.0765 dB`
- local speech leak proxy `-0.3086 dB`

## Positioning relative `v178`

- same-gender keep `-0.5269 dB`
- local speech leak proxy `+0.0672 dB`
- Interpretation:
  `v187`
  lands close to the old
  `v178`
  keep-heavy region,
  not as a new balanced orthogonal route.

## Verdict

- `v187`
  is not a no-op.
- It is also not a valid continuation.
  The direct output rewrite is gone,
  but the broader-path local objective does not survive as a useful signal.
- Instead,
  the shared route drifts back toward keep-heavy behavior while the local blocker worsens.
- So this is a shared-route auxiliary-only reject,
  not a near-real candidate.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  only as mechanism-positive evidence.
- Keep
  `v179`
  only as broader-path explicit-local-target evidence.
- Mark
  `v187`
  as:
  auxiliary-only shared-route drift reject.
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - broader-path
    `auxiliary_only`
    target projection on top of
    `v179`
  - routes that decouple output application
    but still share the same trainable broader-path temporal or gate modules
- If this branch continues,
  the local objective needs a truly disjoint trainable path,
  not just a non-writing apply mode.
