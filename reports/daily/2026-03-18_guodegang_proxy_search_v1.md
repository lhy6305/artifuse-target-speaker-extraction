# 2026-03-18 guodegang proxy search v1

## 背景

上一轮已经确认：

- `near_real_guodegang_transient_probe_v1` 上的客观排序是：
  - `v7 > v8 > v9`
- `v9` 证伪了旧假设：
  - `target_hard_speech + target_full + high-overlap + target transient-rich`
  不是 `guodegang / 0006` 的可靠 synthetic 代理

因此本轮不继续训练 `v10`，先做一件更小但更关键的事：

- 在现有 default synthetic speech rows 里，搜索一个能复现
  - `v7 > v8 > v9`
  排序的 metadata-defined 子集

## 本轮使用的脚本

- `scripts/eval/search_synthetic_proxy_candidates.py`
- `scripts/data/build_metadata_focused_manifest.py`
- `scripts/eval/compare_checkpoints_on_manifest.py`

## 搜索设置

compare 输入：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_default/per_sample_metrics.jsonl`
- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_default/per_sample_metrics.jsonl`
- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_default/per_sample_metrics.jsonl`

ordered aliases：

- `v7 v8 v9`

搜索输出：

- `reports/eval/synthetic_proxy_search_v7_v8_v9_on_default/summary.json`

本轮约束：

- `min_count = 8`
- `min_speaker_count = 8`
- `min_order_gap_db = 0.0`

## 搜索结果

当前 top order-pass 候选没有落在旧的 `hard/full-overlap/transient` 方向。

相反，最稳定复现 `v7 > v8 > v9` 的候选会收敛到同一类过滤条件：

- `recipe = target_clean_speech`
- `temporal_pattern = target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.75`
- `interference_pool = speech_interference_clean_pool`
- `target_transient_presence_minus_mid_db_mean >= -11.5350723`

代表性子集：

- count:
  - `31`
- alias scores:
  - `v7 = +1.916698 dB`
  - `v8 = +1.032723 dB`
  - `v9 = +0.866308 dB`
- pair gaps:
  - `v7 - v8 = +0.883974 dB`
  - `v8 - v9 = +0.166415 dB`

这说明当前最接近 `guodegang / 0006` 排序的 metadata-defined synthetic 子集，更像：

- `clean speech`
- `target full / high overlap`
- `target transient 较强`

而不是：

- `hard speech`
- 或“越像 friend overlap 越对”的那条线

## 物化后的正式 manifest

基于上述 top candidate，本轮已生成：

- `data/synthetic/val_manifest_guodegang_proxy_v1.jsonl = 31`
- `data/synthetic/train_manifest_guodegang_proxy_v1.jsonl = 85`

它们的过滤条件保持一致：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.75`
- `speech_interference_clean_pool`
- `target_transient_presence_minus_mid_db_mean >= -11.5350723`

## 复核 compare

为了避免只停留在搜索 summary，本轮已直接对 `val_manifest_guodegang_proxy_v1.jsonl` 重跑 checkpoint compare。

### `stage2 vs v7`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +1.916698`

### `stage2 vs v8`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +1.032723`

### `stage2 vs v9`

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = +0.866308`

### `v7 vs v8`

- `reports/eval/compare_v7_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = -0.883974`

### `v8 vs v9`

- `reports/eval/compare_v8_vs_legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1_on_guodegang_proxy_v1/summary.json`
- `avg_sisdr_delta_db = -0.166415`

当前这套新 manifest 已能独立复现：

- `v7 > v8 > v9`

## 当前结论

1. `0006` 的当前最佳 metadata-defined synthetic proxy，不是 `hard/full-overlap/transient`。
2. 更接近真实 `guodegang / 0006` 排序的，是：
   - `clean speech + target_full + overlap>=0.75 + target transient 较高`
3. 这说明上一轮把 `0006` 直觉性地往 `hard speech / friend-like overlap` 上映射，是方向性错误，而不是只差一点权重。
4. `guodegang_proxy_v1` 现在可以作为：
   - `v10+` 的 synthetic 预筛子集
   - 或 focused fine-tune / focused val 的保守锚点

## 对下一步的影响

1. 若继续自动推进，下一条 `v10` 不应再从 `hard_transient_focus_v1_any` 出发。
2. 更合理的 synthetic 入口应改成：
   - `train_manifest_guodegang_proxy_v1.jsonl`
   - `val_manifest_guodegang_proxy_v1.jsonl`
3. 但这条新 proxy 仍只是 synthetic 预筛，不替代：
   - `near_real_guodegang_transient_probe_v1`
4. 任何声称“在补 `0006`”的后续版本，至少应满足：
   - 在 `guodegang_proxy_v1` 上不弱于当前参考版本
   - 同时继续通过 `near_real_guodegang_transient_probe_v1` 的独立 guardrail

## 验证

- `.\python.exe scripts/eval/search_synthetic_proxy_candidates.py --compare v7=... --compare v8=... --compare v9=... --ordered-aliases v7 v8 v9 --output-json reports/eval/synthetic_proxy_search_v7_v8_v9_on_default/summary.json`
- `.\python.exe scripts/data/build_metadata_focused_manifest.py --input-manifest data/synthetic/val_manifest.jsonl --output-manifest data/synthetic/val_manifest_guodegang_proxy_v1.jsonl ...`
- `.\python.exe scripts/data/build_metadata_focused_manifest.py --input-manifest data/synthetic/train_manifest.jsonl --output-manifest data/synthetic/train_manifest_guodegang_proxy_v1.jsonl ...`
- 已完成：
  - `stage2 vs v7/v8/v9` on `guodegang_proxy_v1`
  - `v7 vs v8` on `guodegang_proxy_v1`
  - `v8 vs v9` on `guodegang_proxy_v1`
