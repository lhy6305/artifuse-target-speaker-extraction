# 2026-03-21 `candidate_v7` bridgepair active microbuffer core trio

## 背景

上一轮已经确认：

- 宽版 active microbuffer
  `v66top_v1`
  一混入 nonfull / absent
  就会整体塌成：
  - `v65 > v64 > v66`
- 同一条 carve
  只保留 `target_full`
  后，
  aggregate 会恢复成：
  - `v66 > v64 > v67 > v20 > v65`

但 `target_full` 版里
仍还混着一条 noisy carry-over：

- `train_001843`

因此本轮只剩最后一个问题：

- 如果把
  `train_001843`
  再拆出去，
  剩下的核心三条
  能不能形成一个更干净的
  active-split bridge core。

## 本轮做法

把上一轮 `target_full` 版：

- `train_000597`
- `train_001599`
- `train_001843`
- `val_000430`

继续收窄成 core trio：

- `train_000597`
- `train_001599`
- `val_000430`

并物化为：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core.jsonl = 2`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core.jsonl = 1`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core_all.jsonl = 3`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core_{train,val,all}.txt`

然后继续补跑：

- `v19 -> v20 / v24 / v64 / v65 / v66 / v67`

对应 compare 输出：

- `reports/eval/compare_v19_vs_v20_on_bridgepair_active_microbuffer_v66top_v1_targetfull_core/`
- `reports/eval/compare_v19_vs_v24_on_bridgepair_active_microbuffer_v66top_v1_targetfull_core/`
- `reports/eval/compare_v19_vs_v64_on_bridgepair_active_microbuffer_v66top_v1_targetfull_core/`
- `reports/eval/compare_v19_vs_v65_on_bridgepair_active_microbuffer_v66top_v1_targetfull_core/`
- `reports/eval/compare_v19_vs_v66_on_bridgepair_active_microbuffer_v66top_v1_targetfull_core/`
- `reports/eval/compare_v19_vs_v67_on_bridgepair_active_microbuffer_v66top_v1_targetfull_core/`

方向汇总：

- `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`

## 结果

### 1. 去掉 `train_001843` 后，core trio aggregate 继续保持 `v66` 第一，而且 full extra constraints 全过

当前 core trio
aggregate ranking 为：

1. `v66`
2. `v64`
3. `v67`
4. `v20`
5. `v24`
6. `baseline`
7. `v65`

关键 aggregate gaps 为：

- `v66 > v64 = +0.030334 dB`
- `v66 > v65 = +0.181224 dB`
- `v66 > v67 = +0.052351 dB`
- `v64 > v67 = +0.022017 dB`
- `v20 > v24 = +0.009617 dB`

也就是：

- 相比上一轮 `target_full` 版，
  这条 core trio
  不只是：
  - aggregate top alias
    仍是 `v66`
- 而是：
  - full extra constraints
    继续全部 aggregate pass；
  - 且 `v66 > v65`
    进一步拉大到：
    - `+0.181224 dB`

### 2. `train_001843` 的确就是上一轮 target_full 微缓冲里的主要 carry-over；一拆掉它，`v66` 与 `v64/65` 的 aggregate 关系明显变硬

上一轮 `target_full` 版：

- `v66 > v64 = +0.014670 dB`
- `v66 > v65 = +0.114106 dB`

本轮 core trio：

- `v66 > v64 = +0.030334 dB`
- `v66 > v65 = +0.181224 dB`

也就是说：

- 去掉
  `train_001843`
  之后，
  `v66`
  对：
  - `v64`
  - `v65`
  的 aggregate margin
  都明显变硬了；
- 所以当前可以正式把
  `train_001843`
  记成：
  - 上一轮 target_full 微缓冲里的
    主要 noisy carry-over

### 3. 这条 core trio 还不是 row-level clean family；当前剩下的唯一 row-level 漏点仍是 train 侧两条在 `v64 > v67`

当前 core trio
samplewise 指标为：

- `ordered pass = 3 / 3`
- `extra pass = 1 / 3`

逐条看：

- `train_000597`
  - top alias：
    - `v66`
  - fail 的唯一 extra constraint：
    - `v64 > v67 = -0.016609 dB`
- `train_001599`
  - top alias：
    - `v66`
  - fail 的唯一 extra constraint：
    - `v64 > v67 = -0.031424 dB`
- `val_000430`
  - top alias：
    - `v66`
  - full extra constraints
    全部 samplewise pass

所以：

- 当前 core trio
  已经不是：
  - 混着多个前沿的 buffer
- 而是：
  - 一个 aggregate 上已经很干净、
  - 但 train 侧两条
    还差同一条旧 guard
    `v64 > v67`
    的小 core

## 当前结论

1. `train_001843`
   已可正式判定为：
   - `target_full` 微缓冲里的
     主要 noisy carry-over
2. 当前 active-split
   最小可保留 bridge-like core
   应进一步收窄为：
   - `train_000597`
   - `train_001599`
   - `val_000430`
3. 这条 core trio
   当前应正式定位为：
   - aggregate-pass active microbuffer core
   with shared train-side
   `v64 > v67` leak
4. 它仍不能升级成：
   - row-level clean family
   但已经比：
   - active-neighbor top10
   - 宽版 `v66top_v1`
   - 上一轮 4 条 target_full 微缓冲
   都更接近可保留的 train-side mirror

## 当前默认下一步

默认顺序继续收紧为：

1. 若继续在 active split
   保留 bridge 方向资产，
   当前默认核心改成：
   - core trio
     `{train_000597, train_001599, val_000430}`
2. `train_001843`
   继续单独保留为：
   - target_full 微缓冲的 carry-over
   不再并入 core。
3. 后续若还要继续追 train-side 镜像，
   默认优先围绕：
   - 为什么两条 train row
     都只差：
     - `v64 > v67`
   这一个 shared leak
   去看；
   不再回到更宽的 mixed buffer。
4. 仍不启动新训练。
