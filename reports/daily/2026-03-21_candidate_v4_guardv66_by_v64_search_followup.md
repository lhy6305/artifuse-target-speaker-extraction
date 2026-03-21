# 2026-03-21 `candidate_v4_guardv66_by_v64` search follow-up

## 背景

上一轮已经确认：

- `v66`
  在 `candidate_v3_guardv20`
  上不是没学到方向；
- 问题更像：
  - `candidate_v3`
    aggregate 正向，
  - 但 row-level 仍不够硬，
    还没真正闭环 real `0004`

所以这轮默认不直接开新训练，
而是继续在
`val_manifest_friend_speech_leak_search_v1.jsonl`
上做 follow-up 搜索，
目标改成：

- 找一条更直接区分
  `v64 / v66`
  的新 family
- 同时尽量保留
  当前还站得住的旧排序约束

## 本轮对照

先做了三组搜索：

1. 原搜索约束
   再加：
   - `v32 > v66`
2. 原搜索约束
   再加：
   - `v64 > v66`
3. 原搜索约束
   再加：
   - `v32 > v66`
   - `v64 > v66`

结论很快收敛：

- `v32 > v66`
  这条线没有给出
  有价值的新 family；
- `v64 > v66`
  才是当前更有信息量的 guard

但第一轮 `v64 > v66`
  top near-miss
  仍卡在：

- `v25 > v24`

于是继续做第二层对照：

1. 直接放掉：
   - `v25 > v24`
2. 保留：
   - `v35 > v25 > v24`
   - `v20 > v24`
   - `v64 > v66`
   只放掉：
   - `v20 > v65`

## 为什么没选“放掉 `v25 > v24`”

这条路线虽然能得到 order-pass family，
但它明显退回：

- 更高 gain
- 更高 target transient

对应 val `9` 条 rows aggregate 为：

- `v35 = +0.346875 dB`
- `v20 = +0.214014 dB`
- `v65 = +0.198172 dB`
- `v64 = +0.056567 dB`
- `v66 = +0.006272 dB`
- `v25 = -0.001659 dB`

这更像旧 strong-transient 家族，
不是当前要找的
`0004-like speech_leak` proxy。

所以这条线不升格。

## 选中的新 family

保留：

- `v35 > v25 > v24`
- `v20 > v24`
- `v64 > v66`

只放掉：

- `v20 > v65`

之后，
得到一条新的 order-pass family，
当前命名为：

- `candidate_v4_guardv66_by_v64`

val `10` 条 rows 为：

- `val_000034`
- `val_000041`
- `val_000076`
- `val_000165`
- `val_000202`
- `val_000223`
- `val_000274`
- `val_000365`
- `val_000401`
- `val_000469`

builder 语义收敛为：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.75`
- `speech_interference_clean_pool`
- `interference_transient_presence_minus_mid_db_mean >= 4.159853935241699`
- `target_interference_logspec_cosine >= 0.5872839093208313`

## 已物化资产

本轮已正式生成：

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 33`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 10`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_val.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_all.txt`

selector builder 摘要：

- train `33`
- val `10`
- all `43`

## 当前诊断

