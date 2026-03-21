# 踩坑记录 历史归档 51-60

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `51-60`

## 2026-03-16

### 51. 把 interference selector 缩到 music-only，容易出现“局部 metric 更漂亮，但整体比上一版更差”的过拟合假象

现象：

- `legacy_transient_leakguard_probe_v2_musiconly` 只对：
  - `target_music`
  - `target_clean_plus_music`
  - `target_hard_plus_music`
  施加 interference selector。
- 它在默认 synthetic val 上相对 `legacy stage2` 仍有：
  - `avg_sisdr_delta_db = +0.665876`
- 同时 `interference_projection_ratio` 进一步压到：
  - `0.0319`
- 但相对上一版 `legacy_transient_leakguard_probe_v1` 却变成：
  - `avg_sisdr_delta_db = -0.183896`
  - 并在 `target_only / hard_speech / clean_speech` 等非 music 主体上大面积回退。

影响：

- 这说明“leak metric 更低”不等于“当前 candidate 更稳”。
- 当 selector 缩得过窄时，模型会更像在针对某一类干扰专门收缩，而不是整体 trade-off 更好。

处理：

- 当前已明确不保留 `legacy_transient_leakguard_probe_v2_musiconly` 作为后续主候选。

后续要求：

1. 后面只要改 selector 范围，默认必须同时看：
   - 相对 `legacy stage2`
   - 相对上一版 objective-only 最强候选
2. 不能只因为某个 focused metric 更好，就把更窄 selector 当成自然升级。

### 52. 单纯下调 interference loss 权重，虽然能减 residual-heavy，但不等于 near-real 风险就同步转正

现象：

- `legacy_transient_leakguard_probe_v3_w0005` 将 `interference_weight` 从：
  - `0.01 -> 0.005`
- 相对 `legacy_transient_leakguard_probe_v1`，它在 near-real trade-off 上确实收回了一部分 residual-heavy 问题：
  - `more_residual_heavy` 从 `6` 条降到 `1` 条
  - `residual_output_share` 均值从 `0.679 -> 0.654`
- 但同时它也带来：
  - `retention_minus_leak_db` 从 `28.938 -> 28.585`
  - 带宽收窄计数从 `2 -> 3`
  - `more_interference_leaky` 仍是 `5` 条

影响：

- 这说明“把 loss 调轻一点”更像是在移动 trade-off，而不是自动修复根因。
- 如果没有同时盯 leakage、带宽和 retention-minus-leak，只看 residual share，很容易误判 `v3` 已经更稳。

处理：

- 当前已把 `legacy_transient_leakguard_probe_v3_w0005` 记录为“更保守的参考分支”，但不替代 `v1`。

后续要求：

1. 后续若继续调 interference 权重，必须把以下指标成组看：
   - `interference_projection_ratio`
   - `residual_output_share`
   - `retention_minus_leak_db`
   - near-real 带宽 / 瞬态诊断
2. 不要把“residual 更轻”单独当作升级依据。

### 53. 把 leak-guardrail 的 interference selector 收窄到 speech-only recipes，不等于 speech-only near-real 回退就会自动修好

现象：

- 本轮新增 `legacy_transient_leakguard_probe_v4_speechfocus_ft1`：
  - 从 `legacy_transient_leakguard_probe_v1` warm-start；
  - 保留 `interference_weight = 0.01`；
  - 但把 `interference_focus_recipes` 从全 interference recipe 收窄到：
    - `target_clean_speech`
    - `target_hard_speech`
- 它在 synthetic 默认 val 上相对 `legacy stage2` 反而更强：
  - `avg_sisdr_delta_db = +0.969665`
- 相对 `legacy_transient_leakguard_probe_v1` 也仍是正增益：
  - `avg_sisdr_delta_db = +0.119893`

影响：

- 如果只看 synthetic 总体均值，很容易误判成：
  - “既然 speech-focused 更强，那 speech-only near-real 应该也更稳”
