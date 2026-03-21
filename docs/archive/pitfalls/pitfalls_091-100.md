# 踩坑记录 历史归档 91-100

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `91-100`

## 2026-03-16

### 91. 即使把 `0004-like speech-leak` 再重写成 `high similarity + low target transient + low interference transient` 的 mixed-pattern exact family，也不代表当前 interference-extra objective 已经足够；`v30` 证明 sample family 更像了，训练方向仍然可能不对

现象：

- 本轮在 `samplewise-order-pass` 搜索里新增：
  - `interference_transient_presence_minus_mid_db_mean`
  - `target_interference_logspec_cosine`
- 因而首次搜到一条不同于 `v23 / v29` 的新 family：
  - clean pool
  - higher gain
  - higher similarity
  - lower target transient
  - lower interference transient
  - `target_full + absent_head + absent_tail`
- 基于这条 family 落盘：
  - train exact `7`
  - val exact `3`
- 并开出：
  - `v30 = legacy_transient_leakguard_probe_v30_v19_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_ft1`

处理：

- 训练侧继续保留 `v19` 基座；
- 新 family 挂到：
  - `interference_extra_focus_sample_ids`
- 这次 selector 命中已明确增加到：
  - train interference `58 / 97`
  - val interference `21 / 29`

结果：

- 相对 `v19`：
  - default `+0.015689 dB`
  - `v30 exact proxy = -0.141952 dB`
  - near-real speech probe overall `-0.053396 dB`
  - near-real `speech_leak_like (0004) = -0.035911 dB`
- 新 exact family 的 full 行：
  - `val_000075`
  - 仍明显回退 `-0.340267 dB`

影响：

- 以后不能把：
  - “搜索结果终于更像 speech-leak 了”
  直接等价成：
  - “当前 objective 已经接近正确”
- `v30` 更准确的解释应写成：
  - sample family 的确比旧 `v23 / v29` 更换了一层语义；
  - 但当前 interference-extra objective / guardrail 形式仍不足以把这类样本训练成正收益。

后续要求：

1. 不继续围绕这条 `v30` family 扫权重、epoch、lr。
2. 后续若还要补 `0004-like speech-leak`，优先改：
   - objective 形式
   - leak-specific guardrail
   - 或更明确的 branch-local loss 归属
3. 不再把“又找到一条更像的 exact family”误写成：
   - objective 已基本闭环

### 92. 即使把 interference objective 从整段预测投影比改成残差投影比，也不代表 `0004-like speech-leak` 已经被补正；`v31` 证明这类 mode swap 只能部分缩小 exact proxy 回退，还可能把代价转移到 default 或其他锚点

现象：

- 本轮 `v31` 保持：
  - `v30` exact family
  - `v19` 基座
  - selector 命中边界
  全部不变；
- 唯一改动是：
  - `interference_loss_mode = residual_projection_ratio`
- 结果相对 `v19`：
  - default `-0.011286 dB`
  - exact proxy `-0.082113 dB`
  - near-real overall `-0.054149 dB`
- 结果相对 `v30`：
  - exact proxy `+0.059839 dB`
  - near-real overall `-0.000753 dB`

处理：

- 工程上保留：
  - `interference_projection_loss(..., mode=...)`
  - `--loss-interference-mode`
- 新增模式：
  - `residual_projection_ratio`
  只看 `prediction - target` 里的 interference-aligned 残差，而不再直接约束整段预测。

结果：

- `v31` 的确把 `v30` exact family 三条都往正方向推了一点；
- 但：
  - `v19` 基线仍未被超过；
  - `near_real_0004` 仍为负；
  - `guodegang / 0006` 还出现了新的回吐。

影响：

- 以后不能把：
  - “projection target 换对了”
  直接等价成：
  - “speech-leak objective 已经基本成形”
- 更准确的理解应写成：
  - residual-projection 只是一个更像样的 primitive；
  - 但若没有额外 leak-specific guardrail 或分侧保护，
  - 它仍可能只是把代价从 exact speech-leak proxy 挪到 default / 其他锚点。

后续要求：

1. 不继续围绕 `v31` 直接扫权重、epoch、lr。
2. 后续若继续补 `0004-like speech-leak`，优先试：
   - leak-specific guardrail
   - friend-side 与 `guodegang / 0006` 的解耦保护
   - 或只在 speech-leak exact family 上叠加更局部的 residual constraint
