# 2026-03-23 `candidate_v7` post-entry `v64` collapse neighbor scan

## 背景

上一轮已经把
`train_001610`
和
`train_001745`
压成 post-entry depth split，
并确认：

- `train_001745`
  比
  `train_001610`
  更深，
  不是因为
  `v65`
  takeover
  继续加深；
- 而是因为：
  - `v64`
    剩余 buffer
    被继续单边打穿

因此当前最窄的问题
变成：

- 这条
  `both-crossed + v64-deeper`
  几何
  在
  `train_001745`
  周围的窄 ring
  里，
  到底有没有第二条
  同型 row

也就是：

- 之前从
  `001610 -> 001745`
  看到的那组：
  - 更早 overlap
  - 更长 reference
  - 更高双侧 transient
  - 更弱 gain
  是否已经足以在
  train-side
  近邻里
  再复现一条
  mirror case

## 本轮做法

这一步不再扩大搜索空间，
只在当前最窄的
train-side `topv67`
ring 内继续做：

1. 先复用：
   - `scripts/eval/analyze_proxy_case_neighbors.py`
   把：
   - `train_001745`
   对
   `27`
   条 train-side `topv67`
   row
   的全量 metadata 近邻
   都展开出来，
   输出：
   - `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`
2. 再新增：
   - `scripts/eval/analyze_proxy_neighbor_signature_scan.py`
   把这些近邻按：
   - `v66 - v64`
   - `v66 - v65`
   的组合形态
   分桶，
   输出：
   - `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_signature_scan/summary.json`

这里的 bucket
定义固定为：

- `pre_entry_or_pure`
  = `v66 > v64` 且 `v66 > v65`
- `hinge_secondary_crossed_first`
  = `v66 > v64` 但 `v66 < v65`
- `post_entry_both_crossed_reference_deeper`
  = `v66 < v64` 且 `v66 < v65`，并且 `v64` 这一侧更深
- `post_entry_both_crossed_secondary_deeper_or_equal`
  = `v66 < v64` 且 `v66 < v65`，但更深的是 `v65`
- `reference_only_crossed_unexpected`
  = `v66 < v64` 但 `v66 > v65`

当前
`train_001745`
要找的真正同型，
只定义为：

- `post_entry_both_crossed_reference_deeper`

## 结果

### 1. 当前窄 ring 里没有第二条真正复制 `train_001745` 的同型 row

扫完
`27`
条 train-side `topv67`
近邻后，
bucket
计数为：

- `pre_entry_or_pure = 20`
- `hinge_secondary_crossed_first = 4`
- `post_entry_both_crossed_secondary_deeper_or_equal = 1`
- `reference_only_crossed_unexpected = 2`
- `post_entry_both_crossed_reference_deeper = 0`

也就是说：

- 当前窄 ring
  里没有任何一条
  row
  同时满足：
  - `v66 < v64`
  - `v66 < v65`
  - 且
    `v66 - v64`
    比
    `v66 - v65`
    更深

因此：

- `train_001745`
  的
  `both-crossed + v64-deeper`
  几何
  目前仍是
  narrow-ring
  内的
  singleton pocket

### 2. 最近的 post-entry 邻居确实存在，但它落在另一种 drift 几何：`v65` 更深，而不是 `v64` 更深

离
`train_001745`
最近的
post-entry row
是：

- `train_001543`
  - `metadata_distance_z = 2.964676`
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`
  - ranking：
    - `v67 > v65 > v64 > v66`

所以它虽然也已经进入：

- `v66 < v64`
- `v66 < v65`

但更深的
不是：

- `v64`

而是：

- `v65`

这说明：

- `train_001543`
  是
  `both-crossed + v65-deeper`
  的 post-entry 变体；
- 它不能作为：
  - `train_001745`
    那种
    `v64`
    single-sided deeper collapse
  的 mirror

### 3. 另外两条出现 `v66 < v64` 的 row 也不是同型，它们还停在 `v64-only crossed` 的异型分支

当前还出现了两条：

- `train_000664`
  - `metadata_distance_z = 3.388037`
  - `v66 - v64 = -0.009173 dB`
  - `v66 - v65 = +0.004478 dB`
  - ranking：
    - `v67 > v64 > v66 > v65`
- `train_000210`
  - `metadata_distance_z = 4.753802`
  - `v66 - v64 = -0.008782 dB`
  - `v66 - v65 = +0.003251 dB`
  - ranking：
    - `v67 > v64 > v66 > v65`

它们的问题是：

- 虽然已经出现：
  - `v66 < v64`
- 但还没有出现：
  - `v66 < v65`

所以它们属于：

- `reference_only_crossed_unexpected`

这和
`train_001745`
已经进入的：

- `both-crossed + v64-deeper`

不是同一条支路。

### 4. 当前最稳的结论已经可以固定成：在这层窄 ring 里，metadata 最近不等于 margin 几何同型

从这次扫描看，
最接近
`train_001745`
metadata package
的近邻
大多仍是：

- `pre_entry_or_pure`
  或
- `hinge_secondary_crossed_first`

真正进入：

- `v66 < v64`

的 row
已经很少；
而真正同时满足：

- `v66 < v64`
- `v66 < v65`
- 且
  `v64`
  这一侧更深

的 row
则是：

- `0`

所以当前应该明确写成：

- `train_001745`
  的更深 `v64`
  collapse
  在这层 ring
  内更像
  rare conditional singleton；
- 不能因为
  metadata
  最相近，
  就把相邻 row
  直接视作同型 margin family

## 结论

1. 在当前最窄的 train-side `topv67` ring 内，`train_001745` 没有找到第二条 `both-crossed + v64-deeper` 同型 row。
2. 最近的 post-entry 邻居 `train_001543` 走向的是 `v65` 更深的另一支；`train_000664 / train_000210` 则是 `v64-only crossed` 的异型支路。
3. 当前最合理的下一步，不该再继续外扩 ring，而应固定成只解释：
   - 为什么 `train_001745`
     最像它的假近邻
     会分流到
     `v65` deeper
     或
     `v64-only crossed`
   - 而只有它自己
     落在
     `both-crossed + v64-deeper`
     的 singleton pocket
