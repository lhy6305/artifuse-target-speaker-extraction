# 踩坑记录

## 归档说明

- 本文档当前只保留 `119` 及之后的活跃记录，便于接班和日常维护。
- 更早的历史记录已拆分归档到 `docs/archive/pitfalls/`。
- 归档总索引见 `docs/archive/pitfalls/README.md`。

## 当前活跃记录

## 2026-03-16

### 119. 对 dual-head 来说，exact-family `SI-SDR guard` 依然很容易把训练推成 exact overfit；`v55` 证明“exact 更好”并不等于 near-real protect 真成立

现象：

- 本轮在 dual-head 上测试了：
  - `v55 = dual-head + proxy_v7 reconstruction + exact SI-SDR guard`
- relative to `v19`：
  - default `+0.126371 dB`
  - exact proxy overall `+0.394224 dB`
  - `proxy_v7 = +1.859823 dB`
- 但 near-real 明显转负：
  - speech probe overall `-0.140416 dB`
  - `guodegang_anchor = -0.494584 dB`
  - `guodegang_absent = -0.157483 dB`

影响：

- 如果只看到：
  - exact family 变正
  - `proxy_v7` 继续变强
  很容易误以为 dual-head protect objective 已经更接近 keep。
- 实际上这更像：
  - exact-family overfit
  - 而不是 friend-side / near-real protect 真正成立。

处理：

- 已把 `v55`
  的训练、compare、gate 与解释集中落盘到：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

后续要求：

1. 后续 dual-head protect objective 不能把 exact-family 变正自动当作放行理由。
2. 若某条 protect objective 把 exact / `proxy_v7` 一起推强，但 `guodegang` 或 near-real speech 明显转负，应直接判成 overfit 型失败。
3. 对这条线，默认不再继续扫 exact `SI-SDR guard` 的小权重变体。

### 120. 新增 extra-only protect weight 时，如果 selector 激活逻辑没把它算进 `extra_weight_keys`，实验会静默失效；`v56` 就属于这种无效轮次

现象：

- 首次跑 dual-head `base-align` 版本时，
  训练命令已经传了：
  - `--loss-interference-extra-base-align-weight`
  - `--loss-interference-extra-focus-sample-ids-file`
- 但当时
  `resolve_selector_sample_weights(...)`
  里，
  `interference_extra`
  的激活条件还没把：
  - `interference_extra_base_align_weight`
  算进去。
- 结果：
  - `v56`
    实际上 `interference_extra = inactive`
  - exact ids 并没有真正命中这条 protect objective。

影响：

- 这类问题不会像 shape error 那样直接崩；
  训练能跑完，
  但实验结论是假的。
- 如果不单独标记，
  后续很容易把这类无效轮次误当成：
  - objective 无效
  - 或 dual-head 本身没信号。

处理：

- 已在：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  把：
  - `interference_extra_base_align_weight`
  加入 `interference` 分支的 `extra_weight_keys`。
- 并把：
  - `v56`
    明确记为无效 plumbing 轮次；
  - 有效结论从 `v57`
    开始算。

后续要求：

1. 以后每新增一个 extra-only loss weight，都要同步检查 selector 激活条件是否已纳入它。
2. 新 protect primitive 首轮若结果异常平，应先核对 selector 命中，再下模型结论。
3. 无效轮次要明确写成 invalid / plumbing issue，不能混进模型比较序列。

### 121. dual-head 的 `base-align` protect primitive 有信号，但继续扫同一条 weight 已进入平台区；`v57 / v58` 说明当前缺的不是“小数点再调一下”

现象：

- 本轮在 dual-head 上新增：
  - `interference_extra_base_align_l1`
  - 语义是：
    - exact ids 上约束 branch output 不要偏离 frozen base output
- `v57`（weight `0.02`）relative to `v19`：
  - `speech_leak_like (0004) = -0.047720 dB`
  - `guodegang_absent = -0.000021 dB`
  - `proxy_v7 = -1.498264 dB`
  - relative to `v32 gate`：
    - `overall_judgement = near_tie`
    - 唯一 near-tie rule：
      - `speech_leak_like_gain_floor`
- `v58`（weight `0.005`）relative to `v19`：
  - `speech_leak_like (0004) = -0.076592 dB`
  - `guodegang_anchor = +0.061275 dB`
  - `guodegang_absent = +0.027740 dB`
  - `proxy_v7 = +0.042581 dB`
  - relative to `v32 gate`：
    - 唯一 clear fail：
      - `speech_leak_like_gain_floor`

影响：

- `base-align`
  说明 protect primitive 方向是对题的；
  它确实能把 dual-head 拉近 gate。
- 但当前 trade-off 已经很清楚：
  - 保护重了，
    `proxy_v7` 会被压塌；
  - 放轻一点，
    `speech_leak_like (0004)` 又重新 clear fail。
- 如果继续只扫这同一条 weight，
  很容易进入：
  - 实验很多，
  - 但结论不再变硬
  的平台区。

处理：

- 已把：
  - `v57`
  - `v58`
  的结果与解释集中落盘到：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

后续要求：

1. 当前默认不再继续扫 `interference_extra_base_align_weight` 的近邻小变体。
2. 下一条 dual-head protect objective 应更直接面向：
   - `speech_leak_like (0004)`
   - 而不是继续只做 exact-family base 对齐。
3. 同时继续保留：
   - dual-head plumbing
   - `proxy_v7`
   - `v32` frozen base anchor
   这三项资产，作为下一条新 protect objective 的底座。

### 122. 即使 protect primitive 看起来更“局部更聪明”，如果它在 exact ids 上的实际 loss 量级几乎为 `0`，继续扫权重也不会自动变成有效约束；`v59 / v60` 证明 `base-delta-interference projection` 当前就属于这种情况

现象：

- 本轮新增并正式测试了：
  - `interference_extra_base_delta_projection_weight`
- selector 已真实命中：
  - train `7 / 129`
  - val `3 / 37`
- 但 `v59 / v60`
  的 train summary 里，
  新 protect 项量级都极小：
  - `v59`
    - train `2.0131949656154081e-07`
    - val `1.8925945539649546e-07`
  - `v60`
    - train `1.9598214456009678e-07`
    - val `1.7825688871653256e-07`
- 同时：
  - `proxy_v7 / guodegang`
    仍明显变强
  - 但 friend-side
    `exact target_full / speech_leak_like (0004)`
    仍 clear fail

影响：

- 如果只看：
  - “这是更局部的 protect primitive”
  很容易主观上觉得它比 `base-align`
  更有希望。
- 但当实际 loss 量级已经接近 `0` 时，
  继续把权重从：
  - `0.005`
  调到：
  - `0.02`
  往往也只会得到近乎同形态结果，
  不是新的结构性结论。

处理：

- 已完成：
  - `v59`
  - `v60`
  两个正式点；
- 并把训练、compare、gate 与结论集中落盘到：
  - `reports/daily/2026-03-20_v59_v60_dualdecoder_basedeltaproj_followup.md`

后续要求：

1. 对任何新 protect primitive，不能只看 selector 是否命中；还要看该项 loss 的实际量级。
2. 如果在有效命中样本上，该项 loss 长期只有 `~1e-7` 这种接近零的量级，就不要继续扫近邻权重。
3. 这类结果应直接判成：
   - primitive 没真正碰到当前坏掉的行为语义，
   而不是：
   - “再多试两档 weight 也许就行”。

### 123. 如果 protect selector 仍把多类 exact-family 行为绑在一起，可能会把本来对题的 protect primitive 误判成“方向不对”；`v61` 说明 `base-align` 真正的问题之一是 selector 过粗，而不是 primitive 本身失效

现象：

- `v57 / v58`
  已说明 dual-head 上的 `base-align`
  primitive 有信号；
- 但当时 protect selector
  仍挂在整组
  `v30 exact 10 ids`
  上，
  会同时混入：
  - `target_full`
  - `speech_leak_like (0004)`
  - 以及其它 exact-family 行为；
- 本轮把 selector 收窄到：
  - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt`
  后，
  `v61`
  相对 `v19`：
  - exact `target_full`
    从前一轮同类失败点
    `-0.95 / -0.98 dB`
    回收到：
    - `-0.369736 dB`
  - `speech_leak_like (0004)`
    也回收到：
    - `-0.071034 dB`
    并在 relative to `v32` gate
    中只剩：
    - `near_tie`
  - 同时：
    - `guodegang_anchor = +0.069889 dB`
    - `guodegang_absent = +0.043306 dB`
    都没有塌。

影响：

- 如果只看早一轮粗 selector 下的表现，
  很容易把：
  - `base-align`
    误写成：
    - primitive 本身不对题
- 但 `v61`
  说明更准确的解释是：
  - protect primitive 可能是对的；
  - 真正坏的是 selector 语义过粗，
    把不同坏行为绑成同一条约束。

处理：

- 已把 `v61 / v62`
  的结果集中落盘到：
  - `reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`

后续要求：

1. 以后评估 protect objective 时，不能只问“primitive 是什么”，还要问“selector 语义是不是过粗”。
2. 如果一个 protect primitive 在粗 selector 下表现摇摆，但在更细 selector 下出现实质回收，应先把问题归因到 selector，再决定是否放弃 primitive。
3. 当前 dual-head protect 线里，`target_full` 应视为一个独立保护子问题，不再默认和整组 exact-family 绑死。

### 124. 当更细 selector 已证明方向成立后，继续单纯把同一条 protect weight 往上推，可能只会把 trade-off 再次推回去；`v62` 说明下一步该补的是第二条行为约束，而不是同一 primitive 的更强档

现象：

- `v61`
  已证明：
  - `target_full`-only selector
    是对的；
- 本轮继续把同一条
  `interference_extra_base_align_weight`
  从：
  - `0.02`
  加到：
  - `0.05`
  得到 `v62`；
- `v62`
  相对 `v61`：
  - `speech_leak_like (0004)`
    只小幅改善：
    - `-0.071034 -> -0.063768 dB`
  - 但 exact `target_full`
    明显变差：
    - `-0.369736 -> -0.586134 dB`
  - 同时：
    - `proxy_v7`
      从：
      - `-0.029114 dB`
      变成：
      - `+0.861507 dB`
    - `guodegang_anchor`
      也进一步转强。

影响：

- 这说明当前缺的
  已不是：
  - “同一条 protect primitive
     的 weight 还没调到位”
- 而是：
  - `target_full`
  - 与 `0004-like speech leak`
    其实是两类不同的保护行为，
    需要拆开约束。

处理：

- 已把这条结论同步写入：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`
  - `reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`

