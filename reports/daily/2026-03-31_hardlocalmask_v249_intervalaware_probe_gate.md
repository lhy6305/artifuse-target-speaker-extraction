# 2026-03-31 hardlocalmask v249 interval-aware probe gate

## Summary

- Goal:
  formalize the interval-aware probe read on top of
  `v249`
  instead of leaving it only as a narrative conclusion.
- Method:
  use
  `gate_probe_subset_guardrail.py`
  against shared-baseline probe summaries,
  with
  `v240`
  as the reference candidate and
  `v249`
  as the new candidate.
- Result:
  `v249`
  passes both the broad speech-probe guardrail and the focused guodegang transient guardrail relative to
  `v240`.

## Broad Speech Probe Guardrail

- Output:
  `reports/eval/compare_stage2_vs_hardlocalmask_v249_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v240.json`
- Overall:
  `pass`
- Rules included:
  overall,
  `friend_raw`,
  `guodegang_raw`,
  anchors
  `near_real_0003 / 0004 / 0006`,
  and clips
  `friend_absent_820s`
  plus
  `guodegang_anchor_120s`.
- Key margins over
  `v240`:
  overall `+0.7692 dB`,
  `friend_raw +0.9288 dB`,
  `guodegang_raw +0.2902 dB`,
  `near_real_0003 +0.9038 dB`,
  `near_real_0004 +0.9538 dB`,
  `near_real_0006 +0.2902 dB`,
  `friend_absent_820s +0.8891 dB`,
  `guodegang_anchor_120s +0.2884 dB`.

## Guodegang Transient Guardrail

- Output:
  `reports/eval/compare_stage2_vs_hardlocalmask_v249_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v240.json`
- Overall:
  `pass`
- Rules included:
  overall,
  `guodegang_raw`,
  anchor
  `near_real_0006`,
  and clips
  `guodegang_absent_480s`
  plus
  `guodegang_anchor_120s`.
- Key margins over
  `v240`:
  overall `+0.0764 dB`,
  `guodegang_raw +0.2902 dB`,
  `near_real_0006 +0.2902 dB`,
  `guodegang_absent_480s +0.2921 dB`,
  `guodegang_anchor_120s +0.2884 dB`.

## Interpretation

- This does not overturn the synthetic fixed-proxy failure of
  `v249`.
- It does make the real-side read more defensible:
  the route is no longer just "probe-positive on average";
  it also clears focused interval-aware probe guardrails relative to the best earlier mixed candidate,
  `v240`.
- So the current state is now:
  `v249`
  is a synthetic-negative but interval-aware probe-guardrail-positive continuation.

## Current Decision

- Keep
  `v157`
  as the active automatic base.
- Keep
  `v240`
  as the leading mixed candidate inside the split-route
  `refine_base`
  family.
- Keep
  `v249`
  as the leading interval-aware real-side evidence point on that family.
- Do not treat these new probe-pass results as a promotion trigger by themselves.
  They justify targeted listening and future interval-aware real assets,
  not a replacement for the fixed synthetic guardrails.
