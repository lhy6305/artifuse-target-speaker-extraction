# 2026-03-28 true-absent dual-controller `v131` follow-up

## Summary

- 这轮不再扫 `absent_extra_weight` 或 `complement-head gate shaping`，
  而是改做更显式的 controller-side true-absent supervision：
  - `v131 = v126 + true-absent dual-controller absent-mix v1`
- 具体做法是：
  - 保留 `v126` 的 split local-control 主线；
  - 新开 `branch_overlap_dual_decoder_head`
    并使用 `gate_controller` apply mode；
  - 不再对 final output 直接加 absent loss，
    而是对 dual residual/controller branch
    在 true-absent local window 上做 `mixture` 对齐。
- 训练侧命中不是空转：
  - `overlap_dual = 95 / 203` train
  - `overlap_dual = 24 / 63` val
  - `overlap_dual_absent_mix_l1` 在 train / val summary 中均非零。
- 但 fixed synthetic checks relative `v126`
  四条同时全线转负，而且没有一条接近持平：
  - abstention `-3.0643 dB`
  - same-gender keep `-2.3636 dB`
  - hard-present keep `-1.9456 dB`
  - artifact proxy `-1.7674 dB`
- 裁决：
  - `v131 = reject`
  - 不补 near-real
  - `v126` 继续保持全局最佳 automatic continuation。

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v131_v126_trueabsent_dualcontroller_absentmix002_v1_ft1`
- 初始化：
  - `v126`
- teacher：
  - `v109`
- trainable：
  - `branch_overlap_dual_decoder_temporal_model`
  - `branch_overlap_dual_decoder_head`
- 训练资产：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`

### Model / routing

- `enable_branch_overlap_dual_decoder_head = true`
- `branch_overlap_dual_decoder_max_delta = 0.08`
- `branch_overlap_dual_decoder_gate_mode = complement`
- `branch_overlap_dual_decoder_source_mode = residual`
- `branch_overlap_dual_decoder_apply_mode = gate_controller`
- `branch_overlap_dual_decoder_max_blend = 0.15`
- `branch_overlap_dual_decoder_gate_floor = 0.0`

### Loss / selector

- 新增：
  - `overlap_dual_absent_mix_weight = 0.02`
- 保持为零：
  - `overlap_dual_mix_consistency_weight = 0.0`
  - `overlap_dual_residual_target_projection_weight = 0.0`
  - `absent_weight = 0.0`
  - `absent_extra_weight = 0.0`
- `overlap_dual` selector 改为只打 true absent rows：
  - `overlap_dual_focus_recipes = ['target_clean_speech']`
  - `overlap_dual_focus_patterns = ['target_absent_head', 'target_absent_tail']`
  - `overlap_dual_require_speech_interference = true`
  - `overlap_dual_require_music_interference = false`
  - `overlap_dual_require_other_interference = false`
  - `overlap_dual_min_overlap_ratio = 0.8`

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `num_samples = 8`
  - `avg_sisdr_delta_db = -3.0643 dB`
  - `improved = 0`
  - `regressed = 8`
- `same_gender_present_keep_guardrail_v1`
  - `num_samples = 11`
  - `avg_sisdr_delta_db = -2.3636 dB`
  - `improved = 0`
  - `regressed = 11`
- `hard_present_gate_keep_guardrail_v1`
  - `num_samples = 16`
  - `avg_sisdr_delta_db = -1.9456 dB`
  - `improved = 0`
  - `regressed = 16`
- `hard_present_artifact_proxy_v1`
  - `num_samples = 7`
  - `avg_sisdr_delta_db = -1.7674 dB`
  - `improved = 0`
  - `regressed = 7`

## Interpretation

- 这轮已经不是
  “true absent supervision 灌进 final output 会坏掉”
  那个旧问题；
- 它说明更进一步的事：
  - 即便 absent supervision
    只打在 dual residual/controller branch，
    只要这个 branch 最终仍通过
    `gate_controller`
    回灌到主输出路由，
    就会系统性伤到：
    - abstention
    - target-present keep
    - artifact guardrail
- 也就是说，
  `controller-side absent mix supervision`
  这条思路本体不等于安全，
  当前这版 apply / coupling 方式仍然过强。

## Conclusion

- `v131` 不是 no-op，
  也不是局部负向；
  而是四条 fixed checks
  全线同向转坏的明确 reject。
- 当前状态保持为：
  - `v126` 仍是全局最佳 automatic continuation
  - `v129` 仍是 decoupled true-absent 支线最佳 continuation
  - `v131` 只留下一个新边界：
    - 不再继续
      `overlap_dual_absent_mix_weight`
      或同构的 `gate_controller + absent-mix`
      这条接法。

## Next

1. 收口 `v131`
2. 不补 near-real，也不给听审
3. 若继续 true-absent 方向，默认只考虑更强解耦机制：
   - local-window-only apply
   - auxiliary-only / monitor-only path
   - 或不会通过 global gate 回灌 present path 的 controller route
