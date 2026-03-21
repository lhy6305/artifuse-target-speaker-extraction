# 2026-03-21 `candidate_v7` fail-both pure `v67` takeover case diagnosis

## 背景

上一轮已经把
near-shell edge band `4`
拆成了：

- pure `v67` takeover edge `3`
  - `train_001079`
  - `train_001494`
  - `train_000697`
- `v67 + v65` takeover singleton `1`
  - `train_001589`

当前还差最后一个更细问题：

- `v67`
  到底是先在什么类型的 row 上
  抢走 `v66`；
- 以及为什么这一步
  还没有同时把
  `v65`
  一起带进来。

如果这一步切清，
active bridge
这条线就可以从：

- near-shell edge 搜索

进一步收紧成：

- pure `v67` takeover
  的首发 case composition 诊断

## 本轮做法

### 1. 只保留 pure `v67` takeover edge `3`

输入直接采用上一轮已经拆好的：

- `reports/eval/active_targetfull_clean_failboth_nearshell_case_diagnosis/summary.json`
- `reports/eval/active_targetfull_clean_failboth_edgeband_pure_v67_takeover_direction_analysis/summary.json`

当前只围绕：

- `train_001079`
- `train_001494`
- `train_000697`

做解释，
不再把：

- `train_001589`

和它们混写。

### 2. 同时对照三层参照组

本轮固定同时看：

- dual-leak shell `4`
- pure `v67` takeover edge `3`
- `v67 + v65` takeover singleton `1`
- outer compare band `4`

新增精简 summary：

- `reports/eval/active_targetfull_clean_failboth_pure_v67_takeover_case_diagnosis/summary.json`

这份 summary
只保留三类最关键事实：

- pure `3`
  相对 shell 的漂移
- pure `3`
  相对 outer compare 的位置
- singleton `1`
  相对 pure `3`
  的额外漂移

### 3. 用 per-case metadata
确认 pure `3`
是不是同一类首发 takeover

逐条补看：

- `target_duration_sec`
- `interference_gain_db`
- `interference_start_offset_sec`
- `target_interference_logspec_cosine`
- `v66` 相对 `v64 / v65 / v67`
  的 gap

## 结果

### 1. pure `v67` takeover edge `3` 不是“更强 interference 把 `v66` 打掉”的 case；它反而是一层更弱 gain、稍更早 overlap 的 takeover 过渡带

相对 dual-leak shell `4`，
pure `3`
的均值变化为：

- `target_duration_sec = +0.2425 sec`
- `reference_duration_sec = -0.1325 sec`
- `interference_gain_db = -3.5023 dB`
  即：
  - interference 更弱
- `interference_start_offset_sec = -0.0433 sec`
  即：
  - 更早混入
- `target_interference_logspec_cosine = -0.1010`

同时，
它在 transient 侧
并没有变成：

- 更高的 interference transient

相反，
pure `3`
相对 shell `4`
是：

- `interference_transient_presence_minus_mid_db_mean = -0.5595`
- `interference_transient_presence_share_mean = -0.0266`

也就是说，
pure `v67` takeover
先发生的那一步，
当前更接近：

- 更长一点的 target
- 更弱 gain
- 更早 overlap
- 更低 cosine

的过渡态，
而不是：

- 高 interference 压制

### 2. pure `3` 已经是稳定的 `v67` takeover 首发层，但还不是 `v65` 一起进场的外层

这 `3` 条当前共享的 direction
非常整齐：

- 全部保住：
  - `v66 > v64`
  - `v66 > v65`
- 全部失败：
  - `v66 > v67`
  - `v64 > v67`
  - `v20 > v24`

aggregate 排序为：

- `v67 > v66 > v64 > v24 > v65 > baseline > v20`

关键 gap 为：

- `v66 > v64 = +0.081117`
- `v66 > v65 = +0.142099`
- `v66 > v67 = -0.083212`

这说明：

- `v67`
  已经稳定接管 `v66`
- 但 `v65`
  还没有一起进来

所以这 `3` 条
当前更准确的身份应固定为：

- pure `v67` takeover
  first-stage edge

不是：

- `v67 / v65`
  双接管层

### 3. pure `3` 仍明显比 outer compare band 更像 shell，而不是已经完全漂到外层 random frontier

相对 outer compare band `4`，
pure `3`
当前仍表现为：

- `interference_gain_db = -2.7298 dB`
  更弱
