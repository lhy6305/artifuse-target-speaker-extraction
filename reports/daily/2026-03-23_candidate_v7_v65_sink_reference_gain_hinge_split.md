# 2026-03-23 `candidate_v7` `v65` sink reference+gain hinge split

## 背景

上一轮已经把
`reference`
和
`gain`
做成交叉四象限，
并确认：

- `train_001543`
  落在：
  - `both`
- `train_001745`
  和
  `train_000664`
  都落在：
  - `neither`

这说明：

- `short reference + weak gain`
  这组组合
  确实比单因子
  更接近
  `v65 sink`
  的 entry gate

但四象限里
还有最后一个关键问题：

- 在 `both`
  这格里，
  不是只有
  `train_001543`
  一个 sink，
  还躺着一个：
  - `train_000266`
    的 hinge

所以当前最窄的问题
变成：

- 当
  `short reference + weak gain`
  已经同时成立以后，
  到底还差哪半步，
  才会从
  hinge
  走成
  sink

## 本轮做法

这一步不再增脚本，
直接复用：

- `scripts/eval/analyze_proxy_group_split.py`

只对比两条 singleton：

- `v65_sink`
  - `train_001543`
- `reference_gain_both_hinge`
  - `train_000266`

新增 singleton 资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_reference_gain_both_hinge_train.txt`

输出：

- `reports/eval/active_targetfull_clean_failboth_v65_sink_vs_reference_gain_hinge/summary.json`

## 结果

### 1. 从 `train_000266` 的 hinge 走到 `train_001543` 的 sink，不是靠 gain 再继续变弱；gain 基本已经到位了

`001543 - 000266`
的 pairwise delta
显示：

- `interference_layers.0.gain_db = +0.059`

这基本可视为：

- gain
  几乎不变

也就是说：

- 一旦进入
  `reference + gain`
  的 `both`
  象限，
  `gain`
  已经更像：
  - 进入 gate
    的必要条件
- 它不是：
  - 从 hinge
    继续推到 sink
    的最后主导步

### 2. 真正把 `000266` 推成 `001543` 的第一主轴，仍然是 `reference` 继续缩短

同一份 pairwise delta
里，
最直接的结构差异是：

- `reference_duration_sec = -0.27`

也就是：

- `train_001543`
  的 reference
  比
  `train_000266`
  还要更短

而且这一步对应的
margin 变化是：

- `v66 - v64`
  从
  `+0.015989 dB`
  到
  `-0.008828 dB`
  额外下掉
  `0.024817 dB`
- `v66 - v65`
  从
  `-0.039845 dB`
  到
  `-0.113984 dB`
  额外下掉
  `0.074139 dB`

所以：

- `001543`
  相比
  `000266`
  并不是
  单纯把
  `v65`
  更深压低；
- 它是：
  - `v66 - v64`
    先从正侧翻到负侧
  - 同时
    `v66 - v65`
    再继续更负

而其中最稳定的
metadata 主轴
仍是：

- reference
  继续缩短

### 3. 真正补上的不是“更早 overlap”，而是 target-side transient 的抬升；甚至 overlap 反而更晚了一点

这一步还有一个重要修正：

- `interference_layers.0.start_offset_sec = +0.049`

也就是：

- `train_001543`
  相比
  `train_000266`
  overlap
  不是更早，
  而是
  略更晚

因此：

- 在
  `reference + gain`
  已经同时满足之后，
  overlap
  不再是把
  hinge
  推成
  sink
  的主导因子

真正更显著抬升的，
是 target-side transient：

- `target_transient_presence_minus_mid_db_mean = +5.912337`
- `target_transient_presence_share_mean = +0.056539`

而 interference 侧
反而是：

- `interference_transient_presence_minus_mid_db_mean = -0.377890`
- `interference_transient_presence_share_mean = -0.042478`

这说明：

- 从
  `000266`
  到
  `001543`
  的最后半步，
  更像是：
  - 更短 reference
  - 再叠加
    更高的 target-side transient
- 而不是：
  - overlap
    继续更早
  - 或
    gain
    继续更弱

### 4. `cosine` 在这一步也会动，但仍然更像辅助项，不应抢过 `reference`

同一组 delta
里：

- `target_interference_logspec_cosine = -0.094766`

说明：

- `train_001543`
  的 cosine
  也更低

但放在当前局部因果顺序里，
它更像：

- 和 target transient
  一起出现的
  后随信号

而不是：

- 比 `reference`
  更靠前的主分界

所以这一步后，
当前主线应继续保持：

- `reference`
  第一
- target-side transient
  进入第二层补充分界
- `gain / overlap / cosine`
  都退到更后面

## 结论

1. `short reference + weak gain` 更像 `v65 sink` 的 entry gate，而不是最终完成 sink 的全部解释。
2. 在已经进入 `both` 象限以后，`gain` 基本不再变化，`overlap` 甚至略晚；因此二者都不是把 `000266` 推成 `001543` 的最后主导步。
3. 真正把 hinge 推成 sink 的，更像是：
   - reference 继续缩短
   - 再叠加 target-side transient 明显抬升
4. 当前最合理的下一步应继续收紧成只拆：
   - `reference`
   - `target transient`
   看谁更接近 `v65 sink` 的最终主导。 
