# 2026-03-19 `v34 / v35` guardrail follow-up

## 背景

`v32 / v33` 已确认：

- 把 `residual_projection_ratio` 局部化到 `interference_extra`，
  的确比 `v31` 的全局替换更稳；
- 但 `0004-like speech-leak` 仍没有相对 `v19` 转正；
- 继续放大 `interference_extra_weight` 也几乎没有新变化。

因此本轮继续沿“更明确的 guardrail / 解耦保护”推进，
但不再扫同一类 extra weight。

## 工程补充

- `src/tse_prefix/pipeline/baseline_train.py`
  - `LossBreakdown` 新增：
    - `interference_extra_guard_sisdr_loss`
  - `compute_losses(...)` 新增：
    - `interference_extra_guard_sisdr_weight`
  - 新增：
    - `masked_sisdr_per_sample(...)`
    - `weighted_sisdr_loss(...)`
- `scripts/train/train_stft_mask_baseline.py`
  - 新增：
    - `--loss-interference-extra-guard-sisdr-weight`
  - train summary / log 新增：
    - `interference_extra_guard_sisdr_loss`
- `scripts/eval/eval_stft_mask_baseline.py`
  - eval summary 新增：
    - `interference_extra_guard_sisdr_loss`

这条能力的目的很明确：

- 在 `interference_extra` exact speech-leak family 上，
  除了压泄漏残差，
  再额外给一条很轻的 target-preservation guardrail。

## `v34 = legacy_transient_leakguard_probe_v34_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_sisdrguard0002_ft1`

### 训练配置

在 `v32` 基础上只新增：

- `interference_extra_guard_sisdr_weight = 0.0002`

其余保持：

- base interference：
  - `prediction_projection_ratio`
- interference_extra：
  - `residual_projection_ratio`
- exact family：
  - 继续使用 `v30` 的 10 条 ids

### 结果

相对 `v19`：

- default：
  - `+0.058461 dB`
- `v30 exact proxy`：
  - `+0.026174 dB`
- near-real speech probe overall：
  - `-0.071357 dB`
- near-real `friend_raw`：
  - `-0.054449 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.045359 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.063539 dB`
- near-real `transient_like (0006)`：
  - `-0.122081 dB`

exact val 3 条：

- `val_000075 (target_full)`：
  - `-0.200607 dB`
- `val_000096 (target_absent_tail)`：
  - `-0.034282 dB`
- `val_000297 (target_absent_head)`：
  - `+0.313410 dB`

相对 `v32`：

- exact proxy：
  - `+0.147378 dB`
- near-real speech probe overall：
  - `-0.020892 dB`

解释：

- `v34` 是当前第一条把 `v30` exact proxy 推到整体正增益的版本；
- 但它同时把 near-real，尤其 `guodegang / 0006`，拉得更差；
- 因而它更像：
  - exact-family overfit
  而不是：
  - 可保留的真实改进。

## `v35 = legacy_transient_leakguard_probe_v35_v19_friend_guard_sisdrplus_guodegang_anchor_guard_ft1`

### 训练配置

`v34` 暴露出：

- friend exact family 被推正；
- 但 `guodegang_anchor_120s` 明显变差。

本轮因此补一条显式 decoupling guard：

1. 由 `train/val_manifest_guodegang_anchor_proxy_v1.jsonl`
   生成：
   - `sample_ids_guodegang_anchor_proxy_v1_train.txt = 84`
   - `sample_ids_guodegang_anchor_proxy_v1_val.txt = 22`
   - `sample_ids_guodegang_anchor_proxy_v1_all.txt = 106`
2. 生成 union manifests：
   - `train_manifest_v35_v19_plus_friend_reverse_guardrail_proxy_v8_plus_guodegang_anchor_proxy_v1.jsonl = 176`
   - `val_manifest_v35_v19_plus_friend_reverse_guardrail_proxy_v8_plus_guodegang_anchor_proxy_v1.jsonl = 47`
3. 在 `v34` 的基础上新增：
   - `transient_extra_focus_sample_ids = guodegang_anchor_proxy_v1`

目标是：

- 保留 friend-side exact guard；
- 同时用 `guodegang_anchor_proxy_v1` 给 `0006` anchor 侧加一条显式保护。

### 结果

相对 `v19`：

- default：
  - `+0.061993 dB`
- `v30 exact proxy`：
  - `+0.152425 dB`
- near-real speech probe overall：
  - `-0.078793 dB`