后续要求：

1. 当前默认不再继续扫 `target_full`-only `base-align` 的近邻更强档。
2. 下一条 dual-head protect objective，应在保留 `target_full` 保护的前提下，再补一条更直接面向 `speech_leak_like (0004)` 的 branch-local protect signal。
3. 以后遇到“更强权重把一个子问题略微拉好、却把另一个关键子问题重新推坏”的情况，应优先考虑拆目标，而不是继续扫同一条 weight。

### 125. 当主线是否切换其实已经有稳定主观结论后，项目如果继续默认沿 objective / gate 自动扩实验树，就会让“研究排雷”和“主线决策”混层；这时需要项目级 stop rule，而不是继续靠局部 gate 自己滚

现象：

- 当前项目早已得到：
  - `ref_film + stft0.5 + sisdr0.0005`
    不升主线；
  - focused `ft2 / ft3`
    也不升主候选；
- 但后续推进仍然持续长出了：
  - `v36+`
    大量 absent / friend-side / dual-head
    objective 研究分支；
- 这些分支的价值主要是：
  - 排雷
  - 定位冲突
  - 写清哪些 primitive / routing / selector
    不值得再扫；
  - 而不是：
    - 已经接近替换默认主线。

影响：

- 如果不显式把：
  - 默认主线
  - 研究基座
  - 已关闭分支
  这三层拆开，
  项目会自然滑向：
  - 还有什么能试就继续试什么；
- 这会让：
  - objective / gate
    成为实际节奏驱动，
  - 而不是：
    - 主观结论
    - 真实症状
    - 项目级停止条件。

处理：

- 已新增：
  - `reports/daily/2026-03-20_project_state_reset_after_review.md`
- 并把正式口径更新为：
  - 默认主线：
    - `legacy stage2`
  - 当前 `v36+`
    解释为：
    - 研究排雷分支
  - 默认下一步：
    - 暂停等待用户指示，
      不自动起新实验

后续要求：

1. 以后必须把“主线是否切换”与“研究是否继续”分成两套决策，不再混用同一条默认推进逻辑。
2. 当主线结论已锁定而研究仍在继续时，默认计划应写成：
   - `paused / pending instruction`
   而不是：
   - `continue training`
3. 若后续重新启动实验，新分支必须先写明：
   - 服务的真实问题症状是什么；
   - 为什么不是旧 primitive 的近邻重扫；
   - 对应哪条人耳或 near-real 复核入口。

### 126. `exact_all - exact_targetfull_all` 这种“补集 selector”如果没先过 metadata 语义复核，很容易被误当成另一个症状族；在本项目里它并不是 `0004-like speech leak`，而几乎全是 `target_absent_head / tail`

现象：

- `v61 / v62`
  已经证明：
  - `target_full`-only `base-align`
    是对的；
- 因而后续很自然地把：
  - `exact_all - exact_targetfull_all`
  当成
  “第二条 `0004-like` protect selector”
  去执行了 `v63`；
- 但 `v63`
  的结果形态是：
  - exact `target_full`
    继续明显收回；
  - `proxy_v7`
    继续放大；
  - near-real `0004`
    几乎没变好；
  - `guodegang_anchor / absent`
    一起转负。

复盘：

- 进一步检查这 5 个
  `exact_nontargetfull`
  ids 的 metadata 后发现：
  - `train_000405`
    - `target_absent_head`
  - `train_001279`
    - `target_absent_head`
  - `train_001491`
    - `target_absent_tail`
  - `val_000096`
    - `target_absent_tail`
  - `val_000297`
    - `target_absent_head`
- 也就是：
  - 这个补集 selector
    几乎全是
    `absent-like nonfull`
    行为；
  - 它并不表达
    `speech_leak_like (0004)`
    语义。

影响：

- 如果直接把这种补集
  当成另一个症状族去训练，
  很容易出现：
  - exact / proxy
    某一侧继续变强；
  - 但真正想修的 near-real 症状
    不动甚至更差；
  - 同时把别的 real anchor
    一起打坏。

处理：

- 已把 `v63`
  结论落盘到：
  - `reports/daily/2026-03-20_v63_dualdecoder_targetfull_basealign_branchprotect_followup.md`
- 并同步修正文档口径：
  - `exact_all - exact_targetfull_all`
    不再保留为
    第二 protect selector
    的默认定义。

后续要求：

1. 以后任何“补集 selector”
   在进入训练前，
   必须先抽样读 metadata，
   确认它的实际 pattern / recipe
   语义。
2. 如果一个 selector
   的语言标签是：
   - `0004-like`
   - `friend speech leak`
   之类真实症状名，
   那它必须能在 metadata 复核里
   说清为什么真对应这类症状，
   不能只靠集合差。
3. 下一条 dual-protect
   若继续，
   应先重建真正对应
   `speech_leak_like (0004)`
   的 proxy / selector，
   而不是继续扫
   `exact_nontargetfull`
   的 guard weight。

### 127. checkpoint / compare / gate 已落盘但日报未补，会把“当前停点”误导回更早分支；`v64 / v65` 本轮就是这个问题

现象：

- 本次接班恢复时，
  主文档和分支图都还停在：
  - `v63`
  - 以及
    “不要直接起 `v64`”
- 但磁盘上已经实际存在：
  - `v64 / v65` checkpoint
  - 对应 compare summary
  - 对应 `friend_speech_leak_followup_gate`
  - 对应新 selector / union manifest
- 也就是：
  - 真实实验状态
    已经比日报和总览
    多往前走了两步；
  - 只是当轮没有把
    结果及时写回文档。

影响：

- 下次接手的人如果只看文档，
  会误以为：
  - `v64 / v65`
    还没跑；
  - 或仍值得按旧思路
    再启动一次。
- 这种错位最麻烦的地方在于：
  - 它不是“文件丢了”
  - 而是“文件在，但裁决缺席”
- 于是很容易把：
  - `v64`
    这种只差一条 `near_tie`
    的证据轮次
  - 和
    `v65`
    这种已经明确伤到
    `guodegang` guardrail
    的失败轮次
  一起重新考古一遍。

处理：

- 已新增恢复补记日报：
  - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`
- 并同步回填：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`

后续要求：

1. 以后只要实际生成了：
   - 新 checkpoint
   - compare summary
   - 或 gate summary
   三者中的任意关键组合，
   当轮就必须至少补一份最小日报。
2. 若当轮来不及写完整复盘，
   也至少要补齐：
   - checkpoint 名称
   - train / val manifest
   - gate 结果
   - keep / drop judgement
3. 在准备起下一条分支前，
   先检查上一条是否已经同时写进：
   - 日报
   - 总览
   - 分支图；
   否则先补文档，
   不继续开新实验。

### 128. `branch_protect` selector 如果继续靠手工做集合差和手工 union manifest，后续“到底测的是哪条语义”会再次漂掉

现象：

- `v64 / v65` 使用的
  `speech_leak_exact_minus_targetfull`
  资产，
  在恢复前虽然已经有：
  - sample-id 文件
  - merged manifest
  - checkpoint / compare / gate
- 但生成过程没有正式脚本入口，
  实际上仍靠：
  - 记住源 manifest 名称
  - 记住要减哪份 targetfull selector
  - 再手工拼出 merged manifest

影响：

- 一旦后续再重做
  `0004-like speech_leak`
  的 selector / proxy，
  很容易出现两类恢复噪声：
  - 同名 selector，
    但减的不是同一份 overlap 集；
  - 同一批 ids，
    但 union 回去的 base manifest
    已经换了版本
- 这样看起来都叫
  `speech_leak_exact_minus_targetfull`，
  实际测到的却可能不是同一条语义。

处理：

- 已新增正式脚本：
  - `scripts/data/build_branch_protect_selector_assets.py`
