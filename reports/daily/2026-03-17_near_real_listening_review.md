# 2026-03-17 Near-Real Listening Review

## 背景

本轮实际完成了第一版 near-real blind A/B：

- 对照：
  - `legacy stage2`
  - `ref_film + stft0.5 + sisdr0.0005`
- 听评包：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind/`

这包不是 synthetic hard-case，而是基于本地 raw target、真实人声片段、真实音乐片段拼出的 near-real 样本。

## 盲态汇总

`listening_results_summary.json` 中的盲态表面计数为：

- `file_a`: `4`
- `file_b`: `3`
- `tie`: `2`
- `uncertain`: `1`

总样本数：

- `10`

## 解盲后真实偏好

结合 `blind_key.json` 解盲后，真实模型偏好为：

- `legacy_stage2`: `6`
- `ref_film_sisdr0005`: `1`
- `tie`: `2`
- `uncertain`: `1`

当前结论很直接：

- 即使换到 near-real 包，`ref_film_sisdr0005` 仍然没有形成足够强的主观优势
- 当前默认主线继续保持 `legacy stage2`

## 分场景观察

### 1. raw target only

- `near_real_0001`
- `near_real_0002`

结果：

- 两条都偏向 `legacy_stage2`

当前含义：

- 即使输入里几乎只有目标 raw 语音，`ref_film_sisdr0005` 也更容易带出额外伪影
- 这说明问题不只是“干扰压不住”，还包括“目标保真时的处理中间伪影”

### 2. target + real speech / music

- `near_real_0003`
- `near_real_0004`
- `near_real_0005`
- `near_real_0006`
- `near_real_0007`

结果：

- `legacy_stage2`: `3`
- `ref_film_sisdr0005`: `2`
- `uncertain`: `1`

其中需要单独记的点：

- `near_real_0005`
  - 用户主观偏向 `ref_film_sisdr0005`
  - 主要原因是 source retention 略好
- `near_real_0006`
  - 实际偏向 `legacy_stage2`
  - 用户备注指出：
    - 干扰素材本身稍带混响
    - A/B 的主要伪影更多出现在干扰侧，而不是目标真值
- `near_real_0007`
  - 复杂场景下记为 `uncertain`
  - `ref_film_sisdr0005` 的 artifact 仍更重

### 3. target absent

- `near_real_0008`
- `near_real_0009`
- `near_real_0010`

结果：

- `legacy_stage2`: `1`
- `tie`: `2`

这里最关键的不是谁赢，而是共同暴露出的错误类型：

- `near_real_0008`
  - A/B 都出现了一个小音量瞬态
  - 且听起来很像目标音色
- `near_real_0010`
  - A/B 几乎静音
  - 但残留泄漏处的音色仍听起来像目标
- `near_real_0009`
  - 两边都存在干扰泄漏和较强伪影
  - 只是 `legacy_stage2` 相对更轻

这说明：

- 当前两条模型线都存在“target absent 时仍吐出一点像目标的东西”的风险
- 问题不是单纯的 residual leakage，也可能包含：
  - 目标音色 hallucination
  - 或把处理中间伪影误当作目标保留

## 本轮新增主观判断

用户本轮额外给出的关键直觉是：

1. 对输入的混响处理存在问题。
2. 模型有可能将处理中间过程产生的伪影误当作目标音频。

当前这条主观判断与现有实现事实是对得上的，因为：

- 设计稿中把“轻混响 / RIR 卷积”列为后续 realism 增强项；
- 但当前代码里还没有真正落地任何混响 / RIR 数据增强；
- near-real 包中一旦引入轻微混响说话素材，就开始更明显暴露：
  - 干扰泄漏
  - 目标样瞬态
  - 伪影被误判为目标保留

## 当前判断

截至本轮，当前最值得保留的判断是：

1. `legacy stage2` 继续是默认主线。
2. `ref_film_sisdr0005` 在 near-real 条件下仍未通过主观复核。
3. 当前真正暴露出来的新问题，不再只是“干净/不干净”，而是：
   - 混响输入处理不稳
   - target absent 时存在目标样瞬态
   - 处理中间伪影可能被模型当成目标相关成分保留

## 下一步建议

建议优先级改成：

1. 先不要继续开新的 checkpoint 近邻分支。
2. 先补一轮面向混响/尾音拖尾的 synthetic realism 增强。
3. 同时把 target absent 场景当成单独 guardrail 去盯，而不是只混在总体均值里。
4. 若后续继续做新训练，对照重点优先看：
   - raw target only 是否更干净
   - target absent 是否还会吐目标样瞬态
   - 轻微混响人声下是否还会把伪影当目标保留