3. 不再把“objective mode 换成 residual projection 后 exact proxy 变好了一些”误写成：
   - 整条路线已经可保留

### 93. 即使把 residual objective 局部化到 `interference_extra`，也不代表 `0004-like speech-leak` 已经基本补正；`v32 / v33` 证明“全局替换过宽”只是问题的一部分，extra weight 也不是当前主瓶颈

现象：

- `v32` 首次把：
  - base interference
  - interference_extra
  做成了真正 branch-local 的不同 objective；
- 其中：
  - base interference 继续保留 `prediction_projection_ratio`
  - 只有 `interference_extra` exact speech-leak family 改成 `residual_projection_ratio`
- `v32` 相对 `v31` 已明显更稳：
  - default `+0.030320 dB`
  - near-real overall `+0.003684 dB`
- 但相对 `v19` 仍然：
  - exact proxy `-0.121204 dB`
  - near-real `speech_leak_like (0004) = -0.041680 dB`
- 后续 `v33` 再把：
  - `interference_extra_weight = 0.0075 -> 0.015`
  也没有带来新的结构性改善。

处理：

- 工程上保留：
  - branch-local selector weights
  - `interference_extra_weight`
  - `interference_extra_loss_mode`
  - `interference_extra_projection_ratio`
- 并通过 `v32 / v33` 明确验证：
  - localized residual extra
  - 以及更高 extra weight
  的真实边界。

结果：

- `v32` 证明：
  - “全局 residual 替换过宽”这件事确实存在；
  - 局部化后，default / near-real 稳定性明显优于 `v31`
- `v33` 又证明：
  - 当前瓶颈不在 extra branch 的 weight 还太小；
  - 至少在这一级额外放大下，exact / near-real 形态几乎不动。

影响：

- 以后不能把：
  - “把 residual objective 局部化到 exact family”
  直接等价成：
  - “speech-leak 这条线已经只差一点 weight”
- 更准确的理解应改写为：
  - 过宽的全局 interference objective 确实是问题之一；
  - 但即便修掉这点，`0004-like speech-leak` 仍需要更具体的 guardrail / 解耦约束；
  - 简单继续推 extra weight，大概率只是低价值重复试验。

后续要求：

1. 不继续围绕 `v32 / v33` 扫更多 extra weight。
2. 保留 branch-local interference-extra split 这套能力，作为后续实验底座。
3. 后续若继续补 `0004-like speech-leak`，优先试：
   - 只在 speech-leak exact family 上触发的 leak-specific guardrail
   - friend-side 与 `guodegang / 0006` 的显式解耦保护
   - 或更贴近“只压泄漏残差、不动目标保留”的局部约束

### 94. 即使 exact speech-leak family 已经被推到正增益，也不代表 near-real 就会一起转正；`v34` 证明 weighted SI-SDR guard 很容易把这条线推成 exact-family overfit

现象：

- `v34` 在 `v32` 基础上给 `interference_extra` exact family 叠加：
  - `interference_extra_guard_sisdr_weight = 0.0002`
- 结果相对 `v19`：
  - default `+0.058461 dB`
  - exact proxy `+0.026174 dB`
  - near-real overall `-0.071357 dB`
  - `guodegang / 0006 = -0.122081 dB`

处理：

- 工程上保留：
  - `weighted_sisdr_loss(...)`
  - `interference_extra_guard_sisdr_weight`
- 并只把这条 guardrail 作用于：
  - exact speech-leak family

结果：

- exact proxy 的确第一次转正；
- 但 near-real 同时更差，尤其：
  - `guodegang_anchor_120s`
  - `guodegang_absent_480s`
  都明显回退。

影响：

- 以后不能把：
  - “exact family 已转正”
  直接等价成：
  - “真实 speech-leak 已被修正”
- 更准确的理解应写成：
  - 当前这类 exact-family weighted guard 很容易把模型推向 synthetic exact overfit，
  - 而不是真正提升 near-real。

后续要求：

1. 不继续沿这条 exact-family sisdr guard 直接扫权重。
2. 后续若要继续保留这类 guard，必须同时通过：
   - near-real speech probe
   - 尤其 `guodegang / 0006` 子门