- 已用它实际重建并核对：
  - `sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_{train,val,all}.txt`
  - `train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
  - `val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`

后续要求：

1. 以后只要继续改
   `0004-like speech_leak`
   的 selector / proxy，
   默认从脚本入口重建，
   不再手工改 sample-id 文本。
2. 任何新的 branch-protect 资产，
   至少同时登记：
   - focus proxy manifest
   - subtract selector
   - base manifest
   - 输出 sample-id / merged manifest
3. 若只是改了集合差或 union 基座，
   也要视为“实验定义变化”，
   必须写日报，
   不能沿用旧名字默认视作同一轮。

### 129. 不能再把历史上“名字都叫 on default”的 compare 报告直接当成 shared-sample 搜索输入；如果没有严格复跑到同一份 manifest，`search_synthetic_proxy_candidates.py` 可能根本找不到共同 speech rows

现象：

- 本轮准备继续重建
  `speech_leak_like (0004)`
  proxy 时，
  直接把历史：
  - `compare_v19_vs_v20_on_default`
  - `compare_v19_vs_v25_on_default`
  - 等多份 report
  喂给
  `scripts/eval/search_synthetic_proxy_candidates.py`
- 结果脚本直接报：
  - `No shared speech-only rows found across compare inputs.`

原因：

- 这些 report
  虽然名字都写着：
  - `on_default`
- 但并不等价于：
  - 它们来自严格同一批
    shared `sample_id`
- 一旦输入 compare
  不是同一份 manifest
  上的新复跑结果，
  搜索脚本就可能在：
  - shared ids
  - 或 samplewise-order-pass 行
  两层之一直接掉空。

处理：

- 本轮先补了统一搜索底座：
  - `data/synthetic/val_manifest_friend_speech_leak_search_v1.jsonl = 50`
- 再在这同一份 manifest 上
  重跑：
  - `v19 vs v20 / v24 / v25 / v29 / v30 / v32 / v35 / v64 / v65`

后续要求：

1. 以后凡是要做
   synthetic proxy 搜索，
   默认先物化一份公共 manifest。
2. 搜索输入只接受：
   - 在该公共 manifest 上
     新重跑出来的 compare report
3. 不再把：
   - 目录名相似
   - summary 都写 `default`
   视作“可以直接混用”的证据。

### 130. 即使已经有了 shared-sample 搜索底座，也不能把第一个 order-pass candidate 直接当成真 `0004` proxy；如果它不能同时压住明显错误的旧模型排序，它仍只是 candidate family

现象：

- 在新的 shared search manifest
  `val_manifest_friend_speech_leak_search_v1.jsonl`
  上，
  当前能稳定站住的 working order
  是：
  - `v35 > v25 > v24`
- relaxed 搜索得到的 top candidate
  进一步收敛成：
  - 高 overlap
  - 更高 gain
  - 低 target transient
  - 低 interference transient
  的 clean-speech family
- 物化后规模为：
  - train `12`
  - val `3`

但同一组 `3` 条 val rows
上的完整排序却是：

- `v35 > v25 > v65 > v24 > v29 > v64 > v32 > v30 > v20`

影响：

- 这说明当前 family
  虽然已经不是
  `v23 / v30`
  的旧 exact rows 重复，
  也确实抓到了一批新样本；
- 但它还没有复现
  near-real `0004`
  的完整行为，
  至少：
  - `v20` 方向仍不对
  - `v65` 仍然过强

后续要求：

1. 这类新 family
   先登记成：
   - `candidate`
   不登记成：
   - `proxy_keep`
2. 下一步若继续搜索，
   要显式加入负约束，
   例如至少避免：
   - `v65` 继续显著占优
   - `v20` 继续明显落后
3. 只有当新的 candidate
   在 shared manifest 与 near-real
   的关键排序上都更一致时，
   才考虑升格成正式
   `branch_protect` proxy。

### 131. 如果“压 `v65` 伪阳性”的约束把候选清得只剩 near-tie，再单独沿这条线继续收紧，往往会把 family 洗得太弱；这时更有效的是同时加入“把 `v20` 拉回前排”的约束，寻找 compromise candidate

现象：

- `candidate_v2_guardv65`
  已证明：
  - 单独要求
    `v24 > v65`
  确实能把明显的 `v65`
  伪阳性压掉
- 但代价是：
  - top candidate
    几乎把所有模型都压成 near-tie
  - proxy 辨识度明显变弱

本轮继续加的约束是：

- `v20 > v24`
- 并进一步测试：
  - `v20 > v65`

结果：

- 当前更好的 compromise candidate
  会收敛到：
  - 高 overlap
  - 低 target transient
  - 高 target/interference similarity
  - 中高 gain
  的 clean-speech family
- 这版已经比单独 `guard_v65`
  更有辨识度，
  且重新接回了
  `v23 speech_leak exact`
  的旧 val 锚点
  `val_000165`

后续要求：

1. 如果一个 guard candidate
   已经被洗成 near-tie，
   不要继续只沿同一条
   负约束往死里收紧。
2. 这时更该补的是：
   - “哪条旧模型顺序
      需要被拉回前排”
   这种正向恢复约束。
3. 当前 `0004-like` 搜索里，
   `candidate_v3_guardv20`
   应优先于
   `candidate_v2_guardv65` 继续细化。

### 132. 即使 real gate 已经只剩单点 fail，也不能跳过“新 proxy rows 到底有没有被训练推高”这一步；否则会把“proxy 仍 partial / mismatch”与“训练根本没吃到新 rows”混成同一种失败

现象：

- `v66`
  relative to `v32`
  的 real gate
  已经只剩：
  - `speech_leak_like_gain_floor = clear_fail`
- 但在补这轮诊断前，
  磁盘上只有：
  - real / near-real gate
  - `v19 vs v66`
    on `candidate_v3_guardv20`
    的单 compare
- 还没有直接回答：
  - `v66`
    是否真的把
    新 `candidate_v3`
    这批 synthetic rows
    往想要的方向推

风险：

- 如果缺这一步，
  后续很容易把
  `v66` 的失败
  直接脑补成：
  - “branch_protect training
     没起作用”
- 但实际也可能是：
  - aggregate synthetic proxy
    已经转正；
  - 真正还没闭环的是
    proxy 本体和 real `0004`
    的语义对齐

处理：

- 本轮新增：
  - `scripts/eval/analyze_proxy_candidate_direction.py`
- 并补跑：
  - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/summary.json`
  - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v3_guardv20_direction_analysis/summary.json`
- 现在可以明确看到：
  - 在 `candidate_v3_guardv20`
    的 3 条 val rows 上，
    aggregate 排名已是：
    - `v66 > v64 > v35 > v20 > v30 > v32 > v29 > v25 > v65 > v24 > v19`
  - `v66 - v32 = +0.051855 dB`
  - 说明 aggregate synthetic 方向
    已经被推正
- 但同时也能看到：
  - strict samplewise order-pass
    仍是 `0 / 3`
  - `v66`
    的单条 rank 分布为：
    - `7 / 10 / 1`
  - 说明当前 gain
    主要集中在单个 row，
    row-level 仍不够硬

后续要求：

1. 以后凡是说
   “某条新 proxy / selector
   训练后 real gate 仍 failed”，
   默认都补一份 focused synthetic direction diagnosis。
2. 至少同时回答两件事：
   - aggregate 上，
     candidate 相对 reference
     有没有被推高
   - row-level 上，
     gain 是不是只靠个别 row 拉动
3. 若 aggregate 已正向、
   row-level 仍很散，
   默认优先怀疑：
   - proxy coverage / semantic hardness
   而不是先怀疑
   - training plumbing 完全无效。

### 133. 给 `v66` 加 `v64` 反向 guard 时，不要先把 `v35 > v25 > v24` 这条结构约束扔掉；更该先检查的是 `v20 > v65` 这种辅助 guard 是否过强。前者一放掉，搜索很容易退回高 gain / 高 transient 的旧 strong-transient 家族

现象：

- 在 `candidate_v3`
  之后继续加：
  - `v64 > v66`
  做 follow-up 搜索时，
  先出现的是一个
  `21` 条 rows 的 near-miss：
  - `v64 > v66`
    已成立
  - 缺口只剩：
    - `v25 > v24`
- 但如果直接顺着这个 near-miss
  去放掉：
  - `v25 > v24`
  top order-pass family
  会立刻退回：
  - 更高 gain
  - 更高 target transient
  的家族
  - `v65`
    也重新变得很强

影响：

- 这说明当前真正“该先松”的，
  不一定是
  `v25 > v24`
  这种结构性旧排序；
- 更可能是：
  - `v20 > v65`
  这种后来补上的
  辅助负约束
  已经开始压掉
  更像 `v64 / v66`
  分界面的 family。

处理：

- 本轮对照后保留的是：
  - `v35 > v25 > v24`
  - `v20 > v24`
  - `v64 > v66`
- 放掉的是：
  - `v20 > v65`
- 最终得到：
  - `candidate_v4_guardv66_by_v64`
  - train `33`
  - val `10`
  - aggregate：
    - `v64 > v66 > v65 > v20 > v30 > v32 > v35 > v29 > v25 > v24`

后续要求：

1. 以后继续在
   `speech_leak_like (0004)`
   搜索里加
   “新 checkpoint guard”
   时，
   不要默认优先删掉
   `v35 > v25 > v24`
   这种老排序。
2. 先检查：
   - 哪条辅助负约束
     只是为了压伪阳性，
     现在却开始把目标 family
     一起压没。
3. 一旦发现“放掉结构约束后，
   family 退回高 gain / 高 transient
   老家族”，
   这条路默认直接判错，
   不继续升格成新 proxy。

### 134. 新 proxy candidate 如果和当前 active train / val split 几乎不重叠，只替换 selector 基本等于没训练到；这时必须先补 union manifest，再谈 objective 是否有效

现象：

- `candidate_v4_guardv66_by_v64`
  作为搜索结果本身是有信号的：
  - aggregate 上
    已形成：
    - `v64 > v66 > v65`
- 但实际把它和当前
  `v66`
  使用的 active split
  去做 overlap 后，
  结果几乎掉空：
  - vs `v42` base train：
    - `1 / 33`
  - vs `v42` base val：
    - `0 / 10`

影响：

- 这意味着如果下一轮只是把：
  - `branch_protect_focus_sample_ids`
  换成 `candidate_v4`
  但 train / val manifest
  仍沿用当前 `v42` split，
  实际上几乎等于：
  - 新 candidate rows
    根本没进训练
- 这种情况下，
  后续再看到 real gate
  没改善，
  很容易误判成：
  - objective / proxy
    本身没方向
  实际却只是：
  - manifest coverage
    没补进去

处理：

- 本轮已直接补出：
  - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
  - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`

