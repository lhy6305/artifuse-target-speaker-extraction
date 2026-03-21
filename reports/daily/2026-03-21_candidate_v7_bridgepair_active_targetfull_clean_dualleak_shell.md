# 2026-03-21 `candidate_v7` bridgepair active targetfull clean dual-leak shell

## 背景

上一轮已经把
active split
里最小可保留的 bridge-like core
收窄到：

- `train_000597`
- `train_001599`
- `val_000430`

当时的口径是：

- 这条 core trio
  aggregate 上已经成立；
- train 侧两条
  只剩同一条 shared leak：
  - `v64 > v67`

但继续把它投回
`active_targetfull_clean`
这 `88` 条
workspace 后，
需要确认两件事：

1. 这两个 train rows
   周围是不是存在
   一个更大的
   `v64 > v67`
   单漏 train-side mirror；
2. 当前 `strict_near_miss`
   里出现的 all-pass rows
   能不能直接当成
   bridge core
   的继续扩张入口。

## 本轮做法

### 1. 先回到 `88` 条 `target_full clean` workspace 做 strict-near-miss 复盘

直接读取：

- `reports/eval/active_targetfull_clean_strict_nearmiss_analysis/summary.json`

重点看：

- `single_fail_constraint_summaries`
- `failed_signature_summaries`
- `all_constraints_pass_rows`

### 2. 修正 direction summary 的 fail 展示口径

本轮顺手发现：

- `scripts/eval/analyze_proxy_candidate_direction.py`

里原来的：

- `order_pass(...)`
- `extra_constraints_pass(...)`

都会在遇到第一条 fail 后
立刻提前返回；
这会导致：

- row-level 后续 failed guards
  被 summary 静默截断；
- 前一轮 core trio
  两条 train rows
  看起来像：
  - 只差 `v64 > v67`
  但实际上 raw compare 里
  还同时差：
  - `v20 > v24`

本轮已改成：

- 先把所有 constraint gap
  全部记下；
- 最后再统一返回
  overall pass / fail

并重跑：

- `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`

### 3. 把 dual-leak shell 单独物化并补跑 focused direction

