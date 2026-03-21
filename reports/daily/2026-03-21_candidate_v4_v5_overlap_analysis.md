# 2026-03-21 `candidate_v4 / candidate_v5` overlap analysis

## 背景

上一轮已经明确：

- `candidate_v4_guardv66_by_v64`
  不是单语义 family；
- `candidate_v5_guardv67_negative`
  是从 `v66 > v67`
  的 negative search
  物化出来的
  一个粗诊断锚点；
- 但它只在口头上
  被描述为：
  - 横跨
    `candidate_v4 carve`
    与
    `candidate_v4 pruned`

这还不够。

当前真正要回答的是：

1. `candidate_v5`
   到底是不是
   `candidate_v4`
   外部的新 family；
2. 若不是，
   它在 `candidate_v4`
   内部到底对应哪一类 rows；
3. 哪些 rows
   是：
   - `v64 / v66`
     的分界信号
   - 哪些 rows
     是：
     `v66 / v67`
     的纯负向信号

## 本轮新增

已新增可复用脚本：

- `scripts/eval/analyze_proxy_family_overlap.py`

作用：

- 输入多份 focused proxy manifest；
- 自动按 membership
  拆成：
  - group summary
  - pairwise overlap
  - exclusive / intersection subset summary；
- 再 join
  compare per-sample metrics，
  输出每个 subset 的：
  - aggregate ranking
  - `candidate vs reference`
    平均差值
  - numeric metadata
    统计
  - row list

本轮实际产出：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`

分析输入：

- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_carve_lowtargettrans_highintshare.jsonl`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_pruned_lowtargettrans_highintshare.jsonl`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl`

## 结果

### 1. `candidate_v5` 在 val 上不是新族，而是 `candidate_v4` 的真子集

val union
仍是 `10` 条
`candidate_v4` rows：

- `val_000034`
- `val_000041`
- `val_000076`
- `val_000165`
- `val_000202`
- `val_000223`
- `val_000274`
- `val_000365`
- `val_000401`
- `val_000469`

其中 `candidate_v5`
只命中：

- `val_000076`
- `val_000274`
- `val_000469`

并且没有任何
`v5-only`
rows。

也就是：

- `candidate_v5`
  在 val 上
  不是 `candidate_v4`
  之外的新 family；
- 它只是
  `candidate_v4`
  内部跨分区的一小簇子集。

### 2. `candidate_v4` 当前可直接拆成四类 row

按
`candidate_v4 carve/pruned`
与 `candidate_v5`
交并后，
当前 val 上实际变成
四类：

1. `v4 carve only`
   - `val_000165`
   - `val_000223`
   - `val_000401`
2. `v4 carve ∩ v5`
   - `val_000469`
3. `v4 pruned only`
   - `val_000034`
   - `val_000041`
   - `val_000202`
   - `val_000365`
4. `v4 pruned ∩ v5`
   - `val_000076`
   - `val_000274`

这一步最重要，
因为它说明：

- 当前已经不该再把
  `candidate_v4`
  或 `candidate_v5`
  继续当成单语义 family
  去讨论。

### 3. `v4 carve only = {165,223,401}` 更像纯 `v67` 负向 rows，而不是 `v64 / v66` 边界负向

在这 `3` 条上：

- `v66 - v64 = +0.007515 dB`
- `v67 - v66 = -0.068223 dB`

也就是：

- 这组 rows
  对 `v66`
  relative to `v64`
  并不坏，
  反而还是小正向；
- 但 `v67`
  会明确把它们推坏。

因此更合理的解释是：

- `val_000165 / 000223 / 000401`
  更像
  “纯 `v67` negative”
  rows；
- 它们不该再和
  `v64 > v66`
  的 boundary-negative rows
  混写。

### 4. `val_000469` 是当前最硬的双信号 anchor

`v4 carve ∩ v5`
当前只有：

- `val_000469`

它同时满足：

- `v66 - v64 = -0.025435 dB`
- `v67 - v66 = -0.171768 dB`
- `v66 - v65 = +0.313288 dB`

也就是：

- 它同时处在：
  - `v64 > v66`
    这条 boundary-negative
  - `v66 > v67`
    这条 negative anchor
    的交叉点；
- 且 `v67`
  的回退幅度
  远大于其他 rows。

因此当前应把
`val_000469`
固定解释为：

- 硬双信号 anchor；
- 而不是仅仅
  “`candidate_v5`
   里的一条 row”。

### 5. `v4 pruned ∩ v5 = {076,274}` 不是稳定的 `v67` negative core

这两条在 aggregate 上：

- `v66 - v64 = -0.046281 dB`
- `v67 - v66 = +0.001157 dB`

样本级更直接：

- `val_000076`
  - `v67 - v66 = -0.012177 dB`
  - `v66 - v65 = -0.190807 dB`
- `val_000274`
  - `v67 - v66 = +0.014491 dB`
  - `v66 - v65 = -0.044429 dB`

这说明：

- `val_000076 / 000274`
  的主要作用
  更像
  `v64 > v66`
  的 boundary-negative tail；
- 它们并不是
  稳定纯净的
  `v66 > v67`
  negative core；
- 之前
  `candidate_v5`
  整体表现为
  `v66 > v67`
  的很大一部分 aggregate，
  实际是被
  `val_000469`
  这条强锚点带出来的。

### 6. `v4 pruned only = {034,041,202,365}` 当前是最像 keep rows 的子族

在这 `4` 条上：

- `v66 - v64 = +0.014094 dB`
- `v67 - v66 = +0.007854 dB`

也就是：

- 它们对
  `v64 -> v66`
  是正向；
- 对
  `v66 -> v67`
  也不是负向；
- 当前最像应保留的
  safe working rows。

## 当前结论

1. `candidate_v5`
   仍可保留为
   粗粒度 `v67 negative`
   诊断入口，
   但它本身不是单语义 family。
2. 当前 val 上更合理的职责切分应写成：
   - `val_000165 / 000223 / 000401`
     = 纯 `v67` negative rows
   - `val_000469`
     = 硬双信号 anchor
   - `val_000076 / 000274`
     = `v64 > v66`
       boundary-negative tail，
       不是稳定 `v67 negative` core
   - `val_000034 / 000041 / 000202 / 000365`
     = 当前最像 keep 的 working rows
3. 因而下一步若继续，
   默认不该再把
   全量 `candidate_v5`
   当成新的单独训练入口，
   也不该只写成
   “`candidate_v5`
    横跨 `v4`
    两边”。

## 当前默认下一步

默认顺序更新为：

1. 保留
   `candidate_v4`
   作为大框架，
   但内部至少按上述
   四类 row
   重新解释。
2. 若后续继续做 proxy，
   默认优先考虑：
   - `v4 carve only`
     作为更纯的
     `v67` negative rows
   - `val_000469`
     作为单独的
     硬双信号 anchor
   - 不把
     `v4 pruned ∩ v5`
     直接当成
     `v67 negative` 核心
3. 在这一步之前，
   仍不启动新训练。
