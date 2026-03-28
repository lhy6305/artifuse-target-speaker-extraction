# 2026-03-28 overlap-refine split-present activation-guard `v121 / v122` follow-up

## Summary

- 延续 `v120 = v113 + split target-present / target-absent local control current_residual v1`
  这条 active 语义线，
  本轮连续做了两个 present-head activation-guard pilot：
  - `v121 = v120 + hard present gate floor 0.8`
  - `v122 = v120 + soft present gate power 2.0`
- 最终结论：
  - `v121` 证明 activation guard 方向本身是对的，
    因为它确实修到了：
    - `near_real_0009` absent local speech leak
    - `near_real_0007` local `speech_only` leak
    但 hard floor 过硬，直接把 synthetic 与 whole-tradeoff 一起拉坏；
  - `v122` 证明 soft gate shaping 才是更对的 continuation：
    - relative `v120` 四条 synthetic 固定验收重新全绿
    - whole near-real tradeoff gate 重新通过
    - overlap-local total leak relative `v120` 全样本继续下降
    - `near_real_0006 / 0009` local speech leak 也继续改善
    - 但 `near_real_0007` local `speech_only` leak 仍未转正
    - `export_ab_listening_pack.py` relative `v120` 仍是 `0 candidate sample`
- 因此当前裁决是：
  - `v121 = reject`
  - `v122 = keep active but still not listening candidate`

## Setup

共同前提：

- init:
  - `v120`
- teacher:
  - `v109`
- train manifest:
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- val manifest:
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
- 只训练：
  - `branch_overlap_refine_present_head`
- shared base semantics 保持：
  - `enable_branch_overlap_refine_head = true`
  - `enable_branch_overlap_refine_present_head = true`
  - `branch_overlap_refine_gate_mode = complement`
  - `branch_overlap_refine_source_mode = residual`
  - `branch_overlap_refine_present_source_mode = current_residual`

差异只有 present-head activation shaping：

- `v121`
  - `branch_overlap_refine_present_gate_floor = 0.8`
- `v122`
  - `branch_overlap_refine_present_gate_power = 2.0`
  - `branch_overlap_refine_present_gate_floor = 0.0`

实现补充：

- 本轮额外把 present head 的 activation shaping 参数化为：
  - `branch_overlap_refine_present_gate_power`
- 这样：
  - `v121` 的 hard floor 逻辑可以原样复现；
  - `v122` 则走 soft `gate^p` 路径，
    不再用硬阈值切断中低 gate 区域。

## `v121` relative `v120`

### Synthetic

- `overlap_abstention_proxy_v4`
  - `-0.6085 dB`
  - `2 improve / 4 regress / 2 near tie`
