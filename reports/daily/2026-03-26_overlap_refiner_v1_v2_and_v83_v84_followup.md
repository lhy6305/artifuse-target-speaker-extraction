# 2026-03-26 overlap refiner `v1/v2` and `v83/v84` follow-up

## 本轮目标

`v81 vs v82` 听审已经确认：

- overlap residual leak 方向的 objective 改善还没有推到可听层；
- 继续做 `v82` 同结构 mask sweep，预期收益很低。

所以本轮直接升级机制，不再只改 branch mask，而是加显式 residual canceller：

- `overlap refiner`

目标是：

- 只在 branch 输出之后，再减一层 overlap residual speech leak；
- 尽量把 `near_real_0006 / 0009` 往更静方向推；
- 同时不把 `near_real_0003 / 0007` 这种 present keep case 再次压坏。

## 代码改动

修改：

- `src/tse_prefix/models/stft_mask_baseline.py`
- `scripts/train/train_stft_mask_baseline.py`

### 1. `branch_overlap_refine_head`

在 `STFTMaskBaseline` 里新增：

- `enable_branch_overlap_refine_head`
- `branch_overlap_refine_max_delta`

实现方式：

- 从 branch temporal features 预测一个复数 ratio；
- 默认经 `tanh` 限幅；
- 再乘 `branch_decoder_frame_gate`；
- 最后做：
  - `estimated_stft = estimated_stft - mix_stft * refine_ratio`

这不是继续调 branch mask，而是显式学习“从当前输出里减掉一部分 residual mixture 成分”。

### 2. 显式导出 branch pre-refine baseline

模型现在额外输出：

- `estimated_stft_branch_base`
- `estimated_waveform_branch_base`

作用：

- 把“refiner 之前的 branch 输出”单独保留下来；
- 这样后续可以明确比较：
  - pre-refine branch
  - post-refine branch
- 不再误把 shared base decoder 当成 refiner baseline。

### 3. refiner 训练可切到 branch pre-refine baseline

训练脚本新增：

- `--loss-use-branch-prerefine-as-primary-prediction`

作用：

- 当 refiner 打开时；
- `compute_losses()` 里的 primary prediction 可改为：
  - `estimated_waveform_branch_base`
- 而 refined output 继续作为 `extra_prediction`

这让已有的：

- `interference_extra_base_align_weight`
- `interference_extra_base_delta_projection_weight`

真正开始约束：

- “refiner 相对 branch 原输出的新增改动”

而不是去和 shared base decoder 对齐。

## 新训练

### `v83 = v81 + overlap refiner v1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v83_v81_overlap_refiner_v1_ft1`

训练口径：

- init：
  - `v81`
- 只训：
  - `branch_overlap_refine_head`
- 开：
  - `overlap_interference_extra_weight = 0.06`
  - `overlap_interference_extra_mode = residual_projection_ratio`
- 保留：
  - `reconstruction_extra`
  - `branch_protect`
  - `interference / interference_extra`

但当时还没有：

- branch pre-refine baseline
- refiner delta 对齐约束

所以它本质上是：

- 一个很强的 residual canceller；
- 但几乎只被 synthetic overlap objective 驱动。

### `v84 = v81 + overlap refiner v2 prerefine`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v84_v81_overlap_refiner_v2_prerefine_ft1_rerun2`

训练口径相对 `v83` 的新增变化：

- 打开：
  - `--loss-use-branch-prerefine-as-primary-prediction`
- 新增约束：
  - `interference_extra_base_align_weight = 0.03`
  - `interference_extra_base_delta_projection_weight = 0.02`
- 收窄 refiner 强度：
  - `branch_overlap_refine_max_delta = 0.08`
  - `overlap_interference_extra_weight = 0.04`

解释：

- `v84` 不是继续裸推 suppression；
- 而是显式要求：
  - refiner 的新增改动要更贴近 branch 原输出；
  - 而且不能把新增改动又投影回 interference。

## 结果

### A. `v83`：synthetic 巨幅前进，但 near-real 守门线明显失控

synthetic：

- `reports/eval/compare_v81_vs_v83_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `+8.5779 dB`
  - `8 / 8 improve`
- `reports/eval/compare_v81_vs_v83_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `+6.4518 dB`
  - `11 / 11 improve`
- `reports/eval/compare_v81_vs_v83_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `+5.6606 dB`
  - `16 / 16 improve`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v81_v82_v83/summary.json`
  - `combined_rank = v83 > v82 > v81 > v54`
  - 但 `present_guardrail_violation_count = 2`
  - `target_capture_regression_sample_ids = [near_real_0007]`
  - `residual_increase_sample_ids = [near_real_0003, near_real_0007]`

关键均值：

