# 2026-03-24 `candidate_v7` `v65` sink outer-anchor side-route split

## 背景

上一轮已经把
`000799`
外面的
`loose shadow`
正式拆成：

- `001610`
  = hinge-entry shadow
- `000207`
  = shortgain-side projection
- `000266`
  = archetype-side floor hinge

但到这一步，
`001610`
和
`000207`
虽然已经不再被写成
同一种 shadow，
却还停留在：

- “都最近 `000799`”

这一层。

如果后续不再往下压，
就还是会留下一个
模糊口径：

- 它们是不是
  同一路
  barrier-facing shadow
  的两个深浅

所以本轮不回到
`000266`
线，
也不扩新 coverage，
只继续回答一个更窄的问题：

1. `001610`
   和
   `000207 / 000216`
   到底是不是
   同一路 shadow
2. 如果不是，
   它们各自的
   side-route signature
   到底是什么
3. `000799`
   邻域里
   哪些 row
   会支持
   这两条 side route

## 本轮做法

这一步仍然只做
旧 rows 重路由，
不加新训练。

本轮新落五份 summary：

1. `side route split`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_outer_anchor_side_route_split/summary.json`
2. `000799`
   邻域 scan
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_outer_anchor_neighbor_scan/summary.json`
3. `001610`
   对
   `000207 / 000216`
   factor contrast
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_outer_hinge_entry_vs_shortgain_factor_contrast/summary.json`
4. `000207 / 000216`
   对
   `001610`
   factor contrast
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_outer_shortgain_vs_hinge_entry_factor_contrast/summary.json`
5. 两张象限图：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_outer_hinge_entry_offset_gain_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_outer_shortgain_gain_intshare_quadrants/summary.json`

本轮 group
不再沿用
`loose shadow`
聚合口径，
而是直接拆成：

- `partialmean_outer_anchor`
  = `000799`
- `outer_hinge_entry_shadow`
  = `001610`
- `outer_shortgain_projection`
  = `000207 / 000216`
- `archetype_floor_hinge`
  = `000266`

也就是：

- 先把
  `000207`
  真正挂回
  `000207 / 000216`
  这条已有短 gain 支线
- 再看它和
  `001610`
  的差异
  到底落在哪些轴上

## 结果

### 1. `001610` 和 `000207 / 000216` 不是同一路 shadow 的两个深浅；它们的第一分界已经固定成：更高 gain + 更晚 offset vs 更低 gain + 更短 reference

看
`outer_hinge_entry_vs_shortgain_factor_contrast`
，
以
`000799`
为 baseline，
`001610`
相对
`000207 / 000216`
的专属残差
前三位是：

1. `interference_layers.0.gain_db`
   - `+2.5731 z`
2. `interference_layers.0.start_offset_sec`
   - `+2.0286 z`
3. `reference_duration_sec`
   - `+1.5872 z`

也就是：

- `001610`
  相对
  shortgain 支线
  的独特之处
  不是：
  - target 更深
  - share 更塌
- 而是：
  - gain 更高
  - offset 更晚
  - reference 更长

反过来看
`outer_shortgain_vs_hinge_entry_factor_contrast`
，
`000207 / 000216`
相对
`001610`
的前三位
完全镜像回来：

1. `interference_layers.0.gain_db`
   - `-2.5731 z`
2. `interference_layers.0.start_offset_sec`
   - `-2.0286 z`
3. `reference_duration_sec`
   - `-1.5872 z`

所以这一步已经足够明确：

- `001610`
  这条 side route
  的第一主轴
  是：
  - higher gain
  - later offset
  - longer reference
- `000207 / 000216`
  这条 side route
  的第一主轴
  则是：
  - lower gain
  - earlier overlap
  - shorter reference

它们不是
同一条 shadow
的深浅差，
而是两套
相反方向的
route signature。

### 2. `001610` 的 side-route geometry 已经固定成 `late offset + higher gain`；而且它会自然接到 `000664`，不接到 shortgain 支线

看
`outer_hinge_entry_offset_gain_quadrants`
：

- baseline
  `000799`
  在：
  - `neither`
- target
  `001610`
  在：
  - `both`
- contrast
  `000207 / 000216`
  在：
  - `neither`

这里两轴就是：

- factor A
  = `offset` 更晚
- factor B
  = `gain` 更高

也就是：

- `001610`
  不是靠
  shortgain 那套
  low-gain 轴
  靠近 `000799`
- 它是沿着：
  - late offset
  - higher gain
  这条门口旋转线
  贴到 barrier 外沿

更关键的是，
`both`
象限里
除了
`001610`
之外，
还会出现：

- `000664`
  (`v64_only_crossed`)
- `000951`
  (`pre_entry_or_pure`)

其中
`000664`
正好和更早的
`001610 -> 000664`
那条
low-share rotation
旧结论对上：

- `001610`
  外侧这条 shadow
  不是会自然
  滑进
  `000207 / 000216`
  shortgain 支线
- 它更像继续沿：
  - late offset
  - higher gain
  这条轴
  转向
  `000664`
  那边

所以
`001610`
当前最稳的固定写法
应再收紧成：

- outer-anchor-facing
  hinge-entry shadow
- low-share route
  在 barrier 外沿的入口点

### 3. `000207 / 000216` 的 side-route 不是 generic low-gain shadow；它已经固定成 `low gain + high interference share + shorter reference` 的 shortgain 支线

虽然
前三位残差
已经把
`low gain + earlier overlap + shorter reference`
写出来了，
但只看前三位
还不够，
因为
`000207 / 000216`
并不是单纯
“gain 更低”。

在同一个
`outer_shortgain_vs_hinge_entry_factor_contrast`
里，
接下来的字段
还包括：

- `interference_transient_presence_minus_mid_db_mean`
  - `+1.5123 z`
- `target_transient_presence_minus_mid_db_mean`
  - `+1.3074 z`
- `target_transient_presence_share_mean`
  - `+1.2397 z`
- `interference_transient_presence_share_mean`
  - `+1.2293 z`

这说明：

- `000207 / 000216`
  相对
  `001610`
  的专属方向
  不是：
  - gain 单轴
- 而是：
  - lower gain
  - shorter reference
  - higher interference share
  - 更高的
    target / interference
    transient 残留

也就是，
它们确实更像：

- `000697`
  线里
  之前已经落盘的
  `shortgain neighbor`

而不是：

- `000799`
  门口
  被 offset
  旋走的那类
  hinge-entry shadow

### 4. `000207` 才是当前真正踩进 outer ring 的 shortgain 投影，`000216` 只是这条支线的 broad support

看
`outer_shortgain_gain_intshare_quadrants`
：

- target
  `000207 / 000216`
  的 group anchor
  在：
  - `both`
- contrast
  `001610`
  在：
  - `neither`

这里两轴是：

- factor A
  = `gain` 更低
- factor B
  = `interference share` 更高

但把邻域 rows
展开后会看到：

- `000207`
  在：
  - `both`
- `000216`
  只在：
  - `factor_a_only`

这说明：

- `000207`
  是当前真正
  把 shortgain 签名
  投影进
  `000799`
  outer ring
  的那一条 row
- `000216`
  虽然和它同路，
  但目前只守住：
  - low gain
  还没有一起守住：
  - high interference share

因此，
这条支线内部
也不应再写成：

- 两条完全对称的
  outer-ring twin

更稳的写法是：

- `000207`
  = tight outer-ring projection
- `000216`
  = broad shortgain support

### 5. `000266` 会误踩进 shortgain 的 `gain + intshare` 象限；这反过来说明 shortgain route 不能只用两轴命名，必须带上 reference 缩短

同一张
`outer_shortgain_gain_intshare_quadrants`
里，
`both`
象限
还出现了：

- `000266`

但这并不代表：

- `000266`
  也属于
  shortgain 支线

它只是再次说明：

- `low gain + high interference share`
  这对轴
  本身
  还不够唯一

必须和
上一节 factor contrast
里的：

- `reference_duration_sec`
  明显更短

一起看，
shortgain route
才会收紧成：

- low gain
- higher interference share
- shorter reference

所以：

- `000266`
  继续固定在
  archetype floor hinge
  口径下
- `000207 / 000216`
  则固定回
  shortgain 支线

### 6. 这一步之后，`000799` 邻域里的两条 side route 已经可以不再互相借名

把前几轮结果
合起来后，
现在
`000799`
这条 route
外侧的结构
已经能再收紧一层：

1. stable core
   - `000799`
     = outer barrier anchor
   - `000681`
     = inner depth companion
2. outer side route A
   - `001610`
     = hinge-entry shadow
   - 向外继续接：
     - `000664`
       这类
       low-share rotation
3. outer side route B
   - `000207`
     = tight shortgain projection
   - `000216`
     = broad shortgain support
4. archetype-side projection
   - `000266`
     = floor hinge

也就是：

- `001610`
  不再借名
  `shortgain`
- `000207`
  也不再借名
  `hinge-entry`

这两条 side route
现在已经足够独立，
可以直接按各自
已知旧路线
继续记账。

## 结论

本轮把
`000799`
外侧两条主要 side route
正式拉开了：

1. `001610`
   不是
   `000207`
   的同类 shadow，
   它的专属轴
   已固定成：
   - higher gain
   - later offset
   - longer reference
   所以应继续挂在：
   - hinge-entry / low-share rotation
     这条线
2. `000207 / 000216`
   则不是
   `001610`
   的浅层版本，
   它们的专属轴
   已固定成：
   - lower gain
   - higher interference share
   - shorter reference
   所以应继续挂在：
   - shortgain side-route
3. 其中：
   - `000207`
     是 tight outer-ring projection
   - `000216`
     只是 broad support

所以后续
`000799`
线
默认应继续写成：

- `000799`
  = outer barrier anchor
- `000681`
  = inner depth companion
- `001610`
  = hinge-entry shadow
- `000207`
  = tight shortgain projection
- `000216`
  = broad shortgain support
- `000266`
  = archetype-side floor hinge

本轮未启动新训练。