- 但实际 near-real 自动诊断并没有这么走：
  - `more_interference_leaky` 仍是 `5` 条；
  - `better_retention_minus_leak` 仍是 `2` 条，落后 `legacy stage2` 的 `3` 条；
  - `near_real_0003 / 0004` 这两条 speech-only 回退点仍未修正；
  - `target_only / target_singing_vocal` 相对 `v1` 还开始出现 guardrail 回退。

处理：

- 已将该分支正式记录为：
  - `reports/daily/2026-03-17_speech_only_leakguard_followup.md`
- 当前把它定位为：
  - 有价值的诊断性 follow-up
  - 但不升级为新的主候选，也不排到 `v3_w0005` 前面

后续要求：

1. 后续若继续围绕 speech-only 问题做实验，不能只靠“把 selector 再收窄一点”作为默认思路。
2. 必须继续同时看：
   - `near_real_0003 / 0004` 这类关键 speech-only 样本；
   - `more_interference_leaky`
   - `better_retention_minus_leak`
   - `target_only / singing` guardrail 代价
3. 若目标真的是修 speech-only near-real 回退，下一步更应该考虑：
   - 更贴近 residual / leak 机制的约束
   - 或 target absent / speech absent guardrail
   - 而不是继续单改 selector 覆盖范围。

### 54. 直接把 target-absent guardrail 权重拉高，虽然能明显压低 absent leakage，但很容易把模型推成 residual-heavy / over-suppressed

现象：

- 本轮已把 `target_absent_intervals` 正式接入训练 / 评估管线，并新增：
  - `absent_interval_l1`
- 基于这条入口，新增 `legacy_transient_leakguard_probe_v5_absentguard_ft1`：
  - 从 `legacy_transient_leakguard_probe_v1` warm-start；
  - 保留 `transient_weight = 0.002` 与 `interference_weight = 0.01`；
  - 新增 `absent_weight = 20`；
  - focused 在：
    - `target_clean_speech`
    - `target_hard_speech`
    - `target_clean_plus_music`
    - `target_hard_plus_music`
  - pattern 限于：
    - `target_absent_head`
    - `target_absent_tail`
    - `target_intermittent`
- 它在 synthetic 上确实把 absent leakage 压得很明显：
  - `absent_interval_l1: 0.00010835 -> 0.00001870`
- 但同时：
  - 默认 val 相对 `legacy_transient_leakguard_probe_v1` 变成 `avg_sisdr_delta_db = -0.662080`
  - focused absent-guard recipes 上也仍为 `avg_sisdr_delta_db = -0.894569`

影响：

- 如果只看 `absent_interval_l1`，很容易误判成：
  - “target-absent guardrail 已经修好了”
- 但 near-real 自动诊断给出的实际信号是：
  - `better_source_retention = legacy_stage2 7`
  - `more_interference_leaky = legacy_stage2 8`
  - `more_residual_heavy = legacy_transient_leakguard_probe_v5_absentguard_ft1 7`
- 也就是：
  - 干扰确实压得更狠；
  - 但 target capture 也一起被压掉；
  - 最终变成更明显的 residual-heavy / over-suppressed 版本。
- 关键回退样本包括：
  - `near_real_0003`
  - `near_real_0005`
  - `near_real_0007`
  - `near_real_0010`

处理：

- 已将该分支正式记录为：
  - `reports/daily/2026-03-18_absent_guardrail_probe.md`
- 当前把它定位为：
  - 有价值的机制探针
  - 但不升级为新的 objective-only 候选

后续要求：

1. 以后若继续做 target-absent guardrail，不能只盯 `absent_interval_l1` 单指标。
2. 必须继续同时看：
   - 默认 val 相对 `v1` 的退化
   - near-real `better_source_retention`
   - near-real `more_residual_heavy`
   - `near_real_0003 / 0004 / 0005 / 0007 / 0010`
