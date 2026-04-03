# 2026-04-02 `v273` combo listening asset

## Summary

- Status:
  asset-only continuation, no new training
- Decision:
  use a single combined blind pack for the next human check on
  `v249` versus `v273`
  instead of listening to the artifact and leak slices as two separate packs first

## New Assets

- Combined manifest:
  `data/probes/near_real_interval_artifact_leak_combo_probe_v1_manifest.jsonl`
- Combined blind A/B pack:
  `reports/eval/ab_inference_near_real_interval_artifact_leak_combo_probe_v1_hardlocalmask_v249_vs_hybridadapterartifactoverlay_v273_blind`
- Focused artifact-only blind A/B pack:
  `reports/eval/ab_inference_near_real_interval_artifact_probe_v3_subspan_hardlocalmask_v249_vs_hybridadapterartifactoverlay_v273_blind`
- Leak-only blind A/B pack:
  `reports/eval/ab_inference_near_real_interval_leak_probe_v1_hardlocalmask_v249_vs_hybridadapterartifactoverlay_v273_blind`

## Asset Design

- The combo manifest contains
  `18`
  rows:
  `9`
  rows from
  `near_real_interval_artifact_probe_v3_subspan`
  and
  `9`
  rows from
  `near_real_interval_leak_probe_v1`.
- The intent is not to create a new automatic metric.
- The intent is to give the next human pass a single pack that can answer both:
  - does
    `v273`
    sound better on the target-conditioned artifact slice
  - does it keep leak behavior at least neutral on the leak-control slice

## Why This Matters

- `v273`
  is now the first adapter-family point that keeps the fixed synthetic five-pack
  and the interval-aware leak probe exact tie to
  `v249`
  while remaining clearly positive on the active real artifact probes.
- So the next highest-value validation is no longer another same-family scalar retune.
- The next highest-value validation is a focused human check on whether the real artifact gain is audible
  without introducing a meaningful leak regression.

## Next Step

- Prefer the combo pack first for human review.
- If the combo review shows a clear artifact win without a clear leak cost,
  then follow with the tighter artifact-only pack for more detailed notes.
