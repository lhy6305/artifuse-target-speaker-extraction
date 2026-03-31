# 2026-03-31 hardlocalmask v249 probe listening followup

## Summary

- Goal:
  follow up the new interval-masked `v249` route with interval-aware blind listening-pack assets,
  instead of reusing the old whole `near_real_v1` real-eval pack that does not carry `local_proxy`.
- Result:
  the probe-side evidence stays positive for `v249`,
  and the new listening-pack analyses suggest that the real-side gain is not explained by simple bandwidth narrowing.
- Scientific read:
  `v249` remains a probe-positive but synthetic-guardrail-negative continuation.
  The new pack analyses strengthen the claim that the route is touching a real downstream-application issue,
  but they do not convert `v249` into a promotion candidate.

## Assets Exported

- Blind pack:
  `reports/eval/ab_listening_pack_near_real_speech_probe_v1_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`
- Blind pack:
  `reports/eval/ab_listening_pack_near_real_guodegang_transient_probe_v1_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`

Each pack was exported with interval-aware inference, so
`local_proxy_intervals`
were passed through the export path instead of being dropped.

## Analysis Results

### Broad speech probe pack

- Bandwidth analysis:
  `tie = 24 / 24`
- Transient analysis:
  `tie / file_a / file_b = 11 / 7 / 6`
- Tradeoff analysis:
  mean decoded metrics favor
  `hardlocalmask_v249`
  over
  `refinebase_artifactteacher_v240`
  on the broad probe pack:
  `target_capture_db -10.8616 vs -11.4593`,
  `interference_capture_db -34.7729 vs -33.6658`,
  `retention_minus_leak_db 23.9113 vs 22.2065`,
  `residual_output_share 0.5736 vs 0.6159`,
  `joint_fit_r2 0.4264 vs 0.3841`.
- Decoded tradeoff labels on the same pack:
  `better_source_retention = hardlocalmask_v249 8, tie 16`
  `more_interference_leaky = hardlocalmask_v249 13, refinebase_artifactteacher_v240 5, tie 6`
  `better_retention_minus_leak = hardlocalmask_v249 5, refinebase_artifactteacher_v240 4, tie 15`

Interpretation:
the pack does not show a global "narrower bandwidth" story,
and the transient read is mixed rather than one-sided.
The stronger signal is that
`v249`
usually improves target capture and average retention-minus-leak,
while also changing interference capture.
So the route looks more like a real tradeoff relocation than a trivial spectral collapse.

### Guodegang transient probe pack

- Bandwidth analysis:
  `tie = 6 / 6`
- Transient analysis:
  `tie / file_a / file_b = 3 / 2 / 1`
- Tradeoff analysis:
  mean decoded metrics still favor
  `hardlocalmask_v249`
  over
  `refinebase_artifactteacher_v240`:
  `target_capture_db -7.0329 vs -7.2619`,
  `interference_capture_db -25.9329 vs -25.6588`,
  `retention_minus_leak_db 18.9000 vs 18.3970`,
  `residual_output_share 0.5192 vs 0.5362`,
  `joint_fit_r2 0.4808 vs 0.4638`.
- Decoded tradeoff labels:
  `better_source_retention = tie 6`
  `more_interference_leaky = refinebase_artifactteacher_v240 2, tie 4`
  `better_retention_minus_leak = hardlocalmask_v249 2, tie 4`

Interpretation:
on the dedicated
`guodegang_raw / transient_like`
subset,
the pack again does not support a bandwidth-collapse explanation.
The aggregate tradeoff metrics still move slightly toward
`v249`,
which is directionally consistent with the earlier probe objective gains.

## Tooling Fix

- The original
  `scripts/eval/analyze_listening_pack_tradeoff.py`
  assumed synthetic-style
  `sample_meta.json`
  plus
  `components`.
- Probe assets instead carry
  `metadata.json`
  with
  `target_source`,
  `interference_layers`,
  and
  `target_segments`.
- I patched the script to:
  resolve metadata through the pack-recorded
  `metadata_path`
  when present,
  fall back to either
  `sample_meta.json`
  or
  `metadata.json`,
  and support probe-style reconstruction by using
  `target.wav`
  plus
  `mixture - target`
  when synthetic-style
  `components`
  are absent.

## Current Decision

- Keep
  `v157`
  as the active automatic base.
- Keep
  `v240`
  as the leading mixed synthetic-plus-near-real candidate inside the split-route
  `refine_base`
  family.
- Keep
  `v249`
  as a probe-positive real-side evidence point that is worth interval-aware listening follow-up,
  but not as a synthetic promotion candidate.

## Next Step

- Do not go back to the old whole
  `near_real_v1`
  pack as the decisive next gate for
  `v249`.
- Prefer either:
  interval-aware real assets with explicit
  `local_proxy`,
  or
  human listening on the two newly exported blind probe packs.
