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

### `v191`

- Route:
  `v190 + branch_overlap_dual_monitor_controller + monitor_max_blend 0.02`
- Status:
  positive-all-guardrails monitor-coupling evidence, still reject for promotion
- Takeaway:
  the coupling path is real and safe on fixed synthetic guardrails,
  but the local blocker stayed near exact tie;
  the monitor head is writing to output,
  but not yet selectively enough inside the blocker windows

### `v192`

- Route:
  `v191 + gate_supervision_source overlap_dual_monitor_controller`
- Status:
  direct monitor-controller supervision reject
- Takeaway:
  direct absent and overlap supervision on the existing monitor head
  still did not align the coupling with the local blocker;
  the four non-blocker checks improved slightly,
  but the local blocker regressed relative to `v191`

### `v193`

- Route:
  `v192 + audibility gate target on overlap_dual_monitor_controller`
- Status:
  practical no-op reject
- Takeaway:
  the monitor head was already effectively sitting at the frozen
  `branch_overlap_dual_controller`
  ceiling on the active blocker set,
  so a head-only monitor target had almost no remaining freedom;
  the four non-blocker checks moved only
  `~+0.0003 to +0.0004 dB`,
  while the local blocker still regressed

### `v194`

- Route:
  `v193 + local current-output residual interval loss on the monitor-applied correction path`
  with
  `branch_overlap_dual_decoder_head + branch_overlap_dual_monitor_controller_head`
  trainable
- Status:
  local monitor-residual reject
- Takeaway:
  even blocker-specific monitor correction on a widened trainable path
  still improved the four non-blocker checks
  while regressing the active local blocker;
  the small-blend monitor family remains misaligned with the blocker

### `v195`

- Route:
  `v194 + branch_overlap_dual_monitor_max_blend 0.08`
- Status:
  higher-blend monitor closure reject
- Takeaway:
  stronger monitor coupling does not unlock local selectivity;
  it amplifies the same pattern:
  four non-blocker checks improve more,
  while the active local blocker gets much worse.
  This closes the monitor family rather than extending it.

### `v196`

- Route:
  intended
  `v190 + branch_overlap_cancel_apply_controller` distill from
  `branch_overlap_dual_controller`
- Status:
  invalid no-op semantics audit
- Takeaway:
  under the active
  `current_output`
  no-write dual semantics,
  the intended teacher tensor was not materialized,
  so the run stayed exact tie to both
  `v157`
  and
  `v190`

### `v197`

- Route:
  `v190 + actual apply-controller distill from materialized dual controller`
- Status:
  live teacher-bridge tradeoff reject
- Takeaway:
  this is the first version of the family that really moves the blocker
  (`local_speech_leak_proxy_v1 +0.1082 dB`),
  but it spends guardrail margin in the wrong direction
  (`abstention / same-gender / hard-present / artifact = -0.1949 / -0.0839 / -0.0889 / -0.0736 dB`)

### `v198`

- Route:
  `v197` with
  `overlap_dual_controller_distill_weight = 0.5`
- Status:
  practical tie calibration reject
- Takeaway:
  simple distill-weight reduction did not open a new regime;
  it landed in practical tie to
  `v197`

### `v199`

- Route:
  `v190 + dual-controller distill into branch_overlap_cancel_pre_present_controller`
- Status:
  safe near-no-op reject
- Takeaway:
  this write-back location is safer than the pure apply-controller bridge,
  but it collapses into a weak regime:
  the four non-blocker checks stay slightly positive,
  while the active local blocker still regresses slightly

### `v200`

- Route:
  `v199 + branch_overlap_cancel_head` joint unfreeze
- Status:
  exact-tie closure reject
- Takeaway:
  adding the cancel head back to the same pre-present teacher-bridge route
  does not reopen the basin;
  direct
  `v199 -> v200`
  compare is
  `0.0 dB`
  on all five fixed proxies

### `v201`

- Route:
  `v190 + branch_overlap_dual_decoder_apply_mode gate_controller`
  with
  `branch_overlap_dual_decoder_gate_mode = gate`
  and
  `branch_overlap_dual_decoder_max_blend = 0.02`
- Status:
  old-family collapse reject
- Takeaway:
  this route is training-real on the intended local selector,
  but it lands in practical tie to
  `v188`;
  direct gate rewrite from the dual route is not a new selective regime

### `v202`

- Route:
  `v201` family with explicit
  `branch_overlap_dual_controlled_gate`
  output and
  `gate_supervision_source = overlap_dual_controlled_gate`
- Status:
  controlled-gate tie closure reject
- Takeaway:
  even after gate supervision is attached to the actual rewritten gate,
  the family still lands in practical tie to
  `v201`;
  the route is fully closed rather than merely miswired

