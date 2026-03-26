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

### 8. `selector -> gate supervision` 这条收窄链已经走完，不应回退

事实：

- `proxy_v3 / v4`
- `present_keep_guardrail_v1 / v2`

已经把“缺 selector / 缺数据切片”的问题收窄得差不多了。

这一步之后的瓶颈更像：

- keep
- abstain

虽然已经不必完全共享同一条输出自由度，但 `gate` 还没有自己的监督目标。

当前要求：

- 不要再把“补 selector / 补 gate-level loss”当成默认下一步；
- 这一步已经被：
  - `v78 / v79 / v80 / v81`
  走完；
- 当前默认应继续往：
  - `present_overlap_residual_leak_purification`
  推进。

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

### 11. gate 专属监督成立，但只补 keep 覆盖面还不够

事实：

- `v78`
  - `abstention_gate_proxy_v1 + gate-level loss`
  - 首次恢复到 present-safe
  - 但 absent 收益不足
- `v79`
  - 加大 gate push 后
  - `near_real_0006 / 0009` 确实更静
  - 但 `near_real_0007` 开始回退
- `v80`
  - 接入 `hard_present_gate_keep_guardrail_v1 + keep_union_v2`
  - `near_real_0006 / 0009` 更静
  - 但 `same_gender / hard_present keep guardrail` 仍分别是 `11 / 16` 条 violation
  - `near_real_0007` 反而比 `v79` 更坏
- `v81`
  - 改成 `audibility-conditioned gate target v1`
  - `same_gender keep violation`
    - `11 -> 4`
  - `hard_present keep violation`
    - `16 -> 12`
  - near-real 重新回到 `0` present violation

结论：

- 问题已经从“缺 gate supervision”推进到：
  - 当前 gate supervision 的目标语义确实是关键杠杆
- 继续扩大 keep union 本身不够
- 但 `audibility-conditioned gate target` 已经证明是有效方向

### 12. train sample-id selector 不能直接充当 val keep 监控

事实：

- `v80` 训练里：
  - `reconstruction_extra_focus_sample_ids`
  - `branch_protect_focus_sample_ids`
  都指向 `sample_ids_gate_keep_union_v2_train.txt`
- 结果 `train_summary.json` 里：
  - `train_selector_metrics.branch_protect.selected_count = 63`
  - `val_selector_metrics.branch_protect.selected_count = 0`

影响：

- 当 keep selector 依赖 train sample id union，而 val manifest 不复用这些 id 时：
  - val loss 并不能代表 keep 约束是否真正泛化；
  - 训练日志会低估 keep regression 风险。

要求：

- 这类训练必须继续依赖外部 guardrail / near-real 裁决：
  - `same_gender_present_keep_guardrail_v1`
  - `hard_present_gate_keep_guardrail_v1`
  - `real_eval_manifest_residual_speech_leak_floor_v1`
- 后续若继续做 gate supervision，优先改成：
  - 可跨 train / val 共享的 metadata / target 语义
  - 而不是只靠 train sample-id selector

### 13. near-real 已回到安全，不等于 synthetic keep 风险已经消失

事实：

- `v81`
  - near-real residual leak floor 已回到 `0` violation
  - 但 synthetic keep guardrail 仍有残余：
    - `same_gender = 4`
    - `hard_present = 12`

结论：

- `v81` 已经值得进 focused 听审关；
- 但还不该直接凭 objective / near-real 自动升格为默认线。

### 14. objective / guardrail 变健康，不等于已经形成可听优势

事实：

- `v81`
  - 相对 `v79 / v80`
    - synthetic abstention 回正
    - keep guardrail 明显回拉
    - near-real residual leak floor 回到 `0` violation
- 但 `v54 vs v81` GUI 听审解盲后仍是：
  - `4 / 4 tie`
  - 且备注明确指出：
    - 分离仍不干净
    - 干扰泄漏仍存在

结论：

- 当前问题已经从 calibration 题推进到：
  - `overlap residual leak floor`
- 后续不应再默认做：
  - `v54 / v81 / v82` 之间的 checkpoint 选美
 - 而应直接开新的机制子题，去打残余泄漏本身

### 15. overlap residual purification 也可能重新伤到 `0007`

