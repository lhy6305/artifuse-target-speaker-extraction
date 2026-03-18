# 2026-03-18 v10 v8 guodegang-proxy ft1

## 背景

上一轮已经确认：

- `v9` 失败的根因，不是预算不够，而是 `0006` proxy 映射错了
- 新搜索得到的 `guodegang_proxy_v1`，能在 synthetic 上稳定复现：
  - `v7 > v8 > v9`

因此本轮目标不是继续沿旧 `hard_transient_focus_v1_any` 开近邻，而是：

- 以 `v8` 为基座
- 用 `guodegang_proxy_v1` 做 very small focused fine-tune
- 先看它能否把 `0006` 拉回，同时不破坏 `0003 / 0004`

## 训练设置

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1/best.pt`

train / val manifest：

- `data/synthetic/train_manifest_guodegang_proxy_v1.jsonl = 85`
- `data/synthetic/val_manifest_guodegang_proxy_v1.jsonl = 31`

warm-start：

- `v8`

配置：

- `conditioning_mode = legacy_bias`
- `epochs = 3`
- `batch_size = 4`
- `lr = 8e-5`
- `global_steps = 66`
- loss 保持保守：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
  - `absent_weight = 2.0`

## 训练摘要

`train_summary.json`：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1/train_summary.json`

关键点：

- `best_val_loss = 0.025156`
- 训练总耗时：
  - `5.911 sec`

这说明这轮 focused fine-tune 的工程成本很低，适合继续作为预筛模板复用。

## 预筛结果

### 1. default val

相对 `stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.238452`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = -0.031839`

解释：

- `v10` 相对 `v8` 的 default 回吐很小
- broad synthetic 默认分布上没有明显炸掉

### 2. synthetic `guodegang_proxy_v1`

相对 `stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +1.513346`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +0.480623`

解释：

- 这条 focused 训练在 synthetic `guodegang_proxy_v1` 上是有效的
- 也就是说，模型确实学到了这条新 proxy 的优化方向

### 3. broad near-real speech micro probe

相对 `stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.156412 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.080006 dB`

按锚点：

- `near_real_0003 = +0.280721 dB`
- `near_real_0004 = +0.211316 dB`
- `near_real_0006 = -0.418033 dB`

按 family：

- `friend_raw = +0.246018 dB`
- `guodegang_raw = -0.418033 dB`

解释：

- `v10` 相对 `v8` 确实继续推进了：
  - `0003`
  - `0004`
- 但代价不是“轻微回吐 `0006`”，而是把 `0006` 再次系统性推坏

### 4. real `near_real_guodegang_transient_probe_v1`

相对 `stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.641934 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.418033 dB`

更关键的是：

- `6 / 6` 样本全部 regression

并且两类 clip 都一起回退：

- `guodegang_anchor_120s = -0.276978 dB`
- `guodegang_absent_480s = -0.559087 dB`

## Gate 结果

### speech follow-up gate

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`

结果：

- `FAIL`

失败项：

- `anchor_0006_regression_floor`

解释：

- `0003 / 0004` 其实都比 `v8` 更好
- default 也没有明显回吐
- 但因为 `0006` 全面回退，这条 branch-local follow-up 仍然不能保留

### `guodegang` focused guardrail

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_summary.json`

结果：

- `FAIL`

失败项：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`

解释：

- 这轮失败不是 broad probe 被平均值拖偏
- 而是 focused `0006` guardrail 本身就直接不过线

## 失败后的附加搜索

为了避免只得到一句“proxy 还不够像”，本轮继续做了一次失败面搜索：

- `scripts/eval/search_synthetic_proxy_candidates.py`
- 输出：
  - `reports/eval/synthetic_proxy_search_v8_v10_on_default/summary.json`

目标排序：

- `v8 > v10`

当前最稳定复现 `v8 > v10` 的 synthetic 子集，不在 clean proxy 上，而是集中在：

- `target_hard_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`
- `speech_interference_hard_pool`
- `interference_speaker_name = friend_hard_negative_segments`

代表性子集：

- count：
  - `18`
- alias scores：
  - `v8 = +0.240256 dB`
  - `v10 = -0.036000 dB`
- pair gap：
  - `+0.276255 dB`

## 当前结论

1. `v10` 不是保留候选。
2. `guodegang_proxy_v1` 虽然比旧 `hard_transient_focus_v1_any` 更接近 `0006`，但仍不足以替代真实 `guodegang` guardrail。
3. `v10` 的失败形态已经更清楚：
   - 它同时推进了：
     - `friend_raw / 0003`
     - `friend_raw / 0004`
   - 但继续系统性伤到：
     - `guodegang_raw / 0006`
4. 当前 synthetic 侧对这轮失败最有解释力的，不是 clean proxy 自己，而是：
   - `friend_hard_negative_segments`
   - `target_hard_speech`
   - `full-overlap`
   这一侧的回吐

## 对下一步的影响

1. 下一条自动 follow-up 不应再是“只用 `guodegang_proxy_v1` 单边微调”。
2. 更合理的方向应改为：
   - 以 `v8` 为基座
   - 把 `guodegang_proxy_v1` 当成正向信号
   - 同时把
     - `target_hard_speech + target_full + overlap>=0.9 + friend_hard_negative_segments`
     当成反向 guardrail 子集
3. 大白话讲，就是：
   - `v10` 不是完全修错方向
   - 它是“补 `0006` 的同时把原来 `v8` 擅长的 hard friend overlap 侧顶松了”
   - 所以下一步更像要做双锚点平衡，而不是单边继续加 `guodegang` focused 训练

## 验证

- 已完成 `v10` 训练
- 已完成 compare：
  - `default`
  - `guodegang_proxy_v1`
  - `near_real_speech_probe_v1`
  - `near_real_guodegang_transient_probe_v1`
- 已完成：
  - `analyze_near_real_speech_probe.py`
  - `gate_speech_probe_followup.py`
  - `gate_probe_subset_guardrail.py`
  - `search_synthetic_proxy_candidates.py` on `v8 > v10`
