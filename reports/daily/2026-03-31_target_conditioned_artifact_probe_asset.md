# 2026-03-31 target-conditioned artifact probe asset

## Summary

- Goal:
  turn the new listening clue into a reusable real-side probe asset.
- Result:
  a dedicated
  `near_real_target_conditioned_artifact_probe_v1`
  manifest and blind pack now exist for
  `v240`
  versus
  `v249`,
  and can be reused for future candidates.

## Why This Asset Exists

- The reduced
  `diverse8`
  listening pass suggested that a short telephone-like or synthetic artifact may be tied to the target audio itself,
  not only to interference leak.
- The clearest evidence came from
  `probe_0011`
  and
  `probe_0014`,
  where the target source is the same
  `segment_0010_0000058750_0000060100`
  but the interference clip changes.
- I also included
  `probe_0017`
  so the same target segment is checked against a third interference position with the same gain.

## New Assets

- Manifest:
  `data/probes/near_real_target_conditioned_artifact_probe_v1_manifest.jsonl`
- Blind pack:
  `reports/eval/ab_listening_pack_near_real_target_conditioned_artifact_probe_v1_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`

## Pack Contents

- `probe_0011`
  same target segment,
  interference clip
  `friend_anchor_45s`
- `probe_0014`
  same target segment,
  interference clip
  `friend_anchor_215s`
- `probe_0017`
  same target segment,
  interference clip
  `friend_absent_820s`

All three use the same gain
`-5.5 dB`
so the asset isolates interference-position changes instead of gain changes.

## Intended Use

- Use this pack when a future candidate claims to reduce leak but may actually be changing a target-conditioned artifact.
- If the same telephone-like artifact persists across all three rows,
  the failure is likely target-linked rather than a pure interference-leak effect.
- If the artifact changes materially with interference position while the target segment stays fixed,
  that is stronger evidence that the route is interacting with interference leak.