- `absent_mean_interference_capture_db = -65.974`
- `present_mean_target_capture_db = -12.878`
- `present_mean_interference_capture_db = -34.681`
- `present_mean_residual_output_share = 0.664`

解释：

- `v83` 在 `0009` 上太会“闭嘴”了；
- 但它不是安全收益，而是把 `0003 / 0007` 的 residual share 也一起推高；
- 这条结果已经足够说明：
  - overlap refiner 机制不是伪方向；
  - 但 `v1` 监督语义太宽，不能直接进听审。

### B. `v84`：把 `v83` 拉回一截，但仍未超过 `v81`

synthetic 相对 `v81` 仍然全面改善：

- `reports/eval/compare_v81_vs_v84_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `+7.3566 dB`
  - `8 / 8 improve`
- `reports/eval/compare_v81_vs_v84_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `+5.1392 dB`
  - `11 / 11 improve`
- `reports/eval/compare_v81_vs_v84_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `+4.4538 dB`
  - `16 / 16 improve`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v81_v82_v83_v84/summary.json`
  - `combined_rank = v83 > v84 > v82 > v81 > v54`
  - `guardrail_filtered_rank = v81 > v54 > v84 > v82 > v83`

`v84` 的关键均值：

- `absent_mean_interference_capture_db = -48.580`
- `present_mean_target_capture_db = -12.387`
- `present_mean_interference_capture_db = -35.240`
- `present_mean_residual_output_share = 0.626`
- `present_guardrail_violation_count = 1`
- `target_capture_regression_sample_ids = [near_real_0007]`
- `residual_increase_sample_ids = [near_real_0007]`

相对 `v83`：

- absent suppression 从 `-65.974` 回到 `-48.580`
- present residual share 从 `0.664` 回到 `0.626`
- violation 从 `2` 降到 `1`

说明：

- branch pre-refine baseline + delta guard 不是伪修复；
- 它确实把 `v83` 从“明显失控”拉回了“部分受控”。

### C. 但 `v84` 仍不值得进听审

`v84` 相对 `v81` 的逐样本：

- `near_real_0003`
  - `target_capture_db`
    - `-11.474 -> -12.413`
  - `interference_capture_db`
    - `-24.538 -> -27.446`
  - `residual_output_share`
    - `0.637 -> 0.706`
- `near_real_0006`
  - `target_capture_db`
    - `-4.830 -> -5.082`
  - `interference_capture_db`
    - `-31.249 -> -39.096`
  - `residual_output_share`
    - `0.349 -> 0.394`
- `near_real_0007`
  - `target_capture_db`
    - `-17.715 -> -19.667`
  - `interference_capture_db`
    - `-47.206 -> -39.179`
  - `residual_output_share`
    - `0.665 -> 0.779`
- `near_real_0009`
  - `interference_capture_db`
    - `-34.050 -> -48.580`
  - `residual_output_share`
    - `0.944 -> 0.998`

解释：

- `0006 / 0009` 方向上，`v84` 确实更静；
- 但 `0003 / 0007` 仍然被 refiner 一起改坏；
- 尤其 `0007`：
  - target 更弱
  - leak 反而更重
  - residual share 还更高

所以当前不值得导 `v81 vs v84` 听审包。

原因不是“主观可能打平”，而是：

- near-real guardrail 已经明确告诉我们：
  - `v84` 还没到安全线。

## 本轮裁决

1. overlap refiner 是有效机制，不是伪方向。
   - `v83 / v84` 都证明它能非常强地压 overlap leakage。

2. `v83` 已经证伪“宽触发 refiner 可以直接拿去听审”。
   - synthetic 全线大涨；
   - 但 near-real 明显坏掉。

3. `v84` 证明 refiner-specific baseline / delta guard 是必要的。
   - 它成功把 `v83` 从 `2` 条 violation 拉回 `1` 条；
   - 但还不够。

4. 当前默认不导听审，不升格 `v84`。
   - `v81` 仍是当前最健康的 guardrail-safe 候选；
   - `v84` 只是证明 refiner v2 比 v1 更受控，不代表它已经可用。

## 下一步

当前默认下一步不是继续做 `v84` 附近小权重 sweep。

应该直接改成：

- `overlap refiner v3`

默认设计方向：

1. 进一步收窄 refiner 生效范围。
   - 只允许它在：
     - high-overlap
     - weak-target
     - speech interference
     的子集上强激活
   - 对 `0007` 这类 hard-present case 继续压低 refiner activity

2. 把 refiner activation 与现有 gate / audibility target 更紧地绑定。
   - 当前虽然已经乘了 `branch_decoder_frame_gate`
   - 但这还不够区分：
     - weak-target abstain
     - hard-present keep

3. 继续把 near-real 作为先验裁决，不急着回到听审。
   - 至少要先把：
     - `present_guardrail_violation_count`
     压回 `0`
   - 才值得再导包。
