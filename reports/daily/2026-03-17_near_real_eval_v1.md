# 2026-03-17 Near-Real Eval V1

## 背景

在主线 synthetic blind A/B 已经给出“`legacy stage2` 更稳”的前提下，当前更缺的不是继续扫 synthetic 近邻分支，而是：

1. 补一套可复用的真实/近真实验证清单；
2. 让主线对照能直接在更接近真实输入的样本上开听。

当前仓库里还没有真正整理好的“现场多说话真实录音验证集”，但已经有几类更接近真实域的原料：

- `data_in/source_dataset_ly65_raw.wav`
- `data_in/friend_dataset_fuhuo_raw_concat.wav`
- `data_in/郭德纲 生肉.mp4`
- `data_in/pure_music_dataset/*.mp3`
- `data/manifests/target_reference_pool.jsonl`

因此本轮先落一个可复现的 `near_real_v1`，明确把它定义为：

- 近真实验证集
- 不是最终真实验证集

## 新增脚本

- `scripts/data/build_near_real_eval_manifest.py`

作用：

- 从目标原始长录音中，按历史切片时间戳裁出 raw target clip；
- 从 friend 长录音、郭德纲素材、纯音乐中裁出真实干扰片段；
- 组合出一组 deterministic 的 near-real mixture/reference 对；
- 产出正式 manifest 与样本目录。

## 生成命令

```powershell
.\python.exe scripts\data\build_near_real_eval_manifest.py --force-clean
```

## 产出

manifest：

- `data/references/real_eval_manifest_near_real_v1.jsonl`

样本目录：

- `data/references/real_eval_near_real_v1/`

当前总样本数：

- `10`

## 当前样本覆盖

### 目标存在

- `target_raw_only`
- `target_plus_friend_speech`
- `target_plus_music`
- `target_plus_guodegang_speech`
- `target_plus_friend_plus_music`

### 目标缺席

- `target_absent_friend_only`
- `target_absent_guodegang_only`
- `target_absent_friend_plus_music`

大白话讲，就是这版样本不再只看“合成 clean target”，而是开始看：

- 原始 target 录音会不会被模型削坏；
- 真实人声干扰进来后会不会压不住；
- target 不在场时会不会乱吐目标声音。

## blind A/B 导出

命令：

```powershell
.\python.exe scripts\eval\export_ab_inference_from_manifest.py --manifest data\references\real_eval_manifest_near_real_v1.jsonl --checkpoint-a experiments\checkpoints\baseline_stft_mask_stage2\best.pt --checkpoint-b experiments\checkpoints\baseline_stft_mask_stage2_ref_film_sisdr0005\best.pt --label-a legacy_stage2 --label-b ref_film_sisdr0005 --output-dir reports\eval\ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind --blind
```

输出目录：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind/`

当前 blind 包已包含：

- `10` 条样本目录
- `summary.json`
- `blind_key.json`
- `listening_sheet.csv`
- `listening_rubric.json`

## 启动听评

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind
```

## 当前结论

截至本轮：

1. 仓库里已经不再只有模板，已有第一版可听的 near-real 验证清单。
2. 主线对照 `legacy stage2 vs ref_film_sisdr0005` 已经能直接在 near-real 样本上做 blind A/B。
3. 这一步仍然不能叫“真实验证完成”，因为：
   - mixture 仍由本地规则拼出；
   - 还不是现场录制的真实混合输入。

## 下一步

1. 优先听：
   - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind/`
2. 若 near-real 听感仍明显偏向 `legacy stage2`，则当前更没有理由把 `ref_film_sisdr0005` 升为默认主线。
3. 若后续补到真正现场样本，可继续沿用：
   - `scripts/eval/export_ab_inference_from_manifest.py`
   - `data/references/real_eval_manifest_template.jsonl`
   这条路径扩展到真正的 real eval。
