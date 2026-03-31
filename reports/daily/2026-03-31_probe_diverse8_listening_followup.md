# 2026-03-31 probe diverse8 listening followup

## Summary

- Goal:
  close the reduced
  `near_real_speech_probe_v1_diverse8`
  listening pass for
  `v240`
  versus
  `v249`.
- Result:
  the reduced listening pass does not show an audible win for
  `v249`.
  All eight samples were scored,
  but none preferred one candidate over the other.

## Listening Outcome

- Pack:
  `reports/eval/ab_listening_pack_near_real_speech_probe_v1_diverse8_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`
- GUI summary:
  `num_scored = 8`
  with
  `tie = 3`
  and
  `uncertain = 5`.
- Decoded result:
  no sample preferred
  `refinebase_artifactteacher_v240`
  or
  `hardlocalmask_v249`.
- Friend side:
  `3 uncertain + 3 tie`
- Guodegang side:
  `2 uncertain`

## Important Listening Notes

- The user listening notes reinforce the earlier cross-pack impression that gain variation inside the same probe bucket does not materially change the audible verdict.
- Multiple samples were rated as:
  strong or excellent target retention,
  but still moderate to heavy leak,
  often with moderate to heavy artifact.
- The most important new clue is that the same short telephone-like or synthetic artifact appeared at the same target-audio position across
  `probe_0011`
  and
  `probe_0014`,
  even though the second case changes the interference condition and one related case has silence at that position.
  That makes the artifact more plausibly target-conditioned or target-frequency-triggered,
  not a clean readout of interference leak alone.
- On the guodegang side,
  the decoded ratings remain leak-heavy on both candidates,
  and one note explicitly says the interference path shows very strong telephone or synth artifact while the target stays mostly clean.

## Interpretation

- The automatic probe metrics and interval-aware probe guardrails for
  `v249`
  are still real.
- But the reduced human listening pass suggests those gains are not translating into a reliable audible leak reduction.
- The current best interpretation is:
  `v249`
  changes the tradeoff surface in a measurable way,
  but the dominant audible effect is still "target kept very well while leak and artifact remain",
  not "leak audibly fixed".

## Current Decision

- Do not promote
  `v249`
  from these probe wins.
- Do not keep expanding listening on the same
  `v240`
  versus
  `v249`
  probe family by adding more gain variants.
- If this family is revisited,
  future real-side assets should prioritize:
  target diversity,
  leak phenotype diversity,
  and explicit separation between target-conditioned artifact and interference leak.
