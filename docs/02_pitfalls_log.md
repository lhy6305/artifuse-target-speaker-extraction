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

### 153. 对 train-side pure frontier 做 metadata-rich 近邻搜索时，如果不先把 val rows 剥掉，`val_000182` 这类 metadata-only outlier 会重新挤进 top-k；而在 pure `v67` takeover` 的最近 train 邻域里，真正区分 pure-signature 与 `v65` drift 的也不是“低 transient 是否还在”，而是 `v66>v64` 保护带有没有先被磨平

现象：

- 本轮围绕：
  - `train_001079`
  - `train_001494`
  - `train_000697`
  跑 metadata-rich 近邻后，
  如果直接把：
  - train
  - val
  混在一起看，
  top-k 会重新混进：
  - `val_000182`
  - `val_000396`
  - `val_000041`
- 其中：
  - `val_000182`
    依旧表现为：
    - metadata 看着不远
    - 但 direction 彻底失真
  - `val_000396`
    甚至已经变成：
    - `v66 < v64`
    - `v66 < v65`
- 改成 train-only 后，
  pure trio 最近邻才稳定裂成：
  - shell-like `v66-top 3`
  - pure-signature `v67-top 5`
  - `v65` drift `v67-top 4`
- 更关键的是：
  - pure-signature `v67-top 5`
    相对 pure trio
    已经出现：
    - `interference_transient_presence_minus_mid_db_mean = +5.666825`
    - `interference_transient_presence_share_mean = +0.134391`
    但仍保住：
    - `v66 > v64`
    - `v66 > v65`
  - `v65` drift `v67-top 4`
    则更接近：
    - `interference_transient_presence_minus_mid_db_mean = +6.529567`
    - `interference_transient_presence_share_mean = +0.153944`
    同时：
    - `v66 > v64`
      均值只剩：
      - `+0.007218`
    - `v66 > v65`
      已翻到：
      - `-0.036646`

影响：

- 如果不先拆掉 val，
  会把：
  - metadata-only false neighbor
  误当成：
  - pure frontier 最近 train 邻居
- 如果继续把 pure `v67` takeover
  写成：
  - 低 transient 的一层
  就会错过真正的分界；
  因为 pure-signature 邻居
  已经可以带着很高的
  interference transient
  继续保住：
  - `v66 > v65`
- 当前更危险的误写是把：
  - transient 升高
  直接当成：
  - `v65`
    已经开始进场

处理：

- 新增脚本：
  - `scripts/eval/analyze_proxy_case_neighbors.py`
- 新增 summary：
  - `reports/eval/active_targetfull_clean_failboth_pure_v67_neighbor_diagnosis/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_pure_v67_neighbor_diagnosis_train_only/summary.json`
- 新日报：
  - `reports/daily/2026-03-23_candidate_v7_pure_v67_neighbor_diagnosis.md`

后续要求：

1. 以后只要诊断 train-side pure frontier，默认先做 train-only neighbor search，再决定是否补看 val。
2. 不要再把：
   - “interference transient 还低”
   当成 pure `v67` takeover 的必要条件。
3. 当前更该优先跟的边界应写成：
   - `v66 > v64`
     是否先被磨到接近 `0`
   - 随后
     `v66 > v65`
     是否一起翻负
   而不是继续围着
   单个 transient 字段打转。

### 154. 当 pure-signature `v67-top` 与 `v65` drift 都已经进入高 interference-transient 区间后，再继续把“transient 变高”当作两组分界，会把真正先塌的 `v66>v64` 保护带忽略掉

现象：

- 本轮把 mixed ring
  继续拆成：
  - pure-signature `v67-top 5`
  - `v65` drift `v67-top 4`
  后，
  两组都已经有：
  - 较高的
    `interference_transient_presence_minus_mid_db_mean`
  - 较高的
    `interference_transient_presence_share_mean`
- 具体均值为：
  - pure-signature `5`
    - `interference_transient_presence_minus_mid_db_mean = 5.294541`
    - `interference_transient_presence_share_mean = 0.423214`
  - `v65` drift `4`
    - `interference_transient_presence_minus_mid_db_mean = 6.157284`
    - `interference_transient_presence_share_mean = 0.442767`
- 但真正先翻掉的不是：
  - `v66 > v67`
    再变差很多
  而是：
  - pure-signature `5`
    仍有：
    - `v66 > v64 = +0.065665`
    - `v66 > v65 = +0.164763`
  - `v65` drift `4`
    已掉到：
    - `v66 > v64 = +0.007218`
    - `v66 > v65 = -0.036646`

影响：

- 如果继续把：
  - transient 升高
  直接写成：
  - `v65`
    进场原因
  会把 pure-signature `5`
  也误判成 drift；
  因为它们本身已经能带着较高 transient
  继续保住：
  - `v66 > v65`
- 真正危险的误写是：
  - 看到两组都很吵
  就忘了先去看
  `v66 > v64`
  这层缓冲还剩多少

处理：

- 已新增：
  - `scripts/eval/analyze_proxy_group_split.py`
- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_neighbor_ring_split/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_neighbor_ring_split.md`

后续要求：

1. 以后诊断 pure-signature vs drift 时，默认先看：
   - `v66 > v64`
   - `v66 > v65`
   两条 margin，再看 transient。
2. 不要把：
   - “两组 transient 都高”
   误写成：
   - “两组没有结构差异”；
   差异可能早就转移到
   guard margin 上了。
3. `train_001589`
   当前默认直接归入：
   - `v65` drift
   不再作为 pure edge
   留作开放问题。

### 155. 当 mixed ring 已经拆到纯 `v67-top` 与 `v65` drift 两组后，如果还继续默认往 raw metadata 上找单字段 hard carve，很容易忽略这层 ring 里真正稳定联动的是 `v66>v64` 和 `v66>v65` 两条模型 margin，而不是哪一个 duration / gain / transient 字段

现象：

- 本轮把 ring `9`
  条样本按
  `v66 > v64`
  做排序后，
  最明显的联动是：
  - `corr(v66>v64, v66>v65) = +0.5021`
- 其余字段都偏弱：
  - `target_duration_sec = +0.0028`
  - `reference_duration_sec = -0.2362`
  - `interference_gain_db = -0.2443`
  - `start_offset_sec = +0.1786`
  - `cosine = +0.0873`
  - `interference_transient_mean = -0.1387`
- 按中位数
  `0.044802`
  切开后：
  - low-buffer `5`
    的
    `v66 > v65 = -0.007487`
  - high-buffer `4`
    的
    `v66 > v65 = +0.178667`
  - 但：
    - `v66 > v67`
      两边均值几乎不变

影响：

- 如果继续把当前这条线
  默认写成：
  - 再找 duration / gain / transient
    的硬阈值
  很容易白跑；
  因为这层 ring
  已经不像 shell vs outer 那样
  还存在明显单字段 carve
- 当前更危险的误写是：
  - 看到某条 row
    transient 更高
  就推断它一定更靠近
    `v65` drift；
  但真正更稳定的判断
  是先看：
  - `v66 > v64`
    还剩多少
  - `v66 > v65`
    是否已经贴到 `0`

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_neighbor_ring_buffer_collapse/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_neighbor_buffer_collapse_diagnosis.md`

后续要求：

1. 以后进入 mixed ring 内部诊断时，默认先看 margin 联动，再看 metadata。
2. 不要再把：
   - “这一层一定还能再用单字段 carve”
   当成默认假设。
3. 当前下一步若继续，优先做：
   - `train_001006`
   - `train_001589`
   - `train_001610`
   - `train_001745`
   的 case-to-case 对照，
   不再继续扩大样本面。

