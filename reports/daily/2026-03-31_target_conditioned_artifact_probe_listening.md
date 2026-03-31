# 2026-03-31 target-conditioned artifact probe listening

## Summary

- Goal:
  listen to a fixed-target probe that keeps the same target segment and gain while changing only the interference clip position.
- Result:
  the listening outcome supports the target-conditioned-artifact hypothesis.
  It does not show an audible difference between
  `v240`
  and
  `v249`.

## Listening Outcome

- Pack:
  `reports/eval/ab_listening_pack_near_real_target_conditioned_artifact_probe_v1_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`
- GUI summary:
  `3 / 3` scored,
  with
  `tie = 1`
  and
  `uncertain = 2`.
- Decoded result:
  no sample preferred either candidate.

## Per-Sample Read

- `probe_0011`:
  same target segment,
  interference clip
  `friend_anchor_45s`,
  note:
  severe artifact on the target audio itself,
  with no perceptible difference between the two candidates.
- `probe_0014`:
  same target segment,
  interference clip
  `friend_anchor_215s`,
  note:
  the artifact remains at the corresponding target position even though that position does not contain interference audio.
- `probe_0017`:
  same target segment,
  interference clip
  `friend_absent_820s`,
  note:
  severe full-span artifact on the target audio.

Across all three rows,
the ratings stay the same on both candidates:
target retention remains excellent,
interference leak stays only slight to moderate,
and artifact remains moderate to extreme.

## Interpretation

- This is the strongest listening evidence so far that the telephone-like or synthetic artifact is at least partly target-conditioned.
- The artifact persists while interference position changes,
  and one note explicitly says the corresponding location has no interference audio.
- Therefore the current
  `v240`
  versus
  `v249`
  comparison should not be treated as a clean leak-repair contest.
  Both routes are being judged through a target-linked artifact failure mode.

## Current Decision

- Do not continue using
  `v249`
  as if it were a near-real leak-repair candidate awaiting only more listening.
- Treat the split-route
  `refine_base`
  family as blocked by a target-conditioned artifact confound on this probe slice.
- Future work on this branch should either:
  build a target-artifact-specific synthetic or real probe and optimize against it,
  or move to a different writer family instead of continuing to retune
  `v240`
  versus
  `v249`.
