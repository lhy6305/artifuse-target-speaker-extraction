# 2026-03-17 Repo Evaluation Summary

## 目的

在当前物理环境暂时不支持继续做人耳听评的前提下，本文件用于把仓库现状压缩成一份可执行总结：

1. 哪些能力已经稳定落地；
2. 哪些模型路线已经可以明确淘汰；
3. 当前默认主线是什么；
4. 在无主观听评条件下，下一步还值得做什么，不值得做什么。

## 一、仓库整体成熟度

### 1. 数据与资产侧

当前已经稳定具备：

- curated target / reference / clean / hard / music / singing 数据桶；
- synthetic train / val 生成链路；
- near-real eval v1 资产与 manifest；
- blind A/B 导包；
- 本地 GUI 听评；
- 带宽与瞬态诊断脚本。

这意味着当前仓库已经不是“概念验证”阶段，而是：

- 能稳定复现实验；
- 能在 synthetic 与 near-real 两个层面做客观和主观闭环；
- 能把失败分支真实沉淀成反例，而不是只留在对话里。

### 2. 训练与评估侧

当前已经稳定具备：

- baseline train / eval；
- checkpoint 结构兼容；
- objective compare；
- A/B blind export；
- transient / bandwidth objective diagnostics；
- warm-start 小预算 probe 工作流。

当前最关键的工程事实是：

- 训练基础设施已经足够支持小步、低风险、可复现的 probe；
- 当前瓶颈已经不在“能不能跑”，而在“哪条方向值得继续消耗预算”。

## 二、当前主线判断

### 1. 默认主线

当前默认主线仍然是：

