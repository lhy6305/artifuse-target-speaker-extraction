# Project Overview And Active Plan

## Role

- This file keeps only the active project summary and next-step plan.
- Long history belongs in archived docs and daily reports.
- This file must remain English-only and ASCII-only.

## Encoding And Doc Rules

- Treat all repo docs and reports as UTF-8 on disk.
- Do not trust default PowerShell text decoding on this machine.
- Read text with explicit UTF-8 when using shell tools.
- Do not use PowerShell text write APIs for repo docs or reports.
- Keep active docs and active daily reports English-only and ASCII-only.
- Use `apply_patch` for doc edits so files stay BOM-free.

## Current Scientific Snapshot

- Date:
  `2026-03-30`
- Active automatic base:
  `v157`
- Mechanism-positive evidence point:
  `v172`
- Current status:
  no listening candidate
- Current decision:
  keep `v157` as active base;
  `v191` remains the structural monitor-coupling milestone;
  the monitor family is now closed through `v195`,
  the pure apply-controller dual-teacher family is now bounded through `v198`,
  the pre-present dual-teacher family is now closed through `v200`,
  the direct dual gate-controller family is now closed through `v202`,
  the dual-conditioned cancel-controller family is now closed through `v205`,
  and the dual residual-correction family is now bounded through `v210`
- Restored handoff status on `2026-03-30`:
  the next blocker is not missing code;
  direct monitor-controller supervision is already reachable with the current model outputs,
  training entry, and selector plumbing

## Active Conclusions

- `v157` remains the active base for the interval-veto family.
- `v172 = v157 + parallel pre-present total-risk controller`
  remains the key mechanism-positive evidence point:
  all four fixed keep or abstention guardrails stay positive,
  `near_real_0007 total leak` improved,
  and `near_real_0009` absent whole leak improved,
  but `near_real_0007` whole and speech-only still failed.
- `v173` showed that shrinking `pre_present_max_blend` only scales good and bad effects together.
- `v174` and `v175` showed that controller-floor shaping and same-head outside-overlap abstain supervision are both practical no-ops.
- `v176` showed that jointly unfreezing `branch_overlap_cancel_head` with the same pre-present controller is still a practical no-op.
- `v177` is invalid scratch because the `overlap_cancel` selector bundle was accidentally omitted.
- `v178` proved that a broader pre-present decision source is not a no-op:
  it strongly improved all fixed keep or abstention guardrails,
  but it also badly regressed `local_speech_leak_proxy_v1`.
- `v179` proved that explicit local target projection can pull the local blocker partly back in the correct direction,
  but the gain comes mostly from giving back same-gender keep margin.
- `v180` was practical tie to `v179`,
  so the `overlap_cancel_target_projection_weight` sweep is closed.
- `v181 = v178 + overlap_cancel_waveform_weight 0.02`
  is a route-wide collapse:
  it strongly fails all keep or abstention guardrails and the targeted local proxy together.
- `v182 = v178 + overlap_cancel_waveform_weight 0.002`
  fails in the same global direction,
  so the waveform-local route is not just mis-scaled.
- The broader-path `overlap_cancel_waveform_weight` sweep is closed.
- `v183 = v179 + gate_pre_present_keep_weight 6.0`
  showed that stronger keep pressure on the same controller does not balance the route:
  relative `v179`,
  same-gender keep only recovered `+0.0424 dB`,
  while local blocker quality regressed `-0.4003 dB`,
  and both target-projection and pre-present keep signals collapsed to near zero.
- `v184 = v179 + keep-critical reconstruction guard on gate_keep_union_v2`
  is training-real and slightly better than `v183`,
  but it still gives the wrong tradeoff:
  relative `v179`,
  same-gender keep moved only `+0.0776 dB`
  while local blocker quality regressed `-0.3093 dB`.
