# Multi-Candidate Blind Listening Pack

- input packs: `reports/eval/ab_listening_pack_silence_over_leak_frontier_v1_v32_vs_v49_blind`, `reports/eval/ab_listening_pack_silence_over_leak_frontier_v1_v32_vs_v54_blind`, `reports/eval/ab_listening_pack_silence_over_leak_frontier_v1_v32_vs_v59_blind`
- candidate labels: `v32`, `v49_adaptermask`, `v54_dualdecoder_exactguard`, `v59_dualdecoder_basedeltaproj_w005`

Use the GUI with this directory and listen to `candidate_1.wav`, `candidate_2.wav`, `candidate_3.wav`, ...
Reserved files like `mixture.wav`, `reference.wav`, and `target.wav` are preserved when present in the input packs.
Merged export audio is written in mono so mixture/reference/target/candidates share the same channel layout.
Do not open `blind_key.json` until scoring is complete.
