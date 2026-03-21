# 任务分支图

## 1. 文档目的

这份文档专门用来管理当前阶段的任务分支，防止出现下面几种常见失忆：

- 忘记当前真正的基座 checkpoint 是哪个；
- 忘记某条分支为什么被判死；
- 忘记某条 follow-up 到底是“新 coverage”还是“旧样本重路由”；
- 忘记下一条准备推进的候选分支具体入口文件在哪里。

大白话讲，这就是“当前这堆分支到底谁还活着、谁已经死了、下一步该接哪条”的总地图。

## 2. 当前裁决口径

### 参考基座

- 长期参考基线：
  - `v19`
  - checkpoint:
    - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`

### 当前 friend-side 工作基座

- 当前 absent / friend-side follow-up 的直接比较基座：
  - `v32`
  - checkpoint:
    - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1`

### 默认 keep / drop gate

- friend-side 主 gate：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- 当前最关键的 stop condition：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`
- 当前裁决解释采用三档：
  - `pass`
  - `near_tie`
    - 默认指低于 floor 不超过 `0.03 dB`
    - 只改变解释，不改变 `overall_pass`
  - `clear_fail`
- 因而：
  - `overall_pass`
    仍保持严格；
  - 但文档表述不再把所有 failed rule
    都混写成同一级别失败

## 3. 已判死分支

### `v36`

- 定义：
  - `anchor transient-extra only`
- 结论：
  - `FAIL`
- 主要原因：
  - `guodegang_anchor_proxy_v1` 对 real `guodegang_anchor_120s` 仍是错配保护项
  - exact / `0004-like` 也一起回退
- 入口：
  - `reports/daily/2026-03-19_v36_anchor_transientextra_absentunion_smoke.md`

### `v37`

- 定义：
  - `v32 + absent reconstruction_extra`
- 结论：
  - `FAIL`
- 主要原因：
  - `guodegang_absent_proxy_v3_strict` 早已在 base manifest 中
  - 这条线本质是 objective re-routing，不是 coverage 扩样
  - `guodegang` floor 回拉一点，但 exact / `0004-like speech-leak` 变差
- 入口：
  - `reports/daily/2026-03-19_reconstruction_extra_branch_and_v37_absent_followup.md`

### `v38`

- 定义：
  - `v37` 的 lighter waveform-only absent reconstruction + stronger friend extra
- 结论：
  - `FAIL`
- 主要原因：
  - 说明冲突不只是 `interference_extra_weight` 不够大
  - absent-side objective 已经在改写 shared hard `target_full` 优化方向
- 入口：
  - `reports/daily/2026-03-19_v38_absentreconwave_friendextra_rebalance.md`

### `v39`

- 定义：
  - `v32 + v5 cleancarve metadata carve-out + waveform-only reconstruction_extra`
- 结论：
  - `FAIL`
- 主要原因：
  - synthetic `v5 cleancarve` 子集虽然转正
  - 但 real gate 仍 failed：
    - exact `target_full`
    - `speech_leak_like (0004)`
    - `guodegang_anchor`
    - `guodegang_absent`
- 入口：
  - `reports/daily/2026-03-19_v39_absent_recon_cleancarve_followup.md`

### `v40`

- 定义：
  - `v39 selected carve-out - exact overlap`
- 结论：
  - `FAIL`
- 主要原因：
  - 去掉 overlap 之后，
    broad near-real overall 虽仍在 gate 容忍区；
  - 但关键 real floor 仍 failed：
    - exact `target_full = -0.467909 dB`
    - `speech_leak_like (0004) = -0.086817 dB`
    - `guodegang_anchor_120s = -0.099242 dB`
    - `guodegang_absent_480s = -0.057473 dB`
  - 连 `proxy_v6` 本体也仍是：
    - `-0.424082 dB`
- 入口：
  - `reports/daily/2026-03-19_v40_v41_absent_followup_results.md`

### `v41`

- 定义：
  - `v32 + reconstruction_extra(proxy_v6 currentsignal cleanonly allowlist)`
- 结论：
  - `FAIL`
- 主要原因：
  - exact proxy overall 虽转为：
    - `+0.036695 dB`
  - 但真正关键的裁决证据仍是回退：
    - exact `target_full = -0.325134 dB`
    - `speech_leak_like (0004) = -0.062535 dB`
    - `guodegang_anchor_120s = -0.258474 dB`
    - `guodegang_absent_480s = -0.112892 dB`
  - `proxy_v6` 本体更进一步转负：
    - `-0.627418 dB`
  - gate 还额外 failed：
    - `speech_probe_overall_floor`
- 入口：
  - `reports/daily/2026-03-19_v40_v41_absent_followup_results.md`

### `v42`

- 定义：
  - `v32 + reconstruction_extra(proxy_v7 high-overlap low-target-transient low-int-trans)`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 这次不是 absent-side real floor 全线失败；
  - 相反：
    - `guodegang_anchor_120s = +0.126568 dB`
    - `guodegang_absent_480s = +0.031863 dB`
    都已经转正；
  - 但 friend-side 两条关键 floor 仍明显回退：
    - exact `target_full = -0.664459 dB`
    - `speech_leak_like (0004) = -0.113430 dB`
  - relative to `v32` gate，
    只 failed：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
  - 因此当前失败点更像：
    - `reconstruction_extra(proxy_v7)` routing
      仍未和 friend-side speech-leak 解耦；
    - 而不是 `proxy_v7` 本体无效
- 入口：
  - `reports/daily/2026-03-19_v42_absent_proxy_v7_followup.md`

### `v43`

- 定义：
  - `v42` 的 lighter-weight follow-up
  - 唯一变化：
    - `reconstruction_extra_waveform_weight: 0.005 -> 0.0025`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 结果几乎与 `v42` 重合；
  - friend-side 仍 clear fail：
    - exact `target_full = -0.663965 dB`
    - `speech_leak_like (0004) = -0.113233 dB`
  - 但 `guodegang_anchor / absent`
    仍保持正向：
    - `+0.125676 dB`
    - `+0.031660 dB`
  - 说明当前 `proxy_v7`
    的微幅 waveform weight rescale
    基本是 no-op
- 入口：
  - `reports/daily/2026-03-19_gate_margin_reassessment_and_v43_followup.md`

### `v44`

- 定义：
  - `v32 + reconstruction_extra_stft_only(proxy_v7)`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 相对 `v42 / v43`，
    `stft_only`
    确实略微回收了：
    - exact `target_full`
    - `speech_leak_like (0004)`
  - 但幅度仍不足以脱离 clear fail：
    - exact `target_full = -0.647221 dB`
    - `speech_leak_like (0004) = -0.110539 dB`
  - 同时：
    - default 变弱
      - `+0.072833 dB`
    - `proxy_v7` 本体也变弱
      - `+0.359405 dB`
  - 因而：
    - 单纯 `stft_only`
      不是这条线的解法；
    - 但它说明 routing mode 变化
      比微幅 wave weight rescale
      更有信号
- 入口：
  - `reports/daily/2026-03-19_v44_proxy_v7_stft_followup.md`

### `v45`

- 定义：
  - `proxy_v7` 内部按 `full / nonfull` split routing
  - `nonfull -> reconstruction waveform`
  - `full -> reconstruction_extra stft`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 比 `v44` 更平衡地保住了：
    - default
    - `proxy_v7`
    - `guodegang_anchor / absent`
  - 但 friend-side 仍 clear fail：
    - exact `target_full = -0.653286 dB`
    - `speech_leak_like (0004) = -0.111924 dB`
  - 因此：
    - `full / nonfull` split routing
      是有信号的；
    - 但当前这一级 split
      还不足以形成 keep 候选
- 入口：
  - `reports/daily/2026-03-19_v45_proxy_v7_splitrouting_followup.md`

### `v46`

- 定义：
  - `proxy_v7 nonfull-only reconstruction`
  - `proxy_v7 full` 完全退出 absent reconstruction
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 即便把 `full` 组完全拿掉，
    friend-side 两条仍几乎不回收：
    - exact `target_full`
    - `speech_leak_like (0004)`
  - 同时：
    - default 仍正
    - `proxy_v7` 仍正
    - `guodegang_anchor / absent`
      仍正
  - 这说明当前冲突不只是：
    - `proxy_v7 full`
      的局部 selector 冲突；
    - 而更像是 absent-side reconstruction
      通过共享参数更新
      全局改写了 friend-side 行为
- 入口：
  - `reports/daily/2026-03-19_v46_proxy_v7_nonfullonly_followup.md`

### `v47`

- 定义：
  - `proxy_v7 all ids`
    继续使用 `v42`
    同级 reconstruction
  - 仅允许：
    - `ref_encoder`
    - `condition_proj`
    继续训练
  - trainable parameter count：
    - `131,968 / 2,367,617`
    - `5.57%`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - friend-side 确实几乎被拉回：
    - `exact_target_full_gain_floor = pass`
    - `speech_leak_like_gain_floor = near_tie`
  - 但 absent-side 本体直接塌掉：
    - `proxy_v7 = -0.858876 dB`
    - `guodegang_anchor / absent`
      也都回到负向
- 解释：
  - 纯 ref-conditioning freeze
    对 friend-side 太友好，
    但对 absent-side
    过于保守；
  - 当前需要的不是：
    - 更少参数更新
  - 而是：
    - 给 absent-side
      一点专属 output plasticity，
      但别再改写共享主干
- 入口：
  - `reports/daily/2026-03-20_v47_v48_prefix_freeze_decoupling_followup.md`

### `v48`

- 定义：
  - 在 `v47`
    基础上额外放开：
    - `mask_head`
  - trainable parameter count：
    - `329,345 / 2,367,617`
    - `13.91%`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - default 与 `proxy_v7`
    的确比 `v47`
    回来了一些；
  - 但 `proxy_v7`
    仍为负向；
  - 同时 friend-side 两条重新 clear fail：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
- 解释：
  - 单纯放开一个 shared `mask_head`
    还不是真正足够的 decoupling；
  - 它有一点 output-side plasticity，
    但还不够 branch-local
- 入口：
  - `reports/daily/2026-03-20_v47_v48_prefix_freeze_decoupling_followup.md`

### `v49`

- 定义：
  - 启用：
    - `adapter_mask_head`
  - `reconstruction_extra(proxy_v7)`
    只走 adapter-combined output
  - shared base losses
    继续只看 `estimated_waveform_base`
  - 仅训练：
    - `adapter_mask_head`
  - `adapter_mask_max_delta = 0.25`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `proxy_v7`
    在这条 simple residual adapter 上
    明显反向：
    - `-1.542894 dB`
  - friend-side 也没被真正守住：
    - exact `target_full`
      仍 clear fail
- 解释：
  - “给 absent-side 独立输出分支”
    这个大方向是对的；
  - 但当前这条
    simple output residual adapter
    还不够表达
- 入口：
  - `reports/daily/2026-03-20_v49_v50_adaptermask_followup.md`

### `v50`

- 定义：
  - 与 `v49`
    相同，
    仅改：
    - `adapter_mask_max_delta = 0.05`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - friend-side 已回到 near-tie：
    - exact `target_full`
    - `speech_leak_like`
    - `guodegang_absent`
      都只差 very small negative delta
  - 但 `proxy_v7`
    仍明显负向：
    - `-1.082981 dB`
- 解释：
  - `v49`
    的问题部分确实来自 residual step 太大；
  - 但即便把幅度压小，
    simple adapter branch
    仍拉不回 absent proxy 本体
- 入口：
  - `reports/daily/2026-03-20_v49_v50_adaptermask_followup.md`

### `v51`

- 定义：
  - `adapter_mask_head`
    保留
  - adapter branch
    额外启用：
    - `adapter_conditioning_mode = ref_film`
  - 仅训练：
    - `adapter_condition_scale`
    - `adapter_condition_shift`
    - `adapter_mask_head`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - friend-side 仍只到 near-tie；
  - `proxy_v7`
    仍明显负向：
    - `-1.016036 dB`
- 解释：
  - 当前问题不只是：
    - adapter branch 没看到 reference
  - 即便 adapter
    已吃到自己的 reference-conditioned feature，
    absent proxy 本体仍拉不回
- 入口：
  - `reports/daily/2026-03-20_v51_v52_adapter_conditioning_and_temporal_followup.md`

### `v52`

- 定义：
  - `adapter_mask_head`
    保留
  - adapter branch
    额外启用：
    - `adapter_temporal_model`
    - `adapter_gru_layers = 1`
  - 仅训练：
    - `adapter_temporal_model`
    - `adapter_mask_head`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - friend-side 仍只到 near-tie；
  - `proxy_v7`
    仍明显负向：
    - `-0.876078 dB`
- 解释：
  - 当前缺的已经不是：
    - adapter branch 更强一点的 conditioning
    - 或更大一点的 temporal capacity
  - 即便给 adapter branch
    自己的一层双向 GRU，
    也仍拉不回 absent proxy 本体
- 入口：
  - `reports/daily/2026-03-20_v51_v52_adapter_conditioning_and_temporal_followup.md`

### `v53`

- 定义：
  - 第一条正式
    `dual-head / branch-local decoder`
    候选
  - `enable_branch_decoder_head = true`
  - 仅训练：
    - `branch_decoder_temporal_model`
    - `branch_decoder_mask_head`
  - 当前实际有效梯度：
    - `reconstruction_extra(proxy_v7)`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `proxy_v7 / guodegang`
    明显更强，
    说明 dual-head 不是没方向；
  - 但 friend-side 两条仍 clear fail：
    - exact `target_full = -0.875034 dB`
    - `speech_leak_like (0004) = -0.104842 dB`
  - 更关键的是：
    - 这时 friend-side extra guardrail
      还没有真正回流到 branch decoder
- 解释：
  - `v53`
    不应记成：
    - dual-head fully tested and failed
  - 而应记成：
    - single-sided absent training on dual-head
- 入口：
  - `reports/daily/2026-03-20_v53_v54_dualdecoder_followup.md`

### `v54`

- 定义：
  - `v53`
    基础上，
    把 `v30 exact 10 ids`
    的 `interference_extra`
    真正路由到 branch decoder
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 这次不是 extra routing 没接上；
    已确认：
    - train `7 / 129`
    - val `3 / 37`
  - 但结果表明：
    - `proxy_v7 / guodegang`
      继续更强：
      - `proxy_v7 = +2.016788 dB`
      - `guodegang_anchor = +0.465969 dB`
      - `guodegang_absent = +0.097155 dB`
    - friend-side 却更差：
      - exact `target_full = -1.349682 dB`
      - `speech_leak_like (0004) = -0.128521 dB`
- 解释：
  - 当前 dual-head 的阻塞点
    已不再是：
    - extra routing 没接上
  - 而是：
    - 现有 friend-side
      `interference_extra residual_projection_ratio`
      即便接到 branch decoder，
      也不会形成 keep 方向的有效对冲
- 入口：
  - `reports/daily/2026-03-20_v53_v54_dualdecoder_followup.md`

### `v55`

- 定义：
  - `v53`
    同一条 dual-head 底座上，
    不再用 `interference_extra`
    residual objective，
    而是只挂：
    - exact-family `SI-SDR guard`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - exact family 与 `proxy_v7`
    都明显更强；
  - 但 near-real 尤其 `guodegang`
    明显转负：
    - `guodegang_anchor = -0.494584 dB`
    - `guodegang_absent = -0.157483 dB`
- 解释：
  - 这条 protect objective
    仍然更像：
    - exact-family overfit
  - 而不是：
    - dual-head 上有效的 friend-side protect
- 入口：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

### `v56`

- 定义：
  - 第一条 dual-head `base-align`
    protect 尝试
- 结论：
  - `invalid / plumbing-only`
- 主要原因：
  - 当时 selector 激活逻辑
    还没把：
    - `interference_extra_base_align_weight`
      算进 `interference_extra`
  - 结果 exact ids
    根本没真正命中
    `base-align`
- 解释：
  - `v56`
    不能拿来判：
    - dual-head `base-align`
      本身有没有方向；
  - 有效结论应从：
    - `v57`
      开始看
- 入口：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

### `v57`

- 定义：
  - dual-head + `proxy_v7 reconstruction`
  - 再挂：
    - strong `base-align`
    - `interference_extra_base_align_weight = 0.02`
- 结论：
  - `NOT keep`
- 主要原因：
  - 这是目前最接近 gate
    的 dual-head protect 版本；
  - 但代价是：
    - `proxy_v7 = -1.498264 dB`
      直接塌掉
- 解释：
  - `base-align`
    是有信号的 protect primitive；
  - 但 `v57`
    属于“保护过头”，
    不是 keep
- 入口：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

### `v58`

- 定义：
  - 与 `v57`
    相同，
    仅把：
    - `interference_extra_base_align_weight`
      从 `0.02`
      放轻到 `0.005`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `proxy_v7 / guodegang`
    已能回到近零或正向；
  - 但：
    - `speech_leak_like (0004) = -0.076592 dB`
      又掉回 clear fail
- 解释：
  - `v57`
    说明：
    - protect primitive 方向是对题的；
  - `v58`
    又说明：
    - 缺的不是“同一条 weight 再扫一点点”
    - 而是更直接面向
      `speech_leak_like (0004)`
      的新 protect objective
- 入口：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

### `v59`

- 定义：
  - 第一条正式
    `base-delta-interference projection`
    候选
  - friend-side protect：
    - `interference_extra_base_delta_projection_weight = 0.005`
    - `focus = v30 exact 10 ids`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `proxy_v7 / guodegang`
    明显更强：
    - `proxy_v7 = +1.597651 dB`
    - `guodegang_anchor = +0.356478 dB`
    - `guodegang_absent = +0.070337 dB`
  - 但 friend-side
    仍 clear fail：
    - exact `target_full = -0.983311 dB`
    - `speech_leak_like (0004) = -0.117378 dB`
  - 更关键的是：
    - protect 项虽然命中了 exact ids，
      但量级几乎为 `0`
- 解释：
  - 当前不是：
    - primitive 没接上
  - 而是：
    - 它没有真正碰到
      现在坏掉的 `0004-like` 行为
- 入口：
  - `reports/daily/2026-03-20_v59_v60_dualdecoder_basedeltaproj_followup.md`

### `v60`

- 定义：
  - `v59`
    的更强档位
  - `interference_extra_base_delta_projection_weight = 0.02`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - 结果与 `v59`
    仅是微小扰动；
  - 仍然卡在：
    - exact `target_full`
    - `speech_leak_like (0004)`
  - protect 项量级也仍接近 `0`
- 解释：
  - 这条 primitive
    当前不值得继续扫权重；
  - `0.005 -> 0.02`
    没有带来新的结构性变化
- 入口：
  - `reports/daily/2026-03-20_v59_v60_dualdecoder_basedeltaproj_followup.md`

### `v61`

- 定义：
  - `dual-head + proxy_v7 reconstruction`
  - friend-side protect
    改为：
    - `target_full`-only `base-align`
    - `interference_extra_base_align_weight = 0.02`
  - protect selector：
    - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt`
