# local speech leak proxy `v1` and `v107` follow-up

## 本轮目标

`v106` 已经证明：

- local teacher-overlap veto 能先止住 `v103 / v105` 那种 artifact 爆炸；
- 但它不会自动把 `near_real_0007` 里的局部 speech leak 压下去。

因此本轮不再继续做“更强 teacher 对齐”，而是把问题改写成更显式的训练监督：

1. 仍然从 `speech_plus_music` 原样本里自动选 `0007` 风格高 risk 局部窗；
2. 但导出的训练视图只保留 `target + speech layer`；
3. 让现有 `speech_only overlap_interference_extra` 直接变成显式的 local speech-leak backstop；
4. 不改模型结构，先验证这条监督语义本身是否足够形成更好的中间解。

## 新增资产

### `local_speech_leak_proxy_v1`

新增脚本：

- `scripts/data/build_local_speech_leak_proxy.py`

做法：

- 输入来源仍是：
  - `hard_present_artifact_proxy_v1`
- 只接受：
  - `interference_profile = speech_plus_music`
- 先在完整 `music_plus_speech` 混合上切 `1.0s` 局部窗；
- 选择规则优先找：
  - local speech 能量高
  - local music 仍在场
  - local target share 不退化成纯 absent
- 导出时改写训练视图：
  - `mixture.wav = target + speech_only`
  - `interference_profile = speech_only`
- 同时保留原局部统计，便于回看：
  - `local_fullmix_target_share`
  - `local_speech_share_of_interference`
  - `local_music_share_of_interference`

脚本侧还补了一处实际兼容：

- 源 `interference_layers` 里存在 `.m4a`；
- 当前 `torchaudio + soundfile` 后端不能稳定读这类文件；
- 因此脚本加入了 `ffmpeg` 解码回退，避免局部 proxy 物化因输入格式中断。

物化结果：

- `data/synthetic/train_manifest_local_speech_leak_proxy_v1.jsonl`
- `data/synthetic/val_manifest_local_speech_leak_proxy_v1.jsonl`
- `data/synthetic/sample_ids_local_speech_leak_proxy_v1_train.txt`
- `data/synthetic/sample_ids_local_speech_leak_proxy_v1_val.txt`
- `reports/data/selector_local_speech_leak_proxy_v1_train_summary.json`
- `reports/data/selector_local_speech_leak_proxy_v1_val_summary.json`

关键统计：

- train `selected_count = 33`
- val `selected_count = 7`
- train `selection_mode_counts`
  - `speech_target_share_bounded_peak = 12`
  - `speech_peak_music_present_fallback = 21`
- val `selection_mode_counts`
  - `speech_target_share_bounded_peak = 4`
  - `speech_peak_music_present_fallback = 3`
- train `local_speech_share_of_interference_mean = 0.8485`
- train `local_music_share_of_interference_mean = 0.1515`
- train `local_target_to_speech_energy_db_mean = -8.2558 dB`

### `speech_leak_local_aware_bundle_v1`

新的训练 bundle：

- `data/synthetic/train_manifest_speech_leak_local_aware_bundle_v1.jsonl`
- `data/synthetic/val_manifest_speech_leak_local_aware_bundle_v1.jsonl`
- `data/synthetic/sample_ids_speech_leak_local_aware_bundle_v1_train.txt`
- `data/synthetic/sample_ids_speech_leak_local_aware_bundle_v1_val.txt`
- `reports/data/merge_speech_leak_local_aware_bundle_v1_train_summary.json`
- `reports/data/merge_speech_leak_local_aware_bundle_v1_val_summary.json`

组成：

- 基础仍是：
  - `abstention_gate_bundle_v2`
- 追加：
  - `local_speech_leak_proxy_v1`

规模：

- train `102 + 33 = 135`
- val `33 + 7 = 40`

## `v107` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v107_v81_overlap_purify_v5_local_speech_leak_bundle_v1_ft1`

初始化：

- `v81`

训练口径：

- 结构与 trainable scope 继续复用 `v102`
- 仍然只训练：
  - `branch_decoder_mask_head`
- 保留：
  - `branch_decoder_head`
  - `branch_abstention_gate`
- overlap-local loss 仍是：
  - `speech_only overlap_interference_extra`
- 关键差异不在 loss 配置，而在 bundle 中新增了显式 local speech-leak 样本

selector 激活：

- train
  - `overlap_interference_extra = 38 / 135`
- val
  - `overlap_interference_extra = 12 / 40`

相对 `v102`：

- `v102`
  - train `22 / 102`
  - val `7 / 33`
- `v107`
  - train `38 / 135`
  - val `12 / 40`

说明：

- 新 bundle 确实把显式 speech-leak 监督命中率拉高了；
- 这不是参数偶然漂移，而是数据子域真的被物化进训练集。

训练结果：

- 训练成功结束
- `elapsed_sec = 11.655`
- `best.pt / latest.pt / train_summary.json` 已落盘

## 自动验收结果

### synthetic 固定验收

relative `v81`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +3.0895 dB`
  - `7 improve / 1 regress`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.4266 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.1428 dB`
  - `14 improve / 2 regress`

结论：

- `v107` 在当前 `v102 -> v106 -> v107` 这条显式 speech-leak family 里，synthetic 是明显更强的一版；
- 而且不是只在 abstention proxy 上涨，两个 keep guardrail 也没有被一起拉坏。

### near-real whole-utterance

non-blind pack：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107`

tradeoff gate：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107/tradeoff_analysis/gate_summary.json`
- `overall_pass = true`

whole-utterance 主结论：

- `better_source_retention_candidate_counts`
  - `v81 = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v81 = 2`
  - `tie = 2`
