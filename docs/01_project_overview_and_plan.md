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
  `2026-03-31`
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
  the original dual residual-correction family is now bounded through `v210`,
  the first disjoint-downstream keep-output continuation on top of that family
  is now mapped through `v219`,
  the writable residual-correction local-objective continuation family is now mapped through `v236`,
  the writable pre-present main-output family is now bounded through `v232`,
  the first `refine_base` local-only writer route is now bounded through `v233`,
  the `refine_present` writer family is closed through `v231`,
  and the first dedicated dual-local writer bridge route is now bounded through `v237`
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
- `v211 = v206 + pre-present keep-output path on estimated_waveform_post_pre_present_controller + dual residual-correction`
  is the first continuation in this family whose keep-preserve route is disjoint both:
  in trainable path,
  and in downstream output application.
  Relative
  `v157`,
  abstention, same-gender keep, hard-present keep, and artifact proxy all improved
  (`+0.0461 / +0.0227 / +0.0193 / +0.0433 dB`),
  while the local blocker regressed only mildly
  (`-0.0364 dB`).
  This is the first safe non-collapsing continuation on top of the dual residual-correction family,
  but it is still not promotion-worthy because the blocker stays wrong-way.
- `v212 = v211 + branch_overlap_dual_residual_correction_max_blend 0.08`
  moved along a gentler tradeoff surface than the earlier
  `v206 -> v208`
  family.
  Relative
  `v157`,
  the local blocker recovered to practical tie
  (`+0.0006 dB`),
  while abstention, same-gender keep, hard-present keep, and artifact proxy slipped only slightly negative
  (`-0.0311 / -0.0156 / -0.0139 / -0.0048 dB`).
  So disjoint downstream application avoids collapse,
  but it still does not open true selectivity.
- `v213 = v212` with doubled keep-output weights
  (`reconstruction_extra_waveform_weight 0.4`,
  `reconstruction_extra_stft_weight 0.2`)
  was practical tie to
  `v212`
  on the active proxy set.
  Direct
  `v212 -> v213`
  compare stayed only
  `-0.0004 / +0.0024 / -0.0003 / +0.0022 / +0.0015 dB`.
  So the first keep-output-weight strengthening axis on this family is closed.
- The pre-present keep-output plus dual residual-correction continuation family is now bounded in its first three tested forms:
  safe but local-negative
  (`v211`),
  near-tie tradeoff
  (`v212`),
  and keep-weight-strengthening practical tie
  (`v213`).
- `v214 = v212 + branch_protect_guard_sisdr_weight 0.0002`
  tested the first more expressive keep objective on the same disjoint-downstream route.
  It is training-real:
  `branch_protect train 63 / 233, val 27 / 67`,
  final
  `val_branch_protect_guard_sisdr_loss = 6.560211`.
  But relative
  `v212`,
  the fixed deltas stayed only
  `+0.0003 / +0.0021 / -0.0001 / +0.0027 / +0.0051 dB`,
  so output-side it is practical tie.
- `v215 = v214` with
  `branch_protect_guard_sisdr_weight 0.001`
  only raised optimization pressure,
  not output movement.
  Relative
  `v214`,
  the fixed deltas stayed only
  `-0.0062 / -0.0066 / -0.0000 / +0.0014 / -0.0005 dB`.
- `v216 = v215` with
  `branch_protect_guard_sisdr_weight 0.003`
  closed the tested weight sweep.
  Relative
  `v215`,
  the fixed deltas stayed only
  `+0.0038 / +0.0086 / +0.0033 / -0.0013 / -0.0083 dB`.
  Relative
  `v157`,
  all five fixed checks still stayed near tie
  (`-0.0333 / -0.0115 / -0.0107 / -0.0020 / -0.0031 dB`).
- The
  `branch_protect_guard_sisdr_weight`
  sweep on the pre-present keep-output plus dual residual-correction route is now closed:
  across
  `0.0002 -> 0.001 -> 0.003`,
  the keep loss is optimization-real,
  but output-capped at the active proxy resolution.
