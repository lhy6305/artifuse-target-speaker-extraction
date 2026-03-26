# 2026-03-26 Overlap Canceller V1/V2 And V87/V88 Follow-up

## Scope

- Continue the new subproblem `reference-conditioned overlap residual canceller v1`.
- Keep `v81` as the research base.
- First verify code wiring, then run the first two canceller-only pilots.

## Code Changes

### New mechanism

- Added an explicit branch-level overlap residual canceller head in `src/tse_prefix/models/stft_mask_baseline.py`.
- The canceller is reference-conditioned through the existing branch path and only changes the final estimate by subtracting a learned overlap residual estimate.
- Current active configuration for this line:
  - `branch_overlap_cancel_gate_mode = complement`
  - `branch_overlap_cancel_source_mode = residual`

### New losses

- Added `overlap_cancel_waveform_l1` in `src/tse_prefix/pipeline/baseline_train.py`.
- Added `overlap_cancel_target_projection_ratio` in `src/tse_prefix/pipeline/baseline_train.py`.
- The canceller is now supervised to:
  - match the overlap interference residual target
  - avoid projecting onto the target speaker inside overlap intervals

### Training / eval plumbing

- Added the new model args and loss args in `scripts/train/train_stft_mask_baseline.py`.
- Added the new selector family `overlap_cancel` in `scripts/train/train_stft_mask_baseline.py`.
- Unified `scripts/eval/eval_stft_mask_baseline.py` with the new overlap-cancel path so offline eval no longer lags train-time semantics.

## Pilot Results

### `v87`

Checkpoint:
- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v87_v81_overlap_canceller_v1_ft1`

Result:
- Synthetic comparisons vs `v81` were all positive.
- Near-real residual leak floor was also positive and safe.
- But direct `v86 vs v87` compare showed near-total collapse to the same behavior.

Key evidence:
- `compare_v86_vs_v87_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`: `avg_sisdr_delta_db = +0.0053`
- `compare_v86_vs_v87_on_same_gender_present_keep_guardrail_v1/summary.json`: `avg_sisdr_delta_db = +0.0017`
- `compare_v86_vs_v87_on_hard_present_gate_keep_guardrail_v1/summary.json`: `avg_sisdr_delta_db = +0.0011`

Interim judgment:
- `v87` is not a new frontier checkpoint.
- It behaves as an objective near-equivalent of `v86`.

### `v88`

Checkpoint:
- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v88_v87_overlap_canceller_v2_targetorth_ft1`

Result:
- `v88` is the first canceller variant that clearly moves beyond the `v86/v87` plateau.
- Synthetic all improved again.
- Near-real residual leak floor rank also moved to the top while keeping `0` present violations.

Key objective evidence:
- `compare_v87_vs_v88_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = +1.0108`
  - `7 improve / 0 regress / 1 near tie`
- `compare_v87_vs_v88_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +0.5571`
  - `8 improve / 0 regress / 3 near tie`
- `compare_v87_vs_v88_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +0.5978`
  - `14 improve / 0 regress / 2 near tie`

Key near-real evidence:
- `rank_residual_speech_leak_floor_v1_v54_v81_v86_v87_v88/summary.json`
  - `combined_rank`: `v88 > v87 > v86 > v81 > v54`
  - `guardrail_filtered_rank`: `v88 > v87 > v86 > v81 > v54`
  - `present_guardrail_violation_count = 0`

Sample-level direction:
- `near_real_0006`: `v88` is materially less leaky than `v81`
- `near_real_0007`: `v88` is also materially less leaky, but with some extra target attenuation
- `near_real_0003`: small gain only
- `near_real_0009`: absent suppression is stronger than `v81`

## Focused Listening Pack

Pack:
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v88_blind`

Automatic analysis already completed:
- `asset_audit_summary.json`: `all_mono = true`, `all_have_target = true`
- `bandwidth_analysis/summary.json`: `narrower_candidate_counts = tie: 4`
- `tradeoff_analysis/summary.json`:
  - source retention: `tie = 3`, `not_applicable = 1`
  - more interference leaky: `v81 = 3`, `tie = 1`
  - better retention-minus-leak: `v88 = 2`, `tie = 1`, `not_applicable = 1`

Interpretation:
- The current automatic prior is favorable to `v88`.
- The main remaining question is whether those gains become audible without introducing a new subjective downside.

## Current Decision

- `v87` stops here as a non-frontier near-equivalent of `v86`.
- `v88` is promoted to the next focused human-listening gate.
- Do not start `v89+` before human listening resolves `v81 vs v88`.

## Next Step

Run GUI listening on:

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v88_blind
```

Listening focus:
- `near_real_0006`: overlap leak under external guodegang speech
- `near_real_0007`: whether lower leak comes with worse target preservation
- `near_real_0009`: whether stronger absent suppression is actually preferable by ear

