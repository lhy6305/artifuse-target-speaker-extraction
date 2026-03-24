# 2026-03-24 `candidate_v7` `v65` sink lowshare rotation local fanout

## 背景

上一轮已经把
`001610 -> 000664`
正式接上，
当前口径也已经固定成：

- `001610`
  = outer-anchor-facing hinge-entry shadow
- `000664`
  = low-share `v64_only` rotation

但把这条 route
接上之后，
还剩下一个
更窄的问题
没有回答：

1. `000664`
   自己周围
   有没有
   tight local companion
2. 如果没有，
   它附近的最近邻
   到底是在：
   - 支持
     `000664`
     这条 local pocket
   - 还是已经开始
     分流到别的 branch

这个问题必须先压实，
因为如果
`000664`
本地还能继续收成
双核，
后续就该沿
companion route
继续记账；
但如果它周围
其实已经是
分叉结构，
那后续口径就必须改成：

- `000664`
  是一个 rotation hub
  或 local fanout

所以本轮
不回到
`001610`
那一层，
也不重做
`000697 / 001543`
旧对照，
只继续回答：

1. `000664`
   窄 ring
   里
   有没有第二条
   真正同状态
   `v64_only` crossed
2. 最近那批 row
   分别更像：
   - `000664`
     的 loose support
   - upstream shell
   - 还是 downstream branch

## 本轮做法

这一步仍然只做
旧 rows 重路由，
不加新训练。

本轮新落四份 summary：

1. `000664`
   本地邻域 scan
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_neighbor_scan/summary.json`
2. `000664`
   邻域 signature scan
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_signature_scan/summary.json`
3. `000664`
   周围非锚点近邻的
   local route positioning
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_local_support_positioning/summary.json`
4. `001610 -> 000664`
   support axes
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_hinge_to_rotation_support_axes/summary.json`

本轮 route group
固定成：

- `partialmean_outer_anchor`
  = `000799`
- `outer_hinge_entry_shadow`
  = `001610`
- `lowshare_v64only_rotation`
  = `000664`
- `pre000697_singleton_core`
  = `000697`
- `v65_sink_singleton`
  = `001543`
- `post_entry_v64_deeper_than_v65`
  = `001745`

也就是：

- 先看
  `000664`
  周围最近
  20 条 row
  到底是什么 state
- 再把其中
  非锚点近邻
  放回已有 route center
  之间做 positioning
- 最后单独验证：
  那批最像 support 的 row
  究竟是不是
  真在
  `001610 -> 000664`
  这条 path 上

## 结果

### 1. `000664` 的前 20 近邻里，没有第二条 `v64_only` crossed；它周围首先出现的是大量 pre-shell，其次才是 downstream 分支

先看
`pre000664_neighbor_scan`
和
`pre000664_signature_scan`。

`000664`
向外看的
前十个近邻是：

1. `001610`
   - `metadata_distance_z = 1.7331684512698804`
2. `000759`
   - `metadata_distance_z = 2.055266580227977`
3. `001639`
   - `metadata_distance_z = 2.5600567263216853`
4. `000117`
   - `metadata_distance_z = 2.874619151269278`
5. `001725`
   - `metadata_distance_z = 2.996327672986455`
6. `000799`
   - `metadata_distance_z = 3.0777659151205734`
7. `001745`
   - `metadata_distance_z = 3.388150938657853`
8. `000697`
   - `metadata_distance_z = 3.4334234361997367`
9. `001543`
   - `metadata_distance_z = 3.448212722469956`
10. `001006`
   - `metadata_distance_z = 3.4710463847604527`

而同一批 top-20
做 signature scan 后，
bucket 直接收成：

- `pre_entry_or_pure = 16`
- `hinge_secondary_crossed_first = 2`
- `post_entry_both_crossed_reference_deeper = 1`
- `post_entry_both_crossed_secondary_deeper_or_equal = 1`
- `reference_only_crossed_unexpected = 0`

这件事的含义
非常直接：

- `000664`
  周围没有
  第二条新的
  `v64_only` crossed
  近邻
- 它最近那圈
  先被
  大量 pre-shell
  占满
- 真正 crossed 的
  downstream row
  反而只有：
  - `001745`
  - `001543`

也就是说，
`000664`
当前不是
一个会自然收成
双核 pocket
的中心；
它周围最近出现的
不是第二个
同状态 companion，
而是：

- upstream pre-shell
- 加上少量 downstream branch

### 2. `000759` 是最像 `000664` 的 loose bridge，但它和 `001610` 的距离几乎没真正拉开，不能升成 tight companion

看
`pre000664_local_support_positioning`，
`000759`
当前最近 group
虽然是：

- `lowshare_v64only_rotation`

但它相对第二名
`outer_hinge_entry_shadow`
的 margin
其实非常小：

- `distance_margin_vs_second_best = 0.09200046913276516`

也就是：

- `000759`
  不是明确落进
  `000664`
  核心内部
- 它更像卡在
  `001610`
  和
  `000664`
  之间的
  一条 loose bridge

这点
在
`hinge_to_rotation_support_axes`
里也很一致：

- metadata-axis
  `transition_ratio = 0.5836996923089257`
- margin-axis
  `transition_ratio = 0.451875933836106`

两条轴
都只走了
大约一半，
而且 residual
仍然不小：

- metadata residual
  `= 2.742919004223096`
- margin residual
  `= 2.7681440509298105`

所以：

- `000759`
  可以保留成
  `001610 -> 000664`
  的 broad bridge support
- 但它不足以升格成
  `000664`
  的 tight companion

### 3. `001639` 没有继续贴住 `000664`；它会回落到 `000799` 那侧 outer shell

同样看
`pre000664_local_support_positioning`，
`001639`
最近的 group
不是
`lowshare_v64only_rotation`，
而是：

