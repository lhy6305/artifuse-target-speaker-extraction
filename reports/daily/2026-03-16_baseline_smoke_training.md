# 2026-03-16 Baseline Smoke Training

## 本次目标

在没有现成 baseline 代码的前提下，先落地一个本地可自训的最小训练闭环，验证：

- synthetic manifest 是否能正常被训练代码读取
- 模型前向和 loss 是否能正常反传
- checkpoint 和 summary 是否能正常落盘

本次不追求效果结论，先追求“系统能完整跑一轮”。

## 本次新增

代码：

- `src/tse_prefix/data/synthetic_dataset.py`
- `src/tse_prefix/models/stft_mask_baseline.py`
- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`

配置：

- `configs/baseline_stft_mask_smoke.json`

## 当前 baseline 结构

采用的是务实最小版：

- 输入：
  - `mixture`
  - `reference`
- 模型：
  - STFT magnitude mask baseline
  - reference 走简单频谱统计编码
  - mixture 走条件化 GRU
  - 输出 mask 后用 mixture phase 重建
- loss：
  - waveform L1
  - log-magnitude STFT L1

## 本次运行命令

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 1 --batch-size 2 --log-every 2 --max-steps 4
```

## 运行结果

运行环境：

- device: `cuda`

时间：

- start: `2026-03-16T18:37:58`
- end: `2026-03-16T18:38:00`
- elapsed: `2.018 sec`

本次 summary：

- global steps: `4`
- best val loss: `0.046443975220123924`

落盘产物：

- `experiments/checkpoints/baseline_stft_mask_smoke/latest.pt`
- `experiments/checkpoints/baseline_stft_mask_smoke/best.pt`
- `experiments/checkpoints/baseline_stft_mask_smoke/train_summary.json`

## 本次踩到的工程问题

### 1. `istft` 输出长度不能直接 batch stack

- 原因：不同样本真实长度不同。
- 处理：改为 batch 内补齐。

### 2. `istft` 与 target 偶发 1 个采样点的边界偏差

- 原因：STFT/ISTFT 边界取整误差。
- 处理：loss 中按公共最短长度对齐。

## 当前结论

baseline 最小训练闭环已经打通。

这一步的意义不是“模型已经好用”，而是：

- 数据读取能跑
- 模型能训
- 产物能落盘

后续就可以继续往：

1. 扩大 synthetic 训练规模
2. 做正式 baseline 训练
3. 补 inference / 验证脚本

这三件事推进，而不用再停留在纯目录和数据准备阶段。
