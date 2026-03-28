# 踩坑记录

## 文档定位

- 本文档只保留当前仍会影响日常推进的活跃坑点。
- 历史长版已归档到：
  - `docs/archive/pitfalls/pitfalls_active_snapshot_2026-03-26.md`
- 更早分卷索引见：
  - `docs/archive/pitfalls/README.md`

## 活跃坑点

### 0. 评估主流程必须与训练链共用同一套 loss / selector / summary 口径；脚本升级后旧摘要要视为待重评估资产

事实：

- `2026-03-28` 已把训练 / 评估共用逻辑收口到：
  - `src/tse_prefix/pipeline/runtime_helpers.py`
- 当前 `scripts/eval/eval_stft_mask_baseline.py`
  已补齐：
  - `branch_protect_teacher_overlap_l1`
  - `overlap_dual_*`
  - `selector_metrics`
  - teacher checkpoint metadata fallback
- 同日已对 active overlap family 做旧实验重评估：
  - `reports/daily/2026-03-28_old_experiment_reevaluation.md`
  - `reports/eval/reeval_2026-03-28_active_overlap_family`

要求：

- 训练与评估必须共用同一套 metric registry / selector plumbing；
- 不能把脚本升级前导出的旧 `eval_summary.json / sample_meta.json`
  和升级后新导出的结果混着当成同口径资产；
- 尤其是 dual / teacher 类 checkpoint，
  默认应优先使用 `2026-03-28` 之后的重评估结果。

影响：

- 这类问题通常不会直接报错；
- 但会悄悄污染 `summary.json / eval_summary.json / sample_meta.json`；
- 进而影响 checkpoint 排序和人工裁决入口；
- 本轮虽然已修正脚本，
  但修正前资产若不重评估，仍会继续误导判断。

### 0.1 按 `interference_pool / speaker` 筛样时，必须按全层语义匹配；历史 selector hit 统计可能已过期

事实：

- `src/tse_prefix/data/synthetic_dataset.py`
  已同时产出：
  - 第一层字段：
    - `interference_pool`
    - `interference_speaker_name`
  - 全层汇总字段：
    - `interference_pools_all`
    - `interference_speaker_names_all`
- 但 `src/tse_prefix/pipeline/loss_selectors.py`
  已在 `2026-03-28` 修正为：
  - 优先读取 `interference_pools_all / interference_speaker_names_all`
  - 按全层 `any-match`
  - 仅在 `_all` 缺失时回退到单层字段

要求：

- mixed-interference 样本上，pool / speaker selector 必须按“任一层命中”或明确约定的全层语义处理；
- 历史上依赖这组 selector 的 checkpoint，
  若要重新比较命中率或 loss summary，
  应优先看修正后重新导出的结果。

影响：

- 这会导致 targeted loss 命中集与设计口径不一致；
- 尤其会伤到：
  - `speech + music`
  - 多层 speech hard-negative
  等混合 recipe 的实验解释。

### 0.2 训练 / 评估主指标必须按 sample 聚合；旧的 batch-average 结果不能当成完全同口径

事实：

- `2026-03-28` 已把：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  的主指标聚合
  从 `batch_count / step_count`
  改为按 `sample_count` 平均。

要求：

- 比较 `2026-03-28` 前后的 train / eval summary 时，
  必须记住聚合口径发生过一次切换；
- 若要做严格横向比较，
  默认应使用修正后重导出的结果。

影响：

- 这类偏差通常不大，
  但会持续污染多个 checkpoint 之间的细粒度排序；
- batch size 不整除时尤其明显。

### 0.3 活跃文档与主入口脚本体量不能继续自然膨胀

事实：

- `docs/01_project_overview_and_plan.md`
  - `1328` 行
- `docs/02_pitfalls_log.md`
  - `1636` 行
- `docs/05_task_branch_map.md`
  - `1608` 行
- `scripts/train/train_stft_mask_baseline.py`
  - `1709` 行
- `scripts/eval/eval_stft_mask_baseline.py`
  - `1401` 行
- `scripts/eval/listening_pack_gui.py`
  - `1087` 行

要求：

- 活跃摘要继续留在主文档；
- 但详细历史、专项逻辑、GUI 组件、metric helpers、selector helpers
  都应继续拆分；
- 不能等到“已经难以通读”后再一次性救火。

影响：

- 体量过大本身就会放大遗漏概率；
- 也会让局部改动更难看出是否破坏了实验口径。

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

### 26. auxiliary interference decoder 的自动收益，仍可能只在 `0007` 上转化成更重伪影

事实：

- `v93`
  - 通过 `branch_decoder_temporal_model` 转移 `v88` prior
  - synthetic 明显变强
  - 但 near-real 重新伤到：
    - `near_real_0003`
    - `near_real_0007`
- `v94`
  - 收窄到 `branch_decoder_mask_head`
  - failure 被压到：
    - `near_real_0007`
- `v95`
  - 再加 hard-present protect
  - automatic suppression 更强
  - 但 `v81 vs v95` focused 听审解盲后：
    - `tie = 3`
    - `v81 = 1`
    - `v95 = 0`
  - 唯一可感知差异正是：
    - `near_real_0007 = v81 > v95`
    - 原因是 `v95` 伪影更重

结论：

- `auxiliary interference decoder` 不是伪方向；
- 但当前 `v93 / v94 / v95` 这条家族，仍然没有把：
  - `0006 / 0009` 的 suppression 收益
  转化为可听优势；
- 一旦跨过人耳阈值，先暴露出来的是：
  - `0007` hard-present case 上更重的伪影

要求：

- 不要再把 `v95` 附近的小步 sweep 当作默认下一步；
- 新机制若继续沿显式干扰辅助方向推进，必须优先把：
  - `hard-present artifact risk`
  当成一等 guardrail，
  而不是只看 suppression objective 继续上升。

### 27. `auxiliary_only + overlap_cancel_head-only` 是结构性 output-inactive probe，不应误当真实候选

事实：

- `v96 / v97`
  - 都使用：
    - `branch_overlap_cancel_apply_mode = auxiliary_only`
    - 只训练 `branch_overlap_cancel_head`
- 结果三条 synthetic 全是：
  - `0 improve / 0 regress / all near tie`

结论：

- 在这类接线下，overlap cancel estimate 会被监督；
- 但不会真正改变最终 `estimated_waveform`；
- 所以这只适合拿来验证接线或梯度，不适合当真实候选做自动裁决。

要求：

- 后续只要是：
  - `auxiliary_only`
  - 且只训练 `overlap_cancel_head`
- 默认标记为：
  - `mechanism_probe`
  - 不是 `candidate`

### 28. `phase_preserve` 能把 overlap canceller 变安全，但当前表示下很容易退化成 near-noop

事实：

- `v98`
  - 是第一条有效的 `phase-preserving subtractive overlap canceller` pilot
  - 但相对 `v81`：
    - abstention `-0.0028 dB`
    - same-gender keep `+0.0005 dB`
    - hard-present keep `+0.0004 dB`
  - near-real tradeoff 四条也全部 `tie`

结论：

- 当前问题不只是“complex ratio 太激进”；
- 单纯把 overlap canceller 改成 phase-preserving，只会把它推向：
  - 更安全
  - 但几乎不再产生可感知行为变化

要求：

- 不要继续把：
  - `phase-preserving overlap-canceller ratio mode`
  当成默认突破口；
- 若继续推进，应优先改：
  - 表示方式
  - 或监督语义
  - 并显式处理 `hard-present artifact risk`

### 29. near-real tradeoff gate 不能把缺失的 optional bucket 当失败

事实：

- `scripts/eval/gate_near_real_tradeoff.py`
  之前会把：
  - focused subset pack 中本来就不存在的 `target_present__none`
  直接判成 `missing_bucket -> fail`

影响：

- 会把像 `residual_speech_leak_floor_v1` 这种只含：
  - `target_present__speech`
  - `target_present__music_plus_speech`
  - `target_absent__speech`
  的包误写成 `overall_pass = false`

要求：

- `target_present__none` 在 near-real focused subset gate 中只能算 optional bucket；
- 若该 bucket 不存在，应：
  - 保留 `present = false`
  - 但不能拉低 `overall_pass`

### 30. `teacher artifact veto` 能减轻失败，但仍可能完全过不了人耳阈值

事实：

- `v100`
  - 相对 `v95`
  - 确实把 `near_real_0007` 上的 artifact 风险从更重拉回了一档
- 但 `v81 vs v100` 解盲后仍然是：
  - `tie = 3`
  - `v81 = 1`
  - `v100 = 0`

结论：

- frozen teacher overlap veto 不是完全无效；
- 但它当前只能把已知失败“变轻”，还不能把它“变成胜利”；
- 如果核心目标是可听胜出，就不应继续把 `v95 / v100` 家族当默认扩展方向。

### 31. `delta blend` 只对真正改 final output 的 subtractive 家族有意义

事实：

- `v100` 这条家族使用的是：
  - `branch_overlap_cancel_apply_mode = auxiliary_only`
- 在这种接线下，overlap cancel 只作为辅助监督存在；
- 即使给 cancel 路径新增 final delta blend，也不会改变最终输出。

要求：

- `delta blend` 类机制只能挂在：
  - `branch_overlap_cancel_apply_mode = subtract`
  的 subtractive 家族上；
- 不要再把这类输出路径机制错误地尝试在 `auxiliary_only` 家族上。

### 32. `delta blend` 能把 subtractive canceller 拉回安全区，但仍可能完全过不了人耳阈值

事实：

- `v101`
  - 相对 `v88`
  - 确实把 hard-present 风险拉回来了
  - `v81 vs v101` 解盲结果是：
    - `tie = 3`
    - `v81 = 1`
    - `v101 = 0`
- 唯一分出胜负的是：
  - `near_real_0009`
  - 而且仍是 `v81` 更好

结论：

- `delta blend` 是有效的 safety-calibration 机制；
- 但它当前只能把 `v88` 这类 subtractive canceller 变得更稳，
  还不能把它变成新的可听前沿；
- 不应继续把 `v101 / v102` 这类同家族小步 sweep 当默认推进方向。

### 33. whole-utterance leak tradeoff 在 overlap frontier 上可能系统性和人耳反向

事实：

- 用 `overlap_local_benchmark` 回放：
  - `v81 vs v88`
  - `v81 vs v95`
  - `v81 vs v100`
  - `v81 vs v101`
- 在这 4 个已听 pack 的 `5` 个 decisive 样本上：
  - whole-utterance `more_interference_leaky`
  - 全部指向“新候选更好”
  - 但人耳终裁全部是 `v81`

结论：

- 对 overlap frontier，整句 `interference_capture` 风格 tradeoff 不能再当作主裁决依据；
- 它会把：
  - 更静
  - 但更糊
  - 或更有伪影
  的候选误判成更优。

要求：

