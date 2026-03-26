# 2026-03-26 V81 Vs V88 Listening Review

## Scope

- Decode GUI listening results for:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v88_blind`
- Decide whether `v88` should replace `v81` as the active research base.

## Decoded Result

Decoded summary:
- `tie = 2`
- `v81 = 2`
- `v88 = 0`

Source:
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v88_blind/listening_review_decoded_summary.json`

Per-sample result:
- `near_real_0003`
  - `tie`
- `near_real_0006`
  - `tie`
- `near_real_0007`
  - `v81 > v88`
- `near_real_0009`
  - `v81 > v88`

## Human Interpretation

The audible difference is limited to interference suppression only, and even that difference is subtle.

But the two samples that did separate do **not** favor `v88`.

- `near_real_0007`
  - GUI choice decoded to `v81`
  - tag: `less_interference_leak`
- `near_real_0009`
  - GUI choice decoded to `v81`
  - tag: `less_interference_leak`

This means:

- `v88` still did not create a broader perceptual change in source retention, artifacts, or overall usability.
- The only marginally audible axis remained interference suppression.
- On that axis, the user still preferred `v81` on the two samples that separated.

## Objective / Human Divergence

Automatic prior before listening was favorable to `v88`:

- tradeoff:
  - `more_interference_leaky = v81` on `3 / 4`
  - `better_retention_minus_leak = v88` on `2 / 4`
- bandwidth:
  - no clear yellow flag
- near-real rank:
  - `v88` was the top guardrail-safe candidate in this local family

But human listening still resolved as:

- `v81 >= v88`
- and on the only audible axis, the decoded winner was `v81`, not `v88`

So this line repeats the same pattern already seen in `v85 / v86`:

- objective and near-real guardrails improve
- but the improvement still does not convert into a reliable audible win

## Decision

- `v88` does **not** upgrade to the active research base.
- `v81` remains the current research base.
- `v87 / v88` confirm that the overlap canceller mechanism is real and trainable.
- But this `overlap canceller v1/v2` family still does not solve the main audible pain point:
  - overlap segments remain not clean enough
  - residual speech leak is still present

## Updated Status

- default usable line:
  - `legacy stage2`
- current research base:
  - `v81`
- closed selection problems:
  - `v81 vs v85`
  - `v81 vs v86`
  - `v81 vs v88`

## Conclusion

`v88` is the strongest automatic canceller variant so far, but it still fails the real decision criterion.

The current project state remains:

- no replacement for `legacy stage2`
- no audible promotion over `v81`
- core pain point still unresolved:
  - target-present overlap residual speech leak