- 结论：
  - `NOT keep`
- 主要原因：
  - 这是目前最有信息量的一次 selector 修正；
  - `target_full`
    明显从此前
    `-0.95 / -0.98 dB`
    级别回收到：
    - `-0.369736 dB`
  - `speech_leak_like (0004)`
    也只剩 near-tie：
    - `-0.071034 dB`
  - 同时：
    - `guodegang_anchor = +0.069889 dB`
    - `guodegang_absent = +0.043306 dB`
    都保持正向；
  - 但相对 `v32` gate
    仍有：
    - `exact_target_full_gain_floor = clear_fail`
- 解释：
  - `v61`
    不能记成：
    - keep 候选
  - 但也不能只记成：
    - 又一次 fail
  - 它真正写死的是：
    - `base-align`
      的关键问题之一
      确实是 selector 过粗；
    - 只保护 `target_full` 子集
      是对的
- 入口：
  - `reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`

### `v62`

- 定义：
  - `v61`
    的更强档位
  - 仅改：
    - `interference_extra_base_align_weight = 0.05`
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `speech_leak_like (0004)`
    只小幅改善到：
    - `-0.063768 dB`
  - 但 exact `target_full`
    明显变差到：
    - `-0.586134 dB`
  - 同时：
    - `proxy_v7 = +0.861507 dB`
    - `guodegang_anchor = +0.118074 dB`
    又继续变强