### `v203`

- Route:
  `v190 + dual-conditioned cancel-controller head-only`
  with
  `branch_overlap_dual_cancel_max_blend = 0.02`
- Status:
  safe practical near-no-op reject
- Takeaway:
  the new controller is training-real,
  but writing no-write dual evidence back through the existing overlap-cancel estimate path
  moves the four non-blocker checks only slightly positive
  while the active local blocker still regresses slightly

### `v204`

- Route:
  `v203` family with
  `branch_overlap_dual_cancel_max_blend = 0.08`
- Status:
  higher-blend tiny-direction replication reject
- Takeaway:
  stronger write-back only amplifies the same tiny
  guardrail-positive / local-negative
  direction;
  it does not open a new regime

### `v205`

- Route:
  `v203` family with
  `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head`
  trainable
- Status:
  joint dual-head tie closure reject
- Takeaway:
  small widening above the new controller stays practical tie to
  `v203`;
  the issue is not just a frozen-upstream ceiling

### `v206`

- Route:
  `v190 + dual residual-correction head-only`
  with
  `branch_overlap_dual_residual_correction_max_blend = 0.02`
- Status:
  safe practical near-no-op evidence
- Takeaway:
  this is the first dual no-write evidence family here that turns the active local blocker
  slightly the right way,
  but the movement is still too small to matter

### `v207`

- Route:
  `v206` family with
  `branch_overlap_dual_residual_correction_max_blend = 0.08`
- Status:
  blocker-positive but guardrail-negative tradeoff reject
- Takeaway:
  higher blend amplifies a real direction,
  but that direction spends guardrail margin to buy local blocker gain

### `v208`

- Route:
  `v207` family with
  `branch_overlap_dual_decoder_temporal_model + branch_overlap_dual_decoder_head`
  jointly trainable
- Status:
  widened-tradeoff closure reject
- Takeaway:
  upstream widening does not recover selectivity;
  it only moves farther along the same local-positive and guardrail-negative surface

### `v209`

- Route:
  `v206 + branch_protect_overlap_base_align_weight 0.01`
  on
  `gate_keep_union_v2`
  while keeping the same residual-correction heads trainable
- Status:
  same-head keep-backstop collapse reject
- Takeaway:
  even a weak keep-preserve term can destroy the route
  if it backpropagates through the same dual residual-correction heads;
  selector disjointness alone is not enough

### `v210`

- Route:
  `v206 + prerefine keep-bypass on pre-dual output`
  with
  `branch_overlap_refine_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  trainable
- Status:
  trainable-path-disjoint keep-bypass collapse reject
- Takeaway:
  even when the keep-preserve path is disjoint in trainable modules,
  the route can still collapse if both objectives remain coupled through the same downstream branch behavior;
  trainable-path disjointness alone is not enough

### `v211`

- Route:
  `v206 + pre-present keep-output path on estimated_waveform_post_pre_present_controller + dual residual-correction`
  with
  `branch_overlap_cancel_pre_present_controller_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  trainable
- Status:
  disjoint-downstream keep-output safe-but-local-negative evidence
- Takeaway:
  this is the first continuation on top of the dual residual-correction family
  that is disjoint both in trainable path and in downstream output application.
  It avoids the catastrophic collapse seen in
  `v209` and `v210`,
  keeps all four non-blocker checks positive,
  and only mildly regresses the active local blocker

### `v212`

- Route:
  `v211` family with
  `branch_overlap_dual_residual_correction_max_blend = 0.08`
- Status:
  higher-local-blend near-tie tradeoff evidence
- Takeaway:
  stronger local correction no longer collapses the family;
  it moves onto a gentler local-versus-guardrail tradeoff surface,
  with the blocker recovering toward tie
  while the four non-blocker checks slip only slightly negative

### `v213`

- Route:
  `v212` family with
  `reconstruction_extra_waveform_weight = 0.4`
  and
  `reconstruction_extra_stft_weight = 0.2`
- Status:
  keep-weight-strengthening practical tie closure
- Takeaway:
  doubling the keep-output weights on this new disjoint route
  is practical tie to
  `v212`,
  so the first simple keep-weight axis on this family is closed

### `v214`

- Route:
  `v212 + branch_protect_guard_sisdr_weight 0.0002`
  on the same
  `estimated_waveform_post_pre_present_controller`
  route
- Status:
  optimization-real practical tie evidence
- Takeaway:
  the first more expressive keep objective on this disjoint route is active,
  but output-side it stays practical tie to
  `v212`

### `v215`

- Route:
  `v214` family with
  `branch_protect_guard_sisdr_weight = 0.001`
- Status:
  higher-weight practical tie evidence
