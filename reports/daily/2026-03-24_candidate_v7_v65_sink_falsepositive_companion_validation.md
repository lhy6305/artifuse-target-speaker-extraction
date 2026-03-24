# 2026-03-24 `candidate_v7` `v65` sink false-positive companion validation

## 背景

上一轮已经把：

- `001589 -> 000799`
- `000664 -> 000697`

两条 local route
都压到了
archetype-local support，
并得到一个
更窄的工作假设：

- `000799`
  这条线
  当前最紧 support
  是：
  - `train_000681`
- `000697`
  这条线
  当前最紧 support
  是：
  - `train_000904`
  更宽一点的 tail
  是：
  - `train_000219`

但那一步的 support
仍然是：

- 在局部邻域上
  先做 route-specific projection

所以它回答的是：

- 谁会落进
  同一个投影 pocket

还没有回答：

- 这个 row
  到底是不是
  稳定 companion
- 还是只是
  沿着同一条线
  偶然扫到的
  外圈 tail / 极端点

因此本轮不再扩大邻域，
只把：

- `000681`
- `000904`
- `000219`

拿出来做
companion validation。

## 本轮做法

这一步不加新脚本，
只补 companion 资产，
继续复用已有：

- `scripts/eval/analyze_proxy_group_split.py`
- `scripts/eval/analyze_proxy_case_positioning.py`
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`

本轮新增 sample-id 资产：

1. `000681`
   singleton：
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_partialmean_companion_000681_train.txt`
2. `000799 + 000681`
   core：
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_partialmean_core_train.txt`
3. `000904`
   singleton：
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_v64only_companion_000904_train.txt`
4. `000697 + 000904`
   core：
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_v64only_core_train.txt`
5. `000219`
   singleton：
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_sink_v64only_tail_000219_train.txt`

本轮新增输出：

1. companion split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_falsepositive_companion_split/summary.json`
2. companion positioning：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_falsepositive_companion_positioning/summary.json`
3. `000799 vs 000681`
   reverse contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_000681_factor_contrast/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000681_vs_000799_factor_contrast/summary.json`
4. `000697 vs 000904`
   reverse contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_000904_factor_contrast/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000904_vs_000697_factor_contrast/summary.json`
