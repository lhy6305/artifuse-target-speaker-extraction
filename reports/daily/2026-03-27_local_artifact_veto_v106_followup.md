# local artifact veto `v106` follow-up

## 本轮目标

在 `v104 / v105` 证明“整条 hard-present artifact proxy 全局加权”仍然过粗之后，本轮改做更外科式的新 pilot：

- 基座仍用 `v81`
- 保留 `speech_only overlap_interference_extra`
- 只对 `hard_present_artifact_local_proxy_v1` 子集加局部 teacher overlap veto

目标不是继续把整条 proxy 做高，而是先回答：

1. `0007` 风格 hard-present music-plus-speech 局部窗，是否能在不重演 `v103 / v105` artifact 回退的前提下得到改善。
2. 这条更局部的 teacher veto，是否足够形成值得导听审的中间解。

## 新增资产

### `hard_present_artifact_local_proxy_v1`

新增脚本：

- `scripts/data/build_hard_present_artifact_local_proxy.py`

做法：

- 从 `hard_present_artifact_proxy_v1` 自动切出 `1.0s` 局部窗；
- 窗口选择规则以高 interference-to-target risk 为主，同时约束 local target share 不至于退化成纯 absent；
- 输出局部 `mixture.wav / target.wav / metadata.json`，并物化新的 train / val manifest。

物化结果：

- `data/synthetic/train_manifest_hard_present_artifact_local_proxy_v1.jsonl`
- `data/synthetic/val_manifest_hard_present_artifact_local_proxy_v1.jsonl`
- `reports/data/selector_hard_present_artifact_local_proxy_v1_train_summary.json`
- `reports/data/selector_hard_present_artifact_local_proxy_v1_val_summary.json`

关键统计：

- train `selected_count = 33`
- val `selected_count = 7`
- 窗口模式全部为 `target_share_bounded_peak`

### 训练 bundle

用于 `v106` 的 bundle：

- `data/synthetic/train_manifest_artifact_local_aware_bundle_v1.jsonl`
- `data/synthetic/val_manifest_artifact_local_aware_bundle_v1.jsonl`

## `v106` 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v106_v81_overlap_purify_v4_local_artifact_veto_ft1`

配置要点：

- `branch_protect_teacher_overlap_weight = 6.0`
- teacher 仍为 `v81`
- teacher selector 只命中：
  - `sample_ids_hard_present_artifact_local_proxy_v1_all.txt`
- 保留：
  - `speech_only overlap_interference_extra`
  - 原 keep-union / branch_protect guard

selector 激活：

- train
  - `overlap_interference_extra = 22 / 160`
  - `branch_protect = 63 / 160`
  - `branch_protect_teacher = 33 / 160`
- val
  - `overlap_interference_extra = 8 / 46`
  - `branch_protect = 27 / 46`
  - `branch_protect_teacher = 7 / 46`

训练摘要：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v106_v81_overlap_purify_v4_local_artifact_veto_ft1/train_summary.json`

## 自动评测结果

### synthetic 固定验收

整体排序特征很明确：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `v106` 排第一
- `hard_present_artifact_local_proxy_v1`
  - `v106` 明显强于 `v81 / v104`
  - 但仍落后 `v102 / v105`
- `same_gender_present_keep_guardrail_v1`
  - `v106` 处于 `v102 / v105` 与 `v81 / v104` 之间
- `hard_present_gate_keep_guardrail_v1`
  - 同样是中间解
- `hard_present_artifact_proxy_v1`
  - 也是中间解，不是最强，但已高于 `v81 / v104`

结论：

- `v106` 不是 `v105` 那种 proxy 过拟合极端点；
- 也不是 `v104` 那种过于保守的回缩；
- 它是这条 local-veto 设计下第一个真正的中间候选。

### near-real whole-utterance

主验收：

- `reports/eval/rank_residual_speech_leak_floor_v1_v81_v102_v104_v105_v106/summary.json`

相对 `v81`：

- `0003`
  - `target_capture`
    - `v81 = -11.474 dB`
    - `v106 = -11.731 dB`
  - `retention_minus_leak`
    - `v81 = 13.064 dB`
    - `v106 = 14.134 dB`
- `0006`
  - `target_capture`
    - `v81 = -4.830 dB`
    - `v106 = -5.059 dB`
  - `retention_minus_leak`
    - `v81 = 26.419 dB`
    - `v106 = 26.650 dB`
- `0007`
  - `target_capture`
    - `v81 = -17.715 dB`
    - `v106 = -16.869 dB`
  - `retention_minus_leak`
    - `v81 = 29.491 dB`
    - `v106 = 29.848 dB`
- `0009`
  - `interference_capture`
    - `v81 = -34.050 dB`
    - `v106 = -33.120 dB`

解释：

- `0003 / 0006 / 0007` 的 whole-utterance backstop 都没坏；
- `0007` 甚至是本轮第一次比 `v81` 更好的 target capture；
- 但 `0009` absent suppression 回退。

### overlap-local

non-blind pack：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106`

