# 2026-03-24 决策关卡听审包导出

## 背景

在重新复核

- 2026-03-17 主线 blind A/B
- 2026-03-17 near-real blind A/B
- 2026-03-20 项目状态重置

之后，当前更需要的不是继续细分
`candidate_v7`
旧 rows 重路由，
而是先回答一个更高层的问题：

- `v32`
  和
  `v64`
  这两个仍有讨论价值的研究基座，
  到底还有没有足够强的可听价值，
  值得继续消耗训练与分析预算。

因此本轮不启动新训练，
只导出一版
小而硬的决策关卡听审包。

## 本轮目标

只做两组 A/B：

1. `legacy stage2`
   vs
   `v32`
2. `legacy stage2`
   vs
   `v64`

样本只使用
`near_real_v1`
这 10 条固定资产，
不再新增 synthetic 扩包，
原因是这组样本已经覆盖：

- raw target only
- friend speech leakage
- music interference
- `guodegang` anchor
- target absent
- speech + music harder mix

## 使用的输入

### Manifest

- `data/references/real_eval_manifest_near_real_v1.jsonl`

### Checkpoint

- `legacy stage2`
  - `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- `v32`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt`
- `v64`
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v64_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_v23minus0002_ft1/best.pt`

### 导出命令

```powershell
.\python.exe scripts\eval\export_ab_inference_from_manifest.py `
  --manifest data\references\real_eval_manifest_near_real_v1.jsonl `
  --checkpoint-a experiments\checkpoints\baseline_stft_mask_stage2\best.pt `
  --checkpoint-b experiments\checkpoints\baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1\best.pt `
  --label-a legacy_stage2 `
  --label-b v32 `
  --output-dir reports\eval\decision_gate_listening_pack_near_real_v1_stage2_vs_v32_blind `
  --sample-rate 16000 `
  --blind
```

```powershell
.\python.exe scripts\eval\export_ab_inference_from_manifest.py `
  --manifest data\references\real_eval_manifest_near_real_v1.jsonl `
  --checkpoint-a experiments\checkpoints\baseline_stft_mask_stage2\best.pt `
  --checkpoint-b experiments\checkpoints\baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v64_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_v23minus0002_ft1\best.pt `
  --label-a legacy_stage2 `
  --label-b v64 `
  --output-dir reports\eval\decision_gate_listening_pack_near_real_v1_stage2_vs_v64_blind `
  --sample-rate 16000 `
  --blind
```

## 输出

### Pack A

- `reports/eval/decision_gate_listening_pack_near_real_v1_stage2_vs_v32_blind`

### Pack B

- `reports/eval/decision_gate_listening_pack_near_real_v1_stage2_vs_v64_blind`

两组目录均已包含：

- `README.md`
- `summary.json`
- `blind_key.json`
- `listening_sheet.csv`
- `listening_rubric.json`
- 每条样本的
  `mixture / reference / candidate_a / candidate_b`

## 当前建议的听审顺序

建议先听：

1. `stage2 vs v64`
   - 因为 `v64`
     是当前唯一仍可记作
     `closed_but_evidence_keep`
     的 dual-protect 候选
2. 再听
   `stage2 vs v32`
   - 作为研究基座对照，
     判断后续是否还需要继续沿 friend-side 研究树细分

## 当前停点

本轮只完成导包，
不做新的训练、
compare、
gate
或额外 proxy 细分。

下一步默认等待用户完成听审后，
再决定：

1. `v64`
   是否仍值得继续；
2. `v32`
   是否只保留为工程基座；
3. `candidate_v7`
   这条高粒度分析线
   是否应阶段性停止。