- frontier 样本上必须补 localized 指标；
- 特别是 target-present overlap，不再只看 whole-utterance leak tradeoff。

### 34. localized `speech-only` 比 `total interference` 更适合做人耳对齐

事实：

- overlap-local 回放里：
  - `better_retention_minus_speech_leak`
    - 对 `3` 个 target-present decisive 样本全部对齐人耳；
  - `more_total_interference_leaky`
    - 在 `near_real_0007` 这类 `music_plus_speech` 样本上会被 music 成分污染，
    - 与人耳出现反向。

结论：

- 对当前这批 near-real overlap frontier，
  - 人耳更接近：
    - `speech leak`
    - `retention-minus-speech-leak`
    - `artifact proxy`
  - 而不是：
    - `total interference leak`

要求：

- 后续 overlap-local benchmark 默认优先报告：
  - `more_speech_interference_leaky_candidate`
  - `better_retention_minus_speech_leak_candidate`
  - `more_artifact_proxy_heavy_candidate`
- `more_total_interference_leaky_candidate` 只保留为辅助观察，不再当主裁决列。

### 35. listening pack 的人耳标签不能只依赖 `listening_review_decoded_summary.json`

事实：

- `v81 vs v100` blind 包只有：
  - `listening_sheet.csv`
  - `blind_key.json`
  - 没有现成的 `listening_review_decoded_summary.json`
- 如果分析脚本只读 decoded summary，会把：
  - `human_alignment_summary`
  整列算成空。

要求：

- pack 分析脚本必须支持回退到：
  - `listening_sheet.csv + blind_key.json`
- 否则会把已经完成的听审资产误判成“没人耳标签”。

### 36. synthetic selector 只看第一层 `interference_pool` 会把 `speech_plus_music` 错分成 `speech-only`

事实：

- 旧版 `SyntheticTSEDataset`
  - 在 `__getitem__`
  - 只暴露第一层：
    - `interference_pool`
    - `interference_speaker_name`
- 但 `target_hard_plus_music` / `target_clean_plus_music`
  - 实际 `interference_layers` 是：
    - 第一层 speech
    - 第二层 music
- 因此任何只基于第一层 pool 的 selector
  - 都会把这类样本误当成纯 speech 干扰。

结论：

- 这不是单纯的阈值问题，而是 selector 元数据表达不够；
- 如果不先补 interference profile，后续所谓 `speech-only local residual` 训练会在样本定义上自相矛盾。

要求：

- selector 不能再只依赖第一层 `interference_pool`；
- 后续必须改用：
  - `interference_profile`
  - `has_speech_interference`
  - `has_music_interference`
  - `interference_layer_count`
  这类派生字段来定义纯 speech overlap 子域。

### 37. 把 overlap-local selector 收窄到 `speech_only`，能保住 synthetic 主收益，但不会自动修好 `0007`

事实：

- `v102`
  - 在 `v82` 基础上把 overlap-local selector 收窄到真正的 `speech_only`
- relative `v81`
  - synthetic 三条主验收仍为正：
    - abstention `+2.829 dB`
    - same-gender keep `+1.252 dB`
    - hard-present keep `+1.022 dB`
- 但 near-real 上：
  - `0003`
    - 变成明确正 tradeoff
  - `0006`
    - localized speech-only 指标更好
    - whole-utterance 却没有同步转正
  - `0007`
    - whole-utterance 黄灯只略收窄
    - localized `retention-minus-speech-leak` 仍明显更差
  - `0009`
    - absent 近乎打平，没有形成明确收益

结论：

- selector 污染确实是问题的一部分；
- 但 `0007` 的 blocker 不只是 selector 污染，
  仍包含 hard-present artifact / preservation 难题本身；
- 因此 `speech_only selector` 不是终解，只是把问题重新压缩回更明确的 target-present speech 子域。

要求：

- `v102` 不应自动升格；
- 必须先做 `v81 vs v102` focused 听审；
- 若听审确认：
  - `0003 / 0006` 有真实收益，
  - 且 `0007 / 0009` 代价可接受，
  才值得继续做后续 `v103+`。

### 38. `export_ab_listening_pack.py` 不能再假设 near-real manifest 具备 synthetic 全字段

