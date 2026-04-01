# 2026-04-01 interval-aware real scouting on `v240`, `v249`, and `v253`

## Summary

- Goal:
  use the new interval-aware real probes to decide whether the next move should stay on the merged-bundle
  `v253`
  line or return to the original
  `v249`
  hardlocalmask family.
- Method:
  compare
  `v240`
  versus
  `v249`
  and
  `v249`
  versus
  `v253`
  on:
  - `near_real_interval_leak_probe_v1`
  - `near_real_interval_artifact_probe_v1`
- Result:
  interval-aware real probes strongly confirm that
  `v249`
  is genuinely better than
  `v240`,
  not just on the old schema-inactive probe packs.
  They also show that the merged-bundle replay
  `v253`
  keeps almost all of that leak-side gain and only gives back a small amount on the artifact slice.
- Decision:
  merged-bundle shift is not the main blocker.
  The next branch should not keep exploring
  `v253 -> v254/v255/v256/v257`
  style merged-bundle artifact-local continuations by default.
  The more valuable direction is to return to the
  `v249`
  hardlocalmask family and target the target-conditioned artifact confound directly.

## `v240 -> v249` on interval-aware real probes

### Leak probe

- Compare output:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_on_near_real_interval_leak_probe_v1`
- Overall:
  `+0.4940 dB`
  with
  `9 / 9`
  improvements
- By speech family:
  - `friend_raw = +0.9050 dB`
  - `guodegang_raw = +0.2884 dB`
- By clip:
  - `friend_anchor_45s = +0.9539 dB`
  - `friend_anchor_215s = +0.9341 dB`
  - `friend_absent_820s = +0.8271 dB`
  - `guodegang_anchor_120s = +0.2851 dB`
  - `guodegang_absent_480s = +0.2911 dB`

### Artifact probe

- Compare output:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_on_near_real_interval_artifact_probe_v1`
- Overall:
  `+0.9545 dB`
  with
  `3 / 3`
  improvements
- By fixed-target clip:
  - `friend_anchor_45s = +0.9331 dB`
  - `friend_anchor_215s = +0.9725 dB`
  - `friend_absent_820s = +0.9578 dB`

## `v249 -> v253` on interval-aware real probes

### Leak probe

- Compare output:
  `reports/eval/compare_hardlocalmask_v249_vs_hardlocalmask_covctrl_v253_on_near_real_interval_leak_probe_v1`
- Overall:
  `+0.0045 dB`
  with
  `0 improved / 0 regressed / 9 near tie`
- Read:
  the merged-bundle control replay is effectively tie to
  `v249`
  on the interval-aware leak slice.

### Artifact probe

- Compare output:
  `reports/eval/compare_hardlocalmask_v249_vs_hardlocalmask_covctrl_v253_on_near_real_interval_artifact_probe_v1`
- Overall:
  `-0.0519 dB`
  with
  `0 improved / 1 regressed / 2 near tie`
- Read:
  the merged-bundle replay gives back only a small amount on the fixed-target artifact slice,
  mostly concentrated in
  `friend_absent_820s = -0.1249 dB`.

## Interpretation

- The interval-aware real probes now say something sharper than the old probe packs.
- First,
  `v249`
  is not merely a listening-confounded curiosity.
  Relative
  `v240`,
  it improves both the leak-focused and artifact-focused interval-aware real probes,
  and it does so uniformly.
- Second,
  the merged-bundle replay
  `v253`
  is not the core reason later merged-bundle branches failed.
  On the new interval-aware probes,
  it is almost exact tie to
  `v249`
  on leak and only mildly worse on artifact.
- So the current bottleneck is not
  "recover the whole
  `v249`
  interval-aware real edge after bundle shift."
  The bottleneck is
  "keep the
  `v249`
  interval-aware real edge while specifically repairing the target-conditioned artifact confound."

## Conclusion

- Keep
  `v249`
  as the leading interval-aware real-side evidence point for the hardlocalmask family.
- Keep
  `v253`
  as the merged-bundle control when a merged-bundle continuation is explicitly needed,
  but do not treat merged-bundle shift as the main blocker anymore.
- The next experiment should target the target-conditioned artifact confound directly,
  not continue the current merged-bundle artifact-local continuation family by inertia.
