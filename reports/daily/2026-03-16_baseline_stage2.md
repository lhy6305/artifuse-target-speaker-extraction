# 2026-03-16 Baseline Stage2

## 本次目标

在 stage1 已经证明“baseline 能学到东西”的基础上，继续往前推一轮更大的 stage2 实验：

- 扩大 synthetic 数据规模
- 跑更长一点的训练
- 用更细粒度的 eval 统计判断哪里仍然难

## 数据规模

本次 synthetic 数据规模：

- train: `2048`
- val: `512`

## 本次训练

命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 6 --batch-size 16 --log-every 50 --output-dir experiments\checkpoints\baseline_stft_mask_stage2
```

训练时间：

- start: `2026-03-16T19:52:24`
- end: `2026-03-16T19:54:11`
- elapsed: `107.104 sec`

训练配置：

- epochs: `6`
- batch size: `16`
- global steps: `768`
- device: `cuda`

best val loss：

- `0.020418131665792316`

产物：

- `experiments/checkpoints/baseline_stft_mask_stage2/latest.pt`
- `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- `experiments/checkpoints/baseline_stft_mask_stage2/train_summary.json`

## 本次评估

命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage2\best.pt --output-dir reports\eval\baseline_stft_mask_stage2_eval --save-audio-count 8
```

stage2 synthetic val 指标：

- `loss`: `0.024477669885527575`
- `waveform_l1`: `0.013033535506110638`
- `stft_l1`: `0.02288826880248962`
- `sisdr_db`: `-10.324090986978263`

产物：

- `reports/eval/baseline_stft_mask_stage2_eval/eval_summary.json`
- `reports/eval/baseline_stft_mask_stage2_eval/samples/`

## 与 stage1 对比

stage1：

- `loss`: `0.028332312998827547`
- `waveform_l1`: `0.014389460542588495`
- `stft_l1`: `0.027885705087101087`
- `sisdr_db`: `-13.101354904472828`

stage2 相比 stage1：

- `loss`: `-0.0038546431132999714`
- `waveform_l1`: `-0.0013559250364778563`
- `stft_l1`: `-0.004997436284611467`
- `sisdr_db`: `+2.7772639174945652 dB`

## stage2 分组观察

### 按 temporal pattern

- `target_intermittent` 当前 SI-SDR 最好：`-9.6090 dB`
- `target_absent_tail` 次之：`-9.8955 dB`
- `target_full` 和 `target_absent_head` 仍略差一些

### 按 recipe

当前更难的 recipe：

- `target_clean_plus_music`: `-12.8992 dB`
- `target_clean_speech`: `-11.8779 dB`

当前相对容易的 recipe：

- `target_singing_vocal`: `-7.2946 dB`
- `target_only`: `-7.8198 dB`

### 按 target present ratio bucket

- `ratio_lt_0.6`: `-8.3852 dB`
- `ratio_0.6_0.8`: `-9.9804 dB`
- `ratio_ge_0.95`: `-10.6085 dB`
- `ratio_0.8_0.95`: `-11.0600 dB`

这说明当前不是“目标越完整越一定更容易”，还和 recipe、干扰类型一起耦合。

## 当前结论

stage2 继续证明了：

1. baseline 在 synthetic 上还能继续往上走，不是 stage1 后就停滞。
2. 现在更需要盯分组难点，而不是只盯总 loss。

## 下一步建议

1. 若继续做 stage3，优先针对难 recipe 调整 synthetic 配比。
2. 若尝试模型升级，优先增强 reference conditioning，而不是先大改训练框架。
3. 待有试听环境后，再核对这些数值改善是否对应真实可听改善。