事实：

- `v82`
  - 是第一条直接把 `overlap_interval_interference_projection_loss` 接进训练的 pilot
  - relative `v81`：
    - `overlap_abstention_proxy_v4`
      - `+2.8258 dB`
    - `same_gender_present_keep_guardrail_v1`
      - `11 / 11` improve
    - `hard_present_gate_keep_guardrail_v1`
      - `13` improve / `2` regress / `1` near tie
- 但 near-real `real_eval_manifest_residual_speech_leak_floor_v1` 上：
  - `combined_rank = v82 > v81 > v54`
  - `guardrail_filtered_rank = v81 > v54 > v82`
  - 原因是：
    - `near_real_0007` 重新出现 `1` 条 `target_capture_regression`

结论：

- overlap residual loss 是有效方向；
- 但它仍可能把：
  - `0003 / 0006 / 0009`
  的 leakage 改善
  和
  - `0007`
  的 keep 回退
  一起带出来。

要求：

- `v82` 这类 overlap purification pilot 不能只看 synthetic 三连涨；
- 必须同时过：
  - `real_eval_manifest_residual_speech_leak_floor_v1`
  - 且优先补 focused 听审：
    - `v81 vs v82`

### 16. `v81 -> v82` 级别的 objective 改善仍可能完全低于人耳阈值

事实：

- `v82`
  - 相对 `v81`
    - `overlap_abstention_proxy_v4 = +2.8258 dB`
    - `same_gender_present_keep_guardrail_v1 = 11 / 11 improve`
    - `hard_present_gate_keep_guardrail_v1 = 13 improve / 2 regress / 1 near tie`
- 但 `v81 vs v82` focused 听审解盲后仍是：
  - `4 / 4 tie`
  - `0003 / 0006 / 0007 / 0009` 都无可感知差异

结论：

- 当前这条 `overlap residual purify v1` 机制，虽然方向正确；
- 但改进幅度仍小于人耳可感知阈值。

要求：

- 不要再把：
  - `objective 连涨`
  - `near-real combined rank 更高`
  视为继续做同结构 sweep 的充分理由；
- `v82` 之后默认应升级机制复杂度，而不是继续做 `v83 / v84` 同构微调。

### 17. overlap refiner 会极强地放大 synthetic 收益，但也最容易把 near-real 一起推坏

事实：

- `v83`
  - overlap-abstention proxy
    - `+8.5779 dB`
  - same-gender keep guardrail
    - `+6.4518 dB`
  - hard-present keep guardrail
    - `+5.6606 dB`
- 但 near-real：
  - `present_guardrail_violation_count = 2`
  - `target_capture_regression_sample_ids = [near_real_0007]`
  - `residual_increase_sample_ids = [near_real_0003, near_real_0007]`

结论：

- overlap refiner 机制不是伪方向；
- 但它比前面的 gate / mask reweight 更容易把 synthetic objective 推到“过强但不安全”的区域。

要求：

- 这类 refiner pilot 不能先导听审再判断；
- 必须先过 near-real guardrail，再决定是否值得听。

### 18. refiner 训练若拿 shared base 当 baseline，会把“新增改动”对齐错对象

事实：

- `v83` 之前，训练里 primary prediction 默认是：
  - `estimated_waveform_base`
- 这对应 shared base decoder；
- 但 overlap refiner 实际修改的是：
  - branch decoder 的输出

影响：

- `interference_extra_base_align_weight`
- `interference_extra_base_delta_projection_weight`

如果之后要用，实际上会去约束：

- refiner 相对 shared base 的偏移

而不是：

- refiner 相对 branch pre-refine 输出的新增改动

要求：

- overlap refiner 线必须显式导出：
  - `estimated_waveform_branch_base`
- 并通过：
  - `--loss-use-branch-prerefine-as-primary-prediction`
  把 branch pre-refine 输出设为 baseline。

### 19. prerefine baseline / delta guard 是必要条件，但还不是充分条件

事实：

- `v84`
  - 相对 `v83`
    - `present_guardrail_violation_count = 2 -> 1`
    - `residual_increase_sample_ids`
      - `[near_real_0003, near_real_0007] -> [near_real_0007]`