### 95. `guodegang_anchor_proxy_v1` 当前不能直接当作 friend-side speech-leak 线的 decoupling protection；`v35` 证明 synthetic anchor 更强，真实 `guodegang_anchor_120s` 反而可能更差

现象：

- 本轮 `v35` 把：
  - `guodegang_anchor_proxy_v1`
  并入 `v34` 的训练集，
  并通过：
  - `transient_extra_focus_sample_ids = guodegang_anchor_proxy_v1`
  试图给 `0006` 加一条显式保护。
- 结果相对 `v19`：
  - default `+0.061993 dB`
  - exact proxy `+0.152425 dB`
  - near-real overall `-0.078793 dB`
  - `near_real_guodegang_anchor_probe_v1 = -0.352486 dB`

处理：

- 生成了：
  - `sample_ids_guodegang_anchor_proxy_v1_{train,val,all}.txt`
  - `train/val_manifest_v35_v19_plus_friend_reverse_guardrail_proxy_v8_plus_guodegang_anchor_proxy_v1.jsonl`
- 并把它们真实并入训练，而不是只停留在文档假设里。

结果：

- synthetic friend-side exact proxy 继续变强；
- 但真实 `guodegang_anchor_120s` 不但没被保护住，
  反而比 `v34` 还更差。

影响：

- 以后不能把：
  - “某个 synthetic `guodegang_anchor_proxy` 在训练里被显式照顾了”
  直接等价成：
  - “真实 `guodegang_anchor_120s` 已有保护”
- 更准确的理解应写成：
  - 当前 `guodegang_anchor_proxy_v1` 对这条 friend-side speech-leak 线而言，
  - 仍是高风险的错配保护项。

后续要求：

1. 不继续并更多同类 synthetic `guodegang` proxy 充当保护项。
2. 下一步若还要做 decoupling protection，优先考虑：
   - real / near-real gate 优先
   - 或重新设计更贴近 `guodegang_anchor_120s` 的保护代理

### 96. 即使 exact target_full 与 near-real `speech_leak_like (0004)` 都变好，也不代表 friend-side speech-leak follow-up 已可保留；`friend_speech_leak_followup_gate` 证明真正卡口可能只剩 `guodegang_anchor / absent` 两条 real floor

现象：

- 本轮已把 friend-side follow-up gate 正式固化到：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- 对 `v35` 运行后可见：
  - relative to `v34`：
    - default `+0.003533 dB`
    - exact target_full `+0.102182 dB`
    - near-real `speech_leak_like (0004) = +0.022676 dB`
  - relative to `v32`：
    - exact target_full `+0.204893 dB`
    - near-real `speech_leak_like (0004) = +0.018996 dB`
- 但两种 reference 下都仍然：
  - `overall_pass = false`
  - failed rules 只剩：
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`

处理：

- 已补跑并落盘：
  - `friend_speech_leak_followup_gate_vs_v34.json`
  - `friend_speech_leak_followup_gate_vs_v32.json`
- 同时保留：
  - `v34 vs v32` 的 gate 结果
  作为这条线的前序对照。

结果：

- `v34` 证明：
  - exact-family 推正并不等于能过 friend-side real gate；
- `v35` 又进一步证明：
  - 即使 `0004-like speech-leak` 也开始回升，
  - 只要 `guodegang_anchor / absent` 两条 real floor 还在回退，
  - 这条 candidate 仍应直接判掉。

影响：

- 以后不能把：
  - “speech-leak side 指标终于变好了”
  直接等价成：
  - “这条 follow-up 已经能保留”
- 更准确的 keep/drop 口径应写成：
  - 先过 friend-side follow-up gate；
  - 尤其先守住：
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`
  - 之后才有资格讨论 exact / `0004-like speech-leak` 的局部收益。

后续要求：

1. 后续这条线所有新 candidate 默认先跑 `friend_speech_leak_followup_gate`。
2. 不再把“`exact target_full` 或 `0004-like speech-leak` 转好”单独当作放行依据。
3. 若下一步继续推进，优先补的是：
   - 直接面向 `guodegang_anchor / absent` real floor 的 guardrail
   - 或更贴近真实锚点的保护代理，而不是继续并新的 synthetic `guodegang` proxy

