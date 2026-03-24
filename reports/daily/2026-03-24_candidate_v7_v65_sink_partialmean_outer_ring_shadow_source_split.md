# 2026-03-24 `candidate_v7` `v65` sink partialmean outer-ring shadow source split

## 背景

上一轮已经把
`000799 <-> 000681`
这条 stable core
正式拆成：

- `000799`
  = outer barrier anchor
- `000681`
  = inner depth companion
- `001610 / 000207 / 000266`
  = outer-ring loose shadow

并且已经明确：

- shadow
  过不掉
  `000799`
  的
  `target share collapse`
- shadow
  也够不到
  `000681`
  的
  deeper mean depth

但到这一步，
`loose shadow`
还只是一个
聚合标签。

如果后续还继续把
`001610 / 000207 / 000266`
整包写成：

- 同一路外圈支撑
- 同 pocket 的第三层影子

就会把
outer ring
内部已经存在的
source split
重新抹平。

所以本轮不回到
`000697`
线，
也不做新 coverage，
只继续压实一个更窄的问题：

1. `001610`
   到底更像
   哪一层的 shadow
2. `000207`
   到底是
   outer-anchor shadow，
   还是别的旁路投影
3. `000266`
   为什么一直
   更像 archetype-side
   floor hinge
4. 这三条 row
   为什么能同落外圈，
   却不能写成
   同一路 shadow branch

## 本轮做法

这一步仍然只做
旧 rows 重路由，
不加新训练。

本轮新落两份 summary：

1. `source split`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_loose_shadow_source_split/summary.json`
2. `source positioning`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_loose_shadow_source_positioning/summary.json`

做法和上一轮
最大的区别是：

- 不再把
  `000799 / 000681`
  合并成一个
  `partialmean_core`
- 而是把 reference
  明确拆成：
  - `partialmean_archetype`
    = `001589`
  - `partialmean_outer_anchor`
    = `000799`
  - `partialmean_inner_companion`
    = `000681`
  - `v64only_target`
    = `000697`

然后直接看：

- `001610`
- `000207`
- `000266`

分别离哪一层最近，
最近后又偏离在哪些轴上。

## 结果

### 1. `001610` 已经不该再写成 generic loose shadow；它更像 outer-anchor 这一层的 hinge-entry shadow

看
`partialmean_loose_shadow_source_positioning`
：

- `001610`
  最近的 reference group
  是：
  - `partialmean_outer_anchor`
- 到第二近的
  `v64only_target`
  还有：
  - `+1.462189`
    total-z margin

也就是说，
它不只是
“大概靠近 core”，
而是已经更明确地
贴向：

- `000799`
  这一层

但它相对
`000799`
最大的偏离
不是：

- `target share`
- `target mean`

而是：

- 更晚的
  `offset`
  - `+2.096 z`
- 更高的
  `gain`
  - `+1.432 z`

`source split`
里的 pair delta
也完全对上：

- 相对
  `000799`
  ，
  `001610`
  的
  `target share`
  仍明显更高
  - `+0.001677`
- 但真正把它
  从
  `outer anchor`
  上旋走的，
  是：
  - `offset`
    晚了
    `+0.118 sec`
  - `gain`
    高了
    `+2.88 dB`

所以
`001610`
最稳的固定写法
应是：

- outer-anchor-facing
  shadow
- hinge-entry shadow
- 已经贴到
  barrier 外沿，
  但被
  `late offset + higher gain`
  从 pocket 门口
  旋走

它不是：

- inner companion
- archetype-side floor hinge

更不是：

- `000799`
  的稳定第三成员

### 2. `000207` 也最近 `000799`，但它不是同款 hinge-entry shadow；它更像 shortgain-side outer-ring projection

看
`source_positioning`
：

- `000207`
  最近的 reference group
  也是：
  - `partialmean_outer_anchor`
- 但它对第二近
  `partialmean_archetype`
  的 total-z margin
  只有：
  - `+0.899213`

比
`001610`
更不稳，
说明它虽然贴到
`000799`
这一层，
但本地来源
并不纯。

它相对
`000799`
最大的偏离
也和
`001610`
完全不同：

- `interference_share`
  太高
  - `+2.637 z`
- `reference`
  太短
  - `-2.033 z`

`source split`
的 pair delta
进一步把
这个来源写实了：

- 相对
  `000799`
  ，
  `000207`
  仍然缺：
  - `target share collapse`
    `+0.001677`
- 但它更突出的
  偏离
  是：
  - `interference_share`
    更高
    `+0.177418`
  - `reference`
    更短
    `-1.23 sec`
  - `gain`
    更低
    `-2.373 dB`

这说明：

- `000207`
  当然会踩进
  `lower target mean`
  这层外圈
