# 2026-03-19 `v29` exact speech-leak sample-id selector follow-up

## 背景

`v24-v27` 已确认：

- friend-side `0004-like speech-leak` 不是 “selector 没接上” 的问题；
- 但上一轮 `v28` 的 metadata-only 宽集合也证明：
  - 仅靠 `gain / target transient / similarity` 之类元数据阈值，
  - 还不足以稳定重建真正的 `samplewise-order-pass` speech-leak proxy。

因此本轮改成两步：

1. 先把 `v12 > v19 > v8` 的 exact speech-leak 子集收成 sample-id allowlist；
2. 再给训练侧补 `focus_sample_ids` selector，让 objective 真正命中 exact proxy，而不是命中它的宽泛元数据近似。

## 工程补充

- `scripts/data/build_metadata_focused_manifest.py`
  - 新增 `--include-derived-metrics`
  - 允许在不靠 transient/similarity 过滤的情况下，也把派生声学字段写回 manifest
- `scripts/train/train_stft_mask_baseline.py`
  - 新增 `--loss-*-focus-sample-ids-file`
- `src/tse_prefix/pipeline/loss_selectors.py`
  - selector 新增 `focus_sample_ids`
  - 可在 base / extra branch 上直接按 sample-id allowlist 精确命中

## 新 exact proxy

### train exact

- `data/synthetic/sample_ids_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact_train.txt = 21`
- `data/synthetic/train_manifest_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 21`
- 语义：
  - `target_clean_speech`
  - `target_full`
  - clean speech interference
  - exact `samplewise-order-pass`
- stage2-relative train ordering：
  - `v12 = 1.651502 dB`
  - `v19 = 1.517228 dB`
  - `v8 = 0.828849 dB`

### val exact

- `data/synthetic/sample_ids_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact_val.txt = 3`
- `data/synthetic/val_manifest_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 3`
- stage2-relative default ordering：
  - `v12 = 1.782149 dB`
  - `v19 = 1.559787 dB`
  - `v8 = 0.557526 dB`

### union training manifests

- `data/synthetic/train_manifest_v29_v19_plus_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 111`
- `data/synthetic/val_manifest_v29_v19_plus_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 30`
- combined selector ids:
  - `data/synthetic/sample_ids_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact_all.txt = 24`

## `v29 = legacy_transient_leakguard_probe_v29_v19_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact_ft1`

### 训练配置

- init checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1/best.pt`
- train manifest:
  - `data/synthetic/train_manifest_v29_v19_plus_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl`
- val manifest:
  - `data/synthetic/val_manifest_v29_v19_plus_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl`
- epochs:
  - `1`
- batch size:
  - `4`
- lr:
  - `1e-5`
- model conditioning:
  - `legacy_bias`
- branch 挂法：
  - 保留 `v19` 原有 `transient / interference / absent`
  - 新 speech-leak exact 子集挂到 `interference_extra_focus_sample_ids`

### selector 命中

- train:
  - transient `51 / 111`
  - interference `72 / 111`
  - absent `24 / 111`
- val:
  - transient `18 / 30`
  - interference `21 / 30`
  - absent `4 / 30`

这说明：

- `interference_extra` 新增命中正好是：
  - train `+21`
  - val `+3`
- 本轮已经不是宽 metadata selector，而是 exact sample-id selector 真命中。

## 结果

相对 `v19`：

- default:
  - `-0.004999 dB`
- `v29 exact speech-leak proxy`:
  - `-0.142498 dB`

因此当前结论很直接：

- 即便把 `0004-like speech-leak` 的训练入口收紧到 exact sample-id；
- 即便让 selector 精确命中这批样本；
- 也仍然没有把 `v19` 往前推。

这次失败可以排除掉的解释包括：

- selector 没接上
- 宽 metadata proxy 混入了太多坏样本
- train / val exact proxy 只是没有被真正命中

剩下更可信的解释是：

- `0004-like speech-leak` 这条 objective / proxy 语义本身仍然不够对；
- 即使 exact boundary 对了，当前 loss 归属与优化方向也还没有形成正收益。

## 当前结论

- `v29` 不保留为新候选；
- `focus_sample_ids` selector plumbing 保留，可复用到后续 exact proxy；
- 当前 friend-side 主线结论继续保持：
  - `v19` 仍是基座；
  - 下一步若继续自动推进，应优先重做 `0004-like speech-leak` 的 objective / proxy 语义，而不是继续扫描这条 exact selector 的权重或 epoch。