- `interference_start_offset_sec = -0.1285 sec`
  更早
- `interference_transient_presence_minus_mid_db_mean = -6.1971`
  显著更低
- `interference_transient_presence_share_mean = -0.1028`
  显著更低

而在 direction 上，
pure `3`
也仍保留更强的：

- `v66 > v64 = +0.054262`
- `v66 > v65 = +0.016049`

优势差。

大白话讲，
它们不是：

- 已经完全掉进更外层 mixed frontier

而是：

- 还挂在 shell 外侧、
  但已经被 `v67`
  先抢走的一层过渡带

### 4. `train_001589` 必须继续单列；它不是 pure `v67` takeover 的同类样本

如果把 singleton
`train_001589`
拿来和 pure `3`
对照，
最关键的新事实是：

- `target_duration_sec = +0.86 sec`
- `reference_duration_sec = +0.83 sec`
- `interference_gain_db = -1.3827 dB`
  进一步更弱
- `interference_transient_presence_minus_mid_db_mean = +6.0701`
- `interference_transient_presence_share_mean = +0.0884`
- `target_interference_logspec_cosine = +0.0775`

而 direction 上，
最关键的翻转是：

- `v66 > v65`
  从 pure `3` 的
  `+0.142099`
  掉到：
  - `-0.053612`

这说明：

- `train_001589`
  不是 pure `v67` takeover
  再普通加一条的成员；
- 它是 edge band
  继续向外漂时，
  第一个连 `v65`
  也一起拉进来的异常点。

所以：

- edge `4`
  的整体均值
  不能直接拿来解释
  pure `v67` takeover
  的首发机制

### 5. pure `3` 内部虽然有长短差异，但首发 takeover 语义仍然一致

#### `train_001079`

- `target_duration_sec = 1.02`
- `interference_gain_db = -2.78`
- `start_offset_sec = 0.006`
- `cosine = 0.677314`
- `v66 > v64 = +0.069593`
- `v66 > v65 = +0.192631`
- `v66 > v67 = -0.085964`

它是：

- 最早混入的 short-target
  low-gain takeover case

#### `train_001494`

- `target_duration_sec = 1.02`
- `interference_gain_db = -4.393`
- `start_offset_sec = 0.068`
- `cosine = 0.673604`
- `v66 > v64 = +0.146255`
- `v66 > v65 = +0.140989`
- `v66 > v67 = -0.146031`

它是：

- 对 `v64`
  保留最强、
  但被 `v67`
  超车也最稳的 case

#### `train_000697`

- `target_duration_sec = 2.22`
- `interference_gain_db = -4.993`
- `start_offset_sec = 0.205`
- `cosine = 0.561251`
- `v66 > v64 = +0.027504`
- `v66 > v65 = +0.092676`
- `v66 > v67 = -0.017641`

它是：

- pure `3`
  里最长、
  cosine 最低、
  但 `v67`
  超车最窄的一条；
- 更像 shell
  走向 outer frontier
  前的末端过渡 case

## 当前结论

1. pure `v67` takeover edge `3`
   当前应正式记成：
   - `v67`
     对 shell 外层过渡带的首发 takeover
2. 这一步 takeover
   不是：
   - 更强 interference
     压制
   而更接近：
   - 更弱 gain
   - 更早 overlap
   - 更长一点的 target
   - 更低 cosine
     共同出现时，
     `v67`
     先抢走 `v66`
3. `train_001589`
   不能继续和 pure `3`
   并写；
   它是：
   - `v67 + v65`
     双接管开始出现的 singleton
4. 因而 active bridge
   当前更准确的层级应进一步收紧为：
   - dual-leak shell
     = train-only inner core
   - pure `v67` takeover edge `3`
     = 第一层 `v67`
       接管过渡带
   - `train_001589`
     = edge-to-outer drift singleton
   - remaining `v67-top`
     = 更外层 mixed frontier

## 当前默认下一步

默认顺序继续收紧为：

1. 不再把 edge `4`
   的混合均值
   直接当成 pure takeover
   的解释。
2. 若还继续推进，
   默认只围绕：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   做更细 case diagnosis，
   解释：
   - 为什么 low-gain early-overlap
     + lower cosine
     会先触发 pure `v67` takeover
3. `train_001589`
   只保留为：
   - `v67 + v65`
     takeover singleton
4. `val_000182`
   继续只保留为：
   - metadata-only outlier
5. 仍不启动新训练。
