# 2026-03-24 `candidate_v7` `v65` sink partialmean barrier-depth mechanics

## 背景

上一轮已经把
`000799 <-> 000681`
这对 stable core
正式拆成：

- `000799`
  = outer anchor
- `000681`
  = inner companion
- `001610 / 000207 / 000266`
  = loose shadow

并确认：

- `000799`
  和 shadow
  的第一道边界
  是：
  - `target share collapse`
- `000681`
  则比
  `000799`
  再往里压一层，
  让 shadow
  连更深的 mean
  也够不到

但这一步还只是
给出了
role label，
还没有把
最关键的 mechanics
写透：

1. 为什么
   `000799`
   更像 barrier，
   而不是
   “稍浅一点的 companion”
2. 为什么
   `000681`
   更像 depth，
   而不是
   “另一个 barrier anchor”
3. 为什么
   loose shadow
   会稳定卡在
   这两层外面

所以本轮不再扩样本，
也不回到
`000697`
线，
只继续压实：

- `000799`
  这条 partialmean-core route
  的
  barrier vs depth
  mechanics

## 本轮做法

这一步仍是
旧 rows 重路由，
不是新 coverage。

本轮不加新训练，
只把四类已有结果
收进同一张解释图：

1. `core role split`
   group split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_role_split/summary.json`
2. `000799 -> loose_shadow`
   factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_loose_shadow_factor_contrast/summary.json`