### 156. 当 low-buffer ring 里的 case 已经出现“metadata 位置还靠 pure-signature，但 margin 状态已先倒向 drift”的分叉时，不能再用单一 nearest-group 或单一元数据画像给它贴 pure / drift 身份；这一步必须把 metadata position 与 margin state 分开读

现象：

- 本轮对：
  - `train_001006`
  - `train_001589`
  - `train_001610`
  - `train_001745`
  做 reference-group positioning 后，
  发现：
  - `train_001006`
    对 pure-signature
    的
    total / metadata / margin
    三条距离都最近
  - `train_001589`
    total 与 margin
    都最近：
    - `v65` drift
  - 但：
    - `train_001610`
    - `train_001745`
      的 total / metadata
      最近组
      仍是：
      - pure-signature
      同时：
      - margin
        最近组
        已经变成：
        - `v65` drift

影响：

- 如果继续默认把当前这层
  写成：
  - “谁 total 最近哪组，
    谁就是哪组”
  会把：
  - `train_001610`
  - `train_001745`
    误判成
    还没进入 drift；
  但它们的：
  - `v66 > v64`
  - `v66 > v65`
    已经明显更像 drift
- 反过来，
  如果只看
  - target transient
  - duration
  - gain
  之类单条 metadata
  也会误以为
  `train_001006`
  只是“还没跑完的 drift”；
  但它当前
  三条距离
  仍一致指向：
  - pure-signature

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_case_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_positioning/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_lowbuffer_edge_positioning.md`

后续要求：

1. 进入 low-buffer ring 个例诊断时，默认同时写：
   - metadata position
   - margin state
2. 不要再用：
   - 单轴 nearest-group
   作为 pure / drift 身份的唯一判定。
3. 当前若继续推进，优先解释：
   - `train_001610`
   - `train_001745`
   的 margin-first collapse，
   而不是再回头扩大样本面。

### 157. 当 case 已经落在 pure-signature -> drift 的过渡带里，如果只看总距离或 metadata 进度，很容易误以为“必须先把 metadata 迁到 drift，margin 才会翻”；但在当前 low-buffer ring 里，`train_001610` 与 `train_001745` 已经证明 margin 完全可以先塌完，metadata 迁移反而是滞后的

现象：

- 本轮把：
  - `train_001006`
  - `train_001610`
  - `train_001745`
  投影到：
  - pure-signature
    -> `v65` drift
    的 metadata axis
  - pure-signature
    -> `v65` drift
    的 margin axis
  后发现：
  - `train_001006`
    - metadata ratio
      = `-1.581300`
    - margin ratio
      = `+0.051259`
  - `train_001610`
    - metadata ratio
      = `+0.004083`
    - margin ratio
      = `+1.240782`
  - `train_001745`
    - metadata ratio
      = `+0.349352`
    - margin ratio
      = `+1.046646`

影响：

- 如果继续把当前这条线
  默认写成：
  - 先找 metadata
    谁先把样本整体推向 drift
  会把：
  - `train_001610`
    这种最干净的
    margin-first collapse
    看漏；
    因为它 metadata
    几乎还停在 pure center，
    但 margin
    已经超过 drift center
- 同理，
  `train_001745`
  也不是
  metadata
  先整体换挡，
  而是：
  - margin
    已经基本走完
  - metadata
    只走到约三分之一

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_margin_first_transition_axes/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_margin_first_transition_axes.md`

后续要求：

1. 当前 low-buffer ring 若继续推进，默认先拆：
   - `v66 > v64`
   - `v66 > v65`
   的次序关系，
   不再默认先找 metadata 主导项。
2. 不要把：
   - “metadata 先迁到 drift”
   当成 drift 成立的必要条件。
3. `train_001610`
   应作为当前 margin-first collapse
   的主锚点样本。

### 158. 当已经确认 drift 是 margin-first collapse 后，如果还把 `v66 > v64` 与 `v66 > v65` 的越零次序混写成“同步翻掉”，会把 `train_001610` 这类 hinge-entry 样本和 `train_001745` 这类更深 post-entry 样本混成一类

现象：

- 本轮显式计算后，
  两条 gap 的 zero-cross threshold
  已明确为：
  - `v66 > v64`
    = `1.123493`
  - `v66 > v65`
    = `0.818051`
- 这说明：
  - `v66 > v65`
    会更早越过 `0`
- 对当前 3 条 case：
  - `train_001006`
    - `v66 > v64`
      progress to zero
      = `0.317728`
    - `v66 > v65`
      progress to zero
      = `0.337545`
    - 两条都未越零
  - `train_001610`
    - `v66 > v64`
      progress to zero
      = `0.982427`
      仍未越零
    - `v66 > v65`
      progress to zero
      = `1.310871`
      已越零
  - `train_001745`
    - `v66 > v64`
      progress to zero
      = `1.418327`
    - `v66 > v65`
      progress to zero
      = `1.011576`
    - 两条都已越零，
      但 `v66 > v64`
      更深

影响：

- 如果继续把当前这条线
  简写成：
  - “`v66 > v64`
    和
    `v66 > v65`
    一起翻掉”
  会丢掉当前最关键的
  阶段差异：
  - `train_001610`
    是：
    - `v66 > v65`
      先翻
    - `v66 > v64`
      只剩最后一层
  - `train_001745`
    才是：
    - `v66 > v64`
      进一步翻成负值
      的更深阶段

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_margin_order_split/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_margin_order_split.md`

后续要求：

1. 当前 low-buffer ring 若继续推进，默认把：
   - hinge-entry
   - post-entry depth
   分开写。
2. 不要再把：
   - `v66 > v64`
   - `v66 > v65`
   的翻转
   当成同步事件。
3. `train_001610`
   应作为：
   - `v66 > v65`
     先越零
   的主锚点；
   `train_001745`
   应作为：
   - `v66 > v64`
     后续继续翻负
   的主锚点。

### 159. 当已经进入 post-entry depth split 后，如果还把更深阶段误写成“`v65` takeover 继续加深”，会看漏 `train_001745` 相对 `train_001610` 的真正差异其实是 `v64` 剩余保护带被继续单边打穿，而不是 `v66 > v65` 继续变得更负

现象：

- 本轮对：
  - `train_001610`
  - `train_001745`
  做 singleton split 后，
  pairwise delta
  显示：
  - `v66 - v64`
    继续下掉
    `0.028624 dB`
  - 但
    `v66 - v65`
    反而回升
    `0.049313 dB`
- ranking
  也同步从：
  - `v67 > v65 > v66 > v64`
  变成：
  - `v67 > v64 > v65 > v66`

影响：

- 如果继续把当前更深阶段
  简写成：
  - `v65`
    继续 takeover
  就会把：
  - `train_001745`
    为什么会出现
    `v66 < v64`
    看反；
  因为它这一步
  真正更深的是：
  - `v64`
    剩余 buffer
    被继续打穿
- 同时也会错过：
  在这对样本里，
  与更深 `v64` collapse
  同步出现的是一组
  条件性组合：
  - 更早 overlap
  - 更长 reference
  - 更高 target / interference transient
  - 更弱 gain

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_post_entry_depth_split/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_post_entry_depth_split.md`

后续要求：

1. 当前 post-entry 分析若继续推进，默认先问：
   - `v64`
     为什么继续单边塌
   而不是：
   - `v65`
     是否继续 takeover
2. 不要把：
   - deeper drift
     = `v66 > v65`
       更负
   当成默认假设。
3. `train_001745`
   应作为当前：
   - `v64`
     single-sided collapse
   的主锚点。

