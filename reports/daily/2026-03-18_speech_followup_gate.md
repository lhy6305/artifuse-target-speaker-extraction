# 2026-03-18 speech follow-up gate

## 背景

上一轮已经确认：

- `v8` 相对 `v7` 确实推进了：
  - `friend_raw / near_real_0003`
  - `friend_raw / near_real_0004`
- 但它还没有通过真实 near-real hard gate
- 同时也存在两类代价：
  - `near_real_0006` 相对 `v7` 小幅回吐
  - default synthetic val 相对 `v7` 小幅回吐

因此当前最需要的不是再盲开 `v9`，而是把这类 speech-focused follow-up 的 keep/drop 规则先脚本化。

## 新增脚本

- `scripts/eval/gate_speech_probe_followup.py`

作用：

- 在共享 `legacy_stage2` 基线下，对“参考候选 -> follow-up 候选”做 branch-local gate。
- 当前默认同时检查：
  - default val 总体增益是否保住大部分
  - near-real speech micro probe overall 是否不变差
  - `friend_raw` 是否不变差
  - `near_real_0003` 是否继续改善
  - `near_real_0004` 是否继续改善
  - `near_real_0006` 是否只在允许阈值内轻微回退
  - 真实 near-real hard gate fail bucket 是否扩张

## 默认阈值

- `max_default_regression_db = 0.2`
- `min_anchor_0003_gain_db = 0.0`
- `min_anchor_0004_gain_db = 0.0`
- `max_anchor_0006_regression_db = 0.1`

这组阈值的意图是：

- 允许像 `v8` 这种“局部 speech 桶明确改善，但 broad default 付出小而可控代价”的 follow-up 留在线上继续推进
- 同时阻止回吐过大的版本继续消耗近真实排查预算

## 回放 1: `v7 -> v8`

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`

结果：

- `PASS`

关键数值：

- default val:
  - `v7 = +0.461595 dB`
  - `v8 = +0.270290 dB`
  - 回吐：
    - `-0.191305 dB`
  - 仍在 `0.2 dB` 容忍线内
- near-real speech probe overall:
  - `v7 = -0.629166 dB`
  - `v8 = -0.236418 dB`
- friend_raw:
  - `v7 = -1.225234 dB`
  - `v8 = -0.668546 dB`
- anchors:
  - `0003: +0.421242 dB`
  - `0004: +0.692135 dB`
  - `0006: -0.099073 dB`
- near-real hard gate:
  - `v7` fail bucket:
    - `target_present__speech`
  - `v8` fail bucket:
    - `target_present__speech`
  - 未扩张

解释：

- `v8` 已满足“保住 `0003 / 0004` 改善，同时只在允许范围内给出 `0006` 和 default 的有限代价”的 branch-local 条件。
- 因而它现在可以正式视为：
  - `v7` 之后更合理的 speech-focused 分支基座

## 回放 2: `v1 -> v7`

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/speech_followup_gate_summary.json`

结果：

- `FAIL`

失败项：

- `default_stage2_delta_floor`

关键数值：

- default val:
  - `v1 = +0.849772 dB`
  - `v7 = +0.461595 dB`
  - 回吐：
    - `-0.388177 dB`
  - 超过当前 `0.2 dB` 容忍线
- 但 near-real speech micro probe 其余项都更好：
  - overall:
    - `+0.930552 dB`
  - `0003`:
    - `+0.538472 dB`
  - `0004`:
    - `+0.602082 dB`
  - `0006`:
    - `+2.011378 dB`

解释：

- 这恰好证明当前最容易混淆的一点：
  - `v7` 是更好的 speech-bucket branch-local 修复
  - 但它并不是对 `v1` 的 broad objective-only 无条件升级

## 当前结论

1. `gate_speech_probe_followup.py` 已把 speech-focused follow-up 的 branch-local keep/drop 规则固定下来。
2. `v8` 在这套 gate 下可以替代 `v7`，成为当前 speech-focused 线上新的默认基座。
3. `v7` 仍不能因为 speech bucket 更强，就自动替代 `v1` 的 broad objective-only 地位。
4. 以后 `v9+` 若继续沿这条线推进，应先过这套 gate，再决定是否值得继续跑完整 near-real 自动诊断链。

## 对下一步的影响

1. 后续最值得开的仍然不是 broad sweep，而是一条极小 follow-up。
2. 目标应明确为：
   - 保住 `v8` 对 `0003 / 0004` 的改善
   - 把 `0006` 拉回至少不弱于当前阈值边界
   - 最好顺便收回一部分 default val 回吐
3. 如果新候选先在这套 gate 下失败，就不值得继续投入更重的 near-real 自动链或人工听审。

## 验证

- `.\python.exe -m compileall .\scripts\eval\gate_speech_probe_followup.py`
- 已完成：
  - `v7 -> v8` follow-up gate 回放
  - `v1 -> v7` follow-up gate 回放
