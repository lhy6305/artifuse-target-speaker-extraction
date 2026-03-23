# 2026-03-23 `candidate_v7` low-buffer edge positioning

## 背景

上一轮已经确认：

- mixed ring `9`
  条样本里，
  最稳的分界
  不是：
  - 某个单字段 metadata
    阈值
- 而是：
  - `v66 > v64`
  - `v66 > v65`
    两条 buffer
    如何联动塌

同时也已经看到：

- `train_001006`
  仍挂在
  pure-signature `v67-top`
  组里；
- `train_001589`
  `train_001610`
  `train_001745`
  则已经落进
  `v65` drift
  解释带

但还缺最后一层：

- `train_001006`
  为什么还能算
  pure-signature low-buffer edge；
- 其余几条
  为什么虽然 metadata
  不一定已经完全跑远，
  但 margin
  已经先翻到 drift

## 本轮做法

先把已有
4-case 对照结果
保留下来：

- `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_case_contrast/summary.json`

再新增一层
reference-group positioning：

- 新脚本：
  - `scripts/eval/analyze_proxy_case_positioning.py`
- 新 summary：
  - `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_positioning/summary.json`

当前把 4 条 focus case：

- `train_001006`
- `train_001589`
- `train_001610`
- `train_001745`

分别放到 3 个 reference group
中间做定位：

- pure `v67` takeover edge `3`
  - `train_001079`
  - `train_001494`
  - `train_000697`
- pure-signature `v67-top 5`
  - `train_000216`
  - `train_000759`
  - `train_000799`
  - `train_001006`
  - `train_001639`
- `v65` drift `v67-top 4`
  - `train_000266`
  - `train_001589`
  - `train_001610`
  - `train_001745`

使用字段分两类：

1. metadata side
   - transient
   - cosine
   - target/reference duration
   - gain / offset
2. margin side
   - `v66 > v64`
   - `v66 > v65`
   - `v66 > v67`
   - `v64 > v67`

并对 focus case
命中的 reference group
自动做 leave-one-out，
避免把样本自己
拉回本组中心。

## 结果

### 1. `train_001006` 是当前 low-buffer ring 里唯一一条“metadata 位置”和“margin 状态”都还站在 pure-signature 侧的样本

`train_001006`
到三组中心的距离为：

- pure-signature `v67-top 5`
  - total `4.474274`
  - metadata `4.150747`
  - margin `1.670457`
- pure `v67` takeover edge
  - total `5.005685`
  - metadata `4.221869`
  - margin `2.689370`
- `v65` drift
  - total `5.236600`
  - metadata `4.496268`
  - margin `2.684316`

这说明：

- `train_001006`
  不是“已经进入 drift，
  只是还没翻完”的样本；
- 它当前仍然是：
  - pure-signature
    组里的 low-buffer edge

它偏离 pure-signature 中心
最大的几项，
主要是：

- target transient
  更高
- target transient share
  更高
- interference transient share
  更低
- reference
  更短
- gain
  更弱

但关键是：

- `v66 > v64 = +0.044802`
- `v66 > v65 = +0.109148`

两条 buffer
仍然都保持为正，
所以它只是“变薄”，
不是“已翻”。

### 2. `train_001589` 已经可以稳定写成 drift；它的 metadata 轨迹异质，但 margin 身份不再开放

`train_001589`
到三组中心的距离为：

- `v65` drift
  - total `4.311819`
  - metadata `4.171045`
  - margin `1.092780`
- pure `v67` takeover edge
  - total `4.424937`
  - metadata `3.946150`
  - margin `2.001992`
- pure-signature `v67-top 5`
  - total `4.799170`
  - metadata `4.300195`
  - margin `2.130812`

所以：

- total
  最近的是 drift
- margin
  更明显最近的是 drift
- 只有 metadata
  还保留一点
  向 pure `v67` edge
  靠拢的痕迹

这与上一轮结论一致：

- `train_001589`
  已经不该再被保留成
  pure edge
  的开放身份

### 3. `train_001610` 与 `train_001745` 都出现了“metadata 还靠 pure-signature，margin 已先倒向 drift”的 margin-first collapse

`train_001610`：

- pure-signature `v67-top 5`
  - total `4.194075`
  - metadata `2.767252`
- `v65` drift
  - total `4.388509`
  - metadata `4.184080`
  - margin `1.323814`
- pure-signature `margin = 3.151600`

`train_001745`：

- pure-signature `v67-top 5`
  - total `4.004559`
  - metadata `2.906215`
- `v65` drift
  - total `4.237308`
  - metadata `4.024652`
  - margin `1.325500`
- pure-signature `margin = 2.755070`

也就是说：

- 这两条
  从 total / metadata 位置看，
  还更像
  pure-signature ring
  里的成员；
- 但从 margin 状态看，
  已经明显更靠
  `v65` drift

因此当前更准确的解释不是：

- “它们已经先在 metadata 上
  整体跑到 drift 区”

而是：

- `v66 > v64`
  与
  `v66 > v65`
  的保护带
  可以先塌；
- metadata center
  的迁移
  反而是滞后的

### 4. 这 4 条 case 现在必须按“双轴”来写，不能再用单轴 nearest-group 强行贴标签

当前最稳的两轴是：

1. metadata position
   样本整体更靠哪一圈
2. margin state
   `v66 > v64`
   与
   `v66 > v65`
   是否已经进入 drift

落到 4 条 case 上：

- `train_001006`
  - metadata：pure-signature
  - margin：pure-signature
- `train_001589`
  - metadata：更杂，
    略偏 pure `v67` edge
  - margin：drift
- `train_001610`
  - metadata：pure-signature
  - margin：drift
- `train_001745`
  - metadata：pure-signature
  - margin：drift

所以真正的稳定结论是：

- low-buffer ring
  内部，
  drift 已经不是
  一个 metadata
  同质组；
- 但它已经是一个
  margin
  同质组

## 结论

1. `train_001006`
   当前仍应写成：
   - pure-signature low-buffer edge
   不是半个 drift。
2. `train_001589 / train_001610 / train_001745`
   虽然 metadata
   轨迹并不一致，
   但 margin
   已经共同进入：
   - `v66 > v65 <= 0`
     或接近翻转
   的 drift 解释带。
3. 因而当前 mixed ring
   的更窄主结论应更新为：
   - `v65` drift
     是 margin-first collapse；
   - metadata
     位置迁移
     可以滞后
4. 后续如果还继续推进，
   默认不再扩大样本面；
   应优先解释：
   - 为什么
     `train_001610`
     `train_001745`
     在 metadata
     还贴着 pure-signature ring
     时，
     margin
     已经先塌
   - 以及
     `train_001006`
     为什么还能保住
     最后一层
     `v66 > v65`
     buffer
