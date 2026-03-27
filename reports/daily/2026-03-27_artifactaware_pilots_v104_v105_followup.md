# artifact-aware pilots `v104 / v105` follow-up

## 本轮目标

`hard_present_artifact_proxy_v1` 已经物化完成，接下来要回答的问题不是“proxy 能不能复现 `0007` 风格风险”，而是：

1. 基于 `v81` 的首轮 artifact-aware pilot，能否在不重演 `v103` artifact 失控的前提下，改善 `near_real_0007`。
2. 如果 proxy 上升、near-real 反而下滑，是否应该立刻停止这条小家族。

因此本轮连续推进两个 pilot：

- `v104 = v81 + artifactaware_anchor`
- `v105 = v81 + artifactguard`

## 训练配置

### `v104`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v104_v81_overlap_purify_v3_artifactaware_anchor_ft1`

思路：

- 保留 `v102` 的 `speech_only overlap_interference_extra`
- 保留旧的 keep union
- 对 `hard_present_artifact_proxy_v1` 语义子集增加 `branch_protect_teacher_overlap_weight = 6.0`
- teacher 设为 `v81`

数据：

- `data/synthetic/train_manifest_artifact_aware_bundle_v1.jsonl`
- `data/synthetic/val_manifest_artifact_aware_bundle_v1.jsonl`

结果：

- selector 激活正常
- synthetic 固定验收整体在 `v81` 与 `v102` 之间
- near-real whole-utterance `present_guardrail_violation_count = 0`
- 但 `near_real_0007` 没有形成明确 rescue

### `v105`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v105_v81_overlap_purify_v3_artifactguard_ft1`

思路：

- 去掉 `v104` 的 teacher-overlap anchor
- 直接把 `hard_present_artifact_proxy_v1` 并入更强的 `branch_protect_guard_sisdr`
- 继续保留 `speech_only overlap_interference_extra`

结果：

- synthetic 四条固定验收都排到最前
- `hard_present_artifact_proxy_v1` 也排第一
- 但 near-real `present_guardrail_violation_count = 2`

## 自动评测结果

### `v104`

结论：

- 比 `v103` 安全
- 但也比 `v103` 更“缩回去”
- 对 `near_real_0007` 没有形成真正的局部收益

关键现象：

- whole-utterance `v81 vs v104` 基本打平
- overlap-local 里：
  - `0007`
    - target capture 比 `v81` 更差
    - artifact proxy 也略更重
    - `retention-minus-speech-leak` 也没超过 `v81`

裁决：

- `v104` 不值得再导 focused 听审
- 它说明“teacher anchor 过弱时，只会把 `v103` 拉回中庸，而不会真正解决 blocker”

### `v105`

近实测主验收：

- `reports/eval/rank_residual_speech_leak_floor_v1_v81_v102_v104_v105/summary.json`

局部回放：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v105/tradeoff_debug/summary.json`
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v105/overlap_local_benchmark_debug/summary.json`

一开始我误以为 `v81 vs v105` 的 pack analysis 产物是空的；重跑后确认：

- 分析脚本本身没有坏
- `tradeoff_debug` 和 `overlap_local_benchmark_debug` 都正常得到 `num_samples = 4`
- 之前看到的 `num_samples = 0` 不是当前有效结果

`v105` 的真实结论非常明确：

- synthetic 上最强
  - `overlap_abstention_proxy_v4_audibility_v1`
  - `same_gender_present_keep_guardrail_v1`
  - `hard_present_gate_keep_guardrail_v1`
  - `hard_present_artifact_proxy_v1`
  都能排前
- 但 near-real `0003 / 0007` 同时出现 target capture regression
  - `0003`
    - `v81 = -11.474 dB`
    - `v105 = -13.512 dB`
  - `0007`
    - `v81 = -17.715 dB`
    - `v105 = -19.801 dB`
- overlap-local 上，`v105` 更像“过拟合 proxy 后把两边都压低”
  - `0003`
    - `better_retention_minus_speech_leak = v105`
    - 但 `more_artifact_proxy_heavy = v105`
  - `0006`
    - `better_retention_minus_speech_leak = v105`
    - 但 `more_artifact_proxy_heavy = v105`
  - `0007`
    - `better_retention_minus_speech_leak = v81`
    - `more_artifact_proxy_heavy = v105`

这说明：

- `v105` 的确学会了把 artifact proxy asset 上的分数做高
- 但它没有学会“保住近实测 hard-present target capture 再顺手降 artifact”
- 相反，它把真实目标也一起压下去了

## 本轮裁决

1. `v104` 过于保守，不值得继续。
2. `v105` 是典型的 `hard_present_artifact_proxy_v1` 过拟合候选。
3. `v105` 不应再导听审；automatic 已足够判定它不能升格。
4. `artifact-first` 方向本身没错，但当前这版损失设计仍然过粗。

## 下一步

下一步不再做 `v104+ / v105+` 同结构小步 sweep，而是改成更外科式的新子题：

- 基于 `v81`
- 继续保留 localized `speech leak / retention-minus-speech-leak`
- 但 artifact-aware 约束不再只依赖整条 proxy asset
- 必须显式压住：
  - `near_real_0007` 风格 hard-present music-plus-speech 局部 artifact
- 同时避免再次伤到：
  - `near_real_0003` target capture

更具体地说，下轮要优先设计的是：

- 面向 `0007` 局部窗的 artifact veto / local backstop
- 而不是继续扩大整条 hard-present proxy 的全局 guard weight
