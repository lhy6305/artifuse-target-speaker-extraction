# 2026-03-25 定向评估资产物化

## 背景

在确认当前阶段可以结题后，
若后续仍要继续，
默认不再回到
friend-side
大树，
而是只保留：

- `v32`
  基座上的
  `same_gender_reverb_like`
  与 bandwidth guardrail
  focused follow-up

因此本轮不启动训练，
只把这条窄线需要的入口资产先物化好。

## 已补好的导包底座

本轮已先完成：

1. `near_real_v1`
   重建
   - 现在每条样本目录都带：
     - `target.wav`
   - manifest 也带：
     - `target_audio_path`
2. `scripts/eval/export_ab_inference_from_manifest.py`
   已更新为：
   - 优先导出 `target.wav`
   - 统一导出为单声道
3. 新增：
   - `scripts/eval/audit_listening_pack_assets.py`
   用于在听审前检查：
   - mono
   - target.wav

## 新物化的 focused manifest

### 1. same-gender / mild-reverb seed family

当前先用最明确的两条 seed：

- `near_real_0006`
- `near_real_0009`

生成：

- `data/references/real_eval_manifest_same_gender_reverb_like_v1.jsonl`

作用：

- 作为下一阶段
  target present / absent
  外部同类男声风险的最小 near-real family 入口

当前样本数：

- `2`

### 2. bandwidth guardrail v1

当前先固定四条：

- `near_real_0001`
- `near_real_0002`
- `near_real_0006`
- `near_real_0009`

生成：

- `data/references/real_eval_manifest_bandwidth_guardrail_v1.jsonl`

作用：

- `0001 / 0002`
  负责看 raw target only
  会不会被削窄；
- `0006 / 0009`
  负责看
  same-gender external speech
  场景下，
  为了 suppress
  是否把频带一起削掉。

当前样本数：

- `4`

## 下一阶段固定执行顺序

若后续起
`v32`
focused follow-up，
默认命令顺序应固定为：

### 1. 导出 same-gender reverb-like 听审包

```powershell
.\python.exe scripts\eval\export_ab_inference_from_manifest.py `
  --manifest data\references\real_eval_manifest_same_gender_reverb_like_v1.jsonl `
  --checkpoint-a experiments\checkpoints\baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1\best.pt `
  --checkpoint-b <candidate_checkpoint> `
  --label-a v32 `
  --label-b <candidate_label> `
  --output-dir <pack_dir> `
  --blind
```

### 2. 听审前先做资产审计

```powershell
.\python.exe scripts\eval\audit_listening_pack_assets.py --pack-dir <pack_dir> --require-target
```

若：

- `all_mono != true`
- 或 `all_have_target != true`

则先修导包，
不进入听审。

### 3. 听审后固定跑 bandwidth 分析

```powershell
.\python.exe scripts\eval\analyze_listening_pack_bandwidth.py --pack-dir <pack_dir>
```

### 4. synthetic focused pre-screen

继续保留：

- `data/synthetic/train_manifest_guodegang_proxy_v1.jsonl`
- `data/synthetic/val_manifest_guodegang_proxy_v1.jsonl`

作为训练前的 focused pre-screen。

## 当前 stop rule

下一阶段若继续，
默认只要出现任一条，
就直接停：

1. same-gender reverb-like
   near-real family
   人耳没有相对 `v32`
   的稳定收益
2. `near_real_0006`
   更差
3. `near_real_0009`
   更差
4. raw target only
   更差
5. bandwidth analysis
   显示候选更窄带

## 当前结论

截至本轮，
当前已经不缺“继续推进的大方向”，
而是已经把：

- 导包口径
- focused near-real family
- bandwidth guardrail
- stop rule

这四件事先落成了可执行资产。

也就是说，
如果后续继续，
默认不再需要临时拼口径，
而是按这套 fixed workflow
直接执行即可。
