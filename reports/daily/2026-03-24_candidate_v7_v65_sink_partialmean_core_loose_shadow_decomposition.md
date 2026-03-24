# 2026-03-24 `candidate_v7` `v65` sink partialmean core loose-shadow decomposition

## 背景

上一轮已经把
`000799`
这条线
正式固定成：

- `000799 + 000681`
  的 stable companion route
- 一个
  cohesive
  target-transient-collapse
  micro-pocket

同时也已经明确写了：

- `001610 / 000207 / 000266`
  只能保留为
  loose shadow /
  partial support

但这句话
还不够稳，
因为它仍然留了
两个没回答完的口子：

1. 这三个 row
   到底是不是
   同一个 shadow 小簇
2. 它们为什么
   虽然会反复落进：
   - `target mean`
   - `duration + target mean`
   这一侧，
   却始终升不上
   `000799 + 000681`
   的 stable core

所以本轮不再回头
讨论
`000697`，
而是沿
`000799`
这条线
继续把：

- stable core
- loose shadow

正式拆干净。

## 本轮做法

这一步是旧 rows 重路由，
不是新 coverage。

本轮不加新训练，
也不扩大搜索 ring，
只把
`partialmean_core`
direct ring 里
最像 shadow 的
三条 row
单独物化成一组：

- `train_001610`
- `train_000207`
- `train_000266`

新增 sample-id 资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_partialmean_loose_shadow_train.txt`

本轮复用已有脚本：

- `scripts/eval/analyze_proxy_group_split.py`
- `scripts/eval/analyze_proxy_case_positioning.py`
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`
- `scripts/eval/analyze_proxy_factor_slice_support.py`
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

本轮新增输出：

1. core vs shadow split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_shadow_split/summary.json`
2. `001610 / 000207 / 000266`
   positioning：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_loose_shadow_positioning/summary.json`
3. `partialmean_core`
   vs
   `partialmean_loose_shadow`
   factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_vs_loose_shadow_factor_contrast/summary.json`
4. `partialmean_core`
   vs
   `partialmean_loose_shadow`
   slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_vs_loose_shadow_slice_support/summary.json`
