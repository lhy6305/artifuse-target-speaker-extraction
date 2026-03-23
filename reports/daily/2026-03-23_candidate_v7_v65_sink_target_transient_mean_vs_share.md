# 2026-03-23 `candidate_v7` `v65` sink target-transient mean vs share

## 背景

上一轮已经把
`v65 sink`
的因子层级
固定成：

1. `reference+gain`
   = conjunction entry gate
2. 进入 gate 以后，
   `target transient`
   更像 gate 内
   的 final push

因此当前最窄的问题
已经只剩一个：

- 在
  `target transient`
  里面，
  到底是：
  - `mean`
  还是：
  - `share`
  更接近
  `v65 sink`
  的最终主导

## 本轮做法

这一步不再加新脚本，
直接复用前面两类已有工具：

1. 用
   - `scripts/eval/analyze_proxy_branch_factor_contrast.py`
   对：
   - `v65_sink`
   - `reference_gain_both_nonsink`
   - `reference_gain_both_hinge`
   做局部 factor contrast，
   只比较：
   - `target_transient_presence_minus_mid_db_mean`
   - `target_transient_presence_share_mean`
   - `reference_duration_sec`
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_factor_contrast/summary.json`
2. 再用
   - `scripts/eval/analyze_proxy_factor_slice_support.py`
   看
   `mean`
   和
   `share`
   各自的 target-side
   切片，
   是否能把
   hinge anchor
   `train_000266`
   留在外面，
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_slice_support/summary.json`

## 结果

### 1. 在 gate 内的 factor contrast 排序里，`target transient mean` 现在已经正式超过 `share`

当前标准化 residual
排序为：

- `target_transient_presence_minus_mid_db_mean = 1.2788 z`
- `target_transient_presence_share_mean = 1.0665 z`
- `reference_duration_sec = 0.5316 z`

所以现在可以明确写成：

- 在
  `reference+gain`
  这个 gate 内，
  真正更稳定的
  final push
  候选，
  已经从：
  - 泛泛的
    `target transient`
  收窄成：
  - `target transient mean`
    第一
  - `target transient share`
    第二

### 2. `mean` 和 `share` 都能把 hinge anchor `train_000266` 留在 target-side 之外，但 `mean` 的切片更干净

slice support
里：

- `target_transient_presence_minus_mid_db_mean`
  的：
  - `contrast_on_target_side = false`
- `target_transient_presence_share_mean`
  的：
  - `contrast_on_target_side = false`

说明：

- 这两项
  都能把
  hinge anchor
  `train_000266`
  留在 target-side 之外；
- 两者都具备
  gate 内
  final-push
  的分界力

但进一步看
target-side
里的混入情况：

- `mean`
  target-side
  状态计数为：
  - `pre = 11`
  - `hinge = 1`
  - `sink = 1`
- `share`
  target-side
  状态计数为：
  - `pre = 9`
  - `hinge = 1`
  - `sink = 1`
  - `v64_only = 1`

这里最关键的是：

- `share`
  会把
  `train_000210`
  这条
  `v64_only`
  分支
  也一起吸进来；
- `mean`
  没有这个额外污染

因此当前更稳的写法是：

- `share`
  仍然有效，
  但更容易把
  非 sink 的
  旁支
  一起带进来
- `mean`
  是当前更干净的
  gate 内分界

### 3. 所以这条线现在可以正式收口成：`target transient mean` 是当前 `v65 sink` 的最终主导候选，`share` 是辅助项

综合两份 summary：

- `mean`
  有更高的
  residual z
- `mean`
  也没有把
  `v64_only`
  旁支
  一起吸进来

所以当前主线应正式改写成：

- `reference+gain`
  负责把样本送进 gate
- `target transient mean`
  负责 gate 内
  更稳定的
  final push
- `target transient share`
  保留为辅助项，
  但不再和
  `mean`
  并列

## 结论

1. `target transient mean` 现在已经明确超过 `share`，成为当前 `v65 sink` 的最终主导候选。
2. `target transient share` 仍然有分界力，但它更容易把 `v64_only` 旁支一起吸进来，因此应降级成辅助项。
3. 当前最合理的下一步，如果还继续推进，应固定成只围绕 `target transient mean`，检查它在当前窄 ring 里有没有更细的近邻支持，而不再把 `share` 和它并列。 