- 解释：
  - `v62`
    说明当前不该继续把
    同一条 `target_full`-only `base-align`
    primitive 往上加权；
  - 现在缺的不是：
    - “最后一点 weight”
  - 而是：
    - 在保留 `target_full`
      保护的同时，
      单独补一条更直接面向
      `speech_leak_like (0004)`
      的 protect objective
- 入口：
  - `reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`

## 4. 当前分支状态

### 分支 `B1`: `v5 cleancarve` 内继续细粒度 carve-out

- 状态：
  - `closed / failed`
- 当前判断：
  - `v40` 已证明：
    单纯去掉 exact overlap
    还不足以把 absent-side real gate 拉回
- 已知事实：
  - `v40` relative to `v19`：
    - exact `target_full = -0.467909 dB`
    - `speech_leak_like (0004) = -0.086817 dB`
    - `guodegang_anchor_120s = -0.099242 dB`
    - `guodegang_absent_480s = -0.057473 dB`
    - `proxy_v6 = -0.424082 dB`

### 分支 `B2`: 更贴近 near-real `guodegang_absent` 的保护代理

- 状态：
  - `closed / failed`
- 当前判断：
  - `v41` 已证明当前
    `proxy_v6 currentsignal cleanonly`
    还不是可保留的 near-real absent 保护代理
- 已知事实：
  - `v41` relative to `v19`：
    - exact `target_full = -0.325134 dB`
    - `speech_leak_like (0004) = -0.062535 dB`
    - `guodegang_anchor_120s = -0.258474 dB`
    - `guodegang_absent_480s = -0.112892 dB`
    - `proxy_v6 = -0.627418 dB`
  - relative to `v32` 的 gate：
    - 额外 failed
      `speech_probe_overall_floor`

### 分支 `B3`: 重新定义 absent-side protection proxy / real-floor guardrail

- 状态：
  - `active / proxy found`
- 当前判断：
  - `B1 / B2` 当前这两条收紧版都已失败；
  - 但 `v42` 已说明：
    - 新的 `proxy_v7`
      不是旧 rows 重路由；
    - val 侧 `0` exact overlap；
    - 且能把
      `guodegang_anchor / absent`
      两条 real floor
      同时拉回正向
