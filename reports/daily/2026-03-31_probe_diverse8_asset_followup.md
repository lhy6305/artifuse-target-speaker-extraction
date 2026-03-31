# 2026-03-31 probe diverse8 asset followup

## Summary

- Goal:
  collapse the low-value gain triplets inside
  `near_real_speech_probe_v1`
  into a smaller listening asset after the user reported that mixture gain ratio did not materially change the audible outcome.
- Result:
  a new reduced manifest and blind pack were created for faster interval-aware listening follow-up.

## New Asset

- Manifest:
  `data/probes/near_real_speech_probe_v1_diverse8_manifest.jsonl`
- Blind pack:
  `reports/eval/ab_listening_pack_near_real_speech_probe_v1_diverse8_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`

## Selection Rule

- Keep one representative per
  `anchor x speech_clip_tag`
  bucket.
- Use the middle gain variant from each gain triplet because the completed and verbal listening read suggested the gain sweep itself has low perceptual information value.

## Selected Samples

- `near_real_0003 / friend_anchor_45s`:
  `probe_0002`
- `near_real_0003 / friend_anchor_215s`:
  `probe_0005`
- `near_real_0003 / friend_absent_820s`:
  `probe_0008`
- `near_real_0004 / friend_anchor_45s`:
  `probe_0011`
- `near_real_0004 / friend_anchor_215s`:
  `probe_0014`
- `near_real_0004 / friend_absent_820s`:
  `probe_0017`
- `near_real_0006 / guodegang_anchor_120s`:
  `probe_0020`
- `near_real_0006 / guodegang_absent_480s`:
  `probe_0023`

## Current Decision

- Do not keep using the full 24-sample gain-triplet pack as the default human-listening asset for this family.
- Prefer the new
  `diverse8`
  pack for future targeted listening,
  unless the task specifically needs gain-sensitivity analysis.
