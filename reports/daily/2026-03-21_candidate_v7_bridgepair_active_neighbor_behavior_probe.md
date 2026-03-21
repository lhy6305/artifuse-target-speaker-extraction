# 2026-03-21 `candidate_v7` bridgepair active-neighbor behavior probe

## 背景

上一轮已经确认：

- row-level bridge
  仍只有：
  - `val_000376`
  - `val_000430`
- `{331,376,430}`
  仍只是：
  - aggregate-only trio
  不能升级成新的 family 中心

因此如果还要继续向 active split
外推，
下一步就不能再沿：

- trio soft-seed

去找第四条，
而应该先回答一个更基础的问题：

- 在当前 active split 里，
  到底有没有贴近
  `{376,430}`
  这对 bridge 的邻域；
- 如果有，
  它们行为上
  到底更像：
  - `v66`
    的 bridge 方向，
  还是
  - `v67 / v65`
    的别的前沿。

## 本轮新增

### 1. 新脚本

已新增：

- `scripts/eval/analyze_manifest_seed_neighbors.py`

作用：

- 从 seed manifest
  读入一组 seed rows；
- 在另一个或多个 search manifests
  中，
  按 metadata z-distance
  排序最近邻；
- 输出：
  - seed center
  - 最近邻列表
  - split / recipe / pattern 统计

### 2. active split val manifest 补齐 metrics

为让 train / val
都能进入同一套 metadata 距离分析，
本轮先补出：

- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_with_metrics.jsonl`

### 3. active split 上的 bridgepair 邻域分析输出

- `reports/eval/active_split_bridgepair_neighbor_analysis/summary.json`

seed 保持为：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_val.txt`

也就是：

- `val_000376`
- `val_000430`

search 空间为当前 active split：

- `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_with_metrics.jsonl`

### 4. 物化 active-neighbor top10 资产