### 160. 当 `train_001745` 这种 singleton case 的 metadata 邻居已经扫到窄 ring 以后，不能因为“最近邻里也有 `v66 < v64`”就把它们并成同型 family；还必须继续检查 `v66 < v65` 是否同时成立，以及两条负 gap 里到底是谁更深

现象：

- 本轮对
  `train_001745`
  的 train-side `topv67`
  邻域做全量 `27` 条
  signature scan 后，
  bucket
  变成：
  - `pre_entry_or_pure = 20`
  - `hinge_secondary_crossed_first = 4`
  - `post_entry_both_crossed_secondary_deeper_or_equal = 1`
  - `reference_only_crossed_unexpected = 2`
  - `post_entry_both_crossed_reference_deeper = 0`
- 最近的
  post-entry row
  `train_001543`
  虽然满足：
  - `v66 < v64`
  - `v66 < v65`
  但它的：
  - `v66 - v64 = -0.008828 dB`
  - `v66 - v65 = -0.113984 dB`
  实际是
  `v65`
  更深；
  不是
  `train_001745`
  那种：
  - `v64`
    deeper
- 另外两条：
  - `train_000664`
  - `train_000210`
  虽然也出现：
  - `v66 < v64`
  但仍保有：
  - `v66 > v65`
  属于另一条
  `v64-only crossed`
  异型支路

影响：

- 如果只因为：
  - 邻居里也有
    `v66 < v64`
  就把它们并成：
  - `train_001745`
    同型 family
  会把三种不同几何
  混成一类：
  - `both-crossed + v64-deeper`
  - `both-crossed + v65-deeper`
  - `v64-only crossed`
- 这样会误以为：
  - `train_001745`
    已经在窄 ring
    找到 mirror
  实际上当前 ring
  内同型数是：
  - `0`

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_signature_scan/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_post_entry_v64_collapse_neighbor_scan.md`

后续要求：

1. 之后凡是再说
   `train_001745`
   是否有同型近邻，
   默认至少同时检查：
   - `v66 < v64`
   - `v66 < v65`
   - 以及
     `v66 - v64`
     是否比
     `v66 - v65`
     更深。
2. 不要把：
   - `metadata_distance`
     最近
   当作：
   - margin 几何同型
   的充分条件。
3. 当前窄 ring
   内对
   `train_001745`
   的默认表述
   应固定为：
   - rare conditional singleton
   而不是：
   - local family member。

### 161. 当已经把 `train_001745` 的假近邻压成 `001543 / 000664` 这种分叉对照后，不能再把它们写成“离 `001745` 远近不同的同一路 drift 深度”；真正要看的，是它们是否在同一个 `v64 crossed` 台阶后分流到不同 branch identity

现象：

- 本轮把：
  - `train_001745`
  - `train_001543`
  - `train_000664`
  压成 singleton group split 后，
  看到：
  - `001543 - 000664`
    的
    `v66 - v64`
    只差
    `+0.000345 dB`
    基本不动；
    但
    `v66 - v65`
    额外下掉
    `0.118462 dB`
  - `001745 - 000664`
    则是：
    - `v66 - v64`
      再下掉
      `0.018296 dB`
    - `v66 - v65`
      只再下掉
      `0.006385 dB`
  - `001745 - 001543`
    甚至表现为：
    - `v66 - v64`
      更负
      `0.018641 dB`
    - 但
      `v66 - v65`
      反而更高
      `0.112077 dB`

影响：

- 如果继续把这三条
  理解成：
  - 同一条 drift
    上只是深浅不同
  就会把：
  - `001543`
    的
    `v65 sink`
  - 和
  - `001745`
    的
    `v64 pocket`
  混成同一类
- 这样会看不见：
  - `000664 -> 001543`
    实际上几乎只是在
    `v65`
    这一侧翻负
  - 而
    `000664 -> 001745`
    则是在
    `v64`
    已翻负的前提下，
    把
    `v65`
    只刚好推过零

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_post_entry_branch_divergence_split/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_post_entry_branch_divergence_split.md`

后续要求：

1. 之后凡是再说
   `001543 / 000664 / 001745`
   这组三角关系，
   默认先问：
   - 它们共享的是不是同一个
     `v64 crossed`
     shelf
   - 分流的是：
     `v65 sink`
     还是
     `v64 pocket`
2. 不要再把：
   - `距离 `001745` 更近`
   自动等同于：
   - `在同一条 drift 深度线上`
3. 当前如果还要继续压窄，
   默认优先用：
   - `train_001543`
   - `train_000664`
   这对
   去隔离：
   - 什么因素
     只会推动
     `v66 > v65`
     翻负，
     而不会明显继续加深
     `v66 > v64`。

### 162. 当已经找到 `train_001543 / train_000664` 这种 clean isolation pair 后，不要再把 `train_001745` 混回同一条“谁在推动 `v66 > v65` 翻负”的分析线；否则会把 `v65 sink` 和 `v64 pocket` 两种不同触发方向再次糊在一起

现象：

- 本轮把：
  - `train_001543`
  - `train_000664`
  单独做 `v65 sink`
  isolation 后，
  看到：
  - `v66 - v64`
    只变化
    `+0.000345 dB`
  - 但
    `v66 - v65`
    额外下掉
    `0.118462 dB`
- 同时，
  与这一步同步出现的
  是：
  - 更短 reference
  - 更早 overlap
  - 更弱 gain
  - 更高双侧 transient
  - 更低 cosine
- 而
  `train_001745`
  那条支路
  虽然也有：
  - 更早 overlap
  - 更高 transient
  但它更关键的变化
  是：
  - `v66 - v64`
    继续更负
  - `v66 - v65`
    只刚好越零

影响：

- 如果这时还把
  `001745`
  混回同一条 isolation 线，
  就会把：
  - `谁在推动`
    `v65 sink`
  和
  - `谁在维持`
    `v64 pocket`
  再次混成一包
- 这样会让：
  - 更短 reference /
    更弱 gain /
    更低 cosine
  这组只在
  `001543 -> 000664`
  上干净显影的信号
  被
  `001745`
  的异型支路
  冲淡

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_isolation/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_isolation.md`

后续要求：

1. 之后凡是要隔离：
   - `v66 > v65`
     为什么翻负
   默认先用：
   - `train_001543`
   - `train_000664`
   这对，
   不要先把
   `train_001745`
   混回来。
2. 当前
   `train_001745`
   只应保留在：
   - `v64 pocket`
     支路
   的解释线上。
3. 当前如果继续推进，
   默认优先检查：
   - 更短 reference
   - 更弱 gain
   - 更低 cosine
   这三项
   在
   `v65 sink`
   里
   哪一项更像主导因子。

### 163. 当已经把 `v65 sink` 的 factor contrast 做到 sink-branch vs pocket-branch 的 residual 排序后，不要还把 `cosine` 和 `reference / overlap / gain` 并列写成主导候选；这会把真正有分支区分力的因子稀释掉

现象：

- 本轮用：
  - `train_001543`
    作为 target sink
  - `train_000664`
    作为 shared shelf
  - `train_001745`
    作为 pocket contrast
  做 branch factor contrast 后，
  标准化 residual
  排序为：
  - `reference_duration_sec = 2.0673 z`
  - `interference_layers.0.start_offset_sec = 1.5845 z`
  - `interference_layers.0.gain_db = 1.2125 z`
  - `target_transient_presence_share_mean = 0.5273 z`
  - `interference_transient_presence_share_mean = 0.3164 z`
  - `target_interference_logspec_cosine = 0.2609 z`
- 也就是：
  - `cosine`
    比
    `reference / overlap / gain`
    都弱很多；
  - 双侧 transient share
    也更像 shared package，
    不是 sink identity
    的主导项

影响：

- 如果这时还把：
  - 更低 cosine
  和：
  - 更短 reference
  - 更早 overlap
  - 更弱 gain
  并列写成：
  - `v65 sink`
    主导候选
  就会让下一步继续排查时，
  把注意力浪费在
  已经明显偏弱的因子上
- 同时也会把：
  - overlap
    明明比
    gain
    更强的 sink-specific
    区分力
  看低

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_factor_contrast/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_factor_contrast.md`

