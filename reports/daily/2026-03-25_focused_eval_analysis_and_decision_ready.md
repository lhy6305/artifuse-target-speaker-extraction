# 2026-03-25 focused eval 分析补层与裁决口径固化

## 背景

本轮已经把下一阶段最小闭环资产跑出来：

- `guodegang probe`
  的 objective 基线
- `guodegang proxy`
  的 objective 基线
- `same_gender_reverb_like`
  focused 听审包
- `bandwidth_guardrail`
  focused 听审包

但如果只把这些结果留在目录里，
仍然不够直接做裁决。

这一步要补的是：

1. 把 objective 基线解成
   “能不能支持继续保留 `v32` 作为 focused 基座”
2. 把两个 focused 听审包解成
   “现在哪些已经能先判，
   哪些仍必须等人耳”
3. 把 stop rule
   从口头方案，
   进一步压成
   当前就能执行的裁决口径

## 本轮新增分析输出

### 1. same-gender reverb-like 包

- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind/asset_audit_summary.json`
- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind/bandwidth_analysis/summary.json`
- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind/tradeoff_analysis/summary.json`

### 2. bandwidth guardrail 包

- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind/asset_audit_summary.json`
- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind/bandwidth_analysis/summary.json`
- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind/tradeoff_analysis/summary.json`

## 结论先行

当前这批 focused 资产已经足够支持下面这组**直接裁决**：

1. `v32`
   仍应保留为下一阶段唯一的 focused 基座。
2. `legacy stage2`
   仍不应被这批 focused objective 结果直接替换。
3. `same_gender_reverb_like`
   听审包现在已经进入
   - 资产 QA 已过
   - objective 先验偏向 `v32`
   - 但仍需人耳最终裁决
   的状态。
4. `bandwidth_guardrail`
   听审包也已经进入可裁决状态，
   但默认口径必须带一个明显黄灯：
   - `near_real_0001`
     已出现
     `v32`
     更窄带的结构化证据，
     不能自动判通过。

更直白地说：

- 现在不是“目录已经有了，之后再看”；
- 而是已经能明确写成：
  - `v32`
    有资格继续做 focused 基座；
  - 但它必须先过
    `0001/0002/0006/0009`
    的最终人耳关；
  - 尤其不能在
    raw-target-only
    上带来电话音回退。

## 一、objective 基线怎么判

### 1. `guodegang_proxy_v1`

来源：

- `reports/eval/compare_stage2_vs_v32_on_guodegang_proxy_v1/summary.json`

关键数值：

- `count = 31`
- `avg_sisdr_delta_db = +1.591012`
- `median_sisdr_delta_db = +0.414856`
- `improved / regressed / near_tie = 19 / 9 / 3`

补充解释：

- 这组平均值明显为正，
  说明 `v32`
  在 focused synthetic proxy
  上总体方向是对的；
- 但离散度也很大：
  - 最差回退：
    `-16.152349 dB`
  - 最强提升：
    `+47.696764 dB`
- 所以它适合被解释成：
  - **focused pre-screen baseline**
- 不适合被直接解释成：
  - “已经足够证明 near-real 人耳一定更好”

当前裁决：

- `PASS as objective pre-screen baseline`

### 2. `near_real_guodegang_transient_probe_v1`

来源：

- `reports/eval/compare_stage2_vs_v32_on_near_real_guodegang_transient_probe_v1/summary.json`
- `reports/eval/compare_stage2_vs_v32_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/summary.json`

关键数值：

- `count = 6`
- `avg_sisdr_delta_db = +1.167128`
- `median_sisdr_delta_db = +1.125977`
- `improved / regressed / near_tie = 5 / 0 / 1`

细分观察：

1. `guodegang_absent_480s`
   三条都明显转正：
   - `+1.623785`
   - `+1.963995`
   - `+2.546212`
2. `guodegang_anchor_120s`
   三条里：
   - 两条小幅转正
   - 一条基本打平：
     - `-0.002021`

含义：

- `v32`
  对
  `guodegang`
  focused near-real probe
  不是偶然单点转正，
  而是已经形成一条可重复的客观优势；
- 但 target-present anchor 侧的收益
  仍没有强到可以跳过人耳确认。

当前裁决：

- `PASS as near-real objective guardrail`

## 二、same-gender reverb-like 包怎么判

对应目录：

- `reports/eval/ab_listening_pack_real_eval_same_gender_reverb_like_v1_stage2_vs_v32_blind`

### 1. 资产 QA

当前已确认：

- `num_samples = 2`
- `all_mono = true`
- `all_have_target = true`

也就是说，
这包已经不存在：

- 缺 `target.wav`
- 声道不一致

这类会污染听感口径的资产问题。

### 2. tradeoff 先验

来源：

- `tradeoff_analysis/summary.json`

当前两条样本的结构化结论是：

1. `near_real_0006`
   - `better_source_retention = tie`
   - `more_interference_leaky = legacy_stage2`
   - `better_retention_minus_leak = v32`
   - `delta_retention_minus_leak_db_b_minus_a = +1.145859`
2. `near_real_0009`
   - `more_interference_leaky = legacy_stage2`
   - `v32`
     对外部语音的 capture 更低：
     - `delta_interference_capture_db_b_minus_a = -3.901588`
   - 但残差占比更高：
     - `delta_residual_output_share_b_minus_a = +0.097302`

含义：

1. 在
   target present
   的 `0006` 上，
   当前 objective 先验偏向：
   - `v32`
     更像“泄漏更少，
     但保真没明显掉”
