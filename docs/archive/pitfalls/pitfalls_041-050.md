# 踩坑记录 历史归档 41-50

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `41-50`

## 2026-03-16

### 41. reverb probe 若直接复用默认 synthetic 输出路径，会污染主线数据集边界

现象：

- 当前主线 synthetic 数据固定使用：
  - `data/synthetic/train_manifest.jsonl`
  - `data/synthetic/val_manifest.jsonl`
- reverb probe 若也直接写这两个默认文件，会把 side experiment 的数据静默覆盖到主线入口上。

影响：

- 后续训练、评估或 compare 脚本可能在不知情的情况下吃到 probe 数据，而不是默认主线数据。
- 这类错误不会像崩溃那样立刻暴露，但会让实验结论和目录名逐渐对不上。

处理：

- 已在 `scripts/data/build_synthetic_dataset.py` 中补入 `--output-tag`。
- 当前 probe 数据改为写到：
  - `data/synthetic/*_{tag}/`
  - `data/synthetic/*_manifest_{tag}.jsonl`
  - `data/synthetic/summary_{tag}.json`

后续要求：

1. 任何非主线 synthetic 数据都必须使用 `--output-tag` 隔离落盘。
2. 主线默认 manifest 只保留给当前默认数据分布，不拿来承载 side experiment。

### 42. 把 target 与 speech 干扰同时做轻混响，不等于更接近 near-real；首轮 joint reverb probe 反而几乎全面回退

现象：

- 首轮 small probe `legacy_reverb_probe_v1` 使用：
  - `target_reverb_prob=0.35`
  - `speech_reverb_prob=0.45`
  - train / val：`256 / 64`
- 结果相对 `legacy stage2` 为：
  - 默认 val：`avg_sisdr_delta_db = -0.264`
  - probe val：`avg_sisdr_delta_db = -0.194`
- 且回退不是只集中在一两个角落，而是大多数 recipe / pattern 都没有占优。

影响：

- 说明“target 和 speech 一起加轻混响”这条最直观的 realism 改法，当前更像是在伤害 dry target 保真，而不是稳定修正 near-real 暴露的问题。
- 如果不先止损，后面继续沿这条线加规模，只会把算力花在已知不稳的方向上。

处理：

- 已保留 `legacy_reverb_probe_v1` 的训练、评估和 near-real blind 包产物，作为反例参考。
- 当前不再沿这条 joint reverb 方向继续放大训练规模。

后续要求：

1. 若继续做 reverb realism，优先先隔离 speech-like interference 侧，而不是再次一起改 target。
2. `legacy_reverb_probe_v1` 当前只保留为反例和回看材料，不再视作积极候选。

### 43. 即使把轻混响限制到 speech-like interference，small probe 也不会自动转正；仍需 near-real 人听把关

现象：

- 第二轮 `legacy_speechreverb_probe_v2` 改为：
  - `target_reverb_prob=0.0`
  - `speech_reverb_prob=0.55`
  - train / val：`256 / 64`
- 它相对 `legacy_reverb_probe_v1` 明显更稳，但相对 `legacy stage2` 仍为：
  - 默认 val：`avg_sisdr_delta_db = -0.183`
  - probe val：`avg_sisdr_delta_db = -0.195`
- probe 集上虽有一些方向性改善：
  - `target_clean_speech`: `+0.015 dB`
  - `target_clean_plus_music`: `+0.033 dB`
  但整体平均仍未转正。

影响：

- 说明“只给 speech 干扰加轻混响”更接近当前问题，但仍不足以仅凭 synthetic 指标就宣布有效。
- 如果这时直接扩到更大规模训练，仍有较大概率把一个“方向更对但证据还不硬”的分支提前放大。

处理：

