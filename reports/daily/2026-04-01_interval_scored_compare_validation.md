# 2026-04-01 interval-scored compare validation for the current interval-aware real probes

## Summary

- Goal:
  verify whether the current
  `v240 / v249 / v253 / v257`
  interval-aware real conclusions depended on a compare-script scoring bug.
- Change:
  extend
  `scripts/eval/compare_checkpoints_on_manifest.py`
  with
  `--score-interval-source`
  so SI-SDR and waveform L1 can be computed inside
  `local_proxy`
  rather than over the whole utterance.
- Result:
  the branch conclusions do not change.
  On the current interval-aware real probes,
  the interval-scored numbers match the earlier whole-utterance numbers to rounding.
- Read:
  this is not because interval scoring is unnecessary in general.
  It is because the current interval-aware real assets use full-span local windows:
  `window_start_sec = 0.0`
  and
  `window_duration_sec = target_duration_sec`.
- Decision:
  keep the current
  `v240 -> v249`,
  `v249 -> v253`,
  and
  `v253 -> v257`
  conclusions unchanged.
  For any future interval-aware real asset whose local window is not full-span,
  use interval scoring by default.

## Tooling Change

- Updated:
  `scripts/eval/compare_checkpoints_on_manifest.py`
- New flag:
  `--score-interval-source {none, local_proxy, target_overlap, target_absent}`
- Behavior:
  when a score interval source is provided,
  the compare script still runs normal model inference,
  but SI-SDR and waveform L1 are computed only inside the selected intervals.

## Why The Current Numbers Stay The Same

- On
  `near_real_interval_leak_probe_v1`,
  the active metadata clones use
  `local_proxy.window_start_sec = 0.0`
  and
  `local_proxy.window_duration_sec = target_duration_sec`
  for every sample.
- On
  `near_real_interval_artifact_probe_v2`,
  the same full-span pattern holds.
- So for these two assets,
  `score over whole target clip`
  and
  `score over local_proxy`
  are equivalent.

## Revalidated Comparisons With `--score-interval-source local_proxy`

### `v240 -> v249`

- Leak probe:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_on_near_real_interval_leak_probe_v1_localproxy`
  gives
  `+0.4940 dB`
  with
  `9 / 9`
  improvements.
- Target-conditioned artifact probe v2:
  `reports/eval/compare_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_on_near_real_interval_artifact_probe_v2_localproxy`
  gives
  `+0.9545 dB`
  with
  `9 / 9`
  improvements.

### `v249 -> v253`

- Leak probe:
  `reports/eval/compare_hardlocalmask_v249_vs_hardlocalmask_covctrl_v253_on_near_real_interval_leak_probe_v1_localproxy`
  gives
  `+0.0045 dB`
  with
  `9`
  near ties.
- Target-conditioned artifact probe v2:
  `reports/eval/compare_hardlocalmask_v249_vs_hardlocalmask_covctrl_v253_on_near_real_interval_artifact_probe_v2_localproxy`
  gives
  `-0.0525 dB`
  with
  `2 / 9`
  regressions.

### `v253 -> v257`

- Leak probe:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_leak_probe_v1_localproxy`
  gives
  `-0.5154 dB`
  with
  `9 / 9`
  regressions.
- Target-conditioned artifact probe v2:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_artifact_probe_v2_localproxy`
  gives
  `-0.9587 dB`
  with
  `9 / 9`
  regressions.

## Conclusion

- The previous branch decisions stand.
- `v249` remains the leading hardlocalmask real-side evidence point.
- `v253` remains the necessary merged-bundle control and is still near tie to
  `v249`
  on leak and only mildly worse on target-conditioned artifact.
- `v257` remains closed as a bounded reject once the writer is actually activated.
- The next scientific move should still target the target-conditioned artifact confound on top of
  `v249`,
  not reopen the merged-bundle or dual-bridge hardlocalmask branches.
