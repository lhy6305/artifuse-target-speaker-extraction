# 2026-03-25 决策关卡听审复盘

## 背景

本轮实际完成了
`near_real_v1`
决策关卡听审，
使用的是磁盘上后续合并出的三候选 blind pack：

- `reports/eval/decision_gate_listening_pack_near_real_v1_stage2_v32_v64_blind_v2`

三者分别为：

- `legacy stage2`
- `v32`
- `v64`

本轮最重要的注意点不是盲态计数本身，
而是：

- 这是三候选单选 GUI；
- 遇到
  “两条候选几乎一样，另一条明显更差”
  时，
  `better_output`
  只能随机点其中一边；
- 因此必须结合
  `decision_tags`
  与 `note`
  一起解读，
  不能把表面计数直接当真实偏好。

## 盲态表面计数

`listening_results_summary.json`
里的表面计数为：

- `candidate_1 = 1`
- `candidate_2 = 1`
- `candidate_3 = 2`
- `tie = 6`

这组数字本身不能直接解释成：

- 某一条真实模型只赢了几次

因为其中至少有三条样本
带了“随机选边”的备注。

## 解盲后真实偏序

结合
`blind_key.json`
与样本备注后，
10 条样本的真实关系应还原为：

1. `near_real_0001`
   - `legacy stage2 = v32 = v64`
   - raw target only
2. `near_real_0002`
   - `legacy stage2 = v32 = v64`
   - raw target only
3. `near_real_0003`
   - `legacy stage2 > v32 = v64`
   - 主要原因：
     - `less_interference_leak`
   - 场景：
     - raw target + domain-matched friend speech
4. `near_real_0004`
   - `legacy stage2 = v32 = v64`
   - another friend speech slice
5. `near_real_0005`
   - `v32 = v64 > legacy stage2`
   - 用户备注：
     - 候选 1 和 2 无明显差异，
       3 明显不行
   - 场景：
     - raw target + real music
6. `near_real_0006`
   - `legacy stage2 = v32 = v64`
   - `guodegang` external speech
7. `near_real_0007`
   - `v32 = v64 > legacy stage2`
   - 用户备注：
     - 候选 2 和 3 无明显差异，
       1 明显不行
   - 场景：
     - raw target + friend speech + music
8. `near_real_0008`
   - `legacy stage2 = v32 = v64`
   - target absent / friend speech only
9. `near_real_0009`
   - `v32 = v64 > legacy stage2`
   - 用户备注：
     - 候选 1 和 3 无明显差异，
       2 明显不行
   - 场景：
     - target absent / external speech only
10. `near_real_0010`
    - `legacy stage2 = v32 = v64`
    - 用户备注：
      - 三条都是完美静音

## 两两比较后的真实结果

### `legacy stage2` vs `v32`

- `v32` 更好：`3`
  - `near_real_0005`
  - `near_real_0007`
  - `near_real_0009`
- `legacy stage2` 更好：`1`
  - `near_real_0003`
- `tie`：`6`

### `legacy stage2` vs `v64`

- `v64` 更好：`3`
  - `near_real_0005`
  - `near_real_0007`
  - `near_real_0009`
- `legacy stage2` 更好：`1`
  - `near_real_0003`
- `tie`：`6`

### `v32` vs `v64`

- `v32` 更好：`0`
- `v64` 更好：`0`
- `tie`：`10`

这说明当前人耳层面的关键事实不是：

- `v64` 比 `v32` 多赢一次

而是：

- `v32`
  和
  `v64`
  在这 10 条 near-real 样本上
  实际完全没有拉开。

## 分场景观察

### 1. raw target only

- `near_real_0001`
- `near_real_0002`

结果：

- 三者都打平

含义：

- `v32 / v64`
  没有在纯目标保真上形成可稳定听出的额外优势；
- 但也没有明显比
  `legacy stage2`
  更差。

### 2. friend speech leakage

- `near_real_0003`
- `near_real_0004`

结果：

- `near_real_0003`
  - `legacy stage2 > v32 = v64`
- `near_real_0004`
  - 三者打平

含义：

- 这轮最不利于
  `v32 / v64`
  的点，
  恰好仍落在
  friend speech
  这条当前最关键的症状上；
- 也就是说，
  它们没有在最想修的主问题上
  形成稳定可听优势。

### 3. music / harder mix / absent external speech

- `near_real_0005`
- `near_real_0007`
- `near_real_0009`

结果：

- 三条都表现为：
  - `v32 = v64 > legacy stage2`

共同原因：

- 主要是
  `source_retention`
  或
  `interference_leak`
  略好；
- 但这些优势
  目前仍没有细到
  `v64 > v32`
  这一层。

### 4. `guodegang` 与其余 absent guardrail

- `near_real_0006`
- `near_real_0008`
- `near_real_0010`

结果：

- 全部打平

含义：

- 当前在这些 guardrail 场景上，
  人耳没有继续听出
  `v64`
  或
  `v32`
  的单独加分项。

## 当前判断

截至本轮，
当前最该落盘的结论是：

1. `v32` 与 `v64` 在人耳上没有拉开。
2. 因而当前没有证据支持：
   - 继续把 `v64`
     当作一个需要单独推进的
     可听 keep 候选。
3. `v32 / v64` 确实在部分样本上
   相对 `legacy stage2`
   有局部收益，
   但这些收益主要落在：
   - music
   - harder mix
   - absent external speech
   不是当前最优先的
   friend speech leakage
   主问题。
4. `legacy stage2`
   仍不应因为这轮结果
   就被直接替换掉。
5. 若研究线上只保留一个基座，
   当前更合理的是保留：
   - `v32`
   作为研究基座；
   - `v64`
     保留为历史证据轮次，
     但不再作为独立 active 候选继续消耗预算。
6. `candidate_v7`
   这条高粒度旧 rows 重路由分析，
   当前应阶段性停止，
   直到出现新的、
   能在同一 near-real 小包上
   真正把
   `v32`
   与
   `v64`
   也一起拉开的候选。

## 下一步建议

1. 默认主线继续保持：
   - `legacy stage2`
2. 默认研究基座保留：
   - `v32`
3. `v64`
   继续保留磁盘证据，
   但默认不再单独推进：
   - 听审扩包
   - `candidate_v7`
     细分链路解释
   - 新训练 follow-up
4. 如果后续要重启研究，
   新候选至少要先满足：
   - 在同一组
     `near_real_v1`
     10 条样本上，
     不只是
     `> legacy stage2`
   - 还要能相对
     `v32`
     形成新的稳定可听差异
