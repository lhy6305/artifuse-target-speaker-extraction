# 2026-03-24 `candidate_v7` `v65` sink `pre000697` tight companion search

## 背景

上一轮已经把
false-positive companion
压到了
validation，
并得到一个
不对称结论：

- `000799`
  这条线
  已经拿到
  stable companion
  - `train_000681`
- `000697`
  这条线
  目前还没有
  tight companion
  - `train_000904`
    只能保留为
    extreme edge support
  - `train_000219`
    只能保留为
    broad tail

但到这里，
关于
`000697`
还剩最后一个关键空白：

- 到底是真的
  没有 tighter companion
- 还是我们前面
  围着
  `000664`
  做
  archetype-centered ring
  时，
  漏掉了某条
  更贴
  `000697`
  本人的 row

因此本轮不再围着
`000664`
看，
而是直接以：

- `train_000697`

本人做 seed，
去找：

- direct-metadata companion

如果仍找不到，
再把最近的几条
非-core row
拆成旁支，
把
“为什么它们看起来近，
但不是 tight companion”
讲清楚。

## 本轮做法

这一步不加新脚本，
继续复用已有：

- `scripts/eval/analyze_proxy_case_neighbors.py`
- `scripts/eval/analyze_proxy_case_positioning.py`
- `scripts/eval/analyze_proxy_group_split.py`
- `scripts/eval/analyze_proxy_factor_slice_support.py`
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`

先做两层分析：

1. 以
   `000697`
   本人做
   direct neighbor scan
2. 把 direct ring
   里最像
   `000697`
   但又不是 core
   的 row
   再拆成小簇：
   - `000207 + 000216`
     `shortgain_neighbor`
   - `001079 + 001494`
     `shortshare_neighbor`

本轮新增资产：

1. `shortgain_neighbor`
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_v64only_shortgain_neighbor_train.txt`
2. `shortshare_neighbor`
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_v64only_shortshare_neighbor_train.txt`

本轮新增输出：

1. `000697`
   direct neighbor scan：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_neighbor_scan/summary.json`
