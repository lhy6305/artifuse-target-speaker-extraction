# 2026-03-24 `candidate_v7` `v65` sink final case divergence split

## 背景

上一轮已经把
crossed edge
正式拆成：

- `000951 -> 001705`
  - shared-target soft hinge
- `000951 -> 001610 -> 000664`
  - low-share 路线
  - 其中
    `000664`
    已经旋成
    `v64_only`

因此当前不再问：

- crossed edge
  是否还是
  单一路径

而只问最后一层：

- `001705`
  为什么没继续走成
  `v65 sink`
- `000664`
  为什么没从
  `v64_only`
  再路由回
  `v65 sink`

也就是只继续做：

- `001705 -> 001543`
- `000664 -> 001543`

这两条终分歧。

## 本轮做法

这一步不加新脚本，
只把
`train_001543`
从整组
`v65_sink`
里单独拉成
singleton anchor，
然后复用现有
split / contrast / support / quadrants
脚本做 final case split。

本轮新增资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_edge_v65_sink_singleton_train.txt`

本轮输出：

1. final case split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_final_case_divergence_split/summary.json`
2. `shared_target_hinge -> sink` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_factor_contrast/summary.json`
3. `v64_only -> sink` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_factor_contrast/summary.json`
4. `shared_target_hinge -> sink` slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_slice_support/summary.json`
5. `v64_only -> sink` slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_slice_support/summary.json`
6. `shared_target_hinge -> sink` quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_gain_reference_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_gain_cosine_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_reference_cosine_quadrants/summary.json`
7. `v64_only -> sink` quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_cosine_reference_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_gain_reference_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_gain_cosine_quadrants/summary.json`

## 结果

### 1. `001705 -> 001543` 不是把 shared-target hinge 那套 package 继续拉高，而是把它反向收紧

先看 compare margin：

- `train_001705`
  - `v66 - v64 = +0.020573 dB`
  - `v66 - v65 = -0.000834 dB`
- `train_001543`
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`

也就是从
`001705`
到
`001543`：

- `v66 - v64`
  只再下去
  `0.029401 dB`
- `v66 - v65`
  则继续下去
  `0.113151 dB`

说明这条路
进入 sink
时，
更像：

- `v65`
  继续明显翻负
- `v64`
  只做次级跟进

再看
`target = v65_sink_singleton`
`baseline = shared_target_hinge`
`contrast = low_share_v64only`
的 factor contrast，
当前 sink-specific residual
前三位是：

- `interference_layers.0.gain_db = -2.2305 z`
- `reference_duration_sec = -2.1826 z`
- `target_interference_logspec_cosine = -1.6398 z`

方向上就是：

- sink
  相对
  `001705`
  为：
  - gain 更弱
    `-3.841 dB`
  - reference 更短
    `-0.96 sec`
  - cosine 更低
    `-0.034218`

所以这条终分歧
不能再写成：

- interference package
  再抬得更高

更准确的写法应改成：

- shared-target hinge
  要真正走成 sink，
  不是继续放大
  shared-target /
  interference package
- 而是要把：
  - long reference
  - high cosine
  - mid-strong gain
  这套 crossed shelf / hinge package
  反向收紧

### 2. `000664 -> 001543` 也不是继续向 `v64_only` 更深，而是基本回到“只压 `v65`”的 sink 路线

先看 compare margin：

- `train_000664`
  - `v66 - v64 = -0.009173 dB`
  - `v66 - v65 = +0.004478 dB`
- `train_001543`
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`

也就是从
`000664`
到
`001543`：

- `v66 - v64`
  只回弹
  `+0.000345 dB`
- `v66 - v65`
  却继续下去
  `0.118462 dB`

这说明：

- `000664 -> 001543`
  几乎不是
  再压低
  `v64`
- 而是把：
  - 已经旋成
    `v64_only`
    的 margin
  再重新压回：
  - `v65`
    这一侧

再看
`target = v65_sink_singleton`
`baseline = low_share_v64only`
`contrast = shared_target_hinge`
的 factor contrast，
当前 sink-specific residual
前三位是：

