# 2026-03-17 Reverb Probe Follow-up

## 背景

在 `near_real_v1` 听评把问题进一步收敛到：

1. 混响输入处理不稳；
2. `target absent` 时仍会吐出目标样瞬态；
3. 处理中间伪影可能被误当作目标保留。

之后，本轮没有继续开新的结构或 loss 近邻分支，而是先沿 synthetic realism 做了两轮 small reverb probe。

## 代码与数据生成器补充

本轮在 `scripts/data/build_synthetic_dataset.py` 上新增了：

- `--output-tag`

作用：

- 让 probe 数据写到独立的 `data/synthetic/*_{tag}` 目录；
- 同时把 manifest 和 `summary.json` 也按 tag 隔离；
- 避免 side experiment 覆盖主线默认的 `train_manifest.jsonl / val_manifest.jsonl`。

当前与轻混响相关的入口变为：

- `--target-reverb-prob`
- `--speech-reverb-prob`
- `--output-tag`

## Probe V1: `legacy_reverb_probe_v1`

### 观测到的输入配置

- synthetic tag：`legacy_reverb_probe_v1`
- train / val：`256 / 64`
- `target_reverb_prob=0.35`
- `speech_reverb_prob=0.45`
- warm-start：`experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- 训练输出：`experiments/checkpoints/baseline_stft_mask_stage2_legacy_reverb_probe_v1/`

### 训练结果

- `best_val_loss`: `0.019016`
- 训练预算：`4 epochs / batch size 16 / lr 3e-4 / 64 steps`

### 评测结果

probe 集上先看“旧主线直接跑 probe 数据”：

- `reports/eval/baseline_stft_mask_stage2_on_legacy_reverb_probe_v1_eval/`
- `sisdr_db = -9.565`

再看 probe checkpoint 自己：

- `reports/eval/baseline_stft_mask_stage2_legacy_reverb_probe_v1_on_probe_eval/`
- `sisdr_db = -9.821`

差值：

- probe val 相对 `legacy stage2`：`avg_sisdr_delta_db = -0.194`

默认 val 上也回退：

- `reports/eval/compare_stage2_vs_legacy_reverb_probe_v1_on_default/`
- `avg_sisdr_delta_db = -0.264`

当前判断：

- 这版基本可以视为 joint reverb 的反例，不再继续扩大。

### 听评准备

已导出 near-real blind 包：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/`

当前仍未完成听评；`listening_sheet.csv` 为空，且尚无 `listening_results_summary.json`。

## Probe V2: `legacy_speechreverb_probe_v2`

### 观测到的输入配置

- synthetic tag：`legacy_speechreverb_probe_v2`
- train / val：`256 / 64`
- `target_reverb_prob=0.0`
- `speech_reverb_prob=0.55`
- warm-start：`experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- 训练输出：`experiments/checkpoints/baseline_stft_mask_stage2_legacy_speechreverb_probe_v2/`

### 训练结果

- `best_val_loss`: `0.019050`
- 训练预算：`4 epochs / batch size 16 / lr 3e-4 / 64 steps`

### 评测结果

默认 val：

- `reports/eval/compare_stage2_vs_legacy_speechreverb_probe_v2_on_default/`
- `avg_sisdr_delta_db = -0.183`

probe val：

- `reports/eval/compare_stage2_vs_legacy_speechreverb_probe_v2_on_probe/`
- `avg_sisdr_delta_db = -0.195`

probe 集上局部观察：

- `target_clean_speech`: `+0.015 dB`
- `target_clean_plus_music`: `+0.033 dB`
- 但 `target_hard_plus_music`、`target_music`、`target_hard_speech` 仍整体回退

当前判断：

- `v2` 明显比 `v1` 更接近“可能有用”的方向；
- 但它还不是客观转正的候选，暂时不能升成新的默认主线或直接扩到更大训练规模。

## 新导出的 near-real A/B 包

为避免只靠 synthetic 指标下判断，本轮已额外导出：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`