2. 在
   target absent
   的 `0009` 上，
   当前 objective 先验偏向：
   - `v32`
     suppress 更狠，
   但同时要防：
   - hollow
   - 过度压干
   - 残差更空

### 3. bandwidth 先验

来源：

- `bandwidth_analysis/summary.json`

结果：

- `narrower_candidate_counts = tie: 2`

逐条看：

1. `near_real_0006`
   - `delta_upper_vs_mid_db_b_minus_a = -2.212801`
   - 但没有叠到足够多证据，
     所以未被判成明确更窄带
2. `near_real_0009`
   - 指标分裂：
     - `legacy stage2`
       在 `upper_vs_mid`
       更差
     - `v32`
       在 `frame_upper_share_p90`
       更差
   - 最终记为 `tie`

当前裁决：

- **这包已具备正式听审条件**
- **objective 先验轻微偏向 `v32`**
- **但不能仅凭 objective 直接判通过**

最终听审问题应收敛成：

1. `0006`
   上，
   `v32`
   是不是真的在
   “少泄漏”
   的同时
   没把 target 弄薄
2. `0009`
   上，
   `v32`
   是不是
   “更干净但更空”

## 三、bandwidth guardrail 包怎么判

对应目录：

- `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_stage2_vs_v32_blind`

### 1. 资产 QA

当前已确认：

- `num_samples = 4`
- `all_mono = true`
- `all_have_target = true`

所以这包也已经可以直接进入正式听审。

### 2. tradeoff 先验

来源：

- `tradeoff_analysis/summary.json`

当前结构化结果：

1. raw target only
   - `near_real_0001`
   - `near_real_0002`
   上，
   `better_source_retention`
   都是 `tie`
2. 但 `v32`
   在两条 raw-only 上
   都有：
   - 轻微更高的 `target_capture`
   - 同时也有更高的 `residual_output_share`
3. `near_real_0006`
   仍是：
   - `legacy stage2`
     更 leak
   - `v32`
     的 retention-minus-leak
     更好
4. `near_real_0009`
   仍是：
   - `v32`
     suppress 更狠，
   但 residual 更高

这说明：

- 当前真正危险的不是
  “完全压不住”
  或
  “完全保不住”，
- 而是：
  - raw-only
    会不会被削成更窄带
  - absent speech
    会不会压得太空

### 3. bandwidth 结构化黄灯

来源：

- `bandwidth_analysis/summary.json`

关键结果：

- `narrower_candidate_counts`
  为：
  - `file_b = 1`
  - `tie = 3`

其中唯一被明确打成
`file_b` 更窄带的样本是：

- `near_real_0001`

对应证据：

- `delta_rolloff_hz_b_minus_a = -250.0`
- `delta_frame_upper_share_p90_b_minus_a = -0.290927`
- `narrowing_evidence_file_b = ["lower_rolloff", "lower_frame_upper_p90"]`

这条结论非常关键，
因为 `0001`
正是：

- raw target clip only

也就是说，
当前最该被当真的是：

- **`v32` 已经在 raw-target-only 样本上出现明确的窄带黄灯**

虽然：

- `near_real_0002`
- `near_real_0006`
- `near_real_0009`

都还只是 `tie`，
但只要 `0001`
人耳上真能听出电话音，
这一包就应该直接判为：

- bandwidth guardrail 不通过

当前裁决：

- **这包已具备正式听审条件**
- **默认不能预判通过**
- **当前默认要带“`0001` 原地黄灯”的口径进入听审**

## 四、当前直接裁决口径

基于现有 objective 与 pack 分析，
当前可以直接落盘的裁决是：

### 1. 已经能直接判的

1. `v32`
   继续保留为 focused follow-up 唯一基座
2. `guodegang_proxy_v1`
   正式保留为 synthetic pre-screen baseline
3. `near_real_guodegang_transient_probe_v1`
   正式保留为 focused objective guardrail
4. 两个 focused 听审包
   都已经通过资产 QA，
   不再只是“目录”，
   而是可直接进入正式听审的裁决资产

### 2. 还不能直接判通过的

1. `same_gender_reverb_like`
   是否通过
2. `bandwidth_guardrail`
   是否通过

原因不是缺脚本，
而是：

- 听审表还没填
- 人耳最终结论还没解盲

### 3. 默认 stop rule

后续一旦正式听审，
默认只要出现任一条，
就直接停：

1. `near_real_0001`
   明显更电话音 / 更窄带
2. `near_real_0002`
   明显更电话音 / 更窄带
3. `near_real_0006`
   人耳没有证明
   `v32`
   真正更少泄漏，
   或虽然更少泄漏但 target 更薄
4. `near_real_0009`
   suppress 虽强，
   但人耳上更空 / 更假 / 更窄

## 五、下一步默认执行顺序

当前最合理的默认顺序应固定为：

1. 先听
   `bandwidth_guardrail_v1`
   包
   - 优先检查 `0001 / 0002`
     有没有电话音
2. 再听
   `same_gender_reverb_like_v1`
   包
   - 重点看
     `0006 / 0009`
     的“更少泄漏”
     是否伴随
     “更空 / 更薄 / 更假”
3. 若任一包不过，
   不启动训练
4. 只有两个包都过，
   才允许把
   `v32`
   作为新一轮 focused follow-up
   的训练起点

## 当前结论

截至本轮，
这批 focused 资产已经从：

- “只有目录和音频”

推进到：

- objective 基线已解释
- 资产 QA 已确认
- tradeoff / bandwidth 结构化分析已补齐
- 听审 stop rule 已明确
- 默认裁决顺序已固定

因此现在缺的已经不是分析层，
而只剩最后一步：

- 人耳把两个 focused 包听完并解盲

