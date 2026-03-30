# Pitfalls Log

## Role

- This file keeps only active pitfalls that still affect daily work.
- This file must remain English-only and ASCII-only.

## Active Pitfalls

### 0. PowerShell text decoding on this machine is unsafe by default

- Repo docs and reports are UTF-8 on disk.
- Default PowerShell text reads can render UTF-8 files as GBK-decoded text.
- The visible console mojibake does not automatically mean the file on disk is corrupted.
- Even when PowerShell is forced to UTF-8 for writing, it can add a BOM that this repo does not want.
- Rule:
  read with explicit UTF-8 when needed, and do not use PowerShell text write APIs for repo docs.
- Rule:
  use `apply_patch` for doc writes so files stay BOM-free.

### 1. Active docs and active reports must stay English-only and ASCII-only

- This is now a hard convention.
- The rule applies even when the user talks to the assistant in Chinese.
- User-facing assistant replies stay Simplified Chinese.
- On-disk active docs stay English-only and ASCII-only.

### 2. Byte-level audit matters more than shell rendering

- The active doc audit on `2026-03-28` found no BOM in the active docs.
- The same audit found no on-disk mojibake in the active docs that were checked.
- The encoding problem observed this turn was a shell read or render problem, not a file-by-file corruption event.

### 3. Teacher metadata fallback must be handled explicitly

- The training entry can inherit `teacher_checkpoint` metadata from the init checkpoint.
- That fallback can silently turn a supposed no-teacher run into a teacher-backed run.
- Rule:
  always set `--disable-teacher-checkpoint-metadata-fallback` unless inherited teacher behavior is intentionally wanted.

### 4. Selector restoration is mandatory before comparing continuation runs

- `v177` became invalid scratch because the `overlap_cancel` selector bundle was omitted.
- That made `train_selector_metrics.overlap_cancel.active = false` and collapsed targeted supervision.
- Rule:
  when cloning an earlier route, restore the exact selector bundle before interpreting the run.

### 5. Practical no-op must be checked with direct compare, not only training metrics

- `v174`, `v175`, and `v176` all changed training-side metrics but barely moved output.
- Rule:
  after any training-real continuation that looks suspiciously unchanged, compare directly against the parent checkpoint on a small fixed proxy set.

### 6. Do not run near-real if fixed synthetic gate already fails clearly

- `v178`, `v179`, and `v180` all failed the active local blocker at the fixed synthetic stage.
- Rule:
  if the active blocker is clearly wrong-way on fixed synthetic proxies, stop there and do not spend time on near-real.

### 7. Broader pre-present decision source can improve keep while breaking the blocker

- `v178` strongly improved all keep or abstention guardrails.
- The same run badly regressed `local_speech_leak_proxy_v1`.
- The failure mode is now explicit:
  stronger keep behavior does not imply the local blocker is solved.

### 8. Explicit local target projection is real, but current weight calibration is not enough

- `v179` showed that `overlap_cancel_target_projection_weight = 0.02` can pull the local blocker partly back.
- The cost was a large give-back on same-gender keep.
- `v180` showed that lowering the weight to `0.01` is practical tie to `v179`.
- Rule:
  do not keep sweeping `overlap_cancel_target_projection_weight`.

### 9. Broad-path waveform-local overlap-cancel can collapse the whole route

- `v181` and `v182` both strongly failed every active fixed proxy.
- The failure remained after lowering
  `overlap_cancel_waveform_weight`
  by
  `10x`.
- Rule:
  do not sweep
  `overlap_cancel_waveform_weight`
  on top of the broader pre-present route.

### 10. Broad-path paired keep objectives can suppress or overpower local pullback

- `v183` showed that stronger pre-present keep reweight on top of
  `v179`
  only recovered
  `+0.0424 dB`
  of same-gender keep while regressing the local blocker
  `-0.4003 dB`.
- `v184` showed that keep-critical reconstruction guard is training-real,
  but still regresses the local blocker
  `-0.3093 dB`
  relative to
  `v179`
  for only
  `+0.0776 dB`
  same-gender keep recovery.
- `v185` showed that direct keep-critical
  `branch_protect_guard_sisdr`
  can dominate the route:
  same-gender keep jumped
  `+7.6046 dB`
  relative to
  `v179`,
  while the local blocker collapsed
  `-12.8808 dB`.