启动 GUI 的命令为：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind
```

## 当前结论

截至本轮，当前最值得保留的判断是：

1. `legacy_reverb_probe_v1` 已可视为反例，不继续。
2. `legacy_speechreverb_probe_v2` 是目前唯一值得继续人工复核的 reverb realism 候选。
3. 但 `v2` 仍未在默认 val 或 probe val 上形成客观正增益，因此下一步必须先看 near-real 人听，而不是立刻扩训练规模。

## 下一步

1. 人工优先听：
   - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`
2. 如需反例对照，再回看：
   - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/`
3. 若 `v2` 在 near-real 上仍不占优，则先停止继续扩大 reverb 训练预算，转回：
   - 更贴近问题类型的 realism 设计；
   - 单独盯 `raw target only` 与 `target absent` guardrail。

## V2 Near-Real Listening Review Update

上述第 1 步现已完成。当前 GUI 落盘结果位于：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/listening_sheet.csv`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/listening_results_summary.json`

盲态计数为：

- `file_a`: `1`
- `file_b`: `0`
- `tie`: `8`
- `uncertain`: `1`

结合 `blind_key.json` 解盲后，真实模型偏好为：

- `legacy_stage2`: `1`
- `legacy_speechreverb_probe_v2`: `0`
- `tie`: `8`
- `uncertain`: `1`

当前结论不是“`v2` 明显更差很多”，而是：

1. 它没有形成任何明确可听优势。
2. 大多数样本都落在“几乎平手”区间。
3. 但新增暴露出的主观问题更像：
   - 电话音
   - 降采样感
   - 某些频率被削掉后的带宽收窄

这说明：

- `v2` 可能确实在往“压混响尾巴”方向动；
- 但代价不是简单的噪声或残留，而是更像频谱被掐瘦，导致人耳觉得发闷、发窄、像电话。

因此当前动作更新为：

1. 不继续扩大 `legacy_speechreverb_probe_v2` 的训练预算。
2. 后续若继续做 realism，优先补：
   - 频带缺失诊断
   - 更细的频谱侧客观检查
3. 再决定是否需要重新设计更贴近症状的 realism 增强，而不是继续沿现有概率配方往上加。

## Quick Spectral Spot Check

在收到“更像电话音 / 降采样感”的主观反馈后，本轮又对 near-real blind 包里的输出做了一次 very quick 频谱抽检。

当前观察到的点是：

1. 没有看到一种“所有样本都出现明显全局高频整体塌掉”的简单低通模式。
2. raw target only 的两条样本上，`legacy stage2` 与 `legacy_speechreverb_probe_v2` 的全局频谱重心差异很小。
3. 但在部分更复杂样本上，`v2` 更像是：
   - 某些局部频段被掐瘦；
   - 或清辅音、吹气声、尾部瞬态被削掉；
   - 因此主观上会被听成“电话音 / 频带被收窄”。

这和听评备注里的现象是对得上的，例如：

- `near_real_0006`：
  - A/B 都在目标尾部的清辅音或吹气声位置发生截断；
- `near_real_0005`：
  - 唯一非平手样本里，用户更偏向 `legacy stage2`，并备注旧主线前段多保住了一点噪声级别的目标真值。

因此当前更倾向把问题描述成：

- 不是简单的“整段被整体低通”；
- 而是更接近：
  - 局部频带缺失
  - 高频瞬态保真不足
  - 清辅音边缘被过度压制

这也说明后续若补客观诊断，不能只看全局高频能量均值；更适合补：

1. 分频带能量占比的逐样本对照；
2. 针对清辅音 / 尾音瞬态的局部频谱检查；
3. 必要时增加更贴近“带宽收窄感”的主观标签或诊断脚本。

## Diagnostic Script Added

为把这类“电话音 / 带宽收窄感”从主观备注推进到可复跑分析，本轮已新增：

- `scripts/eval/analyze_listening_pack_bandwidth.py`

当前脚本会对 listening pack 中的 `candidate_a.wav / candidate_b.wav` 输出：

- `rolloff_95_hz`
- `upper_vs_mid_db`
- `frame_upper_share_p90`
- 逐样本 A/B delta
- 一个面向“带宽更窄”的 heuristic flag

已实际跑在：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/bandwidth_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/bandwidth_analysis/`

