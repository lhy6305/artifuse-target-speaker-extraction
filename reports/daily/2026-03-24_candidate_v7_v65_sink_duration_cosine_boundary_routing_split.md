# 2026-03-24 `candidate_v7` `v65` sink duration-cosine boundary routing split

## 背景

上一轮已经把
`duration + cosine both`
这层 shell
收紧成：

1. 这不是 near-sink 小壳，
   而是：
   - `11` 条 pre
   - `4` 条 boundary
   - `1` 条 sink
     的 mixed shell
2. shell 内残留
   不能再写成：
   - `mean`
     还没抬够
3. 真正需要继续拆的
   已经变成：
   - `gain`
   - `reference`
   - `offset`

因此当前更窄的问题
已经只剩：

- 在
  `duration + cosine`
  已经固定后，
  到底是谁
  先把 row
  从 pre
  推进 boundary，
  又是谁
  继续把它
  从 boundary
  分叉到 sink

## 本轮做法

这一步不加新脚本，
直接复用：

- `scripts/eval/analyze_proxy_branch_factor_contrast.py`
- `scripts/eval/analyze_proxy_factor_slice_support.py`
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

但把口径翻成：

- `target = duration_cosine_both_boundary`
- `baseline = duration_cosine_both_pre`
- `contrast = v65_sink`

也就是：

- 直接问：
  - boundary
    相对 pre
    的主轴是什么
  - 并检查
    sink
    是否还站在
    同一侧

本轮输出：

1. boundary factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_factor_contrast/summary.json`
2. boundary slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_slice_support/summary.json`
3. 两组 quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_reference_offset_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_reference_gain_quadrants/summary.json`

## 结果

### 1. `boundary` 相对 `pre` 的最强主轴已经固定成：更强 gain + 更长 reference

当前标准化 residual
排序前三位是：

- `interference_layers.0.gain_db = +2.4854 z`
- `reference_duration_sec = +1.3520 z`
- `interference_transient_presence_minus_mid_db_mean = -1.1194 z`

而：

- `target_interference_logspec_cosine = +0.5080 z`
- `interference_layers.0.start_offset_sec = -0.3507 z`
- `target_transient_mean = -0.2708 z`

所以当前可以正式写成：

- 当 row
  已经进入
  `duration + cosine`
  shell
  后，
  把它从 pre
  推成 boundary
  的最强变化
  不是：
  - `mean`
  - `duration`
  - `cosine`
  而是：
  - gain 变强
  - reference 变长

### 2. `offset` 更像 boundary 与 sink 共享的 package，不是 boundary-specific 主语

slice support
里：

- `start_offset`
  的：
  - `contrast_on_target_side = true`

也就是：

- sink
  `train_001543`
  也站在
  boundary
  的 target-side

所以当前应把：

- 更晚 offset

写成：

- pre -> boundary -> sink
  共享 package

而不是：

- 只属于 boundary
  的主分界

### 3. 真正把 `boundary` 与 `sink` 分开的，是 `gain` 和 `reference`，而且两者方向都和 sink 相反

slice support
里：

- `gain`
  的：
  - `contrast_on_target_side = false`
- `reference`
  的：
  - `contrast_on_target_side = false`

说明：

- sink
  不站在：
  - stronger gain
  - longer reference
    这一侧

也就是：

- `gain`
  与
  `reference`
  在这层里
  不是
  boundary 与 sink
  的共享入口
- 它们反而更像：
  - boundary-specific routing

大白话说：

- row
  从 pre
  进 boundary
  时，
  会朝：
  - 更强 gain
  - 更长 reference
    这边走
- 但要继续进 sink，
  反而要把这两项
  再折回去

### 4. `reference + gain` 已经是当前最像 boundary 的 conjunction，但还不是硬 gate

`reference + gain`
四象限里：

- target
  `boundary`
  anchor
  在：
  - `both`
- sink
  `train_001543`
  在：
  - `neither`

同时：

- `both`
  桶里有：
  - `2` 条 hinge
  - `1` 条 `v64_only`
  - `1` 条 pre
  - `0` 条 sink

这说明：

- `long reference + stronger gain`
  已经是
  当前最像
  boundary
  的 conjunction
- 但它仍然会混进：
  - `train_000951`
    这条 pre
  所以还不能写成
  独立 hard gate

### 5. `reference + offset` 不如 `reference + gain`，因为它会把 sink 放进 `offset-only`

`reference + offset`
四象限里：

- target
  `boundary`
  anchor
  在：
  - `both`
- sink
  `train_001543`
  在：
  - `factor_b_only`

而且：

- `both`
  桶里仍有：
  - `1` 条 hinge
  - `1` 条 `v64_only`
  - `3` 条 pre

所以这一步可以继续排除：

- `reference + offset`
  是当前
  最优 boundary carve

它更像：

- `reference`
  再叠加
  一层共享 offset package，
  但没有把
  sink
  明确排掉

## 结论

1. 在 `duration + cosine` 已经固定后，把 row 从 pre 推成 boundary 的最强主轴已经改写成：更强 `gain` + 更长 `reference`，不是 `mean`。
2. `offset` 更像 boundary 与 sink 共享的 package，因为 sink 也站在它的 target-side；它不适合继续写成 boundary-specific 主语。
3. `gain` 与 `reference` 才是当前 boundary 与 sink 的反向分叉轴：boundary 站在更强 gain / 更长 reference 一侧，sink 则不在这边。
4. 当前最合理的下一步应只拆 `reference + gain` 这条 boundary conjunction 里，为什么还会残留 `train_000951` 这类 pre，以及 `hinge / v64_only` 为什么会优先落在这里；仍不启动新训练。