- `legacy stage2`
- checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`

原因很简单：

1. 它不是客观最强点，但它是当前综合最稳的点。
2. 多轮 synthetic / near-real / blind A/B 后，仓库里还没有任何候选能够稳定替代它。

### 2. 客观强但主观未过关的历史候选

这条线的典型代表是：

- `ref_film + stft0.5 + sisdr0.0005`

结论：

1. 客观上它一度是最强候选；
2. 但主线 blind A/B 和 near-real blind A/B 都没有通过；
3. 当前不再沿这条线继续扫近邻。

这条历史经验非常重要：

- 仓库已经明确验证过“客观更强不等于耳朵更喜欢”。

## 三、已淘汰路线

### 1. joint reverb realism

代表分支：

- `legacy_reverb_probe_v1`

结论：

- 可以直接视作反例；
- 不值得再扩大训练预算。

### 2. speech-only reverb realism

代表分支：

- `legacy_speechreverb_probe_v2`

结论：

1. 比 `v1` 更稳；
2. 但 near-real 人听没有形成优势；
3. 还暴露出“电话音 / 频带缺失 / 瞬态被削”的问题；
4. 当前不值得继续沿 reverb 概率方向加预算。

### 3. 全局 hard-recipe focus

结论：

- 已证伪“纯拉高难样本配比就能把难场景救回来”；
- 当前不再作为默认分布候选。

## 四、仍保留但未升主线的路线

### 1. clean_plus_music focused fine-tune 线

代表分支：

- `cpm_focus_ft1`
- `cpm_recipe_focus_v2_ft2`
- `ft3`

结论：

1. 客观上有过小幅收益；
2. 但主观上没有形成稳定可听优势；
3. 当前只保留历史参考价值，不再作为第一优先级。

### 2. transient-loss 全局版

代表分支：

- `legacy_transient_probe_v1`
- `legacy_transient_probe_v2`

结论：

1. 这条线不是空想；
2. 它确实能系统性压低 `transient_presence_l1`；
3. `legacy_transient_probe_v2` 还拿到了 very weak positive human signal：
   - `2` 次偏好
   - `0` 次失利
   - `8` 次平手
4. 但 trade-off 也很明确：
   - source retention 更好时，往往伴随更多 interference leak；
   - 默认全分布上仍伤 `target_only / hard_speech / hard_plus_music`。

当前状态：

- 值得保留；
- 但不足以升主线。

## 五、当前最值得继续的候选

### `legacy_transient_focus_probe_v4`

这是本轮继续探索后，当前仓库里最值得保留的 objective-only 候选。

配置：

- 基于 `legacy stage2` warm-start；
- `transient_weight=0.002`；
- transient loss 只作用于：
  - `target_clean_speech`
  - pattern 限于 `target_full / target_absent_head / target_absent_tail`

为什么它比全局版 `legacy_transient_probe_v2` 更值得保留：

1. 默认全分布代价更小：
   - `-0.314 dB -> -0.228 dB`
2. `target_clean_speech` 收益更强：
   - `+0.263 dB -> +0.315 dB`
3. `clean_speech + clean_plus_music` 合并后仍为正：
   - `+0.063 dB`
4. near-real 自动带宽收窄 side effect 更轻：
   - 全局版 `v2`: `4 / 0 / 6`
   - 局部版 `v4`: `2 / 0 / 8`

但它仍未解决的点也很明确：

1. near-real 自动瞬态缺失诊断还没有明显转正：
   - `legacy_transient_focus_probe_v4`: `7`
   - `legacy_stage2`: `1`
   - `tie`: `2`
2. 新增的 trade-off 诊断并没有帮它放行：
   - `better_source_retention`: `2`
   - `more_interference_leaky`: `7`
   - `better_retention_minus_leak`: `1`
   - 反向 `legacy_stage2`: `3`
3. 它还没有经过新一轮人工 blind 听评；
4. 因此仍不能升主线。

这里要特别修正一个口径：

- `legacy_transient_focus_probe_v4` 仍然是“训练侧 / synthetic 侧最值得保留的 selector-based 候选”；
- 但它已经不再能被概括为“当前整体上最值得继续的 objective-only 候选”。

原因是新的 near-real trade-off 脚本已经表明：

1. 它比 `legacy stage2` 平均多保住了一些 target：
   - `target_capture_db: -12.578 -> -9.779`
2. 但也平均多漏了更多 interference：
   - `interference_capture_db: -45.209 -> -41.562`
3. 最关键的 `retention_minus_leak_db` 反而变差：
   - `27.905 -> 26.665`
4. 并且从这个新脚本看，它在 near-real 上的 trade-off 还不如全局版 `legacy_transient_probe_v2` 收敛。

### `legacy_transient_leakguard_probe_v1`

这是在 `legacy_transient_focus_probe_v4` 基础上继续加了显式 leak guardrail 的 follow-up。

最关键的 synthetic 结果是：

1. 默认 val 相对 `legacy stage2`：
   - `avg_sisdr_delta_db = +0.850`
2. 相对 `legacy_transient_focus_probe_v4`：
   - `avg_sisdr_delta_db = +1.077`
3. 新增 leakage metric 也同步下降：
   - `legacy stage2: 0.0713`
   - `legacy_transient_focus_probe_v4: 0.0801`
   - `legacy_transient_leakguard_probe_v1: 0.0444`
4. 分 recipe 当前也基本全线转正。

这使它成为当前仓库里最强的 synthetic objective 候选。

但 near-real 自动结果仍然不能直接放行：

1. 带宽收窄：
   - `legacy_transient_leakguard_probe_v1 = 2`
   - `legacy_stage2 = 0`
   - `tie = 8`
2. 瞬态缺失：
   - `legacy_transient_leakguard_probe_v1 = 7`
   - `legacy_stage2 = 1`
   - `tie = 2`
3. trade-off 计数：
   - `better_source_retention = 2`
   - `legacy_stage2 = 3`
   - `more_interference_leaky = 5`
   - `legacy_stage2 = 2`
   - `better_retention_minus_leak = 2`
   - `legacy_stage2 = 3`
4. 不过它的均值 `retention_minus_leak_db` 已经高于 `legacy stage2`：
   - `27.905 -> 28.938`

当前判断：

1. 它已经明显优于 `legacy_transient_focus_probe_v4`；
2. 也是当前最值得保留的 objective-only 候选；
3. 但在没有人耳听评前，仍不能替代 `legacy stage2` 主线。

### `legacy_transient_leakguard_probe_v2_musiconly`

这是基于 `v1` 做的更窄 selector follow-up，只对 music-like recipe 施加 interference selector。

当前结论很明确：

1. 相对 `legacy stage2`，它不是纯失败：
   - `avg_sisdr_delta_db = +0.666`
   - `interference_projection_ratio = 0.0319`
2. 但相对 `legacy_transient_leakguard_probe_v1`，它已经大面积回退：
   - `avg_sisdr_delta_db = -0.184`
   - `regressed_count = 299`
3. 这说明 selector 缩得太窄之后，metric 会更像被“music-like leakage”单点牵着走。

当前定位：

- 不保留。

### `legacy_transient_leakguard_probe_v3_w0005`

这是在 `v1` 路线基础上，把 `interference_weight` 从 `0.01` 回收到 `0.005` 的更保守 follow-up。

关键观察：

1. synthetic 默认 val 相对 `legacy stage2` 仍为正：
   - `avg_sisdr_delta_db = +0.384`
2. 但相对 `legacy_transient_leakguard_probe_v1` 明显更弱：
   - `avg_sisdr_delta_db = -0.466`
3. near-real 自动 trade-off 上，它最有价值的新信号不是“更强”，而是：
   - `more_residual_heavy: 6 -> 1`
   - `residual_output_share: 0.679 -> 0.654`
4. 但它没有把关键风险一起压到更稳：
   - 带宽收窄：`2 -> 3`
   - `more_interference_leaky` 仍是 `5`
   - `retention_minus_leak_db: 28.938 -> 28.585`

当前定位：

1. 它不能替代 `legacy_transient_leakguard_probe_v1`。
2. 但它值得保留成一个“更保守、residual 更轻”的 side-effect 对照参考。

### `legacy_transient_leakguard_probe_v4_speechfocus_ft1`

这是在 `legacy_transient_leakguard_probe_v1` 基础上做的 speech-focused follow-up：

- warm-start 直接来自 `v1`
- `interference_weight` 保持 `0.01`
- 但 `interference_focus_recipes` 收窄到：
  - `target_clean_speech`
  - `target_hard_speech`

这条线最容易误读的地方在于：

1. synthetic 默认 val 上，它并不差；
2. 相反，它相对 `legacy stage2` 更强：
   - `avg_sisdr_delta_db = +0.970`
3. 相对 `legacy_transient_leakguard_probe_v1` 也仍有：
   - `avg_sisdr_delta_db = +0.120`

但把这些结果拆开看，结论就没那么乐观：

1. 它的收益更像集中在 speech-like recipe：
   - `target_clean_speech: +0.208 dB vs v1`
   - `target_hard_speech: +0.110 dB vs v1`
2. 同时它开始回退：
   - `target_only: -0.380 dB vs v1`
   - `target_singing_vocal: -0.301 dB vs v1`
   - `target_music: -0.023 dB vs v1`
3. near-real 自动结果里，它没有把最想修的 speech-only 回退点真正救回来：
   - `near_real_0003`: `delta_retention_minus_leak_db = -1.377`
   - `near_real_0004`: `delta_retention_minus_leak_db = -4.718`
4. 它在 near-real 上的关键 trade-off 也没有优于 `v1`：
   - `more_interference_leaky = 5`
   - `better_retention_minus_leak = 2`
   - `retention_minus_leak_db = 28.397`
   - 低于 `v1` 的 `28.938`

不过它也不是纯失败：

1. `residual_output_share` 从 `v1` 的 `0.679` 收到：
   - `0.664`
2. 说明“把 selector 收到 speech-only”这步，确实会改变副作用分布；
3. 只是这并没有自动转化成：
   - speech-only near-real 更稳
   - 或 leakage 更低

当前定位：

1. 它不应替代 `legacy_transient_leakguard_probe_v1`。
2. 也不应排到 `legacy_transient_leakguard_probe_v3_w0005` 前面。
3. 它最有价值的意义是：
   - 证明“单纯收窄到 speech-only selector”不是当前真正缺的那一环。

### `legacy_transient_leakguard_probe_v5_absentguard_ft1`

这是在 `legacy_transient_leakguard_probe_v1` 基础上做的 target-absent guardrail probe：

- warm-start 直接来自 `v1`
- 保留 `transient_weight = 0.002`
- 保留 `interference_weight = 0.01`
- 新增 `target_absent_intervals -> absent_interval_l1`
- `absent_weight = 20`

它的最关键价值不是“又找到了一版更强候选”，而是把一个机制问题验证清楚了：

1. target-absent 空窗段泄漏，确实可以被显式 loss 压下去；
2. 但如果权重给得太猛，模型会明显向 over-suppression / residual-heavy 方向走。

synthetic 上最直接的证据是：

1. 相对 `legacy_transient_leakguard_probe_v1`：
   - `absent_interval_l1: 0.00010835 -> 0.00001870`
2. 但默认 val 同时变成：
   - `avg_sisdr_delta_db = -0.662080`
3. 即使只看本轮 focused absent-guard recipes，也仍为：
   - `avg_sisdr_delta_db = -0.894569`

near-real 自动结果则更直接暴露了它的问题：

1. 带宽并没有形成新的大面积负面：
   - `tie = 9`
   - `legacy_transient_leakguard_probe_v5_absentguard_ft1 = 1`
2. 但 trade-off 解码后：
   - `better_source_retention = legacy_stage2 7`
   - `more_interference_leaky = legacy_stage2 8`
   - `more_residual_heavy = legacy_transient_leakguard_probe_v5_absentguard_ft1 7`
3. 关键回退样本包括：
   - `near_real_0003`
   - `near_real_0005`
   - `near_real_0007`
   - `near_real_0010`

当前定位：

1. 它不应替代 `legacy_transient_leakguard_probe_v1`。
2. 也不应排到 `legacy_transient_leakguard_probe_v3_w0005` 或 `v4_speechfocus_ft1` 前面。
3. 它最有价值的意义是：
   - 证明 `target_absent_intervals` 这条 guardrail 机制有效；
   - 同时证明“高权重 absent guardrail”不是当前可直接晋升主候选的解法。

## 六、当前仓库的路线优先级

### 第一层：当前默认主线

- `legacy stage2`

### 第二层：当前最值得保留的 objective-only 候选

- `legacy_transient_leakguard_probe_v1`

### 第三层：可保留历史参考，但不优先继续

- `legacy_transient_leakguard_probe_v3_w0005`
- `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
- `legacy_transient_leakguard_probe_v5_absentguard_ft1`
- `legacy_transient_focus_probe_v4`
- `legacy_transient_probe_v2`
- `cpm_recipe_focus_v2_ft2`

