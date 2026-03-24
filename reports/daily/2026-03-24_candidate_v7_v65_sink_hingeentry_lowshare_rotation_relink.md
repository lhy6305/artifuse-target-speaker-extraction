# 2026-03-24 `candidate_v7` `v65` sink hinge-entry lowshare rotation relink

## 背景

上一轮已经把
`001610`
和
`000207 / 000216`
这两条都最近
`000799`
的 outer side route
正式拆开：

- `001610`
  = hinge-entry shadow
- `000207`
  = tight shortgain projection
- `000216`
  = broad shortgain support

但那一步
只完成了
“先拆开”
这半步，
还没有把
`001610`
重新接回
它原来更像的
那条旧 route：

- hinge-entry
- low-share rotation

也就是说，
如果这一步
不继续往下压，
当前口径里
还是会留下一个
悬空点：

1. `001610`
   虽然已经不再借名
   `shortgain`
2. 但它
   到底朝哪一侧
   继续展开
3. `000664`
   到底是不是
   它的本地 continuation

所以本轮
不回到
`000799 <-> 000681`
的 core，
也不扩新 coverage，
只继续回答
一个更窄的问题：

1. `001610`
   的最近 continuation
   是不是
   `000664`
2. 如果是，
   `000664`
   应该挂成：
   - shortgain 投影
   - shared-target 软 hinge
   - 还是 low-share rotation
3. 这条 relink
   在
   `001610`
   局部邻域里
   最稳定的 support
   又是哪两个轴

## 本轮做法

这一步仍然只做
旧 rows 重路由，
不加新训练。

本轮新落五份 summary：