- Rule:
  do not continue paired keep objectives that act on the same controller or the same final output path
  on top of the broader-path
  `v179`
  target-projection route.

### 11. Separate keep reference alone is not enough if final-output degrees of freedom stay shared

- `v186` showed that prerefine-base keep alignment is training-real:
  `branch_protect train 63 / 233, val 27 / 67`
  and final
  `val_branch_protect_overlap_base_align_l1 = 0.0008964`.
- But relative to
  `v179`,
  it still regressed every keep or abstention guardrail
  (`-3.0676 / -0.7755 / -1.7387 / -1.6118 dB`)
  while improving the local blocker
  `+2.6262 dB`.
- Relative to
  `v157`,
  all four fixed keep or abstention guardrails were still negative
  (`-1.7370 / -0.7234 / -0.5724 / -0.6573 dB`).
- Rule:
  do not continue broader-path keep-preserve routes that only change the reference path
  while still constraining the same final output degrees of freedom.

### 12. Auxiliary-only apply mode is still not enough if the trainable route stays shared

- `v187` removed direct output rewrite through
  `branch_overlap_cancel_apply_mode = auxiliary_only`,
  but the branch still moved in the wrong direction:
  relative to
  `v157`,
  keep or abstention guardrails improved
  (`+1.4179 / +0.1285 / +1.2877 / +0.9857 dB`)
  while the local blocker regressed
  `-1.9193 dB`.
- Relative to
  `v179`,
  same-gender keep recovered only
  `+0.0765 dB`
  while the local blocker regressed
  `-0.3086 dB`.
- Training-side the intended local path collapsed to near zero:
  final
  `val_overlap_cancel_target_projection_ratio = 2.58e-09`
  and
  `val_gate_pre_present_keep_mean = 1.64e-05`.
- Rule:
  do not continue broader-path
  `auxiliary_only`
  local routes
  if they still backpropagate through the same trainable temporal or gate modules.

### 13. Dual auxiliary semantics and loss choice need separate validation

- `v188` showed that
  `branch_overlap_dual_decoder_apply_mode = final_output`
  with
  `max_blend = 0`
  is not a non-writing auxiliary mode.
  Relative to
  `v157`,
  all fixed keep or abstention guardrails regressed
  while the local blocker improved
  (`-3.2585 / -2.4507 / -2.0340 / -1.8415 / +0.7581 dB`).
- `v189` corrected the semantics:
  `branch_overlap_dual_decoder_apply_mode = current_output`
  with
  `max_blend = 0`
  is exact tie to
  `v157`
  on all five active fixed checks.
- But `v189` also showed that the current no-write dual objective pair is trivial:
  the selector is active
  (`train 33 / 233, val 7 / 67`),
  yet
  `overlap_dual_mix_consistency_l1`
  and
  `overlap_dual_residual_target_projection_ratio`
  stay exact
  `0.0`.
- Rule:
  do not treat
  `dual final_output + max_blend 0`
  as a non-writing auxiliary mode,
  and do not continue the current no-write dual objective pair on this blocker.

### 14. A non-writing auxiliary path still needs a separate coupling mechanism

- `v190` showed that the dual auxiliary path can be both:
  - truly non-writing at inference
  - non-trivial during training
- Evidence:
  relative to
  `v157`,
  all five fixed checks are exact
  `0.0 dB`,
  while final
  `val_overlap_dual_residual_waveform_l1 = 0.015926`
  with selector coverage
  `train 33 / 233, val 7 / 67`.
- Rule:
  once a no-write auxiliary path is proven non-trivial,
  do not keep replaying no-write training-only runs.
  The next step must add a separate coupling path back to output behavior.

### 15. `v157` is still the active base even after stronger-looking branches

- `v172` is useful evidence, not promotion.
- `v178` looked stronger on several fixed guardrails, but it was wrong-way on the active local blocker.
- Rule:
  do not replace the active base just because a branch wins on keep or abstention alone.

### 16. Monitor coupling at small blend is real but not yet locally selective

- `v191` showed that `branch_overlap_dual_monitor_max_blend = 0.02` on top of the frozen `v190` dual decoder
  produces a genuinely real output coupling:
  relative to `v190` (exact `0.0` on all five checks),
  all five fixed synthetic deltas turned nonzero positive.
