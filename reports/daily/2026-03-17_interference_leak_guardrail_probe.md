# 2026-03-17 Interference Leak Guardrail Probe

## 背景

在完成：

- `bandwidth_analysis`
- `transient_analysis`
- `tradeoff_analysis`

之后，当前 transient-loss 线的核心问题已经比较清楚：

1. `legacy_transient_probe_v2`
2. `legacy_transient_focus_probe_v4`

都不是“纯修电话音”的分支，而更像：

- 多保一点 target
- 同时也多漏一点 interference

因此本轮没有继续扫更窄的 transient selector，而是直接补一条显式 leak guardrail：

- `interference_projection_loss(...)`

目标不是继续拉高 target retention，而是把：

- `mixture - target`

这条 synthetic 干扰轨在模型输出里的投影占比显式压下去。

## 代码改动

入口已接到：

- `src/tse_prefix/pipeline/baseline_train.py`
- `src/tse_prefix/pipeline/__init__.py`
- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

新增内容：

1. `interference_projection_loss(...)`
   - 对 `interference = mixture - target` 做单向投影；
   - 用投影能量占输出能量的比例作为 loss / metric；
   - 当前命名为：
     - `interference_projection_ratio`
2. 训练脚本新增：
   - `--loss-interference-weight`
   - `--loss-interference-focus-recipes`
   - `--loss-interference-focus-patterns`
   - `--loss-interference-min-target-ratio`
   - `--loss-interference-max-target-ratio`
3. eval summary、train history、sample meta 当前都会记录：
   - `interference_projection_ratio`

## Metric Baseline

先用新版 eval 给几条已有分支补一次 leakage metric 基线。

### `legacy stage2`

- eval:
  - `reports/eval/baseline_stft_mask_stage2_eval_with_leak_metric/`
- 当前：
  - `sisdr_db = -10.324`
  - `transient_presence_l1 = 0.756`
  - `interference_projection_ratio = 0.0713`

### `legacy_transient_probe_v2`

- eval:
  - `reports/eval/baseline_stft_mask_stage2_legacy_transient_probe_v2_eval_with_leak_metric/`
- 当前：
  - `sisdr_db = -10.626`
  - `transient_presence_l1 = 0.583`
  - `interference_projection_ratio = 0.0771`

### `legacy_transient_focus_probe_v4`

- eval:
  - `reports/eval/baseline_stft_mask_stage2_legacy_transient_focus_probe_v4_eval_with_leak_metric/`
- 当前：
  - `sisdr_db = -10.564`
  - `transient_presence_l1 = 0.278`
  - `interference_projection_ratio = 0.0801`

当前判断：

1. 新 metric 的量级是稳定可读的，默认 val 大约落在 `0.07 ~ 0.08`。
2. `v2 / v4` 虽然压低了 transient 指标，但 leakage metric 反而更高。
3. 这和前面的 near-real trade-off 诊断是一致的。

## Smoke Validation

先做了一轮最小 smoke，确认新 loss 真能参与 forward / backward：

- checkpoint:
  - `experiments/checkpoints/baseline_stft_mask_interference_smoke/`
- eval:
  - `reports/eval/baseline_stft_mask_interference_smoke_eval/`

smoke 配置：

- warm-start:
  - `legacy_transient_focus_probe_v4`
- `transient_weight = 0.002`
- `interference_weight = 0.05`

只跑 `1 step` 后，当前 full eval 为：

- `sisdr_db = -11.768`
- `transient_presence_l1 = 0.330`
- `interference_projection_ratio = 0.0478`

当前判断：

1. 这版明显过猛，`SI-SDR` 退得太多；
2. 但方向是对的：
   - `interference_projection_ratio`
   - 确实被快速压下来了。

因此后续正式 probe 改用更保守的权重。

## Probe V1: `legacy_transient_leakguard_probe_v1`

### 配置

- 输出目录：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v1/`
- warm-start：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_focus_probe_v4/best.pt`
- 主配置：
  - `conditioning_mode = legacy_bias`
  - `epochs = 3`
  - `batch_size = 16`
  - `lr = 3e-4`
- transient 分支：
  - `transient_weight = 0.002`
  - `transient_focus_recipes = [target_clean_speech]`
  - `transient_focus_patterns = [target_full, target_absent_head, target_absent_tail]`
