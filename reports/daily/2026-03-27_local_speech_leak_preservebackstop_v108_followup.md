# 2026-03-27 local speech-leak preserve backstop `v108` follow-up

## 本轮目标

`v107` 已经证明：

- 显式 local speech-leak supervision 是成立方向；
- 但它在 `near_real_0007` 上仍会重新输在 artifact。

因此本轮不再改模型结构，也不重做 proxy，而是做最小机制增量：

1. 保留 `v107` 的 `speech_leak_local_aware_bundle_v1`；
2. 保留原 `speech_only overlap_interference_extra`；
3. 在 `local_speech_leak_proxy_v1` 全量子集上新增：
   - `branch_protect_guard_sisdr`
   - `branch_protect_teacher_overlap(v81)`
4. 先验证“local preservation + teacher backstop”是否足以止住电话音式 artifact，而不把 `v107` 的主收益一起抹掉。

## 新增资产

- `data/synthetic/sample_ids_local_speech_leak_proxy_v1_all.txt`

用途：

- 把 `local_speech_leak_proxy_v1` 的 train / val sample-id 合并成统一 selector；
- 供 `branch_protect` 与 `branch_protect_teacher` 同时命中同一批 local proxy 样本。

## `v108` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v108_v107_local_speech_leak_preservebackstop_v1_ft1`

初始化：

- `v107`

teacher：

- `v81`

核心配置：

- 继续复用 `v107` 的：
  - `speech_leak_local_aware_bundle_v1`
  - `speech_only overlap_interference_extra`
  - `sample_ids_gate_keep_union_v2_train.txt`
- 新增：
  - `branch_protect_focus = sample_ids_local_speech_leak_proxy_v1_all.txt`
  - `branch_protect_teacher_focus = sample_ids_local_speech_leak_proxy_v1_all.txt`
  - `branch_protect_guard_sisdr_weight = 0.003`
  - `branch_protect_teacher_overlap_weight = 3.0`

selector 激活：

- train
  - `overlap_interference_extra = 38 / 135`
  - `branch_protect = 33 / 135`
  - `branch_protect_teacher = 33 / 135`
- val
  - `overlap_interference_extra = 12 / 40`
  - `branch_protect = 7 / 40`
  - `branch_protect_teacher = 7 / 40`

训练结果：

- 训练成功结束
- `elapsed_sec = 50.3`
- `best.pt / latest.pt / train_summary.json` 已落盘

## 自动验收结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -0.6017 dB`
  - `4 improve / 4 regress`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.3024 dB`
  - `10 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0170 dB`
  - `10 improve / 4 regress`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.2906 dB`
  - `4 improve / 1 regress`

解释：

- `v108` 相对 `v81` 没有立即炸掉 keep / artifact proxy；
- 但 abstention 已经明显回吐；
- 这不是一个能直接升格的自动结果。

### relative `v107`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -3.6913 dB`
  - `1 improve / 7 regress`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -1.1242 dB`
  - `0 improve / 11 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -1.1257 dB`
  - `3 improve / 13 regress`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = -1.5016 dB`
  - `0 improve / 7 regress`

解释：

- 这说明 `v108` 不是“用一部分 abstention 损失换来更稳的 artifact / keep”；
- 而是把 `v107` 的主收益几乎整体抹掉了。

## near-real 结果

### `v81 vs v108`

whole-utterance：

- `better_retention_minus_leak_candidate_counts`
  - `v108 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v81 = 1`
  - `tie = 3`
- `better_source_retention_candidate_counts`
  - `tie = 3`
  - `not_applicable = 1`

分样本：

- `near_real_0003`
  - `better_retention_minus_leak = v108`
  - `more_interference_leaky = v81`
- `near_real_0006`
  - `better_retention_minus_leak = tie`
- `near_real_0007`
  - `better_retention_minus_leak = tie`
- `near_real_0009`
  - absent suppression 基本 tie

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `v81 = 2`
  - `v108 = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `v108 = 3`
  - `v81 = 1`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v81 = 1`
  - `tie = 3`

关键点：

- `near_real_0007`
  - `better_retention_minus_speech_leak = v81`
  - `more_speech_interference_leaky = v108`
  - `more_artifact_proxy_heavy = tie`

解释：

- 相对 `v81`，`v108` 没有再像 `v107` 那样在 `0007` 上显式更 artifact-heavy；
- 但也没有把 `0007` 的局部 leak / retention tradeoff 拉成正向。

### `v107 vs v108`

whole-utterance：

- `better_retention_minus_leak_candidate_counts`
  - `v108 = 1`
  - `tie = 2`
  - `not_applicable = 1`
- `more_interference_leaky_candidate_counts`
  - `v108 = 1`
  - `tie = 3`

overlap-local：

- `better_retention_minus_speech_leak_candidate_counts`
  - `v107 = 1`
  - `v108 = 1`
  - `tie = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky_candidate_counts`
  - `v108 = 2`
  - `tie = 2`
- `more_artifact_proxy_heavy_candidate_counts`
  - `v107 = 3`
  - `v108 = 1`

关键点：

- `near_real_0007`
  - `better_retention_minus_speech_leak = v108`
  - `more_speech_interference_leaky = tie`
  - `more_artifact_proxy_heavy = v107`
- `near_real_0006`
  - `better_retention_minus_speech_leak = v107`
  - `more_speech_interference_leaky = v108`
  - `more_artifact_proxy_heavy = v107`

解释：

- `v108` 确实在 `0007` 风格样本上止住了一部分 `v107` 的 artifact / leak 失衡；
- 但它是靠更广泛地回缩 `v107` 的有效行为换来的。

## phone-artifact gate

### `v81 vs v108`

- `narrower_candidate_counts = tie: 4`
- `more_transient_lossy_candidate_counts`
  - `tie = 2`
  - `v108 = 2`
- `phone_artifact_gate_v1`
  - `overall_pass = false`
  - `failed_buckets = [target_present__speech, target_absent__speech]`

说明：

- 相对 `v81`，`v108` 仍不过当前 phone-artifact gate；
- 但它已经比 `v103 / v107` 少了一个 `raw_target_only` 失败桶。

### `v107 vs v108`

- `narrower_candidate_counts = tie: 4`
- `more_transient_lossy_candidate_counts`
  - `tie = 2`
  - `v107 = 2`
- `phone_artifact_gate_v1`
  - `overall_pass = true`

说明：

- `v108` 相对 `v107`，电话音式 transient-loss 确实被压下来了；
- 这版 backstop 不是完全无效，而是过于宽打。

## 本轮结论

1. `v108` 证明“在 `local_speech_leak_proxy_v1` 全量子集上叠 local preservation + teacher backstop”确实能减轻 `v107` 的 phone-artifact。
2. 但这版约束打得太宽：
   - 相对 `v107`
   - abstention / keep / artifact proxy 几乎全线回退。
3. relative `v81`，`v108` 也没有形成足够强的自动前沿：
   - `0007` 没有转正
   - `phone_artifact_gate_v1` 仍 fail
4. 因此 `v108` 不导听审，直接收口。

## 下一步

如果继续这条子题，默认不再做：

- `local_speech_leak_proxy_v1` 全量子集上的宽 `branch_protect + teacher` backstop

而应改成：

1. 只在更窄的 `0007` 风格 `music_plus_speech hard-present` 局部窗上打 preservation / artifact backstop；
2. 不再把整个 `local_speech_leak_proxy_v1` 语义子域一起拉回；
3. 新候选继续先过：
   - `phone_artifact_gate_v1`
   - 再决定是否值得导听审。
