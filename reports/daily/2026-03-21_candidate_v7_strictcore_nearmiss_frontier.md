# 2026-03-21 `candidate_v7` strict-core near-miss frontier

## 背景

上一轮已经把
strict core
固定为：

- `val_000239`
- `val_000430`

也已明确：

- 不能再默认沿
  `candidate_v6`
  的 low-transient family
  继续收窄；
- 更合理的下一步
  应该改成：
  - 以 strict core
    为行为锚点，
    去找新的同向 rows。

但在真正继续扩之前，
还缺一个关键问题：

- 当前 search manifest
  里的剩余 `48` 条 rows，
  到底是谁最接近 strict core；
- 它们分别是卡在哪条 guard；
- 这些 near-miss
  是不是同一类，
  还是应该拆成不同扩张前沿。

## 本轮新增

### 1. 新脚本

已新增：

- `scripts/eval/analyze_proxy_strict_near_miss.py`

作用：

- 直接对 shared compare rows
  做 row-level guard 诊断；
- 输出：
  - all-pass rows
  - top near-miss rows
  - single-fail family
  - failed-signature family

### 2. enriched search manifest

为避免 near-miss 结果里
派生特征为空，
本轮先补了：

- `data/synthetic/val_manifest_friend_speech_leak_search_v1_with_metrics.jsonl`

这份 manifest
与原
`friend_speech_leak_search_v1`
保持同一批 `50` 条 rows，
只是补齐：

- transient metrics
- similarity metrics

### 3. near-miss summary

输出：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_nearmiss_analysis_with_metrics/summary.json`

诊断口径仍保持：

- `v66 > v64`
- `v66 > v65`
- `v66 > v67`
- `v64 > v67`
- `v20 > v24`

## 总体结果

当前 `50` 条 shared rows
中：

- strict-all pass：
  - `2`
  - `val_000239`
  - `val_000430`
- near-miss：
  - `48`

各 guard
总体失败频次接近：

- `v66 > v65`
  - `29`
- `v66 > v67`
  - `28`
- `v20 > v24`
  - `27`
- `v64 > v67`
  - `26`
- `v66 > v64`
  - `24`

所以当前真正重要的
不是“哪条 guard
最常失败”，
而是：

- 哪些 rows
  只差一条 guard；
- 且差得最小。

## 单条 guard 失败前沿

### 1. `guardv65_only`

只失败：

- `v66 > v65`

当前 val rows：

- `val_000376`
- `val_000202`

已物化资产：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65.jsonl = 0`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65.jsonl = 2`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65_{train,val,all}.txt`
- `tmp/candidate_v7_singlefail_guardv65_selector_assets_summary.json`

aggregate：

- `v66 - v64 = +0.011899 dB`
- 唯一失败：
  - `v66 - v65 = -0.079787 dB`

其中最关键的是：

- `val_000376`
  只差：
  - `v66 - v65 = -0.004292 dB`

并且它的形态相对更靠近 strict core：

- very low target transient share：
  - `0.004953`
- higher similarity：
  - `0.704216`
- interference transient share：
  - `0.430377`

这说明：

- `guardv65_only`
  是当前最值得优先追的
  strict-core 扩张前沿；
- 尤其
  `val_000376`
  已经接近
  “只差一口气”。

### 2. `guardv20_only`

只失败：

- `v20 > v24`

当前 val rows：

- `val_000223`
- `val_000316`

已物化资产：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20.jsonl = 0`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20.jsonl = 2`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20_{train,val,all}.txt`
- `tmp/candidate_v7_singlefail_guardv20_selector_assets_summary.json`

aggregate：

- `v66 - v64 = +0.020531 dB`
- 唯一失败：
  - `v20 - v24 = -0.057057 dB`

这条前沿的意义是：

- 它保留了全部
  `v66 / v64 / v65 / v67`
  相关 guards；
- 但和旧
  `v20`
  那条 legacy guard
  不再对齐。

所以它更像：

- 另一条可解释的行为分支；
- 而不是 strict core
  的默认主扩张方向。

## 其他已确认事实

### `val_000469`

仍然不是 strict-core near-miss 的第一优先前沿。

它当前是：

- fail：
  - `v66 > v64`
  - `v20 > v24`
- pass：
  - `v66 > v65`
  - `v66 > v67`
  - `v64 > v67`

所以它继续更适合被解释为：

- 单点边界 anchor；
- 而不是 single-fail 扩张候选。

### `candidate_v6` 旧 carry-over

例如：

- `val_000165`

当前仍是：

- fail：
  - `v66 > v64`
  - `v66 > v65`

因此：

- 它不会回到 strict-core
  的第一层扩张前沿。

## 当前结论

1. strict-core 的最近扩张前沿
   当前已明确拆成两条：
   - `guardv65_only`
   - `guardv20_only`
2. 其中默认优先级应写成：
   - 第一优先：
     `guardv65_only`
   - 第二优先：
     `guardv20_only`
3. `guardv65_only`
   更像 strict core
   的直接扩张，
   因为它保住了：
   - `v66 > v64`
   - `v66 > v67`
   - `v64 > v67`
   - `v20 > v24`
   只在
   `v66 > v65`
   上 near-miss。
4. `guardv20_only`
   则更像：
   - 对旧 `v20` guard
     不再对齐的另一条分支，
   暂不应和
   `guardv65_only`
   混成同一条扩张线。

## 当前默认下一步

默认顺序更新为：

1. 若继续做 strict-core 扩张，
   默认先围绕：
   - `guardv65_only`
     特别是
     `val_000376`
   继续找同向 rows。
2. `guardv20_only`
   继续保留，
   但作为第二优先分支，
   用来判断：
   - strict core
     是否还存在一条
     与旧 `v20` guard
     解耦的行为族。
3. `val_000469`
   继续单独保留为
   边界 anchor，
   不并入上述两条前沿。
4. 当前仍不启动新训练。
