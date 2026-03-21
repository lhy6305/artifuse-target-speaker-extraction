# 踩坑记录 历史归档 61-70

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `61-70`

## 2026-03-16

### 61. broad synthetic regrouping 可能会把 near-real speech-only 候选排错顺序；如果 proxy 没有把真实 source family 和失败锚点带进去，就可能继续偏爱 `v1` 这类“更强但不更近真实”的版本

现象：

- 在完成 `target_present__speech` 的样本级诊断后，已经明确：
  - `near_real_0003`
  - `near_real_0004`
  - `near_real_0006`
  才是当前真正卡住的 speech-only target-present 样本。
- 早一轮 broad synthetic speech proxy 分析里：
  - `v1` 在 `speech_full_overlap_like`
  - `speech_leak_risk_proxy`
  - `speech_transient_proxy`
  - `speech_compound_proxy`
  上都仍优于 `v7`
- 但新补的 near-real-aligned 微型 probe：
  - 直接锚定 `0003 / 0004 / 0006`
  - 只使用真实近源 `friend_raw / guodegang_raw` 语音族
  之后，排序反过来了：
  - 相对 `legacy_stage2`
    - `v1 = -1.559718 dB`
    - `v7 = -0.629166 dB`
  - 相对 `v1`
    - `v7 = +0.930552 dB`
    - `24 / 24` 样本全胜

影响：

- 这说明“按 synthetic 默认 metadata 重新分桶”还不够接近当前 near-real speech bucket 的真实难点。
- 如果继续只依赖 broad proxy 排序，很容易误判成：
  - `v1` 仍是 speech-only follow-up 的更好基座
- 但更近真实的 probe 已经表明：
  - `v7` 才是更稳、更接近 near-real 排序的起点。

处理：

- 已新增：
  - `scripts/data/build_near_real_speech_probe_manifest.py`
  - `scripts/eval/analyze_near_real_speech_probe.py`
- 已生成并实跑：
  - `data/probes/near_real_speech_probe_v1_manifest.jsonl`
  - `stage2 vs v1`
  - `stage2 vs v7`
  - `v1 vs v7`

后续要求：

