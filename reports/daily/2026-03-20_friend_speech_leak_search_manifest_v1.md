# 2026-03-20 friend speech-leak common search manifest v1

## 背景

`v64 / v65` 恢复后，当前下一步已经收敛成：

- 不是继续重跑 `v64 / v65`
- 也不是继续扫现有 `branch_protect` 权重
- 而是先重建真正对应 `speech_leak_like (0004)` 的新 selector / proxy

上一轮直接拿历史 compare report 喂
`scripts/eval/search_synthetic_proxy_candidates.py`
时，已经暴露出一个工程前置问题：

- 历史 `compare_v19_vs_v20 / v25 / ... on default`
  虽然名字都写着 `default`
- 但它们并不保证来自严格同一批 shared `sample_id`
- 因而搜索脚本会直接报：
  - `No shared speech-only rows found across compare inputs.`

所以这轮先不猜 proxy，
先做统一搜索底座。

## 新公共搜索 manifest

本轮先从 `data/synthetic/val_manifest.jsonl`
物化一份专门给 `0004-like speech_leak`
做多 checkpoint shared compare 的公共搜索集：

- `data/synthetic/val_manifest_friend_speech_leak_search_v1.jsonl`

过滤条件为：

- `recipe = target_clean_speech`
- `temporal_pattern = target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.75`
- `interference_pool = speech_interference_clean_pool`

实际规模：

- `val = 50`

这一步的目的不是宣称它已经是
“新的 `0004` proxy”，
而是先保证：

- 后续所有 compare
  都在同一批 `sample_id` 上
- 搜索脚本终于能稳定工作

## 统一 compare 结果

基于同一份
`val_manifest_friend_speech_leak_search_v1.jsonl`，
本轮已重跑：

- `v19 vs v20`
- `v19 vs v24`
- `v19 vs v25`
- `v19 vs v29`
- `v19 vs v30`
- `v19 vs v32`
- `v19 vs v35`
- `v19 vs v64`
- `v19 vs v65`

相对 `v19` 的平均 SI-SDR delta 为：

- `v35 = +0.246194 dB`
- `v65 = +0.197365 dB`
- `v25 = +0.162377 dB`
- `v24 = +0.073098 dB`
- `v64 = +0.053230 dB`
- `v29 = -0.005659 dB`
- `v32 = -0.083233 dB`
- `v30 = -0.098669 dB`
- `v20 = -0.255740 dB`

当前说明：

- 这 50 条 shared rows
  里确实已经存在一批
  更像 `speech_leak_like`
  的候选样本
- 但它们并不自动复现
  near-real `0004`
  的完整历史排序

最直接的反例是：

- `near_real_0004`
  历史上 `v20` 是前排
- 但在这份 shared search manifest 上，
  `v20` 反而最差

所以这份公共搜索 manifest
可以作为“搜索底座”，
但还不能直接等价成
“新的 `0004` 真 proxy”。

## 搜索结果

### 失败的顺序

先按更贴近
`near_real_0004`
旧排序的：

- `v20 > v35 > v25 > v24`

去跑 strict samplewise order-pass 搜索，
结果为：

- `0` 条 shared speech rows pass

这说明当前 50 条公共搜索底座里，
并不存在一批样本能同时稳定复现：

- `v20 > v35 > v25 > v24`

### 当前可站住的 working order

改成当前 shared search 底座里
真正能站住的顺序：

- `v35 > v25 > v24`

则 strict samplewise order-pass
可得到：

- `8` 条 shared speech rows

