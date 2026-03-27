# 2026-03-27 local speech-leak `0007-like` backstop `v109` follow-up

## 本轮目标

`v108` 已证明：

- 在整个 `local_speech_leak_proxy_v1` 子域上宽打 preservation / teacher backstop，
- 虽然能止住一部分 phone-artifact，
- 但会把 `v107` 的主收益一起回缩。

因此本轮改成更窄的外科式 backstop：

1. 仍从 `v107` 出发，不沿用 `v108`；
2. 保留：
   - `speech_leak_local_aware_bundle_v1`
   - `speech_only overlap_interference_extra`
3. 只在更窄的 `0007` 风格 `music_plus_speech hard-present` 局部窗上打开：
   - `branch_protect_guard_sisdr`
   - `branch_protect_teacher_overlap(v81)`
4. 先看是否能：
   - 保住 `v107` 的主收益，
   - 同时止住 phone-artifact，
   - 再决定是否值得导 blind 听审。

## 新增资产

- selector 构建脚本：
  - `scripts/data/build_local_speech_leak_0007_like_proxy.py`
- selector summary：
  - `reports/data/selector_local_speech_leak_0007_like_proxy_v1_summary.json`
- selector manifests / sample ids：
  - `data/synthetic/train_manifest_local_speech_leak_0007_like_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_0007_like_proxy_v1.jsonl`
  - `data/synthetic/sample_ids_local_speech_leak_0007_like_proxy_v1_train.txt`
  - `data/synthetic/sample_ids_local_speech_leak_0007_like_proxy_v1_val.txt`
  - `data/synthetic/sample_ids_local_speech_leak_0007_like_proxy_v1_all.txt`

selector 口径：

- `local_selection_mode = speech_target_share_bounded_peak`
- `local_music_share_of_interference >= 0.10`
- `local_fullmix_target_share <= 0.14`
- `target_energy_ratio <= 0.22`
- `0.02 <= target_transient_presence_share_mean <= 0.08`
- `target_interference_logspec_cosine >= 0.50`

selector 结果：

- train `3`
- val `3`
- all `6`
- recipe 全部为：
  - `target_clean_plus_music`

## `v109` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v109_v107_local_speech_leak_0007like_backstop_v1_ft1`

初始化：

- `v107`

teacher：

- `v81`

新增 selector：

- `sample_ids_local_speech_leak_0007_like_proxy_v1_all.txt`

selector 激活：

- train
  - `overlap_interference_extra = 38 / 135`
  - `branch_protect = 3 / 135`
  - `branch_protect_teacher = 3 / 135`
- val
  - `overlap_interference_extra = 12 / 40`
  - `branch_protect = 3 / 40`
  - `branch_protect_teacher = 3 / 40`

训练结果：

- 训练成功结束
- `elapsed_sec = 16.3`
- `best.pt / latest.pt / train_summary.json` 已落盘

## 自动验收结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +2.5930 dB`
  - `8 improve / 0 regress`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.0756 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.6735 dB`
  - `14 improve / 2 regress`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +1.4404 dB`
  - `6 improve / 1 regress`

解释：

- `v109` relative `v81` 四条固定验收重新全绿；
- 它没有重走 `v108` 那种“artifact 止血但整体回缩”的路径。

### relative `v107`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -0.4966 dB`
  - `2 improve / 5 regress`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.3511 dB`
  - `1 improve / 8 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.4693 dB`
  - `6 improve / 9 regress`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = -0.3518 dB`
  - `1 improve / 3 regress`

解释：

- 窄 backstop 仍然会让 `v107` 回缩一点；
- 但回缩幅度已经明显小于 `v108`；
- 当前更像“可接受的定向 tradeoff”，不是“整体抹平”。

## near-real 结果

### `v81 vs v109`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `v81 = 3`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v81 = 4`
- `better_retention_minus_leak_candidate_counts`
  - `v109 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `gate_near_real_tradeoff`
  - `overall_pass = true`

分样本：

- `near_real_0003`
  - `better_retention_minus_leak = v109`
- `near_real_0006`
  - `better_retention_minus_leak = tie`
- `near_real_0007`
  - `better_retention_minus_leak = tie`
- `near_real_0009`
  - absent suppression 偏向 `v109`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `v109 = 2`
  - `tie = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `v81 = 4`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v81 = 1`
  - `v109 = 2`
  - `tie = 1`

关键点：

- `near_real_0007`
  - `better_retention_minus_speech_leak = v109`
  - `better_retention_minus_total_leak = v81`
  - `more_artifact_proxy_heavy = v109`

解释：

- `v109` relative `v81` 已把 `0007` 的局部 speech-leak tradeoff 拉成正向；
- 但它还没有把 `0007` 整体变成一个无争议正向样本，
- 因为 source retention 与 artifact 仍在拉扯。

### `v107 vs v109`

whole-utterance：

- `better_source_retention_candidate_counts`
  - `tie = 2`
  - `v107 = 1`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v107 = 3`
  - `tie = 1`