- leak guardrail 分支：
  - `interference_weight = 0.01`
  - `interference_focus_recipes =`
    - `target_clean_speech`
    - `target_hard_speech`
    - `target_music`
    - `target_clean_plus_music`
    - `target_hard_plus_music`
    - `target_singing_vocal`
  - `interference_focus_patterns =`
    - `target_full`
    - `target_absent_head`
    - `target_absent_tail`
    - `target_intermittent`

### Synthetic Eval

eval 产物：

- `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v1_eval/`

当前指标：

- `loss = 0.025120`
- `waveform_l1 = 0.012895`
- `stft_l1 = 0.022470`
- `sisdr_db = -9.492`
- `transient_presence_l1 = 0.272716`
- `interference_projection_ratio = 0.044442`

对比 `legacy stage2`：

- `sisdr_db: -10.324 -> -9.492`
- `interference_projection_ratio: 0.0713 -> 0.0444`

对比 `legacy_transient_focus_probe_v4`：

- `sisdr_db: -10.564 -> -9.492`
- `interference_projection_ratio: 0.0801 -> 0.0444`

### Synthetic Compare

默认 val compare：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v1_on_default/`
- `avg_sisdr_delta_db = +0.849772`
- `improved_count = 376`
- `regressed_count = 83`

相对 `legacy_transient_focus_probe_v4`：

- `reports/eval/compare_v4_vs_legacy_transient_leakguard_probe_v1_on_default/`
- `avg_sisdr_delta_db = +1.077438`
- `improved_count = 459`
- `regressed_count = 35`

`target_clean_speech`：

- `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v1_on_clean_speech/`
- `avg_sisdr_delta_db = +1.235570`

分 recipe 观察，相对 `legacy stage2` 当前全部转正：

- `target_clean_speech: +1.236 dB`
- `target_clean_plus_music: +0.915 dB`
- `target_hard_speech: +0.688 dB`
- `target_hard_plus_music: +0.875 dB`
- `target_music: +0.445 dB`
- `target_only: +0.529 dB`
- `target_singing_vocal: +0.443 dB`

而 leakage metric 也不是只在单一 recipe 上好看，而是几乎全线下降。例如：

- `target_clean_speech: 0.0593 -> 0.0286`
- `target_hard_speech: 0.0728 -> 0.0540`
- `target_music: 0.0980 -> 0.0687`
- `target_clean_plus_music: 0.0585 -> 0.0313`

当前判断：

1. 这是目前仓库里第一次出现：
   - `SI-SDR` 大幅正增益
   - 同时 `interference_projection_ratio` 也明显下降
2. 从 synthetic 角度看，它已经明显强于：
   - `legacy stage2`
   - `legacy_transient_focus_probe_v4`

## Near-Real Blind Pack Exported

已导出：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v1_blind/`

## Near-Real Auto Diagnostics

已补跑：

- `bandwidth_analysis`
- `transient_analysis`
- `tradeoff_analysis`