### 97. 如果 `anchor` 或 `absent` 保护项仍只能并进 base transient / absent 分支同权计算，就很容易把“想保护某个 real floor”误做成“再次把 base branch 搅宽”；`v35` 暴露的不是只差一个新 proxy，而是缺真正的 branch-local extra weight 通道

现象：

- `v35` 虽然把：
  - `transient_extra_focus_sample_ids = guodegang_anchor_proxy_v1`
  接到了 selector；
- 但当时训练图里并没有：
  - `transient_extra_weight`
  - `absent_extra_weight`
  这类独立权重；
- 实际效果仍等价于：
  - 保护样本被并回 base transient / absent 分支一起算。

处理：

- 本轮已补齐：
  - `transient_extra_sample_weights`
  - `absent_extra_sample_weights`
  - `transient_extra_weight`
  - `absent_extra_weight`
- 并同步补齐：
  - train / eval summary
  - selector metrics
  - smoke 验证

结果：

- 现在已经可以真正做：
  - `anchor -> transient_extra`
  - `absent -> absent_extra`
  的分侧小权重保护；
- 不必再把：
  - `guodegang_anchor_proxy_v1`
  或
  - `guodegang_absent_proxy_v3_strict`
  粗暴并回 base 分支。

影响：

- 以后不能把：
  - “extra selector 已经命中了”
  直接等价成：
  - “这条保护项已经是独立可控的 branch-local guardrail”
- 更准确的判断应写成：
  - 只有当 extra selector 对应的 loss 也有独立 weight / 独立 summary / 独立 gate 观察位时，
  - 才算真正具备可控的 branch-local 保护能力。

后续要求：

1. 后续凡是涉及 `anchor / absent` 保护项的实验，默认优先走：
   - `transient_extra`
   - `absent_extra`
   这两条独立分支。
2. 不再把新的 `anchor / absent` proxy 直接并进 base transient / absent 分支，除非实验目标就是验证“宽分支是否故意更强”。
3. 下一步若继续推进，优先做：
   - 分侧轻量 protection smoke
   - 然后直接用 friend-side follow-up gate 裁决是否值得保留

### 98. 只把 `guodegang_anchor_proxy_v1` 拆到 `transient_extra`，并不能自然变成可保留的 real-floor 保护；`v36` 证明这条 `anchor transient-extra only` 路线会同时伤到 exact speech-leak side 与 `guodegang` real floor

现象：

- `v36` 是第一条真正使用新 plumbing 的分侧 smoke：
  - 基座是 `v32`
  - 保留现有 friend-side `interference_extra` exact speech-leak branch
  - 新增：
    - `transient_extra = guodegang_anchor_proxy_v1`
    - `transient_extra_weight = 0.001`
- 结果 relative to `v19`：
  - default `+0.042394 dB`
  - exact proxy overall `-0.038284 dB`
  - exact `target_full = -0.322388 dB`
  - near-real `speech_leak_like (0004) = -0.042726 dB`
  - near-real `guodegang_anchor_120s = -0.300635 dB`
  - near-real `guodegang_absent_480s = -0.094534 dB`
- relative to `v32` 的 `friend_speech_leak_followup_gate`：
  - `overall_pass = false`
  - failed rules：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`

处理：

- 已将 `v36` 作为明确失败样本落盘，不进入 keep 候选。

结果：

- 这次失败不只是：
  - `guodegang_anchor / absent` 还没守住；
- 而是连：
  - exact `target_full`
  - near-real `0004-like speech-leak`
  也一并回退。

影响：

- 以后不能把：
  - “把某个 `anchor proxy` 从 base transient 拆到 `transient_extra`”
  直接等价成：
  - “real floor 保护会更稳”
- 更准确的理解应写成：
  - `guodegang_anchor_proxy_v1` 对 real `guodegang_anchor_120s`
    仍然是高风险错配保护项；
  - `anchor transient-extra only`
    不是这条 friend-side follow-up 的 keep 路径。

后续要求：

1. 不继续扫 `guodegang_anchor_proxy_v1` 的 `transient_extra_weight`。
2. 后续若还做 `guodegang` 保护，优先补：
   - 新 objective / branch
   - 或更贴近 real / near-real gate 的保护代理
3. 所有新 candidate 仍默认先过 `friend_speech_leak_followup_gate`。

### 99. 只要 sample-id 列表文件可能来自 Windows / PowerShell 落盘，就不能假设它一定是不带 BOM 的 UTF-8；否则 selector 首个样本会 silently 失配

现象：

- `sample_ids_guodegang_anchor_proxy_v1_{train,val,all}.txt`
  原先带有 UTF-8 BOM；
- 旧的 sample-id loader 使用 `encoding=\"utf-8\"` 读取时，
  会把首个样本读成：
  - `\\ufefftrain_000029`
