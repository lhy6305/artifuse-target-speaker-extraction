# 2026-03-26 `v81 vs v95` focused listening review

## Scope

- Pack:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v95_blind`
- Task:
  - determine whether `v95` converts its automatic suppression gains into audible improvement over current research base `v81`

## Decoded result

- Decoded summary:
  - `tie = 3`
  - `v81 = 1`
  - `v95 = 0`
- Decoded json:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v95_blind/listening_review_decoded_summary.json`

## Sample-level verdict

- `near_real_0003`
  - `tie`
  - both sides still have moderate residual leakage
- `near_real_0006`
  - `tie`
  - both sides still have moderate-to-heavy overlap leakage
- `near_real_0007`
  - `v81 > v95`
  - decisive reason:
    - `less_artifact`
  - decoded ratings:
    - `v81`
      - `artifact = moderate`
    - `v95`
      - `artifact = heavy`
- `near_real_0009`
  - `tie`
  - stronger automatic absent suppression in `v95` did not become an audible win

## Interpretation

- `v95` is not a silent near-equivalent to `v81`.
- The only audible difference is negative:
  - on `near_real_0007`, `v95` introduces clearly heavier artifact.
- The hoped-for gains on:
  - `near_real_0006`
  - `near_real_0009`
  remain below the audible threshold.

## Decision

- `v95` does not get promoted.
- `v81` remains the current research base.
- `overlap auxiliary interference decoder v2 / v3 / v4` does not yet solve the core pain point at the audible level.

Current project-level meaning:

- automatic suppression can still be improved,
- but the main overlap residual leak problem remains unresolved by ear,
- and the current auxiliary-only line has started to trade those gains for artifact on `0007`-style hard-present cases.
