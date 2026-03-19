# 2026-03-19 `reconstruction_extra` branch plumbing 与 `v37` absent follow-up

## 背景

`v36` 已确认：

- 只把 `guodegang_anchor_proxy_v1` 拆到 `transient_extra`
  不是可保留方向；
- `guodegang_absent_proxy_v3_strict`
  虽已并进 union manifest，
  但由于样本本质仍是 `target_full`，
  并没有触发真正匹配的独立 objective。

因此这一轮不再继续扫：

- `guodegang_anchor_proxy_v1` 的 `transient_extra_weight`
- 或旧 `interference_extra_guard_sisdr`

而是补一条更贴近 `guodegang_absent_proxy_v3_strict`
语义的 branch-local objective：

- 针对指定 sample-id 子集，
  单独施加 target reconstruction 约束，
  不再误借 `target_absent_intervals` 去表达
  一组本来就是 `target_full` 的 hard-speech 行。

## 工程补充

- `src/tse_prefix/pipeline/baseline_train.py`
  - 新增：
    - `weighted_waveform_l1_loss(...)`
    - `weighted_stft_l1_loss(...)`
  - `LossBreakdown` 新增：
    - `reconstruction_waveform_l1`
    - `reconstruction_stft_l1`
    - `reconstruction_extra_waveform_l1`
    - `reconstruction_extra_stft_l1`
  - `compute_losses(...)` 新增：
    - `reconstruction_sample_weights`
    - `reconstruction_extra_sample_weights`
    - `reconstruction_waveform_weight`
    - `reconstruction_stft_weight`
    - `reconstruction_extra_waveform_weight`
    - `reconstruction_extra_stft_weight`
- `src/tse_prefix/pipeline/__init__.py`
  - 导出：
    - `weighted_waveform_l1_loss`
    - `weighted_stft_l1_loss`
- `src/tse_prefix/pipeline/loss_selectors.py`
  - selector config 前缀增加：
    - `reconstruction`
- `scripts/train/train_stft_mask_baseline.py`
  - 新增 CLI：
    - `--loss-reconstruction-waveform-weight`
    - `--loss-reconstruction-stft-weight`
    - `--loss-reconstruction-extra-waveform-weight`
    - `--loss-reconstruction-extra-stft-weight`
  - train / val summary 新增：
    - `reconstruction_waveform_l1`
    - `reconstruction_stft_l1`
    - `reconstruction_extra_waveform_l1`
    - `reconstruction_extra_stft_l1`
  - selector metrics 新增：
    - `reconstruction`
    - `reconstruction_extra`
- `scripts/eval/eval_stft_mask_baseline.py`
  - eval summary / sample meta / bucket 聚合新增上述 4 个 reconstruction 指标

## smoke 验证

- train smoke：
  - `tmp/smoke_reconstruction_extra/train_summary.json`
- eval smoke：
  - `tmp/smoke_reconstruction_extra_eval/eval_summary.json`

已确认：

- `reconstruction_extra_waveform_l1`
- `reconstruction_extra_stft_l1`
- `reconstruction / reconstruction_extra` selector metrics

都会在 train / eval 两侧正常落盘。

## 一个关键工程事实

本轮额外核对了：

- `train_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
- `train_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
- `val_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
- `val_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`

结果是：

- train：
  - `97 vs 97`
  - `same_order = true`
  - `same_set = true`
- val：
  - `29 vs 29`
  - `same_order = true`
  - `same_set = true`

解释：

- `v37` 并没有真的引入新样本；
- `guodegang_absent_proxy_v3_strict`
  这组行其实早已完整包含在 `v32` 的 base manifest 中；
- `v37` 的变化完全来自：
  - objective routing
  - 而不是 manifest coverage

这条结论很重要，因为它把当前 absent-side 缺口明确收敛为：

- 不是“样本没并进去”
- 而是“这批已存在的 hard `target_full` 行，
  之前没有被一个语义匹配的 branch-local objective 单独约束”

## `v37 = legacy_transient_leakguard_probe_v37_v32_absent_reconstructionextra_smoke_ft1`

### 训练配置

- init checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt`
- manifest：
  - `data/synthetic/train_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
  - `data/synthetic/val_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
  - 但这两份 manifest 与 `v32` base manifest 完全同序等价
