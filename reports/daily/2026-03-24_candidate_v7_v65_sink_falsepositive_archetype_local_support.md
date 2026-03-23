# 2026-03-24 `candidate_v7` `v65` sink false-positive archetype local support

## 背景

上一轮已经把：

- `train_000799`
- `train_000697`

分别放回
已知 pre archetype
坐标系，
并确认：

- `000799`
  最近的 archetype
  是
  `train_001589`
  weak-gain partial-mean hinge
- `000697`
  最近的 archetype
  是
  `train_000664`
  low-share `v64_only`

但那一步还只是
“最近 archetype”
的全局定位。

当前更窄的问题
变成：

1. 在
   `001589`
   的局部 neighbor ring
   里，
   `000799`
   到底是不是一条
   稳定可复现的
   target-transient-collapse pocket
2. 在
   `000664`
   的局部 neighbor ring
   里，
   `000697`
   到底是不是一条
   稳定可复现的
   long-duration / low-share pocket

也就是：

- 全局 positioning
  已经说清了
  “它最像谁”
- 现在要继续压清：
  “在它最近的局部 archetype
  邻域里，
  到底还有没有
  同方向 support”

## 本轮做法

这一步不加新脚本，
只复用已有：

- `scripts/eval/analyze_proxy_case_neighbors.py`
- `scripts/eval/analyze_proxy_factor_slice_support.py`
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

先分别对：

1. `train_001589`
   做局部 neighbor scan
2. `train_000664`
   做局部 neighbor scan

然后直接在各自邻域上，
只投影
route-specific residual：

- `001589 -> 000799`
  这条线
  用：
  - `target_duration`
  - `target transient share`
  - `target transient mean`
  - `interference transient share`
- `000664 -> 000697`
  这条线
  用：
  - `target_duration`
  - `target transient share`
  - `interference transient share`
  - `interference transient mean`

本轮新增输出：

1. `001589`
   局部 neighbor scan：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_partialmean_neighbor_scan/summary.json`
2. `000664`
   局部 neighbor scan：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_v64only_neighbor_scan/summary.json`
3. `000799`
   local slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmean_slice_support/summary.json`
4. `000799`
   local quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmean_duration_targetmean_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmean_targetshare_targetmean_quadrants/summary.json`
5. `000697`
   local slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_slice_support/summary.json`
6. `000697`
   local quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_duration_targetshare_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_duration_intshare_quadrants/summary.json`

## 结果

### 1. 只看 raw 邻域排序还不够；两个 archetype ring 本身都是 mixed shelf

先看
`001589`
的局部邻域。

最近的前几条 row
是：

1. `train_000266`
   - `metadata_distance_z = 3.289924`
   - `hinge_v65_crossed`
2. `train_000799`
   - `metadata_distance_z = 3.391752`
   - `pre_entry_or_pure`
3. `train_001639`
   - `metadata_distance_z = 3.396388`
   - `pre_entry_or_pure`
4. `train_001494`
   - `metadata_distance_z = 3.474744`
   - `pre_entry_or_pure`
5. `train_000697`
   - `metadata_distance_z = 3.479785`
   - `pre_entry_or_pure`

整个
`001589`
邻域
`27`
条 row
的 state 分布为：

- `pre_entry_or_pure = 20`
- `hinge_v65_crossed = 3`
- `v64_only_crossed = 2`
- `both_crossed_v64_deeper = 1`
- `both_crossed_v65_deeper = 1`

再看
`000664`
的局部邻域。

最近的前几条 row
是：

1. `train_001610`
   - `metadata_distance_z = 1.733168`
   - `hinge_v65_crossed`
2. `train_000759`
   - `metadata_distance_z = 2.055267`
   - `pre_entry_or_pure`
3. `train_001639`
   - `metadata_distance_z = 2.560057`
   - `pre_entry_or_pure`
4. `train_000117`
   - `metadata_distance_z = 2.874619`
   - `pre_entry_or_pure`
5. `train_001725`
   - `metadata_distance_z = 2.996328`
   - `pre_entry_or_pure`
6. `train_000799`
   - `metadata_distance_z = 3.077766`
   - `pre_entry_or_pure`
7. `train_001745`
   - `metadata_distance_z = 3.388151`
   - `both_crossed_v64_deeper`
8. `train_000697`
   - `metadata_distance_z = 3.433423`
   - `pre_entry_or_pure`

整个
`000664`
邻域
`27`
条 row
的 state 分布为：

- `pre_entry_or_pure = 20`
- `hinge_v65_crossed = 4`
- `v64_only_crossed = 1`
- `both_crossed_v64_deeper = 1`
- `both_crossed_v65_deeper = 1`