- 已知事实：
  - `v7` 物化后：
    - train `33`
    - val `8`
  - 与 `v32` base 的关系：
    - 新增 coverage：
      - train `32`
      - val `8`
  - `v42` relative to `v19`：
    - default `+0.077955 dB`
    - exact `target_full = -0.664459 dB`
    - `speech_leak_like (0004) = -0.113430 dB`
    - `guodegang_anchor_120s = +0.126568 dB`
    - `guodegang_absent_480s = +0.031863 dB`
    - `proxy_v7 = +0.444459 dB`
  - `v43` relative to `v19`：
    - default `+0.077610 dB`
    - exact `target_full = -0.663965 dB`
    - `speech_leak_like (0004) = -0.113233 dB`
    - `guodegang_anchor_120s = +0.125676 dB`
    - `guodegang_absent_480s = +0.031660 dB`
    - `proxy_v7 = +0.440865 dB`
  - `v44` relative to `v19`：
    - default `+0.072833 dB`
    - exact `target_full = -0.647221 dB`
    - `speech_leak_like (0004) = -0.110539 dB`
    - `guodegang_anchor_120s = +0.113703 dB`
    - `guodegang_absent_480s = +0.029381 dB`
    - `proxy_v7 = +0.359405 dB`
  - `v45` relative to `v19`：
    - default `+0.075720 dB`
    - exact `target_full = -0.653286 dB`
    - `speech_leak_like (0004) = -0.111924 dB`
    - `guodegang_anchor_120s = +0.119305 dB`
    - `guodegang_absent_480s = +0.029907 dB`
    - `proxy_v7 = +0.396169 dB`
  - `v46` relative to `v19`：
    - default `+0.077715 dB`
    - exact proxy overall `-0.315450 dB`
    - `speech_leak_like (0004) = -0.113260 dB`
    - `guodegang_anchor_120s = +0.126034 dB`
    - `guodegang_absent_480s = +0.031888 dB`
    - `proxy_v7 = +0.441273 dB`
  - `v47` relative to `v19`：
    - default `+0.018882 dB`
    - exact `target_full = -0.290016 dB`
    - `speech_leak_like (0004) = -0.042893 dB`
    - `guodegang_anchor_120s = -0.059132 dB`
    - `guodegang_absent_480s = -0.007238 dB`
    - `proxy_v7 = -0.858876 dB`
  - `v48` relative to `v19`：
    - default `+0.061926 dB`
    - exact `target_full = -0.347332 dB`
    - `speech_leak_like (0004) = -0.089823 dB`
    - `guodegang_anchor_120s = -0.014192 dB`
    - `guodegang_absent_480s = -0.017526 dB`
    - `proxy_v7 = -0.274633 dB`
  - `v49` relative to `v19`：
    - default `+0.004926 dB`
    - exact `target_full = -0.406366 dB`
    - `speech_leak_like (0004) = -0.048850 dB`
    - `guodegang_anchor_120s = -0.056997 dB`
    - `guodegang_absent_480s = -0.015182 dB`
    - `proxy_v7 = -1.542894 dB`
  - `v50` relative to `v19`：
    - default `+0.013945 dB`
    - exact `target_full = -0.323341 dB`
    - `speech_leak_like (0004) = -0.042961 dB`
    - `guodegang_anchor_120s = -0.064364 dB`
    - `guodegang_absent_480s = -0.013611 dB`
    - `proxy_v7 = -1.082981 dB`
  - `v51` relative to `v19`：
    - default `+0.015467 dB`
    - exact `target_full = -0.317694 dB`
    - `speech_leak_like (0004) = -0.042935 dB`
    - `guodegang_anchor_120s = -0.064897 dB`
    - `guodegang_absent_480s = -0.013696 dB`
    - `proxy_v7 = -1.016036 dB`
  - `v52` relative to `v19`：
    - default `+0.017187 dB`
    - exact `target_full = -0.310738 dB`
    - `speech_leak_like (0004) = -0.041941 dB`
    - `guodegang_anchor_120s = -0.065335 dB`
    - `guodegang_absent_480s = -0.013233 dB`
    - `proxy_v7 = -0.876078 dB`
- 当前缺口：
  - 现在不再缺 absent proxy 本体；
  - 当前真正缺的是：
    - 如何在保留 `proxy_v7`
      的同时，
      不再同步拖坏
      `exact target_full`
      与 `speech_leak_like (0004)`
  - 同时已知：
    - 微幅 waveform weight 缩放
      基本不改变这条结论
    - 单纯切成 `stft_only`
      虽然比 wave-only 更有信号，
      但仍不足以越过 friend-side 两条 clear fail
    - `full / nonfull` split routing
      比单一路由更像正确方向，
      但当前仍未把两条 clear fail
      拉回 near-tie
    - 即便把 `full`
      完全退出 absent reconstruction，
      friend-side 两条仍几乎不回收；
      问题更像共享参数层面的全局耦合
    - 纯 ref-conditioning freeze
      虽能把 friend-side
      拉回 `near_tie / pass`，
      但会让 `proxy_v7`
      与 real `guodegang`
      一起塌掉
    - 再放开 shared `mask_head`
      虽可恢复一部分 default / proxy，
      但还没等 `proxy_v7`
      回到正向，
      friend-side 两条就先重新坏掉了
    - simple output residual adapter
      已证明：
      - 大残差会把 absent proxy 明显推反
      - 小残差只能把 friend-side
        拉回 near-tie，
        但仍带不回 absent proxy 本体
    - 继续给 adapter branch
      增加：
      - reference conditioning
      - 或自己的 temporal model
      也仍然只能把结果压到 near-tie，
      拉不回 absent proxy 本体
    - `dual-head / branch-local decoder`
      的工程底座现已补齐：
      - `enable_branch_decoder_head`
      - `reset_branch_decoder_from_base()`
      - `--model-enable-branch-decoder-head`
      - `v32 -> tmp/smoke_branch_decoder_v53`
        已跑通 1-step smoke
    - 因而当前默认下一条
      已不再是“继续补 plumbing”，
      而是：
      - 直接跑第一条正式 dual-head follow-up
    - `v53`
      已证明：
      - dual-head 本身不是没方向；
      - `proxy_v7 / guodegang`
        可被明显拉强；
      - 但若 friend-side extra guardrail
        没真正回流到 branch decoder，
        它就会变成单边 absent 训练
    - `v54`
      已证明：
      - 把现有 friend-side
        `interference_extra residual_projection_ratio`
        真接到 branch decoder，
        也不会把它拉向 keep；
      - 反而会把
        `proxy_v7 / guodegang`
        与 friend-side clear fail
        一起放大
    - `v55`
      已证明：
      - exact-family `SI-SDR guard`
        在 dual-head 上
        仍是 overfit 型 protect；
      - 不能把
        exact / `proxy_v7`
        变强
        直接等价成：
        friend-side protect 已成立
    - `v56`
      记为：
      - invalid plumbing round；
      - 不纳入模型结论
    - `v57`
      已证明：
      - `base-align`
        是有信号的 protect primitive；
      - 它能把 dual-head
        拉到非常接近 gate；
      - 但强版本会直接压塌
        `proxy_v7`
    - `v58`
      已证明：
      - 把 `base-align`
        放轻后，
        `proxy_v7 / guodegang`
        能回来；
      - 但 `speech_leak_like (0004)`
        又重新 clear fail
      - 因而当前缺的
        不是同一条 `base-align` weight
        的再细扫，
        而是更直接面向
        `speech_leak_like (0004)`
        的 protect objective
    - `v59 / v60`
      已证明：
      - `base-delta-interference projection`
        不是没接上；
      - 但它在当前 exact ids 上
        的实际 loss 量级几乎为 `0`
      - 所以会继续允许：
        - `proxy_v7 / guodegang`
          很强
        - friend-side
          `target_full / 0004`
          继续 clear fail
      - 因而这条 primitive
        当前也不值得继续扫权重
    - `v61`
      已证明：
      - 把 protect selector
        收窄到 `target_full` 子集
        是有效修正；
      - 这不是 trivial 摆动，
        而是把：
        - exact `target_full`
        - `0004`
        - `guodegang`
        三者同时拉回到更平衡的区间
    - `v62`
      已证明：
      - 在这个更细 selector 上，
        继续把同一条 `base-align`
        weight 往上推，
        不是 closing gap 的正确方向；
      - 当前缺的已不是：
        - 同一 primitive 的更强档
      - 而是：
        - 面向 `0004-like speech leak`
          的第二条显式 protect 信号
    - 当前已补好第二条 protect selector
      的工程入口：
      - `branch_protect`
      - `--loss-branch-protect-guard-sisdr-weight`
      - `--loss-branch-protect-*`
      - `tmp/smoke_branch_protect_guard_sisdr`
        已完成 1-step smoke
      - 已确认：
        - selector 命中
        - train / eval summary
          新指标落盘
      - 因而下一条已不再缺：
        - 双 protect selector
          的 plumbing
    - `v63`
      已实际执行并失败：
      - `target_full`
        确实继续收回；
      - 但 `0004-like`
        没有被真正拉正；
      - `guodegang_anchor / absent`
        反而一起转负；
      - 额外 metadata 复盘已确认：
        - `exact_nontargetfull`
          并不是
          `0004-like`
          的保守近似，
          而几乎全是
          `target_absent_head / tail`
          子集
      - 因而：
        - `exact_all - exact_targetfull_all`
          不再保留为
          第二 protect selector
          的默认定义
    - `v64`
      已实际执行并回收：
      - 第二 selector
        改成直接的
        `v23 friend speech_leak exact minus target_full`
      - 但仍直接跑在默认
        `v42` split 上，
        `branch_protect`
        实际命中只有：
        - train `1 / 129`
        - val `0 / 37`
      - gate 结果为：
        - 只剩
          `speech_leak_like_gain_floor`
          一个 `near_tie`
      - 因而：
        - 这条 selector
          语义上
          比 `exact_nontargetfull`
          更像对题；
        - 但当前 hit 太稀，
          不能直接记成 keep
    - `v65`
      已实际执行并回收：
      - 把上述 `v23minus`
        rows 真正 union
        进 train / val manifest
      - `branch_protect`
        命中补到：
        - train `7 / 135`
        - val `2 / 39`
      - `target_full`
        进一步转正到：
        - `+0.031807 dB`
      - 但：
        - `speech_leak_like (0004)`
          仍未转正；
        - `guodegang_anchor / absent`
          明显转负
      - 因而：
        - 单纯 union
          这批 rows
          不是 keep 方向；
        - 当前不应再直接沿
          `v65`
          放大训练预算

