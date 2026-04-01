# 2026-04-01 target-conditioned artifact probe v2 asset and validation

## Summary

- Goal:
  expand the original
  `3`
  row fixed-target artifact probe into a fuller same-target asset,
  then verify whether the old
  `v240 -> v249`
  read still holds.
- New assets:
  - `data/probes/near_real_target_conditioned_artifact_probe_v2_manifest.jsonl`
  - `data/probes/near_real_interval_artifact_probe_v2_manifest.jsonl`
- Construction rule:
  keep the same target segment
  `segment_0010_0000058750_0000060100`
  and include all
  `9`
  available rows across the three friend clips and three gain levels.
- Validation:
  on the interval-aware
  `v2`
  artifact probe,
  `v240 -> v249`
  stays strongly positive at
  `+0.9545 dB`
  with
  `9 / 9`
  improvements.
  `v249 -> v253`
  stays only mildly negative at
  `-0.0525 dB`
  with
  `2 / 9`
  regressions.
- Extra output:
  a blind A/B inference pack for
  `v240`
  versus
  `v249`
  on the full
  `v2`
  artifact asset now exists.

## Asset Contents

- Target segment:
  `segment_0010_0000058750_0000060100`
- Sample count:
  `9`
- Clip tags:
  - `friend_anchor_45s`
  - `friend_anchor_215s`
  - `friend_absent_820s`
- Gains:
  - `-7.0 dB`
  - `-5.5 dB`
  - `-4.0 dB`

## `v240 -> v249` on interval-aware artifact probe v2

- Compare output:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_on_near_real_interval_artifact_probe_v2`
- Overall:
  `+0.9545 dB`
  with
  `9 / 9`
  improvements
- Read:
  the original
  `3`
  row artifact conclusion was not a small-sample accident.
  The full same-target family still favors
  `v249`
  uniformly.

## `v249 -> v253` on interval-aware artifact probe v2

- Compare output:
  `reports/eval/compare_hardlocalmask_v249_vs_hardlocalmask_covctrl_v253_on_near_real_interval_artifact_probe_v2`
- Overall:
  `-0.0525 dB`
  with
  `0 improved / 2 regressed / 7 near tie`
- Read:
  the merged-bundle replay still gives back only a small amount on this target-conditioned artifact asset.
  The mild loss is concentrated in the stronger artifact rows
  (`probe_0017` and `probe_0018`).

## Blind Pack

- Output:
  `reports/eval/ab_inference_near_real_target_conditioned_artifact_probe_v2_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`
- Sample count:
  `9`
- Use:
  this is now the preferred listening asset if a larger same-target human check is needed.

## Conclusion

- Promote
  `near_real_target_conditioned_artifact_probe_v2`
  to the active target-conditioned artifact asset.
- The stronger
  `v2`
  validation confirms that the hardlocalmask family still owns the real-side edge,
  and that merged-bundle shift is only a secondary perturbation.
- The next experiment should target the target-conditioned artifact confound on top of
  `v249`,
  not continue the already closed
  `v253 -> v254/v255/v256/v257`
  merged-bundle artifact-local continuation family.
