# 2026-03-26 abstention-gate proxy `v1` and `v78 / v79` follow-up

## 本轮目标

上一轮已经把 `branch abstention gate` 结构落进模型，也用 `v76 / v77` 证明了两件事：

1. gate 机制本身不是伪方向。
2. 但没有 gate 专属监督时，joint 训练会走向 `v76` 式过关门，gate-only 会退回 `v77` 式 safe/no-op。

所以本轮只做一件更窄的事：

- 给 gate 单独建 focused proxy 和 gate-level loss；
- 直接验证它能否比 `v77` 更靠近“弱目标时闭嘴，但别误杀 present case”。

## 代码改动

### 1. gate-level loss

修改：

- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`

新增：

- `weighted_gate_target_loss()`
- `gate_abstain_mean`
- `gate_keep_mean`
- CLI：
  - `--loss-gate-abstain-weight`
  - `--loss-gate-keep-weight`

本轮最小实现仍复用现有 selector 口径：

- `gate_abstain_sample_weights`
  - 直接复用 `interference_extra_sample_weights`
- `gate_keep_sample_weights`
  - 直接复用 `branch_protect_sample_weights`

这意味着：

- 弱目标 abstention 样本直接监督 gate 接近 `0`
- keep backstop 样本直接监督 gate 接近 `1`

## 新增资产

### 1. `abstention_gate_proxy_v1`

文件：

- `data/synthetic/train_manifest_abstention_gate_proxy_v1.jsonl`
- `data/synthetic/val_manifest_abstention_gate_proxy_v1.jsonl`
- `reports/data/selector_abstention_gate_proxy_v1_train_summary.json`
- `reports/data/selector_abstention_gate_proxy_v1_val_summary.json`

来源：

- `overlap_abstention_backstop_union_metrics_v1`

过滤口径：

- `target_full`
- `target_energy_ratio <= 0.20`
- `target_transient_presence_share_mean <= 0.03`
- `target_transient_presence_minus_mid_db_mean <= -10`

规模：

- train `70`
- val `14`

recipe 分布：

- train
  - `target_clean_speech = 25`
  - `target_clean_plus_music = 20`
  - `target_hard_speech = 10`
  - `target_hard_plus_music = 15`
- val
  - `target_clean_speech = 5`
  - `target_clean_plus_music = 4`
  - `target_hard_speech = 4`
  - `target_hard_plus_music = 1`

### 2. `abstention_gate_bundle_v1`

文件：

- `data/synthetic/train_manifest_abstention_gate_bundle_v1.jsonl`
- `data/synthetic/val_manifest_abstention_gate_bundle_v1.jsonl`
- `data/synthetic/sample_ids_abstention_gate_bundle_v1_train.txt`
- `data/synthetic/sample_ids_abstention_gate_bundle_v1_val.txt`
- `reports/data/merge_abstention_gate_bundle_v1_train_summary.json`
- `reports/data/merge_abstention_gate_bundle_v1_val_summary.json`

组成：

- `abstention_gate_proxy_v1`
- `same_gender_present_keep_guardrail_v1`

规模：

- train `80`
- val `25`

作用：

- 让 gate 训练直接面对：
  - `70 / 14` 条弱目标 abstention 样本
  - `10 / 11` 条 keep backstop 样本

## 新训练

### 1. `v78 = v72 + gate proxy v1 supervised`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v78_v72_abstention_gate_proxy_v1_supervised_ft1`

训练口径：

- init：`v72`
- 只训：
  - `branch_decoder_gate_head`
- train/val：
  - `abstention_gate_bundle_v1`
- gate loss：
  - `gate_abstain_weight = 0.04`
  - `gate_keep_weight = 0.02`

训练期 gate 指标：

- val `gate_abstain_mean`
  - `0.9807 -> 0.9345`
- val `gate_keep_mean`
  - `0.0142 -> 0.0319`

解释：

- gate 终于不再是接近完全恒等；
- 但 abstain push 还偏弱。

### 2. `v79 = v78 + stronger gate supervision`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v79_v78_abstention_gate_proxy_v1_supervised_tuned_ft1`

训练口径：

- init：`v78`
- 只训：
  - `branch_decoder_gate_head`
- gate loss：
  - `gate_abstain_weight = 0.12`
  - `gate_keep_weight = 0.03`

训练期 gate 指标：

- val `gate_abstain_mean`
  - `0.8702 -> 0.3153`
