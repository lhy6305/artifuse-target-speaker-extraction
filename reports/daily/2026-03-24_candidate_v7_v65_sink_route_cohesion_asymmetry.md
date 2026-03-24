# 2026-03-24 `candidate_v7` `v65` sink route cohesion asymmetry

## 背景

上一轮已经把
`000697`
这条线
压到
singleton-core mechanism，
并确认：

- `000697`
  不是
  “暂时没找到
  companion”
- 而是：
  - 周围已经有
    多条 partial route
  - 但每条 route
    只接住
    core 的一部分

与此同时，
`000799`
这条线
已经有了
稳定 companion：

- `000799`
- `000681`

所以本轮要回答的
不再是：

- `000799`
  和
  `000697`
  谁更像
  sink-side residual

而是直接回答：

1. 为什么
   `000799`
   这条线
   能稳定收缩成
   `000799 + 000681`
   的 cohesive micro-pocket
2. 为什么
   `000697`
   这条线
   却会长期留成
   singleton core
3. 这两条 route
   之后的默认口径
   应该怎么分开写

## 本轮做法

本轮不加新训练，
也不再开新的
row search，
只把已经落盘的
route-cohesion 结果
正式固化成日报。

本轮主要引用：

1. `route cohesion`
   split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_route_cohesion_split/summary.json`
2. `partialmean_core`
   direct neighbor scan：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_direct_neighbor_scan/summary.json`
3. `partialmean_core`
   direct slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_direct_slice_support/summary.json`
4. `partialmean_core`
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_direct_targetshare_targetmean_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_direct_duration_targetmean_quadrants/summary.json`
5. 上一轮已经确认的
   `000697`
   singleton-core mechanism：
   - `reports/daily/2026-03-24_candidate_v7_v65_sink_pre000697_singleton_core_mechanics.md`

本轮比较的
两条 route
固定写成：

- `partialmean_core`
  = `000799 + 000681`
- `partialmean_archetype`
  = `001589`
- `v64only_target`
  = `000697`
- `v64only_archetype`
  = `000664`

## 结果

### 1. `000799` 这条线之所以能出现稳定 companion，不是因为“附近没人”，而是因为它的 residual 会收缩成一个足够干净的 target-collapse micro-pocket

先看
`route_cohesion_split`
里
`partialmean_core`
对
`partialmean_archetype`
的主差值：

- `target_transient_presence_share_mean`
  - `-0.001393`
- `target_transient_presence_minus_mid_db_mean`
  - `-4.985060`
- `target_duration_sec`
  - `-1.02`
- `reference_duration_sec`
  - `-1.17`
- `target_interference_logspec_cosine`
  - `-0.112930`
- `interference_layers.0.gain_db`
  - `+3.161`

这组差值
说明：

- `001589`
  这类
  partial-mean hinge
  往
  `000799 + 000681`
  这条线
  收缩时，
  最先塌下去的
  仍然是：
  - target transient share
  - target transient mean
- shorter duration
  与
  shorter reference
  更像
  支撑这类 pocket
  收紧的次级轴

也就是说，
`000799`
这条线
的主语
不是泛化的
“duration 变短”
或
“gain 变弱”，
而是：

- target-side
  transient collapse
  本身

### 2. `partialmean_core` 的 direct ring 里，真正稳定定义 pocket 的是 `target share + target mean`；duration 只是 supporting axis，不是 pocket identity

`partialmean_core_direct_slice_support`
直接给出了
三个 factor 的
target-side support：

1. `target_transient_presence_share_mean`
   - `target_value = 0.000376`
   - `baseline_value = 0.001769`
   - `contrast_value = 0.008534`
   - `contrast_on_target_side = false`
   - `target_side_sample_ids = []`
2. `target_transient_presence_minus_mid_db_mean`
   - `target_side_sample_ids`
     只有：
     - `001610`
     - `000207`
     - `000266`
3. `target_duration_sec`
   - `target_side_sample_ids`
     有
     `22`
     个

这三条一起看，
信息很明确：

- 在
  `partialmean_core`
  的 direct ring
  里，
  只有
  target transient share
  是真正
  “几乎没人能踩进来”
  的 axis
- target transient mean
  还有少量 shadow rows
- duration
  虽然也向
  core 一侧
  偏，
  但它单独并不稀缺，
  只是 supporting axis

所以：

- `000799 + 000681`
  之所以能形成
  稳定双核，
  不是因为
  它们在所有轴上
  都最极端
- 而是因为：
  - 定义 pocket identity
    的那组 target-collapse
    轴
    已经足够收紧
  - 其他邻居
    最多只是在
    次级轴上
    靠近

### 3. `target share + target mean` 二维上，`partialmean_core` 的口袋非常干净；这正是它能稳定成双核的关键

看
`partialmean_core_direct_targetshare_targetmean_quadrants`
：

- `partialmean_core`
  anchor
  在：
  - `both`
- `partialmean_archetype`
  在：
  - `neither`
- `v64only_target`
  也在：
  - `neither`

更关键的是：

- 非 core rows
  在
  `both`
  里：
  - 一个都没有
- 只有：
  - `001610`
  - `000207`
  - `000266`
  落在：
  - `factor_b_only`

这代表：

- 附近会有人
  部分踩进
  target mean collapse
- 但没人能同时
  把
  target share collapse
  也踩进去

