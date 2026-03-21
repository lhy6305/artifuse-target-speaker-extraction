# 踩坑记录 历史归档 71-80

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `71-80`

## 2026-03-16

### 71. `near_real_0006` 现在已经不是单一子问题；如果还把 `guodegang_anchor_120s` 和 `guodegang_absent_480s` 混成同一条 proxy 或同一条 gate，只会继续把训练信号互相抵消

现象：

- 本轮把 `near_real_guodegang_transient_probe_v1` 再拆成：
  - `near_real_guodegang_anchor_probe_v1`
  - `near_real_guodegang_absent_probe_v1`
- 结果发现两条 clip 的真实排序已经冲突：
  - `anchor`:
    - `v7 > v8 > v10 > v11`
  - `absent`:
    - `v8 > v7 > v10 > v11`

影响：

- 如果继续把两条 clip 混在同一条 `0006` guardrail 里看 overall：
  - 会看见一个折中的均值
  - 但看不出 candidate 到底是在修：
    - `anchor`
    - 还是 `absent`
- 这会导致：
  - 误把某个“只修好其中一条”的版本理解成“`0006` 已整体转正”
  - 或继续错误寻找一条“统一总 proxy”

处理：

- 本轮已把 clip 级 guardrail 正式脚本化：
  - `scripts/eval/gate_probe_subset_guardrail.py --clip-tags ...`
- 同时把 synthetic proxy 也拆成两条：
  - `guodegang_anchor_proxy_v1`
  - `guodegang_absent_proxy_v2_speechonly`

后续要求：

1. 今后凡是声称“补 `0006`”的版本，至少同时汇报：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
2. 若只看合并后的 `near_real_guodegang_transient_probe_v1` overall，不再视为足够。
3. 下一步默认不再寻找“统一 `0006` 总 proxy”，而是分别维护：
   - `anchor` proxy
   - `absent` proxy

### 72. `absent` proxy 一旦把 `music / singing` 一起混进来，排序会立刻漂掉；这条 proxy 必须保持 speech-only 边界

现象：

- 本轮先按较宽口径物化了：
  - `guodegang_absent_proxy_v1`
- 它包含：
  - `speech`
  - `music`
  - `singing`
  的 full-overlap 高 transient rows
- 结果在 synthetic compare 上，排序变成：
  - `v7 > v8 > v10 > v11`
  而不是 near-real `absent_480s` 想要的：
  - `v8 > v7 > v10 > v11`

影响：

- 这说明 `absent_480s` 的 proxy 不是“只要高 transient 就行”
- 一旦把 non-speech rows 混进来，就会把排序重新带偏
- 也就是：
  - `absent` proxy 的关键边界之一就是 speech-only

处理：

- 本轮已收回并改成：
  - `guodegang_absent_proxy_v2_speechonly`