后续要求：

1. 之后凡是再写
   `v65 sink`
   的主导候选，
   默认顺序固定为：
   - `reference`
   - `overlap`
   - `gain`
   - `cosine`
     仅作弱辅助
2. 不要再把：
   - 双侧 transient share
   当作当前
   sink branch
   identity
   的主导因子。
3. 当前如果继续推进，
   默认只拆：
   - `reference`
   - `overlap`
   这两项，
   不再优先拆
   `cosine`。

### 164. 当已经把 `reference / overlap / gain` 做成 target-side slice support 后，不要再把 `overlap` 写成 `v65 sink` 的主分界；它会把 `train_001745` 这条 pocket 分支一起吸进来

现象：

- 本轮用
  `target=001543`
  / `baseline=000664`
  / `contrast=001745`
  做 factor slice support 后，
  看到：
  - `reference`
    的
    `contrast_on_target_side = false`
  - `gain`
    的
    `contrast_on_target_side = false`
  - 但
    `start_offset`
    的
    `contrast_on_target_side = true`
- 也就是：
  - `001745`
    会和
    `001543`
    一起落到：
    - 更早 overlap
      这一侧
  - 却不会一起落到：
    - 更短 reference
    - 更弱 gain
      这一侧

影响：

- 如果这时还把：
  - 更早 overlap
  写成：
  - `v65 sink`
    主分界
  就会把：
  - `v64 pocket`
    这条支路
  一起吸进来
- 这样会把：
  - `reference`
    明明是当前最干净
    sink-vs-pocket
    分界
  的事实
  再次冲淡

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_factor_slice_support/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_factor_slice_support.md`

后续要求：

1. 之后凡是再写
   `v65 sink`
   的主分界，
   默认优先级固定为：
   - `reference`
   - `gain`
   - `overlap`
     仅作 shared package
2. 不要再把：
   - `overlap`
   当作当前
   sink-vs-pocket
   的主切片边界。
3. 当前如果继续推进，
   默认只拆：
   - `reference`
   - `gain`
   不再优先拆
   `overlap`。

### 165. 当已经把 `v65 sink` 压到 `reference+gain both` 象限内部后，不要再把 `gain` 或“更早 overlap”继续当作 hinge -> sink 的最后主导步；这会把已经解释成 entry gate 的条件又误写成最终触发器

现象：

- 本轮对：
  - `train_001543`
  - `train_000266`
  做局部 split 后，
  看到：
  - `interference_layers.0.gain_db = +0.059`
    基本不变
  - `interference_layers.0.start_offset_sec = +0.049`
    overlap
    反而略更晚
- 但同时：
  - `reference_duration_sec = -0.27`
  - `target_transient_presence_minus_mid_db_mean = +5.912337`
  - `target_transient_presence_share_mean = +0.056539`
  明显上升
- margin 也同步从：
  - `v66 - v64 = +0.015989`
  走到：
  - `-0.008828`
  并把：
  - `v66 - v65`
    再额外下掉
    `0.074139 dB`

影响：

- 如果这时还把：
  - 弱 gain
  或：
  - 更早 overlap
  写成：
  - hinge -> sink
    最后主导步
  就会把：
  - 已经属于
    `reference+gain`
    entry gate
    的条件
  和：
  - 真正把
    `000266`
    推成
    `001543`
    的最后局部变化
  再次混在一起
- 这样会错过：
  - `reference`
    继续缩短
  - `target transient`
    抬升
  才是当前更像
  最终补刀的组合

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_vs_reference_gain_hinge/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_reference_gain_hinge_split.md`

后续要求：

1. 之后凡是再写
   `v65 sink`
   的局部因子层级，
   默认改写成：
   - `reference + gain`
     = entry gate
   - `reference`
     再缩短
     + `target transient`
     抬升
     = hinge -> sink
2. 不要再把：
   - `overlap`
   写成当前
   hinge -> sink
   的最后主导步。
3. 当前如果继续推进，
   默认只拆：
   - `reference`
   - `target transient`
   不再优先拆
   `gain / overlap`。

### 166. 当已经把 `reference+gain both` 象限继续拆成 sink / hinge / pre 后，不要再把 `reference` 写成 gate 内统一最强的 final push；这会把真正更稳定的 `target transient` 分离作用盖掉

现象：

- 本轮把
  `reference+gain`
  做成交叉四象限后，
  看到：
  - `train_001543`
    在
    `both`
  - `train_001745`
    和
    `train_000664`
    都在
    `neither`
  说明：
  - `reference+gain`
    更像
    conjunction entry gate
- 进一步把
  `both`
  象限拆成：
  - sink
  - hinge
  - pre
  后，
  看到：
  - `sink - both_pre`
    的
    `reference = -0.0375`
    很小
    但
    `target_transient_mean = +0.5340`
    `target_transient_share = +0.04247`
  - `sink - both_nonsink`
    的
    `reference = -0.084`
    也不大，
    但
    `target_transient_mean = +1.6097`
    `target_transient_share = +0.04528`
- 只有在：
  - `sink - hinge`
  这条局部边界上，
  `reference = -0.27`
  仍然比较显著

影响：

- 如果这时还把：
  - `reference`
  写成：
  - gate 内
    统一最强的
    final push
  就会把：
  - `target transient`
    明明对
    sink-vs-nonsink
    更稳定的
    分离作用
  压掉
- 这样会误把：
  - `reference`
    的局部补刀作用
  夸大成：
  - 对所有 gate 内
    非-sink
    都同样主导

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_vs_target_transient_split/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_reference_vs_target_transient_split.md`

后续要求：

1. 之后凡是再写
   `v65 sink`
   的层级，
   默认改写成：
   - `reference+gain`
     = conjunction entry gate
   - `target transient`
     = gate 内 final push
   - `reference`
     = hinge -> sink
       局部补刀
2. 不要再把：
   - `reference`
   当作当前 gate 内
   所有非-sink
   的统一第一分界。
3. 当前如果继续推进，
   默认只拆：
   - `target transient mean`
   - `target transient share`
   不再优先回到
   `reference / gain`。

### 167. 当已经把 gate 内的 `target transient` 拆成 `mean` vs `share` 后，不要再把两者并列写成同等主导；这会忽略 `share` 更容易把旁支一起吸进来的污染

现象：

- 本轮 gate 内 factor contrast
  显示：
  - `target_transient_mean = 1.2788 z`
  - `target_transient_share = 1.0665 z`
  说明：
  - `mean`
    已经更强
- 同时，
  slice support
  里：
  - `mean`
    和
    `share`
    都能把
    hinge anchor
    `train_000266`
    挡在 target-side 外
  - 但
    `share`
    会额外吸进：
    - `train_000210`
      这条
      `v64_only`
      旁支
  - `mean`
    没有这层污染

影响：

- 如果这时还把：
  - `mean`
  和：
  - `share`
  写成：
  - 同等主导
  就会把：
  - `share`
    更容易误吸旁支
  这层缺点
  抹掉
- 这样会让下一步继续诊断时，
  还在两项上平均分配注意力，
  而不是直接把主线收口到
  `mean`

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_slice_support/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_target_transient_mean_vs_share.md`

后续要求：