- `better_retention_minus_leak_candidate_counts`
  - `v107 = 1`
  - `v81 = 1`
  - `tie = 1`
  - `not_applicable = 1`

分样本：

- `near_real_0003`
  - `v107` 更不漏
  - `retention_minus_leak = v107`
  - 但 `target_capture` 比 `v81` 更弱
- `near_real_0006`
  - `v81` 仍是更好的 whole-utterance `retention_minus_leak`
- `near_real_0007`
  - whole-utterance 仍没有形成清晰正收益
  - `better_retention_minus_leak = tie`
- `near_real_0009`
  - absent suppression 基本 tie，且不触发 gate 失败

decoded means：

- `v81`
  - `target_capture_db = -11.4230`
  - `interference_capture_db = -33.9791`
  - `retention_minus_leak_db = 22.5235`
- `v107`
  - `target_capture_db = -12.8337`
  - `interference_capture_db = -35.0088`
  - `retention_minus_leak_db = 22.4012`

解释：

- whole-utterance 上，`v107` 的“更不漏”确实存在；
- 但 target retention 也更保守，所以整体只到 `overall_pass`，还没有强到自动升格。

### overlap-local

局部 benchmark：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107/overlap_local_benchmark/summary.json`

关键统计：

- `better_source_retention_candidate_counts`
  - `v81 = 3`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `v81 = 2`
  - `v107 = 2`
- `better_retention_minus_speech_leak_candidate_counts`
  - `v107 = 2`
  - `v81 = 1`
  - `not_applicable = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `tie = 2`
  - `v107 = 2`

分样本：

- `near_real_0003`
  - `better_retention_minus_speech_leak = v107`
  - `more_artifact_proxy_heavy = tie`
- `near_real_0006`
  - `better_retention_minus_speech_leak = v107`
  - 但 `more_artifact_proxy_heavy = v107`
- `near_real_0007`
  - `better_source_retention = v81`
  - `more_speech_interference_leaky = v107`
  - `better_retention_minus_speech_leak = v81`
  - `more_artifact_proxy_heavy = v107`
- `near_real_0009`
  - `more_speech_interference_leaky = v107`
  - artifact 基本 tie

decoded means：

- `v81`
  - `target_capture_db = -10.7559`
  - `speech_interference_capture_db = -39.1594`
  - `retention_minus_speech_leak_db = 25.2249`
  - `artifact_proxy_db = -2.2932`
- `v107`
  - `target_capture_db = -12.2078`
  - `speech_interference_capture_db = -39.6744`
  - `retention_minus_speech_leak_db = 25.0404`
  - `artifact_proxy_db = -2.0780`

解释：

- `v107` 对 `0003 / 0006` 这类 pure-speech present case 确实有局部正收益；
- 但 `0007` 这个真正的 `music_plus_speech` blocker 还没打穿；
- 而且 `v107` 在 `0007` 上又重新露出了：
  - 更差的 retention-minus-speech-leak
  - 更重的 artifact proxy

### bandwidth

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107/bandwidth_analysis/summary.json`
- `narrower_candidate_counts = tie: 4`

说明：

- 当前差异仍主要来自 leak / retention / artifact tradeoff；
- 不是频带明显变窄导致的假改善。

## 导包状态

non-blind：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107`

blind：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v107_blind`

说明：

- `v81 vs v107` 的 focused 听审包已经备好；
- 听审现已完成，结果见：
  - `reports/daily/2026-03-27_v81_vs_v107_listening_review.md`

## 听审解盲结果

最终结果：

- `v81 = 4`
- `v107 = 0`
- `tie = 0`

共同原因：

- 四条样本全部判为：
  - `less_artifact`
- blind 解盲后对应的是：
  - `v81` 一边倒胜出

artifact 主观记录：

- `v81`
  - 四条都为 `slight`
- `v107`
  - `0003 / 0006 / 0009 = slight`
  - `0007 = moderate`

解释：

- `v107` 不是像 `v106` 那样“自动有进步，但主观 tie”；
- 而是已经重新跨到可感知差异区间，
  且这次可感知差异全部对它不利；
- 这说明当前这版显式 speech-leak backstop，
  还没有把 automatic 上的收益转成可听层正收益。

## 本轮结论

`v107` 的结论是：

1. “从 `speech_plus_music` 选局部窗，但导出 `target + speech_only` 训练视图”这条实现路径是成立的。
2. 新 bundle 让显式 speech-leak 监督命中率明显提高，synthetic 三条固定验收也同步转强。
3. near-real whole-utterance gate 已通过，说明这版没有走回 `v103 / v105` 那种明显不安全状态。
4. 但 overlap-local 仍显示：
   - `0003 / 0006` 有收益
   - `0007` 依然是核心 blocker
   - 而且 `v107` 在 `0007` 上又重新出现更重 artifact proxy
5. blind 听审进一步确认：
   - `v81 = 4`
   - `v107 = 0`
   - `tie = 0`
   - 四条样本全部因为 artifact 更重而偏向 `v81`
6. 因此当前最准确的判断不是“已经解决 speech leak”，而是：
   - 显式 local speech-leak supervision 已经把问题收窄到了 `0007` 这一类 `music_plus_speech` hard-present preservation / artifact tradeoff
   - 但还没有把它变成可放行的候选

## 下一步

当前默认下一步不是立刻开 `v107+` 权重 sweep，而是：

1. `v107` 正式收口，不继续同结构小步 sweep。
2. 当前 blocker 已不再是“缺显式 speech-leak 监督”；
3. 下一轮机制应继续保留 local speech-leak proxy，但额外补：
   - `0007` 风格 `music_plus_speech` hard-present 局部窗的 preservation / artifact backstop
4. 不再默认回到：
   - teacher-overlap 对齐
   - 或同结构轻量权重 sweep
