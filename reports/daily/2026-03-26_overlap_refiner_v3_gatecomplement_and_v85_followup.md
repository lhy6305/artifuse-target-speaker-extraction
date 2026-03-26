# 2026-03-26 overlap refiner `v3 gate-complement` and `v85` follow-up

## 本轮目标

上一轮 `v84` 已经说明：

- overlap refiner `v2` 比 `v1` 更受控；
- 但 refiner 仍会把 `near_real_0006 / 0009` 的 suppression 收益
  和
- `near_real_0007` 的 keep 回退

一起带出来。

所以本轮不再继续做 `v84` 附近权重 sweep，而是只改 refiner 的激活语义：

- 从 `refiner * gate`
- 改成 `refiner * (1 - gate)`

目标是：

- 让 refiner 只在 gate 已经倾向闭嘴的区间强激活；
- 对 hard-present keep case 自动收手；
- 不再让 refiner 在“该保留目标”的区域里大幅改写输出。

## 代码改动

修改：

- `src/tse_prefix/models/stft_mask_baseline.py`
- `scripts/train/train_stft_mask_baseline.py`

新增：

- `branch_overlap_refine_gate_mode`
  - `none`
  - `gate`
  - `complement`

当前 `v3` 用的是：

- `branch_overlap_refine_gate_mode = complement`

也就是：

- `branch_overlap_refine_ratio *= (1 - branch_decoder_frame_gate)`

解释：

- `v81` 的 gate 已经是当前最健康的 audibility 语义载体；
- 当 gate 较低时，通常对应：
  - weak target
  - more abstain-like
- 这正是更允许 refiner 出手的区域；
- 当 gate 较高时，则更像：
  - keep / hard-present
- 此时 refiner 会被自动压低。

## 新训练

### `v85 = v81 + overlap refiner v3 gate-complement`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v85_v81_overlap_refiner_v3_gatecomplement_ft1`

训练口径：

- init：
  - `v81`
- 只训：
  - `branch_overlap_refine_head`
- 保留 `v84` 的 refiner 安全约束：
  - `--loss-use-branch-prerefine-as-primary-prediction`
  - `interference_extra_base_align_weight = 0.03`
  - `interference_extra_base_delta_projection_weight = 0.02`
- 保留 overlap focused selector：
  - `target_full`
  - `speech_interference_clean_pool / speech_interference_hard_pool`
  - `overlap_ratio >= 0.6`
  - `0.05 <= target_energy_ratio <= 0.22`
  - `target_transient_presence_share_mean <= 0.04`
- 保持：
  - `branch_overlap_refine_max_delta = 0.08`
  - `overlap_interference_extra_weight = 0.04`

因此本轮唯一核心变量就是：

- refiner 的 gate-scaling 语义

## 结果

### A. synthetic：仍然全面优于 `v81`

- `reports/eval/compare_v81_vs_v85_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = +4.7489`
  - `8 / 8 improve`
- `reports/eval/compare_v81_vs_v85_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +2.1718`
  - `10 improve / 1 near tie / 0 regress`
- `reports/eval/compare_v81_vs_v85_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +2.3698`
  - `15 improve / 1 near tie / 0 regress`

解释：

- `v85` 不像 `v84` 那样一味猛推；
- 但也没有把 synthetic 收益完全让回去；
- 它更像是“收益变小，但 still 全面为正”。

### B. near-real：第一次把 overlap refiner 拉回 `0 violation`

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v81_v82_v83_v84_v85/summary.json`

关键结果：

- `combined_rank`
  - `v83 > v84 > v85 > v82 > v81 > v54`
- 但真正重要的是：
  - `guardrail_filtered_rank = v85 > v81 > v54 > v84 > v82 > v83`

`v85` 关键均值：

- `absent_mean_interference_capture_db = -45.111`
- `present_mean_target_capture_db = -11.488`
- `present_mean_interference_capture_db = -38.047`
- `present_mean_residual_output_share = 0.5689`
- `present_guardrail_violation_count = 0`
- `target_capture_regression_sample_ids = []`
- `residual_increase_sample_ids = []`

解释：

- 这是第一条 overlap refiner pilot：
  - 既保住 `0` violation
  - 又把 absent / weak-overlap suppression 明显推高。

### C. 相对 `v81` 的逐样本

- `near_real_0003`
  - `target_capture_db`
    - `-11.474 -> -11.506`
  - `interference_capture_db`
    - `-24.538 -> -25.239`
  - `residual_output_share`
    - `0.637 -> 0.642`
- `near_real_0006`
  - `target_capture_db`
    - `-4.830 -> -4.852`
  - `interference_capture_db`
    - `-31.249 -> -39.476`
  - `residual_output_share`
    - `0.349 -> 0.361`
- `near_real_0007`
  - `target_capture_db`
    - `-17.715 -> -18.107`
  - `interference_capture_db`
    - `-47.206 -> -49.424`
  - `residual_output_share`
    - `0.665 -> 0.703`
- `near_real_0009`
  - `interference_capture_db`
    - `-34.050 -> -45.111`
  - `residual_output_share`
    - `0.944 -> 0.996`

解释：

- `0006 / 0009` 的 suppression 收益非常明确；
- `0003` 基本近似打平；
- `0007` 虽然 target capture 略降、residual share 略升，但 interference 也更低，且没有越过当前 guardrail。

这就是 `v85` 能到 `guardrail_filtered_rank = 1st` 的原因：

- 它不再像 `v84` 那样只会靠牺牲 `0007` 换取 `0006 / 0009`。

## focused 听审包

我已经把 `v81 vs v85` near-real 包导好了：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind`

资产审计：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind/asset_audit_summary.json`
  - `all_mono = true`
  - `all_have_target = true`

tradeoff 先验：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind/tradeoff_analysis/summary.json`
  - `more_interference_leaky`
    - `v81 = 3`
    - `tie = 1`
  - `better_retention_minus_leak`
    - `v85 = 2`
    - `tie = 1`
    - `not_applicable = 1`

解释：

- 自动分析已经给出明确先验：
  - `v85` 至少不是“更漏”的那个；
  - 在 2 条 present case 上它有更好的 retention-vs-leak tradeoff。

bandwidth 先验：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind/bandwidth_analysis/summary.json`
  - `narrower_candidate_counts = tie: 4`

解释：

- 当前没有明显窄带黄灯；
- 这次听审可以更专注盯：
  - leakage
  - keep
  - artifact

## 本轮裁决

1. `overlap refiner v3 gate-complement` 是当前最有效的 refiner 机制。
   - 它第一次把 overlap refiner 拉回 near-real `0 violation`。

2. `v85` 是当前第一条值得进 focused 听审的 refiner checkpoint。
   - 和 `v83 / v84` 不同；
   - 这次不是“objective 很强但不安全”，而是：
     - objective 仍明显更强
     - near-real 也已过 guardrail

3. 当前默认不再继续做自动 sweep。
   - 最合理的下一步是：
     - `v81 vs v85` GUI 听审
   - 先确认这些收益有没有推进到可听层。

## 下一步

直接开 GUI 听：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v85_blind
```

重点盯：

- `near_real_0006`
  - overlap 段有没有更干净
  - target 有没有变空
- `near_real_0009`
  - absent 情况下是不是更接近真正闭嘴
- `near_real_0007`
  - 有没有为了更静而牺牲掉可用目标
- `near_real_0003`
  - 是否仍基本打平
