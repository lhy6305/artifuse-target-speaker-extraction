# overlap purify `v2` speech-only selector and `v102` follow-up

## 本轮目标

在不重开新 head 家族的前提下，验证一个更窄的问题：

- `v82` 的 `0007` 黄灯，
- 是否主要来自 overlap residual loss 的 selector 被 `speech_plus_music` 污染，
- 而不是 overlap-local residual 这条方向本身不可用。

因此本轮不换结构，只把 `v82` 的 overlap-local selector 改成真正的 `speech_only` 子域。

## 配置

### `v102 = v81 + overlap purify v2 speech-only selector`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v102_v81_overlap_purify_v2_speechonly_ft1`

初始化：

- `v81`

训练口径：

- 复用 `v82` 的 head / weight / optimizer 设置
- 只训：
  - `branch_decoder_mask_head`
- 保留：
  - `reconstruction_extra`
  - `branch_protect`
  两条 keep 约束
- overlap-local loss 仍是：
  - `overlap_interference_extra_weight = 0.03`
  - `overlap_interference_extra_mode = residual_projection_ratio`

本轮唯一实质变更：

- 把 `v82` 的：
  - `focus_interference_pools = {speech_interference_clean_pool, speech_interference_hard_pool}`
- 改成：
  - `focus_interference_profiles = speech_only`
  - `require_speech_interference = true`
  - `require_music_interference = false`
  - `min_interference_layer_count = 1`
  - `max_interference_layer_count = 1`

## selector 命中规模

相对 `v82` 旧 selector：

- train manifest
  - 旧：`52`
    - 其中 `speech_only = 22`
    - `speech_plus_music = 30`
  - 新：`22`
    - 全部 `speech_only`
- val manifest
  - 旧：`14`
    - 其中 `speech_only = 7`
    - `speech_plus_music = 7`
  - 新：`7`
    - 全部 `speech_only`

结论：

- 本轮确实不是“轻微语义修辞”；
- 它把 `v82` overlap-local loss 的 `plus_music` 污染样本全部移除了。

## 训练结果

训练摘要：

- `elapsed_sec = 14.587`
- `best_val_loss = 0.0270065`

selector 命中：

- train `overlap_interference_extra = 22 / 102`
- val `overlap_interference_extra = 7 / 33`

训练期 loss：

- train `overlap_interference_extra_projection_ratio`
  - epoch1 `0.01376`
  - epoch4 `0.01380`
- val `overlap_interference_extra_projection_ratio`
  - epoch1 `0.007302`
  - epoch4 `0.007075`

说明：

- 新 speech-only overlap loss 被稳定激活；
- 不是 no-op；
- 而且它在更窄 selector 上没有数值崩掉。

## synthetic 固定验收

相对 `v81`：

- `overlap_abstention_proxy_v4_audibility_v1`
  - `+2.8291 dB`
  - `7 improve / 1 regress`
- `same_gender_present_keep_guardrail_v1`
  - `+1.2517 dB`
  - `11 improve / 0 regress`
- `hard_present_gate_keep_guardrail_v1`
  - `+1.0218 dB`
  - `13 improve / 2 regress`

结论：

- `v102` 基本保住了 `v82` 那组 synthetic 正收益；
- 说明把 selector 收窄到 `speech_only`，并没有把 overlap-local residual 这条主效应打没。

## near-real 非盲 objective

非盲包：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v102`

### whole-utterance tradeoff

- `better_source_retention`
  - `v81 = 3`
  - `not_applicable = 1`
- `more_interference_leaky`
  - `v81 = 2`
  - `tie = 2`
- `better_retention_minus_leak`
  - `v102 = 1`
  - `v81 = 1`
  - `tie = 1`
  - `not_applicable = 1`

gate：

- `overall_pass = true`

bandwidth：

- `narrower_candidate_counts = tie: 4`

样本级：

- `near_real_0003`
  - `target_capture_db = -1.161 dB`
  - `interference_capture_db = -2.233 dB`
  - `retention_minus_leak = +1.071 dB`
  - 相对 `v81` 为正 tradeoff
- `near_real_0006`
  - `target_capture_db = -0.982 dB`
  - `interference_capture_db = +0.171 dB`
  - `retention_minus_leak = -1.153 dB`
  - whole-utterance 上反而回退
- `near_real_0007`
  - `target_capture_db = -1.347 dB`
  - `interference_capture_db = -1.057 dB`
  - `retention_minus_leak = -0.290 dB`
  - 仍是 hard-present 黄灯，但比 `v82` 的 `-1.449 / -1.240` 略收窄
- `near_real_0009`
  - `interference_capture_db = -0.123 dB`
  - 接近打平，没有形成明确 absent 改善

### overlap-local benchmark

- `better_retention_minus_speech_leak`
  - `v102 = 2`
  - `v81 = 1`
  - `not_applicable = 1`
- `more_speech_interference_leaky`
  - `v81 = 2`
  - `v102 = 2`
- `more_artifact_proxy_heavy`
  - `v102 = 2`
  - `tie = 2`

target-present 样本解释：

- `near_real_0003`
  - speech leak 更低
  - `retention-minus-speech-leak = +1.072 dB`
- `near_real_0006`
  - speech leak 更低
  - `retention-minus-speech-leak = +1.048 dB`
- `near_real_0007`
  - speech leak 反而更高
  - `retention-minus-speech-leak = -3.006 dB`
  - `artifact_proxy` 更重

解释：

- 这次和 `v82` 最大的不同，不是“全部目标都更强”，而是：
  - `0003 / 0006` 这两个纯 speech target-present case，
    localized speech-only 指标明确变好；
  - `0007` 这个 `speech_plus_music` hard-present case，
    仍然没有被真正解掉，只是 whole-utterance 黄灯略收窄；
  - `0009` absent 也没有形成稳定收益。

## blind 包

已导出并补齐分析：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v102_blind`
- `asset_audit_summary.json`
- `tradeoff_analysis/summary.json`
- `tradeoff_analysis/decision_gate_summary.json`
- `bandwidth_analysis/summary.json`
- `overlap_local_benchmark/summary.json`

当前 blind 映射：

- `candidate_a = v81`
- `candidate_b = v102`

## 当前裁决

1. `speech_only selector` 不是空改动。
   - 它成功把 `v82` overlap selector 里的 `speech_plus_music` 污染全部剥离了。

2. `v102` 保住了 `v82` 的 synthetic 主收益。
   - 这说明 overlap-local residual 方向本身仍然成立。

3. `v102` 还不能自动升格。
   - `0007` 仍然没有被真正修好；
   - `0009` absent 也没有给出明确改进；
   - whole-utterance 只在 `0003` 上给出清晰正结果。

4. `v102` 已经值得进 focused 听审。
   - 原因不是 whole-utterance 变得特别强；
   - 而是 localized speech-only benchmark 首次把：
     - `0003`
     - `0006`
     两个纯 speech target-present case 一起推到更优侧，
     同时 `0007` whole-utterance 黄灯比 `v82` 略收窄。

## 下一步

默认下一步直接做：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v102_blind
```

focused 听审重点：

- `near_real_0003`
  - `v102` 是否真的更干净，且没更空
- `near_real_0006`
  - localized speech-only gain是否终于转成可听改善
- `near_real_0007`
  - 尽管 selector 已剥离 `plus_music`，hard-present artifact / target-preservation 风险是否仍可听
- `near_real_0009`
  - absent case 是否仍然是 `v81` 更自然
