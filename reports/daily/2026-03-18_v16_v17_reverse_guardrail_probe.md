# 2026-03-18 v16 v17 reverse guardrail probe

## 背景

上一轮 synthetic dual-proxy gate 已经固定下来：

- `anchor_proxy_v1` 相对 `v12` 不能回退；
- `guodegang_absent_proxy_v3_strict / v4_broad` 相对 `v12` 不能变差。

但仅有这条 gate，还不够直接给出下一条 objective。

因此本轮先做两步：

1. 在 `default` synthetic speech rows 里搜索能稳定把：
   - `v12 > v15 > v13 > v14`
   排出来的 metadata 子集；
2. 用该子集构造一条新的 reverse guardrail，再与 `absent_proxy_v3_strict` 联立成小预算 probe。

## 新的 reverse guardrail proxy

### 搜索

搜索输入：

- `v12`
- `v15`
- `v13`
- `v14`

输出：

- `reports/eval/synthetic_proxy_search_v12_v15_v13_v14_on_default/summary.json`

top order-pass 候选集中在同一类子集：

- `recipe = target_clean_speech`
- `interference_pool = speech_interference_clean_pool`
- `interference_gain_db >= q67 = -0.8906667`
- `target_transient_presence_minus_mid_db_mean >= q67 = -9.1790574`

代表性候选规模：

- `val = 9`
- 排序：
  - `v12 = +1.919239 dB`
  - `v15 = +1.779815 dB`
  - `v13 = +1.721242 dB`
  - `v14 = +1.638906 dB`

### 物化 manifest

新 manifest：

- `data/synthetic/train_manifest_v16_v12_reverse_guardrail_proxy_v1.jsonl = 39`
- `data/synthetic/val_manifest_v16_v12_reverse_guardrail_proxy_v1.jsonl = 9`

统计：

- 仅含：
  - `target_clean_speech`
  - `speech_interference_clean_pool`
- pattern 分布：
  - train：
    - `target_absent_head = 10`
    - `target_absent_tail = 8`
    - `target_full = 15`
    - `target_intermittent = 6`
  - val：
    - `target_absent_head = 3`
    - `target_absent_tail = 1`
    - `target_full = 5`
- `mean_overlap_ratio`
  - train：`0.797311`
  - val：`0.932174`

当前理解：

- 这不是新的 absent objective proxy；
- 它更像：
  - 一个“`v12` 相对 `v15/v13/v14` 的 reverse guardrail carve-out”。

## 联合 manifest

本轮把：

- `guodegang_absent_proxy_v3_strict`
- `v16_v12_reverse_guardrail_proxy_v1`

做去重并集，得到：

- `data/synthetic/train_manifest_v16_absent_proxy_v3_plus_reverse_guardrail_v1.jsonl = 90`
- `data/synthetic/val_manifest_v16_absent_proxy_v3_plus_reverse_guardrail_v1.jsonl = 27`

重叠：

- train overlap = `0`
- val overlap = `0`

## `v16 = legacy_transient_leakguard_probe_v16_v12_absent_proxy_v3_reverse_guardrail_v1_ft1`

### 配置

- warm-start：
  - `v12`
- manifest：
  - `absent_proxy_v3_strict ∪ reverse_guardrail_proxy_v1`
- 预算：
  - `epochs = 1`
  - `lr = 1e-5`
  - `global_steps = 23`

focused loss 拆成两路：

1. transient / interference：
   - `target_hard_speech`
   - `target_full`
   - `speech_interference_hard_pool`
   - `friend_hard_negative_segments`
   - `target_present_ratio >= 0.95`
   - `overlap >= 0.9`
2. absent：
   - `target_clean_speech`
   - `target_absent_head / tail / intermittent`
   - `speech_interference_clean_pool`
   - `interference_gain_db >= -0.8906667`

selector 命中：

- train：
  - transient = `51 / 90`
  - interference = `51 / 90`
  - absent = `24 / 90`
- val：
  - transient = `18 / 27`
  - interference = `18 / 27`
  - absent = `4 / 27`

### synthetic 结果

相对 `legacy_stage2`：

- default：
  - `+0.166572 dB`
