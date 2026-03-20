# 2026-03-20 `v53` dual-head / branch-local decoder plumbing

## 背景

`v49 -> v52` 已把当前这条 adapter 路线压得足够清楚：

- simple residual adapter 不够；
- adapter 看 reference 仍不够；
- adapter 自己再加 temporal model 也仍不够。

因此下一条默认不再继续堆：

- adapter conditioning；
- adapter temporal capacity；
- 或 residual safety knob。

而是先把真正独立的 `dual-head / branch-local decoder`
工程能力补齐，保证下一轮实验不再卡在 plumbing。

## 工程补充

### `src/tse_prefix/models/stft_mask_baseline.py`

新增：

- `enable_branch_decoder_head`

当前语义：

- shared 主分支仍输出：
  - `estimated_waveform_base`
- 若启用 `branch_decoder_head`：
  - 额外复制一套：
    - `branch_decoder_temporal_model`
    - `branch_decoder_mask_head`
  - 默认推理输出切到：
    - `estimated_waveform`
      = branch decoder output
- 新增：
  - `reset_branch_decoder_from_base()`
    用于把 branch decoder
    从当前 base `temporal_model + mask_head`
    复制初始化

解释：

- 这次不再是：
  - 在 shared encoded feature 上叠 residual delta；
- 而是：
  - 给 absent-side
    一套真正独立的 decoder 主干与输出头。

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `--model-enable-branch-decoder-head`

并补充旧 checkpoint 兼容：

- 从旧 checkpoint 初始化时，
  允许缺失：
  - `branch_decoder_temporal_model.*`
  - `branch_decoder_mask_head.*`
- 若缺失，
  自动调用：
  - `reset_branch_decoder_from_base()`

解释：

- 这样第一条 dual-head follow-up
  就不是“旧模型 + 一个随机新头”；
- 而是：
  - 先从旧主分支等价起步，
  - 再只让 branch-local decoder
    学自己的增量。

## smoke 验证

### 目标

确认下面三件事已经接通：

1. `v32` 旧 checkpoint
   能初始化带 branch decoder 的新模型；
2. 只训练：
   - `branch_decoder_temporal_model`
   - `branch_decoder_mask_head`
   能正常反传；
3. `train_summary.json`
   能把新结构和 selector 命中落盘。

### smoke 命令

- 输出目录：
  - `tmp/smoke_branch_decoder_v53`
- init checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt`
- manifest：
  - `data/synthetic/train_manifest_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl`
  - `data/synthetic/val_manifest_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl`
- 只训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- 只开：
  - `reconstruction_extra_waveform_weight = 0.005`
- `max_steps = 1`

### smoke 结果

- 运行通过；
- `device = cuda`
- trainable parameter count：
  - `2,169,601 / 4,537,218`
  - `47.82%`
- `reconstruction_extra`
  selector 命中：
  - train `1 / 1`
  - val `8 / 8`
- 结果文件已落盘：
  - `tmp/smoke_branch_decoder_v53/train_summary.json`

说明：

- dual-head 的最小训练闭环已经接通；
- 旧 checkpoint 兼容与 branch decoder 自举初始化都正常；
- 下一步可以直接开第一条正式 dual-head follow-up，
  不需要再补工程底座。

## 当前结论

本轮还没有给出 `v53` keep / drop 裁决。

这次完成的是：

- `dual-head / branch-local decoder`
  的正式工程接入；
- 以及一轮
  `v32 -> branch decoder`
  的最小 smoke 验证。

因此当前默认下一步应写成：

1. 继续保留 `proxy_v7`；
2. 以 `v32` 为基座；
3. 直接跑第一条真正的
   `dual-head / branch-local decoder`
   follow-up；
4. 仍按同一套：
   - default
   - exact
   - near-real
   - `guodegang`
   - `friend_speech_leak_followup_gate`
   裁决。