- `v185 = v179 + keep-critical branch_protect_guard_sisdr 0.003`
  is the strongest boundary point:
  relative `v179`,
  same-gender keep jumped `+7.6046 dB`,
  but local blocker quality collapsed `-12.8808 dB`.
- `v186 = v179 + branch_protect_overlap_base_align_weight 0.04`
  with
  `loss_use_branch_prerefine_as_primary_prediction = True`
  showed that a separate prerefine-base keep reference is training-real
  (`branch_protect train 63 / 233, val 27 / 67`,
  final
  `val_branch_protect_overlap_base_align_l1 = 0.0008964`),
  but it still gives the wrong fixed tradeoff:
  relative `v179`,
  local blocker quality improved `+2.6262 dB`,
  while abstention, same-gender keep, hard-present keep, and artifact proxy all regressed
  (`-3.0676 / -0.7755 / -1.7387 / -1.6118 dB`);
  relative `v157`,
  all four fixed guardrails are still negative
  (`-1.7370 / -0.7234 / -0.5724 / -0.6573 dB`).
- The broader-path paired keep-objective family is now bounded:
  when keep preservation acts on the same controller or the same final output,
  it suppresses or overpowers the local pullback instead of balancing it.
- The broader-path separate-reference keep family is also now bounded:
  changing the keep reference alone is not enough
  if the objective still constrains the same final output degrees of freedom.
- `v187 = v179 + branch_overlap_cancel_apply_mode auxiliary_only`
  showed that decoupling direct output rewrite alone is still not enough.
  Relative `v157`,
  all four fixed keep or abstention guardrails improved
  (`+1.4179 / +0.1285 / +1.2877 / +0.9857 dB`),
  but `local_speech_leak_proxy_v1` regressed
  `-1.9193 dB`.
  Relative `v179`,
  same-gender keep recovered only `+0.0765 dB`
  while the local blocker regressed `-0.3086 dB`.
  Training-side the route stayed selected
  (`train 33 / 233, val 7 / 67`),
  but final
  `val_overlap_cancel_target_projection_ratio = 2.58e-09`
  and
  `val_gate_pre_present_keep_mean = 1.64e-05`,
  so the intended auxiliary local signal collapsed while the shared branch drifted back toward keep-heavy behavior.
- The broader-path auxiliary-only family is now bounded:
  removing direct output rewrite is not sufficient
  if the local objective still backpropagates through the same trainable broader-path temporal or gate route.
- `v188 = v157 + overlap_dual auxiliary path with final_output and max_blend 0`
  exposed a semantics trap:
  it is not a no-write auxiliary mode.
  Relative `v157`,
  fixed checks moved
  `-3.2585 / -2.4507 / -2.0340 / -1.8415 / +0.7581 dB`,
  which shows
  `dual final_output + max_blend 0`
  falls back to a branch-base rewrite.
- `v189 = v157 + overlap_dual auxiliary path with current_output and max_blend 0`
  corrected that semantics.
  Relative `v157`,
  all five active fixed checks are exact
  `0.0 dB`,
  so this is the first clean proof that a truly disjoint non-writing auxiliary branch can be attached without disturbing active-base behavior.
  But the current dual objective is trivial:
  selector coverage is real
  (`train 33 / 233, val 7 / 67`),
  yet
  `overlap_dual_mix_consistency_l1` and `overlap_dual_residual_target_projection_ratio`
  stayed exact
  `0.0`,
  so the auxiliary branch simply learns the zero-residual solution.
- The dual auxiliary family is now bounded in two ways:
  `final_output + max_blend 0` is not a true no-write mode,
  and the current no-write dual objective pair is a trivial no-op on this blocker.
- `v190 = v157 + overlap_dual current_output + max_blend 0 + residual_waveform_weight 0.02`
  resolved the second half of that boundary.
  Relative `v157`,
  all five active fixed checks are still exact
  `0.0 dB`,
  but the auxiliary branch is no longer trivial:
  `overlap_dual train 33 / 233, val 7 / 67`,
  final
  `val_overlap_dual_residual_waveform_l1 = 0.015926`.
  This is the first clean proof that a truly disjoint no-write auxiliary local path can also be training-real.
