# 2026-03-28 parallel pre-present total-risk controller on `v157`: `v172 / v173` follow-up

## Summary

- New mechanism:
  `v172 = v157 + parallel pre-present total-risk controller`
  adds a second controller head that applies overlap-cancel on the
  `refine_base`
  path before the existing
  `present_head`,
  while leaving the original
  `v157`
  post-present interval-veto route intact.
- `v172`
  is the first continuation on top of
  `v157`
  that is positive on all four fixed synthetic guardrails at once after the recent
  `v168 / v169 / v170 / v171`
  reject cluster.
- But near-real still blocks promotion:
  `near_real_0007`
  local total leak improves,
  `near_real_0009`
  absent whole leak also improves,
  yet
  `0007`
  whole and speech-only both stay wrong-way.
- `v173 = v172 + pre_present_max_blend 0.1`
  confirms that simple amplitude scaling is not the fix:
  it shrinks both the good and bad effects together, so this family stays below promotion bar.
- Active base remains:
  `v157`.

## `v172 = v157 + parallel pre-present total-risk controller`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v172_v157_parallel_prepresent_totalrisk_controller_v1_ft1`
- New code support:
  - `enable_branch_overlap_cancel_pre_present_controller`
  - `branch_overlap_cancel_pre_present_max_blend`
  - `gate_pre_present_keep_weight`
- Trainable set:
  `branch_overlap_cancel_pre_present_controller_head`
- Init:
  `v157`
  best checkpoint, with teacher metadata fallback disabled
- Selector coverage:
  `overlap_cancel train 33 / 233, val 7 / 67`
- Training signal is real:
  epoch-1
  `train_gate_pre_present_keep_mean = 0.639066`
  /
  `val_gate_pre_present_keep_mean = 0.390970`
  ;
  final
  `train_gate_pre_present_keep_mean = 0.106705`
  /
  `val_gate_pre_present_keep_mean = 0.054194`

### Fixed Checks relative `v157`

- abstention `+0.0659 dB`
- same-gender keep `+0.0348 dB`
- hard-present keep `+0.0288 dB`
- artifact proxy `+0.0221 dB`
- local speech leak proxy `-0.0537 dB`

### Near-real Whole relative `v157`

- overall:
  `more_interference_leaky = v172:1, v157:1, tie:2`
  and
  `better_retention_minus_leak = v157:1, tie:2, n/a:1`
- positive evidence:
  - `near_real_0009`
    absent whole leak
    `delta_interference_capture_db = -3.1018 dB`
  - `near_real_0006`
    `delta_interference_capture_db = -0.4919 dB`
    /
    `delta_retention_minus_leak_db = +0.4906 dB`
  - `near_real_0003`
    `delta_interference_capture_db = -0.1727 dB`
    /
    `delta_retention_minus_leak_db = +0.1714 dB`
- blocker remains:
  `near_real_0007`
  - `delta_interference_capture_db = +23.1863 dB`
  - `delta_retention_minus_leak_db = -23.2420 dB`

### Near-real Local relative `v157`

- `near_real_0007`
  gives the desired total-risk signal:
  - `delta_total_interference_capture_db = -1.4142 dB`
  - `delta_retention_minus_total_leak_db = +1.3819 dB`
- but the same sample still regresses on speech-only leak:
  - `delta_speech_interference_capture_db = +2.9102 dB`
  - `delta_retention_minus_speech_leak_db = -2.9425 dB`
- `near_real_0009`
  absent local leak also regresses:
  `+2.4940 dB`
- `near_real_0006`
  remains modestly positive on both speech and total local leak:
  `-0.6585 dB`
  /
  `+0.6573 dB`

### Verdict

- `v172`
  is a mechanism-positive evidence point.
- It proves the parallel pre-present total-risk controller can:
  - keep all four fixed guardrails positive,
  - improve
    `0007 total leak`,
  - and improve
    `0009`
    absent whole leakage.
- But it still does not solve the key promotion gate because
  `0007`
  whole and speech-only remain wrong-way.

## `v173 = v172 + pre_present_max_blend 0.1`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v173_v172_parallel_prepresent_totalrisk_controller_maxblend01_v1_ft1`
- Key change:
  lower only
  `branch_overlap_cancel_pre_present_max_blend`
  from
  `0.2`
  to
  `0.1`
- Important interpretation:
  training trajectory and controller metrics stay effectively identical to
  `v172`,
  so this is a pure inference-scale calibration, not a new learned controller regime.

### Fixed Checks relative `v157`

- abstention `+0.0341 dB`
- same-gender keep `+0.0175 dB`
- hard-present keep `+0.0149 dB`
- artifact proxy `+0.0117 dB`
- local speech leak proxy `-0.0263 dB`

### Near-real Whole relative `v157`

- overall:
  `more_interference_leaky = v173:1, v157:1, tie:2`
  and
  `better_retention_minus_leak = v157:1, tie:2, n/a:1`
- `near_real_0007`
  whole regression shrinks but does not clear:
  - `delta_interference_capture_db = +16.5421 dB`
  - `delta_retention_minus_leak_db = -16.5700 dB`
- side effects also shrink on the positive side:
  - `near_real_0009`
    absent whole leak becomes only
    `-1.4132 dB`
  - `near_real_0006`
    `-0.2425 / +0.2418 dB`
  - `near_real_0003`
    `-0.0859 / +0.0853 dB`

### Near-real Local relative `v157`

- `near_real_0007`
  keeps the same mixed pattern at smaller magnitude:
  - `delta_speech_interference_capture_db = +1.5764 dB`
  - `delta_total_interference_capture_db = -0.6784 dB`
  - `delta_retention_minus_speech_leak_db = -1.5926 dB`
  - `delta_retention_minus_total_leak_db = +0.6622 dB`
- `near_real_0009`
  absent local leak still regresses:
  `+1.3362 dB`
- `near_real_0006 / 0003`
  remain minor positive or tie:
  `-0.3230 / +0.3224 dB`
  and
  `-0.0345 / +0.0338 dB`

### Verdict

- `v173`
  proves this is not a simple over-strength problem.
- Lowering
  `pre_present_max_blend`
  only scales the whole profile down:
  - less
    `0007`
    whole/speech-only damage,
  - but also less
    `0007 total leak`
    improvement and less
    `0009`
    absent-whole gain.
- Therefore this family should not continue along
  `pre_present_max_blend`
  sweep.

## Final Verdict

- Keep
  `v157`
  as the active base.
- Keep
  `v172`
  only as a mechanism-positive evidence point.
- Mark
  `v173`
  as the calibration reject that closes the simple
  `pre_present_max_blend`
  axis.
- No listening pack is exported.

## Next Step

- Do not continue:
  - `parallel pre-present total-risk controller + max_blend sweep`
  - same-controller amplitude calibration on this route
- If this branch continues, it should target selectivity rather than strength:
  the total-risk path must stop sharing the same dense apply pattern that still spills into
  `0007`
  speech-only / whole behavior.
