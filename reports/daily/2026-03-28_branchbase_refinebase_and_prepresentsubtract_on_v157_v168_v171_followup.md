# 2026-03-28 corrected `branch_base_blend` / `refine_base_blend` and `pre_present_subtract` on `v157`: `v168 / v169 / v170 / v171` follow-up

## Summary

- Correction:
  `v166 / v167`
  are now marked as invalid scratches because the restored check found
  `overlap_cancel / absent`
  selector config was missing there.
  Their
  `gate_absent_mean / gate_keep_mean = 0.0`
  and controller weights staying bitwise-identical to
  `v157`
  were caused by selector mismatch, not by the
  `branch_base_blend`
  mechanism itself.
- Corrected conclusion:
  once selectors are restored,
  `branch_base_blend`
  is still a real reject,
  and
  `refine_base_blend`
  only narrows the damage but does not cross the guardrail bar.
- New timing probe:
  `v171 = v157 + pre_present_subtract`
  is mechanism-on and fixed-check safe,
  but it fails the near-real gate because
  `near_real_0007`
  whole tradeoff collapses even though local total leak finally flips the right way.
- Active base remains:
  `v157`.

## `v168 = v157 + corrected branch_base_blend`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v168_v157_applycontroller_intervalveto_branchbaseblend_fixselectors_v1_ft1`
- Restored selectors:
  - `overlap_cancel` focus ids:
    `reports/data/v152_overlap_cancel_focus_sample_ids.txt`
  - `absent_focus_patterns`:
    `target_absent_head / target_absent_tail`
  - `absent_require_speech_interference = true`
- Training signal is real:
  - selector hits:
    `overlap_cancel train 33 / 233, val 7 / 67`
  - absent hits:
    `train 95 / 233, val 24 / 67`
  - final gate means:
    `train_gate_absent_mean = 0.1870`
    / `train_gate_keep_mean = 0.0998`
    / `val_gate_absent_mean = 0.2446`
    / `val_gate_keep_mean = 0.0690`
- Fixed checks relative `v157`:
  - abstention `-2.8097 dB`
  - same-gender keep `-2.2604 dB`
  - hard-present keep `-1.8620 dB`
  - artifact proxy `-1.7195 dB`
  - local speech leak proxy `+0.6641 dB`
- Verdict:
  corrected
  `branch_base_blend`
  is not an inference-only rewrite artifact;
  it is a real mechanism-on reject.

## `v169 = v157 + corrected refine_base_blend`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v169_v157_applycontroller_intervalveto_refinebaseblend_fixselectors_v1_ft1`
- Key change:
  blend toward
  `refine_base - cancel`
  instead of
  `branch_base - cancel`
- Fixed checks relative `v157`:
  - abstention `-1.8759 dB`
  - same-gender keep `-1.7629 dB`
  - hard-present keep `-1.3051 dB`
  - artifact proxy `-1.4098 dB`
  - local speech leak proxy `+0.5827 dB`
- Verdict:
  `refine_base_blend`
  is better than
  `branch_base_blend`,
  but still far too negative on all four guardrails.

## `v170 = v157 + refine_base_blend max_blend 0.2`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v170_v157_applycontroller_intervalveto_refinebaseblend_maxblend02_v1_ft1`
- Training signal stayed alive with the same selector coverage as
  `v168 / v169`.
- Fixed checks relative `v157`:
  - abstention `-2.0514 dB`
  - same-gender keep `-1.8388 dB`
  - hard-present keep `-1.3761 dB`
  - artifact proxy `-1.4598 dB`
  - local speech leak proxy `+0.6458 dB`
- Verdict:
  lowering
  `max_blend`
  does not rescue
  `refine_base_blend`.
  This family stops here.

## `v171 = v157 + pre_present_subtract`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v171_v157_prepresentsubtract_intervalveto_v1_ft1`
- New code support:
  - `branch_overlap_cancel_apply_mode = pre_present_subtract`
  - semantics:
    apply overlap-cancel on
    `refine_base`
    before replaying the existing
    `present_head`
- Trainable set remains minimal:
  `branch_overlap_cancel_apply_controller_head`
- Training signal is real:
  - selector hits:
    `overlap_cancel train 33 / 233, val 7 / 67`
  - absent hits:
    `train 95 / 233, val 24 / 67`
  - final gate means:
    `train_gate_absent_mean = 0.1870`
    / `train_gate_keep_mean = 0.0998`
    / `val_gate_absent_mean = 0.2427`
    / `val_gate_keep_mean = 0.0694`

### Fixed Checks relative `v157`

- abstention `-0.0064 dB`
- same-gender keep `+0.0019 dB`
- hard-present keep `-0.0058 dB`
- artifact proxy `-0.0051 dB`
- local speech leak proxy `-0.0103 dB`

### Near-real Whole relative `v157`

- overall:
  `more_interference_leaky = v171:1, tie:3`
  and
  `better_retention_minus_leak = v157:1, tie:2, n/a:1`
- decisive blocker:
  `near_real_0007`
  - `delta_interference_capture_db = +27.3024 dB`
  - `delta_retention_minus_leak_db = -27.3334 dB`
- minor side effects:
  - `near_real_0003`
    `delta_interference_capture_db = -0.2648 dB`
    / `delta_retention_minus_leak_db = +0.2647 dB`
  - `near_real_0006`
    `delta_interference_capture_db = -0.0441 dB`
    / `delta_retention_minus_leak_db = +0.0441 dB`
  - `near_real_0009`
    absent whole leak `-0.6549 dB`

### Near-real Local relative `v157`

- `near_real_0007`
  finally flips the total-leak direction:
  - `delta_total_interference_capture_db = -1.5087 dB`
  - `delta_retention_minus_total_leak_db = +1.4923 dB`
- but the same sample gets worse on speech-only local leak:
  - `delta_speech_interference_capture_db = +5.5358 dB`
  - `delta_retention_minus_speech_leak_db = -5.5522 dB`
- `near_real_0009`
  absent local leak is slightly worse:
  `+0.2099 dB`
- `near_real_0003 / 0006`
  stay in error-level tie.

### Verdict

- `pre_present_subtract`
  proves that changing cancel timing can flip
  `near_real_0007 total leak`
  the right way.
- But with the current shared controller supervision,
  this comes at the cost of:
  - much worse
    `0007 speech_only`
  - much worse
    whole
    `0007`
    tradeoff
- So
  `v171`
  is a mixed mechanism-positive reject,
  not a candidate.

## Final Verdict

- `v165`
  still stands:
  broader
  `present-total`
  local assets do not unlock
  `v157 + no-teacher refine_base`.
- `v168`
  is the corrected
  `branch_base_blend`
  reject.
- `v169 / v170`
  close
  `refine_base_blend`
  and its
  `max_blend`
  calibration.
- `v171`
  closes the simplest
  `pre_present`
  timing rewrite:
  timing alone can improve local total leak,
  but not without breaking the
  `0007`
  speech-only / whole tradeoff.

## Next Step

- Keep
  `v157`
  as the active base.
- Do not give listening commands.
- If continuing, do not keep sweeping:
  - `branch_base_blend`
  - `refine_base_blend`
  - `refine_base_blend + max_blend`
  - plain
    `pre_present_subtract`
- The next mechanism should decouple:
  - `0007 total-leak` control
  - from
    `speech-only / absent-veto`
    pressure,
  not just move the same shared controller earlier in the graph.
