# 2026-03-24 `candidate_v7` `v65` sink pocket false-positive case contrast

## 背景

上一轮已经把
`train_001543`
固定成
singleton sink，
并确认：

- `001705 -> 001543`
- `000664 -> 001543`

这两条终分歧
共同最紧的 local support pair
都落在：

- `gain + cosine`

但这个 pair
还残留两条 pre：

- `train_000697`
- `train_000799`

所以当前问题
不再是：

- sink route
  还没拆清

而是：

- 为什么
  `000697 / 000799`
  虽然都已经踩进
  `gain + cosine`
  的 sink-side，
  却仍停在 pre

本轮因此不再继续做 branch-level 均值，
而是把它们各自单独对
`train_001543`
做 case contrast。

## 本轮做法

这一步不加新脚本，
只复用已有：

- `scripts/eval/analyze_proxy_group_split.py`
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`
- `scripts/eval/analyze_proxy_factor_slice_support.py`
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

先把：

- `train_001543`
- `train_000697`
- `train_000799`

放进同一份 split，
再做两条独立 contrast：

1. `000697 -> 001543`
   - `000799`
     作为 distractor
2. `000799 -> 001543`
   - `000697`
     作为 distractor

本轮新增输出：

1. 三组 split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_gaincosine_falsepositive_case_split/summary.json`
2. `000697 -> sink` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_factor_contrast/summary.json`
3. `000799 -> sink` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_to_sink_factor_contrast/summary.json`
4. `000697 -> sink` slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_slice_support/summary.json`
5. `000799 -> sink` slice support：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_to_sink_slice_support/summary.json`
6. `000697 -> sink` quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_duration_reference_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_duration_targettransient_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_reference_targettransient_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_reference_targetshare_quadrants/summary.json`
7. `000799 -> sink` quadrants：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_to_sink_duration_intmean_quadrants/summary.json`
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_to_sink_duration_intshare_quadrants/summary.json`

## 结果

### 1. `000799` 与 `000697` 虽然都踩进了 `gain + cosine` sink-side，但 compare margin 与 metadata 已经先说明它们不是同一种残留

先看三条 anchor 的 compare margin：

- `train_001543`
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`
- `train_000697`
  - `v66 - v64 = +0.027504 dB`
  - `v66 - v65 = +0.092676 dB`
- `train_000799`
  - `v66 - v64 = +0.065615 dB`
  - `v66 - v65 = +0.117254 dB`

也就是：

- 两条 false positive
  都还明显站在
  `pre margin`
  一侧；
- 但
  `000799`
  比
  `000697`
  还更 pre，
  并不是
  “同一残留再深一点”

再看 metadata：

- `000697`
  - `target_duration = 2.22 sec`
  - `reference = 2.52 sec`
  - `gain = -4.993 dB`
- `000799`
  - `target_duration = 1.50 sec`
  - `reference = 2.76 sec`
  - `gain = -3.311 dB`
- sink `001543`
  - `target_duration = 1.14 sec`
  - `reference = 1.68 sec`
  - `gain = -5.331 dB`

这已经先给出一个直观分叉：

- `000799`
  是两条 false positive
  里更短时长的那条；
- `000697`
  则是
  更长 duration
  且 reference
  也明显更长
  的另一条

### 2. `000799 -> 001543` 更像 short-duration false positive 上的 target / interference transient 全面塌陷，不是 gain / offset 还差一点

对
`target = sink`
`baseline = 000799`
`contrast = 000697`
做 factor contrast，
target-specific residual
前三位是：

- `interference_transient_presence_share_mean = +2.4473 z`
- `target_duration_sec = -2.4054 z`
- `interference_transient_presence_minus_mid_db_mean = +2.3615 z`

继续往下看，
仍排前列的是：

- `target_interference_logspec_cosine = +2.0376 z`
- `target_transient_presence_share_mean = +1.9498 z`

反过来说，
相对
`000799`，
真正把 row
送进 sink 的，
不是：

- gain 再降一点
- offset 再挪一点

因为这两项当前只剩：

- `gain = -0.3826 z`
- `offset = -0.0986 z`

而更像是：

- target duration
  继续缩短
- interference transient
  mean / share
  一起抬起
- target transient share
  也同步回收

从 pairwise delta
也能看到这点：

- `000799 - sink`
  当前是：
  - `target_duration = +0.36 sec`
  - `reference = +1.08 sec`
  - `target_transient_mean = -5.1124`
  - `target_transient_share = -0.0582`
  - `interference_transient_mean = -4.9647`
  - `interference_transient_share = -0.0423`
  - `gain = +2.020 dB`

