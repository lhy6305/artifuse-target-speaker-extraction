# 2026-03-25 same_gender reverb proxy v2 target-present listening gate

## 背景

在
`same_gender_reverb_proxy_v2`
完成物化后，
当前最有价值的下一步
不是直接起训练，
而是先做一个：

- target-present
- same-gender
- speech-side reverb
- high-overlap

的小型 GUI 听审 gate。

这一步的目的不是再看
synthetic 平均分，
而是先确认：

- `v32`
  在这类更贴近
  `near_real_0006`
  家族的 synthetic proxy 上，
  是否真的能被人耳稳定听成：
  - 少泄漏
  - 但不更空
  - 不更薄

## 新导出的 listening pack

当前已导出：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind`

对比对象：

- `legacy_stage2`
- `v32`

输入 manifest：

- `data/synthetic/val_manifest_same_gender_reverb_proxy_v2.jsonl`

导包命令：

```powershell
.\python.exe scripts/eval/export_ab_listening_pack.py `
  --manifest data/synthetic/val_manifest_same_gender_reverb_proxy_v2.jsonl `
  --checkpoint-a experiments/checkpoints/baseline_stft_mask_stage2/best.pt `
  --checkpoint-b experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt `
  --label-a legacy_stage2 `
  --label-b v32 `
  --focus-recipes target_clean_speech `
  --max-samples 10 `
  --stable-count 2 `
  --blind `
  --output-dir reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind
```

## 当前 pack 组成

当前候选总量：

- `100`

当前导出样本数：

- `10`

当前导出的 sample-id：

- `val_000166`
- `val_000013`
- `val_000191`
- `val_000167`
- `val_000212`
- `val_000236`
- `val_000252`
- `val_000011`
- `val_000105`
- `val_000092`

这些样本都来自：

- `target_clean_speech`
- `target_full`
- high-overlap
- male-only clean speech interference
- speech-side reverb only

## 资产审计

已跑：

```powershell
.\python.exe scripts/eval/audit_listening_pack_assets.py `
  --pack-dir reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind `
  --require-target
```

结果：

- `all_mono = true`
- `all_have_target = true`
- `missing_target_count = 0`
- `non_mono_file_count = 0`

落盘：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind/asset_audit_summary.json`

## bandwidth 预分析

已跑：

```powershell
.\python.exe scripts/eval/analyze_listening_pack_bandwidth.py `
  --pack-dir reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind
```

结果：

- `10` 条样本里：
  - `9` 条未触发明确窄带判定
  - `1` 条触发 heuristic narrow-band 黄灯

当前口径：

- 这只是预听审黄灯，
  不能代替人耳；
- 但后续听审时，
  应额外盯：
  - 电话音
  - 高频存在感
  - target 是否变薄

落盘：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind/bandwidth_analysis/summary.json`

## 下一步

当前这包已经 ready for GUI。

启动命令：

```powershell
.\python.exe scripts/eval/listening_pack_gui.py --pack-dir reports/eval/ab_listening_pack_same_gender_reverb_proxy_v2_stage2_vs_v32_blind
```

当前建议你在 GUI 里重点盯：

1. target 是否更空、更薄
2. consonant / edge transient
   是否被削掉
3. suppress 更强时，
   是否顺带出现电话音
4. 高 overlap 样本里，
   `v32`
   是否真的是
   少泄漏但不伤 target

听完导出后，
下一步就不是再导包，
而是：

1. GUI 解盲
2. 合并现有 objective / bandwidth 先验
3. 决定：
   - `same_gender_reverb_proxy_v2`
     只保留为 pre-screen
   - 还是足够支持
     第一轮 focused training
