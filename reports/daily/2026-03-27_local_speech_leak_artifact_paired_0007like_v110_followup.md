# 2026-03-27 local speech-leak / artifact paired `0007-like` pilot `v110` follow-up

## 本轮目标

`v109` 已证明：

- 把 preservation / teacher backstop 缩到 `0007-like` 子域后，
- 可以避开 `v108` 式全局回缩，
- 也能通过 `near-real tradeoff gate + phone_artifact_gate_v1`，
- 但 `near_real_0007` 仍没有在主观上转正。

因此本轮改成更显式的双视图窄 bundle：

1. 仍从 `v109` 出发；
2. 对同一批 `0007-like` base id 同时物化两种局部视图：
   - `speech_only` leak view
   - `target_clean_plus_music` artifact / preservation view
3. 在 leak view 上继续打 `overlap_interference_extra`；
4. 在 artifact view 上单独打：
   - `branch_protect_guard_sisdr`
   - `branch_protect_teacher_overlap(v81)`
5. 看是否能：
   - 保留 `v109` 的 phone-artifact relief，
   - 再把 `0007` 的 retention / artifact 拉扯继续往前推。

## 新增资产

- 配对 artifact selector 构建脚本：
  - `scripts/data/build_hard_present_artifact_0007_like_proxy.py`
- manifests / sample ids：
  - `data/synthetic/train_manifest_hard_present_artifact_0007_like_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_hard_present_artifact_0007_like_proxy_v1.jsonl`
  - `data/synthetic/sample_ids_hard_present_artifact_0007_like_proxy_v1_train.txt`
  - `data/synthetic/sample_ids_hard_present_artifact_0007_like_proxy_v1_val.txt`
  - `data/synthetic/sample_ids_hard_present_artifact_0007_like_proxy_v1_all.txt`
- paired bundle：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`

配对结果：

- `local_speech_leak_0007_like_proxy_v1` 与 `hard_present_artifact_local_proxy_v1`
  在 base sample id 上可一一配对；
- train `3`
- val `3`
- all `6`

## `v110` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v110_v109_local_speech_leak_artifact_paired_0007like_bundle_v1_ft1`

初始化：

- `v109`

teacher：

- `v81`

关键 selector：

- leak view：
  - `sample_ids_local_speech_leak_0007_like_proxy_v1_all.txt`
- artifact view：
  - `sample_ids_hard_present_artifact_0007_like_proxy_v1_all.txt`

selector 激活：

- train
  - `overlap_interference_extra = 3 / 108`
  - `branch_protect = 3 / 108`
  - `branch_protect_teacher = 3 / 108`
- val
  - `overlap_interference_extra = 2 / 39`
  - `branch_protect = 3 / 39`
  - `branch_protect_teacher = 3 / 39`

## 自动验收结果

### relative `v81`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +3.2903 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +1.2213 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.9344 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +1.6590 dB`
- `near-real tradeoff gate = pass`
- `phone_artifact_gate_v1 = pass`

### relative `v109`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.6973 dB`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.1458 dB`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.2610 dB`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.2186 dB`
- `near-real tradeoff gate = pass`
- `phone_artifact_gate_v1 = pass`

## near-real 结果

### `v81 vs v110`

- whole-utterance：
  - `better_source_retention_candidate_counts = v81:3, n/a:1`
  - `better_retention_minus_leak_candidate_counts = v110:1, tie:1, v81:1, n/a:1`
  - `near_real_0007`
    - `better_retention_minus_leak = v81`
    - `delta_target_capture_db = -2.8253 dB`
    - `delta_retention_minus_leak_db = -2.6063 dB`
- overlap-local：
  - `better_retention_minus_speech_leak_candidate_counts = v110:2, tie:1, n/a:1`
  - `better_retention_minus_total_leak_candidate_counts = v110:1, tie:1, v81:1, n/a:1`
  - `more_artifact_proxy_heavy_candidate_counts = v110:2, tie:2`
  - `near_real_0007`
    - `better_retention_minus_speech_leak = v110`
    - `better_retention_minus_total_leak = v81`
    - `more_artifact_proxy_heavy = v110`

### `v109 vs v110`

- whole-utterance：
  - `better_source_retention_candidate_counts = v109:1, tie:2, n/a:1`
  - `better_retention_minus_leak_candidate_counts = v109:1, tie:2, n/a:1`
  - `near_real_0007`
    - `better_retention_minus_leak = v109`
    - `more_interference_leaky = v110`
- overlap-local：
  - `better_retention_minus_speech_leak_candidate_counts = v109:1, v110:1, tie:1, n/a:1`
  - `better_retention_minus_total_leak_candidate_counts = v109:2, tie:1, n/a:1`
  - `more_artifact_proxy_heavy_candidate_counts = v110:1, tie:3`
  - `near_real_0007`
    - `better_retention_minus_speech_leak = v110`
    - `better_retention_minus_total_leak = v109`

## 当前裁决

1. `v110` 证明：
   - paired dual-view 即使精确落在同一批 `0007-like` base id 上，
   - 也仍会把 `0007` 往“speech-only leak 更小”方向继续推。
2. 但这个增益没有转成：
   - 更好的 whole-utterance tradeoff，
   - 也没有转成更好的 `0007` total-leak / retention 结果。
3. `phone_artifact_gate_v1` 继续 pass，
   - 只说明没有回到 `v103 / v107` 那种电话音失败，
   - 不说明 `0007` 已被自动修好。

因此当前正式裁决是：

- `v110 = objective_positive_but_over_suppressive`
- 不导 blind 听审
- 不继续 `v110+` 同构小步 sweep

## 下一步

默认下一步改为：

1. 收口 `v110`；
2. 不再继续“`v81` teacher + paired dual-view”这一路同构微调；
3. 如果继续 `0007` 子题，
   - 应改成更保守的 self-anchor 约束，
   - 先保住 `v109` 的 whole-tradeoff，
   - 再观察局部 leak 改善是否还能留下。