- The current branch boundary is now sharper:
  the blocker is no longer "find a non-trivial no-write local objective".
  The blocker is "couple a proven no-write auxiliary local path back to output behavior without collapsing into the old shared-route failures".
- `v191 = v190 + enable_branch_overlap_dual_monitor_controller + monitor_max_blend 0.02`
  is the first safe coupling evidence point:
  relative `v157`,
  all five active fixed checks turned nonzero positive
  (`+0.0486 / +0.0162 / +0.0467 / +0.0278 / +0.0008 dB`),
  but the local blocker stayed practical tie.
- `v192 = v191 + gate_supervision_source overlap_dual_monitor_controller`
  showed that direct monitor supervision alone still does not solve local selectivity.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all stayed small positive
  (`+0.0637 / +0.0241 / +0.0510 / +0.0317 dB`),
  but the local blocker moved wrong-way
  `-0.0140 dB`.
  Relative `v191`,
  the four non-blocker checks improved only
  `+0.0151 / +0.0078 / +0.0043 / +0.0039 dB`,
  while the local blocker regressed
  `-0.0149 dB`.
  The frozen dual residual path stayed preserved
  (`val_overlap_dual_residual_waveform_l1 = 0.015926`),
  so the failure is monitor-head selectivity, not auxiliary-path collapse.
- `v193 = v192 + audibility gate target on overlap_dual_monitor_controller`
  was a practical no-op.
  Relative `v192`,
  the four non-blocker checks changed only
  `+0.0004 / +0.0004 / +0.0003 / +0.0004 dB`,
  while the local blocker regressed
  `-0.0004 dB`.
  On the active local blocker set,
  the monitor head was already effectively sitting at the frozen
  `branch_overlap_dual_controller`
  ceiling,
  so a head-only target had almost no remaining freedom.
- `v194 = v193 + local monitor-applied residual interval loss`
  widened training to
  `branch_overlap_dual_decoder_head + branch_overlap_dual_monitor_controller_head`
  and supervised the actual monitor correction path
  against the current-output residual inside blocker windows.
  Relative `v157`,
  the four non-blocker checks improved further
  (`+0.0769 / +0.0323 / +0.0578 / +0.0364 dB`),
  but the local blocker regressed to
  `-0.0262 dB`.
  Relative `v193`,
  the same four checks improved
  `+0.0128 / +0.0078 / +0.0065 / +0.0043 dB`,
  while the local blocker regressed another
  `-0.0117 dB`.
  So even blocker-specific monitor correction still sharpened general safe suppression
  more than local selectivity.
- `v195 = v194 + branch_overlap_dual_monitor_max_blend 0.08`
  closed the last unresolved axis in the monitor family.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy improved further
  (`+0.1546 / +0.0811 / +0.0887 / +0.0595 dB`),
  but the local blocker regressed sharply to
  `-0.1134 dB`.
  Relative `v194`,
  the same four non-blocker checks improved again
  (`+0.0777 / +0.0488 / +0.0309 / +0.0231 dB`),
  while the local blocker regressed another
  `-0.0872 dB`.
  This is the clearest closure result yet:
  higher monitor blend amplified the same wrong direction rather than fixing local selectivity.
- `v196 = intended v190 -> apply-controller dual-teacher bridge`
  exposed a semantics gap rather than a scientific result.
  Under
  `branch_overlap_dual_decoder_apply_mode = current_output`
  with no monitor head,
  `branch_overlap_dual_controller`
  was not materialized,
  so the new distill term had no teacher tensor.
  Relative both `v157` and `v190`,
  all five fixed checks stayed exact
  `0.0 dB`.
  `v196` therefore counts as an invalid no-op read on the family,
  not as evidence for or against coupling quality.