后续要求：

1. 以后凡是把
   新 candidate / selector
   准备接进训练前，
   默认先算它与当前 active split
   的 overlap。
2. 如果 overlap 低到
   `~0`
   或只有极少数样本，
   默认不允许只换 selector
   就直接启动训练。
3. 这时应先补：
   - union manifest
   - 或新的 focused split
   再去判断训练方向。

### 135. 如果把新 proxy rows 真正 union 进 active split 后，selector 命中已经从稀命中变成高命中，但 candidate rows 自身的 aggregate 方向仍然继续变差，就不该再把问题归因于 coverage；这时更该怀疑 objective / proxy 语义本身仍是错的

现象：

- `v67`
  已经把
  `candidate_v4_guardv66_by_v64`
  真正 union
  进 active split
- `branch_protect`
  命中显著抬高到：
  - train `33 / 161`
  - val `10 / 47`
- 但在
  `candidate_v4`
  那 `10` 条 val rows 上，
  aggregate 排名反而退成：
  - `v64 > v66 > v65 > v67`
- 同时 real gate
  仍是：
  - `speech_leak_like_gain_floor = clear_fail`
  - `guodegang_absent_floor = clear_fail`

影响：

- 这说明当前不能再解释成：
  - “新 rows 其实没进训练”
- 更准确的解释应是：
  - 训练确实吃到了
    这批 rows，
  - 但当前
    `branch_protect_guard_sisdr`
    或 `candidate_v4`
    语义本身，
    仍没有把模型推向
    想要的 near-real 方向

处理：

- `v67`
  之后，
  默认不再继续做：
  - “只补 union manifest”
  - “只补 coverage”
  的同类动作
- 下一层若继续，
  默认应直接转向：
  - 检查 objective
    是否错语义 / 错号
  - 或继续做
    `candidate_v4`
    的 row-level
    semantic split / hardness 提升

后续要求：

1. 以后如果新 candidate
   已经在训练侧
   有明显命中，
   仍在自身 rows 上
   aggregate 退化，
   默认就不要再把
   “没训到”
   当主假设。
2. 这时优先检查：
   - loss 方向
   - selector 语义
   - 以及 row-level
     是否仍混入了
     对 real gate
     方向相反的子族。

### 136. 即使某条新 proxy 在 aggregate 上能稳定区分 `v64 / v66`，也不能默认它是单语义 family；如果不先做 subgroup 诊断，就会把“部分 rows 真对题、另一部分 rows 在推反”误读成一个模糊的整体 near-tie

现象：

- `candidate_v4_guardv66_by_v64`
  在 aggregate 上
  已经能稳定形成：
  - `v64 > v66 > v65`
- 但在 `v67`
  做完 union training 之后，
  如果只看整体，
  看到的只是一句：
  - `v67 - v66 = -0.034271 dB`
- 这会让人容易停留在：
  - `objective / proxy mismatch`
  这种过粗解释，
  却看不出：
  - 到底是全部 rows
    一起反向
  - 还是某个 subgroup
    单独拖坏整体。

处理：

- 本轮补了正式脚本：
  - `scripts/eval/analyze_proxy_candidate_subgroups.py`
- 并对
  `candidate_v4`
  的 `10` 条 val rows
  做了 subgroup 诊断。
- 结果表明：
  - 按
    `interference_transient_presence_share_mean`
    中位数切分时，
    `v67`
    对 high-share half
    relative to `v66`
    为：
    - `-0.086806 dB`
    - improved count `0 / 5`
  - 按
    `target_transient_presence_minus_mid_db_mean`
    中位数切分时，
    `v67`
    对 low-target-transient half
    relative to `v66`
    为：
    - `-0.072390 dB`
  - 两条危险条件交集的 `4` 条 rows 上：
    - `v66 - v64 = -0.000723 dB`
      近 tie
    - `v67 - v66 = -0.094110 dB`
- 这说明：
  - 当前真正的问题
    不只是 aggregate 没过；
  - 更是
    `candidate_v4`
    已混入一簇
    低目标瞬态 /
    高干扰瞬态占比
    的危险子族。

后续要求：

1. 以后凡是新 proxy
   aggregate 上看起来
   只是 near-tie / 小正负波动，
   默认都要补 subgroup 诊断。
2. 至少先按：
   - target transient
   - interference transient
   - target/interference similarity
   这几类连续字段
   做 median split。
3. 如果发现
   “某一半 rows 明显正向，
    另一半 rows 系统性负向”，
   默认先做：
   - semantic split / carve-out
   - hardness 提升
   不要先把它粗暴记成：
   - 整条 proxy 无效。

### 137. shared-sample 搜索 summary 里的 top candidate 如果仍保留 `all_pools / all_patterns` 默认自由度，不能直接把那组 `builder_filters` 投影到 full manifest；否则很可能在训练资产物化时撞到 search manifest 从未暴露出来的非语音源

现象：

- `synthetic_proxy_search_candidate_v5_guardv67_negative_on_friend_speech_leak_search_v1`
  的 top order-pass family
  在 shared compare 上
  合法且稳定，
  val rows 为：
  - `val_000076`
  - `val_000274`
  - `val_000469`
- 但它最顶部那组
  `builder_filters`
  只显式写了：
  - `max_interference_gain_db`
  - `max_target_transient_presence_minus_mid_db_mean`
  - `min_interference_transient_presence_minus_mid_db_mean`
  - `min_target_interference_logspec_cosine`
- 若直接把这组条件
  投影到 full train / val manifest，
  `build_metadata_focused_manifest.py`
  会读到 search manifest
  外部的非语音 interference 文件，
  实际报错包括：
  - `data_in/pure_music_dataset/无吉他.m4a`
  - `data_in/pure_music_dataset/Lightmore.m4a`

处理：