正式分析：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106/tradeoff_analysis/summary.json`
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106/overlap_local_benchmark/summary.json`
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106/bandwidth_analysis/summary.json`

关键局部结论：

- `0003`
  - `better_retention_minus_speech_leak = v106`
  - `more_artifact_proxy_heavy = tie`
  - 代价是 target capture 小幅回退
- `0006`
  - `better_retention_minus_speech_leak = tie`
  - `more_speech_interference_leaky = v81`
  - `more_artifact_proxy_heavy = tie`
  - 整体为轻微正向或近 tie
- `0007`
  - `better_source_retention = v106`
  - `more_speech_interference_leaky = v106`
  - `better_retention_minus_speech_leak = v81`
  - `more_artifact_proxy_heavy = tie`
- `0009`
  - `more_speech_interference_leaky = v106`

bandwidth：

- `narrower_candidate_counts = tie: 4`

这说明：

- `v106` 没有再重演 `v103 / v105` 那种“artifact 明显更重”的失败；
- 但 `0007` 的核心 blocker 也还没真正解决；
- 现在更像是：
  - `0007` target capture 更强
  - artifact 不再更差
  - 但 speech leak 仍偏重

## 导包状态

non-blind：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106`

blind：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106_blind`

blind key：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v106_blind/blind_key.json`

说明：

- blind 包里当前 `candidate_a = v81`
- `candidate_b = v106`
- `tradeoff / overlap_local_benchmark / bandwidth` 已全部重跑

## 过程坑点

本轮再次遇到一次“分析目录显示 `num_samples = 0`”的假失败，但原因不是脚本坏掉，而是：

1. 先前第一次 near-real 导包失败时留下了旧 summary；
2. blind 包导出与分析并行跑时，分析脚本先读到了尚未写完的目录。

重跑到正式目录后，`tradeoff / overlap_local_benchmark / bandwidth` 都恢复为 `num_samples = 4`。

## 本轮裁决

`v106` 的结论是：

1. 它是一个真实的中间候选，不再像 `v103 / v105` 那样因为 artifact 更重而可直接淘汰。
2. 但它还没有解决 `0007` 的核心局部问题。
3. 如果只看自动结果，最准确的描述不是“失败”，而是：
   - `artifact` 侧止血成功
   - `speech leak` 侧还没打穿
4. 它当时值得进入一轮很小范围的 focused 听审，但不值得直接开 `v106+` 权重 sweep。

## 听审解盲结果

听审报告：

- `reports/daily/2026-03-27_v81_vs_v106_listening_review.md`

最终结果：

- `v81 = 0`
- `v106 = 0`
- `tie = 4`

解释：

- 四条样本都没有形成可感知差异；
- `0007` 的核心痛点也没有出现主观改善；
- 因此 `v106` 虽然比 `v103 / v105` 更安全，但仍未转化为可听层收益。

## 下一步

默认下一步不做 `v106+`，而是：

1. 收口 `local_artifact_veto` 这一版 teacher-overlap 对齐方案。
2. 如果还继续 `0007` 子题：
   - 下一轮 local veto 不再只做 teacher-overlap 对齐；
   - 要显式把 `music_plus_speech` hard-present 局部窗里的 speech leak 当主约束。
