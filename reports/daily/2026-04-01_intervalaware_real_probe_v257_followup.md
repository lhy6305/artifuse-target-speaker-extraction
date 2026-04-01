# 2026-04-01 interval-aware real probes close `v257`

## Summary

- Goal:
  resolve the ambiguity left by
  `v257`,
  where the current near-real probe packs were exact tie only because they did not carry local-proxy interval metadata.
- Method:
  build two first-pass interval-aware real manifests with manual full-span local proxies:
  a leak-focused probe that excludes the fixed-target artifact trio,
  and an artifact-focused probe that isolates that trio.
  Then re-evaluate
  `v253`
  versus
  `v257`
  on those manifests.
- Assets:
  - `data/probes/near_real_interval_leak_probe_v1_manifest.jsonl`
  - `data/probes/near_real_interval_artifact_probe_v1_manifest.jsonl`
- Result:
  once the writer is actually activated on real assets,
  `v257`
  is uniformly worse than
  `v253`
  on both probes.
  Leak probe:
  `9 / 9`
  regressions,
  average
  `-0.5154 dB`.
  Artifact probe:
  `3 / 3`
  regressions,
  average
  `-0.9569 dB`.
- Verdict:
  the dedicated dual-local-bridge hardlocalmask-source swap is now closed as a bounded reject.
  The earlier
  `0.0 dB`
  read on the old real probes was a schema-inactive artifact, not real-side safety.

## Assets

- Leak manifest:
  `data/probes/near_real_interval_leak_probe_v1_manifest.jsonl`
- Artifact manifest:
  `data/probes/near_real_interval_artifact_probe_v1_manifest.jsonl`
- Local-proxy mode:
  `manual_fullspan_probe`
- Leak sample count:
  `9`
  (`probe_0002 / 0005 / 0008 / 0019 / 0020 / 0021 / 0022 / 0023 / 0024`)
- Artifact sample count:
  `3`
  (`probe_0011 / 0014 / 0017`)

## Interval-Aware Leak Probe relative `v253`

- Compare output:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_leak_probe_v1`
- Probe analysis:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_leak_probe_v1/near_real_speech_probe_analysis/summary.json`
- Overall:
  `-0.5154 dB`
  with
  `0 improved / 9 regressed / 0 near tie`
- By speech family:
  - `friend_raw = -0.9034 dB`
  - `guodegang_raw = -0.3214 dB`
- By anchor:
  - `near_real_0003 = -0.9034 dB`
  - `near_real_0006 = -0.3214 dB`
- By clip:
  - `friend_anchor_45s = -0.9385 dB`
  - `friend_anchor_215s = -0.9329 dB`
  - `friend_absent_820s = -0.8389 dB`
  - `guodegang_anchor_120s = -0.3555 dB`
  - `guodegang_absent_480s = -0.2874 dB`

## Interval-Aware Artifact Probe relative `v253`

- Compare output:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_artifact_probe_v1`
- Probe analysis:
  `reports/eval/compare_hardlocalmask_covctrl_v253_vs_dualbridgehardmask_v257_on_near_real_interval_artifact_probe_v1/near_real_speech_probe_analysis/summary.json`
- Overall:
  `-0.9569 dB`
  with
  `0 improved / 3 regressed / 0 near tie`
- By fixed-target clip:
  - `friend_anchor_45s = -0.9195 dB`
  - `friend_anchor_215s = -0.9696 dB`
  - `friend_absent_820s = -0.9816 dB`

## Read

- The earlier whole-probe
  `0.0 dB`
  result is now explained cleanly.
  The old probe manifests did not expose local-proxy interval metadata,
  so the hard local-mask writer family could not activate there.
- Once a first-pass interval-aware schema is added,
  the route is readable,
  and it reads badly.
  The direction is not mixed:
  every leak-focused sample regresses,
  and every artifact-focused sample regresses.
- That matters scientifically.
  The
  `v257`
  writer-family swap is not merely "unread on real assets" anymore.
  It is now "readable and wrong-way" on the first interval-aware real assets.
- These new assets are still first-pass probes,
  not final business gates.
  The full-span local proxy is intentionally coarse and may over-activate the writer.
  But it is already sufficient to reject this family as a promising real-side continuation.

## Conclusion

- Close the
  `v257`
  dedicated dual-local-bridge hardlocalmask-source-swap family as a bounded reject.
- Do not retune this family with the current
  `post_dual_local_bridge`
  hard local-mask source.
- Keep the schema lesson:
  interval-gated writer families need interval-aware real assets before their real-side reads are interpretable.
- But keep the stronger lesson too:
  once that schema is added,
  `v257`
  is not a hidden winner.
  It is uniformly worse than
  `v253`
  on both the leak-focused and artifact-focused interval-aware real probes.
