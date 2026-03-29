# 2026-03-30 handoff restore and `v192` launch plan

## Summary

- Restored context from the active docs, the initial design docs, and the `v190` / `v191` daily reports.
- Verified that there is no active leftover `python` training process in the workspace.
- Verified that the next blocker is not missing code:
  the repository already exposes
  `branch_overlap_dual_monitor_controller`
  in model outputs and already supports
  `gate_supervision_source = overlap_dual_monitor_controller`
  in the train and eval entrypoints.
- The most direct next step is therefore a command-only continuation run,
  not another round of model-plumbing edits.

## Restored Scientific State

- Active automatic base:
  `v157`
- Non-trivial no-write auxiliary evidence point:
  `v190`
- Safe monitor-coupling evidence point:
  `v191`
- Current blocker:
  the coupling path is real,
  but the local blocker
  `local_speech_leak_proxy_v1`
  stayed near exact tie
  (`+0.0008 dB` relative to `v157`)

## Code Reality Check

- `src/tse_prefix/models/stft_mask_baseline.py`
  already returns
  `branch_overlap_dual_monitor_controller`.
- `scripts/train/train_stft_mask_baseline.py`
  already accepts
  `--loss-gate-supervision-source overlap_dual_monitor_controller`
  in both train and validation.
- The active `overlap_dual` selector sample set can be preserved through a small id file,
  so the next branch does not need any new selector implementation either.

## Recommended Immediate Run

- Name:
  `v192`
- Parent:
  `v191`
- Goal:
  directly supervise the existing monitor head on absent and overlap intervals,
  instead of only letting it learn through the weak output-coupling side effect from `v191`
- Keep fixed from `v191`:
  - trainable module prefix:
    `branch_overlap_dual_monitor_controller_head`
  - `branch_overlap_dual_monitor_max_blend = 0.02`
  - `overlap_dual_residual_waveform_weight = 0.02`
  - selector scope:
    `overlap_dual` local blocker ids
- Change from `v191`:
  - `--init-checkpoint` -> `v191/best.pt`
  - `--output-dir` -> `...v192_v191_monitor_directgate_v1_ft1`
  - `--loss-gate-supervision-source overlap_dual_monitor_controller`

## Suggested Launch Skeleton

```powershell
.\python.exe scripts/train/train_stft_mask_baseline.py `
  --train-manifest data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl `
  --val-manifest data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl `
  --output-dir experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v192_v191_monitor_directgate_v1_ft1 `
  --init-checkpoint experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v191_v190_dualaux_monitorcouple_blend002_v1_ft1/best.pt `
  --disable-teacher-checkpoint-metadata-fallback `
  --epochs 4 `
  --batch-size 8 `
  --lr 0.00012 `
  --model-conditioning-mode legacy_bias `
  --model-enable-branch-decoder-head `
  --model-enable-branch-abstention-gate `
  --model-enable-branch-overlap-refine-head `
  --model-enable-branch-overlap-refine-present-head `
  --model-enable-branch-overlap-cancel-head `
  --model-enable-branch-overlap-cancel-apply-controller `
  --model-enable-branch-overlap-dual-decoder-head `
  --model-enable-branch-overlap-dual-monitor-controller `
  --model-branch-overlap-refine-source-mode mixture `
  --model-branch-overlap-cancel-source-mode residual `
  --model-branch-overlap-cancel-apply-mode subtract `
  --model-branch-overlap-cancel-ratio-mode complex `
  --model-branch-overlap-cancel-delta-blend-mode complement `
  --model-branch-overlap-cancel-max-blend 0.5 `
  --model-branch-overlap-dual-decoder-source-mode residual `
  --model-branch-overlap-dual-decoder-apply-mode current_output `
  --model-branch-overlap-dual-decoder-max-blend 0.0 `
  --model-branch-overlap-dual-monitor-max-blend 0.02 `
  --loss-stft-weight 0.5 `
  --loss-overlap-dual-residual-waveform-weight 0.02 `
  --loss-gate-absent-weight 1.0 `
  --loss-gate-keep-weight 2.0 `
  --loss-gate-supervision-source overlap_dual_monitor_controller `
  --loss-overlap-dual-focus-sample-ids-file data/manifests/selectors/overlap_dual_local_speech_leak_proxy_v1_ids.txt `
  --trainable-module-prefixes branch_overlap_dual_monitor_controller_head
```

## Why This Is The Best Next Cut

- It isolates the missing ingredient from `v191`:
  the monitor head itself was already writing,
  but it was not directly supervised on the blocker windows.
- It avoids another ambiguous branch where both coupling strength and supervision source change together.
- It reuses the proven no-write auxiliary residual predictor from `v190`
  and the already safe monitor coupling initialization from `v191`.

## If `v192` Still Stays Near Tie

- The next reasonable follow-up is not more code plumbing.
- The next reasonable follow-up is:
  - add `gate_target_mode audibility` on the same monitor path
  - or increase `monitor_max_blend`
  after first measuring whether direct monitor supervision alone moves the local blocker
