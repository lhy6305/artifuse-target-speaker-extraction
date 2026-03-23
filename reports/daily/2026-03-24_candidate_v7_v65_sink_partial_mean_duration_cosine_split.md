# 2026-03-24 `candidate_v7` `v65` sink partial-mean duration-cosine split

## 背景

上一轮已经把
`train_001589`
固定成：

- weak-gain shell
  内部
  `partial mean rise`
  的 near-sink hinge

因此当前最窄的问题
已经收敛成：

- `001589`
  没跨进 sink，
  更像：
  - `mean`
    还没抬够
  还是：
  - 长 duration /
    高 cosine
    这层壳
    还在托住
    `v64 buffer`

## 本轮做法

这一步仍然不加新脚本，
只补一个新 singleton：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_hinge_floor_train.txt`

然后复用现有脚本
做四层落盘：

1. 三层 ladder split：
   - `v65_sink`
   - `weak_gain_hinge_floor`
   - `weak_gain_partial_mean_hinge`
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_hinge_ladder_split/summary.json`
2. factor contrast：
   - `v65_sink`
     相对
     `weak_gain_partial_mean_hinge`
     的最后边界，
     用
     `weak_gain_hinge_floor`
     做参照，
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partial_mean_edge_factor_contrast/summary.json`
3. 单因子 slice support：
   - `mean`
   - `target_duration_sec`
   - `reference_duration_sec`
   - `target_interference_logspec_cosine`
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_partial_mean_edge_slice_support/summary.json`
4. 两组 factor quadrants：
   - `mean + target_duration`
   - `mean + cosine`
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_targetduration_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_cosine_quadrants/summary.json`

## 结果

### 1. 按当前窄 ring 的标准化尺度，最后这条边界里排在 `mean` 前面的已经是 duration 和 cosine

factor contrast
对
`001543 - 001589`
这一步的排序
是：

- `reference_duration_sec = 3.3076 z`
- `target_duration_sec = 2.2258 z`
- `target_interference_logspec_cosine = 1.6606 z`
- `target_transient_mean = 0.7337 z`

所以当前如果还把：

- `001589`
  没进 sink

写成纯粹的：

- `mean`
  还没抬够

已经不够窄了。

### 2. 但 `reference` 不能直接升级成最后边界，因为 floor hinge `train_000266` 早就已经落在它的 target-side

slice support
里：

- `reference_duration_sec`
  的：
  - `contrast_on_target_side = true`

也就是：

- `train_000266`
  这条
  floor hinge
  也已经落到了
  短 reference
  那一侧

所以这里可以正式排除：

- `reference`
  是
  `001589 -> 001543`
  最后一条边界

它更像：

- 更早的壳层描述

### 3. 真正还能挡住 floor hinge 的，是 `target_duration` 和 `cosine`

slice support
里：

- `target_duration_sec`
  的：
  - `contrast_on_target_side = false`
- `target_interference_logspec_cosine`
  的：
  - `contrast_on_target_side = false`

说明：

- 这两项
  都还能把
  `train_000266`
  留在 target-side 外

而且
`001543`
相对
`001589`
的差异也都明显：

- `target_duration_sec = -1.14`
- `target_interference_logspec_cosine = -0.1075`

所以当前更稳的写法是：

- `001589`
  最后没跨过去，
  更像：
  - 长 target duration
  - 高 cosine
    这层壳
    还在

### 4. 在这两个候选里，`target_duration` 更强，`cosine` 更干净，但两者都还不是独立 hard gate

`mean + target_duration`
四象限里：

- `train_001543`
  在：
  - `both`
- `train_001589`
  与
  `train_000266`
  都在：
  - `neither`

但：

- `both`
  桶仍有：
  - `1` 条 sink
  - `1` 条 hinge
  - `10` 条 pre

`mean + cosine`
也是同样结构：

- `train_001543`
  在：
  - `both`
- `train_001589`
  与
  `train_000266`
  都在：
  - `neither`

但：

- `both`
  桶仍有：
  - `1` 条 sink
  - `1` 条 hinge
  - `8` 条 pre

所以当前更准确的判断是：

- `target_duration`
  比
  `cosine`
  更强
- `cosine`
  比
  `target_duration`
  略更干净
- 但两者都还不是
  独立 hard gate

### 5. 因而当前最窄结论应改写成：`mean` 是必要条件，但 near-sink 最后托住 `001589` 的更像 duration shell，cosine 是辅助约束

综合四份结果，
当前主线应更新成：

1. `001589`
   已经有：
   - partial mean rise
2. 但这还不够，
   因为在当前窄 ring
   标准化尺度里，
   真正排在
   `mean`
   前面的已经是：
   - duration shell
   - cosine shell
3. 其中：
   - `reference`
     不是最后边界，
     因为
     `000266`
     已经站到了
     它的 target-side
   - `target_duration`
     是当前更强的
     near-sink blocker
   - `cosine`
     是更干净的
     辅助约束

## 结论

1. `train_001589` 没跨进 sink，已经不能再写成单纯“`mean` 还没抬够”；在当前窄 ring 里，排在 `mean` 前面的已经是 `duration` 与 `cosine`。
2. `reference` 不再适合写成最后边界，因为 floor hinge `train_000266` 早已落在短 reference 的 target-side。
3. 当前更稳的写法是：`target_duration` 是 near-sink 最强 blocker，`cosine` 是更干净的辅助约束，`mean` 则是必要但不充分条件。
4. 当前最合理的下一步应只拆 `target_duration` 对 `cosine`，看 `001589` 最后没跨进 sink，更像是长 duration 壳在主导，还是高 cosine 还在继续托住 `v64 buffer`。 