- But the local blocker (`local_speech_leak_proxy_v1`) moved only `+0.0008 dB`,
  effectively a tie.
- The monitor head learned a general output-suppression signal,
  not a locally targeted one.
- Rule:
  do not treat small-blend monitor coupling as equivalent to local-blocker improvement;
  a local-blocker-specific objective on the monitor path is still needed.

### 17. The direct monitor-supervision path already exists

- The repository already exposes
  `branch_overlap_dual_monitor_controller`
  in model outputs.
- The train and eval entry already accept
  `gate_supervision_source = overlap_dual_monitor_controller`.
- The `overlap_dual` selector path is already compatible with the active local blocker sample set.
- The handoff restore on `2026-03-30` also found that
  `data/manifests/`
  was too broad for small selector id metadata;
  a narrow allowlist was needed for
  `data/manifests/selectors/**/*.txt`.
- Rule:
  before adding new code for monitor-local supervision,
  first check whether the next branch can be launched by command and selector changes alone.

### 18. Direct monitor-controller supervision alone can still miss the blocker

- `v192` reused the safe `v191` coupling path and switched
  `gate_supervision_source`
  to
  `overlap_dual_monitor_controller`
  with the proven local-blocker selector.
- Relative to `v191`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all improved slightly
  (`+0.0151 / +0.0078 / +0.0043 / +0.0039 dB`),
  but `local_speech_leak_proxy_v1` regressed
  `-0.0149 dB`.
- The frozen dual auxiliary predictor stayed intact:
  `val_overlap_dual_residual_waveform_l1 = 0.015926`,
  same as `v190` and `v191`.
- Rule:
  do not assume that moving gate supervision directly onto the monitor head
  is enough to make the coupling locally selective.
  It can still strengthen general safe suppression
  while missing the local blocker.

### 19. A head-only monitor target can become a practical no-op once the ceiling is already hit

- `v193` added an audibility-style gate target on top of `v192`,
  but it changed the four non-blocker checks only
  `~+0.0003 to +0.0004 dB`
  and regressed the local blocker
  `-0.0004 dB`.
- On the active local blocker set,
  `branch_overlap_dual_monitor_controller`
  was already almost equal to the frozen
  `branch_overlap_dual_controller`
  ceiling:
  mean about
  `0.1122`
  versus
  `0.1136`.
- So a head-only target on the same path had almost no remaining degrees of freedom.
- Rule:
  before launching another monitor-head-only target branch,
  check whether the trainable head is already saturating against a frozen upstream ceiling.

### 20. Even blocker-specific monitor correction can still move in the wrong direction

- `v194` widened training to
  `branch_overlap_dual_decoder_head + branch_overlap_dual_monitor_controller_head`
  and added a local interval objective on the actual monitor-applied correction path.
- The target had to be defined against the current output residual
  (`prediction - target`),
  not full interference,
  because
  `monitor_max_blend = 0.02`
  makes the monitor path only a small correction route.
- This branch was training-real:
  `val_overlap_dual_monitor_waveform_l1 = 0.004913`.
- But relative `v193`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all improved
  (`+0.0128 / +0.0078 / +0.0065 / +0.0043 dB`),
  while `local_speech_leak_proxy_v1` regressed
  `-0.0117 dB`.
- Rule:
  do not assume that making the monitor objective blocker-specific is enough.
  The same family can still keep rewarding broader safe suppression
  more than the active local blocker.

### 21. Higher monitor blend closes the family in the same wrong direction

- `v195` raised
  `branch_overlap_dual_monitor_max_blend`
  from
  `0.02`
  to
  `0.08`
  on top of the already training-real
  `v194`
  route.
- Relative `v194`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all improved again
  (`+0.0777 / +0.0488 / +0.0309 / +0.0231 dB`),
  while `local_speech_leak_proxy_v1` regressed another
  `-0.0872 dB`.
- Relative `v157`,
  the local blocker reached
  `-0.1134 dB`,
  and hard-present keep even picked up
  `1`
  regressed sample.
- Rule:
  do not continue this monitor family with more blend sweeps or target variants.
  Higher coupling strength does not restore local selectivity here;
  it amplifies the same wrong behavior.

### 22. A conditionally missing teacher signal can silently turn a continuation into an exact no-op

