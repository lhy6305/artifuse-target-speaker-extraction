# 2026-03-28 split-controller and refine-base on `v157`: `v161 / v162 / v163 / v164` follow-up

## Summary

- Goal:
  continue from `v157`, but stop treating
  `0007 total leak`
  as a side effect of the same scalar controller that also carries absent veto.
- Two mechanism families were checked:
  - split keep / absent apply controllers on top of `v157`
  - no-teacher `refine_base` sibling on top of `v157`
- Main conclusion:
  both families are closed for now.
  - `v161` is a true reject because split joint training blows up
    `near_real_0007 speech_only`
    and whole `0007`
  - `v162` is mechanism-safe but effectively exact tie
  - `v163 / v164` show that hanging a no-teacher
    `refine_base`
    sibling on `v157`
    is still structural no-op, even after broadening the selector from
    `3 / 99`
    to
    `8 / 99`
- Active base remains:
  `v157`.

## New Training Support

- Code landed in:
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
- Added split gate supervision support:
  - `branch_overlap_cancel_apply_keep_controller`
  - `branch_overlap_cancel_apply_absent_controller`
  - combined controller
    `keep * (1 - absent)`
- Added loss-side wiring so
  `gate_absent / gate_keep / gate_target`
  can read separate controller tensors instead of always sharing one scalar map.
- `py_compile` had already passed for these code changes.

## `v161 = v157 + split keep / absent apply controllers`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v161_v157_applycontroller_splitcontrollers_v1_ft1`
- Setup:
  - init = `v157`
  - teacher metadata fallback disabled
  - trainable prefixes:
    - `branch_overlap_cancel_apply_controller_head`
    - `branch_overlap_cancel_apply_absent_controller_head`
  - gate supervision source:
    `overlap_cancel_apply_controller_split`
  - gate weights:
    `absent = 1.0`
    / `keep = 2.0`

### Training Signal

- Both heads were genuinely active.
- But keep-side activation collapsed very low:
  - `val_gate_absent_mean ~= 0.000173`
  - `val_gate_keep_mean ~= 0.004094`
- This already suggested over-veto / near-dead routing.

### Fixed Checks relative `v157`

- abstention `-0.0086 dB`
- same-gender keep `+0.0004 dB`
- hard-present keep `-0.0072 dB`
- artifact proxy `-0.0059 dB`
- local speech leak proxy `-0.0099 dB`

### Near-Real relative `v157`

- whole:
  - `more_interference_leaky = tie:3, v161:1`
  - `better_retention_minus_leak = tie:2, v157:1, n/a:1`
- decisive regression:
  `near_real_0007`
  - `delta_interference_capture_db = +27.0105 dB`
  - `delta_retention_minus_leak_db = -27.0409 dB`
- local:
  - `more_speech_interference_leaky = tie:3, v161:1`
  - `more_total_interference_leaky = tie:3, v157:1`
- decisive local contradiction:
  `near_real_0007`
  - `delta_speech_interference_capture_db = +5.4442 dB`
  - `delta_total_interference_capture_db = -1.4732 dB`

### Verdict

- `v161`
  proves that jointly training split keep / absent controllers is not the answer.
- It improves
  `0007 total leak`
  locally,
  but does so by sharply worsening
  `0007 speech_only`
  and whole `0007`.
- Direct reject.

## `v162 = v157 + absent-veto-only split controller`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v162_v157_applycontroller_absentvetoonly_v1_ft1`
- Setup:
  same as `v161`,
  except only
  `branch_overlap_cancel_apply_absent_controller_head`
  was trainable and
  `gate_keep_weight = 0.0`.

### Training Signal

- This time the keep controller did not collapse:
  `val_gate_keep_mean ~= 0.075943`
- The absent veto still learned strongly:
  `val_gate_absent_mean ~= 0.000173`
- So the mechanism itself was trainable.

### Fixed Checks relative `v157`

- abstention `-0.0002 dB`
- same-gender keep `-0.0001 dB`
- hard-present keep `-0.0001 dB`
- artifact proxy `-0.0001 dB`
- local speech leak proxy `+0.0001 dB`