3. 当前这条线只允许做更保守的小步 follow-up：
   - 更低 absent weight
   - 更窄 selector
   - 不再直接沿 `absent_weight = 20` 扩训。

### 55. `.gitignore` 如果按目录整块屏蔽生成产物，容易把恢复关键摘要一起挡掉

现象：

- 当前公开仓库最初的 ignore 规则更偏“公开边界安全”，但对“误删后最大可恢复目标”还不够细：
  - `experiments/*`
  - `reports/eval/`
  这类整块忽略会把以下小文件一起挡掉：
  - `train_summary.json`
  - `eval_summary.json`
  - compare `summary.json`
  - blind pack `README.md`
  - `blind_key.json`
  - `sample_meta.json`

影响：

- 这些文件虽然是生成物，但通常：
  - 体积很小
  - 不含音频本体
  - 正是恢复实验配置、评估结论和 blind pack 组成的关键元数据
- 如果把它们和 checkpoint / wav 一起整体忽略，仓库会丢掉一整层可恢复信息。

处理：

- 已把 `.gitignore` 调整为“重资产继续本地，结构化摘要恢复可跟踪”：
  - `experiments/**/train_summary.json` 重新保持可跟踪
  - `reports/eval/**` 下的 `eval_summary.json`、`summary.json`、`README.md`、`blind_key.json`、`sample_meta.json` 重新保持可跟踪
- 仍继续留本地的内容包括：
  - 音频本体
  - checkpoint / `.pt`
  - synthetic 生成音频
  - 指向本地/非公开资产的 manifest

后续要求：

1. 以后审 ignore 规则时，不能只问“会不会泄露”，还要同时问“删盘后还能恢复到什么程度”。
2. 目录里若同时存在大文件和关键摘要，应优先用“忽略重资产 + 反向放行摘要”的写法，而不是整目录屏蔽。
3. 每次改完 `.gitignore`，至少补看一次 `git status --short --ignored`，确认：
   - 摘要文件没有被误伤
   - 重资产仍留在本地边界内

### 56. near-real trade-off 只看整包均值，很容易把“某个桶明显更好、另一个桶明显更差”的候选误判成中庸或稳定

现象：

- `analyze_listening_pack_tradeoff.py` 早期 summary 主要给：
  - 整包计数
  - 整包 decoded means
- 这足以看大方向，但不够直接回答：
  - `speech-only near-real` 是不是修好了
  - `target absent` 的收益到底落在哪个桶
  - 某个 candidate 的正收益是不是只是被 `music` 或 mixed bucket 拉起来

影响：

- 如果只看整包均值，很容易把：
  - `legacy_transient_leakguard_probe_v1`
  - `legacy_transient_leakguard_probe_v3_w0005`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1`
  这些分支之间真正的症状差异压平。
- 结果就是：
  - 某些“只在 music 桶更好”的版本会看起来像整体候选；
  - 某些“只在 target-absent speech 桶更强，但会压坏 raw-only”的版本，也会被误读成只是“整体更 residual-heavy”。

处理：

- 已给 `scripts/eval/analyze_listening_pack_tradeoff.py` 增加：
  - `scenario_groups`
  - `target_status_groups`
  - `interference_profile_groups`
  - `target_interference_bucket_groups`
- 已实际在 `v1 / v3_w0005 / v4_speechfocus_ft1 / v5_absentguard_ft1` 的 near-real blind 包上重跑。

当前新增结论：

1. `legacy_transient_leakguard_probe_v1` 的主要收益集中在：
   - `target_present__music`
   - `target_present__music_plus_speech`
2. 当前真正没修好的主缺口更明确地落在：
   - `target_present__speech`
   - `target_present__none`
3. `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 没有修好 `target_present__speech`
4. `legacy_transient_leakguard_probe_v5_absentguard_ft1` 的收益主要落在：
   - `target_absent__speech`
   但代价分散到：
   - `target_present__none`
   - `target_present__music`
   - `target_present__music_plus_speech`

