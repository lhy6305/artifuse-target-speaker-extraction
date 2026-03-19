# 2026-03-19 `v24-v27` friend proxy branch split follow-up

## 背景

`v23` 已把 friend-side speech overlap 回退进一步拆成两条语义：

- `0003-like = residual_transient_like`
- `0004-like = speech_leak_like`

并且已经确认：

- `v21 transient_extra` 在这两族 exact proxy 上都仍低于 `v19`
- 因而下一步不能再把 `0003 / 0004` 合并成单一 transient-only friend objective

本轮继续做的不是“再搜 proxy”，而是把这两条语义真正落到训练侧，验证：

1. 把两条语义分别挂到不同 loss 归属后，是否能比 `v19` 更稳；
2. 若拆成单侧 branch-local follow-up，是否至少有一侧可以独立转正。

## 本轮实验设计

### `v24` semantic split one-shot

- checkpoint:
  - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v24_v19_friend_reverse_guardrail_proxy_v4_semantic_split_ft1`
- proxy manifests:
  - `train_manifest_v24_v19_friend_reverse_guardrail_proxy_v4_semantic_split.jsonl = 21`
  - `val_manifest_v24_v19_friend_reverse_guardrail_proxy_v4_semantic_split.jsonl = 7`
- 训练侧挂法：
  - `0003-like residual-transient` 继续走 `transient_extra`
  - `0004-like speech-leak` 转到 `interference_extra`
- selector 命中：
  - train transient `55 / 109`
  - train interference `51 / 109`
  - train absent `24 / 109`

### `v25` semantic split exact-with-metrics refresh

- checkpoint:
  - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v25_v19_friend_reverse_guardrail_proxy_v4_semantic_split_ft1`
- proxy manifests:
  - `train_manifest_v25_v19_friend_reverse_guardrail_proxy_v4_semantic_split.jsonl = 21`
  - `val_manifest_v25_v19_friend_reverse_guardrail_proxy_v4_semantic_split.jsonl = 7`
- 这是在同一 semantic-split 方向上，基于补过 metrics 的 manifest 重新做的一版更积极命中；
- selector 命中：
  - train transient `63 / 109`
  - train interference `62 / 109`
  - train absent `24 / 109`

### `v26` residual-only carve-out

- checkpoint:
  - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v26_v19_friend_reverse_guardrail_proxy_v4_residual_only_ft1`
- proxy manifests:
  - `train_manifest_v26_v19_friend_reverse_guardrail_proxy_v4_residual_only.jsonl = 10`
  - `val_manifest_v26_v19_friend_reverse_guardrail_proxy_v4_residual_only.jsonl = 4`
- 仅保留 `0003-like residual-transient` 这一侧；
- selector 命中：
  - train transient `63 / 98`
  - train interference `51 / 98`
  - train absent `24 / 98`

### `v27` speech-leak-only carve-out

- checkpoint:
  - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v27_v19_friend_reverse_guardrail_proxy_v4_speech_leak_only_ft1`
- proxy manifests:
  - `train_manifest_v27_v19_friend_reverse_guardrail_proxy_v4_speech_leak_only.jsonl = 11`
  - `val_manifest_v27_v19_friend_reverse_guardrail_proxy_v4_speech_leak_only.jsonl = 3`
- 仅保留 `0004-like speech-leak` 这一侧；
- selector 命中：
  - train transient `51 / 101`
  - train interference `62 / 101`
  - train absent `24 / 101`

## 结果

### 1. `v24-v27` 都不是“selector 没接上”的问题

本轮 4 条 follow-up 都已经把 friend-side proxy 真正接入了 active selector：

- `v24`:
  - transient `55 / 109`
  - interference `51 / 109`
- `v25`:
  - transient `63 / 109`
  - interference `62 / 109`
- `v26`:
  - transient `63 / 98`
  - interference `51 / 98`
- `v27`:
  - transient `51 / 101`
  - interference `62 / 101`

因此这批实验的失败，不应再解释成：

