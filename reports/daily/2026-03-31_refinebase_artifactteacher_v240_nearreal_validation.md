# 2026-03-31 near-real validation for the split-route `refine_base` candidate `v240`

## Summary

- Goal:
  validate whether
  `v240`,
  the first split-route
  `refine_base`
  point that is positive on all five active fixed synthetic checks versus
  `v157`,
  is ready to move from synthetic-only evidence into a real listening candidate.
- Validation scope:
  - near-real blind A/B pack on
    `near_real_v1`
  - objective
    bandwidth / transient / tradeoff
    diagnostics on the exported pack
  - a targeted
    `near_real_speech_probe_v1`
    compare to see whether the active speech-family blocker moved the right way
- Main result:
  `v240`
  is not listening-ready.
  The near-real whole tradeoff gate still fails on
  `target_present__speech`,
  and the transient heuristic is materially negative.
  But the route is also not a monolithic reject:
  the speech probe turns positive on the
  `friend_raw`
  blocker family and only regresses on the
  `guodegang_raw / transient_like`
  side.
- Verdict:
  keep
  `v157`
  as the active base.
  Keep
  `v240`
  as the leading mixed candidate inside the split-route
  `refine_base`
  family,
  but do not promote it and do not start formal listening review from it yet.
  The next step should target the
  `target_present__speech`
  whole-tradeoff failure and the
  `guodegang_raw / transient_like`
  transient drag,
  not another
  `branch_protect_teacher_overlap_weight`
  micro-sweep.

## Code Change

- None.
  This round only exported evaluation assets and ran existing analysis and gate scripts.

## Exported Assets

- Near-real blind A/B pack:
  `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_refinebase_artifactteacher_v240_blind`
- Near-real speech probe compare:
  `reports/eval/compare_stage2_vs_refinebase_artifactteacher_v240_on_near_real_speech_probe_v1`

## Near-Real Pack: `legacy_stage2` vs `v240`

- Pack:
  `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_refinebase_artifactteacher_v240_blind`
- Baseline:
  `legacy_stage2`
  =
  `v157`
- Candidate:
  `refinebase_artifactteacher_v240`

### Bandwidth

- Decoded narrowing counts:
  `legacy_stage2 = 1`,
  `v240 = 1`,
  `tie = 8`
- Read:
  bandwidth is not the primary blocker.
  The only explicit candidate-narrower sample is
  `near_real_0010`,
  while
  `near_real_0008`
  moves the opposite way.

### Transients

- Decoded transient-lossy counts:
  `v240 = 5`,
  `legacy_stage2 = 1`,
  `tie = 4`
- Worst candidate-lossy samples:
  - `near_real_0010`
    with
    `delta_presence_minus_mid_retention_db_mean_b_minus_a = -10.1161 dB`
    and
    `delta_strong_presence_loss_frame_ratio_b_minus_a = +0.7917`
  - `near_real_0005`
    with
    `-6.2952 dB`
    and
    `+0.5000`
  - `near_real_0007`
    with
    `-6.0593 dB`
    and
    `+0.6522`
  - `near_real_0006`
    with
    `-2.8787 dB`
    and
    `+0.5294`
  - `near_real_0009`
    with
    `-2.1330 dB`
    and
    `+0.3333`
- Read:
  transient-side damage is real and broad enough that this candidate should not go to listening by default.

### Whole Tradeoff Gate

- Gate:
  `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_refinebase_artifactteacher_v240_blind/tradeoff_analysis/gate_summary.json`
- Result:
  `overall_pass = false`
- Failed bucket:
  `target_present__speech`

### Whole Tradeoff Read

- Decoded whole-tradeoff counts:
  - `better_source_retention_label`:
    `v240 = 1`,
    `tie = 6`,
    `not_applicable = 3`
  - `more_interference_leaky_label`:
    `v240 = 5`,
    `legacy_stage2 = 2`,
    `tie = 1`,
    `not_applicable = 2`
  - `more_residual_heavy_label`:
    `tie = 10`
  - `better_retention_minus_leak_label`:
    `legacy_stage2 = 4`,
    `v240 = 1`,
    `not_applicable = 5`
