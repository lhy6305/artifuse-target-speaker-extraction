# 2026-03-18 v15 v12 anchor absent proxy v3 nudge ft1

## 背景

上一轮 `v14` 已经证明两件事：

1. 新的 `absent` proxy 已经重建成功：
   - `guodegang_absent_proxy_v3_strict`
   - `guodegang_absent_proxy_v4_broad`
2. 但直接拿 `v3_strict` 从 `v12` 做单路 focused fine-tune，会明显把模型往错误方向推：
   - `anchor_120s` 回吐过大
   - `absent_480s` 也没有收回

因此本轮不再继续做单路 `absent-only` 跟进，而是验证一条更小、更保守的假设：

- 从 `v12` warm-start；
- 把：
  - `guodegang_anchor_proxy_v1`
  - `guodegang_absent_proxy_v3_strict`
  做并集；
- 但只做一次：
  - 极轻微
  - full-pattern
  - 带 anchor floor 的 nudging

本轮目标不是“修好 absent”，而是先看：

- 能否在基本保住 `v12` 的前提下
- 至少别再像 `v14` 一样把 `0006` 整体打坏

## focused manifest

新 manifest：

- `data/synthetic/train_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl`
- `data/synthetic/val_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl`

组成：

- `anchor_proxy_v1 ∪ absent_proxy_v3_strict`

由于两者 val 集完全不重叠：

- `overlap_count = 0`

最终规模：

- train：
  - `135`
  - `target_clean_speech = 84`
  - `target_hard_speech = 51`
- val：
  - `40`
  - `target_clean_speech = 22`
  - `target_hard_speech = 18`

## 训练

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1/best.pt`

warm-start：

- `v12`

配置刻意压小：

- `epochs = 1`
- `batch_size = 4`
- `lr = 1e-5`
- `global_steps = 34`

loss：

- 保留：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
- 显式关闭：
  - `absent_weight = 0.0`

原因：

- 当前这条训练不是在验证 explicit absent-loss；
- 新 proxy 本身也没有 `target_absent_intervals`

训练摘要：

- `best_val_loss = 0.025820`
- `elapsed_sec = 3.682`

## 客观结果

### 1. default val

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.142876`

相对 `v8`：

- `-0.127415 dB`

相对 `v12`：

- `-0.028237 dB`

解释：

- 这版 broad default 已经明显比 `v14` 更接近 `v12`；
- 但仍没有回到 `v12` 本身。

### 2. synthetic anchor / absent proxy

相对 `legacy_stage2`：

- `guodegang_anchor_proxy_v1`
  - `+2.213110 dB`
- `guodegang_absent_proxy_v3_strict`
  - `-0.038012 dB`

相对 `v12`：

- `anchor_proxy_v1 = +0.322262 dB`
- `absent_proxy_v3_strict = -0.126638 dB`

解释：

- 这条 `nudge` 路线更像：
  - 继续强化 `anchor` 侧
  - 但没有把新的 `absent proxy` 收回来

### 3. broad near-real speech probe

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.023170 dB`

按锚点相对 `legacy_stage2`：

- `near_real_0003 = -0.835371 dB`
- `near_real_0004 = +0.112841 dB`
- `near_real_0006 = +0.991116 dB`

相对 `v12`：

- overall：
  - `-0.025787 dB`
- `friend_raw = +0.013641 dB`
- `near_real_0003 = +0.010377 dB`
- `near_real_0004 = +0.016905 dB`
- `near_real_0006 = -0.144069 dB`

解释：

- 相对 `v12`，这版已经不再像 `v14` 那样大面积打坏 `friend_raw / 0003 / 0004`；
- 真正还过不去的点，已经收缩到：
  - `0006` 仍小幅回退
  - 导致 overall 也小幅不及 `v12`

### 4. real `near_real_guodegang_transient_probe_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.991116 dB`

clip 级相对 `legacy_stage2`：

- `guodegang_anchor_120s = +0.033892 dB`
- `guodegang_absent_480s = +1.948341 dB`

相对 `v8`：

- overall：
  - `-0.068851 dB`
- `guodegang_anchor_120s = +0.049097 dB`
- `guodegang_absent_480s = -0.186798 dB`

相对 `v12`：

- overall：
  - `-0.144069 dB`
- `guodegang_anchor_120s = -0.217707 dB`
- `guodegang_absent_480s = -0.070432 dB`

解释：

- 与 `v14` 不同，`v15` 已经把：
  - `anchor_120s`
  至少重新拉回到：
  - 相对 `v8` 为正
- 但它仍没有把：
  - `absent_480s`
  收回到 `v8`
- 也没有超过 `v12`

## Gate 结果

### speech follow-up gate: `v12 -> v15`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_vs_v12_summary.json`

结果：

- `FAIL`

失败项仅剩：

- `speech_probe_overall_floor`
- `anchor_0006_regression_floor`

解释：

- 这说明本轮已经比 `v14` 收敛得多；
- 但离“可替代 `v12`”还差最后一小段 `0006` floor。

### `guodegang` clip 级 guardrail vs `v8`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v8_with_clips.json`

结果：

- `FAIL`

失败项：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`
- `clip__guodegang_absent_480s`

通过项：

- `clip__guodegang_anchor_120s`

解释：

- 当前这条轻量双路 `nudge` 已经从：
  - “anchor / absent 两条都坏”
  收敛成：
  - “anchor 线重新站回来了”
  - 但 `absent_480s` 仍不够

## 额外排除：高增益 hard-core 子集

本轮顺手检查了 `v4_broad` 里更高干扰增益的小子集。

例如：

- `gain_db >= 1.0`
- count：
  - `8`

stage2-relative 排序会变成：

- `v8 = +0.111198 dB`
- `v13 = +0.010445 dB`
- `v12 = -0.034069 dB`

也就是说：

- 会变成 `v8 > v13 > v12`

这条更窄的 high-gain carve-out 已经不再保持当前真实排序：

- `v8 > v12 > v13`

因此本轮不把它升级成新的 objective proxy。

## 当前结论

1. `v15` 明显优于 `v14`：
   - 它把路线重新收敛成：
     - 主要只差 `0006 / absent`
   - 而不是像 `v14` 那样把 `friend_raw / 0003 / 0006` 一起打坏
2. 但 `v15` 仍不保留。
3. 它的实际形态是：
   - `anchor` 重新回到安全区附近
   - `absent` 仍没有超过：
     - `v8`
     - `v12`
4. 因而当前不能再把这条路线理解成：
   - “再调一点 learning rate / step 数就能过”
5. 更准确的口径应是：
   - 这条轻量双路 `nudge` 主要在强化 `anchor`
   - 但并没有解决真正要补的 `absent_480s`

## 对下一步的影响

1. 当前不要继续沿：
   - `v12 + anchor_proxy_v1 + absent_proxy_v3_strict`
   的轻量 warm-start 路线继续加预算。
2. `v15` 的价值在于：
   - 它证明了轻量双路 `nudge` 可以把 `anchor_120s` 保回来
   - 但也同时证明：
     - 这条路仍不会自然补好 `absent_480s`
3. 当前接班口径应进一步收紧为：
   - `v8` 继续保留为 broad speech 参考基座
   - `v12` 继续保留为当前 anchor-focused 第二候选
   - `v13 / v14 / v15` 都不保留
   - `guodegang_absent_proxy_v3_strict / v4_broad` 继续保留为 absent-side synthetic guardrail
   - 但下一步若继续推进，应换新的 objective / gate 设计，而不是继续在这条 warm-start 路线上做小步长搜索
