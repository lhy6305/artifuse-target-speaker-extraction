# 2026-03-16 Reference Conditioning Upgrade

## 本次目的

在确认 pure `hard_recipe_focus` 不是更优主线之后，当前主线从“继续极端调数据配比”转向“先做模型侧增强”。

本次选择的切入点是：

- 不改 synthetic 分布
- 不大改训练框架
- 先增强 baseline 的 reference conditioning

## 本次改动

本轮把 baseline 的 reference conditioning 从旧版：

- `legacy_bias`
  - reference 频谱做简单全局统计
  - 作为加性偏置注入 mixture 分支

升级为新版：

- `ref_film`
  - reference 频谱先做逐帧编码
  - 再做 attention pooling
  - 通过 FiLM 风格的 scale / shift 调制 mixture 特征
  - 额外拼接一个 mixture-vs-reference 的 cosine similarity 标量特征

同时补了实验兼容性：

- 训练 checkpoint 现已保存 `model_config`
- eval 脚本会按 checkpoint 的 `model_config` 还原模型
- 对历史旧 checkpoint，若检测到 `condition_proj.weight`，则自动按 `legacy_bias` 兼容加载

## 兼容性验证

命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage2\best.pt --output-dir tmp\legacy_stage2_eval_check --save-audio-count 0
```

结果：

- 旧 `stage2` checkpoint 可被新版 eval 脚本正常加载
- 指标与历史记录一致：
  - `loss`: `0.024477669885527575`
  - `waveform_l1`: `0.013033535506110638`
  - `stft_l1`: `0.02288826880248962`
  - `sisdr_db`: `-10.324090986978263`

## 新结构 smoke 训练

命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 1 --batch-size 2 --log-every 2 --max-steps 6 --output-dir experiments\checkpoints\baseline_stft_mask_ref_film_smoke
```

训练时间：

- start: `2026-03-16T20:55:46`
- end: `2026-03-16T20:55:52`
- elapsed: `6.136 sec`

训练配置：

- epochs: `1`
- batch size: `2`
- global steps: `6`
- device: `cuda`
- model:
  - `conditioning_mode`: `ref_film`
  - `n_fft`: `512`
  - `hop_length`: `128`
  - `win_length`: `512`
  - `hidden_dim`: `256`
  - `reference_dim`: `128`
  - `gru_layers`: `2`

best val loss：

- `0.04189818295708392`

产物：

- `experiments/checkpoints/baseline_stft_mask_ref_film_smoke/latest.pt`
- `experiments/checkpoints/baseline_stft_mask_ref_film_smoke/best.pt`
- `experiments/checkpoints/baseline_stft_mask_ref_film_smoke/train_summary.json`

## 新结构 smoke 评估

命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_ref_film_smoke\best.pt --output-dir reports\eval\baseline_stft_mask_ref_film_smoke_eval --save-audio-count 4
```

评估指标：

- `loss`: `0.04189818295708392`
- `waveform_l1`: `0.019178545579052297`
- `stft_l1`: `0.0454392746432859`
- `sisdr_db`: `-21.66497934702784`

产物：

- `reports/eval/baseline_stft_mask_ref_film_smoke_eval/eval_summary.json`
- `reports/eval/baseline_stft_mask_ref_film_smoke_eval/samples/`

## 当前结论

这轮的结论是“结构升级已打通并保持历史 checkpoint 可复验”，而不是“`ref_film` 已经优于旧结构”。

更准确地说：

1. 新结构代码可训练、可评估、可落盘。
2. 旧结构 checkpoint 没有因为脚本升级而失去可评估性。
3. 当前还缺少同数据规模、同训练预算下的正式 A/B 对照。

## stage2 正式对照

为了不把判断停留在 smoke 层面，本轮继续补了一个与 legacy stage2 同预算的正式对照：

- synthetic 分布：当前工作区 `2048 / 512 / default`
- epochs: `6`
- batch size: `16`
- model: `ref_film`

训练命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 6 --batch-size 16 --log-every 50 --output-dir experiments\checkpoints\baseline_stft_mask_stage2_ref_film
```

训练结果：

- start: `2026-03-16T20:58:18`
- end: `2026-03-16T20:59:45`
- elapsed: `87.297 sec`
- best val loss: `0.019916923949494958`

评估命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage2_ref_film\best.pt --output-dir reports\eval\baseline_stft_mask_stage2_ref_film_eval --save-audio-count 8
```

评估指标：

- `loss`: `0.023573425842187135`
- `waveform_l1`: `0.013290688400957151`
- `stft_l1`: `0.02056547490064986`
- `sisdr_db`: `-10.559770353371277`

相对 legacy stage2 的变化：

- `loss`: `-0.0009042440433404401`
- `waveform_l1`: `+0.00025715289484651313`
- `stft_l1`: `-0.0023227939018397586`
- `sisdr_db`: `-0.23567936639301403 dB`

按 recipe 看，当前 `ref_film` 的表现并不统一：

- `target_clean_speech`
  - `sisdr_db` 相对 legacy: `+0.358857 dB`
- `target_clean_plus_music`
  - `sisdr_db` 相对 legacy: `+0.014251 dB`
- `target_hard_speech`
  - `sisdr_db` 相对 legacy: `-0.656944 dB`
- `target_hard_plus_music`
  - `sisdr_db` 相对 legacy: `-0.490780 dB`
- `target_music`
  - `sisdr_db` 相对 legacy: `-0.901662 dB`

## 更新后的结论

现在可以把结论从“尚无正式对照”更新为：

1. `ref_film` 已经具备完整实验条件，不再只是 smoke 原型。
2. 在当前 stage2 同预算设置下，它确实改善了：
   - 总 `loss`
   - `stft_l1`
3. 但它没有改善当前更关键的 `sisdr_db`，反而整体略退化。
4. 因此当前还不能把 `ref_film` 升为默认主线结构。

更准确地说，`ref_film` 当前更像是：

- 对某些 clean recipe 有帮助；
- 但会伤到一部分 hard / music 相关场景；
- 需要继续调参或配套损失，不能直接替换 legacy baseline。

## 下一步

1. 当前默认主线仍保持 `legacy_bias + stage2 default`。
2. 如果继续推进 `ref_film`，优先尝试：
   - 调整损失权重，避免只优化频谱重建
   - 或补更适合 hard/music 场景的条件化设计
3. 后续所有模型升级都继续保留“旧 checkpoint 可复验”作为硬要求。
