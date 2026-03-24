# 2026-03-24 `candidate_v7` `v65` sink lowshare rotation terminal route priority

## 背景

上一轮已经把
`000664`
这一步
正式定型成：

- low-share `v64_only` rotation hub

而不是：

- 还在等待
  tight companion
  的 pocket center

同时，
我们也已经知道
它附近最关键的
三条 downstream 方向
分别是：

- `000697`
  = pre singleton offshoot
- `001543`
  = sink branch
- `001745`
  = post-entry `v64`-deeper branch

但到这一步，
还有一个
必须继续压实的点：

1. 这三条 downstream 方向里，
   哪一条
   才是
   `000664`
   的主干终向
2. `000117 / 001725 / 001006`
   这批
   sink-facing shell
   到底是在：
   - 真正沿主干
     走向 sink
   - 还是只是
     被两端都 crossed
     的 branch
     吸过去

如果这个问题
不补，
当前口径里
就仍会留下一个
不够收紧的地方：

- `000664`
  虽然已经是 fanout hub，
  但
  “主干往哪边走”
  还没有被正式排序

所以本轮
只继续回答：

1. `000664`
   的 terminal continuation
   默认应先写成
   哪一侧
2. `000697`
   和
   `001745`
   为什么只能算
   side exit

## 本轮做法

这一步仍然只做
旧 rows 重路由，
不加新训练。

本轮新落两份 summary：

1. `000664 -> 001543`
   二元 terminal positioning
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_downstream_terminal_positioning/summary.json`
2. `000664 -> 001543`
   transition axes
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000664_to_sink_terminal_axes/summary.json`

本轮只保留
最窄的 terminal frame：

- `lowshare_v64only_rotation`
  = `000664`
- `v65_sink_singleton`
  = `001543`

focus case
直接放：

- `000117`
- `001725`
- `001006`
- `000697`
- `001745`
- `000759`
- `001639`

也就是：

- 先在
  最窄的
  `000664 -> 001543`
  二元 frame
  下，
  看这几条 row
  各自贴向哪一边
- 再看它们在
  source -> target
  transition 上
  是不是同向前进

## 结果

### 1. `000117 / 001725 / 001006` 在最窄的 terminal frame 里都稳定贴向 `001543`，所以 `000664` 的主干默认应先写向 sink

先看
`pre000664_downstream_terminal_positioning`。

把 reference
只收成：

- `000664`
- `001543`

以后，
三条
sink-facing shell
的最近 group
都稳定是：

1. `000117`
   - `nearest_reference_group = v65_sink_singleton`
   - `distance_margin_vs_second_best = 0.6913560218408357`
2. `001725`
   - `nearest_reference_group = v65_sink_singleton`
   - `distance_margin_vs_second_best = 0.5499421213856062`
3. `001006`
   - `nearest_reference_group = v65_sink_singleton`
   - `distance_margin_vs_second_best = 0.7971237092267431`

这件事的意义
和上一轮
已经不一样了：

- 上一轮
  只是说
  它们在多路 frame
  里
  更像 sink-facing shell
- 这一步
  则是在最窄的
  `000664 -> 001543`
  terminal frame
  下，
  它们仍然稳定贴向
  `001543`

也就是说：

- `000664`
  这条 route
  的默认主干
  不应先写向
  `000697`
  或
  `001745`
- 而应先写成：
  - 经过 sink-facing shell
  再去
    `001543`

### 2. 这三条 shell row 里，`000117` 是当前最平衡的 preterminal shell；`001725 / 001006` 也朝 sink 走，但各自带着不同偏斜

再看
`pre000664_to_sink_terminal_axes`，
把 source
固定成：

- `000664`

把 target
固定成：

- `001543`

当前三条 shell row
的双轴进度是：

1. `000117`
   - metadata-axis
     `transition_ratio = 0.637658941183893`
   - margin-axis
     `transition_ratio = 0.42130385600569453`
   - residual
     也最稳：
     - metadata `2.39409668384302`
     - margin `1.263508394865997`
2. `001725`
   - metadata-axis
     `transition_ratio = 0.6921624832100801`
   - margin-axis
     `transition_ratio = 0.018168134003235085`
3. `001006`
   - metadata-axis
     `transition_ratio = 0.6111003507701834`
   - margin-axis
     `transition_ratio = 1.2159720790739323`

这说明：

- `000117`
  当前最像
  一条平衡地
  落在
  `000664 -> 001543`
  主干上的
  preterminal shell
- `001725`
  metadata
  已经明显向 sink
  走过去，
  但 margin
  还没真正开始
  sink-side collapse
- `001006`
  则相反，
  margin
  走得更快，
  但 metadata
  带着更多噪声

所以：

- 当前不需要
  把这三条
  再压成单一 twin
- 但已经可以固定写成：
  - 它们共同属于
    `000664 -> 001543`
    主干上的
    sink-facing shell
  - 其中
    `000117`
    是当前最平衡的
    preterminal shell

### 3. `000697` 不能算 terminal continuation；它虽然还贴着 `000664`，但在 `000664 -> 001543` 轴上 margin 已经反向

在同一个
二元 terminal frame
里，
`000697`
最近的 group
稳定还是：

- `lowshare_v64only_rotation`
  (`000664`)
- `distance_margin_vs_second_best = 0.5850783086561098`

也就是：

- `000697`
  不是往
  `001543`
  主干上贴
- 它仍然更贴着
  `000664`
  本身

transition axes
里，
这一点更清楚：

- metadata-axis
  `transition_ratio = 0.4346663956577011`