进一步跑 relaxed 搜索后，
当前最稳定的 top candidate
会收敛到同一类过滤条件：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`
- `speech_interference_clean_pool`
- `interference_gain_db >= -2.9865000247955322`
- `target_transient_presence_minus_mid_db_mean <= -10.191147327423096`
- `interference_transient_presence_minus_mid_db_mean <= 4.159853935241699`

对应 val candidate ids 为：

- `val_000182`
- `val_000331`
- `val_000430`

这 3 条样本上的完整排序为：

- `v35 = +3.279488 dB`
- `v25 = +1.830512 dB`
- `v65 = +1.443289 dB`
- `v24 = +0.238458 dB`
- `v29 = -0.297660 dB`
- `v64 = -1.536799 dB`
- `v32 = -2.128319 dB`
- `v30 = -2.445112 dB`
- `v20 = -4.555402 dB`

所以当前更准确的表述是：

- 已找到一族新的
  `high-overlap + higher-gain + low-target-transient + low-interference-transient`
  clean-speech candidate family
- 但它还不是
  near-real `0004`
  的完整行为复刻
- 因为：
  - `v20` 仍然方向不对
  - `v65` 仍然过强

## 物化后的 candidate manifest

基于上述 top candidate filters，
本轮已正式物化：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v1.jsonl = 12`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v1.jsonl = 3`

与旧 exact family 的 overlap 为：

- train vs `v23 speech_leak exact`：
  - overlap `2`
  - `train_001225`
  - `train_002042`
- train vs `v30 similarity_lowtransient_lowinttrans exact`：
  - overlap `1`
  - `train_001225`
- val vs `v23`：
  - overlap `0`
- val vs `v30`：
  - overlap `0`

这说明：

- 当前 candidate family
  不是 `v23 / v30`
  的简单重命名
- 至少在 val 侧，
  它是一组此前没有被旧 exact proxy
  真正覆盖到的新 rows

## 当前结论

1. `0004-like speech_leak`
   的下一步前置条件已经补齐：
   - 现在已有统一 shared `sample_id`
     的公共搜索 manifest
   - 不再依赖历史 compare report
     的偶然交集
2. 当前已经找出一组新的
   candidate filters，
   它们比 `v23minus`
   稍宽：
   - `train 12 / val 3`
3. 但这组 candidate
   还不能直接宣称是
   “新的真 `0004` proxy”；
   更准确地说，
   它是：
   - 下一轮继续搜索 / 加负约束
     时的可复用锚点
4. 下一步若继续，
   优先级应是：
   - 在这份公共搜索 manifest 上
     继续加入负约束，
     尤其避免：
     - `v65` 仍显著占优
     - `v20` 仍明显落后
   - 再决定是否把
     `candidate_v1`
     升格为正式 `branch_protect`
     proxy 资产

## 追加推进：负约束搜索

为避免后续继续靠手工肉眼筛掉
`v65` 这类伪阳性，
本轮已直接增强：

- `scripts/eval/search_synthetic_proxy_candidates.py`

新增能力：

- `--extra-order-constraint higher>lower`

作用：

- 在保留主 `ordered_aliases`
  的同时，
  再加入额外 aggregate 排序约束
- 适合表达：
  - “主候选顺序仍然成立”
  - 但某个已知错误方向的模型
    不能继续占优

### `v65` guard 结果

先测试：

- 主顺序：
  - `v35 > v25 > v24`
- 额外约束：
  - `v24 > v65`

在 strict samplewise order-pass 模式下，
结果为：

- `0` 个 top order-pass candidate

这说明：

- 当前那 8 条 strict pass rows 里，
  只要再要求
  `v24 > v65`，
  现有候选会全部掉空

改成 relaxed 搜索后，
当前 top guarded candidate
会收敛到：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`
- `speech_interference_clean_pool`
- `target_transient_presence_minus_mid_db_mean <= -10.191147327423096`
- `interference_transient_presence_minus_mid_db_mean <= 4.159853935241699`
- `target_interference_logspec_cosine >= 0.611259937286377`

已物化：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v2_guardv65.jsonl = 13`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v2_guardv65.jsonl = 3`

val ids 为：

- `val_000331`
- `val_000376`
- `val_000430`

与 `candidate_v1` 的关系：

- train：
  - overlap `8 / 12 / 13`
- val：
  - overlap `2 / 3 / 3`
  - `candidate_v1` 独有：
    - `val_000182`
  - `candidate_v2_guardv65` 独有：
    - `val_000376`

### 当前判断

这条 guarded candidate
比 `candidate_v1`
更干净：

- 不再依赖高 gain
- 也把 `v65` 从候选顶端压了下去

但它同时也更弱：

- 在这 3 条 val rows 上，
  各模型几乎都压成 near-tie
- 已不再是一条高辨识度 proxy

例如同一组 rows 上相对 `v19`：

- `v64 = +0.122681 dB`
- `v29 = +0.085519 dB`
- `v30 = +0.078702 dB`
- `v20 = +0.073521 dB`
- `v35 = +0.072778 dB`
- `v32 = +0.072402 dB`
- `v25 = +0.063059 dB`
- `v24 = +0.026916 dB`
- `v65 = +0.017790 dB`

所以当前更准确的结论是：

- `candidate_v2_guardv65`
  说明负约束方向是对的
- 但这版更像“剔除伪阳性后的 cleaner family”
  而不是已经足够尖锐的
  真 `0004` proxy

## 追加推进：`v20` 回拉约束

上一节已经说明：

- 单独压 `v65`
  会把 candidate
  清得更干净
- 但也会把模型差异压到 near-tie

