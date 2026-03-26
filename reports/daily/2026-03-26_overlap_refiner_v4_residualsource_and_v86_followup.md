# 2026-03-26 overlap refiner `v4 residual-source` and `v86` follow-up

## 本轮目标

`v85` 已经说明：

- `gate-complement` 是当前最有效的 refiner 激活语义；
- 但它虽然在 objective / near-real guardrail 上都是前沿，
  仍然没有转成可听层收益；
- 特别是 `near_real_0009` 上，人耳明确偏向 `v81`，而不是自动更强的 `v85`。

所以本轮不再做权重 sweep，也不再改 gate target 曲线，只改一件事：

- refiner 不再直接减 `mixture * ratio`
- 改成减 `residual-source * ratio`

这里的 residual-source 定义为：

- `mix_stft - estimated_stft_branch_base`

目的：

- 让 refiner 优先清理 branch base 输出之外的残余成分；
- 尽量减少对已保住的目标主体直接下手；
- 看能否把 `v85` 那种“自动更静，但人耳不一定更好”的过激 suppression 往回收一截。

## 代码改动

修改：

- `src/tse_prefix/models/stft_mask_baseline.py`
- `scripts/train/train_stft_mask_baseline.py`

新增参数：

- `branch_overlap_refine_source_mode`
  - `mixture`
  - `branch_base`
  - `residual`

当前 `v86` 用的是：

- `branch_overlap_refine_source_mode = residual`
- `branch_overlap_refine_gate_mode = complement`

含义：

- refiner 仍只在 `(1 - gate)` 区域激活；
- 但实际被减掉的，不再是整段 mixture，而是 branch-base 之外的剩余 STFT。

## 新训练

### `v86 = v81 + overlap refiner v4 residual-source gate-complement`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v86_v81_overlap_refiner_v4_residualsource_gatecomplement_ft1`

训练口径：

- init：
  - `v81`
- 只训：
  - `branch_overlap_refine_head`
- train / val：
  - `abstention_gate_bundle_v2`
- 保持 `v85` 的安全约束：
  - `branch_overlap_refine_max_delta = 0.08`
  - `interference_extra_base_align_weight = 0.03`
  - `interference_extra_base_delta_projection_weight = 0.02`
  - `overlap_interference_extra_weight = 0.04`
  - `overlap_interference_extra_loss_mode = residual_projection_ratio`
  - `use_branch_prerefine_as_primary_prediction = true`
- overlap focused selector 保持不变：
  - `target_full`
  - `speech_interference_clean_pool / speech_interference_hard_pool`
  - `0.05 <= target_energy_ratio <= 0.22`
  - `overlap_ratio >= 0.6`
  - `target_transient_presence_share_mean <= 0.04`

本轮唯一核心变量就是：

- `refine_source: mixture -> residual`

## 结果

### A. 相对 `v81`：三条 synthetic 仍然全正

- `reports/eval/compare_v81_vs_v86_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = +3.5979`
  - `8 / 8 improve`
- `reports/eval/compare_v81_vs_v86_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +1.6103`
  - `8 improve / 3 near tie / 0 regress`
- `reports/eval/compare_v81_vs_v86_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +1.7029`
  - `15 improve / 1 near tie / 0 regress`

解释：

- `v86` 不是回到 no-op；
- residual-source refiner 仍然保留了真实有效的清理能力。

### B. 相对 `v85`：objective 前沿会让回一部分

- `reports/eval/compare_v85_vs_v86_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -1.1510`
  - `0 improve / 7 regress`
- `reports/eval/compare_v85_vs_v86_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = -0.5616`
  - `0 improve / 8 regress`
- `reports/eval/compare_v85_vs_v86_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = -0.6669`
  - `0 improve / 15 regress`

解释：

- `v86` 不是新的 objective frontier；
- 它本质上是把 `v85` 的 refiner 收窄了一档；
- 但这正符合本轮目的，因为 `v85` 的问题恰恰是 absent 侧可能过激。

