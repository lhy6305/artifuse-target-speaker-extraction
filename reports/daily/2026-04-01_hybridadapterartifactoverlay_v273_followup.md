# 2026-04-01 hybrid adapter artifact overlay `v273` follow-up

## Summary

- Experiment:
  `v273-smoke = v249 trunk route + adapter artifact overlay on branch output + artifact-subspan teacher anchor`
  and
  `v273 = full replay of the same route`
- Status:
  `v273` is a new active frontier mixed candidate
- Decision:
  do not promote `v273`,
  do not reopen the `v269` to `v272` semantic or scalar retune axes,
  and do not read the current blocker as fixed synthetic guardrail control anymore;
  the remaining blocker on this adapter family is the still-negative matched synthetic artifact-subspan asset

## Configuration

- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Full output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v273_v249_hybridadapterartifactoverlay_v1_ft1/best.pt`
- Smoke output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v273smoke_v249_hybridadapterartifactoverlay_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable modules:
  `adapter_condition_scale`
  `adapter_condition_shift`
  `adapter_temporal_model`
  `adapter_mask_head`
- Key model settings:
  `enable_branch_decoder_head = true`
  `enable_adapter_mask_head = true`
  `enable_adapter_temporal_model = true`
  `adapter_conditioning_mode = ref_film`
  `adapter_mask_max_delta = 0.1`
  `enable_adapter_artifact_overlay_on_branch_output = true`
- Key loss settings:
  `extra_prediction_source = estimated_waveform_post_pre_present_controller`
  `local_prediction_source = estimated_waveform_post_adapter_artifact_overlay`
  `extra_local_teacher_waveform_extra_weight = 0.5`
  `reconstruction_extra_waveform_weight = 0.2`
  `reconstruction_extra_stft_weight = 0.1`
  `branch_protect_teacher_overlap_weight = 0.04`
  `absent_extra_weight = 0.02`
  `gate_absent_weight = 1.0`
  `gate_keep_weight = 2.0`

## Training Reality Check

- Smoke train start:
  `2026-04-01T22:32:05`
- Smoke train end:
  `2026-04-01T22:32:48`
- Smoke elapsed:
  `42.610 s`
- Full train start:
  `2026-04-01T22:35:00`
- Full train end:
  `2026-04-01T22:38:45`
- Full elapsed:
  `225.478 s`
- Trainable fraction:
  `1118977 / 9471889 = 0.118137`
- Selector coverage:
  `overlap_dual train 66 / 266, val 14 / 74`
  `overlap_dual_extra train 33 / 266, val 7 / 74`
  `absent_extra train 95 / 266, val 24 / 74`
  `branch_protect_teacher train 120 / 266, val 27 / 74`
- Final validation metrics:
  `val_extra_local_teacher_waveform_extra_l1 = 0.000226`
  `val_artifact_local_split_teacher_waveform_extra_l1 = 0.000116`
  `val_loss = 0.2976`

Interpretation:

- The new hybrid route is clearly training-real.
- Unlike `v269-smoke` and `v270-smoke`, the branch is no longer paying for its real artifact gains with a fixed synthetic guardrail collapse.
- The remaining blocker is not route activation, not leak control, and not the old keep or abstention scalar path.

## Full Readout

Relative to `v249`:

- Fixed synthetic five-pack:
  `abstention = 0.0 dB`
  `same_gender_keep = 0.0 dB`
  `hard_present_keep = 0.0 dB`
  `artifact = 0.0 dB`
  `local_speech_leak_proxy_v1 = 0.0 dB`
- Interval-aware leak probe:
  `near_real_interval_leak_probe_v1 = 0.0 dB`
- Active real artifact probes:
  `near_real_interval_artifact_probe_v2 = +0.3936 dB`
  `near_real_interval_artifact_probe_v3_subspan = +0.5627 dB`
- Matched synthetic artifact-subspan asset:
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan = -6.5760 dB`
  `1 improved / 6 regressed`

Relative to `v270-smoke`:

- The hybrid overlay preserves almost all of the real artifact gain.
- The interval-aware leak probe is repaired from
  `-0.0125 dB`
  to exact tie.
- The fixed synthetic five-pack is repaired from
  `-8.0302 / -2.4539 / -2.1597 / -2.9470 / +0.4976 dB`
  to exact tie.
- The matched synthetic artifact-subspan asset remains strongly negative.

## Conclusion

- `v273` is the first adapter-family point that keeps the fixed synthetic five-pack
  and the interval-aware leak probe exact tie to
  `v249`
  while still retaining clearly positive real artifact deltas.
- This moves the blocker diagnosis again:
  the frontier is no longer missing explicit guardrail control on fixed synthetic or leak behavior.
- The remaining blocker is that the currently matched synthetic artifact-subspan asset
  still reads strongly negative even while the real artifact probes stay strongly positive.
- So `v273` is an active frontier mixed candidate,
  not a promotion point and not a bounded reject.

## Next Step

- Do not reopen the `v269` to `v272` axes through more fallback semantics,
  more hard-mask micro-tuning,
  or larger keep or abstention scalars.
- If this adapter family continues,
  the next useful step should validate the real-side gain directly through focused listening
  and treat the remaining blocker as artifact-asset mismatch,
  not as another fixed-synthetic guardrail-control problem.
- A focused blind A/B pack for the tighter real artifact slice is already exported at
  `reports/eval/ab_inference_near_real_interval_artifact_probe_v3_subspan_hardlocalmask_v249_vs_hybridadapterartifactoverlay_v273_blind`.
