# 2026-03-26 `v81 vs v101` focused listening review

## Scope

- Pack:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v101_blind`
- Task:
  - determine whether `v101` converts its stronger objective suppression and safer delta-blend behavior into an audible improvement over current research base `v81`

## Decoded result

- GUI summary:
  - `file_a = 1`
  - `file_b = 0`
  - `tie = 3`
- Blind key:
  - `candidate_a = v81`
  - `candidate_b = v101`
- Therefore decoded result:
  - `tie = 3`
  - `v81 = 1`
  - `v101 = 0`

Source:

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v101_blind/listening_review_decoded_summary.json`

## Sample-level verdict

- `near_real_0003`
  - `tie`
  - both sides still have moderate residual leakage
- `near_real_0006`
  - `tie`
  - both sides still have heavy overlap leakage
- `near_real_0007`
  - `tie`
  - `v101` no longer reproduces the earlier `v88`-style or `v95`-style audible loss on this hard-present sample
- `near_real_0009`
  - `v81 > v101`
  - decisive reason:
    - `less_interference_leak`
  - despite objective suppression favoring `v101`, the audible preference still resolves to `v81`

## Comparison against earlier `v88 / v100`

- `v88` listening result:
  - `tie = 2`
  - `v81 = 2`
  - `v88 = 0`
- `v100` listening result:
  - `tie = 3`
  - `v81 = 1`
  - `v100 = 0`
- `v101` listening result:
  - `tie = 3`
  - `v81 = 1`
  - `v101 = 0`

Interpretation:

- `v101` is meaningfully safer than `v88`
  - `near_real_0007` no longer loses audibly
- but it still does not cross the human threshold into a new audible win
- the only separating sample remains `near_real_0009`
  - and that separation still favors `v81`, not the newer candidate

## Interpretation

This round has mechanism-diagnosis value, but not promotion value.

What it proved:

- `delta blend v1` is not a no-op
  - it did move the subtractive canceller family off the harsher `v88` failure pattern
- it successfully pulled the family back from hard-present audible loss on `near_real_0007`
- but the core pain point remains unchanged:
  - `near_real_0003 / 0006` still have audible residual speech leakage
  - `near_real_0009` still does not convert stronger objective suppression into better human preference

What it did not prove:

- it did not create a better research base
- it did not solve overlap residual speech leak at the audible level
- it did not justify continuing `v101 / v102` style small sweeps in this family

## Decision

- `v101` does not get promoted.
- `v81` remains the current research base.
- `overlap cancel delta blend` closes as a useful safety-calibration branch, but not an audible frontier branch.

Project-level meaning:

- this round reduced uncertainty about the subtractive canceller family's failure mode,
- but it did not produce an audibly better checkpoint.
- current unresolved problem remains:
  - target-present overlap segments are still not separated cleanly enough.