1. `001610`
   本地邻域 scan
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre001610_neighbor_scan/summary.json`
2. `001610`
   的 route split
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_hingeentry_rotation_split/summary.json`
3. `000664`
   在四条 side route
   之间的 positioning
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_side_route_positioning/summary.json`
4. `000664`
   相对
   `001610`
   与
   shortgain 支线
   的 factor contrast
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_lowshare_v64only_vs_shortgain_factor_contrast/summary.json`
5. `later offset + longer target duration`
   象限图
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_lowshare_v64only_offset_targetdur_quadrants/summary.json`

本轮 group
直接固定成：

- `partialmean_outer_anchor`
  = `000799`
- `outer_hinge_entry_shadow`
  = `001610`
- `lowshare_v64only_rotation`
  = `000664`
- `outer_shortgain_projection`
  = `000207 / 000216`
- `shared_target_soft_hinge`
  = `001705`

也就是：

- 先以
  `001610`
  本人做 seed，
  看它最先接到谁
- 再反过来
  用
  `000664`
  做 focus case，
  看它最近的是
  哪条 reference route
- 最后再单独验证：
  `000664`
  和
  `000207 / 000216`
  到底分在哪些轴上

## 结果

### 1. `000664` 是 `001610` 本地邻域里的第一近邻，不是 `000207`

先看
`pre001610_neighbor_scan`。

`001610`
向外看的
前几名近邻
已经很清楚：

1. `000664`
   - `metadata_distance_z = 1.7331684512698804`
2. `000759`
   - `metadata_distance_z = 2.0366880961002787`
3. `001639`
   - `metadata_distance_z = 2.242649199021557`
4. `000799`
   - `metadata_distance_z = 2.4907638851289584`
5. `000681`
   - `metadata_distance_z = 2.7303560655762698`

而
`000207`
直到更后面
才出现：

- `000207`
  - `metadata_distance_z = 3.5746658777249367`

这件事的含义
已经不是：

- `000664`
  也在附近

而是：

- 当 seed
  真正切到
  `001610`
  本人时，
  它最先接到的
  continuation
  就是
  `000664`
- `000207`
  并不是
  `001610`
  的 tighter continuation，
  只是在
  `000799`
  那一层
  也会投到外圈

所以到这一步，
`001610`
已经不能再被写成：

- 一个
  只相对
  `000799`
  成立、
  但没有自己后续的
  悬空 shadow

它已经有了
明确的本地 continuation：

- `001610 -> 000664`

### 2. `000664` 最近的 route center 是 `001610`，不是 shortgain，也不是 shared-target 软 hinge

再看
`pre000664_side_route_positioning`。

`000664`
相对四条 route
的排序是：

1. `outer_hinge_entry_shadow`
   - `distance_total_z = 4.208998269997649`
2. `shared_target_soft_hinge`
   - `distance_total_z = 5.565737132187143`
3. `outer_shortgain_projection`
   - `distance_total_z = 5.622756731678016`
4. `partialmean_outer_anchor`

而且它相对
第二名的 margin
也不小：

- `distance_margin_vs_second_best = 1.356738862189494`

也就是：

- `000664`
  不是勉强挤在
  `001610`
  这条 route
  和别的 route
  中间
- 它现在
  最近的 reference
  已经稳定回到
  `outer_hinge_entry_shadow`

同时，
它相对
`001610`
的主要偏移
也不是
shortgain 那种
方向：

- `gap::v20>v24`
  - `+2.927254644124986 z`
- `interference_transient_presence_minus_mid_db_mean`
  - `+1.2373412716602243 z`
- `interference_layers.0.start_offset_sec`
  - `+1.125170041518005 z`
- `target_transient_presence_minus_mid_db_mean`
  - `+1.1232265029372253 z`
- `gap::v66>v65`
  - `+1.088373868955691 z`

这组偏移
更像：

- 在
  `001610`
  那条 hinge-entry
  线上
  继续向外做
  一次 rotation
- 而不是
  掉进
  `000207 / 000216`
  那种
  low-gain shortgain
  外投影

所以：

- `000664`
  当前应该明确重挂成
  `001610`
  的 continuation
- 不是
  shared-target soft hinge
- 也不是
  outer shortgain projection

### 3. `000664` 相对 shortgain 的专属轴已固定成：更晚 offset + 更长 reference + 更高 gain

看
`lowshare_v64only_vs_shortgain_factor_contrast`，
如果把：

- `000664`
  当 target group
- `001610`
  当 baseline
- `000207 / 000216`
  当 contrast

那么
`000664`
相对 shortgain
最稳定的几根专属轴
已经固定成：

1. `interference_layers.0.start_offset_sec`
   - `abs_target_specific_residual_z = 2.2304841411268685`
2. `reference_duration_sec`
   - `abs_target_specific_residual_z = 2.2038212708458467`
3. `interference_layers.0.gain_db`
   - `abs_target_specific_residual_z = 2.182707689111641`
4. `target_duration_sec`
   - `abs_target_specific_residual_z = 0.9657341699694753`
5. `interference_transient_presence_share_mean`
   - `abs_target_specific_residual_z = 0.9366441847376811`

把方向翻回
原始值后，
实际口径就是：

- `000664`
  比
  `000207 / 000216`
  更晚 offset
- `000664`
  比
  `000207 / 000216`
  更长 reference
- `000664`
  比
  `000207 / 000216`
  高得多的 gain
  或者说
  没那么 low-gain
- `000664`
  还有
  略长一点的
  target duration
- 同时
  它的
  interference share
  比 shortgain
  更低

这刚好说明：

- `000664`
  不是
  `001610`
  的 “再浅一层 low-gain 版本”
- 它也不是
  shortgain branch
  在
  `001610`
  邻域里的
  另一个点

相反，
它更像是：

- 在
  `001610`
  已经具备的
  later-offset
  方向上
  继续转出去
- 再带上
  更长 duration
  和更低 share

也就是：

- hinge-entry
  向
  low-share rotation
  的 continuation

### 4. `later offset + longer target duration` 是 `001610 -> 000664` 当前最干净的局部 support pair

再看
`lowshare_v64only_offset_targetdur_quadrants`。

这一步
用的两根轴
是：

- factor A
  = `interference_layers.0.start_offset_sec`
- factor B
  = `target_duration_sec`

anchor quadrant
结果很干净：

- `000664`
  在 `both`
  - `offset = 0.298`
  - `target_duration = 1.23`
- `001610`
  在 `neither`
  - `offset = 0.213`
  - `target_duration = 1.08`
- `000207 / 000216`
  在 `neither`
  - `offset = 0.1295`
  - `target_duration = 1.08`

更关键的是，
整个邻域里：

- `both`
  只有两个点：
  - `000664`
  - `000117`
- `factor_a_only`
  为空
- `factor_b_only`
  虽然有：
  - `000799`
  - `000266`
  - `000697`
  - `000759`
  - `001639`
  等
  但都没有同时守住
  `later offset`
- `neither`
  则明确包含：
  - `000207`
  - `000216`

也就是说，
在
`001610`
的 local ring
里，
当前最稳定的
support pair
已经可以固定成：

- later offset
- longer target duration

而这对组合
恰好把：

- `000664`
  从
  `000207 / 000216`
  那条 shortgain 支线
  里完整拉开

### 5. 到这一步，`001610` 这条外圈支路已经可以不再悬空记账

把前面几层结果
合起来后，
`000799`
外侧的结构
现在已经能再收紧一层：

1. stable core
   - `000799`
     = outer barrier anchor
   - `000681`
     = inner depth companion
2. side-route A
   - `001610`
     = outer-anchor-facing hinge-entry shadow
   - `000664`
     = low-share `v64_only` rotation
3. side-route B
   - `000207`
     = tight shortgain projection
   - `000216`
     = broad shortgain support
4. archetype-side route
   - `000266`
     = floor hinge

这一步最重要的
不是新增了
一个 case，
而是把
`001610`
从
“已经与 shortgain 拆开，
但还没重新接回旧 route”
的悬空状态，
正式改成：

- 一条已经有
  continuation
  的 side-route

所以后续
默认不再把
`001610`
写成：

- 单点 hinge-entry shadow

而应直接写成：

- `001610 -> 000664`
  这条
  hinge-entry / low-share rotation
  continuation

## 结论

本轮把
`001610`
这条 outer-anchor-facing route
正式接回了
`000664`
这条旧的
low-share rotation：

1. `000664`
   是
   `001610`
   局部邻域里的
   第一近邻，
   不是
   `000207`
2. `000664`
   最近的 route center
   也稳定是
   `outer_hinge_entry_shadow`，
   不是
   shortgain，
   也不是
   shared-target soft hinge
3. `000664`
   相对 shortgain
   的专属轴
   已固定成：
   - 更晚 offset
   - 更长 reference
   - 更高 gain
   再加上
   - 略长 target duration
   - 更低 interference share
4. `later offset + longer target duration`
   是当前
   `001610 -> 000664`
   最干净的局部 support pair

所以当前
`000799`
线
默认应继续写成：

- `000799`
  = outer barrier anchor
- `000681`
  = inner depth companion
- `001610`
  = outer-anchor-facing hinge-entry shadow
- `000664`
  = low-share `v64_only` rotation
- `000207`
  = tight shortgain projection
- `000216`
  = broad shortgain support
- `000266`
  = archetype-side floor hinge

本轮未启动新训练。
