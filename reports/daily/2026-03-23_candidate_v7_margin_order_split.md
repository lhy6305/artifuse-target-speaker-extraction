# 2026-03-23 `candidate_v7` margin order split

## 背景

上一轮已经确认：

- current low-buffer ring
  的路径
  不是 metadata
  先整体迁到 drift
- 而是：
  - margin 先塌
  - metadata 后迁

但还差最关键的一层次序：

- `v66 > v64`
- `v66 > v65`

到底是哪一条
先真正越过 `0`，
哪一条只是先被磨到
接近 `0`

这一步如果不拆开，
就很难解释：

- 为什么
  `train_001610`
  已经能进 drift
- 而 `train_001745`
  又比它更深，
  走到了
  `v66 < v64`

## 本轮做法

新脚本：

- `scripts/eval/analyze_proxy_margin_order_split.py`

新 summary：

- `reports/eval/active_targetfull_clean_failboth_margin_order_split/summary.json`

当前直接读取：

- `reports/eval/active_targetfull_clean_failboth_margin_first_transition_axes/summary.json`

只拆两条关键 gap：

- `gap::v66>v64`
- `gap::v66>v65`

并对 3 条 focus case：

- `train_001006`
- `train_001610`
- `train_001745`

分别计算：

1. pure-signature -> drift
   路径上的
   zero-cross threshold
2. case 当前
   走到该 zero threshold
   的多少比例
3. 是否已经越零

## 结果

### 1. 两条 margin 的越零次序现在已经明确：`v66 > v65` 先过零，`v66 > v64` 更像后续的第二阶段深塌

当前两条 gap 的
zero-cross threshold
分别是：

- `v66 > v64`
  - zero-cross transition ratio
    = `1.123493`
- `v66 > v65`
  - zero-cross transition ratio
    = `0.818051`

这说明沿 pure-signature -> drift
路径前进时：

- `v66 > v65`
  会更早碰到 `0`
- `v66 > v64`
  会更晚碰到 `0`

所以当前更准确的时序应写成：

1. `v66 > v64`
   先被磨到接近 `0`
2. `v66 > v65`
   先真正翻负
3. 更深阶段里，
   `v66 > v64`
   才继续翻到负区

### 2. `train_001006` 还处在 pre-entry low-buffer edge；两条 gap 距离越零都只走了约三分之一

`train_001006`：

- `v66 > v64`
  - case value
    = `+0.044802`
  - progress to zero
    = `0.317728`
  - crossed zero
    = `false`
- `v66 > v65`
  - case value
    = `+0.109148`
  - progress to zero
    = `0.337545`
  - crossed zero
    = `false`

所以它仍然只是：

- pre-entry low-buffer edge

也就是说：

- 两条 buffer
  都已经明显变薄，
  但还远没到 drift
  的零点

### 3. `train_001610` 是当前最干净的 hinge entry：`v66 > v65` 已经翻负，而 `v66 > v64` 只差最后一小步

`train_001610`：

- `v66 > v64`
  - case value
    = `+0.001154`
  - progress to zero
    = `0.982427`
  - crossed zero
    = `false`
- `v66 > v65`
  - case value
    = `-0.051220`
  - progress to zero
    = `1.310871`
  - crossed zero
    = `true`

它现在的 stage
可以明确写成：

- `hinge_entry_v65_crossed_first`

这就是当前最窄的
drift 进入机制：

- `v66 > v64`
  已经几乎耗尽，
  但还没翻负
- `v66 > v65`
  先一步越过 `0`

因此：

- `train_001610`
  是当前最干净的
  “先由 `v65` 侧入侵，
  再等 `v64` 保护带彻底翻掉”
  样本

### 4. `train_001745` 已经进入 post-entry deeper stage；它不是简单复制 `train_001610`，而是多走了 `v66 > v64` 进一步翻负的那半步

`train_001745`：

- `v66 > v64`
  - case value
    = `-0.027470`
  - progress to zero
    = `1.418327`
  - crossed zero
    = `true`
- `v66 > v65`
  - case value
    = `-0.001907`
  - progress to zero
    = `1.011576`
  - crossed zero
    = `true`

它现在的 stage
可以明确写成：

- `post_entry_v64_deeper_than_v65`

也就是说：

- 相比 `train_001610`，
  `train_001745`
  不是简单“更坏一点”
- 而是：
  - `v66 > v65`
    只刚刚越零
  - 但
    `v66 > v64`
    已经继续深入负区

所以它才会呈现出：

- `v66 < v64`
- `v66 ≈ v65`

这类更深的塌缩形态

## 结论

1. 当前 low-buffer ring
   的 margin 次序已经可以固定成：
   - `v66 > v64`
     先被磨到近零
   - `v66 > v65`
     先实际翻负
   - 然后
     `v66 > v64`
     才在更深阶段翻负
2. `train_001610`
   是当前最干净的
   hinge-entry 样本；
   drift 进入
   首先由
   `v66 > v65`
   越零定义。
3. `train_001745`
   则是更深一层的
   post-entry 样本；
   它相对 `train_001610`
   多走的是：
   - `v66 > v64`
     从近零
     进一步翻成负值
4. `train_001006`
   仍应固定写成：
   - pure-signature low-buffer edge
5. 若继续推进，
   默认下一步应固定为：
   - 不再讨论
     drift 是否已进入
   - 而只解释：
     - 为什么
       `train_001745`
       会比
       `train_001610`
       多走这一步
     - 以及这一步
       是否主要由
       `v66 > v64`
       单边继续崩塌
       决定