5. 两组 quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_vs_loose_shadow_targetshare_targetmean_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partialmean_core_vs_loose_shadow_duration_targetmean_quadrants/summary.json`

本轮只回答三个窄问题：

1. `001610 / 000207 / 000266`
   合起来
   像不像一个
   可升格的
   第三 pocket
2. `000799 + 000681`
   相对它们
   真正多占住了
   哪些 factor
3. 之后
   `000799`
   这条线
   应该如何固定写：
   - core
   - shadow

## 结果

### 1. `001610 / 000207 / 000266` 只能合称 loose shadow，但它们本身并不是一个新的 cohesive pocket

先看
`partialmean_core_shadow_split`
里
`partialmean_loose_shadow`
这组的均值：

- `target_transient_presence_minus_mid_db_mean`
  - `-16.964048`
- `target_transient_presence_share_mean`
  - `0.002240`
- `target_duration_sec`
  - `1.30`
- `reference_duration_sec`
  - `1.94`
- `interference_layers.0.gain_db`
  - `-3.835`
- `interference_layers.0.start_offset_sec`
  - `0.157667`

和
`partialmean_archetype = 001589`
相比，
这组三条 row
确实已经共享了
一部分
`000799`
方向的变化：

- `target transient mean`
  更低
  - `-2.611338`
- `target duration`
  更短
  - `-0.98 sec`
- `reference duration`
  更短
  - `-1.42 sec`
- `gain`
  也更高一点
  - `+1.603 dB`

但问题在于，
它们共享的
主要是：

- `target mean`
- `short duration`
- `short reference`

而不是
定义
`partialmean_core`
identity 的
那组最干净因子。

所以这组三条 row
最多只能写成：

- 会一起投影到
  core 附近的
  loose shadow

不能写成：

- 新的
  third pocket

### 2. `target share + target mean` 上，shadow 只占住 `target mean`，完全接不住 `target share collapse`

这一步最关键。

看
`partialmean_core_vs_loose_shadow_targetshare_targetmean_quadrants`
：

- `partialmean_core`
  anchor
  在：
  - `both`
- `partialmean_archetype`
  在：
  - `neither`
- `partialmean_loose_shadow`
  在：
  - `factor_b_only`

这里：

- `factor_a`
  是
  `target_transient_presence_share_mean`
- `factor_b`
  是
  `target_transient_presence_minus_mid_db_mean`

也就是：

- `001610 / 000207 / 000266`
  这组三条 row
  的共同点是：
  - 都踩进了
    lower
    `target mean`
    这一侧
- 但它们共同缺的
  也是：
  - 没有谁
    能把
    `target share`
    一起塌到
    core 那一边

而且这不是
“差一点”
的问题。

`slice_support`
直接给出：

- `target share`
  的
  `contrast_on_target_side`
  是：
  - `false`
- `target_side_sample_ids`
  是：
  - 空

这代表：

- 在当前
  `partialmean_core`
  direct ring
  里，
  真正把
  `target share collapse`
  占住的，
  还是只有
  `000799 + 000681`

所以 shadow
无论怎么看，
都不可能升级成：

- 对称第三 core

### 3. `duration + target mean` 上 shadow 会整体踩进 `both`，但这恰好证明 duration 只是 support，不是 pocket identity

看
`partialmean_core_vs_loose_shadow_duration_targetmean_quadrants`
：

- `partialmean_core`
  在：
  - `both`
- `partialmean_loose_shadow`
  也在：
  - `both`

如果只看这张图，
很容易误判成：

- shadow
  已经和 core
  没差太多

但它和上一节
必须一起读。

一起读后的正确结论是：

- `001610 / 000207 / 000266`
  当然能在：
  - shorter duration
  - lower target mean
  上
  和 core
  重叠
- 但这只能说明：
  - duration
    是 shared support axis
- 不能说明：
  - 它们已经占住了
    pocket identity

换句话说：

- `duration + mean`
  会把 shadow
  吸进来
- `share + mean`
  才会把
  true core
  与 shadow
  真正分开

这一步等于把
上一轮那句：

- duration
  是 support，
  不是 identity

正式坐实了。

### 4. `core vs shadow` 的 residual 对照也在重复同一个结论：它们最像的不是“再深一点的 core”，而是 mixed source 的 mean-only shadow

看
`partialmean_core_vs_loose_shadow_factor_contrast`
，
排序最前的字段是：

1. `interference_layers.0.start_offset_sec`
   - `target_specific_residual_z = -1.3529`
2. `interference_transient_presence_share_mean`
   - `target_specific_residual_z = -1.1435`
3. `target_interference_logspec_cosine`
   - `target_specific_residual_z = -0.8676`
4. `target_transient_presence_minus_mid_db_mean`
   - `target_specific_residual_z = -0.8573`
5. `interference_layers.0.gain_db`
   - `target_specific_residual_z = +0.7747`
6. `target_transient_presence_share_mean`
   - `target_specific_residual_z = -0.7253`

这里面最重要的
不是
字段顺序本身，
而是方向：

- core
  相对 shadow
  并没有再额外依赖：
  - `target_duration`
    继续缩短
  因为这项 residual
  几乎为零
  - `-0.04 sec`
- 真正把 core
  和 shadow
  拉开的，
  反而是：
  - 更早的 offset
  - 更低的 interference share
  - 更低的 cosine
  - 更深的 target mean
  - 以及最终仍没被 shadow
    接住的
    target share collapse

也就是说：

- shadow
  并不是
  “一个只差一点
  `target share`
  的整齐 subgroup”
- 它更像：
  - 已经踩进
    `target mean + short duration`
    的外圈
  - 但 source
    仍然是 mixed 的
  - 所以会在
    offset /
    interference share /
    cosine /
    gain
    上
    各自乱开

这正是
loose shadow
而不是
stable companion
的结构。

### 5. `001610 / 000207 / 000266` 三个 case 本身也不是同一路 shadow 来源；这就是它们只能合称 loose shadow、不能升格为独立 pocket 的根本原因

看
`partialmean_loose_shadow_positioning`
：

#### 5.1 `001610`

- 最近的 reference group：
  - `partialmean_core`
- 但 margin
  只有：
  - `0.080712`

这不是稳定归属，
只是擦边靠近。

它相对 core
最大的偏离
是：

- 更晚 `offset`
  - `+2.336 z`
- `v66>v65`
  已经翻负
  - `-2.005 z`
- `v66>v64`
  也几乎磨到零
  - `-1.684 z`

所以
`001610`
更像：

- 一条
  margin 已经旋走的
  hinge-entry shadow

不是：

- `000799`
  的 pocket companion

#### 5.2 `000207`

- 最近的 reference group：
  - `partialmean_core`
- margin
  比
  `001610`
  稍大：
  - `0.280258`

但它相对 core
最大的偏离
是：

- `interference_share`
  太高
  - `+2.299 z`
- `gain`
  太低
  - `-1.694 z`

这和上一轮
`000697`
线里
`shortgain neighbor`
的读法
其实一致：

- `000207`
  会贴近
  short duration +
  lower target mean
- 但它带着
  明显的
  low-gain /
  high-int-share
  侧味道

所以它更像：

- 被别的 route
  顺带投影进来的
  pre-side shadow

#### 5.3 `000266`

- 最近的 reference group
  反而不是 core，
  而是：
  - `partialmean_archetype`
- margin
  也足够大：
  - `1.292192`

它相对 archetype
最大的偏离
是：

- `reference`
  更短
  - `-2.330 z`
- `interference share`
  更高
  - `+1.523 z`
- `offset`
  更晚
  - `+1.457 z`

这和更早的
weak-gain hinge
诊断是连着的：

- `000266`
  仍然更像
  archetype-side
  floor hinge
- 它能踩进 shadow，
  不是因为
  它已经进了 core
- 而是因为
  它先占住了：
  - lower target mean
  - shorter duration
  的那一侧

所以：

- `000266`
  连 shadow 里
  都更像
  archetype-side source

### 6. 因此 `001610 / 000207 / 000266` 这组三条 row 最多只能写成 mixed-source loose shadow，不能再写成同 pocket 的第三核

把上一节合起来，
现在这组三条 row
的最稳口径应写成：

1. 共享的只是：
   - lower target mean
   - shorter duration
2. 共同缺失的是：
   - target share collapse
3. 内部来源仍是 mixed：
   - `001610`
     更像
     hinge-entry shadow
   - `000207`
     更像
     shortgain-side shadow
   - `000266`
     更像
     archetype-side floor hinge

所以：

- 它们当然可以合称：
  - loose shadow
- 但这个 group
  本身
  不是
  一个新的 cohesive pocket

## 结论

本轮把
`000799`
这条线的
stable core
和
loose shadow
正式拆开了：

1. `000799 + 000681`
   仍然是唯一稳定 core，
   因为当前只有它们
   真正占住了：
   - `target share + target mean`
     同时塌陷
2. `001610 / 000207 / 000266`
   虽然会一起踩进：
   - `duration + target mean`
   这一侧，
   但它们共同缺失：
   - `target share collapse`
3. 这组三条 row
   内部来源还是 mixed，
   只能固定写成：
   - loose shadow /
     partial support
   不能再升格成：
   - third core
   - 或对称 companion family

所以后续
`000799`
这条线
默认写法再收紧成：

- stable core：
  - `000799 <-> 000681`
- loose shadow：
  - `001610 / 000207 / 000266`
  - 只表示
    `target mean + short duration`
    外圈
  - 不表示
    新 pocket

本轮未启动新训练。