事实：

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`
  只有：
  - `sample_id`
  - `mixture_audio_path`
  - `target_audio_path`
  - `reference_audio_path`
  - `note`
- 如果 `export_ab_listening_pack.py` 继续硬取：
  - `recipe`
  - `temporal_pattern`
  - `metadata_path`
  - 或直接走 `SyntheticTSEDataset`
  就会在 near-real pack 导出时崩掉，或写出缺字段的 `sample_meta.json`，
  进一步把：
  - `analyze_listening_pack_tradeoff.py`
  - `analyze_overlap_local_benchmark.py`
  一起带崩。

要求：

- near-real pack 导出必须：
  - 从样本同目录 `sample_meta.json` 回填缺省字段；
  - 直接按 manifest 音频路径读取 `mixture / target / reference`；
  - 在导出的 `sample_meta.json` 里补写：
    - `mixture_audio_path`
    - `target_audio_path`
    - `reference_audio_path`
    - `exports`
- 对 near-real manifest 导包时，默认要显式传：
  - `--focus-recipes`
  以清空 synthetic 默认 recipe 过滤。

### 39. `v103` 证明“automatic 转绿”仍可能对应“主观全败”

事实：

- `v103 = v102 + plus_music teacher veto`
  在 automatic 上同时满足：
  - synthetic 三条主验收继续更强
  - near-real whole-utterance `overall_pass = true`
- 但 blind `v81 vs v103` 听审结果是：
  - `v81 = 4`
  - `v103 = 0`
  - `tie = 0`
- 四条样本共同决策标签都是：
  - `less_artifact`

结论：

- 当前这组 `speech leak / retention-minus-leak / teacher veto`
  目标，仍不足以约束真正会被人耳否掉的伪影；
- 如果一个新候选已经出现“全样本都因为 artifact 更差而输掉”的结果，
  默认动作不是继续做同结构权重 sweep，
  而是停掉这条家族，回到：
  - artifact proxy 物化
  - artifact-aware 训练约束
  这一级问题上。

### 40. `near_real_0007` 不能再用“recipe 近似”或“低 transient 近似”粗代理

事实：

- `near_real_0007` 的 blocker 不是单纯：
  - `plus_music recipe`
  - 或 `target_transient_presence_share_mean` 很低
- 它更接近：
  - 弱目标
  - `speech_plus_music`
  - `interference_layer_count = 2`
  - `target_full`
  - 中高 transient share 的 hard-present overlap

如果只用：

- `recipe in {target_clean_plus_music, target_hard_plus_music}`
- 或继续沿用
  - `target_transient_presence_share_mean <= 0.05`

就会把：

- `0007` 型 artifact-risk
- `0006` 型 speech-only keep-case

重新混在一起，导致 proxy 失焦。

要求：

- 后续凡是要物化 `0007` 风格 synthetic proxy，
  默认都要显式带上：
  - `interference_profile = speech_plus_music`
  - `interference_layer_count = 2`
  - `require_speech_interference = true`
  - `require_music_interference = true`
- 并且不要再把“更低 transient share”直接当作更接近 `0007` 的充分条件。

### 41. `hard_present_artifact_proxy_v1` 不能脱离 near-real `0003 / 0007` 单独升格候选

事实：

- `v105` 在 synthetic 四条固定验收上都能排前；
- `hard_present_artifact_proxy_v1` 也会把 `v105` 排到最前；
- 但 near-real 上：
  - `0003` target capture 从 `-11.474 dB` 掉到 `-13.512 dB`
  - `0007` target capture 从 `-17.715 dB` 掉到 `-19.801 dB`
  - overlap-local `0007` 仍是 `v81` 更好，且 `v105` artifact 更重

说明：

- 这条 proxy 可以用来暴露 `v103` 这种 artifact-risk；
- 但如果直接把它当主目标强推，也会把真实 target capture 一起压低；
- 它更适合作为 veto / backstop，而不是单独的升格依据。

要求：

- 后续凡是 `hard_present_artifact_proxy_v1` 排前的候选，
  默认都必须同时检查：
  - near-real `0003`
  - near-real `0007`
  - overlap-local `more_artifact_proxy_heavy`
- 如果出现：
  - proxy 更强
  - 但 `0003 / 0007` target capture 回退
  
  则默认判为 proxy 过拟合，不导听审。

### 42. A/B 导包分析出现 `num_samples = 0` 时，先排除旧 summary 或导包未完成，不要先怀疑分析脚本本身

事实：

- `v81 vs v106` 的 near-real pack 在导出成功后，目录里确实有 `4` 条样本；
- 但第一次看到的：
  - `tradeoff_analysis/summary.json`
  - `overlap_local_benchmark/summary.json`
  - `bandwidth_analysis/summary.json`
  
  都是 `num_samples = 0`；
- 原因分别是：
  - 旧失败导包留下的过期 summary
  - blind 包里把导包和分析并行跑，分析脚本先读到尚未写完的目录

说明：

- 这是流程时序问题，不是当前分析脚本回归；
- 如果不先核对 pack 根目录和 `sample_meta.json`，很容易误把有效候选当成导包失败。

要求：

- 后续凡是 A/B pack analysis 出现 `num_samples = 0`，默认先检查：
  - pack 根目录 `summary.json` 的 `num_exported_samples`
  - 样本子目录里的 `sample_meta.json`
  - `candidate_a.wav / candidate_b.wav` 或真实 label 音频是否已落盘
- 如果导包与分析要连续执行，默认顺序应为：
  - 先导包
  - 再分析
  
  不要并行。

### 43. `local artifact veto` 只做 teacher-overlap 对齐，不足以自动压住 `0007` 风格 speech leak

事实：

- `v106` 已经不再像 `v103 / v105` 那样在 `0007` 上出现更重 artifact；
- overlap-local `0007` 上：
  - `better_source_retention = v106`
  - `more_artifact_proxy_heavy = tie`
  - 但 `more_speech_interference_leaky = v106`
  - `better_retention_minus_speech_leak = v81`

说明：

- “把局部输出往 `v81` teacher 靠近”可以先止住最明显的 artifact 爆炸；
- 但它并不会自动学会把 `music_plus_speech` hard-present 局部窗里的 speech leak 压下去；
- 所以下一轮如果听审仍不转正，主问题就不再是 artifact 本身，而是：
  - 局部 speech leak 没被显式建模

要求：

- 后续 `0007` 风格 local veto 若继续推进，默认应额外加入：
  - `music_plus_speech` 局部窗的显式 speech-leak backstop
- 不要再假设：
  - teacher-overlap 对齐
  
  会自然等价于更低的 local speech leak。

### 44. 主观听审默认只对同批次 A/B 负责，不能把不同批次的严重度标签直接横向串联

事实：

- 同一条样本，在不同批次听审里，主观上对 leak / artifact 严重度的命名可能会漂移；
- 例如这次主观记为“中等泄漏”，下次也可能主观记为“明显泄漏”；
- 但同一批次内的 A/B 比较，主观标准是统一的。

说明：

- 因此听审最可靠的信息是：
  - 同批次里谁更好
  - 是否有可感知差异
- 不能把：
  - `v81 vs v103` 这批里记作 `moderate artifact`
  - 和 `v81 vs v106` 这批里的 `slight / moderate leak`
  
  直接当成绝对可比的跨批次量尺。

要求：

- 后续记录主观结论时，默认优先写：
  - `v81 / candidate / tie` 的同批次裁决
  - 以及“核心痛点是否在本批次内改善”
- 不要把不同批次的主观强弱标签直接用于跨包排序。

### 45. `music_plus_speech` 局部窗如果不把导出训练视图改成 `target + speech_only`，就不会形成显式 speech-leak 监督

事实：

- `v106` 已经证明：
  - 只在 `music_plus_speech` hard-present 局部窗上做 teacher-overlap 对齐，
  - 并不会自动把 `near_real_0007` 风格局部 speech leak 压下去；
- `v107` 的有效变化不是“再选一遍局部窗”，而是：
  - 仍从完整 `speech_plus_music` 原样本选局部高 risk 窗；
  - 但导出的训练混合只保留：
    - `target + speech layer`
  - 让现有 `speech_only overlap_interference_extra` 直接变成显式 speech-leak backstop。

结论：

- 关键不是有没有 local proxy；
- 而是：
  - local proxy 的“窗口选择语义”
  - 和“导出训练视图语义”
  不能再绑在同一个 full-mix 表达上。

要求：

- 后续凡是继续做 `music_plus_speech` 局部 speech-leak proxy，
  默认都要区分两层语义：
  - 选择窗时看完整 `speech_plus_music`
  - 训练视图只导出显式要压的那部分干扰
- 否则 loss 看到的仍是 speech 与 music 混合残差，
  监督目标不会真正对准 speech leak。

### 46. local proxy builder 不能假设 `torchaudio` 后端能直接读完所有源干扰素材

事实：

- 这轮在物化 `local_speech_leak_proxy_v1` 时，源 `interference_layers[].audio_path` 中包含 `.m4a`；
- 当前环境里 `torchaudio` 实际落到 `soundfile` 后端时，不能稳定读取这类输入；
- 如果脚本只走 `torchaudio.load`，会在 proxy 物化阶段中断。

要求：

- 后续凡是需要直接回读原始 interference layer 音频的脚本，
  默认都要准备兼容解码回退；
- 当前可行做法是：
  - 先尝试 `torchaudio.load`
  - 失败后回退到 `ffmpeg` 解码并重采样
- 不要把“manifest 已存在 wav 路径”错误地类推到所有源 layer 资源也都是 wav。

### 47. 显式 local speech-leak supervision 成立，不等于主观就不会重新输在 artifact

事实：

- `v107`
  - automatic 上同时满足：
    - synthetic 三条固定验收 relative `v81` 全部更强
    - near-real whole-utterance `overall_pass = true`
    - overlap-local `0003 / 0006` 的 `retention-minus-speech-leak` 转正
- 但 blind `v81 vs v107` 听审结果是：
  - `v81 = 4`
  - `v107 = 0`
  - `tie = 0`
- 四条样本共同决策标签都是：
  - `less_artifact`

结论：

- 这说明当前问题已经不是：
  - “speech leak 没被显式监督”
- 而是：
  - “显式压 speech leak 后，`music_plus_speech` hard-present 局部窗里的 preservation / artifact 代价仍没有被约束住”

要求：

- 后续凡是沿 `local speech-leak proxy` 继续推进，
  默认都不能只盯：
  - speech leak
  - retention-minus-speech-leak
- 必须同时补：
  - 局部 preservation backstop
  - 局部 artifact backstop
- 如果一个新候选已经出现：
  - blind 听审 `4 / 4` 全部因 artifact 输掉
  
  默认动作应是收口当前 family，
  不再继续同构 sweep。

### 48. 当前这批“电话音”失败，纯 bandwidth narrowing 抓不住，必须补 transient-loss

事实：

- 用 `real_eval_manifest_bandwidth_guardrail_v1` 回放：
  - `v81 vs v103`
  - `v81 vs v107`
- `bandwidth_analysis/summary.json` 都没有抓到 decisive narrowing：
  - `v81 vs v103`
    - `narrower_candidate_counts = tie: 4`
  - `v81 vs v107`
    - 结论同型，纯 bandwidth 仍不分胜负
- 但 `transient_analysis/summary.json` 两组都能抓到：
  - `more_transient_lossy_candidate_counts = tie: 1, file_b: 3`
  - 被抓到的都是：
    - `near_real_0002`
    - `near_real_0006`
    - `near_real_0009`

结论：

- 当前这批主观上像“电话音”的失败，
  更接近：
  - 高频瞬态存在感丢失
  而不是：
  - 单纯频宽收窄

要求：

- 后续不要再把纯 `bandwidth_analysis` 当作当前 artifact frontier 的充分代理；
- 任何要解释这批电话音失败的自动诊断，
  默认都必须至少补：
  - `transient-loss`

### 49. `phone_artifact_gate_v1` 应作为导听审前的固定前置 gate，而不是事后分析脚本

事实：

- 已新增：
  - `scripts/eval/gate_near_real_phone_artifact.py`
- 它组合：
  - `bandwidth_analysis`
  - `transient_analysis`
- 在两组已知主观失败 pack 上都能稳定判 fail：
  - `v81 vs v103`
    - `overall_pass = false`
  - `v81 vs v107`
    - `overall_pass = false`
- 两组共同失败 bucket 都是：
  - `raw_target_only`
  - `target_present__speech`
  - `target_absent__speech`

结论：

- 这说明当前 artifact-first 诊断链已经不是概念性想法，
  而是已有可执行 gate。

要求：

- 后续任何沿：
  - `local speech-leak proxy`
  - `music_plus_speech hard-present`
  继续推进的新候选，
  在导听审前默认都先过：
  - `real_eval_manifest_bandwidth_guardrail_v1`
  - `gate_near_real_phone_artifact.py`
- 如果该 gate 已 fail，
  默认动作不是继续导听审，
  而是先回到 artifact / preservation 约束本身。

### 50. 把 preservation / teacher backstop 宽打到整个 `local_speech_leak_proxy_v1` 子域，会把 `v107` 的主收益一起抹掉

事实：

- `v108`
  - 在 `v107` 基础上新增：
    - `branch_protect_guard_sisdr`
    - `branch_protect_teacher_overlap(v81)`
  - 两条 selector 都打到：
    - `sample_ids_local_speech_leak_proxy_v1_all.txt`
- 结果不是“牺牲一点 abstention，换来更稳的 artifact / keep”，而是：
  - relative `v107`
    - abstention `-3.6913 dB`
    - same-gender keep `-1.1242 dB`
    - hard-present keep `-1.1257 dB`
    - hard-present artifact proxy `-1.5016 dB`
- near-real / phone-artifact 上：
  - relative `v107`
    - `phone_artifact_gate_v1 = pass`
  - 说明 artifact 的确止住了
  - 但 relative `v81`
    - `phone_artifact_gate_v1` 仍 fail
    - `0007` 也没转成正向 candidate

结论：

- 当前问题不是“preservation backstop` 无效”；
- 而是：
  - 把它宽打到整个 `local_speech_leak_proxy_v1` 子域过于粗暴，
  - 会把 `v107` 在 `0003 / 0006` 上的有效行为一起拉回。

要求：

- 后续若继续推进 `v107` 这条显式 speech-leak family，
  默认不要再做：
  - `local_speech_leak_proxy_v1` 全量子集上的宽 `branch_protect + teacher` backstop
- 默认应改成：
  - 只在更窄的 `0007` 风格 `music_plus_speech hard-present` 局部窗上打 preservation / artifact backstop
  - 先过 `phone_artifact_gate_v1`
  - 再决定是否值得导听审。

### 51. 把 backstop 缩到 `0007-like` 子域，可以避开 `v108` 式过度回缩；但这不等于 `0007` 已被自动解掉

事实：

- `v109`
  - 不再沿用 `v108` 的全量子域 backstop
  - 改成只打：
    - `sample_ids_local_speech_leak_0007_like_proxy_v1_all.txt`
- relative `v81`：
  - 四条 synthetic 固定验收重新全绿
  - `near-real tradeoff gate = pass`
  - `phone_artifact_gate_v1 = pass`
- relative `v107`：
  - `0003 / 0007` 的 overlap-local
    - `better_retention_minus_speech_leak = v109`
  - 且 `phone_artifact_gate_v1` 继续 pass

但同时：

- relative `v81` 的 `near_real_0007`
  - overlap-local 上
    - `better_retention_minus_speech_leak = v109`
  - 但 whole-utterance 上
    - `better_retention_minus_leak = tie`
  - 且 overlap-local 上
    - `more_artifact_proxy_heavy = v109`

结论：

- `0007-like` 窄 backstop 是当前有效方向；
- 但它解决的是：
  - `v108` 式全局回缩
  - 与 `v107` 式明显电话音失败
- 还没有自动解决：
  - `0007` 的最终 retention / artifact 拉扯。

要求：

- 这类候选一旦已经同时通过：
  - `near-real tradeoff gate`
  - `phone_artifact_gate_v1`
- 默认动作应改为：
  - 直接导 focused blind 听审
- 而不是继续做同构小步 sweep，
  因为剩余不确定性已经是主观裁决层问题。

### 52. 即使通过 `near-real tradeoff gate + phone_artifact_gate_v1`，也只说明“值得导听审”，不说明核心痛点已主观解决

事实：

- `v109`
  - relative `v81`
    - 四条 synthetic 固定验收全绿
    - `near-real tradeoff gate = pass`
    - `phone_artifact_gate_v1 = pass`
- 但 blind `v81 vs v109` 解盲后仍是：
  - `tie = 3`
  - `v81 = 1`
  - `v109 = 0`
- 唯一非 tie 样本仍是：
  - `near_real_0007`
  - 决策标签：
    - `less_artifact`

结论：

- 当前两条客观 gate 的作用边界很明确：
  - 它们能筛掉“明显不值得听”的候选；
  - 但不能证明候选已经解决核心痛点。
- `v109` 的意义是：
  - 从 `v107` 那种明显 artifact 失败，
  - 收敛到和 `v81` 很接近；
  - 不是：
    - 已经主观超越 `v81`

要求：

- 后续不要把：
  - `objective 全绿`
  - `tradeoff gate pass`
  - `phone_artifact_gate_v1 pass`
  误读成“已经可以升格”；