- The decisive failure is the
  `target_present__speech`
  bucket:
  - `better_retention_minus_leak_label`:
    `legacy_stage2 = 3`,
    `v240 = 0`
  - `more_interference_leaky_label`:
    `legacy_stage2 = 0`,
    `v240 = 3`
- Per-sample shape inside that bucket:
  - `near_real_0003`
    `delta_interference_capture_db = +2.4809 dB`
    /
    `delta_retention_minus_leak_db = -2.3484 dB`
  - `near_real_0004`
    `+3.0824 dB`
    /
    `-3.0389 dB`
  - `near_real_0006`
    `+6.1639 dB`
    /
    `-6.0999 dB`
- Read:
  the route is not failing because of higher residual share.
  It is failing because the speech-present whole tradeoff still moves toward more leak than retained benefit.

### Phone-Artifact Gate

- Gate:
  `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_refinebase_artifactteacher_v240_blind/phone_artifact_gate_summary.json`
- Raw result:
  `overall_pass = false`
- But this output is not substantive for this round:
  all three required buckets are reported as
  `missing_bucket`.
  This is the same bucket-name mismatch issue seen in earlier pack analyses,
  not a new scientific failure specific to
  `v240`.

## Near-Real Speech Probe

- Compare:
  `reports/eval/compare_stage2_vs_refinebase_artifactteacher_v240_on_near_real_speech_probe_v1/summary.json`
- Analysis:
  `reports/eval/compare_stage2_vs_refinebase_artifactteacher_v240_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

### Probe Overall

- `avg_sisdr_delta_db = +0.1529`
- `improved_count = 11`
- `regressed_count = 3`
- `near_tie_count = 10`

### Probe By Anchor

- `near_real_0003`:
  `+0.2643 dB`
  with
  `6 improve / 0 regress / 3 tie`
- `near_real_0004`:
  `+0.1840 dB`
  with
  `5 improve / 0 regress / 4 tie`
- `near_real_0006`:
  `-0.0610 dB`
  with
  `0 improve / 3 regress / 3 tie`

### Probe By Speech Family

- `friend_raw`:
  `+0.2242 dB`
  with
  `11 improve / 0 regress / 7 tie`
- `guodegang_raw`:
  `-0.0610 dB`
  with
  `0 improve / 3 regress / 3 tie`

### Probe Read

- This is the most useful new information from the round.
  The route is not uniformly bad on speech families.
- The active
  `friend_raw`
  blocker family now moves in the right direction on the targeted probe,
  especially on:
  - `near_real_0003`
    `residual_transient_like`
  - `near_real_0004`
    `speech_leak_like`
- The remaining speech-side drag is concentrated on:
  - `near_real_0006`
    `guodegang_raw / transient_like`
  - the same family also shows up in the whole-pack transient heuristic.

## Conclusion

- `v240`
  survives the fixed synthetic screen,
  but it does not survive near-real whole validation yet.
- The scientific picture is now sharper:
  - fixed synthetic says the split-route
    `refine_base`
    family is finally nontrivial and can cross all five active fixed checks
  - near-real whole tradeoff says the candidate still leaks too much on
    `target_present__speech`
  - the near-real speech probe says the failure is not on
    `friend_raw`
    anymore;
    it is concentrated on the
    `guodegang_raw / transient_like`
    side and on broader transient behavior
- Keep
  `v157`
  as the active base.
- Keep
  `v240`
  as a bounded mixed candidate,
  not a listening-ready promotion.
- Do not start by retuning the same
  `branch_protect_teacher_overlap_weight`.
  If this family continues,
  the next continuation should target:
  - whole
    `target_present__speech`
    tradeoff repair
  - and the
    `near_real_0006 / guodegang_raw / transient_like`
    transient-side regression
  while preserving the new
  `friend_raw`
  gains.
