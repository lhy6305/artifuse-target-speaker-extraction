# 2026-03-25 阶段结题判断与 guodegang 下一步建议

## 结论先行

当前项目**足够做阶段结题**，
但**不等于所有真实症状都已经解决**。

更准确地说：

1. 这条 TSE 前置模块路线，
   已经完成了
   “是否值得继续作为长期主线大范围推进”
   这个核心决策。
2. 结论已经稳定：
   - 默认主线继续保持
     `legacy stage2`
   - `v32`
     只保留为研究基座
   - `v64`
     不再作为独立 active 候选
   - `candidate_v7`
     高粒度旧 rows 重路由分析停止
3. 因而如果从项目管理角度问：
   - 这一阶段是否可以收尾？
   当前答案是：
   - 可以
4. 但如果从症状角度问：
   - `guodegang` / external speech leakage
     有没有被真正修好？
   当前答案是：
   - 还没有

所以当前最合理的口径应是：

- **Phase C / 当前研究阶段可以结题**
- 若还要继续，只能作为一个更窄的新子题重开，
  题目不再叫“继续优化整条 friend-side 研究树”，
  而应直接叫：
  - `guodegang / external speech leakage targeted follow-up`

## 为什么说当前已经足够阶段结题

因为当前最关键的几个问题都已经有稳定答案：

1. 主线是否切换：
   - 不切
2. `v32`
   是否值得继续作为研究基座：
   - 值得，但仅限基座
3. `v64`
   是否有足够强的人耳价值继续单独推进：
   - 没有
4. 继续沿
   `candidate_v7`
   旧 rows 重路由分析，
   还能不能产生新的高价值结论：
   - 当前看不能

也就是说，
“要不要继续在现有大树上投入”
这个决策，
已经被答完了。

## 为什么又说 `guodegang` 还没解决

因为历史证据一直很一致：

1. `guodegang`
   不是 broad speech probe
   里的普通一条样本，
   而是需要单独 guardrail 的特殊症状。
2. 已有 focused guardrail：
   - `near_real_guodegang_transient_probe_v1`
3. 已有更对题的 synthetic proxy：
   - `train_manifest_guodegang_proxy_v1.jsonl`
   - `val_manifest_guodegang_proxy_v1.jsonl`
4. 之前多轮失败也说明了：
   - 不能把它误映射成
     `hard speech / friend overlap`
   - 也不能只靠把一般的
     speech-leak rows
     union 回训练集来修

大白话讲：

- `guodegang`
  不是“把当前 friend-side 线再多推一点”就会自然变好的副产物；
- 它更像一个单独的真实症状族。

## 如果继续，下一步该怎么调

### 不该再做的事

1. 不继续沿
   `v64`
   这条 dual-protect 线放大。
2. 不继续做
   `candidate_v7`
   旧 rows 路由细分。
3. 不继续把
   `guodegang`
   问题混在
   friend speech leakage
   的总均值里看。
4. 不再用
   broad union manifest
   的方式，
   期待它顺便把
   `guodegang`
   修好。

### 应改成的更窄口径

下一条若重开，
建议只保留一个非常窄的目标：

- **在不回退 `v32` 现有总体质量的前提下，单独降低 `guodegang / external speech leakage`**

对应工程口径建议改成：

1. 基座固定：
   - `v32`
2. focused train / val：
   - `train_manifest_guodegang_proxy_v1.jsonl`
   - `val_manifest_guodegang_proxy_v1.jsonl`
3. focused near-real guardrail：
   - `near_real_guodegang_transient_probe_v1`
   - 再加本轮听审里最相关的：
     - `near_real_0006`
     - `near_real_0009`
4. 同时保留反向 guardrail：
   - friend speech leakage
   - target absent
   - raw target only

### 训练策略建议

如果要试，
建议只做**一轮很小的 focused follow-up**，
而不是重新开树：

1. 从 `v32` 初始化
2. 只给一条很轻的
   `guodegang_proxy_v1`
   focused objective
3. 保留现有
   `target_full`
   保真和 absent-side guardrail
4. 不做大 union
5. 不做 5 条以上近邻 sweep

换句话说：

- 这一步该像“带硬 guardrail 的小手术”，
  不是“再开一轮搜索树”。

## 新一轮的放行条件

如果真要重开这条窄任务，
建议放行条件直接写死成：

1. 相对 `v32`，
   `near_real_guodegang_transient_probe_v1`
   必须明确转正
2. `near_real_0006`
   人耳上不能更差
3. `near_real_0009`
   人耳上不能更差
4. friend speech leakage
   不能比 `v32` 更差
5. raw target only
   不能新增明显 artifact

只要有任一条不过，
就直接停，
不继续扩树。

## 当前建议

如果从收益 / 时间比看，
我当前建议是：

1. 先把当前阶段正式收尾
2. 把默认主线 / 研究基座 / 停线条件固定下来
3. 只有在你明确认为
   `guodegang / external speech leakage`
   是高频真实痛点时，
   再单开一个窄题继续

否则，
当前最合理的动作不是继续补洞，
而是：

- 以“阶段结题，问题清单已知”收口
