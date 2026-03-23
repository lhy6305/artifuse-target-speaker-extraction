# 2026-03-24 `candidate_v7` `v65` sink duration vs cosine split

## 背景

上一轮已经把
`001589 -> 001543`
的最后边界
收紧成：

1. `target_duration`
   更强
2. `cosine`
   更干净
3. 但两者都还不是
   独立 hard gate

因此当前更窄的问题
已经只剩：

- 到底该把
  near-sink
  最后托住
  `train_001589`
  的主语
  写成：
  - 长 duration 壳
  还是：
  - 高 cosine
    仍在继续托住
    `v64 buffer`

## 本轮做法

这一步继续不加新脚本，
直接复用上一轮
已经补好的：

- `scripts/eval/analyze_proxy_factor_slice_support.py`
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

输入固定为：

- `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`
- `reports/eval/active_targetfull_clean_failboth_v65_sink_hinge_ladder_split/summary.json`

目标固定为：

- `target_group = v65_sink`
- `baseline_group = weak_gain_partial_mean_hinge`
- `contrast_group = weak_gain_hinge_floor`

本轮只看两个字段：

- `target_duration_sec`
- `target_interference_logspec_cosine`

输出两份 focused summary：

1. 单因子 target-side support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_slice_support/summary.json`
2. 双因子 quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_quadrants/summary.json`

## 结果

### 1. `duration` 与 `cosine` 都能保住同一批 boundary-support rows，但单独任何一边都不够

slice support
显示：

- `target_duration`
  的 target-side
  为：
  - `1` 条 sink
  - `2` 条 hinge
  - `2` 条 `v64_only`
  - `17` 条 pre
- `cosine`
  的 target-side
  为：
  - `1` 条 sink
  - `2` 条 hinge
  - `2` 条 `v64_only`
  - `13` 条 pre

也就是：

- 两者都能保住
  同一批真正贴边的
  boundary-support rows：
  - `train_001543`
  - `train_001705`
  - `train_001610`
  - `train_000664`
  - `train_000210`
- 但
  `cosine`
  会额外排掉
  一部分纯 pre
  行，
  所以它确实更干净

### 2. 但真正更像主 blocker 的仍是 `duration`，因为它把 `001589` 和 floor hinge `000266` 拉开的幅度远大于 `cosine`

本轮最关键的新数值
不是 target-side 计数，
而是：

- `target_duration`
  的 midpoint
  为：
  - `1.71 sec`
  - `001589`
    离 target-side
    还差：
    - `0.57 sec`
  - `000266`
    离 target-side
    只差：
    - `0.03 sec`
  - 两者间的
    gap 差
    为：
    - `0.54 sec`
- `cosine`
  的 midpoint
  为：
  - `0.661089`
  - `001589`
    离 target-side
    还差：
    - `0.053765`
  - `000266`
    离 target-side
    只差：
    - `0.041001`
  - 两者间的
    gap 差
    只有：
    - `0.012763`

这说明：

- 对
  `001589`
  相对
  `000266`
  “还差多远”
  这件事，
  `duration`
  给出的分离
  远比
  `cosine`
  大
- 因而如果只能保留
  一个主语，
  当前更应该保留：
  - 长 duration 壳

### 3. `cosine` 更像 secondary trim，因为它单独成立时根本抓不住任何真正贴边的 row

quadrants
进一步把这层关系
写死成：

- `both`
  桶：
  - `1` 条 sink
  - `2` 条 hinge
  - `2` 条 `v64_only`
  - `11` 条 pre
- `duration-only`
  桶：
  - `6` 条
  - 全部都是
    pre
- `cosine-only`
  桶：
  - `2` 条
  - 也全部都是
    pre
- `neither`
  桶：
  - `train_000266`
  - `train_001589`
  - `train_000219`

这一步最关键的含义是：

- 真正贴到
  sink 边界
  的样本，
  没有任何一条
  落在：
  - `duration-only`
  或：
  - `cosine-only`
- 它们都要求：
  - 短 duration
  - 低 cosine
    同时成立

所以当前更准确的写法
应改成：

- `cosine`
  不是独立 blocker
- 它更像：
  - duration shell
    上的
    secondary trim

### 4. 但 `duration + cosine` 的 conjunction 也还不是最后 hard gate，因为 `both` 桶里仍塞着大量 pre

`both`
桶里虽然已经包含：

- sink
- hinge
- `v64_only`

但同时仍混着：

- `11` 条 pre

所以这一步可以继续排除：

- “只要
   短 duration
   + 低 cosine
   就会进 sink”

更准确的层级
应固定为：

1. `duration`
   = 当前更强的
   主 blocker
2. `cosine`
   = 更干净的
   secondary trim
3. `duration + cosine`
   = boundary-support shell
4. 但 shell 内
   还需要别的因素
   才能把 pre
   真正推成
   sink

## 结论

1. `target_duration` 仍应保留为 `train_001589` 没跨进 sink 的主 blocker，因为它把 `001589` 与 floor hinge `000266` 拉开的 target-side gap 是 `0.54 sec`，远大于 cosine 的 `0.012763`。
2. `target_interference_logspec_cosine` 仍有价值，但当前更准确的身份应写成：duration shell 上的 secondary trim，而不是与 duration 并列的主 blocker。
3. `duration-only` 与 `cosine-only` 两个桶都没有任何真正贴边的 hinge / `v64_only` row；所有 boundary-support rows 都落在 `duration + cosine both` 里，说明两者都不是独立 hard gate。
4. 当前最合理的下一步不再是继续问“duration 还是 cosine”，而应只看 `duration + cosine both` 这层 shell 内部，为什么还会残留大量 pre；默认只回到 `mean` 作为 shell 内 final push，不启动新训练。
