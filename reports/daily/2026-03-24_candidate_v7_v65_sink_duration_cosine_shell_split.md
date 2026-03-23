# 2026-03-24 `candidate_v7` `v65` sink duration-cosine shell split

## 背景

上一轮已经把
`001589`
没跨进 sink
的最后 blocker
收紧成：

1. `target_duration`
   是主 blocker
2. `cosine`
   是 secondary trim
3. 真正贴边的 row
   都要求：
   - `duration + cosine both`

因此当前更窄的问题
已经不再是：

- `duration`
  还是
  `cosine`

而是：

- 在
  `duration + cosine both`
  这层 shell
  里面，
  为什么还会残留
  大量 pre

## 本轮做法

这一步继续不加新脚本，
只把
`duration + cosine both`
里的 row
正式拆成三组资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_duration_cosine_both_pre_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_duration_cosine_both_boundary_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_duration_cosine_both_nonsink_train.txt`

其中：

1. `both_pre`
   - `11` 条
   - 全是
     `pre_entry_or_pure`
2. `both_boundary`
   - `4` 条
   - `2` 条 hinge
   - `2` 条 `v64_only`
3. `both_nonsink`
   - 上面两组合并
   - 共 `15` 条

然后复用：

- `scripts/eval/analyze_proxy_group_split.py`
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`

输出：

1. shell group split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_shell_split/summary.json`
2. shell 内 sink-specific factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_shell_factor_contrast/summary.json`

## 结果

### 1. `duration + cosine both` 不是 near-sink 小壳，而是一个很宽的 mixed shell

本轮 shell
的真实结构是：

- `1` 条 sink
- `4` 条 boundary
- `11` 条 pre

也就是：

- 真正贴边的 row
  虽然都要求
  `duration + cosine both`
- 但反过来
  进入
  `both`
  并不意味着
  已经接近 sink

所以当前不能再把：

- `duration + cosine both`

写成：

- near-sink 小壳

它更准确的是：

- 一个很宽的
  boundary-support shell

### 2. 这层 shell 里的 pre 不是“mean 还低一点”的残留，而是混着一批 mean 已经很高、但 margin 仍稳定的 row

`both_pre`
里，
按
`target_transient_mean`
从高到低排，
最典型的几条是：

- `train_000578 = -3.4491`
- `train_001495 = -4.9590`
- `train_001725 = -5.1932`
- `train_000951 = -6.3755`

而 sink
`train_001543`
只有：

- `-10.9606`

也就是：

- 这层 shell
  里已经存在
  一批
  `mean`
  比 sink
  还更高的 pre
- 它们的
  `v66 > v64`
  与
  `v66 > v65`
  仍然保持正值

所以当前可以正式排除：

- shell 内残留 pre
  只是因为
  `mean`
  还没抬够

### 3. shell 内真正把 sink 从 boundary / pre 里再切出来的，已经不是 `mean`，而是 `gain`、`reference`、`offset`

用：

- `target = v65_sink`
- `baseline = duration_cosine_both_boundary`
- `contrast = duration_cosine_both_pre`

做 factor contrast，
当前标准化 residual
排序前三是：

- `interference_layers.0.gain_db = -1.4061 z`
- `reference_duration_sec = -0.7075 z`
- `interference_layers.0.start_offset_sec = +0.6134 z`

而：

- `cosine = -0.4143 z`
- `target_duration = -0.1379 z`
- `target_transient_mean = -0.0223 z`

说明：

- 在
  `duration + cosine`
  已经固定住以后，
  `mean`
  基本已经没有
  额外分离力
- 真正还在把
  sink
  从 shell 内
  切开的，
  反而是：
  - 更弱 gain
  - 更短 reference
  - 略更晚 offset

### 4. `pre -> boundary -> sink` 在这层 shell 内不是单调的 mean 梯子，而是另一套 margin routing

group split
也对应着同样现象：

- `boundary - pre`
  的：
  - `target_transient_mean = -1.5486`
  - `gain = +2.0691`
  - `reference = +0.2932`
  说明：
  - boundary
    不是 mean 更高
      才从 pre 里出来；
  - 它反而平均上
    是：
    - mean 更低
    - gain 更强
    - reference 更长
- `sink - boundary`
  才出现：
  - `target_transient_mean = +1.4306`
  - 但同时还有：
    - `gain = -4.7648`
    - `reference = -0.615`

所以当前更准确的层级
应改写成：

1. `duration + cosine`
   负责把 row
   送进宽 shell
2. shell 内
   不是
   `mean`
   单轴继续爬坡
3. 真正把 row
   再路由成：
   - pre
   - boundary
   - sink
   的，
   更像：
   - gain
   - reference
   - offset
     这套 margin routing

## 结论

1. `duration + cosine both` 只是 boundary-support shell，不是 near-sink 小壳，因为里面仍有 `11` 条 pre、`4` 条 boundary、只有 `1` 条 sink。
2. shell 内残留的 pre 不能再写成“`mean` 还没抬够”；这层 shell 里已经存在多条 `mean` 高于 sink 的 pre row。
3. 在 `duration + cosine` 已固定的前提下，shell 内最强的 sink-specific 因子已经改成：更弱 `gain`、更短 `reference`、略更晚 `offset`；`mean` 的额外 residual 只剩 `-0.0223 z`。
4. 当前最合理的下一步应只拆 shell 内的 `gain / reference / offset`，看它们谁更接近把 `duration+cosine both` 里的 row 从 pre 再路由成 boundary / sink；仍不启动新训练。