- 已导出：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`
- 当前把它视作唯一保留的 reverb realism 候选，等待 near-real 人工听评。

后续要求：

1. 下一步人工优先听 `legacy stage2 vs legacy_speechreverb_probe_v2` 这包 near-real blind A/B。
2. 若 near-real 仍不占优，则先停止继续加大 reverb 训练预算，回到更细的 realism / guardrail 方案设计。

### 44. 只给 speech-like interference 加轻混响，可能不会变成“更稳的 near-real”，而会先冒出“电话音 / 带宽缺失感”

现象：

- `legacy_speechreverb_probe_v2` 的 near-real blind 听评现已完成。
- 解盲后的真实偏好为：
  - `legacy_stage2`: `1`
  - `legacy_speechreverb_probe_v2`: `0`
  - `tie`: `8`
  - `uncertain`: `1`
- 用户新增的关键主观判断是：
  - 这轮伪影更像“丢失了某些频率”
  - 听感接近“降低采样率”或“电话机里那种感觉”

影响：

- 这说明当前问题不只是：
  - 混响没处理好
  - 或单纯有残余泄漏
- 还包括一种更像“频带被削窄 / 高频或某些共振段被吃掉”的失真。
- 这类失真很容易在均值型 synthetic 指标里只表现成“小退步”或“看起来差不多”，但人耳会明显觉得不自然。

处理：

- 已把这轮主观结果补记到：
  - `reports/daily/2026-03-17_reverb_probe_followup.md`
- 当前不继续沿 `legacy_speechreverb_probe_v2` 直接放大训练规模。

后续要求：

1. 若后续继续做 realism 方向，优先补“频带缺失 / 电话音”诊断，而不是先继续抬 reverb 概率。
2. 后续客观分析不应只看 SI-SDR / L1；应增加更能暴露频带收窄的频谱侧检查。

### 45. “电话音 / 降采样感”未必表现成简单的全局高频均值塌陷，更可能是局部频带或清辅音瞬态被削掉

现象：

- 针对 near-real blind 包，已补一版诊断脚本：
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
- 首轮分析表明：
  - `legacy_speechreverb_probe_v2` 并没有稳定表现成“所有样本都更低的全局高频占比”
  - 但在 `near_real_0005`、`near_real_0007` 等样本上，仍能看到：
    - `upper_vs_mid` 明显下降
    - `frame_upper_share_p90` 明显下降
- 这与人耳听到的“电话音”并不矛盾，因为它更像：
  - 局部频带被削窄
  - 清辅音、吹气声或高频边缘瞬态被压掉

影响：

- 如果后续只盯“全局高频能量均值”或简单 rolloff，很可能漏掉最接近人耳感受的那部分失真。
- 这类失真在主观上很明显，但在均值型指标里容易只表现成“小变化”。

处理：

- 已把诊断脚本加入仓库，并实际跑在：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/`

后续要求：

1. 后续若继续做这类诊断，优先同时看：
   - `rolloff`
   - `upper_vs_mid`
   - `frame_upper_share_p90`
2. 不要把“没有明显全局低通”误判成“没有电话音式失真”。

### 46. “电话音”里最伤耳朵的部分，常常是高频瞬态相对中频被削掉；只看全局频带仍然不够

现象：

- 已新增：
  - `scripts/eval/analyze_listening_pack_transients.py`
- 该脚本以 mixture 的高频瞬态帧为锚点，对比 candidate 在这些帧上的：
  - `presence` 频段保留
  - 相对 `mid` 频段的保留差
- 首轮结果表明：
  - `legacy_speechreverb_probe_v2` 在 `near_real_0005 / 0007 / 0010` 上仍会被标成更 transient-lossy
  - `legacy_reverb_probe_v1` 的瞬态缺失问题更广、更重

影响：

- 这进一步说明，人耳听到的“电话音”很可能不是纯带宽问题，而是：
  - 清辅音
  - 吹气声
  - 高频边缘瞬态
  在相对中频的保留上被削弱了。
- 如果后续只做带宽均值检查，仍然可能漏掉这类最接近主观听感的问题。

处理：

- 已将该脚本实际跑在两套 near-real blind 包上。
- 当前这类瞬态缺失诊断，已成为后续 realism 方向的固定辅助检查项。

后续要求：

1. 后续若继续做 candidate 对比，至少同时跑：
   - `analyze_listening_pack_bandwidth.py`
   - `analyze_listening_pack_transients.py`
2. 若两者都指向同一侧“更窄带 / 更 transient-lossy”，再把它视作更强的客观证据。

### 47. 把“电话音 / 瞬态缺失”从诊断推进到训练钩子时，`sample_rate` 不能再靠 loss 内部写死

现象：

- 本轮已在 baseline loss 中新增：
  - `transient_presence_l1_loss`
  - 以及训练脚本入口 `--loss-transient-weight`
- 该 loss 需要把 `3k-8k`、`0.8k-3k` 这类频带边界映射到 STFT bin。
- 如果直接在 loss 里写死 `16000 Hz`，短期虽然和当前主线数据一致，但会把“当前数据约束”偷偷变成“代码永久假设”。

影响：

- 当前项目主数据确实是 `16k`，所以问题不会立刻炸出来。
- 但一旦后续 near-real 资产或其他评估入口改采样率，loss 里的频带解释就会静默漂移，变成很难察觉的错位。

