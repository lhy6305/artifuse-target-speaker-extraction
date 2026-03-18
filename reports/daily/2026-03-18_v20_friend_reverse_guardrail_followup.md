# 2026-03-18 `v20` friend reverse guardrail follow-up

## 背景

在 `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
首次通过 synthetic dual-proxy gate 之后，当前主问题已经不再是：

- 继续只补 `0006 / absent_480s`

而是：

- 如何以 `v19` 为基座补 friend-side `friend_raw / 0003 / 0004` reverse guardrail

本轮围绕这个问题做了一次最小 warm-start 跟进，并同步把下一步要用到的 selector plumbing 补到了当前工作树。

## 本轮工程补充

已把以下字段接入 dataset / train / eval / selector：

- `target_transient_presence_minus_mid_db_mean`
- `target_transient_presence_share_mean`

对应当前工作树改动为：

- `src/tse_prefix/data/synthetic_dataset.py`
- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`
- `src/tse_prefix/pipeline/loss_selectors.py`

当前这些改动只是在为下一步 friend-side branch-local selector 做准备；
本轮 `v20` 本身并没有实际启用这些新 selector 阈值。

## `v20 = legacy_transient_leakguard_probe_v20_v19_friend_reverse_guardrail_v1_ft1`

### 训练配置

- init checkpoint：
  - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1/best.pt`
- train manifest：
  - `data/synthetic/train_manifest_v20_v19_plus_friend_reverse_guardrail_v1.jsonl`
- val manifest：
  - `data/synthetic/val_manifest_v20_v19_friend_reverse_guardrail_proxy_v1.jsonl`
- epochs：
  - `1`
- batch size：
  - `4`
- lr：
  - `1e-5`

### manifest 结构事实

- 相对 `v19`：
  - train total：`90 -> 111`
  - val total：`27 -> 35`
- 新增样本实际只有：
  - train `21`
  - val `8`
- 这些新增样本全部都是：
  - `target_clean_speech`
  - `target_full`
- 新增 val 样本为：
  - `val_000033`
  - `val_000034`
  - `val_000041`
  - `val_000050`
  - `val_000202`
  - `val_000338`
  - `val_000365`
  - `val_000496`

### selector 命中事实

- `v19` train selector：
  - transient / interference / absent = `51 / 51 / 24` out of `90`
- `v20` train selector：
  - transient / interference / absent = `51 / 51 / 24` out of `111`
- `v19` val selector：
  - transient / interference / absent = `18 / 18 / 4` out of `27`
- `v20` val selector：
  - transient / interference / absent = `18 / 18 / 4` out of `35`

这说明当前新加的 friend reverse guardrail 样本：

- 没有增加任何一条 transient 命中
- 没有增加任何一条 interference 命中
- 没有增加任何一条 absent 命中

也就是说，`v20` 不是：

- “把 friend-side guardrail 接进了 branch-local objective”

而更接近：

- “在 `v19` 现有 objective 外面，再额外加了一批只吃 base reconstruction loss 的 `target_clean_speech + target_full` 样本”

## 结果

### 相对 `v19` 的 synthetic default

- overall：
  - `-0.020962 dB`
- `target_clean_speech`：
  - `-0.104638 dB`
- `target_full`：
  - `-0.070204 dB`

### 相对 `v19` 的 friend reverse guardrail proxy

- `v20_v19_friend_reverse_guardrail_proxy_v1`：
  - `-0.131127 dB`

也就是说，本轮 candidate 连自己新增的 friend-side proxy 都没保住。

### 相对 `v19` 的 near-real speech probe

- overall：
  - `-0.051919 dB`
- `near_real_friend_speech_probe` overall：
  - `-0.021704 dB`
- `near_real_guodegang_speech_probe` overall：
  - `-0.142566 dB`

样本级上：

- guodegang 6 条里有 4 条明显回退：
  - `probe_0020 = -0.230226 dB`
  - `probe_0021 = -0.214543 dB`
  - `probe_0019 = -0.211931 dB`
  - `probe_0024 = -0.101816 dB`

### `speech_followup_gate_vs_v12`

- `FAIL`
- failed：
  - `speech_probe_overall_floor`
  - `speech_probe_friend_raw_floor`
  - `anchor_0003_gain_floor`
  - `anchor_0004_gain_floor`

而且这四项都比 `v19` 更差：

- speech overall：
  - `v19 = +0.002617 dB`
  - `v20 = -0.061228 dB`
- `friend_raw`：
  - `v19 = -0.374906 dB`
  - `v20 = -0.436343 dB`
- `0003`：
  - `v19 = -0.845748 dB`
  - `v20 = -0.942904 dB`
- `0004`：
  - `v19 = +0.095936 dB`
  - `v20 = +0.070217 dB`

### `probe_subset_guardrail_vs_v8_with_clips`

- overall / family / `0006` / `anchor_120s`：
  - 仍通过
- 但：
  - `clip__guodegang_absent_480s`
  - 继续失败
- 相对 `v8`：
  - `v19 = +2.135139 dB`
  - `v20 = +1.991658 dB`

## 结论

- `v20` 不保留
- 不继续沿：
  - `v19 + friend_reverse_guardrail_proxy_v1`
  - 这种“无 selector 命中增量的并集 warm-start”路线继续加预算

更准确地说，本轮已经证明：

- friend-side 问题确实不能靠只修 `absent_480s` 自动带回来
- 但如果新增 friend-side proxy 样本本身没有进入任何专项 selector，
  那它只会作为 base-loss nudging 去拉扯 `v19`
- 这类拉扯会同时伤到：
  - broad speech probe
  - guodegang 子 probe
  - 以及新增 proxy 自己

## 下一步建议

下一步若继续自动推进，应优先做以下两类动作之一，而不是再直接复制 `v20`：

1. 把 friend-side proxy 接入显式 selector
   - 直接使用当前已补好的：
     - `min/max_target_transient_presence_minus_mid_db_mean`
     - `min/max_target_transient_presence_share_mean`
   - 让新增 friend-side样本真正进入 branch-local transient / interference 路

2. 先重做 friend-side synthetic proxy
   - 目标不是“再找一批 `target_clean_speech + target_full` 样本直接并集”
   - 而是先验证它是否能稳定复现：
     - `v12` 相对 `v19` 的 friend-side 排序差异
   - 再决定是否值得开训练

当前默认接班口径应更新为：

- `v19` 继续保留为 absent-side objective 基座
- `v20` 不保留
- 下一步优先补：
  - friend-side branch-local selector / proxy
- 不再继续：
  - 无 selector 命中增量的 `v19 + friend proxy` 并集 warm-start
