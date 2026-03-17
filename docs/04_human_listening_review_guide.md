# 人耳复核操作指南

## 1. 当前复核目标

当前默认优先顺序不是继续开新训练，而是先做人耳复核，确认客观指标变化是否真有可听意义。

本轮建议按以下顺序执行：

1. 先复核 near-real 包里的 `legacy stage2` vs `ref_film + stft0.5 + sisdr0.0005`
2. 再决定是否继续复核 `base` vs `cpm_recipe_focus_v2_ft2`

大白话讲，就是先判断“新的主候选到底值不值得替掉旧主线”，再判断“focused 分支值不值得继续保留”。

## 2. 推荐盲听包

### 第一优先级：near-real 主线候选对照

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind/`

用途：

- 对照当前旧主线 `legacy stage2`
- 对照当前新主候选 `ref_film + stft0.5 + sisdr0.0005`
- 覆盖 raw target、真实人声干扰、真实音乐干扰与 target absent 场景

这是当前最重要的一包，因为它已经不再只是 synthetic hard-case，而是第一版 near-real 入口。

### 第二优先级：synthetic 主线候选对照

- `reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005_blind/`

用途：

- 对照当前旧主线 `legacy stage2`
- 对照当前新主候选 `ref_film + stft0.5 + sisdr0.0005`

这是当前最重要的一包，因为它直接决定后续默认模型主线该不该切换。

### 第三优先级：focused 分支主收益包

- `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_clean_plus_music_blind/`

用途：

- 判断 `ft2` 在 `clean_plus_music` 上是否真有可听收益

### 第四优先级：focused 分支 guardrail 包

- `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_guardrail_blind/`

用途：

- 判断 `ft2` 是否在 `clean_speech` / `hard_speech` 上带来副作用

## 3. 启动命令

在仓库根目录执行，统一使用仓库内 `python.exe`：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind
```

如果要听后面的优先级，把 `--pack-dir` 换成对应目录即可。

## 4. GUI 使用顺序

建议每条样本都按同一顺序听，避免口径漂移：

1. 先播放 `mixture.wav`
2. 再播放 `reference.wav`
3. 再听 `candidate_a` / `candidate_b`
4. 最后听 `target.wav`

建议打开：

- `同一样本共享峰值增益`

原因：

- 现在 GUI 已修正为“同一样本共享一个播放增益”
- 这样更接近公平对比，不会把 A/B 的真实相对差异悄悄抹平

## 5. 每条样本怎么打分

统一按这个顺序填：

1. 先填 `better_output`
2. 再分别给 A/B 填四类标签强度
3. 最后再补 `decision_tags` 和 `note`

`better_output` 的含义：

- `file_a`：A 更好
- `file_b`：B 更好
- `tie`：两者基本打平
- `uncertain`：这条样本不好判，或者两边都不满意

四类标签的判断重点：

- `source_retention`：目标人声音色、清晰度、完整度保留得怎么样
- `interference_leak`：背景干扰、人声串音、音乐残留漏出来多少
- `volume_fluctuation`：响度是否忽大忽小、是否抽动
- `artifact`：金属感、毛刺、泵音、断裂感等伪影

`decision_tags` 推荐只写真正影响你判定的原因，例如：

- `better_source_retention`
- `less_interference_leak`
- `steadier_volume`
- `less_artifact`

## 6. 什么时候记 `uncertain`

以下情况优先考虑记成 `uncertain`，并在 `note` 里写原因：

- A/B 差异很小，重复多次仍听不稳
- `target.wav` 本身就不自然，影响判断
- 两边各有明显优缺点，暂时无法给稳定偏好

不要为了“必须二选一”硬选一个。

## 7. 建议记录的备注

如果遇到下面这些现象，建议直接写进 `note`：

- `target.wav` 本身疑似有截断、门限、跳变
- A 更干净但更薄
- B 更稳但干扰残留更多
- 两边主要差异只体现在尾音、停顿或局部片段

这类备注后面回看时很有用，因为它能告诉我们问题到底像“源保留”还是“抑制过猛”。

## 8. 每包听完后怎么收尾

1. 点击 `一键导出`
2. 确认盲听包目录下已经更新：
   - `listening_sheet.csv`
   - `listening_results_summary.json`
3. 听完整包之前，不要先看 `blind_key.json`
4. 整包评分结束后，再解盲看 A/B 对应的真实模型

## 9. 当前建议的复核策略

建议不要一上来整包扩听，而是先把最关键的问题听清楚：

1. 先完成 `ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind`
2. 再回头参考 `ab_listening_pack_stage2_vs_ref_film_sisdr0005_blind`，判断 synthetic 与 near-real 结论是否一致
3. 如果新主候选没有形成稳定可听优势，就先停在这里，不继续补更多 focused 包
4. 如果新主候选确认更值得保留，再继续听 `ft2` 的两包

## 10. 当前判断标准

这一轮最重要的不是“新模型有没有某几条特别惊艳的样本”，而是：

- 它是否在多数关键样本上更稳
- 它是否没有明显增加副作用
- 它的客观提升是否能被耳朵听出来

如果答案还是“不够稳”或“不够明显”，那就应该优先保留现有主线，而不是继续盲推新分支。