- 但它带着明显的：
  - shortgain-side
    侧味道
  - high-interference-share
    侧味道

所以：

- `000207`
  不能和
  `001610`
  写成同一类
  barrier-facing shadow
- 它更像：
  - shortgain-side
    outer-ring projection

### 3. `000266` 的最近参考系已经重新固定成 `001589`，所以它应从 loose shadow 里单独挂回 archetype-side floor hinge

看
`source_positioning`
：

- `000266`
  最近的 reference group
  不是：
  - `000799`
- 而是：
  - `partialmean_archetype`
    (`001589`)
- 而且对第二近
  `000799`
  还有：
  - `+0.698045`
    total-z margin

它相对
`001589`
最大的偏离
是：

- `reference`
  更短
  - `-2.330 z`
- `interference_share`
  更高
  - `+1.523 z`

`source split`
也继续对上：

- 相对
  `001589`
  ，
  `000266`
  的
  `target share`
  只多了：
  - `+0.000457`
  并不大
- 更核心的改动
  其实是：
  - `reference`
    缩短
    `-1.41 sec`
  - `interference_share`
    抬高
    `+0.102479`
  - `offset`
    更晚
    `+0.082 sec`

同时，
它相对
`000799`
的最大偏离
反而是：

- cosine
  更高
  - `+0.144423`
- interference mean
  更高
  - `+5.342542`

这说明：

- `000266`
  之所以会落进
  outer ring，
  不是因为
  它真的开始贴近
  `000799`
  这条 barrier route
- 而是因为
  archetype-side
  的 floor hinge
  先沿着：
  - shorter reference
  - lower target mean
  这一侧
  投影进来

所以：

- `000266`
  在 loose shadow
  这个聚合标签里，
  仍应单独固定成：
  - archetype-side floor hinge

### 4. 三条 shadow 都能落进 outer ring，但没有一条真正接近 `000681`；这说明 outer ring 不是 core 的第三层，而是多来源投影层

把三条 row
同时对
`000681`
看，
结论反而最整齐：

- `001610`
  对
  `000681`
  的 total-z distance
  = `7.611312`
- `000207`
  对
  `000681`
  的 total-z distance
  = `7.417405`
- `000266`
  对
  `000681`
  的 total-z distance
  = `7.406761`

而且三者
相对
`000681`
的 pair delta
都共同保留：

- 明显更高的
  `target share`
  - 大约
    `+0.00204`
- 明显不够深的
  `target mean`
  - 大约
    `+5.59 ~ +5.73`

也就是：

- 不管它们
  各自来自
  哪条 side route
- 一旦拿
  `000681`
  当参考，
  它们都会一起暴露成：
  - share 不够塌
  - mean 不够深

这进一步说明：

- outer ring
  不是 stable core
  的第三层
- 它只是
  barrier 外侧
  被不同 route
  投影进来的
  mixed-source layer

### 5. 因此 `loose shadow` 仍然可以保留为聚合标签，但默认不应再把它当成单一路由名词

把这轮结果
和上一轮
barrier-depth mechanics
合起来后，
当前最稳口径
已经可以再收紧一层：

1. `000799`
   负责：
   - outer barrier
   - share-collapse gate
2. `000681`
   负责：
   - inner depth
   - deeper mean collapse
3. `001610`
   是：
   - outer-anchor-facing
     hinge-entry shadow
4. `000207`
   是：
   - shortgain-side
     outer-ring projection
5. `000266`
   是：
   - archetype-side
     floor hinge

所以：

- `loose shadow`
  这个词
  仍然可以保留，
  但它只应该当：
  - 聚合标签
  - 外圈统称

不能再当：

- 单一路 shadow route
- 同 pocket 的
  第三层 core

## 结论

本轮把
`001610 / 000207 / 000266`
这组三条
outer-ring shadow
的来源正式拆开了：

1. `001610`
   最近的是
   `000799`
   ，
   但它是：
   - hinge-entry shadow
   主要被：
   - late offset
   - higher gain
   从 barrier 门口
   旋走
2. `000207`
   也最近
   `000799`
   ，
   但它更像：
   - shortgain-side projection
   主要偏离在：
   - high interference share
   - shorter reference
   - lower gain
3. `000266`
   最近的是
   `001589`
   ，
   所以应固定回：
   - archetype-side floor hinge

因此，
`000799`
这条 route
现在的最稳写法
应收紧成：

- `000799`
  = outer barrier anchor
- `000681`
  = inner depth companion
- `001610`
  = hinge-entry shadow
- `000207`
  = shortgain-side outer-ring projection
- `000266`
  = archetype-side floor hinge

只有在需要
聚合统称时，
才把后三者
合称为：

- outer-ring loose shadow

本轮未启动新训练。
