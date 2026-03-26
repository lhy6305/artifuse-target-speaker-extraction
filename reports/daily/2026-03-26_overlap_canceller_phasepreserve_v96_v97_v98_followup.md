# 2026-03-26 overlap canceller `phase_preserve` follow-up: `v96 / v97 / v98`

## Scope

- Continue after `v93 / v94 / v95` and test whether the overlap canceller family can be made safer by preserving phase.
- Add a new `branch_overlap_cancel_ratio_mode = phase_preserve`.
- Check two questions:
  - whether a phase-preserving canceller avoids the `0007`-style artifact risk seen in stronger suppression families
  - whether that safer canceller still creates any meaningful behavior change relative to `v81`

## Code change

Files:

- `src/tse_prefix/models/stft_mask_baseline.py`
- `scripts/train/train_stft_mask_baseline.py`

Added:

- `branch_overlap_cancel_ratio_mode`
  - `complex`
  - `phase_preserve`

Meaning:

- `complex`
  - old behavior
  - predict a complex ratio delta
- `phase_preserve`
  - new behavior
  - only scale magnitude with a nonnegative real ratio
  - keep phase unchanged

Implementation note:

- The first `phase_preserve` version used a dead-zone-prone startup.
- It was corrected in the same round:
  - reset bias to `-8.0`
  - use `sigmoid(logits) * max_delta`
- This keeps the initial behavior close to zero while still leaving usable gradient.

## `v96`: auxiliary-only no-op probe

Checkpoint:

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v96_v81_overlap_aux_interference_decoder_v5_phasepreserve_ft1`

Setup:

- init: `v81`
- enabled:
  - `branch_overlap_cancel_head`
  - `branch_overlap_cancel_ratio_mode = phase_preserve`
  - `branch_overlap_cancel_apply_mode = auxiliary_only`
- trainable:
  - `branch_overlap_cancel_head`
  - and nothing that changes the final waveform path

Result:

- relative `v81`
  - abstention proxy: exact tie
  - same-gender keep: exact tie
  - hard-present keep: exact tie

Interpretation:

- This is not a real candidate.
- Under `auxiliary_only`, the overlap cancel estimate is supervised but does not alter the final output.
- If only the overlap-cancel head is trainable, the final waveform is structurally output-inactive.

Judgment:

- `v96` stops here as a mechanism probe.

## `v97`: gradient-fixed rerun, still structurally inactive

Checkpoint:

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v97_v81_overlap_aux_interference_decoder_v5_phasepreserve_fixgrad_ft1`

Setup:

- same as `v96`
- but after the `phase_preserve` gradient-startup fix

Result:

- relative `v81`
  - abstention proxy: exact tie
  - same-gender keep: exact tie
  - hard-present keep: exact tie

Interpretation:

- The startup fix was necessary for code correctness.
- But it does not change the more important structural fact:
  - `auxiliary_only + overlap_cancel_head-only` still cannot materially change the final output.

Judgment:

- `v97` also stops here as a no-op probe.

## `v98`: first valid phase-preserving subtractive pilot

Checkpoint:

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v98_v81_overlap_canceller_v3_phasepreserve_subtract_ft1`

Setup:

- init: `v81`
- model:
  - `enable_branch_overlap_cancel_head = true`
  - `branch_overlap_cancel_apply_mode = subtract`
  - `branch_overlap_cancel_gate_mode = complement`
  - `branch_overlap_cancel_source_mode = residual`
  - `branch_overlap_cancel_ratio_mode = phase_preserve`
  - `branch_overlap_cancel_max_delta = 0.08`
- trainable:
  - `branch_overlap_cancel_head`
- selectors:
  - same focused overlap-abstention / branch-protect family already used around `v95`

### Synthetic results relative to `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -0.0028`
  - `0 improve / 0 regress / 8 near tie`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0005`
  - `0 improve / 0 regress / 11 near tie`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0004`
  - `0 improve / 0 regress / 16 near tie`

Interpretation:

- `v98` is a near-exact synthetic tie with `v81`.
- It is safer than the more aggressive overlap-canceller family, but it also does not create a meaningful new behavior.

### Near-real tradeoff pack

Pack:

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v98_blind`

Tradeoff summary:

- `better_source_retention_label`
  - `tie = 3`
  - `not_applicable = 1`
- `more_interference_leaky_label`
  - `tie = 4`
- `more_residual_heavy_label`
  - `tie = 4`
- `better_retention_minus_leak_label`
  - `tie = 3`
  - `not_applicable = 1`

Bandwidth summary:

- `narrower_candidate_counts`
  - `tie = 4`

Sample-level reading:

- `near_real_0003`
  - tie
- `near_real_0006`
  - tie
- `near_real_0007`
  - tie
- `near_real_0009`
  - tie

Interpretation:

- `v98` is also a near-exact tie with `v81` on the current near-real residual leak floor pack.
- There is no meaningful suppression win, no meaningful keep-side rescue, and no new artifact signal.

Judgment:

- `v98` does not enter focused human listening.
- The `phase_preserve` path is now code-correct and available, but this concrete pilot is effectively a no-op relative to `v81`.

## Decision

- `v96`
  - not a valid output-moving candidate
- `v97`
  - not a valid output-moving candidate
- `v98`
  - valid candidate
  - but effectively tied with `v81` on synthetic, near-real tradeoff, and bandwidth

Current judgment:

- `v81` remains the research base.
- The new `phase_preserve` ratio mode is kept in code.
- But the `phase-preserving overlap canceller` branch does not look like a promising next frontier.

## What this round actually established

1. The earlier `v95`-style artifact risk is not solved just by preserving phase.
2. A phase-preserving subtractive overlap canceller can be made safe, but in the current representation it becomes almost behavior-inert.
3. The current bottleneck is therefore not just "the canceller ratio should be more conservative".
4. The next useful pivot should change representation or supervision semantics, not keep sweeping overlap-canceller ratio parameterization.

## Next step

Default next step is not:

- `v98` neighborhood sweep
- another `phase_preserve` overlap-canceller tuning round

Default next step should instead be:

- a new mechanism-level pivot that explicitly controls hard-present artifact risk,
- rather than another variant of the same multiplicative overlap-cancel head.