后续要求：

1. 以后看 near-real trade-off，不能只盯整包均值。
2. objective-only 候选默认至少同时过这三类桶：
   - `target_present__speech`
   - `target_present__none`
   - `target_absent__speech`
3. 若某个版本只在 `music` 桶变强，但 `speech` 或 `raw-only` 桶继续输给 `legacy_stage2`，不能把它误判成“下一主候选”。

### 57. 即使已经按桶看 near-real，如果 gate 规则仍停留在自然语言里，后续还是会反复回到“这个候选整体看着还行”的模糊判断

现象：

- 在补了 `target_interference_bucket_groups` 之后，已经能更清楚地看见：
  - `v1` 的收益主要集中在带 `music` 的桶；
  - `v3 / v4` 主要卡在 `target_present__speech`；
  - `v5` 主要卡在 `target_present__speech` 与 `target_present__none`
- 但如果这些结论只写在日报里，后续仍很容易再次退回到：
  - 看整包 summary
  - 口头回忆“上次好像是这个桶有问题”
  - 再重新人工解释一次

影响：

- 同样的 near-real 放行条件会被反复人工重述。
- 很容易出现：
  - 某个分支已经明显卡在 `speech-only target-present`
  - 但因为整包上还有别的亮点，又被误当成“可以继续保留的主候选”

处理：

- 已新增：
  - `scripts/eval/gate_near_real_tradeoff.py`
- 当前已把以下三类桶正式固化为 hard gate：
  - `target_present__speech`
  - `target_present__none`
  - `target_absent__speech`