对应目录：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v1_blind/bandwidth_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v1_blind/transient_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v1_blind/tradeoff_analysis/`

### 带宽结论

解码后：

- `legacy_transient_leakguard_probe_v1`: `2`
- `legacy_stage2`: `0`
- `tie`: `8`

当前理解：

- 至少没有比 `legacy_transient_focus_probe_v4` 更糟；
- 但也没有把“窄带化风险”完全清零。

### 瞬态结论

解码后：

- `legacy_transient_leakguard_probe_v1`: `7`
- `legacy_stage2`: `1`
- `tie`: `2`

当前理解：

- 这项和 `v2 / v4` 基本同量级；
- 说明显式 leak guardrail 还没有把 near-real 的瞬态 side effect 真正救正。

### Trade-Off 结论

解码后计数：

- `better_source_retention`
  - `legacy_transient_leakguard_probe_v1 = 2`
  - `legacy_stage2 = 3`
  - `tie = 2`
  - `not_applicable = 3`
- `more_interference_leaky`
  - `legacy_transient_leakguard_probe_v1 = 5`
  - `legacy_stage2 = 2`
  - `tie = 1`
  - `not_applicable = 2`
- `more_residual_heavy`
  - `legacy_transient_leakguard_probe_v1 = 6`
  - `legacy_stage2 = 2`
  - `tie = 2`
- `better_retention_minus_leak`
  - `legacy_transient_leakguard_probe_v1 = 2`
  - `legacy_stage2 = 3`
  - `not_applicable = 5`

解码后均值：

- `legacy_stage2`
  - `target_capture_db = -12.578`
  - `interference_capture_db = -45.209`
  - `retention_minus_leak_db = 27.905`
  - `residual_output_share = 0.661`
- `legacy_transient_leakguard_probe_v1`
  - `target_capture_db = -10.211`
  - `interference_capture_db = -44.356`
  - `retention_minus_leak_db = 28.938`
  - `residual_output_share = 0.679`

关键样本：

- `near_real_0005`
  - `delta_retention_minus_leak_db = +5.722`
- `near_real_0007`
  - `delta_retention_minus_leak_db = +7.826`

这两条说明它在“目标保留提升大于泄漏增加”的样本上，确实比 `v2 / v4` 更接近可保留形态。

但反向样本也很明确：

- `near_real_0003`
  - `delta_retention_minus_leak_db = -2.148`
- `near_real_0004`
  - `delta_retention_minus_leak_db = -3.681`

并且整体 residual 仍偏高。

## 当前结论

截至本轮，`legacy_transient_leakguard_probe_v1` 的判断是：

1. 它是当前仓库里最强的 synthetic objective 候选。
2. 它也是目前第一条同时做到：
   - `SI-SDR` 系统性提升
   - leakage metric 系统性下降
   的路线。
3. 相比 `legacy_transient_focus_probe_v4`，它在 near-real trade-off 上也更接近可保留：
   - `better_retention_minus_leak: 1 -> 2`
   - `more_interference_leaky: 7 -> 5`
4. 但它仍然没有通过 near-real 自动放行：
   - 瞬态缺失 heuristic 仍偏负面
   - residual-heavy 计数偏高
   - `near_real_0003 / 0004` 这类 speech-only 近真实样本仍有回退
5. 因此当前仍不能升成新主线。

## 下一步

如果仍不能做人耳听评，当前最合理的下一步不是继续扫大范围权重，而是：

1. 基于 `legacy_transient_leakguard_probe_v1` 再做一轮更保守的 speech-side 修正；
2. 优先针对：
   - `near_real_0003`
   - `near_real_0004`
   这类 speech-only 回退点；
3. 方向上更像：
   - 保留当前 leak guardrail 主体
   - 但对 speech-like interference 再加一层 residual / projection 约束细化
   - 或把 leakage selector 从“全 interference recipe”再拆成 speech / music 两类控制。

## Probe V2: `legacy_transient_leakguard_probe_v2_musiconly`

在 `v1` 的 near-real 自动诊断里，speech-only 回退仍明显之后，先做了一轮更窄 selector 的 follow-up：

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v2_musiconly/`
- eval：
  - `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v2_musiconly_eval/`

关键配置：

- warm-start：
  - `legacy_transient_leakguard_probe_v1`
- `transient_weight = 0.002`
- `interference_weight = 0.01`
- `interference_focus_recipes =`
  - `target_music`
  - `target_clean_plus_music`
  - `target_hard_plus_music`

当前结果：

1. 相对 `legacy stage2`，它在默认 synthetic val 上仍是正增益：
   - `avg_sisdr_delta_db = +0.665876`
   - `interference_projection_ratio = 0.0319`
2. 但相对 `legacy_transient_leakguard_probe_v1`，它已经明显回退：
   - `avg_sisdr_delta_db = -0.183896`
   - `improved_count = 58`
   - `regressed_count = 299`
3. 分 recipe 看，它并不是“只牺牲少数非目标场景”：
   - `target_clean_speech: -0.165 dB`
   - `target_hard_speech: -0.212 dB`
   - `target_only: -0.274 dB`
   - `target_singing_vocal: -0.233 dB`

当前判断：

- 这版更像是“把 leakage selector 缩得太窄后，对 music-like 干扰更用力，但整体 trade-off 比 `v1` 更差”。
- 因此当前不保留 `v2_musiconly`。

## Probe V3: `legacy_transient_leakguard_probe_v3_w0005`

在确认 `v2_musiconly` 不是正确方向后，又做了一轮更保守的权重回收：

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v3_w0005/`
- eval：
  - `reports/eval/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v3_w0005_eval/`
- near-real blind pack：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v3_w0005_blind/`