- near-real `friend_raw`：
  - `-0.024845 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.022684 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.027006 dB`
- near-real `transient_like (0006)`：
  - `-0.240638 dB`

独立 `near_real_guodegang_anchor_probe_v1`：

- 相对 `v19`：
  - `-0.352486 dB`
- 相对 `v34`：
  - `-0.168818 dB`

解释：

- `v35` 并没有把真正的 `guodegang_anchor_120s` 保护住；
- 反而：
  - friend-side 的 broad near-real 回退缩小了；
  - 但 `guodegang_anchor_120s` 真实锚点进一步明显变差。

这说明：

- `guodegang_anchor_proxy_v1` 作为 synthetic decoupling guard，
  当前并不能可靠保护真实 `guodegang_anchor_120s`；
- 把它并进来，反而会进一步把模型推向：
  - synthetic anchor 更强
  - real anchor 更差
  的旧陷阱。

## 结论

- `v34` 不保留：
  - 它能把 exact speech-leak proxy 推正，
  - 但 near-real 明显过拟合，尤其伤到 `guodegang / 0006`
- `v35` 也不保留：
  - `guodegang_anchor_proxy_v1` 当前不适合作为这条线的 decoupling protection
  - 至少在本轮组合里，它对真实 `guodegang_anchor_120s` 是反向信号

这轮更可信的结论应升级为：

1. `interference_extra` 上加 target-preservation guardrail，
   的确能把 exact speech-leak proxy 推正；
2. 但 exact-family 正增益不等于 near-real 正增益；
3. `guodegang_anchor_proxy_v1` 也不能直接当作 friend-side speech-leak 线的保护项并进来；
4. 下一步若继续自动推进，更优先的不是：
   - 继续扫 `sisdr_guard` 权重
   - 或继续并更多 synthetic `guodegang` proxy
5. 而应优先考虑：
   - 只在 real / near-real guardrail 上先做 gate
   - 或重新设计更贴近 `guodegang_anchor_120s` 的保护代理

## Friend-Side Follow-Up Gate

为避免后续再次把：

- exact speech-leak proxy 转正
- 或 `0004-like speech_leak` 局部回升

误写成“这条线已经可以保留”，本轮又把 `v34 / v35` 过了一次专门的 friend-side follow-up gate：

- 脚本：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- gate 输出：
  - `reports/eval/compare_v19_vs_v34_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`
  - `reports/eval/compare_v19_vs_v35_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v34.json`
  - `reports/eval/compare_v19_vs_v35_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`

### `v34` relative to `v32`

- `overall_pass = false`
- failed rules：
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

解释：

- 即便 `v34` 已把 exact target_full 从 `-0.303318 dB` 拉到 `-0.200607 dB`；
- 也即便 default 仍更高；
- 它仍没有通过：
  - near-real `0004-like speech_leak`
  - 以及 `guodegang anchor / absent`
  这三条 real floor。

### `v35` relative to `v34`

- `overall_pass = false`
- failed rules：
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

同时可见：

- default：
  - `+0.003533 dB`
- exact target_full：
  - `+0.102182 dB`
- near-real `speech_leak_like (0004)`：
  - `+0.022676 dB`

但：

- `guodegang_anchor_floor = -0.168818 dB`
- `guodegang_absent_floor = -0.068296 dB`

这说明：

- `v35` 的确把 friend-side speech-leak 这边拉回来了一些；
- 但它仍然没有保住真正决定能否留存的 `guodegang` real floors。

### `v35` relative to `v32`

- `overall_pass = false`
- failed rules 仍然只有：
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

更具体地说：

- 相对 `v32`：
  - exact target_full `+0.204893 dB`
  - near-real `speech_leak_like (0004) = +0.018996 dB`
- 但：
  - `guodegang_anchor_floor = -0.286603 dB`
  - `guodegang_absent_floor = -0.115565 dB`

## 对结论的额外收紧

这一轮 gate 把结论又压实了一层：

1. `v34` 的问题不只是“overall near-real 负”，而是它已经在 friend-side follow-up gate 上明确失败；
2. `v35` 的问题也不再只是“某个真实 anchor 变差”，而是：
   - 即便 default / exact / `0004-like speech_leak` 都改善，
   - 它仍会因为 `guodegang anchor / absent` 两条 real floor 失败而被淘汰；
3. 因此后续这条线的 keep/drop 口径应固定为：
   - 先过 real / near-real gate；
   - 再讨论 speech-leak side gain；
   - 不能反过来。