这说明：

- archetype ring
  本身并不是
  单语义 pocket；
- 只看
  raw metadata neighbor rank，
  还不能直接判：
  - 哪条 row
    属于
    `000799`
    那条 local route
  - 哪条 row
    属于
    `000697`
    那条 local route

所以本轮关键不是
“谁离 archetype 最近”，
而是：

- 谁会在
  route-specific residual
  投影后，
  继续和目标 case
  留在同一个
  target-side pocket

### 2. `001589` 邻域里，`000799` 会在 target-side transient collapse 投影上收缩成一条非常窄的 pre-only pocket

先看
`000799 -> 001589`
的单因子 slice。

#### 2.1 `target transient share`
单独就已经很干净

target-side midpoint
为：

- `0.001170`

落到 target side
的只有：

- `train_000799`
- `train_000681`

state 计数只有：

- `pre_entry_or_pure = 2`

并且
contrast
`train_000697`
不在 target side。

这已经说明：

- 在
  `001589`
  邻域里，
  `000799`
  最核心的
  target-share collapse
  不是一大片
  mixed shelf；
- 它更像一条
  极窄的 pre-only
  micro-pocket

#### 2.2 `duration + target transient mean`
会把 `000697` 稳定留在 pocket 外

做
`target_duration + target_transient_mean`
四象限后：

- `both`
  里共有
  `7`
  条：
  - `train_000266`
  - `train_000799`
  - `train_001639`
  - `train_001494`
  - `train_000207`
  - `train_001610`
  - `train_000681`
- 其中 state
  计数为：
  - `pre_entry_or_pure = 5`
  - `hinge_v65_crossed = 2`
- contrast
  `train_000697`
  落在：
  - `neither`

而
`neither`
里只剩：

- `train_000697`
- `train_000219`
- `train_000904`

也就是：

- 只要把：
  - shorter duration
  - lower target transient mean
  联立起来，
  `000799`
  就会从
  `001589`
  邻域里
  明显分出一条线；
- `000697`
  即便 raw 距离
  也贴得不远，
  仍然会被稳定甩到
  pocket 外

#### 2.3 `target share + target transient mean`
进一步把 pocket 压到只剩两条纯 pre

做
`target_transient_share + target_transient_mean`
四象限后：

- `both`
  里只剩：
  - `train_000799`
  - `train_000681`
- state 计数为：
  - `pre_entry_or_pure = 2`
- `factor_b_only`
  里有：
  - `train_000266`
  - `train_001639`
  - `train_001494`
  - `train_000207`
  - `train_001610`
- contrast
  `train_000697`
  仍在：
  - `neither`

这一步很关键：

- `000799`
  并不是
  `001589`
  邻域里
  一大片 low-cosine 或 low-duration
  混合区的一员；
- 它在
  target-side transient collapse
  投影上，
  已经收缩成：
  - `000799`
  - `000681`
  这条
  极小的
  pre-only support pocket

因此当前应把
`001589 -> 000799`
这条 local route
固定写成：

- partial-mean hinge
  之后，
  朝
  target-side transient collapse
  + shorter duration
  回摆的小 pocket

### 3. `000664` 邻域里，`000697` 会在 long-duration + low-share 投影上收缩成另一条 pre-only pocket

先看
`000697 -> 000664`
的单因子 slice。

#### 3.1 `target_duration`
先把它从短时长 pre 里抬出去

target-side midpoint
为：

- `1.725 sec`

落到 target side
的只有：

- `train_000697`
- `train_000266`
- `train_001589`
- `train_000219`
- `train_000904`

state 计数为：

- `pre_entry_or_pure = 3`
- `hinge_v65_crossed = 2`

并且
contrast
`train_000799`
不在 target side。

这说明：

- `000697`
  在
  `000664`
  邻域里，
  首先不是
  low-share 本身最极端；
- 它更先表现为：
  - duration
    被抬长了

#### 3.2 `interference transient share`
再把它推向 weak-interference package

`interference transient share`
的 target side
定义为：

- 更低

落在 target side
的有：

- `train_000697`
- `train_001006`
- `train_001494`
- `train_000951`
- `train_001079`
- `train_000210`
- `train_000904`

state 计数为：

- `pre_entry_or_pure = 6`
- `v64_only_crossed = 1`

contrast
`train_000799`
仍不在 target side。

也就是：

- `000697`
  在
  `000664`
  邻域里，
  不是
  target transient collapse
  那条线；
- 它更像：
  - duration 拉长
  - interference share 变低
  的那条线