- val `gate_keep_mean`
  - `0.0535 -> 0.2904`

解释：

- gate 被显著拉下来了；
- 但 keep 侧也开始明显受压。

## 结果

### A. `v78`：第一次把 gate 专属监督变成了 near-real 安全结果

synthetic abstention：

- `reports/eval/compare_v72_vs_v78_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -6.4552`
  - `1` improve / `7` regress
- `reports/eval/compare_v77_vs_v78_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = +0.7502`
  - `1` improve / `1` regress / `6` near tie

解释：

- 对旧的 abstention SI-SDR proxy 而言，`v78` 依然很差
- 但和 `v77` 相比已经不是完全 safe/no-op

keep guardrail：

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v72_v77_v78/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v72 = 10`
    - `v77 = 0`
    - `v78 = 0`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v72_v77_v78/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v72 = 2`
    - `v77 = 0`
    - `v78 = 0`

逐样本：

- `near_real_0003`
  - `target_capture_db`
    - `v54 = -11.464`
    - `v78 = -11.457`
- `near_real_0006`
  - `target_capture_db`
    - `v54 = -4.754`
    - `v78 = -4.802`
- `near_real_0007`
  - `target_capture_db`
    - `v54 = -16.596`
    - `v78 = -15.943`
- `near_real_0009`
  - `interference_capture_db`
    - `v54 = -33.385`
    - `v78 = -31.981`

裁决：

- `v78` 是第一条“显式 gate 监督后仍然 present-safe”的机制样本
- 但 absent 侧没有赢到可接受水平

### B. `v79`：更强的 gate push 确实带来 absent 收益，但又回到 keep regression

synthetic abstention：

- `reports/eval/compare_v78_vs_v79_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = -0.2665`
  - `1` improve / `7` regress

keep guardrail：

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v78_v79/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v78 = 0`
    - `v79 = 11`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v78_v79/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v78 = 0`
    - `v79 = 1`
  - 违规样本：
    - `near_real_0007`

逐样本：

- `near_real_0006`
  - `interference_capture_db`
    - `v78 = -29.170`
    - `v79 = -36.393`
  - 说明强 gate push 确实能把这条再压下去
- `near_real_0009`
  - `interference_capture_db`
    - `v78 = -31.981`
    - `v79 = -36.617`
  - absent 也确实变静
- 但 `near_real_0007`
  - `target_capture_db`
    - `v78 = -15.943`
    - `v79 = -22.369`
  - hard present backstop 又开始被误杀

裁决：

- `v79` 证明强 gate 监督不是白加
- 但它也清楚证明：
  - 当前 keep backstop 还太窄
  - 没有覆盖 `0007` 风格 hard present case

## 本轮最终结论

### 已确认成立

1. `abstention_gate_proxy_v1` 是有效资产。
2. gate-level loss 是有效机制，不再只是结构占位。
3. `v78 / v79` 共同证明，gate supervision 能在：
   - absent 更静
   - keep 更安全
   之间形成真实可调的 tradeoff。

### 已确认不成立

1. 只靠 `same_gender_present_keep_guardrail_v1` 就能守住 gate 训练的全部 present 风险。
2. 旧的 abstention SI-SDR proxy 适合直接裁决 gate 机制成败。

## 当前最准确的判断

当前最缺的已经不是：

- gate 结构
- gate loss
- gate focused proxy

而是下一层 keep backstop：

- 现有 keep backstop 主要覆盖 `0003` 风格 same-gender clean-speech
- 还没覆盖 `0007` 风格 hard present + music / harder mixture

所以一旦把 gate abstain push 拉强，`0007` 就先掉下去。

## 默认下一步

不建议继续做：

- `v80 / v81` 这种单纯 gate loss 权重 sweep

下一步应改成：

1. 物化 `hard_present_gate_keep_guardrail_v1`
   - 目标是覆盖 `near_real_0007` 风格样本
   - 来源优先从当前 metrics manifest 的
     - `target_hard_speech`
     - `target_clean_plus_music`
     - `target_hard_plus_music`
     里切
2. 然后再做 gate-supervised follow-up
   - 保留 `abstention_gate_proxy_v1`
   - 保留 `same_gender_present_keep_guardrail_v1`
   - 新增 `hard_present_gate_keep_guardrail_v1`

如果继续推进，默认下一步应是第 1 条，而不是继续扫 `v79` 附近权重。
