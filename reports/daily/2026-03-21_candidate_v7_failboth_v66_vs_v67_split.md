# 2026-03-21 `candidate_v7` fail-both `v66` vs `v67` split

## 背景

上一轮已经把
`active_targetfull_clean`
里共同 fail：

- `v64 > v67`
- `v20 > v24`

的 `fail_both` 大桶
切出来，
并确认：

- 这 `43` 条里，
  只有 `4` 条
  仍保持：
  - `v66` top
- 另外 `34` 条
  已经滑到：
  - `v67` top

这一步已经说明：

- dual-leak shell
  不是 `fail_both`
  大桶里随手挑出来的样本；
- 它是这条大桶里
  唯一还没有被
  `v67`
  完全压过去的
  小核。

但还差最后一个问题：

- 这 `4` 条
  和那 `34` 条
  到底差在哪；
- 为什么两边都属于
  `fail_both`，
  却只有前者还能保住
  `v66-top`。

## 本轮做法

### 1. 把 `fail_both` 里的 `v66-top / v67-top` 正式物化成两组资产

基于：

- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_top_alias_split/summary.json`

本轮新增：

#### `v66-top`

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66.jsonl = 4`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66.jsonl = 0`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66_all.jsonl = 4`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66_{train,val,all}.txt`

当前固定为：

- `train_000597`
- `train_000865`
- `train_001477`
- `train_001599`

#### `v67-top`

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67.jsonl = 28`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67.jsonl = 6`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67_all.jsonl = 34`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67_{train,val,all}.txt`

### 2. 对两组分别补 focused direction

输出：

- `reports/eval/active_targetfull_clean_failboth_topv66_direction_analysis/summary.json`
- `reports/eval/active_targetfull_clean_failboth_topv67_direction_analysis/summary.json`

### 3. 再对整个 `fail_both` 大桶做 subgroup split

使用：

- `scripts/eval/analyze_proxy_candidate_subgroups.py`

输出：

- `reports/eval/active_targetfull_clean_failboth_subgroup_analysis/summary.json`

重点看：

- `v66 - v67`
- `v66 - v65`
- `v66 - v64`

在各个 numeric fields
上做 median split
后的变化。

### 4. 补一份直接均值对照 summary

输出：

- `reports/eval/active_targetfull_clean_failboth_topv66_vs_topv67_analysis/summary.json`

## 结果

### 1. `v66-top 4` 和 `v67-top 34` 最大的分界，不是 `v66 > v64`，而是 `v67` 有没有把 `v66` 彻底压过去

#### `v66-top 4`

aggregate 排序：

1. `v66`
2. `v67`
3. `v24`
4. `v64`
5. `baseline`
6. `v65`
7. `v20`

关键 gaps：

- `v66 > v64 = +0.129529 dB`
- `v66 > v65 = +0.175244 dB`
- `v66 > v67 = +0.050005 dB`
- `v64 > v67 = -0.079525 dB`
- `v20 > v24 = -0.105507 dB`

#### `v67-top 34`

aggregate 排序：

1. `v67`
2. `v65`
3. `v66`
4. `v24`
5. `baseline`
6. `v64`
7. `v20`

关键 gaps：

- `v66 > v64 = +0.187917 dB`
- `v66 > v65 = -0.069366 dB`
- `v66 > v67 = -0.296784 dB`
- `v64 > v67 = -0.484701 dB`
- `v20 > v24 = -0.523036 dB`

这里最重要的事实是：

- `v67-top 34`
  的
  `v66 > v64`
  反而更强正；
- 也就是说，
  真正把两边分开的
  不是：
  - `v66`
    能不能压住
    `v64`
- 而是：
  - `v67`
    有没有把
    `v66`
    彻底反超

所以：

- dual-leak shell
  的特殊性
  不是：
  - 它的 `v66-v64`
    特别大
- 而是：
  - 它还能把
    `v67`
    压在
    贴身第二；
  - 外层那 `34` 条
    则已经完全切换成：
    - `v67` 主导前沿

### 2. `v66-top 4` 在 metadata 上明显更“低 transient / 低 interference / 高 cosine”

直接均值对照：

#### `v66-top 4`

- 全部是：
  - `train`
  - `4 / 4`
- numeric means：
  - `target_transient_presence_minus_mid_db_mean = -13.018489`
  - `target_transient_presence_share_mean = 0.014222`
  - `interference_transient_presence_minus_mid_db_mean = +0.187193`
  - `interference_transient_presence_share_mean = 0.315380`
  - `target_interference_logspec_cosine = 0.738410`

#### `v67-top 34`

- `train = 28`
- `val = 6`
- numeric means：
  - `target_transient_presence_minus_mid_db_mean = -11.392187`
  - `target_transient_presence_share_mean = 0.047677`
  - `interference_transient_presence_minus_mid_db_mean = +4.553607`
  - `interference_transient_presence_share_mean = 0.422509`
  - `target_interference_logspec_cosine = 0.618595`

也就是：

- `v66-top 4`
  相对 `v67-top 34`
  更偏：
  - 更低的
    target transient
  - 更低的
    target share
  - 更低的
    interference transient
  - 更低的
    interference share
  - 更高的
    target / interference cosine

直接均值差
`v66-top - v67-top`
为：

- `target_transient_presence_minus_mid_db_mean = -1.626303`
- `target_transient_presence_share_mean = -0.033455`
- `interference_transient_presence_minus_mid_db_mean = -4.366413`
- `interference_transient_presence_share_mean = -0.107130`
- `target_interference_logspec_cosine = +0.119815`

所以：

- dual-leak shell
  当前仍保住
  `v66-top`
  的最合理解释是：
  - 它更像一层
    低 transient /
    低 interference /
    高相似度
    的 train-only 内核；
- 一旦这些量往外升，
  `v67`
  就会更容易接管排序。

### 3. subgroup split 进一步证明：`v66-v67` 的崩塌主要跟“字段往外变大”一起发生

在整个 `fail_both`
大桶里做 median split 后，
对
`v66 - v67`
最敏感的字段，
几乎方向一致：

#### 按 `target_transient_presence_share_mean`

- low half：
  - `v66 - v67 = -0.380999 dB`
- high half：
  - `v66 - v67 = -0.078546 dB`

#### 按 `interference_transient_presence_minus_mid_db_mean`

- low half：
  - `v66 - v67 = -0.358721 dB`
- high half：
  - `v66 - v67 = -0.101886 dB`

#### 按 `interference_transient_presence_share_mean`

- low half：
  - `v66 - v67 = -0.345423 dB`
- high half：
  - `v66 - v67 = -0.115817 dB`

#### 按 `target_interference_logspec_cosine`

- low half：
  - `v66 - v67 = -0.359032 dB`
- high half：
  - `v66 - v67 = -0.101560 dB`

这层结果说明：

- 在 `fail_both`
  大桶内部，
  `v66-v67`
  的差异
  不是靠某一个字段
  单独决定；
- 它更像是：
  - 一组字段
    同时把 row
    推向更外层 mixed frontier；
- 而 dual-leak shell
  恰好是这条大桶里
  还没被这股趋势
  完全推走的
  最内层 `v66-top` 小核

### 4. `v66-top 4` 依然没有 val mirror；这进一步说明它是 train-only 内核，不是待补齐的 family

当前：

- `v66-top 4`
  全部是：
  - `train`
- `v67-top 34`
  才开始混入：
  - `6` 条 val

也就是说：

- 只要开始出现 val mirror，
  当前这条 fail-both
  前沿就已经大概率
  不是：
  - `v66-top` 的继续扩张
- 而是：
  - `v67-top`
    mixed frontier

这和之前 dual-leak shell
做邻域扩张时
看到的现象一致：

- 一旦往外长，
  val 行会先接进来；
- 但它们接进来的同时，
  也会把排序带到：
  - `v67`
    主导

## 当前结论

1. `fail_both` 内部真正值得保留的，
   只有：
   - `v66-top 4`
   也就是当前 dual-leak shell
2. `v67-top 34`
   不是 dual-leak shell
   的外环 family；
   它已经是：
   - `v67`
     主导的外层 mixed frontier
3. `v66-top 4`
   能保住：
   - `v66-top`
   的关键，
   不在于：
   - `v66 > v64`
     特别强
   而在于：
   - 它还没让
     `v67`
     完全接管排序
4. 这 `4` 条
   在 metadata 上
   共同表现为：
   - 更低的
     target transient / share
   - 更低的
     interference transient / share
   - 更高的
     target-interference cosine
   - 且完全没有 val mirror
5. 因而当前应把
   dual-leak shell
   正式固定为：
   - train-only inner diagnostic core
   而不是：
   - 等 val 补齐的半个 family

## 当前默认下一步

默认顺序继续收紧为：

1. active bridge
   这条线，
   当前只保留：
   - `core trio`
   - dual-leak shell
2. dual-leak shell
   的正式解释
   更新为：
   - `fail_both`
     大桶里唯一仍是
     `v66-top`
     的 train-only inner core
3. 若后续还继续推进，
   默认优先看：
   - dual-leak shell
     和
     `v67-top 34`
     在更细 metadata /
     音频案例上
     是否存在可解释的
     单一声学触发因子；
   不再继续把
   `v67-top 34`
   当成 bridge family 外环
4. 仍不启动新训练。