- 这次没有继续硬改脚本兜底，
  而是改用
  top-equivalent 的
  clean/full variant
  去物化：
  - `target_clean_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `overlap >= 0.75`

### 138. aggregate 上成立的负向 family 可能只是被单条硬锚点带出来；在做 proxy 解释前，必须先把交并 subset 拆开，不能把整个 family 当单语义

现象：

- `candidate_v5_guardv67_negative`
  在 val `3` 条上
  aggregate 明确满足：
  - `v64 > v66 > v65 > v67`
- 但继续和
  `candidate_v4`
  的 `carve / pruned`
  交并后，
  会发现它其实分成：
  - `v4 carve ∩ v5`
    只有：
    - `val_000469`
  - `v4 pruned ∩ v5`
    为：
    - `val_000076`
    - `val_000274`

真正的问题在于：

- `val_000469`
  同时满足：
  - `v66 - v64 = -0.025435 dB`
  - `v67 - v66 = -0.171768 dB`
  - `v66 - v65 = +0.313288 dB`
  是非常强的双信号锚点；
- 但
  `val_000076 / 000274`
  这两条 aggregate 上反而是：
  - `v66 - v64 = -0.046281 dB`
  - `v67 - v66 = +0.001157 dB`
  并不是稳定的
  `v67 negative` core

教训：

- 以后看到
  “小 family
   aggregate order-pass
   很漂亮”
  时，
  不能立刻把整包 rows
  解释成同一种 proxy 语义；
- 尤其当 family
  只有 `3~5` 条时，
  先做：
  - 和现有 family
    的交并分析
  - membership subset
    方向 summary
  再决定是否值得当成
  新 proxy 资产

处理：

- 这次补了：
  - `scripts/eval/analyze_proxy_family_overlap.py`
- 并把当前 family
  固定拆成：
  - `v4 carve only`
  - `v4 carve ∩ v5`
  - `v4 pruned only`
  - `v4 pruned ∩ v5`
- 之后默认不再把
  全量 `candidate_v5`
  直接写成
  “纯 `v67 negative` family”
  - `speech_interference_clean_pool`
  - 再叠加原先那组数值 filters
- 这条更收紧的 variant
  在 shared search manifest
  上保留了完全相同的
  `3` 条 val rows，
  但可以安全投影到 full manifest，
  最终得到：
  - `candidate_v5_guardv67_negative`
    train `12`
    / val `3`

后续要求：

1. 以后凡是从 shared-sample
   搜索 summary
   物化 full train / val 资产，
   默认先检查：
   - top candidate
     是否仍保留
     `all_pools`
     或 `all_patterns`
     这类默认自由度。
2. 如果保留了，
   不要直接套用；
   先看：
   - 是否存在 top-equivalent
     的更收紧 variant
     仍保持同一批 val rows。
3. 若存在，
   默认优先物化
   那条更收紧 variant，
   再把它记成正式资产；
   否则 full manifest
   与 shared search manifest
   的语义边界会再次漂掉。

### 139. `require-samplewise-order-pass` 只会过滤主顺序，不会自动把 extra guard 一起收紧；如果不单独补齐，strict family 仍可能混入 carry-over rows

现象：

- 在继续解释
  `candidate_v6_v4carve_only_expand`
  时，
  已知 aggregate 上满足：
  - `v66 > v64`
  - `v66 > v65`
  - `v66 > v67`
  - `v64 > v67`
  - `v20 > v24`
- 但把
  `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`
  的 `3` 条 row
  拆开看，
  只有：
  - `val_000430`
    真正逐条满足全部 guard；
  - `val_000165 / val_000331`
    至少会在
    `v66 > v65`
    或
    `v66 > v64`
    上掉线。
- 追查后确认：
  `scripts/eval/search_synthetic_proxy_candidates.py`
  里的
  `--require-samplewise-order-pass`
  只检查
  `ordered_aliases`；
  它不会把
  `--extra-order-constraint`
  一起提升到
  samplewise 层。

影响：

- 如果把此前的
  “strict / samplewise”
  结果直接当成
  row-level 已经很干净的 family，
  会高估 proxy 的纯度；
- 也会误把
  `candidate_v6`
  这种 aggregate 过关、
  但 row-level
  仍混着 carry-over 的 family
  写成
  strict core。

处理：

- 这次已补脚本参数：
  - `--require-samplewise-all-constraints-pass`
- 并补出两个统计：
  - `num_samplewise_extra_constraint_pass_rows_before_optional_filter`
  - `num_samplewise_all_constraints_pass_rows_before_optional_filter`
- 在
  `candidate_v6`
  那条 pure-negative expand
  口径下，
  真正 samplewise
  全约束过关的 shared rows
  只有：
  - `val_000239`
  - `val_000430`
- `min-count = 3`
  时直接掉空，
  说明当前并不存在
  `3+ row`
  的 strict-all clean family。

后续要求：

1. 以后凡是要把某条 proxy family
   写成
   “strict / row-level 已收敛”，
   默认先确认：
   - 用的是
     `--require-samplewise-all-constraints-pass`
     而不是只用
     `--require-samplewise-order-pass`
2. 如果 strict-all
   `min-count = 3`
   已经掉空，
   不要再把旧 aggregate family
   误写成 strict core；
   应明确区分：
   - aggregate working family
   - strict-all diagnostic core
3. 如果新的 strict-all core
   只是
   `1~2` 条 row，
   默认先把它当：
   - 诊断锚点
   而不是：
   - 立刻投影成新的训练入口

### 140. 行为上 strict-all 过关的 core，不一定会落在单一 metadata 语义里；如果只沿旧语义继续收紧，可能会把真正核心漏掉

现象：

- 在
  `candidate_v7`
  这轮 strict-all
  口径下，
  当前真正保留下来的 core
  只有：
  - `val_000239`
  - `val_000430`
- 但这两条的元数据形态并不接近：
  - `val_000239`
    - `target_transient_presence_minus_mid_db_mean = +0.631591`
    - `interference_transient_presence_minus_mid_db_mean = +1.396928`
  - `val_000430`
    - `target_transient_presence_minus_mid_db_mean = -17.009609`
    - `interference_transient_presence_minus_mid_db_mean = -3.319185`
- 也就是说：
  - 一个更像
    旧 reverse-guardrail /
    anchor 风格；
  - 一个更像
    之前
    `candidate_v6`
    的 low-transient
    pure-negative row；
  - 但它们都能在行为排序上
    同时满足
    strict-all guards。

影响：

- 如果后续还把
  strict core
  误当成
  `candidate_v6`
  那套
  low-target-transient /
  low-interference-transient
  family 的继续收紧版，
  会把
  `val_000239`
  这类真核心
  直接漏掉；
- 也会误以为
  “没找到更大 family”
  只是阈值没调好，
  而不是当前 metadata 语义
  本身还不够。

处理：

- 这次已把
  strict-core 资产正式物化：
  - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl`
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_{train,val,all}.txt`
- 并补了 overlap summary：
  - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
  - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`

后续要求：

1. 以后如果某条 strict core
   只有 `1~3` 条，
   默认先检查：
   - 它们是不是行为上同类、
     但 metadata 上异质。
2. 如果是，
   不要立刻沿旧 metadata family
   继续缩阈值；
   否则会把另一类真核心筛掉。
3. 更合适的下一步应改成：
   - 以行为 core 为锚，
     再找新的同向 rows；
   - 而不是默认把
     旧 aggregate family
     当成唯一语义模板。

### 141. strict core 的 near-miss rows 必须按“失败 guard”拆开管理；如果把不同失败签名混成一包，会把两条扩张方向重新搅糊

现象：

- 在 strict core
  `{val_000239, val_000430}`
  周围继续看 near-miss 时，
  最靠前的 rows
  并不会收敛成一条单语义 family，
  而是先分成：
  - `guardv65_only`
    - `val_000376`
    - `val_000202`
  - `guardv20_only`
    - `val_000223`
    - `val_000316`
- 两组都只差一条 guard，
  但差的不是同一条：
  - 前者只差
    `v66 > v65`
  - 后者只差
    `v20 > v24`

影响：

- 如果后续把这两组 near-miss
  继续并成一包去解释，
  会重新回到：
  - 行为上都“挺像”
  - 但到底该扩哪边
    又说不清
  的混沌状态；
- 也会误把
  `v20`
  这条 legacy guard
  仍未对齐的 rows，
  混进 strict core
  的直接扩张线上。

处理：

- 这次已补脚本：
  - `scripts/eval/analyze_proxy_strict_near_miss.py`
- 并正式物化两条单-fail 前沿：
  - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65.jsonl`
  - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20.jsonl`
- 当前默认优先级也已固定成：
  - 先追
    `guardv65_only`
  - 再看
    `guardv20_only`

后续要求：

1. 以后凡是继续做 strict-core 扩张，
   默认先按
   failed-guard signature
   分组。
2. 只差一条 guard 的 rows
   之间，
   若失败的是不同 guard，
   默认视作不同前沿，
   不要直接并包。
3. 若某组只差
   `v20 > v24`
   这类 legacy guard，
   默认单独保留，
   不并入 strict core
   的第一优先扩张线。

### 142. 放松单条 guard 后，搜索最先返回的常常只是“relaxed shell”；必须同时看 `min-count=3` 和 `min-count=2`，否则会把真正的 bridge pair 淹没掉

现象：

- 在 strict core
  周围继续追
  `guardv65_only`
  时，
  若只放松：
  - `v66 > v65`
  并保住其余四条 guards，
  当前 samplewise row universe
  会先塌成：
  - `val_000202`
  - `val_000239`
  - `val_000376`
  - `val_000430`
- 这个 `4` 条 shell
  aggregate 上
  甚至已经恢复成：
  - `v66 > v65`
  但 `min-count=3`
  搜索仍不会进一步 carve，
  只会不断返回整包 shell。

影响：

- 如果只看
  `3+ row`
  结果，
  很容易误以为：
  - `guardv65_only`
    还是只能整体并包解释；
- 从而看不见更关键的事实：
  - 真正最先被 metadata
    稳定挑出来的 bridge
    其实是：
    - `{val_000376, val_000430}`
  - 而不是：
    - `{val_000202, val_000376}`
    - 或 `{val_000202, val_000239}`。

处理：

- 这次已补：
  - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min3_on_friend_speech_leak_search_v1/summary.json`
  - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min2_on_friend_speech_leak_search_v1/summary.json`
- 并把两层资产分开物化：
  - relaxed shell：
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell.jsonl`
  - bridge pair：
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`

后续要求：

1. 以后凡是做“放松单条 guard”的 frontier 搜索，
   默认同时检查：
   - `min-count=3`
   - `min-count=2`
2. 若 `min3`
   只反复返回整包 relaxed shell，
   不要立刻把该 shell
   当成新 family。
3. 应继续看：
   - `min2`
     下最先稳定出现的 pair
   才能判断：
   - 哪条 row
     真正在接桥；
   - 哪条 row
     只是被 relaxed shell
     一起裹进来。

### 143. 强 seed pair 会把坏第三条在 aggregate 上洗白；`seed + 1` 过全约束，不等于拿到了 row-level clean family

现象：

- 以 bridge pair
  `{val_000376, val_000430}`
  做 seed 时，
  当前最近的第三条 row
  是：
  - `val_000331`
- 但 `val_000331`
  自己 row-level
  仍 fail：
  - `v66 > v65`
  - `v66 > v67`
  - `v64 > v67`
- 只是把它和 seed pair
  并成：
  - `{331,376,430}`
  后，
  aggregate gaps
  会重新全部转正。

影响：

- 如果只盯着
  `seed + 1`
  aggregate 是否过关，
  很容易误把：
  - 被强 seed pair
    均值冲淡后的
    aggregate-pass row
  当成：
  - 真正 row-level clean
    的第三成员；
- 这会让文档再次把
  aggregate family
  和 row-level family
  写混。

处理：

- 这次已补脚本：
  - `scripts/eval/analyze_proxy_seed_expansion.py`
- 并把两层东西分开资产化：
  - row-level bridge：
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`
  - aggregate-only bridge trio：
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331.jsonl`

后续要求：

