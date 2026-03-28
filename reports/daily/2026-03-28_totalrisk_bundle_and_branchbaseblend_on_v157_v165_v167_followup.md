# 2026-03-28 total-risk bundle and `branch_base_blend` on `v157`: `v165 / v166 / v167` follow-up

## Summary

- Goal:
  after `v164`, first verify whether a truly broader
  `present-total`
  local asset can move the
  `v157 + no-teacher refine_base`
  route, then try one genuinely new output apply path on top of
  `v157`.
- Main conclusion:
  both directions are closed.
  - `v165`
    proves that even after materializing a real broader
    `hardlocal_totalrisk`
    asset, the
    `v157 + no-teacher refine_base`
    sibling is still exact no-op.
  - `v166 / v167`
    prove that
    `branch_base_blend`
    is not no-op, but it is the wrong kind of movement:
    it improves the targeted
    `local_speech_leak_proxy_v1`
    while systematically blowing up all four fixed guardrails.
- Active base remains:
  `v157`.

## New Training Support

- Code landed in:
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `scripts/train/train_stft_mask_baseline.py`
- Added new apply mode:
  `branch_overlap_cancel_apply_mode = branch_base_blend`
- Semantics:
  instead of scaling the direct subtract on the current output,
  the controller blends the current refined output toward a
  `branch_base - cancel`
  bounded candidate.
- `py_compile` passed after the code change.

## New Asset Boundary

- Train:
  `data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_totalrisk_bundle_v1.jsonl`
- Val:
  `data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_totalrisk_bundle_v1.jsonl`
- This bundle is the first one that actually combines:
  - the existing hardlocal family
  - the full
    `hard_present_artifact_local_proxy_v1`
    local windows
- Effective selector coverage for
  `sample_ids_hard_present_artifact_local_proxy_v1_all.txt`:
  - train `33 / 129`
  - val `7 / 41`

## `v165 = v157 + no-teacher refine-base hardlocal total-risk bundle`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v165_v157_refinebase_hardlocaltotalrisk_noteacher_v1_ft1`
- Setup:
  - init = `v157`
  - teacher metadata fallback disabled
  - trainable prefixes:
    `branch_overlap_refine_head`
  - overlap loss:
    `overlap_interference_weight = 0.04`
  - mode:
    `residual_projection_ratio`
  - focus selector:
    `sample_ids_hard_present_artifact_local_proxy_v1_all.txt`
  - train / val assets:
    `hardlocal_totalrisk_bundle_v1`

### Training Signal

- This run is not blocked by selector sparsity anymore:
  - train `33 / 129`
  - val `7 / 41`
- Training-side
  `overlap_interference_projection_ratio`
  stayed non-zero across all epochs.

### Fixed Checks relative `v157`

- abstention `+0.0000 dB`
- same-gender keep `+0.0000 dB`
- hard-present keep `+0.0000 dB`
- artifact proxy `+0.0000 dB`
- local speech leak proxy `+0.0000 dB`

### Verdict

- `v165`
  proves that the problem is no longer “asset too narrow”.
- Even with a real broader
  `present-total`
  local asset, the
  `v157 + no-teacher refine_base`
  sibling still cannot move output.
- Direct reject.

## `v166 = v157 + branch_base_blend apply path`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v166_v157_applycontroller_intervalveto_branchbaseblend_v1_ft1`
- Setup:
  identical to
  `v157`,
  except:
  - `branch_overlap_cancel_apply_mode = branch_base_blend`
  - trainable prefixes still only:
    `branch_overlap_cancel_apply_controller_head`

### Training Signal

- The important implementation fact is:
  controller training never actually engaged.
- Evidence:
  - train / val
    `gate_absent_mean = 0.0`
  - train / val
    `gate_keep_mean = 0.0`
  - all four controller head tensors are bitwise identical to
    `v157`
- So this run should be interpreted as:
  primarily an inference-path rewrite on top of
  `v157`,
  not a genuinely re-trained controller continuation.

### Fixed Checks relative `v157`

- abstention `-2.8127 dB`
- same-gender keep `-2.2610 dB`
- hard-present keep `-1.8606 dB`
- artifact proxy `-1.7204 dB`

### Targeted Local Proxy Check

- `local_speech_leak_proxy_v1`
  relative `v157`:
  `+0.6618 dB`

### Verdict

- `v166`
  is not no-op.
- But it is a strong global reject:
  every fixed guardrail regresses,
  even though the targeted local proxy improves.
- This means
  `branch_base_blend`
  is the wrong writeback semantics for this family.

## `v167 = v157 + branch_base_blend max_blend 0.1`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v167_v157_applycontroller_intervalveto_branchbaseblend_maxblend01_v1_ft1`
- Setup:
  same as
  `v166`,
  except:
  - `branch_overlap_cancel_max_blend = 0.1`

### Training Signal

- Same structural outcome as
  `v166`:
  - train / val
    `gate_absent_mean = 0.0`
  - train / val
    `gate_keep_mean = 0.0`
  - controller head tensors remain bitwise identical to
    `v157`

### Fixed Checks relative `v157`

- abstention `-3.1254 dB`
- same-gender keep `-2.3924 dB`
- hard-present keep `-1.9762 dB`
- artifact proxy `-1.8001 dB`

### Targeted Local Proxy Check

- `local_speech_leak_proxy_v1`
  relative `v157`:
  `+0.7356 dB`

### Verdict

- Lowering
  `max_blend`
  does not rescue this path.
- `v167`
  is even more negative on the fixed guardrails than
  `v166`,
  while still behaving like an inference-only rewrite.

## Final Verdict

- `v165`
  closes the “broader present-total local asset will unlock
  `v157 + no-teacher refine_base`”
  hypothesis.
- `v166 / v167`
  close the
  `branch_base_blend`
  output-path hypothesis.
- Do not continue:
  - `hardlocal_totalrisk_bundle_v1`
    as a
    `v157 + no-teacher refine_base`
    rescue attempt
  - `branch_base_blend`
  - `branch_base_blend + max_blend` sweep

## Next Step

- Keep
  `v157`
  as the active base.
- Do not give listening commands yet.
- If continuing, the next mechanism should be:
  - a non-`branch_base` output apply path
  - or a route that keeps controller supervision truly live instead of collapsing into pure inference rewrite
  - but not another
    `branch_base_blend`
    calibration run
