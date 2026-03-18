# 2026-03-18 v12 v8 anchor proxy ft1

## 背景

上一轮 `guodegang clip split` 已确认：

- `near_real_0006` 不是单一子问题；
- `guodegang_anchor_120s` 更像：
  - `v7 > v8 > v10 > v11`
- `guodegang_absent_480s` 更像：
  - `v8 > v7 > v10 > v11`

因此如果继续自动推进，下一步不该再做“统一 `0006` 总 proxy”，而应先验证一个更窄的问题：

- 以 `v8` 作为 broad speech 基座；
- 只用 `guodegang_anchor_proxy_v1` 做一次保守 focused fine-tune；
- 看它能否：
  - 拉回 `anchor_120s`
  - 同时不明显破坏 `v8` 在 `absent_480s` 上的收益

本轮就是这次验证。

## 训练设置

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1/best.pt`

warm-start：

- `v8`

train / val manifest：

- `data/synthetic/train_manifest_guodegang_anchor_proxy_v1.jsonl = 84`
- `data/synthetic/val_manifest_guodegang_anchor_proxy_v1.jsonl = 22`

配置保持保守：

- `conditioning_mode = legacy_bias`
- `epochs = 3`
- `batch_size = 4`
- `lr = 8e-5`
- `global_steps = 63`
- loss 保持与 `v8 / v10 / v11` 一致：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
  - `absent_weight = 2.0`

## 训练摘要

`train_summary.json`：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1/train_summary.json`

关键点：

- `best_val_loss = 0.026733`
- 训练总耗时：
  - `5.326 sec`

## 预筛结果

### 1. default val

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.171113`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = -0.099178`

解释：

- `v12` 没把 broad default synthetic 炸掉；
- 但它不是无代价升级，相对 `v8` 仍有小幅默认集回吐。

### 2. synthetic `guodegang_anchor_proxy_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_guodegang_anchor_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +1.890848`

解释：

- 这说明 `v12` 的确学到了本轮想注入的 anchor-focused 信号；
- 不是只在 near-real 上偶然波动。

### 3. synthetic `guodegang_absent_proxy_v2_speechonly`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_guodegang_absent_proxy_v2_speechonly/summary.json`
- `avg_sisdr_delta_db = +3.652780`

解释：

- 即使本轮只训 `anchor` proxy，`absent` proxy 相对 `legacy_stage2` 也仍是明显正增益；
- 但这还不够说明它一定保住了 `v8`，因为 `v8` 本来就在 `absent` 上更强。

### 4. broad near-real speech micro probe

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.002617 dB`

相对 `v8`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`
- 关键差值：
  - default relative to `v8`：`-0.099178 dB`
  - probe overall relative to `v8`：`+0.239034 dB`
  - `friend_raw` relative to `v8`：`+0.293640 dB`
  - `near_real_0003` relative to `v8`：`+0.271202 dB`
  - `near_real_0004` relative to `v8`：`+0.316077 dB`
  - `near_real_0006` relative to `v8`：`+0.075219 dB`

解释：

- 从 broad speech follow-up gate 口径看，`v12` 是过线的；
- 它没有像 `v10 / v11` 那样把 `0006` 整体推坏；
- 同时也没有回吐 `v8` 在 `0003 / 0004 / friend_raw` 上的主收益。

### 5. real `near_real_guodegang_transient_probe_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+1.135186 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.075219 dB`

clip 级别分开看，相对 `v8`：

- `guodegang_anchor_120s = +0.266803 dB`
- `guodegang_absent_480s = -0.116366 dB`

解释：

- `v12` 已经不是 `v10 / v11` 那种“`0006` 整体继续输给 `v8`”；
- 它确实把 `anchor_120s` 拉回来了；
- 但代价是：
  - `absent_480s` 相对 `v8` 出现了小幅回吐

## Gate 结果

### speech follow-up gate

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`

结果：

- `PASS`

解释：

- 按 broad speech follow-up 的当前规则，`v12` 已经满足：
  - default 不过度回退；
  - `0003 / 0004 / friend_raw` 不变差；
  - `0006` overall 不弱于 `v8`。

### `guodegang` clip 级 guardrail vs `v8`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v8_with_clips.json`

结果：

- `FAIL`

唯一失败项：

- `clip__guodegang_absent_480s`

解释：

- `v12` 不是 broad gate 不过线；
- 它的问题已经收窄成：
  - `anchor_120s` 修回来了；
  - `absent_480s` 只相对 `v8` 小幅回吐

## 当前结论

1. `v12` 不是废分支，已经比 `v10 / v11` 更接近可保留候选。
2. 它当前更像：
   - `anchor` 方向的成功 follow-up；
   - 但还不是完整替代 `v8` 的无代价升级。
3. 若按 `v12+` 的新口径看，本轮已经满足：
   - 明确说明它更接近哪条 clip 排序：
     - 更接近 `guodegang_anchor_120s`
   - 也明确说明付出的代价：
     - `guodegang_absent_480s` 相对 `v8` 小幅回吐
4. 因而当前最合理的定位不是“立刻升主线”，而是：
   - 保留 `v8` 作为 broad speech 参考基座；
   - 保留 `v12` 作为 anchor-focused 第二候选。

## 对下一步的影响

1. 当前不要再回到“统一 `guodegang` 总 proxy”的宽口径微调。
2. 若继续自动推进，下一步更合理的问题应改成：
   - 如何在保住 `v12` 的 `anchor_120s` 收益前提下，
   - 给 `guodegang_absent_480s` 加一个显式 floor / guardrail。
3. 更直白地说：
   - `v12` 已证明“anchor-focused follow-up”这条方向是通的；
   - 但下一步该补的是 `absent` 的保底，而不是再做更宽的 `anchor` 强化。
