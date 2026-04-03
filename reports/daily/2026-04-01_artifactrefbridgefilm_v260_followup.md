# 2026-04-01 reference-conditioned artifact-side bridge on top of `v249`: `v260` follow-up

## Summary

- Goal:
  test whether the blocker after
  `v258`
  and
  `v259`
  was mainly the missing target-conditioning mechanism,
  rather than the artifact-side bridge writer family itself.
- Route:
  keep the same
  `v249`
  parent,
  keep the same synthetic artifact-subspan bundle and the same artifact-side bridge writeback path,
  but make the bridge explicitly reference-conditioned through
  `ref_film`
  before the artifact bridge ratio and controller heads.
- Smoke:
  passed.
  The new conditioning layers loaded cleanly from
  `v249`
  with optional-key init,
  and the bridge loss stayed non-zero.
  Quick artifact-probe reads were practical tie rather than immediately negative,
  so the point was worth a full run.
- Full:
  the new reference-conditioned bridge is still training-real and stays strongly positive on the matched synthetic artifact-subspan asset,
  but both active real artifact probes still regress relative to
  `v249`.
  Fixed synthetic five-pack checks and the interval-aware leak probe stay exact tie,
  so those remain activation-dormant checks for this family.
- Verdict:
  close this first explicit target-conditioned continuation on the dedicated artifact-side bridge family.
  Once the same bridge stays negative on the active real artifact probes even after explicit reference conditioning,
  the next blocker is better read as a writer-family mismatch than as a missing conditioning mechanism.

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add
  `branch_overlap_artifact_local_bridge_conditioning_mode`
  with
  `none / ref_bias / ref_film`,
  build optional artifact-bridge conditioning layers,
  zero-init them for identity-safe continuation from old checkpoints,
  and apply the conditioned features before the artifact bridge ratio and controller heads.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose
  `--model-branch-overlap-artifact-local-bridge-conditioning-mode`,
  store it in the checkpoint model config,
  and allow the new conditioning layers as optional init-checkpoint mismatches.
- Validation:
  `py_compile`
  passed after the code change.

## `v260 = v249 + reference-conditioned artifact-side bridge`

- Smoke checkpoint:
  `experiments/checkpoints/_smoke_v260_v249_artifactrefbridgefilm05_v1`
- Full checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v260_v249_artifactrefbridgefilm05_v1_ft1`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Teacher checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v157_v156_applycontroller_intervalveto_unionbundle_absent1p0_v1_ft1/best.pt`
- Trainable:
  `branch_overlap_artifact_local_bridge_condition_scale + branch_overlap_artifact_local_bridge_condition_shift + branch_overlap_artifact_local_bridge_head + branch_overlap_artifact_local_bridge_controller_head`
  (`527107 / 8880019`,
  `5.9359%`)
- Training start:
  `2026-04-01T18:30:47`
- Training end:
  `2026-04-01T18:32:03`
- Elapsed:
  `75.603s`
- Best validation checkpoint:
  epoch 4 with
  `best_val_loss = 0.298181`
- Final validation metrics at best epoch:
  - `val_artifact_local_bridge_teacher_waveform_extra_l1 = 0.000081`
  - `val_reconstruction_extra_waveform_l1 = 0.008684`
  - `val_reconstruction_extra_stft_l1 = 0.018042`
  - `val_extra_local_waveform_l1 = 0.001307`
  - `val_branch_protect_teacher_overlap_l1 = 0.000443`
  - `val_overlap_dual_residual_waveform_l1 = 0.004605`
  - `val_overlap_dual_residual_correction_waveform_l1 = 0.001550`
  - `val_overlap_dual_residual_correction_local_waveform_l1 = 0.001204`
  - `val_gate_keep_mean = 0.124413`
- Selector activity:
  - reconstruction extra `train 63 / 266, val 27 / 74`
  - overlap dual `train 66 / 266, val 14 / 74`
  - overlap dual extra `train 33 / 266, val 7 / 74`
  - absent extra `train 95 / 266, val 24 / 74`
  - branch protect teacher `train 120 / 266, val 27 / 74`

## Fixed Synthetic Checks relative `v249`

- Order:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`
- Result:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`

## Interval-Aware Real Probes relative `v249`

- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.1705 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.1589 dB`

## Matched Synthetic Artifact Read relative `v249`

- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +2.5453 dB`
  with
  `6 / 7`
  improved samples

## Read

- This is not a no-op.
  The bridge loss remains non-zero,
  the new conditioning layers are trainable,
  and the matched synthetic artifact-subspan asset still moves strongly positive.
- But explicit reference conditioning does not convert the family into a real artifact repair.
  Both active real artifact probes stay negative relative to
  `v249`.
- The shape is also now informative across the last three bridge-family points:
  `v258`
  was negative on both real artifact probes,
  `v259`
  was even more negative,
  and
  `v260`
  lands between them while keeping the same activation-dormant exact ties on the fixed five-pack and the leak probe.
  That is not the pattern of
  "the right bridge, still missing conditioning."
- The tighter conclusion after
  `v260`
  is:
  do not keep reusing the dedicated artifact-side bridge writer even with a better target-conditioning guess.
  The more likely next blocker is the writer family itself,
  not the absence of explicit reference conditioning on this writer.

## Conclusion

- `v260`
  closes the first explicit reference-conditioned continuation on the dedicated artifact-side bridge family.
- Do not continue this family through:
  - more small sweeps on
    `branch_overlap_artifact_local_bridge_conditioning_mode`
  - simple weight or blend retunes on the same
    `artifact_local_bridge`
    writer
  - more booster-asset swaps on the same bridge family
- If this line continues at all,
  the next step should change writer family or target representation,
  not keep the same artifact-side bridge and only change its conditioning.