### 4. 把 `duration` 与 `share` 联立后，`000697` 的 pocket 会比 raw 邻域小得多，而且 `000799` 会稳定掉出去

#### 4.1 `duration + target transient share`
会把 `000697`
压成三条纯 pre

做
`target_duration + target_transient_share`
四象限后：

- `both`
  里只有：
  - `train_000697`
  - `train_000219`
  - `train_000904`
- state 计数为：
  - `pre_entry_or_pure = 3`
- `factor_a_only`
  里只有：
  - `train_000266`
  - `train_001589`
- contrast
  `train_000799`
  落在：
  - `neither`

这说明：

- 只要把：
  - 长 duration
  - 高于 `000664`
    的 target share
  联立起来，
  `000697`
  就会从
  `000664`
  邻域里
  收缩成
  一个非常小的
  pre-only tail pocket

#### 4.2 `duration + interference share`
则把 pocket 再压成两条纯 pre

做
`target_duration + interference_transient_share`
四象限后：

- `both`
  里只剩：
  - `train_000697`
  - `train_000904`
- state 计数为：
  - `pre_entry_or_pure = 2`
- `factor_a_only`
  里有：
  - `train_000266`
  - `train_001589`
  - `train_000219`
- `factor_b_only`
  里有：
  - `train_001006`
  - `train_001494`
  - `train_000951`
  - `train_001079`
  - `train_000210`
- contrast
  `train_000799`
  仍在：
  - `neither`

这一步说明：

- `000697`
  也不是
  `000664`
  邻域里
  一个大而散的
  low-share 棚；
- 在
  `duration + low interference share`
  这条 local route
  上，
  它已经收缩成：
  - `000697`
  - `000904`
  这条更小的
  pre-only pocket

因此当前应把
`000664 -> 000697`
这条 local route
固定写成：

- low-share `v64_only`
  之后，
  朝
  long-duration
  + weak-interference-package
  回摆的小 pocket

### 5. 两条 local route 现在都已经拿到各自的局部 support row，不能再并回同一个 sink-side pocket

到这一步，
各自的最近 support
已经可以明确点名：

- `001589 -> 000799`
  这条线
  当前最紧的
  局部 support row
  是：
  - `train_000681`
- `000664 -> 000697`
  这条线
  当前最紧的
  局部 support row
  是：
  - `train_000904`
  更宽一点的
  support tail
  还有：
  - `train_000219`

也就是说：

- `000799`
  不是孤零零漂在
  `001589`
  边上；
- `000697`
  也不是孤零零漂在
  `000664`
  边上；
- 两者都已经在
  各自 archetype ring
  内找到
  本地 support，
  但 support 的语义完全不同：
  - 一条是
    target-transient-collapse
  - 一条是
    long-duration + low-share

所以后续默认不能再写成：

- 同一个 sink-side false-positive pocket

更准确的口径应固定成：

- `001589 -> 000799`
  micro-pocket
- `000664 -> 000697`
  micro-pocket

## 当前解释

本轮之后，
这两条 false-positive route
应继续收紧成：

1. `000799`
   不是
   generic sink-side pre；
   它是
   `001589`
   邻域里，
   由：
   - shorter duration
   - target transient share collapse
   - target transient mean collapse
   共同定义的
   pre-only micro-pocket
2. `000697`
   不是
   `000799`
   的长一点版本；
   它是
   `000664`
   邻域里，
   由：
   - longer duration
   - lower interference share
   - weaker interference package
   共同定义的
  另一条 pre-only micro-pocket
3. 之后如果还要继续推进，
   默认不再比较：
   - `000799`
     和
     `000697`
     谁更像 sink
   而是直接比较：
   - `000799`
     与
     `000681`
   - `000697`
     与
     `000904 / 000219`
   看这些 support row
   到底是
   同 pocket
   的稳定 companion，
   还是只是邻域尾巴

## 结论

1. `001589`
   与
   `000664`
   的 raw 邻域
   都是 mixed shelf，
   不能只靠
   neighbor rank
   判定 local route。
2. `000799`
   在
   `001589`
   邻域里，
   已经被压成
   `000799 + 000681`
   这条
   target-transient-collapse
   pre-only micro-pocket。
3. `000697`
   在
   `000664`
   邻域里，
   已经被压成
   `000697 + 000904`
   这条
   long-duration + low-share
   pre-only micro-pocket，
   `000219`
   则是更宽一点的 tail support。
4. 后续默认沿：
   - `000799 <-> 000681`
   - `000697 <-> 000904 / 000219`
   两条 companion 线继续推进，
   不回到单一 sink pocket 解释。
5. 本轮仍不启动新训练。
