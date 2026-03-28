# 2026-03-29 broader-path prerefine-base-align keep on `v179`: `v186` follow-up

## Summary

- Goal:
  test whether broader-path
  `v179`
  can preserve keep quality through a separate prerefine-base reference path
  instead of acting on the same controller or using direct final-output keep guards.
- `v186 = v179 + branch_protect_overlap_base_align_weight 0.04`
  with
  `loss_use_branch_prerefine_as_primary_prediction = True`
  is training-real:
  the new
  `branch_protect`
  selector stays active at
  `train 63 / 233, val 27 / 67`,
  and final
  `val_branch_protect_overlap_base_align_l1 = 0.0008964`.
- But fixed synthetic evaluation shows the route still gives the wrong tradeoff.
  Relative
  `v179`,
  local blocker quality improves strongly,
  yet all keep or abstention guardrails regress.
  Relative
  `v157`,
  the branch is still below gate because all four fixed guardrails are negative.
- New branch boundary:
  a separate keep-preserve reference path is not enough
  if it still constrains the same final output degrees of freedom.

## `v186 = v179 + prerefine-base-align keep`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v186_v179_targetproj002_prerefinebasealign_keepunion004_v1_ft1`
- Parent:
  `v179`
- Keep selector:
  `data/synthetic/sample_ids_gate_keep_union_v2_all.txt`
- New keep loss:
  `branch_protect_overlap_base_align_weight = 0.04`
- New routing flag:
  `loss_use_branch_prerefine_as_primary_prediction = True`
- Intent:
  keep the
  `v179`
  broader-path local target objective,
  but preserve keep-critical overlap regions by aligning final output to the branch prerefine base
  instead of directly guarding toward the target reference.

## Training Evidence

- `branch_protect` selector coverage:
  `train 63 / 233, val 27 / 67`
- `overlap_cancel` selector coverage:
  `train 33 / 233, val 7 / 67`
- Final training metrics:
  - `train_branch_protect_overlap_base_align_l1 = 0.0009077`
  - `val_branch_protect_overlap_base_align_l1 = 0.0008964`
  - `train_gate_keep_mean = 0.0361`
  - `val_gate_keep_mean = 0.0351`
  - `val_overlap_cancel_target_projection_ratio = 2.21e-09`
  - `val_gate_pre_present_keep_mean = 3.36e-05`
- Interpretation:
  the new prerefine-base-align path is real,
  but the route still does not behave like a balanced keep-plus-local solution.

## Fixed Checks relative `v157`

- abstention `-1.7370 dB`
- same-gender keep `-0.7234 dB`
- hard-present keep `-0.5724 dB`
- artifact proxy `-0.6573 dB`
- local speech leak proxy `+1.0155 dB`

## Direct Comparison relative `v179`

- abstention `-3.0676 dB`
- same-gender keep `-0.7755 dB`
- hard-present keep `-1.7387 dB`
- artifact proxy `-1.6118 dB`
- local speech leak proxy `+2.6262 dB`

## Verdict

- `v186`
  is not a no-op.
- It is also not a balanced continuation.
  The route clearly buys local blocker improvement,
  but it does so by giving back all four fixed keep or abstention guardrails.
- So this is a mechanism-real tradeoff reject,
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
  `v186`
  as:
  separate-reference-path keep-preserve tradeoff reject.
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - broader-path prerefine-base-align keep on top of
    `v179`
  - any keep-preserve route that changes only the reference path
    while still constraining the same final output degrees of freedom
- If this branch continues,
  the keep path must be orthogonal in both reference and output application,
  or the local objective must stop sharing the same final-output route.
