# 2026-03-26 overlap 痛点、两条思路可行性评估与下一步计划

## 用户给出的核心痛点

当目标说话人和干扰语音在时间上重合时：

- 模型通常能知道“这里有目标说话人”
- 但输出分离不干净
- 结果不是完全找不到目标，
  而是：
  - 目标存在
  - 但同时残留了一层明显的干扰语音

用户提出的两个方向：

1. 当目标太弱、人耳也几乎不可辨时，
   直接当作没看到，
   静音不要输出
2. 参考目标说话人的音色特征，
   做一层类似共振峰/音色过滤

## 现状量化

当前 frontier pack：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind`

主观结论：

- `reports/daily/2026-03-26_silence_over_leak_frontier_v1_listening_review.md`
- `tie = 6`

但 tie 不等于“没有问题”。

从样本级主观评分看，
当前共同未解缺陷是：

- `near_real_0003`
  - 四个前沿候选全部：
    - `interference_leak = moderate`
- `near_real_0006`
  - 四个前沿候选全部：
    - `interference_leak = heavy`
- `near_real_0007`
  - 四个前沿候选全部：
    - `interference_leak = moderate`
    - `artifact = moderate`
- `near_real_0009`
  - 四个前沿候选全部：
    - `interference_leak = moderate`

这说明：

- 现在的主问题已经不是：
  - “找不找得到目标”
- 而是：
  - “重合时，残余语音泄漏的下限压不下去”

objective 也支持这个判断：

- `reports/eval/decision_gate_listening_pack_silence_over_leak_frontier_v1_v32_v49_v54_v59_blind/silence_over_leak_objective_summary.json`

在 6 条 frontier 样本上，
不同候选之间的 spread 已经不大：

- `near_real_0003`
  - leak spread = `0.49 dB`
  - target capture spread = `0.18 dB`
- `near_real_0006`
  - leak spread = `2.28 dB`
  - target capture spread = `0.13 dB`
- `near_real_0007`
  - leak spread = `1.65 dB`
  - target capture spread = `1.10 dB`
- `near_real_0008`
  - leak spread = `1.71 dB`
- `near_real_0009`
  - leak spread = `1.86 dB`
- `near_real_0010`
  - leak spread = `2.71 dB`

这能解释为什么：

- objective 还能继续排 `v54 > v59 > v49 > v32`
- 但人耳已经全部听成 `tie`

也就是：

- 当前 frontier 的主要瓶颈
  不是 checkpoint 选型，
  而是同一种 overlap leak floor。

## 思路一：弱目标 overlap 下直接闭嘴

### 结论

这是高可行性、高收益、和当前架构最对题的方向。

### 为什么可行

当前训练框架已经有现成入口：

- 模型本体是：
  - reference-conditioned STFT mask
  - `src/tse_prefix/models/stft_mask_baseline.py`
- loss selector 已支持：
  - `min_target_ratio / max_target_ratio`
  - `min_overlap_ratio / max_overlap_ratio`
  - `min_interference_gain_db / max_interference_gain_db`
  - `scripts/train/train_stft_mask_baseline.py`
- 现有 loss 已支持：
  - `interference_projection_ratio`
  - `absent_interval_l1`
  - `interference_extra_base_delta_projection`
  - `branch_protect_guard_sisdr`
  - `src/tse_prefix/pipeline/baseline_train.py`

大白话讲：

- 我们现在不是缺“能不能表达弱目标闭嘴”；
- 而是还没把这类 overlap 场景
  做成一个足够对题的 focused selector / proxy / gate。

### 预期收益

它直接贴合用户口径：

- 当目标弱到人耳也难分辨时，
  输出静音
  比输出一层脏的残余语音更好

它也与当前新子题
`residual_speech_leak_floor_v1`
的主锚点高度一致：

- `near_real_0006`
- `near_real_0007`
- `near_real_0009`

其中：

- `0006 / 0007`
  是 target present 但弱
- `0009`
  是 target absent

这三条正好构成：

- “弱目标 overlap 时可选择性闭嘴”
  的主战场。

### 风险

最大风险不是做不出来，
而是做过头：

- 把本来还应保留的目标一起压没
- 或把正常 target-present case
  也误打成静音

因此它必须配：

- `near_real_0003`
  这种 target 仍可用的 backstop

### 量化评分

- 技术可行性：`4.5 / 5`
- 与当前痛点匹配度：`5.0 / 5`
- 预期收益：`4.5 / 5`
- 工程风险：`2.5 / 5`
- 综合优先级：`最高`

## 思路二：基于音色/共振峰做一层过滤

### 结论

可以作为低优先级诊断思路，
但不适合作为下一条主线方案。

### 为什么不适合作为主线

1. 当前问题发生在：
   - same-gender / speech overlap
   - 目标与干扰在频带上高度重叠
2. 共振峰不是稳定静态模板，
   会随音素、发音方式、语速变化
3. 当前模型已经在做：
   - reference-conditioned spectral masking
   - 本质上已经在利用目标说话人音色信息
4. 如果再叠一层手工 formant filter，
   很可能出现：
   - 漏不一定明显更少
   - 但 target 会更薄、更闷、更假

大白话讲：

- overlap 泄漏的问题，
  更像是：
  - mask 还不够果断
  - weak-target 时不会主动 abstain
- 而不是：
  - “只差一层固定音色滤波器”

### 什么时候它还有价值

它仍可作为：

- 一个很便宜的 post-hoc falsification baseline

也就是：

- 不用把它当主线训练方向；
- 但可以用极小成本做一次离线后处理实验，
  看它能不能至少把 `0009 / 0006`
  的 leak 再压一点而不明显伤 target。

如果连这个都做不到，
就可以更干脆地把这条思路淘汰。

### 量化评分

- 技术可行性：`2.5 / 5`
- 与当前痛点匹配度：`2.0 / 5`
- 预期收益：`1.5 / 5`
- 工程风险：`4.0 / 5`
- 综合优先级：`低`

## 严谨判断

因此当前最严谨的判断是：

1. 用户提出的“弱目标时直接闭嘴”
   是可行且应优先验证的主方向
2. 用户提出的“按音色/共振峰过滤”
   不是完全不可做，
   但更适合作为便宜的旁路诊断，
   不适合拿来当下一条主线训练方案

## 下一步计划

### Phase 1：把新子题固定成 overlap abstention

统一问题定义：

- `weak-target overlap abstention under residual speech leak floor`

主 manifest：

- `data/references/real_eval_manifest_residual_speech_leak_floor_v1.jsonl`

角色分工：

- 主锚点：
  - `near_real_0006`
- 次锚点：
  - `near_real_0007`
  - `near_real_0009`
- backstop：
  - `near_real_0003`

### Phase 2：先做资产，不急着训

先补一个 focused proxy / selector，
目标是显式命中：

- 高 overlap
- 低 target ratio
- speech interference

优先选择器口径：

- `min_overlap_ratio`
  设高
- `max_target_ratio`
  设低
- `focus_interference_pools`
  限定 speech / external speech

这一步优先于任何新训练，
因为现在真正缺的是：

- 一个与用户标准完全一致的训练/评估切片

而不是再多一个 checkpoint。

### Phase 3：第一轮训练只验证“选择性闭嘴”是否成立

推荐初始化：

- `v54`
  或 `v59`

原因：

- 它们已经在 objective 上
  是当前 frontier 最强 absent-side 候选；
- 如果这条方向还能往前推，
  最可能从这两条继续长出来。

训练口径：

- 对弱目标 overlap selector：
  提高 `interference_extra` / `absent_extra`
  一类的惩罚
- 对正常 target-present backstop：
  保留 `branch_protect` / reconstruction 约束

### Phase 4：验收 gate

第一轮不看大盘，
只看这 4 条：

- `0006`
- `0007`
- `0009`
- `0003`

放行条件：

1. `0006`
   不再是当前的 `heavy leak`
2. `0007 / 0009`
   至少有一条不再停留在
   `moderate leak`
3. `0003`
   不能因为 abstention
   被压成“该听到的目标也没了”

## 建议执行顺序

1. 先把 overlap-abstention 的 focused proxy / selector 物化
2. 再起一轮极小训练
3. 再只对 `residual_speech_leak_floor_v1`
   这 4 条样本做 gate
4. 如有需要，
   另开一个极便宜的 post-hoc formant-filter baseline
   作为否证实验，
   但不占主线

## 最终建议

下一步主线方案应是：

- 继续项目，
  但不继续做 checkpoint 选型；
- 直接转入：
  - `weak-target overlap abstention`
  - 也就是：
    - 低可辨目标时宁可闭嘴，
      不要吐脏的 residual speech leak

这条方向与用户痛点、
当前评审标准、
现有代码入口、
以及当前 near-real 资产
是一致的。
