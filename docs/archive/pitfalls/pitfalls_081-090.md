# 踩坑记录 历史归档 81-90

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `81-90`

## 2026-03-16

### 81. 新增 reverse guardrail 并不等于可以靠简单下调 `absent_weight` 把 synthetic dual-proxy gate 的最后一点差距补过去；`v16 / v17` 证明这条路线的敏感点不在这里

现象：

- 本轮先构造了新的 reverse guardrail proxy：
  - `target_clean_speech`
  - `speech_interference_clean_pool`
  - 高 `interference_gain_db`
  - 高 `target_transient_presence_minus_mid_db_mean`
- 随后开的 `v16`：
  - `absent_proxy_v3_strict ∪ reverse_guardrail_proxy_v1`
  - 相对 `v12` 已经收敛到：
    - default = `-0.004540 dB`
    - `anchor_proxy_v1 = +0.298964 dB`
    - `absent_proxy_v3_strict = -0.007883 dB`
    - `absent_proxy_v4_broad = -0.001475 dB`
  - dual-proxy gate 只差：
    - absent 双项极小回退
- 但随后把：
  - `absent_weight = 1.0 -> 0.5`
  得到的 `v17` 反而变成：
  - default = `-0.038008 dB`
  - `anchor_proxy_v1 = -0.532572 dB`
  - `absent_proxy_v3_strict = -0.019250 dB`
  - `absent_proxy_v4_broad = -0.009301 dB`

影响：

- 这说明 `v16` 没过线的原因，不是“absent loss 稍微太重，降一点就会自然通过”；
- 更准确地说：
  - 这条路线已经接近 synthetic pre-screen；
  - 但真正还需要调的是：
    - full-pattern hard-speech 一侧的 transient / interference 路
    - 或整体预算分配
  - 不是继续把 absent side 越降越轻

处理：

- 本轮已将：
  - `v16`
  - `v17`
  都记录为：
  - 不保留
- 但同步保留一个更重要的中间结论：
  - `v16` 这条 objective 方向显著优于 `v13 / v14 / v15`

后续要求：

1. 以后若某条新路线已经接近 dual-proxy gate，只差极小 absent 回退，不要默认第一反应就是继续下调 `absent_weight`。
2. 对这类 near-miss，优先调整：
   - transient / interference selector
   - full-pattern 预算
   - 或总 step 分配
3. 如果一次降权重直接导致：
   - anchor floor 也丢
   - default 也回吐
   就应停止把“继续降 absent weight”当成默认搜索方向。

### 82. 对 `v16` 这条 reverse-guardrail 路线，把 transient / interference 一起减半并不会把 absent-side synthetic 缺口自动补回来；`v18` 说明“整体一起降预算”会先把 absent proxy 拉弱，而不是帮这条路线过线

现象：

- 本轮 `v18 = legacy_transient_leakguard_probe_v18_v12_absent_proxy_v3_reverse_guardrail_v1_ti_half_ft1`
  在 `v16` 同 manifest / 同 selector 下，仅把：
  - `transient_weight = 0.002 -> 0.001`
  - `interference_weight = 0.005 -> 0.0025`
- 结果相对 `v12`：
  - `anchor_proxy_v1 = +0.233116 dB`
  - 但：
    - `absent_proxy_v3_strict = -0.065609 dB`
    - `absent_proxy_v4_broad = -0.042189 dB`
- synthetic dual-proxy gate 仍然：
  - `FAIL`
  - failed：
    - `absent_proxy_v3_strict`
    - `absent_proxy_v4_broad`

影响：

- 这说明 `v16` 路线当前卡住的点，不是“transient / interference 总预算略高，降一点就自然过线”；
- 更准确地说：
  - 这两条 loss 在当前路线里仍提供了必要支撑；
  - 如果一起往下砍，先掉下去的反而是 absent-side synthetic 支配关系。

处理：

- 本轮已将 `v18` 记录为：
  - 不保留

后续要求：

1. 以后若某条 synthetic near-miss 路线还差 absent-side 最后一点，不要默认第一反应就是“把 transient / interference 一起减半”。
2. 优先改：
   - selector 形状
   - branch-local carve-out
   - 或单路预算
   而不是无差别整体减半。
3. 如果某条 follow-up 仍然表现为：
   - `anchor` 继续通过
   - absent 双失败
   就应明确写成：
   - 这版没有修掉真正的 absent 缺口。

### 83. 即使某个 absent follow-up 已经首次通过 synthetic dual-proxy gate，也不代表它可以直接晋升；`v19` 证明 synthetic 过线之后，broad near-real 仍可能卡在完全不同的 friend-side 锚点