- 但相对 `v81`：
  - `near_real_0007`
    - `target_capture_db = -17.715 -> -19.667`
    - `interference_capture_db = -47.206 -> -39.179`
    - `residual_output_share = 0.665 -> 0.779`

结论：

- prerefine baseline + delta guard 的确把 refiner 从失控状态拉回来了；
- 但当前 refiner 触发范围仍然太宽，`0007` 这类 hard-present case 还会被一起卷进去。

要求：

- 下一步不要做 `v84` 附近轻量 sweep；
- 默认应直接收窄到：
  - weak-target
  - high-overlap
  - speech interference
  的 refiner 激活子域。

### 20. overlap refiner 更适合绑到 `1 - gate`，不适合继续乘 `gate`

事实：

- `v84`
  - 使用 `refiner * gate`
  - near-real：
    - `present_guardrail_violation_count = 1`
    - `target_capture_regression_sample_ids = [near_real_0007]`
    - `residual_increase_sample_ids = [near_real_0007]`
- `v85`
  - 使用 `refiner * (1 - gate)`
  - synthetic 相对 `v81` 仍全面为正：
    - abstention `+4.7489 dB`
    - same-gender keep `+2.1718 dB`
    - hard-present keep `+2.3698 dB`
  - near-real：
    - `present_guardrail_violation_count = 0`
    - `target_capture_regression_sample_ids = []`
    - `residual_increase_sample_ids = []`
    - `guardrail_filtered_rank = 1st`

结论：

- 当前 gate 更像“哪里该保留目标”的语义；
- overlap refiner 更像“哪里允许进一步清理 residual”的语义；
- 所以直接乘 `gate` 会更容易把 refiner 拉进 hard-present 区域；
- 乘 `1 - gate` 更符合当前子题。

要求：

- 后续若继续做 refiner 线，默认基线应是：
  - `branch_overlap_refine_gate_mode = complement`
- 不再回到：
  - `branch_overlap_refine_gate_mode = gate`
  作为默认起点。

### 21. absent-case 的自动 suppression 优势，可能不会转化成人耳更优

事实：

- `v85`
  - 自动上相对 `v81`
    - `near_real_0009`
      - `delta_interference_capture_db_b_minus_a = -11.124 dB`
      - tradeoff 标成：
        - `more_interference_leaky = v81`
- 但 `v81 vs v85` GUI 听审里：
  - `near_real_0009`
    - 人耳明确选了 `v81`
    - 决策标签：
      - `less_interference_leak`

结论：

- 当前 absent-case 的 objective / tradeoff 指标，还不能单独代表真实听感；
- 数值上“更静”并不自动等于主观更好。

要求：

- 这类 absent / silence-over-leak 前沿，不要只靠自动指标切研究基座；
- 只要进入 frontier 区间，仍必须回到人耳终裁。

### 22. `v85 / v86` 级别的 overlap refiner 优化，已经足以改善自动与 guardrail，但仍可能完全不解决核心听感痛点

事实：

- `v85`
  - near-real guardrail 已过
  - 但 `v81 vs v85` 听审解盲后：
    - `3 / 4 tie`
    - `1 / 4 = v81`
- `v86`
  - relative `v81`
    - abstention `+3.5979 dB`
    - same-gender keep `+1.6103 dB`
    - hard-present keep `+1.7029 dB`
  - near-real 仍是 `0` violation
  - 但 `v81 vs v86` 听审解盲后：
    - `3 / 4 tie`
    - `1 / 4 = v81`
    - `v86 = 0`

结论：

- 当前 overlap refiner 家族已经不是“没学到东西”；
- 真正的问题是：
  - 自动收益没有推进到可听层；
  - `present overlap residual leak` 这个主观痛点仍然原地存在。

要求：

- 不要再把：
  - `v85 / v86` 这类 objective-safe refiner 变体
  当成默认继续微调的理由；
- 若继续推进，应优先换机制题，不再做当前 refiner 家族的小步 sweep。

### 23. overlap canceller 的自动收益，也可能仍然无法转化为人耳正收益

事实：

- `v87`
  - 虽然 relative `v81` 在 synthetic / near-real 都是正收益；
  - 但直接对比后基本只是 `v86` 的 objective 近等价体