### Near-Real relative `v157`

- whole:
  - `more_interference_leaky = tie:4`
  - `better_retention_minus_leak = tie:3, n/a:1`
- key sample:
  `near_real_0007`
  - `delta_interference_capture_db = +0.1007 dB`
  - `delta_retention_minus_leak_db = -0.1006 dB`
- local:
  - `more_speech_interference_leaky = tie:4`
  - `more_total_interference_leaky = tie:4`
  - `better_retention_minus_speech_leak = tie:3, n/a:1`
  - `better_retention_minus_total_leak = tie:3, n/a:1`
- local key deltas:
  `near_real_0007`
  - `delta_speech_interference_capture_db = -0.0003 dB`
  - `delta_total_interference_capture_db = +0.0026 dB`
  `near_real_0009`
  - `delta_speech_interference_capture_db = +0.0011 dB`

### Verdict

- `v162`
  is mechanism-safe but ineffective.
- It does not inherit the
  `v161`
  failure mode,
  but it is also not a real candidate and not worth listening.

## `v163 = v157 + no-teacher refine-base hardlocaltotal sibling`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v163_v157_refinebase_hardlocaltotal_noteacher_v1_ft1`
- Setup:
  - init = `v157`
  - teacher metadata fallback disabled
  - trainable prefixes:
    `branch_overlap_refine_head`
  - overlap loss:
    `overlap_interference_weight = 0.04`
  - mode:
    `residual_projection_ratio`
  - selector:
    `sample_ids_hard_present_artifact_local_proxy_v1_all.txt`

### Training Signal

- This selector is structurally sparse on the available asset:
  - train `3 / 99`
  - val `3 / 37`
- Non-zero training metrics existed,
  but fixed evaluation came back exact tie.

### Fixed Checks relative `v157`

- abstention `+0.0000 dB`
- same-gender keep `+0.0000 dB`
- hard-present keep `+0.0000 dB`
- artifact proxy `+0.0000 dB`
- local speech leak proxy `+0.0000 dB`

### Verdict

- `v163`
  is practical exact no-op.
- This closes the idea that simply adding a no-teacher
  `refine_base`
  sibling with the ultra-sparse
  hardlocal total-leak selector
  can rescue
  `v157`.

## `v164 = v157 + no-teacher refine-base broader hard-present artifact sibling`

- Checkpoint:
  `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v164_v157_refinebase_hardpresentartifact_noteacher_v1_ft1`
- Setup:
  identical to `v163`,
  except the selector was broadened to
  `sample_ids_hard_present_artifact_proxy_v1_all.txt`.

### Training Signal

- Coverage broadened from
  `3 / 99`
  to
  `8 / 99`
  on train,
  but val still only had
  `1 / 37`.
- `overlap_interference_projection_ratio`
  stayed clearly non-zero during training.

### Fixed Checks relative `v157`

- abstention `+0.0000 dB`
- same-gender keep `+0.0000 dB`
- hard-present keep `+0.0000 dB`
- artifact proxy `+0.0000 dB`
- local speech leak proxy `+0.0000 dB`

### Verdict

- `v164`
  is also exact no-op.
- So the blocker is not just
  `3 / 99`
  sparsity.
  Even a slightly broader hard-present artifact selector still fails to produce any observable output movement on top of `v157`.

## Final Verdict

- Keep `v157` as the active base.
- Stop here for:
  - split keep / absent apply-controller training
  - absent-veto-only split controller
  - no-teacher `refine_base` sibling on top of `v157`
    with
    `hardlocaltotal`
    or
    `hard_present_artifact`
    selectors
- No listening pack is exported from this round.

## Next Step

- If continuing, do not keep sweeping these families.
- The next requirement is stronger data support for
  `present-total`
  local supervision:
  either
  - materialize a broader selector / asset that truly covers
    `0007 total leak`
    beyond the current
    `3 / 99`
    or
    `8 / 99`
    regime
  - or design a new output apply path that does not rely on such sparse total-risk selectors