1. 以后只要当前 near-real 主缺口已经收敛到少数真实锚点，优先先补“带真实 source family 的微型 probe”，不要只靠 broad synthetic regrouping 排下一步候选。
2. 若 broad proxy 与 near-real-aligned micro probe 排序冲突，默认以更接近真实锚点的 micro probe 为准。
3. 当前 speech-only objective follow-up 的默认基座应改成：
   - `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
   而不是回到 `v1`。
4. 下一步若继续开新实验，默认只修：
   - `friend_raw`
   - `near_real_0003 / 0004` 型
   同时把 `guodegang_raw / 0006` 型当前已拿回的收益当 guardrail。

### 62. 只盯 `friend_raw / 0003 / 0004` 做 focused fine-tune，虽然能把 speech micro-probe 往前推，但很容易同步回吐 `guodegang / 0006` 和 broad default val；后续必须双侧设 guardrail

现象：

- 本轮基于：
  - `target_hard_speech + target_full + high-overlap`
  - `target_clean_speech + target_full + mid-gain + high-overlap`
  做了 very small focused fine-tune：
  - `legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1`
- 相对 `v7`，它在 near-real speech micro probe 上明显更好：
  - overall `+0.392748 dB`
  - `near_real_0003 = +0.421242`
  - `near_real_0004 = +0.692135`
- 但同时也出现了两类回吐：
  - default synthetic val 相对 `v7 = -0.191305 dB`
  - `near_real_0006` micro probe 相对 `v7 = -0.099073 dB`

影响：

- 这说明“对准 friend speech overlap 去修”是有效的，但它不会自动兼容：
  - `guodegang_raw / transient_like`
  - broad default synthetic coverage
- 如果后续继续只按 `0003 / 0004` 定向加力，很容易把：
  - `0006`
  - 或默认 val
  当作隐性代价慢慢吃掉。

处理：

- 当前已把 `v8` 记录为：
  - speech-bucket-focused 线上新的保留候选
- 但还未把它升成 broad objective-only 的无条件替代版。

后续要求：

1. 以后任何 `friend_raw` focused follow-up，至少同时看三层 guardrail：
   - `friend_raw / 0003 / 0004` 是否继续改善
   - `guodegang_raw / 0006` 是否回吐
   - default synthetic val 是否继续系统性回退
2. 不能只因为 speech micro-probe 更强，就直接把 focused 版本当成下一默认候选。
3. 当前下一条 follow-up 如果继续开，应优先做：
   - 在保住 `v8` 对 `0003 / 0004` 改善的前提下
   - 单独补 `0006` 的 transient-like guardrail
   而不是继续扩大 friend-only focused 训练预算。

### 63. `export_ab_inference_from_manifest.py` 的非 blind 导出文件命名，不兼容当前 near-real 自动分析脚本；要走 bandwidth / transient / tradeoff 链，仍应使用 blind 包

现象：

- 本轮尝试直接对 near-real manifest 做非 blind 导出：
  - `export_ab_inference_from_manifest.py`
- 导出目录内生成的是：
  - `legacy_stage2.wav`
  - `legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1.wav`
- 但现有自动分析脚本默认读取的是：
  - `candidate_a.wav`
  - `candidate_b.wav`

影响：

- 如果直接把非 blind 导出目录喂给：
  - `analyze_listening_pack_bandwidth.py`
  - `analyze_listening_pack_transients.py`
  - `analyze_listening_pack_tradeoff.py`
  会在读盘阶段直接报找不到或打不开 `candidate_a.wav / candidate_b.wav`。

处理：

- 本轮已改用：
  - `--blind`
  的导出方式重跑 near-real 包
- 随后 bandwidth / transient / tradeoff / gate / bucket diagnosis 链均恢复正常。

后续要求：

1. 只要目标是走现有 near-real 自动分析链，默认使用 blind 导出目录。
2. 如果未来需要支持非 blind 自动分析，应先统一命名约定或补兼容逻辑，不能假设现有分析脚本会自动识别 label-named wav。
3. 遇到这类“导出成功但分析读不到 wav”的问题，先检查文件命名约定，不要先怀疑音频本体损坏。

### 64. `speech-focused follow-up` 的 branch-local 进步，必须和 broad objective-only 升级分开判定；否则会把 `v7/v8` 这类局部修复线误当成总冠军

现象：

- `v7` 相对 `v1` 在 near-real speech micro-probe 上更强
- `v8` 相对 `v7` 在 `0003 / 0004` 也继续改善
- 但这两类“speech-focused 改进”并不自动等价于：
  - broad default synthetic val 也足够保住
  - 或 broad objective-only 排位已经完成替换

影响：

- 如果只盯着 micro-probe 或 `target_present__speech` 一条局部线索，会高估 branch-local follow-up 的全局价值。
- 这会导致：
  - 误把 `v7` 当成对 `v1` 的 broad keeper 升级
  - 或误把 `v8` 当成已经足够替代当前全部保留候选

处理：

- 本轮已新增：
  - `scripts/eval/gate_speech_probe_followup.py`
- 它明确要求：
  - 共享 `stage2` 基线
  - `0003 / 0004` 要继续改善
  - `0006` 只能在允许阈值内轻微回退
  - default val 不能回吐过多
  - near-real hard gate fail bucket 不能扩张

后续要求：

1. 以后所有 `v8` 之后的 speech-focused follow-up，先过这套 branch-local gate，再谈是否值得继续推进。
2. broad keeper 排位仍应单独判断，不能用 branch-local gate 结果直接替代。
3. “局部 speech 桶更强”和“全局更适合替主线”必须继续分开写结论。

### 65. 用 PowerShell `Set-Content` 或默认文本拼接 JSONL 时，容易写入 UTF-8 BOM，进而让 dataset 读盘直接报错

现象：

- 本轮在合并 focused manifest JSONL 时，最初直接用 PowerShell 文本写回。
- 生成文件头部带了 UTF-8 BOM。
- `SyntheticTSEDataset` 读这些 manifest 时，会在首行 JSON 解码阶段报：
  - `json.decoder.JSONDecodeError: Unexpected UTF-8 BOM`

影响：

- 表面上看像是某条 manifest 行坏了。
- 实际上是整个 JSONL 文件编码带 BOM，导致训练入口在最开始就失败。

处理：

- 本轮已改成显式使用无 BOM 的 UTF-8 写回组合 manifest。
- 问题随后消失，训练恢复正常。

后续要求：

1. 以后生成或拼接 JSONL manifest，默认使用 `utf-8` 无 BOM。
2. 遇到 `Unexpected UTF-8 BOM` 时，先查文件编码，不要先怀疑样本内容。
3. 若继续用 PowerShell 生成 JSONL，必须显式控制编码行为，不能依赖默认文本输出。

### 66. `hard/full-overlap/transient` synthetic proxy 目前会把 `friend` 侧修得更顺，却会系统性误伤真正想补的 `guodegang 0006`

现象：

- 本轮从 `v8` 出发，构造了一个看似合理的 `0006` 代理方向：
  - `target_hard_speech`
  - `target_full`
  - `overlap >= 0.9`
  - target transient 指标较高
- 再把这批样本叠加到 `v8` 的 friend-focused combo 上，训练出：
  - `v9`

影响：

- `v9` 在 synthetic default 上只小幅回吐：
  - `v8 -> v9 = -0.046169 dB`
- 但 near-real speech micro probe 上却出现反向结果：
  - `friend_raw = +0.073949 dB`
  - `0003 = +0.064120 dB`
  - `0004 = +0.083778 dB`
  - `guodegang_raw / 0006 = -0.285347 dB`
- 也就是这条 proxy 并没有把训练信号导向 `0006 recovery`，反而继续把模型往 friend 侧推。

处理：

- 本轮已用：
  - `scripts/eval/gate_speech_probe_followup.py --max-anchor-0006-regression-db 0.0`
  对 `v8 -> v9` 做严格预筛
- 结果直接 `FAIL`：
  - `speech_probe_overall_floor`
  - `anchor_0006_regression_floor`

后续要求：

1. 当前不要再沿这条 `hard/full-overlap/transient` synthetic proxy 继续开近邻训练。
2. 若要继续补 `0006`，应先重做 objective proxy，而不是再复用同类 manifest。
3. 以后所有声称“在补 `0006`”的 follow-up，都必须先看：
   - `guodegang_raw`
   - `near_real_0006`
   不能只看 broad speech proxy 是否转正。

### 67. `0006` 的 guardrail 不能继续混在 broad speech probe 里看整体均值；必须拆成独立 `guodegang` 子 probe，否则会被 `friend` 侧改善掩盖

现象：

- broad near-real speech probe v1 里：
  - `friend_raw = 18` 条
  - `guodegang_raw = 6` 条
- 当 follow-up 同时出现：
  - `friend` 侧略好
  - `guodegang 0006` 侧明显变差
  时，overall 只会表现成很小的正负波动。

影响：

- 如果只看 broad speech probe overall，很容易误判成：
  - “只是轻微波动，还能继续试”
- 实际上像 `v9` 这种情况，已经是：
  - `0006` 被系统性推坏
  - 但 `friend` 侧改善把整体均值部分抵消了

处理：

- 本轮已新增：
  - `data/probes/near_real_guodegang_transient_probe_v1_manifest.jsonl`
  - `scripts/eval/gate_probe_subset_guardrail.py`
- 并已确认：
  - `v8 -> v9` 在这条子 probe 上 `6 / 6` 全 regression

后续要求：

1. 今后所有“补 `0006`”的实验，必须单独看 `guodegang` 子 probe，不得只看 broad speech probe overall。
2. broad speech probe 继续保留，但它负责看 branch 的整体方向，不再承担 `0006` 专用 guardrail 职责。
3. 若 focused follow-up 在 `guodegang` 子 probe 上不过线，应直接止损，不再进入下一轮训练扩展。

### 68. `0006` 的 synthetic 代理若继续凭直觉往 `hard speech / friend overlap` 上靠，会把 proxy 重建方向带偏；当前最接近真实排序的反而是 `clean speech + high-target-transient`

现象：

- 在 `v9` 失败之后，本轮没有继续开训练，而是先用：
  - `scripts/eval/search_synthetic_proxy_candidates.py`
  在 default synthetic speech rows 上搜索能复现
  - `v7 > v8 > v9`
  的 metadata-defined 子集。
- 搜索得到的 top order-pass 候选，没有落在旧的：
  - `target_hard_speech`
  - `target_full`
  - `overlap >= 0.9`
  - transient-rich
  方向。
- 当前最稳定复现 `guodegang / 0006` 排序的，反而是：
  - `target_clean_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `overlap >= 0.75`
  - `speech_interference_clean_pool`
  - `target_transient_presence_minus_mid_db_mean >= -11.5350723`

