# 2026-03-16 SI-SDR Loss Alignment

## 本次目的

上一轮对照已经确认：

- `ref_film` 相对 `legacy_bias`
  - 改善了 `loss`
  - 改善了 `stft_l1`
  - 但没有改善 `sisdr_db`

这说明当前 baseline 的训练目标和主评估指标之间存在偏差。

因此本轮的核心问题是：

- 给训练目标补一个很轻的 `SI-SDR` 项后
- 能不能把 `sisdr_db` 拉回来
- 以及这个收益到底来自 loss，还是来自 `ref_film` 结构

## 本次代码改动

本轮新增：

- 在 `src/tse_prefix/pipeline/baseline_train.py` 中加入可配置的 `sisdr_weight`
- `compute_losses(...)` 现在会额外返回：
  - `sisdr_loss`
  - `sisdr_db`
- 训练脚本新增参数：
  - `--loss-stft-weight`
  - `--loss-sisdr-weight`
- checkpoint 与 summary 现已记录：
  - `loss_config`

兼容性处理：

- 训练时新增的 SI-SDR loss 使用 zero-mean 版本
- eval 侧继续保留历史非 zero-mean 口径

这样可以同时满足：

1. 训练目标更贴近分离任务
2. 历史 `sisdr_db` 结果仍然可与新结果直接对比

## Smoke 验证

命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 1 --batch-size 2 --log-every 2 --max-steps 6 --loss-sisdr-weight 0.001 --output-dir experiments\checkpoints\baseline_stft_mask_ref_film_sisdr_smoke
```

说明：

- 这一步只验证“新损失项能稳定反传并正常落盘”
- 不用它做结构优劣判断

## 正式对照设置

统一设置：

- synthetic 分布：当前工作区 `2048 / 512 / default`
- epochs: `6`
- batch size: `16`
- `loss_sisdr_weight`: `0.001`

本轮补了两个正式对照：

1. `legacy_bias + sisdr001`
2. `ref_film + sisdr001`

## 对照一：legacy_bias + sisdr001

训练命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 6 --batch-size 16 --log-every 50 --model-conditioning-mode legacy_bias --loss-sisdr-weight 0.001 --output-dir experiments\checkpoints\baseline_stft_mask_stage2_legacy_sisdr001
```

评估命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage2_legacy_sisdr001\best.pt --output-dir reports\eval\baseline_stft_mask_stage2_legacy_sisdr001_eval --save-audio-count 8
```

评估指标：

- `loss`: `0.028788995019567665`
- `waveform_l1`: `0.014994449769801577`
- `stft_l1`: `0.027589090601395583`
- `sisdr_db`: `-9.514256422407925`

相对 legacy stage2：

- `loss`: `+0.00431132513404009`
- `waveform_l1`: `+0.001960914263690939`
- `stft_l1`: `+0.004700821798905962`
- `sisdr_db`: `+0.8098345645703387 dB`

结论：

- 单纯给 legacy 版加轻量 `SI-SDR loss`，确实能把 `sisdr_db` 往上拉
- 但代价是重建类指标整体退化明显

## 对照二：ref_film + sisdr001

训练命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 6 --batch-size 16 --log-every 50 --loss-sisdr-weight 0.001 --output-dir experiments\checkpoints\baseline_stft_mask_stage2_ref_film_sisdr001
```

评估命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage2_ref_film_sisdr001\best.pt --output-dir reports\eval\baseline_stft_mask_stage2_ref_film_sisdr001_eval --save-audio-count 8
```

评估指标：

- `loss`: `0.02540873806356103`
- `waveform_l1`: `0.012997952913792687`
- `stft_l1`: `0.02482157020131126`
- `sisdr_db`: `-8.443684442725498`

相对 legacy stage2：

- `loss`: `+0.0009310681780334546`
- `waveform_l1`: `-0.00003558259231795109`
- `stft_l1`: `+0.001933301398821639`
- `sisdr_db`: `+1.8804065442527646 dB`

相对 `ref_film`（不带 SI-SDR loss）：

- `loss`: `+0.0018353122213738938`
- `waveform_l1`: `-0.0002927354871644641`
- `stft_l1`: `+0.0042560953006614`
- `sisdr_db`: `+2.1160859106457794 dB`

## ref_film + sisdr001 vs legacy + sisdr001

这是本轮最关键的隔离结论。

`ref_film + sisdr001` 相对 `legacy_bias + sisdr001`：

- `loss`: `-0.0033802569560066337`
- `waveform_l1`: `-0.0019964968560088894`
- `stft_l1`: `-0.002767520400084323`
- `sisdr_db`: `+1.070571979682427 dB`

说明：

- 收益不只是“加了 SI-SDR loss”带来的
- `ref_film` 结构和 `SI-SDR loss` 是有协同的
- 单纯把 loss 加到 legacy 上，达不到同等效果

## 分组观察

相对 legacy stage2，`ref_film + sisdr001` 的 `sisdr_db` 提升是比较全面的，而不是只靠个别 recipe 拉高平均值。

按 recipe：

- `target_clean_plus_music`: `+1.847172 dB`
- `target_clean_speech`: `+2.189440 dB`
- `target_hard_plus_music`: `+1.607464 dB`
- `target_hard_speech`: `+1.699822 dB`
- `target_music`: `+1.690880 dB`
- `target_only`: `+2.132959 dB`
- `target_singing_vocal`: `+1.879672 dB`

按 temporal pattern：

- `target_absent_head`: `+1.579670 dB`
- `target_absent_tail`: `+1.597637 dB`
- `target_full`: `+2.175601 dB`
- `target_intermittent`: `+1.689561 dB`

## 当前结论

本轮可以明确得到三条结论：

1. 轻量 `SI-SDR loss` 能有效缓解“重建项改善但分离主指标不上升”的问题。
2. 单纯 `legacy_bias + SI-SDR loss` 不够好，重建类指标退化较明显。
3. 当前最强候选是：
   - `ref_film + sisdr001`

更准确地说：

- 它不是所有指标都最好；
- 但在当前更关注的分离主指标 `sisdr_db` 上，已经明显优于已有 stage2 主线；
- 而且提升不是集中在单一 recipe 上，而是比较全面。

## 下一步

1. 当前可把 `ref_film + sisdr001` 视为新的“分离导向候选主线”。
2. 在没有试听环境前，先不要把旧 legacy stage2 完全废弃，保留作回退对照。
3. 下一步优先尝试：
   - 小范围扫 `sisdr_weight`
   - 或微调 `stft_weight`
   看能否在保住当前 `sisdr_db` 提升的同时，把 `stft_l1` 再拉回一点。
