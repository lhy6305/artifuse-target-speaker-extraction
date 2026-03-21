# 2026-03-21 `candidate_v7` bridgepair seed expansion

## 背景

上一轮已经把
`guardv65_only`
进一步拆成：

- relaxed shell：
  - `val_000202`
  - `val_000239`
  - `val_000376`
  - `val_000430`
- row-level bridge pair：
  - `val_000376`
  - `val_000430`

当前默认下一步已经改成：

- 先围绕
  `{val_000376, val_000430}`
  继续找同向 rows

但真正继续扩之前，
还差两个关键问题：

1. 这对 bridge
   最近的第三条 row
   到底是谁；
2. 它若并进来，
   是：
   - row-level clean 扩张
   还是
   - 只在 aggregate 上
     能被 seed pair 洗白的假扩张。

## 本轮新增

### 1. 新脚本

已新增：

- `scripts/eval/analyze_proxy_seed_expansion.py`

作用：

- 给定 seed rows，
  计算：
  - metadata center
  - constraint-gap center
  - 非 seed rows
    到 seed center 的距离
  - `seed + 1 row`
    的 aggregate 约束结果

### 2. 新分析输出

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`

seed 输入：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_val.txt`

也就是：

- `val_000376`
- `val_000430`

诊断约束保持 full 口径：

- `v66 > v64`
- `v66 > v65`
- `v66 > v67`
- `v64 > v67`
- `v20 > v24`

### 3. aggregate search 对照

为了确认
generic aggregate search
会不会自动找回同一条扩张线，
本轮又补跑了：

- `reports/eval/synthetic_proxy_search_candidate_v7_bridgepair_aggregate_expand_min3_on_friend_speech_leak_search_v1/summary.json`

## 结果

### 1. bridge pair 最近的第三条 row 是 `val_000331`

按 seed-center
joint distance 排序，
当前最接近
`{376,430}`
的非 seed row
是：

- `val_000331`

其 joint distance 为：

- `0.975332`

明显早于后续 rows：

- `val_000075`
  - `1.226977`
- `val_000305`
  - `1.478448`
- `val_000269`
  - `1.676178`
- `val_000065`
  - `1.810191`

`val_000331`
的 metadata 也确实贴近 bridge pair：

- target transient db：
  - `-12.867053`
- target transient share：
  - `0.012056`
- interference transient db：
  - `0.316395`
- interference transient share：
  - `0.191423`
- similarity：
  - `0.632220`

### 2. 但 `val_000331` 不是 row-level clean 第三条；它自己仍 fail 三条 guards

`val_000331`
当前 row-level 仍 fail：

- `v66 > v65`
- `v66 > v67`
- `v64 > v67`

对应 gaps：

- `v66 - v65 = -0.096889 dB`
- `v66 - v67 = -0.065627 dB`
- `v64 - v67 = -0.088484 dB`

所以它不能被解释为：

- strict-core /
  bridge pair
  的第三条 row-level clean 成员

### 3. 但一旦并进 seed pair，`{331,376,430}` 的 aggregate 会重新全约束过关

把

- `val_000331`
- `val_000376`
- `val_000430`

并成
`seed + 1`
后，
aggregate 为：

- `v66 - v64 = +0.016071 dB`
- `v66 - v65 = +0.120962 dB`
- `v66 - v67 = +0.024827 dB`
- `v64 - v67 = +0.008756 dB`
- `v20 - v24 = +0.046605 dB`

也就是：

- full constraints
  全部 aggregate pass；
- 且当前最小 gap
  仍为正：
  - `+0.008756 dB`

所以：

- `{331,376,430}`
  是当前 bridge pair
  最合理的 aggregate-only
  第三条扩张；
- 但它仍不是
  samplewise clean family。

### 4. `val_000202` 不是 bridge pair 的第三条主扩张

虽然
`val_000202`
也能形成
`seed + 1`
aggregate pass，
但它到 bridge pair center
的 joint distance 为：

- `3.448653`

明显远于：

- `val_000331 = 0.975332`

因此：

- `val_000202`
  仍更适合保留为
  `guardv65_only`
  的另一支 near-miss；
- 不再是
  bridge pair
  的第一第三条候选。

### 5. generic aggregate search 会重新塌回旧 family；不会自动保住 bridge 语义

本轮补跑的 generic
`min-count=3`
aggregate search
输出为：

- `reports/eval/synthetic_proxy_search_candidate_v7_bridgepair_aggregate_expand_min3_on_friend_speech_leak_search_v1/summary.json`

当前 top family
仍然回到旧的：

- `val_000165`
- `val_000331`
- `val_000430`

也就是旧
`candidate_v6`
那条 aggregate working family，
而不是：

- `val_000331`
- `val_000376`
- `val_000430`

这说明：

- 若继续依赖 generic aggregate search，
  会再次塌回旧 family；
- bridge 语义只能通过：
  - seed-anchored expansion
    单独保持。

## 本轮已物化资产

### aggregate-only bridge trio

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331.jsonl = 0`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331.jsonl = 3`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331_{train,val,all}.txt`
- `tmp/candidate_v7_bridgepair_aggregate_plus331_selector_assets_summary.json`

val rows：

- `val_000331`
- `val_000376`
- `val_000430`

## 当前结论

1. bridge pair
   `{376,430}`
   最近的第三条 row
   当前是：
   - `val_000331`
2. 但 `val_000331`
   只能算：
   - aggregate-only
     bridge extension
   不能算：
   - row-level clean
     第三条成员
3. 当前最合适的分层解释应改成：
   - row-level bridge：
     `{376,430}`
   - aggregate-only bridge trio：
     `{331,376,430}`
4. generic aggregate search
   不足以保住这条 bridge 语义；
   它会自动塌回旧
   `candidate_v6`
   family。

## 当前默认下一步

默认顺序继续更新为：

1. 若继续做 strict-core 扩张，
   默认第一优先仍围绕：
   - row-level bridge
     `{val_000376, val_000430}`
   继续找同向 rows。
2. `{val_000331, val_000376, val_000430}`
   保留为：
   - aggregate-only bridge trio
   用来跟踪：
   - 哪条第三 row
     会被 seed pair
     在 aggregate 上洗白；
   - 但不要把它误写成
     row-level clean family。
3. generic aggregate search
   若再次塌回
   `candidate_v6`
   或其它旧 family，
   默认不要据此覆盖
   bridge-pair 这条 seed-anchored 解释。
4. 仍不启动新训练。