- 但
  margin-axis
  `transition_ratio = -0.1212044061558796`

关键是：

- `gap::v66>v65`
  这条
  对 sink 最关键的 gap，
  在
  `000697`
  上
  已经明确
  反向：
  - `field_transition_ratio = -0.7445337154633864`
  - `path_direction_match = false`

再加上
它最突出的
metadata 偏斜
仍然是：

- `target_duration_sec`
  - `field_transition_ratio = -10.999999999999993`

这就把口径
彻底收紧了：

- `000697`
  不是
  `000664`
  的 terminal continuation
- 它虽然仍从
  `000664`
  这条 archetype
  分出来，
  但主导它的
  不是 sink 方向
  的 terminal collapse，
  而是那条
  long-duration
  pre offshoot

### 4. `001745` 也不能算 terminal continuation；它在二元 frame 里会被吸到 sink 侧，但真正走的是 `v64`-deeper pocket

在
`000664 / 001543`
这两个 group
组成的
极窄 frame
里，
`001745`
最近的 group
确实是：

- `v65_sink_singleton`
  (`001543`)
- `distance_margin_vs_second_best = 1.3379843295594291`

但这一点
不能直接写成：

- `001745`
  是更深 sink

因为看
transition axes，
它虽然：

- metadata-axis
  `transition_ratio = 0.7007623815776733`
- margin-axis
  `transition_ratio = 1.2252490006279915`

可真正的分叉
落在：

- `gap::v66>v64`
  - `field_transition_ratio = -52.997237569060886`
  - `path_direction_match = false`

而它自己的 key gaps
也已经表明：

- `v66_minus_v64 = -0.027469635009765625`
- `v66_minus_v65 = -0.0019073486328125`

也就是说：

- `001745`
  之所以会在
  二元
  `000664 / 001543`
  frame 里
  被吸向 sink 侧，
  只是因为
  它也已经 both-crossed
- 但它真正继续加深的
  是：
  - `v64`
    那一侧

所以：

- `001745`
  只能继续记成
  post-entry `v64`-deeper
  side exit
- 不能写成
  `000664`
  到 sink 的
  main terminal continuation

### 5. `000759` 和 `001639` 也都不是 terminal 主干；前者还停在 upstream bridge，后者则是 noisy fallback

同一套 terminal frame
里：

- `000759`
  最近仍是
  `000664`
  - margin
    `0.6301020675737643`
- `001639`
  也最近
  `000664`
  - margin
    `0.36981374442176573`

而它们在
transition axes
里也都不稳：

- `000759`
  - metadata-axis
    `0.45314814740348`
  - margin-axis
    `-0.06815992952912218`
- `001639`
  - metadata-axis
    `0.18593211579361985`
  - margin-axis
    `1.6348777539654205`
  - residual
    很大：
    - metadata `3.421063556665944`
    - margin `5.57729608961609`

这说明：

- `000759`
  还停在
  hinge-to-rotation bridge
  那一边，
  没有真正进入
  sink terminal path
- `001639`
  则更像一条
  noisy fallback，
  不适合再被写成
  terminal support

### 6. 到这一步，`000664` 的下游优先级已经可以正式排序：主干先去 sink，`000697 / 001745` 都只算 side exit

把这一步
和上一轮
合起来后，
`000664`
这条线
当前已经可以改写成
一个有主次的 fanout：

1. upstream
   - `001610`
     = outer-anchor-facing hinge-entry shadow
2. rotation node
   - `000664`
     = low-share `v64_only` rotation hub
3. main terminal trunk
   - `000117 / 001725 / 001006`
     = sink-facing shell
   - `001543`
     = sink terminal
4. side exit A
   - `000697`
     = pre singleton offshoot
5. side exit B
   - `001745`
     = post-entry `v64`-deeper pocket
6. upstream loose support
   - `000759`
     = broad bridge
   - `001639`
     = noisy fallback

所以后续
默认不再把：

- `000697`
- `001745`

和
`001543`
并写成：

- `000664`
  fanout 里
  三条并列的 terminal continuation

而应写成：

- 主干默认先去
  sink-facing shell
  再到
  `001543`
- `000697 / 001745`
  都只是
  从
  `000664`
  分出去的
  side exit

## 结论

本轮把
`000664`
这条 low-share rotation
的 downstream 优先级
正式排出来了：

1. `000117 / 001725 / 001006`
   在最窄的
   `000664 -> 001543`
   terminal frame
   里都稳定贴向
   `001543`，
   所以
   `000664`
   的主干默认应先写向：
   - sink-facing shell
   - 再到
     `001543`
2. 其中
   `000117`
   当前是
   最平衡的
   preterminal shell；
   `001725`
   更偏 metadata-side，
   `001006`
   更偏 margin-side
3. `000697`
   虽然仍贴着
   `000664`，
   但在
   `000664 -> 001543`
   轴上
   margin
   已经反向，
   所以只能继续记成：
   - pre singleton offshoot
4. `001745`
   虽然在二元 frame
   里会被吸到 sink 侧，
   但真正继续加深的是：
   - `v64`
     那一侧
   所以它只能继续记成：
   - post-entry `v64`-deeper branch

所以当前固定口径
应继续写成：

- `001610`
  = outer-anchor-facing hinge-entry shadow
- `000664`
  = low-share `v64_only` rotation hub
- `000117 / 001725 / 001006`
  = sink-facing shell
- `001543`
  = main terminal sink continuation
- `000697`
  = pre singleton side exit
- `001745`
  = post-entry `v64`-deeper side exit

本轮未启动新训练。
