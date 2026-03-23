# 2026-03-23 `candidate_v7` `v65` sink weak-gain hinge split

## 背景

上一轮已经把
当前最窄的
`v65 sink`
局部 carve
收紧成：

- `target transient mean + weak gain`

但这里还差
最后一个更具体的问题：

- 既然
  `train_000266`
  和
  `train_001589`
  也都已经落在
  weak-gain
  这一侧，
  为什么只有
  `train_001543`
  会继续掉进
  sink

## 本轮做法

这一步不加新脚本，
只补一个新资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_hinge_train.txt`

内容固定为：

- `train_000266`
- `train_001589`

然后复用：

- `scripts/eval/analyze_proxy_group_split.py`

做两组 split：

1. `v65_sink`
   - `train_001543`
2. `weak_gain_hinge`
   - `train_000266`
   - `train_001589`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_weak_gain_hinge_split/summary.json`

## 结果

### 1. `gain` 在这一步已经只是外壳，不是最后推力

`v65_sink - weak_gain_hinge`
的：

- `interference_layers.0.gain_db = +0.083`

这里最关键的是：

- sink
  并没有
  更弱 gain；
- 相反，
  `train_001543`
  的 gain
  还比
  两条 hinge
  平均值
  略高一点点

同样，
`start_offset`
也是：

- `+0.090 sec`

也就是：

- sink
  overlap
  反而更晚，
  不是更早

所以当前可以正式写成：

- 在 weak-gain 壳内，
  真正把 hinge
  推成 sink
  的已经不是：
  - 更弱 gain
  - 更早 overlap

### 2. 壳内真正拉开的第一主轴仍然是 `target transient mean`

同一份 split
里，
最显著的 target-side
变化是：

- `target_transient_presence_minus_mid_db_mean = +4.6522`
- `target_transient_presence_share_mean = +0.05677`

也就是：

- `train_001543`
  的
  `mean = -10.9606`
- `weak_gain_hinge`
  均值只有：
  - `-15.6128`

这已经不是边缘波动，
而是明显整段抬升。

因此当前更稳的写法是：

- weak gain
  只是把样本送进
  同一个壳；
- 真正决定
  能不能继续掉进
  sink
  的第一主轴，
  仍然是：
  - `target transient mean`

### 3. `mean` 抬升以后，两条 margin 会继续一起往 sink 方向塌

和这层
`mean`
抬升同步出现的
margin 变化是：

- `v66 - v64`
  从 hinge 均值
  `+0.0276 dB`
  走到 sink
  `-0.0088 dB`
  额外下掉：
  - `0.0364 dB`
- `v66 - v65`
  从 hinge 均值
  `-0.0467 dB`
  走到 sink
  `-0.1140 dB`
  额外下掉：
  - `0.0673 dB`

所以当前更准确的主线应写成：

- weak-gain hinge
  已经先进入：
  - `v66 < v65`
    的壳
- 但只有当
  `mean`
  再明显抬升时，
  才会继续把：
  - `v66 > v64`
    一起拖到负侧，
  同时把：
  - `v66 > v65`
    再往下压深

### 4. `reference` 和 `cosine` 仍有作用，但更像辅助配套，不再是最终主语

这一步里，
sink 相对 hinges
还同时出现：

- `reference_duration_sec = -0.975`
- `target_duration_sec = -0.870`
- `target_interference_logspec_cosine = -0.1011`

也就是：

- sink
  更短
- 更低 cosine

这些信号仍然和
sink
同向，
但它们没有改写
前面那条主结论：

- 在 weak-gain 壳内，
  最终把 hinge
  推成 sink
  的第一主轴
  仍然是
  `mean`
  不是
  `gain`

### 5. `train_001589` 已经比 `train_000266` 更靠近 sink，但还没有跨过壳内最后一条线

看单条 row：

- `train_001589`
  的
  `mean = -14.3527`
  已经高于
  `train_000266 = -16.8729`

说明：

- `001589`
  确实比
  `000266`
  更靠近 sink

但它仍没到
`train_001543`
的：

- `mean = -10.9606`

同时，
`001589`
还带着：

- 更长 reference
  `3.36 sec`
- 更高 cosine
  `0.7149`

所以它现在更准确的身份应写成：

- weak-gain shell
  内部，
  已经出现
  partial mean rise
  的 hinge

## 结论

1. `weak gain` 在这一步已经只是外壳条件，不是把 hinge 推成 sink 的最后主导；因为 sink 相对 hinges 的 gain 只差 `+0.083 dB`，overlap 还更晚 `+0.09 sec`。
2. 在 weak-gain 壳内，真正把 `train_001543` 和 `train_000266 / train_001589` 拉开的第一主轴，仍然是 `target transient mean` 的整段抬升。
3. 这层 `mean` 抬升会继续把两条 margin 一起拖向 sink，其中 `v66-v65` 再深 `0.0673 dB`，`v66-v64` 也再下掉 `0.0364 dB`。
4. `train_001589` 已经是更靠近 sink 的 weak-gain hinge，但还只是 partial mean rise；当前最合理的下一步应只看 `train_001589 / train_001543`，解释为什么它已经抬起一截 `mean`，却还没跨过最后那条壳内边界。 
