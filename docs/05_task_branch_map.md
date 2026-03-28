# Task Branch Map

## Role

- This file tracks only the active branch structure that matters for the next decision.
- This file must remain English-only and ASCII-only.

## Main Line

- Active base:
  `v157`
- Meaning:
  best current automatic continuation on the interval-veto family
- Status:
  still the default comparison point for new work

## Evidence Branch

### `v172`

- Route:
  `v157 + parallel pre-present total-risk controller`
- Status:
  mechanism-positive evidence point
- Why it matters:
  all four fixed keep or abstention guardrails stayed positive,
  `near_real_0007 total leak` improved,
  and `near_real_0009` absent whole leak improved
- Why it did not promote:
  `near_real_0007` whole and speech-only still failed

### `v173`

- Route:
  lower `pre_present_max_blend`
- Status:
  closed calibration branch
- Takeaway:
  simple amplitude shrink only scales good and bad together

### `v174` and `v175`

- Route:
  selectivity micro-tuning on the same controller
- Status:
  practical no-op branch
- Takeaway:
  controller floor and same-head outside-overlap abstain supervision do not move output meaningfully

### `v176`

- Route:
  joint unfreeze of `branch_overlap_cancel_head` with the same pre-present controller
- Status:
  practical no-op branch
- Takeaway:
  small local unfreeze around the same route is not enough

## Broader Pre-Present Branch

### `v177`

- Route:
  broader-path continuation attempt with
  `branch_decoder_temporal_model + branch_decoder_gate_head + branch_overlap_cancel_head + branch_overlap_cancel_pre_present_controller_head`
- Status:
  invalid scratch
- Reason:
  selector bundle was omitted

### `v178`

- Route:
  same broader-path trainable set, with selector restored
- Status:
  strong-tradeoff reject
- Good:
  large gains on keep and abstention fixed guardrails
- Bad:
  severe regression on `local_speech_leak_proxy_v1`

### `v179`

- Route:
  `v178 + overlap_cancel_target_projection_weight 0.02`
- Status:
  explicit-local-target mechanism-positive reject
- Good:
  local blocker moved partly back in the correct direction
- Bad:
  same-gender keep margin dropped sharply

### `v180`

- Route:
  `v178 + overlap_cancel_target_projection_weight 0.01`
- Status:
  practical tie to `v179`
- Takeaway:
  projection-weight calibration is not the useful axis here

### `v181`

- Route:
  `v178 + overlap_cancel_waveform_weight 0.02`
- Status:
  waveform-local global-collapse reject
- Takeaway:
  direct waveform-local overlap-cancel supervision blows up both keep and local blocker metrics together

### `v182`

- Route:
  `v178 + overlap_cancel_waveform_weight 0.002`
- Status:
  lower-weight replication that closes the waveform-local sweep
- Takeaway:
  lowering the waveform-local weight by
  `10x`
  does not restore the route

### `v183`

- Route:
  `v179 + gate_pre_present_keep_weight 6.0`
- Status:
  same-controller keep-reweight reject
- Takeaway:
  stronger keep pressure on the same controller erases local pullback faster than it restores keep

### `v184`

- Route:
  `v179 + keep-critical reconstruction guard on gate_keep_union_v2`
- Status:
  keep-critical reconstruction-guard reject
- Takeaway:
  direct final-output reconstruction guard is training-real,
  but still gives only a small keep gain for a wrong-way local regression

### `v185`

- Route:
  `v179 + keep-critical branch_protect_guard_sisdr 0.003`
- Status:
  keep-critical final-output guard dominate-and-collapse reject
- Takeaway:
  direct keep-critical final-output guard can dominate this route,
  but it dominates in the wrong way and destroys the local blocker

### `v186`

- Route:
  `v179 + branch_protect_overlap_base_align_weight 0.04 + use_branch_prerefine_as_primary_prediction`
- Status:
  separate-reference-path keep-preserve tradeoff reject
- Takeaway:
  a separate keep reference is not enough
  if the route still spends the same final-output degrees of freedom;
  local blocker quality improves,
  but all four fixed keep or abstention guardrails regress

### `v187`

- Route:
  `v179 + branch_overlap_cancel_apply_mode auxiliary_only`
- Status:
  auxiliary-only shared-route drift reject
- Takeaway:
  decoupling direct output rewrite alone is not enough;
  the intended local auxiliary signal collapses,
  while the shared broader-path route drifts back toward keep-heavy behavior

### `v188`

- Route:
  `v157 + overlap_dual auxiliary path with final_output and max_blend 0`
- Status:
  dual final-output zero-blend semantic reject
- Takeaway:
  `final_output + max_blend 0`
  is not a non-writing auxiliary mode;
  it rewrites output toward branch base

### `v189`

- Route:
  `v157 + overlap_dual auxiliary path with current_output and max_blend 0`
- Status:
  true no-write auxiliary evidence but trivial-objective no-op
- Takeaway:
  a truly disjoint non-writing auxiliary path now exists,
  but the current dual objective pair collapses to the zero-residual trivial solution

### `v190`

- Route:
  `v157 + overlap_dual current_output max_blend 0 + residual_waveform_weight 0.02`
- Status:
  non-trivial no-write auxiliary local-path evidence
- Takeaway:
  the no-write dual auxiliary path can be genuinely training-real,
  but it still needs a separate coupling path before it can affect output behavior

## Closed Branch Families

- `predicted_activity` direct-apply family
- `apply-controller` direct-subtract family
- split keep or absent controller family
- no-teacher sparse `refine_base` sibling family
- `branch_base_blend` family
- `refine_base_blend` family
- plain `pre_present_subtract`
- pre-present max-blend and controller-floor calibration
- same-head outside-overlap abstain reweight
- cancel-head plus controller joint unfreeze alone
- target-projection weight sweep
- broader-path waveform-local weight sweep
- broader-path `gate_pre_present_keep_weight` sweep on top of `v179`
- broader-path keep-critical reconstruction guard on top of `v179`
- broader-path keep-critical `branch_protect_guard_sisdr` guard on top of `v179`
- broader-path prerefine-base-align keep on top of `v179`
- broader-path `auxiliary_only` target projection on top of `v179`
- `dual final_output + max_blend 0` as a supposed non-writing auxiliary path
- no-write `overlap_dual_mix_consistency + overlap_dual_residual_target_projection` on the active local blocker

## Next Valid Branches

- a different local objective that does not share the same final-output degrees of freedom
- keep-preserve supervision outside the local-blocker windows only if it does not still rewrite the same final-output path
- a non-trivial local objective on a truly disjoint trainable auxiliary path
- a separate coupling path that reads a proven non-trivial auxiliary local predictor
- only if needed, a materially larger path change with disjoint keep and local supervision paths

## Immediate Rules

- Keep `v157` as the active base.
- Keep `v172` as the evidence point.
- Do not export listening packs from this family until the active local blocker turns the right way on fixed synthetic proxies.
