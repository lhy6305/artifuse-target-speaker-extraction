# 2026-04-01 target-conditioned artifact probe v3 subspan asset and split-localmasked family screen

## Summary

- Goal:
  refine the target-conditioned artifact read from a full-span same-target probe into a tighter subspan probe,
  then decide whether the next branch should actually start a
  `v258`
  continuation on the existing
  `split_localmasked`
  writer family.
- Method:
  derive a subspan local window from the current
  `artifact_probe_v2`
  pack by finding the stable cross-interference peak in the target-error envelope,
  then re-score:
  - `v240 -> v249`
  - `v249 -> v253`
  - `v253 -> v257`
  - `v253 -> v255`
  - `v253 -> v256`
  and the corresponding
  `v249`
  comparisons where relevant.
- Result:
  the tighter artifact read strengthens the
  `v249`
  real-side edge rather than weakening it,
  but it does not rescue the existing
  `split_localmasked`
  artifact-objective continuations.
- Decision:
  do not start
  `v258`
  as another small objective retune on the same
  `split_localmasked`
  writer family.
  The next branch should move to a different artifact-specific writer or to a new training asset family,
  not keep iterating the current
  `v255 / v256`
  route.

## Subspan Asset Construction

- New manifest:
  `data/probes/near_real_interval_artifact_probe_v3_subspan_manifest.jsonl`
- Rows:
  `9`
- Parent asset:
  `near_real_target_conditioned_artifact_probe_v2`
- Window:
  `start = 0.90s`
  and
  `duration = 0.22s`
- Construction rule:
  use the existing
  `v240`
  versus
  `v249`
  artifact probe v2 inference pack,
  align all
  `9`
  same-target rows,
  compute the smoothed absolute target-error envelope,
  and select the stable cross-interference peak region.
- Peak read:
  the strongest shared peak lands near
  `0.97s`,
  with the next peak near
  `1.08s`.
  Across all
  `9`
  rows,
  the chosen
  `0.90s - 1.12s`
  window carries about
  `4.4x - 4.7x`
  the full-clip average target-error energy.

## `v240 -> v249` on the Subspan Artifact Probe

- Compare output:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `+0.9956 dB`
  with
  `9 / 9`
  improvements
- Read:
  the target-conditioned artifact edge of
  `v249`
  survives the tighter local window and is slightly stronger than on the full-span
  `artifact_probe_v2`
  read.

## `v249 -> v253` on the Subspan Artifact Probe

- Compare output:
  `reports/eval/compare_hardlocalmask_v249_vs_hardlocalmask_covctrl_v253_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `-0.0483 dB`
  with
  `2 / 9`
  regressions
- Read:
  the merged-bundle replay stays only mildly negative on the tighter artifact slice.
  This matches the earlier conclusion that merged-bundle shift is not the main blocker.

## `v253 -> v257` on the Subspan Artifact Probe

- Compare output:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `-1.0061 dB`
  with
  `9 / 9`
  regressions
- Read:
  the dual-bridge hardlocalmask source swap remains a bounded reject on the tighter local artifact target.

## Screen of Existing Split-Localmasked Artifact Continuations

### `v253 -> v255`

- Compare output:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_artifactlocalfinalextra_v255_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `-0.0258 dB`
  with no meaningful improvements

### `v249 -> v255`

- Compare output:
  `reports/eval/compare_hardlocalmask_v249_vs_artifactlocalfinalextra_v255_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `-0.0741 dB`
  with
  `3`
  regressions

### `v253 -> v256`

- Compare output:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_artifactlocalteacherfinal_v256_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `-0.0432 dB`
  with no meaningful improvements

### `v249 -> v256`

- Compare output:
  `reports/eval/compare_hardlocalmask_v249_vs_artifactlocalteacherfinal_v256_on_near_real_interval_artifact_probe_v3_subspan`
- Overall:
  `-0.0916 dB`
  with
  `3`
  regressions

## Interpretation

- The subspan probe validates the core
  `v249`
  story more strongly:
  the hardlocalmask family is not merely better on a broad whole-window target-conditioned artifact read.
  It is still better when the artifact slice is narrowed to the strongest shared local peak.
- But this same tighter probe does not rescue the current artifact-objective continuations on the same
  `split_localmasked`
  writer.
  Both the raw-target extra route
  (`v255`)
  and the teacher-anchor route
  (`v256`)
  stay near tie to weak negative relative
  `v253`,
  and remain clearly negative relative
  `v249`.
- So the next step should not be:
  "start
  `v258`
  as another small loss or weight variation on the same
  `split_localmasked`
  writer."
- The tighter artifact probe now says the main problem is structural:
  the current writer family can produce the
  `v249`
  edge,
  but the existing artifact-objective add-ons do not improve that edge on the local artifact slice itself.

## Conclusion

- Promote
  `near_real_interval_artifact_probe_v3_subspan`
  as the active local target-conditioned artifact probe.
- Keep
  `v249`
  as the leading real-side evidence point.
- Keep
  `v253`
  as the merged-bundle control.
- Close the current
  `split_localmasked`
  artifact-objective continuation family as not worth another small retune.
- The next experimental plan should change writer family or training asset family,
  not continue the current
  `v255 / v256`
  style objective tuning on top of
  `v249 / v253`.
