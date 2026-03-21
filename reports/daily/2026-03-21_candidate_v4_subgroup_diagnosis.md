# 2026-03-21 `candidate_v4` subgroup diagnosis

## 背景

`v67`
已经把
`candidate_v4_guardv66_by_v64`
真实 union 进训练：

- train `33 / 161`
- val `10 / 47`

所以 coverage
问题已经排除。

但当前还缺一块关键事实：

- `candidate_v4`
  这 `10` 条 val rows
  到底是不是同一类语义；
- 还是里面已经混进了
  一簇会把
  `branch_protect`
  方向拖反的子族。

如果这一步不补，
后续就只能停留在：

- `v67 = objective / proxy mismatch`

这种过粗结论，
没法继续决定
下一步该优先：

- 改 loss primitive
- 还是先拆 proxy family。

## 本轮新增

已新增可复用脚本：

- `scripts/eval/analyze_proxy_candidate_subgroups.py`

作用：

- 读取
  `analyze_proxy_candidate_direction.py`
  的 focused summary
- 再 join
  focused manifest 里的连续元数据字段
- 输出：
  - overall focused compare
  - 每个数值字段的 median split subgroup summary
  - 每个 compare alias 下
    最明显改善 / 回退的 row 列表

本轮实际产出：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_guardv66_by_v64_subgroup_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v4_guardv67_by_v64_subgroup_analysis/summary.json`

输入 manifest：

- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`

重点分析字段：

- `target_transient_presence_minus_mid_db_mean`
- `target_transient_presence_share_mean`
- `interference_transient_presence_minus_mid_db_mean`
- `interference_transient_presence_share_mean`
- `target_interference_logspec_cosine`

## 结果

### 1. `candidate_v4` 不是均匀 family

`v66`
在这 `10` 条 rows 上
relative to `v64`
整体只是：

- `-0.003908 dB`

看起来像 near-tie。

但一旦按 subgroup 拆开，
方向就不均匀：

- 按
  `interference_transient_presence_share_mean`
  中位数切分：
  - low share `5` 条：
    - `v66 - v64 = +0.007478 dB`
  - high share `5` 条：
    - `v66 - v64 = -0.083835 dB`
- 按
  `target_transient_presence_minus_mid_db_mean`
  中位数切分：
  - higher target transient `5` 条：
    - `v66 - v64 = +0.012002 dB`
  - lower target transient `5` 条：
    - `v66 - v64 = -0.088359 dB`

也就是：

- `candidate_v4`
  里已经至少混着两种不同方向的 rows；
- `v66`
  不是“在全部 `candidate_v4` rows 上都接近 `v64`”；
- 它只是：
  - 在一组 rows 上 near-tie / 小正向
  - 在另一组 rows 上系统性负向。

### 2. `v67` 进一步把同一簇 rows 推坏

`v67`
relative to `v66`
整体为：

- `-0.034271 dB`

但主要回退也集中在同一簇 rows：

- 按
  `interference_transient_presence_share_mean`
  中位数切分：
  - low share `5` 条：
    - `v67 - v66 = +0.018265 dB`
    - `v67 - v64 = +0.007478 dB`
  - high share `5` 条：
    - `v67 - v66 = -0.086806 dB`
    - `v67 - v64 = -0.083835 dB`
    - improved count：
      - `0 / 5`
- 按
  `target_transient_presence_minus_mid_db_mean`
  中位数切分：
  - higher target transient `5` 条：
    - `v67 - v66 = +0.003848 dB`
    - `v67 - v64 = +0.012002 dB`
  - lower target transient `5` 条：
    - `v67 - v66 = -0.072390 dB`
    - `v67 - v64 = -0.088359 dB`

这说明：

- `v67`
  不是“整个 `candidate_v4`
  family 全面一起退”；
- 更接近的事实是：
  - 它保住甚至略推高了
    一簇
    higher-target-transient /
    lower-interference-transient-share
    rows；
  - 但把另一簇
    lower-target-transient /
    higher-interference-transient-share
    rows
    系统性推坏了。

### 3. 当前最值得单独 carve-out 的 intersection 已经很清楚

若取两条最稳定的危险条件交集：

- `target_transient_presence_minus_mid_db_mean <= median`
- `interference_transient_presence_share_mean > median`

会得到 `4` 条 rows：

- `val_000165`
- `val_000223`
- `val_000401`
- `val_000469`

在这 `4` 条上：

- `v66 - v64 = -0.000723 dB`
  - 基本 near-tie
- `v67 - v66 = -0.094110 dB`
- `v67 - v64 = -0.094832 dB`

也就是：

- 这 `4` 条
  不是 `v66`
  已经明显压住的 rows；
- 但它们是
  `v67`
  明确进一步推坏的
  核心子族。

### 4. 最明显的坏 row 已经不是随机噪声

`v67 - v66`
回退最大的前几条为：

- `val_000469 = -0.171768 dB`
- `val_000401 = -0.097972 dB`
- `val_000223 = -0.058512 dB`
- `val_000202 = -0.057591 dB`
- `val_000165 = -0.048185 dB`

其中：

- `val_000469 / val_000401 / val_000165`
  同时落在：
  - high similarity
  - low target transient
  - high interference transient share
    的危险区域；
- 这更像一簇稳定子族，
  不是几条无规律 outlier。

## 当前结论

1. `candidate_v4`
   当前仍是有信号的 working candidate，
   但它不是单语义 family。
2. 当前更像：
   - 一簇 rows
     能帮助回答
     `v64 / v66`
     分界；
   - 另一簇 rows
     会把 `branch_protect`
     objective
     推向相反方向。
3. 因而 `v67`
   之后更合理的默认前置动作
   不是再补 coverage，
   也不是立刻继续放大
   同一条 `branch_protect_guard_sisdr_weight`；
4. 下一层若继续，
   默认应优先做：
   - `candidate_v4`
     row-level semantic split / hardness 提升
   - 特别优先排查或 carve-out：
     - low target transient
     - high interference transient share
     的这组 rows

## 当前更新后的下一步建议

默认顺序改为：

1. 先把
   `candidate_v4`
   拆成至少两条 subgroup candidate，
   优先以：
   - `interference_transient_presence_share_mean`
   - `target_transient_presence_minus_mid_db_mean`
   作为第一版 carve-out 边界。
2. 先验证：
   - 去掉上述危险子族后，
     `v64 > v66 > v65`
     的 aggregate family
     是否仍成立。
3. 只有在 split 后
   family 仍保留信号时，
   才值得再去判断：
   - 现有 `branch_protect_guard_sisdr`
     还需不需要新的 protect primitive；
   - 否则先不要把
     objective mismatch
     全部归因到 loss 形式本身。
