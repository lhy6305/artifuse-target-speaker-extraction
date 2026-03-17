# 2026-03-16 Subjective Follow-up And Hybrid Probe

## 背景

在首轮 blind A/B 试听中，用户已给出 3 个样本反馈：

- `val_000071`
  - 主观偏向：新模型 `ref_film_sisdr0005`
- `val_000089`
  - 主观偏向：旧模型 `legacy_stage2`
- `val_000090`
  - 主观偏向：旧模型 `legacy_stage2`

这三条反馈说明：

- 新模型不是“全面主观更好”
- 当前最需要重点盯的是：
  - `target_clean_plus_music`

## 当前客观与主观的关系

从 recipe 平均指标看，新模型仍然整体优于旧模型：

- `target_clean_speech`
  - legacy: `-11.877870 dB`
  - new: `-8.880672 dB`
  - delta: `+2.997199 dB`
- `target_clean_plus_music`
  - legacy: `-12.899197 dB`
  - new: `-10.319467 dB`
  - delta: `+2.579730 dB`

但主观反馈显示：

- `clean_plus_music` 中确实存在单样本回退点
- 而且这些回退点在“目标保留、干扰残留、毛刺感”几个维度上都值得重点复核

## 自动分析：试听包中的 clean_plus_music 单样本回退

当前试听包中被导出的 `target_clean_plus_music` 样本里，既有大幅提升点，也有明确回退点。

典型提升点：

- `val_000325`
  - `sisdr_delta_db`: `+20.454082`
- `val_000398`
  - `sisdr_delta_db`: `+15.213614`

典型回退点：

- `val_000186`
  - `sisdr_delta_db`: `-14.663211`
- `val_000466`
  - `sisdr_delta_db`: `-1.831463`
- `val_000089`
  - `sisdr_delta_db`: `-0.053754`
- `val_000090`
  - `sisdr_delta_db`: `-0.063712`

说明：

- 新模型在 `clean_plus_music` 上不是“均匀更强”
- 而是“平均更强，但分布更分化”

## 轻量 hybrid probe

为了验证“旧模型更保守、新模型更激进”的 tradeoff 是否可以在推理期折中，本轮做了一个不重训的轻量融合试探：

- `fused = legacy * (1 - alpha) + new * alpha`

测试了：

- `alpha = 0.25`
- `alpha = 0.5`
- `alpha = 0.75`

## hybrid probe 结果

### overall

| alpha_new | waveform_l1 | sisdr_db |
|---|---:|---:|
| `0.25` | `0.011349` | `-9.328331` |
| `0.5` | `0.011271` | `-8.753847` |
| `0.75` | `0.011226` | `-8.338542` |

对照：

- legacy stage2
  - `waveform_l1`: `0.013034`
  - `sisdr_db`: `-10.324091`
- ref_film_sisdr0005
  - `waveform_l1`: `0.012757`
  - `sisdr_db`: `-8.092701`

### clean_plus_music

| alpha_new | avg_l1 | avg_sisdr_db |
|---|---:|---:|
| `0.25` | `0.012081` | `-11.579489` |
| `0.5` | `0.012043` | `-10.857890` |
| `0.75` | `0.012056` | `-10.487696` |

对照：

- legacy: `-12.899197`
- new: `-10.319467`

## 当前判断

这个 hybrid probe 还不能当正式主线，但已经提供了一个有用信号：

1. 简单融合在客观指标上能明显优于旧模型。
2. `alpha = 0.75` 是当前三组里最有价值的折中点。
3. 它在 `clean_plus_music` 上没有超过纯新模型，但可能在主观上更稳。

大白话讲，就是：

- 如果后面听感继续表明“新模型有点过激，旧模型更稳”
- 那么推理期轻量融合是个值得认真准备的低成本退路

## 下一步

1. 继续优先收集 `clean_plus_music` 的主观听感样本。
2. 若后续主观反馈继续支持“旧模型更稳”，可把 `alpha=0.75` 附近的 hybrid 输出也做成试听包。
3. 在没有更多人工反馈前，hybrid probe 先只作为备选方向记录，不直接替换当前主候选。
