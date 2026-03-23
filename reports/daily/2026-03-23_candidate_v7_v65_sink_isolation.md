# 2026-03-23 `candidate_v7` `v65` sink isolation

## 背景

上一轮已经把：

- `train_001745`
- `train_001543`
- `train_000664`

压成 post-entry branch divergence split，
并确认：

- `train_000664`
  是
  `v64 crossed`
  shared shelf
- `train_001543`
  是
  `v65 sink`
- `train_001745`
  是
  `v64 pocket`

因此当前最窄的问题
已经不再是：

- `001745`
  为什么比别人更深

而是：

- 从
  `train_000664`
  到
  `train_001543`
  这一跳里，
  到底是什么
  把
  `v66 > v65`
  从刚好为正
  推成显著为负，
  同时几乎不改写
  `v66 > v64`

换成大白话就是：

- 这一步要单独隔离：
  - “只让 `v65` 掉下去”
  这条支路

## 本轮做法

这一步不再增加新脚本，
直接复用：

- `scripts/eval/analyze_proxy_group_split.py`

只保留两条 singleton：

- `post_entry_v65_deeper_than_v64`
  - `train_001543`
- `v64_only_crossed_unexpected`
  - `train_000664`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_isolation/summary.json`

字段仍然固定在：

- target / interference transient
- cosine
- target / reference duration
- gain / overlap offset
- 以及
  `v20 / v24 / v64 / v65 / v66 / v67`
  的 samplewise ranking

## 结果

### 1. `train_001543` 相对 `train_000664` 的关键变化，几乎完全是 `v66 > v65` 单边翻负；`v66 > v64` 基本不动

两条 row
的关键 gap
分别是：

- `train_000664`
  - `v66 - v64 = -0.009173 dB`
  - `v66 - v65 = +0.004478 dB`
  - ranking：
    - `v67 > v64 > v66 > v65`
- `train_001543`
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`
  - ranking：
    - `v67 > v65 > v64 > v66`

pairwise delta
显示：

- `v66 - v64`
  只变化：
  - `+0.000345 dB`
  几乎等于不动
- 但
  `v66 - v65`
  额外下掉：
  - `0.118462 dB`

这说明：

- `001543`
  相对
  `000664`
  的跃迁
  不是：
  - `v64`
    进一步继续塌
- 而是：
  - `v65`
    这一侧
    单边继续下沉

所以这对样本
可以正式当作：

- `v65 sink`
  的最干净 isolation pair

### 2. 这一步同步出现的 metadata 变化，不是“更长 reference”那一支，而是更短 reference、 更早 overlap、 更弱 gain、 更高双侧 transient share

`001543 - 000664`
的 metadata delta
为：

- `reference_duration_sec = -1.02`
  说明
  `001543`
  reference 更短
- `interference_start_offset_sec = -0.098`
  说明
  `001543`
  overlap 更早
- `interference_layers.0.gain_db = -4.301`
  说明
  `001543`
  gain 更弱
- `target_transient_presence_minus_mid_db_mean = +1.901528`
  说明
  `001543`
  target transient
  更高
- `target_transient_presence_share_mean = +0.057351`
  说明
  `001543`
  target transient share
  更高
- `interference_transient_presence_minus_mid_db_mean = +1.463378`
  说明
  `001543`
  interference transient
  更高
- `interference_transient_presence_share_mean = +0.041330`
  说明
  `001543`
  interference transient share
  更高
- `target_interference_logspec_cosine = -0.023421`
  说明
  `001543`
  cosine 更低

因此在当前这对 isolation pair
里，
与
`v65`
继续翻负
同步出现的
是这样一组组合：

- 更短 reference
- 更早 overlap
- 更弱 gain
- 更高 target / interference transient
- 更低 cosine

### 3. 这组 `v65 sink` 组合和 `train_001745` 的 `v64 pocket` 不是同一方向，所以不能再混写成“更深 drift”

上一轮已经看到：

- `train_001745`
  相对
  `train_000664`
  也有：
  - 更早 overlap
  - 更高 transient share

但它同时还有：

- `reference_duration_sec` 基本不变
- `v66 - v65`
  只再下掉
  `0.006385 dB`
- `v66 - v64`
  反而更深
  `0.018296 dB`

这说明：

- “更早 overlap + 更高 transient”
  还不够定义
  `v65 sink`
- 真正把
  `000664`
  推成
  `001543`
  的，
  还包括：
  - 更短 reference
  - 更弱 gain
  - 更低 cosine

所以当前应明确分开写：

- `001543`
  代表：
  - `v65 sink`
- `001745`
  代表：
  - `v64 pocket`

它们不是：

- 同一条 drift
  上的不同深度

### 4. 当前最窄主结论已经可以固定成：如果想隔离“谁在推动 `v66 > v65` 单边翻负”，就应该优先看 `001543 / 000664`，而不是把 `001745` 再混回来

对当前主线来说，
最重要的不是
再去问：

- `001745`
  为什么特殊

而是先把
这条更干净的
`v65 sink`
支路
固定住：

- 哪些组合
  只会推动
  `v66 > v65`
  继续翻负
- 同时
  几乎不改变
  `v66 > v64`

当前最好的 pair
就是：

- `train_001543`
- `train_000664`

## 结论

1. `train_001543` 相对 `train_000664` 的跃迁，本质上是一次 `v65 sink`：`v66 - v64` 基本不动，真正翻负的是 `v66 - v65`。
2. 与这次 `v65 sink` 同步出现的 clean 组合是：
   - 更短 reference
   - 更早 overlap
   - 更弱 gain
   - 更高 target / interference transient
   - 更低 cosine
3. 当前最合理的下一步，应继续只围绕 `train_001543 / train_000664`，检查这组组合里哪一部分更接近真正的 `v65` 单边翻负触发器，而不要再把 `train_001745` 混回同一条分析线。 
