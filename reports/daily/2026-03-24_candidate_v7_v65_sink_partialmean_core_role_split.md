# 2026-03-24 `candidate_v7` `v65` sink partialmean core role split

## 背景

上一轮已经把
`000799`
这条线
正式拆成：

- stable core
  - `000799 <-> 000681`
- loose shadow
  - `001610 / 000207 / 000266`

并确认：

- shadow
  只能共享：
  - `target mean + short duration`
    外圈
- 接不住：
  - `target share collapse`

但到这里，
stable core
内部还有最后一个
没写透的问题：

- `000799`
  和
  `000681`
  虽然都属于
  同一个 core，
  但它们在这个 core
  里的角色
  并不完全一样

也就是说，
现在需要补的
不是：

- core
  是否成立

而是：

1. `000799`
   在 core 里
   更像什么角色
2. `000681`
   在 core 里
   更像什么角色
3. 为什么
   这两个 row
   虽然角色不同，
   却都能守住
   share-collapse barrier

## 本轮做法

这一步仍是
旧 rows 重路由，
不是新 coverage。

本轮不加新训练，
不扩 neighbor ring，
只把四类已有资产
拼到同一张图里：

1. 上一轮已经落盘的：
   - `partialmean_core_loose_shadow`
     分解
2. companion validation
   已有的：
   - `000799 vs 000681`
     reverse contrast
3. 新补一张
   `core role split`
   group split：
   - `partialmean_archetype`
   - `partialmean_target`
   - `partialmean_companion`
   - `partialmean_loose_shadow`
4. 分别检查：
   - `000799`
     对 loose shadow
     的 barrier
   - `000681`
     对 loose shadow
     的 barrier

本轮新增输出：

1. core role split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_role_split/summary.json`
2. `000799 -> loose_shadow`
   factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_loose_shadow_factor_contrast/summary.json`