1. 之后凡是再写
   `v65 sink`
   的 final push，
   默认主线固定为：
   - `target transient mean`
2. `target transient share`
   只保留为：
   - 辅助项
   不再与
   `mean`
   并列。
3. 当前如果继续推进，
   默认只围绕：
   - `target transient mean`
   做更细支持复核。

### 168. 当已经把 gate 内的 `target transient` 拆成 `mean` vs `share`，并确认 `share` 会误吸 `v64_only` 旁支后，不要再把 `share` 写成和 `mean` 同等干净的 final-push 指标

现象：

- 本轮 gate 内 factor contrast
  显示：
  - `target_transient_mean = 1.2788 z`
  - `target_transient_share = 1.0665 z`
  说明：
  - `mean`
    更强
- 同时，
  slice support
  里：
  - `mean`
    和
    `share`
    都能把
    hinge anchor
    `train_000266`
    挡在外面
  - 但
    `share`
    会额外吸进：
    - `train_000210`
      这条
      `v64_only`
      旁支
  - `mean`
    没有这层额外污染

影响：

- 如果这时还把：
  - `share`
  写成：
  - 和 `mean`
    同等干净的
    final push
    指标
  就会把：
  - `share`
    对旁支的误吸
  这一层风险
  藏掉
- 这样会让：
  - `v65 sink`
    的最终主导
  再次被写得过宽

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_slice_support/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_target_transient_mean_vs_share.md`

后续要求：

1. 之后凡是再写
   `v65 sink`
   的 final push，
   默认只把：
   - `target transient mean`
   当作当前主导候选。

### 169. 当已经证明 `mean+gain` 的 `both` 桶只剩 sink 本人时，不要再把 `reference` 继续写成和 `gain` 对 `mean` 同等有效的本地搭档

现象：

- 本轮
  `mean + reference`
  四象限里：
  - `both`
    桶共有：
    - `6`
      条
  其中：
  - `1` 条 sink
  - `5` 条 pre
- 同时，
  `mean + gain`
  四象限里：
  - `both`
    桶只有：
    - `train_001543`
  这一条 sink
- 而且：
  - `train_000266`
    仍在：
    - `factor_b_only`
  说明：
  - `weak gain`
    单独还不够
  - 但它和
    `mean`
    结合后，
    已经比
    `mean + reference`
    更接近
    当前窄 ring
    的 sink-only carve

影响：

- 如果这时还把：
  - `reference`
  写成：
  - 和 `gain`
    对
    `mean`
    同等有效的
    本地 partner
  就会把：
  - 上游 entry 约束
  和：
  - 当前局部 carve
    条件
  再次混在一起
- 这样会让：
  - `v65 sink`
    当前最窄的
    操作性切面
  被写得偏宽，
  也会错过：
  - 为什么
    `weak gain`
    壳里的
    hinge
    还需要
    `mean`
    再抬一截

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_reference_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_gain_quadrants/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_mean_gate_partner_split.md`

后续要求：

1. 之后凡是再写
   当前窄 ring
   的
   `v65 sink`
   局部 carve，
   默认优先写成：
   - `mean + gain`
   而不是：
   - `mean + reference`。
2. `reference`
   继续保留为：
   - 上游 entry
     描述，
   不再和
   `gain`
   并列成
   `mean`
   的同级本地搭档。
3. 当前如果继续推进，
   默认只看：
   - `train_000266 / train_001589 / train_001543`
   这组
   `weak gain`
   壳内样本，
   不再把
   `reference`
   拉回同一级。 

### 170. 当已经把 `train_000266 / train_001589 / train_001543` 压成 weak-gain 壳内 split，并看到 sink 的 gain 并没有更弱时，不要再把 `gain` 写成壳内 final push

现象：

- 本轮
  `v65_sink - weak_gain_hinge`
  的：
  - `interference_layers.0.gain_db = +0.083`
  说明：
  - sink
    的 gain
    并没有
    更弱
- 同时：
  - `interference_layers.0.start_offset_sec = +0.090`
  也就是：
  - sink
    overlap
    反而更晚
- 真正最大的
  target-side
  变化反而是：
  - `target_transient_mean = +4.6522`
  - `target_transient_share = +0.05677`
  且这一步会继续带出：
  - `v66-v64 = -0.0364 dB`
  - `v66-v65 = -0.0673 dB`
    的更深塌缩

影响：

- 如果这时还把：
  - `gain`
  写成：
  - weak-gain 壳内
    的 final push
  就会把：
  - 上游 entry shell
  和：
  - 壳内真正主导的
    `mean`
  再次混在一起
- 这样会直接误读：
  - 为什么
    `train_000266`
    和
    `train_001589`
    虽然都已落到
    weak-gain
    一侧，
    却仍然停在
    hinge

处理：

- 已落盘：
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_hinge_train.txt`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_weak_gain_hinge_split/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_weak_gain_hinge_split.md`

后续要求：

1. 之后凡是再写
   weak-gain 壳内
   的
   `v65 sink`
   分界，
   默认不要再把：
   - `gain`
   当作壳内
   final push。
2. 当前默认主语
   应固定为：
   - `target transient mean`
   才是把 hinge
   真正推进 sink
   的第一主轴。
3. 当前如果继续推进，
   默认只看：
   - `train_001589 / train_001543`
   不再回到
   “gain
   是否还要更弱”
   这条线。 

### 171. 当已经把 `train_001589 / train_001543` 压成 one-to-one split，并确认 `001589` 已经是 partial-mean hinge 后，不要再把它写成“还没进入 weak-gain 壳”

现象：

- 本轮
  `v65_sink - weak_gain_partial_mean_hinge`
  显示：
  - `target_transient_mean = +3.3921`
  - `target_transient_share = +0.056997`
  说明：
  - `train_001589`
    相对 floor hinge
    已经抬起了一截
    `mean`
- 同时：
  - `gain = +0.107`
  - `start_offset = +0.131 sec`
  依然说明：
  - 它卡住的原因
    不是：
    - 不够 weak gain
    - overlap 不够早
- 真实的卡点是：
  - `v66 < v65`
    已成立
  - 但
    `v66 > v64`
    还没有一起翻负
  并且
  `001589`
  还带着：
  - 更长 duration
  - 更高 cosine

影响：

- 如果这时还把：
  - `train_001589`
  写成：
  - 还没进入
    weak-gain 壳
  就会把：
  - 壳外
  和：
  - 壳内 near-sink hinge
  再次混掉
- 这样会直接错过
  当前最窄的问题：
  - `mean`
    还没抬够
  还是：
  - duration / cosine
    壳
    还在托住
    `v64 buffer`

处理：

- 已落盘：
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_partial_mean_hinge_train.txt`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_vs_partial_mean_hinge/summary.json`
  - `reports/daily/2026-03-23_candidate_v7_v65_sink_partial_mean_hinge_split.md`

后续要求：

1. 之后凡是再写
   `train_001589`
   的身份，
   默认固定为：
   - weak-gain shell
     内部
     `partial mean rise`
     的 near-sink hinge。
2. 当前如果继续推进，
   默认只拆：
   - `mean`
   对
   - `duration / cosine`
   不再回到
   “它是否已经进壳”
   这条线。 

### 172. 当已经把 `001589 -> 001543` 的最后边界拆成 `mean / duration / cosine`，并看到 `duration` 与 `cosine` 在当前窄 ring 标准化尺度里都排在 `mean` 前面后，不要再把 near-sink 卡点写成单纯“mean 还没抬够”

现象：

- 本轮 factor contrast
  显示：
  - `reference_duration = 3.3076 z`
  - `target_duration = 2.2258 z`
  - `cosine = 1.6606 z`
  - `mean = 0.7337 z`
