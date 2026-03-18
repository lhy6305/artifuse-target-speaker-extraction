# 2026-03-18 v11 v8 dualanchor ft1

## 背景

上一轮已经确认：

- `v10` 的问题不是“完全没学到 `guodegang_proxy_v1`”，而是：
  - `0003 / 0004` 继续变强
  - 真实 `guodegang / 0006` 反而继续系统性回退
- 因而默认下一步不再是“单边 `guodegang_proxy_v1` 微调”，而是：
  - 以 `v8` 为基座
  - 保留 `guodegang_proxy_v1` 作为正向 focused 信号
  - 同时加入 `friend_hard_negative_segments / target_hard_speech / target_full / overlap>=0.9` 作为反向 guardrail

本轮目标就是验证这条“双锚点平衡”思路，看看它能否：

- 不丢 `v8` 在 `friend_raw / 0003 / 0004` 上的收益
- 同时把 `guodegang / 0006` 至少拉回到不弱于 `v8`

## 训练设置

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1/best.pt`

warm-start：

- `v8`

train / val manifest：

- `data/synthetic/train_manifest_v11_dualanchor_v1.jsonl = 136`
- `data/synthetic/val_manifest_v11_dualanchor_v1.jsonl = 49`

manifest 组成已核对：

- 与 `guodegang_proxy_v1` 的重合部分：
  - train `85`
  - val `31`
- 新增的反向 guardrail 部分全部是：
  - `target_hard_speech`
  - `target_full`
  - `speech_interference_hard_pool`
  - `friend_hard_negative_segments`
  - train `51`
  - val `18`

配置保持保守：

- `conditioning_mode = legacy_bias`
- `epochs = 3`
- `batch_size = 4`
- `lr = 8e-5`
- `global_steps = 102`
- loss 保持与 `v8 / v10` 一致：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
  - `absent_weight = 2.0`

## 训练摘要

`train_summary.json`：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1/train_summary.json`

关键点：

- `best_val_loss = 0.024402`
- 训练总耗时：
  - `7.746 sec`

## 预筛结果

### 1. default val

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.190317`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = -0.079973`

解释：

- `v11` 没有把 default synthetic 明显炸掉
- 但相对 `v8` 也不是无代价升级，已有可见回吐

### 2. synthetic `guodegang_proxy_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +1.828146`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +0.795423`

解释：

- 从 synthetic proxy 视角看，`v11` 明显比 `v10` 更进一步
- 说明这条 dual-anchor 训练并不是“没学到东西”

### 3. broad near-real speech micro probe

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.211357 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.025061 dB`

按锚点相对 `v8`：

- `near_real_0003 = +0.260091 dB`
- `near_real_0004 = +0.241347 dB`
- `near_real_0006 = -0.651915 dB`

按 family 相对 `v8`：

- `friend_raw = +0.250719 dB`
- `guodegang_raw = -0.651915 dB`

解释：

- `v11` 的 dual-anchor 确实保住并继续推进了 `friend_raw / 0003 / 0004`
- 但代价不是“轻微回吐 `0006`”，而是把 `0006` 整条线继续系统性压坏

### 4. real `near_real_guodegang_transient_probe_v1`

相对 `legacy_stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `+0.408052 dB`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.651915 dB`

更关键的是：

- `6 / 6` 样本全部 regression

clip 级别分开看，相对 `legacy_stage2`：

- `guodegang_absent_480s = +1.228311 dB`
- `guodegang_anchor_120s = -0.412207 dB`

解释：

- `v11` 不是“所有 `0006` 形态都更差”
- 它更像是：
  - 明显补强了 `absent_480s`
  - 但把更关键的 `anchor_120s` 压坏
- 可是从保留标准看，这仍然不能接受，因为相对当前参考 `v8`，`0006` 六条是全线回退

## Gate 结果

### speech follow-up gate

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`

结果：

- `FAIL`

失败项：

- `anchor_0006_regression_floor`

解释：

- `0003 / 0004` 相对 `v8` 都继续变好
- default 回吐也还在容忍带内
- 但只要 `0006` 相对 `v8` 明显回退，这条 speech-focused follow-up 仍然不放行

### `guodegang` focused guardrail

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_summary.json`

结果：

- `FAIL`

失败项：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`

解释：

- 这次不是 broad probe 均值掩盖问题
- 而是 focused `guodegang` guardrail 本身就不过线

## 当前结论

1. `v11` 不是保留候选。
2. “`guodegang_proxy_v1` 正向信号 + friend hard/full-overlap 反向 guardrail” 这条双锚点思路，按当前 one-shot 拼法仍然不够。
3. `v11` 的失败形态比 `v10` 更清楚：
   - 它确实把 `friend_raw / 0003 / 0004` 再往前推了一步
   - 也在 `guodegang_absent_480s` 上比 `legacy_stage2` 更好
   - 但它仍然系统性弱于 `v8` 的真实 `0006`
4. 相对同一参考 `v8`，`v11` 的 `0006` 回退还比 `v10` 更重：
   - `v10: -0.418033 dB`
   - `v11: -0.651915 dB`
5. 这说明当前问题不再只是“正向 proxy 太弱”，而更像：
   - 反向 guardrail 的加入方式仍在把优化重点推回 `friend` 侧
   - 且 `guodegang_anchor_120s` 与 `guodegang_absent_480s` 可能不是同一种子问题

## 对下一步的影响

1. 当前不要继续沿同配方放大 `v11` 训练预算。
2. 若继续自动推进，问题表述应再收窄为：
   - 不是“再做一版 broad dual-anchor”
   - 而是优先拆开 `guodegang_anchor_120s` 与 `guodegang_absent_480s`
   - 弄清楚到底是哪一类 `0006` 形态在被 friend-side guardrail 挤压
3. 在这之前，不应把：
   - synthetic `guodegang_proxy_v1` 继续转正
   - `0003 / 0004` 继续改善
   当成足以放行的理由

## 验证

- 已完成 `v11` 训练
- 已完成 compare：
  - `default`
  - `guodegang_proxy_v1`
  - `near_real_speech_probe_v1`
  - `near_real_guodegang_transient_probe_v1`
- 已完成：
  - `analyze_near_real_speech_probe.py`
  - `gate_speech_probe_followup.py`
  - `gate_probe_subset_guardrail.py`
