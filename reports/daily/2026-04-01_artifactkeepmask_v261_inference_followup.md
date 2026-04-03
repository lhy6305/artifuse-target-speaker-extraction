# 2026-04-01 artifact hard keep-mask inference check on top of `v249`: `v261` follow-up

## Summary

- Goal:
  test the narrow application hypothesis after
  `v260`:
  whether the target-conditioned artifact confound on top of
  `v249`
  was mainly caused by the local writer still being applied inside the artifact subspan itself.
- Route:
  no new training.
  Reuse the exact
  `v249`
  weights and add a second hard interval split:
  after the local hard split,
  force
  `artifact_local_proxy_intervals`
  back to
  `estimated_waveform_post_pre_present_controller`.
- Type:
  inference-only derived checkpoint.
- Result:
  the derived route stays strongly positive on the matched synthetic artifact-subspan asset,
  but both active real artifact probes are practical tie to tiny negative relative to
  `v249`,
  and the interval-aware leak probe plus the fixed synthetic five-pack stay exact tie.
- Verdict:
  close this first artifact hard keep-mask application family.
  The current real blocker is not well explained by
  "the local writer is simply writing in the wrong artifact subspan."

## Code Change

- Updated:
  `src/tse_prefix/models/stft_mask_baseline.py`
  to add
  `enable_branch_overlap_refine_artifact_hard_mask`
  and export
  `estimated_waveform_post_artifact_keepmasked`.
  When enabled,
  the model keeps the usual
  `v249`
  local hard split,
  then overwrites
  `artifact_local_proxy_intervals`
  with
  `estimated_waveform_post_pre_present_controller`.
- Updated:
  `scripts/train/train_stft_mask_baseline.py`
  to expose the new model flag in checkpoint configs for future trainable continuations.
- Validation:
  `py_compile`
  passed after the code change.

## `v261 = v249 + artifact hard keep-mask`

- Derived checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v261_v249_artifactkeepmask_inferenceonly_v1/best.pt`
- Parent checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- Type:
  inference-only config replay with identical weights and new output application logic

## Fixed Synthetic Checks relative `v249`

- Order:
  `abstention / same-gender keep / hard-present keep / artifact / local_speech_leak_proxy_v1`
- Result:
  `+0.0000 / +0.0000 / +0.0000 / +0.0000 / +0.0000 dB`

## Interval-Aware Real Probes relative `v249`

- `near_real_interval_leak_probe_v1 = +0.0000 dB`
- `near_real_interval_artifact_probe_v2 = -0.0007 dB`
- `near_real_interval_artifact_probe_v3_subspan = -0.0003 dB`

## Matched Synthetic Artifact Read relative `v249`

- `val_manifest_hard_present_artifact_local_proxy_v2_subspan = +1.3469 dB`
  with
  `6 / 7`
  improved samples

## Read

- This is a clean application-level test.
  No optimizer noise is involved because the weights are unchanged from
  `v249`.
- The result is not
  "positive but too small."
  It is a practical tie on the active real artifact probes.
  So the old hypothesis
  "the blocker is mainly that the local writer keeps writing inside the artifact subspan"
  does not explain the current real artifact confound.
- At the same time,
  the same application rule still improves the matched synthetic artifact-subspan asset.
  That reinforces the existing theme from
  `v258`
  to
  `v260`:
  the synthetic artifact-subspan family is easier to satisfy than the real target-conditioned artifact confound.
- The tighter conclusion after
  `v261`
  is that the next blocker is more likely upstream or representational.
  It does not look like a pure downstream application mistake inside the artifact window.

## Conclusion

- `v261`
  closes the first inference-only artifact hard keep-mask family on top of
  `v249`.
- Do not continue this family through:
  - more subspan hard-mask replay variants on the same
    `estimated_waveform_post_pre_present_controller`
    overwrite rule
  - simple threshold or window retunes on the same application-only idea
- If this line continues at all,
  the next step should change target representation or shared writer family,
  not keep re-testing application-only vetoes inside the artifact window.