- That gap is now fixed in code:
  `branch_overlap_dual_controller`
  is emitted whenever the dual residual path exists,
  and the optional monitor or distill losses in
  `compute_losses`
  now safely return zero when their tensors are absent.
- `v197 = v190 + actual apply-controller distill from materialized dual controller`
  is the first live version of the teacher-bridge idea.
  It is training-real:
  final
  `val_overlap_dual_controller_distill_l1 = 0.113235`.
  Relative `v157`,
  the local blocker finally moved the right way
  (`+0.1082 dB`),
  but all four fixed keep or abstention guardrails regressed
  (`-0.1949 / -0.0839 / -0.0889 / -0.0736 dB`).
  This shows the family can now spend auxiliary evidence on the blocker,
  but it spends guardrail margin through the same apply-controller route.
- `v198 = v197` with
  `overlap_dual_controller_distill_weight = 0.5`
  was practical tie to `v197`.
  Relative `v157`,
  the fixed deltas stayed effectively identical
  (`-0.1949 / -0.0839 / -0.0889 / -0.0736 / +0.1082 dB`).
  Direct local-proxy compare
  `v197 -> v198`
  was only
  `-1.7e-07 dB`.
  So simple weight reduction does not open a better regime on this family.
- `v199 = v190 + pre-present-controller distill from materialized dual controller`
  showed that a safer write-back location exists,
  but it collapses toward near-no-op.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy stayed tiny positive
  (`+0.0101 / +0.0049 / +0.0045 / +0.0034 dB`),
  while the local blocker stayed slightly wrong-way
  (`-0.0079 dB`).
  Final
  `val_overlap_dual_controller_distill_l1 = 0.008762`
  confirms the route is training-real,
  but too weak to move the blocker.
- `v200 = v199 + branch_overlap_cancel_head` joint unfreeze
  was exact tie to `v199`
  at the active proxy resolution.
  Relative `v157`,
  the same five fixed deltas stayed identical,
  and direct
  `v199 -> v200`
  compare was
  `0.0 dB`
  on all five fixed proxies.
  So the obvious local widening around the same pre-present write-back route does not reopen a useful basin.
- `v201 = v190 + branch_overlap_dual_decoder_apply_mode gate_controller`
  with
  `branch_overlap_dual_decoder_gate_mode = gate`
  and
  `branch_overlap_dual_decoder_max_blend = 0.02`
  is training-real on the intended local selector
  (`overlap_dual train 33 / 233, val 7 / 67`;
  final
  `val_overlap_dual_residual_waveform_l1 = 0.015890`),
  but the fixed outcome is immediate reject.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy collapsed
  (`-3.2598 / -2.4518 / -2.0349 / -1.8415 dB`),
  while the local blocker improved
  `+0.7576 dB`.
  Direct
  `v188 -> v201`
  compare stayed near exact tie on all five fixed proxies
  (`-0.0013 / -0.0011 / -0.0009 / -0.0000 / -0.0005 dB`),
  so this route lands back in the old
  `v188`
  family rather than opening a new selective regime.
- `v202 = v201 family + explicit controlled-gate supervision`
  removed the last ambiguity on that route.
  The code now exports
  `branch_overlap_dual_controlled_gate`,
  and train or eval can supervise it directly through
  `gate_supervision_source = overlap_dual_controlled_gate`.
  Training-side the connection is real:
  final
  `val_gate_keep_mean = 0.165753`
  is nonzero.
  But output-side it is still practical tie to
  `v201`:
  direct
  `v201 -> v202`
  compare stayed only
  `+0.0013 / +0.0011 / +0.0009 / +0.0000 / +0.0005 dB`.
  So the direct dual gate-controller family is now fully closed.