- 同时，
  slice support
  里：
  - `reference`
    的
    `contrast_on_target_side = true`
    说明：
    - `train_000266`
      已经落在
      它的 target-side
  - `target_duration`
    与
    `cosine`
    则都满足：
    - `contrast_on_target_side = false`
- 两组 quadrants
  还进一步表明：
  - `mean + target_duration`
    和
    `mean + cosine`
    都不是独立 hard gate，
    但：
    - `target_duration`
      更强
    - `cosine`
      更干净

影响：

- 如果这时还把：
  - `001589`
    没进 sink
  写成：
  - 只是
    `mean`
    还没抬够
  就会把：
  - duration shell
  和：
  - cosine
    这层 near-sink
    约束
  整体藏掉
- 这样会让
  当前最后一条边界
  被写得过粗，
  也会误把
  `reference`
  再次抬成
  最后主语

处理：

- 已落盘：
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_hinge_floor_train.txt`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_hinge_ladder_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_partial_mean_edge_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_partial_mean_edge_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_targetduration_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_cosine_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_partial_mean_duration_cosine_split.md`

后续要求：

1. 之后凡是再写
   `train_001589`
   最后没跨进 sink
   的原因，
   默认不要再写成：
   - 单纯
     `mean`
     不够。
2. 当前默认主语
   应固定成：
   - `target_duration`
     是更强的
     near-sink blocker
   - `cosine`
     是更干净的
     辅助约束。
3. `reference`
   不再抬回
   最后边界主语，
   因为
   `train_000266`
   已经落在
   它的 target-side。
4. 当前如果继续推进，
   默认只拆：
   - `target_duration`
   对
   - `cosine`。 

### 173. 当已经把 `target_duration` 与 `cosine` 正式压成 focused split 后，不要因为 `cosine` 的 target-side 更干净，就把它误写成比 `duration` 更强的主 blocker

现象：

- 本轮 focused split
  显示：
  - `target_duration`
    的 target-side
    为：
    - `1` 条 sink
    - `2` 条 hinge
    - `2` 条 `v64_only`
    - `17` 条 pre
  - `cosine`
    的 target-side
    为：
    - `1` 条 sink
    - `2` 条 hinge
    - `2` 条 `v64_only`
    - `13` 条 pre
- 也就是：
  - `cosine`
    确实更干净，
    会多排掉一部分
    pure pre
- 但真正决定
  `001589`
  与
  `000266`
  “还差多远”
  的，仍是：
  - `duration`
  因为：
  - `target_duration`
    midpoint
    为：
    - `1.71 sec`
  - `001589`
    离 target-side
    还差：
    - `0.57 sec`
  - `000266`
    只差：
    - `0.03 sec`
  - gap 差为：
    - `0.54 sec`
  而：
  - `cosine`
    midpoint
    为：
    - `0.661089`
  - `001589`
    还差：
    - `0.053765`
  - `000266`
    只差：
    - `0.041001`
  - gap 差只有：
    - `0.012763`

影响：

- 如果这时只看：
  - `cosine`
    的 target-side
    更干净
  很容易把它误写成：
  - 比 `duration`
    更接近
    最后主 blocker
- 但这会把：
  - “谁更像
     主导 001589
     还没跨进去
     的幅度”
  和：
  - “谁更像
     shell 上的
     干净 trim”
  混成一件事

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_duration_vs_cosine_split.md`

后续要求：

1. 之后凡是再写
   `001589`
   没跨进 sink
   的主 blocker，
   默认固定为：
   - `target_duration`
2. `cosine`
   只保留为：
   - duration shell
     上的
     secondary trim
   不再和
   `duration`
   并列成
   同级主语。
3. 当
   `duration-only`
   与
   `cosine-only`
   桶里
   都没有
   hinge / `v64_only`
   row 时，
   不要再把
   任一单因子
   写成独立 hard gate。
4. 当前如果继续推进，
   默认只看：
   - `duration + cosine both`
     这层 shell
     内部
     为什么还残留
     大量 pre，
   不再继续问：
   - `duration`
   还是：
   - `cosine`。

### 174. 当已经把 `duration + cosine both` 这层 shell 正式拆成 `pre / boundary / sink` 后，不要再惯性把 shell 内残留的 pre 写成“`mean` 还没抬够”

现象：

- 本轮 shell split
  显示：
  - `both`
    里实际是：
    - `1` 条 sink
    - `4` 条 boundary
    - `11` 条 pre
- 更关键的是：
  - shell pre
    里已经混着
    多条
    `mean`
    高于 sink
    的 row，
    例如：
    - `train_000578 = -3.4491`
    - `train_001495 = -4.9590`
    - `train_001725 = -5.1932`
    - `train_000951 = -6.3755`
  - 而 sink
    `train_001543`
    只有：
    - `-10.9606`
- 同时，
  用
  `sink`
  对
  `boundary`
  相对
  `pre`
  做 factor contrast，
  排名前三已经变成：
  - `gain = -1.4061 z`
  - `reference = -0.7075 z`
  - `offset = +0.6134 z`
  而：
  - `target_transient_mean`
    只剩：
    - `-0.0223 z`

影响：

- 如果这时还把：
  - shell 内残留 pre
  写成：
  - `mean`
    还没抬够
  就会把：
  - 一批
    `mean`
    已经很高、
    但 margin
    仍稳定的 pre
  直接写漏
- 这样会把：
  - `duration + cosine`
    这层 shell
    误写成
    单调的
    `mean`
    进阶梯子，
  而不是：
  - 另一套
    `gain / reference / offset`
    margin routing

处理：

- 已落盘：
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_duration_cosine_both_pre_train.txt`
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_duration_cosine_both_boundary_train.txt`
  - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_duration_cosine_both_nonsink_train.txt`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_shell_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_shell_factor_contrast/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_duration_cosine_shell_split.md`

后续要求：

1. 之后凡是再写
   `duration + cosine both`
   这层 shell，
   默认不要再写成：
   - `mean`
     final push。
2. 当前更准确的
   shell 内主语
   应固定改成：
   - `gain`
   - `reference`
   - `offset`
3. 当 shell pre
   里已经存在
   多条
   `mean`
   高于 sink
   的 row 时，
   不要再把
   `mean`
   当成
   shell 内
   单调分层轴。
4. 当前如果继续推进，
   默认只拆：
   - `gain`
   - `reference`
   - `offset`
   不再回到：
   - `mean`
   是否还是
   shell 内主导
   这条线。

### 175. 当已经把 `duration + cosine` shell 的口径翻成 `boundary vs pre` 后，不要再把 `offset` 和 `gain / reference` 并列写成 boundary-specific 主语

现象：

- 本轮用：
  - `target = boundary`
  - `baseline = pre`
  - `contrast = sink`
  做 split 后，
  factor contrast
  排名前三是：
  - `gain = +2.4854 z`
  - `reference = +1.3520 z`
  - `interference transient mean = -1.1194 z`
- 同时，
  slice support
  里：
  - `offset`
    的
    `contrast_on_target_side = true`
    说明：
    - sink
      也站在
      boundary
      的 target-side
  - `gain`
    与
    `reference`
    则都是：
    - `contrast_on_target_side = false`
    说明：
    - sink
      不站在
      这两项的
      target-side

影响：

- 如果这时还把：
  - `offset`
  和：
  - `gain / reference`
  并列写成：
  - boundary-specific
    主语
  就会把：
  - shared package
  和：
  - boundary-vs-sink
    反向分叉轴
  再次混掉
- 这样会直接误导下一步，
  还去拆：
  - `offset`
    为什么让 row
    进 boundary
  而不是先收口到：
  - `reference + gain`
    这条真正的
    conjunction

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_reference_offset_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_boundary_reference_gain_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_duration_cosine_boundary_routing_split.md`