- Takeaway:
  increasing guard-SI-SDR pressure mostly raises optimization loss,
  not fixed-proxy behavior

### `v216`

- Route:
  `v215` family with
  `branch_protect_guard_sisdr_weight = 0.003`
- Status:
  guard-SI-SDR sweep closure
- Takeaway:
  even the old stronger weight scale stays in the same practical-tie basin,
  so the tested guard-SI-SDR weight sweep is closed on this family

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
- direct `overlap_dual_monitor_controller` supervision alone on top of `v191`
- audibility-style gate target on top of `v192`
- local current-output residual interval supervision on the small-blend monitor family
- higher-blend continuation on the monitor family
- naive dual-teacher launch without a materialized controller teacher
- pure apply-controller dual-teacher distill on top of `v190`
- simple distill-weight retune on that same apply-controller dual-teacher family
- head-only pre-present dual-teacher distill on top of `v190`
- joint `branch_overlap_cancel_head + pre-present controller` widening on that same family
- direct dual `gate_controller` coupling on top of `v190`
- explicit controlled-gate supervision on that same direct dual `gate_controller` family
- dual-conditioned cancel-controller head-only coupling on top of `v190`
- higher-blend continuation on that same dual-conditioned cancel-controller family
- joint `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head` widening on that same family
- dual residual-correction head-only coupling on top of `v190`
- higher-blend continuation on that same dual residual-correction family
- joint dual-path widening on that same family
- same-head keep-backstop continuation on that same dual residual-correction family
- prerefine keep-bypass continuation on that same dual residual-correction family
- simple keep-output weight strengthening on the same pre-present keep-output plus dual residual-correction family
- `branch_protect_guard_sisdr_weight` sweep on the same pre-present keep-output plus dual residual-correction family

## Next Valid Branches

- a different local objective that does not share the same final-output degrees of freedom
- keep-preserve supervision outside the local-blocker windows only if it does not still rewrite the same final-output path
- a path whose local objective is not capped by the current monitor-correction route
- a coupling path that reads the no-write dual auxiliary evidence without writing only through
  `branch_overlap_cancel_apply_controller`
- a coupling path that is more expressive than the current pre-present controller bridge
- a coupling path that does not directly rewrite the existing `branch_decoder_frame_gate`
- a coupling path that does not write back only through the existing overlap-cancel estimate path
- a route that adds a disjoint keep-preserve path outside the blocker windows
  instead of only scaling the same dual residual-correction write-back
- a route whose keep-preserve path is disjoint in trainable modules,
  not only in sample selector
- a route whose keep-preserve path is disjoint both in trainable modules and in downstream output application
- a more expressive keep path on the same disjoint downstream route used by `v211` to `v213`
- a qualitatively different keep objective on the same disjoint downstream route after `v216`
- only if needed, a materially larger path change with disjoint keep and local supervision paths

## Immediate Rules

- Keep `v157` as the active base.
- Keep `v172` as the evidence point.
- `v191` remains the structural monitor-coupling evidence point.
- Do not replay `v192`-style direct monitor supervision alone.
- Do not replay `v193`-style audibility target on the same small-blend monitor head.
- Do not replay `v194`-style small-blend local monitor correction by default.
- Do not replay `v195`-style higher-blend continuation on the same monitor family.
- Do not read a `v196`-style dual-teacher run without first checking that the teacher tensor exists.
- Do not replay `v197`-style pure apply-controller dual-teacher distill by default.
- Do not replay `v198`-style simple weight halving on the same family.
- Do not replay `v199`-style head-only pre-present dual-teacher distill by default.
- Do not replay `v200`-style joint-cancel widening on the same pre-present family.
- Do not replay `v201`-style direct dual gate rewrite by default.
- Do not replay `v202`-style controlled-gate-supervised direct dual gate rewrite by default.
- Do not replay `v203`-style head-only dual-conditioned cancel-controller coupling by default.
- Do not replay `v204`-style higher-blend continuation on that same family.
- Do not replay `v205`-style joint dual-head widening on that same family.
- Do not replay `v206`-style small-blend dual residual-correction continuation by default.
- Do not replay `v207`-style higher-blend continuation on that same family.
- Do not replay `v208`-style joint dual-path widening on that same family.
- Do not replay `v209`-style same-head keep backstop on that same family.
- Do not replay `v210`-style prerefine keep bypass on that same family.
- Do not replay `v213`-style simple keep-output weight doubling on that same disjoint-downstream family.
- Do not replay `v214` to `v216`-style guard-SI-SDR weight sweeps on that same disjoint-downstream family.
- Do not export listening packs from this family until the active local blocker turns the right way on fixed synthetic proxies.