- `v196` tried to distill
  `branch_overlap_cancel_apply_controller`
  from
  `branch_overlap_dual_controller`
  on top of
  `v190`.
- But under
  `branch_overlap_dual_decoder_apply_mode = current_output`
  with no monitor head,
  the model did not emit
  `branch_overlap_dual_controller`
  at all.
- The new loss weight was present in config,
  but the teacher tensor was absent,
  so the run stayed exact tie to both
  `v157`
  and
  `v190`
  on all five fixed checks.
- Rule:
  before trusting a new teacher-style continuation,
  verify that the intended teacher tensor is actually materialized
  under the active model semantics.

### 23. Pure apply-controller distill can move the blocker, but it spends guardrail margin through the same route

- After materializing
  `branch_overlap_dual_controller`
  for the no-write dual path,
  `v197`
  became the first live teacher-bridge continuation on top of
  `v190`.
- It was training-real:
  final
  `val_overlap_dual_controller_distill_l1 = 0.113235`.
- Relative
  `v157`,
  the local blocker improved
  `+0.1082 dB`,
  but abstention, same-gender keep, hard-present keep, and artifact proxy regressed
  `-0.1949 / -0.0839 / -0.0889 / -0.0736 dB`.
- `v198`
  lowered
  `overlap_dual_controller_distill_weight`
  from
  `1.0`
  to
  `0.5`
  and landed in practical tie to
  `v197`.
- Rule:
  do not keep sweeping plain apply-controller dual-teacher distill weights by default.
  This family now looks like another shared-route tradeoff,
  not a new selective regime.

### 24. Pre-present dual-teacher write-back is safer, but it collapses toward no-op

- `v199`
  redirected the same dual-controller distill signal into
  `branch_overlap_cancel_pre_present_controller`
  instead of the pure apply-controller head.
- Relative
  `v157`,
  the four non-blocker checks stayed tiny positive
  (`+0.0101 / +0.0049 / +0.0045 / +0.0034 dB`),
  while the local blocker stayed slightly wrong-way
  (`-0.0079 dB`).
- The route was still training-real:
  final
  `val_overlap_dual_controller_distill_l1 = 0.008762`.
- `v200`
  then jointly unfroze
  `branch_overlap_cancel_head`
  with the same pre-present controller,
  but direct
  `v199 -> v200`
  compare was
  exact
  `0.0 dB`
  on all five fixed proxies.
- Rule:
  do not keep sweeping head-only or joint-cancel variants on the same pre-present dual-teacher family.
  This route is safer than pure apply-controller distill,
  but it currently lacks enough expressivity to move the blocker.

### 25. Direct dual gate-controller rewrite falls back into the old `v188` family

- `v201`
  changed the dual route on top of
  `v190`
  to
  `branch_overlap_dual_decoder_apply_mode = gate_controller`
  with
  `gate_mode = gate`
  and
  `max_blend = 0.02`.
- The run was training-real on the intended local selector:
  `overlap_dual train 33 / 233, val 7 / 67`,
  final
  `val_overlap_dual_residual_waveform_l1 = 0.015890`.
- But relative
  `v157`,
  the fixed proxy shape was immediate catastrophic tradeoff:
  `-3.2598 / -2.4518 / -2.0349 / -1.8415 / +0.7576 dB`.
- Direct
  `v188 -> v201`
  compare then showed practical tie on all five fixed proxies.
- Rule:
  do not assume that switching the dual route to direct gate rewrite escapes the old shared-output failure family.
  On the active blocker,
  this route currently collapses back into the same
  `v188`
  regime.

### 26. The `v201` failure was not just a disconnected gate-loss bug

- `v202`
  exported the actual rewritten gate as
  `branch_overlap_dual_controlled_gate`
  and attached gate supervision directly to it.
- Training-side this really changed the optimization boundary:
  `val_gate_keep_mean = 0.165753`,
  whereas
  `v201`
  had gate metrics effectively stuck at zero because the supervised tensor was frozen.
- But output-side
  `v202`
  is still practical tie to
  `v201`:
  direct fixed-proxy deltas are only
  `+0.0013 / +0.0011 / +0.0009 / +0.0000 / +0.0005 dB`.
- Rule:
  do not keep this family open by blaming
  `v201`
  only on a supervision disconnect.
  After
  `v202`,
  direct dual gate rewrite through the existing gate path is scientifically closed.