- `v88`
  - 是当前 overlap canceller 家族最强自动候选
  - `tradeoff_analysis` 里：
    - `3 / 4` 样本显示 `v81` 更漏
  - near-real rank 里也排到这条小 family 第一
  - 但 `v81 vs v88` focused 听审解盲后：
    - `tie = 2`
    - `v81 = 2`
    - `v88 = 0`

结论：

- overlap canceller 机制不是伪方向；
- 但当前这条 `v87 / v88` 线和之前的 `v85 / v86` 一样，仍停留在：
  - 自动变强
  - 人耳不转正

要求：

- 不要把 `tradeoff / near-real rank` 的继续改善，直接当成这条 family 可以继续微调扩树的理由；
- 当前主观裁决仍优先于自动排名；
- 只要听审结果没有出现 `v88 > v81`，就不能升格研究基座。

### 24. 在现有 overlap canceller head 上继续叠 dual-source consistency，可能只会得到 `v81` 和 `v88` 之间的中间解

事实：

- `v89`
  - 在现有 overlap canceller head 上新增：
    - `overlap_dual_mix_consistency_l1`
    - `overlap_dual_residual_target_projection_ratio`
  - relative `v81`
    - `overlap_dualsource_proxy_v1 = +3.6070 dB`
    - `same_gender_present_keep_guardrail_v1 = +1.6128 dB`
    - `hard_present_gate_keep_guardrail_v1 = +1.7024 dB`
  - 但 relative `v88`
    - overlap-abstention `-1.0070 dB`
    - same-gender keep `-0.5562 dB`
    - hard-present keep `-0.5994 dB`
  - near-real rank 也只是：
    - `v88 > v89 > v81 > v54`

结论：

- 这说明当前 `dual-source consistency v1` 更像：
  - 对既有 overlap canceller 的 regularization
- 而不是：
  - 真正引入了一个更强的双源分解机制

要求：

- 不要再把“在同一个 overlap canceller head 上继续叠一致性损失”当成默认下一步；
- 只要它仍然过不了 `v88`，就不值得再导新的 focused 听审包；
- 若继续推进，应换到新的机制类，而不是在 `v89` 周围继续做轻量 sweep。

### 25. 显式 dual-source 分解如果直接接管最终 target 输出，会非常危险

事实：

- `v90`
  - 新增 `overlap dual decoder v1`
  - 直接走：
    - `interference_est -> dual_target = mixture - interference_est -> final output`
  - relative `v81`
    - overlap-abstention `-6.8556 dB`
    - same-gender keep `-4.7200 dB`
    - hard-present keep `-11.6327 dB`
  - near-real 也掉到：
    - `v88 > v81 > v54 > v90`
- `v91`
  - 只加了 `max_blend = 0.25`
  - 虽然比 `v90` 稳定，但 relative `v81` 仍是：
    - overlap-abstention `-5.1942 dB`
    - same-gender keep `-5.2723 dB`
    - hard-present keep `-5.0749 dB`
  - near-real 仍是：
    - `v88 > v81 > v54 > v91`

结论：

- dual-source decomposition 这个想法本身不一定错；
- 真正错的是：
  - 让 dual path 直接接管最终 target output

要求：

- 不要再做：
  - `v90 / v91` 这类 direct dual-target output sweep
- 如果保留显式干扰分解思路，默认应该改成：
  - `auxiliary interference decoder`
  - 只做训练辅助 / regularizer
  - 不直接替代最终输出路径

## 近期关键案例入口

- `reports/daily/2026-03-26_overlap_abstention_proxy_v3_v4_and_v71_v72_followup.md`
- `reports/daily/2026-03-26_present_keep_guardrail_v1_v2_and_v73_v74_followup.md`
- `reports/daily/2026-03-26_audibility_conditioned_v1_and_abstention_gate_v1_v75_v76_v77.md`
- `reports/daily/2026-03-26_abstention_gate_proxy_v1_and_v78_v79_followup.md`
- `reports/daily/2026-03-26_hard_present_gate_keep_guardrail_v1_and_v80_followup.md`
- `reports/daily/2026-03-26_audibility_gate_target_v1_and_v81_followup.md`
- `reports/daily/2026-03-26_v54_vs_v81_listening_review.md`
