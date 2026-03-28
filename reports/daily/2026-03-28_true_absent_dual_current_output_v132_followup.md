# 2026-03-28 true-absent dual current-output `v132` follow-up

## Summary

- `v131` 已经证明：
  - true-absent supervision
    即便改打到 dual residual/controller branch，
    只要最终仍通过 `gate_controller`
    回灌主输出，
    就会系统性伤 guardrail。
- 这轮改成更温和的局部输出接法：
  - `v132 = v126 + true-absent dual current-output absent-mix v1`
  - 核心变化只有一处：
    - dual decoder 不再
      `gate_controller`
      重算全局输出；
    - 改为把当前 `v126` 输出
      用 dual target 做局部 blend：
      - `estimated_stft <- estimated_stft + blend * (dual_target - estimated_stft)`
- 目标是验证：
  - 问题是否只在 `global gate recoupling`
  - 如果改成 current-output local blend，
    能否保住 fixed guardrail。
- 结果是否定的：
  - relative `v126`
    四条 fixed synthetic checks
    再次全线转负，
    而且 abstention 比 `v131` 更差：
    - abstention `-6.6014 dB`
    - same-gender keep `-1.3396 dB`
    - hard-present keep `-2.3761 dB`
    - artifact proxy `-2.4415 dB`
- 裁决：
  - `v132 = reject`
  - 不补 near-real
  - `v126` 继续保持全局最佳 automatic continuation。

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v132_v126_trueabsent_dualcurrentoutput_absentmix002_v1_ft1`
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

- 与 `v131` 保持一致，仅改：
  - `branch_overlap_dual_decoder_apply_mode = current_output`
- 其余 dual 设置不变：
  - `branch_overlap_dual_decoder_max_delta = 0.08`
  - `branch_overlap_dual_decoder_gate_mode = complement`
  - `branch_overlap_dual_decoder_source_mode = residual`
  - `branch_overlap_dual_decoder_max_blend = 0.15`
  - `branch_overlap_dual_decoder_gate_floor = 0.0`

### Loss / selector

- 与 `v131` 保持一致：
  - `overlap_dual_absent_mix_weight = 0.02`
  - `overlap_dual_focus_recipes = ['target_clean_speech']`
  - `overlap_dual_focus_patterns = ['target_absent_head', 'target_absent_tail']`
  - `overlap_dual_require_speech_interference = true`
  - `overlap_dual_require_music_interference = false`
  - `overlap_dual_require_other_interference = false`
  - `overlap_dual_min_overlap_ratio = 0.8`
- selector 命中仍然有效：
  - train `95 / 203`
  - val `24 / 63`

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `num_samples = 8`
  - `avg_sisdr_delta_db = -6.6014 dB`
  - `improved = 0`
  - `regressed = 8`
- `same_gender_present_keep_guardrail_v1`
  - `num_samples = 11`
  - `avg_sisdr_delta_db = -1.3396 dB`
  - `improved = 0`
  - `regressed = 9`
- `hard_present_gate_keep_guardrail_v1`
  - `num_samples = 16`
  - `avg_sisdr_delta_db = -2.3761 dB`
  - `improved = 1`
  - `regressed = 15`
- `hard_present_artifact_proxy_v1`
  - `num_samples = 7`
  - `avg_sisdr_delta_db = -2.4415 dB`
  - `improved = 0`
  - `regressed = 7`

## Interpretation

- `v132` 说明：
  - 问题不只在
    `gate_controller`
    这种 global gate recoupling；
  - 即便 dual target
    只对当前输出做局部 blend，
    只要这条 absent-supervised dual path
    仍然直接改 final output，
    abstention / keep / artifact
    guardrail 还是会被系统性打坏。
- 而且这轮的关键信号更明确：
  - abstention 比 `v131`
    更大幅转坏，
    说明 `current_output` 局部 blend
    并不是更安全的 soften 版，
    反而更容易把 absent-target rewrite
    直接写进最终输出。

## Conclusion

- `v132` 不是 no-op，
  也不是 `v131` 的轻微变体噪声；
  它是另一个独立的负向证据：
  - `dual target -> final output`
    不管是
    `gate_controller`
    还是
    `current_output local blend`
    都会打坏当前 guardrail。
- 当前状态保持为：
  - `v126` 仍是全局最佳 automatic continuation
  - `v129` 仍是 decoupled true-absent 支线最佳 continuation
  - `v131 / v132`
    共同收口了
    “dual absent-supervised branch 直接改 final output”
    这条家族。

## Next

1. 收口 `v132`
2. 不补 near-real，也不给听审
3. 若继续 true-absent 方向，默认不能再做：
   - `gate_controller + absent-mix`
   - `current_output + absent-mix`
4. 下一轮若继续，只应考虑更强解耦：
   - monitor-only / auxiliary-only teacher path
   - 只在 target-absent local window 内生效、但不会直接重写 final output 的局部 apply 机制
   - 或把 absent 信号改为对现有 split-local-control 路径的间接约束，而不是新 dual path 直接接管输出
