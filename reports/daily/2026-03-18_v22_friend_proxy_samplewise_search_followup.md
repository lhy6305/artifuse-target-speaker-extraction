# 2026-03-18 `v22` friend proxy samplewise search follow-up

## 背景

`v21` 已经说明：

- 让 friend-side proxy 显式命中 selector 是必要条件
- 但当前 `clean/full/high-transient` 这批 proxy 即使进了 objective，也仍会把 `v19` 拉退

因此本轮不再继续训练，而是先把 proxy 搜索口径再收紧一层：

- 不再接受“均值 order-pass 但单样本混有大量反向行”的 proxy
- 改为要求单样本先满足：
  - `v12 > v19 > v8`
  - 再在这些行里搜索 metadata 子集

## 本轮工程补充

为后续 exact proxy 构建补了两项通用能力：

1. `scripts/eval/search_synthetic_proxy_candidates.py`
   - 新增 `--require-samplewise-order-pass`
   - 允许只在单样本已满足目标顺序的行上搜索
   - top candidate 里同步落盘 `sample_ids`
2. `scripts/data/build_metadata_focused_manifest.py`
   - 新增 `--sample-ids-file`
   - 允许直接把 exact `sample_id` allowlist 落成 manifest

## 结果一：samplewise-order-pass 会把候选空间大幅收紧

### val / default

- 原先 shared speech rows：
  - `237`
- 要求单样本先满足 `v12 > v19 > v8` 后，只剩：
  - `38`

这说明之前很多“均值上 order-pass”的 candidate，
其实内部混有大量单样本方向相反的行。

### train / default

- `train_manifest` 上补跑 `stage2 vs v8 / v12 / v19` compare 之后：
  - single-sample order-pass speech rows = `176`

因此 train 侧不是稀有偶然，而是确实存在一批更稳定的 friend-side order-pass 行。

## 结果二：train / val 的 top candidate 已经明显比 `v21` 更窄

### train top full candidate

samplewise-order-pass 搜索在 train 上的 top full candidate 为：

- `target_clean_speech`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap_ratio >= 0.9`
- `speech_interference_clean_pool`
- `interference_gain_db >= -2.127000093460083`
- `target_transient_presence_minus_mid_db_mean >= -10.407621065775553`

exact train ids 共 `10` 条：

- `train_000162`
- `train_000225`
- `train_000237`
- `train_000245`
- `train_000700`
- `train_000762`
- `train_000826`
- `train_001360`
- `train_001586`
- `train_001894`

落盘：

- `data/synthetic/train_manifest_v22_friend_reverse_guardrail_proxy_v3_full_exact.jsonl = 10`

### val top full candidate

对应 val 侧的 exact full candidate 共 `4` 条：

- `val_000033`
- `val_000200`
- `val_000446`
- `val_000496`

落盘：

- `data/synthetic/val_manifest_v22_friend_reverse_guardrail_proxy_v3_full_exact.jsonl = 4`

### val nonfull candidate

另一个仍然 samplewise-order-pass 的 clean nonfull candidate 共 `7` 条：

- `val_000018`
- `val_000032`
- `val_000080`
- `val_000096`
- `val_000297`
- `val_000417`
- `val_000500`

落盘：

- `data/synthetic/val_manifest_v22_friend_reverse_guardrail_proxy_v3_nonfull_exact.jsonl = 7`

## 结果三：`v21` 在这些 exact proxy 上依然低于 `v19`

### exact full proxy

- `compare_v19_vs_v21_on_v22_friend_reverse_guardrail_proxy_v3_full_exact`
- 相对 `v19`：
  - `v21 = -0.065412 dB`

样本级上：

- `val_000200`：
  - `+0.010943 dB`
- `val_000446`：
  - `-0.014272 dB`
- `val_000496`：
  - `-0.355292 dB`

也就是说：

- 即便已经把 full proxy 收紧成 exact samplewise-order-pass 子集
- `v21` 仍没有超过 `v19`

### exact nonfull proxy

- `compare_v19_vs_v21_on_v22_friend_reverse_guardrail_proxy_v3_nonfull_exact`
- 相对 `v19`：
  - `v21 = -0.156167 dB`

而且 `7` 条里：

- improved = `0`
- regressed = `4`

因此 nonfull clean candidate 也不能作为 `v21` 现有 objective 的正向证据。

## 结论

本轮结论已经进一步收紧为：

- `v21` 失败不是因为 proxy 只是“太宽”
- 即便把 proxy 收紧成 exact、single-sample order-pass 的 full / nonfull 子集
- `v21` 相对 `v19` 仍然是负的

因此当前不应继续：

- 直接起 `v22` 训练
- 或对 `v21` 现有 objective 扫更多权重 / epoch / lr

## 当前建议

下一步若继续自动推进，优先级应改成：

1. 继续保留本轮新增的 exact proxy 工具链
   - `samplewise-order-pass` 搜索
   - `sample_ids_file` manifest 构建
2. 不要直接沿 `v21 transient_extra` objective 开 `v22`
3. 下一轮真正值得尝试的，应该是改 proxy 的语义，而不是只改 proxy 的宽窄：
   - 更贴近 `0003 / 0004` 的 residual-transient / speech-leak 形态
   - 或与当前 full / nonfull 分支不同的 loss 归属，而不是继续只挂在 `transient_extra`
