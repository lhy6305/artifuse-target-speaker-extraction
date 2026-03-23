# 2026-03-24 `candidate_v7` `v65` sink false-positive archetype positioning

## 背景

上一轮已经把
`gain + cosine`
sink-side 里
剩下的两个 false positive
拆开：

- `train_000799`
- `train_000697`

并确认：

- `000799 -> 001543`
  更像
  shorter-duration
  的 transient-collapse pocket
- `000697 -> 001543`
  更像
  long-duration
  + long-reference
  + low transient/share
  的另一类 pre

但这还只说明了：

- 它们不是同一种 sink residual

还没有回答：

- 它们各自
  更像从哪条
  已知 pre archetype
  旋回来的

所以本轮不再继续围着
`001543`
做均值解释，
而是把：

- `000799`
- `000697`

分别放回
已知局部 archetype
坐标系里定位。

## 本轮做法

这一步继续复用已有脚本，
不加新训练：

- `scripts/eval/analyze_proxy_case_positioning.py`
- `scripts/eval/analyze_proxy_group_split.py`
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`

reference groups
固定成 5 个局部锚点：

1. `v65_sink_singleton`
   - `train_001543`
2. `weak_gain_partial_mean_hinge`
   - `train_001589`
3. `reference_gain_pre`
   - `train_000951`
4. `shared_target_hinge`
   - `train_001705`
5. `low_share_v64only`
   - `train_000664`

focus cases
固定成：

- `train_000697`
- `train_000799`

本轮新增输出：

1. case positioning：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_falsepositive_case_positioning/summary.json`
2. archetype split：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_falsepositive_archetype_split/summary.json`
3. `000799 -> 001589` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000799_vs_partialmeanhinge_factor_contrast/summary.json`
4. `000697 -> 000664` factor contrast：
   - `reports/eval/active_targetfull_clean_failboth_v65_sink_pre000697_vs_v64only_factor_contrast/summary.json`

## 结果

### 1. `000799` 最近的已知 archetype 不是 sink，而是 `001589` 那条 weak-gain partial-mean hinge

`case_positioning`
里，
`train_000799`
最近的 reference group
已经固定成：

- `weak_gain_partial_mean_hinge`
  (`train_001589`)

且它和第二近 reference
之间还有
`0.427533`
的总距离 margin。

相对
`001589`
的最大偏离项为：

1. `target_interference_logspec_cosine`
   - `-0.157187`
   - `-3.183 z`
2. `gap::v66>v65`
   - `+0.170866 dB`
   - `+2.122 z`
3. `target_duration_sec`
   - `-0.78 sec`
   - `-1.591 z`
4. `reference_duration_sec`
   - `-0.60 sec`
   - `-1.239 z`
5. `gap::v66>v64`
   - `+0.026417 dB`
   - `+1.082 z`

也就是：

- `000799`
  不是凭空长在
  sink 边上的新 pocket；
- 它更像已经非常贴近
  `001589`
  这条
  partial-mean hinge；
- 但又因为：
  - cosine 更低
  - `v66>v65`
    margin
    重新翻回正值
  - duration / reference
    更短
  所以没有进入 sink，
  而是被重新拉回
  pre。

### 2. 但把 `000799` 真正从 `001589` 拉回 pre 的，不是“再降一点 cosine”，而是 target-side transient collapse + shorter duration

直接看
`000799 -> 001589`
的 factor contrast，
并用
`000697`
作 distractor，
target-specific residual
排前的字段固定成：

1. `target_transient_presence_share_mean`
   - `-2.501890 z`
2. `interference_transient_presence_share_mean`
   - `+2.382530 z`
3. `target_transient_presence_minus_mid_db_mean`
   - `-2.318440 z`
4. `target_duration_sec`
   - `-1.588786 z`

而
`target_interference_logspec_cosine`
在这一步
几乎是中性的：

- `-0.056001 z`

这点很关键：

- 相对 sink 看，
  `000799`
  当然仍是
  transient-collapse pocket；
- 但相对它最近的
  archetype `001589`
  看，
  真正把它从
  hinge
  拉回 pre 的
  主 residual
  已不再是
  “再降一点 cosine”；
- 更像是：
  - target transient share
    进一步塌缩
  - target transient mean
    进一步下沉
  - duration
    继续缩短

因此：

- `000799`
  应写成
  “最接近
  `001589`
  partial-mean hinge，
  但被
  target-side transient collapse
  与 shorter duration
  重新拉回 pre”
- 不能再写成：
  - 单纯低 cosine
    的 sink-side 残留

### 3. `000697` 最近的已知 archetype 不是 `001589`，而是 `000664` 那条 low-share `v64_only`

`case_positioning`
里，
`train_000697`
最近的 reference group
已经固定成：

