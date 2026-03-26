# 2026-03-26 hard-present gate keep guardrail `v1` and `v80` follow-up

## 本轮目标

上一轮已经确认：

- `v79` 确实能把 `near_real_0006 / 0009` 往更静方向推进；
- 但它重新伤到了 `near_real_0007` 这条 hard-present backstop。

所以本轮不再继续扫普通 gate 权重，而是先把更宽的 keep 侧约束真正接进训练：

- 物化 `hard_present_gate_keep_guardrail_v1`
- 合并成 `gate_keep_union_v2`
- 用它替换窄的 keep selector，验证是否能在保住 `v79` 的 abstention 收益同时把 `0007` 拉回来

## 新增资产

### 1. `hard_present_gate_keep_guardrail_v1`

文件：

- `data/synthetic/train_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
- `data/synthetic/val_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
- `data/synthetic/sample_ids_hard_present_gate_keep_guardrail_v1_train.txt`
- `data/synthetic/sample_ids_hard_present_gate_keep_guardrail_v1_val.txt`
- `reports/data/selector_hard_present_gate_keep_guardrail_v1_train_summary.json`
- `reports/data/selector_hard_present_gate_keep_guardrail_v1_val_summary.json`

过滤口径：

- `recipe in {target_hard_speech, target_clean_plus_music, target_hard_plus_music}`
- `target_full`
- `0.05 <= target_energy_ratio <= 0.30`
- `target_transient_presence_share_mean <= 0.05`

规模：

- train `54`
- val `16`

### 2. `gate_keep_union_v2`

文件：

- `data/synthetic/train_manifest_gate_keep_union_v2.jsonl`
- `data/synthetic/val_manifest_gate_keep_union_v2.jsonl`
- `data/synthetic/sample_ids_gate_keep_union_v2_train.txt`
- `data/synthetic/sample_ids_gate_keep_union_v2_val.txt`
- `reports/data/merge_gate_keep_union_v2_train_summary.json`
- `reports/data/merge_gate_keep_union_v2_val_summary.json`

组成：

- `same_gender_present_keep_guardrail_v1`
- `hard_present_gate_keep_guardrail_v1`

规模：

- train `63`
- val `27`

### 3. `abstention_gate_bundle_v2`

文件：

- `data/synthetic/train_manifest_abstention_gate_bundle_v2.jsonl`
- `data/synthetic/val_manifest_abstention_gate_bundle_v2.jsonl`
- `data/synthetic/sample_ids_abstention_gate_bundle_v2_train.txt`
- `data/synthetic/sample_ids_abstention_gate_bundle_v2_val.txt`
- `reports/data/merge_abstention_gate_bundle_v2_train_summary.json`
- `reports/data/merge_abstention_gate_bundle_v2_val_summary.json`

组成：

- `abstention_gate_proxy_v1`
- `gate_keep_union_v2`

规模：

- train `102`
- val `33`

## 新训练

### `v80 = v79 + keep_union_v2`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v80_v79_abstention_gate_keepunion_v2_ft1`

训练口径：

- init：`v79`
- 只训：
  - `branch_decoder_gate_head`
- train / val：
  - `abstention_gate_bundle_v2`
- keep selector：
  - `reconstruction_extra_focus_sample_ids = sample_ids_gate_keep_union_v2_train`
  - `branch_protect_focus_sample_ids = sample_ids_gate_keep_union_v2_train`
- abstain 侧保持：
  - `target_energy_ratio <= 0.20`
  - `target_transient_presence_share_mean <= 0.03`
  - `target_transient_presence_minus_mid_db_mean <= -10`
- gate loss：
  - `gate_abstain_weight = 0.12`
  - `gate_keep_weight = 0.03`

训练期信号：

- train `gate_abstain_mean`
  - 最终约 `0.1706`
- train `gate_keep_mean`
  - 最终约 `0.7193`

需要单独记一条：

- `val_selector_metrics.branch_protect.selected_count = 0`
- `val_selector_metrics.reconstruction_extra.selected_count = 0`

