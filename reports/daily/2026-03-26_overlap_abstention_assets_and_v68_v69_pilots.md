# 2026-03-26 overlap-abstention 资产物化与 `v68 / v69` pilot 结果

## 本轮目标

把 `weak-target overlap abstention` 从方案层推进到可执行训练入口，并用极小 pilot 验证：

1. focused proxy / backstop selector 是否真的能驱动 objective 往“更少 speech leak / 更愿意闭嘴”移动；
2. 这种移动是否已经能在 near-real 主锚点上成立；
3. 如果没成立，问题是方向错误，还是 selector / 权重仍过宽。

## 新增资产

### focused synthetic manifests

- `data/synthetic/train_manifest_overlap_abstention_proxy_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_proxy_v1.jsonl`
  - 目标：
    - 高 overlap
    - speech-only
    - 低于 full-target 的弱目标近似
  - 规模：
    - train `127`
    - val `29`

- `data/synthetic/train_manifest_overlap_abstention_backstop_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_backstop_v1.jsonl`
  - 目标：
    - speech-only full-target keep backstop
  - 规模：
    - train `122`
    - val `38`

- `data/synthetic/train_manifest_overlap_abstention_mixed_backstop_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_mixed_backstop_v1.jsonl`
  - 目标：
    - speech+music full-target keep backstop
  - 规模：
    - train `89`
    - val `17`

### union / selector assets

新增脚本：

- `scripts/data/merge_jsonl_manifests.py`
  - 用于把多个 JSONL manifest 按 `sample_id` 做 deterministic union

产出：

- `data/synthetic/train_manifest_overlap_abstention_bundle_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_bundle_v1.jsonl`
  - 规模：
    - train `338`
    - val `84`

- `data/synthetic/train_manifest_overlap_abstention_backstop_union_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_backstop_union_v1.jsonl`
  - 规模：
    - train `211`
    - val `55`

selector sample-id 文件：

- `data/synthetic/sample_ids_overlap_abstention_proxy_v1_{train,val,all}.txt`
- `data/synthetic/sample_ids_overlap_abstention_backstop_v1_{train,val,all}.txt`
- `data/synthetic/sample_ids_overlap_abstention_mixed_backstop_v1_{train,val,all}.txt`
- `data/synthetic/sample_ids_overlap_abstention_backstop_union_v1_{train,val,all}.txt`
- `data/synthetic/sample_ids_overlap_abstention_bundle_v1_{train,val,all}.txt`

## 初始化点选择

先在新切片上重新比较 `v32 / v54 / v59`：

- `reports/eval/compare_v32_vs_v54_on_overlap_abstention_proxy_v1/summary.json`
- `reports/eval/compare_v32_vs_v59_on_overlap_abstention_proxy_v1/summary.json`
- `reports/eval/compare_v32_vs_v54_on_overlap_abstention_backstop_v1/summary.json`
- `reports/eval/compare_v32_vs_v59_on_overlap_abstention_backstop_v1/summary.json`
- `reports/eval/compare_v32_vs_v54_on_overlap_abstention_bundle_v1/summary.json`
- `reports/eval/compare_v32_vs_v59_on_overlap_abstention_bundle_v1/summary.json`
- `reports/eval/rank_residual_speech_leak_floor_v1_v32_v54_v59/summary.json`

结论：

- `v54` 与 `v59` 在 bundle / backstop 上都优于 `v32`
- 两者在最关键的 proxy 切片上都仍比 `v32` 更差
- 但 near-real `residual_speech_leak_floor_v1` 的程序打分里：
  - `v54 > v59 > v32`
  - 且 `v54` 在 `near_real_0009` 的 absent suppression 和 `near_real_0006` 的 present backstop 上都略强于 `v59`

因此本轮默认初始化点固定为：

- `v54`

## `v68 = v54 + overlap-abstention bundle pilot`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v68_v54_overlap_abstention_bundle_v1_ft1`

训练口径：

- branch-only fine-tune：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- proxy：
  - `interference_extra_weight = 0.02`
  - `absent_extra_weight = 0.25`
- backstop union：
  - `reconstruction_extra_waveform_weight = 0.01`
  - `reconstruction_extra_stft_weight = 0.005`
  - `branch_protect_guard_sisdr_weight = 0.001`

synthetic 结果，相对 `v54`：

- proxy：
  - `+1.119117 dB`
  - `23` improve
  - `6` regress
- backstop union：
  - `+2.002556 dB`
  - `51` improve
  - `4` regress
- bundle：
  - `+1.697559 dB`
  - `74` improve
  - `10` regress

对应文件：

- `reports/eval/compare_v54_vs_v68_on_overlap_abstention_proxy_v1/summary.json`
- `reports/eval/compare_v54_vs_v68_on_overlap_abstention_backstop_union_v1/summary.json`
- `reports/eval/compare_v54_vs_v68_on_overlap_abstention_bundle_v1/summary.json`

