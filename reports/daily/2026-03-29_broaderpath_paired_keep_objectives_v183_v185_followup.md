# 2026-03-29 broader-path paired keep objectives on `v179`: `v183 / v184 / v185` follow-up

## Summary

- Goal:
  test whether the broader-path
  `v179`
  route can keep its local pullback while adding explicit keep-preserving supervision.
- `v183 = v179 + stronger pre-present keep weight`
  showed that more keep pressure on the same controller does not balance the route.
  It mostly erases the local pullback while giving back only a tiny amount of same-gender keep.
- `v184 = v179 + keep-critical reconstruction guard`
  is training-real and slightly better than
  `v183`,
  but it still trades away local blocker improvement for only a very small keep gain.
- `v185 = v179 + keep-critical branch-protect SI-SDR guard`
  is the strongest evidence point:
  direct keep-critical final-output guard dominates the route,
  pushes all keep or abstention guardrails strongly positive,
  and destroys the local blocker completely.
- New branch boundary:
  on this broader-path target-projection route,
  keep-preserving objectives that act on the same controller or the same final output do not balance the blocker.
  They suppress or overpower the local pullback instead.

## `v183 = v179 + gate_pre_present_keep_weight 6.0`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v183_v179_parallel_prepresent_targetproj002_keep6p0_v1_ft1`
- Intent:
  keep the
  `v179`
  local target-projection objective,
  but strengthen pre-present keep supervision on the same route.
- Training evidence:
  this is not a launch failure,
  but both key route signals collapse:
  final
  `val_overlap_cancel_target_projection_ratio = 2.56e-09`
  and
  `val_gate_pre_present_keep_mean = 1.31e-05`.

### Fixed Checks relative `v157`

- abstention `+1.4254 dB`
- same-gender keep `+0.0944 dB`
- hard-present keep `+1.3249 dB`
- artifact proxy `+0.9750 dB`
- local speech leak proxy `-2.0110 dB`

### Direct Comparison relative `v179`

- same-gender keep `+0.0424 dB`
- local speech leak proxy `-0.4003 dB`

### Verdict

- `v183`
  does not preserve the
  `v179`
  local pullback.
- Stronger keep pressure on the same controller mostly pushes the route back toward the
  `v178`
  keep-heavy regime.
- So the broader-path
  `gate_pre_present_keep_weight`
  axis is not a useful continuation.

## `v184 = v179 + keep-critical reconstruction guard`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v184_v179_targetproj002_keeprecon_gatekeepunion_v1_ft1`
- New keep selector:
  `data/synthetic/sample_ids_gate_keep_union_v2_all.txt`
- Selector coverage:
  `train 63 / 233, val 27 / 67`
- New losses:
  - `reconstruction_waveform_weight = 0.2`
  - `reconstruction_stft_weight = 0.1`
- Intent:
  move keep preservation off the controller and onto the final output on keep-critical samples.

### Fixed Checks relative `v157`

- abstention `+1.4188 dB`
- same-gender keep `+0.1296 dB`
- hard-present keep `+1.2889 dB`
- artifact proxy `+0.9864 dB`
- local speech leak proxy `-1.9200 dB`

### Direct Comparison relative `v179`

- same-gender keep `+0.0776 dB`
- local speech leak proxy `-0.3093 dB`

### Verdict

- `v184`
  is the first training-real keep-preserving pilot that acts on keep-critical final-output samples.
- It is slightly better than
  `v183`,
  but it still gives the wrong tradeoff:
  same-gender keep moves only a little,
  while the local blocker regresses on all
  `7 / 7`
  proxy samples.
- Therefore
  `v184`
  is still below gate and does not warrant near-real evaluation.

## `v185 = v179 + keep-critical branch-protect SI-SDR guard`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v185_v179_targetproj002_branchprotectkeep0003_v1_ft1`
- New keep selector:
  `data/synthetic/sample_ids_gate_keep_union_v2_all.txt`
- Selector coverage:
  `train 63 / 233, val 27 / 67`
- New loss:
  `branch_protect_guard_sisdr_weight = 0.003`
- Training evidence:
  final
  `val_branch_protect_guard_sisdr_loss = 0.9256`
  and
  `val_gate_keep_mean = 0.4632`,
  so this objective really moved the route.

### Fixed Checks relative `v157`

- abstention `+6.2479 dB`
- same-gender keep `+7.6566 dB`
- hard-present keep `+7.8479 dB`
- artifact proxy `+5.3301 dB`
- local speech leak proxy `-14.4915 dB`

### Direct Comparison relative `v179`

- same-gender keep `+7.6046 dB`
- local speech leak proxy `-12.8808 dB`

### Verdict

- `v185`
  proves that direct keep-critical final-output guard can dominate this route.
- But it dominates in exactly the wrong way for the active blocker:
  keep or abstention all surge positive,
  while the local blocker collapses catastrophically.
- So this is a strong mechanism-positive reject,
  not a candidate continuation.

## Final Verdict

- Keep
  `v157`
  as active base.
- Keep
  `v172`
  only as mechanism-positive evidence.
- Keep
  `v179`
  only as the best broader-path explicit-local-target evidence point.
- Mark:
  - `v183`:
    same-controller keep-reweight reject
  - `v184`:
    keep-critical reconstruction guard reject
  - `v185`:
    keep-critical final-output guard dominate-and-collapse reject
- No near-real evaluation and no listening pack are exported.

## Next Step

- Do not continue:
  - broader-path
    `gate_pre_present_keep_weight`
    sweep on top of
    `v179`
  - keep-critical reconstruction guard on top of
    `v179`
  - keep-critical
    `branch_protect_guard_sisdr`
    guard on top of
    `v179`
- If this branch continues,
  keep preservation must become orthogonal to the local objective.
- The next valid options are:
  - keep-preserve supervision on a separate reference path or outside the local-blocker windows
  - a different local objective that does not share the same final-output degrees of freedom
  - only if needed, a larger route change with disjoint keep and local supervision paths
