# 2026-03-24 `candidate_v7` `v65` sink reference-gain edge case branch split

## 背景

上一轮已经把
`reference + gain both`
从：

- crossed `3`
- pre `1`

拆开，
并确认：

- 这条边
  不是 hard edge
- 而是
  crossed-support shelf

同时也已经明确：

- `train_000951`
  不是因为
  `gain`
  不够
  才没 crossed
- 真正需要继续拆的，
  已经变成：
  - `000951 -> 001705`
    为什么会走成
    shared-target hinge
  - `000951 -> 001610 / 000664`
    为什么会裂成
    low-share hinge
    与
    `v64_only`

因此这一步只继续回答一个更窄的问题：

- crossed edge
  内部
  到底是不是
  单一路径
  继续深化，
  还是已经裂成
  两条正交子支路

## 本轮做法

这一步不加新脚本，
只把 crossed edge
进一步物化成
最小 case groups：

- `reference_gain_pre`
  - `train_000951`
- `shared_target_hinge`
  - `train_001705`
- `low_share_hinge`
  - `train_001610`
- `low_share_v64only`
  - `train_000664`
- `v65_sink`
  - `train_001543`

本轮新增资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_edge_shared_target_hinge_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_edge_low_share_hinge_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_edge_low_share_v64only_train.txt`

本轮输出：

1. case split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_case_split/summary.json`
2. shared-target factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_shared_target_factor_contrast/summary.json`
3. shared-target slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_shared_target_slice_support/summary.json`
4. shared-target share+cosine quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_shared_target_share_cosine_quadrants/summary.json`
5. `v64_only` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_v64only_factor_contrast/summary.json`
6. `v64_only` slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_v64only_slice_support/summary.json`
7. `v64_only` offset+duration quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_v64only_offset_duration_quadrants/summary.json`

## 结果

### 1. crossed edge 不是单一路径深化，而是已经裂成两条正交子支路

显式拆成
singleton groups
后，
compare margin
已经直接裂成三种不同几何：

- `train_001705`
  - `v66 - v64 = +0.020573 dB`
  - `v66 - v65 = -0.000834 dB`
- `train_001610`
  - `v66 - v64 = +0.001154 dB`
  - `v66 - v65 = -0.051220 dB`
- `train_000664`
  - `v66 - v64 = -0.009173 dB`
  - `v66 - v65 = +0.004478 dB`

也就是：

- `001705`
  是：
  - `v65`
    刚翻负
  - `v64`
    还明显为正
    的 soft hinge
- `001610`
  是：
  - `v65`
    更深翻负
  - `v64`
    只差最后一线
    的 low-share hinge
- `000664`
  则不是更深 hinge，
  而是直接旋成：
  - `v64_only`

所以当前 crossed edge
不能再写成：

- 同一条边
  只是深浅不同

更准确的口径应改成：

- shared-target soft hinge
- low-share hinge
- low-share `v64_only`

三种不同子支路

### 2. `000951 -> 001705` 这条是 shared-target soft hinge；它的主语不是 target 继续抬升，而是“target 不塌 + interference package 拉满 + cosine 抬高”

用：

- `target = shared_target_hinge`
- `baseline = reference_gain_pre`
- `contrast = low_share_hinge`

做 factor contrast，
当前标准化 residual
前三位是：

- `target_transient_presence_minus_mid_db_mean = +2.6266 z`
- `target_interference_logspec_cosine = +2.3739 z`
- `interference_transient_presence_share_mean = +2.2648 z`

继续往下看，
还包括：

- `target_transient_presence_share_mean = +2.2151 z`
- `interference_transient_presence_minus_mid_db_mean = +2.0120 z`
- `interference_layers.0.start_offset_sec = -1.8759 z`

关键不是：

- `001705`
  比
  `000951`
  的 target
  更高

因为：

- `001705`
  与
  `000951`
  的
  target mean / share
  完全相同

真正发生的是：

- `001705`
  保住了
  `000951`
  这套
  shared target package
- 同时叠加：
  - 更高 interference mean
    `+8.8124`
  - 更高 interference share
    `+0.3519`
  - 更高 cosine
    `+0.024343`
  - 更长 reference
    `+0.48 sec`
  - 更弱 gain
    `-1.648 dB`
  - 更早 offset
    `-0.127 sec`

所以这条支路更准确的写法是：

- shared-target
  不塌
- interference package
  强力抬起
- cosine
  同步抬高
- overlap
  反而更早

### 3. `001705` 不是更深 hinge，而是更软的 `v65-first` hinge

相对
`low_share_hinge`
`001610`，
`001705`
的 compare 差为：

- `v66 - v64`
  更高
  `+0.019419 dB`
