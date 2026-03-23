# 2026-03-23 `candidate_v7` pure-signature vs `v65` drift neighbor-ring split

## 背景

上一轮已经确认：

- pure `v67` takeover edge `3`
  周围最近的 train-side 邻域
  不是单线外扩，
  而是：
  - shell-like `v66-top`
  - pure-signature `v67-top`
  - `v65` drift `v67-top`
    三层 mixed ring

但还差最后一个更细问题：

- 在 pure-signature `v67-top`
  与 `v65` drift `v67-top`
  之间，
  到底是哪条边界先塌；
- 以及
  `train_001589`
  到底更像：
  - pure takeover 的末端
  - 还是已经进入
    `v65`
    drift 组

如果这一步切清，
当前默认下一步
就可以继续从：

- “围绕两组 ring 做 split”

收紧成：

- “只盯 `v66 > v64`
   保护带何时塌平”

## 本轮做法

### 1. 先把两组 ring 正式物化成可复用资产

新资产：

- pure-signature `v67-top 5`
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_pure_signature_v67_top_5_all.txt`
  - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_pure_signature_v67_top_5.jsonl`
  - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_pure_signature_v67_top_5_all.jsonl`
- `v65` drift `v67-top 4`
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_v65_drift_v67_top_4_all.txt`
  - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_v65_drift_v67_top_4.jsonl`
  - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_v65_drift_v67_top_4_all.jsonl`

对应 sample-id 为：

- pure-signature `5`
  - `train_000216`
  - `train_000759`
  - `train_000799`
  - `train_001006`
  - `train_001639`
- `v65` drift `4`
  - `train_000266`
  - `train_001589`
  - `train_001610`
  - `train_001745`

### 2. 补一个 group-split 汇总脚本

新增：

- `scripts/eval/analyze_proxy_group_split.py`

作用：

- 读多个显式 sample-id group；
- 同时拼：
  - manifest 字段
  - `metadata.json` 字段
  - compare 结果
- 输出：
  - 每组均值
  - 组内代表样本
  - pairwise delta
  - aggregate ranking

### 3. 对两组 ring 直接做 split summary

输出：

- `reports/eval/active_targetfull_clean_failboth_neighbor_ring_split/summary.json`

字段仍固定为：

- manifest：
  - `target_transient_presence_minus_mid_db_mean`
  - `target_transient_presence_share_mean`
  - `interference_transient_presence_minus_mid_db_mean`
  - `interference_transient_presence_share_mean`
  - `target_interference_logspec_cosine`
- metadata：
  - `target_duration_sec`
  - `reference_duration_sec`
  - `interference_layers.0.gain_db`
  - `interference_layers.0.start_offset_sec`
- compare：
  - `v20`
  - `v24`
  - `v64`
  - `v65`
  - `v66`
  - `v67`

## 结果

### 1. pure-signature `5` 与 `v65` drift `4` 都已经处在高 interference transient 区间，所以“transient 升高”本身不是分界

两组均值分别为：

#### pure-signature `v67-top 5`

- `interference_transient_presence_minus_mid_db_mean = 5.294541`
- `interference_transient_presence_share_mean = 0.423214`

#### `v65` drift `v67-top 4`

- `interference_transient_presence_minus_mid_db_mean = 6.157284`
- `interference_transient_presence_share_mean = 0.442767`

两组差值只有：

- transient mean：
  - `-0.862743`
- transient share：
  - `-0.019553`

这说明：

- `v65`
  是否已经进场
  不能靠
  “transient 开始升高”
  来解释；
- 因为 pure-signature `5`
  本身也已经处在
  不低的 transient 区间

### 2. 真正把两组拉开的主边界是 `v66 > v64` 保护带是否塌平，而不是 `v66 > v67` 单独再差多少

两组均值对照：

#### pure-signature `v67-top 5`

- `v66 > v64 = +0.065665`
- `v66 > v65 = +0.164763`
- `v66 > v67 = -0.173643`
- aggregate：
  - `v67 > v66 > v64 > v24 > v65 > v20`

#### `v65` drift `v67-top 4`

- `v66 > v64 = +0.007218`
- `v66 > v65 = -0.036646`
- `v66 > v67 = -0.133630`
- aggregate：
  - `v67 > v65 > v66 > v64 > v24 > v20`

pairwise delta
`pure_signature - v65_drift`
最关键的是：

- `mean_v66_minus_v64 = +0.058448`
- `mean_v66_minus_v65 = +0.201409`
- `mean_v66_minus_v67 = -0.040013`

大白话讲：

- 两组都会输给
  `v67`
- 但 pure-signature `5`
  还保着一层
  `v66 > v64`
  和
  `v66 > v65`
  的缓冲
- `v65` drift `4`
  则是这层缓冲已经被磨平，
  于是
  `v65`
  开始一起挤进来

### 3. metadata 侧也支持“先塌的是保护带，不是简单的 louder / longer”

pairwise delta
`pure_signature - v65_drift`
为：

- `target_duration_sec = -0.2865 sec`
- `reference_duration_sec = -0.4050 sec`
- `interference_gain_db = +0.7323 dB`
  - 即：
    - pure-signature 反而更弱一些
- `start_offset_sec = +0.01885 sec`
- `cosine = -0.00819`

这说明：

- `v65` drift
  相对 pure-signature
  并不是被某个单字段
  大幅拉开的
- 更接近的是：
  - target / reference
    稍变长
  - transient 再抬一点
  - 但真正决定行为翻转的，
    仍是
    `v66 > v64`
    这层 margin
    是否还在

### 4. `train_001589` 已经稳定站在 `v65` drift 组里，不再适合回写到 pure takeover 边缘

`train_001589`
在本轮 split 里：

- 被正式物化到：
  - `v65` drift `v67-top 4`
- 组内方向为：
  - `v66 > v64 = +0.039198`
  - `v66 > v65 = -0.053612`
  - `v66 > v67 = -0.131577`

它与：

- `train_000266`
- `train_001610`
- `train_001745`

共同构成的不是：

- pure `v67` takeover
  的自然延长

而是：

- 已经把
  `v66 > v65`
  一起翻掉的
  drift ring

## 当前结论

1. pure-signature `v67-top 5`
   和 `v65` drift `4`
   的分界，
   不能再写成：
   - transient 从低到高
2. 当前更准确的边界应固定为：
   - `v66 > v64`
     是否还保有稳定正 margin
   - 一旦这层 margin
     被磨到接近 `0`
     `v65`
     就开始一起进入
3. `train_001589`
   当前应正式并入：
   - `v65` drift `v67-top`
     这条线
   不再作为 pure takeover
   边缘样本保留

## 当前默认下一步

默认顺序继续收紧为：

1. 不再继续围绕：
   - `train_001589`
     是否还算 pure edge
   反复判断；
   这件事当前已经定性。
2. 若还继续推进，
   默认只围绕：
   - pure-signature `v67-top 5`
   - `v65` drift `v67-top 4`
   做保护带塌缩诊断。
3. 下一步默认解释目标
   应固定为：
   - 哪些 row
     还能保住
     `v66 > v64`
     的最后一层 buffer
   - 以及这层 buffer
     与：
     - target / reference length
     - gain / offset
     - cosine
     的共变关系
4. 仍不启动新训练。
