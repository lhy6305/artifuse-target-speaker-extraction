# 2026-03-19 `v42` absent proxy `v7` follow-up

## 背景

`v40 / v41` 已经把上一轮 absent-side follow-up 收紧得很清楚：

- `v40` 证明：
  - 去掉 exact overlap
    还不足以把 absent-side real gate 拉回；
- `v41` 证明：
  - `proxy_v6 currentsignal cleanonly`
    本体就在反向，
    不能继续当默认 keep 候选。

因此本轮不再沿：

- `v5 cleancarve`
  再做 overlap carve-out；
- 或 `proxy_v6 currentsignal cleanonly`
  再做小修小补。

而是正式执行 `B3`：

- 重新定义 absent-side protection proxy；
- 先找一条：
  - 与 friend-side exact overlap 更干净；
  - 同时对 real `guodegang_anchor / absent`
    更贴近的 synthetic proxy。

## 结果一：`v7` 已从搜索候选落成正式 proxy

### 1. `v7` selector 定义

本轮把之前搜索到的 top positive-order candidate 直接物化为：

- `train_manifest_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl = 33`
- `val_manifest_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl = 8`

对应条件是：

- `recipe = target_clean_speech`
- `overlap >= 0.9`
- `interference_pool = speech_interference_clean_pool`
- `target_transient_presence_minus_mid_db_mean <= -11.535072326660156`
- `interference_transient_presence_minus_mid_db_mean <= 4.414128621419269`

并同步补了：

- `sample_ids_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans_train.txt`
- `sample_ids_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans_val.txt`
- `sample_ids_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans_all.txt`

### 2. overlap 与 coverage 核对

和 friend-side exact family 的交集：

- train：
  - `33` 条里只有 `1` 条 overlap：
    - `train_001225`
- val：
  - `8` 条里 `0` 条 overlap

和 `v32` base manifest 的关系：

- 这不是旧 rows 重路由；
- 而是：
  - train 新 coverage `32`
  - val 新 coverage `8`

即：

- `v7`
  已经满足 `B3`
  最关键的两个前提：
  - 不是再拿旧 rows 换 routing；
  - val 侧没有再撞回 friend-side exact family。

### 3. 旧 checkpoint 在 `v7` 上的对比

relative to `v19`：

- `v32 = -0.788730 dB`
- `v40 = +0.537238 dB`
- `v41 = +1.267294 dB`

这说明：

- `v7`
  的确能把
  `v32 < v40 < v41`
  这条 absent-side 后续变化拉开；
- 它至少不是像 `proxy_v6`
  那样本体直接一路反向的 proxy。

## 结果二：已完成 `v42 = v32 + reconstruction_extra(proxy_v7)` 训练

### 训练定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v42_v32_absent_reconstructionextra_v7_highoverlap_lowtargettransient_lowinttrans_wave_ft1`
- init：
  - `v32`
- merged manifest：
  - train `129`
  - val `37`
- 新增 coverage：
  - train `32`
  - val `8`
- `reconstruction_extra`：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `reconstruction_extra_focus_sample_ids = proxy_v7 all ids`
- 其余 branch 维持 `v41` 同级配置：
  - friend-side exact `interference_extra`
  - base transient / interference / absent

### selector 命中

- train：
  - `reconstruction_extra = 33 / 129`
- val：
  - `reconstruction_extra = 8 / 37`

说明：

- 本轮新 objective
  确实只落在 `v7`
  这批新 absent proxy rows 上；
- 没有再退回
  `v37`
  那种“旧集合原地改 routing”的情况。

## 结果三：`v42` 的标准裁决面板

### relative to `v19`

- default：
  - `+0.077955 dB`
- exact proxy overall：
  - `-0.316042 dB`
- exact `target_full`：
  - `-0.664459 dB`
- near-real speech probe overall：
  - `-0.078007 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.113430 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.126568 dB`
- near-real `guodegang_absent_480s`：
  - `+0.031863 dB`
- `guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans`：
  - `+0.444459 dB`

### relative to `v32` 的 `friend_speech_leak_followup_gate`

- `overall_pass = false`
- failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

其余 floor 都通过：

- `default_stage2_delta_floor`
- `speech_probe_overall_floor`
- `guodegang_anchor_floor`
- `guodegang_absent_floor`

## 裁决

`v42` 仍不能作为 keep 候选。

但这次的失败性质和 `v40 / v41` 不一样，必须分开记：

1. `v42` 不是 `proxy` 本体反向。
   - `proxy_v7` 本体 relative to `v19` 仍是：
     - `+0.444459 dB`
2. `v42` 也不是 absent-side real floor 全线失败。
   - `guodegang_anchor_120s = +0.126568 dB`
   - `guodegang_absent_480s = +0.031863 dB`
3. 当前真正没守住的，只剩 friend-side 两条：
   - exact `target_full = -0.664459 dB`
   - `speech_leak_like (0004) = -0.113430 dB`

大白话讲：

- `v7`
  这条新 absent proxy
  本身是成立的；
- 它甚至是当前第一条能在
  `val` 零 exact overlap
  的前提下，
  同时把
  `guodegang_anchor / absent`
  两条 real floor
  拉回正向的 proxy；
- 但当前这种
  `waveform-only reconstruction_extra(proxy_v7)`
  routing
  仍然会把 friend-side
  `exact target_full`
  和 `0004-like speech-leak`
  一起拖坏。

## 当前阶段结论

因此 `B3` 到这里应写成：

1. `proxy_v6` 应淘汰。
2. `proxy_v7` 可保留为新的 absent-side protection proxy。
3. `v42` 证明：
   - 代理本体与 real `guodegang` floor
     已经比 `v6` 更对；
   - 但 objective routing
     还不能直接照搬 `v41` 的
     `reconstruction_extra_waveform_only`
     方案。

## 下一步建议

若继续自动推进，默认下一条应是：

- 保留 `proxy_v7`
- 但重写它与 friend-side speech-leak 的解耦方式

优先级应收紧为：

1. 不再回退到 `proxy_v6`。
2. 不把 `v42` failed 误写成：
   - `proxy_v7` 也无效。
3. 下一条默认优先保护：
   - exact `target_full`
   - `speech_leak_like (0004)`
   而不是再重新搜索 absent proxy 本体。
