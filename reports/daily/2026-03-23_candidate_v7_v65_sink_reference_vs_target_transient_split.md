# 2026-03-23 `candidate_v7` `v65` sink reference vs target-transient split

## 背景

上一轮已经把
`v65 sink`
主线收紧成两层：

1. `short reference + weak gain`
   更像
   entry gate
2. 进入这个 gate
   之后，
   把
   `train_000266`
   从 hinge
   推成
   `train_001543`
   的最后半步，
   更像：
   - `reference`
     再缩短
   - 叠加
     `target transient`
     抬升

但这里还差一个
更严格的问题：

- 到底是：
  - `reference`
  还是：
  - `target transient`
  更接近
  `v65 sink`
  的最终主导

## 本轮做法

这一步分两层落盘：

### 1. 先把 `reference + gain` 做成交叉四象限

新增脚本：

- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

输入：

- `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`
- `reports/eval/active_targetfull_clean_failboth_post_entry_branch_divergence_split/summary.json`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_quadrants/summary.json`

目标是确认：

- `train_001543`
  是不是必须同时落在：
  - `short reference`
  - `weak gain`
  这两个 target-side
  才会进入 sink

### 2. 再把 `reference+gain both` 这格拆成 sink / hinge / pre

新增两个 group 资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_both_pre_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_both_nonsink_train.txt`

然后复用：

- `scripts/eval/analyze_proxy_group_split.py`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_vs_target_transient_split/summary.json`

当前比较四组：

- `v65_sink`
  - `train_001543`
- `reference_gain_both_hinge`
  - `train_000266`
- `reference_gain_both_pre`
  - `train_000216 / train_000788 / train_000207 / train_000117`
- `reference_gain_both_nonsink`
  - 上面两组并集

## 结果

### 1. `short reference + weak gain` 确实是一个 conjunction gate，而不是单因子门

四象限结果显示：

- `train_001543`
  的 anchor quadrant
  是：
  - `both`
- `train_001745`
  的 anchor quadrant
  是：
  - `neither`
- `train_000664`
  也在：
  - `neither`

而在当前窄 ring
里：

- `both`
  象限共有
  `6`
  条：
  - `1` 条 sink
  - `1` 条 hinge
  - `4` 条 pre
- `factor_a_only`
  也就是
  `reference-only`
  象限里
  没有 sink
- `factor_b_only`
  也就是
  `gain-only`
  象限里
  也没有 sink

所以当前可以正式写成：

- `short reference + weak gain`
  更像：
  - `v65 sink`
    的 conjunction gate
- 单独只有：
  - `reference`
  或：
  - `gain`
  都还不够把样本推进 sink

### 2. 但进入这个 gate 以后，真正更稳定把 sink 和非-sink 分开的，是 `target transient`，不是 `reference`

看
`v65_sink - reference_gain_both_pre`
这组 delta：

- `reference_duration_sec = -0.0375`
  几乎只差一点点
- 但：
  - `target_transient_presence_minus_mid_db_mean = +0.5340`
  - `target_transient_presence_share_mean = +0.04247`

这说明：

- 相比已经满足
  `reference+gain both`
  的 pre rows，
  `train_001543`
  并不是靠
  reference
  再明显缩短
  才变成 sink；
- 更稳定补上的，
  反而是：
  - target transient
    明显抬升

再看
`v65_sink - reference_gain_both_nonsink`
这组 delta：

- `reference_duration_sec = -0.084`
- `target_transient_presence_minus_mid_db_mean = +1.6097`
- `target_transient_presence_share_mean = +0.04528`

这里也是同样方向：

- `target transient`
  的分离更稳定，
  比
  `reference`
  更像：
  - gate 内部
    把 non-sink
    推成 sink
    的主导项

### 3. `reference` 仍然重要，但它更像“卡住 hinge -> sink 的最后一小段”，不是 gate 内对所有非-sink 都统一最强的分界

看
`v65_sink - reference_gain_both_hinge`
这组 delta：

- `reference_duration_sec = -0.27`
  说明：
  - `001543`
    相对
    `000266`
    reference
    确实继续更短
- 同时：
  - `target_transient_presence_minus_mid_db_mean = +5.9123`
  - `target_transient_presence_share_mean = +0.05654`

所以：

- 对
  hinge -> sink
  这条边界，
  `reference`
  仍然是重要因素；
- 但如果把视角放到
  整个
  `reference+gain both`
  象限，
  真正对：
  - sink
  vs
  - all non-sink
  更稳定的分离项，
  已经更偏向：
  - `target transient`

### 4. 当前最窄结论可以固定成两层结构：`reference+gain` 负责 entry，`target transient` 负责 gate 内 final push

因此当前主线应改写为：

1. `short reference + weak gain`
   负责把样本送进：
   - `reference+gain both`
     entry gate
2. 进入 gate
   以后，
   `target transient`
   的抬升
   更像：
   - 把 non-sink
     真正推进
     `v65 sink`
     的 final push
3. `reference`
   仍然保留作用，
   但更偏向：
   - hinge -> sink
     的局部补刀
   而不是：
   - gate 内
     所有非-sink
     的统一第一分界

## 结论

1. `short reference + weak gain` 已经可以固定为 `v65 sink` 的 conjunction entry gate。
2. 进入这个 gate 以后，`target transient` 比 `reference` 更稳定地区分了 sink 和 gate 内的非-sink，因此更接近当前 `v65 sink` 的最终主导。
3. `reference` 仍然重要，但更像针对 `hinge -> sink` 的局部补刀，而不是 gate 内统一最强的 final push。
4. 当前最合理的下一步，应继续收紧成只围绕 `target transient`，检查是：
   - `mean`
   还是：
   - `share`
   更接近 `v65 sink` 的最终主导。 