- 并已实际跑在：
  - `legacy_transient_leakguard_probe_v1`
  - `legacy_transient_leakguard_probe_v3_w0005`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1`

当前新增结论：

1. `v1`
   - fail:
     - `target_present__speech`
     - `target_present__none`
2. `v3_w0005`
   - fail:
     - `target_present__speech`
3. `v4_speechfocus_ft1`
   - fail:
     - `target_present__speech`
4. `v5_absentguard_ft1`
   - fail:
     - `target_present__speech`
     - `target_present__none`

后续要求：

1. 以后 near-real objective-only 候选，默认先过 `gate_near_real_tradeoff.py`，再谈是否值得继续保留。
2. 若一个候选已经明确 fail 某个关键桶，不能再只因为整包上某些局部亮点就把它当成“下一主候选”。
3. 后续若要改 gate，必须：
   - 先在文档里写清改动理由；
   - 再改脚本；
   - 不能只在对话里临时换标准。

### 58. 相对保守锚点通过 hard gate，不等于已经对主基线过关；`v7` 的正确定位是“替换 `v3`”，不是“替换 `stage2` 或 `v1`”

现象：

- 本轮新增 `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`。
- 它相对 `legacy_transient_leakguard_probe_v3_w0005` 已通过三类关键桶 hard gate：
  - `target_present__speech`
  - `target_present__none`
  - `target_absent__speech`
- 但相对 `legacy_stage2` 时，仍 fail：
  - `target_present__speech`

影响：

- 如果只看到：
  - “`v7` 已经通过 gate”
  而不区分它过的是谁的 gate，就很容易误判成：
  - `v7` 已经可以升成新主候选
  - 或者已经能替换 `legacy_stage2 / v1`
- 这会把“相对保守锚点的改进”误读成“相对主基线的放行”。

处理：

- 当前已把 `v7` 的定位明确写回日报与总览：
  - 它可以替换 `v3_w0005` 成为新的第二保留候选；
  - 但它还不能替换 `legacy_stage2`；
  - 也还不能替换 `legacy_transient_leakguard_probe_v1`。

后续要求：

1. 以后凡是说“某个 candidate 通过 gate”，必须同时写清：
   - baseline 是谁；
   - candidate 替换的是哪一层候选。
2. 若 candidate 只对“保守锚点”过关，但仍对主基线失守，就只能升级它在保守分支里的顺位，不能直接升成新的主候选。
3. 后续汇报候选顺位时，至少明确区分：
   - 默认主线
   - 当前 objective-only 最强候选
   - 保守升级锚点 / 副作用回收锚点

### 59. 同一个 listening-pack 输出目录，不能把 `export_ab_inference_from_manifest.py` 和下游分析脚本并行跑

现象：

- 本轮在导出 near-real blind 包时，曾把：
  - `scripts/eval/export_ab_inference_from_manifest.py`
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
  - `scripts/eval/analyze_listening_pack_transients.py`
  - `scripts/eval/analyze_listening_pack_tradeoff.py`
  - `scripts/eval/gate_near_real_tradeoff.py`
  针对同一个输出目录并行启动。
- 结果分析脚本在 export 还没写完样本目录和 `sample_meta.json` 时就开始读盘，出现过：
  - `num_samples = 0`
  - `summary.json` 缺失或不完整
  - gate 读取到半成品 summary

影响：

- 这类失败不是模型结论本身有问题，而是执行顺序错了。
- 如果不追根因，后续很容易把：
  - “分析结果为空”
  - “某脚本突然报缺文件”
  误判成数据包本身损坏或脚本逻辑回归。

处理：

- 当前已确认正确顺序应为：
  1. 先完整执行 export；
  2. 确认 blind 包样本与元数据已落盘；
  3. 再跑 bandwidth / transient / tradeoff / gate 分析。

后续要求：

1. 同一输出 pack 目录上，`export` 与下游分析默认串行，不并行。
2. 只有在 export 完成之后，多个纯分析脚本之间才允许并行。
3. 若再次看到：
   - `num_samples = 0`
   - 缺 `summary.json`
   - gate 读到空目录
   先检查是否是 export 和 analysis 抢同一个目录，而不是先怀疑模型或数据本身。

### 60. 即使已经把 near-real 失败压到单个 bucket，bucket 内也可能仍是几种互相冲突的子问题；`target_present__speech` 当前就是 3 条样本、3 种失败机制

现象：

- 在 hard gate 层面，当前 objective-only 主缺口已经收敛成：
  - `target_present__speech`
- 但进一步做样本级诊断后发现，这个 bucket 实际上只包含：
  - `near_real_0003`
  - `near_real_0004`
  - `near_real_0006`
- 且三条样本的失败主因并不一样：
  1. `near_real_0003`
     - 更像 over-suppression / residual-heavy + transient loss
  2. `near_real_0004`
     - 更像 speech leak trade-off
  3. `near_real_0006`
     - 更像 transient loss

影响：

- 如果只看到：
  - “当前只剩 `target_present__speech` 没过”
  就继续开一条统一的 loss / selector follow-up，很容易出现：
  - 修 `0006` 时把 `0004` 推回 leak；
  - 压 `0004` 时又把 `0003` 压成更 residual-heavy；
  - 最终 bucket 级 summary 继续原地打转。

处理：

- 当前已新增：
  - `scripts/eval/diagnose_near_real_bucket_failures.py`
- 并已把 `target_present__speech` 的样本级 failure signature 写回日报与总览。

后续要求：

1. 以后即使某个 near-real bucket 已经很小，也不要默认把它当成“单一机制问题”。
2. 在继续开下一条 objective-only follow-up 前，至少先确认：
   - 这个 bucket 内是不是其实由几条不同症状的样本组成。
3. 若 bucket 内症状已明显分裂，优先先做样本级诊断或可控映射，再决定：
   - 修哪一类
   - 先不修哪一类
4. 当前 `target_present__speech` 下，若只允许推进 1 条 follow-up，应优先选最单一的：
   - transient-only 子问题
   而不是继续对整个 bucket 做统一加权扫点。
