# 2026-03-16 Clean Plus Music Focus Fine-tune

## 背景

在首轮主观反馈后，当前最明确的回退风险集中在：

- `target_clean_plus_music`

此前已经完成：

- `legacy stage2`
- `ref_film + stft0.5 + sisdr0.0005`
- blind A/B 试听包
- 主观回退点与 lightweight hybrid probe 分析

但还没有做过“从当前主候选继续小步微调，专门盯 `clean_plus_music` 回退”的低成本验证。

## 本轮动作

### 1. 训练脚本补充 warm-start 能力

`scripts/train/train_stft_mask_baseline.py` 新增：

- `--init-checkpoint`

作用：

- 允许从已有 checkpoint 加载模型权重，再对新的训练 manifest 做继续训练。

当前实现行为：

- 只加载 `model_state_dict`
- 不恢复旧 optimizer 状态
- 更适合“继续微调 / 轻量 domain focus”
- 不是严格意义上的中断恢复训练

### 2. 定向微调实验

实验名：

- `baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_focus_ft1`

初始化 checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_ref_film_sisdr0005/best.pt`

训练清单：

- `data/synthetic/train_manifest_clean_plus_music_regression_focus_v1.jsonl`

训练配置：

- epochs: `3`
- batch size: `16`
- lr: `3e-4`
- conditioning: `ref_film`
- loss: `stft0.5 + sisdr0.0005`

训练时间：

- start: `2026-03-16T22:37:34`
- end: `2026-03-16T22:37:48`
- elapsed: `13.954 sec`

focused manifest 当前统计：

- 总样本数：`364`
- recipe 分布：
  - `target_clean_plus_music`: `207`
  - `target_clean_speech`: `47`
  - `target_hard_speech`: `41`
  - `target_hard_plus_music`: `29`
  - `target_only`: `14`
  - `target_music`: `13`
  - `target_singing_vocal`: `13`
- temporal pattern 分布：
  - `target_full`: `189`
  - `target_absent_tail`: `105`
  - `target_intermittent`: `36`
  - `target_absent_head`: `34`

对比默认 train manifest：

- 默认 train 为 `2048` 条
- 该 focused manifest 明显提高了 `target_clean_plus_music` 占比
- 同时保留了少量其他 recipe，避免完全退化成单一 recipe 微调

## 评估结果

评估输出：

- `reports/eval/baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_focus_ft1_eval/`

相对基线 `ref_film + sisdr0005` 的变化如下：

| metric | base | focused ft1 | delta |
|---|---:|---:|---:|
| `loss` | `0.024297` | `0.024138` | `-0.000158` |
| `waveform_l1` | `0.012757` | `0.012769` | `+0.000012` |
| `stft_l1` | `0.023078` | `0.022738` | `-0.000340` |
| `sisdr_db` | `-8.092701` | `-8.024813` | `+0.067887 dB` |

recipe 级别最关注的变化：

- `target_clean_plus_music`
  - `sisdr_db`: `-10.319467 -> -10.143199`
  - delta: `+0.176268 dB`
- `target_clean_speech`
  - delta: `+0.152179 dB`
- `target_hard_plus_music`
  - delta: `+0.036144 dB`
- `target_music`
  - delta: `+0.110005 dB`

当前判断：

1. 这次 focused fine-tune 不是空收益，客观指标方向总体偏正。
2. 但收益幅度偏小，远不足以仅凭平均指标就宣布主观回退已经解决。
3. `waveform_l1` 基本持平略差，说明它更像是“轻微偏移主候选”，不是明显的新主线。

大白话讲，就是：

- 这轮微调看起来没有把模型训坏
- 也确实往 `clean_plus_music` 方向推了一点
- 但推得不算大，仍然必须听

## Focused Blind A/B 试听包

为了直接核对“它有没有救回 clean_plus_music 的主观回退”，本轮额外导出：

- `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_focus_ft1_clean_plus_music_blind/`

对照对象：

- A: `ref_film_sisdr0005`
- B: `cpm_focus_ft1`

范围：

- 只看 `target_clean_plus_music`
- 候选样本总数：`95`
- 导出样本数：`8`

当前被选出的代表样本包括：

- 明显提升候选：
  - `val_000288`: `+3.464334 dB`
  - `val_000470`: `+3.002275 dB`
  - `val_000186`: `+1.945715 dB`
- 明显回退候选：
  - `val_000053`: `-2.138281 dB`
  - `val_000507`: `-1.451818 dB`
  - `val_000412`: `-1.345046 dB`
- 接近平手：
  - `val_000193`
  - `val_000400`

这说明：

- focused fine-tune 也不是“全样本统一更好”
- 它依然是“有些点明显救回，有些点反而回退”

## 当前结论

截至本报告为止，`clean_plus_music` 的针对性微调结论更新为：

1. `--init-checkpoint` 形式的低成本 focused fine-tune 已可稳定执行。
2. `cpm_focus_ft1` 在平均客观指标上略优于 `ref_film_sisdr0005`。
3. 但该提升仍然不足以跳过听感验证，尤其不能直接覆盖此前的主观回退结论。
4. 当前最合理的下一步不是继续盲扫更多 ft 版本，而是先完成这套 focused blind A/B 的人工听感。

## 当前风险

### 1. focused manifest 的生成过程还没有正式落盘

当前仓库里已经有：

- `data/synthetic/train_manifest_clean_plus_music_regression_focus_v1.jsonl`

但还没有找到对应的生成脚本或生成说明。

这会导致：

- 下次即使看到 manifest，也不容易知道它是怎么从默认 train manifest 派生出来的
- 若要复刻 `v2` 或做更严格对照，容易失去可重复性

### 2. 实验目录和总览文档已经出现轻微漂移

新实验和试听包产物已经存在，但如果不及时登记到总览文档，下次接手的人会只看到目录，不知道哪一个是当前主线之后的最新分支。

## 下一步建议

1. 优先听 `ab_listening_pack_ref_film_sisdr0005_vs_cpm_focus_ft1_clean_plus_music_blind/`。
2. 若主观上 focused ft1 明显更稳，再考虑：
   - 补一个更温和或更长一点的 `ft2`
   - 或把 focused ft1 作为 `clean_plus_music` 定向分支继续分析
3. 若主观上仍然回退明显，则应停止沿“只做 focused fine-tune”继续深挖，转回：
   - hybrid 推理退路
   - 或更明确的结构/损失约束