### 27. Writing dual evidence back through the existing overlap-cancel estimate still collapses toward near-no-op

- `v203`
  introduced a new
  `branch_overlap_dual_cancel_controller_head`
  that reads the proven no-write dual auxiliary evidence from
  `v190`
  and writes back through the existing overlap-cancel estimate path.
- The route was training-real:
  the selector stayed active
  (`train 33 / 233, val 7 / 67`),
  and final
  `val_overlap_dual_controller_distill_l1 = 0.281731`.
- But relative
  `v157`,
  the four non-blocker checks moved only
  `+0.0026 / +0.0014 / +0.0013 / +0.0009 dB`,
  while the local blocker still regressed
  `-0.0015 dB`.
- `v204`
  raised
  `branch_overlap_dual_cancel_max_blend`
  from
  `0.02`
  to
  `0.08`,
  but only amplified the same tiny
  guardrail-positive / local-negative
  direction:
  relative
  `v203`,
  the four non-blocker checks changed
  `+0.0077 / +0.0042 / +0.0038 / +0.0026 dB`,
  while the local blocker regressed another
  `-0.0046 dB`.
- `v205`
  widened training to
  `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head`,
  but output-side it stayed practical tie to
  `v203`:
  direct fixed-proxy deltas were only
  `+0.0010 / +0.0005 / +0.0005 / +0.0003 / -0.0006 dB`.
- Rule:
  do not keep sweeping small blend changes or small local widening on the dual-conditioned cancel-controller family.
  If this branch continues,
  avoid writing back only through the existing overlap-cancel estimate path itself.

### 28. Dual residual-correction is real, but the tested axes still buy blocker gain by spending guardrail margin

- `v206`
  added a new dual-conditioned residual-correction family that writes directly on the current output residual
  through its own complex correction head and scalar controller.
- This route is genuinely real:
  final
  `val_overlap_dual_residual_correction_waveform_l1 = 0.004909`,
  and relative
  `v157`
  the active local blocker improved
  `+0.0088 dB`.
- But
  `v206`
  was still practical near-no-op on the fixed proxies overall,
  with small guardrail regressions
  (`-0.0165 / -0.0079 / -0.0082 / -0.0045 dB`).
- `v207`
  raised the correction blend from
  `0.02`
  to
  `0.08`
  and amplified the same direction:
  relative
  `v157`,
  the local blocker improved
  `+0.0420 dB`,
  while abstention, same-gender keep, hard-present keep, and artifact proxy regressed
  `-0.0792 / -0.0385 / -0.0393 / -0.0235 dB`.
- `v208`
  widened training to the upstream dual temporal model and dual decoder head,
  but it only moved farther along that same tradeoff surface:
  relative
  `v157`,
  the local blocker improved
  `+0.0863 dB`,
  while the four guardrails regressed
  `-0.0977 / -0.0623 / -0.0522 / -0.0452 dB`.
- Rule:
  do not keep scaling the same dual residual-correction family by simple blend sweeps or simple dual-path widening.
  If this branch continues,
  add a disjoint keep-preserve path outside the blocker windows,
  not another local-only scaling change on the same correction route.

### 29. A weak keep backstop can still collapse the dual residual-correction family if it hits the same heads

- `v209`
  added a weak
  `branch_protect_overlap_base_align_weight = 0.01`
  on
  `gate_keep_union_v2`
  samples,
  while keeping the trainable set fixed to
  `branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`.
- This continuation was training-real:
  `overlap_dual train 33 / 233, val 7 / 67`,
  `branch_protect train 63 / 233, val 27 / 67`,
  and final
  `val_branch_protect_overlap_base_align_l1 = 0.015515`.
- But output-side it was a full collapse,
  not a mild tradeoff.
  Relative
  `v157`,
  the five fixed proxies moved
  `-16.4520 / -9.0633 / -13.4505 / -15.2722 / -5.9793 dB`,
  and every fixed-proxy sample regressed.
- Relative
  `v206`,
  the same collapse shape remained
  (`-16.4355 / -9.0555 / -13.4424 / -15.2642 / -5.9881 dB`),
  so this is not just failure to recover the small guardrail loss on
  `v206`;
  it destroys the whole route.