后续要求：

1. 之后凡是再写
   shell 内
   `boundary` routing，
   默认固定成：
   - `reference + gain`
     是当前主 conjunction
2. `offset`
   只保留为：
   - pre -> boundary -> sink
     共享 package
   不再和
   `reference / gain`
   并列成
   boundary-specific 主语。
3. 当
   `reference + gain both`
   桶里
   已经没有 sink，
   但仍混有
   少量 pre
   时，
   下一步默认只拆：
   - 为什么
     `train_000951`
     这类 pre
     还残留在这里
   - 以及
     `hinge / v64_only`
     为什么优先落在
     这条 conjunction
     上。

### 176. 当已经把 `reference + gain both` 这条 boundary conjunction 单独拆开后，不要再把残留的 `train_000951` 写成“只差最后一点 gain 就能 crossed”

现象：

- 本轮把：
  - crossed edge
    `3` 条
  - `train_000951`
    这条残留 pre
  单独做 split 后，
  行为均值直接变成：
  - crossed mean：
    - `v66 - v64 = +0.004184 dB`
    - `v66 - v65 = -0.015859 dB`
  - `train_000951`：
    - `v66 - v64 = +0.027298 dB`
    - `v66 - v65 = +0.101198 dB`
- 同时，
  用：
  - `target = crossed`
  - `baseline = 000951`
  - `contrast = sink`
  做 factor contrast，
  当前 residual
  排名前三是：
  - `reference = +2.3843 z`
  - `gain = +2.2473 z`
  - `cosine = +1.6143 z`
  但方向上实际是：
  - crossed
    相对
    `000951`
    为：
    - reference 更长
    - cosine 更高
    - gain 更低
- 更关键的是：
  - `train_000951`
    与
    `train_001705`
    有完全相同的：
    - `target_transient_presence_minus_mid_db_mean = -6.375519`
    - `target_transient_presence_share_mean = 0.155784`
  - 但一个仍是 pre，
    一个已是 hinge

影响：

- 如果这时还把
  `000951`
  写成：
  - 只差最后一点 gain
  就会把方向写反；
  因为它并不是
  gain 不够，
  而是已经站得比 crossed
  更靠 strong-gain 一侧
- 同时也会把：
  - `reference + gain both`
    误判成：
    - crossed hard edge
  但当前
  `000951`
  的局部邻域
  最近 `12` 条
  仍混着：
  - `6` 条 pre
  - `2` 条 hinge
  - `2` 条 `v64_only`
  - `1` 条 `both_crossed_v64_deeper`
  - `1` 条 sink
  说明这层其实是：
  - mixed shelf
    不是单线 near-miss edge
- 若继续忽略
  `001705`
  与
  `000951`
  的 shared-target 事实，
  还会把：
  - target-side transient
    错写成
    `000951`
    的主 blocker
  但当前更像 blocker 的
  已经是：
  - 更长 reference
  - 更高 cosine
  - 更完整的 interference package

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_pre_neighbor_scan/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_both_edge_interference_cosine_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_reference_gain_edge_residual_split.md`

后续要求：

1. 之后凡是再写
   `train_000951`
   为什么还停在 pre，
   默认先排除：
   - gain 不够
   这条旧口径。
2. `reference + gain both`
   之后默认固定写成：
   - crossed-support shelf
   不再写成：
   - hard gate。
3. 如果还要继续压窄，
   默认改成 case-level：
   - `000951 -> 001705`
   - `000951 -> 001610 / 000664`
   两条子路径分开解释，
   不再把 crossed edge
   当成单一机制。

### 177. 当 `001705 / 001610 / 000664` 已经被显式拆成 singleton groups 后，不要再把它们写成“同一路径只差 crossed 深浅”

现象：

- 本轮把 crossed edge
  进一步拆成：
  - `train_001705`
  - `train_001610`
  - `train_000664`
  后，
  compare margin
  直接裂成三种几何：
  - `001705`：
    - `v66 - v64 = +0.020573 dB`
    - `v66 - v65 = -0.000834 dB`
  - `001610`：
    - `v66 - v64 = +0.001154 dB`
    - `v66 - v65 = -0.051220 dB`
  - `000664`：
    - `v66 - v64 = -0.009173 dB`
    - `v66 - v65 = +0.004478 dB`
- 同时：
  - `001705`
    与
    `000951`
    的 target transient
    mean / share
    完全相同
  - `000664`
    相对
    `001610`
    的 strongest residual
    则已固定成：
    - later offset
    - longer target duration
    - lower share

影响：

- 如果这时还把
  这三条 case
  写成：
  - 同一路径
    只是更深 / 更浅
  就会把：
  - shared-target soft hinge
  - low-share hinge
  - low-share `v64_only`
  三种不同分岔
  压扁成一条假深度轴
- 进一步会误把：
  - `000664`
    解释成：
    - 更深 hinge
  但它实际已经是：
  - branch rotation
    到
    `v64_only`

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_case_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_shared_target_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_shared_target_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_shared_target_share_cosine_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_v64only_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_v64only_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_edge_v64only_offset_duration_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_reference_gain_edge_case_branch_split.md`

后续要求：

1. 之后凡是再写
   crossed edge
   内部 case，
   默认先排除：
   - 单一路径深浅
   这条旧口径。
2. `001705 / 001610 / 000664`
   之后默认固定写成：
   - shared-target soft hinge
   - low-share hinge
   - low-share `v64_only`
   三条不同子支路。
3. 如果还要继续压窄，
   默认直接接：
   - `001705 -> 001543`
   - `000664 -> 001543`
   两条终分歧，
   不再回头平均 crossed edge。

### 178. 当已经把 `001705` 或 `000664` 对到 `001543` 时，不要再把 sink 写成“把 hinge / v64_only package 继续拉高”

现象：

- 本轮把
  `train_001543`
  单独拉成
  singleton sink
  后：
  - `001705 -> 001543`
    的 sink-specific residual
    前三位是：
    - `gain = -2.2305 z`
    - `reference = -2.1826 z`
    - `cosine = -1.6398 z`
  - `000664 -> 001543`
    的 sink-specific residual
    前三位是：
    - `cosine = -2.3958 z`
    - `reference = -2.0542 z`
    - `gain = -1.9920 z`
- 更关键的是：
  - `001705 -> 001543`
    时：
    - `v66 - v64`
      只再下降
      `0.029401 dB`
    - `v66 - v65`
      却再下降
      `0.113151 dB`
  - `000664 -> 001543`
    时：
    - `v66 - v64`
      只回弹
      `+0.000345 dB`
    - `v66 - v65`
      却再下降
      `0.118462 dB`

影响：

- 如果这时还把 sink
  写成：
  - shared-target 更强
  - `v64_only` 更深
  就会把方向写反；
  因为当前 sink
  不是沿着旧 package
  继续放大，
  而是在两条路径上共同执行：
  - 降 gain
  - 降 cosine
  - 缩短 reference
