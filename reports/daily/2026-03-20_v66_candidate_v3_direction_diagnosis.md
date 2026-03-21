# 2026-03-20 `v66` candidate_v3 synthetic direction diagnosis

## 背景

`v66`
的 real / near-real gate
已经实际落盘：

- relative to `v32`
  的 `friend_speech_leak_followup_gate`
  只剩：
  - `speech_leak_like_gain_floor = clear_fail`
- 其它 gate 项：
  - `default`
  - `speech probe overall`
  - exact `target_full`
  - `guodegang_anchor`
  - `guodegang_absent`
  都已通过

但在这之前，
还缺一块关键诊断：

- `v66`
  到底有没有把
  新的 `candidate_v3_guardv20`
  这批 synthetic rows
  往想要的方向推

如果这一步没补，
就没法区分：

1. 训练本身没吃到
   `candidate_v3`
2. 还是 `candidate_v3`
   这条 proxy
   aggregate 方向虽对，
   但仍和 real `0004`
   语义不完全对齐

## 本轮补做

### 1. 补齐 `v66` 在 shared search manifest 上的 compare

已新增：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/summary.json`
- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/per_sample_metrics.jsonl`

对应 manifest：

- `data/synthetic/val_manifest_friend_speech_leak_search_v1.jsonl`

结果：

- relative to `v19`
  on shared search v1：
  - `avg_sisdr_delta_db = +0.168823 dB`
  - `improved_count = 10`
  - `regressed_count = 6`

### 2. 新增可复用方向诊断脚本

已新增：

- `scripts/eval/analyze_proxy_candidate_direction.py`

作用：

- 读取多份
  同 baseline compare 的
  `per_sample_metrics.jsonl`
- 再只截目标 candidate subset
- 输出：
  - aggregate ranking
  - candidate 相对 reference 的平均增益
  - row-level 排名分布
  - 原始 search 约束
    在该 subset 上
    是否仍成立

### 3. 对 `candidate_v3_guardv20` 做定点诊断

输入：

- sample ids：
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_val.txt`
  - 即：
    - `val_000165`
    - `val_000331`
    - `val_000430`
- compare aliases：
  - `v20 / v24 / v25 / v29 / v30 / v32 / v35 / v64 / v65 / v66`
- reference：
  - `v32`
- candidate：
  - `v66`

输出：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v3_guardv20_direction_analysis/summary.json`

## 结果

### aggregate 排名

在这 3 条 `candidate_v3` val rows 上，
当前 aggregate SI-SDR 排名为：

1. `v66`
2. `v64`
3. `v35`
4. `v20`
5. `v30`
6. `v32`
7. `v29`
8. `v25`
9. `v65`
10. `v24`
11. `v19`

对应 `v66`
相对关键锚点的 aggregate gap：

- vs `v32`：
  - `+0.051855 dB`
- vs `v64`：
  - `+0.013671 dB`
- vs `v35`：
  - `+0.027735 dB`
- vs `v20`：
  - `+0.034547 dB`
- vs `v65`：
  - `+0.083866 dB`
- vs `v24`：
  - `+0.105357 dB`

也就是：

- 从 aggregate 看，
  `v66`
  已经是这批
  `candidate_v3`
  rows 上的当前第一名

### 原 search 方向是否仍成立

在同一组 3 条 rows 上，
`candidate_v3`
当初保留的 aggregate 约束
依然成立：

- `v35 > v25 > v24`
- `v20 > v24`
- `v20 > v65`

说明这次诊断
并不是因为
subset 被替换成了
别的语义才成立。

### row-level 稳定性

不过 row-level
仍明显不够硬：

- `samplewise_order_pass_count = 0 / 3`
- `v66` 的单条 rank 分布：
  - `val_000165`：
    - rank `7`
  - `val_000331`：
    - rank `10`
  - `val_000430`：
    - rank `1`

逐条看：

- `val_000430`
  明显被推正：
  - `v66 - v32 = +0.184288 dB`
- `val_000165`
  基本 near-tie，
  还略低于 `v32`：
  - `v66 - v32 = -0.003362 dB`
- `val_000331`
  也仍低于 `v32`：
  - `v66 - v32 = -0.025361 dB`

因此更准确的表述不是：

- `candidate_v3`
  这 3 条 rows
  已经被统一推正

而是：

- aggregate 方向
  已经被推到
  明显比 `v32`
  更前；
- 但 row-level
  仍高度不均匀，
  gain 主要集中在
  `val_000430`

## 结论

本轮补诊断后，
可以先排除一种误读：

- 不能把 `v66`
  的 real gate fail
  直接解释成：
  - “训练根本没沿
     `candidate_v3`
     方向走”

因为从 synthetic
`candidate_v3` 自身看：

- `v66`
  aggregate 已经排到第一；
- 相对 `v32`
  也确实是正向：
  - `+0.051855 dB`

更合理的当前解释应是：

1. `candidate_v3`
   aggregate 方向
   确实被训练吃到了；
2. 但这条 proxy
   仍只有 aggregate 意义上的
   “working candidate”，
   row-level 语义还不够硬；
3. 因而 real `speech_leak_like (0004)`
   clear fail
   现在更像是：
   - proxy 仍然 partial / mismatch
   而不是
   - branch-protect routing
     完全没起作用

## 当前更新

后续若继续这条线，
默认不再只看：

- real gate failed

还要同时看：

- focused proxy rows
  有没有被真正推高
- 推高是 aggregate 统一成立，
  还是只靠一两条 row 拉动

`v66`
在这套口径下
应记成：

- synthetic direction = yes, aggregate positive
- row-level consistency = still weak
- real `0004` proxy alignment = still unresolved
