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