3. `000681 -> loose_shadow`
   factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_loose_shadow_factor_contrast/summary.json`
4. `share + mean`
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_loose_shadow_targetshare_targetmean_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_loose_shadow_targetshare_targetmean_quadrants/summary.json`
5. 更早已经落盘的
   `000799 vs 000681`
   reverse contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_000681_factor_contrast/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_000799_factor_contrast/summary.json`

本轮只回答三个窄问题：

1. outer anchor
   的核心职责
   到底是什么
2. inner companion
   的核心职责
   到底是什么
3. loose shadow
   为什么会稳定卡在
   barrier 外面

## 结果

### 1. `000799` 的主职责不是把 mean 压到最深，而是把 shadow 已经摸到的 mean-side 外圈拦在 share barrier 外面

看
`pre000799_vs_loose_shadow_factor_contrast`
，
排前字段依次是：

1. `target_transient_presence_share_mean`
   - `target_specific_residual_z = -1.9719`
2. `target_interference_logspec_cosine`
   - `-1.7706`
3. `interference_transient_presence_minus_mid_db_mean`
   - `-1.5968`
4. `interference_transient_presence_share_mean`
   - `-1.5570`
5. `reference_duration_sec`
   - `+1.2691`

而
`target_transient_presence_minus_mid_db_mean`
只排到更后面，
`z`
也只有：

- `+0.3510`

这已经说明：

- 对
  `000799`
  来说，
  真正把它和
  loose shadow
  拉开的
  不是：
  - mean
    再继续下压
- 而是：
  - share-collapse barrier
    本身
  - 再配合：
    - 更低 cosine
    - 更弱 interference package

所以：

- `000799`
  不是
  “离 shadow
  最远的那个 core row”
- 它更像：
  - shadow
    已经摸到外圈后，
    最先撞到的
    barrier row

### 2. `000799` 对 shadow 的 `share + mean` 象限，直接把这层 barrier 的几何结构写出来了：shadow 已经有 mean，但还没有 share

看
`pre000799_vs_loose_shadow_targetshare_targetmean_quadrants`
：

- `000799`
  在：
  - `both`
- `loose_shadow`
  在：
  - `factor_b_only`

这里：

- `factor_a`
  是
  `target share`
- `factor_b`
  是
  `target mean`

也就是：

- 对
  `000799`
  这层来说，
  shadow
  已经能落在：
  - lower mean
    这一侧
- 但 shadow
  仍然落不进：
  - share collapse

而且这个读法
不只来自
三条 loose shadow：

- 象限里的
  `factor_b_only`
  其实还有：
  - `001639`
  - `001494`

这说明：

- 靠近
  mean-side 外圈
  的 row
  并不少
- 真正稀缺的
  仍然是：
  - share-collapse

因此：

- `000799`
  的 mechanics
  最稳的固定写法
  应该是：
  - 它守住的是
    mean 外圈
    到 share-collapse core
    的第一道门槛

### 3. `000681` 的职责则完全不同：它不是第二道 share 门，而是在 share 门之后，把 mean depth 再往内压深一层

看
`pre000681_vs_loose_shadow_factor_contrast`
，
排前字段变成：

1. `target_transient_presence_share_mean`
   - `target_specific_residual_z = -2.4281`
2. `target_transient_presence_minus_mid_db_mean`
   - `-2.2214`
3. `interference_layers.0.start_offset_sec`
   - `-1.7572`
4. `interference_layers.0.gain_db`
   - `+1.2309`

和
`000799`
最不一样的
地方就在这里：

- `000799`
  对 shadow
  的第一主导项
  是：
  - share
- `000681`
  对 shadow
  的第一主导项
  仍然有：
  - share
  但第二主导项
  立即变成：
  - 更深的 mean

这代表：

- `000681`
  不是在重复
  `000799`
  的 barrier role
- 它更像：
  - 通过更深 pre
  - 更短 reference
  - 更深 mean collapse
  把 core
  从 barrier
  再向内压了一层

### 4. `000681` 对 shadow 的 `share + mean` 象限里，shadow 直接退到 `neither`；这就是 inner companion 的直接证据

看
`pre000681_vs_loose_shadow_targetshare_targetmean_quadrants`
：

- `000681`
  在：
  - `both`
- `loose_shadow`
  在：
  - `neither`

这和
`000799`
那张图
形成了
稳定而清晰的
role split：

1. 对
   `000799`
   来说，
   shadow
   还能留在：
   - `factor_b_only`
   说明它还站在
   mean 外圈
2. 对
   `000681`
   来说，
   shadow
   连：
   - mean
   - share
   都一起退掉

这意味着：

- `000681`
  不是 shadow
  一步之内
  能贴到的层级
- 它已经属于：
  - barrier 内侧
    的 deeper core depth

所以：

- `000681`
  最稳口径
  就应该固定写成：
  - inner companion

### 5. 反过来看 `000799 vs 000681` 的 pair contrast，更能说明它们是“同 core 的两层”，而不是“两条不同 core”

更早的
`000799 vs 000681`
reverse contrast
已经说明：

- 双边最前的字段
  始终是：
  - `reference_duration_sec`
  - `target_transient_presence_minus_mid_db_mean`
  - `interference_layers.0.gain_db`
- `target_transient_presence_share_mean`
  几乎不动

而
`partialmean_core_role_split`
里
`partialmean_target_minus_partialmean_companion`
的 pair delta
也完全对上：

- `target_transient_presence_share_mean`
  - 只差
    `+0.000386`
- `target_transient_presence_minus_mid_db_mean`
  - `+6.529472`
- `reference_duration_sec`
  - `+1.14 sec`
- `interference_layers.0.gain_db`
  - `-2.068 dB`

这说明：

- `000799`
  和
  `000681`
  并不是
  在 core identity
  上分叉
- 它们共享的
  仍然是：
  - share-collapse core
- 真正有层次差的，
  是：
  - mean depth
  - reference shortening
  - deeper-pre margin

所以：

- 两者不是
  两个不同 pocket
- 而是
  同一个 pocket
  的两层结构

### 6. loose shadow 之所以始终卡在外面，不是因为“还不够像 core”，而是因为它只占到外圈 support，既穿不过 barrier，也够不到 depth

把前几轮结果
合起来看，
loose shadow
目前稳定停留在：

1. 它共享：
   - lower mean
   - shorter duration
   外圈
2. 它缺：
   - share collapse
3. 它更缺：
   - inner companion
     那层的
     deeper mean depth

也就是说，
它不是单纯
“往 core 继续靠一点”
的问题。

它被两层机制
一起挡在外面：

1. `000799`
   的 outer barrier
   先卡住：
   - share collapse
2. `000681`
   的 inner depth
   再卡住：
   - deeper mean collapse

所以
loose shadow
现在最稳的固定写法
应是：

- outer-ring support
- mixed-source projection
- not-yet-through-barrier
- not-even-near-depth

## 结论

本轮把
`000799`
这条 partialmean-core route
的 mechanics
正式写透了：

1. `000799`
   不是“较浅 companion”，
   而是：
   - outer anchor
   - share-collapse barrier
2. `000681`
   不是“第二个壳边 anchor”，
   而是：
   - inner companion
   - barrier 内侧的
     deeper mean depth
3. loose shadow
   之所以始终扩不进 core，
   不是因为
   它还不够像，
   而是因为：
   - 先过不掉
     `000799`
     的 share barrier
   - 再够不到
     `000681`
     的 depth layer

所以后续
`000799`
线
默认再收紧成：

- `000799`
  = outer barrier anchor
- `000681`
  = inner depth companion
- `001610 / 000207 / 000266`
  = outer-ring loose shadow

本轮未启动新训练。
