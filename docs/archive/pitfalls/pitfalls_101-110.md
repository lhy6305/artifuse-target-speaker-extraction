# 踩坑记录 历史归档 101-110

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `101-110`

## 2026-03-16

### 101. 如果 absent-side objective 直接作用在与 friend-side exact branch 共用的 hard `target_full` 行上，单纯继续加大 `interference_extra_weight` 并不能把 speech-leak side 拉回；`v38` 证明这不是一个“再平衡权重不够大”的简单问题

现象：

- `v37` 已说明：
  - `guodegang_absent_proxy_v3_strict`
    接到 `reconstruction_extra`
    会把 `guodegang` 两条 real floor 往回拉一点；
  - 但同时会伤到：
    - exact `target_full`
    - near-real `speech_leak_like (0004)`
- 因此本轮又做了 `v38`：
  - 把 absent-side 改成更轻的 `waveform-only reconstruction_extra`
  - 同时把：
    - `interference_extra_weight = 0.0075 -> 0.03`

处理：

- `v38` 继续从 `v32` 起步，
  直接用 `v32` base manifest，
  避免 manifest coverage 因素混入解释。
- 然后只改变：
  - `reconstruction_extra` 的形式与强度
  - `interference_extra_weight`

结果：

- `v38` 相对 `v37`：
  - default 更好
  - `guodegang_anchor / absent` 也都略有回升
- 但：
  - exact `target_full` 更差
  - near-real `speech_leak_like (0004)` 也更差
