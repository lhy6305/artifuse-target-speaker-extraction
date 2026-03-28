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

## Current Safe Defaults

- Keep `v157` as the active base.
- Keep `v172` as mechanism-positive evidence only.
- If this branch resumes, prefer keep preservation that is orthogonal to the local objective over more calibration of the same route.
