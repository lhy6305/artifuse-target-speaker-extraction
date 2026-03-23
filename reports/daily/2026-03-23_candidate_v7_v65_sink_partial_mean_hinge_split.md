# 2026-03-23 `candidate_v7` `v65` sink partial-mean hinge split

## 背景

上一轮已经把
weak-gain
壳内结构
收紧成：

1. `gain`
   只是外壳
2. 真正把 hinge
   推成 sink
   的第一主轴
   仍是：
   - `target transient mean`

因此当前最窄的问题
已经只剩：

- 为什么
  `train_001589`
  明明已经出现
  partial mean rise，
  却还没有跨到
  `train_001543`
  这一侧

## 本轮做法

这一步继续不加新脚本，
只补一个新 singleton：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_partial_mean_hinge_train.txt`

内容固定为：

- `train_001589`

然后继续复用：

- `scripts/eval/analyze_proxy_group_split.py`

做 one-to-one split：

1. `v65_sink`
   - `train_001543`
2. `weak_gain_partial_mean_hinge`
   - `train_001589`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_vs_partial_mean_hinge/summary.json`

## 结果

### 1. `train_001589` 确实已经不是 floor hinge，但它离 sink 还差一整段 `mean`

这一步最关键的 delta
是：

- `target_transient_presence_minus_mid_db_mean = +3.3921`
- `target_transient_presence_share_mean = +0.056997`

也就是：

- `train_001589`
  的
  `mean = -14.3527`
- `train_001543`
  的
  `mean = -10.9606`

所以现在可以把
`train_001589`
正式写成：

- weak-gain shell
  里已经抬起一截
  `mean`
  的 near-sink hinge

但它仍然没有抬到
sink
那一档。

### 2. 这一步仍然不是 `gain` 或 `overlap` 在主导

`v65_sink - weak_gain_partial_mean_hinge`
里：

- `gain = +0.107`
- `start_offset = +0.131 sec`

说明：

- sink
  的 gain
  仍然没有更弱
- overlap
  也仍然更晚，
  不是更早

所以这一步可以继续排除：

- 更弱 gain
- 更早 overlap

它们都不是
`001589 -> 001543`
的最后主导。

### 3. `001589` 卡住的位置是：`v66 < v65` 已成立，但 `v66 > v64` 还没被一起拖负

这一步的 margin
变化是：

- `v66 - v64`
  从
  `+0.0392 dB`
  走到
  `-0.0088 dB`
  额外下掉：
  - `0.0480 dB`
- `v66 - v65`
  从
  `-0.0536 dB`
  走到
  `-0.1140 dB`
  额外下掉：
  - `0.0604 dB`

这说明：

- `train_001589`
  已经具备：
  - `v66 < v65`
    的 hinge 身份
- 但它还没把：
  - `v66 > v64`
    一起拖到负侧

所以它更准确的状态
应写成：

- `v65 crossed`
  但
  `v64 buffer`
  仍未完全打穿

### 4. 除了 `mean` 还不够，`001589` 还带着明显更长的 duration 壳和更高 cosine

同步出现的
配套差异是：

- `target_duration_sec = -1.14`
- `reference_duration_sec = -1.68`
- `target_interference_logspec_cosine = -0.1075`

也就是：

- `train_001543`
  更短
- 更低 cosine

所以当前最稳的写法是：

- `001589`
  不只是
  `mean`
  还没抬够；
- 它还带着：
  - 更长 target/reference
  - 更高 cosine
    这一层 near-sink hinge 壳

## 结论

1. `train_001589` 已经是 weak-gain shell 里的 `partial mean rise` near-sink hinge，但它离 `train_001543` 还差 `+3.3921` 的 `target transient mean` 抬升。
2. `gain` 和 `overlap` 在这一步仍然不能当主语，因为 sink 相对 `001589` 的 gain 只差 `+0.107 dB`，而 overlap 还更晚 `+0.131 sec`。
3. `001589` 当前卡住的核心位置是：`v66 < v65` 已成立，但 `v66 > v64` 还没被一起拖到负侧。
4. 当前最合理的下一步应只拆 `mean` 对 `duration/cosine`，看 `001589` 没能跨进 sink 的最后那条边界，更像是 `mean` 还没抬够，还是长 duration 壳仍在托住 `v64 buffer`。 
