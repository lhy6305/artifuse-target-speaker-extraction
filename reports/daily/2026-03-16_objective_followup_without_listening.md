# 2026-03-16 Objective Follow-up Without Listening

## 背景

当前没有试听条件，因此这轮推进目标改成两件事：

1. 先把 `clean_plus_music` focused fine-tune 的可复现性补上。
2. 在不做主观判断的前提下，把 `ref_film_sisdr0005` 和 `cpm_focus_ft1` 的客观差异看细一点。

大白话讲，就是：

- 现在先不硬猜“听起来谁更好”
- 先把以后还能继续做实验、还能看懂差异这两件事补扎实

## 新增工具

### 1. focused manifest 生成脚本

新增：

- `scripts/data/build_recipe_focused_manifest.py`

作用：

- 从现有 synthetic train manifest 中，按显式 `recipe=count` 配额，生成可复现的 focused manifest。
- 相比之前只留下一个 `train_manifest_clean_plus_music_regression_focus_v1.jsonl` 产物，这个脚本至少把“未来怎么稳定再做一版 focused manifest”补成了正式流程。

### 2. 双 checkpoint 自动对比脚本

新增：

- `scripts/eval/compare_checkpoints_on_manifest.py`

作用：

- 在同一个 manifest 上逐样本比较两个 checkpoint；
- 输出：
  - overall 汇总
  - recipe 分组
  - temporal pattern 分组
  - target present ratio bucket 分组
  - top improvements / regressions / near ties

这一步的重要性在于：

- 没有试听时，至少能更清楚地知道“新分支到底是在什么分布上赚了、又在什么分布上赔了”。

## 新生成的可复现 focused manifest

本轮额外生成：

- `data/synthetic/train_manifest_clean_plus_music_recipe_focus_v2.jsonl`

生成脚本：

- `scripts/data/build_recipe_focused_manifest.py`

当前 recipe 配额直接对齐到旧 `v1` 的规模：

- `target_clean_plus_music=207`
- `target_clean_speech=47`
- `target_hard_speech=41`
- `target_hard_plus_music=29`
- `target_only=14`
- `target_music=13`
- `target_singing_vocal=13`

结果：

- 总样本数：`364`
- recipe 分布与 `v1` 对齐
- temporal pattern 分布为：
  - `target_full`: `166`
  - `target_absent_tail`: `71`
  - `target_absent_head`: `66`
  - `target_intermittent`: `61`

当前意义：

1. 它不是对旧 `v1` 的历史精确复刻。
2. 但它已经是一个“相同预算、来源可复现、以后还能继续做 `ft2`”的正式替代基线。

## 自动对比结果

### 1. 全验证集对比

输出目录：

- `reports/eval/compare_ref_film_sisdr0005_vs_cpm_focus_ft1/`

整体结果：

- 样本数：`512`
- `avg_sisdr_delta_db`: `+0.062616`
- meaningful improvement（> `0.1 dB`）：`142`
- meaningful regression（< `-0.1 dB`）：`149`
- near ties：`221`

说明：

- `cpm_focus_ft1` 的平均值略优
- 但并不是“多数样本统一变好”
- 更像是：
  - 一部分样本明显赚到
  - 一部分样本也明显赔掉
  - 还有相当多样本几乎没区别

### 2. recipe 级别观察

对当前最关键的 recipe：

- `target_clean_plus_music`
  - `avg_sisdr_delta_db`: `+0.177162`
  - improved: `41`
  - regressed: `36`
  - near tie: `18`

- `target_clean_speech`
  - `avg_sisdr_delta_db`: `+0.154943`

明显变差的 recipe：

- `target_hard_speech`
  - `avg_sisdr_delta_db`: `-0.100230`

弱退化：

- `target_singing_vocal`
  - `avg_sisdr_delta_db`: `-0.051889`

这说明：

- focused fine-tune 不只是改了 `clean_plus_music`
- 它顺带也把 `clean_speech` 往上推了一点
- 但代价是 `hard_speech` 方向略受损

### 3. temporal pattern 级别观察

在 `target_clean_plus_music` 聚焦对比里：

- `target_absent_tail`
  - `avg_sisdr_delta_db`: `+0.346226`
- `target_full`
  - `avg_sisdr_delta_db`: `+0.242714`
- `target_intermittent`
  - `avg_sisdr_delta_db`: `-0.033209`

说明：

- 这轮 focused fine-tune 更像是在：
  - `full`
  - `absent_tail`
  上更有帮助
- 但对 `intermittent` 并没有带来明确收益

### 4. target present ratio 级别观察

`target_clean_plus_music` 聚焦对比里：

- `ratio_0.6_0.8`
  - `avg_sisdr_delta_db`: `+0.169482`
- `ratio_ge_0.95`
  - `avg_sisdr_delta_db`: `+0.242714`
- `ratio_0.8_0.95`
  - `avg_sisdr_delta_db`: `-0.253706`

说明：

- 当前最不稳的是“中高占空比但又不是全程存在”的那一小段区间
- 这和前面 `absent_tail / intermittent` 的分化是相互呼应的

## 代表样本

### `clean_plus_music` 中明显改善

- `val_000288`: `+3.464334 dB`
- `val_000470`: `+3.002275 dB`
- `val_000186`: `+1.945715 dB`
- `val_000089`: `+1.525942 dB`

注意：

- `val_000089` 之前的主观反馈偏向旧模型
- 但当前 `cpm_focus_ft1` 相对 `ref_film_sisdr0005` 在这个点上客观是提升的

这说明：

- focused fine-tune 有可能确实救回了个别旧的主观回退点
- 但因为现在不能听，不能提前宣布已经救回

### `clean_plus_music` 中明显回退

- `val_000053`: `-2.138281 dB`
- `val_000507`: `-1.451818 dB`
- `val_000412`: `-1.345046 dB`
- `val_000146`: `-1.258663 dB`
- `val_000134`: `-1.200968 dB`

当前直观印象：

- 回退点明显集中在：
  - `target_absent_head`
  - 一部分 `target_intermittent`
  - 以及个别 `target_full`

## 当前结论

在没有试听条件的情况下，这轮客观补充分析给出的结论是：

1. 可以继续推进，但应以“提高可复现性 + 缩小问题范围”为主，而不是继续盲猜主观优劣。
2. `cpm_focus_ft1` 的平均客观收益是真实存在的，不是噪声。
3. 但它仍然是明显的“有赢有输”分支，不具备直接接管主线的证据。
4. `hard_speech` 的客观退化值得盯住，说明 focused fine-tune 已经开始出现侧向代价。
5. 新的 `recipe_focus_v2` manifest 可作为后续正式 focused 实验的更稳起点。

## 下一步建议

在仍然没有试听条件时，优先级建议改成：

1. 若继续做 focused fine-tune，优先基于：
   - `data/synthetic/train_manifest_clean_plus_music_recipe_focus_v2.jsonl`
   而不是继续依赖历史来源不明的 `regression_focus_v1`
2. 若继续跑 `ft2`，要同时评估：
   - overall
   - `clean_plus_music`
   - `hard_speech`
   避免只看局部收益
3. 若短期内仍无法试听，不建议连续堆很多新分支；先把实验节奏控制在“一个清晰假设 + 一个可复现 manifest + 一轮对比”。
