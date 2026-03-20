# 2026-03-20 `v63` dual-head `target_full` base-align + `branch_protect` follow-up

## 背景

`v61` 已说明：

- 只保护 `target_full` 子集
  是对的；
- `target_full`
  可从 `-0.95 / -0.98 dB`
  明显收回到
  `-0.369736 dB`；
- `0004`
  也收到 near-tie；
- `guodegang`
  没塌。

因此本轮直接执行
之前只保留为书面规格的：

- `v63 = target_full-only base-align`
  `+`
  `0004-like branch_protect guard`

本轮想回答的唯一问题是：

- 当 `target_full`
  与第二条 protect signal
  被拆成两条 selector 后，
  剩下这点 gap
  能不能被真正关掉。

## 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v63_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect0002_ft1`
- init：
  - `v32`
- dual-head：
  - `enable_branch_decoder_head = true`
- 仅训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- absent-side：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `focus = proxy_v7`
- protect A：
  - `interference_extra_base_align_weight = 0.02`
  - `focus = exact_targetfull_all`
- protect B：
  - `branch_protect_guard_sisdr_weight = 0.0002`
  - `focus = exact_nontargetfull_all`

## selector 命中与训练侧确认

- `interference_extra`
  selector 命中：
  - train `4 / 129`
  - val `1 / 37`
- `branch_protect`
  selector 命中：
  - train `3 / 129`
  - val `2 / 37`
- `train_branch_protect_guard_sisdr_loss`
  - `1.173397`
- `val_branch_protect_guard_sisdr_loss`
  - `3.488044`
- `train_interference_extra_base_align_l1`
  - `4.740740014850455e-06`
- `val_interference_extra_base_align_l1`
  - `1.4153738447930664e-05`

结论：

- 两条 protect
  都确实进了训练图；
- 这不是
  “第二 selector 没命中”
  的无效轮次。

## 结果

relative to `v19`：

- default：
  - `+0.133461 dB`
- exact proxy overall：
  - `+0.170221 dB`
- exact `target_full`：
  - `-0.145699 dB`
- near-real speech probe overall：
  - `-0.100990 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.072646 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.311379 dB`
- near-real `guodegang_absent_480s`：
  - `-0.114641 dB`
- `proxy_v7`：
  - `+1.460838 dB`

relative to `v32` 的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- near-tie：
  - `speech_probe_overall_floor`
- clear fail：
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`
- pass：
  - `default_stage2_delta_floor`
  - `exact_target_full_gain_floor`

## 与 `v61` 对照的关键信号

下面是根据已有 `v61`
与本轮 `v63`
结果做的直接对照推断：

- exact `target_full`
  从 `-0.369736 dB`
  收到 `-0.145699 dB`
  说明第二条 protect
  确实继续推了
  exact `target_full`
- 但 near-real `speech_leak_like (0004)`
  几乎没变好：
  - `v61 = -0.071034 dB`
  - `v63 = -0.072646 dB`
- broad near-real speech probe
  反而明显变差：
  - `v61 = -0.051933 dB`
  - `v63 = -0.100990 dB`
- `guodegang_anchor / absent`
  从 `v61`
  的正向保护
  一起翻成负向：
  - anchor
    `+0.069889 -> -0.311379 dB`
  - absent
    `+0.043306 -> -0.114641 dB`
- 同时 `proxy_v7`
  被继续放大：
  - `-0.029114 -> +1.460838 dB`

这说明：

- 新增的第二条 protect
  并没有在真实 near-real
  上形成
  `0004-like speech leak`
  的有效保护；
- 它更像是又一次把训练
  推向了
  absent / broad exact
  更强的一侧。

## 关键复盘：`exact_nontargetfull` 并不等于 `0004-like`

本轮额外检查了
`exact_nontargetfull`
这 5 个 ids 的 metadata。

结果很明确：

- `train_000405`
  - `target_clean_speech`
  - `target_absent_head`
- `train_001279`
  - `target_clean_speech`
  - `target_absent_head`
- `train_001491`
  - `target_clean_speech`
  - `target_absent_tail`
- `val_000096`
  - `target_clean_speech`
  - `target_absent_tail`
- `val_000297`
  - `target_clean_speech`
  - `target_absent_head`

也就是：

- 这条补集 selector
  本质上几乎全是
  `absent_head / absent_tail`
  行为；
- 它并不是
  “`0004-like speech leak` 的保守近似”；
- 更准确的解释应是：
  - `exact_all - targetfull_all`
    在当前数据里，
    主要选出来的是
    `nonfull absent-like`
    子集。

这与本轮结果是对得上的：

- exact `target_full`
  被继续推好；
- `proxy_v7`
  也被继续放大；
- 但 `0004-like`
  没有被真正修正；
- `guodegang`
  反而被重新打坏。

## 裁决

`v63` 不保留。

不是因为：

- dual protect plumbing
  没接上；
- 或者
  `branch_protect`
  没命中。

而是因为：

1. `exact_nontargetfull`
   这个 selector 假设本身就是错的。
2. 它保护到的主要不是
   `speech_leak_like (0004)`，
   而是
   `absent-like nonfull`
   行为。
3. 因而它会把：
   - exact `target_full`
   - `proxy_v7`
   往上推，
   却不能把
   near-real `0004`
   拉回正向，
   还会连带打坏
   `guodegang_anchor / absent`。

## 当前更新

本轮后，
当前 dual-head protect 线的新边界应改写为：

1. `target_full`-only `base-align`
   仍然是有效子结论。
2. 但第二条 protect selector
   不能再用：
   - `exact_all - exact_targetfull_all`
3. 下一步若继续这条线，
   应先重建一个
   真正对应
   `speech_leak_like (0004)`
   的第二 selector / proxy，
   而不是直接起 `v64`
   扫现有 guard weight。