因此：

- `000799 + 000681`
  这条线
  不是
  “很多 row
  都差不多，
  随便挑两个”
- 而是：
  - 当前只有
    这两个 row
    真正占住了
    `target share + target mean`
    同时塌陷的 pocket

这就是
stable companion
出现的根本条件。

### 4. `duration + target mean` 二维上确实会出现 shadow rows，但这不会推翻 `000799 + 000681` 的 core；反而说明 duration 不是 identity，而是 support

看
`partialmean_core_direct_duration_targetmean_quadrants`
：

- `partialmean_core`
  在：
  - `both`
- `v64only_target`
  在：
  - `neither`
- 非 core rows
  在
  `both`
  里
  有：
  - `001610`
  - `000207`
  - `000266`

这一步很关键，
因为它避免了
另一种误判：

- 如果只看
  `duration + target mean`
  会误以为：
  - `001610 / 000207 / 000266`
    也快要进 core

但和上一节
合起来后，
正确读法应是：

- 这些 row
  只能在：
  - shorter duration
  - lower target mean
  上
  靠近
- 它们接不住：
  - target share collapse

所以它们的角色
只能写成：

- loose shadow
- partial support

不能升格成：

- `000799`
  的对称 companion

这也再次说明：

- `000799`
  这条线
  真正的
  route cohesion
  来自
  target-collapse identity
- 不来自
  某个单独的
  duration pocket

### 5. `000697` 这条线恰好相反：它没有形成单一 micro-pocket identity，而是一个被分散到不同邻支上的 conjunction

`route_cohesion_split`
里
`v64only_target`
对
`v64only_archetype`
的主差值是：

- `target_transient_presence_share_mean`
  - `+0.007118`
- `interference_transient_presence_minus_mid_db_mean`
  - `-5.257997`
- `interference_transient_presence_share_mean`
  - `-0.037527`
- `target_duration_sec`
  - `+0.99`
- `interference_layers.0.gain_db`
  - `-3.963`
- `target_interference_logspec_cosine`
  - `-0.069493`

这组差值
和
`partialmean_core`
最大的不同是：

- 它没有一个
  像
  `target share + target mean`
  那样
  一收就形成
  pocket identity
  的单组轴
- 它更像是
  多个条件
  同时成立
  才能定义的
  conjunction：
  - long duration
  - low gain
  - weak interference package
  - 更低 cosine

而上一轮已经确认：

- `000904`
  只能接住：
  - long duration
  - weak interference package
  接不住：
  - low gain
- `000207 / 000216`
  只能接住：
  - low gain
  接不住：
  - long duration
  - weak interference package
- `001079 / 001494`
  只能接住：
  - offset / shortshare
    那一侧
  接不住：
  - long duration
  - low cosine

所以：

- `000697`
  附近不是
  没有 support
- 而是
  support 被拆散成了
  多条 partial route

这就是它
长期维持
singleton core
的原因。

### 6. 两条 route 的真正 asymmetry，不在“离 archetype 远近”，而在 residual 有没有压成一个 coherent pocket

如果只看
“附近有没有邻居”，
两条线
其实都不孤独：

- `partialmean_core`
  direct ring
  最近也有：
  - `001610`
  - `001639`
  - `000759`
  - `001494`
  - `000207`
  - `000266`
- `000697`
  周围也有：
  - `000904`
  - `000207 / 000216`
  - `001079 / 001494`
  - `000219`

但这不是重点。

真正的差别在于：

1. `000799` 线
   - 主 residual
     会压成：
     - `target share + target mean`
       的 cohesive collapse
   - 所以
     `000681`
     能稳定留在 core
   - 其他近邻
     大多只能踩到
     单轴或次级轴
2. `000697` 线
   - 主 residual
     是多条件 conjunction
   - 每个近邻
     都只接住
     其中一部分
   - 所以
     核心始终无法
     收缩成
     `2-row`
     或
     `3-row`
     的 tight pocket

因此，
当前最稳的
route-level 结论
应固定写成：

- `000799`
  线：
  - stable companion route
  - core 是
    cohesive target-transient-collapse micro-pocket
- `000697`
  线：
  - singleton-core route
  - core 是
    distributed conjunction
    而不是
    单 pocket

## 结论

本轮把
两条 false-positive route
的非对称性
正式定型了：

1. `000799`
   能稳定收缩成
   `000799 + 000681`
   的原因，
   不是因为
   它比
   `000697`
   “更 sink”，
   而是因为
   它的主 residual
   已经压成
   一个足够干净的
   target-transient-collapse
   micro-pocket
2. `000697`
   之所以长期维持
   singleton core，
   不是因为
   没有 support，
   而是因为
   support 被拆成了：
   - extreme support
   - shortgain branch
   - shortshare / offset branch
   没有任何一条
   能整块接住 core conjunction

所以后续默认口径
改成：

- `000799`
  线：
  - 继续沿
    `000799 <-> 000681`
    这条
    cohesive micro-pocket
    写
  - `001610 / 000207 / 000266`
    只作为
    loose shadow
    或
    partial support
- `000697`
  线：
  - 不再继续做
    tighter companion search
  - 继续按
    singleton-core mechanism
    解释
  - 只讨论
    每条 partial route
    为什么接不住
    core conjunction

本轮未启动新训练。