- 对这类候选，blind 听审仍是最终裁决。
- 如果听审结果是：
  - 大量 `tie`
  - 且唯一 decisive 样本仍偏向 baseline
  
  默认动作应是收口当前 family，
  而不是继续做同构小步 sweep。

### 53. 即使把 `speech_only leak view` 和 `plus_music artifact view` 精确配对到同一批 `0007-like` base id，也仍可能继续把 `0007` 推向过抑制

事实：

- `v110`
  - 从 `v109` 出发
  - 对同一批 `0007-like` base id 同时引入：
    - `local_speech_leak_0007_like_proxy_v1`
    - `hard_present_artifact_0007_like_proxy_v1`
  - leak view 上继续打：
    - `overlap_interference_extra`
  - artifact view 上继续打：
    - `branch_protect_guard_sisdr`
    - `branch_protect_teacher_overlap(v81)`
- relative `v81 / v109`
  - 四条 synthetic 固定验收都仍是正向
  - `near-real tradeoff gate = pass`
  - `phone_artifact_gate_v1 = pass`
- 但 `near_real_0007`
  - relative `v81`
    - overlap-local：
      - `better_retention_minus_speech_leak = v110`
      - `better_retention_minus_total_leak = v81`
      - `more_artifact_proxy_heavy = v110`
    - whole-utterance：
      - `better_retention_minus_leak = v81`
  - relative `v109`
    - overlap-local：
      - `better_retention_minus_speech_leak = v110`
      - `better_retention_minus_total_leak = v109`
    - whole-utterance：
      - `better_retention_minus_leak = v109`

结论：

- 问题不只是“artifact view 没有一起在场”；
- 即使 paired dual-view 已经在场，
  当前这组 loss 仍会把 `0007` 往
  “speech-only leak 更小，但 total / whole tradeoff 更差”
  的方向继续推。
- `phone_artifact_gate_v1` 在这里也只能说明：
  - 没有回到明显电话音失败；
  - 不能说明 `0007` 的核心 retention / total-leak 拉扯已经解掉。

要求：

- 这类 paired dual-view 候选一旦出现：
  - synthetic 继续正向
  - `tradeoff gate + phone_artifact_gate_v1` 继续 pass
  - 但 `0007` whole-tradeoff 反而退化

  默认动作应是直接收口当前参数化，
  不再继续做 `v110+` 同构 sweep。
- 若继续 `0007` 子题，
  默认应改成：
  - 更保守的 self-anchor / frontier-anchor 约束，
  - 先保住当前最接近可听边界的 whole-tradeoff，
  - 再观察局部 leak 改善是否还能留下。

### 54. 把 paired dual-view 收成 self-anchor 虽能止住过抑制，但当前 family 会迅速退成 near-no-op

事实：

- `v111`
  - 仍使用 `paired 0007-like dual-view bundle`
  - 但改成：
    - `teacher = v109`
    - `overlap_interference_extra_weight` 减半
    - `branch_protect_teacher_overlap_weight` 加强
- relative `v81`
  - `0007`
    - 仍是：
      - overlap-local `better_retention_minus_speech_leak = v111`
      - 但 whole `better_retention_minus_leak = v81`
- relative `v109`
  - near-real whole / local 基本全 `tie`
  - `0007`
    - `better_retention_minus_speech_leak = tie`
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = tie`
- `export_ab_listening_pack.py` relative `v81 / v109` 也都给出：
  - `num_candidate_samples = 0`

结论：

- 当前这组 paired dual-view family 的边界已经比较清楚：
  - 放松一点，会走向 `v110` 式 over-suppressive；
  - 收紧一点，会走向 `v111` 式 safe / near-no-op。
- 这说明继续做同构权重 sweep，
  大概率只是在：
  - “过抑制”
  - 和
  - “基本不动”
  之间来回摆动。

要求：

- `v111` 这类 self-anchor 控制实验一旦确认 near-real relative frontier 基本全 tie，
  默认动作应是收口当前 family，
  不再继续 `v111+`。
- 如果继续 `0007` 子题，
  下一步默认应改做：
  - 新的约束语义
  - 或新的表示机制
  而不是继续沿这组 loss 组合细调。

### 55. `frozen branch_base + overlap_cancel_head` 的 split-path 首版可以保持 safe，但当前表示会迅速收成 near-no-op，且未保住 `v109` 的 `0007` local speech-leak 优势

事实：

- `v112`
  - 初始化：
    - `v109`
  - 新开：
    - `branch_overlap_cancel_head`
  - 但只训练：
    - `branch_overlap_cancel_head`
  - 同时打开：
    - `loss_use_branch_prerefine_as_primary_prediction = true`
  - 含义是：
    - `branch_base(v109)` 继续作为主输出
    - `overlap_cancel_head` 只在 `speech_only overlap` 子域承担独立 suppress 路径
- selector 激活是成立的：
  - train
    - `overlap_cancel = 38 / 135`
    - `branch_protect = 3 / 135`
  - val
    - `overlap_cancel = 12 / 40`
    - `branch_protect = 3 / 40`
- relative `v81`
  - 四条 synthetic 固定验收仍全绿
  - `tradeoff gate = pass`
  - bandwidth / transient 也没有新坏桶
- 但 relative `v109`
  - synthetic 基本全 tie
  - near-real whole 也基本全 tie
  - `export_ab_listening_pack`
    - relative `v81 / v109`
      - 都是 `0 candidate sample`
- 更关键的是 `near_real_0007` relative `v109`
  - overlap-local：
    - `more_speech_interference_leaky = v112`
    - `better_retention_minus_speech_leak = v109`
    - `more_artifact_proxy_heavy = tie`

结论：

- 当前问题并不只是“主路径和 suppress 路径还没有拆开”；
- 把它们形式上拆开以后，
  如果 suppress 仍停留在当前：
  - multiplicative
  - overlap-cancel
  - complement-gated
  表示里，
  这条 family 仍会快速收成：
  - safe
  - 但几乎不前进。

要求：

- 不继续：
  - `v112+`
  - 当前这组 `frozen branch_base + overlap_cancel_head` split-path 小步 sweep
- 后续若继续 `0007` 子题，
  默认应改：
  - 更明确的 preserve / bypass 表示
  - 或新的 integration point
- 不要再把“split-path 首版能训起来”误判成“这条 overlap-cancel family 已经具备解题能力”。

### 56. paired `0007-like` manifest 不会自动替训练入口激活 selector；如果 CLI 漏传 `--loss-*-focus-*` 参数，run 会表面成功但实际没打中目标子域

事实：

- `v113` 首个 `ft1` 试跑：
  - manifest 已经换成
    - `train_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
    - `val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1.jsonl`
  - 但 CLI 漏传了：
    - `--loss-reconstruction-extra-focus-sample-ids-file`
    - `--loss-overlap-interference-extra-focus-sample-ids-file`
    - `--loss-branch-protect-focus-sample-ids-file`
    - `--loss-branch-protect-teacher-focus-sample-ids-file`
- 结果是：
  - head 本身确实在训练
  - 但 train / val `selector_metrics` 全是：
    - `active = false`
    - `selected_count = 0`
  - 也就是 paired `0007-like` 子域根本没有被实际命中
- 只有在 `ft2` 把 selector 参数显式补齐以后，
  才恢复成预期命中：
  - train
    - `reconstruction_extra = 63 / 108`
    - `overlap_interference_extra = 3 / 108`
    - `branch_protect = 3 / 108`
  - val
    - `overlap_interference_extra = 2 / 39`
    - `branch_protect = 3 / 39`

原因：

- 训练脚本里的 selector 是由 `loss_config` 里的显式 `focus_* / require_* / min_* / max_*` 参数驱动的；
- manifest 只是提供样本池与元数据；
- 它不会“自动把 paired bundle 的 sample id 语义转成训练时的 selector 条件”。

要求：

- 后续凡是复用这类：
  - paired bundle
  - local proxy
  - hard-present backstop
  训练入口，
  都必须同时检查：
  - `train_summary.json` 里的 `loss_config` 是否真的带上目标 selector；
  - `selector_metrics` 是否出现预期命中数；
- 不能只看：
  - manifest 已切换
  - 训练已跑完
  就把该 run 计入有效实验。

### 57. 在 preserve/bypass self-anchor family 里，直接上调 `overlap_interference_extra_weight` 可能让 synthetic / whole-tradeoff 继续变好，但同时把真正想要的 overlap-local `speech_only` leak 拉坏

事实：

- `v114` 相对 `v113`：
  - 唯一主动改动只是：
    - `loss_overlap_interference_extra_weight`
      - `0.04 -> 0.05`
  - selector 命中完全一致；
  - synthetic 四条固定验收全部继续正向；
  - whole-utterance near-real 也继续正向：
    - `more_interference_leaky = v113` on `2 / 4`
    - `better_retention_minus_leak = v114` on `1 / 4`
  - 但 overlap-local：
    - `more_speech_interference_leaky = tie:1, v113:1, v114:2`
    - `better_retention_minus_speech_leak = tie:2, v113:1, not_applicable:1`
- 最关键的是 `near_real_0007`：
  - whole-utterance：
    - `better_retention_minus_leak = v114`
    - `delta_interference_capture_db = -1.8998 dB`
  - overlap-local：
    - `more_speech_interference_leaky = v114`
    - `better_retention_minus_speech_leak = v113`
    - `delta_speech_interference_capture_db = +6.7240 dB`
    - `delta_retention_minus_speech_leak_db = -6.7384 dB`

原因：

- 当前这条 preserve/bypass refiner family 里，
  同一个 whole-pack `speech_only local push` 权重，
  优先优化到的可能是：
  - whole-tradeoff
  - total-leak
  而不是：
  - overlap-local `speech_only` leak

要求：

- 后续凡是继续这条 family 的 follow-up，
  不能再把：
  - synthetic 更好
  - whole-tradeoff 更好
  当作“local `speech_only` leak 也会一起更好”的近似代理；
- 必须先看：
  - `overlap_local_benchmark`
  - 尤其 `near_real_0007`
    - `more_speech_interference_leaky`
    - `better_retention_minus_speech_leak`
  两项是否真的转正；
- 如果这两项没转正，
  就不应继续做同语义的 `overlap_interference_extra_weight` 小步加码。

### 58. 在 preserve/bypass self-anchor family 里，把 selector 切得更像 `0007`，也不等于优化就会从 whole / total-leak 自动转到 overlap-local `speech_only` leak

事实：

- `v115` 相对 `v113`：
  - 只改了 `speech_only local leak` selector 子域；
  - synthetic 四条固定验收仍全正；
  - whole-utterance near-real 也仍正向：
    - `more_interference_leaky = v113` on `2 / 4`
    - `better_retention_minus_leak = v115` on `1 / 4`
  - 但 overlap-local：
    - `more_speech_interference_leaky = tie:1, v113:1, v115:2`
    - `better_retention_minus_speech_leak = tie:2, v113:1, not_applicable:1`
