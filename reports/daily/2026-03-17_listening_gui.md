# 2026-03-17 Listening GUI

## 背景

当前 blind A/B 试听包已经能导出，但实际使用时仍然存在两个工程问题：

1. 需要手动点进样本文件夹逐个播放，操作成本高。
2. 虽然已经有结构化 `listening_sheet.csv`，但人工填写仍然偏机械，容易漏项。

因此本轮补一个本地 GUI 端，直接消费现有 blind 包目录。

## 已实现能力

新增脚本：

- `scripts/eval/listening_pack_gui.py`

当前功能：

1. 选择并加载现有 blind listening pack 文件夹。
   - 兼容早期老版 `listening_sheet.csv` 字段
2. 按以下维度筛选样本：
   - `recipe`
   - `temporal_pattern`
   - 评分状态
3. 在 GUI 中直接播放：
   - `mixture.wav`
   - `reference.wav`
   - `file_a`
   - `file_b`
   - `target.wav`
4. 提供播放时的音量选项：
   - 是否按“同一样本共享增益”播放
   - 共享增益按该样本目录内所有播放文件的最大峰值计算，而不是把每个文件单独拉到目标峰值
   - 全局播放音量滑杆
5. 直接在 GUI 里填写：
   - `better_output`
   - `source_retention`
   - `interference_leak`
   - `volume_fluctuation`
   - `artifact`
   - `decision_tags`
   - `note`
   - 当前分档评估已改成单选按钮，而不是下拉框
6. 一键导出结果：
   - 覆盖写回 `listening_sheet.csv`
   - 同时生成 `listening_results_summary.json`

## 盲听约束

当前 GUI 默认只依赖：

- `listening_sheet.csv`
- 样本子目录下的音频文件
- `listening_rubric.json`

不会把 `summary.json` 里的真实模型标签当成界面展示信息，从而避免在 blind 包里意外泄露 A/B 真实身份。

## 当前使用方式

命令：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_clean_plus_music_blind
```

如果不传 `--pack-dir`，脚本也可以先打开 GUI，再手动选择文件夹。

## 2026-03-17 晚间修正

在实际盲听后又确认到一个重要口径问题：

- GUI 早期实现里的该选项，实际行为是“每个文件单独按自己的峰值拉伸”
- 这会缩小同一样本内 A/B 的真实音量和抑制强弱差异
- 与当初想要的“同一样本共享一个公平增益”并不一致

因此本日晚些时候已修正为：

- 同一样本目录内的 `mixture / reference / target / file_a / file_b`
- 共用同一个播放增益
- 该增益由这一组文件里的最大峰值决定

当前建议：

- 后续若继续做关键样本复核，优先使用修正后的 GUI 口径
- 之前在“单文件单独拉峰值”口径下听出的结果仍可参考
- 但在涉及“谁更稳、谁泄漏更重、谁波动更明显”的细判断时，应更谨慎解释
