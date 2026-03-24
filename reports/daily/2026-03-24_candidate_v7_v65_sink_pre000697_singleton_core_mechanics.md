# 2026-03-24 `candidate_v7` `v65` sink `pre000697` singleton core mechanics

## 背景

上一轮已经把
`000697`
这条线
直接压到
tight-companion search，
并确认：

- 当前没有
  tighter companion
- `000904`
  只能保留为
  extreme support
- `000219`
  只能保留为
  broad tail
- direct ring
  里最像
  `000697`
  的近邻
  会自然拆成：
  - `000207 / 000216`
    shortgain neighbor
  - `001079 / 001494`
    shortshare / offset-cosine neighbor

但到这里，
还只是在回答：

- 没有谁
  可以扶正成
  tighter companion

还没有把
最关键的一句话
讲透：

- 为什么
  `000697`
  会稳定留成
  singleton core

因此本轮不再继续找新 row，
而是直接回答：

1. `000904`
   为什么只能是
   extreme support，
   接不住 core
2. `shortgain`
   与
   `shortshare`
   两条旁支
   分别缺了什么
3. `000697`
   的 irreducible core
   到底是哪组 conjunction

## 本轮做法

这一步不加新脚本，
只继续复用已有结果，
并补两组
route-specific projection：

- `000697`
  对
  `shortgain_neighbor`
  的 slice / quadrants
- `000697`
  对
  `shortshare_neighbor`
  的 slice / quadrants

本轮新增输出：

1. `000697 -> shortgain_neighbor`
   slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortgain_neighbor_slice_support/summary.json`
2. `000697 -> shortgain_neighbor`
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortgain_neighbor_duration_intmean_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortgain_neighbor_reference_intshare_quadrants/summary.json`
3. `000697 -> shortshare_neighbor`
   slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortshare_neighbor_slice_support/summary.json`
4. `000697 -> shortshare_neighbor`
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortshare_neighbor_duration_offset_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortshare_neighbor_duration_cosine_quadrants/summary.json`

