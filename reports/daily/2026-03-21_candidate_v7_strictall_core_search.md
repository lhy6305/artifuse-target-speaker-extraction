# 2026-03-21 `candidate_v7` strict-all core search

## 背景

上一轮已经把
`candidate_v6_v4carve_only_expand`
固定成：

- 当前新的
  pure-negative working family；
- 但它只是
  aggregate 上更干净，
  还不是
  row-level fully clean family。

当时已知的 row-level 现象是：

- `val_000430`
  是最强核心；
- `val_000331`
  只部分支持；
- `val_000165`
  更像旧 family
  留下的 noisy carry-over。

但工程上还有一个更隐蔽的问题没关掉：

- `scripts/eval/search_synthetic_proxy_candidates.py`
  里的
  `--require-samplewise-order-pass`
  只会检查
  `ordered_aliases`
  本身；
- 它不会把
  `--extra-order-constraint`
  也一并收紧到
  samplewise 层。

这意味着：

- 之前说的
  “strict / samplewise”
  搜索，
  其实仍可能混入：
  - 主顺序过了，
  - 但额外 guard
    例如
    `v66 > v65`
    或
    `v66 > v67`
    并没有逐条样本成立
    的 rows。

## 本轮工程补强

已补脚本：

- `scripts/eval/search_synthetic_proxy_candidates.py`

新增参数：

- `--require-samplewise-all-constraints-pass`

新语义为：

- 每条样本必须同时满足：
  - 主 `ordered_aliases`
  - 所有 `extra_order_constraints`
- 之后才允许进入搜索候选池。

同时新增输出统计：

- `num_samplewise_extra_constraint_pass_rows_before_optional_filter`
- `num_samplewise_all_constraints_pass_rows_before_optional_filter`
- `require_samplewise_all_constraints_pass`

## 本轮严格搜索

沿用
`candidate_v6`
那条 pure-negative expand
搜索口径：

- ordered aliases：
  - `v66 > v64`
- extra constraints：
  - `v66 > v65`
  - `v66 > v67`
  - `v64 > v67`
  - `v20 > v24`

输出：

- `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min3_on_friend_speech_leak_search_v1/summary.json`
- `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min2_on_friend_speech_leak_search_v1/summary.json`

### 1. `min-count = 3`

结果：

- shared speech rows
  真正 samplewise
  全约束过关的只有：
  - `2` 条
- 因而：
  - `top_order_pass_count = 0`
  - `num_candidates = 0`

也就是：

- 当前并不存在
  `3+ row`
  的 strict-all clean family。

### 2. `min-count = 2`

结果：

- top strict-all family
  固定收敛到：
  - `val_000239`
  - `val_000430`

aggregate：

- `v66 - v64 = +0.010527 dB`
- `v66 - v65 = +0.256205 dB`
- `v66 - v67 = +0.110576 dB`
- `v64 - v67 = +0.100049 dB`
- `v20 - v24 = +0.060376 dB`

其整体排序为：

- `v66 > v64 > v67 > v30 > v32 > v29 > v25 > v20 > v35 > v24 > baseline > v65`

## 与 `candidate_v6` 的关系

当前最重要的新事实是：

- strict-all core
  不是
  `candidate_v6`
  的简单收紧版。

`candidate_v6`
val `3` 条为：

- `val_000165`
- `val_000331`
- `val_000430`

但 strict-all core
变成：

- `val_000239`
- `val_000430`

也就是：

1. `val_000430`
   被再次确认是
   真核心；
2. `val_000165`
   与
   `val_000331`
   都被 strict-all
   直接筛掉；
3. 同时浮出一条此前没被
   `candidate_v6`
   收进去的新核心：
   - `val_000239`

## row-level 解释

### `val_000430`

继续是最硬核心：

- `v66 - v64 = +0.019306 dB`
- `v66 - v65 = +0.464066 dB`
- `v66 - v67 = +0.133390 dB`
- `v20 - v24 = +0.097162 dB`

### `val_000239`

这条新 core row
不是靠
`v67`
塌得特别厉害才入选，
而是：

- `v66 - v64 = +0.001747 dB`
- `v66 - v65 = +0.048344 dB`
- `v66 - v67 = +0.087762 dB`
- `v20 - v24 = +0.023589 dB`

它属于：

- gap 不大，
  但四条 guard
  都逐条成立
  的稳定 row。

## 当前结论

1. `candidate_v6`
   应继续保留为：
   - aggregate pure-negative working family
   而不是：
   - row-level strict core
2. 当前 row-level
   真正能站住的 strict-all core
   只有：
   - `val_000239`
   - `val_000430`
3. 当前并不存在
   `3+ row`
   的 strict-all clean family，
   因而默认不应把
   `candidate_v6`
   误写成
   “已经严格收敛完成”。
4. 这条新 `{239,430}`
   更适合记为：
   - strict-core 诊断锚点
   而不是立即升格成
   新训练入口

## 当前默认下一步

默认顺序更新为：

1. 若继续停在 proxy 侧，
   先固定区分两层：
   - `candidate_v6`
     = aggregate working family
   - `{val_000239, val_000430}`
     = strict-all core
2. 同时继续保留：
   - `val_000469`
     作为单独硬 anchor
3. 在没有新的
   `3+ row`
   strict-all family
   之前，
   默认仍不启动新训练。
