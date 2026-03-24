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

建议先听：

1. `stage2_vs_v64`
2. `stage2_vs_v32`

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
