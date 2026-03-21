# 2026-03-21 `v67` candidate_v4 union follow-up

## 背景

上一轮已经把
`candidate_v4_guardv66_by_v64`
的两个关键前提补齐：

1. 它是当前
   `v64 > v66 > v65`
   aggregate 约束下的固定点；
2. 它与当前
   `v42 / v66`
   active split
   几乎不重叠，
   所以如果只换 selector，
   基本等于没训练到这批 rows。

因此本轮不再继续搜
`candidate_v5`，
而是直接回答更关键的问题：

- 如果把 `candidate_v4`
  真正 union 进 active split，
  并沿用 `v66`
  的 dual-head + target_full base-align
  + branch_protect recipe，
  real gate
  会不会回正。

## 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v67_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_candv4union_0002_ft1`
- init：
  - `v32`
- train manifest：
  - `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
- val manifest：
  - `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
- absent-side reconstruction：
  - `proxy_v7 all ids`
- protect A：
  - `interference_extra_base_align_weight = 0.02`
  - `focus = exact_targetfull_all`
- protect B：
  - `branch_protect_guard_sisdr_weight = 0.0002`
  - `focus = candidate_v4_guardv66_by_v64_all`
- 其余 recipe
  与 `v66`
  保持一致：
  - dual-head
  - 只训练
    `branch_decoder_temporal_model`
    与 `branch_decoder_mask_head`

## 命中情况

这轮最重要的不是结果本身，
而是先确认：

- `candidate_v4`
  这次是否真的进了训练。

答案是：

- 是，而且不再是稀命中。

`v67` 的 selector metrics：

- train
  - `branch_protect = 33 / 161`
- val
  - `branch_protect = 10 / 47`

相对 `v66`：

- train：
  - `5 / 129 -> 33 / 161`
- val：
  - `2 / 37 -> 10 / 47`

因此这轮如果 real gate 仍不对，
已经不能再解释成：

- “新 rows 其实没被训练到”

## 结果

relative to `v19`：

- default：
  - `+0.148614 dB`
- exact `target_full`：
  - `-0.287388 dB`
- near-real speech probe overall：
  - `-0.106822 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.116563 dB`
- near-real `guodegang_anchor_120s`：
  - `+0.004550 dB`
- near-real `guodegang_absent_480s`：
  - `-0.068236 dB`
- `proxy_v7`：
  - `+0.835037 dB`

relative to `v32`
的 `friend_speech_leak_followup_gate`：

- `overall_judgement = fail`
- pass：
  - `default_stage2_delta_floor`
  - `exact_target_full_gain_floor`
  - `guodegang_anchor_floor`
- near-tie 但仍未过：
  - `speech_probe_overall_floor`
- clear fail：
  - `speech_leak_like_gain_floor`
  - `guodegang_absent_floor`

也就是：

- default
  比 `v66`
  更强；
- exact `target_full`
  也比 `v66`
  更强；
- 但真实 near-real
  的 `speech_leak_like`
  反而继续更差，
  同时把
  `guodegang_absent`
  重新打坏。

## `candidate_v4` 定向诊断

本轮额外把
`v67`
放回 shared search compare，
并只看
`candidate_v4_guardv66_by_v64`
那 `10` 条 val rows。

aggregate 排名变成：

- `v64 > v66 > v65 > v67 > baseline > v20 > v30 > v32 > v35 > v29 > v25 > v24`

关键数值：

- `v64 - v67 = +0.038179 dB`
- `v65 - v67 = +0.019218 dB`
- `v66 - v67 = +0.034271 dB`
- `v67` rank mean = `5.4`
- `samplewise extra constraint pass = 0 / 10`

对照 `v66`
在同一组 rows 上的旧结果：

- `v64 > v66 > v65`
- `v66 - v65 = +0.015052 dB`
- `v66` rank mean = `3.7`

这说明：

1. `candidate_v4`
   这批 rows
   不是“没吃到”；
2. 真 union 进去之后，
   `v67`
   反而在这批目标 rows 上
   被推到了：
   - `v66` 后面
   - `v65` 后面
3. 因而当前更该怀疑的是：
   - objective / proxy
     语义仍不对，
   - 或当前
     `branch_protect_guard_sisdr`
     对这批 rows
     的作用方向仍然 partial / mismatch，
   而不是 manifest coverage。

## 裁决

`v67` 记为：

- `closed_failed`

这条实验的价值不在于
它更接近 keep，
而在于它把一个关键歧义关掉了：

- 当前不是
  “`candidate_v4`
   因为没被训练到，
   所以 real gate
   没改善”
- 而是：
  - `candidate_v4`
    已经被真实吃进训练，
  - 但它把 default / exact / proxy_v7
    往上推的同时，
    仍然没有把真实
    `speech_leak_like (0004)`
    推向正确方向，
  - 还重新伤到了
    `guodegang_absent`

## 当前更新

本轮后，
这条分支的默认判断应改写为：

1. `candidate_v4`
   的 coverage 问题
   已经排除；
2. 继续沿
   “只补 union manifest / 只补 coverage”
   的方向推进，
   默认不再有信息增益；
3. 下一层若继续，
   默认不该再问：
   - “是不是没训到这批 rows”
   而应直接问：
   - `branch_protect` objective
     是否仍是错语义
   - 还是
     `candidate_v4`
     本体仍不够 hard，
     需要进一步做
     row-level semantic split