### `v64`

- 定义：
  - `v63`
    之后的第一条恢复验证轮次
  - `target_full`-only `base-align`
    保持不变
  - 第二 protect selector
    改为：
    - `sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_all.txt`
- 结论：
  - `NOT keep`
  - `closed_but_evidence_keep`
- 主要原因：
  - 相对 `v32` gate
    只剩：
    - `speech_leak_like_gain_floor`
      一个 `near_tie`
  - `guodegang_anchor / absent`
    继续保持正向
  - 但 `branch_protect`
    在当前 split
    实际命中过稀，
    还不足以形成可保留候选
- 解释：
  - `v64`
    不应记成：
    - “又一次普通 fail”
  - 它真正写死的是：
    - 直接对准
      `exact minus target_full`
      的 selector
      语义上更对；
    - 但若这批 rows
      没有真实并入
      当前 manifest，
      证据强度仍然不够
- 入口：
  - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`

### `v65`

- 定义：
  - `v64`
    的 union-manifest follow-up
  - 将：
    - `train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
    - `val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
    作为新的 train / val split
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `target_full`
    虽明显更强，
    甚至转正；
  - 但 `speech_leak_like (0004)`
    仍未过线；
  - 同时：
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`
      都变成 `clear_fail`
- 解释：
  - `v65`
    证明当前问题
    不是简单的
    “让第二 selector
    多命中一点”
  - 一旦真的补足 coverage，
    这条线仍会把
    `guodegang`
    保护项重新打坏
- 入口：
  - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`

## 5. 下一条默认执行分支

如果下一轮没有新用户决策，默认暂停，不启动新实验。

即：

1. 当前项目状态应固定区分为两层：
   - 默认主线：
     - `legacy stage2`
     - status: `mainline_keep`
   - 研究基座：
     - `v19`
     - `v32`
     - `proxy_v7`
     - dual-head / branch-local decoder
     - status: `research_base_keep`
2. 当前 `v36+`
   默认解释为：
   - 研究排雷分支；
   - 不是主线替换候选序列；
3. 默认不再回到
   `proxy_v6 currentsignal cleanonly`
   或继续重做 overlap carve-out；
4. 默认也不继续扫
   `proxy_v7` 的微幅 waveform weight rescale；
5. 单纯 `stft_only`
   也不作为默认延伸方向；
6. 默认不再继续扫：
   - prefix-freeze 小组合
   - simple residual adapter 的小参数
   - adapter branch 的 conditioning / temporal 变体
   - `interference_extra residual_projection_ratio`
     在 dual-head 上的权重或同类小变体
   - `interference_extra_base_align_weight`
     的近邻小变体
   - `interference_extra_base_delta_projection_weight`
     的近邻小变体；
7. `v63`
   已完成并判定：
   - `closed_failed`
8. `v64`
   已完成并判定：
   - `closed_but_evidence_keep`
9. `v65`
   已完成并判定：
   - `closed_failed`
10. 当前不再把：
   - `exact_all - exact_targetfull_all`
   解释为：
   - `0004-like branch_protect selector`
11. 若后续继续 dual-protect，
   默认前置动作改为：
   - 先重建真正对应
     `speech_leak_like (0004)`
     的第二 selector / proxy
   - 不直接重跑
     `v64`
   - 不直接放大
     `v65`
   - 不继续扫现有
     `branch_protect` weight
12. 当前分支标签应固定写成：
   - `v57 / v58 = closed_but_evidence_keep`
   - `v54 / v55 / v59 / v60 = closed_failed`
   - `v63 = closed_failed`
   - `v64 = closed_but_evidence_keep`
   - `v65 = closed_failed`
13. 只有在用户明确允许时，
   才重新从：
   - `v32`
     warm-start
   - 并按同一套裁决口径重新走：
     - 训练
     - default / exact / near-real / guodegang eval
     - `friend_speech_leak_followup_gate`
14. 当前 `0004-like speech_leak`
    已补出第一份公共搜索底座：
    - `data/synthetic/val_manifest_friend_speech_leak_search_v1.jsonl = 50`
    - 作用是统一 shared `sample_id`
      compare 输入，
      不是直接定义真 proxy
15. 当前已物化第一份新 candidate family：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v1.jsonl = 12`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v1.jsonl = 3`
16. 这份 `candidate_v1`
    当前只能解释为：
    - 新的 `0004-like speech_leak` 候选 family
    - 不是已经确认的真 `branch_protect` proxy
17. 下一步若继续，
    默认不是直接训练，
    而是继续在 shared search manifest 上
    加负约束，
    优先避免：
    - `v65` 仍显著占优
    - `v20` 仍明显落后
18. 当前已补第一条 `v65` guard candidate：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v2_guardv65.jsonl = 13`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v2_guardv65.jsonl = 3`
19. 这条 `candidate_v2_guardv65`
    的性质应写成：
    - 比 `candidate_v1` 更干净
    - 但辨识度更弱
    - 不能直接当成正式训练入口
20. 当前最可继续细化的 working candidate
    已改成：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v3_guardv20.jsonl = 10`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v3_guardv20.jsonl = 3`
21. `candidate_v3_guardv20`
    当前性质应写成：
    - 比 `candidate_v2_guardv65` 更有辨识度
    - 比 `candidate_v1` 更少受 `v65` 伪阳性拖偏
    - 但仍不是正式训练入口
22. 下一步若继续，
    默认优先细化：
    - `candidate_v3_guardv20`
    而不是回到：
    - `candidate_v1`
    - 或只继续收紧 `candidate_v2_guardv65`
23. `candidate_v3_guardv20`
    的标准 selector 资产也已补齐：
    - `sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_{train,val,all}.txt`
24. 当前已完成第一条直接使用
    `candidate_v3_guardv20`
    做 `branch_protect`
    的 dual-head follow-up：
    - `v66 = baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v66_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_candv3_0002_ft1`
    - relative to `v32`
      的 real gate：
      - 只剩
        `speech_leak_like_gain_floor = clear_fail`
      - `default / speech probe overall / exact target_full / guodegang_anchor / guodegang_absent`
        均通过
25. `v66`
    现已补齐此前缺失的
    `candidate_v3`
    synthetic 方向诊断：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v3_guardv20_direction_analysis/summary.json`
    - aggregate 排名为：
      - `v66 > v64 > v35 > v20 > v30 > v32 > v29 > v25 > v65 > v24 > v19`
    - `v66 - v32 = +0.051855 dB`
    - 说明训练 aggregate 方向
      已经沿新 `candidate_v3`
      rows 推正
    - 但 row-level 仍弱：
      - strict samplewise order-pass = `0 / 3`
      - `v66` 单条 rank = `7 / 10 / 1`
