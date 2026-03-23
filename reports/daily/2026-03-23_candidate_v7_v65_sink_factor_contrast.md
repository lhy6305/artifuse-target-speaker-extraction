# 2026-03-23 `candidate_v7` `v65` sink factor contrast

## 背景

上一轮已经把
`train_001543 / train_000664`
固定成：

- `v65 sink`
  isolation pair

并确认：

- `v66 - v64`
  几乎不动
- 真正单边翻负的是：
  - `v66 - v65`

当时保留下来的
候选触发组合
是：

- 更短 reference
- 更弱 gain
- 更早 overlap
- 更高双侧 transient
- 更低 cosine

但这里还差最后一步：

- 哪些只是
  `v65 sink`
  和
  `v64 pocket`
  都会共享的 package
- 哪些才是真正
  更偏向
  `v65 sink`
  这条分支的
  branch-specific factor

## 本轮做法

这一步新增：

- `scripts/eval/analyze_proxy_branch_factor_contrast.py`

做法不是再扩样本面，
而是直接复用已经落盘的
三角 split：

- target branch：
  - `post_entry_v65_deeper_than_v64`
    = `train_001543`
- baseline shelf：
  - `v64_only_crossed_unexpected`
    = `train_000664`
- contrast branch：
  - `post_entry_v64_deeper_than_v65`
    = `train_001745`

再把候选字段做成
branch-specific residual 排序。

输入：

- `reports/eval/active_targetfull_clean_failboth_post_entry_branch_divergence_split/summary.json`
- `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`

后者只用来提供
当前窄 ring 的
field stdev，
把 residual
标准化成可排序的
`z`
量级。

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_factor_contrast/summary.json`

本轮关注字段为：

- `reference_duration_sec`
- `interference_layers.0.start_offset_sec`
- `interference_layers.0.gain_db`
- `target_interference_logspec_cosine`
- `target_transient_presence_share_mean`
- `interference_transient_presence_share_mean`

## 结果

### 1. 在当前窄 ring 的标准化 residual 排序里，`reference_duration_sec` 是最强的 `v65 sink`-specific 因子

排序结果里，
`abs_target_specific_residual_z`
最高的是：

- `reference_duration_sec`
  - target-specific residual
    `= -1.05`
  - standardized residual
    `= 2.0673 z`

它的含义是：

- `train_001543`
  相对
  `train_000664`
  确实显著更短；
- 更关键的是，
  这一步在
  `train_001745`
  那条
  `v64 pocket`
  支路里
  并没有一起出现，
  因为：
  - `001745 - 000664`
    的
    `reference_duration_sec`
    只有
    `+0.03`

所以当前可以把：

- 更短 reference

正式提到
`v65 sink`
主导因子候选的第一位。

### 2. `更早 overlap` 的 sink-specific 性甚至比 `gain` 更强；这一步要把它从“共享现象”升级成正式候选

当前第二强的
sink-specific residual
是：

- `interference_layers.0.start_offset_sec`
  - residual
    `= +0.138`
  - standardized residual
    `= 1.5845 z`

这里看起来是正号，
原因只是：

- `001543`
  相对
  `000664`
  的更早 overlap
  没有
  `001745`
  那么极端；
  也就是：
  - 两条分支
    都有更早 overlap
  - 但
    `001745`
    更早得更多

这一步的重要修正是：

- 更早 overlap
  不能再被简单归到
  “shared package”
  然后忽略；
- 它对
  `v65 sink`
  仍然有
  明确 branch-specific
  区分力，
  只是方向上表现为：
  - sink branch
    没有 pocket
    那么极端早

因此下一步如果还要继续压，
`start_offset`
  必须正式留在候选里，
而且优先级已经高于
`gain`

### 3. `gain` 仍然重要，但已经降到第三位；`cosine` 则明显太弱，不适合继续当主导因子写

当前第三强的
sink-specific residual
是：

- `interference_layers.0.gain_db`
  - residual
    `= -2.356`
  - standardized residual
    `= 1.2125 z`

说明：

- `001543`
  相对
  `000664`
  的更弱 gain
  仍然是有效信号；
- 但它的 branch-specific
  强度
  已经弱于：
  - 更短 reference
  - 更早 overlap

而：

- `target_interference_logspec_cosine`
  的 standardized residual
  只有：
  - `0.2609 z`

这已经明显太弱，
不适合继续当作
`v65 sink`
的主导候选去写。

所以当前应明确修正为：

- `cosine`
  可以降级成
  弱辅助信号；
- 不应再和
  `reference / overlap / gain`
  并列当主因子

### 4. 双侧 transient share 更像 shared package，不是决定 sink branch identity 的主导项

两条 transient share
的 standardized residual
分别只有：

- `target_transient_presence_share_mean = 0.5273 z`
- `interference_transient_presence_share_mean = 0.3164 z`

这说明：

- 更高双侧 transient share
  确实会随
  `v65 sink`
  一起出现；
- 但它并不能有效区分：
  - `v65 sink`
  和
  - `v64 pocket`

换句话说：

- transient share
  更像：
  - post-entry 分支共享 package
  的一部分
- 不是当前
  sink branch identity
  的主导因子

## 结论

1. 当前窄 ring 里，对 `v65 sink` 最强的 branch-specific 因子是 `reference_duration_sec`，其次是 `interference_layers.0.start_offset_sec`，再其次才是 `interference_layers.0.gain_db`。
2. `target_interference_logspec_cosine` 的 residual 只有 `0.2609 z`，已经明显过弱，应从主导因子候选里降级。
3. 更高双侧 transient share 更像 post-entry 分支共享 package，不足以解释为什么 `001543` 会走成 `v65 sink`。
4. 当前最合理的下一步应继续收紧成只拆：
   - 更短 reference
   - 更早 overlap
   这两项里谁更接近 `v65 sink` 的真正主导因子；
   `gain` 作为第三候选保留，
   `cosine` 暂时退出主线。 