已物化：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10_{train,val,all}.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10.jsonl`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10.jsonl`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10_all.jsonl`
- `tmp/candidate_v7_bridgepair_active_metadata_neighbor_top10_selector_assets_summary.json`

### 5. 行为 compare 与方向诊断输出

本轮又在上述 top10 子集上，
实际补跑了：

- `v19 -> v20`
- `v19 -> v24`
- `v19 -> v64`
- `v19 -> v65`
- `v19 -> v66`
- `v19 -> v67`

对应输出：

- `reports/eval/compare_v19_vs_v20_on_bridgepair_active_metadata_neighbor_top10_all/`
- `reports/eval/compare_v19_vs_v24_on_bridgepair_active_metadata_neighbor_top10_all/`
- `reports/eval/compare_v19_vs_v64_on_bridgepair_active_metadata_neighbor_top10_all/`
- `reports/eval/compare_v19_vs_v65_on_bridgepair_active_metadata_neighbor_top10_all/`
- `reports/eval/compare_v19_vs_v66_on_bridgepair_active_metadata_neighbor_top10_all/`
- `reports/eval/compare_v19_vs_v67_on_bridgepair_active_metadata_neighbor_top10_all/`

并进一步汇总到：

- `reports/eval/bridgepair_active_metadata_neighbor_top10_direction_analysis/summary.json`

## 结果

### 1. active split 里确实存在 bridgepair 的 metadata-near train 邻域，而且比 `331` 更近的基本全是 train rows

当前 top10 最近邻为：

1. `train_000597`
   - distance：
     - `0.468169`
2. `train_001978`
   - `0.521794`
3. `train_001279`
   - `0.525416`
4. `train_001599`
   - `0.596802`
5. `train_001219`
   - `0.671659`
6. `train_001991`
   - `0.712757`
7. `train_000737`
   - `0.759137`
8. `train_000432`
   - `0.847914`
9. `train_001079`
   - `0.858460`
10. `val_000331`
    - `0.893547`

也就是说：

- 在当前 active split 里，
  bridge pair
  并不是一个完全孤立的 val-only 结构；
- 它周围确实已有一簇
  metadata 更近的 train rows；
- 而 `val_000331`
  反而只是这簇 active-neighbor
  里的第十近邻。

### 2. 这簇 active-neighbor top10 全部是 `target_clean_speech`，但 temporal pattern 已经混入明显 nonfull

top10 资产当前组成是：

- train：
  - `9`
- val：
  - `1`
  - `val_000331`
- recipe：
  - 全部都是：
    - `target_clean_speech`
- temporal pattern：
  - `target_full = 6`
  - `target_absent_head = 3`
  - `target_absent_tail = 1`

更关键的是：

- `train_001279`
  正好命中此前已证伪的：
  - `exact_nontargetfull`
  absent-like 资产

也就是：

- 这批 rows
  虽然 metadata 上贴近 bridge pair；
- 但已经明确混入了
  已知的 absent-like 语义。

因此：

- metadata-near
  在这里最多只能先说明：
  - active split 有 coverage；
- 不能直接说明：
  - 语义也已经对题。

### 3. 行为上，这个 top10 邻域整体不是 bridge-like；aggregate 排序直接塌成 `v67 > v65 > v66 > v64`

在 top10 combined manifest 上，
aggregate ranking 当前为：

1. `v67`
   - `-10.926221`
2. `v65`
   - `-10.940100`
3. `v66`
   - `-10.973165`
4. `v64`
   - `-10.983498`
5. `v20`
   - `-11.033193`
6. `v24`
   - `-11.045107`
7. `baseline`
   - `-11.045114`

也就是：

- `v66 > v64`
  只弱正：
  - `+0.010333 dB`
- 但更关键的：
  - `v66 > v65`
  直接失败：
  - `-0.033064 dB`
- `samplewise_extra_constraint_pass`
  更是：
  - `0 / 10`

所以：

- 这 10 条 active-neighbor
  不能再解释成：
  - bridge pair
    在 active split 里的直接行为扩张；
- 更准确的解释应是：
  - metadata 上贴近 bridge，
  - 但行为排序已经漂到：
    - `v67 / v65`
      主导的混合区。

### 4. top10 行为上会稳定裂成三组，而不是一条连续 bridge family

按真实 top alias
与 `v66` 排名，
当前 top10 可以稳定拆成三组：

#### A. `v66top`

- `train_000597`
- `train_001599`

特点：

- `v66`
  真正排第 `1`
- 是当前 top10 里
  唯二真正站住
  `v66` 主导的 rows

已物化：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v66top_{train,val,all}.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v66top.jsonl`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v66top.jsonl`

#### B. `v67top_v66near`

- `train_001978`
- `train_001991`
- `train_000737`
- `train_001079`

特点：

- top alias
  已经是：
  - `v67`
- 但 `v66`
  仍排在：
  - `2` 或 `3`

这更像：

- 靠近 bridge 区域，
  但已明显滑向
  `v67`
  主导的一层中间带

已物化：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v67top_v66near_{train,val,all}.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v67top_v66near.jsonl`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v67top_v66near.jsonl`

#### C. `v65top_tail`

- `train_001279`
- `train_001219`
- `train_000432`
- `val_000331`

特点：

- top alias
  直接变成：
  - `v65`
- `val_000331`
  就落在这组里，
  rank：
  - `6`
- `train_001279`
  也落在这组里，
  并且它本来就是：
  - 已知 absent-like
    `exact_nontargetfull`
    旧资产

这说明：

- `331`
  虽然在 shared val `50`
  上是 bridge pair
  最近的 aggregate-only 第三条；
- 但一旦投影到 active split
  的 metadata-neighbor 区域，
  它并不落在
  `v66` 领先带里，
  而是直接掉进：
  - `v65top tail`

已物化：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v65top_tail_{train,val,all}.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v65top_tail.jsonl`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_v65top_tail.jsonl`

## 当前结论

1. active split
   对 bridge pair
   不是没有 coverage；
   恰恰相反，
   它周围有一簇
   明显更近的 train rows。
2. 但这簇 coverage
   行为上不是 bridge-like family，
   而是：
   - `v66top`
   - `v67top_v66near`
   - `v65top_tail`
   三层混合区。
3. 因此：
   - metadata-neighbor
     只能先当：
     - 诊断缓冲区
   - 不能直接当：
     - bridge selector
     - bridge projection proxy
     - 训练入口
4. `val_000331`
   的定位也必须继续收紧：
   - 它仍可保留为 shared-val 上的
     aggregate-only 第三条；
   - 但在 active split 投影里，
     它已经明确落在：
     - `v65top_tail`
     而不是：
     - `v66` 领先带

## 当前默认下一步

默认顺序继续更新为：

1. 若继续做 bridge 方向扩张，
   默认只保留：
   - `{val_000376, val_000430}`
   为 row-level bridge；
   不把 active-neighbor top10
   整体当成 bridge family。
2. active-neighbor top10
   默认改解释为：
   - behavior-mixed diagnostic buffer
   而不是：
   - 新 proxy 入口
3. 若后续还要在 active split
   继续追这条线，
   默认优先看：
   - `v66top`
   这 `2` 条
   是否能和 row-level bridge
   建立更直接联系；
   而不是继续沿
   `331`
   或整包 top10
   往外推。
4. `v67top_v66near`
   与 `v65top_tail`
   继续保留为边界层与负向尾部，
   尤其：
   - `train_001279`
   - `val_000331`
   应继续视作
   风险提示样本。
5. 仍不启动新训练。