- `better_retention_minus_leak_candidate_counts`
  - `v109 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `gate_near_real_tradeoff`
  - `overall_pass = true`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `v109 = 2`
  - `tie = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `v107 = 3`
  - `v109 = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v107 = 1`
  - `v109 = 1`
  - `tie = 2`

关键点：

- `near_real_0007`
  - `better_retention_minus_speech_leak = v109`
  - `more_artifact_proxy_heavy = tie`
- `near_real_0003`
  - `better_retention_minus_speech_leak = v109`
  - `more_artifact_proxy_heavy = v107`

解释：

- 相对 `v107`，`v109` 已经把窄 backstop 主要打在该打的位置；
- `0007` 不再出现 `v107` 那种“局部 leak 更强且 artifact 更重”的共同失败模式。

## phone-artifact gate

### `v81 vs v109`

- `narrower_candidate_counts`
  - `tie = 3`
  - `v81 = 1`
- `more_transient_lossy_candidate_counts`
  - `tie = 2`
  - `v81 = 2`
- `phone_artifact_gate_v1`
  - `overall_pass = true`

说明：

- 这是当前 `v107` family 首个 relative `v81` 通过 `phone_artifact_gate_v1` 的候选；
- 它没有再触发之前几轮一致出现的电话音失败桶。

### `v107 vs v109`

- `narrower_candidate_counts`
  - `tie = 3`
  - `v107 = 1`
- `more_transient_lossy_candidate_counts`
  - `tie = 1`
  - `v107 = 3`
- `phone_artifact_gate_v1`
  - `overall_pass = true`

说明：

- `v109` 相对 `v107` 继续保留了 phone-artifact relief；
- 且这次没有付出 `v108` 那种全线回缩代价。

## 当前裁决

1. `v109` 证明：
   - 把 preservation / teacher backstop 缩到 `0007-like` 子域，
   - 可以避免 `v108` 式 over-regularization。
2. relative `v81`：
   - 四条 synthetic 固定验收全绿；
   - `near-real tradeoff gate = pass`；
   - `phone_artifact_gate_v1 = pass`。
3. relative `v107`：
   - `0007` 风格局部 tradeoff 明显更健康；
   - `phone-artifact` relief 仍保留。
4. 但 `near_real_0007` 仍不是纯自动意义上的无争议转正：
   - 局部 speech-leak tradeoff 已转正，
   - 但 whole-utterance retention / artifact 仍有拉扯。

因此当前正式裁决是：

- `v109` 值得进入 `v81 vs v109` focused blind 听审；
- 不在听审前继续做 `v109+` 小步 sweep。

## 已物化听审资产

- non-blind：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v109`
- blind：
  - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v109_blind`

## focused blind 听审结果

- `v81 = 1`
- `v109 = 0`
- `tie = 3`

分样本：

- `near_real_0003`
  - `tie`
- `near_real_0006`
  - `tie`
- `near_real_0007`
  - `v81`
  - 原因：
    - `less_artifact`
- `near_real_0009`
  - `tie`

解释：

- `v109` 已经明显比 `v103 / v107` 更接近 `v81`；
- 但它仍没有把核心痛点 `0007` 主观转正；
- 唯一非 tie 样本仍因 artifact 判给 `v81`。

因此当前正式裁决更新为：

- `v109` 不升格
- `v81` 继续作为研究基座
- `v109+` 小步 sweep 先收口

## 下一步

默认下一步是：

1. 收口 `v109` 这条 `0007-like backstop` family；
2. 不继续 `v109+` 同构小步 sweep；
3. 如果继续 `0007` 子题，
   - 默认不再问“如何继续在当前 family 里微调”，
   - 而要回到 `0007` 的 retention / artifact 二元拉扯本身重新拆约束。