- `target_interference_logspec_cosine = -2.3958 z`
- `reference_duration_sec = -2.0542 z`
- `interference_layers.0.gain_db = -1.9920 z`

方向上就是：

- sink
  相对
  `000664`
  为：
  - cosine 更低
    `-0.023421`
  - reference 更短
    `-1.02 sec`
  - gain 更弱
    `-4.301 dB`

同时，
`offset`
只回到：

- `+1.3159 z`
  的次级残差

`target_duration`
也只剩：

- `+0.9733 z`

说明：

- 之前把
  `000664`
  推成
  `v64_only`
  的
  `offset + duration`
  包，
  到 sink
  这一步
  已经不是主语
- 真正把它从
  `v64_only`
  路由回
  sink 的，
  更像是：
  - 降 cosine
  - 缩 reference
  - 大幅降 gain

### 3. 两条终分歧最紧的共同 support pair 都落在 `gain + cosine`，不是旧的 `reference + gain`

对
`001705 -> 001543`
这条，
我试了：

- `gain + reference`
- `gain + cosine`
- `reference + cosine`

其中最紧的是：

- `gain + cosine`

因为：

- target
  `001543`
  在 `both`
- contrast
  `000664`
  在 `neither`
- `both`
  桶里只有：
  - `1` 条 sink
  - `1` 条 pre

也就是：

- `train_001543`
- `train_000697`

相比之下：

- `gain + reference`
  的 `both`
  还有
  `6` 条
- `reference + cosine`
  的 `both`
  也有
  `6` 条

因此：

- 对 shared-target 终分歧，
  `gain + cosine`
  是当前最紧的
  local support pair

对
`000664 -> 001543`
这条，
我试了：

- `cosine + reference`
- `gain + reference`
- `gain + cosine`

其中同样最紧的是：

- `gain + cosine`

因为：

- target
  `001543`
  在 `both`
- contrast
  `001705`
  在 `neither`
- `both`
  桶里只有：
  - `1` 条 sink
  - `2` 条 pre

也就是：

- `train_001543`
- `train_000799`
- `train_000697`

这比：

- `gain + reference`
  的 `6` 条
- `cosine + reference`
  的 `7` 条

都更紧。

所以当前更统一的写法应改成：

- `001705 -> 001543`
  和
  `000664 -> 001543`
  这两条终分歧
  共享的最紧局部 support pair
  都是：
  - `gain + cosine`

### 4. 但 `gain + cosine` 仍不是 hard gate；真正剩下的是 sink pocket 内的 pre 残留

尽管
`gain + cosine`
已经是当前最紧的
共同 support pair，
它仍不是 hard gate，
因为：

- shared-target 那条
  的 `both`
  里
  还残留：
  - `train_000697`
- `v64_only` 那条
  的 `both`
  里
  还残留：
  - `train_000799`
  - `train_000697`

这意味着：

- 现在剩下的问题
  已经不再是：
  - branch-level
    大方向
    还没拆清
- 而更像：
  - sink local pocket
    内
    为什么这些 pre
    已经踩进
    `gain + cosine`
    的 sink-side，
    却仍没有真的走成 sink

## 结论

1. `001705 -> 001543` 不是继续放大 shared-target hinge 的 interference package；真正把它送进 sink 的，是：
   - 更弱 gain
   - 更短 reference
   - 更低 cosine
2. `000664 -> 001543` 也不是继续向 `v64_only` 更深；它几乎不再压 `v64`，而是主要把：
   - `v65`
     再明显压负，
   同时伴随：
   - 更低 cosine
   - 更短 reference
   - 更弱 gain
3. 两条终分歧当前最紧的共同 support pair 都落在：
   - `gain + cosine`
   不是：
   - `reference + gain`
4. 但 `gain + cosine both` 里仍残留少量 pre，
   所以它依旧只是 sink local support pair，
   不是 hard gate。
5. 当前最合理的下一步，
   不应再回到 branch-level 均值解释；
   默认应只继续拆 sink pocket 内的 false positives：
   - `001543 -> 000697`
   - `001543 -> 000799`
   看为什么这些 row
   已经踩进
   `gain + cosine`
   的 sink-side，
   却仍停在 pre。