1. 以后凡是做 seed-anchored 扩张，
   默认同时记录：
   - candidate 的 row-level failed guards
   - `seed + 1`
     的 aggregate 结果
2. 若某第三条 row
   只有 aggregate pass，
   但自身 row-level
   fail 多条 guards，
   默认写成：
   - aggregate-only extension
   不写成：
   - clean family member
3. generic aggregate search
   若再次塌回旧 family，
   默认不要拿它
   覆盖 seed-anchored
   这层更细的解释。

### 144. `seed+1` aggregate 排名会优先把“被强 seed 洗白的远端 row”顶上来；若不同时按 failed-signature 和 distance 拆开，bridge 第三条会再次选错

现象：

- 在
  `{val_000376, val_000430}`
  这对 bridge seed 上，
  很多 candidate
  都能在：
  - `seed + 1`
    aggregate
    里重新 full-pass；
- 但这些 candidate
  并不属于同一条前沿，
  而是至少混着：
  - bridge-like 三失败签名
    `v66>v65 | v66>v67 | v64>v67`
  - `guardv20_only`
  - `guardv65_only`
  - strict-core 自身
- 更关键的是，
  在 bridge-like 同签名里：
  - 最近的第三条是：
    - `val_000331`
    - joint distance `0.975332`
  - 但 strongest aggregate
    反而是：
    - `val_000235`
    - joint distance `6.092051`

影响：

- 如果只按：
  - `aggregate_min_constraint_gap_db`
  - 或 top aggregate candidate
  选第三条，
  会优先捞到：
  - `val_000223`
    这类其实属于
    `guardv20_only`
    的跨前沿 row；
  - 或
    `val_000235`
    这类距离很远、
    只是被强 seed pair
    在均值上洗白的 washout row。
- 这样一来，
  文档虽然表面上还是在写
  “bridge 扩张”，
  实际却已经把：
  - 第二前沿
  - 远端 washout
  - bridge 邻域
  重新并成一包。

处理：

- 已增强：
  - `scripts/eval/analyze_proxy_seed_expansion.py`
- 新增输出：
  - `top_nearest_aggregate_pass_expansions_by_joint_distance`
  - `aggregate_pass_signature_summaries`
- 并把结论集中落盘到：
  - `reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`

后续要求：

1. 以后做任何 `seed+1` 扩张时，
   不能只看 aggregate 排名；
   必须至少同时看：
   - candidate 自身 failed-signature
   - candidate 到 seed center 的 distance
2. 若同一 failed-signature 内，
   出现：
   - `aggregate 更强`
   但
   - distance 明显更远
   的 row，
   默认先写成：
   - washout-only aggregate candidate
   不写成：
   - 更优第三条
3. 若 top aggregate candidate
   落在别的前沿，
   例如：
   - `guardv20_only`
   则默认保留在原前沿，
   不并入当前 bridge 扩张线。

### 145. aggregate-only trio 不能因为“加进 seed 后还存在 aggregate-pass 第四条”就被误写成新 family；如果第四条一换 seed 就漂到别的前沿，说明 trio 只是局部洗白结构，不是稳定中心

现象：

- 已知：
  - `{val_000331, val_000376, val_000430}`
    在 aggregate 上
    full-pass；
- 但进一步把它当成 soft seed
  去看第四条时，
  最近 non-seed rows
  立刻变成：
  - `val_000075`
  - `val_000305`
  - `val_000269`
  它们都不再属于
  原 bridge-like 三失败签名；
- 最近的 aggregate-pass rows
  也优先落在：
  - `val_000076`
  - `val_000316`
  - `val_000401`
  - `val_000223`
  这些别的前沿上；
- 真正仍留在 bridge-like
  三失败签名里的下一条 row
  已经只剩：
  - `val_000022`
  - distance `2.854296`
  - aggregate min gap `+0.000087 dB`

影响：

- 如果只看到：
  - trio seed 下
    仍然存在 aggregate-pass 第四条
  很容易误判成：
  - `{331,376,430}`
    正在长成一个新的 `4` 条 family；
- 但实际上更准确的解释是：
  - 一旦把 `331`
    升成 seed，
    排名就会迅速漂到别的前沿；
  - 同签名的真正第四条
    既远、又几乎没有 margin；
  - 所以这条 trio
    只是局部 aggregate washout 结构，
    不是稳定 family 中心。

处理：

- 已补分析输出：
  - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_trio_seed_expansion_analysis/summary.json`
- 并把结论集中落盘到：
  - `reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`

后续要求：

1. 以后凡是某条 aggregate-only trio
   想升级成 soft seed family，
   默认至少要再检查：
   - 升 seed 后
     最近第四条
     是否仍留在同一 failed-signature
   - 同签名第四条
     是否还保有明确正 margin
2. 若升 seed 后，
   候选榜优先漂到别的前沿，
   同签名第四条
   又只剩：
   - 很远
   - margin 贴零
   的 row，
   默认应把这条 trio
   固定写成：
   - aggregate-only structure
   不写成：
   - emergent family
3. 默认不要再从这种 trio
   往外推第四条；
   应回到更干净的
   row-level pair
   继续看边界扩张。

### 146. metadata-near bridge coverage 与 behavior-near bridge family 不是一回事；active split 里即使出现大量贴近 `{376,430}` 的 train rows，也可能整体塌成 `v67 / v65` 主导的混合区

现象：

- 用 `{val_000376, val_000430}`
  做 seed，
  投影到当前 active split 后，
  最近的 top10 rows
  并不是：
  - `331`
  加若干同签名 val row；
  而是：
  - `9` 条 train
  - `1` 条 val
    `val_000331`
- 这批 top10
  metadata 上很贴近 bridge pair，
  但实际 compare 后，
  aggregate 排序却是：
  - `v67 > v65 > v66 > v64 > v20 > v24`
- 关键失败点是：
  - `v66 > v64 = +0.010333 dB`
    只弱正；
  - `v66 > v65 = -0.033064 dB`
    直接失败；
  - `samplewise_extra_constraint_pass = 0 / 10`

更关键的新事实：

- 这批 top10
  会稳定裂成三组：
  - `v66top`
    - `train_000597`
    - `train_001599`
  - `v67top_v66near`
    - `train_001978`
    - `train_001991`
    - `train_000737`
    - `train_001079`
  - `v65top_tail`
    - `train_001279`
    - `train_001219`
    - `train_000432`
    - `val_000331`

影响：

- 如果只因为：
  - “active split 上有很多 metadata-near rows”
  就把它整包当成
  bridge family
  或 bridge projection proxy，
  会立刻把：
  - `v67` 中间带
  - `v65` 负向尾部
  - 甚至已知 absent-like 旧资产
  一起混进去；
- 其中最危险的信号是：
  - `train_001279`
    这类已知 absent-like row
    就在 top10 里；
  - `val_000331`
    也并没有落在
    `v66` 领先带，
    而是掉进：
    - `v65top_tail`

处理：

- 已新增：
  - `scripts/eval/analyze_manifest_seed_neighbors.py`
- 已补输出：
  - `reports/eval/active_split_bridgepair_neighbor_analysis/summary.json`
  - `reports/eval/bridgepair_active_metadata_neighbor_top10_direction_analysis/summary.json`
- 并把 top10 与三条行为分层资产
  正式物化并记录到：
  - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_neighbor_behavior_probe.md`

后续要求：

1. 以后凡是把某条 seed family
   从 shared val
   投影到 active split / full train 时，
   不能把：
   - metadata-near coverage
   自动解释成：
   - behavior-near family
2. 只要 active-neighbor
   一做 compare
   就裂成多组，
   默认先把它记成：
   - behavior-mixed diagnostic buffer
   不记成：
   - 新 proxy
   或：
   - 新训练入口
3. 若某个 aggregate-only row
   例如：
   - `val_000331`
   在 active-split 投影里
   掉进：
   - `v65top_tail`
   这类负向尾部，
   默认要下调其“可外推性”解释，
   不能再把它沿 train 侧
   继续当成第三条中心。

### 147. 从少量正例 metadata 往 active split 拉宽缓冲时，如果不先显式拆掉 nonfull / absent pattern，宽版 carve 很容易立刻被 absent-like 资产劫持；同一条 carve 在 `target_full` 与 nonfull 混合口径下可能会给出相反 aggregate 结论

现象：

- 以 active-neighbor 里的
  `v66top`
  两条：
  - `train_000597`
  - `train_001599`
  为起点，
  用：
  - `target_transient_presence_share_mean <= 0.008`
  - `interference_transient_presence_minus_mid_db_mean <= -1.0`
  拉出宽版 active microbuffer：
  - train `7`
  - val `2`
- 但这条宽版 `v66top_v1`
  一混入：
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
  aggregate 就立刻塌成：
  - `v65 > v64 > v66`
- 而同一条 carve
  一旦先收窄到：
  - `target_full`
  aggregate 又会恢复成：
  - `v66 > v64 > v67 > v20 > v65`
  且 full extra constraints
  全部 aggregate pass

更关键的是：

- 宽版里直接混入了：
  - `train_000405`
  - `train_001491`
  这类已知 absent-like
  `exact_nontargetfull`
  旧资产；
- 也就是：
  - 宽版坏掉
    不是因为正例本身没信号，
  - 而是因为 nonfull / absent
    污染直接把 aggregate
    拖向了：
    - `v65`
      一侧

影响：

