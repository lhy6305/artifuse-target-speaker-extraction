# 2026-03-26 present-keep guardrail `v1 / v2` and `v73 / v74` follow-up

## 本轮目标

在 `v71 / v72` 已经明确暴露 `near_real_0003 / 0006` 同时被压坏之后，本轮要回答两个更具体的问题：

1. 能否物化一个真正能复现 `near_real_0003` 风格失败的 synthetic `present keep` guardrail。
2. 如果 guardrail 成立，是否能在不明显破坏 `0006 / 0009` 静音收益的前提下，把 `v72` 往回拉一点。

## 新增资产

### 1. overlap-abstention present-keep 宽切片

文件：

- `data/synthetic/train_manifest_overlap_abstention_present_keep_guardrail_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_present_keep_guardrail_v1.jsonl`
- `data/synthetic/sample_ids_overlap_abstention_present_keep_guardrail_v1_{train,val,all}.txt`
- `reports/data/selector_overlap_abstention_present_keep_guardrail_v1_summary.json`

构造口径：

- 来源：`overlap_abstention_backstop_v1`
- `target_full`
- `0.35 <= target_energy_ratio <= 0.8`
- `target_transient_presence_share_mean <= 0.03`

规模：

- train `15`
- val `10`

裁决：

- 这个切片在 SI-SDR 上会误导，`v71 / v72` 都看起来优于 `v54`
- 但它证明了单看 `compare_checkpoints_on_manifest.py` 不足以评估这类 keep-case

### 2. same-gender present-keep guardrail `v1`

先把旧 proxy 补齐 derived metrics：

- `data/synthetic/train_manifest_same_gender_reverb_proxy_v2_metrics_v1.jsonl`
- `data/synthetic/val_manifest_same_gender_reverb_proxy_v2_metrics_v1.jsonl`

再从中切出新的 keep guardrail：

- `data/synthetic/train_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- `data/synthetic/sample_ids_same_gender_present_keep_guardrail_v1_{train,val,all}.txt`
- `reports/data/selector_same_gender_present_keep_guardrail_v1_summary.json`

构造口径：

- 来源：`same_gender_reverb_proxy_v2_metrics_v1`
- `target_full`
- `0.35 <= target_energy_ratio <= 0.8`
- `target_transient_presence_share_mean <= 0.03`
- `target_interference_logspec_cosine >= 0.45`

规模：

- train `10`
- val `11`

这是本轮最关键的新结论：

- 这条 `same_gender present keep` guardrail 用 near-real 同口径打分时，终于稳定复现了 `0003` 风格 failure
- 对 `v72` 而言：
  - `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v71_v72/summary.json`
  - `present_guardrail_violation_count = 10`
- 也就是说，当前 overlap-abstention 方向确实会在 medium-audibility same-gender keep-case 上系统性过静音

### 3. same-gender present-keep strict guardrail `v2`

文件：

- `data/synthetic/train_manifest_same_gender_present_keep_guardrail_v2_strict.jsonl`
- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v2_strict.jsonl`
- `data/synthetic/sample_ids_same_gender_present_keep_guardrail_v2_strict_{train,val,all}.txt`
- `reports/data/selector_same_gender_present_keep_guardrail_v2_strict_summary.json`

构造口径：

- 在 `same_gender_present_keep_guardrail_v1` 基础上继续收窄
- `target_interference_logspec_cosine >= 0.60`

规模：

- train `3`
- val `7`

用途：

- 不再作为主 guardrail
- 只作为更窄的 keep-nudge probe

### 4. 新训练 bundle

文件：

- `data/synthetic/train_manifest_overlap_abstention_bundle_v3_keepguard_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_bundle_v3_keepguard_v1.jsonl`
- `reports/data/merge_overlap_abstention_bundle_v3_keepguard_v1_{train,val}_summary.json`

- `data/synthetic/train_manifest_overlap_abstention_bundle_v4_strictkeep_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_bundle_v4_strictkeep_v1.jsonl`
- `reports/data/merge_overlap_abstention_bundle_v4_strictkeep_v1_{train,val}_summary.json`

## 新训练

### 1. `v73 = v72 + broad same-gender keep guardrail`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v73_v72_overlap_abstention_bundle_v3_keepguard_v1_ft1`

训练口径：

- init：`v72`
- manifest：`overlap_abstention_bundle_v3_keepguard_v1`
- abstention push：
  - `interference_extra_focus = proxy_v4_audibility`
- keep push：
  - `reconstruction_extra_focus = same_gender_present_keep_guardrail_v1`
  - `branch_protect_focus = same_gender_present_keep_guardrail_v1`
- keep weights：
  - `reconstruction_extra_waveform = 0.03`
  - `reconstruction_extra_stft = 0.015`
  - `branch_protect_guard_sisdr = 0.006`

### 2. `v74 = v72 + strict same-gender keep probe`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v74_v72_overlap_abstention_bundle_v4_strictkeep_v1_ft1`

