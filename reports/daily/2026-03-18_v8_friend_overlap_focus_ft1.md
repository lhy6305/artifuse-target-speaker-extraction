# 2026-03-18 v8 friend-overlap focus ft1

## 背景

上一轮已经确认：

- `v7` 是当前更接近 near-real speech bucket 排序的基座
- 但真正仍未修好的，主要只剩：
  - `near_real_0003`
  - `near_real_0004`
- 它们都更偏 `friend_raw` 的 speech overlap 问题

因此本轮目标不是继续泛化扫点，而是做一条 very small focused fine-tune：

- 从 `v7` warm-start
- 只吃更接近 `0003 / 0004` 的 full-overlap speech focused 子集
- 看能不能把 `friend_raw` 缺口往前推，同时尽量不破坏 `0006`

## 新增脚本

- `scripts/data/build_metadata_focused_manifest.py`

作用：

- 从现有 synthetic manifest 按 metadata 过滤出 focused 子集
- 当前支持：
  - recipe
  - temporal pattern
  - target ratio
  - overlap ratio
  - interference gain
  - interference pool
  - per-recipe cap

## focused manifest

本轮没有重建新 synthetic 数据，只是从现有 default split 里筛子集。

### hard 子集

- train:
  - `data/synthetic/train_manifest_friend_overlap_focus_v1_hard.jsonl`
  - `target_hard_speech + target_full + overlap >= 0.9`
  - `51` 条
- val:
  - `data/synthetic/val_manifest_friend_overlap_focus_v1_hard.jsonl`
  - `18` 条

### clean 子集

- train:
  - `data/synthetic/train_manifest_friend_overlap_focus_v1_clean.jsonl`
  - `target_clean_speech + target_full + overlap >= 0.9 + gain in [-6.0, -3.5]`
  - `21` 条
- val:
  - `data/synthetic/val_manifest_friend_overlap_focus_v1_clean.jsonl`
  - `8` 条

### 组合子集

- train:
  - `data/synthetic/train_manifest_friend_overlap_focus_v1_combo.jsonl`
  - `72` 条
- val:
  - `data/synthetic/val_manifest_friend_overlap_focus_v1_combo.jsonl`
  - `26` 条

## 训练

新实验：

- `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1`

checkpoint:

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1/best.pt`

配置：

- init:
  - `v7`
- epochs:
  - `3`
- batch size:
  - `4`
- lr:
  - `1e-4`
- 训练预算：
  - `54` steps
- loss 保持保守：
  - `stft_weight = 0.5`
  - `transient_weight = 0.002`
  - `interference_weight = 0.005`
  - `absent_weight = 2.0`

## 客观结果

### 1. 相对 `v7` 的 default val

- compare:
  - `reports/eval/compare_v7_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_default/summary.json`

结果：

- `avg_sisdr_delta_db = -0.191305`
- `improved_count = 116`
- `regressed_count = 293`

解释：

- `v8` 不是无代价升级
- default synthetic coverage 上相对 `v7` 有明确但仍算可控的回吐

### 2. 相对 `stage2` 的 default val

- compare:
  - `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_default/summary.json`

结果：

- `avg_sisdr_delta_db = +0.270290`

解释：

- 虽然相对 `v7` 有回吐
- 但相对 `stage2` 仍保持正增益

### 3. near-real speech micro probe: `stage2 vs v8`

- compare:
  - `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_speech_probe_v1/summary.json`
- analysis:
  - `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

整体：

- `avg_sisdr_delta_db = -0.236418`

锚点：

- `near_real_0003 = -1.116950`
- `near_real_0004 = -0.220142`
- `near_real_0006 = +1.059967`

对照意义：

- 相比 `v7` 的 `-0.629166`
- `v8` 在这套更近真实的 speech probe 上明显更接近放行

### 4. near-real speech micro probe: `v7 vs v8`

- compare:
  - `reports/eval/compare_v7_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_speech_probe_v1/summary.json`
- analysis:
  - `reports/eval/compare_v7_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

整体：

- `avg_sisdr_delta_db = +0.392748`

锚点：

- `near_real_0003 = +0.421242`
- `near_real_0004 = +0.692135`
- `near_real_0006 = -0.099073`

结论：

- `v8` 对 `friend_raw / 0003 / 0004` 改善成立
- 但 `0006` 相对 `v7` 有小幅回吐

## 真实 near-real 自动诊断

blind pack:

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_blind/`

### hard gate

- `tradeoff_analysis/gate_summary.json`

结果：

- `FAIL`
- 仍只 fail:
  - `target_present__speech`

继续 `PASS`：

- `target_present__none`
- `target_absent__speech`

### `target_present__speech` 样本级诊断

- `bucket_diagnostics/target_present__speech/summary.json`

当前 failure signature：

- `near_real_0003`
  - `lost_retention_minus_leak + more_transient_lossy`
- `near_real_0004`
  - `lost_retention_minus_leak + more_interference_leaky`
- `near_real_0006`
  - `more_transient_lossy`

关键变化：

- 这一轮 speech bucket 已不再出现：
  - `more_residual_heavy`
- 也就是 `v8` 把 `v7` 在 `0003` 上更像 residual/transient 混合的问题，进一步压成了 retention/transient 型

## 当前结论

1. `v8` 是一条有效的 speech-bucket-focused follow-up，不是空转。
2. 它显著推进了：
   - `friend_raw / near_real_0003`
   - `friend_raw / near_real_0004`
3. 但它还没有通过真实 near-real hard gate。
4. 它的剩余主缺口仍然是：
   - `target_present__speech`
5. 它的新增代价主要是两类：
   - 相对 `v7` 的 default val 小幅回吐
   - 相对 `v7` 的 `near_real_0006` transient-like 小幅回吐

## 对下一步的影响

1. `v8` 应替代 `v7`，成为当前 speech-bucket-focused 线上的优先保留候选。
2. 但 broad objective-only 口径下，还不能仅凭这一轮 focused fine-tune 就宣布它全面替换 `v7` 或 `v1`。
3. 下一条 follow-up 若继续开，目标应明确成：
   - 保住 `v8` 对 `0003 / 0004` 的改善
   - 单独把 `0006` 的 transient-like 回吐拉回至少 `v7` 水平
   - 同时避免 default val 再继续明显回吐

## 验证

- `.\python.exe -m compileall .\scripts\data\build_metadata_focused_manifest.py`
- 已生成 focused train/val manifests
- 已完成 `v8` 训练
- 已完成：
  - `stage2 vs v8` default compare
  - `v7 vs v8` default compare
  - `stage2 vs v8` micro probe compare + analysis
  - `v7 vs v8` micro probe compare + analysis
  - `stage2 vs v8` near-real blind export + bandwidth/transient/tradeoff/gate/bucket diagnosis
