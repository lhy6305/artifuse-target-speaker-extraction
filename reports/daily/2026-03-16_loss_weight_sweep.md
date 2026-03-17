# 2026-03-16 Loss Weight Sweep

## 本次目的

上一轮已经确认：

- `ref_film + sisdr001` 是当前最强的分离导向候选
- 但它相对 legacy stage2 仍有一点 `stft_l1` 代价

因此本轮做一个很小的权重扫描，目标不是“找全局最优”，而是先回答：

1. 把 `sisdr_weight` 从 `0.001` 降到 `0.0005`，能不能更平衡？
2. 把 `stft_weight` 从 `0.5` 提到 `0.6`，能不能把 `stft_l1` 拉回来？

## 本次扫描组合

固定：

- 结构：`ref_film`
- synthetic 分布：`2048 / 512 / default`
- epochs: `6`
- batch size: `16`

扫描的 3 组为：

1. `stft=0.5, sisdr=0.0005`
2. `stft=0.6, sisdr=0.001`
3. `stft=0.6, sisdr=0.0005`

## 结果总览

### A. `ref_film + sisdr0005`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_ref_film_sisdr0005/`

eval：

- `loss`: `0.024296610990859335`
- `waveform_l1`: `0.012757464786773198`
- `stft_l1`: `0.02307829232631775`
- `sisdr_db`: `-8.092700551380403`

### B. `ref_film + stft06 + sisdr001`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_ref_film_stft06_sisdr001/`

eval：

- `loss`: `0.030351983648870373`
- `waveform_l1`: `0.015112058137674467`
- `stft_l1`: `0.030479850916890427`
- `sisdr_db`: `-11.873053622432053`

### C. `ref_film + stft06 + sisdr0005`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_ref_film_stft06_sisdr0005/`

eval：

- `loss`: `0.030443827337876428`
- `waveform_l1`: `0.01536259806198359`
- `stft_l1`: `0.030162458402628545`
- `sisdr_db`: `-11.556573523208499`

## 与当前关键基线对比

### `ref_film + sisdr0005` 相对 legacy stage2

legacy stage2：

- `loss`: `0.024477669885527575`
- `waveform_l1`: `0.013033535506110638`
- `stft_l1`: `0.02288826880248962`
- `sisdr_db`: `-10.324090986978263`

`ref_film + sisdr0005` 相对 legacy stage2：

- `loss`: `-0.0001810588946682397`
- `waveform_l1`: `-0.00027607071933743983`
- `stft_l1`: `+0.00019002352382813095`
- `sisdr_db`: `+2.23139043559786 dB`

这组结果的关键点是：

- `loss` 更好
- `waveform_l1` 更好
- `stft_l1` 只比 legacy 稍差一点点
- `sisdr_db` 却提升了超过 `2.23 dB`

### `ref_film + sisdr0005` 相对 `ref_film + sisdr001`

`ref_film + sisdr001`：

- `loss`: `0.02540873806356103`
- `waveform_l1`: `0.012997952913792687`
- `stft_l1`: `0.02482157020131126`
- `sisdr_db`: `-8.443684442725498`

`ref_film + sisdr0005` 相对 `ref_film + sisdr001`：

- `loss`: `-0.0011121270727016952`
- `waveform_l1`: `-0.0002404881270194887`
- `stft_l1`: `-0.0017432778749935106`
- `sisdr_db`: `+0.35098389134509473 dB`

也就是说：

- `sisdr0005` 直接支配了 `sisdr001`
- 四项主指标全部更好

## 对 `stft_weight=0.6` 的判断

两组 `stft=0.6` 都明显更差。

相对 `ref_film + sisdr0005`：

- `stft06 + sisdr001`
  - `loss`: `+0.006055`
  - `waveform_l1`: `+0.002355`
  - `stft_l1`: `+0.007402`
  - `sisdr_db`: `-3.780 dB`

- `stft06 + sisdr0005`
  - `loss`: `+0.006147`
  - `waveform_l1`: `+0.002605`
  - `stft_l1`: `+0.007084`
  - `sisdr_db`: `-3.464 dB`

结论非常直接：

- 当前把 `stft_weight` 提到 `0.6` 不但没有把 `stft_l1` 拉回来
- 反而让四项主指标一起变差

## 当前结论

本轮小扫描已经足够给出一个实用结论：

1. 当前最佳平衡点不是 `sisdr001`，而是 `sisdr0005`。
2. `ref_film + sisdr0005` 是到目前为止最值得继续往前推的候选主线。
3. `stft_weight=0.6` 方向当前可以先排除，不需要继续在这条线上浪费算力。

## 下一步

1. 当前默认实验候选更新为：
   - `ref_film + stft0.5 + sisdr0.0005`
2. 后续若继续扫权重，优先只在更小范围内动：
   - `sisdr_weight` 约 `0.0003 ~ 0.0008`
3. 在没有试听环境前，继续保留：
   - legacy stage2
   - `ref_film + sisdr0005`
   这两条作为主要对照。
