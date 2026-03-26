# 2026-03-26 overlap-local benchmark on `v81 / v88 / v95 / v100 / v101`

## 本轮目标

- 不重导音频；
- 直接复用：
  - real-eval 原始组件
  - 现有 listening pack 导出音频
- 自动物化 overlap-local 窗口，再检查 localized 指标是否比 whole-utterance tradeoff 更贴近人耳。

## 新增脚本与产物

新增脚本：

- `scripts/eval/build_overlap_local_benchmark_manifest.py`
- `scripts/eval/analyze_overlap_local_benchmark.py`

新增产物：

- `reports/eval/overlap_local_benchmark_manifest_residual_speech_leak_floor_v1.jsonl`

已回放 pack：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v88_blind`
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v95_blind`
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v100_blind`
- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v101_blind`

## 窗口选择规则

- target-present：
  - 先用原始 `sample_meta.json` 里 `target_raw.segment_start_sec / clip_start_sec`
    还原 target 活跃区间；
  - 再在活跃区间内扫描 `1.0s` 窗；
  - 用 `sqrt(target_energy * speech_energy)` 选 overlap 峰值窗。
- target-absent：
  - 直接选 speech interference 能量最高的 `1.0s` 窗。

当前 manifest 结果：

- `near_real_0003`
  - `window_start_sec = 0.49`
- `near_real_0006`
  - `window_start_sec = 0.55`
- `near_real_0007`
  - `window_start_sec = 0.53`
- `near_real_0009`
  - `window_start_sec = 1.82`

## 实现修正

本轮不是只跑脚本，还补了两个分析口径 bug：

1. `human_alignment_summary` 不能把 `more_*_leaky / more_artifact_proxy_heavy` 直接和人耳优选同向比较
   - 这些列输出的是“更差的一边”
   - 对齐统计必须先翻成“隐含更好的一边”
2. 人耳标签不能只读 `listening_review_decoded_summary.json`
   - `v81 vs v100` 只有：
     - `listening_sheet.csv`
     - `blind_key.json`
   - 脚本已补回退逻辑

## decisive 样本

已知听审里真正分出胜负的样本只有 `5` 个：

- `v81 vs v88`
  - `near_real_0007 = v81`
  - `near_real_0009 = v81`
- `v81 vs v95`
  - `near_real_0007 = v81`
- `v81 vs v100`
  - `near_real_0007 = v81`
- `v81 vs v101`
  - `near_real_0009 = v81`

## 对齐结果

### whole-utterance 指标

- `more_interference_leaky`
  - `5 / 5` decisive 样本全部与人耳反向
- `better_retention_minus_leak`
  - `0` 对齐
  - `2` 反向
  - `1` tie
  - `2` not_applicable
- `more_residual_heavy`
  - `5` 个 decisive 样本全部只给 `tie`

解释：

- whole-utterance leak tradeoff 会把：
  - 更静
  - 但更糊
  - 或更有伪影
  的新候选误判成更优；
- 它已经不适合继续做 overlap frontier 终裁。

### overlap-local 指标

- `better_retention_minus_speech_leak`
  - 在 `3 / 3` 个 target-present decisive 样本上全部对齐人耳
  - 对 absent 样本为 `not_applicable`
- `more_artifact_proxy_heavy`
  - `4 / 5` decisive 样本对齐人耳
  - 只在 `v88 / near_real_0007` 上给了 `tie`
- `more_speech_interference_leaky`
  - `3` 对齐
  - `2` tie
  - 没有反向
- `more_total_interference_leaky`
  - `2` 对齐
  - `3` 反向

解释：

- 当前最像人耳的，不是 total interference，而是：
  - speech-only leak
  - retention-minus-speech-leak
  - artifact share
- `near_real_0007` 这类 `music_plus_speech` hard-present case 会污染 total-interference 指标。

## 样本级解释

### `near_real_0007`

- 人耳真实在意的是：
  - target 保真
  - 局部 speech leak
  - artifact
- `v95 / v100`
  - localized `better_retention_minus_speech_leak`
    都指向 `v81`
  - localized `more_artifact_proxy_heavy`
    都指向新候选更差
- 这和听审里：
  - `v81 > v95`
  - `v81 > v100`
  完全一致。

### `near_real_0009`

- whole-utterance tradeoff 一直把新候选判成“更不漏”
- 但人耳在：
  - `v88`
  - `v101`
  两次都还是选 `v81`
- localized `speech leak` 与 `artifact proxy`
  两次都能回到 `v81`，更接近真实听感。

## 当前结论

- overlap-local benchmark 不是噪声；
- 它已经证明：
  - whole-utterance leak tradeoff 会系统性误导 overlap frontier；
  - localized `speech leak / retention-minus-speech-leak / artifact proxy`
    更接近人耳。

更具体地说：

- target-present overlap：
  - 以后优先看
    - `better_retention_minus_speech_leak_candidate`
    - `more_speech_interference_leaky_candidate`
    - `more_artifact_proxy_heavy_candidate`
- target-absent speech-only：
  - `more_speech_interference_leaky_candidate`
  - `more_artifact_proxy_heavy_candidate`
  比 whole-utterance tradeoff 更可信
- `more_total_interference_leaky_candidate`
  保留为辅助列，不再作为主裁决列。

## 下一步建议

- 当前若继续开新机制题，先把 overlap-local benchmark 固化成固定回放链；
- 新候选在进入 focused 听审前，先至少回放：
  - `v81` 对照
  - `near_real_0003 / 0006 / 0007 / 0009`
  - localized `speech leak / retention-minus-speech-leak / artifact proxy`
- 后续若要继续提高人耳对齐，还可以考虑：
  - 把 `artifact proxy` 再拆成更明确的 hard-present 局部失真诊断。