- Rule:
  do not add keep-preserve losses to the dual residual-correction family
  if they backpropagate through the same residual-correction heads.
  The keep path must be disjoint in trainable path,
  not only in sample selector.

### 30. Trainable-path disjointness alone is not enough on the dual residual-correction family

- `v210`
  moved the keep-preserve path onto a different trainable module set:
  `branch_overlap_refine_head`
  handled the keep bypass,
  while
  `branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`
  still handled the local objective.
- This continuation was training-real:
  reconstruction selector coverage stayed
  `train 63 / 233, val 27 / 67`,
  overlap-dual stayed
  `train 33 / 233, val 7 / 67`,
  and both
  `val_reconstruction_extra_waveform_l1`
  and
  `val_overlap_dual_residual_correction_waveform_l1`
  stayed nonzero.
- But output-side it still collapsed globally.
  Relative
  `v157`,
  the five fixed proxies moved
  `-14.0317 / -9.5738 / -11.9342 / -14.4076 / -5.8259 dB`,
  and every fixed-proxy sample regressed.
- Relative
  `v206`,
  the same collapse shape remained
  (`-14.0152 / -9.5660 / -11.9260 / -14.3997 / -5.8348 dB`).
- Rule:
  do not assume a continuation is safe just because keep-preserve and local losses are disjoint in trainable modules.
  On this family,
  disjointness must hold both in trainable path and in downstream output application or control path.

### 31. Disjoint downstream output application can avoid collapse without opening selectivity

- `v211`
  moved keep-preserve supervision onto the actual pre-present-controller-written intermediate output
  while keeping the local blocker on the dual residual-correction route.
- This was the first continuation on top of the dual residual-correction family
  that stayed clearly safe on the four non-blocker guardrails:
  relative
  `v157`,
  the fixed deltas were
  `+0.0461 / +0.0227 / +0.0193 / +0.0433 / -0.0364 dB`.
- `v212`
  then raised the local correction blend and landed on a gentler exchange surface:
  relative
  `v157`,
  the fixed deltas were
  `-0.0311 / -0.0156 / -0.0139 / -0.0048 / +0.0006 dB`.
- Rule:
  do not mistake the absence of catastrophic collapse for a selective solution.
  Even when keep-preserve and local supervision are disjoint in both trainable path and downstream application,
  the route can still remain on a mild local-versus-guardrail tradeoff surface.

### 32. Simple keep-output weight strengthening can be practical tie on the new disjoint route

- `v213`
  doubled
  `reconstruction_extra_waveform_weight`
  and
  `reconstruction_extra_stft_weight`
  on top of
  `v212`.
- Direct
  `v212 -> v213`
  compare stayed only
  `-0.0004 / +0.0024 / -0.0003 / +0.0022 / +0.0015 dB`
  on the five active fixed proxies.
- Rule:
  do not keep doubling keep-output weights on the same pre-present keep-output plus dual residual-correction family by default.
  If this family continues,
  use a more expressive keep path rather than the same scalar reweight.

### 33. A keep objective can be optimization-real yet still output-capped on the disjoint route

- `v214`, `v215`, and `v216`
  all added
  `branch_protect_guard_sisdr`
  on the same
  `estimated_waveform_post_pre_present_controller`
  route.
- Across the full tested weight sweep
  `0.0002 -> 0.001 -> 0.003`,
  the selector stayed active
  (`train 63 / 233, val 27 / 67`)
  and
  `val_branch_protect_guard_sisdr_loss`
  stayed around
  `6.56`.
- But fixed-proxy movement stayed in practical tie:
  - `v212 -> v214`:
    `+0.0003 / +0.0021 / -0.0001 / +0.0027 / +0.0051 dB`
  - `v214 -> v215`:
    `-0.0062 / -0.0066 / -0.0000 / +0.0014 / -0.0005 dB`
  - `v215 -> v216`:
    `+0.0038 / +0.0086 / +0.0033 / -0.0013 / -0.0083 dB`
- Rule:
  do not assume a nonzero keep loss on the disjoint route is enough to move actual output behavior.
  This family can be optimization-real while still being effectively output-capped.

### 34. Do not keep sweeping guard-SI-SDR weight on the same disjoint keep-output route

- `v214`, `v215`, and `v216`
  closed the tested
  `branch_protect_guard_sisdr_weight`
  sweep on the post-pre-present-controller path.