- `v66 - v65`
  也更高
  `+0.050386 dB`

也就是：

- `001705`
  并没有比
  `001610`
  更深
- 它反而是：
  - 保住更多
    `v64`
    buffer
  - 只把
    `v65`
    轻微推过零

所以当前应把：

- `001705`

固定写成：

- shared-target
  `v65-first`
  soft hinge

而不是：

- crossed edge
  更深阶段

### 4. `001610 -> 000664` 不是“hinge 继续加深”，而是一个 margin 旋转：从 `v65` 翻负转成 `v64_only`

`low_share_hinge`
对
`low_share_v64only`
的 compare 差，
当前明确为：

- `v66 - v64`
  下掉：
  - `0.010327 dB`
- `v66 - v65`
  反而回升：
  - `0.055697 dB`

也就是：

- `000664`
  不是把
  `001610`
  那条 hinge
  再向前推深
- 它做的其实是：
  - 把负 gap
    从
    `v65`
    这侧
    旋到
    `v64`
    这侧

所以这一步必须明确排除：

- `000664`
  是更深 hinge

更准确的口径应改成：

- low-share hinge
  -> low-share `v64_only`
    branch rotation

### 5. 这次把 `001610` 旋成 `000664` 的最强 residual 已固定成：更晚 offset + 更长 target duration

用：

- `target = low_share_v64only`
- `baseline = low_share_hinge`
- `contrast = shared_target_hinge`

做 factor contrast，
当前标准化 residual
前三位是：

- `interference_layers.0.start_offset_sec = +3.1314 z`
- `target_duration_sec = +2.5516 z`
- `interference_transient_presence_share_mean = -2.5467 z`

接下来还有：

- `target_transient_presence_share_mean = -2.2270 z`
- `target_transient_presence_minus_mid_db_mean = -1.6022 z`

这说明：

- `000664`
  相对
  `001610`
  不是 target
  更强
- 它其实是：
  - overlap 更晚
    `+0.085 sec`
  - target 更长
    `+0.15 sec`
  - 同时仍停在：
    - low target-share
    - low interference-share
      这边

也就是：

- `000664`
  不是 shared-target 路线
- 它是：
  - low-share 路线
    上
    late-offset + longer-duration
    的子分支

### 6. `offset + duration` 已经是当前最像 `v64_only` 的 support pair，但还不是硬 gate

`offset + duration`
四象限里：

- `000664`
  anchor
  在：
  - `both`
- `001610`
  与
  `001705`
  都在：
  - `neither`

这说明：

- `later offset + longer target duration`
  的确是
  当前最像
  `v64_only`
  的局部组合

但：

- `both`
  桶里仍有：
  - `2` 条 pre
  - `1` 条 `v64_only`

所以它仍只能写成：

- `v64_only`
  support pair

不能升级成：

- hard gate

### 7. `interference-share + cosine` 是当前最像 `001705` 这条 shared-target hinge 的局部 support pair，但也不是硬 gate

`interference share + cosine`
四象限里：

- `001705`
  在：
  - `both`
- `000951`
  在：
  - `neither`
- `001610`
  也在：
  - `neither`

这说明：

- `001705`
  这条支路
  不是靠：
  - target 更高
    才出现
- 它更像：
  - 在 shared target
    不变的前提下，
    额外拿到：
    - 更高 interference share
    - 更高 cosine

但：

- `both`
  桶里仍有：
  - `3` 条 pre
  - `1` 条 hinge

所以这一步同样只能继续写成：

- shared-target hinge
  support pair

## 结论

1. crossed edge 不是单一路径深化，而是已经裂成两条正交子支路：
   - `000951 -> 001705` = shared-target soft hinge
   - `000951 -> 001610 -> 000664` = low-share 路线，其中 `000664` 不是更深 hinge，而是旋成 `v64_only`
2. `001705` 的主语不是 target 再抬升，而是“target 不塌 + interference package 拉满 + cosine 抬高 + 更早 offset”；它因此形成的是更软的 `v65-first` hinge，而不是更深 crossed。
3. `000664` 相对 `001610` 的关键变化已经固定成：更晚 `offset` + 更长 `target_duration`，同时继续停在低 `target_share / interference_share` 一侧；这一步把 margin 从 `v65` 翻负旋成了 `v64_only`。
4. `interference-share + cosine` 与 `offset + duration` 分别是这两条子支路当前最像的 support pair，但两边的 `both` 桶都还混着 pre，所以都不是硬 gate。
5. 当前最合理的下一步，不应再围绕 crossed edge 整包做均值解释；默认应只继续 case-level：
   - `001705` 对 `001543`
     为什么停在
     soft hinge
   - `000664` 对 `001543`
     为什么转成
     `v64_only`
     而不是
     `v65 sink`
