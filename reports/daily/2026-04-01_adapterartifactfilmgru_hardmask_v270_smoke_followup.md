# 2026-04-01 adapter artifact `ref_film + temporal + hard mask` smoke follow-up

## Summary

- Experiment:
  `v270-smoke = v249 trunk init + adapter_mask_head + adapter ref_film + adapter temporal model + adapter artifact-local hard mask + artifact-subspan teacher anchor`
- Status:
  bounded smoke reject, but scientifically useful
- Decision:
  do not run full `v270`;
  do not continue the current adapter-branch artifact family as a simple full run or scalar retune

## Configuration

- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Smoke output checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v270smoke_v249_adapterartifactfilmgru_hardmask10_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable modules:
  `adapter_condition_scale`
  `adapter_condition_shift`
  `adapter_temporal_model`
  `adapter_mask_head`
- Key model settings:
  `enable_adapter_mask_head = true`
  `enable_adapter_artifact_local_hard_mask = true`
  `enable_adapter_temporal_model = true`
  `adapter_gru_layers = 1`
  `adapter_conditioning_mode = ref_film`
  `adapter_mask_max_delta = 0.1`
- Key loss settings:
  `reconstruction_extra_waveform_weight = 0.2`
  `reconstruction_extra_stft_weight = 0.1`
  `extra_local_teacher_waveform_extra_weight = 0.5`
  `branch_protect_teacher_overlap_weight = 0.04`
  `absent_extra_weight = 0.02`

## Training Reality Check

- Train start:
  `2026-04-01T21:54:42`
- Train end:
  `2026-04-01T21:54:57`
- Elapsed:
  `15.095 s`
- Trainable fraction:
  `1118977 / 3486594 = 0.320937`
- Selector coverage:
  `reconstruction_extra train 63 / 266, val 27 / 74`
  `overlap_dual_extra train 33 / 266, val 7 / 74`
- Final validation metrics:
  `val_extra_local_teacher_waveform_extra_l1 = 0.000226`
  `val_branch_protect_teacher_overlap_l1 = 0.003306`

Interpretation:

- The adapter branch remains clearly training-real.
- The new hard local mask materially changes the branch behavior.
- It improves the real-side read relative to `v269-smoke`, but still does not produce a safe continuation point.

## Smoke Readout

Relative to `v249`:

- Active real artifact probes:
  `near_real_interval_artifact_probe_v2 = +0.3988 dB`
  `near_real_interval_artifact_probe_v3_subspan = +0.5629 dB`
- Interval-aware leak probe:
  `near_real_interval_leak_probe_v1 = -0.0125 dB`
- Matched synthetic artifact-subspan asset:
  `val_manifest_hard_present_artifact_local_proxy_v2_subspan = -6.5835 dB`
- Fixed synthetic five-pack:
  `abstention = -8.0302 dB`
  `same_gender_keep = -2.4539 dB`
  `hard_present_keep = -2.1597 dB`
  `artifact = -2.9470 dB`
  `local_speech_leak_proxy_v1 = +0.4976 dB`

Relative to `v269-smoke`:

- The hard mask preserves most of the real artifact gain.
- The interval-aware leak probe improves materially
  (`-0.1445 -> -0.0125 dB`).
- But the matched synthetic artifact-subspan asset stays collapsed,
  and the fixed synthetic guardrails still collapse.

## Conclusion

- This branch confirms that the adapter family can retain most of its real artifact gain
  while largely repairing the leak probe.
- But the fixed synthetic guardrails still fail badly, and the matched synthetic artifact-subspan asset
  remains strongly negative.
- So the adapter family is still not a safe continuation point for a full run.
- The next useful change on this family must control synthetic guardrails explicitly inside the adapter branch,
  not merely localize the writeback window.

## Next Step

- Do not run full `v270`.
- Do not treat this as a simple `adapter_mask_max_delta` tuning problem.
- If work continues on this family, the next change should add an explicit guardrail route for the adapter branch,
  especially on abstention and keep behavior,
  rather than simply opening or localizing the same adapter branch further.