- The main visible effect was higher
  `val_loss`
  (`0.270647 -> 0.275895 -> 0.289015`),
  not better fixed-proxy behavior.
- Rule:
  do not keep sweeping
  `branch_protect_guard_sisdr_weight`
  on this same pre-present keep-output plus dual residual-correction family by default.
  If this family continues,
  change the keep objective or the keep path itself.

## Current Do-Not-Continue List

- `pre_present_max_blend` sweep
- `pre_present_controller_floor`
- same-head outside-overlap abstain supervision or reweight
- `branch_overlap_cancel_head + pre-present controller` joint unfreeze alone
- `overlap_cancel_target_projection_weight` sweep
- broader-path `overlap_cancel_waveform_weight` sweep
- broader-path `gate_pre_present_keep_weight` sweep on top of `v179`
- broader-path keep-critical reconstruction guard on top of `v179`
- broader-path keep-critical `branch_protect_guard_sisdr` guard on top of `v179`
- broader-path prerefine-base-align keep on top of `v179`
- broader-path `auxiliary_only` target projection on top of `v179`
- `dual final_output + max_blend 0` as a supposed non-writing auxiliary path
- no-write `overlap_dual_mix_consistency + overlap_dual_residual_target_projection` on the active local blocker
- monitor coupling at small blend alone without a local-blocker-specific objective
- direct `overlap_dual_monitor_controller` supervision alone on top of `v191`
- audibility-style gate target on top of the same small-blend monitor head
- local current-output residual interval supervision on the same small-blend monitor family
- higher-blend continuation on the same monitor family
- naive dual-teacher distill launches that do not first confirm the teacher tensor exists
- pure apply-controller dual-teacher distill weight sweeps on top of `v190`
- head-only pre-present dual-teacher distill on top of `v190`
- joint `branch_overlap_cancel_head + pre-present controller` widening on that same family
- direct dual `gate_controller` coupling on top of `v190`
- explicit controlled-gate supervision on that same direct dual `gate_controller` family
- head-only dual-conditioned cancel-controller coupling on top of `v190`
- higher-blend continuation on that same dual-conditioned cancel-controller family
- joint `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head` widening on that same family
- head-only dual residual-correction continuation beyond the already tested `blend 0.02 / 0.08` axis
- simple higher-blend continuation on that same dual residual-correction family
- simple joint dual-path widening on that same dual residual-correction family
- same-head `branch_protect_overlap_base_align` keep backstop on that same dual residual-correction family
- prerefine keep-bypass continuation on that same dual residual-correction family
- simple keep-output weight strengthening on the same pre-present keep-output plus dual residual-correction family
- `branch_protect_guard_sisdr_weight` sweep on the same pre-present keep-output plus dual residual-correction family

## Current Safe Defaults

- Keep `v157` as the active base.
- Keep `v172` as mechanism-positive evidence only.
- If this branch resumes, prefer direct monitor-path supervision before adding new monitor-path code.
- After `v194`, do not keep stacking small-blend monitor target variants by default.
- After `v195`, treat the monitor family as closed.
- After `v196`, verify teacher-tensor materialization before reading a teacher-style run.
- After `v198`, prefer coupling paths that do not write only through the same apply-controller head.
- After `v200`, do not keep probing the same pre-present controller family with small local widening.
- After `v201`, do not keep probing direct gate rewrite from the dual route through the existing gate head path.
- After `v202`, do not reopen the same family by only changing which explicit gate tensor is supervised.
- After `v205`, do not keep writing dual evidence back only through the existing overlap-cancel estimate path.
- After `v208`, do not keep scaling the same dual residual-correction family without adding a disjoint keep-preserve route.
- After `v209`, do not backpropagate keep-preserve losses through the same dual residual-correction heads.
- After `v210`, do not treat trainable-path disjointness by itself as sufficient.
  The next route must also be disjoint in downstream output application or control path.
- After `v212`, do not mistake the new disjoint route for a solved selective regime.
  It is gentler than the older residual-correction family,
  but it is still a tradeoff surface.
- After `v213`, do not keep scaling the same keep-output weights by default.
  Prefer a more expressive keep path if this family continues.
- After `v216`, do not keep sweeping guard-SI-SDR weight on the same disjoint keep-output route.
  This axis is optimization-real but output-capped.