- `v203 = v190 + dual-conditioned cancel-controller head-only`
  is the first run on a new coupling family that writes back through the existing
  overlap-cancel estimate
  without reusing the old apply-controller head,
  pre-present controller,
  or direct gate rewrite.
  It is training-real:
  `overlap_dual train 33 / 233, val 7 / 67`,
  final
  `val_overlap_dual_controller_distill_l1 = 0.281731`,
  and
  `val_gate_keep_mean = 0.353940`.
  But relative `v157`,
  the four non-blocker checks moved only
  `+0.0026 / +0.0014 / +0.0013 / +0.0009 dB`,
  while the local blocker still regressed
  `-0.0015 dB`.
  So the head-only small-blend route is safe,
  but practical near-no-op.
- `v204 = v203 family + branch_overlap_dual_cancel_max_blend 0.08`
  showed that higher write-back strength only amplifies the same tiny direction.
  Relative `v157`,
  the four non-blocker checks moved to
  `+0.0103 / +0.0056 / +0.0051 / +0.0035 dB`,
  while the local blocker regressed further to
  `-0.0061 dB`.
  Relative `v203`,
  the same four checks improved only
  `+0.0077 / +0.0042 / +0.0038 / +0.0026 dB`,
  while the local blocker regressed another
  `-0.0046 dB`.
- `v205 = v203 family + branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head`
  tested whether the head-only near-no-op was just a frozen-upstream ceiling.
  The widened route remained training-real:
  final
  `val_overlap_dual_residual_waveform_l1 = 0.016116`,
  `val_overlap_dual_controller_distill_l1 = 0.256049`,
  and
  `val_gate_keep_mean = 0.333589`.
  But output-side it stayed practical tie.
  Relative `v157`,
  fixed deltas were only
  `+0.0036 / +0.0019 / +0.0018 / +0.0012 / -0.0021 dB`;
  relative `v203`,
  direct compare stayed only
  `+0.0010 / +0.0005 / +0.0005 / +0.0003 / -0.0006 dB`.
  So even a widened dual-conditioned cancel-controller route does not open a useful basin.
- The dual-conditioned cancel-controller family is now closed through
  `v205`:
  writing no-write dual auxiliary evidence back through the existing overlap-cancel estimate
  is still not enough,
  even after a blend sweep and small dual-head widening.
- `v206 = v190 + dual residual-correction head-only`
  introduced a new direct write-back family:
  a bounded complex correction on the current output residual,
  driven by dual auxiliary evidence and applied through its own scalar controller.
  The route is training-real:
  final
  `val_overlap_dual_residual_correction_waveform_l1 = 0.004909`.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy moved only
  `-0.0165 / -0.0079 / -0.0082 / -0.0045 dB`,
  while the local blocker moved
  `+0.0088 dB`.
  So the family is not no-op,
  but the small-blend head-only version is still practical near-no-op.
- `v207 = v206 family + branch_overlap_dual_residual_correction_max_blend 0.08`
  showed that the new family scales in a coherent direction.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy moved
  `-0.0792 / -0.0385 / -0.0393 / -0.0235 dB`,
  while the local blocker improved
  `+0.0420 dB`.
  Relative `v206`,
  the same four guardrails regressed
  `-0.0627 / -0.0306 / -0.0311 / -0.0190 dB`,
  while the local blocker improved another
  `+0.0332 dB`.
  This is the first clear monotonic blocker-positive direction from the dual no-write evidence,
  but it is still a straightforward guardrail-spending tradeoff.