26. 因而当前关于 `v66`
    的正确解释应固定为：
    - 不是
      “branch_protect routing
       完全没起作用”
    - 而是
      `candidate_v3`
      这条 proxy
      已能提供 aggregate 正向信号，
      但 row-level 语义仍不够硬，
      还不足以闭环 real `0004`
27. `v66` 诊断之后，
    已继续补第一轮
    `v64>v66`
    导向的 proxy follow-up 搜索：
    - 若直接放掉
      `v25 > v24`
      去找 order-pass family，
      会回到：
      - 高 gain
      - 高 target transient
      的 strong-transient 家族
      - 不作为下一条默认 proxy
28. 当前新物化的 follow-up candidate 为：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 33`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 10`
    - `sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_{train,val,all}.txt`
    - 当前 val aggregate 排名：
      - `v64 > v66 > v65 > v20 > v30 > v32 > v35 > v29 > v25 > v24`
    - 其中：
      - `v64 - v66 = +0.003908 dB`
      - `v66 - v65 = +0.015052 dB`
    - 且保留了：
      - `v35 > v25 > v24`
      - `v20 > v24`
29. `candidate_v4_guardv66_by_v64`
    当前性质应写成：
    - 比 `candidate_v3_guardv20`
      更适合继续细化
      `v64 / v66`
      之间的分界 proxy
    - 与 `candidate_v1 / v2`
      完全不重叠，
      说明不是旧家族重命名
    - 但 row-level
      仍不够硬，
      还不是正式训练入口
    - `candidate_v3_guardv20`
      则保留为：
      - 诊断训练 aggregate
        是否被推正的旧 working candidate
30. 已进一步确认：
    - 直接显式要求
      `v64 > v66 > v65`
      并不会产生新的
      `candidate_v5`
    - top order-pass family
      仍然回到：
      - `candidate_v4_guardv66_by_v64`
    - strict samplewise
      仍为：
      - `0`
31. 当前更关键的新事实是：
    - `candidate_v4_guardv66_by_v64`
      与当前 `v42 / v66`
      active split
      几乎不重叠：
      - vs `v42` base train：
        - `1 / 33`
      - vs `v42` base val：
        - `0 / 10`
    - 因而若后续继续训练，
      默认不能只换 selector
32. 本轮已为后续训练准备好 union split：
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 161`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 47`
    - 这对 manifest
      才是后续若继续验证
      `candidate_v4`
      训练信号时的默认入口
33. 已继续把
    `candidate_v4_guardv66_by_v64`
    真正 union
    进 active split，
    并按 `v66`
    原 recipe
    启动：
    - `v67 = baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v67_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_candv4union_0002_ft1`
34. `v67`
    已把 coverage 问题排除：
    - `branch_protect`
      命中变成：
      - train `33 / 161`
      - val `10 / 47`
    - 说明这轮不是
      selector 没命中
35. 但 `v67`
    结果明确失败：
    - relative to `v32`
      的 `friend_speech_leak_followup_gate`：
      - `overall_judgement = fail`
      - clear fail：
        - `speech_leak_like_gain_floor`
        - `guodegang_absent_floor`
      - near-tie 但未过：
        - `speech_probe_overall_floor`
    - 且在
      `candidate_v4`
      那 `10` 条 val rows 上，
      aggregate 变成：
      - `v64 > v66 > v65 > v67`
    - 说明当前更该怀疑的是：
      - objective / proxy
        语义仍错，
      - 而不是 manifest coverage
36. `v67`
    之后已补 subgroup 级诊断，
    当前对 `candidate_v4_guardv66_by_v64`
    的正确解释应升级为：
    - 不是单语义 family
    - 而是混入了一簇
      低 target transient /
      高 interference transient share
      的危险子族
    - 新入口：
      - `scripts/eval/analyze_proxy_candidate_subgroups.py`
      - `reports/daily/2026-03-21_candidate_v4_subgroup_diagnosis.md`
    - 核心事实：
      - 对 `v66`
        而言，
        `candidate_v4`
        在：
        - higher-target-transient half
          上相对 `v64`
          仍是小正向
        - low-target-transient half
          上则已转负
      - 对 `v67`
        而言，
        当前最明显的系统性回退落在：
        - high interference transient share half
          relative to `v66`：
          - `-0.086806 dB`
          - improved count `0 / 5`
        - low target transient half
          relative to `v66`：
          - `-0.072390 dB`
      - 两条危险条件交集
        当前为 `4` 条 rows：
        - `val_000165`
        - `val_000223`
        - `val_000401`
        - `val_000469`
        - 在这 `4` 条上：
          - `v66 - v64 = -0.000723 dB`
          - `v67 - v66 = -0.094110 dB`
    - 当前默认下一步因此改为：
      - 先做
        `candidate_v4`
        semantic split / carve-out
      - 不直接继续沿
        现有整包 `candidate_v4`
        再放大 branch_protect
