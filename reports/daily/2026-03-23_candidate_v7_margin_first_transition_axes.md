# 2026-03-23 `candidate_v7` margin-first transition axes

## 背景

上一轮已经把 low-buffer ring
压成了双轴定位：

- `metadata position`
- `margin state`

并确认：

- `train_001006`
  仍是
  pure-signature low-buffer edge
- `train_001610`
  `train_001745`
  虽然 total / metadata
  还更靠 pure-signature，
  但 margin
  已经更靠 drift

但还差最后一层量化：

- 这两条到底是
  “metadata 也已经走到 drift，
  只是 total 看起来还没翻”
- 还是：
  - metadata 迁移
    其实还没怎么走
  - 真正先走完的是
    margin collapse

## 本轮做法

新脚本：

- `scripts/eval/analyze_proxy_transition_axes.py`

新 summary：

- `reports/eval/active_targetfull_clean_failboth_margin_first_transition_axes/summary.json`

当前直接以上一轮 positioning summary
为输入：

- `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_positioning/summary.json`

把：

- source group
  固定为
  pure-signature `v67-top 5`
- target group
  固定为
  `v65` drift `v67-top 4`

再把 3 条 focus case：

- `train_001006`
- `train_001610`
- `train_001745`

分别投影到两条 transition axis：

1. metadata axis
2. margin axis

这里：

- `transition_ratio = 0`
  表示还停在 pure-signature center
- `transition_ratio = 1`
  表示已经走到 drift center
- `> 1`
  表示这条轴上
  已经超过 drift center

## 结果

### 1. `train_001006` 在 metadata 和 margin 两条轴上都还停在 pure-signature 侧；它不是“没翻完的 drift”

`train_001006`：

- metadata transition ratio
  = `-1.581300`
- margin transition ratio
  = `+0.051259`

这说明：

- metadata
  不只是没到 drift；
  它甚至比 pure-signature center
  还更偏 pure 一侧
- margin
  也只沿 pure -> drift
  路径前进了很小一段

同时它仍保有：

- `v66 > v64 = +0.044802`
- `v66 > v65 = +0.109148`

因此当前最准确的写法仍是：

- `train_001006`
  是 pure-signature
  组里的 low-buffer edge

### 2. `train_001610` 的 metadata 进度几乎仍停在 pure center，但 margin 已经超过 drift center；这是最干净的 margin-first collapse

`train_001610`：

- metadata transition ratio
  = `+0.004083`
- margin transition ratio
  = `+1.240782`

这几乎就是：

- metadata
  还停在 pure-signature center
- 但 margin
  已经走完整条
  pure -> drift
  路径，
  甚至略过头

它在 margin 轴上
最关键的两条推进是：

- `v66 > v64`
  field ratio
  = `1.103750`
- `v66 > v65`
  field ratio
  = `1.072359`

而当前实际值也已经是：

- `v66 > v64 = +0.001154`
- `v66 > v65 = -0.051220`

所以：

- `train_001610`
  不是 metadata
  先漂到 drift
  才把 margin 带翻；
- 恰恰相反，
  它是 metadata
  还没迁，
  margin
  已经先塌完

### 3. `train_001745` 的 metadata 只大约走了三分之一到 drift，但 margin 也已经基本走完整条路径

`train_001745`：

- metadata transition ratio
  = `+0.349352`
- margin transition ratio
  = `+1.046646`

这说明：

- 它的 metadata
  确实比 `train_001610`
  更往 drift
  方向走了一些；
- 但也只走到
  大约 `35%`
  左右，
  远没有完整迁到 drift center

相反，
margin 轴上它已经基本到位：

- `v66 > v64`
  field ratio
  = `1.593481`
- `v66 > v65`
  field ratio
  = `0.827521`
- `v64 > v67`
  field ratio
  = `0.943238`

对应实际值为：

- `v66 > v64 = -0.027470`
- `v66 > v65 = -0.001907`

所以：

- `train_001745`
  的情况不是
  “metadata 全部迁移后
  自然进入 drift”
- 而是：
  margin
  先进入 drift，
  metadata
  只部分跟上

### 4. 当前最窄的主结论已经可以固定成：`v65` drift 是一条 margin 先塌、metadata 后迁的路径

3 条样本现在非常清楚：

- `train_001006`
  - metadata：仍在 pure 侧
  - margin：仍在 pure 侧
- `train_001610`
  - metadata：几乎还在 pure center
  - margin：已超过 drift center
- `train_001745`
  - metadata：只走到 drift 路径的约三分之一
  - margin：已基本到 drift center

因此当前 mixed ring
内部更准确的路径描述是：

1. 先发生：
   - `v66 > v64`
   - `v66 > v65`
     的保护带塌缩
2. 再发生：
   - metadata center
     的不完全、异质迁移

## 结论

1. `train_001610`
   是当前最干净的
   margin-first collapse
   样本；
   metadata
   几乎还没走，
   margin
   已经走完。
2. `train_001745`
   也属于
   margin-first collapse，
   只是 metadata
   比 `train_001610`
   稍微多迁了一些。
3. `train_001006`
   仍不该写成
   drift；
   它是 pure-signature
   组内的
   low-buffer edge。
4. 若继续推进，
   默认下一步应固定为：
   - 不再问
     “哪些 metadata
     先把样本整体推到 drift”
   - 而改问：
     - `v66 > v64`
     - `v66 > v65`
       两条 margin
       到底哪一条先塌、
       哪一条决定
       `001610`
       和 `001745`
       的分叉
