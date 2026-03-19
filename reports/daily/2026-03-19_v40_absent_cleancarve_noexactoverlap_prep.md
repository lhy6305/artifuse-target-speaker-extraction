# 2026-03-19 `v40` absent cleancarve no-exact-overlap prep

## 背景

`v39` 已证明：

- `v5 cleancarve` 这种更窄的 clean absent metadata carve-out，
  在 synthetic 子集上是有正向信息量的；
- 但它仍 failed 于 friend-side real gate。

本轮进一步核对后发现一个比“selector 大方向不对”更具体的事实：

- `v39` 的 `reconstruction_extra` 实际命中集合里，
  仍和 friend-side exact `interference_extra` 分支有一小块重叠；
- 而验证集唯一一条 overlap：
  - `val_000075`
  恰好也是 `v39` 在 exact `target_full` 上的主要回退点。

因此下一条最直接的 follow-up
不应该先改 loss 图，
而是先做一个更窄的 sample-id carve-out 版本：

- 保留 `v39` 的 metadata carve 思路；
- 但从 `reconstruction_extra` allowlist 里剔除 exact overlap。

## 关键核对结果

### 1. `v39` manifest 仍完整包含 exact family 10 条样本

- train overlap：
  - `train_000001`
  - `train_000405`
  - `train_000432`
  - `train_001225`
  - `train_001279`
  - `train_001491`
  - `train_001610`
- val overlap：
  - `val_000075`
  - `val_000096`
  - `val_000297`

但这只是 manifest 层面的“在集合里”，
还不代表都被 `reconstruction_extra` 命中。

### 2. `reconstruction_extra` 实际命中的 overlap 只有 `4 train + 1 val`

实际命中 overlap：

- train：
  - `train_000001`
  - `train_000432`
  - `train_001225`
  - `train_001610`
- val：
  - `val_000075`

未命中的其他 exact 行之所以没撞上，
主要是因为：

- `target_absent_head / tail`
- `target_present_ratio < 0.95`
- 或 `target_transient_presence_minus_mid_db_mean` 超过上界

### 3. `val_000075` 是当前最可疑的验证冲突点

- 它同时满足：
  - `interference_extra` exact family
  - `reconstruction_extra` carve-out selector
- 并且在：
  - `reports/eval/compare_v19_vs_v39_on_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact/summary.json`
  中是 exact `target_full` 的主要回退样本：
  - `sisdr_delta_db = -0.467426`

## `v40` 预备文件

已生成：

- `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_train.txt`
- `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_val.txt`
- `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_all.txt`

摘要：

- `tmp/v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_summary.json`

规模：

- kept：
  - train `90`
  - val `20`
- excluded exact overlap：
  - train `4`
  - val `1`

被剔除的 overlap 为：

- train：
  - `train_000001`
  - `train_000432`
  - `train_001225`
  - `train_001610`
- val：
  - `val_000075`

## 下一步建议

若继续自动推进，下一条最直接可跑的候选就是：

- `v40 = v39 metadata carve-out + no exact-overlap reconstruction_extra sample-id allowlist`

具体做法：

1. 继续从 `v32` init；
2. 保持 `v39` 的大部分 loss 配置；
3. 给 `reconstruction_extra_focus_sample_ids_file`
   直接换成：
   - `sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_all.txt`
4. 取消或放空 `v39` 原来的 metadata selector 条件，
   避免又把 overlap 样本通过别的筛选条件命回来；
5. 训练后仍按：
   - default
   - exact
   - near-real speech probe
   - guodegang anchor / absent
   - `friend_speech_leak_followup_gate`
   统一裁决。