37. 本轮已进一步把
    `v67 negative`
    top family
    物化为：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 12`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 3`
    - `sample_ids_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 141`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 40`
    - 入口：
      - `reports/daily/2026-03-21_candidate_v5_guardv67_negative_materialization.md`
  - 这条 `candidate_v5_guardv67_negative`
    当前性质应固定为：
    - `v67`
      负向锚点 family
    - 不是
      `candidate_v4`
      的正式替代品
  - val `3` 条 rows 为：
    - `val_000076`
    - `val_000274`
    - `val_000469`
  - aggregate 上明确形成：
    - `v64 > v35 > v66 > v20 > v29 > v65 > ... > v67`
    - `v66 - v64 = -0.039333 dB`
    - `v66 - v65 = +0.026017 dB`
    - `v66 - v67 = +0.056485 dB`
  - 更关键的是：
    - 它并不等于
      `candidate_v4 carve`
      或 `candidate_v4 pruned`
    - 而是横跨了两边：
      - val vs `candidate_v4 carve`：
        - `1 / 3`
        - `val_000469`
      - val vs `candidate_v4 pruned`：
        - `2 / 3`
        - `val_000076`
        - `val_000274`
  - 因而当前默认下一步
    不再只是：
    - `candidate_v4`
      单边 carve-out
  - 而是：
    - 同时保留
      `candidate_v4`
      作为 `v64 / v66`
      分界 working family
    - 保留
      `candidate_v5_guardv67_negative`
      作为 `v67`
      负向锚点 family
    - 若后续继续，
      默认先做：
      - `candidate_v4`
        与 `candidate_v5`
        的交并分析
      - 尤其聚焦：
        - `candidate_v4 carve ∩ candidate_v5`
        - `candidate_v4 pruned ∩ candidate_v5`
      - 不直接启动新训练
38. 已继续把
    `candidate_v4 / candidate_v5`
    交并关系
    拆到 subset 级；
    当前默认解释必须升级为：
    - `candidate_v5`
      在 val 上
      不是独立新族，
      而是
      `candidate_v4`
      的真子集，
      且内部也不是单语义
    - 入口：
      - `scripts/eval/analyze_proxy_family_overlap.py`
      - `reports/daily/2026-03-21_candidate_v4_v5_overlap_analysis.md`
      - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
      - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
  - 当前 val 上已固定成四类：
    - `v4 carve only`：
      - `val_000165`
      - `val_000223`
      - `val_000401`
    - `v4 carve ∩ v5`：
      - `val_000469`
    - `v4 pruned only`：
      - `val_000034`
      - `val_000041`
      - `val_000202`
      - `val_000365`
    - `v4 pruned ∩ v5`：
      - `val_000076`
      - `val_000274`
  - 这四类当前应分别解释为：
    - `v4 carve only`
      = 纯 `v67` negative rows
      - `v66 - v64 = +0.007515 dB`
      - `v67 - v66 = -0.068223 dB`
    - `v4 carve ∩ v5`
      = 硬双信号 anchor
      - 当前只有：
        - `val_000469`
      - `v66 - v64 = -0.025435 dB`
      - `v67 - v66 = -0.171768 dB`
      - `v66 - v65 = +0.313288 dB`
    - `v4 pruned only`
      = 当前最像 keep rows
      - `v66 - v64 = +0.014094 dB`
      - `v67 - v66 = +0.007854 dB`
    - `v4 pruned ∩ v5`
      = `v64 > v66`
        boundary-negative tail，
        不是稳定
        `v67 negative` core
      - `v66 - v64 = -0.046281 dB`
      - `v67 - v66 = +0.001157 dB`
  - 因而当前默认下一步
    已进一步收窄为：
    - 保留
      `candidate_v4`
      大框架
    - 若后续继续做 proxy，
      默认优先考虑：
      - `v4 carve only`
        作为更纯的
        `v67` negative rows
      - `val_000469`
        作为单独的
        硬双信号 anchor
    - 不把整包
        `candidate_v5`
        或
        `v4 pruned ∩ v5`
        直接当成
        新核心 negative family
    - 仍不启动新训练
39. 已继续把
    当前最值得保留的两条 subset family
    物化成标准资产；
    当前默认入口已不再是
    整包 `candidate_v5`
    而是：
    - `v4carve_only_guardv67_negative`
    - `v4carve_v5_dualanchor`
  - 入口：
    - `scripts/data/build_proxy_manifest_setops.py`
    - `reports/daily/2026-03-21_proxy_subfamily_materialization.md`
  - 新物化资产：
    - `train_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 4`
    - `val_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 3`
    - `sample_ids_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 133`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 40`
    - `train_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 2`
    - `val_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 1`
    - `sample_ids_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 131`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 38`
  - focused direction summary：
    - pure negative：
      - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_only_guardv67_negative_direction_analysis/summary.json`
      - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_only_guardv67_negative_direction_analysis/summary.json`
      - 结论：
        - `v66 - v64 = +0.007515 dB`
        - `v67 - v66 = -0.068223 dB`
    - dual anchor：
      - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_v5_dualanchor_direction_analysis/summary.json`
      - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_v5_dualanchor_direction_analysis/summary.json`
      - 结论：
        - `v66 - v64 = -0.025435 dB`
        - `v67 - v66 = -0.171768 dB`
  - 因而当前分支图上的默认下一步
    应固定为：
    - 若继续停在 proxy 侧，
      优先围绕：
      - `v4carve_only_guardv67_negative`
      - `v4carve_v5_dualanchor`
      做后续 family 解释
    - 若未来真要开训练，
      默认不从
      全量 `candidate_v5`
      起步
    - 本轮仍不启动新训练
40. 已继续沿
    `v4carve_only`
    与
    `dualanchor`
    两条线做 family expand 搜索；
    当前结果应固定为：
    - pure-negative
      这边已出现一条新的
      working family
      `candidate_v6_v4carve_only_expand`
    - dualanchor
      这边在
      `min-count = 3`
      下没有新 family，
      top 结果直接回到
      `candidate_v5`
  - 入口：
    - `reports/daily/2026-03-21_candidate_v6_pure_negative_expand.md`
    - `reports/eval/synthetic_proxy_search_candidate_v6_v4carve_only_expand_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v6_dualanchor_expand_on_friend_speech_leak_search_v1/summary.json`
  - 新物化资产：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 13`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 3`
    - `sample_ids_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 135`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 38`
  - 这条 `candidate_v6`
    val rows 为：
    - `val_000165`
    - `val_000331`
    - `val_000430`
  - focused direction：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`
    - 结论：
      - `v66 - v64 = +0.013671 dB`
      - `v66 - v65 = +0.083866 dB`
      - `v66 - v67 = +0.038650 dB`
  - 与旧 pure-negative 的关系：
    - overlap with
      `v4carve_only_guardv67_negative`
      val：
      - `1 / 3`
      - `val_000165`
    - overlap with
      `v4carve_v5_dualanchor`
      val：
      - `0`
  - 当前应解释为：
    - `candidate_v6`
      是新的 pure-negative expand family；
    - `val_000430`
      是最强核心；
    - `val_000331`
      是 partial-support row；
    - `val_000165`
      是旧 family
      留下的 noisy carry-over
  - 另一边更关键的新事实是：
    - dualanchor expand 搜索
      top family
      仍精确回到：
      - `val_000076`
      - `val_000274`
      - `val_000469`
      即旧
      `candidate_v5`
    - 因而当前不再默认继续追
      `469` 的
      `3+ row`
      扩展 family
  - 当前默认下一步
    已进一步固定为：
    - 保留
      `candidate_v6_v4carve_only_expand`
      作为新的 pure-negative working family
    - 保留
      `val_000469`
      作为单独硬 anchor
    - 不启动新训练
41. 已补上真正的
    samplewise 全约束 strict 搜索能力，
    并确认当前不存在
    `3+ row`
    的 strict-all clean family；
    当前更准确的两层状态应固定为：
    - `candidate_v6`
      = aggregate pure-negative working family
    - `{val_000239, val_000430}`
      = strict-all core
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
    - `scripts/eval/search_synthetic_proxy_candidates.py`
    - `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min3_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min2_on_friend_speech_leak_search_v1/summary.json`
  - 本轮新增工程能力：
    - `--require-samplewise-all-constraints-pass`
    - `num_samplewise_extra_constraint_pass_rows_before_optional_filter`
    - `num_samplewise_all_constraints_pass_rows_before_optional_filter`
  - strict-all 搜索结果：
    - 在
      `v66 > v64`
      且额外满足：
      - `v66 > v65`
      - `v66 > v67`
      - `v64 > v67`
      - `v20 > v24`
      的口径下，
      真正逐条样本都过关的 shared rows
      只有：
      - `val_000239`
      - `val_000430`
    - `min-count = 3`
      直接掉空，
      说明当前没有
      `3+ row`
      strict-all family
  - 与旧 pure-negative 的关系：
    - `candidate_v6`
      val：
      - `val_000165`
      - `val_000331`
      - `val_000430`
    - strict-all core：
      - `val_000239`
      - `val_000430`
    - 因而当前不能再把
      `candidate_v6`
      误写成
      row-level strict core
  - 当前默认下一步
    应进一步收紧为：
    - 保留
      `candidate_v6`
      作为 aggregate working family
    - 保留
      `{val_000239, val_000430}`
      作为 strict-all 诊断核心
    - 继续保留
      `val_000469`
      作为单独硬 anchor
    - 在没有新的
      `3+ row`
      strict-all family
      之前，
      不启动新训练
42. 已把 strict-core 资产与 overlap 关系正式物化；
    当前更准确的三层结构应固定为：
    - `candidate_v6`
      = aggregate pure-negative working family
    - `strict_core`
      = row-level strict-all core
    - `dualanchor`
      = 单点边界锚点
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_{train,val,all}.txt`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
  - 当前正式 membership subset：
    - `candidate_v6 only`
      - `val_000165`
      - `val_000331`
    - `strict_core only`
      - `val_000239`
    - `candidate_v6 ∩ strict_core`
      - `val_000430`
    - `dualanchor only`
      - `val_000469`
  - 更关键的新事实：
    - `strict_core only`
      的
      `val_000239`
      行为上严格过关，
      但 metadata 语义
      并不落在
      `candidate_v6`
      的 low-transient 模板里；
    - 因而当前不能把
      strict core
      继续误写成：
      - `candidate_v6`
        的继续收紧版
  - 当前默认下一步
    应更新为：
    - 若继续做 proxy，
      默认改为：
      - 用 strict core
        `{val_000239, val_000430}`
        继续找新的行为同族
      - 同时保留
        `val_000469`
        作为边界 anchor
    - 不再默认只沿
      `candidate_v6`
      那套
      low-transient 语义
      继续缩阈值
    - 仍不启动新训练
