# A/B Listening Pack

- manifest: `data/references/real_eval_manifest_bandwidth_guardrail_v1.jsonl`
- A: `v81` -> `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v81_v79_audibility_gate_target_v1_ft1/best.pt`
- B: `v110` -> `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v110_v109_local_speech_leak_artifact_paired_0007like_bundle_v1_ft1/best.pt`
- focus_recipes: ``

Each sample directory contains:

- `mixture.wav`
- `target.wav`
- `reference.wav`
- `v81.wav`
- `v110.wav`
- `sample_meta.json`
- top-level `listening_sheet.csv`
- top-level `listening_rubric.json`

Suggested listening order:

1. `mixture.wav`
2. `reference.wav`
3. `v81.wav`
4. `v110.wav`
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