2. `000697`
   direct ring
   对
   `000904`
   的 route-specific
   slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_vs_000904_slice_support/summary.json`
3. `000697`
   direct ring
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_duration_gain_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_duration_targetshare_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_gain_intshare_quadrants/summary.json`
4. direct-ring 候选
   positioning：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_candidate_positioning/summary.json`
5. direct-ring family split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_neighbor_family_split/summary.json`
6. `000697`
   对两类 direct 邻居
   的 contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortgain_neighbor_factor_contrast/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortshare_neighbor_factor_contrast/summary.json`

## 结果

### 1. 直接围着 `000697` 本人做邻域后，`000904` 反而根本不近；tight companion search 先从 direct ring 层面就已经转阴

`000697`
的 direct neighbor scan
前几条 row
是：

1. `train_000799`
   - `metadata_distance_z = 2.279`
2. `train_000266`
   - `metadata_distance_z = 3.347`
3. `train_001543`
   - `metadata_distance_z = 3.377`
4. `train_000117`
   - `metadata_distance_z = 3.397`
5. `train_000759`
   - `metadata_distance_z = 3.400`
6. `train_000664`
   - `metadata_distance_z = 3.433`
7. `train_001494`
   - `metadata_distance_z = 3.467`
8. `train_001589`
   - `metadata_distance_z = 3.480`
9. `train_000216`
   - `metadata_distance_z = 3.519`
10. `train_001610`
    - `metadata_distance_z = 3.530`

而
`train_000904`
在这份 direct ring
里的位置是：

- `metadata_distance_z = 6.938`

也就是：

- `000904`
  虽然在
  archetype-centered projection
  里
  可以落进
  `000697`
  那条 route，
  但它从
  direct metadata ring
  看，
  根本不是
  最近那层 neighbor

这点很关键：

- 如果一个 row
  真是
  `000697`
  的 tight companion，
  它至少不该在：
  - direct ring
    里落到这么靠后

因此：

- 仅从
  direct neighbor
  这一步看，
  `000904`
  就已经更像：
  - route-aligned
    extreme support
  而不是：
  - direct tight companion

### 2. direct ring 里最像 `000697 core` 的并不是 `000904`，而是 `000207 / 000216 / 001079 / 001494` 这几条邻居；但它们又会自然拆成两个旁支小簇

把 direct ring
里几条近邻
放回：

- `v64only_target`
  (`000697`)
- `v64only_archetype`
  (`000664`)
- `v64only_extreme`
  (`000904`)

这三个 reference
做 positioning 后，
最像
`v64only_target`
的几条是：

1. `train_000207`
   - nearest = `v64only_target`
   - margin = `0.064316`
2. `train_000216`
   - nearest = `v64only_target`
   - margin = `0.194603`
3. `train_001079`
   - nearest = `v64only_target`
   - margin = `0.439558`
4. `train_001494`
   - nearest = `v64only_target`
   - margin = `0.682745`
5. `train_001589`
   - nearest = `v64only_target`
   - margin = `1.333185`

也就是：

- direct ring
  并不是
  完全没有
  “贴近 `000697`”
  的 row；
- 只是这些 row
  没有自然落成
  一个 tight companion
  cluster；
- 它们更像
  两类不同的
  邻近旁支

因此本轮把它们
先拆成：

1. `shortgain_neighbor`
   - `000207`
   - `000216`
2. `shortshare_neighbor`
   - `001079`
   - `001494`

### 3. `000207 / 000216` 是一条 short-duration + short-reference 的 low-gain 邻支，不是 `000697` 的 tight companion

先看
`v64only_target - v64only_shortgain_neighbor`
的直接均值差：

- `target_duration_sec`
  - `+1.14 sec`
- `reference_duration_sec`
  - `+0.87 sec`
- `interference_transient_presence_minus_mid_db_mean`
  - `-5.538916`
- `interference_transient_presence_share_mean`
  - `-0.147859`
- `target_interference_logspec_cosine`
  - `-0.082567`
- `interference_layers.0.gain_db`
  - `+0.648 dB`

也就是：

- `000207 / 000216`
  相对
  `000697`
  并不是真的
  “几乎一样，
  只差深浅”；
- 它们更像：
  - 时长明显更短
  - reference 更短
  - interference package
    没有被压到
    `000697`
    那么弱

再看
`000697 -> shortgain_neighbor`
的 factor contrast，
排前字段固定成：

1. `reference_duration_sec`
   - `+1.8878 z`
2. `target_duration_sec`
   - `+1.4518 z`
3. `interference_transient_presence_minus_mid_db_mean`
   - `-1.0206 z`
4. `interference_transient_presence_share_mean`
   - `-0.9312 z`
5. `target_interference_logspec_cosine`
   - `-0.9181 z`

这说明：

- `000697`
  相对这组 direct neighbor
  的主 residual，
  不是
  “还要再弱一点 gain”；
- 真正把它们拉开的
  是：
  - 更长 duration
  - 更长 reference
  - 更弱 interference package

因此：

- `000207 / 000216`
  应固定写成：
  - short-duration
  - short-reference
  - low-gain
    邻支
- 不是
  `000697`
  的 tight companion

### 4. `001079 / 001494` 则是另一条 short-duration + offset/cosine 偏移邻支，也不是 tight companion

再看
`v64only_target - v64only_shortshare_neighbor`
的直接均值差：

- `target_duration_sec`
  - `+1.20 sec`
- `interference_layers.0.start_offset_sec`
  - `+0.168`
- `target_interference_logspec_cosine`
  - `-0.114208`
- `interference_layers.0.gain_db`
  - `-1.4065 dB`
- `interference_transient_presence_share_mean`
  - `+0.104251`

也就是：

- 这组 row
  相对
  `000697`
  的差异，
  更像：
  - 时长更短
  - offset
    更靠前
  - cosine
    更高
  - interference share
    也没有压到
    `000697`
    那么低

再看
`000697 -> shortshare_neighbor`
的 factor contrast，
排前字段固定成：

1. `interference_layers.0.start_offset_sec`
   - `+1.6035 z`
2. `target_duration_sec`
   - `+1.5282 z`
3. `target_interference_logspec_cosine`
   - `-1.2700 z`
4. `interference_transient_presence_share_mean`
   - `+0.6566 z`

这说明：

- `001079 / 001494`
  也不是
  `000697`
  那条 core
  在主 residual
  上的稳定同伴；
- 它们更像：
  - short-duration
  - offset / cosine
    偏移
  的另一条
  近邻旁支

因此：

- `001079 / 001494`
  不能并回：
  - `000697`
    core companion

### 5. 直接把 `000904` 放回 `000697` direct ring 的 route-specific quadrants，看见的也不是 tight companion，而是“要么只占时长轴，要么只占极端 interference 轴”

在 direct ring 上，
把：

- `target = 000697`
- `baseline = 000664`
- `contrast = 000904`

重新投影，
能看到更直观的结构。

#### 5.1 `duration + gain`

四象限结果：

- `both`
  里只有：
  - `train_000266`
  - `train_001589`
  两条 hinge
- `factor_a_only`
  里是：
  - `train_000219`
  - `train_000904`
- contrast
  `000904`
  落在：
  - `factor_a_only`

也就是：

- `000904`
  只占住了：
  - duration
  这一条
- 它没有占住：
  - low gain
    这一条

这再次说明：

- `000904`
  不是
  `000697`
  core
  的 tight companion

#### 5.2 `gain + interference share`

四象限结果：

- `both`
  里只剩：
  - `train_001494`
- contrast
  `000904`
  落在：
  - `factor_b_only`

也就是：

- `000904`
  只占住了：
  - 极低 interference share
  这一条
- 它没占住：
  - `000697`
    那条
    low gain

反过来，
`001494`
虽然占住了：

- `gain + interference share`

但又没有：

- `000697`
  的长 duration

所以 direct ring
里的行为空间
被自然拆成了：

- 一个 duration 轴
- 一个 gain/intshare 轴

并没有出现
哪条 row
能把：

- 长 duration
- 低 gain
- 低 interference share

这三件事
一起稳稳接住

### 6. 到这一步，`000697` 的 tighter-companion search 可以正式转成“当前未找到”，而 direct ring 应拆成两条 side-branch，不再继续围着 `000904`

综合：

1. direct ring
   里，
   `000904`
   不近
2. route-specific quadrants
   里，
   `000904`
   也只占住：
   - duration
   或
   - extreme interference-share
     的单轴 / 极端轴
3. 最像
   `000697`
   的 direct 邻居
   其实是：
   - `000207 / 000216`
   - `001079 / 001494`
   这两组
4. 但这两组
   各自又会稳定退成：
   - short-duration / short-reference
     low-gain 邻支
   - short-duration / offset-cosine
     邻支

所以当前更准确的口径应改成：

- `000697`
  目前仍是
  singleton core
- `000904`
  继续保留为
  extreme route support
- `000219`
  继续保留为
  long-duration tail
- direct ring
  不存在
  可以扶正成
  tight companion
  的 row

也就是说：

- 这条 route
  当前最重要的新信息
  不是
  “找到谁最像 `000697`”
- 而是
  “确认暂时没有 tight companion，
  且最近邻会自然分叉成两条 side-branch”

## 当前解释

本轮之后，
`000697`
这条线
应继续收紧成：

1. `000697`
   仍写成：
   - route core singleton
2. `000904`
   仍写成：
   - extreme edge support
3. `000219`
   仍写成：
   - broad long-duration tail
4. direct ring
   新增两条 side-branch：
   - `000207 / 000216`
     shortgain neighbor
   - `001079 / 001494`
     shortshare / offset-cosine neighbor
5. 后续如果继续推进，
   默认不再围着：
   - `000904`
     要不要扶正
   打转，
   而是直接转成：
   - `000697`
     为什么仍是 singleton core
   - 以及
     两条 side-branch
     为什么都只能贴近，
     却接不住 core

## 结论

1. 直接以
   `000697`
   做 seed
   搜 tighter companion，
   当前结果为：
   - 未找到
2. `000904`
   在 archetype-centered route
   里可以保留，
   但在 direct ring
   里并不近，
   也接不住
   `000697`
   的
   low-gain core；
   当前只能继续记成
   extreme support。
3. `000697`
   最近的 direct 邻居
   会稳定拆成两条 side-branch：
   - `000207 / 000216`
     shortgain neighbor
   - `001079 / 001494`
     shortshare / offset-cosine neighbor
4. 这一步之后，
   `000697`
   默认应固定写成：
   - singleton core
   - 当前没有 tight companion
   - 周围只有
     extreme support
     与
     two side-branches
5. 本轮仍不启动新训练。