- 如果只看到宽版 carve
  aggregate 失败，
  很容易误判成：
  - 这条 metadata carve
    整体没信号；
- 但当前更准确的解释是：
  - carve 对于
    `target_full`
    仍有局部信号；
  - 真正必须先显式拆掉的
    是：
    - nonfull / absent pattern
    污染；
- 这类情况如果不写清，
  后面很容易把：
  - “宽版失败”
  与：
  - “full-only 小缓冲成立”
  写成互相矛盾的两句结论。

处理：

- 已补宽版与 `target_full` 版
  两层资产、compare 与方向汇总到：
  - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_targetfull_split.md`

后续要求：

1. 以后凡是从少量正例 rows
   反推 metadata carve
   到 active split，
   默认至少同时给出：
   - 宽版
   - `target_full` 版
   两层诊断；
   不要只看混合口径 aggregate。
2. 若宽版里混入：
   - absent-like 旧资产
   或：
   - nonfull pattern
   后 aggregate 方向翻转，
   默认先把问题归因到：
   - pattern 污染
   而不是：
   - 正例 carve 本身完全无效。
3. `target_full` 版即便 aggregate 全过，
   若 samplewise 仍明显不足，
   也只能写成：
   - aggregate-pass microbuffer
   with noisy carry-over
   不写成：
   - row-level clean family。

### 148. `target_full` 微缓冲里若存在单条 carry-over，会显著稀释 aggregate gap；先剥掉 carry-over 再看 core，可能会直接把“勉强可保留的小缓冲”收紧成明确的 core trio

现象：

- 在上一轮
  `target_full` 微缓冲里，
  当前样本为：
  - `train_000597`
  - `train_001599`
  - `train_001843`
  - `val_000430`
- aggregate 上虽然已经是：
  - `v66 > v64 > v67 > v20 > v65`
  且 full extra constraints
  全过，
  但：
  - `samplewise extra pass = 1 / 4`
- 逐条拆开后发现：
  - `train_001843`
    是唯一 rank 掉到：
    - `4`
    的 row；
  - 去掉它后，
    core trio
    `{train_000597, train_001599, val_000430}`
    aggregate 立即进一步变硬：
    - `v66 > v64`
      从：
      - `+0.014670 dB`
      提升到：
      - `+0.030334 dB`
    - `v66 > v65`
      从：
      - `+0.114106 dB`
      提升到：
      - `+0.181224 dB`

影响：

- 如果只停在
  `4` 条 target_full 微缓冲
  这一层，
  很容易把：
  - 真正 core 的三条
  和：
  - 单条 carry-over
  混写成同纯度成员；
- 这会让后续判断显得总像：
  - 有点信号
  但又不够硬；
  实际上更准确的解释可能是：
  - core 已经成形；
  - 只是被一条 carry-over
    在 aggregate 上稀释了 margin。

处理：

- 已把 core 进一步收窄并落盘到：
  - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_core_trio.md`

后续要求：

1. 以后只要出现：
   - `target_full` 微缓冲
     aggregate 成立，
   但 samplewise 仍偏弱，
   默认先查：
   - 是否只有 `1` 条
     明显掉队的 carry-over
2. 若去掉该 carry-over 后，
   aggregate gap
   明显变硬，
   默认把剩余集合升级成：
   - core trio / core subset
   单独管理；
   而不是一直停在
   “带 carry-over 的小缓冲”。
3. 但即使 core trio
   aggregate 全过，
   只要 train 侧
   还共享同一条 row-level 漏点，
   当前仍只能写成：
   - aggregate-pass core
   不写成：
   - row-level clean family。

### 149. direction summary 如果在第一条 failed guard 就提前返回，会把同一 row 后面的 fail 静默吞掉；这会把 shared leak 误写得比真实更窄

现象：

- 本轮继续复盘
  `core trio`
  `{train_000597, train_001599, val_000430}`
  时，
  先前 summary 里
  两条 train rows
  都只显示：
  - `v64 > v67`
    fail
- 但回到 raw compare
  再核对后发现，
  它们实际上还同时 fail：
  - `v20 > v24`

原因：

- `scripts/eval/analyze_proxy_candidate_direction.py`
  里的：
  - `order_pass(...)`
  - `extra_constraints_pass(...)`
  原先都会在遇到第一条
  `gap <= 0`
  后立刻返回；
- 结果就是：
  - overall pass / fail
    虽然没错；
  - 但 summary 里
    `extra_constraint_gaps_db`
    只保留了
    “失败前缀”，
    后面的 failed guards
    会被静默吞掉

影响：

- 如果直接用这种 summary
  去判断
  family / shell
  的 shared leak，
  很容易把：
  - 多条旧 guard
    共同失败
  误写成：
  - 只差最先出现的
    那一条
- 本轮就出现了这个问题：
  - `core trio`
    train 侧
    原本被写成：
    - shared `v64 > v67` leak
  - 但更准确的真实口径应是：
    - shared
      `v64 > v67`
      `+`
      `v20 > v24`
      dual leak

处理：

- 本轮已修正：
  - `scripts/eval/analyze_proxy_candidate_direction.py`
- 当前做法改成：
  - 先把所有 constraint gaps
    全部记录下来；
  - 最后再统一返回：
    - overall pass / fail
- 并已重跑：
  - `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`

后续要求：

1. 以后任何 direction / overlap / family summary，只要要给出 failed constraints 细节，就不能再用“首个 fail 即返回”的 helper。
2. 若某条 row 的 per-sample fail 解释和 raw compare 直读不一致，默认优先检查 summary helper 是否把后续 guards 截断了。
3. 只要涉及 shared leak 归因，默认至少核对一次：
   - raw compare gap
   - summary 里的 full constraint list
   两边是否一致；
   确认之后再下 family 级结论。

### 150. 某条 train-side 壳层就算内部签名很整齐，也不能默认把它当成可扩张 family；如果一做邻域扩张就立刻漂进多种更坏签名，它更可能只是 train-only diagnostic ring

现象：

- 本轮把
  dual-leak shell
  `{train_000597, train_001477, train_001599, train_000865}`
  单独物化后，
  它内部确实很整齐：
  - 全部共同 fail：
    - `v64 > v67`
    - `v20 > v24`
- 但继续拿它做 seed
  去排
  `active_targetfull_clean`
  邻域时，
  最近邻并没有继续留在
  同一条 dual-leak signature 上，
  而是立刻裂成：
  - `val_000376`
    这种：
    - `v66 > v65`
      单漏
  - `train_001494`
    / `train_001079`
    这种：
    - `v66 > v67`
      插队
  - `train_001181`
    / `val_000075`
    这种：
    - `v66 > v64`
      或
      `v66 > v65`
      反向回顶

影响：

- 如果只因为：
  - “shell 内部签名一致”
  就继续把它当成
  family seed，
  很容易误以为：
  - 再往外扩几条
    也许就能长成新 family
- 但当前更准确的现实是：
  - 这类壳层
    可能只是
    `core`
    与更外层 mixed frontier
    之间的一层
    局部诊断带；
  - 它的意义在于说明：
    - 哪几条旧 guard
      会一起漏
  - 而不是说明：
    - 这里存在一个
      可继续扩张的稳定家族

处理：