关键配置：

- warm-start：
  - `legacy_transient_focus_probe_v4`
- `transient_weight = 0.002`
- `interference_weight = 0.005`
- 其余 selector 回到 `v1` 的全 interference recipe 版本

### Synthetic Eval

相对 `legacy stage2`：

- `avg_sisdr_delta_db = +0.383818`
- `waveform_l1` 基本持平
- `interference_projection_ratio = 0.0560`

相对 `legacy_transient_leakguard_probe_v1`：

- `avg_sisdr_delta_db = -0.465955`
- `improved_count = 33`
- `regressed_count = 426`

当前判断：

- 这版没有保住 `v1` 的 synthetic 强度。
- 但它不是纯回退，因为它的目标本来就是更保守地回收 side effect。

### Near-Real Auto Diagnostics

当前已补跑：

- `bandwidth_analysis`
- `transient_analysis`
- `tradeoff_analysis`

对应目录：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v3_w0005_blind/bandwidth_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v3_w0005_blind/transient_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v3_w0005_blind/tradeoff_analysis/`

解码后结论：

1. 带宽收窄：
   - `legacy_transient_leakguard_probe_v3_w0005 = 3`
   - `legacy_stage2 = 0`
   - `tie = 7`
2. 瞬态缺失：
   - `legacy_transient_leakguard_probe_v3_w0005 = 4`
   - `legacy_stage2 = 4`
   - `tie = 2`
3. trade-off 计数：
   - `better_source_retention`
     - `legacy_transient_leakguard_probe_v3_w0005 = 2`
     - `legacy_stage2 = 1`
     - `tie = 4`
     - `not_applicable = 3`
   - `more_interference_leaky`
     - `legacy_transient_leakguard_probe_v3_w0005 = 5`
     - `legacy_stage2 = 2`
     - `tie = 1`
     - `not_applicable = 2`
   - `more_residual_heavy`
     - `legacy_transient_leakguard_probe_v3_w0005 = 1`
     - `legacy_stage2 = 2`
     - `tie = 7`
   - `better_retention_minus_leak`
     - `legacy_transient_leakguard_probe_v3_w0005 = 2`
     - `legacy_stage2 = 3`
     - `not_applicable = 5`
4. 解码后均值：
   - `legacy_stage2`
     - `target_capture_db = -12.578`
     - `interference_capture_db = -45.209`
     - `retention_minus_leak_db = 27.905`
     - `residual_output_share = 0.661`
   - `legacy_transient_leakguard_probe_v3_w0005`
     - `target_capture_db = -9.558`
     - `interference_capture_db = -43.697`
     - `retention_minus_leak_db = 28.585`
     - `residual_output_share = 0.654`

### 相对 `v1` 的更新判断

`v3_w0005` 的价值主要不在 synthetic 指标，而在 near-real side effect 的移动方向：

1. `more_residual_heavy` 已从 `v1` 的 `6` 条显著收回到 `1` 条。
2. `residual_output_share` 也从：
   - `0.679 -> 0.654`
3. 但它没有把最关键的 leakage / 带宽问题一起收正：
   - `more_interference_leaky` 仍是 `5` 条
   - 带宽收窄从 `v1` 的 `2` 条升到 `3` 条
   - `retention_minus_leak_db` 也从 `28.938` 回落到 `28.585`

因此当前更准确的定位是：

- `v1` 仍是更强的 objective-only 主候选；
- `v3_w0005` 是一个“更保守、residual 更轻”的参考分支；
- 但它不足以替代 `v1`。

## 更新后的当前结论

截至本次 follow-up，leak-guardrail 线的判断更新为：

1. `v2_musiconly` 已证伪，不保留。
2. `v1` 仍是当前最强的 synthetic objective 候选，也是默认优先保留的 objective-only 分支。
3. `v3_w0005` 证明“减 residual-heavy”这件事是可做到的，但它并没有同步解决 leakage / 窄带化问题。
4. 因此在无新增人耳听评条件下，当前更稳的工作顺序应是：
   - 保留 `v1` 作为第一 objective-only 候选
   - 把 `v3` 当作 side-effect 对照参考
   - 下一步继续修 speech-only near-real 回退，而不是再扫 music-only selector 或更小 interference 权重近邻
