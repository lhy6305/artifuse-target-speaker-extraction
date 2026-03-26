# 踩坑记录

## 文档定位

- 本文档只保留当前仍会影响日常推进的活跃坑点。
- 历史长版已归档到：
  - `docs/archive/pitfalls/pitfalls_active_snapshot_2026-03-26.md`
- 更早分卷索引见：
  - `docs/archive/pitfalls/README.md`

## 活跃坑点

### 1. PowerShell 默认不是 UTF-8，读取和写入必须显式指定

事实：

- 仓库规范是：
  - 所有代码、脚本、文档统一使用 `UTF-8 无 BOM`
- 但 Windows PowerShell 默认控制台与部分文本命令常落在 `GBK / ANSI` 语境。

要求：

- 读取文本时显式写：
  - `Get-Content -Encoding UTF8 ...`
- 批量搜索或导出文本时，不要依赖 PowerShell 默认编码。
- 新写文件或覆盖文件时，必须确保输出仍是 `UTF-8 无 BOM`。

影响：

- 若忽略这条，最直接的后果就是：
  - 中文文档出现乱码；
  - patch 上下文对不上；
  - 接班时无法判断内容是真坏还是编码坏。

### 2. `01/02` 主文档不能再堆成长流水账

事实：

- `docs/01_project_overview_and_plan.md`
- `docs/02_pitfalls_log.md`

设计初衷是活跃摘要，不是无限增长的总历史。

要求：

- 长历史、逐轮试验、详细样本分析应进入：
  - `reports/daily/`
  - `docs/archive/...`
- 主文档只保留：
  - 当前状态
  - 当前有效结论
  - 当前验收资产
  - 下一步计划

默认处理方式：

- 当主文档达到“明显不利于接班阅读”的规模时，应：
  1. 先归档当前版本快照；
  2. 再重写为短摘要；
  3. 在归档索引里登记新快照入口。

### 3. SI-SDR 不能单独评估 `present keep` 问题

事实：

- 对 `same_gender present keep` 这类切片，`compare_checkpoints_on_manifest.py` 的 SI-SDR 可能会把过静音误判成更好。

要求：

- 这类切片必须再用 near-real 同口径指标复核：
  - `target_capture_db`
  - `interference_capture_db`
  - `residual_output_share`
  - `present_guardrail_violation_count`

### 4. `same_gender present keep` 已经是正式 guardrail，不可再省略

事实：

- `data/synthetic/val_manifest_same_gender_present_keep_guardrail_v1.jsonl`
  已经能复现 `near_real_0003` 风格 failure。

要求：

- 后续凡是 overlap-abstention 分支继续训练，都必须同时验：
  - `overlap_abstention_proxy_v4_audibility_v1`
  - `same_gender_present_keep_guardrail_v1`
  - `real_eval_manifest_residual_speech_leak_floor_v1`

### 5. branch-only reweighting 目前无法同时修好 keep 和 abstain

事实：

- `v73`：
  - 对 keep guardrail 有改善；
  - 但明显拉坏 `near_real_0009`。
- `v74`：
  - 更极端地走向过静音；
  - present violation 反而增加。

结论：

- 继续做同结构权重 sweep，预期收益很低。

### 6. silence-over-leak objective 适合大筛，不适合裁决 frontier

事实：

- `score_silence_over_leak_pack.py`
- `rank_checkpoints_on_silence_over_leak_manifest.py`

已经证明可用于：

- 批量排除明显掉队 checkpoint

但不适合单独用于：

- frontier 间主观几乎打平的最终裁决

### 7. objective 变强不等于可以放行训练

事实：

- `v68 / v69 / v71 / v72 / v73 / v74`
  都出现过：
  - synthetic objective 变强
  - near-real 或主观裁决仍不过

要求：

- 训练放行必须看：
  - near-real
  - guardrail
  - 必要时的人耳

不能只看 objective summary。

### 8. 当前真正的瓶颈已经从 selector 转到 gate 专属监督

事实：

- `proxy_v3 / v4`
- `present_keep_guardrail_v1 / v2`

已经把“缺 selector / 缺数据切片”的问题收窄得差不多了。

当前瓶颈更像：

- keep
- abstain

虽然已经不必完全共享同一条输出自由度，但 `gate` 还没有自己的监督目标。

要求：

- 下一步优先尝试：
  - `abstention_gate_proxy_v1`
  - `gate-level loss`
- 不再默认继续扫普通权重组合。

### 9. `audibility-conditioned objective v1` 单独不够

事实：

- `v75`
  - synthetic abstention 回退
  - keep / near-real guardrail 都比 `v72` 更差

结论：

- `target_energy_ratio` selector 要保留
- 但不能再假设“只要按能量分段调权重就能自然解决”

### 10. joint gate 和 gate-only 都已跑过第一轮反例

事实：

- `v76`
  - joint gate + mask
  - `0009 / 0006` 有真实收益
  - 但把 `0007` 一起压坏
- `v77`
  - gate-only
  - 不再误伤 present
  - 但 abstention 基本退回 safe/no-op

结论：

- gate 机制本身不是伪方向
- 当前缺的是 gate 的专属监督，而不是更多 gate 学习率 sweep

### 11. gate 专属监督成立，但 keep backstop 仍缺 hard-present 覆盖

事实：

- `v78`
  - `abstention_gate_proxy_v1 + gate-level loss`
  - 首次恢复到 present-safe
  - 但 absent 收益不足
- `v79`
  - 加大 gate push 后
  - `near_real_0006 / 0009` 确实更静
  - 但 `near_real_0007` 开始回退

结论：

- 问题已经从“缺 gate supervision”推进到了“缺 hard-present keep guardrail”
- 下一步不该继续扫 gate loss 权重，而应补：
  - `hard_present_gate_keep_guardrail_v1`

## 近期关键案例入口

- `reports/daily/2026-03-26_overlap_abstention_proxy_v3_v4_and_v71_v72_followup.md`
- `reports/daily/2026-03-26_present_keep_guardrail_v1_v2_and_v73_v74_followup.md`
- `reports/daily/2026-03-26_audibility_conditioned_v1_and_abstention_gate_v1_v75_v76_v77.md`
- `reports/daily/2026-03-26_abstention_gate_proxy_v1_and_v78_v79_followup.md`