- `same_gender_present_keep_guardrail_v1`
  - `-0.2018 dB`
  - `7 improve / 4 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `-0.2776 dB`
  - `1 improve / 7 regress / 8 near tie`
- `hard_present_artifact_proxy_v1`
  - `+0.1089 dB`
  - `2 improve / 3 regress / 2 near tie`

结论：

- hard floor 不是 no-op；
- 但它已经开始系统性伤到 synthetic keep / artifact guardrail，
  尤其 `hard_present keep` 明显回退。

### Whole near-real

- `more_interference_leaky = tie:1, v121:3`
- `better_retention_minus_leak = tie:1, v120:2, not_applicable:1`
- `tradeoff gate = fail`

关键样本：

- `near_real_0007`
  - `delta_target_capture_db = +0.2544 dB`
  - `delta_interference_capture_db = +3.0218 dB`
  - `delta_retention_minus_leak_db = -2.7674 dB`
- `near_real_0009`
  - `delta_interference_capture_db = +1.3610 dB`
- `near_real_0006`
  - `delta_interference_capture_db = +1.5398 dB`
  - `delta_retention_minus_leak_db = -1.6293 dB`

解释：

- hard floor 确实抑制了 present head 的活动区域，
  但 whole-utterance 上已经明显变成：
  - 目标保持差不多
  - 干扰泄漏更高

### Overlap-local

- `more_speech_interference_leaky = tie:1, v121:1, v120:2`
- `more_total_interference_leaky = tie:1, v121:2, v120:1`
- `better_retention_minus_speech_leak = tie:1, v120:1, v121:1, not_applicable:1`
- `better_retention_minus_total_leak = tie:1, v120:2, not_applicable:1`

关键样本：

- `near_real_0009`
  - `delta_speech_interference_capture_db = -9.7150 dB`
  - 说明 absent local speech leak relative `v120` 确实修好了
- `near_real_0007`
  - `delta_speech_interference_capture_db = -8.1160 dB`
  - `delta_total_interference_capture_db = +1.2538 dB`
  - `delta_retention_minus_speech_leak_db = +8.2985 dB`
  - `delta_retention_minus_total_leak_db = -1.0713 dB`
  - 说明 hard floor 把 `speech_only` local leak 拉回来了，
    但 total leak 反而更差
- `near_real_0006`
  - `delta_speech_interference_capture_db = +2.6564 dB`
  - `delta_retention_minus_speech_leak_db = -2.7470 dB`

裁决：

- `v121` 的价值只在于证明：
  - present-head activation guard 确实能动到 `0007 / 0009` 的局部 blocker；
- 但 hard floor 是错误实现，
  因为它把 whole / synthetic 一起拉坏。

## `v122` relative `v120`

### Training

- checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v122_v120_splitpresent_gatepower2_0007like_v1_ft1`
- 训练成功结束
- `elapsed_sec = 14.324`
- selector 激活与 `v120 / v121` 对齐：
  - train
    - `reconstruction_extra = 63 / 108`
    - `overlap_interference_extra = 3 / 108`
    - `branch_protect = 3 / 108`
    - `branch_protect_teacher = 3 / 108`
  - val
    - `reconstruction_extra = 0 / 39`
    - `overlap_interference_extra = 3 / 39`
    - `branch_protect = 3 / 39`
    - `branch_protect_teacher = 3 / 39`

### Synthetic

- `overlap_abstention_proxy_v4`
  - `+0.6248 dB`
  - `8 improve / 0 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+0.6687 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+0.4796 dB`
  - `15 improve / 0 regress / 1 near tie`
- `hard_present_artifact_proxy_v1`
  - `+0.5698 dB`
  - `6 improve / 0 regress / 1 near tie`

解释：

- `v122` 和 `v121` 最大区别不在数值大小，
  而在方向重新统一了：
  - four fixed synthetic checks relative `v120` 全部重新回正；
- 这说明 hard floor 的问题不是“guard 不该加”，
  而是“guard 不能加得太硬”。

### Whole near-real

- `more_interference_leaky = v120:3, tie:1`
- `better_retention_minus_leak = v122:1, tie:2, not_applicable:1`
- `tradeoff gate = pass`

关键样本：

- `near_real_0007`
  - `delta_target_capture_db = -0.3321 dB`
  - `delta_interference_capture_db = -4.1793 dB`
  - `delta_retention_minus_leak_db = +3.8471 dB`
- `near_real_0006`
  - `delta_target_capture_db = -0.0788 dB`
  - `delta_interference_capture_db = -0.9442 dB`
  - `delta_retention_minus_leak_db = +0.8654 dB`
- `near_real_0003`
  - `delta_target_capture_db = -0.3321 dB`
  - `delta_interference_capture_db = -0.8159 dB`
  - `delta_retention_minus_leak_db = +0.4838 dB`
- `near_real_0009`
  - `delta_interference_capture_db = +0.2101 dB`
  - 未继续恶化，但也没有形成 decisive absent whole gain

解释：

- `v122` relative `v120` 的 whole-utterance 结论已经很清楚：
  - target retention 小幅回退但都低于 decisive threshold；
  - interference leak 在三个 target-present 样本上全部继续下降；
  - `0007` whole tradeoff 继续明显前进；