- `v208 = v207 family + joint dual-path widening`
  widened training to
  `branch_overlap_dual_decoder_temporal_model + branch_overlap_dual_decoder_head + branch_overlap_dual_residual_correction_head + branch_overlap_dual_residual_correction_controller_head`.
  The widened route stayed training-real:
  final
  `val_overlap_dual_residual_waveform_l1 = 0.016118`,
  `val_overlap_dual_residual_correction_waveform_l1 = 0.004902`,
  and
  `val_overlap_dual_controller_distill_l1 = 0.255086`.
  Relative `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy regressed further
  (`-0.0977 / -0.0623 / -0.0522 / -0.0452 dB`),
  while the local blocker improved further to
  `+0.0863 dB`.
  Relative `v207`,
  the same four guardrails regressed another
  `-0.0185 / -0.0238 / -0.0129 / -0.0217 dB`,
  while the local blocker improved another
  `+0.0443 dB`.
  So joint widening does not recover selectivity;
  it only moves farther along the same tradeoff surface.
- The dual residual-correction family is now bounded through
  `v208`:
  it is a real new coupling path,
  and it is the first dual family here that moves the blocker monotonically in the correct direction,
  but the tested axes still buy that gain by spending guardrail margin.
- `v209 = v206 + weak branch_protect overlap-base-align on gate_keep_union_v2`
  tested the first command-only keep-preserve continuation on that family.
  It is training-real:
  `overlap_dual train 33 / 233, val 7 / 67`,
  `branch_protect train 63 / 233, val 27 / 67`,
  and final
  `val_branch_protect_overlap_base_align_l1 = 0.015515`.
  But relative both
  `v157`
  and
  `v206`,
  all five active fixed proxies regressed strongly
  (`-16.4520 / -9.0633 / -13.4505 / -15.2722 / -5.9793 dB`
  versus
  `v157`,
  and
  `-16.4355 / -9.0555 / -13.4424 / -15.2642 / -5.9881 dB`
  versus
  `v206`).
  Every sample in every fixed proxy manifest regressed.
  So even a weak keep-preserve loss becomes a collapse route
  when it backpropagates through the same dual residual-correction heads.
- The dual residual-correction family is now bounded through
  `v209`:
  simple scaling and simple widening already showed a local-positive but guardrail-negative surface,
  and the first same-head keep-backstop continuation collapses all five fixed proxies together.
- `v210 = v206 + prerefine keep-bypass on pre-dual output`
  tested the first continuation in this family whose keep-preserve route was disjoint in trainable path.
  It is training-real:
  reconstruction selector coverage stayed
  `train 63 / 233, val 27 / 67`,
  overlap-dual coverage stayed
  `train 33 / 233, val 7 / 67`,
  and final
  `val_reconstruction_extra_waveform_l1 = 0.014815`
  plus
  `val_overlap_dual_residual_correction_waveform_l1 = 0.001671`
  show that both the keep-bypass path and the local path were active.
  But relative both
  `v157`
  and
  `v206`,
  all five active fixed proxies regressed strongly
  (`-14.0317 / -9.5738 / -11.9342 / -14.4076 / -5.8259 dB`
  versus
  `v157`,
  and
  `-14.0152 / -9.5660 / -11.9260 / -14.3997 / -5.8348 dB`
  versus
  `v206`).
  Every sample in every fixed proxy manifest regressed.
  So trainable-path disjointness alone is not enough
  if both objectives still couple through the same downstream branch behavior.
- The dual residual-correction family is now bounded through
  `v210`:
  same-head keep backstop already collapsed,
  and even the first trainable-path-disjoint keep-bypass continuation still collapses all five fixed proxies together.

## Closed Axes

- `predicted_activity`
- `predicted_activity + max_blend`
- `apply-controller only`
- `apply-controller + cancel`
- `apply-controller` selector width
- `interval-veto union-bundle gate_keep_weight`
- `branch_overlap_cancel_apply_max_freq_ratio`
- `branch_overlap_cancel_apply_controller_floor`
- split keep or absent apply-controller
- absent-veto-only split controller
- no-teacher `refine_base` siblings on top of `v157`
- `branch_base_blend`
- `branch_base_blend + max_blend`
- `refine_base_blend`
- `refine_base_blend + max_blend`
- plain `pre_present_subtract`
- parallel pre-present total-risk controller `max_blend` sweep
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
- direct `overlap_dual_monitor_controller` supervision alone on top of `v191`
- audibility-style gate target on top of `v192`
- local current-output residual interval supervision on the small-blend monitor path
- higher-blend continuation on the same monitor family
- naive `branch_overlap_dual_controller` teacher distill on top of `v190` without a materialized controller output
- pure `branch_overlap_cancel_apply_controller <- branch_overlap_dual_controller` distill on top of `v190`
- simple `overlap_dual_controller_distill_weight` downshift from `1.0` to `0.5` on that same family
- head-only pre-present dual-teacher distill on top of `v190`
- joint `branch_overlap_cancel_head + pre-present controller` widening on that same family
- direct dual `gate_controller` coupling on top of `v190`
- explicit controlled-gate supervision on that same direct dual `gate_controller` family
- dual-conditioned cancel-controller head-only coupling on top of `v190`
- higher-blend continuation on that same dual-conditioned cancel-controller family
- joint `branch_overlap_dual_decoder_head + branch_overlap_dual_cancel_controller_head` widening on that same family
- dual residual-correction head-only coupling at `blend 0.02`
- higher-blend continuation on that same dual residual-correction family
- joint dual-path widening on that same dual residual-correction family
- same-head `branch_protect_overlap_base_align` keep backstop on top of `v206`
- prerefine keep-bypass on pre-dual output on top of `v206`

## Active Branch Status

- Main active base:
  `v157`
- Positive but below-promotion evidence:
  `v172`
- Broader-path strong-tradeoff reject:
  `v178`
- Explicit-local-target evidence but still reject:
  `v179`
- Practical tie that closes projection-weight calibration:
  `v180`
- Waveform-local global-collapse reject:
  `v181`
- Lower-weight replication that closes waveform-local calibration:
  `v182`
- Same-controller keep-reweight reject:
  `v183`
- Keep-critical reconstruction-guard reject:
  `v184`
- Keep-critical final-output guard dominate-and-collapse reject:
  `v185`
- Separate-reference-path keep-preserve tradeoff reject:
  `v186`
- Auxiliary-only shared-route drift reject:
  `v187`
- Dual final-output zero-blend semantic reject:
  `v188`
- True no-write auxiliary evidence but trivial-objective no-op:
  `v189`
- Non-trivial no-write auxiliary local-path evidence:
  `v190`
- First positive-all-guardrails monitor-coupling evidence:
  `v191`
- Direct monitor-controller supervision reject:
  `v192`
- Audibility-target monitor reject:
  `v193`
- Local monitor-residual interval reject:
  `v194`
- Higher-blend monitor closure reject:
  `v195`
- Safe but near-no-op pre-present dual-teacher bridge:
  `v199`
- Joint-cancel exact-tie closure on the same pre-present family:
  `v200`
- Direct dual gate-controller collapse back to the `v188` family:
  `v201`
- Controlled-gate-supervised tie that closes the same family:
  `v202`
- Dual-conditioned cancel-controller head-only safe near-no-op:
  `v203`
- Higher-blend tiny-direction replication on the same family:
  `v204`
- Joint dual-head tie that closes the same family:
  `v205`
- Dual residual-correction head-only safe near-no-op:
  `v206`
- Higher-blend blocker-positive but guardrail-negative tradeoff:
  `v207`
- Joint dual-path widening that moves farther along the same tradeoff surface:
  `v208`
- Same-head keep-backstop collapse on top of `v206`:
  `v209`
- Trainable-path-disjoint prerefine keep-bypass collapse on top of `v206`:
  `v210`

## Next Valid Directions

- Do not continue the projection-weight sweep.
- Do not continue the broader-path waveform-local sweep.
- Do not continue small local unfreeze around the same pre-present controller family.
- Do not continue paired keep objectives that act on the same controller or the same final output.
- Do not continue keep-preserve routes that change only the reference path while still constraining the same final output.
- Do not continue auxiliary-only routes that still share the same trainable broader-path temporal or gate modules.
- Do not treat `dual final_output + max_blend 0` as a non-writing auxiliary mode.
- Do not continue the current no-write dual objective pair on the active local blocker.
- If this branch continues, keep preservation must become orthogonal to the local objective in both reference and output application.
- The most reasonable next options are:
  - a different local objective that does not share the same final-output degrees of freedom
  - keep-preserve supervision outside the local-blocker windows only if it does not still rewrite the same final output route
  - a materially larger path change only if it uses disjoint keep and local supervision paths
  - a non-trivial local objective on a truly disjoint trainable auxiliary path
  - a separate coupling path that reads a proven non-trivial auxiliary local predictor without reusing the old shared main-output route
- Do not treat small-blend monitor coupling as equivalent to local-blocker improvement.
- Do not continue the monitor family with more target variants or more blend sweeps.
- Prefer a path whose local objective is not capped by the current monitor-correction route.
- Keep local and keep-preserve supervision disjoint in both trainable path and output application.
- Do not continue head-only or joint-cancel variants on the same pre-present dual-teacher family.
- Prefer a coupling path that is both disjoint from the old apply-controller route and more expressive than the current pre-present controller route.
- Do not continue direct gate rewrite from the dual route through the existing `branch_decoder_frame_gate` output path.
- Do not continue direct dual gate-controller routes even with explicit controlled-gate supervision.
- Do not continue small sweeps or small local widening on the dual-conditioned cancel-controller family.
- Do not continue simple scaling or simple dual-path widening on the same dual residual-correction family.
- Do not continue same-head keep-backstop continuation on that same dual residual-correction family.
- Do not continue prerefine keep-bypass continuation on that same dual residual-correction family.
- If this branch continues,
  the next route must be disjoint both in trainable path and in downstream output application,
  not only avoid backpropagating keep preservation through the same residual-correction heads.

## Active Report Entry Points

- `reports/daily/2026-03-28_parallel_prepresent_totalrisk_controller_on_v157_v172_v173_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_totalrisk_selectivity_v174_v175_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_jointcancelhead_v176_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_broaderpath_targetproj_v177_v180_followup.md`
- `reports/daily/2026-03-28_parallel_prepresent_waveformlocal_v181_v182_followup.md`
- `reports/daily/2026-03-29_broaderpath_paired_keep_objectives_v183_v185_followup.md`
- `reports/daily/2026-03-29_broaderpath_prerefine_basealign_keep_v186_followup.md`
- `reports/daily/2026-03-29_auxiliary_only_targetproj_v187_followup.md`
- `reports/daily/2026-03-29_dual_auxiliary_localpath_v188_v189_followup.md`
- `reports/daily/2026-03-29_dual_auxiliary_residual_waveform_v190_followup.md`
- `reports/daily/2026-03-29_dual_auxiliary_monitor_coupling_v191_followup.md`
- `reports/daily/2026-03-30_handoff_restore_and_v192_launch_plan.md`
- `reports/daily/2026-03-30_direct_monitor_supervision_v192_followup.md`
- `reports/daily/2026-03-30_monitor_local_interval_residual_v194_followup.md`
- `reports/daily/2026-03-30_monitor_blend008_v195_followup.md`
- `reports/daily/2026-03-30_applycontroller_dualteacher_v196_v198_followup.md`
- `reports/daily/2026-03-30_prepresent_dualteacher_v199_v200_followup.md`
- `reports/daily/2026-03-30_dualgatecontroller_v201_followup.md`
- `reports/daily/2026-03-30_dualgatecontroller_controlledgate_v202_followup.md`
- `reports/daily/2026-03-30_dualcancelcontroller_v203_v205_followup.md`
- `reports/daily/2026-03-30_dualresidualcorrection_v206_v208_followup.md`
- `reports/daily/2026-03-30_dualresidual_keepbackstop_v209_followup.md`
- `reports/daily/2026-03-30_dualresidual_refinekeepbypass_v210_followup.md`
- `reports/daily/2026-03-28_encoding_and_active_doc_audit.md`