- 最关键的是 `near_real_0007`：
  - `more_speech_interference_leaky = v115`
  - `delta_speech_interference_capture_db = +9.2226 dB`
  - `delta_retention_minus_speech_leak_db = -9.2569 dB`
  - 同时：
    - `better_retention_minus_total_leak = tie`
    - `more_artifact_proxy_heavy = tie`

原因：

- 当前 family 里，
  即使 selector 已经更接近真实 blocker，
  单一 refiner 头的主优化出口也仍可能先落在：
  - whole-tradeoff
  - total-leak
  而不是：
  - overlap-local `speech_only` leak

要求：

- 后续凡是继续这条 family 的 selector follow-up，
  不能把“selector 更像 `0007`”本身当作足够前提；
- 仍然必须优先检查：
  - `overlap_local_benchmark`
  - 尤其 `near_real_0007`
    - `more_speech_interference_leaky`
    - `better_retention_minus_speech_leak`
- 如果这两项没转正，
  就不应继续做 selector-only 小步 sweep。

### 59. 在 preserve/bypass self-anchor family 里，把 overlap local loss 改成更直接的 `prediction_projection_ratio`，也仍可能复现同方向 local speech-leak 失败

事实：

- `v116` 相对 `v113`：
  - 唯一主动改动是：
    - `loss_overlap_interference_extra_mode`
      - `residual_projection_ratio -> prediction_projection_ratio`
  - synthetic 四条固定验收继续全正；
  - whole-utterance near-real 继续正向：
    - `more_interference_leaky = v113` on `2 / 4`
    - `better_retention_minus_leak = v116` on `1 / 4`
  - 但 overlap-local：
    - `more_speech_interference_leaky = tie:1, v113:1, v116:2`
    - `better_retention_minus_speech_leak = tie:1, v116:1, v113:1, not_applicable:1`
- `near_real_0007` 上：
  - `more_speech_interference_leaky = v116`
  - `better_retention_minus_speech_leak = v113`
  - `delta_speech_interference_capture_db = +9.2733 dB`
  - `delta_retention_minus_speech_leak_db = -9.3285 dB`

原因：

- 当前 family 的瓶颈，
  已经不能简单归因于 `residual_projection_ratio` 语义不够直接；
- 因为即使改成更直接的 prediction-side projection，
  主失败模式仍完全同向复现。

要求：

- 后续若继续 preserve/bypass family，
  不能再把 loss-mode-only 调整当作高价值主线；
- 若关键样本仍是：
  - `more_speech_interference_leaky = new_run`
  - `better_retention_minus_speech_leak = old_run`
  就应直接转去 integration / 表示机制，而不是继续做 loss-mode sweep。

### 60. 在 preserve/bypass self-anchor family 里，把 refiner integration 从 `complement` 切到 `gate`，会把 whole / total-leak 推得很强，但仍可能同时拉坏 `0007` local speech leak、local artifact 和 absent local suppression

事实：

- `v117` 相对 `v113`：
  - 唯一主动改动是：
    - `branch_overlap_refine_gate_mode`
      - `complement -> gate`
  - synthetic 四条固定验收大幅全正；
  - whole-utterance near-real 也大幅正向：
    - `more_interference_leaky = v113` on `4 / 4`
    - `better_retention_minus_leak = v117` on `3 / 4`
  - 但 overlap-local：
    - `more_speech_interference_leaky = v113:2, v117:2`
    - `more_artifact_proxy_heavy = v117:2, tie:2`
- 最关键的是：
  - `near_real_0007`
    - `more_speech_interference_leaky = v117`
    - `better_retention_minus_speech_leak = v113`
    - `more_artifact_proxy_heavy = v117`
    - `delta_speech_interference_capture_db = +10.6017 dB`
    - `delta_retention_minus_speech_leak_db = -11.3125 dB`
  - `near_real_0009`
    - `more_speech_interference_leaky = v117`
    - `delta_speech_interference_capture_db = +10.9446 dB`

原因：

- `gate` integration 会让 refiner 更直接进入 target-present 区域；
- 这确实能极强地推高 whole / total-leak 指标；
- 但当前单一 refiner 头会把：
  - target-present `music_plus_speech`
  - target-absent speech peak
  两类局部桶一起拉扯，
  不能稳定同时守住：
  - local speech leak
  - local artifact
  - absent suppression

要求：

- 当前 `branch_overlap_refine_head` family 若继续，
  不应再做：
  - selector-only
  - loss-mode-only
  - gate-mode-only
  小步 sweep；
- 下一轮必须直接切到：
  - 新的局部表示 / controller
  - 或显式分开的 target-present / target-absent local 控制语义。

### 61. 给 dual decoder 的 direct-output path 加 `gate floor / blend cap`，只能止住 phone-artifact，不足以修正 final-output dual-target takeover

事实：

- `v118` 相对 `v109`：
  - 新增了：
    - `branch_overlap_dual_decoder_gate_floor = 0.75`
  - 并把 dual path 限到：
    - `gate_mode = gate`
    - `max_blend = 0.15`
  - bandwidth / transients：
    - `tie:4 / tie:4`
    - 说明 phone-artifact / narrowing 已被止住；
  - 但 synthetic 四条固定验收全线回退：
    - abstention `-1.7880 dB`
    - same-gender keep `-2.4133 dB`
    - hard-present keep `-1.1600 dB`
    - hard-present artifact proxy `-2.1929 dB`
  - whole-utterance near-real：
    - `better_source_retention = v118:3, not_applicable:1`
    - `more_interference_leaky = v118:4`
    - `better_retention_minus_leak = tie:2, v109:1, not_applicable:1`
  - overlap-local：
    - `more_speech_interference_leaky = v118:4`
    - `more_total_interference_leaky = v118:4`
    - `better_retention_minus_total_leak = v109:3, not_applicable:1`
- 最关键的是 `near_real_0007`：
  - whole：
    - `better_source_retention = v118`
    - `more_interference_leaky = v118`
    - `better_retention_minus_leak = v109`
    - `delta_interference_capture_db = +12.9325 dB`
  - overlap-local：
    - `more_total_interference_leaky = v118`
    - `better_retention_minus_total_leak = v109`
    - `delta_total_interference_capture_db = +13.4918 dB`

原因：

- `gate floor` 只能解决“dual path 一上来就大面积接管”的安全问题；
- 但只要 integration 仍是：
  - `dual target -> direct final output blend`
  它就还是会把输出拉向：
  - 更高 source retention
  - 更高 interference leak
- 所以修掉 phone-artifact，
  不等于修掉 direct-output dual-target takeover。

要求：

- 后续如果继续 dual-source / dual-interference 语义，
  不应再做：
  - `v118+`
  - 或 direct-output dual decoder 的同构 sweep；
- 下一轮只能改成：
  - auxiliary-only
  - controller-only
  - 或其它不直接接管 final output 的 integration。

### 62. 显式 split target-present / target-absent local control 语义虽然能继续推正 synthetic 与 whole-tradeoff，但 gate-side present head 仍可能把 `0007` local `speech_only` leak 与 `0009` absent local suppression 一起拉坏

事实：

- `v120` 相对 `v113`：
  - 新增了：
    - `enable_branch_overlap_refine_present_head = true`
    - `branch_overlap_refine_present_source_mode = current_residual`
  - 并且只训练：
    - `branch_overlap_refine_present_head`
  - synthetic 四条固定验收全部正向：
    - abstention `+1.2922 dB`
    - same-gender keep `+0.9844 dB`
    - hard-present keep `+0.7738 dB`
    - hard-present artifact proxy `+0.7100 dB`
  - whole-utterance near-real：
    - `more_interference_leaky = v113:4`
    - `better_retention_minus_leak = v120:2, tie:1, not_applicable:1`
    - `tradeoff gate = pass`
  - overlap-local：
    - `more_speech_interference_leaky = v113:2, v120:2`
    - `better_retention_minus_speech_leak = tie:1, v120:1, v113:1, not_applicable:1`
    - `better_retention_minus_total_leak = tie:1, v120:2, not_applicable:1`
- 最关键的是：
  - `near_real_0006`
    - `more_speech_interference_leaky = v113`
    - `better_retention_minus_speech_leak = v120`
    - `delta_retention_minus_speech_leak_db = +3.3014 dB`
  - 但 `near_real_0007`
    - `more_speech_interference_leaky = v120`
    - `better_retention_minus_speech_leak = v113`
    - `delta_speech_interference_capture_db = +8.0218 dB`
    - `delta_retention_minus_speech_leak_db = -8.3666 dB`
  - 且 `near_real_0009`
    - `more_speech_interference_leaky = v120`
    - `delta_speech_interference_capture_db = +9.3707 dB`
- `export_ab_listening_pack.py` relative `v113`
  仍是：
  - `0 candidate sample`

原因：

- split local-control semantics 本身是有效的；
- 但只要 present head 仍主要靠：
  - branch gate
  - current residual
  两个信号自行决定何时出手，
  它就还是可能把优化优先落到：
  - whole-tradeoff
  - total-leak
  - `0006` 这类较容易受益的 target-present speech case；
- 却不能自动保证：
  - `0007` 这类 hard-present `speech_only` local leak
  - `0009` 这类 target-absent speech peak
  不被一起拉坏。

要求：

- 后续若继续 split local-control semantics，
  不应只做：
  - `present_max_delta`
  - `present_source_mode`
  的同构 sweep；
- 下一轮必须直接补：
  - present head 的 target-absent veto / activation guard
  - 或其它更显式的 target-present 激活约束，
  否则 `0007 / 0009` 会继续一起成为 blocker。

### 63. hard present activation floor 证明了 activation guard 方向是对的，但 hard floor 本身过硬；soft `gate^2` shaping 可以把问题从 `0007 / 0009` 双 blocker 收口成单一 `0007 speech_only local leak` blocker

事实：

- `v121 = v120 + hard present gate floor 0.8`
  relative `v120`：
  - synthetic：
    - abstention `-0.6085 dB`
    - same-gender keep `-0.2018 dB`
    - hard-present keep `-0.2776 dB`
    - artifact proxy `+0.1089 dB`
  - whole near-real：
    - `more_interference_leaky = tie:1, v121:3`
    - `better_retention_minus_leak = tie:1, v120:2, not_applicable:1`
    - `tradeoff gate = fail`
  - overlap-local：
    - `near_real_0009`
      - `delta_speech_interference_capture_db = -9.7150 dB`
    - `near_real_0007`
      - `delta_speech_interference_capture_db = -8.1160 dB`
      - `delta_retention_minus_speech_leak_db = +8.2985 dB`
      - 但 `delta_total_interference_capture_db = +1.2538 dB`
      - `delta_retention_minus_total_leak_db = -1.0713 dB`
