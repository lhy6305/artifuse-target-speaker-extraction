# 2026-03-21 `candidate_v7` bridgepair active dual-leak shell neighbor drift

## 背景

上一轮已经确认：

- `core trio`
  `{train_000597, train_001599, val_000430}`
  仍是当前唯一可保留的
  bridge-like active core；
- 包住两条 train rows
  的更大 train-side 外壳
  不是单
  `v64 > v67`
  leak，
  而是：
  - `v64 > v67`
  - `v20 > v24`
  双漏
- 对应最小 shell 为：
  - `train_000597`
  - `train_001477`
  - `train_001599`
  - `train_000865`

但还差最后一个问题：

- 这条 dual-leak shell
  有没有可能继续往外长成
  一个稳定 family；
- 还是说它本身就只是
  一个 train-only 诊断壳层，
  一旦往外扩，
  就会立刻漂进更坏的
  mixed frontier。

## 本轮做法

### 1. 先把 dual-leak shell 正式物化成 train-only 资产

本轮新增：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell.jsonl = 4`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell.jsonl = 0`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_all.jsonl = 4`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_{train,val,all}.txt`

当前 shell 固定为：

- `train_000597`
- `train_001477`
- `train_001599`
- `train_000865`

### 2. 以 dual-leak shell 为 seed，重排 `active_targetfull_clean` 的 metadata 邻域

使用：

- `scripts/eval/analyze_manifest_seed_neighbors.py`

输出：

- `reports/eval/active_targetfull_clean_dualleak_shell_neighbor_analysis/summary.json`

### 3. 逐条核对最近邻的 failed-signature

再回到：

- `reports/eval/compare_v19_vs_v20_on_active_targetfull_clean/per_sample_metrics.jsonl`
- `reports/eval/compare_v19_vs_v24_on_active_targetfull_clean/per_sample_metrics.jsonl`
- `reports/eval/compare_v19_vs_v64_on_active_targetfull_clean/per_sample_metrics.jsonl`
- `reports/eval/compare_v19_vs_v65_on_active_targetfull_clean/per_sample_metrics.jsonl`
- `reports/eval/compare_v19_vs_v66_on_active_targetfull_clean/per_sample_metrics.jsonl`
- `reports/eval/compare_v19_vs_v67_on_active_targetfull_clean/per_sample_metrics.jsonl`

对 shell 最近邻逐条重算：

- `v66 > v64`
- `v66 > v65`
- `v66 > v67`
- `v64 > v67`
- `v20 > v24`

看看最近邻会不会继续停在
同一条 dual-leak signature 上。

## 结果

### 1. dual-leak shell 一往外扩，最近邻立刻漂进 mixed frontier；没有稳定的同签名外环

当前 shell seed
在 `active_targetfull_clean`
里的 top10 最近邻为：

1. `val_000376`
2. `val_000305`
3. `train_001181`
4. `val_000075`
5. `train_001494`
6. `train_001589`
7. `train_001079`
8. `train_000432`
9. `train_001219`
10. `train_001404`

也就是说：

- 最近邻前 `4` 名里
  已经有：
  - `3` 条 val
- 整个 top10
  也不是：
  - 更多同签名 dual-leak rows
  而是：
  - `v65` 单漏 / 多漏
  - `v67` 插队
  - `v64` 回到第一
  混在一起的 mixed frontier

所以：

- dual-leak shell
  不具备：
  - 再往外自然长成
    同壳层 family
    的邻域结构；
- 它更像：
  - 一条 train-only 局部诊断壳层
  - 一出壳就会掉进
    bridge / `v65` / `v67`
    混合边界。

### 2. 最近的几条邻居没有继续保持 dual-leak；它们会立刻分裂成三种更坏方向

当前前几条最近邻
及其 failed-signature 为：

- `val_000376`
  - distance `0.952598`
  - fail：
    - `v66 > v65`
  - top alias：
    - `v65`
- `val_000305`
  - distance `1.012006`
  - fail：
    - `v66 > v64`
    - `v66 > v65`
    - `v66 > v67`
    - `v64 > v67`
  - top alias：
    - `v67`
- `train_001181`
  - distance `1.032663`
  - fail：
    - `v66 > v64`
    - `v66 > v65`
    - `v66 > v67`
  - top alias：
    - `v64`
- `val_000075`
  - distance `1.094011`
  - fail：
    - `v66 > v64`
    - `v66 > v65`
    - `v66 > v67`
  - top alias：
    - `v65`
- `train_001494`
  - distance `1.109916`
  - fail：
    - `v66 > v67`
    - `v64 > v67`
    - `v20 > v24`
  - top alias：
    - `v67`
- `train_001589`
  - distance `1.154864`
  - fail：
    - `v66 > v65`
    - `v66 > v67`
    - `v64 > v67`
    - `v20 > v24`
  - top alias：
    - `v67`