- `v217 = v212 + branch_protect_teacher_overlap_weight 0.04`
  tested overlap-only teacher keep on the same
  `estimated_waveform_post_pre_present_controller`
  route against the safe
  `v157`
  teacher.
  It was training-real:
  `branch_protect_teacher train 63 / 233, val 27 / 67`,
  final
  `val_branch_protect_teacher_overlap_l1 = 0.000295`.
  But relative
  `v212`,
  all five fixed checks moved slightly negative
  (`-0.0196 / -0.0156 / -0.0123 / -0.0092 / -0.0029 dB`),
  so the low-weight launch was practical tie but uniformly worse.
- `v218 = v217` with
  `branch_protect_teacher_overlap_weight 0.2`
  partially repaired the four non-blocker checks.
  Relative
  `v217`,
  the fixed deltas moved
  `+0.0406 / +0.0400 / +0.0199 / +0.0163 / -0.0028 dB`.
  Relative
  `v212`,
  the deltas moved
  `+0.0210 / +0.0244 / +0.0076 / +0.0071 / -0.0057 dB`.
  Relative
  `v157`,
  it still stayed near tie
  (`-0.0101 / +0.0088 / -0.0063 / +0.0023 / -0.0052 dB`).
- The
  `branch_protect_teacher_overlap_weight`
  sweep on the same pre-present keep-output plus dual residual-correction route is now also closed:
  it can move this family slightly back toward guardrails,
  but only by giving back local blocker quality,
  so it still does not open a selective regime.
- `v219 = v212 + branch_overlap_cancel_head`
  widened the trainable keep path on the same disjoint downstream route
  while keeping all losses unchanged.
  This was not a practical tie:
  relative
  `v212`,
  the fixed deltas moved
  `+0.6713 / +0.2892 / +0.6024 / +0.2629 / -0.0913 dB`.
  Relative
  `v157`,
  the shape stayed similar
  (`+0.6402 / +0.2737 / +0.5885 / +0.2581 / -0.0907 dB`).
  So simple keep-path widening through the same cancel estimate is a strong tradeoff reject,
  not a selective solution.
- `v220 = v212 + overlap_dual_residual_target_projection_weight 0.01`
  kept the
  `v212`
  route fixed and only added a blocker-aligned local scalar objective.
  This run was training-real,
  but practical tie:
  relative
  `v212`,
  the fixed deltas moved only
  `+0.0026 / +0.0034 / +0.0034 / +0.0024 / +0.0009 dB`.
  Relative
  `v157`,
  it stayed near tie
  (`-0.0285 / -0.0122 / -0.0105 / -0.0024 / +0.0014 dB`).
- `v221 = v220 + overlap_dual_residual_target_projection_weight 0.02`
  also stayed practical tie.
  Relative
  `v220`,
  the fixed deltas moved only
  `-0.0025 / -0.0021 / -0.0043 / -0.0001 / +0.0006 dB`.
  Relative
  `v157`,
  it remained near tie
  (`-0.0310 / -0.0144 / -0.0149 / -0.0025 / +0.0020 dB`).
  So the first
  `overlap_dual_residual_target_projection_weight`
  retune on top of the
  `v212`
  disjoint route is now closed as another ineffective local-objective scalar sweep.
- `v222 = v212 + overlap_dual_residual_correction_local_waveform_weight 0.5`
  was the first continuation on this safer
  `v212`
  family that supervised the writable residual-correction branch directly inside
  `local_proxy_intervals`.
  Relative
  `v212`,
  all five fixed deltas turned slightly positive
  (`+0.0069 / +0.0054 / +0.0038 / +0.0032 / +0.0011 dB`),
  but the magnitude stayed small.
- `v223 = v222 + overlap_dual_residual_correction_local_waveform_weight 2.0`
  kept improving the local blocker,
  but no longer moved the four guardrails in the same direction.
  Relative
  `v222`,
  the fixed deltas became
  `-0.0083 / -0.0045 / -0.0018 / -0.0033 / +0.0078 dB`.
  Relative
  `v212`,
  it still stayed near tie overall
  (`-0.0014 / +0.0009 / +0.0020 / -0.0001 / +0.0090 dB`).
