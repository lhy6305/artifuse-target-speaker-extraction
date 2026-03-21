# 2026-03-21 `candidate_v7` bridgepair `seed+1` signature split

## 背景

上一轮已经确认：

- row-level bridge 目前是：
  - `val_000376`
  - `val_000430`
- 最近的第三条 row 是：
  - `val_000331`
- 但它只能算：
  - aggregate-only bridge extension

不过，
`seed + 1`
分析的原始输出里，
还存在另一个容易误导的点：

- 很多 candidate
  自己 row-level
  并不干净；
- 但只要和
  `{376,430}`
  这个强 seed pair
  平均一下，
  aggregate 就能重新 full-pass。

如果只按：

- `aggregate_min_constraint_gap_db`
- 或
- top aggregate candidate

去看，
很容易把：

- 跨前沿 row
- 远距离 washout row
- 真正 bridge 邻域

重新写混。

## 本轮新增

### 1. 脚本补强

已增强：

- `scripts/eval/analyze_proxy_seed_expansion.py`

新增输出：

- `top_nearest_aggregate_pass_expansions_by_joint_distance`
- `aggregate_pass_signature_summaries`

也就是在原先：

- 最近 non-seed rows
- top `seed+1` aggregate expansions

之外，
再补一层：

- aggregate-pass candidate
  按 candidate 自身
  failed-signature 分组后的摘要。

### 2. 更新后的分析输出

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`

seed 保持不变：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_val.txt`

也就是：

- `val_000376`
- `val_000430`

## 结果

### 1. `seed+1` aggregate-pass candidate 本身不是一条线，而是多条 failed-signature 前沿一起被 seed 洗白

当前 aggregate-pass signature summary
里，至少有以下几类仍然同时存在：

- bridge-like 三失败签名：
  - `v66>v65 | v66>v67 | v64>v67`
  - count：
    - `6`
  - nearest：
    - `val_000331`
    - joint distance：
      - `0.975332`
  - strongest aggregate：
    - `val_000235`
    - joint distance：
      - `6.092051`
- `guardv20_only` 跨前沿：
  - `v20>v24`
  - count：
    - `2`
  - nearest：
    - `val_000316`
    - joint distance：
      - `2.471158`
  - strongest aggregate：
    - `val_000223`
- `guardv65_only` 另一支：
  - `v66>v65`
  - count：
    - `1`
  - nearest / strongest：
    - `val_000202`
    - joint distance：
      - `3.448653`
- strict-core 自身：
  - `all-pass`
  - count：
    - `1`
  - candidate：
    - `val_000239`
    - joint distance：
      - `3.958411`

也就是说：

- bridge pair
  不只会把
  “bridge-like 第三条”
  洗到 aggregate pass；
- 它还会把：
  - strict core 另一侧
  - `guardv20_only`
  - `guardv65_only` 的另一支
  一起洗成 aggregate pass。

因此：

- 以后不能把
  `seed+1 aggregate pass`
  直接解释成：
  - 下一条 bridge 扩张候选。

### 2. 在 bridge-like 同签名内部，`aggregate 最强` 与 `距离最近` 已经明显分离；这说明 aggregate 排名会偏向 washout row

bridge-like 三失败签名：

- `v66>v65 | v66>v67 | v64>v67`

当前最关键的对比是：

- 最近 candidate：
  - `val_000331`
  - joint distance：
    - `0.975332`
  - aggregate min gap：
    - `+0.008756 dB`
- strongest aggregate candidate：
  - `val_000235`
  - joint distance：
    - `6.092051`
  - aggregate min gap：
    - `+0.018723 dB`

这说明：

- 如果只按
  aggregate gap
  排序，
  当前会把：
  - `val_000235`
  这种明显更远的 row
  排到更前；
- 但从 bridge 邻域角度，
  它并不比
  `val_000331`
  更像“下一条第三成员”。

更直白地说：

- `aggregate 更强`
  在这里不等于：
  - bridge 语义更近；
- 它很多时候只是：
  - 更容易被强 seed pair
    在均值上洗白。

### 3. top aggregate candidate `val_000223` 本质上不是 bridge 第三条，而是 `guardv20_only` 被跨前沿救活

当前 `top_seed_plus_one_expansions`
按 aggregate 排序时，
第一名是：

- `val_000223`

但它自己的 failed-signature 是：

- `v20>v24`

也就是它属于：

- `guardv20_only`

这条第二优先前沿，
不是 bridge-like 三失败签名。

因此：

- `223`
  之所以 aggregate 排名最高，
  不能被解释成：
  - 它是 bridge pair
    的最佳第三条；
- 更准确的解释是：
  - bridge pair
    强到足以把另一条前沿的 row
    也在 aggregate 上一起救活。

### 4. 当前应把 `seed+1` 候选分成三层，而不是继续看一个总榜

本轮之后，
更准确的分层应改成：

- row-level bridge：
  - `{376,430}`
- same-signature nearest bridge extension：
  - 先看
    `v66>v65 | v66>v67 | v64>v67`
    这条签名里
    距离最近的：
    - `val_000331`
- aggregate washout candidates：
  - 例如：
    - `val_000235`
    - `val_000223`
    - `val_000202`
    - `val_000239`
  - 它们都可能在
    `seed+1`
    上被洗成 aggregate pass，
    但不该直接当成
    bridge 的下一条第三成员

## 当前结论

1. `seed+1 aggregate pass`
   不能再当作单一候选榜；
   它本质上是多条前沿一起被强 seed 洗白后的混合结果。
2. 若继续围绕 bridge pair
   做第三条扩张，
   默认不能按：
   - aggregate min gap
   直接选；
   必须至少同时看：
   - candidate 自身 failed-signature
   - candidate 到 seed center 的 distance
3. 在当前 bridge-like 同签名里，
   `val_000331`
   仍是默认第一第三条候选；
   `val_000235`
   这类更远但 aggregate 更强的 row
   应解释为：
   - washout-only aggregate candidate
4. `val_000223 / val_000316`
   仍属于：
   - `guardv20_only`
   第二前沿；
   `val_000202`
   仍属于：
   - `guardv65_only`
   的另一支；
   `val_000239`
   仍属于：
   - strict core
   另一侧；
   它们都不应混写成 bridge 第三条。

## 当前默认下一步

默认顺序继续收紧为：

1. 若继续做 bridge row-level 扩张，
   默认先在：
   - `v66>v65 | v66>v67 | v64>v67`
   这条 same-signature 里，
   按 distance
   而不是按 aggregate 排名
   继续看候选；
   当前第一位仍是：
   - `val_000331`
2. `val_000235`
   及其它远距离但 aggregate 很强的 row，
   默认只保留为：
   - washout 诊断样本
   不升级成 bridge 扩张入口。
3. `guardv20_only`、
   `val_000202`、
   `val_000239`
   继续保留在各自分支，
   不并入 bridge 第三条候选序列。
4. 仍不启动新训练。
