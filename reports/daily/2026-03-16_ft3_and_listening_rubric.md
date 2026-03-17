# 2026-03-16 FT3 And Listening Rubric

## 背景

在 `cpm_recipe_focus_v2_ft2` 已经成为 focused 分支客观最优点后，本轮额外做了两件事：

1. 再向前试一个 very small `ft3`，确认是否还有低风险增益空间。
2. 把 blind A/B 听评表从松散备注改成结构化打标，便于后续统一判断。

## 小步 `ft3`

实验名：

- `baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_recipe_focus_v2_ft3`

配置：

- init checkpoint：`cpm_recipe_focus_v2_ft2`
- train manifest：`train_manifest_clean_plus_music_recipe_focus_v2.jsonl`
- epochs：`2`
- lr：`1e-4`

整体指标：

| checkpoint | loss | waveform_l1 | stft_l1 | sisdr_db |
|---|---:|---:|---:|---:|
| `ft2` | `0.024181` | `0.012721` | `0.022920` | `-7.947635` |
| `ft3` | `0.024127` | `0.012668` | `0.022919` | `-7.926801` |

单看均值：

- `ft3` 比 `ft2` 略好一点点

但自动逐样本对比显示：

- `avg_sisdr_delta_db`: `+0.016599`
- improved: `114`
- regressed: `105`

当前判断：

1. `ft3` 没有训坏。
2. 但它没有给出足够强的新证据，整体更像是接近平台区的轻微波动。
3. 因此当前应把 `ft3` 视作“可记录但不主推”的近邻点，而不是继续往下连开更多版本。

大白话讲，就是：

- 它可能有一点点好
- 但好得不够硬
- 不值得现在继续顺着这个方向往下滚很多版

## 听评标准改造

已更新：

- `scripts/eval/export_ab_listening_pack.py`
- `scripts/eval/export_ab_inference_from_manifest.py`

当前 blind pack 会额外导出：

- `listening_sheet.csv`
- `listening_rubric.json`

新的听评表字段核心改成：

1. `better_output`
   - `output_a / output_b / tie / uncertain`
2. 标签强度
   - `output_a_source_retention`
   - `output_b_source_retention`
   - `output_a_interference_leak`
   - `output_b_interference_leak`
   - `output_a_volume_fluctuation`
   - `output_b_volume_fluctuation`
   - `output_a_artifact`
   - `output_b_artifact`
3. `decision_tags`
4. `note`

标度：

- `source_retention`
  - `excellent / good / fair / weak / lost`
- 其余问题项：
  - `none / slight / moderate / heavy / extreme`

推荐的 `decision_tags` 例子：

- `better_source_retention`
- `less_interference_leak`
- `steadier_volume`
- `less_artifact`

这套标准的目的就是：

- 先选哪个好
- 再把“为什么好/为什么差”拆成结构化标签
- 避免后面只留下很散的主观形容词

## 下一步试听范围

当前建议先听两包，不再把范围摊太大。

### 1. 主包：确认收益是否真的可听

- `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_clean_plus_music_blind/`

范围：

- `base` vs `ft2`
- 只看 `target_clean_plus_music`
- `8` 条样本

这包的作用是：

- 直接验证 focused 分支最想解决的问题，到底有没有主观净收益

### 2. guardrail 包：确认副作用是否可接受

- `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_guardrail_blind/`

范围：

- `base` vs `ft2`
- `target_clean_speech + target_hard_speech`
- `10` 条样本

这包的作用是：

- 不是看“主收益场景”
- 而是看 focused 分支会不会在 guardrail 场景上伤人

## 当前结论

截至本轮：

1. `ft2` 仍是 focused 分支里最值得保留的客观点。
2. `ft3` 没有形成足够强的新优势，当前不继续沿这个方向盲开更多版本。
3. 盲测包已经整理成结构化听评标准，后续一旦能试听，可以直接开始记录。

## 后续执行顺序

后续一旦具备试听条件，建议严格按这个顺序：

1. 先听 `clean_plus_music` 主包。
2. 再听 `guardrail` 包。
3. 每条样本都先填：
   - `better_output`
   - 再填四类标签强度
4. 最后才写自由 `note`。