影响：

- 这说明“`0006` 更像 hard speech / friend-like overlap”是一个错误直觉。
- 如果后续还沿旧方向继续构造 focused manifest，很容易再次出现：
  - friend 侧看起来更顺
  - 但真正的 `guodegang / 0006` 继续回退
- 也就是说，问题不只是权重没调对，而是 proxy 映射本身就在把训练信号导向错误子空间。

处理：

- 本轮已物化：
  - `data/synthetic/train_manifest_guodegang_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_guodegang_proxy_v1.jsonl`
- 并已确认它们在独立 compare 上可复现：
  - `v7 > v8 > v9`

后续要求：

1. 若继续做 `0006` 相关 objective-only follow-up，默认先从 `guodegang_proxy_v1` 出发，而不是回到 `hard_transient_focus_v1_any`。
2. 但 `guodegang_proxy_v1` 仍只是 synthetic 预筛，不替代：
   - `near_real_guodegang_transient_probe_v1`
3. 今后任何声称“补回了 `0006`”的版本，都至少要同时说明：
   - 在 `guodegang_proxy_v1` 上是否仍保持 `v7 > v8 > v9` 方向的一致性
   - 在 `near_real_guodegang_transient_probe_v1` 上是否真的不过线或转正

### 69. 即使 synthetic proxy 已经比旧方向更接近真实，也不代表它单独拿来做 focused fine-tune 就足够；`v10` 证明了“单边补 `guodegang`”仍会把真实 `0006` 推坏

