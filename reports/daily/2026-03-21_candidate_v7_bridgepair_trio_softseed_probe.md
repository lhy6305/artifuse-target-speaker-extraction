# 2026-03-21 `candidate_v7` bridgepair trio soft-seed probe

## 背景

上一轮已经把
`bridgepair seed+1`
候选拆成按 failed-signature
分组的多条前沿，
并确认：

- row-level bridge
  仍只有：
  - `val_000376`
  - `val_000430`
- `val_000331`
  只是：
  - aggregate-only
    第三条扩张

但还差最后一个关键判断：

- 如果把
  `{331,376,430}`
  这个 aggregate-only trio
  暂时当成 soft seed，
  第四条 row
  会不会自然贴近这条线；
- 还是说：
  - 它一旦被升成 seed，
    候选榜马上又会被别的前沿抢走。

## 本轮做法

沿用：

- `scripts/eval/analyze_proxy_seed_expansion.py`

只是把 seed 改成：

- `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331_val.txt`

也就是：

- `val_000331`
- `val_000376`
- `val_000430`

输出到：

- `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_trio_seed_expansion_analysis/summary.json`

约束仍保持 full 口径：

- `v66 > v64`
- `v66 > v65`
- `v66 > v67`
- `v64 > v67`
- `v20 > v24`

## 结果

### 1. 一旦把 `331` 升成 soft seed，最近的第四条 non-seed row 已经不再落在原 bridge-like 同签名里

当前 trio seed 下，
最近的 non-seed rows 变成：

- `val_000075`
  - distance：
    - `1.164838`
  - failed-signature：
    - `v66>v64 | v66>v65 | v66>v67`
- `val_000305`
  - distance：
    - `1.415838`
  - failed-signature：
    - `v66>v64 | v66>v65 | v66>v67 | v64>v67`
- `val_000269`
  - distance：
    - `1.694205`
  - failed-signature：
    - `v66>v67 | v64>v67 | v20>v24`

也就是说：

- 最近的第四条 row
  已经不是
  bridge-like 三失败签名；
- `{331,376,430}`
  并没有自然把同一条 bridge 前沿
  再往外拉出一个近邻。

### 2. 在 trio seed 下，最近的 aggregate-pass candidate 也优先落到别的前沿

当前 trio seed 下，
最近的 aggregate-pass candidates
前几位是：

- `val_000076`
  - distance：
    - `1.772650`
  - failed-signature：
    - `v66>v64 | v66>v65`
  - aggregate min gap：
    - `+0.008152 dB`
- `val_000316`
  - distance：
    - `2.313680`
  - failed-signature：
    - `v20>v24`
  - aggregate min gap：
    - `+0.013688 dB`
- `val_000401`
  - distance：
    - `2.482381`
  - failed-signature：
    - `v66>v64 | v20>v24`
  - aggregate min gap：
    - `+0.009346 dB`
- `val_000223`
  - distance：
    - `2.640515`
  - failed-signature：
    - `v20>v24`
  - aggregate min gap：
    - `+0.012564 dB`

也就是说：

- 即使把
  `331`
  并进 seed，
  aggregate-pass 排名
  也仍会优先把：
  - `guardv20`
  一侧
  - `v66>v64 | v66>v65`
    这类别的边界行
  顶上来；
- 它没有把 bridge-like
  这条线
  稳定凝成一个新的 `4` 条 family。

### 3. 真正属于 bridge-like 同签名的第四条 row 已经很远，而且 aggregate margin 几乎掉到零

当前 trio seed 下，
bridge-like 同签名：

- `v66>v65 | v66>v67 | v64>v67`

还能 aggregate-pass 的候选
只剩：

- `val_000022`
  - distance：
    - `2.854296`
  - aggregate min gap：
    - `+0.000087 dB`
- 以及另一条更远的同签名 row

这个结果有两个关键含义：

1. 相比上一轮
   `331`
   对 bridge pair
   的：
   - distance `0.975332`
   - aggregate min gap `+0.008756 dB`
   trio seed 下的下一条同签名 row
   已经明显远很多；
2. 它的 aggregate margin
   几乎贴到：
   - `0 dB`
   边上，
   已经更像：
   - 勉强过线
   而不是：
   - 自然贴上的第四成员。

因此：

- `{331,376,430}`
  不应继续解释成
  “已经在长成 quartet 的 soft family”；
- 更准确的解释仍是：
  - 一个 aggregate-only trio，
    再往外已经没有自然第四条。

## 当前结论

1. 把
   `{331,376,430}`
   升成 soft seed
   后，
   候选榜会立刻被别的前沿抢走，
   说明这条 trio
   不是稳定的 family 中心。
2. bridge-like 同签名下，
   当前没有自然的第四条 row：
   - 最近的同签名第四条
     已经远到
     `2.854296`
   - aggregate min gap
     只剩
     `+0.000087 dB`
3. 因而
   `{331,376,430}`
   的正确定位
   仍应保持为：
   - aggregate-only bridge trio
   而不是：
   - 可继续往外扩的 soft-seed family

## 当前默认下一步

默认顺序继续收紧为：

1. row-level 扩张
   仍只围绕：
   - `{val_000376, val_000430}`
2. `val_000331`
   继续保留为：
   - 唯一站得住的 aggregate-only 第三条
   但不升级成新的 seed 中心。
3. 若后续还要继续找 bridge 第三条之后的结构，
   默认不再从：
   - trio soft-seed
   往外推；
   而是回到：
   - row-level bridge pair
   重新看更近的边界 rows。
4. 仍不启动新训练。
