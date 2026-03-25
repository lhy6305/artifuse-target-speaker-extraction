# 2026-03-25 focused eval GUI 听审解盲与裁决

## 背景

本轮已完成两组 focused pack 的 GUI 听审并导出：

- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind`
- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind`

本次不再走“手工填表”口径，
而是直接基于 GUI 导出的：

- `listening_sheet.csv`
- `listening_results_summary.json`

再结合：

- `blind_key.json`

做解盲。

对应自动解盲输出：

- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind/listening_review_decoded_summary.json`
- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind/listening_review_decoded_summary.json`

## 结论先行

当前最关键的事实不是：

- 两个 pack 都各有 `1` 条偏向 `v32`

而是：

- **这两个“偏向 `v32`”其实落在同一条样本 `near_real_0009` 上**

所以把两包一起看时，
真实结论应还原成：

1. 唯一稳定可感知差异样本：
   - `near_real_0009`
2. 其余样本：
   - `near_real_0001`
   - `near_real_0002`
   - `near_real_0006`
   全部人耳打平

大白话讲：

- 这次不是
  `v32`
  在两个独立问题族上
  都分别新增了一条优势；
- 而是
  两个 pack
  恰好都包含了同一个
  `0009`
  样本，
  所以表面上看成了
  “赢两次”。

## 一、bandwidth guardrail 包解盲

目录：

- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind`

### GUI 盲态计数

- `file_b = 1`
- `tie = 3`

### 解盲后真实结果

- `v32 = 1`
- `tie = 3`
- `legacy stage2 = 0`

逐条样本：

1. `near_real_0001`
   - `legacy stage2 = v32`
   - raw target only
2. `near_real_0002`
   - `legacy stage2 = v32`
   - raw target only
3. `near_real_0006`
   - `legacy stage2 = v32`
   - target present + `guodegang` external speech
4. `near_real_0009`
   - `v32 > legacy stage2`
   - target absent / external speech only
   - `decision_tags = less_interference_leak`

### 这包怎么解释

1. 之前 objective bandwidth 分析里，
   `near_real_0001`
   有一个明确黄灯：
   - `v32`
     更窄带
2. 但这次人耳在
   `0001`
   上并没有听出稳定差异，
   结果是：
   - tie
3. 所以当前应把
   `0001`
   的状态从：
   - “明确听感回退”
   下调成：
   - “objective 黄灯，
     但尚未形成可稳定听出的主观回退”

当前裁决：

- **bandwidth guardrail 包未证伪 `v32`**
- 但也**没有提供新的强听感优势**
- 只有 `0009`
  这一条 absent external speech
  出现可感知收益

## 二、same-gender reverb-like 包解盲

目录：

- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind`

### GUI 盲态计数

- `file_b = 1`
- `tie = 1`

### 解盲后真实结果

- `v32 = 1`
- `tie = 1`
- `legacy stage2 = 0`

逐条样本：

1. `near_real_0006`
   - `legacy stage2 = v32`
   - target present + `guodegang` external speech
2. `near_real_0009`
   - `v32 > legacy stage2`
   - target absent / external speech only
   - `decision_tags = less_interference_leak`

### 这包怎么解释

1. `0006`
   仍然没有被人耳听出：
   - `v32`
     对 target-present
     same-gender / reverb-like
     风险的稳定收益
2. `0009`
   则再次表现为：
   - `v32`
     在 target-absent external speech
     上更干净一些

当前裁决：

- **same-gender reverb-like 包没有形成“family 级稳定收益”**
- 它当前只证明：
  - `0009`
    这条 absent external speech
    上，
    `v32`
    有可听优势
- 但还不能证明：
  - target-present 的
    `guodegang / 0006`
    真被修好了

## 三、两包合并后的真实结果

如果把两个包简单按“胜场”相加，
会得到：

- `v32 = 2`
- `tie = 4`

但这是误导性的，
因为：

- `near_real_0009`
  被两个 pack
  同时复用

所以更合理的 union 口径应是按唯一样本看：

### 唯一样本 union

- `near_real_0001`
  - tie
- `near_real_0002`
  - tie
- `near_real_0006`
  - tie
- `near_real_0009`
  - `v32 > legacy stage2`

也就是说：

- **4 个唯一样本里，只有 1 条可感知差异**
- **这 1 条就是 `near_real_0009`**

这与你的主观总结完全一致：

- 两组样本只在一条测试音频上有差异，
  其他无可感知差异

## 四、结合 objective 分析后的最终评估

### 1. 当前可以确认的

1. `v32`
   在
   target absent / external speech only
   的 `near_real_0009`
   上，
   形成了稳定可听优势
2. 这条优势和 objective 先验一致：
   - tradeoff 里
     `v32`
     确实更少泄漏
3. `near_real_0001`
   的 bandwidth objective 黄灯，
   当前没有变成人耳可稳定识别的电话音回退

### 2. 当前仍不能确认的

1. `v32`
   是否在
   target-present
   `guodegang / 0006`
   上
   真正形成收益：
   - 当前答案仍是不能确认
2. `same_gender_reverb_like`
   family
   是否已经成立：
   - 当前答案仍是否
3. `v32`
   是否值得因为这轮 focused 听审，
   直接进入新训练：
   - 当前证据仍偏弱

## 五、裁决

### 1. 不该得出的过强结论

当前不能写成：

- `v32`
  已经稳定修好
  `same_gender_reverb_like`
- `v32`
  已经通过全部 focused guardrail
- 可以直接启动下一轮 focused follow-up

### 2. 当前更准确的裁决

当前应写成：

1. `v32`
   相对 `legacy stage2`
   的 focused 可听收益，
   目前只稳定落在：
   - `near_real_0009`
     这条
     target absent / external speech only
     样本
2. 其余 focused 样本
   当前都未形成人耳可感知差异
3. 因而：
   - `v32`
     仍然适合作为研究基座保留
   - 但这轮 focused 听审
     还不足以支持
     “重开训练并继续修这条窄题”

### 3. 当前默认建议

当前默认建议应是：

1. **不重开训练**
2. 把这轮结果作为：
   - `0009`
     这条 absent external speech
     已有可听证据
   - `0006`
     这条 target-present
     关键样本仍未转正
   的新基线
3. 若未来真的要重开，
   先补更多
   target-present
   same-gender / reverb-like
   真实样本，
   而不是直接依据这轮
   1 条 win
   就启动训练

## 当前结论

截至 2026-03-25，
focused GUI 听审的真实结论应固定成：

- `v32`
  没有被 bandwidth / raw-only 人耳证伪；
- 但它当前唯一稳定可感知的 focused 收益，
  只落在
  `near_real_0009`
  这一条 absent external speech 样本；
- 因此这轮结果支持：
  - 保留 `v32` 作为研究基座
- 但不支持：
  - 现在就重开 focused follow-up 训练

