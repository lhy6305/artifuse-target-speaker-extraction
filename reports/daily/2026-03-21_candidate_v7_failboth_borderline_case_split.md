# 2026-03-21 `candidate_v7` fail-both persistent borderline case split

## 背景

上一轮已经确认：

- dual-leak shell
  `v66-top 4`
  与
  `v67-top 34`
  的分界
  不是单字段阈值；
- 当前最强解释是：
  - multi-factor co-driven split

但当时还留了一个细问题：

- 那 `5` 条
  persistent borderline rows
  到底是不是同一种
  “近内核边界带”；
- 还是其中已经混入了
  另一类只是
  metadata 近似、
  但方向上并不真的贴着
  dual-leak shell
  的假边界样本。

## 本轮做法

### 1. 用 dual-leak shell 作为 seed，重新对 `fail_both` 全量外层做 joint-distance 排序

输入：

- seed：
  - `train_000597`
  - `train_000865`
  - `train_001477`
  - `train_001599`
- search workspace：
  - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_all.jsonl`

输出：

- `reports/eval/active_targetfull_clean_failboth_topv67_vs_dualleak_seed_expansion/summary.json`

这里同时看两类距离：

- metadata distance
- constraint distance

再合成：

- joint distance

### 2. 把 persistent borderline rows 单独做 case-level summary

当前 persistent borderline rows
沿用上一轮名单：

- `train_001079`
- `train_001494`
- `train_000697`
- `train_001589`
- `val_000182`

新增输出：

- `reports/eval/active_targetfull_clean_failboth_persistent_borderline_case_analysis/summary.json`

这个 summary
会把三层拆开：

- dual-leak shell seed
- persistent borderline band
- remaining `v67-top` outer band

并逐条记录：

- joint / metadata / constraint distance rank
- 当前 failed constraints
- 当前 metadata fields
- 当前 `v66` 相对 `v64 / v65 / v67 / v24 / v20`
  的 gap

### 3. 把真正贴着 shell 的 train-side borderline rows 物化成独立资产

新资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_persistent_borderline_nearshell_all.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_persistent_borderline_nearshell.jsonl`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_persistent_borderline_nearshell_all.jsonl`

对应 focused direction：

- `reports/eval/active_targetfull_clean_failboth_persistent_borderline_nearshell_direction_analysis/summary.json`

## 结果

### 1. 当前 `5` 条 persistent borderline rows 并不是同一种样本；它们已经裂成两类

#### A. 真正贴着 dual-leak shell 的 train near-shell edge band

- `train_001494`
- `train_001079`
- `train_001589`
- `train_000697`

这 `4` 条在
joint-distance 排名里分别是：

- `#1`
- `#2`
- `#3`
- `#9`

均值为：

- `mean_joint_distance_z = 1.420838`
- `mean_metadata_distance_z = 1.392966`
- `mean_constraint_distance_z = 0.255023`

这说明它们不是
“只是在 metadata 上像 shell”，
而是连 constraint signature
也确实贴着 shell。

#### B. 单独的 val metadata-only outlier

- `val_000182`

它虽然会在
`4 / 5`
个单字段 full-recall 阈值下
被误收，
但在 joint-distance 排名里
已经直接掉到：

- `#39 / 39`

而且：

- `metadata_distance_z = 2.616320`
- `constraint_distance_z = 14.799924`
- `joint_distance_z = 15.029400`

也就是说：

- `val_000182`
  只是 metadata 外观上
  仍有一些 shell-like 成分；
- 但在方向约束上
  根本不是
  “贴着 dual-leak shell 的边界带”。

所以：

- 上一轮那 `5` 条
  persistent borderline rows
  当前不能再被当成
  一个同质组。

### 2. 真正的 near-shell edge band 仍然已经是 `v67-top`，只是输得比较窄

对这 `4` 条 train near-shell rows
补跑 focused direction 后，
aggregate 排序为：

- `v67 > v66 > v64 > v65 > v24 > baseline > v20`

关键 gap：

- `v66 > v64 = +0.070637`
- `v66 > v65 = +0.093171`
- `v66 > v67 = -0.095303`
- `v64 > v67 = -0.165941`
- `v20 > v24 = -0.092016`

这说明：

- 它们还保住了
  `v66 > v64`
  和大部分情况下的
  `v66 > v65`；
- 但已经稳定输给
  `v67`，
  所以本质上仍是：
  - outer edge band
  不是：
  - dual-leak shell

### 3. 这 `4` 条 near-shell edge band 的 metadata 确实介于 shell 与外层 `v67-top` 之间

`4` 条 train near-shell rows
的均值为：

- `target_transient_presence_minus_mid_db_mean = -13.782271`
- `target_transient_presence_share_mean = 0.017250`
- `interference_transient_presence_minus_mid_db_mean = 1.145241`
- `interference_transient_presence_share_mean = 0.310912`
- `target_interference_logspec_cosine = 0.656756`

对比 dual-leak shell：

- target transient / share
  仍然接近
- interference transient / share
  略高
- cosine
  明显更低

对比 remaining `v67-top` outer band：

- target transient / share
  明显更低
- interference transient / share
  明显更低
- cosine
  更高

因此这 `4` 条
确实可以写成：

- train-side near-shell edge band

但不能写成：

- 即将并入 dual-leak shell
  的新成员

因为它们已经明确跨过了
最关键的那条边界：

- `v67`
  已经接管
  `v66`

### 4. `val_000182` 的意义需要单独处理

`val_000182`
当前最关键的事实是：

- metadata 上看起来
  像：
  - 低 target transient
  - 低 target share
  - 中低 interference share
- 但 direction 上却是：
  - `v66 > v64 = +4.649479`
  - `v66 > v65 = -4.615799`
  - `v66 > v67 = -6.442936`
  - `v20 > v24 = -14.495071`

这说明它不属于
“train near-shell edge band”，
而属于另一类：

- metadata-only shell lookalike

它的主要价值是提醒：

- 单靠 metadata 近似
  仍然会把完全不同的
  direction behavior
  混进来；
- 所以当前这条线若继续做个例诊断，
  必须把：
  - `val_000182`
  和：
  - `train_001079 / 001494 / 000697 / 001589`
  分开处理。

## 当前结论

1. 上一轮那 `5` 条 persistent borderline rows 当前不能再被看作一个同质的“边界带”。
2. 真正贴着 dual-leak shell 的只有 `4` 条 train rows：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   - `train_001589`
3. 这 `4` 条当前最准确的身份是：
   - train-side near-shell edge band
   不是：
   - dual-leak shell 扩张成员
4. `val_000182` 不能再和这 `4` 条并写；
   它应单独记成：
   - metadata-only borderline outlier
5. 因而 active bridge
   这条线的主解释现在应进一步收紧为：
   - `core trio`
     = 唯一可保留 active core
   - dual-leak shell
     = train-only inner core
   - near-shell edge band `4`
     = 最靠近 shell 的外层 train 边界带
   - `val_000182`
     = metadata-only false shell
   - remaining `v67-top`
     = 更外层 mixed frontier

## 当前默认下一步

默认顺序继续收紧为：

1. 不再把 `5` 条 persistent borderline rows 当成一个整体追。
2. 若还继续推进，默认只围绕这 `4` 条 train near-shell edge band 做更细个例诊断：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   - `train_001589`
3. `val_000182` 只保留为 metadata-only outlier，不再当作 shell 外环候选。
4. 仍不启动新训练。