### 已阶段性停止继续投入的路线

- `ref_film_sisdr0005` 主线替换线
- `legacy_reverb_probe_v1`
- `legacy_speechreverb_probe_v2`
- pure `hard_recipe_focus`
- `legacy_transient_leakguard_probe_v2_musiconly`

## 七、在“无听评条件”下的下一步原则

当前最重要的不是“继续开更多近邻实验”，而是控制实验密度。

建议遵守以下原则：

1. 不再继续扫：
   - reverb 概率
   - `ref_film` 近邻结构
   - 大量 transient weight 邻点
2. 只继续做：
   - 带明确 leakage guardrail 的 very small objective-only 微调
   - 或更偏诊断性的分析脚本
3. 每开一版新分支，都必须同时看：
   - 默认全分布代价
   - `target_clean_speech` 收益
   - `target_only / hard_speech` guardrail 代价
   - near-real 自动带宽 / 瞬态诊断
   - near-real `tradeoff_analysis`
4. 不要把“selector 收到 speech-only 之后 synthetic speech recipe 继续提分”直接等价理解成：
   - speech-only near-real 已经更稳
5. 也不要把 `absent_interval_l1` 单指标明显变好，直接等价理解成：
   - target-absent near-real 已经更稳
   - 或 source retention 仍然安全

