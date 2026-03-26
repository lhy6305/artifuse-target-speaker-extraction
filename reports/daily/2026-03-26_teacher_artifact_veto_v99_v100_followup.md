# 2026-03-26 teacher artifact veto v99/v100 follow-up

## 本轮目标

- 在不放大 `v95` 式 hard-present artifact risk 的前提下，
  继续保留 overlap suppression 收益；
- 判断是否存在值得进入 focused 听审的新候选。

## 新机制

### `v99`: self-align veto probe

新增：

- `branch_protect_overlap_base_align_l1`

接线文件：

- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`

结果：

- 对 `v95` 这条 `branch_overlap_cancel_apply_mode = auxiliary_only` 家族，
  train / val 上该 loss 都严格为 `0.0`；
- 这不是权重问题，而是结构性 no-op：
  - final output 与 `branch_base` 本来就是同一路输出。

裁决：

- `v99` 仅保留为机制诊断 probe，不作为候选。

### `v100`: frozen teacher artifact veto

新增：

- `branch_protect_teacher_overlap_l1`
- `--teacher-checkpoint`

接线文件：

- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`

教师 checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v81_v79_audibility_gate_target_v1_ft1/best.pt`

候选 checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v100_v95_teacher_artifact_veto_v1_ft1`

训练中确认：

- `branch_protect_teacher_overlap_l1` 在 train / val 上都稳定非零；
- 说明 teacher veto 在当前家族上是真实生效的。

## 自动验收

### synthetic

相对 `v81`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `+3.7461 dB`
  - `7 improve / 1 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+1.7647 dB`
  - `10 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.2559 dB`
  - `15 improve / 1 regress`

结论：

- `v100` 是 relative `v81` 的全量 synthetic 正收益候选。

### near-real objective

非盲分析包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100`

核心结果：

- `more_interference_leaky_label`
  - `v81 = 4`
  - `v100 = 0`
- `better_retention_minus_leak_label`
  - `v100 = 2`
  - `tie = 1`
  - `not_applicable = 1`

解释：

- `0009`
  - `v100` suppression 更强
- `0003`
  - `v100` retention-minus-leak 更优
- `0006`
  - tradeoff 基本打平，但 leak 仍更低
- `0007`
  - objective 上仍偏向“更静”，需要人耳终裁是否引入新伪影

### bandwidth

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100/bandwidth_analysis/summary.json`

结果：

- `narrower_candidate_counts = tie: 2, file_a: 2`
- 这里 `file_a = v81`

解释：

- 没有出现 `v100` 更窄带的黄灯；
- heuristic 上反而是 `v81` 在 `0007 / 0009` 更像窄带侧。

## 分析脚本修正

本轮修正：

- `scripts/eval/gate_near_real_tradeoff.py`

修正前：

- focused subset pack 若缺少 `target_present__none`，
  会被直接写成 `missing_bucket -> fail`

修正后：

- `target_present__none` 改为 optional bucket；
- 对当前 `residual_speech_leak_floor_v1` 这类不含 raw-only target-present 样本的 pack，
  缺失该 bucket 不再伪造 `overall_pass = false`

修正后 gate 结果：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100/tradeoff_analysis/decision_gate_summary.json`
  - `overall_pass = true`

## 当前裁决

- `v99`
  - 结构性 no-op probe，淘汰
- `v100`
  - 当前值得进入 focused 听审
  - 原因是它第一次把 `v95` 这条 stronger suppression 家族推进到了：
    - synthetic 全量正收益
    - near-real objective gate 通过
    - bandwidth 无明确黄灯

## 下一步

blind 包已导出：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100_blind`

并已补齐：

- `asset_audit_summary.json`
- `tradeoff_analysis/summary.json`
- `tradeoff_analysis/decision_gate_summary.json`
- `bandwidth_analysis/summary.json`

下一步直接做人耳终裁：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100_blind
```

重点盯：

- `near_real_0007`
  - teacher veto 是否真的把 `v95` 式伪影压住了
- `near_real_0006`
  - 更强 suppression 是否终于转化成可感知更干净
- `near_real_0009`
  - 更强 suppression 是否仍符合“宁可闭嘴”的主观偏好
