# 2026-03-31 hardlocalmask v249 partial listening note

## Summary

- Status:
  partial human listening follow-up is now available for
  `v249`
  versus
  `v240`.
- Machine-readable export currently exists only for the focused
  `near_real_guodegang_transient_probe_v1`
  blind pack.
- The broader
  `near_real_speech_probe_v1`
  pack has not yet been exported back into
  `listening_results_summary.json`
  in the current workspace state,
  but a user verbal summary was provided across both packs.

## Completed Focused Pack

- Pack:
  `reports/eval/ab_listening_pack_near_real_guodegang_transient_probe_v1_refinebase_artifactteacher_v240_vs_hardlocalmask_v249_blind`
- GUI summary:
  `6 / 6` scored,
  with
  `tie = 3`
  and
  `uncertain = 3`.
- Decoded summary:
  all six samples were rated as heavy leak on both candidates,
  while target retention stayed good on both candidates where ratings were filled.
- So the completed focused listening pack does not provide audible evidence that
  `v249`
  truly fixes leak on the guodegang transient side.

## User Verbal Cross-Pack Read

- The user-reported cross-pack conclusion is:
  mixture gain ratio does not appear to materially change the output behavior.
- The same verbal conclusion also says:
  the whole listened group still leaks,
  while target retention remains extremely strong.

## Interpretation

- This is important because the automatic interval-aware probe metrics for
  `v249`
  were strongly positive relative to
  `v240`.
- The partial listening read suggests that those probe gains may be driven more by target retention and related tradeoff terms than by a real audible leak fix.
- The gain-sweep structure inside the probe packs also appears to have low perceptual diversity,
  which matches the user observation that changing the mixture ratio did not materially change the audible outcome.

## Current Decision

- Do not treat
  `v249`
  as listening-ready.
- Keep the existing interpretation:
  `v249`
  is still a real-side evidence point,
  but not a promotion candidate.
- For future listening or real-asset validation,
  prioritize diversity of leak phenotype over repeated gain variants of the same anchor bucket.
