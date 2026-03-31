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

### `v217`

- Route:
  `v212 + branch_protect_teacher_overlap_weight 0.04`
  on
  `estimated_waveform_post_pre_present_controller`
  against the safe
  `v157`
  teacher
- Status:
  training-real practical tie but uniformly slightly worse
- Takeaway:
  overlap-only teacher keep on this disjoint route is not no-op,
  but the first low-weight launch only nudges all five fixed checks slightly wrong-way relative to
  `v212`

### `v218`

- Route:
  `v217` family with
  `branch_protect_teacher_overlap_weight = 0.2`
- Status:
  partial-guardrail-repair tradeoff evidence
- Takeaway:
  higher teacher-overlap pressure can claw back some guardrail margin relative to
  `v217`
  and
  `v212`,
  but it again gives back local blocker quality,
  so the route still stays on the same mild exchange surface rather than opening selectivity

### `v219`

- Route:
  `v212 + branch_overlap_cancel_head`
  added to the trainable keep path on the same
  `estimated_waveform_post_pre_present_controller`
  route
- Status:
  strong-guardrail strong-local-tradeoff reject
- Takeaway:
  widening the keep path through the same cancel estimate is not a no-op.
  It strongly improves the four non-blocker checks,
  but it also clearly worsens the local blocker,
  so this axis is just a steeper version of the same coupled tradeoff

### `v220 / v221`

- Route:
  `v212 + overlap_dual_residual_target_projection_weight`
  on the same
  `estimated_waveform_post_pre_present_controller`
  downstream route,
  with no path widening and no keep-objective changes
- Status:
  practical-tie local-objective scalar retune reject
- Takeaway:
  `v220 = 0.01`
  and
  `v221 = 0.02`
  are both training-real,
  but they stay near tie at the fixed-proxy resolution.
  So this scalar retune does not unlock a more selective local-blocker regime on top of
  `v212`.

### `v222 / v223 / v224`

- Route:
  `v212 + local-window waveform supervision on branch_overlap_dual_residual_correction_estimate_waveform`
  while keeping the same
  `estimated_waveform_post_pre_present_controller`
  downstream route
- Status:
  weak positive evidence below promotion
- Takeaway:
  this is the first local-objective continuation on the
  `v212`
  family that is clearly better aligned than the failed
  `v220 / v221`
  target-projection scalar.
  By
  `v224`,
  direct
  `v212 -> v224`
  deltas reached
  `+0.0260 / +0.0141 / +0.0169 / -0.0031 / +0.0149 dB`.
  But the simple weight sweep
  `0.5 -> 2.0 -> 8.0`
  still does not open a meaningful new regime,
  so further micro-sweeping of the same scalar is not the default next step.

### `v225`

- Route:
  `v224 + local-window supervision on branch_overlap_dual_residual_correction_controller`
  while keeping the writable residual-correction waveform objective unchanged
- Status:
  controller-local continuation reject
- Takeaway:
  the new controller-local term is training-real,
  but it worsens the fixed-proxy surface relative to
  `v224`.
  So explicit controller-local supervision is not an automatic next-step fix on this family.

### `v226 / v227`

- Route:
  `v224 + local-window waveform supervision on estimated_waveform_post_pre_present_controller`
  while keeping the writable residual-correction local-window waveform term active
- Status:
  writable-path-change evidence at
  `v226`,
  then higher-weight closure reject at
  `v227`