5. `000219 vs 000697`
   tail contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000219_vs_000697_factor_contrast/summary.json`

本轮 companion validation
只回答三个窄问题：

1. `000681`
   是不是
   `000799`
   的稳定 companion
2. `000904`
   是不是
   `000697`
   的稳定 companion
3. `000219`
   到底是：
   - `000697`
     core 的 companion
   还是：
   - 只是更宽一点的
     local tail

## 结果

### 1. `000681` 可以保留为 `000799` 的稳定 companion，但要固定写成“更深 pre / 更短 reference”的同 pocket 变体

先看
`companion_positioning`。

`train_000681`
最近的 reference group
已经固定成：

- `partialmean_core`
  (`000799 + 000681`)

和第二近 reference
之间的总距离 margin
为：

- `1.083743`

也就是：

- 在当前这组
  companion 候选里，
  `000681`
  并没有回到：
  - `001589`
    archetype
  - 或
    `000664`
    那条 route
- 它最像的
  仍然是：
  - `000799`
    这条 core

但同时，
它相对
`000799`
的最大偏离
也非常明确：

1. `gap::v66>v64`
   - `+0.472652`
   - `+2.638 z`
2. `gap::v67>v66`
   - `+0.532671`
   - `+2.498 z`
3. `gap::v66>v65`
   - `+0.348421`
   - `+2.164 z`
4. `reference_duration_sec`
   - `-1.14 sec`
   - `-1.839 z`
5. `target_transient_presence_minus_mid_db_mean`
   - `-6.529472`
   - `-1.283 z`

这说明：

- `000681`
  虽然和
  `000799`
  同属一条
  partialmean-core route；
- 但它不是
  深度几乎重合的
  twin；
- 它更像：
  - margin
    更深 pre
  - reference
    更短
  - target transient mean
    更塌
  的
  更激进 companion

再看
`000799 - 000681`
的直接 pair delta：

- `target_transient_presence_share_mean`
  - 只差
    `+0.000386`
- `target_duration_sec`
  - `+0.48 sec`
- `reference_duration_sec`
  - `+1.14 sec`
- `interference_layers.0.gain_db`
  - `-2.068 dB`

也就是：

- 两者在
  target-share collapse
  这条主语上
  基本同 pocket；
- 差异主要在：
  - compare margin
    更深
  - reference
    更短
  - gain
    更强一点

再看 reverse contrast：

`000799 -> 000681`
和
`000681 -> 000799`
两边排前的字段
完全一致，
都集中在：

- `reference_duration_sec`
- `target_transient_presence_minus_mid_db_mean`
- `interference_layers.0.gain_db`

而不是：

- `target_transient_presence_share_mean`

这点很关键：

- 如果 companion
  真不是同 pocket，
  最前面通常会先重新弹出：
  - 主 residual 语义本身
- 但这里没有；
- 这里弹出来的，
  更多是：
  - 深度
  - 参考时长
  - 次级包络
    漂移

因此当前应把
`000681`
固定写成：

- `000799`
  的稳定 companion
- 但属于：
  - 更深 pre
  - 更短 reference
  的同 pocket 变体

### 2. `000904` 虽然仍贴在 `000697` 这条 route 上，但它扛不住 reverse contrast；更像 extreme edge support，而不是 tight companion

先看
`companion_positioning`。

`train_000904`
最近的 reference group
是：

- `v64only_core`
  (`000697 + 000904`)

和第二近 reference
`v64only_archetype`
之间的 margin
为：

- `0.598393`

所以从
“贴哪条 route”
这个问题看：

- `000904`
  仍然贴着
  `000697`
  这条 local route
- 它不是跑回了
  `000664`
  archetype

但它相对 core
的偏离项
也远比
`000681`
更大：

1. `target_transient_presence_share_mean`
   - `+0.184586`
   - `+2.803 z`
2. `interference_layers.0.gain_db`
   - `+5.454 dB`
   - `+2.670 z`
3. `interference_transient_presence_share_mean`
   - `-0.347611`
   - `-2.527 z`
4. `interference_transient_presence_minus_mid_db_mean`
   - `-10.182081`
   - `-1.864 z`
5. `target_transient_presence_minus_mid_db_mean`
   - `+8.891803`
   - `+1.747 z`
6. `reference_duration_sec`
   - `-1.02 sec`
   - `-1.645 z`

这已经不是：

- 同 pocket
  只差一点深浅

而是：

- target-side transient
  已经明显抬高
- interference package
  被继续掏空
- gain
  方向也和
  `000697`
  不同

直接看
`000697 - 000904`
的 pair delta，
差异同样很大：

- `target_transient_presence_share_mean`
  - `-0.184586`
- `interference_transient_presence_share_mean`
  - `+0.347611`
- `interference_layers.0.gain_db`
  - `-5.454 dB`
- `target_interference_logspec_cosine`
  - `+0.160400`
- `reference_duration_sec`
  - `+1.02 sec`

而
`000697 -> 000904`
与
`000904 -> 000697`
两边的 reverse contrast
排前字段
也都稳定卡在：

- `target_transient_presence_share_mean`
- `interference_layers.0.gain_db`
- `interference_transient_presence_share_mean`

这和
`000799 / 000681`
那对完全不同。

这里排前的
已经不只是：

- 次级深浅漂移

而是：

- 主 residual 语义本身
  被改写了

因此当前更准确的口径应改成：

- `000904`
  仍属于
  `000697`
  这条 route
  的
  extreme edge support
- 但它不是
  可以和
  `000697`
  并列写成
  tight companion
  的那种 row

### 3. `000219` 不属于 `000697` 的 core；它更像重新贴回 `000664` archetype 的 broad long-duration tail

`companion_positioning`
里，
`train_000219`
最近的 reference group
已经固定成：

- `v64only_archetype`
  (`train_000664`)

而不是：

- `v64only_core`

并且
与第二近
`partialmean_archetype`
之间还有：

- `0.922173`
的 margin。

它相对
`000664`
的最大偏离
几乎全部集中在：

- `target_duration_sec`
  - `+2.13 sec`
  - `+2.908 z`

其它字段
反而都只是
中低等级偏离：

- `reference_duration_sec`
  - `-0.66 sec`
  - `-1.065 z`
- `target_interference_logspec_cosine`
  - `+0.066238`
  - `+0.669 z`
- `target_transient_presence_share_mean`
  - `+0.037587`
  - `+0.571 z`

也就是：

- `000219`
  没有像
  `000904`
  那样
  把
  interference package
  改写到很极端；
- 它更像：
  - 仍然挂在
    `000664`
    archetype
    附近
  - 只是
    duration
    被单独拖长了

再看
`000219 -> 000697`
tail contrast，
排前字段为：

1. `interference_layers.0.gain_db`
   - `+1.767 z`
2. `target_duration_sec`
   - `+1.557 z`
3. `target_interference_logspec_cosine`
   - `+1.371 z`
4. `interference_transient_presence_minus_mid_db_mean`
   - `+1.193 z`

这里的方向也很重要：

- 相对
  `000697`
  来说，
  `000219`
  是：
  - gain
    更没那么低
  - duration
    更长
  - cosine
    更高
  - interference mean
    更高

这说明：

- `000219`
  不是
  `000697`
  那条
  weak-interference-package core
  的稳定同伴；
- 它更像：
  - 时长被拖长
  - 但其它包络
    重新朝 archetype
    回弹
  的
  broad tail

因此当前应把
`000219`
固定写成：

- `000697`
  route 的外圈 tail
- 不是
  core companion

### 4. 到这一步，两条 route 的 companion 结论已经不对称了

当前可以把两条线
正式分开写成：

#### 4.1 `001589 -> 000799`

这一条线
已经有：

- 明确的 tight companion
  - `train_000681`

并且：

- companion validation
  通过；
- 差异主要是：
  - 更深 pre
  - 更短 reference
  - 次级包络漂移
- 主 residual 语义
  仍然共享：
  - target-transient-collapse

所以这条线
当前可写成：

- `000799`
  core
- `000681`
  stable companion

#### 4.2 `000664 -> 000697`

这一条线
目前没有拿到
同等强度的
tight companion。

当前更合理的拆法是：

- `000697`
  = route core
- `000904`
  = extreme edge support
- `000219`
  = broad long-duration tail

也就是：

- `000904`
  不是
  `000697`
  的
  对称 tight twin
- `000219`
  更不是
  core companion

所以后续如果继续写
这条 route，
默认不能再把：

- `000697 + 000904`

并列当成一个
完全对称的 core。

## 当前解释

本轮之后，
两条 companion 线
应继续收紧成：

1. `000799`
   默认挂：
   - `000681`
     这个稳定 companion
   但 companion 口径
   固定写成：
   - 更深 pre
   - 更短 reference
   的同 pocket 变体
2. `000697`
   当前仍是
   那条 route
   的真正 core
3. `000904`
   只能保留为：
   - extreme edge support
   不能再直接写成：
   - tight companion
4. `000219`
   固定写成：
   - broad long-duration tail
   不是 core

因此后续默认推进方式
应改成：

1. `000799 <-> 000681`
   这条线
   可以继续按
   stable companion
   深挖
2. `000697`
   这条线
   则应优先找：
   - 比 `000904`
     更接近的
     tight companion
   而不是先把
   `000904`
   扶正成 core
3. `000219`
   如再引用，
   默认只作：
   - tail
     对照
   不再作
   core support

## 结论

1. `000681`
   可以正式保留为
   `000799`
   的稳定 companion；
   但它是
   更深 pre / 更短 reference
   的同 pocket 变体，
   不是深度完全重合的 twin。
2. `000904`
   虽然仍贴在
   `000697`
   这条 route 上，
   但 reverse contrast
   显示它已经改写了
   主 residual 语义；
   当前只能记成
   extreme edge support，
   不能扶正成 tight companion。
3. `000219`
   最近的 reference
   已回到
   `000664`
   archetype；
   它应固定写成
   broad long-duration tail，
   不是
   `000697`
   core 的 companion。
4. 后续默认沿：
   - `000799 <-> 000681`
   这条 stable companion
     线继续推进
   - 同时为
     `000697`
     继续搜索
     比 `000904`
     更 tight 的 companion
   不回到
   `000697 + 000904`
   对称双 core
   的旧写法。
5. 本轮仍不启动新训练。
