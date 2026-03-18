# 2026-03-18 v13 v12 anchor absent proxy ft1

## 背景

上一轮 `v12` 已经明确了当前问题形态：

- 相对 `v8`：
  - `guodegang_anchor_120s = +0.266803 dB`
  - `guodegang_absent_480s = -0.116366 dB`
- 也就是说：
  - `anchor` 已被拉回；
  - `absent` 仍有小幅回吐。

因此本轮默认想验证的不是更宽的 `guodegang` focused 微调，而是一条更直白的 follow-up：

- 从 `v12` warm-start；
- 把：
  - `guodegang_anchor_proxy_v1`
  - `guodegang_absent_proxy_v2_speechonly`
  做一次去重并集；
- 看“显式加 absent floor”是否能：
  - 收回 `absent_480s`
  - 同时保住 `v12` 已拿回的 `anchor`

## focused manifest

本轮没有重建新 synthetic 数据，只是合并已有两条 proxy manifest。

新 manifest：

- `data/synthetic/train_manifest_v13_anchor_absent_proxy_v1.jsonl`
- `data/synthetic/val_manifest_v13_anchor_absent_proxy_v1.jsonl`

合并口径：

- `sample_id` 去重并集；
- 重复样本优先保留 `absent` 行，避免丢失其额外 transient 元数据字段。

规模：

- train:
  - `114`
- val:
  - `29`

train 配方组成：

- `target_clean_speech = 84`
- `target_hard_speech = 30`

## 训练

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1/best.pt`

warm-start：

- `v12`

配置保持保守：

- `conditioning_mode = legacy_bias`
- `epochs = 3`
- `batch_size = 4`
- `lr = 5e-5`
- `global_steps = 87`
- loss 仍保持与 `v12` 一致：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
  - `absent_weight = 2.0`

## 训练摘要

`train_summary.json`：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1/train_summary.json`

关键点：

- `best_val_loss = 0.025708`
- 训练总耗时：
  - `6.274 sec`

## 客观结果

### 1. default val

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.195532`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = -0.074758`

相对 `v12`：

- `reports/eval/compare_v12_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.024419`

解释：

- `v13` 没把 broad default val 炸掉；
- 相对 `v12` 甚至有轻微正增益；
- 但这还不能说明它真的修好了 `guodegang/0006`。

### 2. synthetic anchor / absent proxy

相对 `legacy_stage2`：

- `guodegang_anchor_proxy_v1`
  - `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_guodegang_anchor_proxy_v1/summary.json`
  - `avg_sisdr_delta_db = +2.784445`
- `guodegang_absent_proxy_v2_speechonly`
  - `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_guodegang_absent_proxy_v2_speechonly/summary.json`
  - `avg_sisdr_delta_db = +3.741080`

解释：

- synthetic 侧看起来更强；
- 但这次真正的问题不在 synthetic 上，而在相对 `v8 / v12` 的真实 `0006` trade-off。

### 3. broad near-real speech probe

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.028007 dB`

按锚点相对 `legacy_stage2`：

- `near_real_0003 = -0.805782 dB`
- `near_real_0004 = +0.198835 dB`
- `near_real_0006 = +1.022450 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.264425 dB`

按锚点相对 `v8`：

- `near_real_0003 = +0.311168 dB`
- `near_real_0004 = +0.418977 dB`
- `near_real_0006 = -0.037517 dB`

解释：

- `v13` 进一步推进了 `friend_raw / 0003 / 0004`；
- 但相对 `v8`，`0006` overall 重新回到小幅负增益。

### 4. real `near_real_guodegang_transient_probe_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+1.022450 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.037517 dB`

clip 级相对 `v8`：

- `guodegang_anchor_120s = +0.107729 dB`
- `guodegang_absent_480s = -0.182764 dB`

相对 `v12`：

- `reports/eval/compare_v12_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.112736 dB`

clip 级相对 `v12`：

- `guodegang_anchor_120s = -0.159074 dB`
- `guodegang_absent_480s = -0.066398 dB`

解释：

- 本轮最关键的负结论就在这里：
  - `v13` 没把 `absent_480s` 从 `v8` 手里收回来；
  - 反而把 `v12` 已拿回的 `anchor` 也一起回吐了一部分。

## Gate 结果

### speech follow-up gate: `v12 -> v13`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_vs_v12_summary.json`

结果：

- `FAIL`

唯一失败项：

- `anchor_0006_regression_floor`

解释：

- `v13` 相对 `v12` 在：
  - default val
  - friend_raw
  - `0003 / 0004`
  都没变差；
- 但 `0006` 相对 `v12` 回退超过了允许阈值。

### `guodegang` clip 级 guardrail vs `v8`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v8_with_clips.json`

结果：

- `FAIL`

失败项：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`
- `clip__guodegang_absent_480s`

解释：

- `v13` 没有把问题收敛成“只差一点 absent”；
- 因为它对 `v8` 的整体 `guodegang_raw / 0006` 也已经重新转负。

## 当前结论

1. `v13` 不是保留候选。
2. “从 `v12` 出发，把 `anchor + absent` 两条 proxy 直接做 one-shot 并集微调” 这条路当前不成立。
3. 它的实际效果是：
   - 继续增强了 `friend_raw / 0003 / 0004`
   - 但没有把 `absent_480s` 从 `v8` 收回来
   - 还把 `v12` 的 `anchor_120s` 一起回吐
4. 因而这次试探给出的明确信号不是“再调小一点就行”，而是：
   - 当前这条 one-shot union manifest 的训练方向本身就不对。

## 对下一步的影响

1. 当前不要继续沿 `v13` 这条 one-shot `anchor+absent` 并集路线加预算。
2. `v8` 继续保留为 broad speech 参考基座。
3. `v12` 继续保留为当前 anchor-focused 第二候选。
4. 若下一步继续自动推进，更合理的问题应变成：
   - 先重做 `absent` 的 objective proxy / floor
   - 再决定是否值得做新的 clip-specific follow-up
5. 更直白地说：
   - 当前不是“再多喂一点 absent 样本”
   - 而是要先承认：
     - 这条 absent proxy 在 `v12` warm-start 条件下，并没有把训练信号导向真正想修的 `absent_480s`