43. 已继续把 strict-core 周围的 near-miss frontier 正式拆成按失败 guard 分组的两条前沿；
    当前更准确的扩张顺序应固定为：
    - 第一优先：
      `guardv65_only`
    - 第二优先：
      `guardv20_only`
    - 边界锚点：
      `val_000469`
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
    - `scripts/eval/analyze_proxy_strict_near_miss.py`
    - `data/synthetic/val_manifest_friend_speech_leak_search_v1_with_metrics.jsonl`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_nearmiss_analysis_with_metrics/summary.json`
  - 当前两条 single-fail 前沿资产：
    - `guardv65_only`
      - `val_000202`
      - `val_000376`
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65.jsonl`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65_{train,val,all}.txt`
    - `guardv20_only`
      - `val_000223`
      - `val_000316`
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20.jsonl`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20_{train,val,all}.txt`
  - 当前判断：
    - `guardv65_only`
      是 strict core
      的默认主扩张前沿，
      因为它只差：
      - `v66 > v65`
      且保住其余四条 guards；
    - 其中
      `val_000376`
      目前最接近 strict core，
      仅差：
      - `v66 - v65 = -0.004292 dB`
    - `guardv20_only`
      则应解释为：
      - 与旧
        `v20`
        guard
        不再对齐的第二分支，
      不与第一优先前沿混写
  - 当前默认下一步
    已进一步更新为：
    - 若继续做 strict-core 扩张，
      默认先围绕：
      - `guardv65_only`
      - 特别是
        `val_000376`
      继续找同向 rows
    - `guardv20_only`
      保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
44. 已继续确认 `guardv65_only` 内部也要再拆一层；当前更准确的结构不是 `{202,376}` 并列前沿，而是一个 `4` 条 relaxed shell 加上一条 `{376,430}` bridge pair：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
    - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min3_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min2_on_friend_speech_leak_search_v1/summary.json`
  - 当前 relaxed shell：
    - `val_000202`
    - `val_000239`
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell_{train,val,all}.txt`
  - 当前第一条稳定 bridge pair：
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_{train,val,all}.txt`
  - 当前判断：
    - 放松
      `v66 > v65`
      后，
      `3+ row`
      搜索只会回到整包 relaxed shell，
      还 carve 不出更细 family；
    - 但 `2` 条口径下，
      第一条被 metadata
      稳定挑出来的 bridge
      不是：
      - `{202,239}`
      也不是
      - `{202,376}`
      而是：
      - `{376,430}`
    - 因此
      `val_000376`
      当前更像 strict core 里
      `430` 这一侧的外扩桥；
      `val_000202`
      则继续保留，
      但不再默认和
      `376`
      并写成同一条语义前沿
  - 当前默认下一步
    已再次更新为：
    - 若继续做 strict-core 扩张，
      默认先围绕：
      - `{val_000376, val_000430}`
      继续找同向 rows
    - `{202,239,376,430}`
      保留为 relaxed shell，
      作为 guardv65 放松后的诊断壳层
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
45. 已继续围绕 `{376,430}` 做 seed-anchored 扩张，并确认 `331` 是当前最近第三条 row；但它只能算 aggregate-only bridge extension，不能当成 row-level clean 第三成员：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
    - `scripts/eval/analyze_proxy_seed_expansion.py`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_bridgepair_aggregate_expand_min3_on_friend_speech_leak_search_v1/summary.json`
  - 当前 row-level bridge：
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`
  - 当前 aggregate-only bridge trio：
    - `val_000331`
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331_{train,val,all}.txt`
  - 当前判断：
    - `val_000331`
      是 bridge pair
      最近的第三条 row，
      但它 row-level
      仍 fail：
      - `v66 > v65`
      - `v66 > v67`
      - `v64 > v67`
    - 只有并进 seed pair 后，
      `{331,376,430}`
      aggregate 才恢复为 full-pass；
    - 因而这条 trio
      当前只能解释为：
      - aggregate-only bridge extension
      不能写成：
      - row-level clean family
    - 同时 generic aggregate search
      仍会自动塌回旧：
      - `candidate_v6`
      语义；
      所以 bridge 语义
      必须靠 seed-anchored 诊断单独保住
  - 当前默认下一步
    已再次更新为：
    - row-level 扩张
      默认继续围绕：
      - `{val_000376, val_000430}`
    - `{val_000331, val_000376, val_000430}`
      保留为 aggregate-only bridge trio，
      不混写成 strict clean family
    - generic aggregate search
      若再次塌回旧 family，
      默认不覆盖
      上述 bridge 解释
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练

## 6. 忘线检查表

每次恢复上下文前，先看这 5 个入口：

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. 本文档 `docs/05_task_branch_map.md`
5. 当前活跃分支日报：
   - 现在补到：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
     - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
     - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
     - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
     - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
     - `reports/daily/2026-03-21_candidate_v6_pure_negative_expand.md`
     - `reports/daily/2026-03-21_proxy_subfamily_materialization.md`
     - `reports/daily/2026-03-21_candidate_v4_v5_overlap_analysis.md`
     - `reports/daily/2026-03-21_candidate_v5_guardv67_negative_materialization.md`
     - `reports/daily/2026-03-21_candidate_v4_subgroup_diagnosis.md`
   - 当前主停点日报已更新为：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
   - 上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
   - 更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_v67_candidate_v4_union_followup.md`
   - 上一条 `candidate_v4` 搜索日报：
     - `reports/daily/2026-03-21_candidate_v4_guardv66_by_v64_search_followup.md`
   - 上一条 `v66` 定向诊断日报：
     - `reports/daily/2026-03-20_v66_candidate_v3_direction_diagnosis.md`
   - `candidate_v3` 搜索日报：
     - `reports/daily/2026-03-20_friend_speech_leak_search_manifest_v1.md`
   - 上一条 `branch_protect` 资产日报：
     - `reports/daily/2026-03-20_branch_protect_selector_asset_builder.md`
   - `v64 / v65` 恢复日报：
     - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`
   - `v63` 主日报：
     - `reports/daily/2026-03-20_v63_dualdecoder_targetfull_basealign_branchprotect_followup.md`
   - `v63` 旧启动清单：
     - `reports/daily/2026-03-20_v63_written_spec_no_run.md`

每次准备开新分支前，至少回答：

1. 这条分支是新 coverage，还是旧 rows 重路由？
2. 会不会再次误命中 `interference_extra` exact family？
3. 计划跑完后用哪份 gate 判 keep / drop？