3. `000681 -> loose_shadow`
   factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_loose_shadow_factor_contrast/summary.json`
4. `000799 -> loose_shadow`
   `target share + target mean`
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_loose_shadow_targetshare_targetmean_quadrants/summary.json`
5. `000681 -> loose_shadow`
   `target share + target mean`
   quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_loose_shadow_targetshare_targetmean_quadrants/summary.json`

同时继续引用：

- `reports/daily/2026-03-24_candidate_v7_v65_sink_falsepositive_companion_validation.md`
- `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_000681_factor_contrast/summary.json`
- `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_000799_factor_contrast/summary.json`

## 结果

### 1. `000799` 和 `000681` 虽然都在同一个 core 里，但不是对称 twin；更稳的写法是 `000799 = route anchor`，`000681 = deeper companion`

先看
companion validation
已经固定下来的
pair contrast。

`000799 -> 000681`
和
`000681 -> 000799`
两边排前的字段
始终都集中在：

- `reference_duration_sec`
- `target_transient_presence_minus_mid_db_mean`
- `interference_layers.0.gain_db`

而不是：

- `target_transient_presence_share_mean`

这说明：

- 两者并不是
  在
  core identity
  上
  分家
- 它们共享的
  仍然是：
  - target share collapse

真正有分工的，
是：

- 谁更靠近
  shell-facing 边界
- 谁更像
  更深一层的
  pre companion

从已有读数看：

- `000681`
  相对
  `000799`
  是：
  - 更深 pre
  - 更短 reference
  - target mean
    更塌
- `000799`
  相对
  `000681`
  则是：
  - 更靠外层
  - 更像
    core 的 route anchor

所以后续
最稳口径
不应再写成：

- 两个几乎对称的 twin

而应写成：

- `000799`
  = route anchor
- `000681`
  = deeper companion

### 2. `000799` 相对 loose shadow 的关键，不是再多塌一点 mean，而是先把 share-collapse barrier 守住；它是 core 最外层的 anchor

看
`pre000799_vs_loose_shadow_factor_contrast`
，
排前字段是：

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
6. `interference_layers.0.start_offset_sec`
   - `-1.2281`

这里最关键的是：

- 排第一的
  已经不是
  `target mean`
- 而是：
  - `target share`

这和上一轮
shadow decomposition
完全对上。

再看
`pre000799_vs_loose_shadow_targetshare_targetmean_quadrants`
：

- `000799`
  在：
  - `both`
- `loose_shadow`
  在：
  - `factor_b_only`

也就是：

- shadow
  对
  `000799`
  而言，
  已经能踩进：
  - lower target mean
- 但它 still
  接不住：
  - target share collapse

这代表：

- `000799`
  是 stable core
  最外层那道
  share-collapse barrier
- 它离 shadow
  并不是
  “全面都很远”
- 而是：
  - shadow
    已经摸到
    mean-side 外圈
  - 但被
    share-collapse
    卡住了

所以：

- `000799`
  更像
  shell-facing anchor
  而不是
  deeper-pre tail

### 3. `000681` 相对 loose shadow 的关键，则是它不只守住 share，连更深的 mean 也一起守住；它是 stable core 后面那层 deeper companion

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
最不同的地方
就在第二项：

- 对
  `000681`
  而言，
  `target mean`
  又重新变成了
  非常强的分离项

再看
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
正好形成
稳定的 role split：

1. 相对
   `000799`
   - shadow
     还能进：
     - `factor_b_only`
     - 也就是
       mean-side 外圈
2. 相对
   `000681`
   - shadow
     连：
     - mean
     - share
     都不再够得着

所以：

- `000681`
  不是
  “另一个壳边 anchor”
- 它更像：
  - 在 share-collapse
    barrier 之后
  - 再往里压一层
    deeper mean-collapse
    的 companion

### 4. 两个 core row 的真正分工，不是一个守 share、一个守 mean；而是 `000799` 守外层 barrier，`000681` 在 barrier 内部把深度继续拉开

这一步要避免
一个误读：

- 不是说
  `000799`
  只有 share，
  `000681`
  只有 mean

事实不是这样。

两者都在：

- `target share + target mean`
  的
  `both`
  象限里

也就是说：

- 二者都属于
  同一个
  target-collapse core

真正的角色差别是：

1. `000799`
   - 更接近
     shadow 外圈
   - 所以它定义的是：
     - 外层 barrier
   - 典型句式应写成：
     - shadow
       已经摸到 mean，
       但还没摸到 share
2. `000681`
   - 比 `000799`
     再深一层
   - 所以它定义的是：
     - barrier 内部的
       deeper companion depth
   - 典型句式应写成：
     - shadow
       连 share
       和更深 mean
       都不够

因此 stable core
内部最稳的
role split
现在应固定写成：

- `000799`
  = shell-facing anchor
- `000681`
  = deeper companion

### 5. 这也解释了为什么 stable core 只需要两条 row，而不需要把 shadow 再扩进来：因为这两条 row 已经把“外层 barrier”与“内层深度”都占满了

现在把前几轮
结果合起来看：

1. `000799`
   已经把：
   - share-collapse barrier
   占住
2. `000681`
   已经把：
   - 更深 pre
   - 更短 reference
   - 更深 mean collapse
   这一层
   占住
3. `001610 / 000207 / 000266`
   虽然会贴近：
   - mean
   - duration
   外圈，
   但它们
   既不能替代：
   - `000799`
     的 barrier role
   也不能替代：
   - `000681`
     的 deeper role

所以这条 route
现在之所以稳定，
不是因为：

- 只有两个 row
  恰好最像

而是因为：

- 这两个 row
  已经把
  stable core
  需要的两种内部角色
  占满了

这也是为什么
shadow
再怎么贴近，
都不会被自然扩进
core。

## 结论

本轮把
`000799 <-> 000681`
这对 stable core
的内部角色
正式定型了：

1. `000799`
   默认固定写成：
   - shell-facing anchor
   - 它和 shadow
     的真正分界
     首先是
     `target share collapse`
2. `000681`
   默认固定写成：
   - deeper companion
   - 它不是另一个壳边 anchor，
     而是在
     同一条 core
     里把深度
     再往内压一层
3. `001610 / 000207 / 000266`
   默认继续只写成：
   - loose shadow
   因为它们
   既接不住
   `000799`
   的 share barrier，
   也接不住
   `000681`
   的 deeper mean depth

所以后续
`000799`
这条线
默认再收紧成：

- `000799`
  = outer anchor
- `000681`
  = inner companion
- `001610 / 000207 / 000266`
  = mixed-source loose shadow

本轮未启动新训练。
