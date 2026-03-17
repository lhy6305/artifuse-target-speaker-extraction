# 2026-03-18 Near-Real Hard Gate

## 本次目的

在 `2026-03-18_near_real_tradeoff_bucketization.md` 之后，当前 near-real 的判断已经可以明确落到三个关键桶：

1. `target_present__speech`
2. `target_present__none`
3. `target_absent__speech`

但如果这些结论仍只存在于日报文字里，后续很容易再次退回到：

- 看整包均值
- 看整包计数
- 然后重复讨论“这个 candidate 看起来整体像还可以”

因此本轮把这三个桶的放行条件正式固化成一个可直接复用的 hard gate 脚本。

## 新增脚本

- `scripts/eval/gate_near_real_tradeoff.py`

输入：

- 某个 near-real blind 包的：
  - `tradeoff_analysis/summary.json`

默认基线：

- `legacy_stage2`

默认 gate 规则：

### 1. `target_present__speech`

candidate 必须同时满足：

- `better_retention_minus_leak_label` 不输给 baseline
- `more_interference_leaky_label` 不比 baseline 更差
- `more_residual_heavy_label` 不比 baseline 更差

### 2. `target_present__none`

candidate 必须满足：

- `more_residual_heavy_label` 不比 baseline 更差

### 3. `target_absent__speech`

candidate 必须满足：

- `more_interference_leaky_label` 不比 baseline 更差

大白话讲，这个 gate 的含义就是：

- speech-only target-present 不能继续输；
- raw-only 不能继续被压坏；
- target-absent speech 至少要保住当前 suppression 信号。

## 本轮实跑对象

已实际运行：

1. `legacy_transient_leakguard_probe_v1`
2. `legacy_transient_leakguard_probe_v3_w0005`
3. `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
4. `legacy_transient_leakguard_probe_v5_absentguard_ft1`

对应产物：

- 各包下的：
  - `tradeoff_analysis/gate_summary.json`

## Gate 结果

### `legacy_transient_leakguard_probe_v1`

结果：

- `overall_pass = false`
- failed buckets:
  - `target_present__speech`
  - `target_present__none`

当前含义：

- `v1` 仍是当前最强 objective-only 候选；
- 但它没有通过 hard gate；
- 主要卡在：
  - speech-only target-present 仍输给 `legacy_stage2`
  - raw-only 仍更 residual-heavy

### `legacy_transient_leakguard_probe_v3_w0005`

结果：

- `overall_pass = false`
- failed buckets:
  - `target_present__speech`

当前含义：

- `v3` 确实收回了 raw-only side effect；
- `target_absent__speech` 也没丢；
- 但 speech-only target-present 仍没有修好。

这也把 `v3` 的定位进一步压实成：

- “保守副作用锚点”
- 而不是“下一主候选”

### `legacy_transient_leakguard_probe_v4_speechfocus_ft1`

结果：

- `overall_pass = false`
- failed buckets:
  - `target_present__speech`

当前含义：

- `v4` 和 `v3` 一样，没有伤 raw-only；
- 也保住了 `target_absent__speech`
- 但它最该修的 speech-only target-present 仍然没修好

因此这条线继续支持原判断：

- `speech-only selector` 不是根因解。

### `legacy_transient_leakguard_probe_v5_absentguard_ft1`

结果：

- `overall_pass = false`
- failed buckets:
  - `target_present__speech`
  - `target_present__none`

更细一点地看：

- `target_present__speech`
  - 它已经不再卡在：
    - `better_retention_minus_leak`
    - `more_interference_leaky`
  - 它只卡在：
    - `more_residual_heavy`
- `target_absent__speech`
  - 它是四条线里 suppression 最强的一条

当前含义：

- `v5` 确实抓住了 absent suppression 这部分有效信号；
- 但它的副作用仍然会把：
  - speech-only target-present
  - raw-only
  一起推向更 residual-heavy

## 当前更新后的结论

经过 hard gate 之后，当前仓库的 objective-only 候选可以更明确地解释成：

1. `v1`
   - 主基座
   - 但还没过 gate
2. `v3_w0005`
   - 最像“副作用回收版”
   - 但仍过不了 `target_present__speech`
3. `v4_speechfocus_ft1`
   - 再次证明 `speech-only selector` 不是根因解
4. `v5_absentguard_ft1`
   - 证明 absent suppression 机制成立
   - 但 residual-heavy 副作用仍不可接受

## 对下一步的约束

现在如果还要继续做 objective-only 小步 follow-up，方向已经进一步收窄成：

1. 继续以 `legacy_transient_leakguard_probe_v1` 作为主基座；
2. 把 `legacy_transient_leakguard_probe_v3_w0005` 作为 raw-only / side-effect 锚点；
3. 新候选至少要同时做到：
   - 不再输 `target_present__speech`
   - 不再伤 `target_present__none`
   - 不丢 `target_absent__speech`

这相当于把下一步问题改写成一句非常具体的话：

- 不是“再找一个整体更强的 candidate”；
- 而是“找一个能保住 `v5` 那部分 absent suppression，同时不要再像 `v1` 一样压坏 raw-only，也不要继续像 `v3/v4` 一样输在 speech-only target-present 的小步版本”。