处理：

- 已把 `sample_rate` 显式写入 `loss_config`，并由：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  传到 `compute_losses(...) / transient_presence_l1_loss(...)`
- 已实际跑通：
  - `max_steps=1` transient smoke training
  - smoke checkpoint eval

后续要求：

1. 以后凡是涉及“Hz 到 bin”的损失或诊断，都优先从配置或数据入口显式传 `sample_rate`。
2. 不要因为当前主线全是 `16k`，就把采样率约束偷偷散落成多个硬编码常量。

### 48. default 全分布上直接加 transient loss，很容易先伤 guardrail，再换来局部场景收益

现象：

- 本轮基于 `legacy stage2` 做了两轮 warm-start transient probe：
  - `transient_weight=0.005`
  - `transient_weight=0.002`
- 两轮都会明显压低 synthetic val 上的 `transient_presence_l1`：
  - `0.7489 -> 0.5665`
  - `0.7489 -> 0.5788`
- 但在默认全分布 compare 上，`SI-SDR` 仍分别回退：
  - `-0.412 dB`
  - `-0.314 dB`

影响：

- 这说明“更像在保高频瞬态”不等于默认主线就更稳。
- 当前默认分布里，transient loss 更容易先伤：
  - `target_only`
  - `target_hard_speech`
  - `target_hard_plus_music`
- 而局部收益更集中在：
  - `target_clean_speech`
  - 以及部分 `target_absent_head / absent_tail`

处理：

- 已把较保守的 `legacy_transient_probe_v2 (0.002)` 保留下来。
- 但当前不把“直接在默认分布上加 transient loss”视为安全主线升级。

后续要求：

1. 若继续推进 transient loss，优先把它当作候选分支，而不是默认主线改动。
2. 判断是否值得继续，必须同时看：
   - focused recipe 收益
   - `target_only / hard_speech` guardrail 代价
   - near-real blind 听评

### 49. blind 包诊断脚本里的 `file_a / file_b` 计数是候选文件计数，不是模型标签计数；必须结合 `blind_key.json` 解码

现象：

- `analyze_listening_pack_bandwidth.py` 和 `analyze_listening_pack_transients.py` 的 summary 默认输出：
  - `file_a`
  - `file_b`
  - `tie`
- 但 blind 包里 `candidate_a / candidate_b` 与真实模型标签的对应关系会按样本随机打乱。

影响：

- 如果直接把：
  - `file_a: 4`
  - `file_b: 4`
  这种 summary 当作“两个模型各输 4 次”，结论可能是错的。
- 本轮 `legacy_transient_probe_v2` 的 near-real 包就是这样：
  - summary 表面上只是 `file_a: 4 / file_b: 4 / tie: 2`
  - 但结合 `blind_key.json` 解码后，真实结果是：
    - `legacy_transient_probe_v2` 被标成更 transient-lossy `7` 条
    - `legacy_stage2` 仅 `1` 条

处理：

- 当前这轮分析已补做解码，并把真实标签结论写入日报与总览。

后续要求：

1. 以后凡是 blind 包自动诊断，默认先看 summary，再必须结合 `blind_key.json` 解码成真实标签统计。
2. 没做解码前，不要直接用 `file_a / file_b` 计数下模型级结论。

### 50. 听评表里的空白字段不一定代表“无问题”；如果这轮打分策略是“只在差异明显时才填写”，就不能把空白直接当 `none`

现象：

- 本轮 `legacy_transient_probe_v2` 的 near-real 听评里，用户明确采用的是：
  - 只有存在明显差异时，才填写主要差异来源；
  - 其余字段保持未填。
- 因此 `listening_sheet.csv` 中大量空白字段，语义上更接近：
  - “未特别标注”
  - 而不是“明确没有问题”。

影响：

- 如果后续把这些空白字段直接按：
  - `none`
  - 或“没有 artifact / 没有 leak”
  去统计，就会高估这轮结构化标签的确定性。

处理：

- 本轮对结果解读时，已只把：
  - `better_output`
  - 明确填写的 `source_retention / interference_leak / artifact`
  - 以及自由备注
  当作有效证据。

后续要求：

1. 以后汇总这类 listening sheet 时，必须先确认“空白”的语义是：
   - 未评
   - 还是等价于 `none`
2. 如果口径是“只标明显差异”，最终结论里应优先写成：
   - “明确标出的差异是什么”
   - 而不是把未填项也硬转成负面或正面统计。
