# 2026-03-19 `v38` absent-recon-wave + stronger friend-extra rebalance

## 背景

`v37` 已说明：

- `guodegang_absent_proxy_v3_strict`
  的问题不在 manifest coverage，
  而在 objective routing；
- 把它接到 `reconstruction_extra`
  的确比 `anchor transient-extra only` 更接近 real floor；
- 但 `v37` 的 absent-side only 配置会同时伤到：
  - exact `target_full`
  - near-real `speech_leak_like (0004)`

因此这轮不再继续放大 absent-only reconstruction，
而是做一条最小再平衡：

- absent-side 只保留更轻的 `waveform-only reconstruction_extra`
- 同时把 friend-side exact `interference_extra`
  明显加重

目标是验证：

- `v37` 的回退是不是主要因为 absent reconstruction 太重；
- 如果把 friend-side exact branch 提强，
  是否能把 exact / `0004-like speech-leak` 拉回，
  同时保住 `guodegang` 两条 floor。

## 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v38_v32_absentreconwave_friendextra_rebalance_ft1`

初始化：

- `v32`

manifest：

- train：
  - `data/synthetic/train_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
- val：
  - `data/synthetic/val_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`

说明：

- 这次不再沿用 `v37` 那份等价 union manifest；
- 直接使用 `v32` base manifest，
  避免把解释混入虚假的“扩样”因素。

loss 变化点：

- 保留 `v32` 的：
  - base transient
  - base interference
  - absent
  - `interference_extra = exact speech-leak 10 ids`
- 调整为：
  - `reconstruction_extra_waveform_weight = 0.01`
  - `reconstruction_extra_stft_weight = 0.0`
  - `reconstruction_extra_focus_sample_ids = guodegang_absent_proxy_v3_strict_all`
  - `interference_extra_weight = 0.03`
- 对照：
  - `v37` 是：
    - `reconstruction_extra_waveform_weight = 0.02`
    - `reconstruction_extra_stft_weight = 0.01`
    - `interference_extra_weight = 0.0075`

这次假设是：

- `STFT` 型 absent reconstruction
  更容易伤到 exact speech-leak；
- 如果只保留轻量 waveform reconstruction，
  再把 exact friend-side branch 提强，
  也许能把 trade-off 拉回。

## selector 命中

- train：
  - `reconstruction_extra = 51 / 97`
  - `interference_extra = 7 / 97`
- val：
  - `reconstruction_extra = 18 / 29`
  - `interference_extra = 3 / 29`

说明：

- `v38` 的 selector coverage
  与 `v37` / `v32` 一致；
- 这次变化只来自 loss 配比，
  没有 coverage 漂移。

## 结果

相对 `v19`：

- default：
  - `+0.017846 dB`
- exact proxy overall：
  - `-0.238433 dB`
- exact `target_full`：
  - `-0.582605 dB`
- near-real speech probe overall：
  - `-0.093675 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.082113 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.097188 dB`
- near-real `guodegang_absent_480s`：
  - `-0.045739 dB`

相对 `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_pass = false`
- failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

## 与 `v37` 的对照

`v38` 相对 `v37`：

- default 更好：
  - `+0.017846 dB` vs `+0.004330 dB`
- `guodegang_anchor_120s` 更好：
  - `-0.097188 dB` vs `-0.122504 dB`
- `guodegang_absent_480s` 更好：
  - `-0.045739 dB` vs `-0.051134 dB`

但同时：

- exact `target_full` 更差：
  - `-0.582605 dB` vs `-0.553167 dB`
- near-real `speech_leak_like (0004)` 也更差：
  - `-0.082113 dB` vs `-0.077866 dB`

这说明：

- 把 `interference_extra_weight`
  从 `0.0075` 拉到 `0.03`，
  并没有把 exact friend-side speech-leak 拉回来；
- 相反，它没有改变这条 trade-off 的方向：
  - default / `guodegang` 会略回升
  - 但 exact / `0004-like speech-leak`
    仍继续被压坏

## 结论

`v38` 也应直接判掉。

当前更准确的解释应升级为：

- 只要 `guodegang_absent_proxy_v3_strict`
  仍以当前这组 hard `target_full` 行的方式接入 `reconstruction_extra`，
  再去加大 friend-side `interference_extra_weight`
  并不能把 exact speech-leak side 拉回；
- 这说明当前冲突更像是：
  - absent reconstruction 本身就在改写 shared hard-speech region 的优化方向；
  - 而不是单纯“friend-side exact branch 权重还不够大”。

因此下一步若继续自动推进，
优先级应进一步收紧为：

1. 不继续围绕 `v37 / v38` 扫：
   - `interference_extra_weight`
   - 或当前这组 `reconstruction_extra` 权重配比
2. 后续若还做 absent-side protection，
   优先试：
   - 更细粒度的 absent proxy carve-out
   - 更贴近 real gate 的保护代理
   - 或避免直接作用于这批 shared hard `target_full` 行的 objective
