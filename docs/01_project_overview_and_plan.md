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
  `2026-03-29`
- Active automatic base:
  `v157`
- Mechanism-positive evidence point:
  `v172`
- Current status:
  no listening candidate
- Current decision:
  keep `v157` as active base;
  `v191` remains the structural monitor-coupling milestone;
  `v192` rejected as a direct-monitor-supervision follow-up
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
- The most reasonable next options are:
  - do not continue direct monitor-controller supervision alone on top of `v191`
  - add a local-blocker-specific interval loss on the monitor controller output
    so it is penalized when it fails to reduce output in local leak windows
  - add an audibility-style gate target on the same monitor path
    to test whether a softer sample-conditioned target is more selective than plain absent or keep supervision
  - increase `monitor_max_blend` to check if stronger coupling starts to move the local blocker
  - add a disjoint local objective directly on the monitor controller path using the proven selector

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
- `reports/daily/2026-03-28_encoding_and_active_doc_audit.md`







