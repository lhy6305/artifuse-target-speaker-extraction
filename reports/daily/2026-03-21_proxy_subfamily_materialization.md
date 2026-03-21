# 2026-03-21 proxy subfamily materialization

## 背景

上一轮
`candidate_v4 / candidate_v5`
交并分析
已经把 val rows
拆成四类：

1. `v4 carve only`
2. `v4 carve ∩ v5`
3. `v4 pruned only`
4. `v4 pruned ∩ v5`

其中当前最值得继续保留的
不是整包 `candidate_v5`，
而是：

- `v4 carve only`
  这组更纯的
  `v67` negative rows
- `v4 carve ∩ v5`
  这个硬双信号 anchor

如果这一步不物化，
下次继续时仍然会回到：

- 只有日报里的口头结论；
- 没有现成 selector / union manifest；
- 也没有独立 focused summary

## 本轮新增

已新增可复用 set-op 脚本：

- `scripts/data/build_proxy_manifest_setops.py`

作用：

- 对两组 focused proxy manifest
  做：
  - `intersection`
  - `left_minus_right`
- 直接输出新的
  train / val manifest
  与 summary

## 已物化的两条子族

### 1. `v4carve_only_guardv67_negative`

来源：

- `candidate_v4 carve - candidate_v5`

资产：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 4`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 3`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative_{train,val,all}.txt`
- `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 133`
- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 40`

train rows：

- `train_000676`
- `train_000759`
- `train_000999`
- `train_001748`

val rows：

- `val_000165`
- `val_000223`
- `val_000401`

对应 summary：

- `tmp/proxy_subfamily_v4carve_only_guardv67_negative_summary.json`
- `tmp/proxy_subfamily_v4carve_only_guardv67_negative_selector_assets_summary.json`

focused direction summary：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_only_guardv67_negative_direction_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_only_guardv67_negative_direction_analysis/summary.json`

当前方向：

- `v66 - v64 = +0.007515 dB`
- `v67 - v66 = -0.068223 dB`

当前解释：

- 这条子族
  更像纯净的
  `v67 negative`
  rows；
- 不再混入
  `val_000469`
  那种
  同时承担
  `v64 / v66`
  与
  `v66 / v67`
  双信号的 anchor。

### 2. `v4carve_v5_dualanchor`

来源：

- `candidate_v4 carve ∩ candidate_v5`

资产：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 2`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 1`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor_{train,val,all}.txt`
- `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 131`
- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 38`

train rows：

- `train_000207`
- `train_000805`

val row：

- `val_000469`

对应 summary：

- `tmp/proxy_subfamily_v4carve_v5_dualanchor_summary.json`
- `tmp/proxy_subfamily_v4carve_v5_dualanchor_selector_assets_summary.json`

focused direction summary：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_v5_dualanchor_direction_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_v5_dualanchor_direction_analysis/summary.json`

当前方向：

- `v66 - v64 = -0.025435 dB`
- `v67 - v66 = -0.171768 dB`

当前解释：

- 这不是一条普通
  negative family；
- 而是当前最硬的
  单点双信号 anchor。

## 当前结论

1. `candidate_v5`
   现在不再需要继续整体保留为
   下一步默认训练入口。
2. 当前真正值得保留成标准资产的是：
   - `v4carve_only_guardv67_negative`
   - `v4carve_v5_dualanchor`
3. 这两条子族职责已经分开：
   - 前者回答：
     - 哪些 rows
       会被 `v67`
       系统性推坏
   - 后者回答：
     - 哪个 anchor
       同时处在
       `v64 > v66`
       与
       `v66 > v67`
       的交点

## 当前默认下一步

默认顺序更新为：

1. 若继续留在 proxy 侧，
   默认优先围绕：
   - `v4carve_only_guardv67_negative`
   - `v4carve_v5_dualanchor`
   做下一轮 family 解释
2. 若未来真的要开训练，
   默认不再从：
   - 全量 `candidate_v5`
   起步；
   而优先考虑：
   - `v4carve_only_guardv67_negative`
     作为纯 `v67 negative`
     入口
   - `v4carve_v5_dualanchor`
     作为单独硬 anchor
3. 本轮没有启动新训练，
   只补了资产与 focused summary。
