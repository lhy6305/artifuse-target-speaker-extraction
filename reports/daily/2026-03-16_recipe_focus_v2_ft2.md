# 2026-03-16 Recipe Focus V2 FT2

## 背景

在没有试听条件的前提下，上一轮已经完成：

- `cpm_focus_ft1`
- focused manifest 的可复现化
- `recipe_focus_v2` manifest
- `base vs ft1` 的自动对比

当时的下一步判断是：

- 不继续盲堆很多近邻分支
- 先做一个变量更干净的受控 `ft2`

本轮采取的控制方式是：

1. warm-start 仍然从同一个 base checkpoint 开始；
2. 训练预算与 `ft1` 保持一致；
3. 只替换成可复现的 focused manifest。

## 实验配置

实验名：

- `baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_recipe_focus_v2_ft2`

初始化 checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_ref_film_sisdr0005/best.pt`

训练 manifest：

- `data/synthetic/train_manifest_clean_plus_music_recipe_focus_v2.jsonl`

训练参数：

- epochs: `3`
- batch size: `16`
- lr: `3e-4`
- conditioning: `ref_film`
- loss: `stft0.5 + sisdr0.0005`

训练时间：

- start: `2026-03-16T23:19:53`
- end: `2026-03-16T23:20:05`
- elapsed: `11.992 sec`

## 标准评估结果

评估输出：

- `reports/eval/baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_recipe_focus_v2_ft2_eval/`

整体指标：

| checkpoint | loss | waveform_l1 | stft_l1 | sisdr_db |
|---|---:|---:|---:|---:|
| `base` | `0.024297` | `0.012757` | `0.023078` | `-8.092701` |
| `ft1` | `0.024138` | `0.012769` | `0.022738` | `-8.024813` |
| `ft2` | `0.024181` | `0.012721` | `0.022920` | `-7.947635` |

相对 `base`：

- `loss`: `-0.000115`
- `waveform_l1`: `-0.000036`
- `stft_l1`: `-0.000158`
- `sisdr_db`: `+0.145066 dB`

相对 `ft1`：

- `loss`: `+0.000043`
- `waveform_l1`: `-0.000048`
- `stft_l1`: `+0.000182`
- `sisdr_db`: `+0.077178 dB`

当前直观结论：

- `ft2` 不是四项全胜；
- 但它在最关心的 `sisdr_db` 和 `waveform_l1` 上同时优于 `ft1`；
- 相比 `base` 也更像是“分布上更稳的正收益”，而不只是均值小涨。

## 自动对比：base vs ft2

输出目录：

- `reports/eval/compare_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2/`

整体统计：

- `avg_sisdr_delta_db`: `+0.146620`
- improved: `229`
- regressed: `108`
- near tie: `175`

这比 `ft1` 更关键的地方在于：

- `ft1` 相对 `base` 仍然是“improved 和 regressed 数量很接近”
- `ft2` 则已经变成：
  - 明显更多样本改善
  - 回退样本数量明显少于改善样本

大白话讲，就是：

- `ft2` 开始更像一个“真有多数样本收益”的分支
- 不再只是“平均值略好，但赚赔混在一起差不多”

## 关键 recipe

### `target_clean_plus_music`

| checkpoint | avg_sisdr_db |
|---|---:|
| `base` | `-10.319467` |
| `ft1` | `-10.143199` |
| `ft2` | `-10.033389` |

相对 `base`：

- `avg_sisdr_delta_db`: `+0.310862`
- improved: `54`
- regressed: `23`
- near tie: `18`

相对 `ft1`：

- `avg_sisdr_delta_db`: `+0.133700`
- improved: `46`
- regressed: `22`

当前判断：

- `ft2` 确实把 `clean_plus_music` 又往前推了一步
- 而且这一步不是只靠极少数异常大提升样本撑起来的

### `target_hard_speech`

| checkpoint | avg_sisdr_db |
|---|---:|
| `base` | `-7.002237` |
| `ft1` | `-7.093016` |
| `ft2` | `-7.016520` |

相对 `base`：

- `avg_sisdr_delta_db`: `-0.020201`
- improved: `29`
- regressed: `21`
- near tie: `50`

相对 `ft1`：

- `avg_sisdr_delta_db`: `+0.080028`
- improved: `32`
- regressed: `5`

当前判断：

- `ft1` 的 `hard_speech` 退化在 `ft2` 上基本被收回了大半
- 虽然还没有做到明确优于 `base`
- 但已经从“明显副作用”降到了“接近持平、略偏负”的程度

### `target_clean_speech`

| checkpoint | avg_sisdr_db |
|---|---:|
| `base` | `-8.880672` |
| `ft1` | `-8.728493` |
| `ft2` | `-8.657719` |

当前判断：

- `ft2` 也继续改善了 `clean_speech`
- 说明它不是只会在 `clean_plus_music` 单点上冒险

## temporal pattern 观察

`base vs ft2` 的 pattern 分组结果：

- `target_absent_tail`: `+0.220574 dB`
- `target_full`: `+0.147204 dB`
- `target_intermittent`: `+0.123944 dB`
- `target_absent_head`: `+0.079939 dB`

这和 `ft1` 的一个重要区别是：

- `ft1` 在 pattern 上仍然有更明显的分化感
- `ft2` 则四种 pattern 都是正向或接近正向

这也是为什么 `ft2` 更像一个“分布上更健康”的分支。

## base vs ft2 的后续试听包

虽然当前还不能试听，但本轮已经提前导出：

- `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_clean_plus_music_blind/`

这样后续一旦有试听条件，不需要再重新导包。

## 当前结论

截至本轮，focused 分支的客观判断更新为：

1. `ft2` 明显优于 `ft1`。
2. `ft2` 相对 `base` 已经表现出更像“多数样本收益”的分布，而不是只有平均值小幅占优。
3. `clean_plus_music` 收益进一步扩大。
4. `hard_speech` 的副作用显著小于 `ft1`，当前已经接近收回。

如果只看客观证据，当前 focused 分支的排序已经可以更新为：

1. `cpm_recipe_focus_v2_ft2`
2. `cpm_focus_ft1`
3. `base`

但是否把它升成新的主候选，仍然最好等后续试听再定。

## 下一步建议

1. 在没有试听条件时，先把 `cpm_recipe_focus_v2_ft2` 视作新的“focused 客观最优分支”。
2. 暂时不要再继续连开更多近邻 `ft3 / ft4`，先给当前分支留出后续听感验证入口。
3. 若还要继续纯客观推进，优先考虑：
   - 只做一轮 very small LR 的保守 `ft3`
   - 或围绕 `target_absent_head` 的回退点做更针对性的 manifest 调整
   但这两件事都应建立在明确新假设之上，而不是继续顺手试。