- `v122 = v120 + soft present gate power 2.0`
  relative `v120`：
  - synthetic 四条固定验收重新全绿：
    - abstention `+0.6248 dB`
    - same-gender keep `+0.6687 dB`
    - hard-present keep `+0.4796 dB`
    - artifact proxy `+0.5698 dB`
  - whole near-real：
    - `more_interference_leaky = v120:3, tie:1`
    - `better_retention_minus_leak = v122:1, tie:2, not_applicable:1`
    - `tradeoff gate = pass`
  - overlap-local：
    - `more_speech_interference_leaky = v120:3, tie:1`
    - `more_total_interference_leaky = v120:4`
    - `better_retention_minus_total_leak = tie:1, v122:2, not_applicable:1`
    - `near_real_0006`
      - `delta_speech_interference_capture_db = -3.0518 dB`
      - `delta_retention_minus_speech_leak_db = +2.9720 dB`
    - `near_real_0009`
      - `delta_speech_interference_capture_db = -1.4628 dB`
    - `near_real_0007`
      - `delta_speech_interference_capture_db = +0.4987 dB`
      - `delta_total_interference_capture_db = -2.1068 dB`
      - `delta_retention_minus_speech_leak_db = -0.7969 dB`
      - `delta_retention_minus_total_leak_db = +1.8086 dB`
- `export_ab_listening_pack.py`
  relative `v120`：
  - `v122` 仍是 `0 candidate sample`
- `v123 = v122 + hardlocal speech_only selector/bundle v1`
  relative `v122`：
  - synthetic 四条固定验收仍全绿
  - whole near-real tradeoff gate 通过
  - 但 overlap-local：
    - `near_real_0007`
      - `delta_speech_interference_capture_db = +1.3089 dB`
      - `delta_retention_minus_speech_leak_db = -1.4342 dB`
    - `near_real_0009`
      - `delta_speech_interference_capture_db = +1.8143 dB`
  - 说明 hardlocal `speech_only` 子域继续把优化拉向：
    - whole / total-leak
    而不是：
    - `0007` local `speech_only` leak
    - `0009` absent local suppression
- `v124 = v122 + soft present gate power 3.0`
  relative `v122`：
  - synthetic 已出现明确回退：
    - abstention `-0.1189 dB`
    - hard-present keep `-0.0468 dB`
  - 不再补 near-real，直接判定：
    - activation shaping 不能继续往 `3.0+` 扫
- `v125 = v122 + soft present gate power 2.5`
  relative `v122`：
  - synthetic 四条固定验收恢复小幅全绿：
    - abstention `+0.0600 dB`
    - same-gender keep `+0.1311 dB`
    - hard-present keep `+0.0751 dB`
    - artifact proxy `+0.1221 dB`
  - whole near-real：
    - `tradeoff gate = pass`
    - `near_real_0007`
      - `delta_interference_capture_db = -0.7946 dB`
      - `delta_retention_minus_leak_db = +0.7309 dB`
  - overlap-local：
    - `near_real_0009`
      - `delta_speech_interference_capture_db = -2.9284 dB`
    - `near_real_0007`
      - `delta_speech_interference_capture_db = -0.4983 dB`
      - `delta_total_interference_capture_db = -0.5610 dB`
      - `delta_retention_minus_speech_leak_db = +0.4330 dB`
      - `delta_retention_minus_total_leak_db = +0.4957 dB`
  - 自动阈值上仍多是 `tie`，
    但它已经是当前 split local-control semantics
    relative `v122` 首次同时把：
    - `0007`
    - `0009`
    往正确方向推进；
  - blind listening pack 已落盘：
    - `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v122_vs_v125_blind`
  - focused 听审已完成：
    - `tie = 4`
    - `v122 = 0`
    - `v125 = 0`
  - pack 第 1 条 `near_real_0003`
    备注为：
    - `B样本有误差级别的伪影高于A。`
  - 结论更新为：
    - automatic 上的正向 drift 仍未转成可听优势；
    - 核心痛点仍未解决；
    - `v125` 不升格，只保留为当前最好的 automatic continuation。

原因：

- hard floor 的价值只在于证明：
  - activation guard 不是错方向；
- 但 hard floor 会把中低 gate 的 present region 直接砍掉，
  于是 whole / synthetic 很容易一起回退；
- soft `gate^2` shaping 则保留了：
  - 低 gate 区域更弱
  - 高 gate 区域仍可连续出手
  这类更平滑的激活约束，
  因而能同时守住：
  - synthetic
  - whole-tradeoff
  - total leak
- 但 soft shaping 本身仍主要在优化：
  - whole leak
  - total local leak
  还不足以保证：
  - `near_real_0007` 的 `speech_only local leak`
  直接转正。

要求：

- 不再回到：
  - `hard floor`
  - `gate threshold`
  这类同构 activation sweep；
- split local-control semantics 的下一轮应直接补：
  - 当前先不再继续扫：
    - `hardlocal selector`
    - `gate_power`
    - `gate threshold / present_max_delta`
  - 默认直接改机制去打：
    - `0007 speech_only local leak`
    - `target-absent veto`；
- 当前可保留的 active continuation 是：
  - `v125`
  但它只是 automatic continuation，
  不是可听胜出的候选；
- `v121 / v123 / v124`
  仍全部收口，不再回看。
- `v126 = v125 + present-head complement-ratio veto 0.5`
  relative `v125`：
  - synthetic 四条固定验收继续小幅全绿：
    - abstention `+0.0235 dB`
    - same-gender keep `+0.0336 dB`
    - hard-present keep `+0.0146 dB`
    - artifact proxy `+0.0298 dB`
  - whole near-real：
    - `more_interference_leaky = tie:3, v125:1`
    - `better_retention_minus_leak = tie:2, v126:1, not_applicable:1`
    - 核心收益集中在：
      - `near_real_0007`
        - `delta_interference_capture_db = -1.4286 dB`
        - `delta_retention_minus_leak_db = +1.3823 dB`
  - overlap-local：
    - `more_speech_interference_leaky = tie:4`
    - `more_total_interference_leaky = tie:3, v125:1`
    - `near_real_0007`
      - `delta_speech_interference_capture_db = +0.0284 dB`
      - `delta_total_interference_capture_db = -0.7020 dB`
      - `delta_retention_minus_speech_leak_db = -0.0782 dB`
      - `delta_retention_minus_total_leak_db = +0.6521 dB`
    - `near_real_0009`
      - `delta_speech_interference_capture_db = +0.1498 dB`
  - 结论：
    - complement-ratio veto 是真实方向；
    - 但当前只把 `0007` 的 whole / total-leak 再推前一点；
    - 还没有把：
      - `0007 speech_only local leak`
      - `0009 absent local suppression`
      变成决定性收益；
    - `v126` 可接替 `v125`
      成为当前最佳 automatic continuation，
      但仍不导听审。

补充事实：

- 当前 `train / val_manifest_local_speech_leak_artifact_paired_0007_like_bundle_v1`
  实际不含 absent 样本；
- 因而在这套 `0007_like` 训练资产上，
  直接靠 `absent / absent_extra` selector
  去验证 `target-absent veto`
  本质上是空转。

要求更新为：

- 不继续做：
  - `present_veto_strength / power`
  的同构 sweep；
- 若下一轮还要打 `target-absent veto`，
  默认需要：
  - 一套真正含 absent anchor 的训练资产，
    或
  - 与 `0007 speech_only local leak`
    绑定的新机制，
    不能只靠当前 `0007_like bundle`
    反复微调。

- `v127 = v126 + true absent anchor bundle + absent_extra 0.02`
  relative `v126`：
  - 先澄清：
    - `sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap`
      不是“真实 absent interval 训练资产”；
    - 它对应 rows 实际仍是：
      - `target_full`
      - `target_absent_intervals = []`
    - 因而 true absent supervision
      不能继续拿 `v40` 类历史 absent proxy
      代替。
  - 本轮新资产：
    - `target_clean_speech`
    - `target_absent_head / tail`
    - `speech_only`
    - `overlap >= 0.8`
    - train `95`
    - val `24`
    - merged bundle 变成：
      - train `203`
      - val `63`
  - selector 命中：
    - `absent_extra = 95 / 203` train
    - `absent_extra = 24 / 63` val
    - 说明这次不是空 selector
  - synthetic 四条固定验收全线转负：
    - abstention `-0.1881 dB`
    - same-gender keep `-0.1060 dB`
    - hard-present keep `-0.1184 dB`
    - artifact proxy `-0.0378 dB`
  - whole near-real：
    - `more_interference_leaky = v127:3, tie:1`
    - `better_retention_minus_leak = v126:2, tie:1, not_applicable:1`
    - `near_real_0007`
      - `delta_interference_capture_db = +6.3493 dB`
      - `delta_retention_minus_leak_db = -6.0824 dB`
    - `near_real_0003`
      - `delta_interference_capture_db = +1.0259 dB`
    - `near_real_0006`
      - `delta_interference_capture_db = +0.9269 dB`
  - overlap-local：
    - `near_real_0009`
      - `delta_speech_interference_capture_db = -9.3758 dB`
      - true absent local suppression 明显成立
    - `near_real_0007`
      - `delta_speech_interference_capture_db = -3.3370 dB`
      - `delta_total_interference_capture_db = +2.0839 dB`
      - `delta_retention_minus_speech_leak_db = +3.5401 dB`
      - `delta_retention_minus_total_leak_db = -1.8808 dB`
      - 即 speech-only local leak 更干净，
        但 total leak / overall tradeoff 更差
  - 结论：
    - true absent supervision 本体有效；
    - 但当前 `split-present present-head-only`
      routing / coupling 错位；
    - 不导听审，
      不继续扫 `absent_extra_weight`。

- `v128 = v126 + true absent anchor bundle + absent_extra 0.02 + complement-head only routing`
  relative `v126`：
  - 与 `v127` 的唯一区别不是监督本体，
    而是 trainable path 改成：
    - `branch_overlap_refine_head`
    - 而不再直接更新 `present-head-only`
  - synthetic 四条固定验收重新全线转正：
    - abstention `+0.2733 dB`
    - same-gender keep `+0.1355 dB`
    - hard-present keep `+0.2477 dB`
    - artifact proxy `+0.1029 dB`
  - 说明：
    - true absent supervision 的问题
      不在 supervision 本体，
      而在 routing
  - 但 whole near-real 仍不能保留：
    - `more_interference_leaky = v128:2, tie:2`
    - `better_retention_minus_leak = v126:1, tie:2, not_applicable:1`
    - `near_real_0007`
      - `delta_interference_capture_db = +8.5356 dB`
      - `delta_retention_minus_leak_db = -8.3363 dB`
    - `near_real_0009`
      - `delta_interference_capture_db = +1.5064 dB`
  - overlap-local：
    - `near_real_0009`
      - `delta_speech_interference_capture_db = -5.6247 dB`
    - `near_real_0006`
      - `delta_speech_interference_capture_db = -1.3851 dB`
    - `near_real_0007`
      - `delta_speech_interference_capture_db = -0.8117 dB`
      - `delta_total_interference_capture_db = +2.5239 dB`
  - 结论：
    - routing hypothesis 成立，
      但 `v128` 仍不是可升格 continuation。

