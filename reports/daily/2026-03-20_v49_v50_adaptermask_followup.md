# 2026-03-20 `v49 / v50` adapter-mask follow-up

## 背景

`v47 / v48` 已经把 prefix-freeze 路线的边界写清楚：

- 纯 ref-conditioning
  太保守，
  friend-side 接近守住，
  但 absent proxy 本体直接塌掉；
- 再放开 shared `mask_head`
  虽能恢复一点 output-side plasticity，
  但仍会在 `proxy_v7`
  回到正向之前，
  先把 friend-side 两条重新拖坏。

因此本轮不再继续扫：

- `trainable-module-prefixes`
  的小组合；

而是补一条更贴近当前假设的结构：

- 给模型增加一条
  zero-init 的
  `adapter_mask_head`
  残差分支；
- 让 `reconstruction_extra(proxy_v7)`
  只通过这条专属分支更新；
- base losses
  继续只看 shared base output，
  不再让 absent extra
  直接改写共享主输出。

## 工程补充

### `src/tse_prefix/models/stft_mask_baseline.py`

新增可选：

- `enable_adapter_mask_head`
- `adapter_mask_max_delta`

实现方式：

- shared `mask_head`
  仍输出 `base_mask`
- 若启用 adapter：
  - 额外生成
    `adapter_mask_delta`
  - 最终输出 mask 为：
    - `clamp(base_mask + delta, 0, 1)`
- `adapter_mask_head`
  最后一层零初始化，
  保证初始行为与旧模型一致

### `src/tse_prefix/pipeline/baseline_train.py`

`compute_losses(...)`
新增：

- `reconstruction_extra_prediction`

这样可以做到：

- base waveform / stft / transient / interference / absent
  都继续用 shared base prediction；
- 只有 `reconstruction_extra`
  用 adapter-combined prediction。

### `scripts/train/train_stft_mask_baseline.py`

新增：

- `--model-enable-adapter-mask-head`
- `--model-adapter-mask-max-delta`

并补了两个工程兼容：

1. 从旧 checkpoint 初始化时，
   允许 adapter 新参数缺失；
2. 当某个 batch
   对当前 trainable 子集没有梯度时，
   跳过 `backward / step`，
   不再把工程报错误记成实验失败。

## `v49 = adapter_mask_head only`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v49_v32_absent_adaptermask_v7_only_ft1`
- init：
  - `v32`
- manifest：
  - 继续复用 `v42`
    merged manifest
- model：
  - `enable_adapter_mask_head = true`
  - `adapter_mask_max_delta = 0.25`
- loss：
  - `reconstruction_extra_waveform_weight = 0.005`
  - `reconstruction_extra_focus_sample_ids = proxy_v7 all ids`
- trainable prefixes：
  - `adapter_mask_head`
- trainable parameter count：
  - `197,377 / 2,564,994`
  - `7.70%`

解释：

- `v49`
  是最干净的一版：
  - shared 主干完全保持 `v32`
  - 只有新加的 absent residual output branch
    在学

### 结果

relative to `v19`：

- default：
  - `+0.004926 dB`
- exact `target_full`：
  - `-0.406366 dB`
- near-real speech probe overall：
  - `-0.057841 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.048850 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.056997 dB`
- near-real `guodegang_absent_480s`：
  - `-0.015182 dB`
- `proxy_v7`：
  - `-1.542894 dB`

relative to `v32` gate：

- `overall_judgement = fail`
- `clear_fail_rules`：
  - `exact_target_full_gain_floor`
- `near_tie_rules`：
  - `speech_leak_like_gain_floor`
  - `guodegang_absent_floor`

### 裁决

`v49` 不保留。

这条实验最关键的信息是：

- 专属 adapter branch
  本身并不是完全没方向；
- 但当前这条
  simple output residual adapter
  远远不够：
  - absent proxy 本体没有被拉起；
  - 甚至在 `proxy_v7`
    上直接明显反向；
  - friend-side 也没被真正守住

## `v50 = same adapter, tighter max delta`

### 定义

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v50_v32_absent_adaptermask_v7_only_delta005_ft1`
- 与 `v49`
  相同，
  仅改：
  - `adapter_mask_max_delta = 0.05`

解释：

- 这条不是回到旧式微调；
- 而是对新结构补一个必要的安全边界检查：
  - 当前问题到底是
    branch 方向就不对；
  - 还是方向有一点对，
    但残差步子太大。

### 结果

relative to `v19`：

- default：
  - `+0.013945 dB`
- exact `target_full`：
  - `-0.323341 dB`
- near-real speech probe overall：
  - `-0.051803 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.042961 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.064364 dB`
- near-real `guodegang_absent_480s`：
  - `-0.013611 dB`
- `proxy_v7`：
  - `-1.082981 dB`

relative to `v32` gate：

- `overall_judgement = near_tie`
- `clear_fail_rules = []`
- `near_tie_rules`：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_absent_floor`

### 裁决

`v50` 仍不保留。

但它给了当前这条新结构一条明确边界：

1. 把 adapter 残差压小之后，
   friend-side 的确回到：
   - near-tie 级别
2. `v49`
   的严重反向，
   的确部分来自：
   - residual step 太大
3. 但即便把幅度压小，
   `proxy_v7`
   仍然明显负向：
   - `-1.082981 dB`
4. 这说明当前缺的已经不是：
   - 再调这条 simple adapter 的步长
   或 residual safety knob；
   而是：
   - 更强的 adapter 条件化
   - 或真正的 dual-head / branch-local output branch

## 当前阶段结论

`v49 / v50`
联合起来，已经把这条新结构线的结论写清楚：

1. `simple output residual adapter`
   不是完全没方向；
   压小残差后，
   friend-side 能回到 near-tie。
2. 但它仍然不能把 absent proxy 本体拉回正向。
3. 因此下一条默认不再继续扫：
   - `adapter_mask_max_delta`
   - 或 simple residual adapter 的小参数。
4. 下一条更合理的默认方向应升级成：
   - adapter-specific conditioning
   - 或真正的 dual-head / branch-local output branch
   而不是继续停在：
   - shared encoded feature
     上叠一个简单 residual mask head。

## 裁决摘要

- `v49`：
  - 不保留
  - 记为：
    - `simple adapter branch too weak / wrong-signed on proxy_v7`
- `v50`：
  - 不保留
  - 记为：
    - `smaller residual pulls friend-side back to near-tie`
    - `but still cannot recover absent proxy body`
