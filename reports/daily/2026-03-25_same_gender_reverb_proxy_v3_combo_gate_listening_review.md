# 2026-03-25 same_gender reverb proxy v3 combo gate listening review

## 结论

`same_gender_reverb_proxy_v3` 四组合 combo gate 的 GUI 听审已经完成并解盲。

真实结果：

- `legacy_stage2 = 10`
- `v32 = 1`
- `tie = 1`

四个组合的分布：

- `none`: `legacy_stage2 3 / v32 0 / tie 0`
- `target_only`: `legacy_stage2 2 / v32 0 / tie 1`
- `speech_only`: `legacy_stage2 3 / v32 0 / tie 0`
- `both`: `legacy_stage2 2 / v32 1 / tie 0`

这意味着当前不是某一个混响组合单点失效，而是四个组合里 `legacy_stage2` 都更稳；`v32` 只在 `both` 组的 `val_000212` 上赢了一条。

## 与 objective 的冲突

这包导出前，四个组合的 objective 分桶全部仍偏向 `v32`：

- `none`: `avg_sisdr_delta_db = +1.1064`
- `target_only`: `avg_sisdr_delta_db = +1.0708`
- `speech_only`: `avg_sisdr_delta_db = +0.9484`
- `both`: `avg_sisdr_delta_db = +1.0905`

但人耳结果却是全面偏向 `legacy_stage2`。

因此当前可以确认：

1. 现有 objective 指标不能代表这条问题线上的真实听感优劣。
2. `same_gender_reverb_proxy_v3` 当前只能作为 failure-exposure 资产，不能作为训练放行信号。
3. 仅凭 synthetic objective 正收益，不允许启动 focused training。

## 新确认的评审标准

这轮备注里新增了一条非常关键的偏好标准：

- 当源非常弱、人耳几乎不可辨时，`完全闭嘴` 比 `输出几乎全是干扰` 更好。

这不是一个次要口味，而是会改变裁决的主标准。

最明确的样本是：

- `val_000197`
  - 组合：`speech_only`
  - objective：`v32 - legacy = +0.0463 dB`
  - 人耳：`legacy_stage2 > v32`
  - 备注：`legacy_stage2` 几乎是静音，而 `v32` 几乎全是干扰；从后级 VC 输入角度，静音更合适

这条标准还解释了两条“只是音量不同”的样本：

- `val_000212`
  - `both`
  - `v32 > legacy_stage2`
  - 备注表明：两边主要差异接近于音量放大，而目标保留本身足够多，因此更大的 `v32` 获胜
- `val_000252`
  - `target_only`
  - objective：`v32 - legacy = +21.4837 dB`
  - 人耳：`legacy_stage2 > v32`
  - 备注表明：输出几乎只剩干扰时，音量更小的 `legacy_stage2` 更优

所以这轮听审并不是“听感偏好音量更小”或“总是偏好更安静”，而是：

- 目标仍可用时，正常保留更多可用源是加分项
- 目标已几乎不可辨时，宁可闭嘴，也不要放大干扰残留

## 当前裁决

当前最终裁决是：

1. `v32` 不允许基于这条 `same_gender_reverb_proxy_v3` 线继续放行训练。
2. `same_gender_reverb_proxy_v3` 保留为 perceptual-failure diagnostic asset，而不是 pre-screen pass signal。
3. 评审口径里必须显式加入：
   - `弱源不可辨时，silence > interference leak`