- Takeaway:
  `v226`
  showed that moving the local-window waveform objective onto the writable pre-present main-output route is real,
  not a no-op.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.0000 / -0.0193 / +0.0032 / -0.0157 / +0.0071 dB`.
  That was enough to justify one larger follow-up weight jump.
  `v227`
  then bounded the family:
  relative
  `v226`,
  fixed deltas became
  `-0.0891 / -0.0392 / -0.0513 / -0.0385 / +0.0251 dB`.
  So this writable-path change is informative,
  but the first
  `0.5 -> 2.0`
  sweep only steepens the same guardrail-versus-local exchange surface.

### `v228`

- Route:
  `v226 + local-window SI-SDR supervision on estimated_waveform_post_pre_present_controller`
  while keeping the same
  `extra_local_waveform_weight = 0.5`
  route active
- Status:
  local-objective continuation reject on the same writable pre-present main-output family
- Takeaway:
  the new interval-concatenated local SI-SDR term is training-real,
  but it does not create a new regime.
  Relative
  `v226`,
  direct fixed deltas became
  `-0.0900 / -0.0407 / -0.0519 / -0.0396 / +0.0253 dB`,
  which is effectively the same high-tradeoff shape already reached by
  `v227`.
  So changing the local objective from waveform L1 to SI-SDR on the same writable output path is not enough by itself.

### `v229`

- Route:
  `v226 + extra_prediction_source estimated_waveform_pre_dual_residual_correction`
  with the same trainable set as
  `v226`
- Status:
  later-output retarget reject
- Takeaway:
  moving the local supervision target farther downstream without opening that route's own writer
  does not help.
  Relative
  `v226`,
  direct fixed deltas became
  `-0.0151 / -0.0092 / -0.0167 / -0.0061 / -0.0009 dB`,
  so the output-position-only move is slightly negative.

### `v230`

- Route:
  `v229 + branch_overlap_refine_present_head`
  on the same later
  `estimated_waveform_pre_dual_residual_correction`
  supervision target
- Status:
  strong tradeoff reject on the later writable route
- Takeaway:
  reopening the first obvious writer on the later pre-dual route does not recover selectivity.
  Relative
  `v226`,
  direct fixed deltas became
  `-1.1727 / -0.9902 / -0.4938 / -0.7442 / +1.0956 dB`,
  so this axis just buys blocker gain by burning large guardrail margin.

### `v231`

- Route:
  `v226 + estimated_waveform_post_refine_present + branch_overlap_refine_present_head`
  with the same trainable writer shape as
  `v230`,
  but supervising before
  `branch_overlap_cancel_head`
- Status:
  pre-cancel writable-output reject on the same `refine_present` writer family
- Takeaway:
  removing the frozen cancel path from the local supervision target does not rescue the family.
  Relative
  `v230`,
  direct fixed deltas became
  `-0.2026 / -0.1462 / -0.1320 / -0.1930 / +0.0673 dB`,
  so the bad tradeoff is already present at the
  `refine_present`
  writer itself.

### `v232`

- Route:
  `v226 + direct local supervision on branch_overlap_cancel_pre_present_controller applied delta`
  while keeping the same writable pre-present family and trainable set as
  `v226`
- Status:
  applied-delta practical-tie continuation reject
- Takeaway:
  exporting and directly supervising the actual pre-present applied delta is clearly optimization-real,
  but it still does not improve the writable pre-present family.
  Relative
  `v226`,
  direct fixed deltas became
  `-0.0175 / -0.0068 / -0.0229 / +0.0135 / -0.0149 dB`,
  so this axis is another practical tie to slight negative continuation,
  not a new selective regime.

### `v233`

- Route:
  `v224 + local_prediction_source estimated_waveform_refine_base + branch_overlap_refine_head`
  while keep-side reconstruction still writes through
  `estimated_waveform_post_pre_present_controller`
- Status:
  local-only `refine_base` writer exchange-surface reject
- Takeaway:
  splitting keep and local supervision onto different writable outputs is not sufficient by itself.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.7918 / +0.0617 / +0.1080 / -0.4197 / +0.6625 dB`,
  so this first
  `branch_overlap_refine_head`
  local-only writer buys large blocker gain mainly by spending abstention and artifact margin.

### `v234`

- Route:
  `v224 + overlap_dual_residual_correction_local_sisdr_weight 0.001`
  on the same writable
  `branch_overlap_dual_residual_correction`
  estimate and trainable set as
  `v224`
- Status:
  local-window SI-SDR practical-tie-to-negative continuation reject
- Takeaway:
  the first more structural local-quality continuation on the writable residual-correction branch is clearly real,
  but it nudges the route slightly toward better non-blocker checks and slightly worse local blocker behavior.
  Relative
  `v224`,
  direct fixed deltas became
  `+0.0320 / +0.0118 / +0.0037 / +0.0441 / -0.0373 dB`,
  so this is not a useful blocker-positive regime.

### `v235`

- Route:
  `v224 + sparse controller selectivity`
  with local controller supervision inside
  `local_proxy_intervals`
  and complement-interval controller supervision outside them
- Status:
  sparse-controller practical-tie continuation reject
- Takeaway:
  the first controller-selectivity continuation on this writable residual-correction branch is clearly real,
  but it still does not improve the blocker.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.0055 / -0.0091 / -0.0054 / +0.0136 / -0.0040 dB`,
  so this axis stays in the same practical-tie basin rather than opening a new local-positive regime.

### `v236`

- Route:
  `v224 + branch_overlap_dual_decoder_head`
  while keeping the full
  `v224`
  loss unchanged
- Status:
  broader-upstream-predictor mild-tradeoff continuation reject
- Takeaway:
  the first upstream widening on this writable residual-correction branch is clearly real,
  but it does not open a new regime.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.0320 / -0.0320 / -0.0163 / -0.0203 / +0.0323 dB`,
  so unfreezing the upstream
  `branch_overlap_dual_decoder_head`
  only steepens the same mild guardrail-for-local surface instead of resolving the blocker.

### `v237`

- Route:
  `v212 + dedicated branch_overlap_dual_local_bridge writer`
  with keep-side supervision still on
  `estimated_waveform_post_pre_present_controller`
  and blocker-local waveform supervision moved onto
  `estimated_waveform_post_dual_local_bridge`
- Status:
  dedicated dual-local writer tradeoff reject
