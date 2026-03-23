# 2026-03-23 `candidate_v7` `v65` sink factor slice support

## 背景

上一轮已经把
`v65 sink`
的 factor contrast
排了序，
得到：

- `reference`
  最强
- `overlap`
  第二
- `gain`
  第三

但 residual 排序
只回答了：

- 哪些字段
  更像 sink-specific

还没把另一层问题
彻底讲清：

- 这些字段里，
  哪些其实是
  `v65 sink`
  和
  `v64 pocket`
  共享的 post-entry package
- 哪些才是真正
  把两条支路
  分开的切片边界

## 本轮做法

这一步新增：

- `scripts/eval/analyze_proxy_factor_slice_support.py`

做法是：

1. 继续固定：
   - target sink
     = `train_001543`
   - baseline shelf
     = `train_000664`
   - contrast pocket
     = `train_001745`
2. 对每个候选字段，
   用
   `target`
   与
   `baseline`
   的中点
   把当前窄 ring
   近邻切成：
   - target-side
   - shelf-side
3. 再看：
   - target-side
     吸进了哪些 margin state
   - contrast branch
     `train_001745`
     是否也落在同一侧

输入：

- `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`
- `reports/eval/active_targetfull_clean_failboth_post_entry_branch_divergence_split/summary.json`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_factor_slice_support/summary.json`

本轮只切三项：

- `reference_duration_sec`
- `interference_layers.0.start_offset_sec`
- `interference_layers.0.gain_db`

## 结果

### 1. `reference` 是当前最干净的 sink-vs-pocket 分界，因为它把 `001543` 留在 sink-side，却把 `001745` 明确挡在另一侧

对
`reference_duration_sec`
来说：

- baseline
  = `2.70`
- target
  = `1.68`
- midpoint
  = `2.19`

所以：

- sink-side
  定义为：
  - `reference < 2.19`

关键结果是：

- `train_001745`
  的
  `reference = 2.73`
  不在 sink-side
- 也就是：
  - `contrast_on_target_side = false`

这说明：

- 更短 reference
  不是
  pocket branch
  会共享的 package
- 它是当前最干净的
  sink-vs-pocket
  切片边界

虽然 sink-side
里仍然混有很多
`pre`
row，
但当前主问题
不是要做单字段 hard gate，
而是要问：

- 这项字段
  能不能把
  `001543`
  和
  `001745`
  分开

在这个意义上，
`reference`
是当前最强的一项。

### 2. `overlap` 虽然 residual 排名第二，但它是 shared post-entry package，不是 sink-specific 分界

对
`interference_layers.0.start_offset_sec`
来说：

- baseline
  = `0.298`
- target
  = `0.200`
- midpoint
  = `0.249`

所以：

- sink-side
  定义为：
  - `start_offset < 0.249`

这时得到：

- `train_001745`
  的
  `start_offset = 0.062`
  也落在 sink-side
- 也就是：
  - `contrast_on_target_side = true`

同时 target-side
里还混进了：

- `hinge = 4`
- `v64_only = 1`
- `pre = 17`

这说明：

- 更早 overlap
  确实对 post-entry
  有推动作用
- 但它并不能把：
  - `v65 sink`
  和
  - `v64 pocket`
  分开

因此当前应该改写成：

- `overlap`
  是 shared post-entry package
  的强信号；
- 不是
  sink branch
  的主分界

### 3. `gain` 也能把 `001543` 和 `001745` 分开，但它的切片力弱于 `reference`

对
`interference_layers.0.gain_db`
来说：

- baseline
  = `-1.03`
- target
  = `-5.331`
- midpoint
  = `-3.1805`

所以：

- sink-side
  定义为：
  - `gain < -3.1805`

这里得到：

- `train_001745`
  的
  `gain = -2.975`
  不在 sink-side
- 也就是：
  - `contrast_on_target_side = false`

因此：

- 更弱 gain
  也确实有
  sink-specific
  区分力

但与
`reference`
相比，
它的问题是：

- target-side
  仍然吸进：
  - `hinge = 2`
  - `pre = 8`

而且前一轮 residual
也已经表明：

- `gain = 1.2125 z`
  弱于
  `reference = 2.0673 z`

所以：

- `gain`
  当前应保留为
  第三候选
- 但不能再排到
  `reference`
  前面

## 结论

1. 这一步已经把 `reference` 和 `overlap` 拆开了：`reference` 是真正把 `v65 sink` 和 `v64 pocket` 分开的切片边界，而 `overlap` 是两条 post-entry 分支共享的 package。
2. `gain` 也有 sink-specific 区分力，但强度弱于 `reference`，当前仍应排在第三位。
3. 当前最合理的下一步应继续收紧成只拆：
   - `reference`
   - `gain`
   这两项里，
   哪一项更接近 `v65 sink` 的真主导；
   `overlap`
   不再当主分界，
   而改写成 shared post-entry package。 
