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

## 5. 下一条默认执行分支

如果下一轮没有新用户决策，默认继续：

- `B3 / 保留 proxy_v7，重写 absent-side routing 与 friend-side 解耦`

即：

1. 先明确这条新线到底是：
   - 已不再是重搜 proxy；
   - 而是围绕 `proxy_v7`
     的 objective / guardrail 解耦；
2. 默认不再回到
   `proxy_v6 currentsignal cleanonly`
   或继续重做 overlap carve-out；
3. 默认也不继续扫
   `proxy_v7` 的微幅 waveform weight rescale；
4. 单纯 `stft_only`
   也不作为默认延伸方向；
5. 默认优先继续沿
   `proxy_v7` 的更强 branch-local output decoupling；
6. 当前更偏向：
   - 真正独立的 dual-head / branch-local decoder；
   而不是继续做：
   - selector 细修
   - prefix freeze 的小组合
   - simple residual adapter 的小参数
   - adapter branch 的 conditioning / temporal 变体；
   - 并且这一步的工程底座已完成，
     可以直接从：
     - `v32`
       warm-start
   - branch decoder bootstrap from base
   - 但当前又新增一条边界：
     - 默认不再继续扫
       `interference_extra residual_projection_ratio`
       在 dual-head 上的权重或同类小变体；
     - 默认也不再继续扫
       `interference_extra_base_align_weight`
       的近邻小变体；
     - 下一条更合理的默认方向应改成：
       - 更贴近 `keep target_full`
         与尤其直接面向
         `speech_leak_like (0004)`
         的 branch-local protect objective；
       - 而不是继续复用当前这条
         residual extra
         或 exact-family `base-align`
     - 当前工程上已补好一条可直接试验的候选 primitive：
       - `interference_extra_base_delta_projection_weight`
       - 它只约束：
         - branch output
           相对 frozen base 的 interference-like 改动
       - 不再像 `base-align` 那样
         直接约束整段 branch 输出贴回 base
     - 并已完成 1-step smoke：
       - `tmp/smoke_branch_decoder_base_delta_projection`
       - 已确认：
         - `v32` 旧 checkpoint 兼容
         - `interference_extra` selector
           train `1 / 4`
           val `3 / 37`
         - 新指标已写入 `train_summary.json`
7. 仍按同一套裁决口径重新走：
   - 训练
   - default / exact / near-real / guodegang eval
   - `friend_speech_leak_followup_gate`

## 6. 忘线检查表

每次恢复上下文前，先看这 5 个入口：

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. 本文档 `docs/05_task_branch_map.md`
5. 当前活跃分支日报：
   - 现在是 `reports/daily/2026-03-20_dualdecoder_base_delta_projection_smoke.md`

每次准备开新分支前，至少回答：

1. 这条分支是新 coverage，还是旧 rows 重路由？
2. 会不会再次误命中 `interference_extra` exact family？
3. 计划跑完后用哪份 gate 判 keep / drop？