现象：

- 本轮 `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
  首次同时通过：
  - `anchor_proxy_v1`
  - `absent_proxy_v3_strict`
  - `absent_proxy_v4_broad`
- 但补跑 near-real 后，相对 `v12` 仍然是：
  - speech probe overall = `-0.011926 dB`
  - `friend_raw = -0.039734 dB`
  - `near_real_0003 = -0.068178 dB`
  - `near_real_0004 = -0.011290 dB`
  - `near_real_0006 = +0.071497 dB`
- `speech_followup_gate_vs_v12`：
  - `FAIL`
  - failed：
    - `speech_probe_overall_floor`
    - `speech_probe_friend_raw_floor`
    - `anchor_0003_gain_floor`
    - `anchor_0004_gain_floor`
- 同时 `guodegang` 子 probe 虽已相对 `v8` 通过：
  - overall
  - `guodegang_anchor_120s`
  - `near_real_0006`
  但仍卡在：
  - `clip__guodegang_absent_480s`

影响：

- 这说明：
  - synthetic dual-proxy gate
  只负责证明 absent objective 方向终于可训练；
- 它不负责保证：
  - broad near-real `friend_raw / 0003 / 0004`
  不回退；
- 也不负责保证：
  - `guodegang_absent_480s`
  一定已经超过 `v8`。

处理：

- 本轮没有把 `v19` 直接升级成主候选；
- 当前口径改为：
  - `v19` 是新的 objective 基座
  - 但还需要 friend-side reverse guardrail / branch-local proxy

后续要求：

1. 以后任何 synthetic dual-proxy `PASS` 的 absent follow-up，都必须继续补：
   - `speech_followup_gate_vs_v12`
   - `probe_subset_guardrail_vs_v8_with_clips`
   再谈是否值得晋升。
2. 若结果表现为：
   - `0006` 继续变强
   - 但 `friend_raw / 0003 / 0004` 回退
   结论应改写成：
   - “objective 方向对了，但 broad real trade-off 还没闭环”
   而不是写成：
   - “这条线已经基本完成”。
3. 下一步若继续推进，优先补的是：
   - `v19 vs v12` 的 friend-side reverse guardrail
   - 或新的 branch-local synthetic proxy
   而不是继续只围绕 `absent_480s` 单边加力。

### 84. 如果把新加的 friend-side reverse guardrail 样本直接并进 `v19` warm-start，但它们没有命中任何专项 selector，那这轮训练本质上就不是“friend-side branch-local guardrail”，而只是一次 base-loss nudging；`v20` 证明这种做法会同时拖坏 broad real 和新增 proxy 本身

现象：

- 本轮 `v20 = legacy_transient_leakguard_probe_v20_v19_friend_reverse_guardrail_v1_ft1`
  相对 `v19` 只新增了：
  - train `21`
  - val `8`
  条样本；
- 且这些新增样本全部都是：
  - `target_clean_speech`
  - `target_full`
- 但 `v20` 的 selector 命中计数与 `v19` 完全相同：
  - train transient / interference / absent：
    - `51 / 51 / 24`
  - val transient / interference / absent：
    - `18 / 18 / 4`
- 唯一变化只是 total count：
  - train：
    - `90 -> 111`
  - val：
    - `27 -> 35`

影响：

- 这说明新增的 friend reverse guardrail 样本：
  - 没有进入 transient selector
  - 没有进入 interference selector
  - 也没有进入 absent selector
- 因而 `v20` 的真实形态不是：
  - “把 friend-side 风险正式接入 branch-local objective”
- 而更接近：
  - “在 `v19` 现有 objective 外，再额外并入一批只吃 base reconstruction loss 的 `target_clean_speech + target_full` 样本”
- 结果就是：
  - default val 相对 `v19 = -0.020962 dB`
  - `v20_v19_friend_reverse_guardrail_proxy_v1` 相对 `v19 = -0.131127 dB`
  - broad near-real speech probe overall 相对 `v19 = -0.051919 dB`
  - `near_real_guodegang_speech_probe` overall 相对 `v19 = -0.142566 dB`

处理：

- 本轮已把 `v20` 记录为：
  - 不保留
- 同时已把下一步要用的 selector plumbing 补到当前工作树：
  - `target_transient_presence_minus_mid_db_mean`
  - `target_transient_presence_share_mean`

后续要求：

1. 以后凡是新增 branch-local proxy 样本并入 warm-start 训练，必须同时核对：
   - total count 有没有变
   - `selected_count` 有没有同步增加
2. 如果只是：
   - total count 变多
   - `selected_count` 完全不变
   就不要把这轮训练写成：
   - “某个新 guardrail 已接入 objective”
   更准确的写法应是：
   - “只是一次无 selector 命中增量的 base-loss 并集 nudging”
3. 下一步若继续补 friend-side，不要再直接复制 `v20`；
   优先做的是：
   - 让 friend-side样本进入显式 selector
   - 或先重做能复现 friend-side 排序差异的 synthetic proxy

### 85. 即使把新增 friend-side proxy 真正接进了 selector，只要这批 proxy 样本本身没有提供比 `v19` 更正确的优化方向，训练仍然会回退；`v21` 说明“有 selector 命中”只是必要条件，不是充分条件

现象：

- 本轮 `v21 = legacy_transient_leakguard_probe_v21_v19_friend_reverse_guardrail_proxy_v2_transient_extra_ft1`
  在 `v20` 基础上进一步补了：
  - selector `extra` branch
  - 把新的 clean/full/high-transient friend proxy 显式挂进 `transient_extra`
- selector 命中数确实明显增加：
  - train transient：
    - `51 -> 76`
  - val transient：
    - `18 -> 30`
- 说明新增 branch 已经真实进入专项 loss，而不是 `v20` 那种零命中增量

影响：

- 但相对 `v19`，`v21` 仍然没有把目标方向推正：
  - default val：
    - `+0.008857 dB`
  - 新 proxy 自己：
    - `-0.076726 dB`
  - broad near-real speech probe overall：
    - `-0.042540 dB`
  - `near_real_guodegang_transient_probe_v1` overall：
    - `-0.122561 dB`
- stage2-relative 的关键 friend-side锚点也全部低于 `v19`：
  - `friend_raw`
  - `0003`
  - `0004`
  - `0006`
- `speech_followup_gate_vs_v19` 直接失败：
  - `speech_probe_overall_floor`
  - `speech_probe_friend_raw_floor`
  - `anchor_0003_gain_floor`
  - `anchor_0004_gain_floor`
  - `anchor_0006_regression_floor`
- 甚至 guodegang focused probe 相对 `v19` 也全线回退：
  - overall
  - family
  - `0006`
  - `anchor_120s`
  - `absent_480s`

处理：

- 本轮保留：
  - selector `extra` branch 这层基础设施
- 但不保留：
  - `v21` checkpoint

后续要求：

1. 以后凡是新 proxy 已经显式命中 selector，也仍然必须单独核对：
   - 该 proxy 相对当前基座是否真的转正
   - broad near-real 的关键锚点是否同步不回退
2. 如果出现：
   - selector 命中数明显增加
   - 但 proxy 自己和 near-real 关键锚点仍同时低于当前基座
   那问题就不再是“selector 没接上”，而应改判为：
   - “proxy 本身方向不够对，不能继续靠加预算硬推”
3. 下一步若继续补 friend-side，优先先重搜更窄、更贴近：
   - `0003 / 0004`
   的 proxy；
   不要先对这批 `v21` 样本继续扫权重、扫 epoch、扫 lr。

### 86. 如果一个 friend-side objective 在更严格的 exact samplewise-order-pass proxy 上仍然低于当前基座，那问题就不再是“proxy 太宽”，而是当前 objective / proxy 语义本身仍然不对；`v21` 在 `v22` exact full / nonfull proxy 上依然回退，说明继续缩窄同类 proxy 也不足以救活这条线

现象：

- 本轮把 friend-side proxy 搜索进一步收紧为：
  - 单样本先满足 `v12 > v19 > v8`
  - 再搜索 metadata 子集
- 对应地：
  - `val/default` shared speech rows 从 `237` 收缩到 `38`
  - `train/default` 也有 `176` 条 single-sample order-pass speech rows
- 基于这套 exact 搜索又落了两类 proxy：
  - exact full：
    - train `10`
    - val `4`
  - exact nonfull：
    - val `7`
- 但相对 `v19`：
  - `v21` 在 exact full 上仍是：
    - `-0.065412 dB`
  - `v21` 在 exact nonfull 上仍是：
    - `-0.156167 dB`

影响：

- 这说明 `v21` 的失败已经不能再归因于：
  - “proxy 还不够窄”
  - 或“proxy 里还混了太多单样本方向相反的行”
- 更准确的解释应改写为：
  - 当前 `transient_extra` 这条 friend-side objective
  - 即便只看 exact、single-sample order-pass 的 full / nonfull 子集
  - 也仍然没有把优化方向推到 `v19` 之上

处理：

- 本轮保留：
  - `samplewise-order-pass` exact proxy 搜索链
  - `sample_ids_file` manifest 构建链
- 但不保留：
  - 直接沿当前 `v21` 逻辑开 `v22` 训练

后续要求：

1. 以后若某条 friend-side objective 在 exact full / nonfull proxy 上仍低于当前基座，
   就不要再把下一步写成：
   - “继续缩窄 proxy 再试一次”
2. 这种情况下应直接把问题升级为：
   - objective / proxy 语义不匹配
   - 需要换 proxy 形态或换 loss 归属
3. 对当前这条线，下一步优先应改：
   - 更贴近 `0003 / 0004` 的 residual-transient / speech-leak 语义
   - 或不再继续只挂在 `transient_extra`
   而不是继续：
   - 同类 full/high-transient proxy 的宽窄扫描

### 87. `near_real_0004` 不能默认并入同一个 transient-only friend objective；本轮 semantic split 已显示它更像 `target_full + clean-pool + higher-gain + lower-transient` 的 speech-leak 语义，继续把 `0003 / 0004` 合并进单一 `transient_extra`，即使 exact proxy 也仍压不过 `v19`

现象：

- 本轮给 `search_synthetic_proxy_candidates.py` 补了 low-side bucket：
  - `gain_le_q50`
  - `transient_le_q50`
  - `transient_lt_q67`
- 然后把 friend-side exact proxy 明确拆成两族：
  - `0003-like residual-transient`：
    - train `10`
    - val `4`
  - `0004-like speech-leak`：
    - train `11`
    - val `3`
- 其中 `0004-like` 这族在当前 synthetic order-pass 行里并不落在：
  - `nonfull`
  - 或另一批 high-transient
  之上；
  它反而更像：
  - `target_full`
  - clean speech pool
  - higher-gain
  - lower-transient
- 但即便这样拆开后，`v21` 相对 `v19` 仍然：
  - residual-transient exact：`-0.065412 dB`
  - speech-leak exact：`-0.020621 dB`

影响：

- 这说明当前问题已经不能再描述成：
  - “只要把 `0004-like` 再收进同一个 transient 分支就会好”
- 更准确的描述应改成：
  - `0003 / 0004` 虽然都属于 friend-side speech overlap 回退
  - 但它们不是同一种 synthetic proxy 语义
  - 尤其 `0004-like` 不应默认按 transient-only 目标去吸收

处理：

- 本轮保留：
  - semantic-split exact proxy 搜索与 manifests
- 但不保留：
  - 继续把 `0003 / 0004` 合并成一个 single-branch friend objective 的写法

后续要求：

1. 以后若要继续补 friend-side `0003 / 0004`，至少先分两条语义：
   - residual-transient-like
   - speech-leak-like
2. 不要再把 `0004-like` 默认写成：
   - “另一批 transient proxy”
3. 新训练若要开，应优先考虑：
   - `0003-like` 仍挂 transient-adjacent 分支
   - `0004-like` 单独挂 interference / leak 侧归属
   而不是继续：
   - 两者并到同一个 `transient_extra`

### 88. 即使已经把 `0003-like` / `0004-like` 分别接到 `transient_extra` 和 `interference_extra`，one-shot semantic split 也不等于 friend-side objective 已经转正；`v24 / v25` 证明“语义拆开”只是开始，不是完成

现象：

- 本轮已把 friend-side 两条语义真正接进训练：
  - `v24`:
    - train transient `55 / 109`
    - train interference `51 / 109`
  - `v25`:
    - train transient `63 / 109`
    - train interference `62 / 109`
- 说明这批 friend-side proxy：
  - 不是 `v20` 那种零命中增量
  - 已真实进入 active selector
- 但相对 `v19`：
  - `v24 semantic-split proxy = -0.091072 dB`
  - `v25 semantic-split proxy = -0.152489 dB`
  - `v25 residual-transient exact = -0.176585 dB`
  - `v25 speech-leak exact = -0.120362 dB`
  - `v24 near_real_friend_speech_probe = -0.041770 dB`
  - `v25 near_real_friend_speech_probe = -0.037164 dB`

影响：

- 这说明当前问题已经不能再主要解释成：
  - selector 没接上
  - 或 `0003 / 0004` 还没有拆语义
- 更准确的说法应改成：
  - 当前 semantic split 的 objective / proxy 语义仍不够对
  - 即便已经分挂到不同 loss 归属
  - 也还没有把 friend-side 的 exact proxy 和 near-real bucket 一起推正

处理：

- 本轮保留：
  - semantic split 训练入口本身
  - `v24 / v25` 这批结果作为反例与边界
- 但不保留：
  - 把 `v24 / v25` 当成新候选继续放大预算

后续要求：

1. 以后即使已经把多个语义分挂到不同 selector，也不能默认写成：
   - “objective 已经对了”
2. 若 exact proxy 和 near-real friend bucket 仍同时低于当前基座，
   结论应直接升级为：
   - objective / proxy 语义本身仍需重做
3. 对当前这条线，不再优先做：
   - `v24 / v25` 的权重、epoch、lr 微扫

### 89. 把 `0003-like` 或 `0004-like` 单独 carve-out，也不等于至少能救回一半问题；`v26 / v27` 证明两侧 branch-local objective 当前都还不够稳

现象：

- `v26 residual-only` 相对 `v19`：
  - `residual-only proxy = -0.201198 dB`
  - `near_real_friend_speech_probe = -0.049491 dB`
  - `near_real_guodegang_speech_probe = +0.003146 dB`
- `v27 speech-leak-only` 相对 `v19`：
  - `speech-leak-only proxy = -0.144539 dB`
  - `near_real_friend_speech_probe = -0.044400 dB`
  - `near_real_guodegang_speech_probe = -0.004776 dB`

影响：

- 这说明：
  - `0003-like residual-transient`
    当前还不能被视为单独可保留的安全训练入口；
  - `0004-like speech-leak`
    当前也还没有形成稳定的 interference/leak-side 正收益；
  - 尤其后者已经开始把 `guodegang` 侧已有收益一起回吐

处理：

- 本轮不保留：
  - `v26`
  - `v27`
- 当前只把它们记为：
  - 单侧 carve-out 已验证过，但都未转正

后续要求：

1. 以后不要把“先单独 carve-out 一侧试一下”默认理解成：
   - 至少能保住另一侧不坏
2. 如果单侧 carve-out 仍然同时表现为：
   - 自己的 proxy 为负
   - friend-side near-real bucket 也为负
   结论应直接写成：
   - 这一侧的 branch-local objective 还不够对
3. 对当前这条线，下一步优先应继续改：
   - speech-leak / residual-transient 的 proxy 语义或 guardrail
   而不是继续沿当前 `v26 / v27` 直接放大预算

### 90. 如果 synthetic proxy 的正确边界已经依赖 exact `samplewise-order-pass` 子集，就不能再只用宽元数据 selector 近似；需要显式 sample-id selector，否则会把已排除的坏样本重新打回训练目标

现象：

- `v28` 已暴露：
  - metadata-only 宽集合即使长得像 speech-leak，
  - 也可能把 `v19 > v12 > v8` 的坏样本重新混进来；
- 本轮 `v29` 又进一步验证：
  - 即便 exact manifest 已经收成 `samplewise-order-pass`
  - 如果训练侧还只能靠 recipes / patterns / gain / transient 之类宽 selector 近似，
  - 实际 objective 仍然会偏回 “宽 region”，而不是 exact 子集本身。

处理：

- 本轮新增并保留：
  - `scripts/train/train_stft_mask_baseline.py`
    - `--loss-*-focus-sample-ids-file`
  - `src/tse_prefix/pipeline/loss_selectors.py`
    - `focus_sample_ids`
- 同时给 manifest 构建链补了：
  - `scripts/data/build_metadata_focused_manifest.py --include-derived-metrics`
  - 使 exact allowlist manifest 也能保留新的派生声学字段。

结果：

- `v29` 的 `interference_extra` 命中已精确对齐到：
  - train `+21`
  - val `+3`
- 这次可以排除：
  - selector 没接上
  - 宽 metadata 边界导致命中错样本
- 但结果仍然是：
  - default `-0.004999 dB`
  - exact speech-leak proxy `-0.142498 dB`

影响：

- 以后当 proxy 正确性已经依赖 exact samplewise 子集时，不能再写成：
  - “先用宽 metadata selector 近似一下，方向大概一样”
- 更严格的要求应改成：
  - 要么 selector 能直接命中 exact sample-id；
  - 要么就承认当前 objective 还没有真正对准 proxy。

后续要求：

1. 遇到 `samplewise-order-pass` 才能站住的 proxy 时，优先保留：
   - exact sample-id selector
   - exact manifest
2. 如果 exact sample-id selector 已经接通，但结果仍然不转正，
   结论应直接升级为：
   - objective / proxy 语义本身仍需重做
3. 不再把“宽 selector 近似失败”误归因成：
   - plumbing 问题
   - 或命中率还不够
