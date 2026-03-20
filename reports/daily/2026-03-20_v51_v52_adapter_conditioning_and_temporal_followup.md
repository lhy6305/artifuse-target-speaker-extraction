# 2026-03-20 `v51 / v52` adapter conditioning and temporal follow-up

## 背景

`v49 / v50` 已经说明：

- simple residual `adapter_mask_head`
  不是完全没方向；
- 但即便把 `max_delta`
  压到很小，
  它也只能把 friend-side
  拉回 near-tie，
  仍拉不回 absent proxy 本体。

因此本轮不再继续扫：

- `adapter_mask_max_delta`
  这种 residual safety knob；

而是直接补两条更强的 branch-local 表达：

1. `v51`
   给 adapter 分支增加自己的 reference conditioning；
2. `v52`
   给 adapter 分支增加自己的 temporal model。

## 工程补充

### `src/tse_prefix/models/stft_mask_baseline.py`

adapter branch 新增可选：

- `adapter_conditioning_mode`
  - `none`
  - `ref_bias`
  - `ref_film`
- `enable_adapter_temporal_model`
- `adapter_gru_layers`

当前语义是：

- 若只启用 `adapter_mask_head`
  且不启用 adapter temporal model，
  它就是在 shared `encoded`
  上做 residual mask；
- 若启用：
  - `adapter_conditioning_mode`
  则 adapter 分支会额外吃 reference 条件；
- 若启用：
  - `adapter_temporal_model`
  则 adapter 分支会先经过自己的一套双向 GRU，
    再预测 residual mask。

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `--model-enable-adapter-temporal-model`
- `--model-adapter-gru-layers`
- `--model-adapter-conditioning-mode`

并把旧 checkpoint 初始化时允许缺失的新键扩展到：

- `adapter_condition_proj.*`
- `adapter_condition_scale.*`
- `adapter_condition_shift.*`
- `adapter_temporal_model.*`

## `v51 = adapter ref_film conditioning`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v51_v32_absent_adaptermask_reffilm_v7_delta005_ft1`
- init：
  - `v32`
- model：
  - `enable_adapter_mask_head = true`
  - `adapter_conditioning_mode = ref_film`
  - `adapter_mask_max_delta = 0.05`
- trainable prefixes：
  - `adapter_condition_scale`
  - `adapter_condition_shift`
  - `adapter_mask_head`
- trainable parameter count：
  - `329,473 / 2,697,090`
  - `12.22%`

解释：

- `v51`
  不再是：
  - simple output residual head；
- 它的 adapter 分支
  已经能用自己的 reference-conditioned feature
  去生成 residual mask。

### 结果

relative to `v19`：

- default：
  - `+0.015467 dB`
- exact `target_full`：
  - `-0.317694 dB`
- near-real speech probe overall：
  - `-0.051851 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.042935 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.064897 dB`
- near-real `guodegang_absent_480s`：
  - `-0.013696 dB`
- `proxy_v7`：
  - `-1.016036 dB`

relative to `v32` gate：

- `overall_judgement = near_tie`
- `near_tie_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_absent_floor`
- `clear_fail_rules = []`

### 裁决

`v51` 不保留。

重要结论是：

- 单纯把 adapter 分支补成：
  - `ref_film`
  条件化；
- 只能让它在 friend-side 上
  继续维持 near-tie；
- 但仍然没法把 `proxy_v7`
  从明显负向拉回。

这说明当前问题不只是：

- “adapter 分支没看到 reference”

而是：

- 这条分支即便看到了 reference，
  仍缺更本质的 branch-local 建模能力。

## `v52 = adapter temporal model`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v52_v32_absent_adaptergru_v7_delta005_ft1`
- init：
  - `v32`
- model：
  - `enable_adapter_mask_head = true`
  - `enable_adapter_temporal_model = true`
  - `adapter_gru_layers = 1`
  - `adapter_conditioning_mode = none`
  - `adapter_mask_max_delta = 0.05`
- trainable prefixes：
  - `adapter_temporal_model`
  - `adapter_mask_head`
- trainable parameter count：
  - `986,881 / 3,354,498`
  - `29.42%`

解释：

- `v52`
  已经不再是小 adapter；
- 它给 absent branch
  单独加了一套自己的双向时序模型，
  只是仍复用 shared `temporal_input`
  作为入口。

### 结果

relative to `v19`：

- default：
  - `+0.017187 dB`
- exact `target_full`：
  - `-0.310738 dB`
- near-real speech probe overall：
  - `-0.050701 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.041941 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.065335 dB`
- near-real `guodegang_absent_480s`：
  - `-0.013233 dB`
- `proxy_v7`：
  - `-0.876078 dB`

relative to `v32` gate：

- `overall_judgement = near_tie`
- `near_tie_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_absent_floor`
- `clear_fail_rules = []`

### 裁决

`v52` 仍不保留。

但它把当前边界继续写得更硬了：

1. 即便给 adapter branch
   单独的一层双向 GRU，
   它仍然只能把 friend-side
   推到 near-tie；
2. `proxy_v7`
   依然明显负向：
   - `-0.876078 dB`
3. 说明当前缺的已经不是：
   - 更大的 adapter 容量
   - 或更强一点的 adapter conditioning；
   而更像是：
   - 真正独立的 branch-local decoder / dual-head
   - 或独立输出语义，
     而不是在 shared main path 上再叠一条 residual branch。

## 当前阶段结论

`v51 / v52`
联合起来，已经把这条 adapter 路线的边界补完整：

1. simple residual adapter：
   - 不够。
2. reference-conditioned adapter：
   - 仍不够。
3. adapter-specific temporal model：
   - 仍不够。
4. 这些更强的 branch-local residual variants
   都只能把当前裁决压到：
   - `near_tie`
   而不是：
   - `pass`
   并且始终拉不回
   `proxy_v7` 本体。

因此下一条默认不再继续扫：

- adapter branch 的 conditioning 变体；
- 或 adapter branch 的 temporal 容量。

下一条更合理的默认方向应升级为：

- 真正独立的 dual-head / branch-local decoder；
- 或训练图级别的更强语义解耦，
  而不是继续在
  shared base path
  上叠 residual branch。

## 裁决摘要

- `v51`：
  - 不保留
  - 记为：
    - `adapter sees reference now, still cannot recover proxy_v7`
- `v52`：
  - 不保留
  - 记为：
    - `adapter gets its own temporal model, still only near-tie and proxy stays negative`