原因不是代码坏了，而是：

- 当前 keep focus 走的是 train sample-id union；
- `bundle_v2` 的 val manifest 不复用 train sample id；
- 所以 val loss 本身并不能代表 keep 约束是否真的泛化。

这轮 keep 是否成立，只能看外部 guardrail。

## 结果

### A. synthetic abstention proxy：`v80` 比 `v79` 更偏闭嘴

- `reports/eval/compare_v79_vs_v80_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -1.0106`
  - `1` improve / `7` regress

解释：

- `v80` 明显没有把 `v79` 拉回更 balanced 的状态；
- 它在旧 abstention proxy 上反而继续向“更静音”一侧走。

### B. same-gender keep guardrail：没有被救回来

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v78_v79_v80/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v78 = 0`
    - `v79 = 11`
    - `v80 = 11`
  - `present_mean_target_capture_db`
    - `v79 = -23.696`
    - `v80 = -25.266`

解释：

- `v80` 没有降低 violation 数；
- 而且 target capture 还比 `v79` 更差。

### C. hard-present keep guardrail：同样没有被救回来

- `reports/eval/rank_hard_present_gate_keep_guardrail_v1_v54_v78_v79_v80/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v78 = 0`
    - `v79 = 16`
    - `v80 = 16`
  - `present_mean_target_capture_db`
    - `v79 = -25.727`
    - `v80 = -27.820`

解释：

- 更宽的 keep union 没有形成真正的 keep 约束；
- `v80` 在 hard-present 上反而更静了。

### D. near-real residual leak floor：`0006 / 0009` 更静，但 `0007` 更坏

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v78_v79_v80/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v78 = 0`
    - `v79 = 1`
    - `v80 = 1`
  - `absent_mean_interference_capture_db`
    - `v79 = -36.617`
    - `v80 = -38.642`

逐样本：

- `near_real_0003`
  - `target_capture_db`
    - `v79 = -11.512`
    - `v80 = -11.539`
  - 基本持平
- `near_real_0006`
  - `interference_capture_db`
    - `v79 = -36.393`
    - `v80 = -39.064`
  - `v80` 更静
- `near_real_0007`
  - `target_capture_db`
    - `v79 = -22.369`
    - `v80 = -26.456`
  - `v80` 更坏
- `near_real_0009`
  - `interference_capture_db`
    - `v79 = -36.617`
    - `v80 = -38.642`
  - `v80` 更静

解释：

- `v80` 不是把 `v79` 的 hard-present regression 修好；
- 而是把 `v79` 的“更静”趋势继续向前推。

## 本轮裁决

1. `hard_present_gate_keep_guardrail_v1` 作为 guardrail 资产是成立的。
   - 它能稳定揭示 `v79 / v80` 这一类 over-silence regression。
2. `v80` 不能放行。
   - 虽然 `0006 / 0009` 更静，但 keep 侧没有任何真正修复。
3. 仅仅把 keep 样本覆盖面从 `same_gender_present_keep_guardrail_v1` 扩成 `keep_union_v2`，不足以解决问题。
   - 当前失败点已经不是“keep 数据太窄”；
   - 而是 `gate target` 的语义仍然太粗。

## 下一步

下一步不应继续做 `v81 / v82` 这种同结构 sweep，也不应再押“更宽 keep union”。

更合理的下一步是：

1. 把当前二元 gate supervision 改成 `audibility-conditioned gate target`
   - hard-present keep：强推 `1`
   - medium present keep：高 keep target
   - weak-target overlap abstain：强推 `0`
   - 中间灰区：不要再用完全二元目标
2. 尽量避免只靠 train sample-id 做 keep selector
   - 让 val / guardrail 也能共享同一套 gate target 语义
3. 新训练仍固定同时验：
   - `overlap_abstention_proxy_v4_audibility_v1`
   - `same_gender_present_keep_guardrail_v1`
   - `hard_present_gate_keep_guardrail_v1`
   - `real_eval_manifest_residual_speech_leak_floor_v1`
