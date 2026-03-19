# 2026-03-19 `v39` absent reconstruction + `v5 cleancarve` metadata carve-out follow-up

## 背景

`v37 / v38` 已经把 absent-side 这条线的冲突收紧得很清楚：

- 直接对 `guodegang_absent_proxy_v3_strict` 这批 shared hard `target_full` 行施加 `reconstruction_extra`
  的确能把 absent / anchor real floor 往回拉一点；
- 但只要还是作用在这批与 friend-side exact branch 共用的 hard 行上，
  exact `target_full` 与 `0004-like speech-leak` 就会一起被拖坏。

因此这次不再沿：

- `v37 / v38` 的 shared-row reconstruction 配比
- 或继续扫 `interference_extra_weight`

而是转成一个更窄的 metadata carve-out：

- 不再直接复用 `guodegang_absent_proxy_v3_strict` 的整族 sample-id；
- 改为只挑一批更接近 clean absent 语义、同时尽量绕开 friend-side exact 冲突区域的
  `target_clean_speech + target_full + speech_interference_clean_pool` 子集；
- 然后只在这批 carve-out 行上挂轻量 `waveform-only reconstruction_extra`。

大白话讲，就是：

- 先别再拿整坨 absent proxy 去硬拉；
- 先把里面看起来更“干净”、更不像 exact speech-leak 冲突区的那部分切出来，
  看这种更窄的 carve-out 能不能保住真实门。

## `v39 = legacy_transient_leakguard_probe_v39_v32_absent_reconstructionextra_v5_cleancarve_wave_ft1`

### 训练配置

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v39_v32_absent_reconstructionextra_v5_cleancarve_wave_ft1`
- init：
  - `v32`
- manifest：
  - train:
    - `data/synthetic/train_manifest_v39_v30_plus_guodegang_absent_proxy_v5_cleancarve.jsonl`
  - val:
    - `data/synthetic/val_manifest_v39_v30_plus_guodegang_absent_proxy_v5_cleancarve.jsonl`
- manifest 规模：
  - `v32` base:
    - train `97`
    - val `29`
  - `v39 v5 cleancarve`:
    - train `187`
    - val `49`

### `reconstruction_extra` carve-out 口径

`train_summary.json` 里实际落盘的 selector 条件为：

- `reconstruction_extra_focus_recipes = ["target_clean_speech"]`
- `reconstruction_extra_focus_patterns = ["target_full"]`
- `reconstruction_extra_focus_interference_pools = ["speech_interference_clean_pool"]`
- `reconstruction_extra_min_target_ratio = 0.95`
- `reconstruction_extra_max_target_transient_presence_minus_mid_db_mean = -9.231693267822266`
- `reconstruction_extra_max_interference_transient_presence_minus_mid_db_mean = 5.840137958526611`

loss 变化点：

- `reconstruction_extra_waveform_weight = 0.01`
- `reconstruction_extra_stft_weight = 0.0`
- `interference_extra_weight = 0.0075`
- 保留 `v32` 的 friend-side exact `interference_extra`
- 不启用：
  - `transient_extra`
  - `absent_extra`

## selector 命中

- train：
  - `reconstruction_extra = 94 / 187`
  - `interference_extra = 7 / 187`
- val：
  - `reconstruction_extra = 21 / 49`
  - `interference_extra = 3 / 49`

说明：

- 这次不是回到 `v37 / v38` 那种 shared 旧集合原地调权；
- 而是真的把 absent-side candidate coverage 扩成了一批 metadata carve-out；
- 但 friend-side exact branch 的命中规模仍然保持在原来的 7 / 3，
  所以这条实验的主要变化仍是：
  - absent-side carve-out 选样
  - 而不是 friend-side protection 变强

## 结果

### 相对 `v19`

- default：
  - `+0.056255 dB`
- exact proxy overall：
  - `-0.046377 dB`
  - exact `target_full = -0.467426 dB`
- near-real speech probe overall：
  - `-0.090764 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.086908 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.099820 dB`
- near-real `guodegang_absent_480s`：
  - `-0.057543 dB`

### `v5 cleancarve` synthetic absent family 本身

- `reports/eval/compare_v19_vs_v39_on_guodegang_absent_proxy_v5_cleancarve/summary.json`
- overall：
  - `+0.181394 dB`

这说明：

- 这次 metadata carve-out 并不是完全没打中目标；
- 它在 synthetic `v5 cleancarve` 这批自定义 clean absent 子集上，
  确实出现了正向提升。

### 相对 `v32` 的 `friend_speech_leak_followup_gate`

- 输出：
  - `reports/eval/compare_v19_vs_v39_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`
- `overall_pass = false`
- failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

同时也要注意：

- default floor：
  - `PASS`
- near-real speech probe overall floor：
  - `PASS`

也就是说：

- `v39` 不是全面崩；
- 它把 broad default / broad near-real overall 维持在 gate 容忍区间里；
- 但最关键的 friend-side exact 与 `guodegang anchor / absent` 两条 protection floor，
  仍然没有守住。

## 结论

`v39` 也不保留为新候选。

这次更准确的解释应写成：

- 把 absent-side 从 shared old rows 改成更窄的 metadata carve-out，
  的确能在 synthetic clean absent proxy 子集上看到正增益；
- 但这还不等于：
  - friend-side exact speech-leak 会一起回正；
  - 或 `guodegang anchor / absent` 两条 real floor 就能被守住；
- 因此当前 `v5 cleancarve` 更像是：
  - 一个方向更干净的 synthetic carve primitive；
  - 而不是已经可保留升级的 real-gate solution。

## 下一步建议

若继续自动推进，优先级应收紧为：

1. 不把 `v39` 的 synthetic cleancarve 局部转正误写成 real gate 已改善。
2. 不继续直接围绕当前 `v39` 的 metadata 上界继续细扫小数点权重。
3. 下一步若还做 absent-side protection，优先试：
   - 更贴近 near-real `guodegang_absent` 的保护代理；
   - 或进一步确认 `v5 cleancarve` 中哪些样本仍和 friend-side exact 冲突，
     再做更细粒度 carve-out；
   - 或引入一个不直接改写 shared target reconstruction 方向的保护 objective。
