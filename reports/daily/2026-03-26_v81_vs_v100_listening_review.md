# 2026-03-26 `v81 vs v100` focused listening review

## Scope

- Pack:
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100_blind`
- Task:
  - determine whether `v100` converts its stronger objective suppression and teacher-veto regularization into audible improvement over current research base `v81`

## Decoded result

- GUI summary:
  - `file_a = 1`
  - `file_b = 0`
  - `tie = 3`
- Blind key:
  - `candidate_a = v81`
  - `candidate_b = v100`
- Therefore decoded result:
  - `tie = 3`
  - `v81 = 1`
  - `v100 = 0`

## Sample-level verdict

- `near_real_0003`
  - `tie`
  - both sides still have moderate residual leakage
- `near_real_0006`
  - `tie`
  - both sides still have moderate overlap leakage
- `near_real_0007`
  - `v81 > v100`
  - decisive reason:
    - `less_artifact`
  - decoded ratings:
    - `v81`
      - `artifact = slight`
    - `v100`
      - `artifact = moderate`
- `near_real_0009`
  - `tie`
  - stronger objective absent suppression in `v100` still did not become an audible win

## Comparison against `v95`

- `v95` listening result:
  - `tie = 3`
  - `v81 = 1`
  - `v95 = 0`
- `v100` listening result:
  - `tie = 3`
  - `v81 = 1`
  - `v100 = 0`

The audible pattern is effectively unchanged.

The only meaningful difference is:

- on `near_real_0007`,
  - `v95` had heavier artifact than `v81`
  - `v100` reduces that artifact severity somewhat,
  - but not enough to remove the audible loss

So `teacher artifact veto` was not useless, but it was insufficient:

- it softened the known failure,
- but did not create a new audible frontier candidate.

## Interpretation

This round has diagnostic value, but not promotion value.

What it did prove:

- the previous `v95` failure was not just random listening noise;
- `hard-present artifact risk` on `0007` is the real blocking constraint for this family;
- frozen-teacher overlap veto can make that failure milder, but not audibly solve it;
- the objective gain in `0003 / 0006 / 0009` still sits below the human-audible threshold.

What it did **not** prove:

- it did not produce a better research base;
- it did not solve the core pain point;
- it did not justify continuing `v95 / v100` style small sweeps.

## Decision

- `v100` does not get promoted.
- `v81` remains the current research base.
- `v99 / v100` close the current `teacher artifact veto` branch at the objective-diagnostic level.

Project-level meaning:

- this round was useful as a falsification step and mechanism diagnosis,
- but not as a model-quality advance.
- If the bar is “produce an audibly better checkpoint”, then this round failed.
- If the bar is “reduce uncertainty about whether teacher-veto can rescue the `v95` family”, then this round succeeded and the answer is:
  - not enough.
