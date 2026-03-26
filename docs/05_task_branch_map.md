# 任务分支图

## 文档定位

- 本文档只保留当前仍会影响下一步决策的活跃分支地图。
- 历史长版已归档到：
  - `docs/archive/task_branch_map/task_branch_map_active_snapshot_2026-03-26.md`
- 更早分卷与长节索引见：
  - `docs/archive/task_branch_map/README.md`

## 当前主线与研究线

### 默认主线

- `legacy stage2`
- 状态：
  - 默认可用线
  - 当前不被任何研究分支替代

### 当前 overlap-abstention 研究基座

- `v72`
- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v72_v54_overlap_abstention_proxy_v4_audibility_v1_ft1`
- 状态：
  - objective 研究基座
  - 不能放行

### 当前 gate 机制探针

- `v76`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v76_v72_audibility_conditioned_v1_gate_v1_ft1`
  - 状态：
    - 证明 gate 机制有信号
    - 不能放行
- `v77`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v77_v72_audibility_conditioned_v1_gateonly_v1_ft1`
  - 状态：
    - gate-only isolate probe
    - 不能放行
- `v78`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v78_v72_abstention_gate_proxy_v1_supervised_ft1`
  - 状态：
    - gate supervision first safe pilot
    - 不能放行
- `v79`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v79_v78_abstention_gate_proxy_v1_supervised_tuned_ft1`
  - 状态：
    - stronger gate push
    - 不能放行
- `v80`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v80_v79_abstention_gate_keepunion_v2_ft1`
  - 状态：
    - wider keep union follow-up
    - 不能放行

## 当前活跃问题树

### A. silence-over-leak / absent frontier

目的：

- 解决弱目标或 absent 情况下“宁可闭嘴，也不要漏干扰”。

当前资产：

- `scripts/eval/score_silence_over_leak_pack.py`
- `scripts/eval/rank_checkpoints_on_silence_over_leak_manifest.py`
- `data/references/real_eval_manifest_silence_over_leak_guardrail_v2.jsonl`

当前结论：

- 这条线已经完成批量排雷作用；
- 适合筛掉明显更差的 checkpoint；
- 不再适合继续做 frontier 选美。

当前状态：

- `closed_as_selection_problem`

### B. residual speech leak floor / overlap-abstention

目的：

- 解决目标与干扰时间重合时的残余人声泄漏；
- 同时满足“弱目标可闭嘴”和“中等可辨目标不能一起被压坏”。

主 near-real 验收：

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`

关键样本：

- `near_real_0003`
  - medium-audibility keep anchor
- `near_real_0006`
  - weak-target overlap abstention anchor
- `near_real_0007`
  - hard present backstop
- `near_real_0009`
  - absent / external speech only anchor

当前状态：

- `active`

当前子方向：

- `audibility-conditioned objective`
  - `failed_as_loss_only`
- `branch abstention gate`
  - `active_mechanism_probe`
- `hard-present gate keep backstop`
  - `guardrail_materialized_but_insufficient_as_sample_union`

### C. same-gender present keep

目的：

- 专门约束 `near_real_0003` 风格的 same-gender keep-case；
- 防止 overlap-abstention 方向把 target-present 一起压坏。

当前资产：

- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v2_strict.jsonl`

当前结论：

- `v1` 是有效正式 guardrail；
- `v2_strict` 只适合作为更窄 probe，不适合作为主训练方向。

当前状态：

- `active_guardrail`

## 当前 active checkpoint 关系

### 1. `v72`

含义：

- overlap-abstention objective 最强研究基座

优点：

- `0009` absent suppression 比 `v54` 更强
- `proxy_v4` abstention objective 最优

问题：

- near-real 仍有：
  - `0003`
  - `0006`
  两条 present violation

裁决：

- `research_base_keep`

### 2. `v75`

含义：

- `v72 + audibility-conditioned objective v1`

结果：

- combined rank 看起来更强
- 但 synthetic abstention 回退
- keep / near-real guardrail 都更差

裁决：

- `failed_loss_only`

### 3. `v76`

含义：

- `v72 + audibility-conditioned objective v1 + branch abstention gate`

结果：

- `0009 / 0006` 有真实更静收益
- 但 `0007` 被 gate 一起压坏

裁决：

- `failed_joint_gate_drift`

### 4. `v77`

含义：

- `v72 + gate-only isolate probe`

结果：

- present guardrail 恢复安全
- abstention 收益基本消失

裁决：

- `failed_safe_noop`

### 5. `v78`

含义：

- `v72 + abstention_gate_proxy_v1 + gate-level loss`

结果：

- 恢复到 present-safe
- absent 仍不够静

