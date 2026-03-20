# 2026-03-20 dual-head `base-delta-interference projection` smoke

## 背景

`v57 / v58` 已说明：

- exact-family `base-align`
  是有信号的 protect primitive；
- 但它的问题也很明确：
  - weight 重了，
    `proxy_v7`
    会被直接压塌；
  - weight 轻了，
    `speech_leak_like (0004)`
    又重新 clear fail。

因此本轮没有直接开新正式实验，
而是先补一条更局部的 dual-head protect primitive：

- `interference_extra_base_delta_projection_weight`

语义是：

- 只在 `interference_extra`
  exact ids 上；
- 约束 branch output
  相对 frozen base output
  的增量里，
  不要出现 interference-like 投影；
- 而不是像 `base-align`
  那样直接把整段 branch 输出
  都往 base 拉回。

## 工程补充

### `src/tse_prefix/pipeline/baseline_train.py`

新增：

- `base_delta_interference_projection_loss(...)`
- `interference_extra_base_delta_projection_weight`
- `interference_extra_base_delta_projection_ratio`

当前语义：

- `delta = extra_prediction - prediction`
- `interference = mixture - target`
- 只惩罚：
  - `delta`
    在 interference 方向上的投影能量

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `--loss-interference-extra-base-delta-projection-weight`

并补齐：

- `interference_extra`
  selector 的激活条件，
  现在会把：
  - `interference_extra_base_delta_projection_weight`
    也算进去

### `scripts/eval/eval_stft_mask_baseline.py`

同步补齐：

- `interference_extra_base_delta_projection_ratio`
  的 summary 落盘
- pattern / recipe / ratio bucket
  级聚合

## smoke 目标

确认下面几件事已经接通：

1. `v32` 旧 checkpoint
   能初始化这条新 protect primitive；
2. `interference_extra`
   selector
   会因为新 weight 真正激活；
3. `train_summary.json`
   与 val summary
   能把新指标落盘。

## smoke 配置

- 输出目录：
  - `tmp/smoke_branch_decoder_base_delta_projection`
- init checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt`
- manifests：
  - `data/synthetic/train_manifest_v42_v30_plus_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl`
  - `data/synthetic/val_manifest_v42_v30_plus_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl`
- dual-head：
  - `enable_branch_decoder_head = true`
- 仅训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- absent-side：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `focus = proxy_v7 all ids`
- friend-side protect：
  - `interference_extra_base_delta_projection_weight = 0.005`
  - `focus = v30 exact 10 ids`
- 其他 base loss：
  - 沿用 `v58`
    的 `transient / interference / absent`
    基础配置
- `max_steps = 1`

## smoke 结果

- 运行通过；
- `device = cuda`
- trainable parameter count：
  - `2,169,601 / 4,537,218`
  - `47.82%`
- `interference_extra`
  selector 已真实激活：
  - train `1 / 4`
  - val `3 / 37`
- `reconstruction_extra`
  selector 正常：
  - train `2 / 4`
  - val `8 / 37`
- 新指标已落盘：
  - `train_interference_extra_base_delta_projection_ratio`
  - `val_interference_extra_base_delta_projection_ratio`
- 结果文件：
  - `tmp/smoke_branch_decoder_base_delta_projection/train_summary.json`

## 当前结论

这轮还没有给出新 keep / drop 结论。

这次完成的是：

- 下一条 dual-head protect candidate
  的工程接入；
- 以及一轮最小 smoke，
  证明：
  - 旧 checkpoint 兼容；
  - selector 激活正常；
  - summary 落盘正常。

因此当前更准确的状态应写成：

1. `v55 - v58`
   仍然是最近一轮正式实验结论；
2. `interference_extra_base_delta_projection_weight`
   已经具备直接开正式 follow-up 的工程条件；
3. 当前仍未回答的，
   不是 plumbing，
   而是：
   - 这条更局部的 delta-interference protect
     能否比 exact-family `base-align`
     更好地兼顾：
     - `proxy_v7`
     - `speech_leak_like (0004)`
     - `guodegang`