- 这条线已经不再是 `v121` 那种“局部修一点，全局坏一片”。

### Overlap-local

- `more_speech_interference_leaky = v120:3, tie:1`
- `more_total_interference_leaky = v120:4`
- `better_retention_minus_speech_leak = tie:1, v122:1, v120:1, not_applicable:1`
- `better_retention_minus_total_leak = tie:1, v122:2, not_applicable:1`
- `more_artifact_proxy_heavy = tie:4`

关键样本：

- `near_real_0006`
  - `delta_speech_interference_capture_db = -3.0518 dB`
  - `delta_total_interference_capture_db = -3.0518 dB`
  - `delta_retention_minus_speech_leak_db = +2.9720 dB`
  - `delta_retention_minus_total_leak_db = +2.9720 dB`
- `near_real_0009`
  - `delta_speech_interference_capture_db = -1.4628 dB`
  - `delta_total_interference_capture_db = -1.4628 dB`
  - absent local speech peak relative `v120` 继续改善
- `near_real_0003`
  - `delta_speech_interference_capture_db = -0.8149 dB`
  - `delta_retention_minus_speech_leak_db = +0.4829 dB`
  - 虽未过 decisive threshold，但方向继续更干净
- `near_real_0007`
  - `delta_speech_interference_capture_db = +0.4987 dB`
  - `delta_total_interference_capture_db = -2.1068 dB`
  - `delta_retention_minus_speech_leak_db = -0.7969 dB`
  - `delta_retention_minus_total_leak_db = +1.8086 dB`

解释：

- `v122` relative `v120` 已把 overlap-local total leak 推成：
  - `v120:4` 全样本更 leak；
- 但真正未解的 blocker 现在已经被收窄到：
  - `near_real_0007` 的 `speech_only` local leak 仍未转正；
- 也就是说，
  soft gate power 已经把问题从：
  - `0007 + 0009` 双 blocker
  收口成更单一的：
  - `0007 speech_only local leak` blocker。

## Listening export

- `export_ab_listening_pack.py`
  - relative `v120`
    - `0 candidate sample`

解释：

- 这轮已经明显比 `v121` 更值得保留；
- 但还没有跨过当前 listening-pack 的导包阈值，
  不能直接进入正式听审。

## Decision

- `v121 = hard_floor_fixes_local_but_breaks_global`
- `v122 = soft_gate_power_recovers_global_and_improves_local_total_leak_but_still_not_listening_candidate`
- 当前不导听审
- split local-control semantics 保持活跃

## New information

这轮新增的最重要信息是：

1. hard activation floor 确实能修 `0007 / 0009` 的局部 leak，
   所以问题不在“要不要做 activation guard”，
   而在“guard 的实现不能太硬”；
2. soft `gate^2` shaping 相对 `v120` 已经同时满足：
   - synthetic 四条固定验收全绿
   - whole near-real tradeoff gate 通过
   - overlap-local total leak 全样本继续下降；
3. 因此 split local-control semantics 现在的剩余 blocker
   已被缩小为：
   - `near_real_0007` local `speech_only` leak`
   而不是 `0007 / 0009` 继续一起卡住；
4. 但 soft gate shaping 本身仍不足以把这条 blocker
   直接推到 listening-candidate 阈值。

## Next default

默认下一步更新为：

1. 收口 `v121`
2. 保留 `v122` 作为 split local-control semantics 的当前最佳自动口径 continuation
3. 不回退到 `hard floor` family
4. 若继续 `0007` 子题，
   下一轮应直接补：
   - present head 对 `speech_only local leak` 的显式局部目标 / selector
   - 或其它不会重新伤到 whole-tradeoff 的 soft veto 机制
5. 不再把：
   - `gate_floor`
   - `gate_threshold`
   当成同构 sweep 继续扫
