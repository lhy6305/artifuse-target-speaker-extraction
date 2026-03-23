# 2026-03-23 `candidate_v7` post-entry branch divergence split

## 背景

上一轮已经确认：

- `train_001745`
  在当前窄 ring
  里没有第二条
  真正的
  `both-crossed + v64-deeper`
  同型 row；
- 最像它的假近邻
  主要裂成两类：
  - `train_001543`
    这类
    `both-crossed + v65-deeper`
  - `train_000664`
    这类
    `v64-only crossed`

因此当前最窄的问题
就变成：

- 为什么这三条
  都已经碰到
  `v64`
  边界，
  却会分流成
  两条不同的 drift 支路；
- 更直白一点，
  就是：
  - 为什么
    `train_001543`
    会把
    `v65`
    压得更深；
  - 而
    `train_001745`
    会把
    `v64`
    留成更深的负 gap

## 本轮做法

这一步不再加新搜索，
只把三条 singleton
直接并排做 group split：

- `train_001745`
  - `post_entry_v64_deeper_than_v65`
- `train_001543`
  - `post_entry_v65_deeper_than_v64`
- `train_000664`
  - `v64_only_crossed_unexpected`

新增两个 singleton 资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_post_entry_v65_deeper_than_v64_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_v64_only_crossed_unexpected_train.txt`

复用：

- `scripts/eval/analyze_proxy_group_split.py`

输出：

- `reports/eval/active_targetfull_clean_failboth_post_entry_branch_divergence_split/summary.json`

字段仍限定在：

- target / interference transient
- cosine
- target / reference duration
- gain / overlap offset
- 以及
  `v20 / v24 / v64 / v65 / v66 / v67`
  的 samplewise ranking

## 结果

### 1. 这三条不是沿一条“越来越深”的单线排队，而是从同一个 `v64 crossed` 台阶分叉成两支：`v65 sink` 和 `v64 pocket`

三条 row
的关键 gap
分别是：

- `train_001745`
  - `v66 - v64 = -0.027470 dB`
  - `v66 - v65 = -0.001907 dB`
  - ranking：
    - `v67 > v64 > v65 > v66`
- `train_001543`
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`
  - ranking：
    - `v67 > v65 > v64 > v66`
- `train_000664`
  - `v66 - v64 = -0.009173 dB`
  - `v66 - v65 = +0.004478 dB`
  - ranking：
    - `v67 > v64 > v66 > v65`

所以这三者的关系
不是：

- `000664 -> 001543 -> 001745`
  一路同向加深

而更像：

- 先到达：
  - `v64`
    已经先翻负
    的 shared shelf
- 再从这里分叉成：
  - `v65`
    继续下沉的
    `v65 sink`
  - 和
    `v64`
    保持更深负 gap
    的
    `v64 pocket`

### 2. `train_001543` 相对 `train_000664` 的变化几乎不动 `v66 - v64`，真正被推下去的是 `v66 - v65`

`001543 - 000664`
的 pairwise delta
显示：

- `v66 - v64`
  只变化：
  - `+0.000345 dB`
  基本可视为不动
- 但
  `v66 - v65`
  额外下掉：
  - `0.118462 dB`

这说明：

- `train_001543`
  不是在
  `v64`
  这一侧更深；
- 它只是把
  已经踩到的
  `v64 crossed`
  台阶
  继续转成：
  - `v65`
    更深的
    post-entry sink

和这一步同步出现的
metadata 组合
是：

- `reference_duration_sec = -1.02`
  说明
  `001543`
  reference 更短
- `interference_start_offset_sec = -0.098`
  说明
  `001543`
  overlap 更早
- `interference_gain_db = -4.301`
  说明
  `001543`
  gain 更弱
- `target_transient_share = +0.057351`
  和
  `interference_transient_share = +0.041330`
  说明
  `001543`
  双侧 transient share
  更高

当前最稳的解释是：