- `anchor_proxy_v1`：
  - `+2.189812 dB`
- `absent_proxy_v3_strict`：
  - `+0.080743 dB`
- `absent_proxy_v4_broad`：
  - `+0.153673 dB`

相对 `v12`：

- default：
  - `-0.004540 dB`
- reverse guardrail proxy：
  - `-0.076261 dB`
- `anchor_proxy_v1`：
  - `+0.298964 dB`
- `absent_proxy_v3_strict`：
  - `-0.007883 dB`
- `absent_proxy_v4_broad`：
  - `-0.001475 dB`

### synthetic dual-proxy gate

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v16_v12_absent_proxy_v3_reverse_guardrail_v1_ft1_on_guodegang_absent_proxy_v3_strict/synthetic_dual_proxy_gate_vs_v12.json`

结果：

- `FAIL`

失败项：

- `absent_proxy_v3_strict`
- `absent_proxy_v4_broad`

解释：

- `v16` 已经不是 `v13 / v15` 那种明显偏向 anchor 的失败形态；
- 它更像：
  - anchor 仍在正向；
  - default 几乎与 `v12` 持平；
  - absent-side synthetic gate 只差最后极小一段。

但在当前口径下，它仍未过线，因此本轮不扩到 near-real。

## `v17 = legacy_transient_leakguard_probe_v17_v12_absent_proxy_v3_reverse_guardrail_v1_absw05_ft1`

### 配置变化

只改一项：

- `absent_weight`
  - `1.0 -> 0.5`

其余保持与 `v16` 相同。

### synthetic 结果

相对 `legacy_stage2`：

- default：
  - `+0.133105 dB`
- `anchor_proxy_v1`：
  - `+1.358277 dB`
- `absent_proxy_v3_strict`：
  - `+0.069376 dB`
- `absent_proxy_v4_broad`：
  - `+0.145847 dB`

相对 `v12`：

- default：
  - `-0.038008 dB`
- reverse guardrail proxy：
  - `-0.062989 dB`
- `anchor_proxy_v1`：
  - `-0.532572 dB`
- `absent_proxy_v3_strict`：
  - `-0.019250 dB`
- `absent_proxy_v4_broad`：
  - `-0.009301 dB`

### synthetic dual-proxy gate

输出：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v17_v12_absent_proxy_v3_reverse_guardrail_v1_absw05_ft1_on_guodegang_absent_proxy_v3_strict/synthetic_dual_proxy_gate_vs_v12.json`

结果：

- `FAIL`

失败项：

- `anchor_proxy_v1`
- `absent_proxy_v3_strict`
- `absent_proxy_v4_broad`

解释：

- 把 `absent_weight` 从 `1.0` 降到 `0.5`，并没有让这条路线自然过线；
- 相反，它把 `v16` 的近似平衡重新打回：
  - anchor floor 也丢了；
  - default 也重新回吐。

## 当前结论

1. 新的 reverse guardrail carve-out 是有效的：
   - 它能稳定刻画：
     - `v12 > v15 > v13 > v14`
2. `v16` 是本轮第一条真正接近 synthetic dual-proxy gate 的路线：
   - anchor 通过；
   - default 几乎持平；
   - absent `v3 / v4` 只分别差：
     - `0.007883 dB`
     - `0.001475 dB`
3. 但 `v16` 仍不保留，也不扩到 near-real。
4. `v17` 进一步说明：
   - 这条路线不能靠简单下调 `absent_weight` 来补最后一段；
   - 否则会先把 `anchor` 和 default 一起拉回去。

## 对下一步的影响

1. 当前不要把 `v16` 误写成“已经基本可晋升”。
2. 但它已经证明：
   - `absent_proxy_v3_strict + reverse_guardrail_proxy_v1`
   这条 objective 方向比 `v13 / v14 / v15` 更接近可训练。
3. 下一步若继续推进，优先考虑：
   - 固定 `v16` 这条 union manifest；
   - 继续改的是：
     - transient / interference 路的预算或 selector
     - 而不是继续下调 `absent_weight`
4. 在没有新证据前，不继续把：
   - `absent_weight 1.0 -> 0.5`
   当成默认搜索方向。
