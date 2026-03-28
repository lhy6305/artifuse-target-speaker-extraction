# 2026-03-28 apply-controller interval-veto local-apply `v159 / v160` follow-up

## Summary

- Goal:
  continue from `v157`, but make the direct-subtract writeback more local without changing the union-bundle interval-veto supervision.
- New code support:
  - `v159` adds a fixed speech-band apply mask via `branch_overlap_cancel_apply_max_freq_ratio`
  - `v160` adds a controller activation floor via `branch_overlap_cancel_apply_controller_floor`
- Main conclusion:
  both pilots stayed near-tie on fixed checks, but neither fixed the `near_real_0007 total leak` blocker.
- Active base remains:
  `v157`.
- Stop here:
  do not continue sweeping
  `branch_overlap_cancel_apply_max_freq_ratio`
  or
  `branch_overlap_cancel_apply_controller_floor`.

## Setup

- Base checkpoint:
  `v157`
- Train manifest:
  `data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl`
- Val manifest:
  `data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl`
- Trainable prefixes:
  `branch_overlap_cancel_apply_controller_head`
- Shared interval-veto supervision:
  - `gate_absent_weight = 1.0`
  - `gate_keep_weight = 2.0`
  - `gate_supervision_source = overlap_cancel_apply_controller`
  - overlap-cancel selector reused
    `reports/data/v152_overlap_cancel_focus_sample_ids.txt`
  - absent selector reused
    `target_absent_head / target_absent_tail`
    with speech-only requirement

## `v159 = v157 + speech-band-limited direct-apply`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v159_v157_applycontroller_intervalveto_speechbandapply05_v1_ft1`
- Mechanism:
  keep the same controller, but limit direct subtract to the lower `50%` frequency bins.
- Fixed checks relative `v157`:
  `+0.0009 / -0.0003 / +0.0020 / +0.0000 dB`
  on abstention / same-gender keep / hard-present keep / artifact
- Local proxy:
  `+0.0017 dB`
- Whole near-real:
  `near_real_0007`
  got worse:
  - `delta_interference_capture_db = +4.5358 dB`
  - `delta_retention_minus_leak_db = -4.5334 dB`
- Local near-real:
  `near_real_0007`
  - `delta_speech_interference_capture_db = -0.1698 dB`
  - `delta_total_interference_capture_db = +0.1203 dB`
  `near_real_0009`
  - local absent leak `-0.1342 dB`
  - whole absent leak `+0.3058 dB`
- Verdict:
  speech-band limiting preserved near-tie guardrails, but only shrank magnitude.
  It did not flip the sign of the `0007 total leak` blocker, and whole `0007` got clearly worse.

## `v160 = v157 + apply-controller floor 0.2`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v160_v157_applycontroller_intervalveto_controllerfloor02_v1_ft1`
- Mechanism:
  zero out controller values below `0.2`, then renormalize the remaining range to `[0, 1]`, so subtract writeback only happens on higher-confidence local windows.
- Fixed checks relative `v157`:
  `-0.0002 / -0.0003 / +0.0014 / -0.0008 dB`
  on abstention / same-gender keep / hard-present keep / artifact
- Local proxy:
  `+0.0005 dB`
- Whole near-real:
  `near_real_0007`
  still got worse:
  - `delta_interference_capture_db = +3.4971 dB`
  - `delta_retention_minus_leak_db = -3.4958 dB`
- Local near-real:
  `near_real_0007`
  - `delta_speech_interference_capture_db = -0.2607 dB`
  - `delta_total_interference_capture_db = +0.0771 dB`
  `near_real_0009`
  - local absent leak `-0.0979 dB`
  - whole absent leak `+0.2088 dB`
- Verdict:
  controller floor behaved like a softer version of `v159`:
  slightly better `0007 speech_only`,
  slightly smaller `0007 total leak` regression,
  but still the wrong sign and still whole-tradeoff-negative on `0007`.

## Final Verdict

- `v159`:
  fixed-band local apply is insufficient
- `v160`:
  sparse time-window apply is also insufficient
- Shared new boundary:
  attenuating current writeback magnitude does not solve the blocker.
  It only trades:
  - smaller `0007 speech_only` improvements
  - against smaller but still wrong-way `0007 total leak` regression

## Next Step

- Keep `v157` as the active base.
- Do not continue:
  - `branch_overlap_cancel_apply_max_freq_ratio`
  - `branch_overlap_cancel_apply_controller_floor`
- If continuing, the next mechanism should split controller supervision itself so
  `0007 total leak`
  is no longer a side effect of the same scalar controller that also handles absent veto.
