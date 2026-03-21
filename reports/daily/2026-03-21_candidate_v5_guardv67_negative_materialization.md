# 2026-03-21 `candidate_v5_guardv67_negative` materialization

## 背景

`v67`
已经把
`candidate_v4_guardv66_by_v64`
真实 union
进训练，
因此 coverage
问题已经排除。

上一轮新增的关键信息是：

- 在 shared
  `friend_speech_leak_search_v1`
  compare 上，
  显式要求：
  - `v67 > v66`
    的正向 family
    为 `0`
- 而显式要求：
  - `v66 > v67`
    的负向 family
    仍能找到稳定 order-pass 候选

因此当前默认下一步
不该回到训练，
而应先把这条
`v67 negative`
family
正式物化成可复用 proxy 资产，
再判断它和
`candidate_v4`
危险子族
到底是什么关系。

## 先踩到的坑

我先直接尝试把
negative-search top candidate
原样投影到 full train / val manifest，
即只保留搜索 summary
里最顶部那组
`builder_filters`：

- `max_interference_gain_db`
- `max_target_transient_presence_minus_mid_db_mean`
- `min_interference_transient_presence_minus_mid_db_mean`
- `min_target_interference_logspec_cosine`

结果直接失败，
原因不是脚本坏掉，
而是：

- shared search manifest
  只覆盖 speech-only compare rows；
- 但 full manifest
  上若仍保持
  `all_pools / all_patterns`
  的默认自由度，
  就会把过滤条件
  投影到一些
  non-speech interference
  源；
- `build_metadata_focused_manifest.py`
  会因此尝试读取：
  - `data_in/pure_music_dataset/无吉他.m4a`
  - `data_in/pure_music_dataset/Lightmore.m4a`
  这类 `soundfile`
  无法直接解码的文件。

也就是说：

- search summary
  的 top family
  在 shared compare 上是合法的；
- 但它不能未经收紧
  就直接拿去 full manifest
  做训练资产物化。

## 采用的物化口径

当前改用
top-equivalent 的
clean/full variant，
因为它在 search summary
里和 top negative family
共享完全相同的
`3` 条 val rows，
但能安全投影到 full manifest：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.75`
- `speech_interference_clean_pool`
- `interference_gain_db <= -2.9865000247955322`
- `target_transient_presence_minus_mid_db_mean <= -7.436224937438965`
- `interference_transient_presence_minus_mid_db_mean >= 4.159853935241699`
- `target_interference_logspec_cosine >= 0.5872839093208313`

## 已物化资产

本轮已正式生成：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 12`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 3`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative_val.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative_all.txt`

val `3` 条 rows 为：

- `val_000076`
- `val_000274`
- `val_000469`

同时也已准备好
若后续继续训练时
可直接使用的 union split：

- `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 141`
- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 40`

也就是：

- 相对 `v42` base split，
  新增 train `12`
  rows
- 新增 val `3`
  rows
- overlap with current
  `v42` base split
  仍是：
  - train `0 / 12`
  - val `0 / 3`

selector / union
摘要文件：

- `tmp/candidate_v5_guardv67_negative_selector_assets_summary.json`

materialization /
overlap 摘要文件：

- `reports/eval/synthetic_proxy_search_candidate_v5_guardv67_negative_on_friend_speech_leak_search_v1/materialized_candidate_v5_summary.json`

## 定点方向诊断

已补两份 focused summary：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v5_guardv67_negative_direction_analysis/summary.json`
- `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v5_guardv67_negative_direction_analysis/summary.json`

在这 `3` 条 val rows 上，
aggregate 排名为：

- `v64 > v35 > v66 > v20 > v29 > v65 > ... > v67`

关键 gap：

- `v66 - v64 = -0.039333 dB`
- `v66 - v65 = +0.026017 dB`
- `v66 - v67 = +0.056485 dB`

这说明：

- 这条 family
  不是“`v64 / v66`
  near-tie”的中间态；
- 它本身就是更明确的：
  - `v64 > v66 > v65 > v67`
    negative family

row-level
仍不完全硬，
但方向上比
`candidate_v4`
更集中：

- `v66`
  的 rank histogram：
  - `2 x1`
  - `6 x1`
  - `10 x1`
- `v67`
  的 rank histogram：
  - `4 x1`
  - `10 x1`
  - `11 x1`

## 与 `candidate_v4` carve / pruned 的关系

这一步最重要的新事实是：

- `candidate_v5`
  不是简单等于：
  - `candidate_v4`
    的 carve 子族
- 也不是简单等于：
  - `candidate_v4`
    的 pruned 剩余子族

它当前横跨了两边：

- val overlap with
  `candidate_v4 carve`：
  - `1 / 3`
  - `val_000469`
- val overlap with
  `candidate_v4 pruned`：
  - `2 / 3`
  - `val_000076`
  - `val_000274`

train 侧也一样：

- train overlap with
  `candidate_v4 carve`：
  - `2 / 12`
- train overlap with
  `candidate_v4 pruned`：
  - `10 / 12`

也就是说：

- 上一轮用
  `low target transient + high interference transient share`
  做的第一刀 carve-out
  确实切中了
  `v67`
  最危险的核心子族；
- 但新的
  `candidate_v5`
  仍保留了一个
  `carve` 锚点
  `val_000469`；
- 因而当前更合理的解释不是：
  - “坏的就是那 4 条，
     删掉就结束”
- 而是：
  - `v66 > v67`
    这条负向 family
    横跨了
    `candidate_v4`
    的两边，
    只是
    `carve`
    那边更危险、
    幅度更大。

## 当前结论

1. `candidate_v5_guardv67_negative`
   已可作为新的
   `v67 negative`
   诊断锚点，
   但它不是
   `candidate_v4`
   的正式替代品。
2. 它当前更适合回答的是：
   - 哪一小簇 family
     会稳定满足
     `v64 > v66 > v65 > v67`
3. 这条 family
   已经说明：
   - `v67`
     的负向行为
     不是只集中在
     `candidate_v4 carve`
     那 `4` 条 rows；
   - 但 `carve`
     里至少有一个
     强锚点
     `val_000469`
     仍落在
     真正的负向 family
     之内。
4. 因而下一步若继续，
   默认仍不启动新训练，
   而应优先：
   - 继续做
     `candidate_v4 / candidate_v5`
     之间的 semantic split
   - 特别检查：
     - `val_000469`
       为什么同时属于
       `candidate_v4 carve`
       与 `candidate_v5 negative`
     - `val_000076 / val_000274`
       为什么虽然位于
       `candidate_v4 pruned`
       一侧，
       仍稳定满足
       `v66 > v67`

## 当前默认下一步

默认顺序更新为：

1. 保留：
   - `candidate_v4`
     作为“`v64 / v66`
     分界 working family”
2. 新增保留：
   - `candidate_v5_guardv67_negative`
     作为“`v67`
     负向锚点 family”
3. 下一层若继续，
   默认不是训练，
   而是继续做：
   - `candidate_v4`
     与 `candidate_v5`
     的交并分析
   - 尤其聚焦：
     - `candidate_v4 carve ∩ candidate_v5`
     - `candidate_v4 pruned ∩ candidate_v5`
4. 只有在这一步
   重新明确
   哪些 rows
   是：
   - `v64 / v66`
     分界信号
   - 哪些 rows
     是：
     `v66 / v67`
     负向锚点
   之后，
   才值得再考虑：
   - 新 proxy family
   - 或新的 branch-protect
     objective 组合
