# 2026-03-23 `candidate_v7` `v65` sink mean gate-partner split

## 背景

上一轮已经把
`v65 sink`
的 gate 内解释
收紧成：

1. `target transient mean`
   已经正式强于
   `share`
2. 但
   `mean`
   本身还不是
   一个独立硬 gate

所以当前还差
最后一个更细的问题：

- 在当前窄 ring
  里，
  如果只保留
  `mean`
  再配一个旧 gate 因子，
  更像：
  - `mean + reference`
  还是：
  - `mean + gain`
  才能把
  `v65 sink`
  切得最干净

## 本轮做法

这一步不加新脚本，
直接复用：

- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`

共跑两次四象限：

1. `mean + reference`
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_reference_quadrants/summary.json`
2. `mean + gain`
   输出：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_gain_quadrants/summary.json`

两次都固定：

- `target_group = v65_sink`
- `baseline_group = reference_gain_both_nonsink`
- `contrast_group = reference_gain_both_hinge`

也就是只在
当前已经确认的
`reference+gain both`
局部语境下，
继续追问：

- `mean`
  到底更需要谁
  作为本地搭档

## 结果

### 1. `mean + reference` 还不够干净，`both` 桶里仍然混着 5 条 pre

`mean + reference`
四象限里：

- `target`
  `train_001543`
  落在：
  - `both`
- `contrast hinge`
  `train_000266`
  落在：
  - `neither`

但最关键的是：

- `both`
  桶共有
  `6`
  条：
  - `1` 条 sink
  - `5` 条 pre

具体混入的
pre rows
是：

- `train_000634`
- `train_001006`
- `train_000117`
- `train_000578`
- `train_000904`

这说明：

- `reference`
  即便和
  `mean`
  绑在一起，
  仍然更像：
  - 上游 entry
    的背景约束
- 它并没有把
  当前窄 ring
  的 sink
  局部 carve
  收紧干净

### 2. `mean + gain` 的 `both` 桶现在只剩 sink 本人

`mean + gain`
四象限里：

- `target`
  `train_001543`
  落在：
  - `both`
- `contrast hinge`
  `train_000266`
  落在：
  - `factor_b_only`

而更关键的是：

- `both`
  桶只有
  `1`
  条：
  - `train_001543`

也就是：

- 在当前窄 ring
  里，
  `mean + weak gain`
  已经形成了
  一个干净的
  sink-only carve

但这并不表示：

- `gain`
  单独就够

因为：

- `factor_b_only`
  里仍然还有：
  - `train_000266`
  - `train_001589`
  这两条
  hinge

所以当前更准确的写法是：

- `weak gain`
  仍然只是
  局部必要条件
- 真正把它收成
  sink-only
  的，
  是：
  - `mean`
    再补上去

### 3. 因此 `reference` 不该再被写成 `mean` 的同级本地搭档，`gain` 才是更紧的局部伴随项

综合这两份 quadrants：

- `mean + reference`
  仍漏
  `5`
  条 pre
- `mean + gain`
  的
  `both`
  桶已经只剩
  `train_001543`

所以当前主线应再收紧成：

1. `reference + gain`
   仍然保留为：
   - 上游的
     conjunction entry gate
2. 但进入当前窄 ring
   的局部 carve
   以后，
   真正和
   `target transient mean`
   更紧耦合的，
   已经不是：
   - `reference`
   而是：
   - `gain`
3. `reference`
   应退回：
   - 上游 entry
     描述
   不再写成：
   - 和 `gain`
     对
     `mean`
     同等有效的
     本地 partner

## 结论

1. `target transient mean + weak gain` 是当前窄 ring 里最干净的 `v65 sink` 两因子 carve，`both` 桶只剩 `train_001543`。
2. `target transient mean + short reference` 还会混入 `5` 条 pre，因此 `reference` 不再适合被写成 `mean` 的同级本地搭档。
3. 当前更稳的层级应更新成：`reference+gain` 负责上游 entry，`mean+gain` 负责当前局部 sink carve。
4. 如果继续推进，默认下一步应只看 `train_000266 / train_001589 / train_001543`，解释为什么它们都已经落到 `weak gain` 一侧，但只有 `train_001543` 还能再被 `mean` 推成 sink。 
