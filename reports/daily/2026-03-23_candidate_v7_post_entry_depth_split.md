# 2026-03-23 `candidate_v7` post-entry depth split

## 背景

上一轮已经把
low-buffer ring
内部的 margin 次序
拆清成：

1. `v66 > v64`
   先被磨到近零
2. `v66 > v65`
   先越零
3. 更深阶段里，
   `v66 > v64`
   才继续翻负

因此当前更窄的问题
只剩一个：

- 为什么
  `train_001745`
  会比
  `train_001610`
  多走出：
  - `v66 < v64`

也就是：

- 在两者都已进入 drift
  之后，
  到底是哪一侧
  继续塌，
  把 `001745`
  推到了更深阶段

## 本轮做法

这一步不再补新分析脚本，
直接复用已有：

- `scripts/eval/analyze_proxy_group_split.py`

把两个 singleton group
显式物化为：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_hinge_entry_v65_crossed_first_train.txt`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_post_entry_v64_deeper_than_v65_train.txt`

再输出：

- `reports/eval/active_targetfull_clean_failboth_post_entry_depth_split/summary.json`

当前只对比：

- hinge entry
  - `train_001610`
- deeper post-entry
  - `train_001745`

字段仍限定在：

- transient
- cosine
- target/reference duration
- gain / offset
- 以及
  `v20 / v24 / v64 / v65 / v66 / v67`
  的 samplewise ranking

## 结果

### 1. `train_001745` 比 `train_001610` 更深，并不是因为 `v65` 继续把 `v66` 拉得更低；相反，额外塌掉的是剩余的 `v64` buffer

pairwise delta
显示：

- `v66 - v64`
  从
  `+0.001154`
  变成
  `-0.027470`
  额外下掉
  `0.028624 dB`
- 但
  `v66 - v65`
  从
  `-0.051220`
  变成
  `-0.001907`
  反而回升了
  `0.049313 dB`

所以：

- `train_001745`
  的更深阶段
  不是
  `v65`
  进一步压穿
  `v66`
- 而是：
  - 剩下那层
    `v64`
    保护带
    被继续单边打穿

这也是为什么
它最终会呈现：

- `v67 > v64 > v65 > v66`

而不是简单复制
`train_001610`
的：

- `v67 > v65 > v66 > v64`

### 2. 从对 `v67` 的相对位置看，`train_001745` 的额外深度更像“整体一起更差，但 `v64` 没有像 `v65` 那样同步继续坏到更深”，于是剩余排序改写成 `v64` 抬头

相对 `train_001610`，
`train_001745`
还有：

- `v66 - v67`
  更差
  `0.096991 dB`
- `v64 - v67`
  更差
  `0.068367 dB`
- 但
  `v66 - v65`
  没有继续恶化，
  反而更接近 `0`

这说明：

- deeper stage
  不是
  `v65`
  一路继续把
  `v66`
  往下压
- 而是：
  - `v66`
    和 `v65`
    基本一起坏掉
  - 同时
    `v64`
    还保住了一点相对顺位
  最终把：
  - `v66 < v64`
    这件事
    单独放大出来

### 3. 在这对样本内部，把 `001745` 推向更深 `v64` collapse 的不是“更强 gain”，而是一组更偏 early-overlap、transient-richer、longer-reference 的组合

`hinge - deeper`
的 metadata delta
为：

- `reference_duration_sec = -0.39`
  说明 `001745`
  reference 更长
- `interference_gain_db = +2.544`
  说明 `001745`
  gain 更弱
- `interference_start_offset_sec = +0.151`
  说明 `001745`
  overlap 更早
- `interference_transient_mean = -4.262`
  说明 `001745`
  interference transient
  更高
- `interference_transient_share = -0.0509`
  说明 `001745`
  interference transient share
  更高
- `target_transient_mean = -4.700`
  说明 `001745`
  target transient
  也更高
- `target_transient_share = -0.0845`
  说明 `001745`
  target transient share
  也更高
- `cosine = -0.0129`
  说明 `001745`
  cosine
  略更高

因此在这对样本里，
把 `v64` 剩余 buffer
继续打穿的，
更像是这样一包组合：

- 更早 overlap
- 更长 reference
- 更高 target / interference transient
- 更弱 gain

这是一个条件性结论：

- 这里只对
  `001610`
  和
  `001745`
  这对 post-entry split
  成立；
- 不能把它误写成
  当前全 ring
  的单字段规律

### 4. 当前最窄主结论已经可以固定成：post-entry 之后，深度分叉主要看 `v64` buffer 是否继续单边崩塌，而不是 `v65` takeover 是否继续加深

对这对样本来说：

- `train_001610`
  已经完成：
  - `v66 > v65`
    先越零
  但：
  - `v66 > v64`
    还停在零线之上
- `train_001745`
  则额外完成：
  - `v66 > v64`
    继续翻到负区
  同时：
  - `v66 > v65`
    其实只刚刚越零

所以 post-entry
的下一层深度判断
不该再写成：

- `v65`
  继续 takeover

而应写成：

- `v64`
  剩余保护带
  是否还会继续单边塌

## 结论

1. `train_001745`
   比 `train_001610`
   更深，
   主要不是因为
   `v65`
   再进一步压低
   `v66`；
   而是因为：
   - `v64`
     剩余 buffer
     被继续打穿
2. 在这对样本里，
   与更深 `v64` collapse
   同步出现的
   是一组组合信号：
   - 更早 overlap
   - 更长 reference
   - 更高 target / interference transient
   - 更弱 gain
3. 当前最合理的下一步，
   如果还继续推进，
   应固定成：
   - 不再扩大样本面
   - 只解释
     `v64`
     为什么在
     `001745`
     上失去最后 buffer
   - 并检查这一步
     是否能在更窄的
     ring 内
     再找到同型 row