- 过滤条件为：
  - `target_clean_speech / target_hard_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `overlap >= 0.9`
  - `target_transient_presence_minus_mid_db_mean >= q50`
- 新 manifest 已确认复现：
  - `v8 > v7 > v10 > v11`

后续要求：

1. 以后若继续构造 `absent_480s` proxy，默认保持 speech-only。
2. 不要因为某个 broad transient-rich manifest 看起来更“大更全”，就把 `music / singing` 一起混进来。
3. 若某条 `absent` proxy 没有先验证：
   - `v8 > v7 > v10 > v11`
   就不要把它当成新的 objective 入口。

### 73. broad speech gate 过线，不等于 clip 级 `anchor / absent` trade-off 已过线；`v12` 证明如果不同时看两条 clip，仍会把“有代价的成功”误读成“已可替代参考版本”

现象：

- 本轮 `v12 = legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1`：
  - 相对 `v8` 的 `speech_followup_gate_summary.json` 已经 `PASS`
  - `near_real_guodegang_transient_probe_v1` overall 也相对 `v8` 转成：
    - `+0.075219 dB`
- 但同一轮在 clip 级 `probe_subset_guardrail_vs_v8_with_clips.json` 里仍然：
  - `FAIL`
  - 唯一失败项是：
    - `clip__guodegang_absent_480s`
- 也就是说，`v12` 的真实形态是：
  - `guodegang_anchor_120s` 相对 `v8`：
    - `+0.266803 dB`
  - `guodegang_absent_480s` 相对 `v8`：
    - `-0.116366 dB`

影响：

- 如果只看：
  - broad speech follow-up gate
  - 或合并后的 `near_real_0006` overall
- 很容易误判成：
  - `v12` 已经无代价替代 `v8`
- 实际上它只是：
  - 成功修回了 `anchor`
  - 但仍在 `absent` 上付出小幅代价

处理：

- 本轮已把该结论同步写入：
  - `reports/daily/2026-03-18_v12_v8_anchor_proxy_ft1.md`
  - `docs/01_project_overview_and_plan.md`
- 当前默认口径更新为：
  - `v8` 保留为 broad speech 参考基座
  - `v12` 仅作为 anchor-focused 第二候选保留

后续要求：

1. 以后凡是 `v12+` 的 follow-up，至少同时汇报：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
2. 只要 clip 级 `absent` 仍明显回退，就不要把 broad gate 的 `PASS` 误写成“已可切主线”。
3. 下一步若继续推进，优先补的是：
   - `absent` 的显式 floor / guardrail
   而不是继续做更宽的 anchor-only 强化。

### 74. Windows PowerShell 5 的 `Set-Content -Encoding utf8` 默认会写 UTF-8 BOM；对当前 JSONL 读取器来说，这会直接把新 manifest 写坏

现象：

- 本轮在物化：
  - `train_manifest_v13_anchor_absent_proxy_v1.jsonl`
  - `val_manifest_v13_anchor_absent_proxy_v1.jsonl`
  时，先用 `Set-Content -Encoding utf8` 写盘；
- 随后训练入口在读取第一行 JSONL 时直接报错：
  - `Unexpected UTF-8 BOM (decode using utf-8-sig)`

影响：

- 当前训练数据读取链默认按普通 `utf-8` 解码；
- 只要 manifest 带 BOM，就会在首行 `json.loads(...)` 直接失败；
- 这类问题看起来像“JSON 内容坏了”，实际上是编码前缀问题。

处理：

- 本轮已改用 `.NET UTF8Encoding(false)` 将两份 manifest 重写为：
  - UTF-8 无 BOM

后续要求：

1. 后面凡是新写 JSON / JSONL / Markdown，如果走 PowerShell 落盘，默认不要用会写 BOM 的旧口径。
2. 若必须用 PowerShell 原生命令生成文本，写完后至少再核对一次是否带 BOM。
3. 当前仓库的“统一 UTF-8 无 BOM”不是口头约定；它会直接影响训练脚本能不能读文件。

### 75. 把 `anchor_proxy` 和 `absent_proxy` 直接做 one-shot 并集，再从 `v12` warm-start 微调，并不会自然形成“保 anchor、补 absent”的折中；`v13` 证明它会把训练信号继续推向 friend 侧，却仍修不好真正想补的 `absent_480s`

现象：

- 本轮 `v13 = legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1`：
  - 使用：
    - `guodegang_anchor_proxy_v1`
    - `guodegang_absent_proxy_v2_speechonly`
    的去重并集
  - 从 `v12` warm-start
- 结果相对 `v8`：
  - near-real speech probe overall：
    - `+0.264425 dB`
  - `near_real_0003`：
    - `+0.311168 dB`
  - `near_real_0004`：
    - `+0.418977 dB`
  - 但 `near_real_0006`：
    - `-0.037517 dB`
  - 且 clip 级仍是：
    - `guodegang_anchor_120s = +0.107729 dB`
    - `guodegang_absent_480s = -0.182764 dB`
- 结果相对 `v12` 还进一步变成：
  - `guodegang_anchor_120s = -0.159074 dB`
  - `guodegang_absent_480s = -0.066398 dB`

影响：

- 这说明当前 one-shot union 训练不是“把两条目标自然平衡起来”；
- 它更像：
  - 继续强化了 `friend_raw / 0003 / 0004`
  - 却没有把真正要补的 `absent_480s` 拉回来
  - 还顺带把 `v12` 的 anchor 收益也一起回吐

处理：

- 本轮已将 `v13` 记录为：
  - 不保留
- 当前默认口径更新为：
  - 不继续沿这条 one-shot `anchor+absent` 并集路线扩大训练

后续要求：

1. 以后不要把“proxy 数量从 1 条加到 2 条”误读成“目标自然会更平衡”。
2. 若下一步还要补 `absent`，应先重做：
   - `absent` objective proxy
   - 或 `clip` 级 floor / gate
3. 在没有新 proxy 证据前，不要再直接把现有 `absent_proxy_v2_speechonly` 拼进 `v12` 做训练。

### 76. 新重建出来的 `absent` proxy 如果本身是 `target_full`，那就不能再想当然地以为“现有 absent-loss 配置会自动在这条 proxy 上生效”；`v14` 证明当前 selector 下它根本没有触发

现象：

- 本轮按真实排序 `v8 > v12 > v13` 重建出的新 proxy：
  - `guodegang_absent_proxy_v3_strict`
  - `guodegang_absent_proxy_v4_broad`
- 它们都稳定收敛到：
  - `target_hard_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `high-overlap`
- 随后开的 `v14 = legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1` 训练日志里：
  - `train_absent_interval_l1 = 0.0`
  - `val_absent_interval_l1 = 0.0`
  且三轮都如此