- 相对 `v32` 的 friend-side follow-up gate 仍然：
  - `overall_pass = false`
  - failed：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`

影响：

- 以后不能把：
  - “absent-side objective 已经更轻了”
  - “friend-side exact branch 也已经提权了”
  直接等价成：
  - “这条 trade-off 接下来只差继续扫一下 weight”
- 更准确的理解应写成：
  - 一旦 absent-side objective
    直接改写了 shared hard `target_full` 区域的优化方向，
  - friend-side `interference_extra`
    就未必能通过单纯加权把它抵回来

后续要求：

1. 不继续围绕 `v37 / v38` 这族配置扫：
   - `interference_extra_weight`
   - 或当前 `reconstruction_extra` 配比
2. 后续若仍做 absent-side protection，优先做：
   - 更细粒度的 absent proxy carve-out
   - 或避免直接作用于 shared hard `target_full` 行的 objective
3. 所有“再平衡”实验都应先问清：
   - 当前冲突是 branch weight 不够，
   - 还是 objective 本身已经在改写共享区域

### 102. 即使把 absent-side 从 shared rows 改成更窄的 metadata carve-out，也不能把 synthetic carve-out 局部转正直接当成 real gate 已被修好；`v39` 证明这类 clean absent proxy 只够说明“方向更干净”，还不够说明“真实门已过”

现象：

- `v39` 没再直接复用 `guodegang_absent_proxy_v3_strict` 整族 shared hard `target_full` 行；
- 而是切到一批更窄的 metadata carve-out：
  - `target_clean_speech`
  - `target_full`
  - `speech_interference_clean_pool`
  - `target_present_ratio >= 0.95`
  - `target_transient_presence_minus_mid_db_mean <= -9.231693`
  - `interference_transient_presence_minus_mid_db_mean <= 5.840138`
- 这批 `v5 cleancarve` 子集相对 `v19` 的 synthetic summary 为：
  - `+0.181394 dB`
- 但同一 checkpoint 在 real / near-real 侧仍然：
  - exact `target_full = -0.467426 dB`
  - `speech_leak_like (0004) = -0.086908 dB`
  - `guodegang_anchor_120s = -0.099820 dB`
  - `guodegang_absent_480s = -0.057543 dB`
- 相对 `v32` 的 `friend_speech_leak_followup_gate` 仍：
  - `overall_pass = false`

处理：

- 已补写 `v39` 日报与 gate 结果：
  - `reports/daily/2026-03-19_v39_absent_recon_cleancarve_followup.md`
  - `reports/eval/compare_v19_vs_v39_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`

结果：

- 当前可以确认：
  - 更窄的 clean absent metadata carve-out 确实比直接作用 shared rows 更“干净”；
  - 但它的 synthetic proxy 局部转正，并不会自动迁移成：
    - friend-side exact speech-leak 转正
    - 或 `guodegang anchor / absent` 两条 real floor 守住

影响：

- 以后不能把：
  - “某个 absent carve-out 在 synthetic 自定义 proxy 上转正了”
  直接等价成：
  - “这条 absent-side 保护已经可保留”
- 更准确的解释应写成：
  - synthetic carve-out 只说明 selector / 代理方向可能更贴近目标；
  - 是否值得保留，仍必须回到：
    - exact `target_full`
    - `speech_leak_like (0004)`
    - `guodegang_anchor`
    - `guodegang_absent`
    这几条 gate 来裁决

后续要求：

1. 后续所有 absent-side metadata carve-out，都必须同步跑 real / near-real gate，不能只看自定义 proxy summary。
2. 不继续围绕当前 `v39` 的 metadata 上界或权重做低价值细扫。
3. 下一步若还做 absent-side follow-up，优先：
   - 继续排查 `v5 cleancarve` 内与 friend-side exact 冲突的子集；
   - 或补更贴近 near-real `guodegang_absent` 的保护代理；
   - 或改成不直接改写 target reconstruction 方向的 objective。

### 103. metadata carve-out 即使表面上和 friend-side exact family 不是同一条分支，也可能在 selector 交叉后重新命中 exact 样本；`v39 -> v40` 预备说明必须显式核对 overlap，而不能只看“这次没有直接传 exact sample-id”

现象：

- `v39` 的 absent-side `reconstruction_extra`
  没有直接使用 friend-side exact 的 sample-id 文件；
- 但按真实 selector 口径回放后发现，
  它仍然命中了：
  - train：
    - `train_000001`
    - `train_000432`
    - `train_001225`
    - `train_001610`
  - val：
    - `val_000075`
- 其中 `val_000075`
  正是 `v39` 在 exact `target_full` summary 里的主要回退点：
  - `sisdr_delta_db = -0.467426 dB`

处理：

- 已生成一组去 overlap 的 `v40` 预备 allowlist：
  - `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_train.txt`
  - `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_val.txt`
  - `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_all.txt`
- 并补写预备日报：
  - `reports/daily/2026-03-19_v40_absent_cleancarve_noexactoverlap_prep.md`

结果：

- 当前已经能把“metadata carve-out 大方向没问题”和“selector 交叉后误撞 exact family”这两类问题拆开；
- 下一条最直接可测的 follow-up
  就是不改 loss 图，
  先把 overlap 显式剔掉。

影响：

- 以后不能把：
  - “这次 absent-side 没直接传 exact sample-id 文件”
  直接等价成：
  - “它一定没有碰到 friend-side exact family”
- 更准确的检查顺序应写成：
  - 先回放真实 selector 命中集合；
  - 再和当前所有关键 sample-id family 做交集；
  - 最后再判断这条 carve-out 是方向不对，还是只是 selector crossfire。

后续要求：

1. 只要新分支同时存在：
   - metadata selector
   - 与其他 branch 的 sample-id family
   就必须显式核对 overlap。
2. 后续所有 absent-side carve-out 预备，都至少落一份：
   - kept ids
   - excluded overlap ids
   的摘要。
3. 若下一条 `v40` 仍失败，再把解释收紧到：
   - selector crossfire 不是主因，
   - 问题更可能在代理本身与 real gate 的语义错配。

### 104. 不要把“新 absent proxy family 看起来更贴近 current signal”自动等价成“real absent floor 会更好”；`v40 / v41` 证明必须把 proxy 本体分数和 real gate 关键值一起落盘，否则很容易只记住 gate failed，却忘了代理自己也在反向

现象：

- `v40` 已经把 `v39` 的 exact overlap 显式剔掉；
- 但 relative to `v19`，
  它仍然是：
  - exact `target_full = -0.467909 dB`
  - near-real `speech_leak_like (0004) = -0.086817 dB`
  - near-real `guodegang_anchor_120s = -0.099242 dB`
  - near-real `guodegang_absent_480s = -0.057473 dB`
  - `guodegang_absent_proxy_v6_currentsignal_cleanonly = -0.424082 dB`
- `v41` 进一步把 absent-side 直接换成
  `proxy_v6 currentsignal cleanonly allowlist`
  后，
  relative to `v19` 变成：
  - exact proxy overall `+0.036695 dB`
  - 但 exact `target_full = -0.325134 dB`
  - near-real speech probe overall `-0.109792 dB`
  - near-real `speech_leak_like (0004) = -0.062535 dB`
  - near-real `guodegang_anchor_120s = -0.258474 dB`
  - near-real `guodegang_absent_480s = -0.112892 dB`
  - `guodegang_absent_proxy_v6_currentsignal_cleanonly = -0.627418 dB`
- relative to `v32` 的 gate，
  `v41` 还额外 failed：
  - `speech_probe_overall_floor`

处理：

- 已把 `v40 / v41` 的裁决证据集中落盘到：
  - `reports/daily/2026-03-19_v40_v41_absent_followup_results.md`
- 并同步回写：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`

