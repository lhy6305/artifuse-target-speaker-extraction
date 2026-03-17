# 2026-03-17 Mainline A/B Listening Review

## 背景

此前客观主线一度收敛到：

- `ref_film + stft0.5 + sisdr0.0005`

但这仍然只是客观指标上的主候选，还没有经过修正后 GUI 口径下的人耳复核。

因此本轮实际完成：

- `legacy stage2`
- `ref_film + stft0.5 + sisdr0.0005`

的 blind A/B 主观对照。

听评包：

- `reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005_blind/`

## 执行口径

- 使用本地 GUI
- 已开启“同一样本共享峰值增益”
- 评分结果已导出到：
  - `listening_sheet.csv`
  - `listening_results_summary.json`

## 盲态汇总

盲态表面计数：

- `file_a`: `6`
- `file_b`: `2`
- `tie`: `1`
- `uncertain`: `3`

总样本数：

- `12`

## 解盲后真实偏好

结合 `blind_key.json` 解盲后，真实模型偏好为：

- `legacy_stage2`: `7`
- `ref_film_sisdr0005`: `1`
- `tie`: `1`
- `uncertain`: `3`

也就是说：

- 在可判样本里，旧主线明显更稳
- 新模型没有形成足够强的可听优势来替代旧主线

## 分 recipe 结果

### `target_clean_plus_music`

- `legacy_stage2`: `4`
- `ref_film_sisdr0005`: `1`
- `uncertain`: `1`

当前判断：

- 这正好对应此前最担心的回退 recipe
- 本轮主观结果继续支持“旧模型更稳”的判断

### `target_clean_speech`

- `legacy_stage2`: `2`
- `tie`: `1`
- `uncertain`: `2`

当前判断：

- 新模型在这组上也没有形成可稳定复现的可听优势

### `target_hard_speech`

- `legacy_stage2`: `1`

样本数不多，但当前唯一可判样本仍偏向旧主线。

## 样本级备注

本轮有几条样本需要单独标记：

- `val_000071`
  - 音量过小，最终记为 `uncertain`
  - 只能较弱地感觉到 A 的电子/回音伪影更重
- `val_000147`
  - `target.wav` 本身存在截断/瞬态问题
  - 最终记为 `tie`
- `val_000398`
  - A/B 几乎无声
  - 最终记为 `uncertain`
- `val_000325`
  - `target.wav` 结尾出现截断瞬态
  - 本组整体音量偏小
- `val_000404`
  - 本组 A/B 音量偏小

这些样本说明：

- 主观判断里仍有少量“样本本身不干净”或“输出音量过低”的干扰项
- 但即便考虑这些不确定样本，整体偏向仍明显站在 `legacy_stage2` 一边

## 当前结论

截至本轮：

1. `ref_film + stft0.5 + sisdr0.0005` 仍可保留为客观上有信息量的分支。
2. 但它没有通过当前这轮主观主线复核。
3. 默认主线应保持：
   - `legacy stage2`
4. `ref_film_sisdr0005` 当前更适合作为：
   - 客观对照分支
   - 或后续真实样本验证分支
   而不是立即替换默认主线。

## 下一步建议

1. 不继续围绕 `legacy stage2` vs `ref_film_sisdr0005` 开更多 synthetic 近邻分支。
2. 若后续还要做听评，优先只补少量关键不确定样本复核，而不是重新整包扩听。
3. 当前更值得继续判断的是：
   - 是否还需要保留 `ft2` 作为 focused 分支候选
   - 或直接转向更真实验证集准备
