# 2026-03-21 `candidate_v7` strict-core asset and overlap

## 背景

上一轮已经确认：

- 在真正的
  samplewise 全约束 strict
  口径下，
  当前不存在
  `3+ row`
  clean family；
- 当前只能稳定保留：
  - strict-all core
    `{val_000239, val_000430}`
  - 单点硬 anchor
    `val_000469`

但如果这一步只停留在日报结论，
下次继续仍会缺两样东西：

1. 没有现成的
   strict-core selector 资产；
2. 没有正式写清：
   strict core
   与
   `candidate_v6`
   / `dualanchor`
   到底是什么关系。

## 本轮新增资产

### 1. strict-core focused manifest

已物化：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl = 0`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl = 2`

val rows：

- `val_000239`
- `val_000430`

对应输入 sample-id 清单：

- `tmp/candidate_v7_strictall_core_val_ids.txt`

### 2. 标准 selector 资产

已生成：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_val.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_all.txt`

摘要：

- `tmp/candidate_v7_strictall_core_selector_assets_summary.json`

当前这套资产的定位应固定为：

- strict-core 诊断 selector；
- 不是新的训练入口。

## overlap 诊断

本轮新增 focused overlap summary：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`

分析对象：

- `strict_core`
- `candidate_v6`
- `dualanchor`

## 结果

### 1. 当前 union 已固定成 `5` 条 row

val union 为：

- `val_000165`
- `val_000239`
- `val_000331`
- `val_000430`
- `val_000469`

membership subset
当前正式固定为：

- `candidate_v6 only`
  - `val_000165`
  - `val_000331`
- `strict_core only`
  - `val_000239`
- `candidate_v6 ∩ strict_core`
  - `val_000430`
- `dualanchor only`
  - `val_000469`

这说明：

- strict core
  与
  `dualanchor`
  完全解耦；
- `candidate_v6`
  也不是 strict core
  的简单超集或子集。

### 2. `strict_core only = val_000239` 是新的 row-level 核心，但不是旧 pure-negative 那套低 transient 语义

`val_000239`
当前数值为：

- `target_transient_presence_minus_mid_db_mean = +0.631591`
- `interference_transient_presence_minus_mid_db_mean = +1.396928`
- `target_interference_logspec_cosine = 0.706210`

方向上却仍然逐条满足：

- `v66 > v64 = +0.001747 dB`
- `v66 > v65 = +0.048344 dB`
- `v66 > v67 = +0.087762 dB`
- `v20 > v24 = +0.023589 dB`

这说明：

- `val_000239`
  不是
  `candidate_v6`
  那种
  low-target-transient /
  low-interference-transient
  row；
- 它是一个行为上干净、
  但语义上更接近旧
  reverse-guardrail /
  anchor family
  的 strict-core row。

### 3. `candidate_v6 ∩ strict_core = val_000430` 继续是最硬公共核心

`val_000430`
仍然同时满足：

- `v66 > v64 = +0.019306 dB`
- `v66 > v65 = +0.464066 dB`
- `v66 > v67 = +0.133390 dB`
- `v20 > v24 = +0.097162 dB`

并且它的数值形态仍是：

- very low target transient
- low interference transient
- high similarity

所以这条 row
当前仍应固定解释为：

- strict-core 与 aggregate pure-negative
  的公共核心锚点。

### 4. `candidate_v6 only = {165,331}` 继续只应解释为 carry-over / partial-support rows

在
`compare_v19_vs_v66`
侧，
这两条不会同时逐条满足
全部 guard：

- `val_000165`
  会在
  `v66 > v64`
  与
  `v66 > v65`
  上掉线；
- `val_000331`
  会在
  `v66 > v65`
  上掉线。

因此：

- 它们可以继续留在
  `candidate_v6`
  这个 aggregate family
  里；
- 但不应再写成
  strict-core rows。

### 5. `dualanchor only = val_000469` 继续保留为单点边界锚点

`val_000469`
当前仍是：

- `v64 > v66`
- `v66 > v67`
  的硬双信号 anchor

但它不满足：

- `v66 > v64`
- `v20 > v24`

所以它继续属于：

- 边界锚点
  而不是 strict-all core。

## 当前结论

1. strict core
   现已具备可复用 selector 资产，
   后续不需要再手抄 sample ids。
2. 当前应把三类东西明确分开：
   - `candidate_v6`
     = aggregate pure-negative working family
   - `strict_core`
     = row-level strict-all core
   - `dualanchor`
     = 单点边界锚点
3. 更关键的新事实是：
   - strict core
     虽然行为上干净，
     但并不被一组简单的
     metadata 语义统一支配；
   - `239`
     与
     `430`
     在 transient 形态上
     明显不同，
     只是行为排序上
     同时过关。

## 当前默认下一步

默认顺序更新为：

1. 若继续做 proxy 搜索，
   不要把 strict core
   当成已经找到
   单语义 metadata family。
2. 下一步更值得做的是：
   - 沿 strict core
     去找新的行为同族；
   - 但默认不要只沿
     `candidate_v6`
     那套
     low-transient 口径
     继续收紧。
3. 在出现新的
   `3+ row`
   strict-all family
   之前，
   仍不启动新训练。