结果：

- 现在可以明确写死：
  - `proxy_v6` 本体 relative to `v19`
    不是边走边好，
    而是一路更差：
    - `v32 = -0.172916 dB`
    - `v39 = -0.424309 dB`
    - `v40 = -0.424082 dB`
    - `v41 = -0.627418 dB`
- 这说明当前 `currentsignal cleanonly v6`
  不是“更贴近 real absent 的代理还差一点点”，
  而更像是：
  - 代理本体就还在反向；
  - exact overall 即使局部转正，
    也不能推出关键的 exact `target_full`
    和 `guodegang` real floor 已被守住。

影响：

- 以后不能把：
  - `default` 还在正增益
  - 或 exact proxy overall 变正
  - 或代理名字看起来更像 current signal
  直接等价成：
  - absent-side 方向已经接近 keep
- absent-side candidate 的最小裁决证据必须至少同时写 5 个数：
  - exact `target_full`
  - `speech_leak_like (0004)`
  - `guodegang_anchor_120s`
  - `guodegang_absent_480s`
  - proxy 本体 summary

后续要求：

1. 后续每条 absent-side candidate 默认同时落盘这 5 个数值。
2. 若 proxy 本体 relative to `v19` 已明显为负，
   不再把它简单归因成：
   - “只是 gate 太严”
3. 下一条 absent-side proxy 设计，
   必须先说明它与当前 `proxy_v6 currentsignal cleanonly`
   的语义差异；
   否则默认视为同类失败重试。

### 105. 不要把“新 absent proxy candidate 仍没过 friend gate”自动等价成“proxy 本体也失败了”；`v42` 证明新的 `proxy_v7` 已能把 `guodegang_anchor / absent` 两条 real floor 拉回正向，真正失败的是当前 `reconstruction_extra` routing 仍会伤到 friend-side `exact target_full / speech_leak_like`

现象：

- 本轮把 `B3` 的新 absent proxy 正式落成：
  - `guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans`
  - train `33`
  - val `8`
- 它与 friend-side exact family 的 overlap 已明显更干净：
  - train `1`
    - `train_001225`
  - val `0`
- 且它不是旧 rows 重路由：
  - 相对 `v32` base manifest
    新增 coverage：
    - train `32`
    - val `8`
- 在这条 `proxy_v7` 上，
  旧 checkpoint relative to `v19` 已经是：
  - `v32 = -0.788730 dB`
  - `v40 = +0.537238 dB`
  - `v41 = +1.267294 dB`
- 进一步训练得到：
  - `v42 = v32 + reconstruction_extra(proxy_v7)`
- `v42` relative to `v19`：
  - default `+0.077955 dB`
  - exact `target_full = -0.664459 dB`
  - `speech_leak_like (0004) = -0.113430 dB`
  - `guodegang_anchor_120s = +0.126568 dB`
  - `guodegang_absent_480s = +0.031863 dB`
  - `proxy_v7 = +0.444459 dB`
- relative to `v32` 的 gate，
  `v42` 只 failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