- selector plumbing 没接好
- 或 friend-side proxy 只是继续停留在 base-loss nudging

### 2. semantic split one-shot 没有把 friend-side 关键方向推到 `v19` 之上

`v24` 相对 `v19`：

- default:
  - `+0.021078 dB`
- semantic-split proxy:
  - `-0.091072 dB`
- near-real speech probe overall:
  - `-0.016185 dB`
- 其中：
  - `near_real_friend_speech_probe = -0.041770 dB`
  - `near_real_guodegang_speech_probe = +0.060570 dB`

`v25` 相对 `v19`：

- default:
  - `+0.028038 dB`
- semantic-split proxy:
  - `-0.152489 dB`
- residual-transient exact:
  - `-0.176585 dB`
- speech-leak exact:
  - `-0.120362 dB`
- near-real speech probe overall:
  - `-0.005736 dB`
- 其中：
  - `near_real_friend_speech_probe = -0.037164 dB`
  - `near_real_guodegang_speech_probe = +0.088547 dB`

这说明：

- 即便把 `0003-like` 和 `0004-like` 分别挂到 `transient_extra / interference_extra`
- 甚至进一步提高这批样本的 selector 命中率
- 当前 one-shot semantic split 仍没有把：
  - friend-side exact proxy
  - near-real friend speech bucket
  一起推到 `v19` 之上

### 3. 单侧 carve-out 也没有救回来

`v26` residual-only 相对 `v19`：

- default:
  - `+0.045235 dB`
- residual-only proxy:
  - `-0.201198 dB`
- near-real speech probe overall:
  - `-0.036332 dB`
- 其中：
  - `near_real_friend_speech_probe = -0.049491 dB`
  - `near_real_guodegang_speech_probe = +0.003146 dB`

`v27` speech-leak-only 相对 `v19`：

- default:
  - `+0.037512 dB`
- speech-leak-only proxy:
  - `-0.144539 dB`
- near-real speech probe overall:
  - `-0.034494 dB`
- 其中：
  - `near_real_friend_speech_probe = -0.044400 dB`
  - `near_real_guodegang_speech_probe = -0.004776 dB`

这说明：

- `0003-like residual-transient`
  单独做 carve-out，当前也没有独立转正；
- `0004-like speech-leak`
  单独走 interference/leak 侧归属，当前同样没有独立转正；
- 而且后者已经开始把 `guodegang` 侧收益一起回吐。

### 4. `v25` 只是“代价最小”，不是“已经通过”

从这组 follow-up 看：

- `v25` 的 broad overall 代价最小：
  - near-real speech probe overall `-0.005736 dB`
- 但它仍然：
  - friend speech bucket 为负
  - residual exact 为负
  - speech-leak exact 为负

因此 `v25` 不能写成：

- semantic split 已经基本可用

更准确的写法只能是：

- 在 `v24-v27` 里，它是回退最小的一版
- 但仍没有形成任何一条可保留的新 objective 升级线

## 结论

本轮结论继续收紧为：

- `v24-v27` 都不保留为新的主候选；
- 当前 friend-side 的问题已经不是：
  - selector 没接上
  - 或两条语义还没拆开
- 更准确的解释应改写为：
  - 当前这两条 branch-local objective 的语义仍不够对
  - 即便分别接到 `transient_extra / interference_extra`
  - 或分别单独 carve-out
  - 也还没有把 `v19` 上的 friend-side缺口推正

## 当前建议

下一步若继续自动推进，优先级应更新为：

1. 不继续对 `v24-v27` 扫权重、扫 epoch、扫 lr；
2. 不再把“已经 semantic split”误写成“objective 已经对了”；
3. 后续若还要补 friend-side，优先改的是：
   - `0004-like speech-leak` 的 proxy / objective 语义本身
   - 或更明确的 branch-local 归属与 guardrail
4. `0003-like residual-transient` 也暂不视为已找到稳定可训练入口；
5. 当前可继续保留的基座仍是：
   - `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
