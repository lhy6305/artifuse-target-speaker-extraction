# Multi-Candidate Blind Listening Pack

- input packs: `reports/eval/ab_listening_pack_silence_over_leak_guardrail_v1_stage2_vs_v32_blind`, `reports/eval/ab_listening_pack_silence_over_leak_guardrail_v1_stage2_vs_v8_blind`, `reports/eval/ab_listening_pack_silence_over_leak_guardrail_v1_stage2_vs_v13_blind`
- candidate labels: `legacy_stage2`, `v32`, `v8_absentguard`, `v13_absentguard`

Use the GUI with this directory and listen to `candidate_1.wav`, `candidate_2.wav`, `candidate_3.wav`, ...
Reserved files like `mixture.wav`, `reference.wav`, and `target.wav` are preserved when present in the input packs.
Merged export audio is written in mono so mixture/reference/target/candidates share the same channel layout.
Do not open `blind_key.json` until scoring is complete.