已补定点 summary：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_guardv66_by_v64_direction_analysis/summary.json`

在这 `10` 条 val rows 上，
aggregate 排名为：

- `v64 > v66 > v65 > baseline > v20 > v30 > v32 > v35 > v29 > v25 > v24`

若只看 learned checkpoints，
则是：

- `v64 > v66 > v65 > v20 > v30 > v32 > v35 > v29 > v25 > v24`

关键 gap：

- `v64 - v66 = +0.003908 dB`
- `v66 - v65 = +0.015052 dB`
- `v20 - v24 = +0.044266 dB`

保留约束：

- `v35 > v25 > v24`
- `v20 > v24`

aggregate 上都成立。

row-level 仍不硬，
但比 `candidate_v3`
更像专门区分
`v64 / v66` 的 family：

- strict samplewise order-pass = `2 / 10`
- `v20 > v24` samplewise = `4 / 10`
- `v66` rank mean = `3.7`
- `v66` rank histogram：
  - `1 x2`
  - `2 x3`
  - `3 x1`
  - `4 x1`
  - `5 x1`
  - `7 x1`
  - `10 x1`

## 与旧 family 的关系

与前三版 candidate 的 overlap：

- train vs `candidate_v1`：
  - `0`
- train vs `candidate_v2_guardv65`：
  - `0`
- train vs `candidate_v3_guardv20`：
  - `4`
  - `train_000219`
  - `train_000681`
  - `train_000999`
  - `train_001404`
- val vs `candidate_v1 / candidate_v2`：
  - 都是 `0`
- val vs `candidate_v3_guardv20`：
  - `1`
  - `val_000165`

与旧 exact family 的 overlap：

- train vs `v23 speech_leak exact`：
  - `1`
  - `train_001404`
- val vs `v23 speech_leak exact`：
  - `1`
  - `val_000165`

这说明：

- `candidate_v4`
  不是 `candidate_v1 / v2`
  的重命名；
- 也不是简单回退到
  `v23 exact`
  老 rows；
- 但它确实保留了一个
  `v23`
  的旧锚点，
  作为和历史 proxy
  的最小连接。

## 当前结论

1. `candidate_v3_guardv20`
   仍保留，
   但它现在更适合回答：
   - 训练有没有沿既有 working candidate
     把 aggregate 方向推正
2. 当前更适合继续细化
   `v64 / v66`
   分界面的新 working candidate
   已改成：
   - `candidate_v4_guardv66_by_v64`
3. 这条新 family
   仍不是正式训练入口，
   因为 row-level 还不够硬
4. 但如果下一步继续做
   `0004-like speech_leak`
   proxy 搜索，
   默认应优先沿：
   - `candidate_v4_guardv66_by_v64`
   继续，
   而不是再回到
   - 放掉 `v25 > v24`
     的高 transient 家族

## 追加推进：显式 `v64 > v66 > v65` 约束复核

本轮继续直接把目标写成：

- `v64 > v66 > v65`

并保留：

- `v35 > v25`
- `v25 > v24`
- `v20 > v24`

结果表明：

- top order-pass family
  仍然完全回到
  `candidate_v4_guardv66_by_v64`
  这同一批 `10` 条 val rows；
- 也就是说：
  - `candidate_v4`
    不是“还能继续被一个简单新约束
    再推一版”的中间态；
  - 它已经是当前这组
    aggregate 约束下的固定点

同时又补跑了 strict samplewise 版本：

- `require_samplewise_order_pass = true`

结果：

- top order-pass candidate = `0`

这说明当前真正卡住的
仍然不是 aggregate 排序定义，
而是：

- row-level 行为一致性

## 追加推进：训练覆盖率核对

只把 `candidate_v4`
  当 selector
  直接塞回当前训练线
  是不够的。

我直接核对了它和当前 active split 的 overlap：

- 当前 `v66`
  实际用的 train / val manifest 仍是：
  - `train_manifest_v42_v30_plus_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl`
  - `val_manifest_v42_v30_plus_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl`

`candidate_v4` 与 `v42` base split 的 overlap：

- train：
  - `1 / 33`
  - `train_000826`
- val：
  - `0 / 10`

与 `v65` union split 的 overlap
也仍很低：

- train：
  - `2 / 33`
  - `train_000826`
  - `train_001404`
- val：
  - `1 / 10`
  - `val_000165`

这意味着：

- 如果下一轮只是把
  `branch_protect_focus_sample_ids`
  从 `candidate_v3`
  换成 `candidate_v4`，
  但 train / val manifest
  仍沿用当前 `v42` split，
  那基本等于：
  - 训练根本吃不到
    这批新 rows

## 已补 union 资产

因此本轮已直接为下一轮训练准备
union manifest：

- `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
- `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`

merged 后规模为：

- train `161`
- val `47`

也就是说：

- 相对 `v42` base split，
  新增的基本就是
  `candidate_v4`
  这批 rows
- 后续如果真要用
  `candidate_v4`
  开 branch-protect 训练，
  默认不该只换 selector；
  而应直接基于这对 union manifest
  启动

## 当前更新后的默认判断

1. `candidate_v4_guardv66_by_v64`
   已经是当前
   `v64 > v66 > v65`
   aggregate 约束下的固定点，
   不再需要机械地再起一个
   `candidate_v5`
2. 当前真正的下一层阻塞
   不在搜索约束本身，
   而在：
   - row-level 仍不硬
   - 且当前 active split
     几乎不覆盖这批 rows
3. 若后续继续，
   默认前置动作应写成：
   - 用
     `train/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
     作为新训练 split
   - 再谈
     `branch_protect`
     是否真的吃到了
     `candidate_v4`
