# 2026-03-23 `candidate_v7` neighbor-ring buffer collapse diagnosis

## 背景

上一轮已经把 mixed ring
继续拆成：

- pure-signature `v67-top 5`
- `v65` drift `v67-top 4`

并确认两组真正的分界
不是：

- transient
  是否第一次升高

而是：

- `v66 > v64`
  保护带是否还保有正 margin

但还差最后一个更细问题：

- 在这 `9` 条 ring 样本内部，
  `v66 > v64`
  的 margin
  到底有没有被某个单独 metadata 字段
  明确控制；
- 还是说它已经主要表现为：
  - 模型 margin 本身先塌
  - raw metadata
    只剩弱共变

## 本轮做法

新 summary：

- `reports/eval/active_targetfull_clean_failboth_neighbor_ring_buffer_collapse/summary.json`

当前直接围绕 ring `9`
条样本：

- `train_000216`
- `train_000759`
- `train_000799`
- `train_001006`
- `train_001639`
- `train_000266`
- `train_001589`
- `train_001610`
- `train_001745`

记录：

1. 按 `v66 > v64`
   从低到高排序；
2. 计算
   `v66 > v64`
   与各字段的相关方向；
3. 以中位数
   `0.044802`
   把 ring
   切成：
   - low-buffer `5`
   - high-buffer `4`
   再看均值差

## 结果

### 1. ring 内部最稳定跟着 `v66 > v64` 一起动的，仍然是 `v66 > v65`；raw metadata 没有出现单字段强控制

当前相关方向里，
最明显的一条是：

- `corr(v66>v64, v66>v65) = +0.5021`

其余字段都明显更弱：

- `target_duration_sec = +0.0028`
- `reference_duration_sec = -0.2362`
- `interference_gain_db = -0.2443`
- `start_offset_sec = +0.1786`
- `cosine = +0.0873`
- `interference_transient_mean = -0.1387`
- `interference_transient_share = -0.1377`

这说明：

- 一旦进入 mixed ring，
  raw metadata
  已经没有哪一个字段
  能单独稳定解释
  `v66 > v64`
  为什么塌；
- 当前更可靠的可跟踪边界
  仍然是：
  - `v66 > v64`
  和
  - `v66 > v65`
    这两条 margin
    自己的联动

### 2. 按中位数切出的 low-buffer `5` 已经几乎贴到 `v66 > v65 = 0`，而 `v66 > v67` 并没有再明显更差

low-buffer `5`：

- `train_001745`
- `train_001610`
- `train_000266`
- `train_001589`
- `train_001006`

它们均值为：

- `v66 > v65 = -0.007487`
- `v66 > v67 = -0.157295`

high-buffer `4`：

- `train_001639`
- `train_000759`
- `train_000799`
- `train_000216`

它们均值为：

- `v66 > v65 = +0.178667`
- `v66 > v67 = -0.154065`

也就是说：

- 两边对 `v67`
  的失败幅度
  其实差不多；
- 真正被拉开的
  是：
  - `v66 > v65`
    这条 buffer
    从明显为正
    掉到接近 `0`

### 3. low-buffer `5` 里已经混入 `train_001006`，说明 pure-signature 组内部也存在“快塌边缘”

当前按 `v66 > v64`
  排序后，
  最低 `5` 条里除了 `v65` drift `4`
  之外，
  还包含：

- `train_001006`

它当前是：

- pure-signature `v67-top`
- 但：
  - `v66 > v64 = +0.044802`
  - 已经贴着 ring 内中位数

这说明：

- pure-signature
  并不是完全稳定的厚层；
- 其中至少
  `train_001006`
  已经站在
  向 `v65` drift
  过渡的最内侧边缘

### 4. low-buffer 与 high-buffer 的 metadata 差异存在，但都偏弱，不足以单独做 hard carve

`low - high`
均值差为：

- `target_duration_sec = +0.24 sec`
- `reference_duration_sec = +0.0675 sec`
- `interference_gain_db = +0.1824 dB`
- `start_offset_sec = -0.01805 sec`
- `cosine = +0.01798`
- `interference_transient_mean = +0.3310`
- `interference_transient_share = -0.0441`

这些差异都不够硬。

所以当前更合理的写法应是：

- low-buffer band
  在 metadata 上
  只有弱偏移；
- 当前不能指望
  用单字段阈值
  再把它 clean carve 出来；
- 更值得继续追的是：
  - 哪些组合因素
    会把
    `v66 > v64`
    margin
    继续往 `0`
    压

## 当前结论

1. 对当前 mixed ring，
   `v66 > v64`
   buffer collapse
   主要还是模型 margin 现象；
   raw metadata
   只有弱共变，
   没有出现单字段强控制。
2. 当前最稳定的联动关系是：
   - `v66 > v64`
     一旦往 `0`
     掉，
   - `v66 > v65`
     也会很快一起掉到
     接近 `0`
     或翻负。
3. `v66 > v67`
   在 low / high buffer
   两边差异不大，
   所以它不是当前 ring 内
   最关键的下一条分界。
4. `train_001006`
   当前应记成：
   - pure-signature 组内
     的 low-buffer edge

## 当前默认下一步

默认顺序继续收紧为：

1. 不再继续找：
   - 单字段阈值
   去 carve
   low-buffer ring。
2. 若还继续推进，
   默认优先围绕：
   - `train_001006`
   - `train_001589`
   - `train_001610`
   - `train_001745`
   做个例对照，
   解释：
   - 为什么有的 row
     还挂在 pure-signature
   - 有的已经掉进
     `v65` drift
3. 下一步默认关注点
   应固定为：
   - `v66 > v64`
   - `v66 > v65`
     两条 buffer
     的联动塌缩
   而不是继续放大：
   - `v66 > v67`
4. 仍不启动新训练。