本轮把包住
`train_000597`
与
`train_001599`
的最小同签名 train shell
写成：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_all.txt`

内容为：

- `train_000597`
- `train_001477`
- `train_001599`
- `train_000865`

然后在
`active_targetfull_clean`
compare 上补跑：

- `reports/eval/bridgepair_active_targetfull_clean_core_dualleak_shell_direction_analysis/summary.json`

### 4. 再补一层 metadata 邻域校对

为了区分：

- 行为上同签名的 train shell
和
- metadata 上真贴近 core trio
的邻域

又用：

- `scripts/eval/analyze_manifest_seed_neighbors.py`

把
`core trio`
在
`active_targetfull_clean`
上的 metadata 邻域重新排了一次，
输出为：

- `reports/eval/active_targetfull_clean_core_trio_neighbor_analysis/summary.json`

## 结果

### 1. 在 `88` 条 workspace 里，不存在纯 `v64 > v67` 单漏 train shell

当前 `single_fail_constraint_summaries`
只有三组：

- `v66 > v65`
  - `3` 条：
    - `val_000376`
    - `train_001225`
    - `val_000202`
- `v20 > v24`
  - `1` 条：
    - `val_000223`
- `v66 > v64`
  - `1` 条：
    - `train_000676`

也就是说：

- 原本以为
  `core trio`
  train 侧两条
  外面可能包着一个
  纯 `v64 > v67`
  单漏壳层；
- 但全量 workspace
  里实际上没有这种
  单漏 shell。

### 2. 真正包住 `597 / 1599` 的最小 train-side 壳层，是 `v64>v67 | v20>v24` dual leak

当前与
`train_000597`
、
`train_001599`
同签名的最小壳层是：

- `train_000597`
- `train_001477`
- `train_001599`
- `train_000865`

它们共同 fail：

- `v64 > v67`
- `v20 > v24`

这说明前一轮把
`core trio`
写成：

- shared train-side
  `v64 > v67` leak

还不够完整；
更准确的口径应升级为：

- shared train-side
  `v64 > v67 + v20 > v24`
  dual leak

### 3. 但这个 dual-leak shell 不能升级成新的 mirror core；一扩到 4 条，aggregate 排序就开始被 `v67 / v24` 插队

在这 `4` 条
train-only shell 上，
focused direction 为：

1. `v66`
2. `v67`
3. `v24`
4. `v64`
5. `baseline`
6. `v65`
7. `v20`

关键 aggregate gaps：

- `v66 > v64 = +0.129529 dB`
- `v66 > v65 = +0.175244 dB`
- `v66 > v67 = +0.050005 dB`
- `v64 > v67 = -0.079525 dB`
- `v20 > v24 = -0.105507 dB`

samplewise 状态更直接：

- `candidate rank = 1`
  在 `4 / 4`
  rows 上都成立；
- 但
  `samplewise extra pass = 0 / 4`

逐条看：

- `train_000597`
  - fail：
    - `v64 > v67`
    - `v20 > v24`
- `train_001477`
  - fail：
    - `v64 > v67`
    - `v20 > v24`
- `train_001599`
  - fail：
    - `v64 > v67`
    - `v20 > v24`
- `train_000865`
  - fail：
    - `v64 > v67`
    - `v20 > v24`

所以：

- 这 `4` 条
  当然不是
  row-level clean family；
- 甚至也不是
  比 `core trio`
  更干净的 train-side mirror；
- 更准确的定位应是：
  - train-only dual-leak shell
  - 用来说明：
    - `v66`
      领先这批 train rows
      并不难；
    - 真正难的是
      同时保住：
      - `v64 > v67`
      - `v20 > v24`

### 4. dual-leak shell 在 metadata 上也不紧；它不是 `core trio` 的自然邻域扩张

对
`core trio`
做 metadata 邻域排序后，
当前 top10 最近邻为：

1. `train_000432`
2. `val_000075`
3. `train_001219`
4. `train_001079`
5. `train_001494`
6. `train_001181`
7. `val_000331`
8. `train_000865`
9. `train_001225`
10. `train_000001`

而 dual-leak shell
内部两条新增 train rows
的 rank 分裂得很厉害：

- `train_000865`
  - metadata distance rank：
    - `8`
- `train_001477`
  - metadata distance rank：
    - `34`

这说明：

- dual-leak shell
  不是一个 metadata 上
  紧贴 core trio
  的外环；
- 它更像：
  - 行为上同签名，
  - 但几何上已经松开的
    train-only 壳层

### 5. 当前 all-pass rows 也不适合当 bridge 扩张入口；它们整体离 core trio 更远

`strict_near_miss`
里的 all-pass rows
当前为：

- `val_000430`
- `train_001827`
- `val_000239`
- `train_000588`

其中除 seed 本身
`val_000430`
外，
剩余三条相对
`core trio`
的 metadata 邻域 rank 为：

- `train_001827`
  - `67`
- `val_000239`
  - `69`
- `train_000588`
  - `79`

这和它们的 metadata
也一致：

- `train_001827`
  - `target_transient_presence_share_mean = 0.193119`
- `val_000239`
  - `target_transient_presence_minus_mid_db_mean = +0.631591`
- `train_000588`
  - `interference_transient_presence_minus_mid_db_mean = +10.705249`

而
`core trio`
anchor center
仍明显更偏：

- 更低的
  `target_transient_presence_share_mean`
- 更低的
  `interference_transient_presence_minus_mid_db_mean`

所以：

- all-pass rows
  说明的是：
  - `active_targetfull_clean`
    里还存在别的
    fully-pass frontier；
- 但它们并不是
  bridge core
  的自然继续扩张线。

## 当前结论

1. 前一轮 `core trio`
   train 侧 shared leak
   的正式口径应修正为：
   - 不是只差
     `v64 > v67`
   - 而是共同差：
     - `v64 > v67`
     - `v20 > v24`
2. 当前 `active_targetfull_clean`
   上最小能包住
   `train_000597`
   与
   `train_001599`
   的 train-only 壳层为：
   - `{train_000597, train_001477, train_001599, train_000865}`
   - 正式定位应写成：
     - dual-leak shell
     - 不是新的 mirror core
3. `core trio`
   仍是当前最小可保留的
   bridge-like active core：
   - `train_000597`
   - `train_001599`
   - `val_000430`
4. `strict_near_miss`
   里的其它 all-pass rows
   也不应继续当成
   bridge 方向扩张入口；
   它们整体已经偏到
   别的 fully-pass frontier。

## 当前默认下一步

默认顺序继续收紧为：

1. 若继续保留
   active split
   的 bridge 方向资产，
   当前唯一核心仍是：
   - `core trio`
     `{train_000597, train_001599, val_000430}`
2. `{train_000597, train_001477, train_001599, train_000865}`
   只保留为：
   - train-only dual-leak shell
   - 用于诊断：
     - `v64 > v67`
     - `v20 > v24`
     这两个旧 guard
     为什么会一起漏；
   不再把它升级成：
   - 新的 active microbuffer
   - 或新的 train-side mirror core
3. `train_001827 / val_000239 / train_000588`
   保留为：
   - 别的 fully-pass frontier
   不沿 bridge 方向继续解释
4. 仍不启动新训练。