- 特别是
  `000664 -> 001543`
  若仍写成：
  - 更深 `v64_only`
  会错过最关键的事实：
  - 它几乎没有继续压
    `v64`
  - 而是把 margin
    重新压回
    `v65`
    这一侧

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_final_case_divergence_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_sharedtarget_to_sink_gain_cosine_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_v64only_to_sink_gain_cosine_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_final_case_divergence_split.md`

后续要求：

1. 之后凡是再写
   `001705 -> sink`
   或
   `000664 -> sink`，
   默认先排除：
   - 旧 package 更强
   这条口径。
2. sink route
   之后默认固定写成：
   - 降 gain
   - 降 cosine
   - 缩短 reference
   的反向收紧。
3. 如果还要继续压窄，
   默认直接转到
   sink pocket
   false positives：
   - `001543 -> 000697`
   - `001543 -> 000799`
   看为什么这些 row
   已在
   `gain + cosine`
   sink-side，
   却仍停在 pre。

### 179. 当 `gain + cosine both` 里已经残留多个 pre 时，不要再把它们写成同一种 sink-side 残留；`000799` 与 `000697` 已经证明 false positive 会在这个 pocket 里继续分成不同语义

现象：

- 本轮把：
  - `train_001543`
  - `train_000697`
  - `train_000799`
  放进同一份 split，
  再分别做：
  - `000697 -> 001543`
  - `000799 -> 001543`
    两条独立 contrast；
- 结果显示：
  - `000799 -> sink`
    的 factor contrast
    前三位固定成：
    - `interference transient share`
    - `target_duration`
    - `interference transient mean`
  - `000697 -> sink`
    的 absolute delta
    则固定成：
    - `target_duration +1.08 sec`
    - `reference +0.84 sec`
    - `low target/interference transient`
- 同时：
  - `000799`
    相对
    `000697`
    是 shorter-duration
    那条 false positive；
  - `000697`
    则在
    `duration + reference`
    四象限里
    和
    `001589`
    一起留在
    `neither`

影响：

- 如果这时还把：
  - `gain + cosine`
    sink-side
    里的 pre
  统写成：
  - 同一残留
    只差深浅
  就会把：
  - `000799`
    的短时长 transient-collapse pocket
  和：
  - `000697`
    的 long-duration / long-reference / low-transient pocket
  再次压扁成一条假深度轴。
- 进一步还会把：
  - `000697`
    contrast 里排前的
    `gain`
  误写成主 blocker；
  但那更多只是
  它与
  `000799`
  的 case-distinguishing 项，
  不是
  `000697 -> sink`
  的主语。

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_gaincosine_falsepositive_case_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_to_sink_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_to_sink_duration_reference_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_to_sink_duration_intmean_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_pocket_falsepositive_case_contrast.md`

后续要求：

1. 之后凡是再写
   sink pocket false positives，
   默认先排除：
   - 同一种残留
     只差深浅
   这条旧口径。
2. `000799`
   默认固定写成：
   - shorter-duration
   - transient-collapse
     pocket。
3. `000697`
   默认固定写成：
   - long duration
   - long reference
   - low transient / share
     pocket。
4. 当某个 case
   在对照 residual
   里出现：
   - `gain`
     排前
   时，
   要先核对它是不是
   只是用来区分
   另一个 false positive，
   不能直接抬成
   绝对 blocker。

### 180. 当 sink-side false positive 已经被拆开后，不要只继续对 sink 做 contrast；必须先把每个 case 放回最近的已知 pre archetype，否则会把“靠近 sink 的量”误判成它的主 blocker

现象：

- 本轮对：
  - `train_000799`
  - `train_000697`
  做
  case positioning
  后发现：
  - `000799`
    最近的
    reference group
    不是 sink，
    而是：
    - `train_001589`
      那条
      weak-gain partial-mean hinge
  - `000697`
    最近的
    reference group
    不是
    `001589`，
    而是：
    - `train_000664`
      那条
      low-share `v64_only`
- 进一步做
  archetype contrast
  后又发现：
  - `000799 -> 001589`
    的
    direct residual
    前列
    固定成：
    - target transient share
    - target transient mean
    - shorter duration
    而
    `cosine`
    几乎中性
  - `000697 -> 000664`
    的
    direct residual
    前列
    固定成：
    - longer duration
    - lower interference share
    - weaker interference package
    而不是
    “同一种 low-share
    更深一点”

影响：

- 如果跳过
  archetype positioning，
  继续只看：
  - `case -> sink`
  的 contrast，
  就很容易把：
  - `000799`
    写成
    单纯更低 cosine
  - `000697`
    写成
    单纯更弱 gain
  但这两个量
  其实只是：
  - 它离 sink
    最近时
    最显眼的差
  - 不一定是
    它离最近 pre archetype
    最关键的回摆 residual
- 这样会把：
  - `000799`
    与
    `001589`
  - `000697`
    与
    `000664`
  这两条本来不同的
  local 路线
  再次压扁成
  同一条
  sink-side 假深度轴。

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_falsepositive_case_positioning/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_falsepositive_archetype_split/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmeanhinge_factor_contrast/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_factor_contrast/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_falsepositive_archetype_positioning.md`

后续要求：

1. 之后凡是再写
   sink-side false positive，
   默认先问：
   - 它最近的
     已知 pre archetype
     是谁
2. 只有先做完
   archetype positioning，
   才能决定：
   - 哪些字段
     是离 sink
     最近时最显眼的差
   - 哪些字段
     才是把它
     从最近 archetype
     拉回 pre 的主 residual
3. `000799`
   默认挂回：
   - `001589`
     partial-mean hinge
4. `000697`
   默认挂回：
   - `000664`
     low-share `v64_only`
5. 没完成这一步前，
   不要再把
   `000799 / 000697`
   写成同一种
   sink-side 残留。

### 181. archetype-local 分析里不能只看 raw neighbor rank；邻域本身常常还是 mixed shelf，必须再用 route-specific residual 投影一次，否则会把“近邻”误判成“同 pocket support”

现象：

- 本轮分别围着：
  - `train_001589`
  - `train_000664`
  做 local neighbor scan
  后发现：
  - 两个邻域
    都是
    mixed shelf
  - 都同时混着：
    - pre
    - hinge
    - crossed
  - 而且：
    - `000697`
      在
      `001589`
      邻域里
      也排得很近
    - `000799`
      在
      `000664`
      邻域里
      也排得很近
- 但进一步把邻域
  投影到
  route-specific residual
  后，
  pocket
  才真正收缩出来：
  - `001589 -> 000799`
    在
    `target transient share + target transient mean`
    上
    只剩：
    - `000799`
    - `000681`
  - `000664 -> 000697`
    在
    `duration + interference share`
    上
    只剩：
    - `000697`
    - `000904`

影响：

- 如果只因为
  某个 row
  在 archetype 邻域里
  排得近，
  就把它记成：
  - 同 pocket support
  那么就会把：
  - generic metadata 近似
  和：
  - route-specific residual
    一致
  混成一件事
- 这样会直接误判：
  - `000697`
    好像也属于
    `001589 -> 000799`
    这条 pocket
  - `000799`
    好像也属于
    `000664 -> 000697`
    这条 pocket
  但它们在
  local quadrants
  里其实都稳定落在
  `neither`
  一侧。

处理：

- 已落盘：
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_partialmean_neighbor_scan/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_v64only_neighbor_scan/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmean_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmean_duration_targetmean_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmean_targetshare_targetmean_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_slice_support/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_duration_targetshare_quadrants/summary.json`
  - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_duration_intshare_quadrants/summary.json`
  - `reports/daily/2026-03-24_candidate_v7_v65_sink_falsepositive_archetype_local_support.md`

后续要求：

1. 之后凡是做
   archetype-local support，
   默认先分两步写：
   - raw neighbor ring
   - route-specific projection
2. 只有同时满足：
   - 在邻域里排得近
   - 在 route-specific
     quadrants / slice support
     里也站在
     target side
   才能记成：
   - 同 pocket support
3. `000799`
   当前最紧的
   local support
   默认记成：
   - `000681`
4. `000697`
   当前最紧的
   local support
   默认记成：
   - `000904`
   更宽一点的
   tail support
   记成：
   - `000219`
