# 2026-03-24 `candidate_v7` `v65` sink reference-gain edge residual split

## 背景

上一轮已经把
`duration + cosine`
shell
里的
`boundary`
routing
收紧成：

- `reference + gain`
  是当前最像
  boundary
  的 conjunction
- 但
  `both`
  桶里仍混着：
  - `2` 条 hinge
  - `1` 条 `v64_only`
  - `1` 条 pre
  - `0` 条 sink

因此这一步只继续回答两个窄问题：

1. 为什么
   `train_000951`
   仍会残留在
   `reference + gain both`
   里，
   但还没跨进
   crossed edge
2. 为什么
   `hinge / v64_only`
   会优先贴在
   这条边上，
   却没有直接继续走成 sink

## 本轮做法

这一步不加新脚本，
只复用已有分析脚本，
并把
`reference + gain both`
桶显式拆成：

- `reference_gain_both_crossed`
  - `train_001705`
  - `train_001610`
  - `train_000664`
- `reference_gain_both_pre`
  - `train_000951`

本轮新增资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_both_crossed_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_both_pre_train.txt`

本轮输出：

1. edge split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_split/summary.json`
2. edge factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_factor_contrast/summary.json`
3. edge slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_slice_support/summary.json`
4. `000951`
   局部 neighbor scan：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_pre_neighbor_scan/summary.json`
5. `interference transient + cosine`
   edge quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_interference_cosine_quadrants/summary.json`

## 结果

### 1. `reference + gain both` 不是 hard edge，而是一层更宽的 mixed shelf；`train_000951` 只是这层 shelf 里仍然明显 pre 的残留

把
`reference + gain both`
显式拆成：

- crossed：
  - `train_001705`
  - `train_001610`
  - `train_000664`
- pre：
  - `train_000951`

后，行为均值直接变成：

- crossed mean：
  - `v66 - v64 = +0.004184 dB`
  - `v66 - v65 = -0.015859 dB`
- `train_000951`：
  - `v66 - v64 = +0.027298 dB`
  - `v66 - v65 = +0.101198 dB`

也就是：

- crossed
  这组已经贴到：
  - `v64`
    近零
  - `v65`
    刚翻负
- 但
  `000951`
  还稳稳停在：
  - `v64`
    正 gap
  - `v65`
    正 gap

所以当前不能再把：

- `reference + gain both`

写成：

- crossed hard edge

更准确的口径应改成：

- crossed-support shelf

### 2. `train_000951` 的残留，不是“gain 还不够”；相反，它已经在 gain 上走得过头，真正落后的更像 `reference + cosine`

用：

- `target = reference_gain_both_crossed`
- `baseline = reference_gain_both_pre`
- `contrast = v65_sink`

做 branch factor contrast，
当前标准化 residual
前三位是：

- `reference_duration_sec = +2.3843 z`
- `interference_layers.0.gain_db = +2.2473 z`
- `target_interference_logspec_cosine = +1.6143 z`

但这里的方向要特别注意：

- crossed
  相对
  `000951`
  的：
  - `reference`
    更长
    `+0.40 sec`
  - `cosine`
    更高
    `+0.010672`
  - `gain`
    反而更低
    `-1.141667 dB`

也就是：

- `000951`
  不是还差：
  - 更强 gain
- 它其实已经比 crossed
  站得更靠：
  - strong-gain
    那一头

因此当前应改写成：

- `000951`
  留在 pre，
  不是因为
  `gain`
  不够
- 而是因为它只踩中了
  上游
  `reference + gain`
  shelf，
  但还没把：
  - `reference`
    再往 crossed
    那侧推深
  - `cosine`
    再抬到 crossed
    那一侧

### 3. `000951` 的局部邻域也是 mixed shelf，不是“只差一步就进 crossed”的单线 near-miss

以
`train_000951`
为 seed
做 local neighbor scan，
最近 `12` 条搜索邻居里，
状态直接混成：

- `6` 条 pre
- `2` 条 hinge
- `2` 条 `v64_only`
- `1` 条 `both_crossed_v64_deeper`
- `1` 条 sink

而且：

- 最近前三条
  仍全是 pre：
  - `train_000578`
  - `train_001006`
  - `train_001725`
- 第一条 hinge
  要到：
  - `train_001705`
    rank `6`

这说明：

- `000951`
  当前所处位置
  不是：
  - 单线 crossed 入口