处理：

- 已把这轮 `proxy_v7` 定义、coverage、训练与裁决结果集中落盘到：
  - `reports/daily/2026-03-19_v42_absent_proxy_v7_followup.md`
- 并同步回写：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`

结果：

- 现在可以明确拆开两层结论：
  - `proxy_v7` 本体是有效的：
    - 本体 summary 为正；
    - `guodegang_anchor / absent`
      两条 real floor
      也第一次同时转正；
  - 失败的是当前
    `reconstruction_extra(proxy_v7)`
    这条 routing：
    - 它仍会把 friend-side
      `exact target_full`
      与 `speech_leak_like`
      一起拖坏
- 所以：
  - `v42` 不能 keep；
  - 但不能因此退回写成：
    - “`proxy_v7` 也像 `proxy_v6` 一样无效”

影响：

1. 以后若新 absent proxy candidate 已满足：
   - 本体为正
   - real `guodegang_anchor / absent`
     同时转正
   但仍 failed 于 friend gate，
   默认先怀疑：
   - objective routing / decoupling
   而不是立刻把 proxy 本体判死。
2. `proxy_v6` 与 `proxy_v7`
   必须分开记：
   - `proxy_v6` 是本体反向；
   - `proxy_v7` 是本体成立、routing 失败。
3. 下一条 absent-side follow-up，
   默认不再重搜 proxy；
   而是围绕：
   - exact `target_full`
   - `speech_leak_like (0004)`
   的保护与解耦继续做。

### 106. 不能把所有 gate failed rule 都按同一级别解释；当前 absent / friend-side 裁决至少要区分 `near_tie` 和 `clear_fail`，否则会把“局部接近但总体仍失败”和“方向明显错误”混成同一种失败记忆

现象：

- 用户提醒后回看当前主 gate，
  发现它之前虽然已有：
  - default `0.1 dB` 容差
  - speech overall `0.05 dB` 容差
- 但输出层面仍只有：
  - `pass / fail`
- 这会把两类情况混写成同一种失败：
  - 只低于 floor `0.01 ~ 0.02 dB`
  - 明显低于 floor `0.1 ~ 0.3 dB`
- 用新口径回看后，
  `v41` 就是典型例子：
  - `speech_probe_overall_floor = near_tie`
    - `-0.009327 dB` below floor
  - `exact_target_full_gain_floor = near_tie`
    - `-0.021816 dB`
  - `speech_leak_like_gain_floor = near_tie`
    - `-0.020855 dB`
  - 但：
    - `guodegang_anchor_floor = clear_fail`
      - `-0.192590 dB`
    - `guodegang_absent_floor = clear_fail`
      - `-0.099666 dB`

处理：

- 已更新：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- 当前默认解释规范变成：
  - `pass`
  - `near_tie`
    - 低于 floor 不超过 `0.03 dB`
    - 只改变解释，不放宽 `overall_pass`
  - `clear_fail`
    - 低于 floor 超过 `0.03 dB`
- 输出里新增：
  - `candidate_minus_floor`
  - `judgement`
  - `overall_judgement`
  - `near_tie_rules`
  - `clear_fail_rules`

结果：

- `v39` / `v40`
  仍是 clear fail；
- `v41`
  更准确应写成：
  - 局部 near-tie
  - 但 real floor clear fail；
- `v42`
  仍是 clear fail，
  且 clear fail 已只剩：
  - exact `target_full`
  - `speech_leak_like (0004)`

影响：

1. 以后不能再把：
   - “局部 near-tie 但总体 failed”
   误写成：
   - “整条分支方向都错”
2. 也不能反过来把：
   - 某几条 near-tie
   误写成：
   - 这条分支可能其实应当 keep
3. 当前规范下，
   `near_tie`
   的作用是：
   - 防止失真记忆；
   - 不是放宽 keep gate。

### 107. 如果一条 follow-up 从 `v42` 到 `v43` 只做微幅 waveform weight rescale，而 default / exact / near-real / `guodegang` / proxy 本体几乎完全不动，就不该继续扫同类小数点级权重；这类缩放在当前 `proxy_v7` 路线上基本是 no-op

现象：

- `v43 = v42`
  只把：
  - `reconstruction_extra_waveform_weight`
    从 `0.005`
    改到 `0.0025`
- 其余：
  - `proxy_v7`
  - merged manifest
  - friend-side exact branch
  - base transient / interference / absent
  全都不变
- 结果 relative to `v19` 几乎和 `v42` 完全重合：
  - default：
    - `+0.077955 -> +0.077610`
  - exact `target_full`：
    - `-0.664459 -> -0.663965`
  - `speech_leak_like (0004)`：
    - `-0.113430 -> -0.113233`
  - `guodegang_anchor_120s`：
    - `+0.126568 -> +0.125676`
  - `guodegang_absent_480s`：
    - `+0.031863 -> +0.031660`
  - `proxy_v7`：
    - `+0.444459 -> +0.440865`

处理：

- 已把这轮验证集中落盘到：
  - `reports/daily/2026-03-19_gate_margin_reassessment_and_v43_followup.md`

结果：

- 现在可以明确写死：
  - 当前 `proxy_v7`
    路线上的微幅 waveform weight rescale
    基本是 no-op；
  - `v43`
    仍 failed 于：
    - exact `target_full`
    - `speech_leak_like (0004)`
  - 但并没有带来新的可解释 trade-off。

影响：

1. 不继续扫：
   - `0.005 -> 0.0025 -> 0.001`
   这类小数点级 waveform-only rescale。
2. 下一条若继续沿 `proxy_v7`，
   默认应改：
   - routing mode
   - 或 branch-level decoupling
   而不是继续扫同类微幅权重。

### 108. 当 `proxy_v7` 已证明本体成立时，单纯把 `reconstruction_extra` 从 `waveform_only` 切成 `stft_only` 只会带来很小的 friend-side 回收，同时削弱 default / proxy 本体 / `guodegang` 收益；这说明问题不只是损失域选错，而是需要更本质的 branch-level decoupling

现象：

- 在 `v42 / v43` 之后，
  本轮继续做了第一条真正的 routing mode 变化：
  - `v44 = reconstruction_extra_stft_only(proxy_v7)`
  - `reconstruction_extra_waveform_weight = 0.0`
  - `reconstruction_extra_stft_weight = 0.01`
- `v44` relative to `v19`：
  - default `+0.072833 dB`
  - exact `target_full = -0.647221 dB`
  - `speech_leak_like (0004) = -0.110539 dB`
  - `guodegang_anchor_120s = +0.113703 dB`
  - `guodegang_absent_480s = +0.029381 dB`
  - `proxy_v7 = +0.359405 dB`
- 相比 `v42`：
  - friend-side 两条是有小幅回收：
    - exact `target_full`
      `-0.664459 -> -0.647221`
    - `speech_leak_like (0004)`
      `-0.113430 -> -0.110539`
  - 但代价也同时出现：
    - default：
      `+0.077955 -> +0.072833`
    - `proxy_v7`：
      `+0.444459 -> +0.359405`
    - `guodegang_anchor_120s`：
      `+0.126568 -> +0.113703`
    - `guodegang_absent_480s`：
      `+0.031863 -> +0.029381`
- relative to `v32` gate，
  仍 clear fail 于：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

处理：

- 已把这轮结果集中落盘到：
  - `reports/daily/2026-03-19_v44_proxy_v7_stft_followup.md`

结果：

- 现在可以明确写死：
  - `stft_only`
    比微幅 wave weight 缩放更有信号；
  - 但它不是这条线的解法；
  - 当前问题不只是：
    - “选 waveform 还是 STFT”
    而更像是：
    - 这条 absent-side routing
      还没有和 friend-side speech-leak
      真正解耦

影响：

1. 不继续把
   `waveform_only <-> stft_only`
   当成默认主推进方向。
2. 下一条若继续沿 `proxy_v7`，
   优先考虑：
   - 更本质的 branch-level decoupling
   - 或更细的 routing 重写
3. 文档里以后应把 `v44`
   记成：
   - “mode 有信号”
   - 但“signal 还不足以形成 keep 候选”。

### 109. 当 `proxy_v7` 已经被证明本体有效时，把它内部的 `full` 与 `nonfull` 行拆开做不同 reconstruction routing，会比单一路由更平衡，但若 friend-side 两条仍 clear fail，就应把它记成“更好的 decoupling primitive”，而不是误记成已经接近 keep

现象：

- 本轮继续把 `proxy_v7` 内部拆成：
  - full：
    - train `17`
    - val `5`
  - nonfull：
    - train `16`
    - val `3`
- 训练了：
  - `v45 = nonfull waveform + full stft`
- `v45` relative to `v19`：
  - default `+0.075720 dB`
  - exact `target_full = -0.653286 dB`
  - `speech_leak_like (0004) = -0.111924 dB`
  - `guodegang_anchor_120s = +0.119305 dB`
  - `guodegang_absent_480s = +0.029907 dB`
  - `proxy_v7 = +0.396169 dB`
- 相比 `v44`：
  - default 更强
  - `proxy_v7` 更强
  - `guodegang_anchor / absent`
    也更强
- 但 relative to `v32` gate，
  仍 clear fail：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

处理：

- 已把这轮 split-routing 结果集中落盘到：
  - `reports/daily/2026-03-19_v45_proxy_v7_splitrouting_followup.md`

结果：

- 现在可以明确写死：
  - `proxy_v7 full`
    与
    `proxy_v7 nonfull`
    不应继续共用同一种 reconstruction routing；
  - 这类 split routing
    的确比单一路由更平衡；
  - 但当前这一级 split
    还没有把 friend-side 两条 clear fail
    拉回 near-tie，
    所以不能误记成：
    - “这条线已经接近 keep”

影响：

1. 以后若继续沿 `proxy_v7`，
   默认优先继续做：
   - 更细的内部语义拆分
   - 或更本质的 branch-level decoupling
2. 不再把：
   - 单一路由
   当成默认基线思路；
   当前更合理的默认 primitive
   已经是：
   - `full / nonfull` split routing
3. 但也不把当前 `v45`
   误写成：
   - 已接近通过 gate 的准 keep 分支。

### 110. 如果把 absent-side follow-up 的可训练范围压到纯 reference-conditioning，friend-side 两条确实可能被拉回到 `near_tie / pass`，但 absent proxy 本体会直接塌掉；这说明当前缺的不是“更少更新”本身，而是“给 absent-side 一点专属 output plasticity，同时别改写共享主干”

现象：

- 本轮新增了：
  - `scripts/train/train_stft_mask_baseline.py`
    的 `--trainable-module-prefixes`
- 并跑了：
  - `v47 = proxy_v7 all ids + ref_encoder + condition_proj only`
- `v47`
  trainable parameter count：
  - `131,968 / 2,367,617`
  - `5.57%`
- relative to `v32` gate：
  - `overall_judgement = near_tie`
  - `exact_target_full_gain_floor = pass`
  - `speech_leak_like_gain_floor = near_tie`
- 但 relative to `v19`：
  - `proxy_v7 = -0.858876 dB`
  - `guodegang_anchor_120s = -0.059132 dB`
  - `guodegang_absent_480s = -0.007238 dB`

处理：

- 已把这轮 prefix-freeze 工程补充与 `v47`
  结果集中落盘到：
  - `reports/daily/2026-03-20_v47_v48_prefix_freeze_decoupling_followup.md`

结果：

- 现在可以明确写死：
  - 纯 ref-conditioning freeze
    的确能保护 friend-side；
  - 但它对 absent-side
    过于保守，
    连 `proxy_v7`
    本体都带不起来；
  - 所以不能把：
    - `v47` 的 gate 近似通过
    误写成：
    - “这条线已经接近 keep”

影响：

1. 以后若继续沿 branch-level decoupling，
   不要把：
   - “继续减少 trainable 参数”
   当成默认方向
2. 当前更合理的默认目标应改写成：
   - 给 absent-side
     一点专属 output-side 可塑性；
   - 但不要再改写共享时序主干
3. 因此下一条默认不再扫：
   - 纯 prefix freeze 的更窄组合。
