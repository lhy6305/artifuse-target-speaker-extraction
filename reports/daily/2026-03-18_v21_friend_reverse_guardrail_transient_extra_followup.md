# 2026-03-18 `v21` friend reverse guardrail transient-extra follow-up

## 背景

`v20` 已经证明：

- 只把 friend-side proxy 样本并进 `v19` warm-start
- 但不让它们命中任何专项 selector

本质上只是一次 base-loss nudging，不是真正的 branch-local guardrail。

因此本轮改成两步：

1. 先用 `v12 > v19 > v8` 的 synthetic proxy 搜索结果，重建 friend-side proxy；
2. 再把这批样本通过显式 selector 接进 objective，而不是继续做零命中增量的并集 warm-start。

## 本轮工程补充

本轮在 selector plumbing 上新增了“额外 branch”能力：

- `src/tse_prefix/pipeline/loss_selectors.py`
- `scripts/train/train_stft_mask_baseline.py`

当前一个 loss prefix 可以同时保留：

- 原有 selector branch
- `extra` selector branch

两条 branch 用 OR 方式并起来命中 sample weights。

这让我们可以：

- 保留 `v19` 原有的 hard friend branch
- 再额外挂入新的 clean/full/high-transient friend branch

而不是被迫二选一。

## 新 proxy

本轮采用的 top order-pass proxy 条件为：

- `recipe = target_clean_speech`
- `temporal_pattern = target_full`
- `target_present_ratio >= 0.95`
- `overlap_ratio >= 0.9`
- `interference_pool = speech_interference_clean_pool`
- `target_transient_presence_minus_mid_db_mean >= -9.179057439168297`

对应 manifest：

- `data/synthetic/train_manifest_v21_v19_friend_reverse_guardrail_proxy_v2.jsonl = 25`
- `data/synthetic/val_manifest_v21_v19_friend_reverse_guardrail_proxy_v2.jsonl = 12`

但相对 `v19` 基座去重后，真正新增的唯一样本仍然只有：

- train `21`
- val `8`

也就是说：

- `v21` 和 `v20` 的并集增量样本集合本质上还是同一批 friend-side clean/full 样本
- 本轮真正新增的信息，不在 manifest 本身
- 而在这些样本终于被显式接入 selector

## `v21 = legacy_transient_leakguard_probe_v21_v19_friend_reverse_guardrail_proxy_v2_transient_extra_ft1`

### 训练配置

- init checkpoint：
  - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1/best.pt`
- train manifest：
  - `data/synthetic/train_manifest_v21_v19_plus_friend_reverse_guardrail_proxy_v2.jsonl`
- val manifest：
  - `data/synthetic/val_manifest_v21_v19_plus_friend_reverse_guardrail_proxy_v2.jsonl`
- epochs：
  - `1`
- batch size：
  - `4`
- lr：
  - `1e-5`

### selector 命中变化

- `v19`：
  - train transient / interference / absent = `51 / 51 / 24` out of `90`
  - val transient / interference / absent = `18 / 18 / 4` out of `27`
- `v21`：
  - train transient / interference / absent = `76 / 51 / 24` out of `111`
  - val transient / interference / absent = `30 / 18 / 4` out of `35`

这说明本轮新增的 clean/full/high-transient friend proxy：

- 确实进入了 transient selector
- 不再是 `v20` 那种零 selector 增量

## 结果

### 相对 `v19`

- default val：
  - `+0.008857 dB`
- `v21_v19_friend_reverse_guardrail_proxy_v2`：
  - `-0.076726 dB`
- broad near-real speech probe overall：
  - `-0.042540 dB`
- `near_real_guodegang_transient_probe_v1` overall：
  - `-0.122561 dB`

也就是说：

- 显式 selector 命中确实解决了 `v20` 的“零命中增量”问题
- 但这还不足以把 friend-side proxy 或 broad near-real 从 `v19` 往前推

### stage2-relative near-real speech probe

- `v21` overall：
  - `-0.051850 dB`
- `friend_raw`：
  - `-0.430507 dB`
- `0003`：
  - `-0.938342 dB`
- `0004`：
  - `+0.077329 dB`
- `0006 / guodegang`：
  - `+1.084122 dB`

相对 `v19` 的对应值：

- overall：
  - `v19 = -0.009309 dB`
- `friend_raw`：
  - `v19 = -0.414640 dB`
- `0003`：
  - `v19 = -0.913926 dB`
- `0004`：
  - `v19 = +0.084646 dB`
- `0006 / guodegang`：
  - `v19 = +1.206683 dB`

### speech follow-up gate vs `v19`

- `FAIL`
- failed：
  - `speech_probe_overall_floor`
  - `speech_probe_friend_raw_floor`
  - `anchor_0003_gain_floor`
  - `anchor_0004_gain_floor`
  - `anchor_0006_regression_floor`

和 `v20` 相比，本轮虽然没有再出现“proxy 自己大幅塌陷”的那种全面退化，
但相对 `v19` 的 near-real gate 失败项反而更多，已经把 `0006` 也带回退了。

### guodegang focused probe

`probe_subset_guardrail_vs_v19_with_clips`：

- `FAIL`
- failed：
  - `overall_floor`
  - `family__guodegang_raw`
  - `anchor__near_real_0006`
  - `clip__guodegang_anchor_120s`
  - `clip__guodegang_absent_480s`

其中 clip 值从：

- `v19 anchor_120s = +0.355476 dB`
- `v21 anchor_120s = +0.179821 dB`

以及：

- `v19 absent_480s = +2.057890 dB`
- `v21 absent_480s = +1.988424 dB`

都继续回退。

### synthetic dual-proxy gate vs `v12`

- `PASS`

但只是“仍高于 `v12` floor”，并不代表优于 `v19`：

- `guodegang_anchor_proxy_v1`：
  - `v19 = +2.237552 dB`
  - `v21 = +2.026994 dB`
- `guodegang_absent_proxy_v3_strict`：
  - `v19 = +0.142228 dB`
  - `v21 = +0.110022 dB`
- `guodegang_absent_proxy_v4_broad`：
  - `v19 = +0.195950 dB`
  - `v21 = +0.187115 dB`

## 结论

- selector `extra` branch 这层基础设施保留
- `v21` checkpoint 不保留

更准确地说，本轮已经把问题进一步收窄成：

- 不是 selector 接线缺失
- 而是当前这批 clean/full/high-transient friend proxy
  即便被显式接进 transient loss，也没有提供足够正确的优化方向

因此当前默认接班口径应更新为：

- `v19` 继续保留为 absent-side objective 基座
- `v21` 不保留
- `extra selector` plumbing 保留，后续可继续复用

## 下一步建议

下一步若继续自动推进，不应直接再扫：

- 现有 `v21` proxy 的权重
- 或同一批样本的更多 epoch / lr

更合理的是先做更窄的前置验证：

1. 继续重搜 friend-side proxy
   - 目标不只是 `v12 > v19 > v8`
   - 还要额外要求：
     - 当前 proxy 相对 `v19` 不能在 broad near-real 关键锚点上方向相反
2. 必要时把新 branch 从“clean/full/high-overlap”继续缩窄到更接近：
   - `0003 / 0004`
   - 或 friend-side speech-leak / residual-transient 具体片段形态
3. 在新 proxy 本身先证明：
   - `v21` 这种显式 selector 命中不会继续让 `v19` 回退
   再考虑下一轮训练