- `001543`
  这条支路
  更像是在
  已经触到
  `v64`
  边界之后，
  又把
  `v65`
  单边继续拉下去；
- 它和
  `001745`
  不是同一种
  deeper geometry

### 3. `train_001745` 相对 `train_000664` 的额外变化很小，但它同时把 `v66 - v64` 再压深一点，并把 `v66 - v65` 刚好推过零线

`001745 - 000664`
的 pairwise delta
显示：

- `v66 - v64`
  额外下掉：
  - `0.018296 dB`
- `v66 - v65`
  只再下掉：
  - `0.006385 dB`

也就是说：

- 从
  `v64-only crossed`
  走到
  `both-crossed + v64-deeper`
  所需的额外 margin
  其实很小；
- 关键不是
  `v65`
  被大幅压穿，
  而是：
  - `v65`
    刚刚越零
  - 同时
    `v64`
    保持更深负 gap

与这一步同步出现的
metadata 组合
是：

- `interference_start_offset_sec = -0.236`
  说明
  `001745`
  overlap 更早
- `interference_gain_db = -1.945`
  说明
  `001745`
  gain 更弱
- `target_transient_share = +0.085304`
  和
  `interference_transient_share = +0.086691`
  说明
  `001745`
  双侧 transient share
  明显更高
- `reference_duration_sec = +0.03`
  基本不变

因此：

- `001745`
  相对
  `000664`
  不是长出一个全新 family；
- 更像是在同一个
  `v64 crossed`
  shelf 上，
  又多吃到一小步：
  - 更早 overlap
  - 更弱 gain
  - 更高双侧 transient share
  于是把
  `v66 > v65`
  也刚好推到负区

### 4. `train_001745` 相对 `train_001543` 的真正差异不是“更深 drift”，而是负 gap 重心从 `v65` 挪回了 `v64`

`001745 - 001543`
的 pairwise delta
显示：

- `v66 - v64`
  更负：
  - `0.018641 dB`
- 但
  `v66 - v65`
  反而更高：
  - `0.112077 dB`

所以：

- `001745`
  并不是
  `001543`
  的“更深版”
- 两者的关键差异
  是负 gap
  落在哪一侧：
  - `001543`
    深在
    `v65`
  - `001745`
    深在
    `v64`

和这个分叉同步出现的
metadata 组合
是：

- `reference_duration_sec = +1.05`
  说明
  `001745`
  reference 更长
- `interference_start_offset_sec = -0.138`
  说明
  `001745`
  overlap 更早
- `interference_gain_db = +2.356`
  说明
  `001745`
  相比
  `001543`
  gain 更强
- `target_transient_share = +0.027954`
  和
  `interference_transient_share = +0.045361`
  说明
  `001745`
  的 transient share
  仍更高

因此当前更合理的写法是：

- `001543`
  和
  `001745`
  不是单轴深浅关系；
- 它们是两个
  已进入 post-entry
  之后的
  branch identity：
  - 一个是
    `v65 sink`
  - 一个是
    `v64 pocket`

## 结论

1. `train_001745 / train_001543 / train_000664` 不是沿一条连续深度线排队，而是从同一个 `v64 crossed` 台阶分叉成两支：
   - `v65 sink`
   - `v64 pocket`
2. `train_001543` 相对 `train_000664` 基本不动 `v66 - v64`，真正被压深的是 `v66 - v65`，所以它是最干净的 `v65 sink` 对照。
3. `train_001745` 相对 `train_000664` 只多走了很小一步 margin，但刚好把 `v66 - v65` 也推到负区，同时保住 `v64` 更深负 gap，因此形成了稀有的 `both-crossed + v64-deeper` pocket。
4. 当前最合理的下一步应继续收紧成只看 `train_001543` 对 `train_000664`，因为这对几乎固定住了 `v66 - v64`，最适合隔离“到底是什么把 `v66 > v65` 从刚好为正翻成显著为负”。 