现象：

- 本轮基于：
  - `train_manifest_guodegang_proxy_v1.jsonl`
  - `val_manifest_guodegang_proxy_v1.jsonl`
  从 `v8` warm-start 做了：
  - `legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1`
- `v10` 在 synthetic 上看起来并不差：
  - 相对 `v8`
    - default: `-0.031839 dB`
    - `guodegang_proxy_v1`: `+0.480623 dB`
- broad near-real speech probe 相对 `v8` 也仍是小幅正增益：
  - overall: `+0.080006 dB`
  - `0003 = +0.280721 dB`
  - `0004 = +0.211316 dB`

影响：

- 如果只看：
  - default
  - broad speech probe overall
  很容易误判成：
  - `v10` 基本可留
- 但真正关键的：
  - `near_real_guodegang_transient_probe_v1`
  上，`v10` 相对 `v8` 是：
  - `-0.418033 dB`
  - `6 / 6` 样本全部 regression
- 也就是：
  - 新 proxy 虽然比旧的更像
  - 但它单独拿来做 focused 训练，仍不足以约束真实 `0006`

处理：

- 本轮已确认：
  - `gate_speech_probe_followup.py` 失败项只剩：
    - `anchor_0006_regression_floor`
  - `gate_probe_subset_guardrail.py` 在 `guodegang` 子 probe 上直接全线失败