同时继续引用上一轮
已经落盘的：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_duration_gain_quadrants/summary.json`
- `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_direct_gain_intshare_quadrants/summary.json`
- `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortgain_neighbor_factor_contrast/summary.json`
- `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_shortshare_neighbor_factor_contrast/summary.json`

## 结果

### 1. `000697` 之所以还留成 singleton core，不是因为“没人靠近它”，而是因为周围每条路都只能接住它的一部分 conjunction

现在围着
`000697`
已经能看到
三类不同角色：

1. `000904`
   - extreme support
2. `000207 / 000216`
   - shortgain neighbor
3. `001079 / 001494`
   - shortshare / offset-cosine neighbor

它们都能贴近
`000697`
的某一部分，
但没有任何一类
能把
`000697`
当前的核心 conjunction
整块接住。

所以：

- `000697`
  现在不是
  “暂时没找到 twin”
- 而是：
  - 周围已经出现多条
    partial routes
  - 但每条 route
    都只接住
    core 的一部分

### 2. `000904` 能接住 long-duration 与弱 interference-package，但接不住 low-gain core；这就是它只能停在 extreme support 的根本原因

上一轮已经看到：

- `000904`
  在 direct ring
  并不近
- 但在
  route projection
  上
  又反复冒出来

这一步把它为什么
“总会冒出来，
但又扶不正”
讲清了。

先看
`duration + gain`
四象限：

- `target = 000697`
  落在：
  - `both`
- `contrast = 000904`
  落在：
  - `factor_a_only`

也就是：

- `000904`
  占住了：
  - long-duration
    这一侧
- 但它没占住：
  - low gain
    这一侧

再看
`gain + interference share`
四象限：

- `target = 000697`
  落在：
  - `both`
- `contrast = 000904`
  落在：
  - `factor_b_only`

也就是：

- `000904`
  占住了：
  - extreme low
    interference share
- 但它仍没占住：
  - low gain

再把这一点
和上一轮的 pair contrast
合起来看：

- `000697 -> 000904`
  排前字段为：
  - `target share`
  - `gain`
  - `interference share`

可以得出更稳定的口径：

- `000904`
  不是
  `000697`
  的弱化版 /
  加深版
- 它更像：
  - long-duration
  - ultra-weak interference package
  的 extreme support
- 但因为
  low gain
  这条主轴
  没接住，
  所以永远扶不成
  core companion

### 3. `000207 / 000216` 这条 shortgain 邻支，缺的是“长时长 + 弱 interference package”的整块 conjunction

先看
单因子 slice：

- `target_duration`
  上，
  `shortgain_neighbor`
  不在 target side
- `interference transient mean`
  上，
  `shortgain_neighbor`
  也不在 target side
- `interference transient share`
  上，
  `shortgain_neighbor`
  同样不在 target side

也就是：

- `000207 / 000216`
  虽然贴近
  `000697`
  这条 route，
  但：
  - duration
    不够长
  - interference package
    也不够弱

再看
`duration + interference mean`
四象限：

- `target = 000697`
  落在：
  - `both`
- `contrast = shortgain_neighbor`
  落在：
  - `neither`

而且
`both`
里只剩：

- `train_000904`

也就是：

- 对 shortgain 邻支来说，
  一旦把：
  - long duration
  - weak interference mean
  联立，
  它就完全掉出去了

再看
`reference + interference share`
四象限：

- `target = 000697`
  落在：
  - `both`
- `contrast = shortgain_neighbor`
  落在：
  - `factor_a_only`

也就是：

- `000207 / 000216`
  只能接住：
  - reference
    这一边
- 但接不住：
  - low interference share

再结合 factor contrast：

- `000697 -> shortgain_neighbor`
  排前字段为：
  - `reference_duration_sec`
  - `target_duration_sec`
  - `interference_transient_presence_minus_mid_db_mean`

因此这条 shortgain 邻支
应固定写成：

- 贴在
  `000697`
  周围
  的
  short-duration / short-reference
  low-gain branch
- 但它缺失：
  - 长时长
  - 弱 interference package
  这组 core conjunction

### 4. `001079 / 001494` 这条 shortshare 邻支，缺的是“长时长 + 低 cosine / 较晚 offset”的另一块 conjunction

先看
单因子 slice：

- `target_duration`
  上，
  `shortshare_neighbor`
  不在 target side
- `target_interference_logspec_cosine`
  上，
  `shortshare_neighbor`
  也不在 target side
- `start_offset`
  上，
  `shortshare_neighbor`
  则在 target side

这已经说明：

- `001079 / 001494`
  不是完全脱线
- 但它们主要只贴住：
  - offset
    这一边
- 没贴住：
  - long duration
  - low cosine

再看
`duration + offset`
四象限：

- `target = 000697`
  落在：
  - `both`
- `contrast = shortshare_neighbor`
  落在：
  - `factor_b_only`

也就是：

- 这条邻支
  只接住了：
  - offset
    这一轴
- 一旦把
  long duration
  联立，
  它就会从 core
  掉出去

再看
`duration + cosine`
四象限：

- `target = 000697`
  落在：
  - `both`
- `contrast = shortshare_neighbor`
  落在：
  - `neither`

这一步更直接：

- 把：
  - long duration
  - low cosine
  联立后，
  `001079 / 001494`
  会被整块甩出

再结合 factor contrast：

- `000697 -> shortshare_neighbor`
  排前字段为：
  - `start_offset_sec`
  - `target_duration_sec`
  - `target_interference_logspec_cosine`

因此这条 shortshare 邻支
应固定写成：

- 贴在
  `000697`
  周围
  的
  short-duration / offset-cosine branch
- 但它缺失：
  - 长时长
  - 低 cosine
  这组 core conjunction

### 5. 三类旁支拼起来以后，反而更清楚地说明了 `000697` 的 irreducible core 是什么

把上面三类放在一起看，
会发现：

#### 5.1 `000904`

能接住：

- long duration
- 弱 interference package

但缺：

- low gain

#### 5.2 `000207 / 000216`

能接住：

- low gain

但缺：

- long duration
- 弱 interference package

#### 5.3 `001079 / 001494`

能接住：

- 较晚 offset
  的一侧

但缺：

- long duration
- low cosine

因此
`000697`
当前最稳的 core
不能再写成
任何单轴，
而应固定写成
至少三块 conjunction：

1. long duration
2. low gain
3. weak interference package
   - 低 interference mean
   - 低 interference share

并且在 direct ring
里，
还伴随：

4. 较低 cosine /
   不像 shortshare 邻支那样
   回弹

也就是说：

- `000697`
  之所以还留成
  singleton core，
  不是因为
  周围没有近邻
- 而是因为：
  - 每一类近邻
    都只接住
    这套 conjunction
    的一部分
- 当前没有任何一条 row
  能同时接住：
  - long duration
  - low gain
  - weak interference package

### 6. 到这一步，`000697` 这条线已经不该再以“找 companion”为主语，而应转成“解释 singleton core 为何还没被旁支接住”

当前如果还继续写：

- 谁最像
  `000697`

会越来越低效。

因为现在更有信息量的
问题已经变成：

- 为什么
  side-branch
  会在不同轴上
  轮流贴近
  `000697`
  却始终接不住 core

所以这条线
当前应改写成：

- `000697`
  singleton core
  mechanism

而不是：

- `000697`
  companion search

## 当前解释

本轮之后，
`000697`
这条线
应继续固定成：

1. `000697`
   = singleton core
2. `000904`
   = extreme support
   只能接住：
   - long duration
   - weak interference package
   但接不住：
   - low gain
3. `000207 / 000216`
   = shortgain side-branch
   只能接住：
   - low gain
   但接不住：
   - long duration
   - weak interference package
4. `001079 / 001494`
   = shortshare / offset-cosine side-branch
   只能接住：
   - offset
     这一侧
   但接不住：
   - long duration
   - low cosine
5. 后续若继续推进，
   默认不再做：
   - tighter companion search
   而是转成：
   - 解释
     这三类 partial routes
     为什么都只能贴近，
     却接不住 core

## 结论

1. `000697`
   当前仍是
   singleton core，
   而且这个结论
   已经不只是
   “还没找到 companion”，
   而是：
   - 已确认周围每类近邻
     都只接住它的一部分
2. `000904`
   只能继续写成
   extreme support；
   它接住了
   long duration
   与 weak interference package，
   但接不住
   low gain。
3. `000207 / 000216`
   是
   shortgain side-branch；
   `001079 / 001494`
   是
   shortshare / offset-cosine side-branch；
   两条旁支都不能扶正成 core。
4. `000697`
   当前最稳的
   irreducible core
   应固定写成：
   - long duration
   - low gain
   - weak interference package
   的 conjunction。
5. 这条线后续默认转成
   singleton-core mechanism
   解释，
   不再继续做
   companion search。
6. 本轮仍不启动新训练。
