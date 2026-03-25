# 2026-03-26 frontier `imperfection taxonomy` 与下一条子题

## 目标

当前不再回答：

- 哪个 checkpoint 更强

而是回答：

- 这批 frontier 候选
  共同还差在哪
- 下一条最值得继续推进的子题
  应该直接打哪个缺陷

分析对象：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind`
- 解盲结论：
  - `reports/daily/2026-03-26_silence_over_leak_frontier_v1_listening_review.md`

## 先给结论

最有价值的下一步不是继续在
`v32 / v49 / v54 / v59`
之间选赢家，
而是把下一条子题改成：

- `residual speech leakage floor under weak target audibility`

更大白话一点：

- 现在真正没解决的，
  不是“谁更静音”；
- 而是：
  - 在目标很弱、又有别人在说话时，
    这几条前沿模型都会残留一层
    听得出来的语音泄漏。

## 缺陷归因

### A. 已基本解决的部分

`near_real_0008 / 0010`

主观结果：

- 四个前沿候选全是 `tie`
- 评分都是：
  - `interference_leak = none`

意义：

- 对这类 absent core，
  当前前沿已经够静音；
- 继续围绕它们做 checkpoint 排序，
  很难再产出新的可听信息。

### B. 当前最核心的共同缺陷

#### 1. target-present speech leak floor

样本：

- `near_real_0003`
- `near_real_0006`
- `near_real_0007`

共同主观现象：

- 四个前沿候选全部仍有可听泄漏
- 其中：
  - `0003 = moderate leak`
  - `0006 = heavy leak`
  - `0007 = moderate leak`

这说明：

- 真正未解的主问题
  不是 absent silence；
- 而是：
  - `target present + weak target audibility + competing speech`
    时的残余语音泄漏下限。

其中最关键的一条是：

- `near_real_0006`

因为它不是“还有点瑕疵”，
而是四个前沿候选全都被打成：

- `interference_leak = heavy`

所以如果要继续做新子题，
它必须是第一主锚点。

#### 2. target-absent external speech leak floor

样本：

- `near_real_0009`

主观现象：

- 四个前沿候选全部仍为：
  - `interference_leak = moderate`

意义：

- 当前 `silence-over-leak` 分支
  虽然已经把明显更差的候选筛掉，
  但对这条 external-speech-only 样本，
  仍没有把泄漏降到“不可感知”。

不过这条的重要性
仍低于 `0006`，
因为：

- `0009`
  是 target absent；
- `0006`
  则同时要求：
  - 保住 target
  - 压住 external speech

难度更高，
也更接近真实使用痛点。

### C. 次级共同缺陷

#### 3. hard mixed-interference artifact / slight pumping

样本：

- `near_real_0007`

共同主观现象：

- 四个前沿候选都被打成：
  - `artifact = moderate`
- 其中三条还有：
  - `volume_fluctuation = slight`

这说明：

- 在 friend speech + music 混合干扰下，
  当前前沿除了 leak 之外，
  还有一层 hard-case artifact floor。

但它暂时不应成为第一优先级，
因为：

- 这条缺陷只在 `0007` 明显；
- 而 speech leak floor
  在 `0003 / 0006 / 0007 / 0009`
  四条上都存在。

## objective 侧补充判断

同包 objective 摘要：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind/silence_over_leak_objective_summary.json`

能看到两件事：

1. frontier 之间的 spread 很小
   尤其 `target_capture`
   和 `interference_capture`
   的差异，
   大多仍停留在小幅度上；
2. 即便 objective 继续排成：
   - `v54 > v59 > v49 > v32`
   人耳依然全部听成 `tie`

因此：

- 当前 frontier 的问题
  不是“程序没把赢家排出来”；
- 而是：
  - 这些候选在真正可听层面
    还都被同一个 leak floor 卡住。

## 下一条子题

### 名字

建议正式命名为：

- `residual_speech_leak_floor_v1`

### 资产入口

新 focused manifest：

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`

当前包含 4 条最有信息量的样本：

- `near_real_0003`
- `near_real_0006`
- `near_real_0007`
- `near_real_0009`

这 4 条覆盖：

- target present + friend speech
- target present + external speech
- target present + friend speech + music
- target absent + external speech

### 验收口径

下一轮如果要保留新候选，
至少要满足：

1. `near_real_0006`
   从 `heavy leak`
   降到至少不再是当前这一档；
2. `near_real_0003 / 0007 / 0009`
   不能继续全部停留在
   `moderate leak`
3. 不能为压 leak
   把评审重新打回：
   - `prefer_silence_over_leak`
     的反面，
   也就是：
   - 目标被一起压坏
   - 或 artifact / pumping 明显升级

## 阶段裁决

1. `silence-over-leak`
   作为“frontier 选型题”
   可以先结掉
2. 整个项目不建议结题
3. 当前最值得推进的新方向，
   不是继续选：
   - `v32`
   - `v49`
   - `v54`
   - `v59`
   谁更强
4. 而是直接围绕：
   - `residual speech leakage floor`
   开一条新的、更窄的缺陷子题

如果后续继续推进，
默认就从：

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`

这组样本开始，
而不是再回到
`silence-over-leak frontier`
的多候选选型包。
