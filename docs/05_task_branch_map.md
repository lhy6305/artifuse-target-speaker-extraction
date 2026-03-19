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
  - `pending`
- 当前判断：
  - `B1 / B2` 当前这两条收紧版都已失败；
  - 下一条如果继续 absent-side follow-up，
    不能只是：
    - 继续做 overlap carve-out
    - 或继续沿当前 `proxy_v6 currentsignal cleanonly`
- 当前缺口：
  - 仍缺一个对 real `guodegang_absent`
    更贴近、且不会同步拖坏
    `guodegang_anchor`
    的保护口径

## 5. 下一条默认执行分支

如果下一轮没有新用户决策，默认继续：

- `B3 / 重新定义 absent-side protection proxy 或 direct real-floor guardrail`

即：

1. 先明确这条新线到底是：
   - 新 coverage
   - 还是旧 rows 重路由；
2. 默认不再直接沿当前
   `proxy_v6 currentsignal cleanonly`
   做小修小补；
3. 仍按同一套裁决口径重新走：
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
   - 现在是 `reports/daily/2026-03-19_v40_v41_absent_followup_results.md`

每次准备开新分支前，至少回答：

1. 这条分支是新 coverage，还是旧 rows 重路由？
2. 会不会再次误命中 `interference_extra` exact family？
3. 计划跑完后用哪份 gate 判 keep / drop？
