# 2026-03-21 `candidate_v7` fail-both single-trigger scan

## 背景

上一轮已经把
`fail_both`
大桶内部拆成：

- `v66-top 4`
  即 dual-leak shell
- `v67-top 34`
  即外层 mixed frontier

并确认：

- 两边真正的分界
  不是：
  - `v66 > v64`
  而是：
  - `v67`
    有没有把
    `v66`
    完全接管

但还差最后一个更细的问题：

- 这种分界
  能不能被一个单独的
  metadata 字段阈值
  直接解释；
- 还是说它已经明确属于
  多因子共驱动，
  不存在单触发阈值。

## 本轮做法

### 1. 对 `v66-top 4` vs `v67-top 34` 做单字段阈值扫描

输入：

- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_top_alias_split/summary.json`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_all.jsonl`

当前扫描字段：

- `target_transient_presence_minus_mid_db_mean`
- `target_transient_presence_share_mean`
- `interference_transient_presence_minus_mid_db_mean`
- `interference_transient_presence_share_mean`
- `target_interference_logspec_cosine`

输出：

- `reports/eval/active_targetfull_clean_failboth_single_field_trigger_scan/summary.json`

### 2. 两种口径同时记录

对每个字段同时算：

1. `best_balanced_accuracy`
   - 避免被
     `4 vs 34`
     的类不平衡带偏
2. `best_full_v66_recall`
   - 要求：
     - `4 / 4`
       dual-leak shell
       全覆盖
   - 再看会误收多少
     `v67-top`

### 3. 再补 persistent false-positive 名单

统计：

- 哪些 `v67-top`
  rows
  会在多个字段的
  `best_full_v66_recall`
  阈值下
  反复被误收进来

## 结果

### 1. 当前不存在能把 `v66-top 4` 和 `v67-top 34` 一刀切开的单字段阈值

当前五个字段里，
即使要求：

- `4 / 4`
  `v66-top`
  全部保留

最强的单字段也仍会误收
明显数量的 `v67-top`：

#### 最强字段 1：
`interference_transient_presence_minus_mid_db_mean`

- 阈值：
  - `<= 2.428970`
- `balanced_accuracy = 0.897059`
- `recall_v66 = 1.0`
- `specificity_vs_v67 = 0.794118`
- 仍会误收：
  - `7` 条 `v67-top`
    - `train_000210`
    - `train_000697`
    - `train_000904`
    - `train_000951`
    - `train_001079`
    - `train_001494`
    - `val_000182`

#### 最强字段 2：
`target_interference_logspec_cosine`

- 阈值：
  - `>= 0.671519`
- `balanced_accuracy = 0.882353`
- `recall_v66 = 1.0`
- `specificity_vs_v67 = 0.764706`
- 仍会误收：
  - `8` 条 `v67-top`
    - `train_000219`
    - `train_000266`
    - `train_000999`
    - `train_001006`
    - `train_001079`
    - `train_001494`
    - `train_001589`
    - `train_001639`

#### 其它字段更差

- `interference_transient_presence_share_mean`
  - 误收：
    - `12` 条
- `target_transient_presence_share_mean`
  - 误收：
    - `20` 条
- `target_transient_presence_minus_mid_db_mean`
  - 若强行保住
    - `4 / 4`
      `v66-top`
    - 会误收：
      - `24` 条

所以：

- 当前最强的单字段
  也只能做到：
  - 大致把 dual-leak shell
    缩到一个较窄的候选带
- 但远远不够把它
  和 `v67-top 34`
  完全分开

### 2. 这条线已经可以正式定性成“多因子共驱动”，不是单 trigger

因为：

- 最好的单字段
  也必须容忍：
  - `7 ~ 8`
    条 `v67-top`
    假阳性
- 而且不同字段
  漏进来的边界样本
  还并不完全相同

这说明：

- dual-leak shell
  并不是靠某一个
  单独 metadata 条件
  被保护住；
- 更准确的解释是：
  - 一组条件
    一起把 row
    维持在：
    - 低 transient
    - 低 interference
    - 较高 cosine
    的内核状态
- 只要这组条件
  有几项一起往外漂，
  排序就会切到：
  - `v67-top`

### 3. 持续伪装成 `v66-top` 的边界样本也很稳定，说明外层 frontier 内部还有一条“近内核边界带”

按
`best_full_v66_recall`
阈值统计，
当前最常反复被误收的
`v67-top`
边界样本为：

- `train_001079`
  - 命中：
    - `5 / 5`
      字段阈值
- `train_001494`
  - 命中：
    - `5 / 5`
- `train_000697`
  - 命中：
    - `4 / 5`
- `train_001589`
  - 命中：
    - `4 / 5`
- `val_000182`
  - 命中：
    - `4 / 5`

这组样本的意义是：

- 它们虽然已经属于
  `v67-top`
  外层，
  但在多项 metadata 上
  仍保留了较强的
  dual-leak shell
  外观；
- 也就是说，
  当前真正存在的
  不只是：
  - 内核 `4`
  和
  - 外层 `34`
  两层
- 在两者之间，
  还存在一条
  容易伪装成内核的
  borderline band

但当前更关键的是：

- 这条 borderline band
  仍然已经是：
  - `v67-top`
  而不是：
  - `v66-top`
- 所以它不能被回写成
  bridge family
  的可保留外环

## 当前结论

1. 当前没有任何一个
   单独 metadata 字段
   可以把：
   - dual-leak shell
   和：
   - `v67-top 34`
   完整分开
2. 当前最强单字段是：
   - `interference_transient_presence_minus_mid_db_mean`
   和：
   - `target_interference_logspec_cosine`
   但它们仍分别会误收：
   - `7`
   - `8`
     条 `v67-top`
3. 因而这条线当前应正式定性为：
   - multi-factor co-driven split
   不是：
   - single-trigger threshold split
4. `train_001079`
   和
   `train_001494`
   当前是最典型的
   persistent borderline rows；
   它们可保留为：
   - 外层近内核边界样本
   但不能回写成
   dual-leak shell
   成员

## 当前默认下一步

默认顺序继续收紧为：

1. 不再继续找
   “某一个单字段阈值”
   来解释 dual-leak shell
2. 若还继续推进，
   默认优先围绕：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   - `train_001589`
   - `val_000182`
   这组 persistent borderline rows
   做更细的个例诊断
3. 当前 bridge active
   主体解释保持不变：
   - `core trio`
     = 唯一可保留 active core
   - dual-leak shell
     = `fail_both` 大桶里
       唯一仍是 `v66-top`
       的 train-only inner core
   - `v67-top 34`
     = 外层 mixed frontier
4. 仍不启动新训练。