- `v224 = v223 + overlap_dual_residual_correction_local_waveform_weight 8.0`
  was the closure run for this first local-window waveform family.
  Relative
  `v212`,
  it became mildly positive on four of five checks
  (`+0.0260 / +0.0141 / +0.0169 / -0.0031 / +0.0149 dB`).
  Relative
  `v157`,
  it still stayed near tie overall
  (`-0.0051 / -0.0015 / +0.0030 / -0.0079 / +0.0155 dB`).
  So this family is not dead,
  but the weight sweep
  `0.5 -> 2.0 -> 8.0`
  still does not open a meaningful new regime.
- `v225 = v224 + overlap_dual_residual_correction_local_controller_weight 0.5`
  added explicit local-window supervision on
  `branch_overlap_dual_residual_correction_controller`
  while keeping the
  `v224`
  local-window waveform objective unchanged.
  This term was training-real
  (`val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`),
  but output behavior worsened relative to
  `v224`:
  direct fixed deltas became
  `-0.0055 / -0.0091 / -0.0054 / +0.0136 / -0.0040 dB`.
  Relative
  `v157`,
  the run stayed near tie
  (`-0.0106 / -0.0106 / -0.0024 / +0.0058 / +0.0115 dB`).
  So the first controller-local supervision axis is now also closed.