### C. near-real：仍然 `0 violation`，并且位置介于 `v81` 和 `v85` 之间

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v81_v85_v86/summary.json`

关键均值：

- `v81`
  - absent interference capture
    - `-34.050`
  - present target capture
    - `-11.340`
  - present interference capture
    - `-34.331`
- `v85`
  - absent interference capture
    - `-45.111`
  - present target capture
    - `-11.488`
  - present interference capture
    - `-38.047`
- `v86`
  - absent interference capture
    - `-38.892`
  - present target capture
    - `-11.428`
  - present interference capture
    - `-39.410`

guardrail：

- `v86`
  - `present_guardrail_violation_count = 0`
  - `target_capture_regression_sample_ids = []`
  - `residual_increase_sample_ids = []`

解释：

- `v86` 让回了 `v85` 在 `0009` 上最激进的 suppression；
- 但 present 侧没有掉回 `v81`，反而整体 leak capture 仍明显更低。

### D. 逐样本：`0009` 更保守，`0007` 更强

相对 `v81`：

- `near_real_0009`
  - `interference_capture_db`
    - `-34.050 -> -38.892`
  - 仍明显更静
  - 但不像 `v85` 那样推到 `-45.111`
- `near_real_0007`
  - `target_capture_db`
    - `-17.715 -> -17.946`
  - `interference_capture_db`
    - `-47.206 -> -57.693`
  - `retention_minus_leak_db`
    - `+10.256 dB`
- `near_real_0006`
  - `target_capture_db`
    - 仅 `-0.013 dB`
  - `interference_capture_db`
    - `-29.849 -> -33.012`
- `near_real_0003`
  - 基本近似打平，只是轻微更干净

解释：

- `v86` 最像“把 `v85` 的 absent 过推往回拉一点，但保住 present 清理能力”的版本；
- 这正是当前最值得给人耳再确认的一类候选。

## focused 听审包

我已经把 `v81 vs v86` near-real 包导好：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind`

资产审计：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind/asset_audit_summary.json`
  - `all_mono = true`
  - `all_have_target = true`

tradeoff 先验：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind/tradeoff_analysis/summary.json`
  - `more_interference_leaky`
    - `v81 = 3`
    - `tie = 1`
  - `better_retention_minus_leak`
    - `v86 = 2`
    - `tie = 1`
    - `not_applicable = 1`

bandwidth 先验：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind/bandwidth_analysis/summary.json`
  - `narrower_candidate_counts = tie: 4`

解释：

- 自动先验和 `v81 vs v85` 相似：
  - present 侧 `v86` 更干净；
  - absent 侧 `v86` 也更静；
- 但这次 `v86` 比 `v85` 更保守，
  所以它更值得验证是否更贴近人耳偏好。

## 本轮裁决

1. residual-source refiner 是有效机制。
   - 它不是 no-op；
   - 相对 `v81` 仍然带来稳定 synthetic 与 near-real 清理收益。

2. `v86` 不是新的 objective frontier。
   - 自动上它仍落后于 `v85`；
   - 所以这轮不是“自动全面变强”。

3. `v86` 是当前最值得继续做人耳确认的新候选。
   - 它把 `v85` 的 absent 过激 suppression 往回收；
   - 同时保留了 `0006 / 0007` 上相对 `v81` 的明显清理收益；
   - 这比继续在 `v85` 周边做小 sweep 更有价值。

## 下一步

当前默认下一步是直接听：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v86_blind
```

重点盯：

- `near_real_0009`
  - `v86` 是否比 `v85` 更接近人耳可接受的 absent 行为
  - 同时又是否真比 `v81` 更干净
- `near_real_0007`
  - `v86` 在更强 suppression 下有没有变空、变假、变糊
- `near_real_0006`
  - overlap 段有没有真正更干净
- `near_real_0003`
  - 是否仍保持基本打平而不引入副作用
