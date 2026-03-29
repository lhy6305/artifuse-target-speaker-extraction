# 2026-03-29 dual auxiliary monitor coupling on `v190`: `v191` follow-up

## Summary

- Goal:
  attach a separate monitor controller head that reads the proven non-trivial
  no-write auxiliary residual predictor from `v190`
  and couples it back to output behavior via a small output gate reduction.
- `v191 = v190 + enable_branch_overlap_dual_monitor_controller + monitor_max_blend 0.02`
  is the first coupling attempt that stays fully positive on all five active fixed synthetic checks
  relative to `v157`.
- The monitor controller is genuinely writing to output:
  relative to `v190` (which was exact `0.0` on all five checks),
  `v191` shows small positive deltas on four of the five fixed guardrails
  and a near-tie on the local blocker.
- The local blocker (`local_speech_leak_proxy_v1`) moved only `+0.0008 dB`
  relative to `v157`,
  which is effectively a tie.
- The coupling is real but the local blocker effect is not yet present.

## Code

- No code changes were required.
- `enable_branch_overlap_dual_monitor_controller` and `branch_overlap_dual_monitor_max_blend`
  were already implemented in the model and training script.

## `v191 = v190 + monitor_controller_head + monitor_max_blend 0.02`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v191_v190_dualaux_monitorcouple_blend002_v1_ft1`
- Parent:
  `v190/best.pt`
- Trainable:
  `branch_overlap_dual_monitor_controller_head` only
  (`131585` params of `7957901` total, `1.65%`)
- Frozen:
  all other parameters including `branch_overlap_dual_decoder_temporal_model` and
  `branch_overlap_dual_decoder_head` from `v190`
- Monitor coupling:
  `branch_overlap_dual_monitor_max_blend = 0.02`
- Dual auxiliary objective kept active:
  `overlap_dual_residual_waveform_weight = 0.02`
  so `dual_encoded` stays non-trivial while monitor head trains on top
- Selector:
  `train 33 / 233, val 7 / 67`
  (exact match to `v190`)

## Training Evidence

- `val_overlap_dual_residual_waveform_l1 = 0.015926`
  (identical to `v190` final, confirming frozen dual decoder is preserved)
- `train_overlap_dual_residual_waveform_l1 = 0.029566`
- `val_overlap_dual_residual_target_projection_ratio = 0.004308`
- `best_val_loss = 0.025610`
- Elapsed: `36s`

## Fixed Checks relative `v157`

- abstention `+0.0486 dB` (1 improved, 0 regressed of 8)
- same-gender keep `+0.0162 dB` (0 improved, 0 regressed of 11)
- hard-present keep `+0.0467 dB` (2 improved, 0 regressed of 16)
- artifact proxy `+0.0278 dB` (0 improved, 0 regressed of 7)
- local speech leak proxy `+0.0008 dB` (0 improved, 0 regressed of 7)

## Fixed Checks relative `v190`

- All five checks moved from exact `0.0 dB` (v190 was non-writing)
  to small positive deltas.
- The monitor coupling is confirmed real:
  the output is no longer identical to `v157`.
- The local blocker delta is essentially zero:
  the monitor head is coupling auxiliary activity to the gate,
  but not yet in a way that reduces local speech leak.

## Verdict

- `v191` is a positive structural milestone:
  the first coupling attempt that does not break any fixed guardrail.
- It is not a promotion candidate:
  the local blocker shows no meaningful improvement.
- The coupling direction is correct for keep and abstention,
  but the monitor controller is not yet selective enough to target local blocker windows.

## Next Step

- The monitor head learned a general output-suppression signal,
  not a locally targeted one.
- Options going forward:
  - add a local-blocker-specific auxiliary loss on the monitor controller output
    so it is penalized when it fails to reduce output in local leak windows
  - increase `monitor_max_blend` to check whether stronger coupling
    starts to move the local blocker at the cost of keep margin
  - add a disjoint local objective directly on the monitor controller path
    using the proven selector coverage (`train 33 / 233, val 7 / 67`)
