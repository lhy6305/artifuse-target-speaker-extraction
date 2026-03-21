# 2026-03-21 `candidate_v7` guardv65-relaxed bridge search

## 背景

上一轮已经确认：

- strict core 只有：
  - `val_000239`
  - `val_000430`
- 第一优先前沿是：
  - `guardv65_only`
    - `val_000376`
    - `val_000202`

但当时还缺一个关键判断：

- `guardv65_only`
  这两条，
  到底是不是同一条扩张线；
- 还是说：
  - `val_000376`
    其实只贴近 strict core
    的其中一侧；
  - `val_000202`
    只是同样只差
    `v66 > v65`
    的另一种 row。

## 本轮做法

本轮不再直接回到全约束 strict-all 搜索，
而是只放松一条 guard：

- 放松：
  - `v66 > v65`
- 仍要求 samplewise 同时通过：
  - `v66 > v64`
  - `v66 > v67`
  - `v64 > v67`
  - `v20 > v24`

对应输出：

- `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min3_on_friend_speech_leak_search_v1/summary.json`
- `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min2_on_friend_speech_leak_search_v1/summary.json`

## 结果

### 1. 放松 `v66 > v65` 后，row universe 先塌成一个 `4` 条 relaxed shell

当前 samplewise 通过其余四条 guards 的 rows
只有：

- `val_000202`
- `val_000239`
- `val_000376`
- `val_000430`

也就是：

- strict core
  `{239, 430}`
- 加上
  `guardv65_only`
  `{202, 376}`

这 `4` 条正好组成当前唯一的
guardv65-relaxed shell。

对应 aggregate：

- `v66 - v64 = +0.011213 dB`
- `v66 - v65 = +0.088209 dB`
- `v66 - v67 = +0.071365 dB`
- `v64 - v67 = +0.060153 dB`
- `v20 - v24 = +0.120831 dB`

注意：

- 虽然本轮搜索没有要求
  `v66 > v65`，
  但这个 `4` 条 shell
  aggregate 上已经自动恢复成：
  - `v66 > v65`

### 2. `min-count = 3` 时，没有更细的 metadata family；只会反复回到整包 `4` 条 shell

`min3` 搜索里，
top candidate
反复都是同一个 family：

- `val_000202`
- `val_000239`
- `val_000376`
- `val_000430`

也就是说：

- 一旦还要求
  `3+ row`，
  当前 guardv65-relaxed
  这条线
  还不能被稳定 carve 成
  更窄的 metadata family；
- 只会退回到：
  - relaxed shell

所以：

- 这个 shell
  可以保留成诊断资产；
- 但还不能被解释成
  已经干净的一条新 family。

### 3. `min-count = 2` 时，第一条真正被 metadata 稳定挑出来的桥接对子是 `{376, 430}`

`min2` 搜索里，
top order-pass candidate
不再是：

- `{202, 239}`
- `{202, 376}`
- `{239, 376}`

而是稳定收敛到：

- `val_000376`
- `val_000430`

第一层可解释 filters
来自：

- low target transient
  或
- low interference transient

例如：

- `max_target_transient_presence_minus_mid_db_mean <= -8.670663`
- `max_interference_transient_presence_minus_mid_db_mean <= 1.206818`

这对 bridge pair
的 aggregate 为：

- `v66 - v64 = +0.012678 dB`
- `v66 - v65 = +0.229887 dB`
- `v66 - v67 = +0.070054 dB`
- `v64 - v67 = +0.057376 dB`
- `v20 - v24 = +0.061743 dB`

也就是：

- 一旦把 `376`
  和 `430`
  放在一起，
  即使把
  `v66 > v65`
  放宽为可选，
  aggregate 上
  也会明显恢复成：
  - `v66 > v65`

### 4. `guardv65_only` 内部也不是单语义；`376` 和 `202` 应拆开

本轮最重要的新结论是：

- `guardv65_only`
  自己也不是一条单语义前沿；
- 更准确的结构应改写成：
  - `val_000376`
    挂到
    `val_000430`
    这一侧的
    low-target-transient /
    low-interference-transient
    bridge；
  - `val_000202`
    虽然也只差
    `v66 > v65`，
    但并没有先和
    `376`
    组成最稳定的 metadata pair。

一个直接反证是：

- `{val_000202, val_000239}`
  这对虽然也在 relaxed shell 里，
  但 aggregate：
  - `v66 - v65 = -0.053469 dB`

也就是：

- 它不会自动恢复成
  `v66 > v65`；
- 所以不能把
  `202`
  和 `239`
  当作与
  `{376, 430}`
  等价的桥接对子。

## 本轮已物化资产

### 1. relaxed shell

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell.jsonl = 0`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell.jsonl = 4`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell_{train,val,all}.txt`
- `tmp/candidate_v7_guardv65_relaxed_shell_selector_assets_summary.json`

val rows：

- `val_000202`
- `val_000239`
- `val_000376`
- `val_000430`

### 2. lowtransient-lowinttrans bridge pair

- `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl = 0`
- `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl = 2`
- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_{train,val,all}.txt`
- `tmp/candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_selector_assets_summary.json`

val rows：

- `val_000376`
- `val_000430`

## 当前结论

1. `guardv65_only`
   不能继续整体当成一条单语义 frontier。
2. 放松 `v66 > v65`
   后，
   当前先得到的是：
   - `4` 条 relaxed shell
     `{202,239,376,430}`
   它有 aggregate 信号，
   但仍偏混合，
   只能作为诊断壳层。
3. 当前第一条真正稳定的 bridge pair
   是：
   - `{val_000376, val_000430}`
4. 因而
   `val_000376`
   当前更应解释为：
   - strict core 里
     `430` 这一侧的外扩桥
   而不是：
   - 与 `val_000202`
     并列的一整条统一前沿。

## 当前默认下一步

默认顺序应继续更新为：

1. 若继续做 strict-core 扩张，
   默认先围绕：
   - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_all.txt`
   也就是：
   - `{val_000376, val_000430}`
   继续找同向 rows。
2. `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell_all.txt`
   保留为 relaxed diagnostic shell，
   用来判断：
   - 哪些 rows
     只是 guardv65 放松后
     被一起包进来，
     但并不属于同一条 bridge。
3. `val_000202`
   当前继续保留，
   但不要再默认和
   `val_000376`
   并写成同一条前沿。
4. `guardv20_only`
   仍是第二优先分支；
   `val_000469`
   仍是边界 anchor；
   仍不启动新训练。