- 而是：
  - 一个混合 shelf
    中的 pre 残留点

所以不能把它简写成：

- “已经是 crossed，
  只差最后一点”

### 4. `000951` 与 `001705` 的 target transient 完全相同，进一步证明 `000951` 不是被 target 侧 transient 卡住

当前一个更硬的个例事实是：

- `train_000951`
  与
  `train_001705`
  的：
  - `target_transient_presence_minus_mid_db_mean`
    都是
    `-6.375519`
  - `target_transient_presence_share_mean`
    都是
    `0.155784`

但它们的状态却不同：

- `train_000951`
  仍是 pre
- `train_001705`
  已是 hinge

两者真正拉开的更像：

- `reference`
  - `2.16 -> 2.64`
- `gain`
  - `+0.158 -> -1.49`
- `interference transient mean`
  - `0.7970 -> 9.6094`
- `interference transient share`
  - `0.3677 -> 0.7196`
- `cosine`
  - `0.6172 -> 0.6415`

所以这一步可以继续排除：

- `000951`
  还没跨过去，
  是因为 target transient
  还没起来

当前更准确的写法是：

- `000951`
  的 target 侧
  已经不构成主 blocker
- 真正还没到位的，
  是 interference package
  加上更长 reference
  与更高 cosine

### 5. `hinge / v64_only` 会优先落在这条边上，是因为这条边本来就更像“crossed-support shelf”，不是 sink route

当前
`reference + gain both`
里的 crossed
三条是：

- `train_001705`
  - hinge
- `train_001610`
  - hinge
- `train_000664`
  - `v64_only`

同时：

- sink
  `train_001543`
  不在这条边上
- 它相对
  `000951`
  虽然也共享：
  - 更高 interference transient
  - 更低 gain
  但：
  - `reference`
    反而更短
  - `cosine`
    也更低

这说明：

- `reference + gain`
  这条边
  不是 sink 路线
- 它更像：
  - pre
    先贴到
    boundary-support shelf
  - 然后在 shelf 上
    优先出现：
    - hinge
    - `v64_only`
      这些 crossed state
- 要继续走成 sink，
  还得把：
  - `reference`
  - `gain`
    再往回折返

也就是：

- hinge / `v64_only`
  优先落在这里，
  不是偶然污染
- 而是因为这里本来就是：
  - crossed-support
    但非 sink
    的 shelf

### 6. `interference transient + cosine` 只能解释 `000951` 为什么不在 crossed center，但仍不是硬 gate

把：

- `interference transient mean`
- `cosine`

做成 direct quadrants 后，
当前 anchor 位置为：

- crossed anchor
  在：
  - `both`
- `000951`
  在：
  - `neither`
- sink
  `001543`
  在：
  - `factor_a_only`

这说明：

- `000951`
  的确缺少：
  - crossed-side
    interference package
  - crossed-side cosine
- sink
  也确实不共享：
  - higher cosine
    这一侧

但：

- `both`
  桶里仍有：
  - `11` 条 pre
  - `3` 条 hinge
  - `1` 条 `v64_only`

所以这一步也只能继续写成：

- support pair

不能升级成：

- hard gate

## 结论

1. `reference + gain both` 现在应正式改写成一层 crossed-support mixed shelf，而不是 hard edge；`train_000951` 只是这层 shelf 里唯一仍明显 pre 的残留。
2. `train_000951` 的残留，不是因为 `gain` 还不够；相反，它已经更靠 strong-gain 一侧。相对 crossed，它真正落后的更像：更短 `reference`、更低 `cosine`，以及没把 interference package 一起带起来。
3. `train_000951` 与 `train_001705` 共享完全相同的 target transient，但状态一 pre 一 hinge，说明当前不应再把 target 侧 transient 写成 `000951` 的主 blocker。
4. `hinge / v64_only` 会优先落在 `reference + gain` 这条边上，是因为这条边本来就属于 crossed-support shelf，而不是 sink route；sink 还要求把 `reference / gain` 再向另一侧折回。
5. 当前最合理的下一步，不应再把 `reference_gain_both_crossed` 当成单一机制继续做均值解释；默认应收紧成 case-level 双分支：
   - `000951 -> 001705`
     这条
     shared-target
     子路径
   - `000951 -> 001610 / 000664`
     这条
     low-target-share
     子路径
   继续解释 crossed edge 内部为什么会分成 hinge 与 `v64_only`。
