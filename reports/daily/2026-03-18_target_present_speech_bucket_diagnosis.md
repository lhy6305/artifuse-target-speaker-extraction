# 2026-03-18 `target_present__speech` Bucket Diagnosis

## 本次目的

当前 near-real hard gate 已经把 objective-only 主缺口收敛到：

- `target_present__speech`

但在没有人耳听审的前提下，下一步最有价值的工作不是继续盲开 `v8`，而是先回答一个更具体的问题：

- 这个失败桶到底是因为：
  - target retention 不足
  - speech leak 增加
  - residual-heavy / over-suppression
  - 还是 bandwidth / transient 在拖后腿

如果这一步不拆清楚，再继续做泛化的 loss / selector 小扫点，大概率只会把不同症状搅在一起。

## 新增脚本

- `scripts/eval/diagnose_near_real_bucket_failures.py`

输入：

- 已存在 listening pack 下的：
  - `tradeoff_analysis/per_sample_pair_metrics.jsonl`
  - `bandwidth_analysis/per_sample_pair_metrics.jsonl`
  - `transient_analysis/per_sample_pair_metrics.jsonl`

输出：

- `bucket_diagnostics/<bucket_name>/summary.json`
- `bucket_diagnostics/<bucket_name>/per_sample_diagnosis.jsonl`

这版脚本不重新计算底层指标，而是做三件事：

1. 统一 blind 包里 `file_a / file_b` 的方向到：
   - `baseline_label`
   - `candidate_label`
2. 只抽取指定 bucket：
   - 当前默认 `target_present__speech`
3. 把 tradeoff / bandwidth / transient 三路证据合成样本级失败签名

## 本轮实跑范围

已在以下 near-real blind 包上实际运行：

1. `legacy_transient_leakguard_probe_v1`
2. `legacy_transient_leakguard_probe_v3_w0005`
3. `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
4. `legacy_transient_leakguard_probe_v5_absentguard_ft1`
5. `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`

对应输出目录均位于各 pack 下：

- `bucket_diagnostics/target_present__speech/`

## 先看桶内样本数

`target_present__speech` 其实只有 3 条样本：

1. `near_real_0003`
   - `target_plus_friend_speech`
2. `near_real_0004`
   - `target_plus_friend_speech`
3. `near_real_0006`
   - `target_plus_guodegang_speech`

这意味着当前主缺口并不是“很多 speech-only 样本平均都略差”，而是：

- 3 条关键样本在以不同方式卡住 hard gate。

## 样本级主结论

### 1. `near_real_0003`

这是最稳定暴露“over-suppression / residual trade-off”的样本。

在 `v1 / v3 / v4 / v7` 上，反复出现：

- `lost_target_capture`
- `lost_retention_minus_leak`
- `more_residual_heavy`

其中：

- `v1 / v3 / v7` 还会额外命中：
  - `more_transient_lossy`
- `v5` 则更像最重的 over-suppression 版本：
  - target capture 掉得更多
  - residual 也更重

当前解释：

- `near_real_0003` 的根因不是单纯 leak；
- 更像“为了压 speech 干扰，把 target 连同高频瞬态一起压掉了”。

### 2. `near_real_0004`

这是最稳定暴露“speech leak trade-off”的样本。

在 `v1 / v3 / v4 / v7` 上，最一致的失败签名是：

- `lost_retention_minus_leak`
- `more_interference_leaky`

其中：

- `v1` 还会额外带：
  - `lost_target_capture`
  - `more_residual_heavy`
- `v5` 不再是 leak 问题，而是转成：
  - `lost_target_capture`
  - `more_residual_heavy`

当前解释：

- `near_real_0004` 不是“保高频瞬态”就能自然修好的点；
- 它更像是：
  - 目标在
  - 干扰 speech 也在
  - 模型一旦想保留更多目标，就容易把 speech leak 一起放回来。

### 3. `near_real_0006`

这是最接近“纯 transient loss”样本的点。

在 `v1 / v3 / v4 / v5 / v7` 上，都会反复命中：

- `more_transient_lossy`

但它和 `0003 / 0004` 最大的不同在于：

- 到 `v7` 时，它已经：
  - 不再更 residual-heavy
  - 不再更 interference-leaky
  - 反而在 `retention_minus_leak` 上赢过 `legacy_stage2`
- 它仍然 fail 的主要原因，只剩：
  - transient loss

当前解释：

- `near_real_0006` 已不再是 leak / residual 的综合问题；
- 它更像“在 external speech 干扰下，高频瞬态和 presence band 还在被吃掉”。

## 候选间的阶段性比较

### `v1`

`target_present__speech` 的失败更像：

- residual-heavy
- retention-minus-leak 回退
- 并夹带一部分 transient loss 与 speech leak

### `v3_w0005`

相对 `v1` 收回了一部分 residual-heavy，但代价是：

- 3 条样本全部继续输 `retention_minus_leak`
- 3 条样本全部继续更 interference-leaky

### `v4_speechfocus_ft1`

和 `v3` 很接近，说明：

- `speech-only selector` 没有把这个桶的根因拆开

### `v5_absentguard_ft1`

把问题从 leak 转成了更重的：

- target capture 丢失
- over-suppression

因此它不是修复 `target_present__speech` 的主方向。

### `v7`

是当前最值得保留的 sample-level 进展，因为它已经把 3 条样本分成了两类：

1. `near_real_0006`
   - 基本只剩 transient loss
2. `near_real_0003`
   - 仍是 residual-heavy + transient
3. `near_real_0004`
   - 仍是 speech leak trade-off

也就是说，`v7` 首次把这个桶里的问题拆得更干净了：

- 不再是三条都一起 leak / residual / transient 全部混着输；
- 而是开始分化成更可解释的子问题。

## 当前更新后的结论

现在可以把 `target_present__speech` 明确地改写成：

- 不是 1 个 bucket 失败；
- 而是 3 个样本、3 种机制在共同卡 gate。

对应地：

1. `near_real_0003`
   - 主症状：over-suppression / residual-heavy + transient loss
2. `near_real_0004`
   - 主症状：speech leak trade-off
3. `near_real_0006`
   - 主症状：transient loss

这也是为什么：

- `v3 / v4` 修不掉；
- `v5` 会越修越压；
- `v7` 虽然更好，但仍未整体过 gate。

## 对下一步的约束

在没有人工听审的前提下，当前最有价值的下一步不应是再开一条“泛化 loss / selector 扫点”，而应先做：

1. 把 `0003 / 0004 / 0006` 这三类失败形态映射回 synthetic / objective 训练可控项；
2. 明确区分：
   - residual/over-suppression 子问题
   - speech leak 子问题
   - transient 子问题
3. 再决定下一条单实验到底该优先修哪一个。

如果只允许继续推进一条 objective-only follow-up，那么当前最合理的基座仍是：

- `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`

但它的下一步目标应从“继续整体更强”改成一句更窄的话：

- 优先修 `near_real_0006` 这类 transient-only 回退，同时不能把 `near_real_0004` 再推回 speech leak。

原因是：

- `0006` 已经是最单一、最可拆的失败点；
- 而 `0003` 与 `0004` 目前仍分别对应两种不同 trade-off，贸然用一个统一损失去推，很可能再次互相打架。