- budget：
  - `epochs = 1`
  - `batch_size = 4`
  - `lr = 1e-5`
- 在 `v32` 基础上新增：
  - `reconstruction_extra_waveform_weight = 0.02`
  - `reconstruction_extra_stft_weight = 0.01`
  - `reconstruction_extra_focus_sample_ids = sample_ids_guodegang_absent_proxy_v3_strict_all`
- 保留：
  - base transient / interference / absent
  - `interference_extra = exact speech-leak 10 ids`
- 不启用：
  - `transient_extra`
  - `absent_extra`

### selector 命中

- train：
  - `reconstruction = 51 / 97`
  - `reconstruction_extra = 51 / 97`
- val：
  - `reconstruction = 18 / 29`
  - `reconstruction_extra = 18 / 29`

解释：

- 这批 absent proxy 行在当前 manifest 中占比很高；
- 且它们与 base transient 的 hard `target_full` 子集高度重合，
  所以 `v37` 的本质并不是“补一个真正独立的新样本族”，
  而是：
  - 在同一批 hard-speech `target_full` 行上
  - 再额外叠一层 target reconstruction 拉力

### 结果

相对 `v19`：

- default：
  - `+0.004330 dB`
- exact proxy overall：
  - `-0.214515 dB`
- exact `target_full`：
  - `-0.553167 dB`
- near-real speech probe overall：
  - `-0.093653 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.077866 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.122504 dB`
- near-real `guodegang_absent_480s`：
  - `-0.051134 dB`

相对 `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_pass = false`
- failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

### 与 `v36` 的对照解释

`v37` 虽然仍 `FAIL`，
但相对 `v36` 至少说明一件事：

- `absent reconstruction extra`
  的确比 `anchor transient-extra only`
  更接近当前 real floor 的方向

因为：

- `guodegang_anchor_120s`
  从 `-0.300635 dB` 回到 `-0.122504 dB`
- `guodegang_absent_480s`
  从 `-0.094534 dB` 回到 `-0.051134 dB`

但它同时又把：

- exact `target_full`
- near-real `speech_leak_like (0004)`

进一步拉坏。

因此更准确的解释应写成：

- `reconstruction_extra` 这条 absent-side 新 objective
  是有效工程能力；
- 它对 `guodegang` real floor 的方向
  比 `anchor transient-extra only` 更可信；
- 但 `v37` 这组权重下，
  absent-side reconstruction 会和 friend-side speech-leak keep 条件
  形成新的拉扯；
- 所以 `v37` 不保留为新候选。

## 结论

- 本轮有效产出不是一个可保留新 checkpoint，
  而是两条收敛得很关键的结论：

1. `guodegang_absent_proxy_v3_strict`
   已经完整存在于 `v32` base manifest，
   当前缺口不是 coverage，
   而是 objective routing。
2. `reconstruction_extra`
   是比旧 `absent_interval_l1` 更贴近这批样本语义的 branch-local objective；
   但 absent-side only 的 `v37`
   仍会伤到 friend-side exact / `0004-like speech-leak`。

因此下一步若继续自动推进，
更合理的方向应是：

1. 不再把 `v37` 误写成“manifest 扩样 follow-up”；
2. 把它明确视为：
   - `v32` 上的一次 objective re-routing 实验；
3. 后续若继续试新 candidate，
   优先做：
   - 更轻的 absent reconstruction
   - 与更强的 friend-side protection 联动的再平衡
   - 而不是继续放大 absent-only reconstruction 权重
