# 2026-03-16 Hard Recipe Control

## 本次目的

stage3 的 hard-recipe-focus 结果虽然给出了一些方向性信息，但同时改变了：

- 数据规模
- recipe profile

归因不够干净。

所以本次补了一个更严格的对照实验：

- 保持与 stage2 相同的数据规模
- 只改变 train recipe profile

## 对照设置

训练数据：

- train: `2048`
- val: `512`

recipe profile：

- train: `hard_recipe_focus`
- val: `default`

说明：

- 这轮的目的是隔离 `recipe profile` 本身的影响。

## 对照训练

命令：

```powershell
.\python.exe scripts\train\train_stft_mask_baseline.py --epochs 6 --batch-size 16 --log-every 50 --output-dir experiments\checkpoints\baseline_stft_mask_stage2_hard_recipe_control
```

结果：

- best val loss: `0.024526699155103415`

## 对照评估

命令：

```powershell
.\python.exe scripts\eval\eval_stft_mask_baseline.py --checkpoint experiments\checkpoints\baseline_stft_mask_stage2_hard_recipe_control\best.pt --output-dir reports\eval\baseline_stft_mask_stage2_hard_recipe_control_eval --save-audio-count 6
```

对照组指标：

- `loss`: `0.030003366100572748`
- `waveform_l1`: `0.01401316752890125`
- `stft_l1`: `0.03198039711060119`
- `sisdr_db`: `-19.30052874609828`

## 与 stage2 默认配比对比

stage2 默认配比：

- `loss`: `0.024477669885527575`
- `waveform_l1`: `0.013033535506110638`
- `stft_l1`: `0.02288826880248962`
- `sisdr_db`: `-10.324090986978263`

hard-focus 对照相对 stage2 默认配比：

- `loss`: `+0.005525696215045173`
- `waveform_l1`: `+0.0009796320227906108`
- `stft_l1`: `+0.009092128308111569`
- `sisdr_db`: `-8.976437759120017 dB`

## 对难 recipe 的影响

本次想补强的两个难 recipe 也没有被救回来，反而更差：

- `target_clean_speech`
  - `sisdr_db` 变化：`-9.127269 dB`
- `target_clean_plus_music`
  - `sisdr_db` 变化：`-10.181521 dB`

## 当前结论

当前 baseline 结构下，pure `hard_recipe_focus` 不是更好的默认训练分布。

更准确地说：

- 它不是“定向补强难样本”
- 而是“打乱了整体训练分布，并让整体结果明显退化”

## 后续动作

已执行：

- 当前 synthetic 工作集恢复回 stage2 默认配比：
  - train: `2048 / default`
  - val: `512 / default`

后续建议：

1. 不把 pure `hard_recipe_focus` 当作主线。
2. 若继续调数据分布，优先尝试更温和的混合比例。
3. 或直接把下一阶段工作重点转到模型增强，而不是继续极端调样本配比。