这说明 dual-leak shell
最近邻并不会继续停在：

- `v64>v67 | v20>v24`

而是立刻裂成：

1. bridge/guardv65 支：
   - 例如 `val_000376`
2. `v67` 插队支：
   - 例如 `train_001494`
   - `train_001079`
   - `train_001589`
3. `v64` / `v65` 反向回顶支：
   - 例如 `train_001181`
   - `val_000075`
   - `train_000432`

所以：

- dual-leak shell
  不是可扩张中心；
- 一旦继续扩，
  它就会被周围这些
  更强的 mixed signatures
  吞掉。

### 3. 和更外层 mixed frontier 相比，dual-leak shell 其实就是一层“较干净但不可扩”的中间带

当前 strict-near-miss
里和 dual leak
最接近的更外层前沿有两类：

- `v66>v67 | v64>v67 | v20>v24`
  - `23` 条
- `v66>v65 | v66>v67 | v64>v67 | v20>v24`
  - `9` 条

把它们和 dual-leak shell
对比，差异很清楚：

#### dual-leak shell

- `target_transient_presence_minus_mid_db_mean = -13.018489`
- `target_transient_presence_share_mean = 0.014222`
- `interference_transient_presence_minus_mid_db_mean = +0.187193`
- `interference_transient_presence_share_mean = 0.315380`
- `target_interference_logspec_cosine = 0.738410`

#### `v66>v67 | v64>v67 | v20>v24`

- `target_transient_presence_minus_mid_db_mean = -10.274538`
- `target_transient_presence_share_mean = 0.051610`
- `interference_transient_presence_minus_mid_db_mean = +4.362651`
- `interference_transient_presence_share_mean = 0.427516`
- `target_interference_logspec_cosine = 0.616694`

#### anchor `core trio`

- `target_transient_presence_minus_mid_db_mean = -15.637557`
- `target_transient_presence_share_mean = 0.003706`
- `interference_transient_presence_minus_mid_db_mean = -2.168932`
- `interference_transient_presence_share_mean = 0.219087`
- `target_interference_logspec_cosine = 0.713781`

也就是说：

- `core trio`
  是最干净的一层；
- dual-leak shell
  是已经开始往外漂，
  但还没彻底坏掉的中间带；
- 再往外一层，
  就会迅速滑成：
  - 更高的 target share
  - 更高的 interference
  - 更低的 cosine
  的 `v67` / mixed frontier

所以 dual-leak shell
当前最准确的定位是：

- 不是新 family
- 不是 mirror 扩张
- 而是：
  - `core trio`
    与外层 mixed frontier
    之间的一层
    train-only diagnostic ring

### 4. dual-leak shell 本身也没有 val mirror

当前最小 dual-leak shell
只有 train rows：

- `train_000597`
- `train_001477`
- `train_001599`
- `train_000865`

而它的最近 val 邻居：

- `val_000376`
- `val_000305`
- `val_000075`

都已经不在
同一 dual-leak signature 上。

因此：

- 当前不能把 dual-leak shell
  继续解释成：
  - 只是还没找齐 val 行
    的半个 family
- 更合理的解释应是：
  - 这条壳层
    天生就是 train-only
    局部诊断层；
  - 一旦找 val mirror，
    行为就会立刻并入
    别的 frontier。

## 当前结论

1. `{train_000597, train_001477, train_001599, train_000865}`
   这条 dual-leak shell
   当前应正式固定为：
   - train-only diagnostic ring
   - 不是可扩张 family
   - 不是新的 mirror core
2. dual-leak shell
   的最近邻不会继续留在：
   - `v64>v67 | v20>v24`
   而会立刻裂成：
   - bridge/guardv65
   - `v67` 插队
   - `v64 / v65` 反向回顶
   三种 mixed frontier
3. 因而当前 bridge 方向里，
   真正还能保留的 active 资产
   仍只有：
   - `core trio`
     `{train_000597, train_001599, val_000430}`
4. dual-leak shell
   的意义只剩：
   - 帮助解释
     为什么 train 侧
     会一起漏：
     - `v64 > v67`
     - `v20 > v24`
   不再承担 family 扩张角色

## 当前默认下一步

默认顺序继续收紧为：

1. 若继续追
   active bridge
   的 train-side 结构，
   当前仍只围绕：
   - `core trio`
2. dual-leak shell
   只保留为：
   - train-only diagnostic ring
   不再从它继续做
   neighbor seed 扩张
3. 后续若还要继续推进，
   默认优先看：
   - 为什么
     `v64 > v67`
     与
     `v20 > v24`
     会在这层 train rows
     一起漏；
   而不是继续找
   “shell 的第四外环 / 第五外环”
4. 仍不启动新训练。
