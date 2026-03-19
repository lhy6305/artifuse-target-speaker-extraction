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
   `proxy_v7` 的真正 branch-local output decoupling；
6. 当前更偏向：
   - absent-only residual adapter
   - 或独立 output branch / dual-head；
   而不是继续做：
   - selector 细修
   - 或 prefix freeze 的小组合；
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
   - 现在是 `reports/daily/2026-03-20_v47_v48_prefix_freeze_decoupling_followup.md`

每次准备开新分支前，至少回答：

1. 这条分支是新 coverage，还是旧 rows 重路由？
2. 会不会再次误命中 `interference_extra` exact family？
3. 计划跑完后用哪份 gate 判 keep / drop？
