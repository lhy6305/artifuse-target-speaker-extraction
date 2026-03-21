# 2026-03-21 `candidate_v7` bridgepair active microbuffer targetfull split

## 背景

上一轮已经把
bridgepair 的 active-neighbor top10
拆成三层，
并确认：

- top10 整体不是 bridge family；
- 其中最接近可保留训练侧缓冲的
  只有：
  - `v66top`
    两条：
    - `train_000597`
    - `train_001599`

为了不只停在
“这两条看起来像正例”，
本轮继续做了两步：

1. 用它们的共同 metadata
   做一个更宽的 active microbuffer carve；
2. 再检查：
   - 到底是 carve 本身有信号，
   - 还是一混入 nonfull
     就又塌回 absent-like / `v65` 区。

## 本轮做法

### 1. 先构造一个宽版 active microbuffer `v66top_v1`

直接在当前 active split 上
使用：

- `recipe = target_clean_speech`
- `target_transient_presence_share_mean <= 0.008`
- `interference_transient_presence_minus_mid_db_mean <= -1.0`

得到：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1.jsonl = 7`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1.jsonl = 2`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_all.jsonl = 9`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_{train,val,all}.txt`

样本为：

- train：
  - `train_000346`
  - `train_000375`
  - `train_000405`
  - `train_000597`
  - `train_001491`
  - `train_001599`
  - `train_001843`
- val：
  - `val_000243`
  - `val_000430`

### 2. 对宽版 `v66top_v1` 实际补跑 compare 与方向诊断

已补跑：

- `v19 -> v20 / v24 / v64 / v65 / v66 / v67`

对应 compare 输出：

- `reports/eval/compare_v19_vs_v20_on_bridgepair_active_microbuffer_v66top_v1/`
- `reports/eval/compare_v19_vs_v24_on_bridgepair_active_microbuffer_v66top_v1/`
- `reports/eval/compare_v19_vs_v64_on_bridgepair_active_microbuffer_v66top_v1/`
- `reports/eval/compare_v19_vs_v65_on_bridgepair_active_microbuffer_v66top_v1/`
- `reports/eval/compare_v19_vs_v66_on_bridgepair_active_microbuffer_v66top_v1/`
- `reports/eval/compare_v19_vs_v67_on_bridgepair_active_microbuffer_v66top_v1/`

方向汇总：

- `reports/eval/bridgepair_active_microbuffer_v66top_v1_direction_analysis/summary.json`

### 3. 再把宽版 carve 按 temporal pattern 收窄成 `target_full` 版

宽版 `v66top_v1`
的 temporal pattern 为：

- `target_full = 3`
- `target_absent_head = 2`
- `target_absent_tail = 2`
- `target_intermittent = 1`

也就是：

- 它一开始就混着明显 nonfull / absent rows。

于是本轮继续只保留：

- `target_full`

得到：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull.jsonl = 3`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull.jsonl = 1`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_{train,val,all}.txt`
- `tmp/candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_selector_assets_summary.json`

样本固定为：

- `train_000597`
- `train_001599`
- `train_001843`
- `val_000430`

并进一步汇总到：

- `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_direction_analysis/summary.json`

## 结果

### 1. 宽版 `v66top_v1` 一混入 nonfull，就整体塌成 `v65 > v64 > v66`

宽版 `v66top_v1`
aggregate ranking 当前为：

1. `v65`
2. `v64`
3. `v66`
4. `v20`
5. `v67`

关键约束：

- `v66 > v64 = -0.049224 dB`
  - fail
- `v66 > v65 = -0.055437 dB`
  - fail

也就是说：

- 这条宽 carve
  虽然来自：
  - `v66top` 两条
    的共同 metadata
- 但一旦把 nonfull / absent
  rows 混进来，
  整体行为就不再是：
  - `v66` 主导
  而是：
  - `v65`
    主导

### 2. 这次把宽 carve 拉坏的，确实主要就是 nonfull / absent 混入，而不是 carve 本身完全没信号

宽版 `v66top_v1`
里最危险的 rows 包括：

- `train_000405`
- `train_001491`

它们本身就命中此前已知的：

- absent-like
  `exact_nontargetfull`

旧资产。

更直接地说：

- 这条 carve
  之所以整体塌成
  `v65 > v64 > v66`，
  不是因为：
  - `train_000597`
  - `train_001599`
  这类正例本身不稳；
- 而是因为：
  - 只靠 share / interference transient
    这两个阈值，
    还不足以自动排掉
    absent-like rows

### 3. 一旦只保留 `target_full`，aggregate 立刻恢复成 `v66` 第一，而且 full extra constraints 全部 aggregate pass

`target_full` 版
aggregate ranking 当前为：

1. `v66`
2. `v64`
3. `v67`
4. `v20`
5. `v65`

关键约束全部 aggregate pass：

- `v66 > v64 = +0.014670 dB`
- `v66 > v65 = +0.114106 dB`
- `v66 > v67 = +0.062182 dB`
- `v64 > v67 = +0.047513 dB`
- `v20 > v24 = +0.036113 dB`

这说明：

- 同一条 metadata carve
  并不是完全没信号；
- 真正关键的修复动作
  是：
  - 把 nonfull / absent
    先拆出去；
- 一旦只看 `target_full`，
  这条 active microbuffer
  就能恢复成：
  - `v66`
    主导的 aggregate-pass 小缓冲

### 4. 但这个 `target_full` 微缓冲仍不能直接误写成 row-level clean family；目前更像“训练侧弱缓冲”

当前 `target_full` 版
虽然 aggregate 全过，
但 samplewise 仍只有：

- `ordered pass = 3 / 4`
- `extra pass = 1 / 4`

逐条看：

- `train_000597`
  - rank `1`
  - `v66 - v64 = +0.026323`
  - extra 仍 fail
- `train_001599`
  - rank `1`
  - `v66 - v64 = +0.045374`
  - extra 仍 fail
- `train_001843`
  - rank `4`
  - `v66 - v64 = -0.032324`
  - 是当前这条小缓冲里的 noisy carry-over
- `val_000430`
  - rank `1`
  - `v66 - v64 = +0.019306`
  - extra pass = `True`

也就是说：

- 这条 `target_full` 微缓冲
  已经足够说明：
  - train 侧确实有一小块
    `v66` 行为缓冲；
- 但它还不能升级成：
  - row-level clean family
  或：
  - 新训练入口

## 当前结论

1. active-neighbor 上，
   `v66top` 两条
   并不是偶然正例；
   它们确实能拉出一条
   `target_full`-only
   的 `v66` 微缓冲。
2. 但这条微缓冲极易被
   nonfull / absent rows
   污染；
   一旦不先拆 pattern，
   宽版 carve
   就会整体塌成：
   - `v65 > v64 > v66`
3. 因而当前更准确的正式定位应改成：
   - 宽版 `v66top_v1`
     = contaminated active microbuffer
   - `target_full` 版
     = aggregate-pass
       `v66` microbuffer
       with noisy carry-over

## 当前默认下一步

默认顺序继续收紧为：

1. 若继续在 active split
   追 bridge 方向，
   默认优先保留的是：
   - `target_full` 版
     `v66` microbuffer
   而不是：
   - 宽版 `v66top_v1`
2. 宽版 `v66top_v1`
   默认只保留为：
   - “nonfull 混入会把 aggregate
      重新拉回 `v65`”
     的反例资产
3. `train_001843`
   当前继续保留为
   `target_full` 微缓冲里的
   noisy carry-over；
   不与：
   - `train_000597`
   - `train_001599`
   - `val_000430`
   写成同纯度成员
4. 仍不启动新训练。