- 同时又补做了一次：
  - `v8 > v10`
  synthetic 搜索

后续要求：

1. 以后不要把“proxy 更接近真实”误解为“只用这条 proxy 单边微调就够了”。
2. 当前更合理的 follow-up 设计应改成双锚点：
   - `guodegang_proxy_v1` 作为正向 focused 信号
   - `friend_hard_negative_segments / hard full-overlap` 作为反向 guardrail
3. 在真实 `0006` guardrail 没过之前，不能因为：
   - default 没炸
   - `0003 / 0004` 更好
   就把候选继续往下推进。

### 70. 即使已经把“正向 `guodegang` proxy + 反向 friend hard-overlap guardrail”同时放进 one-shot dual-anchor manifest，也不代表真实 `0006` 就会自动被保住；`v11` 证明这种平衡会先继续偏向 friend 侧

现象：

- 本轮基于：
  - `guodegang_proxy_v1`
  - `target_hard_speech + target_full + speech_interference_hard_pool(friend_hard_negative_segments)`
  直接拼出：
  - `train_manifest_v11_dualanchor_v1.jsonl = 136`
  - `val_manifest_v11_dualanchor_v1.jsonl = 49`
- 再从 `v8` warm-start 训练出：
  - `legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1`
- `v11` 在 synthetic 上看起来比 `v10` 还更像成功：
  - 相对 `v8`
    - default: `-0.079973 dB`
    - `guodegang_proxy_v1`: `+0.795423 dB`
- broad near-real speech micro probe 相对 `v8` 也仍是小幅正增益：
  - overall: `+0.025061 dB`
  - `0003 = +0.260091 dB`
  - `0004 = +0.241347 dB`

影响：

- 如果只看：
  - default
  - synthetic `guodegang_proxy_v1`
  - broad speech probe overall
  会很容易误判成：
  - “dual-anchor 已经开始起效”
- 但真正关键的：
  - `near_real_guodegang_transient_probe_v1`
  上，`v11` 相对 `v8` 是：
  - `-0.651915 dB`
  - `6 / 6` 样本全部 regression
- 也就是：
  - friend 侧确实继续变好
  - 可真实 `0006` 仍被系统性挤压
- 更细看还会发现：
  - `guodegang_absent_480s` 相对 `legacy_stage2` 是正增益
  - `guodegang_anchor_120s` 却变成负增益
  说明当前 `0006` 内部可能已经不是单一子问题

处理：

- 本轮已确认：
  - `gate_speech_probe_followup.py` 失败项仍是：
    - `anchor_0006_regression_floor`
  - `gate_probe_subset_guardrail.py` 在 focused `guodegang` 子 probe 上仍直接失败：
    - `overall_floor`
    - `family__guodegang_raw`
    - `anchor__near_real_0006`
- 同时已把这一轮结论写回：
  - `reports/daily/2026-03-18_v11_v8_dualanchor_ft1.md`
  - `docs/01_project_overview_and_plan.md`

后续要求：

1. 以后不要把“正向 proxy 和反向 guardrail 都加进 manifest 了”误读成“真实双锚点已经被平衡住”。
2. 当前不要继续沿 `v11` 同配方扩大训练预算。
3. 若继续补 `0006`，默认先拆开看：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
   不要再把它们当成同一个 objective proxy 目标。
4. 在真实 `0006` guardrail 没过之前，不能因为：
   - `0003 / 0004` 更强
   - broad speech probe overall 仍为正
   就把 dual-anchor 分支继续往下推进。
