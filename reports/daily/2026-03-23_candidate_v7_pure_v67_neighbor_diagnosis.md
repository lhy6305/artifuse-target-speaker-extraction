# 2026-03-23 `candidate_v7` pure `v67` takeover train-side neighbor diagnosis

## 背景

上一轮已经把
near-shell edge band `4`
继续收紧成：

- pure `v67` takeover edge `3`
  - `train_001079`
  - `train_001494`
  - `train_000697`
- `v67 + v65` drift singleton `1`
  - `train_001589`

但还缺最后一层更细解释：

- pure `v67` takeover
  周围最近的 train-side 邻居
  到底更像：
  - dual-leak shell
  - 纯 `v67` 外层延展
  - 还是已经开始带上
    `v65`
    的 drift frontier

如果这层切清，
当前默认下一步
就可以从：

- “继续围绕 pure `3` 做 case diagnosis”

进一步收紧成：

- “只诊断 pure-signature `v67-top`
   和 `v65` drift
   的分界线”

## 本轮做法

### 1. 补一个可复用的 metadata-rich 近邻脚本

新增脚本：

- `scripts/eval/analyze_proxy_case_neighbors.py`

作用：

- 用 seed sample-id 子集
  在 search manifest 中做近邻搜索；
- 同时读取：
  - manifest 里的 transient / cosine 字段
  - `metadata.json`
    里的
    `target_duration_sec`
    `reference_duration_sec`
    `interference_layers.0.gain_db`
    `interference_layers.0.start_offset_sec`
- 可选拼接 compare 结果，
  直接把每个近邻的：
  - top alias
  - failed constraints
  - `v66` 相对 `v64 / v65 / v67`
    的 gap
  一起落盘

### 2. 先跑一版全量近邻，
再确认 train-only 才是当前主解释空间

输出：

- 全量近邻：
  - `reports/eval/active_targetfull_clean_failboth_pure_v67_neighbor_diagnosis/summary.json`
- train-only 近邻：
  - `reports/eval/active_targetfull_clean_failboth_pure_v67_neighbor_diagnosis_train_only/summary.json`

seed 固定为：

- `train_001079`
- `train_001494`
- `train_000697`

search 先看：

- `failboth topv66`
- `failboth topv67`

字段同时纳入：

- manifest：
  - `target_transient_presence_minus_mid_db_mean`
  - `target_transient_presence_share_mean`
  - `interference_transient_presence_minus_mid_db_mean`
  - `interference_transient_presence_share_mean`
  - `target_interference_logspec_cosine`
- metadata：
  - `target_duration_sec`
  - `reference_duration_sec`
  - `interference_layers.0.gain_db`
  - `interference_layers.0.start_offset_sec`

compare 仍固定：

- `v20`
- `v24`
- `v64`
- `v65`
- `v66`
- `v67`

约束仍固定：

- `v66 > v64`
- `v66 > v65`
- `v66 > v67`
- `v64 > v67`
- `v20 > v24`

## 结果

### 1. 如果不先切成 train-only，metadata-only val outlier 会重新混进 pure trio 的“最近邻”里

全量近邻 top 12
里会直接出现：

- `val_000182`
- `val_000396`
- `val_000041`

其中：

- `val_000182`
  依旧表现为：
  - metadata 上并不远
  - 但 direction 完全失真
- `val_000396`
  甚至会出现：
  - `v66 < v64`
  - `v66 < v65`

所以当前这条线
若要解释 pure `v67` takeover
的 train-side frontier，
默认必须先切成：

- train-only neighbor search

不能直接拿全量 top-k
做主结论。

### 2. pure trio 最近的 train-side 邻居并不以 `train_001589` 为主；它周围先出现的是一圈 mixed ring

train-only top 12
最近邻为：

- shell-like `v66-top`
  - `train_001599`
  - `train_000597`
  - `train_000865`
- pure-signature `v67-top`
  - `train_000799`
  - `train_001639`
  - `train_000216`
  - `train_000759`
  - `train_001006`
- `v65` drift `v67-top`
  - `train_001745`
  - `train_001610`
  - `train_000266`
  - `train_001589`

也就是说：

- `train_001589`
  并不是 pure trio
  的最近单一延展方向；
- pure trio 周围
  先出现的是：
  - 少量 shell-like 回缩
  - 一圈仍保持 pure signature 的 `v67-top`
  - 再往外才是
    `v65`
    开始进入的 drift

### 3. pure trio 相对 shell-like 邻居，最稳定的差异仍然是“更弱 gain + 更低 cosine”，不是更猛 interference

最近的 shell-like `v66-top 3`
均值相对 pure trio `3`
为：

