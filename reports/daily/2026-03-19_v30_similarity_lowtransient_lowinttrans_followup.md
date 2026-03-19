# 2026-03-19 `v30` similarity + low-transient + low-interference-transient follow-up

## 背景

`v29` 已确认：

- `focus_sample_ids` plumbing 已经接通；
- 但把 `0004-like speech-leak` 收成 exact sample-id selector 后，
  仍然没有把 `v19` 往前推。

因此本轮不再继续扫同一批 `v29` exact ids，
而是直接重做 `0004-like speech-leak` 的 synthetic family 搜索口径：

- 保留 `samplewise-order-pass` 约束；
- 在原先 `gain / target transient` 之外，
  再把：
  - `interference_transient_presence_minus_mid_db_mean`
  - `target_interference_logspec_cosine`
  纳入搜索。

## 搜索刷新

本轮刷新输出：

- `reports/eval/synthetic_proxy_search_friend_reverse_guardrail_v12_v19_v8_on_default_samplewise_order_pass_semantic_split_v2_metrics/summary.json`
- `reports/eval/synthetic_proxy_search_friend_reverse_guardrail_v12_v19_v8_on_default_samplewise_order_pass_semantic_split_v2_metrics_top400/summary.json`
- `reports/eval/synthetic_proxy_search_friend_reverse_guardrail_v12_v19_v8_on_train_default_samplewise_order_pass_semantic_split_v2_metrics/summary.json`

当前首次搜出一条与旧 `v23 / v29` 不同的候选 family：

- clean pool
- higher gain
- higher target/interference similarity
- lower target transient
- lower interference transient
- pattern 不再是 full-only，而是 `full + absent_head + absent_tail` 混合

### 选定 exact 子集

- train exact：
  - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_train.txt = 7`
  - `data/synthetic/train_manifest_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 7`
- val exact：
  - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_val.txt = 3`
  - `data/synthetic/val_manifest_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 3`
- all ids：
  - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_all.txt = 10`

其中 val exact ids 为：

- `val_000075`
- `val_000096`
- `val_000297`

这条 val family 的平均语义为：

- mean gain = `+0.337 dB`
- mean target transient = `-13.013119 dB`
- mean interference transient = `-2.638405 dB`
- mean target/interference similarity = `0.703030`

## `v30 = legacy_transient_leakguard_probe_v30_v19_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_ft1`

### 训练配置

- init checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1/best.pt`
- base manifests：
  - `data/synthetic/train_manifest_v16_absent_proxy_v3_plus_reverse_guardrail_v1.jsonl = 90`
  - `data/synthetic/val_manifest_v16_absent_proxy_v3_plus_reverse_guardrail_v1.jsonl = 27`
- plus manifests：
  - `data/synthetic/train_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 97`
  - `data/synthetic/val_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 29`
- 预算：
  - `epochs = 1`
  - `batch_size = 4`
  - `lr = 1e-5`
- branch 挂法：
  - 保留 `v19` 原有 `transient / interference / absent`
  - 新 exact family 挂到 `interference_extra_focus_sample_ids`

### selector 命中

- train：
  - transient / interference / absent = `51 / 58 / 27` out of `97`
- val：
  - transient / interference / absent = `18 / 21 / 5` out of `29`

解释：

- 相对 `v19` 基座的 `51 / 51 / 24` 和 `18 / 18 / 4`
- 本轮新增 exact family 已经真实进入：
  - interference branch
  - absent branch（因为混入了 nonfull 行）

## 结果

### 相对 `v19`

- default：
  - `+0.015689 dB`
- `v30 exact proxy`：
  - `-0.141952 dB`
- near-real speech probe overall：
  - `-0.053396 dB`
- near-real `friend_raw`：
  - `-0.047730 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.035911 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.059549 dB`
- near-real `transient_like (0006)`：
  - `-0.070391 dB`

### exact proxy 细节

新 exact val 的 3 条里：

- `val_000075 (target_full)`：
  - `-0.340267 dB`
- `val_000096 (target_absent_tail)`：
  - `-0.075451 dB`
- `val_000297 (target_absent_head)`：
  - `-0.010138 dB`

也就是说：

- 这条新 family 里最该被当成 `speech-leak-like` 的 full 行仍然明显回退；
- nonfull 两条也没有真正转正，只是更接近 near-tie。

### near-real 细节

- `near_real_0004` 没有出现明显大回退，
  但 9 条全部没有一条转正：
  - overall `-0.035911 dB`
- `friend_absent_820s`：
  - `-0.075125 dB`
- `guodegang_anchor_120s`：
  - `-0.098219 dB`

这说明：

- 即便把 speech-leak family 重写成 “高 similarity + 双低 transient”；
- 当前这条 interference-extra objective 仍然没有形成正收益；
- 反而把 `guodegang` 侧已有收益一起轻微回吐。

## 结论

- `v30` 不保留为新候选；
- 这次可以排除的旧解释包括：
  - 还缺 `similarity` 字段
  - 还缺 `interference transient` 字段
  - 还只是在旧 `v23 / v29` family 上原地打转
- 当前更可信的结论应升级为：
  - `0004-like speech-leak` 的问题不只是 sample family 选错；
  - 也不只是 full / nonfull 边界写得不够像；
  - 当前 branch-local objective / guardrail 形式本身仍然不对。

## 当前建议

下一步若继续自动推进，优先级应更新为：

1. 不继续围绕这条 `v30` family 扫权重、epoch、lr；
2. 不把“又找到一条更像 speech-leak 的 exact family”误写成“objective 已接近正确”；
3. 后续若还要补 `0004-like speech-leak`，优先改：
   - objective 形式
   - leak-specific guardrail
   - 或更明确的 branch-local loss 归属
4. 当前基座继续保持：
   - `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
