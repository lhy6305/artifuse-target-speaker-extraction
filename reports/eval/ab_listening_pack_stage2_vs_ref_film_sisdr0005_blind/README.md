# A/B Listening Pack

- manifest: `data/synthetic/val_manifest.jsonl`
- A: `legacy_stage2` -> `experiments\checkpoints\baseline_stft_mask_stage2\best.pt`
- B: `ref_film_sisdr0005` -> `experiments\checkpoints\baseline_stft_mask_stage2_ref_film_sisdr0005\best.pt`
- focus_recipes: `target_clean_plus_music, target_clean_speech, target_hard_plus_music, target_hard_speech`

Each sample directory contains:

- `mixture.wav`
- `target.wav`
- `reference.wav`
- `candidate_a.wav`
- `candidate_b.wav`
- `sample_meta.json`
- top-level `listening_sheet.csv`

Suggested listening order:

1. `mixture.wav`
2. `reference.wav`
3. `candidate_a.wav`
4. `candidate_b.wav`
5. `target.wav`

Use `summary.json` to see which samples are strongest improvements, regressions, or near ties.

Blind mode is enabled:

- listen using `candidate_a.wav` / `candidate_b.wav` only
- record your choice in `listening_sheet.csv`
- reveal model identity later via `blind_key.json`
