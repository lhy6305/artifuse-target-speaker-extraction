# 2026-03-19 `v31` residual-projection follow-up

## 背景

`v29 / v30` 已确认：

- `focus_sample_ids` plumbing 已经接通；
- `0004-like speech-leak` 的 exact family 也已经收紧；
- 但当前 `interference_extra` 仍在：
  - exact proxy 上持续负增益；
  - near-real `speech_leak_like` 上持续负增益。

因此本轮不再改 proxy family，也不再扫权重，而是只改一件事：

- 保持 `v30` 的 exact family 与 `v19` 基座不变；
- 把 interference loss 从：
  - `prediction_projection_ratio`
  切到：
  - `residual_projection_ratio`

目标是把 speech-leak 侧的干扰约束从“看整个预测里沿 interference 的投影占比”，
改成更接近“只看残差里还剩多少沿 interference 的泄漏分量”。

## 工程改动

- `src/tse_prefix/pipeline/baseline_train.py`
  - `interference_projection_loss(...)` 新增 `mode`
  - 支持：
    - `prediction_projection_ratio`
    - `residual_projection_ratio`
- `scripts/train/train_stft_mask_baseline.py`
  - 新增：
    - `--loss-interference-mode`
- `scripts/eval/eval_stft_mask_baseline.py`
  - sample-level interference metric 改为按 checkpoint 自带的 `interference_loss_mode` 复算

默认仍保持旧模式，因此历史 checkpoint 行为不变。

## `v31 = legacy_transient_leakguard_probe_v31_v19_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_residualproj_ft1`

### 训练配置

- init checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1/best.pt`
- train / val manifests：
  - 继续使用 `v30` 的 plus manifests
- budget：
  - `epochs = 1`
  - `batch_size = 4`
  - `lr = 1e-5`
- 唯一关键改动：
  - `interference_loss_mode = residual_projection_ratio`

### selector 命中

- train：
  - transient / interference / absent = `51 / 58 / 27` out of `97`
- val：
  - transient / interference / absent = `18 / 21 / 5` out of `29`

说明：

- 这轮和 `v30` 的 selector 覆盖完全一致；
- 可以把结果变化主要归因到 interference objective 形式，而不是 proxy family 或命中边界变化。

## 结果

### 相对 `v19`

- default：
  - `-0.011286 dB`
- `v30 exact proxy`：
  - `-0.082113 dB`
- near-real speech probe overall：
  - `-0.054149 dB`
- near-real `friend_raw`：
  - `-0.040774 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.041094 dB`
- near-real `residual_transient_like (0003)`：
  - `-0.040455 dB`
- near-real `transient_like (0006)`：
  - `-0.094272 dB`

### exact proxy 细节

`v30` exact val 3 条中：

- `val_000075 (target_full)`：
  - `-0.287630 dB`
- `val_000096 (target_absent_tail)`：
  - `-0.015277 dB`
- `val_000297 (target_absent_head)`：
  - `+0.056568 dB`

解释：

- full 行仍明显为负；
- 但两个 nonfull 行里已有一条转正，一条接近 near-tie；
- 这说明新 objective 的确在 exact family 内部收回了一部分回退。

### 相对 `v30`

- `v30 exact proxy`：
  - `+0.059839 dB`
- near-real speech probe overall：
  - `-0.000753 dB`
- near-real `friend_raw`：
  - `+0.006956 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.005182 dB`
- near-real `residual_transient_like (0003)`：
  - `+0.019095 dB`
- near-real `transient_like (0006)`：
  - `-0.023880 dB`

解释：

- `v31` 确实把 `v30` 的 exact family 三条都往正方向推了一点；
- 但 near-real 总体基本只是持平略负；
- `friend_raw` 略有收回，同时把 `guodegang / 0006` 再吐掉了一点。

## 结论

- `v31` 不保留为新候选；
- 这次可以确认：
  - 单纯把 interference objective 从整段预测投影比改成残差投影比，
  - 的确能部分缩小 exact speech-leak proxy 的回退；
  - 但还不足以把 `v19` 之上的 default / near-real 一起拉正。

更可信的解释应更新为：

- `0004-like speech-leak` 的问题不只是 projection target 选错；
- 仅做一次 scalar objective mode 替换，还不够形成稳定收益；
- 还需要更明确的：
  - leak-specific guardrail
  - 或 friend-side / guodegang-side 的分侧保护
  - 或 residual-only objective 与 default guardrail 的联动约束

## 当前建议

下一步若继续自动推进，优先级应更新为：

1. 不继续围绕 `v31` 扫权重、epoch、lr；
2. 认可 `residual_projection_ratio` 作为一个可复用的 objective primitive；
3. 后续若继续补 `0004-like speech-leak`，优先试：
   - 更显式的 leak-specific guardrail
   - friend-side 提升与 `guodegang / 0006` 保护解耦
   - 或只在 speech-leak exact family 上叠加更局部的 residual constraint，而不是整条 interference branch 统一替换
