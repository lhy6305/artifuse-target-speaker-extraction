# 2026-03-18 v14 v12 absent proxy v3 strict ft1

## 背景

上一轮已经确认：

- `v13` 不保留；
- 下一步若继续推进，应先重做 `absent` objective proxy；
- 真实 `guodegang_absent_480s` 的当前排序是：
  - `v8 > v12 > v13`

因此本轮先不再直接训练，而是先把 synthetic 侧的 `absent` proxy 重新按当前真实排序搜索一遍；只有在找到稳定 order-pass 子集后，才再开一条最小 follow-up。

## 新一轮 absent proxy 搜索

### 搜索输入

compare 输入都来自 `default` synthetic speech rows：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_default/per_sample_metrics.jsonl`
- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_default/per_sample_metrics.jsonl`
- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_default/per_sample_metrics.jsonl`

ordered aliases：

- `v8 v12 v13`

搜索输出：

- `reports/eval/synthetic_proxy_search_guodegang_absent_v8_v12_v13_on_default/summary.json`

### 搜索结果

这次 top order-pass 候选不再落在旧的：

- `pattern_nonfull`
- `target_absent_head / tail / intermittent`

方向上。

相反，稳定复现 `v8 > v12 > v13` 的候选收敛到同一类子集：

- `recipe = target_hard_speech`
- `temporal_pattern = target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`
  或稍宽到：
  - `overlap >= 0.75`

代表性候选有两条：

### `v3_strict`

过滤条件：

- `target_hard_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`

规模：

- `val = 18`
- `train = 51`

stage2-relative 排序：

- `v8 = +0.240256 dB`
- `v12 = +0.088626 dB`
- `v13 = -0.022755 dB`

pair gaps：

- `v8 - v12 = +0.151630 dB`
- `v12 - v13 = +0.111381 dB`

### `v4_broad`

过滤条件：

- `target_hard_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.75`

规模：

- `val = 39`
- `train = 122`

stage2-relative 排序：

- `v8 = +0.256340 dB`
- `v12 = +0.155148 dB`
- `v13 = +0.050509 dB`

pair gaps：

- `v8 - v12 = +0.101192 dB`
- `v12 - v13 = +0.104639 dB`

### 当前理解

1. 新的 `absent` objective proxy 已经可以重建出来。
2. 它不是旧的 `nonfull absent` 路线。
3. 它更像：
   - `hard speech`
   - `target_full`
   - `high-overlap`
4. 因而旧的 `guodegang_absent_proxy_v2_speechonly` 已不再代表当前真实排序。

## 物化后的 manifest

新 manifest：

- `data/synthetic/train_manifest_guodegang_absent_proxy_v3_strict.jsonl = 51`
- `data/synthetic/val_manifest_guodegang_absent_proxy_v3_strict.jsonl = 18`
- `data/synthetic/train_manifest_guodegang_absent_proxy_v4_broad.jsonl = 122`
- `data/synthetic/val_manifest_guodegang_absent_proxy_v4_broad.jsonl = 39`

复核 compare：

- `v3_strict`
  - `v8 = +0.240256 dB`
  - `v12 = +0.088626 dB`
  - `v13 = -0.022755 dB`
- `v4_broad`
  - `v8 = +0.256340 dB`
  - `v12 = +0.155148 dB`
  - `v13 = +0.050509 dB`

因此这两条 manifest 已经独立复现：

- `v8 > v12 > v13`

## 训练：`v14 = legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1`

### 配置

- output dir：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1`
- warm-start：
  - `v12`
- train manifest：
  - `train_manifest_guodegang_absent_proxy_v3_strict.jsonl`
- val manifest：
  - `val_manifest_guodegang_absent_proxy_v3_strict.jsonl`
- epochs：
  - `3`
- batch size：
  - `4`
- lr：
  - `5e-5`

训练摘要：

- `global_steps = 39`
- `best_val_loss = 0.023063`
- `elapsed_sec = 4.226`

### 一个关键事实

虽然这轮名义上是在测新的 `absent proxy`，但当前 loss selector 并没有真的打开 `absent_interval_l1`：

- `train_absent_interval_l1 = 0.0`
- `val_absent_interval_l1 = 0.0`

原因很直接：

- 新 proxy `v3/v4` 全是：
  - `target_full`