- 本轮已把这条结论落盘到：
  - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_dualleak_shell_neighbor_drift.md`
- 并已明确把 dual-leak shell
  从“可能的 mirror 外环”
  下调成：
  - train-only diagnostic ring

后续要求：

1. 以后凡是发现某条 train-only shell 时，默认还要再做一次 seed-neighbor 扩张，确认最近邻是否继续停在同签名上。
2. 若最近邻立刻漂到：
   - bridge / guardv65
   - `v67`
   - `v64 / v65`
   等多种更坏前沿，
   默认把该 shell 写成：
   - diagnostic ring
   不写成：
   - expandable family
3. 这种壳层的默认作用应是：
   - 帮助解释旧 guard 为什么一起漏；
   而不是：
   - 继续向外找第 `5 / 6 / 7` 条成员。

### 151. 对两条旧 guard 做 pair bucketization 时，`pass_both` 也不能默认解释成“更接近目标核心”；在本项目里它反而可能整体塌向别的 fully-pass frontier

现象：

- 本轮把
  `active_targetfull_clean`
  按：
  - `v64 > v67`
  - `v20 > v24`
  切成四桶后，
  直觉上很容易先盯：
  - `pass_both`
  这桶，
  觉得：
  - “两条旧 guard 都过了，
     应该更接近 bridge active core”
- 但实际 focused direction
  完全相反：
  - `pass_both`
    aggregate 排序是：
    - `v65 > v64 > v20 > v66`
  - `v66 > v64 = -0.037591 dB`
  - `v66 > v65 = -0.059018 dB`
- 更关键的是：
  - `core trio`
    与这桶 overlap
    只有：
    - `val_000430`
  - dual-leak shell
    与这桶 overlap
    为：
    - `0`

影响：

- 如果只看到：
  - “这两条 guard 都过”
  就把该桶当成：
  - 更干净的候选 family
  或：
  - 下一步训练入口
  会把解释重新带偏；
- 因为这类 pair bucket
  表达的只是：
  - 两条指定旧 guard
    的 pass/fail 状态
  不是：
  - 完整行为排序
  也不是：
  - 相对当前核心的语义接近度

处理：

- 本轮已把这条反例正式落盘到：
  - `reports/daily/2026-03-21_candidate_v7_active_guardpair_bucketization.md`
- 并把四桶 focused direction
  全部补齐，
  作为以后复用的 stop-rule 证据

后续要求：

1. 以后做 guard-pair bucketization 时，不能把 `pass_both` 自动解释成“最好的一桶”。
2. pair bucket 必须再配 focused direction，至少确认 aggregate top alias 是谁，再决定它到底属于哪条 frontier。
3. 若 `pass_both` 整体已经塌向：
   - `v65`
   - `v64`
   - 或别的 fully-pass frontier，
   默认要把它从当前 family 扩张线里剥掉，
   不再继续沿这桶往下找成员。

### 152. 在同一条 `fail_both` 大桶里，`v66-top` 和 `v67-top` 的真正分界不一定是 `v66>v64`；更常见的是两边都能压住 `v64`，但只有一边还能挡住 `v67`

现象：

- 本轮把
  `fail_both`
  大桶
  按 top alias
  拆开后，
  得到：
  - `v66-top = 4`
  - `v67-top = 34`
- 直觉上很容易先把分界
  解释成：
  - `v66-top`
    是因为
    `v66 > v64`
    更强
- 但实际 focused direction
  正好相反：
  - `v66-top 4`
    的
    `v66 > v64 = +0.129529 dB`
  - `v67-top 34`
    的
    `v66 > v64 = +0.187917 dB`
- 真正拉开两边的是：
  - `v66-top 4`
    仍有：
    - `v66 > v67 = +0.050005 dB`
  - `v67-top 34`
    已变成：
    - `v66 > v67 = -0.296784 dB`

影响：

- 如果后续还把这类大桶
  内部分界
  简化写成：
  - `v66` 有没有压住
    `v64`
  会错过真正关键的行为变化；
- 因为这里更核心的问题是：
  - 两边都还可能保留
    `v66 > v64`
  - 但只有内核那几条
    还没有让
    `v67`
    接管排序

处理：

- 本轮已把这条结论落盘到：
  - `reports/daily/2026-03-21_candidate_v7_failboth_v66_vs_v67_split.md`
- 并补了：
  - `reports/eval/active_targetfull_clean_failboth_topv66_direction_analysis/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_topv67_direction_analysis/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_topv66_vs_topv67_analysis/summary.json`

后续要求：

1. 以后凡是某条大桶内部还要继续拆内核 vs 外层，默认至少同时看：
   - `focus vs reference`
   - `focus vs strongest competitor`
   不要只看前者。
2. 如果外层 rows 仍然保有：
   - `focus > reference`
   但 top alias 已切到：
   - competing alias
   默认应把这层解释成：
   - competitor takeover frontier
   而不是：
   - 参考轴回退。
3. 对当前这条线，
   默认把 dual-leak shell
   的特殊性固定写成：
   - still blocks `v67`
   不写成：
   - stronger `v66 > v64`
   core。

### 153. 当一组内核 rows 与外层 frontier 已明显分层后，不能再执着于寻找“单字段阈值解释”；如果最强单字段仍会误收一串稳定边界样本，就该把这条线正式定性成多因子共驱动

现象：

- 本轮继续把
  dual-leak shell
  `v66-top 4`
  与
  `v67-top 34`
  做成单字段阈值扫描；
- 结果即便要求：
  - `4 / 4`
    dual-leak shell
    全覆盖，
  当前最强单字段：
  - `interference_transient_presence_minus_mid_db_mean <= 2.428970`
  仍会误收：
  - `7`
    条 `v67-top`
- 第二强单字段：
  - `target_interference_logspec_cosine >= 0.671519`
  也仍会误收：
  - `8`
    条 `v67-top`
- 并且：
  - `train_001079`
  - `train_001494`
  会在
    `5 / 5`
    个字段阈值下
    全部伪装成
    `v66-top`

影响：

- 如果这种时候还继续追问：
  - “到底有没有一个单字段阈值”
  很容易把精力继续耗在
  不存在的简单解释上；
- 当前更准确的现实是：
  - 内核与外层的分界
    已经不是单 trigger，
  - 而是一组字段
    同时变化后，
    才把排序彻底推向：
    - `v67-top`

处理：

- 本轮已把这条 stop-rule
  证据落盘到：
  - `reports/daily/2026-03-21_candidate_v7_failboth_single_trigger_scan.md`
- 并新增：
  - `reports/eval/active_targetfull_clean_failboth_single_field_trigger_scan/summary.json`

后续要求：

1. 当最强单字段在 full-recall 口径下仍会误收一串稳定边界样本时，默认停止继续找“单字段解释”。
2. 这时应把问题正式改写成：
   - multi-factor co-driven split
   而不是：
   - hidden single trigger
3. 对当前这条线，
   默认把：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   - `train_001589`
   - `val_000182`
   记成：
   - persistent borderline rows
   用于后续个例诊断；
   不再把它们误写成：
   - 即将并入 dual-leak shell
   的新成员。

### 154. 当一串 persistent borderline rows 已经被挑出来后，不能默认把它们当成同一种“近内核边界带”；必须继续用 joint-distance 和 constraint-distance 把 metadata-only 假边界样本剔出去

现象：

- 上一轮单字段 full-recall 阈值
  共挑出了：
  - `train_001079`
  - `train_001494`
  - `train_000697`
  - `train_001589`
  - `val_000182`
  这 `5` 条 persistent borderline rows；
- 但本轮继续把 dual-leak shell
  当 seed 对 `fail_both`
  全量外层做
  joint-distance 排序后发现：
  - `train_001494`
    `#1`
  - `train_001079`
    `#2`
  - `train_001589`
    `#3`
  - `train_000697`
    `#9`
  的确都贴着 shell；
- 唯独：
  - `val_000182`
  已直接掉到：
  - `#39 / 39`
  而且：
  - `metadata_distance_z = 2.616320`
  - `constraint_distance_z = 14.799924`

影响：

- 如果这时候还把这 `5` 条
  当成一个同质组，
  会把：
  - 真正贴着 shell 的
    train-side edge band
  和：
  - 只是 metadata 外观相似、
    但方向上完全不是
    near-shell 的 val outlier
  混在一起；
- 这会把后续个例诊断
  再次带回
  “metadata 看起来像，
  所以应该是一类”
  的假解释。

处理：

- 本轮已把这条拆分证据
  落盘到：
  - `reports/daily/2026-03-21_candidate_v7_failboth_borderline_case_split.md`
- 并新增：
  - `reports/eval/active_targetfull_clean_failboth_topv67_vs_dualleak_seed_expansion/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_persistent_borderline_case_analysis/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_persistent_borderline_nearshell_direction_analysis/summary.json`

后续要求：

1. 以后遇到 persistent borderline rows，默认先再补一层：
   - joint-distance
   - metadata-distance
   - constraint-distance
   三向拆分，
   不直接把单字段误收名单
   当成最终边界带。
2. 对当前这条线，
   默认只把：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   - `train_001589`
   写成：
   - train near-shell edge band
3. `val_000182`
   默认单独写成：
   - metadata-only borderline outlier
   不再和上面 `4` 条
   混写。

### 155. 如果 near-shell edge band 里已经混入了额外失败签名的 singleton，直接看整包均值会把真正的首发 takeover 机制看反；先按 failed-constraint signature 拆开，再解释字段漂移

现象：

- 上一轮把：
  - `train_001079`
  - `train_001494`
  - `train_000697`
  - `train_001589`
  合写成：
  - near-shell edge band `4`
- 用整包 `4`
  去看均值时，
  很容易得出：
  - `interference_transient_presence_minus_mid_db_mean`
    相对 shell 变高
  - 因而像是
    “更高 interference transient
       把 row 推到
       `v67-top`”
- 但本轮把其中
  `train_001589`
  单独拆出去后发现：
  - 真正的 pure `v67` takeover edge `3`
    相对 shell
    其实是：
    - 更弱 gain
    - 更早 overlap
    - 更低 cosine
    - 更低的
      `interference_transient_presence_minus_mid_db_mean`
  - 整包 `4`
    均值里那条
    “interference transient 变高”
    主要就是被
    `train_001589`
    这条
    `v67 + v65`
    singleton
    拖上去的

影响：

- 如果不先拆签名，
  会把：
  - pure `v67` takeover
    的首发机制
  误写成：
  - 更高 interference transient
    takeover
- 这样会把：
  - `v67`
    第一步先接管什么样的 row
  和：
  - `v65`
    什么时候也一起进场
  两个阶段重新混成一句话

处理：

- 已把：
  - `train_001079`
  - `train_001494`
  - `train_000697`
  单列成：
  - pure `v67` takeover edge `3`
- 并把：
  - `train_001589`
  单列成：
  - `v67 + v65`
    takeover singleton
- 对应落盘到：
  - `reports/daily/2026-03-21_candidate_v7_failboth_nearshell_case_diagnosis.md`
  - `reports/daily/2026-03-21_candidate_v7_failboth_pure_v67_takeover_case_diagnosis.md`

后续要求：

1. 以后只要某个 small edge band 内部已经出现额外 failed constraint，就不要直接用整包均值解释“首发漂移机制”。
2. 默认先按 failed-constraint signature 拆成：
   - pure takeover 主型
   - 额外 frontier 进入的 singleton / tail
   再看字段漂移。
3. 尤其当某条 singleton 会额外翻掉：
   - `v66 > v65`
   这类关键 guard 时，
   它必须单独写，
   不能再和 pure `v67` takeover
   并写成同一个边界带。