所以本轮继续补了第二类约束：

- 不只是避免 `v65` 伪阳性
- 还要避免 `v20`
  在候选 family 里继续掉到后排

### 两组对照

本轮对比了两条 relaxed 搜索路线：

1. `v35 > v20 > v25`
   且
   `v20 > v65`
2. `v35 > v25 > v24`
   且
   `v20 > v24`

结果很明确：

- 第 1 条会把候选重新推回：
  - higher gain
  - higher target transient
  - higher interference transient
  的家族
- 语义上更像旧的强 transient family，
  不像当前要找的
  `speech_leak_like (0004)`

相反，
第 2 条会收敛到一组更像当前目标的 family：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`
- `speech_interference_clean_pool`
- `interference_gain_db >= -2.0026667118072514`
- `target_transient_presence_minus_mid_db_mean <= -10.191147327423096`
- `target_interference_logspec_cosine >= 0.611259937286377`

### 联合约束结果

进一步把两条负约束同时写进去：

- 主顺序：
  - `v35 > v25 > v24`
- 额外约束：
  - `v20 > v24`
  - `v20 > v65`

则：

- strict samplewise order-pass：
  - `0` 个 candidate
- relaxed 搜索：
  - top candidate
    与上面 `v20>v24` 路线完全一致

这说明：

- 当前 shared search 底座里，
  还没有一批 rows
  能在 samplewise strict 层面
  同时满足：
  - `v35 > v25 > v24`
  - `v20 > v24`
  - `v20 > v65`
- 但在 aggregate 层面，
  已经有一组更稳定的
  compromise candidate

## `candidate_v3_guardv20`

基于上述更稳定的 compromise candidate，
本轮已物化：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v3_guardv20.jsonl = 10`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v3_guardv20.jsonl = 3`

val ids 为：

- `val_000165`
- `val_000331`
- `val_000430`

这 3 条 val rows 上相对 `v19` 的均值为：

- `v35 = +0.106455 dB`
- `v20 = +0.099642 dB`
- `v30 = +0.086138 dB`
- `v32 = +0.082334 dB`
- `v29 = +0.079002 dB`
- `v64 = +0.120518 dB`
- `v25 = +0.055091 dB`
- `v65 = +0.050324 dB`
- `v24 = +0.028833 dB`

所以当前它的性质是：

- 比 `candidate_v2_guardv65`
  更有辨识度
- 比 `candidate_v1`
  更少受 `v65`
  伪阳性拖偏
- 同时重新接回了
  `v23 speech_leak exact`
  的一个旧 val 锚点：
  - `val_000165`

### 与旧 family / 新 family 的关系

与旧 exact family 的 overlap：

- train vs `v23 speech_leak exact`：
  - `2`
  - `train_001225`
  - `train_001404`
- train vs `v30 exact`：
  - `1`
  - `train_001225`
- val vs `v23`：
  - `1`
  - `val_000165`
- val vs `v30`：
  - `0`

与前两版 candidate 的 overlap：

- train vs `candidate_v1`：
  - `6`
- train vs `candidate_v2_guardv65`：
  - `6`
- val vs `candidate_v1`：
  - `2`
  - 共享：
    - `val_000331`
    - `val_000430`
- val vs `candidate_v2_guardv65`：
  - `2`
  - 共享：
    - `val_000331`
    - `val_000430`

### 当前结论更新

当前三条 candidate 的排序应写成：

1. `candidate_v3_guardv20`
   - 当前最可继续细化的 working candidate
2. `candidate_v2_guardv65`
   - cleaner 但过弱
3. `candidate_v1`
   - 辨识度更高
     但更容易混入 `v65` 伪阳性

但即便如此，
`candidate_v3_guardv20`
现在也仍然只是：

- 当前最佳 `candidate`

而不是：

- 已确认的真 `0004` proxy

因为：

- strict samplewise order-pass
  仍然掉空
- 这说明当前 shared manifest
  里的这组 rows
  还没有形成足够硬的
  row-level 行为一致性

## 标准 selector 资产

为避免下一步继续从 manifest
手抄 sample ids，
本轮已直接用：

- `scripts/data/build_branch_protect_selector_assets.py`

把 `candidate_v3_guardv20`
物化成标准 selector 资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_val.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_all.txt`

规模为：

- train `10`
- val `3`
- all `13`

这意味着下一步如果要：

- 接 `focus_sample_ids`
- 接 branch-protect selector
- 或继续做 union-manifest probe

都已经不需要再从
`candidate_v3_guardv20` manifest
手动抽 ids。