- `v129 = v128 + absent_extra 0.01`
  relative `v128`：
  - 只做一档最小 reweight，
    不改训练资产，
    不改 trainable path
  - synthetic 四条固定验收继续微正：
    - abstention `+0.0424 dB`
    - same-gender keep `+0.0366 dB`
    - hard-present keep `+0.0541 dB`
    - artifact proxy `+0.0063 dB`
  - whole near-real：
    - `more_interference_leaky = tie:3, v128:1`
    - `better_retention_minus_leak = tie:2, v129:1, not_applicable:1`
    - `near_real_0007`
      - `delta_interference_capture_db = -6.2120 dB`
      - `delta_retention_minus_leak_db = +6.2530 dB`
    - 但 `near_real_0009`
      - `delta_interference_capture_db = +0.2374 dB`
  - overlap-local：
    - `near_real_0007`
      - `delta_speech_interference_capture_db = -2.4872 dB`
      - `delta_total_interference_capture_db = -1.0267 dB`
    - `near_real_0009`
      - `delta_speech_interference_capture_db = +4.1453 dB`
  - 因而 relative `v126`：
    - `near_real_0007`
      - whole `delta_interference_capture_db = +2.3236 dB`
      - local `delta_speech_interference_capture_db = -3.2989 dB`
    - `near_real_0009`
      - whole `delta_interference_capture_db = +1.7438 dB`
      - local `delta_speech_interference_capture_db = -1.4794 dB`
  - 结论：
    - `v129` 是 decoupled true-absent 支线当前最佳 continuation，
      但仍不能替代 `v126` 成为主线最佳 automatic continuation。

- `v130 = v129 + complement-head gate_power 2.0`
  relative `v129`：
  - 新增最小机制：
    - `branch_overlap_refine_head`
      增加 `gate_power / gate_floor`
  - 首档 pilot 直接失败：
    - abstention `-0.3591 dB`
    - same-gender keep `-0.2566 dB`
    - hard-present keep `-0.3005 dB`
    - artifact proxy `-0.1715 dB`
  - 因为四条固定验收已全线明显转负，
    本轮不再补 near-real
  - 结论：
    - complement-head `gate_power / gate_floor`
      shaping 这条轴不值得继续，
      直接收口。

- `v131 = v126 + true-absent dual-controller absent-mix v1`
  relative `v126`：
  - 这轮不再把 true absent supervision
    直接打到 final output，
    而是改为：
    - 新开 `branch_overlap_dual_decoder_head`
    - `apply_mode = gate_controller`
    - 对 `overlap_dual_residual_prediction`
      在 true-absent local window 上做 `mixture` 对齐
  - 训练 selector 命中有效，
    不是 no-op：
    - `overlap_dual = 95 / 203` train
    - `overlap_dual = 24 / 63` val
  - 但四条 fixed synthetic checks
    再次全线明显转负：
    - abstention `-3.0643 dB`
    - same-gender keep `-2.3636 dB`
    - hard-present keep `-1.9456 dB`
    - artifact proxy `-1.7674 dB`
  - 结论：
    - 问题不只是
      “true absent supervision
      不能直接灌进 final output”；
    - 更进一步地，
      只要 absent controller
      最终仍通过 `gate_controller`
      回灌到 global present path，
      就会系统性伤到：
      - abstention
      - present keep
      - artifact guardrail
    - 因而
      `overlap_dual_absent_mix_weight`
      及其同构的
      `gate_controller + absent-mix`
      接法不再继续，
      直接收口。

- `v132 = v126 + true-absent dual current-output absent-mix v1`
  relative `v126`：
  - 这轮把 `v131`
    的 dual branch apply
    从 `gate_controller`
    改为 `current_output` 局部 blend，
    希望只改当前输出的 absent-like 局部区域，
    不再经过 global gate 重算
  - 训练 selector 仍有效，
    不是 no-op：
    - `overlap_dual = 95 / 203` train
    - `overlap_dual = 24 / 63` val
  - 但四条 fixed synthetic checks
    还是全线明显转负，
    而且 abstention 比 `v131` 更差：
    - abstention `-6.6014 dB`
    - same-gender keep `-1.3396 dB`
    - hard-present keep `-2.3761 dB`
    - artifact proxy `-2.4415 dB`
  - 结论：
    - 问题不只在
      `gate_controller`
      这种 global recoupling；
    - 即便 dual target
      只对当前输出做局部 rewrite，
      只要 true-absent dual branch
      直接改 final output，
      也会系统性伤到：
      - abstention
      - present keep
      - artifact guardrail
    - 因而
      `current_output + absent-mix`
      这条接法也不再继续，
      直接收口。

- `v133` 暴露了一个 gate-only supervision 接线坑：
  - 初版 `gate_absent_sample_weights`
    直接沿用了
    `absent_union_sample_weights`
  - 但当 run
    没有显式配置
    `absent_* selector`
    时，
    `resolve_selector_sample_weights(...)`
    会返回 `None`
  - `weighted_gate_target_loss(...)`
    在 `sample_weights is None`
    时直接变成 `0.0`
  - 结果就是：
    - `train_gate_absent_mean = 0.0`
    - `val_gate_absent_mean = 0.0`
    - 表面上像是 “训练稳定”，
      实际上是整条 `gate_absent`
      根本没命中
  - 后续凡是做 gate-only absent supervision，
    必须优先核对：
    - `gate_absent_sample_weights`
      是否直接从
      `target_absent_intervals`
      构造
    - `train / val_gate_absent_mean`
      是否显著非零

- `v134 / v135` 共同补充了一个更强边界：
  - `v134`
    已证明：
    - `target_absent_intervals -> gate=0`
      这条 gate-head-only supervision
      机制是真实生效的，
      不是 no-op
  - `v135`
    又证明：
    - 即便再给当前 gate head
      补 sparse
      `branch_protect`
      keep anchors，
      也救不回 fixed guardrails
  - 因而当前默认不再继续扫：
    - `gate_absent_weight`
    - `gate_keep_weight`
    - `gate-head-only absent veto / keep`
  - 如果还要继续 true-absent indirect path，
    默认应换到：
    - `auxiliary_only / monitor-only`
      分支
    - 而不是继续直接监督
      `branch_decoder_frame_gate`

- `v136 / v137` 补充了
  `auxiliary_only` true-absent indirect path
  的新边界：
  - `v136`
    已证明：
    - 通过
      `branch_overlap_cancel_head`
      做
      `auxiliary_only`
      absent-local indirect supervision
      是真实生效的，
      不是 no-op
    - 它可以在局部窗口里
      给出正确方向的真收益：
      - `near_real_0009`
        absent local leak
        显著下降
      - `near_real_0007 speech_only`
        local leak
        也显著下降
  - 但 `v136`
    同时也证明：
    - `speech_only local leak`
      变好
      不等于
      `total leak`
      会一起变好
    - 更不等于
      whole near-real
      会变好；
      `0003 / 0006 / 0007`
      仍会整体更 leak
  - `v137`
    又进一步证明：
    - 把
      `overlap_cancel_absent_mix_weight`
      从 `0.02`
      降到 `0.01`
      并不能把这条机制
      拉回 guardrail 安全区；
    - 四条 fixed synthetic checks
      反而比 `v136`
      全部更差
  - 因而当前默认不再继续扫：
    - `overlap_cancel_absent_mix_weight`
    - `auxcancel absent-mix`
      的同构 reweight
  - 如果还要继续这条 indirect path，
    默认应改成：
    - 更局部的
      `monitor-only / local-window-only`
      apply 机制
    - 或直接转向
      `near_real_0007 total leak`
      目标，
      而不是继续优化
      broad absent-local mixture target

- `v138 / v139 / v140 / v141 / v142`
  进一步补了
  `split-selector + head-only direct-apply`
  家族的边界：
  - 先是接线层：
    - `overlap_cancel_waveform / target_projection`
      与
      `overlap_cancel_absent_mix`
      不能再共用
      一个 generic
      `overlap_cancel_sample_weights`
    - `v139`
      已证明
      split-selector 本体
      是真实机制，
      不是 no-op
  - `v140`
    明确证明：
    - 只训练
      `branch_overlap_cancel_head`
      且
      `apply_mode = auxiliary_only`
      时，
      即便训练 selector
      和 absent-mix loss
      都显著非零，
      inference 仍会是 exact no-op
    - 所以后续凡是
      `head-only auxiliary_only`
      实验，
      必须先默认它
      没有输出路径；
      除非显式新增
      final-output apply 机制
  - `v141`
    又补出更强边界：
    - 同一个
      direct-apply
      `branch_overlap_cancel_head`
      可以承载
      `present-total`
      或
      `absent-local`
      其中一类目标，
      但不能同时稳定承载两类
    - 一旦把
      absent-local mix target
      也灌回同一个
      direct-apply cancel head，
      就会出现：
      - `0007 total leak`
        改善
      - 但
        `0007 speech_only`
        与
        `0009 absent local`
        同时恶化
  - `v142`
    则证明：
    - `present-total bounded direct path`
      本体是有效且相对安全的
    - 但它并不会自动解决：
      - `0007 speech_only local leak`
      - `0009 absent local`
    - 因而之后不能把
      “`0007 total leak`
      变好”
      误判成
      “核心 blocker
      已被解决”
  - 当前默认不再继续扫：
    - 同一个 direct-apply cancel head
      上的
      `absent_mix` reweight
    - 同头混训
      `present-total + absent-local`
  - 如果要继续，
    默认应改成：
    - 保留 `v142`
      这条
      present-total direct path
    - 另开更强解耦的
      absent path
      去处理
      `0007 speech_only`
      和
      `0009 absent local`