- `target_duration_sec = -0.20 sec`
- `reference_duration_sec = +0.46 sec`
- `interference_gain_db = +3.5687 dB`
  - 即：
    - shell-like 明显更强
- `start_offset_sec = -0.0170 sec`
- `cosine = +0.0593`
- `interference_transient_presence_minus_mid_db_mean = -0.1878`

对应 direction：

- `v66 > v64 = +0.168386`
- `v66 > v65 = +0.218626`
- `v66 > v67 = +0.062774`

这说明：

- pure trio
  走出 shell
  的关键，
  依旧不是：
  - interference 更强
- 而更接近：
  - gain 更弱
  - cosine 更低
  - `v66 > v67`
    由正翻负

### 4. pure-signature `v67-top` 邻居已经允许明显更高的 interference transient；因此“低 transient”不是 pure takeover 的必要条件

最近的 pure-signature `v67-top 5`
均值相对 pure trio `3`
为：

- `target_duration_sec = -0.1540 sec`
- `reference_duration_sec = -0.3400 sec`
- `interference_gain_db = +1.2291 dB`
- `start_offset_sec = +0.0496 sec`
- `cosine = +0.0175`
- `interference_transient_presence_minus_mid_db_mean = +5.6668`
- `interference_transient_presence_share_mean = +0.1344`

但它们仍共同保住：

- `v66 > v64`
- `v66 > v65`

同时共同失败：

- `v66 > v67`
- `v64 > v67`
- `v20 > v24`

均值为：

- `v66 > v64 = +0.065665`
- `v66 > v65 = +0.164763`
- `v66 > v67 = -0.173643`

这说明：

- pure `v67` takeover
  并不要求：
  - interference transient
    一直很低
- 更准确的写法应是：
  - 只要
    `v66 > v64`
    和
    `v66 > v65`
    还在，
    即使 transient 已明显抬高，
    rows
    也仍可能停留在
    pure-signature `v67-top`

### 5. 真正把纯 `v67` 接管推向 `v65` drift 的，不只是更外层，而是“高 transient + `v66 > v64` 几乎塌平”

最近的 `v65` drift `v67-top 4`
均值相对 pure trio `3`
为：

- `target_duration_sec = +0.1325 sec`
- `reference_duration_sec = +0.0650 sec`
- `interference_gain_db = +0.4968 dB`
- `start_offset_sec = +0.0308 sec`
- `cosine = +0.0257`
- `interference_transient_presence_minus_mid_db_mean = +6.5296`
- `interference_transient_presence_share_mean = +0.1539`

对应 direction：

- `v66 > v64 = +0.007218`
  - 基本已经塌平
- `v66 > v65 = -0.036646`
  - 已翻负
- `v66 > v67 = -0.133630`

这说明：

- `train_001589`
  当前应继续和：
  - `train_001745`
  - `train_001610`
  - `train_000266`
  同组理解
- 更关键的边界
  不是：
  - 单看 gain / start offset
- 而是：
  - interference transient
    继续抬高
  - `v66 > v64`
    保护带同时被磨到接近 `0`
  之后，
  `v65`
  才开始一起进入

## 当前结论

1. pure `v67` takeover
   的 train-side 近邻结构
   不能写成：
   - shell -> pure trio -> `train_001589`
     单线推进；
   更准确的是：
   - shell-like 回缩
   - pure-signature `v67-top`
   - `v65` drift
     三层混合环带
2. pure trio
   相对 shell-like 邻居，
   最稳定的主差异
   仍然是：
   - 更弱 gain
   - 更低 cosine
   不是：
   - 更高 interference transient
3. pure-signature `v67-top`
   最近邻已经能容纳明显更高的
   interference transient；
   所以：
   - “低 transient”
     不是 pure takeover
     的必要条件
4. 把 pure `v67` takeover
   推向
   `v65` drift
   的更关键迹象
   当前应写成：
   - interference transient
     继续抬升
   - `v66 > v64`
     保护带塌平
   - 然后
     `v66 > v65`
     才开始翻负

## 当前默认下一步

默认顺序继续收紧为：

1. 不再回到
   shell 搜索
   或全量 val/train 混合近邻。
2. 若还继续推进，
   默认只围绕
   train-side nearest ring
   做下一层 split：
   - pure-signature `v67-top`
     - `train_000799`
     - `train_001639`
     - `train_000216`
     - `train_000759`
     - `train_001006`
   - `v65` drift `v67-top`
     - `train_001745`
     - `train_001610`
     - `train_000266`
     - `train_001589`
3. 下一步优先解释：
   - 为什么前一组
     在高 transient 下
     仍能保住
     `v66 > v65`
   - 而后一组
     会先把
     `v66 > v64`
     磨到接近 `0`
     再把
     `v66 > v65`
     一起翻掉
4. 仍不启动新训练。
