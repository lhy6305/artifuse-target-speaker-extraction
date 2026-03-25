# 决策关卡听审包说明

本说明对应 2026-03-24 的小规模决策关卡听审。

目标不是重新做大范围候选搜索，
而是用同一组 `near_real_v1` 样本，
快速判断：

1. `v64` 还有没有足够强的可听价值；
2. `v32` 是否只应保留为研究基座；
3. 后续是否应继续沿 `candidate_v7` 细分分析，
   还是先停止并回到更高层决策。

本轮 pack：

- `reports/eval/decision_gate_listening_pack_near_real_v1_stage2_vs_v32_blind`
- `reports/eval/decision_gate_listening_pack_near_real_v1_stage2_vs_v64_blind`

磁盘上另有一个后续合并导出的多候选盲包：

- `reports/eval/decision_gate_listening_pack_near_real_v1_stage2_v32_v64_blind_v2`

它的用途不是改变决策问题，
而是把
`legacy stage2 / v32 / v64`
三者合到同一 GUI 里一次性盲听，
减少分两包来回切换造成的口径漂移。
当前若直接开始人工听审，
默认优先使用这个 `v2` 合并包。

建议先听：

1. 若使用旧双包口径：
   - `stage2_vs_v64`
   - 再 `stage2_vs_v32`
2. 若使用当前默认口径：
   - 直接听 `stage2_v32_v64_blind_v2`

样本集固定为：

- `data/references/real_eval_manifest_near_real_v1.jsonl`
- `near_real_0001` 到 `near_real_0010`

覆盖：

- raw target only
- friend speech leakage
- music
- `guodegang` anchor
- target absent
- harder mixed case
