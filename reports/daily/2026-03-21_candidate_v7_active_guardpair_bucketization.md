# 2026-03-21 `candidate_v7` active guard-pair bucketization

## 背景

上一轮已经把
active bridge
这条线收成两层：

- `core trio`
  `{train_000597, train_001599, val_000430}`
- dual-leak shell
  `{train_000597, train_001477, train_001599, train_000865}`

并确认：

- dual-leak shell
  不是可扩张 family，
  而只是
  `core trio`
  外侧一层
  train-only diagnostic ring

接下来需要回答的是：

- 这两条旧 guard
  `v64 > v67`
  和
  `v20 > v24`
  在全量
  `active_targetfull_clean`
  workspace 里
  到底怎么分桶；
- 哪一桶
  真正包住
  `core trio / dual-leak shell`；
- 哪几桶
  只是别的 frontier，
  不该再沿 bridge
  继续解释。

## 本轮做法

### 1. 新增 guard-pair 分桶脚本

本轮补了：

- `scripts/eval/analyze_proxy_constraint_pair_buckets.py`

作用是：

- 对共享 compare rows
  按两条指定约束的
  pass / fail 组合
  直接切成 `4` 个标准桶：
  - `pass_both`
  - `fail_a_only`
  - `fail_b_only`
  - `fail_both`
- 同时自动物化：
  - train / val / all manifests
  - train / val / all sample-id 文件
  - bucket summary json

### 2. 在 `active_targetfull_clean` 上实际分桶

输入：

- manifest：
  - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_with_metrics_all.jsonl`
- compares：
  - `reports/eval/compare_v19_vs_v20_on_active_targetfull_clean/per_sample_metrics.jsonl`
  - `reports/eval/compare_v19_vs_v24_on_active_targetfull_clean/per_sample_metrics.jsonl`
  - `reports/eval/compare_v19_vs_v64_on_active_targetfull_clean/per_sample_metrics.jsonl`
  - `reports/eval/compare_v19_vs_v65_on_active_targetfull_clean/per_sample_metrics.jsonl`
  - `reports/eval/compare_v19_vs_v66_on_active_targetfull_clean/per_sample_metrics.jsonl`
  - `reports/eval/compare_v19_vs_v67_on_active_targetfull_clean/per_sample_metrics.jsonl`

两条 guard：

- A：
  - `v64 > v67`
- B：
  - `v20 > v24`

输出 summary：

- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_bucket_analysis/summary.json`

同时物化 bucket manifests / ids：

- `data/synthetic/*friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_guardpair_v64gtv67_v20gtv24*`

### 3. 对四个桶分别补 focused direction

输出：

- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_pass_both_direction_analysis/summary.json`
- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_a_only_direction_analysis/summary.json`
- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_b_only_direction_analysis/summary.json`
- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_direction_analysis/summary.json`

### 4. 再把 `fail_both` 按 top alias 快速拆开

为了确认：

- dual-leak shell
  是否只是
  `fail_both`
  里的一小簇 `v66-top` row

又补了：

- `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_top_alias_split/summary.json`

## 结果

### 1. guard-pair 四桶数量分布很不均衡，最大桶是 `fail_both`

当前 `88` 条 workspace
按：

- `v64 > v67`
- `v20 > v24`

切完以后得到：

- `pass_both = 18`
- `fail_a_only = 20`
- `fail_b_only = 7`
- `fail_both = 43`

也就是说：

- 真正同时漏掉
  这两条 guard 的 rows
  接近一半；
- 这也解释了为什么前面
  只靠 `core trio`
  或 dual-leak shell
  往外扩时，
  很容易很快掉进
  更大的 mixed frontier。

### 2. `pass_both` 并不等于 bridge-friendly；这桶整体反而是 `v65` 顶

`pass_both`
方向汇总显示：

- aggregate 排序：
  - `v65 > v64 > v20 > v66 > baseline > v67 > v24`
- `v66 > v64 = -0.037591 dB`
- `v66 > v65 = -0.059018 dB`
- `samplewise extra pass = 5 / 18`

更关键的是：

- `core trio`
  与这桶
  的 overlap
  只有：
  - `val_000430`
- dual-leak shell
  与这桶
  overlap：
  - `0`

所以：

- “两条旧 guard 都过了”
  并不意味着
  这批 rows
  更接近 bridge active core；
- 在当前 workspace
  里，
  `pass_both`
  反而更像一批
  已经整体滑向：
  - `v65`
  - `v64`
  一侧的别的 frontier。

### 3. `fail_a_only` 和 `fail_b_only` 也都不是 bridge 方向入口

#### `fail_a_only = 20`

这里只差：

- `v64 > v67`

但 aggregate 排序却是：

- `v67 > v65 > v66 > v64 > v20 > baseline > v24`