- `v226 = v224 + extra_local_waveform_weight 0.5`
  was the first writable-path change after
  `v225`:
  it supervised the writable
  `estimated_waveform_post_pre_present_controller`
  route directly inside
  `local_proxy_intervals`
  while keeping the
  `v224`
  residual-correction local-window waveform term active.
  This run was training-real
  (`val_extra_local_waveform_l1 = 0.001274`)
  and mildly blocker-positive.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.0000 / -0.0193 / +0.0032 / -0.0157 / +0.0071 dB`.
  Relative
  `v157`,
  it stayed near tie overall
  (`-0.0051 / -0.0207 / +0.0062 / -0.0236 / +0.0226 dB`).
  So this was evidence that the writable-path change is real,
  but still only a mild exchange surface.
- `v227 = v226 + extra_local_waveform_weight 2.0`
  was the first closure run on that new writable pre-present main-output family.
  It pushed the blocker further,
  but all four guardrails turned materially negative.
  Relative
  `v226`,
  direct fixed deltas became
  `-0.0891 / -0.0392 / -0.0513 / -0.0385 / +0.0251 dB`.
  Relative
  `v157`,
  they became
  `-0.0942 / -0.0600 / -0.0451 / -0.0621 / +0.0478 dB`.
  So the first
  `extra_local_waveform_weight`
  sweep
  `0.5 -> 2.0`
  is now bounded:
  this family is real,
  but simple scalar strengthening only steepens the same tradeoff.
- `v228 = v226 + extra_local_sisdr_weight 0.001`
  tested whether the
  `v226`
  writable pre-present main-output route was mainly limited by local waveform L1.
  This new objective was training-real
  (`val_extra_local_sisdr_loss = 0.520717`),
  but fixed-proxy behavior almost exactly reproduced the
  `v227`
  shape.
  Relative
  `v226`,
  direct fixed deltas became
  `-0.0900 / -0.0407 / -0.0519 / -0.0396 / +0.0253 dB`.
  Relative
  `v157`,
  they became
  `-0.0951 / -0.0614 / -0.0457 / -0.0633 / +0.0480 dB`.
  So the first local-window SI-SDR continuation on this route is also closed:
  it is not a new regime,
  just another way to move farther along the same guardrail-versus-local surface.
- `v229 = v226 + extra_prediction_source estimated_waveform_pre_dual_residual_correction`
  tested whether the
  `v226`
  route was mainly limited by supervising too early an output.
  This output-position-only move stayed training-real,
  but fixed behavior was slightly negative:
  relative
  `v226`,
  direct fixed deltas became
  `-0.0151 / -0.0092 / -0.0167 / -0.0061 / -0.0009 dB`.
  Relative
  `v157`,
  they were
  `-0.0203 / -0.0300 / -0.0105 / -0.0297 / +0.0217 dB`.
  So simply moving the local supervision target farther downstream,
  without opening that route's own writer,
  does not help.
- `v230 = v229 + branch_overlap_refine_present_head`
  tested the first obvious capacity increase on that later pre-dual route.
  This run was training-real
  (`790022 / 8352912` trainable,
  final
  `val_reconstruction_extra_stft_l1 = 0.020163`),
  but the fixed outcome was immediate strong tradeoff.
  Relative
  `v226`,
  direct fixed deltas became
  `-1.1727 / -0.9902 / -0.4938 / -0.7442 / +1.0956 dB`.
  Relative
  `v157`,
  they became
  `-1.1778 / -1.0109 / -0.4876 / -0.7678 / +1.1182 dB`.
  So the first pre-dual writable-path widening is now bounded too:
  it buys blocker gain by burning large guardrail margin,
  not by opening a selective regime.
- `v231 = v226 + estimated_waveform_post_refine_present + branch_overlap_refine_present_head`
  tested whether the
  `v230`
  tradeoff was mainly caused by the local objective still backpropagating through the frozen cancel path.
  This new pre-cancel output hook was training-real,
  but the fixed outcome was worse than
  `v230`.
  Relative
  `v230`,
  direct fixed deltas became
  `-0.2026 / -0.1462 / -0.1320 / -0.1930 / +0.0673 dB`.
  Relative
  `v157`,
  they became
  `-1.3804 / -1.1572 / -0.6196 / -0.9608 / +1.1856 dB`.
  So the frozen cancel route was not the main problem:
  the
  `refine_present`
  writer itself is already on the wrong tradeoff surface for this blocker.
- `v232 = v226 + pre_present_applied_delta_local_waveform_weight 0.5`
  tested whether the writable pre-present family was mainly missing direct supervision
  on the actual delta written by
  `branch_overlap_cancel_pre_present_controller`,
  rather than another full-output quality term.
  This continuation was training-real
  (`val_pre_present_applied_delta_local_waveform_l1 = 0.001274`),
  but output-side it was practical tie to slightly negative.
  Relative
  `v226`,
  direct fixed deltas became
  `-0.0175 / -0.0068 / -0.0229 / +0.0135 / -0.0149 dB`.
  Relative
  `v157`,
  they became
  `-0.0226 / -0.0275 / -0.0167 / -0.0101 / +0.0078 dB`.
  So directly supervising the actual pre-present applied delta does not open a new selective regime on this writer family.
- `v233 = v224 + local_prediction_source estimated_waveform_refine_base + branch_overlap_refine_head`
  tested whether the next useful writable-path change was to keep the safe keep route on
  `estimated_waveform_post_pre_present_controller`
  while moving the blocker-local objective onto the earlier
  `branch_overlap_refine_head`
  writer through a separate
  `local_prediction_source`.
  This continuation was clearly training-real
  (`val_extra_local_waveform_l1 = 0.001263`),
  and it was not a no-op.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.7918 / +0.0617 / +0.1080 / -0.4197 / +0.6625 dB`.
  Relative
  `v157`,
  they became
  `-0.7969 / +0.0602 / +0.1109 / -0.4276 / +0.6780 dB`.
  So the first
  `refine_base`
  local-only writer route is a steep mixed exchange surface,
  not a selective regime.
- `v234 = v224 + overlap_dual_residual_correction_local_sisdr_weight 0.001`
  tested whether the best still-open
  `v224`
  branch was mainly limited by waveform L1,
  by adding an interval SI-SDR term on the same writable
  `branch_overlap_dual_residual_correction`
  estimate.
  This continuation was clearly training-real
  (`val_overlap_dual_residual_correction_local_sisdr_loss = 0.323750`),
  but fixed-proxy behavior shifted only slightly and in the wrong local direction.
  Relative
  `v224`,
  direct fixed deltas became
  `+0.0320 / +0.0118 / +0.0037 / +0.0441 / -0.0373 dB`.
  Relative
  `v157`,
  they became
  `+0.0269 / +0.0103 / +0.0067 / +0.0363 / -0.0218 dB`.
  So the first local-window SI-SDR continuation on the writable residual-correction branch behaves like a mild regularizer,
  not a blocker-solving local objective.
