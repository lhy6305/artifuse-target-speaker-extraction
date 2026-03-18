# 2026-03-18 near-real speech probe v1

## 背景

上一轮已把 near-real `target_present__speech` bucket 拆到样本级，并确认当前真正卡住的只有三条：

- `near_real_0003`
- `near_real_0004`
- `near_real_0006`

同时也发现，现有 broad synthetic speech proxy 仍把 `v1` 排在 `v7` 前面，和 near-real 诊断想表达的“`v7` 更像保守升级锚点”不一致。

因此本轮目标不是继续开 `v8`，而是补一个更贴近当前 near-real speech bucket 的 micro objective probe，先判断：

- broad synthetic regrouping 是否在把 `v1 / v7` 排错顺序
- 未来小步 follow-up 到底该以 `v1` 还是 `v7` 为基座

## 新增脚本

- `scripts/data/build_near_real_speech_probe_manifest.py`
- `scripts/eval/analyze_near_real_speech_probe.py`

## probe 设计

probe manifest:

- `data/probes/near_real_speech_probe_v1_manifest.jsonl`

样本数：

- 24

只覆盖三类真实锚点：

- `near_real_0003`
  - `friend_raw`
  - hypothesis: `residual_transient_like`
- `near_real_0004`
  - `friend_raw`
  - hypothesis: `speech_leak_like`
- `near_real_0006`
  - `guodegang_raw`
  - hypothesis: `transient_like`

构造原则：

- 目标片段直接取 near-real 对应 target clip
- 参考音频直接沿用 near-real 对应 reference slot
- 干扰只使用真实近源族：
  - `friend_raw`
  - `guodegang_raw`
- 仅做 full-overlap target-present speech probe
- 对每个锚点只做小范围 speech slice / gain sweep，不扩到 music 或其他 source family

## 运行结果

### 1. `legacy_stage2 vs legacy_transient_leakguard_probe_v1`

compare:

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v1_on_near_real_speech_probe_v1/summary.json`

analysis:

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

整体：

- `avg_sisdr_delta_db = -1.559718`
- `improved_count = 2`
- `regressed_count = 21`

按锚点：

- `near_real_0003`: `-2.076664`
- `near_real_0004`: `-1.514359`
- `near_real_0006`: `-0.852338`

### 2. `legacy_stage2 vs legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`

compare:

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_speech_probe_v1/summary.json`

analysis:

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

整体：

- `avg_sisdr_delta_db = -0.629166`
- `improved_count = 5`
- `regressed_count = 16`

按锚点：

- `near_real_0003`: `-1.538192`
- `near_real_0004`: `-0.912277`
- `near_real_0006`: `+1.159040`

### 3. `legacy_transient_leakguard_probe_v1 vs legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`

compare:

- `reports/eval/compare_v1_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_speech_probe_v1/summary.json`

analysis:

- `reports/eval/compare_v1_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/summary.json`

整体：

- `avg_sisdr_delta_db = +0.930552`
- `improved_count = 24`
- `regressed_count = 0`

按锚点：

- `near_real_0003`: `+0.538472`
- `near_real_0004`: `+0.602082`
- `near_real_0006`: `+2.011378`

## 当前结论

1. 这套 near-real-aligned micro probe 给出的排序，和上一轮 broad synthetic speech proxy 不同，而且明显更接近 near-real 样本级诊断。
2. `v7` 虽然仍没有在这套 probe 上整体超过 `legacy_stage2`，但它已经显著优于 `v1`。
3. `v7` 相对 `v1` 是全样本全锚点更优，不是只在局部 gain 或局部 source slice 上偶然占优。
4. `near_real_0006` 型 `guodegang_raw / transient_like` 子问题，在 `v7` 上已经相对 `legacy_stage2` 转正。
5. 当前剩余主缺口主要收缩到：
   - `near_real_0003` 型 `friend_raw / residual_transient_like`
   - `near_real_0004` 型 `friend_raw / speech_leak_like`

## 对下一步的影响

1. future objective-only speech follow-up 的默认基座应从“`v1` 主导”更新为：
   - `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
2. 不建议再继续扩大 broad synthetic speech proxy 的解释权；它已经在 `v1 / v7` 这个排序上暴露出对齐不足。
3. 下一条小步实验若要开，应只围绕：
   - `friend_raw`
   - `near_real_0003 / 0004` 型
   做更保守的 residual / leak 修正。
4. `near_real_0006` 型当前已拿回的收益，应被视为 guardrail，不允许下一条 follow-up 再把它推回负增益。

## 验证

- `.\python.exe -m compileall .\scripts\data\build_near_real_speech_probe_manifest.py`
- `.\python.exe -m compileall .\scripts\eval\analyze_near_real_speech_probe.py`
- `.\python.exe .\scripts\data\build_near_real_speech_probe_manifest.py --force-clean`
- 已实跑 3 组 compare + 3 组 probe analysis