- `v143 / v144 / v145 / v146`
  又补了
  `v142` 之上的
  `overlap_refine` sibling
  边界：
  - `v143`
    已证明：
    - 在
      `v142 + self-teacher`
      前提下，
      稀疏
      `0007-like speech-only`
      selector
      只会收敛成
      practical no-op
  - `v144`
    又证明：
    - 即便把 speech-local selector
      扩到
      `33 / 99` train、
      `7 / 37` val，
      `branch_overlap_refine_present_head`
      仍然推不出
      可观测输出变化
  - `v145`
    进一步证明：
    - 把 sibling
      从
      `refine_present_head`
      换成
      `refine_head`
      本体之后，
      的确能让 training-side
      `overlap_interference_projection_ratio`
      显著非零；
    - 但 inference 侧
      仍然是 near-no-op，
      连 targeted
      `local_speech_leak_proxy_v1`
      compare
      也没有显著变化
  - `v146`
    则补了一个实现坑点：
    - 当前训练入口会对
      init checkpoint
      自动做
      `teacher_checkpoint`
      metadata fallback
    - 因而
      “不传 `--teacher-checkpoint`”
      不等于
      “真的无 teacher”
    - 这轮原本想做
      no-teacher，
      实际却继承到了
      `v126`
      teacher；
      而且最终仍是 exact no-op
  - 当前默认不再继续扫：
    - `v142` 之上的
      `refine_present` sibling
    - `v142` 之上的
      `refine_base` sibling
    - `speech-only selector`
      宽窄同构 sweep
    - `teacher=self`
      同构 rerun
  - 如果后续还要继续：
    默认应先做二选一：
    - 新增真正不同的
      output apply path
    - 或先给训练入口补一个
      明确的
      `disable teacher metadata fallback`
      开关，
      再验证真正的
      no-teacher branch
- `v147 / v148 / v149`
  又补了三条实现边界：
  - `v147`
    证明：
    - 训练入口在补完
      `disable teacher metadata fallback`
      之后，
      true no-teacher
      `refine_base`
      rerun
      relative `v142`
      仍然是 exact no-op
    - 所以
      `v142` 之上的
      `refine_base` sibling
      不只是 teacher-anchor no-op，
      连 true no-teacher
      也推不出输出变化
  - `v148`
    暴露了另一个接班坑点：
    - 不能用更宽的 bundle 文件
      去近似复原
      `v142`
      当时的 hardlocal
      `focus_sample_ids`
    - 否则 selector
      会从
      `3 / 203`
      意外膨胀到
      `105 / 203`
      而失去可比性
  - `v149`
    则证明：
    - 把
      `branch_overlap_cancel_head`
      的 direct-apply blend
      改成
      `predicted_activity`
      这种
      cancel-ratio-derived
      self-bounded 路由，
      并不会更安全
    - 即便 selector
      已精确回到
      `3 / 203`
      与
      `3 / 63`，
      也仍会系统性打坏：
      - `abstention`
      - `same-gender keep`
      - `hard-present keep`
      - `artifact proxy`
  - 当前默认不再继续扫：
    - `predicted_activity`
    - `predicted_activity + max_blend`
    - 同构的
      cancel-strength-derived
      output blend
- `v150 / v151 / v152`
  则补出了
  `decoupled apply-controller`
  的新坑点：
  - `v150`
    说明：
    - 若只训练
      `branch_overlap_cancel_apply_controller_head`
      且沿用
      `v142`
      的
      `3 / 203`
      与
      `3 / 63`
      hardlocal selector，
      结果会是 practical no-op
    - 所以
      “把 apply 从 cancel head 拆出去”
      本身不等于
      “就能安全地产生输出变化”
  - `v151`
    说明：
    - 即便同时训练
      `branch_overlap_cancel_head`
      与
      `apply_controller_head`，
      在窄 selector 下
      也只是：
      - fixed checks
        基本 near-tie
      - targeted
        `local_speech_leak_proxy_v1`
        变差
    - 也就是说：
      signal-on
      不等于
      local blocker
      会自动变好
  - `v152`
    则排除了
    “只是 selector 太稀”：
    - 把 selector
      扩到
      broader hardlocal bundle
      后，
      overlap-cancel signal
      明显变强
    - 但：
      - `abstention`
      - `hard-present keep`
      - `artifact proxy`
      - `local speech-leak proxy`
      反而一起转负
  - 当前默认不再继续扫：
    - `apply-controller` init bias
    - `apply-controller only`
    - `apply-controller + cancel`
    - `apply-controller` selector 宽窄
  - 如果后续还要继续：
    默认应改做：
    - 不直接重写 final output 的
      local-window-only 机制
    - 或完全不经
      overlap-cancel direct subtract
      的
      monitor-only / auxiliary-only path
- `v153 / v154 / v155 / v156 / v157 / v158`
  则继续补齐了
  `interval-veto`
  这条 family
  的边界：
  - `v153`
    证明：
    - interval-scoped
      `apply_controller`
      supervision
      不是 no-op
    - 它第一次在
      `v142`
      之上同时把
      `0007 speech_only`
      与
      `0009 absent local`
      往正确方向推
    - 但它不会自动修好
      `0007 total leak`
      或
      `0009 whole absent`
  - `v154`
    说明：
    - 在窄资产上
      稍微加重 keep
      可以把这条线
      收到一个
      objective 可保留点
    - 但仍会留下
      `0009 whole absent`
      regression
  - `v155`
    暴露了接班坑点：
    - 不能在旧
      `0007_like_plus_true_absent_anchor_bundle_v2`
      上宣称
      broader keep
    - 因为对应 sample ids
      根本不存在，
      selector
      不会真的变宽
  - `v156`
    说明：
    - 一旦 broader keep
      真接到 union bundle，
      controller
      很容易塌回
      near-neutral
    - 结果会变成：
      - 更安全
      - 但也更接近
        practical no-op
  - `v157`
    则说明：
    - 在真实 broader keep
      已接上的前提下，
      重新加压 absent
      仍能恢复
      一部分正确方向 signal
    - 它是当前这条
      family
      的最佳 continuation
    - 但 blocker
      仍是
      `0007 total leak`
      而不是
      `0007 speech_only`
  - `v158`
    则进一步说明：
    - 继续扫
      `gate_keep_weight`
      只会同时削弱：
      - 正确方向的
        `speech_only / absent local`
        改善
      - 错误方向的
        `0007 total leak`
        regression
    - 也就是说，
      keep reweight
      不是修这个 blocker
      的有效轴
  - `v159`
    进一步说明：
    - 固定 low-band
      speech-band apply
      只会把
      `0007 speech_only`
      和 `0009 absent local`
      的正确方向改进
      保留一点点
    - 但改不掉
      `0007 total leak`
      的符号，
      whole `0007`
      还会继续转差
    - 所以
      `branch_overlap_cancel_apply_max_freq_ratio`
      不是有效轴
  - `v160`
    则补齐了另一个边界：
    - 对
      apply-controller
      做 activation floor
      也只是更 sparse 的
      time-local writeback
    - 它会略微改善
      `0007 speech_only`
      并缩小
      `0007 total leak`
      regression
    - 但 `total leak`
      仍然是错方向，
      whole `0007`
      也仍然更漏
    - 所以
      `branch_overlap_cancel_apply_controller_floor`
      也不再继续
  - 当前默认不再继续扫：
    - `interval-veto union-bundle gate_keep_weight`
    - 同构的
      keep-side reweight
    - `branch_overlap_cancel_apply_max_freq_ratio`
    - `branch_overlap_cancel_apply_controller_floor`
  - 如果后续还要继续：
    默认应改做：
    - 以 `v157`
      为 active base
    - 不再只改
      apply 稀疏度
      或频带形状
    - 而是直接拆
      controller supervision
    - 让
      `0007 total leak`
      不再作为
      absent-veto
      同一个 scalar controller
      的副作用

## 近期关键案例入口

- `reports/daily/2026-03-26_overlap_abstention_proxy_v3_v4_and_v71_v72_followup.md`
- `reports/daily/2026-03-26_present_keep_guardrail_v1_v2_and_v73_v74_followup.md`
- `reports/daily/2026-03-26_audibility_conditioned_v1_and_abstention_gate_v1_v75_v76_v77.md`
- `reports/daily/2026-03-26_abstention_gate_proxy_v1_and_v78_v79_followup.md`
- `reports/daily/2026-03-26_hard_present_gate_keep_guardrail_v1_and_v80_followup.md`
- `reports/daily/2026-03-26_audibility_gate_target_v1_and_v81_followup.md`
- `reports/daily/2026-03-26_v54_vs_v81_listening_review.md`
- `reports/daily/2026-03-26_overlap_aux_interference_decoder_v2_v3_v4_and_v93_v94_v95_followup.md`
- `reports/daily/2026-03-26_v81_vs_v95_listening_review.md`
- `reports/daily/2026-03-26_teacher_artifact_veto_v99_v100_followup.md`
- `reports/daily/2026-03-26_v81_vs_v100_listening_review.md`
- `reports/daily/2026-03-26_overlap_cancel_deltablend_v1_v101_followup.md`
- `reports/daily/2026-03-26_v81_vs_v101_listening_review.md`
- `reports/daily/2026-03-26_overlap_local_benchmark_v81_v88_v95_v100_v101_followup.md`
- `reports/daily/2026-03-27_speech_only_selector_profile_prework.md`
- `reports/daily/2026-03-27_overlap_purify_v2_speechonly_v102_followup.md`
- `reports/daily/2026-03-27_plusmusic_teacher_veto_v103_followup.md`
- `reports/daily/2026-03-27_v81_vs_v103_listening_review.md`
- `reports/daily/2026-03-27_hard_present_artifact_proxy_v1_materialization.md`
- `reports/daily/2026-03-27_artifactaware_pilots_v104_v105_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_proxy_v107_followup.md`
- `reports/daily/2026-03-27_v81_vs_v107_listening_review.md`
- `reports/daily/2026-03-27_phone_artifact_gate_v1_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_preservebackstop_v108_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_0007like_backstop_v109_followup.md`
- `reports/daily/2026-03-27_v81_vs_v109_listening_review.md`
- `reports/daily/2026-03-27_local_speech_leak_artifact_paired_0007like_v110_followup.md`
- `reports/daily/2026-03-27_local_speech_leak_artifact_paired_0007like_selfanchor_v111_followup.md`
- `reports/daily/2026-03-27_overlap_cancel_splitpath_0007like_v112_followup.md`
- `reports/daily/2026-03-27_overlap_refine_preservebypass_0007like_selfanchor_v113_followup.md`
- `reports/daily/2026-03-28_true_absent_auxcancel_indirect_v136_v137_followup.md`
- `reports/daily/2026-03-28_splitselector_headonly_directapply_v138_v142_followup.md`
- `reports/daily/2026-03-28_refine_siblings_on_v142_v143_v146_followup.md`
- `reports/daily/2026-03-28_headonly_predactivity_directapply_v148_v149_followup.md`
- `reports/daily/2026-03-28_applycontroller_on_v142_v150_v152_followup.md`
- `reports/daily/2026-03-28_applycontroller_interval_veto_v153_v158_followup.md`
- `reports/daily/2026-03-28_applycontroller_interval_veto_localapply_v159_v160_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_0007like_localpush_v114_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_hardlocal_selector_v115_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_0007like_predproj_v116_followup.md`
- `reports/daily/2026-03-28_overlap_refine_preservebypass_0007like_gateguided_v117_followup.md`
- `reports/daily/2026-03-28_overlap_dual_controller_floor_0007like_v118_followup.md`