训练口径：

- init：`v72`
- manifest：`overlap_abstention_bundle_v4_strictkeep_v1`
- abstention push：
  - `interference_extra_focus = proxy_v4_audibility`
- keep push：
  - `reconstruction_extra_focus = same_gender_present_keep_guardrail_v2_strict`
  - `branch_protect_focus = same_gender_present_keep_guardrail_v2_strict`
- keep weights 更轻：
  - `reconstruction_extra_waveform = 0.015`
  - `reconstruction_extra_stft = 0.0075`
  - `branch_protect_guard_sisdr = 0.003`

## 结果

### A. `v73` 的结论：方向有信号，但 tradeoff 不可接受

synthetic：

- `reports/eval/compare_v72_vs_v73_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `-0.442054 dB`
  - `2` improve / `5` regress / `1` near tie
- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v72_v73/summary.json`
  - `v72` 在 keep guardrail 上是 `10` 条 violation
  - `v73` 降到 `5` 条 violation

解释：

- `v73` 确实不是白跑
- 它第一次证明 `same_gender_present_keep_guardrail_v1` 能被训练信号利用
- 但它是用牺牲 abstention frontier 换来的

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v72_v73/summary.json`
- `v73` 仍然：
  - `present_guardrail_violation_count = 2`
  - 违规样本仍是 `near_real_0003` 和 `near_real_0006`

样本级变化：

- `near_real_0003`
  - `target_capture_db`: `-19.592 -> -18.456`
  - 有所回拉，但仍显著差于 `v54 = -11.464`
- `near_real_0006`
  - `target_capture_db`: `-8.941 -> -8.040`
  - 但 `interference_capture_db`: `-34.935 -> -29.965`
  - 说明它是靠“放更多东西出来”回拉，不是把边界学对了
- `near_real_0009`
  - `interference_capture_db`: `-34.468 -> -27.639`
  - absent suppression 明显变坏

裁决：

- `v73` 不能放行
- 但它证明了 `present keep guardrail` 是真实有效的新资产，不是伪信号

### B. `v74` 的结论：过窄 keep probe 直接走向过静音

synthetic：

- `reports/eval/compare_v72_vs_v74_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `-0.688078 dB`
  - `1` improve / `7` regress
- `reports/eval/rank_same_gender_present_keep_guardrail_v2_strict_v54_v72_v74/summary.json`
  - strict keep violation 只从 `7` 降到 `6`

near-real：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v72_v74/summary.json`
- `v74` 变成典型“objective 更安静，但目标一起被压死”：
  - `near_real_0009`
    - `interference_capture_db = -47.347`
    - absent 极安静
  - 但 present 侧：
    - `present_guardrail_violation_count = 3`
    - 违规样本变成 `near_real_0003 / 0006 / 0007`

样本级：

- `near_real_0003`
  - `target_capture_db = -22.318`
- `near_real_0006`
  - `target_capture_db = -10.156`
- `near_real_0007`
  - `target_capture_db = -24.642`

裁决：

- `v74` 是明显失败样本
- 它说明继续靠“更窄 keep selector + 更轻 keep weight”扫 branch-only 权重，没有把问题拆开

## 本轮最终结论

### 已确认成立

1. `same_gender_present_keep_guardrail_v1` 是有效资产。
2. 之前缺的不是 selector metric，而是缺一个真正能复现 `0003` 风格失败的 same-gender keep guardrail。
3. `v73` 证明 keep guardrail 可以被当前训练流程利用。

### 已确认不成立

1. 只靠 branch-only reweighting，就能同时修好 `0003` keep 和 `0009` abstain。
2. 继续扫 `v72` 附近的 keep weight / strict selector，会自然走到可用解。

## 当前最准确的判断

这条分支现在已经收敛到一个新的瓶颈：

- 不是“缺 guardrail”
- 也不是“缺更窄 selector”
- 而是当前 loss/branch 结构下，`keep` 和 `abstain` 还在共用同一条输出自由度

所以一旦往 keep 方向拉，就会让 `0006 / 0009` 放更多东西出来；
一旦继续往 abstain 方向拉，就会把 `0003` 一起压坏。

## 默认下一步

不建议继续做 `v75 / v76` 这类同结构权重 sweep。

下一步应改成机制层尝试，而不是继续调权重：

1. 增加显式的 audibility-conditioned objective
   - 让 keep / abstain 的惩罚随 `target_energy_ratio` 分段，而不是共用一套固定权重
2. 或者做一个轻量 abstention gate
   - 主分离支路保留 target
   - 额外小 gate 只决定“弱目标时要不要整体闭嘴”
3. 在任何新训练前，继续保留以下 guardrail 不变：
   - `real_eval_manifest_residual_speech_leak_floor_v1.jsonl`
   - `same_gender_present_keep_guardrail_v1`
   - `proxy_v4_audibility`

如果继续推进，默认应优先实现第 1 条，而不是再起同类 branch-only pilot。