- `v235 = v224 + sparse controller selectivity`
  kept the
  `v224`
  family intact,
  preserved the local controller term inside
  `local_proxy_intervals`,
  and added an explicit complement-interval controller term that pushes the same controller toward
  `0`
  outside the blocker windows.
  This continuation was clearly training-real
  (`val_overlap_dual_residual_correction_local_controller_l1 = 0.121247`,
  `val_overlap_dual_residual_correction_nonlocal_controller_l1 = 0.012859`),
  but fixed-proxy behavior was practical tie to slightly negative relative to
  `v224`.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.0055 / -0.0091 / -0.0054 / +0.0136 / -0.0040 dB`.
  Relative
  `v157`,
  they became
  `-0.0106 / -0.0106 / -0.0024 / +0.0058 / +0.0115 dB`.
  So sparse controller shaping on this writable residual-correction branch does not sharpen the blocker.
- `v236 = v224 + branch_overlap_dual_decoder_head`
  kept the
  `v224`
  loss unchanged
  and widened only the trainable set by opening the upstream
  `branch_overlap_dual_decoder_head`
  alongside the existing writable residual-correction heads.
  This continuation was clearly training-real
  (`790022 / 8352912` trainable,
  `9.4580%`),
  but output-side it only steepened the same mild tradeoff surface.
  Relative
  `v224`,
  direct fixed deltas became
  `-0.0320 / -0.0320 / -0.0163 / -0.0203 / +0.0323 dB`.
  Relative
  `v157`,
  they became
  `-0.0371 / -0.0335 / -0.0133 / -0.0282 / +0.0478 dB`.
  So simple upstream widening on this writable residual-correction family is not the missing regime change.
- `v237 = v212 + dedicated dual-local writer bridge`
  tested whether the next useful structural change was not another continuation on the already-bounded
  `v224`
  writer,
  but a fresh local-only writer that reads the dual auxiliary path and writes through its own dedicated bridge.
  This continuation was clearly training-real
  (`395011 / 8747923` trainable,
  `4.5155%`),
  but fixed-proxy behavior was a clear guardrail-for-local tradeoff.
  Relative
  `v212`,
  direct fixed deltas became
  `-0.2272 / -0.1451 / -0.1393 / -0.1284 / +0.0722 dB`.
  Relative
  `v157`,
  they became
  `-0.2584 / -0.1607 / -0.1532 / -0.1332 / +0.0728 dB`.
  So the first dedicated dual-local bridge route is structurally new,
  but it is still not a selective regime.

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
- simple keep-output weight strengthening on the pre-present keep-output plus dual residual-correction family
- `branch_protect_guard_sisdr_weight` sweep on that same pre-present keep-output plus dual residual-correction family
- `overlap_dual_residual_target_projection_weight` retune on that same pre-present keep-output plus dual residual-correction family
- `overlap_dual_residual_correction_local_waveform_weight` micro-sweep on that same family by default
- `overlap_dual_residual_correction_local_controller_weight` micro-sweep on that same family by default
- `overlap_dual_residual_correction_local_sisdr_weight` retune on that same family by default
- sparse local plus nonlocal controller shaping on that same family by default
- simple upstream `branch_overlap_dual_decoder_head` widening on top of `v224` by default
- first-launch `branch_overlap_dual_local_bridge` local-waveform continuation by default
- `extra_local_waveform_weight` micro-sweep on the writable pre-present main-output route by default
- `extra_local_sisdr_weight` micro-sweep on that same writable pre-present main-output route by default
- direct `pre_present_applied_delta_local_waveform_weight` continuation on that same writable pre-present family by default
- direct local-only writable retargeting to
  `estimated_waveform_refine_base`
  through
  `branch_overlap_refine_head`
  while keep still writes through
  `estimated_waveform_post_pre_present_controller`
- output-position-only retargeting to
  `estimated_waveform_pre_dual_residual_correction`
  without opening that route's own writer
- simple
  `branch_overlap_refine_present_head`
  widening on that same pre-dual writable-output route
- simple local-output continuations through the same
  `branch_overlap_refine_present_head`
  writer,
  including the new pre-cancel
  `estimated_waveform_post_refine_present`
  hook

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
- Disjoint-downstream keep-output safe-but-local-negative evidence on top of `v206`:
  `v211`
- Higher local-blend near-tie tradeoff on that same disjoint-downstream family:
  `v212`
- Stronger keep-output weights practical tie on that same family:
  `v213`
- Guard-SI-SDR keep-objective practical ties on that same family:
  `v214`
  to
  `v216`
- Teacher-overlap keep-objective tradeoff continuation on that same family:
  `v217`
  and
  `v218`
- Keep-path widening through the same cancel estimate on that same family:
  `v219`
- Local target-projection scalar retunes practical tie on that same family:
  `v220`
  and
  `v221`
- Weak positive but below-promotion local-window writable-branch evidence on that same family:
  `v224`
- First controller-local supervision reject on that same family:
  `v225`
- First writable-path-change mild tradeoff evidence on the writable pre-present main-output route:
  `v226`
- Higher-weight closure reject on that same writable pre-present main-output family:
  `v227`
- First local-window SI-SDR continuation reject on that same writable pre-present main-output family:
  `v228`
- Later-output retarget reject on the pre-dual writable route:
  `v229`
- First route-capacity widening reject on that same pre-dual writable route:
  `v230`
- Pre-cancel writable-output reject on that same `refine_present` writer family:
  `v231`
- Direct pre-present applied-delta supervision practical-tie continuation on the writable pre-present family:
  `v232`
- First `refine_base` local-only writer strong exchange-surface reject:
  `v233`
- First residual-correction local-window SI-SDR practical-tie-to-negative continuation:
  `v234`
- First sparse local plus nonlocal controller continuation practical tie:
  `v235`

## Next Valid Directions

- Do not continue the projection-weight sweep.
- Do not continue the broader-path waveform-local sweep.
- Do not continue small local unfreeze around the same pre-present controller family.
- Do not continue paired keep objectives that act on the same controller or the same final output.
- Do not continue keep-preserve routes that change only the reference path while still constraining the same final output.
- Do not continue auxiliary-only routes that still share the same trainable broader-path temporal or gate modules.
- Do not treat `dual final_output + max_blend 0` as a non-writing auxiliary mode.
- Do not continue the current no-write dual objective pair on the active local blocker.
- Do not continue scalar target-projection retunes on the same
  `v212`
  disjoint route.
- Do not keep micro-sweeping
  `overlap_dual_residual_correction_local_waveform_weight`
  by default.
  If this newer family continues,
  change the local objective more structurally on the same writable branch,
  or change the writable path itself.
- Do not keep micro-sweeping
  `overlap_dual_residual_correction_local_controller_weight`
  by default.
  This first controller-local continuation is training-real,
  but it does not improve the fixed-proxy surface relative to
  `v224`.
- Do not keep micro-sweeping
  `overlap_dual_residual_correction_local_sisdr_weight`
  by default.
  `v234`
  is clearly training-real,
  but it nudges the four non-blocker checks slightly positive while pushing the active local blocker slightly negative relative to
  `v224`.
- Do not keep micro-sweeping sparse controller shaping on the same writable residual-correction branch by default.
  `v235`
  is clearly training-real,
  but it stays practical tie to slightly negative relative to
  `v224`.
- Do not keep micro-sweeping
  `extra_local_waveform_weight`
  on the writable
  `estimated_waveform_post_pre_present_controller`
  route by default.
  The first
  `0.5 -> 2.0`
  sweep is training-real,
  but it only steepens the guardrail-versus-local exchange surface.
- Do not keep micro-sweeping
  `extra_local_sisdr_weight`
  on that same writable
  `estimated_waveform_post_pre_present_controller`
  route by default.
  The first continuation is training-real,
  but it almost exactly reproduces the
  `v227`
  high-tradeoff shape.
- Do not continue output-position-only retargeting from
  `estimated_waveform_post_pre_present_controller`
  to
  `estimated_waveform_pre_dual_residual_correction`
  by default.
  The first later-output launch
  `v229`
  is slightly negative relative to
  `v226`.
- Do not continue simple
  `branch_overlap_refine_present_head`
  widening on that same pre-dual writable route by default.
  `v230`
  is training-real,
  but it turns the route into a strong guardrail-for-local tradeoff.
- Do not continue local-output retargets that still write through the same
  `branch_overlap_refine_present_head`
  path by default,
  including the new
  `estimated_waveform_post_refine_present`
  hook.
  `v231`
  shows that removing the frozen cancel stage does not rescue this family;
  it makes the same tradeoff even steeper.
- Do not keep micro-sweeping
  `pre_present_applied_delta_local_waveform_weight`
  on the writable
  `branch_overlap_cancel_pre_present_controller`
  family by default.
  `v232`
  is training-real,
  but it is practical tie to slightly negative relative to
  `v226`.
- Do not keep micro-sweeping a split-route local-only writer that uses
  `estimated_waveform_refine_base`
  through
  `branch_overlap_refine_head`
  while keep still uses
  `estimated_waveform_post_pre_present_controller`.
  `v233`
  is clearly training-real,
  but it buys blocker gain mainly by spending abstention and artifact margin.
- Do not keep widening the same writable residual-correction family
  only by unfreezing the upstream
  `branch_overlap_dual_decoder_head`
  on top of
  `v224`
  by default.
  `v236`
  is clearly training-real,
  but it only steepens the same mild guardrail-for-local tradeoff.
- Do not keep micro-sweeping the same first-launch
  `branch_overlap_dual_local_bridge`
  writer by default.
  `v237`
  is clearly training-real,
  but it buys blocker gain mainly by spending material guardrail margin relative to
  `v212`.
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
- Do not continue simple keep-output weight strengthening on the same pre-present keep-output plus dual residual-correction family.
- Do not continue `branch_protect_guard_sisdr_weight` sweeps on that same pre-present keep-output plus dual residual-correction family.
- Do not continue `branch_protect_teacher_overlap_weight` sweeps on that same pre-present keep-output plus dual residual-correction family.
- Do not continue simple keep-path widening through `branch_overlap_cancel_head` on that same pre-present keep-output plus dual residual-correction family.
- If this newer family continues,
  prefer a qualitatively different keep objective or a more expressive keep path on the same disjoint downstream route,
  not another scalar retune or same-cancel-estimate widening on the same route.

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
- `reports/daily/2026-03-30_prepresentkeepoutput_dualresidual_v211_v213_followup.md`
- `reports/daily/2026-03-30_prepresentkeepoutput_guardsisdr_v214_v216_followup.md`
- `reports/daily/2026-03-30_prepresentkeepoutput_teacheroverlap_v217_v218_followup.md`
- `reports/daily/2026-03-30_prepresentkeepoutput_widencancelhead_v219_followup.md`
- `reports/daily/2026-03-30_dualrescorr_localwindow_v222_v224_followup.md`
- `reports/daily/2026-03-31_dualrescorr_localcontroller_v225_followup.md`
- `reports/daily/2026-03-31_extralocalwave_v226_v227_followup.md`
- `reports/daily/2026-03-31_extralocalsisdr_v228_followup.md`
- `reports/daily/2026-03-31_predudual_writablepath_v229_v230_followup.md`
- `reports/daily/2026-03-31_postrefinepresent_writablepath_v231_followup.md`
- `reports/daily/2026-03-31_prepresent_applied_delta_v232_followup.md`
- `reports/daily/2026-03-31_refinebase_localwriter_v233_followup.md`
- `reports/daily/2026-03-31_dualrescorr_localsisdr_v234_followup.md`
- `reports/daily/2026-03-31_dualrescorr_sparsecontroller_v235_followup.md`
- `reports/daily/2026-03-31_dualrescorr_dualheadopen_v236_followup.md`
- `reports/daily/2026-03-31_duallocalbridge_localwave_v237_followup.md`
- `reports/daily/2026-03-28_encoding_and_active_doc_audit.md`