裁决：

- `safe_but_absent_weak`

### 6. `v79`

含义：

- `v78 + stronger gate push`

结果：

- `0006 / 0009` 更静
- `0007` 开始回退

裁决：

- `failed_hard_present_backstop`

### 7. `v73`

含义：

- `v72 + broad same-gender keep guardrail`

结果：

- synthetic keep violation 明显下降
- 但 `near_real_0009` absent suppression 明显回退
- near-real 仍未修好 `0003 / 0006`

裁决：

- `failed_tradeoff`

### 8. `v74`

含义：

- `v72 + strict same-gender keep probe`

结果：

- absent objective 更强
- 但 near-real 变成更严重的过静音
- present violation 增加到：
  - `0003`
  - `0006`
  - `0007`

裁决：

- `failed_over_silence`

### 9. `v80`

含义：

- `v79 + keep_union_v2`

结果：

- `0006 / 0009` 更静
- `same_gender keep guardrail`
  - 仍是 `11` 条 violation
- `hard_present keep guardrail`
  - 仍是 `16` 条 violation
- `0007` 比 `v79` 更坏

裁决：

- `failed_binary_gate_target`

## 当前有效训练与验收入口

### 训练侧

- abstention focused proxy：
  - `data/synthetic/train_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`
  - `data/synthetic/val_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`
- keep guardrail：
  - `data/synthetic/train_manifest_same_gender_present_keep_guardrail_v1.jsonl`
  - `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- gate 机制 follow-up：
  - `data/synthetic/train_manifest_audibility_conditioned_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_audibility_conditioned_bundle_v1.jsonl`
  - `data/synthetic/train_manifest_abstention_gate_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_abstention_gate_proxy_v1.jsonl`
  - `data/synthetic/train_manifest_abstention_gate_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_abstention_gate_bundle_v1.jsonl`
  - `data/synthetic/train_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
  - `data/synthetic/val_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
  - `data/synthetic/train_manifest_gate_keep_union_v2.jsonl`
  - `data/synthetic/val_manifest_gate_keep_union_v2.jsonl`
  - `data/synthetic/train_manifest_abstention_gate_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_abstention_gate_bundle_v2.jsonl`

### 验收侧

- near-real 主验收：
  - `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`
- keep synthetic guardrail：
  - `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
- hard-present keep synthetic guardrail：
  - `data/synthetic/val_manifest_hard_present_gate_keep_guardrail_v1.jsonl`
- abstention synthetic guardrail：
  - `data/synthetic/val_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`

## 当前禁止误接的旧分支

以下分支不应再被当作默认下一步：

- `v64 / v65 / v66 / v67`
- `candidate_v4 / candidate_v5 / candidate_v7`
- `same_gender_reverb_proxy_v3` 直接训
- 纯 checkpoint frontier 继续扫 `v72` 附近权重

原因：

- 它们要么已经被后续阶段覆盖；
- 要么已经证明不再回答当前核心问题。

## 默认下一步

如果没有新的用户决策，当前默认下一步是：

- 不再继续扫 `v80` 同结构权重；
- 直接改机制层目标语义：
  - `audibility-conditioned gate target`
  - 目标是把 hard-present keep、medium present keep、weak-target abstain 从完全二元监督改成分层目标

执行前必须保持四条验收同时在场：

- `real_eval_manifest_residual_speech_leak_floor_v1`
- `same_gender_present_keep_guardrail_v1`
- `hard_present_gate_keep_guardrail_v1`
- `overlap_abstention_proxy_v4_audibility_v1`

## 近期关键日报入口

- `reports/daily/2026-03-26_overlap_abstention_proxy_v3_v4_and_v71_v72_followup.md`
- `reports/daily/2026-03-26_present_keep_guardrail_v1_v2_and_v73_v74_followup.md`
- `reports/daily/2026-03-26_frontier_imperfection_taxonomy_and_next_subproblem.md`
- `reports/daily/2026-03-26_audibility_conditioned_v1_and_abstention_gate_v1_v75_v76_v77.md`
- `reports/daily/2026-03-26_abstention_gate_proxy_v1_and_v78_v79_followup.md`
- `reports/daily/2026-03-26_hard_present_gate_keep_guardrail_v1_and_v80_followup.md`

## 文档维护规则

- 本文档只记录：
  - 当前活跃分支
  - 当前裁决状态
  - 当前默认下一步
- 已终止分支、旧 family 的长历史，不再回填到主文档。
- 当本文件再次膨胀到不利于接班阅读时，默认处理方式是：
  1. 先把当时版本完整快照到 `docs/archive/task_branch_map/`
  2. 再重写为新的短版活跃分支图