near-real 结果：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v68/summary.json`

有效收益：

- `near_real_0009`
  - interference capture:
    - `-33.385 dB -> -38.859 dB`
  - 更接近“闭嘴”
- `near_real_0006`
  - retention-minus-leak:
    - `25.740 dB -> 27.354 dB`
  - 说明泄漏确实被压下去了

失败点：

- `present_guardrail_violation_count = 2`
- 违规样本：
  - `near_real_0003`
  - `near_real_0006`
- 原因不是泄漏没降，而是：
  - target capture 回退过大
  - residual share 反而升高
  - 本质是过静 / 过度 abstain

结论：

- 方向成立
- 但当前 proxy + weight 组合过猛
- 已进入“调参区”，不是“路走错”

## `v69 = 从 v68 回调 suppression、加强 backstop keep`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v69_v68_overlap_abstention_rebalance_v1_ft1`

相对 `v68` 的主要改动：

- `interference_extra_weight`
  - `0.02 -> 0.01`
- `absent_extra_weight`
  - `0.25 -> 0.10`
- `reconstruction_extra_waveform_weight`
  - `0.01 -> 0.02`
- `reconstruction_extra_stft_weight`
  - `0.005 -> 0.01`
- `branch_protect_guard_sisdr_weight`
  - `0.001 -> 0.003`

synthetic 结果，相对 `v54`：

- proxy：
  - `+1.450197 dB`
  - `26` improve
  - `1` regress
- backstop union：
  - `+2.402918 dB`
  - `50` improve
  - `3` regress
- bundle：
  - `+2.074002 dB`
  - `76` improve
  - `4` regress

对应文件：

- `reports/eval/compare_v54_vs_v69_on_overlap_abstention_proxy_v1/summary.json`
- `reports/eval/compare_v54_vs_v69_on_overlap_abstention_backstop_union_v1/summary.json`
- `reports/eval/compare_v54_vs_v69_on_overlap_abstention_bundle_v1/summary.json`

near-real 结果：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v68_v69/summary.json`

变化：

- 相比 `v68`
  - `near_real_0003 / 0006`
    target capture 有所回收
  - `near_real_0009`
    absent suppression 仍明显优于 `v54`
    但略弱于 `v68`

仍然失败：

- `present_guardrail_violation_count = 3`
- 违规样本：
  - `near_real_0003`
  - `near_real_0006`
  - `near_real_0007`

结论：

- `v69` 没有把 `v68` 的真实 guardrail 问题修回来
- synthetic 大幅提升仍然存在
- 说明当前更大的问题不是“训练没学到”，而是：
  - overlap-abstention proxy 仍然过宽
  - 它把一些 near-real present anchor 也推向了过度静音

## 本轮总裁决

### 已确认成立的事

1. `weak-target overlap abstention` 不是空想，objective 可被这条训练线显著驱动。
2. 新 proxy / backstop bundle 不是无效资产，能够稳定推动 synthetic 指标。
3. `v54` 作为初始化点优于 `v59`。

### 已确认不成立的事

1. 不能直接用当前 `proxy_v1 + backstop_union_v1` 放行训练。
2. 不能因为 synthetic bundle 大幅正收益，就认为 near-real `0003 / 0006 / 0007 / 0009` 已转正。
3. 当前 `v68 / v69` 都还不够进入 GUI 听审阶段。

### 当前最准确的判断

这轮训练的价值，不是“已经找到可听新赢家”，而是把下一步问题收窄成了：

- 不是继续找别的旧 checkpoint
- 也不是否定 overlap-abstention
- 而是必须把 `proxy_v1` 收窄成更贴近
  - `低可辨目标`
  - `但不误杀 near_real_0003 / 0006 / 0007`
  的新 selector

## 下一步默认计划

下一步不再继续扫 `v68 / v69` 的权重近邻，而是先改 selector：

1. 构建 `overlap_abstention_proxy_v2`
   - 收窄 `max_target_ratio`
   - 优先更低 ratio bucket
   - 减少会把可用 target-present case 一起拉成静音的样本
2. 继续保留：
   - `backstop_union_v1`
   - `v54` 初始化
   - dual-head branch-only 微调
3. 新一轮 pilot 只在下列 gate 放行：
   - `near_real_0009` 继续比 `v54` 更安静
   - `near_real_0006` 不再触发 target-capture regression
   - `near_real_0003` 不再出现当前这种明显过静

## 本轮产物清单

代码：

- `scripts/data/merge_jsonl_manifests.py`

synthetic assets：

- `data/synthetic/train_manifest_overlap_abstention_bundle_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_bundle_v1.jsonl`
- `data/synthetic/train_manifest_overlap_abstention_backstop_union_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_backstop_union_v1.jsonl`
- `data/synthetic/sample_ids_overlap_abstention_*`

checkpoints：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v68_v54_overlap_abstention_bundle_v1_ft1`
- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v69_v68_overlap_abstention_rebalance_v1_ft1`

evaluation：

- `reports/eval/compare_v54_vs_v68_on_overlap_abstention_proxy_v1/summary.json`
- `reports/eval/compare_v54_vs_v68_on_overlap_abstention_backstop_union_v1/summary.json`
- `reports/eval/compare_v54_vs_v68_on_overlap_abstention_bundle_v1/summary.json`
- `reports/eval/compare_v54_vs_v69_on_overlap_abstention_proxy_v1/summary.json`
- `reports/eval/compare_v54_vs_v69_on_overlap_abstention_backstop_union_v1/summary.json`
- `reports/eval/compare_v54_vs_v69_on_overlap_abstention_bundle_v1/summary.json`
- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v68/summary.json`
- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v68_v69/summary.json`