原因：

- 当前训练参数仍把 absent loss 限定在：
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
- 但这轮新 proxy 全是：
  - `target_full`

影响：

- 名字叫 “absent proxy follow-up”，不代表它真的走了 explicit absent-loss；
- 在当前 selector 下，它其实只是：
  - 一次基于新 proxy 的 `target_full / hard speech` focused fine-tune
- 如果忽略这点，就会把训练结果误读成：
  - “absent loss 没有效果”
  - 但实际更准确的说法是：
    - 这轮根本没触发到 absent loss

处理：

- 本轮已在：
  - `reports/daily/2026-03-18_v14_v12_absent_proxy_v3_strict_ft1.md`
  - `docs/01_project_overview_and_plan.md`
  显式补记该事实

后续要求：

1. 以后只要新 proxy 是 `target_full` 主导，就必须先核对：
   - 当前 loss selector 是否真的会在它上面触发
2. 不要把：
   - “proxy 名字是 absent”
   自动等价成：
   - “训练里一定有 absent-loss 信号”
3. 若后续真要把这条新 proxy 接进 objective，先决定的是：
   - 改 selector
   - 还是承认它只是新的 focused fine-tune subset

### 77. 能复现真实排序的 synthetic proxy，不等于直接拿它从当前候选 warm-start 微调，就会把真实指标往正确方向推；`v14` 证明了“proxy 可搜索”与“proxy 可训练”是两件事

现象：

- 本轮新重建的 `guodegang_absent_proxy_v3_strict / v4_broad` 已经能稳定复现：
  - `v8 > v12 > v13`
- 但基于主候选 `v3_strict` 开出的：
  - `v14 = legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1`
  结果却变成：
  - 相对 `v12`
    - default val：
      - `-0.098198 dB`
    - near-real speech probe overall：
      - `-0.210393 dB`
    - `near_real_0006`：
      - `-0.750831 dB`
    - `guodegang_anchor_120s`：
      - `-1.099112 dB`
    - `guodegang_absent_480s`：
      - `-0.402550 dB`
    - `guodegang_absent_proxy_v3_strict`：
      - `-0.284848 dB`
- 也就是说：
  - 它不但没把真实 `absent` 拉回去；
  - 连这轮新建的主 proxy 自己也没保住

影响：

- 这说明：
  - “找到能复现真实排序的 synthetic 子集”
  - 只是解决了：
    - proxy 定义问题
  - 还没有解决：
    - 当前 warm-start / 预算 / objective / 约束下是否可训练
- 如果跳过这层区分，很容易把后续每次失败都误归因成：
  - proxy 还不够准
  而不是：
  - 训练路径本身不适合

处理：

- 本轮已将 `v14` 记录为：
  - 不保留
- 当前默认口径更新为：
  - `v3_strict / v4_broad` 保留为 absent-side synthetic eval / guardrail
  - 但不再直接当作 `v12` 的 single-route warm-start fine-tune objective

后续要求：

1. 以后先把这两件事分开判断：
   - proxy 是否真实对齐
   - 在当前训练路径下是否可训练
2. 若下一步还要继续补 `absent`，优先考虑的是：
   - 联立 `anchor` floor
   - 或更小预算的 nudging
   - 或先把新 proxy 只当 gate / eval，而不是直接拿来训练
3. 在没有新证据前，不要再把：
   - “proxy 搜索通过”
   直接写成：
   - “这条 focused fine-tune 路线可继续加预算”

### 78. 把 `anchor_proxy_v1` 与新 `absent_proxy_v3_strict` 做极轻量并集 nudging，确实能把 `anchor_120s` 拉回安全区附近，但它仍不会自然把 `absent_480s` 拉到 `v12` 之上；`v15` 说明这条路线本质上还是在强化 `anchor`，而不是在修真正的 `absent`

现象：

- 本轮 `v15 = legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1`：
  - 从 `v12` warm-start
  - 训练集是：
    - `guodegang_anchor_proxy_v1`
    - `guodegang_absent_proxy_v3_strict`
    的去重并集
  - 但预算极小：
    - `1 epoch`
    - `lr = 1e-5`
    - `34 steps`
- 结果相对 `v8`：
  - `guodegang_anchor_120s = +0.049097 dB`
  - `guodegang_absent_480s = -0.186798 dB`
- 结果相对 `v12`：
  - `guodegang_anchor_120s = -0.217707 dB`
  - `guodegang_absent_480s = -0.070432 dB`
  - `guodegang_anchor_proxy_v1 = +0.322262 dB`
  - `guodegang_absent_proxy_v3_strict = -0.126638 dB`

影响：

- 这说明轻量双路 nudging 的真实作用更像：
  - 保住甚至继续加强 `anchor` 方向
  - 但并没有把目标中的 `absent` 一侧往前推进
