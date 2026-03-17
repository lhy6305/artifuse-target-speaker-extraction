# 2026-03-16 Synthetic MVP 记录

## 今日完成

- 新增脚本：`scripts/data/build_synthetic_dataset.py`
- 当前脚本已可消费以下正式 manifest：
  - `data/manifests/target_speech_pool.jsonl`
  - `data/manifests/target_reference_pool.jsonl`
  - `data/manifests/speech_interference_clean_pool.jsonl`
  - `data/manifests/speech_interference_hard_pool.jsonl`
  - `data/manifests/music_interference_pool.jsonl`
  - `data/manifests/singing_vocal_interference_pool.jsonl`
- 已实现最小输出结构：
  - `mixture.wav`
  - `target.wav`
  - `reference.wav`
  - `metadata.json`
  - split 级 `train_manifest.jsonl` / `val_manifest.jsonl`

## 本次验证命令

```powershell
.\python.exe scripts\data\build_synthetic_dataset.py --train-count 2 --val-count 1 --force-clean
```

## 当前已验证的事实

- 脚本可成功生成：
  - `data/synthetic/train/train_000001/`
  - `data/synthetic/train/train_000002/`
  - `data/synthetic/val/val_000001/`
- `data/synthetic/summary.json` 已生成。
- `metadata.json` 已记录：
  - recipe
  - target/reference 来源
  - interference layers
  - gain_db
  - start_offset_sec
  - 输出路径
- 已发现并修复一个关键问题：
  - 若干扰层带延迟，`mixture.wav` 可能比 `target.wav` 更长；
  - 现已在混音输出阶段强制裁回 target 时长；
  - 复测后 `mixture.wav` 与 `target.wav` 时长一致。

## 当前局限

- 目前仍偏 MVP：
  - `target_present_ratio` 固定为 1.0
  - 还没有 `target absent tail`
  - 还没有 `target intermittent`
  - 还没有更复杂的多段 overlap 结构
- 因此这版更适合验证链路，不适合直接视作最终训练数据策略。

## 下一步建议

1. 扩展 temporal patterns。
2. 生成一批更系统的小样本并人工抽听。
3. 在抽听通过后，再接 baseline inference 或最小训练闭环。
