# 2026-03-18 Synthetic Dual Proxy Gate

## 背景

当前接班口径已经收敛到：

- `v8` 保留为 broad speech 参考基座；
- `v12` 保留为当前 anchor-focused 第二候选；
- `v13 / v14 / v15` 都不保留。

但到这一轮为止，还缺一条显式脚本化的 synthetic gate，去回答下面这个更窄的问题：

- 候选版本是否至少保住了 `v12` 在 `guodegang_anchor_proxy_v1` 上的收益；
- 同时又没有在新重建的 absent-side proxy 上低于 `v12`。

如果没有这条 gate，就容易只因为：

- `anchor_proxy_v1` 还在变强；

就把候选误看成“离修好 `absent_480s` 很近”。

## 工程落地

本轮新增：

- `scripts/eval/gate_synthetic_dual_proxy.py`

作用：

1. 读取已有 compare `summary.json`；
2. 对每条规则直接比较：
   - `overall.avg_sisdr_delta_db`
3. 支持两类规则：
   - `floor`
   - `improvement`

当前默认用法是：

- `anchor_proxy_v1`：
  - 走 `floor`
  - 候选不能低于 `v12`
- `guodegang_absent_proxy_v3_strict / v4_broad`：
  - 走 `improvement`
  - 候选至少不能低于 `v12`

换句话说，这条 gate 的语义不是：

- “候选一定比 `v8` 更强”

而是更保守的：

- “如果连 `v12` 这条当前保留次候选都过不去，就不要再继续把它当 absent follow-up 方向。”

## 基础验证

编译：

```powershell
.\python.exe -m py_compile scripts/eval/gate_synthetic_dual_proxy.py
```

sanity check：

- `tmp/synthetic_dual_proxy_gate_v12_selfcheck.json`
- 结果：
  - `PASS`

说明：

- 这不是一条“谁来都 FAIL”的死门；
- 至少对当前参考 `v12` 自身是自洽的。

## 回放验证

### `v13`

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1_on_guodegang_absent_proxy_v3_strict/synthetic_dual_proxy_gate_vs_v12.json`

结果：

- `FAIL`

规则拆解：

- `anchor_proxy_v1`
  - `v13 - v12 = +0.893597 dB`
  - `PASS`
- `absent_proxy_v3_strict`
  - `v13 - v12 = -0.111381 dB`
  - `FAIL`
- `absent_proxy_v4_broad`
  - `v13 - v12 = -0.104639 dB`
  - `FAIL`

解释：

- `v13` 不是 anchor 没保住；
- 它的问题更准确地是：
  - anchor 继续增强了；
  - 但 absent-side synthetic gate 双双低于 `v12`。

### `v14`

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1_on_guodegang_absent_proxy_v3_strict/synthetic_dual_proxy_gate_vs_v12.json`

结果：

- `FAIL`

规则拆解：

- `anchor_proxy_v1`
  - `v14 - v12 = -0.390675 dB`
  - `FAIL`
- `absent_proxy_v3_strict`
  - `v14 - v12 = -0.284848 dB`
  - `FAIL`
- `absent_proxy_v4_broad`
  - `v14 - v12 = -0.138256 dB`
  - `FAIL`

解释：

- `v14` 是三项一起失败；
- 因而它不只是“absent 没补好”，而是 synthetic dual-proxy gate 整体都不过线。

### `v15`

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1_on_guodegang_absent_proxy_v3_strict/synthetic_dual_proxy_gate_vs_v12.json`

结果：

- `FAIL`

规则拆解：

- `anchor_proxy_v1`
  - `v15 - v12 = +0.322262 dB`
  - `PASS`
- `absent_proxy_v3_strict`
  - `v15 - v12 = -0.126638 dB`
  - `FAIL`
- `absent_proxy_v4_broad`
  - `v15 - v12 = -0.078349 dB`
  - `FAIL`

解释：

- `v15` 的 synthetic 形态与真实侧结论一致：
  - anchor 还能继续加强；
  - absent 仍没有被拉回到 `v12` 之上。

## 当前结论

1. synthetic dual-proxy gate 已经脚本化。
2. 它能稳定复现本轮人工结论：
   - `v13`：
     - anchor 通过
     - absent 双失败
   - `v14`：
     - anchor / absent 全失败
   - `v15`：
     - anchor 通过
     - absent 双失败
3. 因而下一步若继续做新的 absent objective / gate 设计，应该把这条 synthetic dual-proxy gate 当成 pre-screen，而不是只看：
   - `anchor_proxy_v1`
   - 或单条 absent proxy

## 对下一步的影响

1. 以后任何 `v12+` 候选，如果：
   - `anchor_proxy_v1` 通过；
   - 但 `absent_proxy_v3_strict / v4_broad` 仍双双低于 `v12`；
   就不要再把它当成“在修 absent”的路线。
2. 这条 gate 只负责 synthetic objective 方向预筛；
   - 不替代：
     - broad speech gate
     - real `guodegang` clip 级 guardrail
3. 下一步更合理的工作，不是继续扫 `v15` 类小步长 warm-start；
   而是设计一条能先在这条 synthetic dual-proxy gate 上过线的新 objective。