关键 gap：

- `v66 > v64 = +0.038151 dB`
- `v66 > v67 = -0.169243 dB`
- `v66 > v65 = -0.005863 dB`

这桶里含有：

- `val_000331`
- `val_000305`
- `val_000365`

也就是：

- 一看就是
  `v67` 插队 / mixed boundary
  更重的一层，
  不是新的 bridge shell。

#### `fail_b_only = 7`

这里只差：

- `v20 > v24`

但 aggregate 排序是：

- `v64 > v66 > v67 > baseline > v65 > v24 > v20`

关键 gap：

- `v66 > v64 = -0.066802 dB`
- `v20 > v24 = -0.061014 dB`

这桶典型成员有：

- `val_000223`
- `val_000274`
- `val_000401`
- `val_000469`

也就是：

- 典型的
  legacy `guardv20`
  未对齐分支；
- 它和当前 bridge active
  也不是同一条解释线。

### 4. `fail_both` 才是真正包住 train-side bridge 诊断层的大桶，但它本身太粗，整体已经塌成 `v67` 前沿

`fail_both`
是最大的桶：

- `43` 条
  其中：
  - train `37`
  - val `6`

aggregate 方向：

- `v67 > v65 > v66 > v24 > baseline > v64 > v20`
- `v66 > v64 = +0.162575 dB`
- `v66 > v67 = -0.233290 dB`
- `v64 > v67 = -0.395865 dB`
- `v20 > v24 = -0.426840 dB`
- `samplewise extra pass = 0 / 43`

membership 上：

- `core trio`
  与这桶 overlap：
  - `train_000597`
  - `train_001599`
- dual-leak shell
  与这桶 overlap：
  - `train_000597`
  - `train_001477`
  - `train_001599`
  - `train_000865`

也就是说：

- 真正包住
  train-side bridge 诊断层的，
  的确就是这桶；
- 但这桶整体已经太粗，
  不能直接拿来当
  新 family
  或新 active buffer。

### 5. `fail_both` 里唯一还保持 `v66` 第一的，恰好只有 dual-leak shell 这 4 条

按 top alias
再拆 `fail_both`，
结果非常干净：

- `v67` top：
  - `34`
- `v65` top：
  - `4`
- `v66` top：
  - `4`
- `v24` top：
  - `1`

而这 `4` 条
`v66-top`
rows
正好就是：

- `train_000597`
- `train_001477`
- `train_001599`
- `train_000865`

也就是当前 dual-leak shell
本身。

这条结果很关键，
因为它说明：

- pair-bucketization
  没有发现
  一个比 dual-leak shell
  更大的
  `v66-top`
  fail-both core；
- 恰恰相反，
  它只是把事实再次钉死：
  - dual-leak shell
    就是 `fail_both`
    里仅存的
    `v66-top` 小核
  - 外面剩下的大多数 rows
    已经全部滑到：
    - `v67`
    - `v65`
    - 或更坏的 mixed frontier

## 当前结论

1. `v64 > v67 / v20 > v24`
   这对 guard
   做成四桶以后，
   并没有长出新的 bridge family；
   只是在全量 workspace 上
   更清楚地重现了：
   - `core trio`
   - dual-leak shell
   - 外层 mixed frontier
   这三层结构
2. `pass_both`
   不能再被误当成
   “更干净的 bridge 候选”，
   因为它整体已经塌成：
   - `v65 > v64 > v20 > v66`
3. `fail_a_only`
   本质更接近：
   - `v67` 插队层
4. `fail_b_only`
   本质更接近：
   - legacy `guardv20`
     分支
5. 真正包住
   train-side bridge
   诊断层的
   仍只有：
   - `fail_both`
   这一大桶；
   但它内部唯一仍能保持
   `v66-top`
   的，
   恰好还是：
   - dual-leak shell
     `4` 条
6. 因而当前 active bridge
   这条线已经基本收死：
   - `core trio`
     是唯一可保留的
     active core
   - dual-leak shell
     是唯一可保留的
     train-only diagnostic ring
   - 四桶本身都不再承担
     family 扩张角色

## 当前默认下一步

默认顺序继续收紧为：

1. 不再继续从：
   - `pass_both`
   - `fail_a_only`
   - `fail_b_only`
   - `fail_both`
   这四桶
   直接找新 family
2. 若继续追
   active bridge
   的机理诊断，
   默认只保留两层资产：
   - `core trio`
   - dual-leak shell
3. 后续若还继续推进，
   默认优先看：
   - 为什么
     `fail_both`
     里只有这 `4` 条
     还能保持 `v66-top`
   - 以及它们和
     `fail_both`
     中那 `34` 条
     `v67-top` rows
     的差异
4. 仍不启动新训练。
