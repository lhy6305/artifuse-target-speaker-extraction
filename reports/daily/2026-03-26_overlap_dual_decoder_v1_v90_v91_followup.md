# overlap dual decoder v1 `v90 / v91` follow-up

## Summary

- New mechanism class tested:
  - `overlap dual decoder v1`
- New checkpoints:
  - `v90 = v81 + overlap dual decoder v1`
  - `v91 = v81 + overlap dual decoder v1 + blend cap 0.25`
- Final verdict:
  - both fail before listening
  - this mechanism should not continue as a direct final-output path

## Mechanism

Unlike the old overlap canceller family, this line did not simply subtract a learned residual delta from `branch_base`.

Instead it added a new explicit path:

- estimate overlap interference from a dedicated dual decoder head
- form a dual target candidate as:
  - `mixture - interference_estimate`
- blend that candidate back toward `branch_base` only inside the gate-selected subdomain

So this was a genuine mechanism change, not just another regularizer on the old canceller head.

## `v90`

### Setup

- init:
  - `v81`
- trainable:
  - `branch_overlap_dual_decoder_temporal_model`
  - `branch_overlap_dual_decoder_head`
- key config:
  - `source_mode = residual`
  - `gate_mode = complement`
  - `max_blend = 1.0`

### Result

`v90` failed immediately and globally.

Relative to `v81`:

- `overlap_abstention_proxy_v4_audibility_v1`
  - `-6.8556 dB`
  - `1 improve / 7 regress`
- `same_gender_present_keep_guardrail_v1`
  - `-4.7200 dB`
  - `1 improve / 10 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `-11.6327 dB`
  - `0 improve / 16 regress`

Near-real rank:

- `v88 > v81 > v54 > v90`

The sample-level failure mode was also clear:

- `near_real_0003`
  - `retention_minus_leak_db = -1.412`
- `near_real_0006`
  - `4.616`
- `near_real_0007`
  - `0.675`
- `near_real_0009`
  - `interference_capture_db = -5.077`

This is not a subtle regression. It means the dual path was over-replacing `branch_base`, causing very loud residual leak and collapse of the keep-vs-leak tradeoff.

## `v91`

### Setup

Only one structural change was made relative to `v90`:

- `branch_overlap_dual_decoder_max_blend = 0.25`

The intent was to keep the explicit interference-decoding path, but limit how much it could pull the final target away from `branch_base`.

### Result

`v91` is much less explosive than `v90`, but still clearly fails.

Relative to `v81`:

- `overlap_abstention_proxy_v4_audibility_v1`
  - `-5.1942 dB`
  - `1 improve / 7 regress`
- `same_gender_present_keep_guardrail_v1`
  - `-5.2723 dB`
  - `0 improve / 10 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `-5.0749 dB`
  - `1 improve / 15 regress`

Near-real rank:

- `v88 > v81 > v54 > v91`

So the blend cap helps numerical stability, but not enough to recover useful behavior.

## Interpretation

The important conclusion is not just that `v90 / v91` failed.

It is *how* they failed:

- explicit interference decomposition may be learnable
- but letting that path directly own the final target waveform is too dangerous
- even with a strong blend cap, the dual path still drags the output away from the safer `branch_base` regime

So the current problem is not "dual-source decomposition is a wrong idea".

The problem is:

- `direct dual-target replacement` is the wrong integration point

## Decision

Do not continue with:

- `v90` listening
- `v91` listening
- `v92+` direct-output dual decoder sweeps around the same structure

## Next default

If this direction continues, the next subproblem should be:

- `overlap interference auxiliary decoder v1`

Meaning:

- keep explicit interference estimation
- but use it only as an auxiliary training branch / regularizer
- do **not** let it directly take over the final target output path

This is the key lesson from `v90 / v91`.