## 八、当前最合理的后续探索方向

在暂时不能做人耳听评的前提下，当前最合理的继续探索方向只有两类。

### 方向 A：继续沿 selector-based transient loss 做“带 leakage guardrail”的微调

目标：

- 看能不能在不继续伤 guardrail 的前提下，把 near-real 的 leak 问题显式压住。

优先尝试：

1. 以 `legacy_transient_leakguard_probe_v1` 为当前落脚点；
2. 把 `legacy_transient_leakguard_probe_v3_w0005` 视为“更保守 residual 版本”的对照锚点，而不是新的主基座；
3. 把 `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 只保留为诊断性参考，不再继续围绕它做 selector 近邻扫点；
4. 不再单扫 transient selector，而是优先修：
   - speech-like interference 的 residual / leak 回退点
   - 特别是 near-real `0003 / 0004` 这类 speech-only 场景；
5. 把是否继续保留候选的判断，改为看：
   - `retention_minus_leak`
   - 而不只是 `target_capture` 或 synthetic focus gain。

不建议做的：

- 再回到全局 transient loss；
- 再把 `clean_plus_music` 整体重新纳入 selector；
- 再单独围绕 `v4` 做没有 leak 约束的近邻扫点。

### 方向 B：做更细的“source retention vs interference leak”自动诊断

当前 transient-loss 的核心 trade-off 已经很明确：

- 更好 source retention
- 对应更高 interference leak 风险

因此下一个更有价值的 objective-only 工具，不一定是新训练分支，而可能是：

- 一个专门量化 `source retention` 与 `interference leak` trade-off 的分析脚本；
- 用来解释为什么某些样本会在主观上出现“保得更多，但也漏得更多”的平衡点。

这条线本轮已经完成第一版落地：

- `scripts/eval/analyze_listening_pack_tradeoff.py`

当前它给出的最关键新结论是：

1. `legacy_transient_probe_v2`：
   - `better_source_retention = 4`
   - `more_interference_leaky = 4`
   - `better_retention_minus_leak = 2`
   - `legacy_stage2 = 2`
2. `legacy_transient_focus_probe_v4`：
   - `better_source_retention = 2`
   - `more_interference_leaky = 7`
   - `better_retention_minus_leak = 1`
   - `legacy_stage2 = 3`
3. 新增 `legacy_transient_leakguard_probe_v1` 之后，当前更准确的结论变成：
   - leak guardrail 这条方向本身是有效的；
   - 但要进一步解决的是 near-real speech-only 场景里的 residual / leak 回退；
   - 而不是回到“只缩 selector”的旧路线。
4. 新增 `legacy_transient_leakguard_probe_v5_absentguard_ft1` 之后，当前又多确认了一件事：
   - target-absent guardrail 这条机制也成立；
   - 但强权重版本会把模型过度推向 residual-heavy；
   - 因此若继续，只能沿更保守的小步版本往下试。

## 九、当前结论

如果只用一句话总结当前仓库状态：

- 仓库已经从“找主线”进入“主线已稳，但 realism / 瞬态保真方向只允许做极小步、强约束的 probe”阶段。

如果只用一句话总结当前最值得继续的分支：

- 在无听评条件下，当前最值得继续的小步实验基座仍是 `legacy_transient_leakguard_probe_v1`，`v3_w0005` 只作为更保守 residual 对照保留，`v4_speechfocus_ft1` 只作为“speech-only selector 不是根因解”的诊断参考，`v5_absentguard_ft1` 只作为“高权重 target-absent guardrail 会过抑制”的机制参考；下一步应继续修 speech-only / target-absent near-real 回退，但只能沿更保守的 leak / absent guardrail 小步推进，而不是继续扫 music-only selector、speech-only selector 或强约束 absent weight 近邻。
