# 2026-03-21 `candidate_v6` pure-negative expand

## 背景

上一轮已经把
`candidate_v4`
拆成：

- `v4carve_only_guardv67_negative`
- `v4carve_v5_dualanchor`

当前若继续停在 proxy 侧，
自然下一步就是：

1. 看
   `v4carve_only`
   能不能扩成更稳定的
   pure-negative family；
2. 看
   `dualanchor`
   能不能扩成
   比 `candidate_v5`
   更聚焦的新 family

## 本轮搜索

### 1. pure-negative expand 搜索

搜索口径：

- ordered aliases：
  - `v66 > v64`
- extra constraints：
  - `v66 > v65`
  - `v66 > v67`
  - `v64 > v67`
  - `v20 > v24`

输出：

- `reports/eval/synthetic_proxy_search_candidate_v6_v4carve_only_expand_on_friend_speech_leak_search_v1/summary.json`

结果：

- top order-pass family
  不是旧的
  `165 / 223 / 401`
  三条；
- 而是新的 val `3` 条：
  - `val_000165`
  - `val_000331`
  - `val_000430`

对应 top-equivalent
clean/full variant：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.90`
- `speech_interference_clean_pool`
- `interference_gain_db >= -2.9865000247955322`
- `target_transient_presence_minus_mid_db_mean <= -10.191147327423096`
- `target_interference_logspec_cosine >= 0.611259937286377`

### 2. dualanchor expand 搜索

搜索口径：

- ordered aliases：
  - `v64 > v66`
- extra constraints：
  - `v66 > v65`
  - `v66 > v67`
  - `v64 > v67`
  - `v20 > v24`

输出：

- `reports/eval/synthetic_proxy_search_candidate_v6_dualanchor_expand_on_friend_speech_leak_search_v1/summary.json`

结果：

- top order-pass family
  没有产生新的
  `469`-centric family；
- 直接塌回已有的
  `candidate_v5`：
  - `val_000076`
  - `val_000274`
  - `val_000469`

这说明：

- 当前在 `min-count = 3`
  口径下，
  `dualanchor`
  还扩不出
  比 `candidate_v5`
  更干净的新 family。

## `candidate_v6` 已物化资产

新资产：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 13`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 3`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand_{train,val,all}.txt`
- `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 135`
- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 38`

selector / union summary：

- `tmp/candidate_v6_v4carve_only_expand_selector_assets_summary.json`

## focused direction

summary：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`

aggregate：

- `v66 - v64 = +0.013671 dB`
- `v66 - v65 = +0.083866 dB`
- `v66 - v67 = +0.038650 dB`

也就是：

- `candidate_v6`
  确实是新的
  pure-negative expand family；
- 而且 aggregate 上
  比旧
  `v4carve_only`
  更明确地满足：
  - `v66 > v64`
  - `v66 > v65`
  - `v66 > v67`

## 与旧 pure-negative 子族的关系

`candidate_v6`
  val `3` 条为：

- `val_000165`
- `val_000331`
- `val_000430`

与旧
`v4carve_only_guardv67_negative`
val 只重叠：

- `val_000165`

与 `dualanchor`：

- 无重叠

这说明：

- `candidate_v6`
  不是对旧 pure-negative
  的简单重命名；
- 它是一个新的
  扩展 family，
  只是保留了
  `val_000165`
  这个旧锚点。

## row-level 解释

虽然 aggregate
已经转成更干净的
`v66` 顶部 family，
但 row-level
仍不完全硬：

- `val_000430`
  是最强核心：
  - `v66 > v64 > v67`
  - `v66 > v65`
  全成立
- `val_000331`
  只满足：
  - `v66 > v64`
  但 `v66 < v65`
- `val_000165`
  仍是旧的 noisy carry-over：
  - `v66 < v64`
  - `v66 < v65`
  但 `v67`
  仍更差

所以当前更合理的解释是：

- `candidate_v6`
  是比旧
  `v4carve_only`
  更强的 aggregate pure-negative family；
- 但它还不是 row-level
  fully clean family。

## 当前结论

1. `candidate_v6_v4carve_only_expand`
   当前值得保留，
   作为新的
   pure-negative expand family。
2. `dualanchor`
   这条线
   在 `min-count=3`
   下没有新解；
   当前仍只能退回：
   - `candidate_v5`
   或单点
   `val_000469`
3. 当前下一步若继续，
   默认应改为：
   - 保留
     `candidate_v6`
     作为新的
     pure-negative working family
   - 保留
     `val_000469`
     作为单独硬 anchor
   - 不继续尝试把
     `dualanchor`
     扩成新的
     `3+ row`
     family

## 当前默认下一步

默认顺序更新为：

1. 若继续做 proxy，
   默认优先围绕：
   - `candidate_v6_v4carve_only_expand`
   - `val_000469`
   继续解释；
2. 若未来真要开训练，
   当前比整包
   `candidate_v5`
   更值得优先考虑的
   是：
   - `candidate_v6`
     这条新 pure-negative family；
3. 本轮没有启动新训练。