这里最该注意的是：

- 它相对 `000697`
  确实是
  shorter-duration
  那条 false positive；
- 但相对 sink，
  更有分支区分力的
  不是单独的 duration，
  而是：
  - short duration
  - 配上
    target / interference transient
    同时偏塌

再看
`duration + interference transient mean`
四象限：

- sink `001543`
  在 `both`
- `000799`
  在 `neither`
- `000697`
  也在 `neither`
- `neither`
  当前只剩：
  - `train_000799`
  - `train_000697`
  - `train_000904`
  且全是
  `pre_entry_or_pure`

这说明：

- 对 `000799`
  而言，
  当前最像 blocker 的
  已经是：
  - duration
  - interference transient
    这组 transient shell
- 不是
  gain / cosine
  之后再差一点

### 3. `000697 -> 001543` 则是 long duration + long reference + low transient/share 的另一类 pre；其中 gain 更像 case-distinguishing 伴随项，不该被抬成主 blocker

对
`target = sink`
`baseline = 000697`
`contrast = 000799`
做 factor contrast，
target-specific residual
前三位是：

- `target_transient_presence_minus_mid_db_mean = +2.4405 z`
- `reference_duration_sec = -2.3324 z`
- `interference_layers.0.gain_db = -2.2866 z`

紧接着仍在前列的是：

- `target_transient_presence_share_mean = +2.2589 z`
- `target_interference_logspec_cosine = +2.1961 z`
- `interference_transient_presence_minus_mid_db_mean = +1.7443 z`

但这条线里
最需要防止写错的地方是：

- `gain`
  虽然在
  contrast residual
  里排得很前，
  但它主要表达的是：
  - `000697`
    相对
    `000799`
    没有那么 strong-gain
- 它不是
  `000697 -> sink`
  的主 blocker

因为看绝对 pairwise delta，
`000697 - sink`
的 gain
只差：

- `+0.338 dB`

真正更硬的绝对差异是：

- `target_duration = +1.08 sec`
- `reference = +0.84 sec`
- `target_transient_mean = -2.1758`
- `target_transient_share = -0.0502`
- `interference_transient_mean = -6.7214`
- `interference_transient_share = -0.0789`

所以
`000697`
更准确的口径应改成：

- long duration
- long reference
- low transient / share

而不是：

- 只是 gain
  还没压够

再看
`duration + reference`
四象限：

- sink `001543`
  在 `both`
- `000799`
  在 `factor_a_only`
  - 也就是：
    duration
    已经较短，
    但 reference
    仍长
- `000697`
  在 `neither`
- `neither`
  当前只剩：
  - `train_001589`
  - `train_000697`

这很关键，
因为它把
`000697`
单独钉在：

- long duration
- long reference

这条更接近
`001589`
型 near-sink hinge
的宽类 pre

再看
`duration + target transient mean`
四象限：

- `000697`
  仍在 `neither`
- 但 `000799`
  只在 `factor_a_only`

这进一步说明：

- `000697`
  确实同时带着：
  - long duration
  - low target transient
- `000799`
  则不是同一宽类，
  它只是
  shorter-duration
  那条

### 4. 因而 sink pocket false positives 不能再写成单一“gain + cosine 之后的残留 pre”

本轮最关键的收口是：

- `000799`
  更像：
  - shorter-duration
    false positive
  - target / interference transient
    一起塌
- `000697`
  更像：
  - long duration
  - long reference
  - low transient / share
    的另一类 pre

也就是：

- 它们虽然都已经在
  `gain + cosine`
  的 sink-side，
  但：
  - `000799`
    不是
    `000697`
    的浅一点版本
  - `000697`
    也不是
    `000799`
    的长一点版本

## 结论

1. sink pocket false positives 已经正式证伪“同一种残留”口径；`000799` 与 `000697` 应拆成两类不同 pre。
2. `000799 -> 001543` 的主语应固定成：
   - shorter-duration false positive
   - target / interference transient 全面塌陷
   - gain / offset 不是当前主 blocker
3. `000697 -> 001543` 的主语应固定成：
   - long duration
   - long reference
   - low transient / share
   - `gain` 只保留为和 `000799` 对照时的 case-distinguishing 伴随项
4. 当前如果还要继续推进，
   默认不再把 sink pocket 回写成单一残留；
   应改成两条独立子问题：
   - `000799` 这条 transient-collapse pocket
   - `000697` 这条 long-duration / long-reference pocket
5. 本轮仍不启动新训练。
