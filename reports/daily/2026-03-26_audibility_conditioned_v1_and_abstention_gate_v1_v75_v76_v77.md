# 2026-03-26 audibility-conditioned `v1` and abstention-gate `v1` follow-up

## 本轮目标

在 `v73 / v74` 已经证明“只靠 branch-only reweighting 无法同时修好 keep 和 abstain”之后，本轮要回答三件事：

1. 只增加 `audibility-conditioned objective`，不改结构，是否足以把 `v72` 推过线。
2. 如果不够，轻量 `abstention gate` 是否能把“整体闭嘴”从频谱分离 mask 里拆出来。
3. gate 如果有信号，它更适合：
   - 和 mask 一起联训
   - 还是只训练 gate 头本身。

## 代码改动

### 1. `target_energy_ratio` 已接入训练 selector

修改：

- `src/tse_prefix/data/synthetic_dataset.py`
- `src/tse_prefix/pipeline/loss_selectors.py`
- `scripts/train/train_stft_mask_baseline.py`

已支持：

- manifest 读取 `target_energy_ratio`
- collate 输出 `target_energy_ratios`
- selector 按
  - `min_target_energy_ratio`
  - `max_target_energy_ratio`
  做切片

### 2. 轻量 branch abstention gate 已实现

修改：

- `src/tse_prefix/models/stft_mask_baseline.py`
- `scripts/train/train_stft_mask_baseline.py`

实现方式：

- 新增 `--model-enable-branch-abstention-gate`
- gate 只挂在 branch decoder 上
- gate 输出逐帧标量 `sigmoid`，再乘 branch mask
- 初始化为接近 `1.0`
  - final bias `= 4.0`

## 新增训练资产

### audibility-conditioned bundle

文件：

- `data/synthetic/train_manifest_audibility_conditioned_bundle_v1.jsonl`
- `data/synthetic/val_manifest_audibility_conditioned_bundle_v1.jsonl`
- `reports/data/merge_audibility_conditioned_bundle_v1_train_summary.json`
- `reports/data/merge_audibility_conditioned_bundle_v1_val_summary.json`

组成：

- `overlap_abstention_backstop_union_metrics_v1`
- `same_gender_reverb_proxy_v2_metrics_v1`

规模：

- train `380`
- val `141`

关键 selector 命中数：

- weak-target abstention slice
  - train `127`
  - val `31`
- medium-audibility keep slice
  - train `10`
  - val `11`

## 新训练

### 1. `v75 = v72 + audibility-conditioned objective`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v75_v72_audibility_conditioned_v1_ft1`

### 2. `v76 = v72 + audibility-conditioned objective + joint gate`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v76_v72_audibility_conditioned_v1_gate_v1_ft1`

训练口径：

- init：`v72`
- 与 `v75` 使用同一 bundle、同一 selector、同一 loss
- trainable：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
  - `branch_decoder_gate_head`

### 3. `v77 = v72 + gate-only isolate probe`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v77_v72_audibility_conditioned_v1_gateonly_v1_ft1`

训练口径：

- init：`v72`
- loss 与 `v76` 相同
- 仅训练：
  - `branch_decoder_gate_head`

## 结果

### A. `v75`：loss-only 方案失败

synthetic abstention：

- `reports/eval/compare_v72_vs_v75_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -0.1956`
  - `2` improve / `5` regress / `1` near tie

keep guardrail：

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v72_v75/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v72 = 10`
    - `v75 = 11`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v72_v75/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v72 = 2`
    - `v75 = 3`
  - 新增回退样本：
    - `near_real_0007`

裁决：

- `audibility-conditioned objective v1` 不能单独解决问题

### B. `v76`：joint gate 有真实信号，但当前训练法会过度闭嘴

synthetic abstention：

- `reports/eval/compare_v72_vs_v76_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -2.1483`
- `reports/eval/compare_v75_vs_v76_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -1.9527`

keep guardrail：

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v72_v75_v76/summary.json`
  - `present_guardrail_violation_count = 11`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v72_v75_v76/summary.json`
  - `present_guardrail_violation_count = 3`
  - 违规样本：
    - `near_real_0003`
    - `near_real_0006`
    - `near_real_0007`

关键样本级变化：

- `near_real_0009`
  - `interference_capture_db`
    - `v72 = -34.468`
    - `v76 = -44.591`
- `near_real_0006`
  - `target_capture_db`
    - `v72 = -8.941`
    - `v76 = -7.419`
  - `interference_capture_db`
    - `v72 = -34.935`
    - `v76 = -42.216`
- `near_real_0007`
  - `target_capture_db`
    - `v72 = -18.567`
    - `v76 = -29.570`

裁决：

- `v76` 不能放行
- 但 `abstention gate` 方向保留

### C. `v77`：gate-only 不再误杀 present，但基本退回 safe/no-op

synthetic abstention：

- `reports/eval/compare_v72_vs_v77_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -7.2054`
  - `1` improve / `7` regress

keep guardrail：

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v72_v76_v77/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v72 = 10`
    - `v76 = 11`
    - `v77 = 0`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v72_v76_v77/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v72 = 2`
    - `v76 = 3`
    - `v77 = 0`

逐样本：

- `near_real_0003`
  - `v77`
    - `target_capture_db = -11.470`
    - `interference_capture_db = -24.375`
- `near_real_0006`
  - `v77`
    - `target_capture_db = -4.815`
    - `interference_capture_db = -28.892`
- `near_real_0009`
  - `v77`
    - `interference_capture_db = -31.721`
  - 比 `v72 = -34.468` 更差

裁决：

- `gate-only + 当前损失` 也不是答案

## 本轮最终结论

### 已确认成立

1. `target_energy_ratio` selector 值得保留。
2. `abstention gate` 机制值得保留。
3. `v76` 证明 gate 不是伪方向，它确实能把 `0009 / 0006` 往更静方向推。

### 已确认不成立

1. `audibility-conditioned objective v1` 单独就能解决问题。
2. gate 和 mask 用当前同一套波形目标直接联训，就会自然收敛到可用解。
3. 只训练 gate 头，就能在不改监督方式的前提下学出有用 abstention。

## 当前最准确的判断

当前瓶颈已经进一步收敛成：

- 不是“要不要 gate”
- 而是“gate 缺少自己专属的监督目标”

现状是：

- `v76`
  - gate 有行为
  - 但容易把 hard present case 一起关掉
- `v77`
  - gate 不再乱关
  - 但也几乎不敢关

## 默认下一步

不建议继续做：

- `v78 / v79` 这种沿 `v76` 的普通权重 sweep
- `v77` 附近继续扫 gate-only 学习率

下一步应改成 gate 专属监督：

1. 新建 `abstention_gate_proxy_v1`
   - 专门服务 gate，不再复用 `proxy_v4` 作为唯一弱目标信号
2. 新增 gate-level loss
   - 对 selector 命中的 weak-target / absent 样本，直接压低 `branch_decoder_frame_gate`
   - 对 keep backstop 样本，直接约束 gate 不能整体塌掉
3. 训练策略默认先用：
   - 固定 `v72` mask
   - 只训 gate 头或 gate 小分支
   - 避免再次出现 `v76` 那种 joint drift
