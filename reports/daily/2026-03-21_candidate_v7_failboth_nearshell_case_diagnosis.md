# 2026-03-21 `candidate_v7` fail-both near-shell case diagnosis

## 背景

上一轮已经把
`persistent borderline rows`
拆成：

- 真正贴着 shell 的
  train near-shell edge band `4`
  - `train_001079`
  - `train_001494`
  - `train_000697`
  - `train_001589`
- 以及单独的
  metadata-only outlier
  - `val_000182`

当前还差最后一个更细问题：

- 为什么这 `4` 条
  train edge band
  还能稳定保住：
  - `v66 > v64`
- 但已经稳定输给：
  - `v67`

如果这一步能切清，
active bridge 这条线
就可以从
“边界搜索”
正式切到
“接管机理诊断”。

## 本轮做法

### 1. 把 shell `4`、edge `4` 和外层最近 `v67-top` 对照组放到同一份 case diagnosis summary

新增：

- `reports/eval/active_targetfull_clean_failboth_nearshell_case_diagnosis/summary.json`

三组分别是：

- dual-leak shell
  - `train_000597`
  - `train_000865`
  - `train_001477`
  - `train_001599`
- near-shell edge band
  - `train_001079`
  - `train_001494`
  - `train_000697`
  - `train_001589`
- outer compare band
  - `train_001639`
  - `train_000219`
  - `train_000664`
  - `train_001006`

这份 summary
统一记录：

- `v66 / v64 / v65 / v67 / v24 / v20`
  的逐例 gap
- failed-constraint 签名
- `target_duration_sec`
- `reference_duration_sec`
- interference
  - `gain_db`
  - `start_offset_sec`
- target/reference/interference
  的 source identity

### 2. 把 edge `4` 再拆成两个子型

新物化资产：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_edgeband_pure_v67_takeover_all.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_edgeband_pure_v67_takeover.jsonl`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_edgeband_pure_v67_takeover_all.jsonl`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_edgeband_v67_plus_v65_takeover_singleton_all.txt`
- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_edgeband_v67_plus_v65_takeover_singleton.jsonl`
- `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_edgeband_v67_plus_v65_takeover_singleton_all.jsonl`

对应 focused direction：

- `reports/eval/active_targetfull_clean_failboth_edgeband_pure_v67_takeover_direction_analysis/summary.json`
- `reports/eval/active_targetfull_clean_failboth_edgeband_v67_plus_v65_takeover_singleton_direction_analysis/summary.json`

## 结果

### 1. near-shell edge band 确实是 shell 和 outer frontier 之间的一层中间过渡层，不是随机外层样本

三组均值对照里，
当前最稳定的结构是：

#### dual-leak shell `4`

- `mean_target_duration_sec = 1.1775`
- `mean_interference_gain_db = -0.5530`
- `mean_interference_start_offset_sec = 0.1363`
- `mean_v66-v64 = +0.129529`
- `mean_v66-v65 = +0.175244`
- `mean_v66-v67 = +0.050005`

#### near-shell edge band `4`

- `mean_target_duration_sec = 1.6350`
- `mean_interference_gain_db = -4.4010`
- `mean_interference_start_offset_sec = 0.0870`
- `mean_v66-v64 = +0.070637`
- `mean_v66-v65 = +0.093171`
- `mean_v66-v67 = -0.095303`

#### outer compare band `4`

- `mean_target_duration_sec = 1.7700`
- `mean_interference_gain_db = -1.3255`
- `mean_interference_start_offset_sec = 0.2215`
- `mean_v66-v64 = +0.026855`
- `mean_v66-v65 = +0.126050`
- `mean_v66-v67 = -0.149374`

所以当前更准确的理解是：

- 从 shell 走到 edge，
  不是突然跳到
  外层 random `v67-top`；
- 而是先进入一层
  仍保留：
  - `v66 > v64`
  的过渡带，
  但
  - `v67`
    已开始稳定接管
    `v66`

### 2. 这层过渡带的核心漂移不是“更高的 interference loudness”，而是更长 target、明显更低的 interference gain、再叠加 cosine 下滑

从 shell `4`
到 edge `4`
的均值变化是：

- `target_duration_sec`
  - `+0.4575 sec`
- `interference_gain_db`
  - `-3.848 dB`
    更弱