- 这会导致：
  - selector 看起来“已命中 sample-id 文件”
  - 但第一条样本实际上不会匹配到 manifest 中的 `train_000029`

处理：

- 已把：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/data/build_metadata_focused_manifest.py`
  的 sample-id 读取改为 `encoding=\"utf-8-sig\"`
- 同时已将：
  - `sample_ids_guodegang_anchor_proxy_v1_train.txt`
  - `sample_ids_guodegang_anchor_proxy_v1_val.txt`
  - `sample_ids_guodegang_anchor_proxy_v1_all.txt`
  重写为无 BOM UTF-8
- 额外 smoke 已确认：
  - 新 summary 中的首个 sample_id 已恢复为 `train_000029`

结果：

- 后续 selector / manifest builder 即使遇到 BOM 文件，也不会再把首个样本读脏。

影响：

- 以后不能把：
  - “sample-id 文件行内容肉眼看起来正常”
  直接等价成：
  - “训练时 selector 一定能命中”
- 更准确的检查方式应写成：
  - sample-id loader 默认对 BOM 容错
  - 并在 summary / smoke 中确认首个样本没有 `\\ufeff`

后续要求：

1. 所有 newline-delimited sample-id 文件默认按 `utf-8-sig` 容错读取。
2. 新生成的 sample-id 文件优先写成无 BOM UTF-8。
3. 遇到 selector 命中率异常时，先排查 BOM / 编码问题，再判断是语义筛选失败。

### 100. 如果一个 proxy family 在 base manifest 中本来就已经完整存在，再去重建“union manifest”很容易让人误以为问题出在 coverage；但像 `v37` 这种 follow-up，真正变化的其实只是 objective routing

现象：

- 本轮为 `guodegang_absent_proxy_v3_strict` 做 `v37` 时，
  曾额外构造：
  - `train_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
  - `val_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
- 但随后核对发现：
  - train 相对 `v32` base manifest：
    - `97 vs 97`
    - `same_order = true`
    - `same_set = true`
  - val 相对 `v32` base manifest：
    - `29 vs 29`
    - `same_order = true`
    - `same_set = true`

处理：

- 已把这条事实明确写入 `v37` 日报和总览：
  - `guodegang_absent_proxy_v3_strict`
    并不是“新并入的样本族”；
  - 它实际上早已完整存在于 `v32` 的 base manifest 中。
- 同时补了新的 branch-local objective：
  - `reconstruction`
  - `reconstruction_extra`
  用来显式表达：
  - 对一组 hard `target_full` 行的 target reconstruction 拉力
  而不是继续误用 `absent_interval_l1`

结果：

- `v37` 的变化来源现在可以被准确表述为：
  - objective re-routing
  - 而不是 manifest coverage 扩充
- 这也解释了为什么：
  - `v37` 能把 `guodegang_anchor / absent` real floor
    从 `v36` 的更差位置往回拉一点；
  - 但同时又会伤到：
    - exact `target_full`
    - near-real `0004-like speech-leak`

影响：

- 以后不能把：
  - “又做了一份 plus / union manifest”
  直接等价成：
  - “这条 follow-up 终于给模型喂到了之前没有的样本”
- 更准确的检查顺序应写成：
  - 先核对新 manifest 与当前 base manifest
    是否真有新增 sample-id
  - 如果没有，
    就把实验解释聚焦到：
    - objective routing
    - branch-local weighting
    - selector coverage

后续要求：

1. 后续所有 plus / union manifest，在起正式训练前都先核对：
   - `same_set`
   - `same_order`
   相对当前基座是否真的有变化。
2. 若 manifest 完全等价，就不要再把实验命名或结论写成“扩样 follow-up”。
3. 像 `guodegang_absent_proxy_v3_strict` 这种早已存在于基座的 hard `target_full` 行，优先从 objective routing / branch-local objective 角度设计 follow-up。