当前观察到的补充结论是：

1. `legacy_speechreverb_probe_v2` 没有表现成“全局统一更低通”。
2. 但在 `near_real_0005`、`near_real_0007` 这类样本上，脚本会把 `v2` 标成更窄带的一侧，这和主观听到的“电话音”是对得上的。
3. `legacy_reverb_probe_v1` 的带宽收窄 flag 更频繁，说明它在这类问题上确实比 `v2` 更重。

## Transient Diagnostic Script Added

在带宽诊断之外，本轮还新增了：

- `scripts/eval/analyze_listening_pack_transients.py`

它的目标不是看“全局有没有低通”，而是看：

1. mixture 中出现高频瞬态的那些帧；
2. candidate 在这些帧上的 `presence(3k-8k)` 保留；
3. 这种保留相对 `mid(0.8k-3k)` 是否被额外削弱。

已实际跑在：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/transient_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/transient_analysis/`

### 当前新观察

对 `legacy_speechreverb_probe_v2`：

- `near_real_0005`
  - 被标成 `legacy_speechreverb_probe_v2` 更 transient-lossy
  - 且这条正好是当前唯一明确偏向 `legacy_stage2` 的样本
- `near_real_0007`
  - 被标成 `legacy_speechreverb_probe_v2` 更 transient-lossy
- `near_real_0010`
  - 也被标成 `legacy_speechreverb_probe_v2` 更 transient-lossy

对 `legacy_reverb_probe_v1`：

- 同类 flag 更频繁，且强度通常更大
- 这与此前“`v1` 比 `v2` 更差”的整体判断保持一致

### 当前理解

这进一步支持了当前主观结论：

- `legacy_speechreverb_probe_v2` 的问题不只是“像被低通”；
- 更具体地说，是：
  - 高频瞬态相对中频保留不足；
  - 清辅音、吹气声、尾部边缘更容易被削掉；
  - 所以才会听成“电话音 / 降采样感”。

因此当前 realism 方向的判断进一步收敛为：

1. 不继续扩大 `v2` 的训练预算。
2. 后续若继续做 realism，优先盯：
   - 局部频带缺失
   - 瞬态高频保真
3. 所有后续 near-real 候选，默认都应补跑：
   - `bandwidth_analysis`
   - `transient_analysis`

## Transient Loss Hook Added

在上述两版诊断脚本之外，本轮还把“高频瞬态 / 清辅音保真”进一步接到了 baseline 训练入口。

新增内容：

- `src/tse_prefix/pipeline/baseline_train.py`
  - 新增 `transient_presence_l1_loss(...)`
  - `compute_losses(...)` 现支持 `transient_weight` 与对应频带参数
- `scripts/train/train_stft_mask_baseline.py`
  - 新增 `--loss-transient-weight`
  - checkpoint 与 `train_summary.json` 会记录 `transient_presence_l1`
- `scripts/eval/eval_stft_mask_baseline.py`
  - eval summary、分组统计、样本 meta 现会同步记录 `transient_presence_l1`

本轮没有直接开正式 budget 的 transient-loss 新训练，而是先做了最小烟测：

- 训练：
  - `experiments/checkpoints/baseline_stft_mask_transient_smoke/`
- 评估：
  - `reports/eval/baseline_stft_mask_transient_smoke_eval/`

烟测结果说明：

1. 新 loss 已能实际参与 forward / backward / checkpoint / eval。
2. `sample_rate` 已显式进入 `loss_config`，避免把 `16k` 写死在频带计算里。
3. 当前仓库状态已从“只有瞬态诊断脚本”推进到“已有可训练 loss hook，可直接开第一轮小预算对照”。 
