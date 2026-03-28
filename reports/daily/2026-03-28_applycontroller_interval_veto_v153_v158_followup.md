# 2026-03-28 apply-controller interval-veto `v153 / v154 / v155 / v156 / v157 / v158` follow-up

## Summary

- Goal:
  continue the `v142` line, but move from generic `apply-controller` direct-subtract routing to interval-supervised local veto on `branch_overlap_cancel_apply_controller`.
- New training support:
  `compute_losses` now supports interval-scoped gate supervision for `overlap_cancel_apply_controller`, so absent / keep targets can be applied only inside annotated local windows instead of whole selected samples.
- Main conclusion:
  this family produced the first credible mechanism-positive evidence point on top of `v142`, but it still did not cross the listening bar.
- Best continuation in this family:
  `v157 = v156 + gate_absent_weight 1.0`.
- Not worth continuing:
  `v155` is invalid because broader keep did not actually broaden on the old asset, and `v158` shows `gate_keep_weight 3.0` only trims both the good and bad local deltas instead of fixing the blocker.

## Training Asset Boundary

- Original narrow asset:
  `train/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
- Real broader-keep asset added this round:
  `train/val_manifest_local_speech_leak_artifact_paired_hardlocal_plus_true_absent_anchor_bundle_v1.jsonl`
- Reason:
  `v2` does not contain the broader hardlocal keep ids from `reports/data/v152_overlap_cancel_focus_sample_ids.txt`, so any "broader keep" run on `v2` is structurally invalid.

## Pilot Results

### `v153 = v142 + apply-controller interval-veto v1`

- selector hits:
  overlap-cancel `train 3/203`, `val 3/63`; absent `train 95/203`, `val 24/63`
- fixed checks relative `v142`:
  `-0.0884 / -0.0366 / -0.0396 / -0.0335 dB`
  on abstention / same-gender keep / hard-present keep / artifact
- local proxy:
  `+0.0840 dB`
- near-real:
  first mechanism-positive point on top of `v142`
  because `near_real_0007 speech_only` and `near_real_0009 absent local` both moved the right way
- blocker:
  `0007 total leak` still regressed, and `0009` whole absent leakage got worse

### `v154 = v153 + gate_keep_weight 2.0`

- selector hits remained narrow:
  overlap-cancel `train 3/203`, `val 3/63`
- fixed checks relative `v142`:
  `-0.0280 / -0.0134 / -0.0113 / -0.0095 dB`
- local proxy:
  `+0.0513 dB`
- near-real:
  `near_real_0007` whole tradeoff improved strongly
  with `delta_interference_capture_db = -15.6794 dB`
  and `delta_retention_minus_leak_db = +15.7378 dB`
- blocker:
  `near_real_0009` whole absent leakage still regressed,
  and local `0007 total leak` still moved the wrong way

### `v155 = intended broader-keep retry on v2 asset`

- verdict:
  invalid scratch
- reason:
  broader keep ids still did not exist in `v2`, so overlap-cancel selector remained effectively the same narrow `3/203`, `3/63` regime
- action:
  no fixed / near-real evaluation retained for this checkpoint

### `v156 = v154 + union-bundle broader keep`

- first valid broader-keep run:
  overlap-cancel `train 33/233`, `val 7/67`
- fixed checks relative `v142`:
  `+0.0029 / -0.0007 / +0.0019 / +0.0022 dB`
- local proxy:
  `+0.0044 dB`
- near-real:
  safer than `v154`, because `near_real_0009` whole absent regression shrank to threshold-level tie
- blocker:
  broader keep also collapsed controller behavior toward near-neutral,
  so the whole family drifted toward practical no-op

### `v157 = v156 + gate_absent_weight 1.0`

- fixed checks relative `v142`:
  `+0.0084 / -0.0005 / +0.0072 / +0.0059 dB`
- local proxy:
  `+0.0101 dB`
- whole near-real:
  strongest point in this family
  with `near_real_0007`
  `delta_interference_capture_db = -27.3083 dB`
  and `delta_retention_minus_leak_db = +27.3392 dB`
- local near-real:
  `near_real_0007`
  `delta_speech_interference_capture_db = -5.5297 dB`
  but `delta_total_interference_capture_db = +1.5121 dB`
- absent side:
  `near_real_0009` whole and local both stayed near tie, slightly on the better side, and artifact stayed tie
- verdict:
  current best continuation in the interval-veto union-bundle family
  but still not a listening candidate because `0007 total leak` remains wrong-way

### `v158 = v157 + gate_keep_weight 3.0`

- fixed checks relative `v142`:
  `+0.0066 / -0.0002 / +0.0060 / +0.0037 dB`
- local proxy:
  `+0.0056 dB`
- local near-real:
  versus `v157`, `0007 total leak` regression shrank only slightly
  from `+1.5121 dB` to `+1.3504 dB`,
  but `0007 speech_only` improvement also weakened
  from `-5.5297 dB` to `-5.0963 dB`,
  and `0009 absent local` weakened
  from `-0.2031 dB` to `-0.1117 dB`
- verdict:
  `gate_keep_weight` sweep is not the answer here

## Final Verdict

- `v153`:
  first credible interval-veto evidence point
- `v154`:
  best narrow-asset continuation, but too aggressive on `0009`
- `v155`:
  invalid broader-keep attempt
- `v156`:
  first valid union-bundle broader-keep run; safer, but too neutral
- `v157`:
  best continuation in this family
- `v158`:
  confirms `gate_keep_weight` sweep should stop here

## Next Step

- Do not give listening commands yet.
- Keep `v157` as the active base for this family.
- If continuing, do not sweep `gate_keep_weight` again.
- The next mechanism should target `near_real_0007 total leak` directly, not just `speech_only` leak:
  either by more local-window-specific apply semantics, or by splitting the current controller supervision so the total-leak blocker is not treated as a side effect of absent-veto pressure.
