# 2026-03-16 Baseline Eval Smoke

## 本次目标

把 baseline 从“能训练”推进到“能评估”。

大白话就是：

- 之前已经能把模型训起来；
- 现在要能拿一个 checkpoint 批量跑验证集，输出指标和样例结果。

## 本次新增

- `scripts/eval/eval_stft_mask_baseline.py`
- `configs/baseline_stft_mask_eval.json`

## 本次能力

当前 eval 脚本支持：

- 读取 synthetic manifest
- 加载 baseline checkpoint
- 批量前向推理
- 统计指标：
  - total loss
  - waveform L1
  - STFT L1
  - SI-SDR
- 按 temporal pattern 汇总子指标
- 导出少量样例：
  - `estimate.wav`
  - `target.wav`
  - `mixture.wav`
  - `sample_meta.json`

## 运行命令

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --save-audio-count 2
```

## 本次结果

评估对象：

- checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_smoke/best.pt`
- manifest:
  - `data/synthetic/val_manifest.jsonl`

运行环境：

- device: `cuda`

核心指标：

- `loss`: `0.046443975220123924`
- `waveform_l1`: `0.023725492258866627`
- `stft_l1`: `0.045436965922514595`
- `sisdr_db`: `-26.483998616536457`

评估产物：

- `reports/eval/baseline_stft_mask_smoke_eval/eval_summary.json`
- `reports/eval/baseline_stft_mask_smoke_eval/samples/`

## 本次额外修正

### checkpoint 加载兼容性

- 直接用 `weights_only=True` 加载时，会因为 checkpoint 内含 `pathlib.WindowsPath` 而失败。
- 已改为：
  - 优先尝试 `weights_only=True`
  - 失败后自动回退

## 当前结论

baseline 已经从“能训”升级到“能训也能评估”。

下一步就可以继续：

1. 扩大训练规模
2. 用更系统的验证集和 pattern 统计看趋势
3. 再决定是否换更强 baseline 结构
