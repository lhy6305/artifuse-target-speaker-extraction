# 2026-03-18 v9 v8 dual-focus hard-transient ft1

## 背景

上一轮已经确认：

- `v8` 是当前 speech-focused 分支的默认基座
- 它相对 `v7` 已经更接近修好：
  - `near_real_0003`
  - `near_real_0004`
- 但它仍对：
  - `near_real_0006`
  留有一小段 transient-like 回吐

因此本轮目标不是再扩大 friend-focused 训练，而是做一条更窄的 follow-up：

- 从 `v8` warm-start
- 保住 `0003 / 0004`
- 尝试补 `0006`

## 数据入口升级

本轮先扩展了：

- `scripts/data/build_metadata_focused_manifest.py`

新增支持：

- `target_transient_presence_minus_mid_db_mean`
- `target_transient_presence_share_mean`
- `--transient-filter-mode all|any`

这样后续可以直接按 target transient 指标构造 manifest，而不必每次手工离线筛子集。

## 本轮 manifest

### 新 hard transient 子集

训练集：

- `data/synthetic/train_manifest_hard_transient_focus_v1_any.jsonl`
- 条件：
  - `target_hard_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `overlap >= 0.9`
  - `target_transient_presence_minus_mid_db_mean >= -7.7124357`
    或
  - `target_transient_presence_share_mean >= 0.0544913`
- 数量：
  - `21`

验证集：

- `data/synthetic/val_manifest_hard_transient_focus_v1_any.jsonl`
- 数量：
  - `5`

### 双焦点组合 manifest

这次没有完全替换 `v8` 的 friend-focused 数据，而是做重复加权叠加：

- 基座：
  - `train_manifest_friend_overlap_focus_v1_combo.jsonl`
  - `val_manifest_friend_overlap_focus_v1_combo.jsonl`
- 叠加：
  - `train_manifest_hard_transient_focus_v1_any.jsonl`
  - `val_manifest_hard_transient_focus_v1_any.jsonl`

组合结果：

- `data/synthetic/train_manifest_v9_dualfocus_v1.jsonl = 93`
- `data/synthetic/val_manifest_v9_dualfocus_v1.jsonl = 31`

两份组合 manifest 已确认：

- `UTF-8`
- `no BOM`

## 训练

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1/best.pt`

配置：

- init：
  - `v8`
- epochs：
  - `3`
- batch size：
  - `4`
- lr：
  - `8e-5`
- global steps：
  - `72`
- loss 保持与 `v8` 同量级：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
  - `absent_weight = 2.0`

## 预筛结果

### 1. default val

相对 `stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = +0.224121`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_default/summary.json`
- `avg_sisdr_delta_db = -0.046169`

解释：

- `v9` 没有像 `v8` 那样出现较大的 default 回吐。
- 这说明它在 broad default 上并没有明显炸掉。

### 2. near-real speech micro probe

相对 `stage2`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.252293 dB`

锚点：

- `0003 = -1.052830`
- `0004 = -0.136364`
- `0006 = +0.774620`

相对 `v8`：

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`
- overall：
  - `-0.015875 dB`

分组：

- `friend_raw = +0.073949 dB`
- `guodegang_raw = -0.285347 dB`

锚点：

- `0003 = +0.064120 dB`
- `0004 = +0.083778 dB`
- `0006 = -0.285347 dB`

## branch-local gate

本轮使用：

- `scripts/eval/gate_speech_probe_followup.py`

并把 `0006` 规则收紧为：

- `--max-anchor-0006-regression-db 0.0`

也就是：

- `v9` 不能比 `v8` 更差

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`

结果：

- `FAIL`

失败项：

- `speech_probe_overall_floor`
- `anchor_0006_regression_floor`

## 关键结论

这轮失败的价值，在于它把一个重要误区证伪了：

1. 当前 synthetic 上看起来合理的：
   - `hard speech`
   - `full overlap`
   - `transient-rich target`
   并不能可靠代表 near-real 里的 `guodegang 0006`。
2. `v9` 的真实效果不是“补回 `0006`”，而是：
   - `0003 / 0004` 再顺一点
   - `0006` 反而系统性回退
3. 更具体地说：
   - 当前这条 proxy 会继续把模型往 `friend` 侧推
   - 而不会把训练信号导向真正需要的 `guodegang transient recovery`

## 当前定位

1. `v9` 不是保留候选。
2. `v8` 继续保持为 speech-focused 分支的默认基座。
3. 当前最该更新的不是训练权重，而是 `0006` 的 objective proxy 设计。

## 对下一步的影响

1. 当前不值得再沿着这条 `hard/full-overlap/transient` synthetic proxy 开近邻实验。
2. 如果继续自动推进，下一步应先做：
   - `guodegang 0006` 的新 objective proxy / guardrail
   - 或更直接的 clip-family-aware probe
3. 在这一步完成前，不应再把：
   - synthetic hard transient subset 转正
   直接解释成：
   - `0006` 已被补回

## 验证

- `.\python.exe -m compileall .\scripts\data\build_metadata_focused_manifest.py`
- 已生成：
  - hard transient focused manifests
  - dual-focus manifests
- 已完成：
  - `v9` 训练
  - `stage2 vs v9` default compare
  - `v8 vs v9` default compare
  - `stage2 vs v9` near-real speech probe compare + analysis
  - `v8 vs v9` near-real speech probe compare + analysis
  - `v8 -> v9` branch-local gate