- `partialmean_outer_anchor`

而且
margin
已经不算小：

- `distance_margin_vs_second_best = 0.4861444259279706`

这说明：

- `001639`
  不是
  `000664`
  这条 low-share rotation
  的 local support
- 它更像会重新回贴
  `000799`
  那个 outer shell

`hinge_to_rotation_support_axes`
里，
它相对
`001610 -> 000664`
这条 path
也明显不稳：

- metadata-axis
  `transition_ratio = 0.29345136028823365`
- margin-axis
  `transition_ratio = -1.8051132392903904`

也就是：

- metadata
  只走了
  一小段
- margin
  则明显不沿
  `001610 -> 000664`
  方向前进

所以：

- `001639`
  不应再被写成
  `000664`
  的 local support
- 它更像
  outer-anchor side
  的 fallback row

### 4. `000117 / 001725 / 001006` 虽然还停在 pre-entry_or_pure，但 geometry 已经更像 sink-facing shell，不像 `000664` companion

这一步最有用的
其实不是
最近谁，
而是：

- 那些一眼看上去
  “也许还能当 support”
  的 row
  到底贴向哪一边

positioning 结果里，
下面三条都最近：

- `000117`
  -> `v65_sink_singleton`
  - `distance_margin_vs_second_best = 0.6763298319660573`
- `001725`
  -> `v65_sink_singleton`
  - `distance_margin_vs_second_best = 0.49910195025322857`
- `001006`
  -> `v65_sink_singleton`
  - `distance_margin_vs_second_best = 0.35640140685297705`

注意，
它们在
signature scan
里
仍属于：

- `pre_entry_or_pure`

这正好说明：

- 这几条 row
  不是
  `000664`
  的同状态 companion
- 它们也不是
  已经 crossed
  的 sink core
- 它们更像：
  还没真正越线，
  但几何位置
  已经开始贴向
  `001543`
  那条 sink-facing shell

所以这几条
应继续记成：

- sink-side broad shell
  或 sink-facing outer support

而不是：

- `000664`
  的 tight local support

### 5. `001543 / 001745 / 000697` 出现在同一圈，不是在帮 `000664` 收核，而是在提醒它已经开始向三条 downstream 方向分流

把
neighbor scan
和
signature scan
合起来看，
在
`000664`
这圈里，
真正 crossed
的 downstream row
只有两条：

- `001745`
  = `post_entry_both_crossed_reference_deeper`
  - `metadata_distance_z = 3.388150938657853`
- `001543`
  = `post_entry_both_crossed_secondary_deeper_or_equal`
  - `metadata_distance_z = 3.448212722469956`

同时，
`000697`
也已经进了前十：

- `000697`
  - `metadata_distance_z = 3.4334234361997367`
  - bucket
    仍是
    `pre_entry_or_pure`

这件事
最关键的地方
不是它们“都离 `000664` 不远”，
而是：

- `001543`
  已经代表
  sink branch
- `001745`
  已经代表
  post-entry `v64`-deeper pocket
- `000697`
  则代表
  `000664`
  那条 archetype
  向另一类
  pre singleton core
  的 offshoot

也就是说，
`000664`
附近出现的
不是：

- 一组还会继续帮它
  收成 companion core
  的同类 row

而是：

- 多条已经能各自
  接到下游 branch
  的分流方向

### 6. 到这一步，`000664` 应改写成 local fanout / rotation hub，而不是 low-share pocket 的双核中心

把前面的结果
压在一起后，
现在这条线
已经可以进一步收紧成：

1. upstream
   - `001610`
     = outer-anchor-facing hinge-entry shadow
2. rotation node
   - `000664`
     = low-share `v64_only` rotation
3. loose bridge
   - `000759`
     = hinge-to-rotation broad bridge support
4. outer fallback
   - `001639`
     = outer-anchor fallback
5. sink-facing broad shell
   - `000117 / 001725 / 001006`
6. downstream branches
   - `000697`
     = pre singleton offshoot
   - `001543`
     = sink branch
   - `001745`
     = post-entry `v64`-deeper branch

所以这一步之后，
默认不再把
`000664`
写成：

- low-share route
  里
  还没找完 companion
  的 pocket center

而应写成：

- 一个已经开始向
  pre / sink / post-entry
  三侧分流的
  rotation hub

## 结论

本轮把
`000664`
这一步的本地结构
正式定型了：

1. `000664`
   前 20 近邻里
   没有第二条
   `v64_only` crossed，
   所以当前没有
   tight same-state companion
2. `000759`
   虽然最近 group
   是
   `lowshare_v64only_rotation`，
   但它相对
   `001610`
   的 margin
   只有
   `0.09200046913276516`，
   只能保留为
   broad bridge support
3. `001639`
   不会继续贴住
   `000664`，
   它会回落到
   `000799`
   那侧 outer shell
4. `000117 / 001725 / 001006`
   几何位置
   已更像
   `001543`
   那条 sink-facing shell，
   不应再被写成
   `000664`
   companion
5. `001543 / 001745 / 000697`
   同时进入
   `000664`
   窄 ring，
   说明这一步
   已经不是收核，
   而是开始向
   sink / post-entry / pre
   三个 downstream 方向
   分流

所以当前默认口径
应继续写成：

- `001610`
  = outer-anchor-facing hinge-entry shadow
- `000664`
  = low-share `v64_only` rotation hub
- `000759`
  = hinge-to-rotation broad bridge support
- `001639`
  = outer-anchor fallback
- `000117 / 001725 / 001006`
  = sink-facing broad shell
- `000697`
  = pre singleton offshoot
- `001543`
  = sink branch
- `001745`
  = post-entry `v64`-deeper branch

本轮未启动新训练。
