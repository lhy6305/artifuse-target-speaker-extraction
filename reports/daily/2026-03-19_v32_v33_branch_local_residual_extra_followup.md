# 2026-03-19 `v32 / v33` branch-local residual-extra follow-up

## 背景

`v31` 已确认：

- 把整条 interference objective 全部切到 `residual_projection_ratio`，
  的确能把 `v30` exact proxy 收回来一点；
- 但 default 会转负，near-real 也没有被一起拉正。

因此本轮不再继续改 proxy family，
也不再做全局 interference mode 替换，
而是先补 branch-local objective 能力：

- base interference 保持 `v19` 的旧 `prediction_projection_ratio`
- 只有 `interference_extra` 的 exact speech-leak family
  才使用 `residual_projection_ratio`

目标是验证：

1. `v31` 的问题是不是主要来自“全局替换过宽”；
2. 如果只在 extra family 上局部化 residual objective，
   是否能同时保住 default 稳定性和 friend-side exact/near-real 收益。

## 工程补充

- `src/tse_prefix/pipeline/loss_selectors.py`
  - 新增：
    - `build_branch_selector_sample_weights(...)`
    - `merge_selector_sample_weights(...)`
- `src/tse_prefix/pipeline/baseline_train.py`
  - `LossBreakdown` 新增：
    - `interference_extra_projection_ratio`
  - `compute_losses(...)` 新增：
    - `interference_extra_sample_weights`
    - `interference_extra_weight`
    - `interference_extra_loss_mode`
- `scripts/train/train_stft_mask_baseline.py`
  - 新增：
    - `--loss-interference-extra-weight`
    - `--loss-interference-extra-mode`
  - 训练 summary / log 新增：
    - `interference_extra_projection_ratio`
    - `interference_extra` selector metrics
- `scripts/eval/eval_stft_mask_baseline.py`
  - eval summary / sample meta / pattern-recipe-bucket 聚合
    新增：
    - `interference_extra_projection_ratio`

这次的关键不是“又换一条 proxy”，
而是训练图终于可以把：

- base interference
- interference_extra

分开赋予不同 objective。

## `v32 = legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1`

### 训练配置

- init checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1/best.pt`
- train / val manifests：
  - 继续使用 `v30` plus manifests
- budget：
  - `epochs = 1`
  - `batch_size = 4`
  - `lr = 1e-5`
- branch-local interference 挂法：
  - base interference：
    - `weight = 0.0075`
    - `mode = prediction_projection_ratio`
  - interference_extra：
    - `weight = 0.0075`
    - `mode = residual_projection_ratio`
    - `focus_sample_ids = v30 exact 10 ids`

### selector 命中

- train：
  - transient / interference / interference_extra / absent
  - `51 / 58 / 7 / 27` out of `97`
- val：
  - transient / interference / interference_extra / absent
  - `18 / 21 / 3 / 5` out of `29`

解释：

- `interference_extra` 终于不再只是 union 里的一部分，
  而是被单独统计出来；
- 这轮可以明确确认：
  - branch-local extra objective 的 plumbing 已经接通。

### 结果

相对 `v19`：

- default：
  - `+0.019034 dB`
- `v30 exact proxy`：
  - `-0.121204 dB`
- near-real speech probe overall：
  - `-0.050465 dB`
- near-real `friend_raw`：
  - `-0.054102 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.041680 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.066523 dB`
- near-real `transient_like (0006)`：
  - `-0.039554 dB`

exact val 3 条：

- `val_000075 (target_full)`：
  - `-0.303318 dB`
- `val_000096 (target_absent_tail)`：
  - `-0.076612 dB`
- `val_000297 (target_absent_head)`：
  - `+0.016317 dB`

相对 `v31`：

- default：
  - `+0.030320 dB`
- exact proxy：
  - `-0.039091 dB`
- near-real overall：
  - `+0.003684 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.000586 dB`
- near-real `transient_like (0006)`：
  - `+0.054717 dB`

解释：

- `v32` 相对 `v31` 明确更稳：
  - default 被拉回正增益；
  - near-real overall 也略优；
  - `0006 / guodegang` 的额外回吐被收回。
- 但它仍没有把：
  - exact speech-leak proxy
  - near-real `0004`
  一起推到 `v19` 之上。

## `v33 = legacy_transient_leakguard_probe_v33_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_w015_ft1`

### 训练配置

`v33` 只做一个最小 follow-up：

- 保持 `v32` 全部配置不变；
- 只把：
  - `interference_extra_weight = 0.0075 -> 0.015`

目标是判断：

- `v32` 没有转正，到底是因为 branch-local extra 方向还不够强，
  还是因为瓶颈根本不在这一级 weight。

### 结果

相对 `v19`：

- default：
  - `+0.020266 dB`
- `v30 exact proxy`：
  - `-0.127022 dB`
- near-real speech probe overall：
  - `-0.050239 dB`
- near-real `friend_raw`：
  - `-0.054374 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.041911 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.066837 dB`
- near-real `transient_like (0006)`：
  - `-0.037836 dB`

exact val 3 条：

- `val_000075 (target_full)`：
  - `-0.310080 dB`
- `val_000096 (target_absent_tail)`：
  - `-0.077396 dB`
- `val_000297 (target_absent_head)`：
  - `+0.006409 dB`

解释：

- `v33` 与 `v32` 几乎重合；
- default 没坏，但 exact family 没继续改善；
- `0004-like speech-leak` 仍未转正。

这说明：

- 当前瓶颈不是：
  - branch-local extra weight 太小；
- 至少在这一级局部权重放大下，
  结果几乎没有新的结构性变化。

## 结论

- `v32`、`v33` 都不保留为新候选；
- 但这轮有两个重要有效结论：

1. `v31` 的问题确实部分来自“全局 residual 替换过宽”；
   - `v32` 已证明：
     - 只在 `interference_extra` 上局部化 residual objective，
     - 可以明显收回 default / near-real 的稳定性。
2. 但当前阻塞点也进一步明确：
   - 即使 branch-local extra objective 已接通，
   - 也即使额外把 `interference_extra_weight` 翻倍，
   - `0004-like speech-leak` exact family 仍没有被推正。

因此当前更可信的解释应升级为：

- 问题不只是：
  - interference branch 过宽
  - 或 extra weight 太小
- 更像是：
  - 还缺一条真正 leak-specific 的 guardrail
  - 或缺 friend-side / `guodegang` side 的更明确解耦保护

## 当前建议

下一步若继续自动推进，优先级应更新为：

1. 不继续围绕 `v32 / v33` 扫更多 extra weight；
2. 保留 branch-local interference-extra split 这套工程能力；
3. 后续若继续补 `0004-like speech-leak`，优先试：
   - 只在 speech-leak exact family 上触发的 leak-specific guardrail
   - friend-side 提升与 `guodegang / 0006` 保护的显式解耦
   - 或比当前 residual projection 更贴近“目标保留不动、只压泄漏残差”的局部约束
