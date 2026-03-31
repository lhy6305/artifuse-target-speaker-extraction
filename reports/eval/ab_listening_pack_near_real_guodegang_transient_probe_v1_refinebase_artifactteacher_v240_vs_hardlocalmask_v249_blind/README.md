# A/B Listening Pack

- manifest: `data/probes/near_real_guodegang_transient_probe_v1_manifest.jsonl`
- A: `refinebase_artifactteacher_v240` -> `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v240_v239_refinebase_artifactteacher004_v1_ft1/best.pt`
- B: `hardlocalmask_v249` -> `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v249_v240_hardlocalmask_v1_ft1/best.pt`
- focus_recipes: `near_real_guodegang_speech_probe`

Each sample directory contains:

- `mixture.wav`
- `target.wav`
- `reference.wav`
- `candidate_a.wav`
- `candidate_b.wav`
- `sample_meta.json`
- top-level `listening_sheet.csv`
- top-level `listening_rubric.json`

Suggested listening order:

1. `mixture.wav`
2. `reference.wav`
3. `candidate_a.wav`
4. `candidate_b.wav`
5. `target.wav`

Use `summary.json` to see which samples are strongest improvements, regressions, or near ties.

Listening sheet rubric:

- `better_output`: `file_a` / `file_b` / `tie` / `uncertain`
- `file_*_source_retention`: choose from `excellent, good, fair, weak, lost`
- `file_*_interference_leak`: choose from `none, slight, moderate, heavy, extreme`
- `file_*_volume_fluctuation`: choose from `none, slight, moderate, heavy, extreme`
- `file_*_artifact`: choose from `none, slight, moderate, heavy, extreme`
- `decision_tags`: optional semicolon-separated tags, e.g. `better_source_retention;less_interference_leak`
- all files in one sample folder share the same safety gain, so playback is more stable while relative A/B level differences are preserved

Blind mode is enabled:

- listen using `candidate_a.wav` / `candidate_b.wav` only
- record your choice in `listening_sheet.csv`
- reveal model identity later via `blind_key.json`