- Takeaway:
  the first dedicated dual-local bridge is clearly real,
  but it does not open a new selective regime.
  Relative
  `v212`,
  direct fixed deltas became
  `-0.2272 / -0.1451 / -0.1393 / -0.1284 / +0.0722 dB`,
  so this new writer still buys blocker gain mainly by spending guardrail margin.

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
- `branch_protect_teacher_overlap_weight` sweep on the same pre-present keep-output plus dual residual-correction family
- simple keep-path widening through `branch_overlap_cancel_head` on the same pre-present keep-output plus dual residual-correction family
- `overlap_dual_residual_target_projection_weight` retune on the same pre-present keep-output plus dual residual-correction family
- `overlap_dual_residual_correction_local_waveform_weight` micro-sweep on that same family
- `overlap_dual_residual_correction_local_controller_weight` micro-sweep on that same family
- `overlap_dual_residual_correction_local_sisdr_weight` retune on that same family
- sparse local plus nonlocal controller shaping on that same family
- simple upstream `branch_overlap_dual_decoder_head` widening on that same family
- first-launch dedicated `branch_overlap_dual_local_bridge` local-waveform continuation
- `extra_local_waveform_weight` micro-sweep on the writable pre-present main-output route
- `extra_local_sisdr_weight` micro-sweep on that same writable pre-present main-output route
- direct `pre_present_applied_delta_local_waveform_weight` continuation on that same writable pre-present family
- split-route local-only writer continuation through
  `estimated_waveform_refine_base`
  and
  `branch_overlap_refine_head`
- output-position-only retargeting to `estimated_waveform_pre_dual_residual_correction`
- simple `branch_overlap_refine_present_head` widening on that same later pre-dual writable route
- local-output retargeting through the same `branch_overlap_refine_present_head` writer, including `estimated_waveform_post_refine_present`

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
- a qualitatively different keep objective or a more structurally disjoint keep path on the same downstream route after `v219`
- a more structural local objective on the writable residual-correction branch after `v224`
- if the writable residual-correction line continues after `v234`,
  a route that does not only strengthen local-window quality on the same
  `branch_overlap_dual_residual_correction`
  estimate
- if the writable residual-correction line continues after `v235`,
  a route that does not only reshape the same
  `branch_overlap_dual_residual_correction_controller`
  with local versus complement sparsity targets
- if the writable residual-correction line continues after `v236`,
  a route that does not only widen the frozen upstream predictor through
  `branch_overlap_dual_decoder_head`
- if the dedicated dual-local bridge line continues after `v237`,
  a route that does not only retune the same first-launch local-waveform writer
- a more structural writable-path change than direct local-window waveform supervision on `estimated_waveform_post_pre_present_controller` after `v227`
- a materially different local objective on that same writable pre-present main-output route after `v228`
- if this writable-path line continues,
  a route that does not rely on the same
  `refine_present`
  writer at all
- if the writable pre-present line continues after
  `v232`,
  a route that does not rely only on direct applied-delta supervision through the same
  `pre_present_controller`
  writer
- if a split-route writable-path line continues after
  `v233`,
  a route that does not rely on
  `branch_overlap_refine_head`
  as the dedicated local-only writer
- a more structural writable-path change than direct local-window quality supervision on `estimated_waveform_post_pre_present_controller`
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
- Do not replay `v217` to `v218`-style teacher-overlap weight sweeps on that same disjoint-downstream family.
- Do not replay `v219`-style simple cancel-head widening on that same disjoint-downstream family.
- Do not replay `v222` to `v224`-style micro-sweeps of the same local-window residual-correction waveform weight by default.
- Do not replay `v225`-style micro-sweeps of the same local-window controller supervision weight by default.
- Do not replay `v226` to `v227`-style micro-sweeps of the same local-window pre-present main-output waveform weight by default.
- Do not replay `v228`-style micro-sweeps of the same local-window pre-present main-output SI-SDR weight by default.
- Do not replay `v229`-style output-position-only retargeting to the same later pre-dual writable route by default.
- Do not replay `v230`-style simple `branch_overlap_refine_present_head` widening on that same route by default.
- Do not replay `v231`-style pre-cancel writable-output continuation on that same `refine_present` writer family by default.
- Do not replay `v232`-style direct applied-delta supervision on that same writable pre-present family by default.
- Do not replay `v233`-style split-route local-only writer continuation through `estimated_waveform_refine_base` and `branch_overlap_refine_head` by default.
- Do not replay `v234`-style local-window SI-SDR continuation on the same writable residual-correction branch by default.
- Do not replay `v235`-style sparse local plus nonlocal controller shaping on the same writable residual-correction branch by default.
- Do not replay `v236`-style simple upstream dual-decoder widening on the same writable residual-correction branch by default.
- Do not replay `v237`-style first-launch dedicated dual-local bridge local-waveform continuation by default.
- Do not export listening packs from this family until the active local blocker turns the right way on fixed synthetic proxies.
