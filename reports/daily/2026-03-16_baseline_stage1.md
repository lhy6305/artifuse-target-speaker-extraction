# 2026-03-16 Baseline Stage1

## 本次目标

从 smoke 级别推进到一轮更像样的小规模 baseline 实验：

- 扩大 synthetic 数据规模
- 跑一个正式一点的训练
- 再用统一 eval 入口评估结果

## 数据规模

本次先将 synthetic 数据扩展到：

- train: `512`
- val: `128`

其中 train split 的目标时序模式分布为：

- `target_full`: `234`
- `target_intermittent`: `71`
- `target_absent_tail`: `102`
- `target_absent_head`: `105`

说明：

- 这批数据没有退回到“几乎全是 target_full”的偏置状态。

## 本次训练

命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 5 --batch-size 8 --log-every 25 --output-dir experiments\checkpoints\baseline_stft_mask_stage1
```

运行时间：

- start: `2026-03-16T19:01:42`
- end: `2026-03-16T19:02:01`
- elapsed: `19.09 sec`

训练配置：

- epochs: `5`
- batch size: `8`
- global steps: `320`
- device: `cuda`

best val loss：

- `0.025460483855567873`

训练产物：

- `experiments/checkpoints/baseline_stft_mask_stage1/latest.pt`
- `experiments/checkpoints/baseline_stft_mask_stage1/best.pt`
- `experiments/checkpoints/baseline_stft_mask_stage1/train_summary.json`

## 本次评估

命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage1\best.pt --output-dir reports\eval\baseline_stft_mask_stage1_eval --save-audio-count 6
```

stage1 synthetic val 指标：

- `loss`: `0.028332312998827547`
- `waveform_l1`: `0.014389460542588495`
- `stft_l1`: `0.027885705087101087`
- `sisdr_db`: `-13.101354904472828`

按 temporal pattern 的 SI-SDR：

- `target_absent_head`: `-14.9476 dB`
- `target_absent_tail`: `-12.2927 dB`
- `target_full`: `-13.7134 dB`
- `target_intermittent`: `-10.8607 dB`

评估产物：

- `reports/eval/baseline_stft_mask_stage1_eval/eval_summary.json`
- `reports/eval/baseline_stft_mask_stage1_eval/samples/`

## 与 smoke run 对比

smoke eval：

- `loss`: `0.046444`
- `waveform_l1`: `0.023725`
- `stft_l1`: `0.045437`
- `sisdr_db`: `-26.484`

stage1 相对 smoke 的变化：

- `loss`: `-0.018112`
- `waveform_l1`: `-0.009336`
- `stft_l1`: `-0.017551`
- `sisdr_db`: `+13.383 dB`

## 当前结论

这轮结果至少说明两点：

1. baseline 不只是“能跑通”，而是在 synthetic 数据上已经开始学到有效分离。
2. 当前结构虽然简单，但已经足够作为后续 stage2 扩展的起点。

## 下一步建议

1. 继续扩大 synthetic 规模，进入 stage2 训练。
2. 在 eval 中增加按 recipe、干扰类型、目标占空比的分组统计。
3. 保留样例导出，等后续有试听条件时补听感验证。
