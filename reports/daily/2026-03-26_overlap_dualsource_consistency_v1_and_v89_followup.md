# overlap dual-source consistency v1 and `v89` follow-up

## Summary

- New subproblem:
  - `overlap dual-source consistency v1`
- New checkpoint:
  - `v89 = v81 + overlap_dual_source_consistency_v1`
- Final verdict:
  - `v89` does not beat `v88`
  - no focused listening pack is exported
  - `v81` remains the active research base
  - `v88` remains the automatic frontier of the current overlap-canceller family, but it has already been rejected by human listening

## What changed

This round tested whether the current overlap canceller could be pushed from a "single-sided suppression head" toward a more explicit overlap decomposition behavior, without increasing model topology again.

The new mechanism was added as two focused losses on the existing overlap-cancel branch:

- `overlap_dual_mix_consistency_l1`
  - enforce `target_est + residual_est ~= mixture` inside target-overlap intervals
- `overlap_dual_residual_target_projection_ratio`
  - penalize target projection remaining inside the residual branch

The selector family was narrowed to:

- `target_full`
- speech interference pools only
- `target_energy_ratio in [0.05, 0.22]`
- `overlap_ratio >= 0.6`
- low target transient share

Implementation landed in:

- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

Bring-up also exposed two real wiring issues before the final run:

- training loop initially missed `overlap_dual_sample_weights`
- overlap-dual residual term initially used unaligned waveform lengths

Both were fixed before the final `v89` run completed.

## Training target

- init:
  - `v81`
- trainable prefixes:
  - `branch_overlap_cancel_head`
- checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v89_v81_overlap_dualsource_consistency_v1_ft1`

## Objective results

### Relative to `v81`

`v89` is clearly better than `v81` on the current synthetic slices:

- `overlap_dualsource_proxy_v1`
  - `+3.6070 dB`
  - `8 improve / 0 regress / 0 near tie`
- `same_gender_present_keep_guardrail_v1`
  - `+1.6128 dB`
  - `8 improve / 0 regress / 3 near tie`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.7024 dB`
  - `15 improve / 0 regress / 1 near tie`

So this is not a dead direction. The added consistency losses do create measurable behavior.

### Relative to `v88`

But `v89` does not cross the current automatic frontier:

- `overlap_dualsource_proxy_v1`
  - `-1.0070 dB`
  - `0 improve / 7 regress / 1 near tie`
- `same_gender_present_keep_guardrail_v1`
  - `-0.5562 dB`
  - `0 improve / 8 regress / 3 near tie`
- `hard_present_gate_keep_guardrail_v1`
  - `-0.5994 dB`
  - `0 improve / 14 regress / 2 near tie`

This means the current `dual-source consistency v1` instantiation did not surpass the already-known `v88` plateau.

## Near-real rank

Near-real ranking on `real_eval_manifest_residual_speech_leak_floor_v1` is:

- `combined_rank`
  - `v88 > v89 > v81 > v54`
- `guardrail_filtered_rank`
  - `v88 > v89 > v81 > v54`

So `v89` is still safe, but it is only an in-between checkpoint.

## Sample-level read

### `near_real_0003`

- `v81`
  - `retention_minus_leak_db = 13.064`
- `v89`
  - `13.419`
- `v88`
  - `13.579`

`v89` improves over `v81`, but still trails `v88`.

### `near_real_0006`

- `v81`
  - `interference_capture_db = -31.249`
- `v89`
  - `-35.713`
- `v88`
  - `-39.287`

Again `v89` moves in the correct direction, but not far enough to beat `v88`.

### `near_real_0007`

- `v81`
  - `target_capture_db = -17.715`
  - `interference_capture_db = -47.206`
- `v89`
  - `-17.954`
  - `-55.318`
- `v88`
  - `-18.079`
  - `-67.534`

`v89` looks like a softened version of `v88`:

- still stronger than `v81` on leak suppression
- slightly less aggressive than `v88`
- but not enough to produce a clearly new tradeoff regime

### `near_real_0009`

- `v81`
  - `interference_capture_db = -34.050`
- `v89`
  - `-39.105`
- `v88`
  - `-40.486`

Absent suppression also lands strictly between `v81` and `v88`.

## Decision

- `v89` is not exported to focused listening
- `v89` does not replace `v81`
- `v89` does not replace `v88` as the current automatic frontier of this family

Reason:

- if a checkpoint is automatically weaker than `v88`, and `v88` has already failed human listening against `v81`, there is no decision value in adding a new `v81 vs v89` pack

## Updated interpretation

`overlap dual-source consistency v1` is not wrong, but in its current form it behaves like a regularizer on the existing canceller head, not like a genuinely stronger decomposition mechanism.

What it achieved:

- better than `v81`
- still guardrail-safe

What it failed to achieve:

- surpass `v88`
- create a new audible frontier

## Next default

Do not continue with:

- `v89` listening
- `v90`-style same-family weight sweeps around the current `v89` setup

If the project continues from here, the next subproblem should no longer be "more consistency losses on the same canceller head", but a new mechanism class with more explicit overlap dual-source decomposition capacity.
