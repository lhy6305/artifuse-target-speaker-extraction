# 2026-03-18 `v23` friend proxy semantic split follow-up

## 背景

`v22` 已经说明：

- 当前 `v21 transient_extra` 路线的问题，不只是 proxy 太宽
- 即便改成 exact、single-sample order-pass 的 full / nonfull proxy，`v21` 也仍低于 `v19`

因此本轮不再继续扫同类 full/high-transient proxy，而是把 friend-side 语义继续拆成两族：

- `0003-like = residual_transient_like`
- `0004-like = speech_leak_like`

## 本轮工程补充

为支持这次语义拆分，补了一个搜索能力：

- `scripts/eval/search_synthetic_proxy_candidates.py`
  - 新增 low-side bucket：
    - `gain_le_q50`
    - `transient_le_q50`
    - `transient_lt_q67`

这使搜索不再只能找“高 transient / 高 gain”子集，也能显式把：

- low-transient speech-leak 族
- low-gain residual-like 子族

拉出来做 exact proxy。

## 结果一：`0003-like` / `0004-like` 已可稳定拆成两族 exact proxy

### `0003-like` residual-transient family

当前最稳定的 `0003-like` synthetic family 仍然是：

- `target_full`
- clean-speech-dominant
- overlap 高
- target transient 偏高

落盘 exact manifests：

- `data/synthetic/train_manifest_v23_friend_reverse_guardrail_proxy_v4_residual_transient_exact.jsonl = 10`
- `data/synthetic/val_manifest_v23_friend_reverse_guardrail_proxy_v4_residual_transient_exact.jsonl = 4`

其中 val exact ids 为：

- `val_000033`
- `val_000200`
- `val_000446`
- `val_000496`

### `0004-like` speech-leak family

当前可稳定抽出的 `0004-like` synthetic family 则不再是 `nonfull`，而更像：

- `target_full`
- clean speech interference pool
- interference gain 偏高
- target transient 偏低

落盘 exact manifests：

- `data/synthetic/train_manifest_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact.jsonl = 11`
- `data/synthetic/val_manifest_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact.jsonl = 3`

其中 val exact ids 为：

- `val_000075`
- `val_000165`
- `val_000263`

这说明：

- `0004-like` 并不等价于之前的 `nonfull` clean candidate
- 至少在当前 samplewise-order-pass 行里，它更接近：
  - full overlap
  - clean pool
  - higher-gain
  - lower-transient

## 结果二：`v21` 在这两族 exact val proxy 上都没有超过 `v19`

### residual-transient exact

- `compare_v19_vs_v21_on_v23_friend_reverse_guardrail_proxy_v4_residual_transient_exact`
- 相对 `v19`：
  - `v21 = -0.065412 dB`

这与前一轮 `v22 full exact` 的结论一致。

### speech-leak exact

- `compare_v19_vs_v21_on_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact`
- 相对 `v19`：
  - `v21 = -0.020621 dB`

样本级上：

- `val_000165`：
  - `+0.043592 dB`
- `val_000263`：
  - `-0.036758 dB`
- `val_000075`：
  - `-0.068697 dB`

虽然幅度不大，但方向仍不是正的。

## 结论

本轮结论进一步收紧为：

- friend-side 问题现在已经可以明确拆成至少两条语义：
  - residual-transient-like
  - speech-leak-like
- 这两条语义都能用 exact sample-id manifest 稳定落盘
- 但当前 `v21 transient_extra` 单一路径：
  - 在 residual-transient exact 上仍低于 `v19`
  - 在 speech-leak exact 上也仍低于 `v19`

因此当前不应继续把下一步写成：

- 继续扫单一 `transient_extra`
- 或继续把 `0004-like` 当作另一批 transient proxy

## 当前建议

下一步若继续自动推进，优先级应改成：

1. 保留本轮新增的 semantic-split 搜索链和 exact manifests
2. 不再把 `0003 / 0004` 合并成一个 friend-side proxy
3. 后续新训练若要开，应至少按两条 branch-local 语义设计：
   - `0003-like` residual-transient proxy：
     - 仍可挂在 transient-adjacent objective
   - `0004-like` speech-leak proxy：
     - 不应默认继续挂在同一个 `transient_extra`
     - 更像需要 interference / leak 侧的独立归属