- `low_share_v64only`
  (`train_000664`)

和第二近 reference
之间的总距离 margin
为：

- `0.574853`

相对
`000664`
的最大偏离项为：

1. `target_duration_sec`
   - `+0.99 sec`
   - `+2.020 z`
2. `interference_layers.0.gain_db`
   - `-3.963 dB`
   - `-1.867 z`
3. `interference_transient_presence_minus_mid_db_mean`
   - `-5.257997`
   - `-1.669 z`
4. `gap::v66>v64`
   - `+0.036677 dB`
   - `+1.503 z`
5. `target_interference_logspec_cosine`
   - `-0.069493`
   - `-1.407 z`

所以：

- `000697`
  不是
  `001589`
  那条 partial-mean hinge
  的长一点版本；
- 它更接近
  `000664`
  这条
  low-share `v64_only`
  archetype；
- 但又因为：
  - target duration
    明显更长
  - gain
    更弱
  - interference transient mean
    更低
  - `v66>v64`
    margin
    重新翻正
  所以没有被继续压进
  sink，
  而是停在另一类 pre。

### 4. 但把 `000697` 从 `000664` 拉开的，也不是“同一种低 share 更深一点”，而是更长时长 + 更弱 interference package

直接看
`000697 -> 000664`
的 factor contrast，
并用
`000799`
作 distractor，
target-specific residual
排前的字段固定成：

1. `target_transient_presence_share_mean`
   - `+2.501890 z`
2. `interference_transient_presence_share_mean`
   - `-2.382530 z`
3. `target_transient_presence_minus_mid_db_mean`
   - `+2.318440 z`
4. `target_duration_sec`
   - `+1.588786 z`

而
`target_interference_logspec_cosine`
同样几乎中性：

- `+0.056001 z`

这说明：

- 相对 sink 看，
  `000697`
  仍然可以写成：
  - long duration
  - long reference
  - low transient / share
    pocket；
- 但相对它最近的
  archetype `000664`
  看，
  它不是
  “target transient
  更低一点”的同轴加深；
- 更像是：
  - duration
    被明显拉长
  - interference share
    继续变低
  - interference mean
    继续变弱
  - gain
    继续下掉

因此：

- `000697`
  应写成
  “最接近
  `000664`
  low-share `v64_only`，
  但被
  long-duration
  + weak-interference-package
  重新拉回 pre”
- 不能再写成：
  - 只是
    `000799`
    的长一点版本

### 5. `000799` 与 `000697` 的差异，现在已经不是“同一种 residual 只差深浅”，而是分别回挂到两条不同 archetype

`archetype_split`
里，
`000697 - 000799`
的直接 delta
已经固定成：

- `target_transient_presence_minus_mid_db_mean`
  - `+2.936604`
- `target_transient_presence_share_mean`
  - `+0.007964`
- `interference_transient_presence_share_mean`
  - `-0.036519`
- `target_duration_sec`
  - `+0.72 sec`
- `interference_layers.0.gain_db`
  - `-1.682 dB`

也就是：

- `000799`
  更短
  也更偏
  target-side transient collapse；
- `000697`
  更长，
  但 interference package
  更弱，
  gain 也更低；
- 两者不是沿同一条轴
  朝 sink
  偏离不同距离；
- 更像分别从：
  - `001589`
    partial-mean hinge
  - `000664`
    low-share `v64_only`
  这两条局部 archetype
  各自旋回来的
  两种 pre。

## 当前解释

到这一步，
sink false positives
的默认解释应继续收紧：

1. `000799`
   不再只写成：
   - sink-side
     low cosine residual
   而应固定写成：
   - 最近 archetype
     是
     `001589`
   - 但被
     target transient collapse
     + shorter duration
     拉回 pre
2. `000697`
   不再只写成：
   - sink-side
     low transient/share residual
   而应固定写成：
   - 最近 archetype
     是
     `000664`
   - 但被
     long duration
     + weak interference package
     拉回 pre
3. 后续如果还要继续压缩，
   默认不再把
   `000799 / 000697`
   重新平均成同一个 pocket，
   而是分别沿：
   - `001589 -> 000799`
   - `000664 -> 000697`
   两条局部路线
   继续找 support。

## 结论

1. `000799`
   最近的已知 archetype
   已固定成
   `001589`
   weak-gain partial-mean hinge；
   它不是独立漂在 sink 边上的随机 pre。
2. `000697`
   最近的已知 archetype
   已固定成
   `000664`
   low-share `v64_only`；
   它也不是
   `000799`
   的长一点版本。
3. `000799`
   与 `000697`
   现在应视为
   两条不同 local archetype
   的回摆，
   不能再压成
   “同一种 sink-side residual”
   的假深度轴。
4. 本轮仍不启动新训练。