- 而当前训练参数仍把 absent loss 限定在：
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`

所以 `v14` 实际上不是“显式 absent-loss follow-up”，而是：

- 一次基于新 proxy 的 `target_full / hard speech` focused fine-tune

## 客观结果

### 1. default val

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.072915`

相对 `v8`：

- `-0.197375 dB`

相对 `v12`：

- `-0.098198 dB`

### 2. synthetic proxy

相对 `legacy_stage2`：

- `guodegang_anchor_proxy_v1`
  - `+1.500173 dB`
- `guodegang_absent_proxy_v3_strict`
  - `-0.196222 dB`
- `guodegang_absent_proxy_v4_broad`
  - `+0.016892 dB`

相对 `v12`：

- `anchor_proxy_v1 = -0.390675 dB`
- `absent_proxy_v3_strict = -0.284848 dB`

解释：

- `v14` 不只是没把 broad / guardrail 保住；
- 它连本轮新建的主 proxy `v3_strict` 自己都没有保住。

### 3. broad near-real speech probe

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.207776 dB`

按锚点相对 `legacy_stage2`：

- `near_real_0003 = -0.923706 dB`
- `near_real_0004 = +0.113401 dB`
- `near_real_0006 = +0.384354 dB`

相对 `v12`：

- overall：
  - `-0.210393 dB`
- `friend_raw = -0.030246 dB`
- `near_real_0003 = -0.077958 dB`
- `near_real_0004 = +0.017465 dB`
- `near_real_0006 = -0.750831 dB`

解释：

- 这不是“只补 `absent`，其他基本不动”；
- 它明显打坏了：
  - `friend_raw`
  - `near_real_0003`
  - `near_real_0006`

### 4. real `near_real_guodegang_transient_probe_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.384354 dB`

clip 级相对 `legacy_stage2`：

- `guodegang_anchor_120s = -0.847514 dB`
- `guodegang_absent_480s = +1.616223 dB`

相对 `v8`：

- overall：
  - `-0.675613 dB`
- `guodegang_anchor_120s = -0.832309 dB`
- `guodegang_absent_480s = -0.518916 dB`

相对 `v12`：

- overall：
  - `-0.750831 dB`
- `guodegang_anchor_120s = -1.099112 dB`
- `guodegang_absent_480s = -0.402550 dB`

解释：

- `v14` 的形态不是“牺牲一点 anchor，换回 absent”；
- 它是：
  - anchor 大幅回吐；
  - absent 也没有回到 `v8` / `v12` 水平。

## Gate 结果

### speech follow-up gate: `v12 -> v14`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_vs_v12_summary.json`

结果：

- `FAIL`

失败项：

- `speech_probe_overall_floor`
- `speech_probe_friend_raw_floor`
- `anchor_0003_gain_floor`
- `anchor_0006_regression_floor`

### `guodegang` clip 级 guardrail vs `v8`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v8_with_clips.json`

结果：

- `FAIL`

失败项：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`
- `clip__guodegang_anchor_120s`
- `clip__guodegang_absent_480s`

## 当前结论

1. 新的 `absent` proxy 已经重建成功：
   - `v3_strict`
   - `v4_broad`
   都能稳定复现：
   - `v8 > v12 > v13`
2. 但 `v14` 证明了另一件事：
   - “proxy 排序能复现真实排序”
   - 不等于
   - “直接拿这条 proxy 从 `v12` warm-start 微调就会往正确方向走”
3. `v14` 不保留。
4. 当前更合理的定位是：
   - `v3_strict / v4_broad` 保留为新的 synthetic eval / guardrail
   - 但不再直接作为这条 single-route follow-up 的训练 objective

## 对下一步的影响

1. 当前不要继续沿：
   - `v12 + absent_proxy_v3_strict direct fine-tune`
   再加预算。
2. 若后续还要继续补 `absent`，下一步应先解决下面至少一项：
   - 让当前 objective 真正接入这条新 proxy
   - 或把 `anchor` floor 明确联立进去
   - 或把优化预算进一步压小到“只做极轻微 nudging”
3. 当前接班口径应更新为：
   - `v8` 继续保留为 broad speech 参考基座
   - `v12` 继续保留为当前 anchor-focused 第二候选
   - `v13 / v14` 都不保留
   - `guodegang_absent_proxy_v3_strict / v4_broad` 保留为新的 absent-side synthetic guardrail