- 如果忽略这点，很容易把它误读成：
  - “已经很接近，只要再把步长调小一点就行”
- 但从当前证据看，更准确的说法是：
  - 这条路线的优化向量本身就偏向 `anchor`
  - 它不是当前 `absent_480s` 的有效修复入口

处理：

- 本轮已将 `v15` 记录为：
  - 不保留
- 当前默认口径更新为：
  - 不继续沿这条 warm-start 小步长搜索路线加预算

后续要求：

1. 以后不要因为某个版本“重新通过了 `clip__guodegang_anchor_120s`”就误判它正在修 `absent`。
2. 对这类双路 nudging，至少同时汇报：
   - `anchor_proxy` 变化
   - `absent_proxy` 变化
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
3. 如果结果表现出：
   - `anchor` 继续增强
   - `absent` 继续不动或回退
   就应直接停止，而不是继续扫更小 learning rate / 更小 step 数。

### 79. 如果训练摘要里不显式记录 selector 命中统计，就很容易把“loss 权重开着但 selector 实际 0 命中”的情况误读成“这项 loss 效果不好”；`v14` 暴露的是 selector 没打中，不只是数值弱

现象：

- `v14` 文档已经确认：
  - `absent_weight = 2.0`
  - 但 `train_absent_interval_l1 = 0.0`
  - 且新 proxy 样本本身都是：
    - `target_full`
- 如果只看旧版 `train_summary.json`：
  - 能看到 loss 数值为 `0.0`
  - 但看不到：
    - selector 到底有没有选中样本
- 这种情况下，很容易把结论写成：
  - “absent loss 开了但没有效果”
  - 而不是更准确的：
    - “当前 selector 配置根本没有命中这批样本”

处理：

- 本轮已在当前工作树补上：
  - dataset 侧 selector 元数据：
    - `overlap_ratio`
    - `interference_gain_db`
    - `interference_pool`
    - `interference_speaker_name`
  - 统一的：
    - `loss_selectors.py`
  - train summary 中的：
    - `train_selector_metrics`
    - `val_selector_metrics`
- 并已用 `tmp/selector_metrics_smoke_v14_style` 做 1-step smoke 验证：
  - `absent.selected_fraction = 0.0`

后续要求：

1. 以后任何 focused fine-tune 只要开了 selector，就必须同时看：
   - loss 数值
   - selector `selected_count / selected_fraction`
2. 如果某项 selector `active = true` 但：
   - `selected_count = 0`
   应先修 selector 或修 proxy 定义，而不是继续解释 loss 曲线。
3. 后续文档汇报里，不要再只写：
   - `absent_interval_l1 = 0.0`
   还要补一句：
   - 是因为命中为零
   - 还是命中了但优化失败。

### 80. 只看 `anchor_proxy_v1` 是否继续增强，无法判断候选是不是在修 `absent`；`v13 / v15` 都证明了“anchor 通过”与“absent 通过”是两回事，后续必须用 dual-proxy gate 同时看

现象：

- 本轮新增 synthetic dual-proxy gate 后，回放结果变得更明确：
  - `v13`
    - `anchor_proxy_v1 - v12 = +0.893597 dB`
    - 但：
      - `absent_proxy_v3_strict - v12 = -0.111381 dB`
      - `absent_proxy_v4_broad - v12 = -0.104639 dB`
  - `v15`
    - `anchor_proxy_v1 - v12 = +0.322262 dB`
    - 但：
      - `absent_proxy_v3_strict - v12 = -0.126638 dB`
      - `absent_proxy_v4_broad - v12 = -0.078349 dB`

影响：

- 如果只盯：
  - `anchor_proxy_v1`
  会很容易得出一种错误直觉：
  - “候选还在往对的方向走，只差一点 absent”
- 但 dual-proxy gate 已经说明：
  - 这些版本不是“差一点”；
  - 而是 synthetic absent-side 方向本身仍低于 `v12`。

处理：

- 本轮已新增：
  - `scripts/eval/gate_synthetic_dual_proxy.py`
- 当前默认规则应固定为：
  - `anchor_proxy_v1` 相对 `v12` 不回退
  - `guodegang_absent_proxy_v3_strict / v4_broad` 相对 `v12` 不变差

后续要求：

1. 以后任何 `v12+` absent follow-up，都不要再只汇报：
   - `anchor_proxy_v1`
   - 或单条 absent proxy
2. 至少同时看：
   - `anchor_proxy_v1`
   - `absent_proxy_v3_strict`
   - `absent_proxy_v4_broad`
3. 如果结果是：
   - anchor 通过
   - absent 双失败
   结论应直接写成：
   - 这条路线仍在强化 anchor，不是在修 absent。
