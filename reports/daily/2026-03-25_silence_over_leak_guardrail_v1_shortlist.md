# 2026-03-25 Silence-Over-Leak Guardrail v1 Shortlist

## 背景

上一轮阶段总结已经明确：

- 默认主线继续是 `legacy stage2`
- `v32` 只保留为研究基座
- `same_gender_reverb` 这条 synthetic 线当前不能再作为训练放行条件
- 新增一条必须显式执行的人耳标准：
  - 当目标已经弱到几乎不可辨时，`完全闭嘴` 优于 `输出几乎全是干扰`

因此下一轮不再先开训练，而是先对这个更窄的子问题做一个新的 near-real 决策关卡。

## 这轮为什么选 `v8 / v13`

当前最像“可能比 `legacy stage2 / v32` 更适合 silence-over-leak 子题”的，不是 `v64`，也不是 `candidate_v7`，而是更早的 absent-guard 家族。

关键依据来自已有 absent probe summary：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1_on_near_real_guodegang_absent_probe_v1/summary.json`
  - `avg_sisdr_delta_db = +2.1351`
  - `improved_count = 3 / 3`
- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_near_real_guodegang_absent_probe_v1/summary.json`
  - `avg_sisdr_delta_db = +1.9524`
  - `improved_count = 3 / 3`
- `reports/eval/compare_v19_vs_v32_on_near_real_guodegang_absent_probe_v1/summary.json`
  - `avg_sisdr_delta_db = -0.0132`
  - `near_tie_count = 3 / 3`

当前可读成大白话：

- `v32` 并没有在 absent 子题上继续超过它的旧 absent-guard 祖先；
- 真正值得复核的历史候选，是 `v8` 和 `v13`；
- `v7` 没被带进来，不是忘了，而是它和 `v8` 同家族且 objective 不如 `v8`；
- `v64` 没被带进来，是因为整轮阶段结论已经把它降级，不再作为独立 active 候选。

## 本轮新关卡资产

### 1. 新 manifest

- `data/references/real_eval_manifest_silence_over_leak_guardrail_v1.jsonl`

包含 `4` 条样本：

- `near_real_0008`
  - target absent / friend speech only
- `near_real_0009`
  - target absent / external speech only
- `near_real_0010`
  - target absent / friend speech + music
- `near_real_0006`
  - target present backstop，防止模型靠“更安静”误过关

这里 `0008 / 0009 / 0010` 是 silence-over-leak 核心，`0006` 只是回归挡板，不是主评分项。

### 2. 三组两两导包

- `reports/eval/ab_listening_pack_silence_over_leak_guardrail_v1_stage2_vs_v32_blind`
- `reports/eval/ab_listening_pack_silence_over_leak_guardrail_v1_stage2_vs_v8_blind`
- `reports/eval/ab_listening_pack_silence_over_leak_guardrail_v1_stage2_vs_v13_blind`

### 3. 四候选最终 blind 包

- `reports/eval/decision_gate_listening_pack_silence_over_leak_guardrail_v1_stage2_v32_v8_v13_blind`

候选顺序解盲后为：

- `legacy_stage2`
- `v32`
- `v8_absentguard`
- `v13_absentguard`

## 当前判断

截至这一步，仍然不能说已经找到“比 legacy 更强的新主线”。

当前更准确的判断是：

1. `v8 / v13` 是最值得进入这条新子题复核的历史候选。
2. `v32` 必须继续留在包里，因为它是当前研究基座，而且 `near_real_0009` 上有真实局部收益。
3. 这轮最优先的人耳问题不是“谁更响”，而是：
   - 谁在 `0008 / 0009 / 0010` 上更接近 `闭嘴而不吐干扰`
   - 同时又不会在 `0006` 上把可用目标一起压没

## 下一步

直接开 GUI 听这个多候选包：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\decision_gate_listening_pack_silence_over_leak_guardrail_v1_stage2_v32_v8_v13_blind
```

听的时候重点看：

- `near_real_0008 / 0009 / 0010`
  - 目标已经不存在时，谁最接近真正闭嘴
  - 谁只是把干扰漏得更少一点，但仍然在“说话”
- `near_real_0006`
  - 有没有候选为了闭嘴而把 target-present 的可用目标一起压坏

这轮听完后，才能决定后续路线到底是：

- 把 `v8 / v13` 中的某条老 absent-guard 线重新升格为研究基座；
- 还是确认 `legacy stage2` 仍然最稳，暂不继续这一窄题训练。
