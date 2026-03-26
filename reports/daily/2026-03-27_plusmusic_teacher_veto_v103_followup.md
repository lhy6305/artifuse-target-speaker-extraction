# plus-music teacher veto `v103` follow-up

## 本轮目标

在 `v102` 已确认“纯 speech overlap 指标更贴近人耳、但 `0007` 痛点仍未改善”之后，
继续验证一个更窄的问题：

- 是否能在不放弃 `v102` 的 `speech_only overlap residual` 主效应前提下，
- 只对 `speech_plus_music` hard-risk 子域加一个 frozen-teacher veto，
- 把 `0007` 对应的 hard-present artifact 风险压回去。

## 配置

### `v103 = v102 + plus_music teacher veto`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v103_v102_speechonly_plusmusic_teacher_veto_ft1`

初始化：

- student：
  - `v102`
- teacher：
  - `v81`

保持不变：

- `v102` 的 `speech_only overlap_interference_extra`
- 只训：
  - `branch_decoder_mask_head`

新增 teacher veto：

- `branch_protect_teacher_overlap_weight = 0.04`
- selector：
  - `focus_patterns = target_full`
  - `focus_interference_profiles = speech_plus_music`
  - `require_speech_interference = true`
  - `require_music_interference = true`
  - `min_interference_layer_count = 2`
  - `max_interference_layer_count = 2`
  - `min_target_energy_ratio = 0.05`
  - `max_target_energy_ratio = 0.12`
  - `min_overlap_ratio = 0.6`
  - `max_target_transient_presence_share_mean = 0.04`

## 训练结果

训练摘要：

- `elapsed_sec = 11.134`
- `best_val_loss = 0.0269295`

teacher selector 命中：

- train `14 / 102`
- val `4 / 33`

结论：

- teacher veto 确实被激活，不是 no-op；
- 命中的就是此前确认风险最高的 `plus_music hard-present` 子域。

## synthetic 固定验收

相对 `v81`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `+3.7743 dB`
  - `7 improve / 1 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+1.9130 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.3545 dB`
  - `14 improve / 1 regress`

结论：

- `v103` 没有因为新增 teacher veto 而把 `v102` 的主收益训坏；
- automatic 上，它比 `v102` 还更强一档。

## near-real 非盲 objective

非盲包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v103`

whole-utterance：

- `overall_pass = true`
- `better_retention_minus_leak`
  - `v103 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `more_interference_leaky`
  - `v81 = 4`

样本解释：

- `near_real_0003`
  - `retention-minus-leak` 明确优于 `v81`
  - 但代价仍是更低 target capture
- `near_real_0006`
  - leak 更低
  - whole-utterance tradeoff 仍只是 `tie`
- `near_real_0007`
  - whole-utterance 已不再出 hard failure
  - 但仍没有形成明确正收益
- `near_real_0009`
  - absent suppression 优于 `v81`

## overlap-local benchmark

- `better_retention_minus_speech_leak`
  - `v103 = 2`
  - `v81 = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky`
  - `v81 = 3`
  - `tie = 1`
- `more_artifact_proxy_heavy`
  - `v103 = 3`
  - `tie = 1`

关键样本解释：

- `near_real_0003`
  - local `retention-minus-speech-leak = v103`
  - 但 artifact proxy 仍更重
- `near_real_0006`
  - local `retention-minus-speech-leak = v103`
  - artifact proxy 也更重
- `near_real_0007`
  - `better_retention_minus_speech_leak = v81`
  - `more_artifact_proxy_heavy = v103`
  - 当前痛点仍未解决
- `near_real_0009`
  - local speech leak 继续更低
  - artifact proxy 基本打平

结论：

- `v103` 已把 whole-utterance automatic gate 拉回绿灯；
- 但真正的 blocker 仍是 `0007` 的局部 artifact / retention 反向点。

## pack 导出兼容修复

本轮顺手修了 `export_ab_listening_pack.py` 的 near-real 兼容问题：

- 不再假设 manifest 必带：
  - `recipe`
  - `temporal_pattern`
  - `metadata_path`
- 不再依赖 `SyntheticTSEDataset` 才能导 near-real pack
- 导出的 `sample_meta.json` 现已补写：
  - `mixture_audio_path`
  - `target_audio_path`
  - `reference_audio_path`
  - `exports`
- non-blind 模式不再错误读取 `candidate_a / candidate_b`

因此当前这条链已能稳定重跑：

- `export_ab_listening_pack.py`
- `audit_listening_pack_assets.py`
- `analyze_listening_pack_tradeoff.py`
- `gate_near_real_tradeoff.py`
- `analyze_listening_pack_bandwidth.py`
- `analyze_overlap_local_benchmark.py`

## 当前裁决

1. `v103` 是目前这一小家族里最值得继续听审的 automatic candidate。
2. 它修好了 automatic gate，但还没修好 `0007` 的局部 artifact 痛点。
3. 因此当前默认下一步不是 `v103+` sweep，而是直接做：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v103_blind
```

focused 听审重点：

- `near_real_0007`
  - `v103` 是否仍比 `v81` 更假、更糙
- `near_real_0003`
  - local 指标转正是否终于对应到可听改善
- `near_real_0006`
  - 是否继续“更干净但也更空”
- `near_real_0009`
  - absent 是否仍保持自然