- `interference_start_offset_sec`
  - `-0.04925 sec`
    更早
- `target_interference_logspec_cosine`
  - `-0.081655`
- `interference_transient_presence_minus_mid_db_mean`
  - `+0.958048`

这说明当前 edge band
并不是因为
interference 更强更猛
而掉出 shell；
更接近的事实是：

- case 变成了
  更长 target、
  更早混入、
  但更低 gain
  的一层过渡态；
- 在这层过渡态里，
  `v66`
  还足以守住：
  - `v64`
- 但已经守不住：
  - `v67`

也就是说，
当前 `v67`
接管的更像是：

- 对一类 longer-target /
  low-gain-early-overlap
  过渡态的系统性优势

不是：

- 单纯的高 interference
  压制

### 3. edge `4` 内部确实再裂成两个子型；主导子型其实只有 `3` 条

#### 子型 A：pure `v67` takeover edge

- `train_001079`
- `train_001494`
- `train_000697`

共同签名：

- 失败约束固定是：
  - `v66>v67`
  - `v64>v67`
  - `v20>v24`
- 仍全部保住：
  - `v66>v64`
  - `v66>v65`

aggregate 为：

- `v67 > v66 > v64 > v24 > v65 > baseline > v20`

关键 gap：

- `v66 > v64 = +0.081117`
- `v66 > v65 = +0.142099`
- `v66 > v67 = -0.083212`

这 `3` 条才是当前真正意义上的：

- clean edge-band takeover subtype

#### 子型 B：`v67 + v65` takeover singleton

- `train_001589`

它已经额外失败：

- `v66>v65`

aggregate 为：

- `v67 > v65 > v66 > v64 > v24 > baseline > v20`

关键 gap：

- `v66 > v64 = +0.039198`
- `v66 > v65 = -0.053612`
- `v66 > v67 = -0.131577`

而且它和另外 `3` 条相比，
最明显的偏移是：

- `target_duration_sec = 2.28`
  最长
- `interference_transient_presence_minus_mid_db_mean = 5.697815`
  明显更高

所以：

- `train_001589`
  当前不该再和其余 `3` 条
  完全等价并写；
- 它更像是
  edge band
  继续向外层漂移时，
  第一个开始同时被：
  - `v67`
  - `v65`
  双重接管的特例

### 4. 当前没有证据表明这 `4` 条只是某个重复 source / speaker 组合的偶然 artifact

本轮把
target / reference / interference
的 identity overlap
也落盘后，结果是：

- shell `4`
  没有任何重复
  target/reference/interference identity
- outer compare `4`
  也没有重复
- edge `4`
  里只有：
  - `train_001494`
  - `train_000697`
  共用了同一个
  `reference_segment_id`

除此之外：

- 没有共同 target segment
- 没有共同 interference audio

所以当前更合理的判断是：

- edge band
  不是一个
  “单一 source 复用”
  造成的假子群；
- 它更像是
  一类真实存在的
  case-composition 过渡层

## 当前结论

1. near-shell edge band `4` 当前应正式记成：
   - shell 与 outer frontier 之间的中间过渡层
2. 这层过渡的关键特征是：
   - 更长的 target duration
   - 更低的 interference gain
   - 更早的 interference start
   - 更低的 cosine
3. 它解释了为什么这些 rows 还能保住：
   - `v66 > v64`
   但已经稳定输给：
   - `v67`
4. edge `4` 内部还应再拆成：
   - `pure v67 takeover edge`
     - `train_001079`
     - `train_001494`
     - `train_000697`
   - `v67 + v65 takeover singleton`
     - `train_001589`
5. 当前更值得继续追的主对象
   已从 edge `4`
   继续收紧成：
   - 上面那 `3` 条
     pure `v67` takeover edge

## 当前默认下一步

默认顺序继续收紧为：

1. 不再把 `train_001589`
   和另外 `3` 条
   完全并写。
2. 若还继续推进，
   默认只围绕：
   - `train_001079`
   - `train_001494`
   - `train_000697`
   做更细 case diagnosis，
   解释 pure `v67` takeover
   为什么先发生。
3. `train_001589`
   只保留为：
   - edge-to-outer drift
     的单独异常子型
4. `val_000182`
   继续只保留为
   metadata-only outlier
5. 仍不启动新训练。
