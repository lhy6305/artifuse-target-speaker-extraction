# 2026-03-17 Transient Loss Probe

## 背景

在完成：

- `bandwidth_analysis`
- `transient_analysis`

之后，当前“电话音 / 降采样感”问题已经比较收敛到：

1. 不是简单全局低通；
2. 更像局部频带收窄；
3. 尤其像高频瞬态、清辅音、吹气声相对中频被削掉。

因此本轮没有继续堆 reverb 概率，而是把这条假设接到了训练入口：

- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

当前 baseline 已支持：

- `transient_presence_l1_loss(...)`
- `--loss-transient-weight`

并且 `sample_rate` 已显式进入 `loss_config`，避免把 `16k` 写死在 loss 内部。

## Synthetic Baseline With New Metric

先用当前默认主线 `legacy stage2` 补跑一次新版 eval，拿到可比的 transient 指标基线：

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- eval：
  - `reports/eval/baseline_stft_mask_stage2_eval_with_transient_metric/`

当前 synthetic val 指标为：

- `waveform_l1 = 0.013091`
- `stft_l1 = 0.014654`
- `sisdr_db = -10.252`
- `transient_presence_l1 = 0.748868`

这个 `0.748868` 是后续 transient probe 的直接参照。

## Probe V1: `legacy_transient_probe_v1`

### 配置

- 输出目录：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_probe_v1/`
- warm-start：
  - `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- 配置：
  - `conditioning_mode=legacy_bias`
  - `epochs=3`
  - `batch_size=16`
  - `lr=3e-4`
  - `transient_weight=0.005`

### 结果

eval 产物：

- `reports/eval/baseline_stft_mask_stage2_legacy_transient_probe_v1_eval/`

当前 synthetic val 指标：

- `waveform_l1 = 0.013215`
- `stft_l1 = 0.013866`
- `sisdr_db = -10.634`
- `transient_presence_l1 = 0.566533`

相对 `legacy stage2`：

- `transient_presence_l1` 明显下降：`0.748868 -> 0.566533`
- 但默认 val compare 结果明显回退：
  - `reports/eval/compare_stage2_vs_legacy_transient_probe_v1_on_default/`
  - `avg_sisdr_delta_db = -0.411792`
- focused recipe 合并后也仍为轻微负增益：
  - `reports/eval/compare_stage2_vs_legacy_transient_probe_v1_on_focus_recipes/`
  - `avg_sisdr_delta_db = -0.025914`

当前判断：

- `0.005` 对默认分布过激，不继续作为主候选。

## Probe V2: `legacy_transient_probe_v2`

### 配置

- 输出目录：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_probe_v2/`
- warm-start：
  - `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
- 配置：
  - `conditioning_mode=legacy_bias`
  - `epochs=3`
  - `batch_size=16`
  - `lr=3e-4`
  - `transient_weight=0.002`

### 结果

eval 产物：

- `reports/eval/baseline_stft_mask_stage2_legacy_transient_probe_v2_eval/`

当前 synthetic val 指标：

- `waveform_l1 = 0.013153`
- `stft_l1 = 0.013842`
- `sisdr_db = -10.495`
- `transient_presence_l1 = 0.578812`

相对 `legacy stage2`：

- `transient_presence_l1` 仍明显下降：`0.748868 -> 0.578812`
- 默认 val compare 仍回退，但已比 `v1` 收敛：
  - `reports/eval/compare_stage2_vs_legacy_transient_probe_v2_on_default/`
  - `avg_sisdr_delta_db = -0.314348`
- focused recipe 合并后首次转正：
  - `reports/eval/compare_stage2_vs_legacy_transient_probe_v2_on_focus_recipes/`
  - `avg_sisdr_delta_db = +0.112091`

分 recipe 观察：

- `target_clean_speech`: `+0.262651 dB`
- `target_clean_plus_music`: `-0.105032 dB`
- `target_hard_plus_music`: `-0.641301 dB`
- `target_hard_speech`: `-0.738324 dB`
- `target_only`: `-0.580118 dB`

当前判断：

1. `v2` 比 `v1` 更接近可保留候选。
2. 它在 `clean_speech` 上已经有明确方向性收益。
3. 但默认全分布上仍会伤：
   - `target_only`
   - `hard_speech`
   - `hard_plus_music`
4. 因此当前仍不能直接升成主线或默认训练配置。

## Near-Real Blind Pack Exported

为了避免只靠 synthetic 指标判断，本轮已导出：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/`

启动 GUI：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind
```

## Auto Diagnostics On The New Near-Real Pack

已补跑：

- `bandwidth_analysis`
- `transient_analysis`

对应目录：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/bandwidth_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/transient_analysis/`

### 重要说明

blind 包里的 summary 默认统计的是：

- `file_a`
- `file_b`

不是模型标签本身，因此必须结合：

- `blind_key.json`

解码后才能下模型级结论。

### 解码后的带宽结论

结合 `blind_key.json` 后，当前 near-real 10 条样本里：

- `legacy_transient_probe_v2` 被标成更窄带：`4`
- `legacy_stage2` 被标成更窄带：`0`
- `tie`: `6`

重点样本：

- `near_real_0005`
- `near_real_0007`
- `near_real_0010`

这些样本上，`legacy_transient_probe_v2` 都会被标成更窄带的一侧。

### 解码后的瞬态结论

结合 `blind_key.json` 后，当前 near-real 10 条样本里：

- `legacy_transient_probe_v2` 被标成更 transient-lossy：`7`
- `legacy_stage2` 被标成更 transient-lossy：`1`
- `tie`: `2`

重点样本：

- `near_real_0003`
- `near_real_0005`
- `near_real_0007`
- `near_real_0010`

这些样本上，`legacy_transient_probe_v2` 都会被标成更 transient-lossy。

也有少数反向点：

- `near_real_0002`

以及 target-absent 场景中的混合信号：

- `near_real_0008`

但整体上，自动诊断目前仍偏向：

- `legacy_transient_probe_v2` 更容易出现局部窄带化和瞬态削弱。

## 当前结论

截至本轮，当前更稳的判断是：

1. transient loss 这条方向不是空想：
   - 它确实能系统性压低 synthetic 上的 `transient_presence_l1`
   - 并在 `target_clean_speech` 上带来第一批可保留的客观收益
2. 但“默认全分布直接加 transient loss”当前仍是高风险动作：
   - 总体 `SI-SDR` 仍回退
   - `target_only / hard_speech / hard_plus_music` guardrail 仍明显受损
3. 更保守的 `legacy_transient_probe_v2 (0.002)` 值得保留为候选分支。
4. 但自动 near-real 诊断目前还没有给它放行，反而提示：
   - 它仍可能在多条 near-real 样本上比 `legacy stage2` 更窄带、更 transient-lossy。

## 下一步

1. 优先人工听：
   - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/`
2. 听评时优先盯：
   - `near_real_0005`
   - `near_real_0007`
   - `near_real_0010`
   - `near_real_0008`
3. 若主观结果仍确认它更容易带出“电话音 / 窄带感”，则当前不再继续在默认全分布上加 transient loss，而应考虑：
   - 更局部的 recipe / pattern 约束
   - 或只在特定 realism 分支上使用这类 loss

## Near-Real Listening Review Update

上述第 1 步现已完成。当前 GUI 落盘结果位于：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/listening_sheet.csv`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/listening_results_summary.json`

盲态计数为：

- `file_a`: `0`
- `file_b`: `2`
- `tie`: `8`
- `uncertain`: `0`

结合 `blind_key.json` 解盲后，真实模型偏好为：

- `legacy_transient_probe_v2`: `2`
- `legacy_stage2`: `0`
- `tie`: `8`
- `uncertain`: `0`

### 重要口径说明

本轮 listening sheet 的填写策略是：

1. 只有在存在明显差异时，才填写主要差异来源；
2. 其余字段保持空白；
3. 因此空白字段不应被自动解释为：
   - `none`
   - 或“明确无问题”。

### 样本级有效信息

`near_real_0005`：

- 主观选择：`legacy_transient_probe_v2`
- 明确标签：
  - `better_source_retention`
- 备注：
  - 差异 very small，但仍可感知

当前理解：

- 更像是 `legacy_transient_probe_v2` 多保住了一点 source retention；
- 但这不是强胜，只能算 very weak positive signal。

`near_real_0007`：

- 主观选择：`legacy_transient_probe_v2`
- 明确标签：
  - `file_a_source_retention = fair`
  - `file_b_source_retention = good`
  - `file_a_interference_leak = slight`
  - `file_b_interference_leak = moderate`
  - `better_source_retention`
- 备注：
  - B 保留更多目标音频，但更多泄漏干扰

当前理解：

- 这是一个更典型的 trade-off 样本：
  - `legacy_transient_probe_v2` 在 source retention 上更好；
  - 但同时把 interference leak 也拉高了。

`near_real_0008`：

- 主观结论仍为 `tie`
- 备注补充：
  - B 有一个极短瞬态泄漏；
  - 且听起来与目标说话声音一致

当前理解：

- 这说明 target-absent guardrail 仍未被完全解决；
- 但由于总体判断仍为 `tie`，当前更适合作为风险备注，而不是单独拉高到主结论。

### 当前结论更新

这轮人听给出的信息，比自动诊断更温和一些：

1. `legacy_transient_probe_v2` 没有像 `legacy_speechreverb_probe_v2` 那样出现明确主观负偏好。
2. 当前 10 条样本里，它拿到：
   - `2` 次偏好
   - `0` 次失利
   - `8` 次平手
3. 但这 `2` 次偏好都不是“纯净的大胜”：
   - 一次只是 very small difference；
   - 一次是更好 source retention 换来更多 interference leak。
4. 用户主观上还感觉：
   - 伪影和“电话音”似乎有些许减轻；
   - 但当前不把这点计入主结论，只把它保留为弱观察。

因此当前更合适的结论是：

1. `legacy_transient_probe_v2` 比前面的 reverb probe 更值得保留。
2. 它已经形成了 very weak positive human signal。
3. 但这还不足以把它升成新主线，也不足以证明“transient loss 已经安全解决电话音问题”。
4. 若后续继续推进，优先级应改为：
   - 更局部、更保守的 transient-loss 使用方式；
   - 或围绕 `source retention vs interference leak` 做更细的约束设计；
   - 而不是直接扩大默认全分布训练预算。

## Selector-Based Local Transient Loss

基于上述主观结论，本轮继续把 transient loss 从“全 batch 默认生效”推进到了“只在局部子集生效”。

训练脚本现支持：

- `--loss-transient-focus-recipes`
- `--loss-transient-focus-patterns`
- `--loss-transient-min-target-ratio`
- `--loss-transient-max-target-ratio`

实现方式是：

1. 不改主训练 manifest；
2. 仍用默认全分布做 warm-start 微调；
3. 但 transient loss 只对命中的 batch 子样本生效；
4. 其余样本继续只受原始 waveform/STFT 项约束。

### Probe V3: `legacy_transient_focus_probe_v3`

配置：

- `transient_weight=0.002`
- focus recipes:
  - `target_clean_speech`
  - `target_clean_plus_music`
- focus patterns:
  - `target_full`
  - `target_absent_head`
  - `target_absent_tail`

结果：

- 默认 val：
  - `reports/eval/compare_stage2_vs_legacy_transient_focus_probe_v3_on_default/`
  - `avg_sisdr_delta_db = -0.368468`
- focused recipes：
  - `reports/eval/compare_stage2_vs_legacy_transient_focus_probe_v3_on_focus_recipes/`
  - `avg_sisdr_delta_db = -0.141059`

当前判断：

- 这版说明“选得还不够窄”时，selector 并不会自动把整体 trade-off 救回来；
- 当前不保留 `v3`。

### Probe V4: `legacy_transient_focus_probe_v4`

配置：

- `transient_weight=0.002`
- focus recipes:
  - `target_clean_speech`
- focus patterns:
  - `target_full`
  - `target_absent_head`
  - `target_absent_tail`

结果：

- 默认 val：
  - `reports/eval/compare_stage2_vs_legacy_transient_focus_probe_v4_on_default/`
  - `avg_sisdr_delta_db = -0.227666`
- clean speech：
  - `reports/eval/compare_stage2_vs_legacy_transient_focus_probe_v4_on_clean_speech/`
  - `avg_sisdr_delta_db = +0.315322`
- clean speech + clean plus music：
  - `reports/eval/compare_stage2_vs_legacy_transient_focus_probe_v4_on_focus_recipes/`
  - `avg_sisdr_delta_db = +0.062535`

与此前全局版 `legacy_transient_probe_v2` 相比：

- 默认全分布代价更小：
  - `-0.314348 -> -0.227666`
- `target_clean_speech` 收益更大：
  - `+0.262651 -> +0.315322`
- 组合 focused 收益仍为正，但略低：
  - `+0.112091 -> +0.062535`

当前判断：

1. `v4` 是目前 transient-loss 线上最平衡的客观候选。
2. 它没有把 `clean_plus_music` 真正救正，但已经把默认全分布代价收窄了一截。
3. 因此当前更值得听的是 `v4`，而不是旧的全局 `v2`。

## Near-Real Pack For `legacy_transient_focus_probe_v4`

已导出：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_focus_probe_v4_blind/`

启动 GUI：

```powershell
.\python.exe scripts\eval\listening_pack_gui.py --pack-dir reports\eval\ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_focus_probe_v4_blind
```

已补跑自动诊断：

- `bandwidth_analysis`
- `transient_analysis`

### 解码后的自动诊断

带宽收窄 heuristic：

- `legacy_transient_focus_probe_v4`: `2`
- `legacy_stage2`: `0`
- `tie`: `8`

相对全局版 `legacy_transient_probe_v2`：

- 已从 `4 : 0 : 6`
- 收敛到 `2 : 0 : 8`

这说明：

- `v4` 在自动带宽收窄侧，比 `v2` 更稳一些。

瞬态缺失 heuristic：

- `legacy_transient_focus_probe_v4`: `7`
- `legacy_stage2`: `1`
- `tie`: `2`

这一项与全局版 `v2` 基本没有明显改善，说明：

- 当前 selector-based 收窄，更多像是在减轻“窄带化”副作用；
- 但并没有把 near-real 上的“瞬态更容易被削”问题真正解决。

## 当前更新结论

截至本轮，transient-loss 方向的结论进一步收敛为：

1. 全局版 `legacy_transient_probe_v2`：
   - 已有弱主观正信号；
   - 但副作用仍明显。
2. 局部版 `legacy_transient_focus_probe_v4`：
   - 是当前更平衡的客观候选；
   - 自动带宽收窄 side effect 也比 `v2` 更轻；
   - 但自动瞬态缺失诊断仍未明显转正。
3. 因此当前最合理的下一步不是继续开更多近邻权重，而是：
   - 直接听 `v4` 的 near-real blind 包；
   - 再决定是否值得继续沿 selector-based transient loss 往下做。

## Trade-Off Analysis Update

在“当前物理环境不支持继续人耳听评”的约束下，本轮补了一个更直接的 near-real 自动诊断脚本：

- `scripts/eval/analyze_listening_pack_tradeoff.py`

它会：

1. 从 listening pack 的 `mixture_audio_path` 回溯到原始 near-real 样本；
2. 按 `sample_meta.json` 里的 `components` 重建：
   - `target_track`
   - `interference_track`
3. 对每个候选输出量化：
   - `target_capture_db`
   - `interference_capture_db`
   - `residual_output_share`
   - `retention_minus_leak_db`

已实跑两个 blind pack：

- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/tradeoff_analysis/`
- `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_focus_probe_v4_blind/tradeoff_analysis/`

### `legacy_transient_probe_v2` 的 trade-off 结果

解码后计数：

- `better_source_retention`:
  - `legacy_transient_probe_v2 = 4`
  - `legacy_stage2 = 0`
  - `tie = 3`
  - `not_applicable = 3`
- `more_interference_leaky`:
  - `legacy_transient_probe_v2 = 4`
  - `legacy_stage2 = 1`
  - `tie = 3`
  - `not_applicable = 2`
- `better_retention_minus_leak`:
  - `legacy_transient_probe_v2 = 2`
  - `legacy_stage2 = 2`
  - `tie = 1`
  - `not_applicable = 5`

解码后均值：

- `legacy_stage2`
  - `target_capture_db = -12.578`
  - `interference_capture_db = -45.209`
  - `retention_minus_leak_db = 27.905`
  - `residual_output_share = 0.661`
- `legacy_transient_probe_v2`
  - `target_capture_db = -9.581`
  - `interference_capture_db = -42.813`
  - `retention_minus_leak_db = 27.407`
  - `residual_output_share = 0.620`

当前理解：

1. `v2` 在 near-real 上确实更偏向“多保一点目标”；
2. 同时也更偏向“多漏一点干扰”；
3. 两边相减后的 `retention_minus_leak` 并没有稳定优于 `stage2`，更像是：
   - 有收益样本；
   - 但总体 trade-off 仍接近打平。

### `legacy_transient_focus_probe_v4` 的 trade-off 结果

解码后计数：

- `better_source_retention`:
  - `legacy_transient_focus_probe_v4 = 2`
  - `legacy_stage2 = 0`
  - `tie = 5`
  - `not_applicable = 3`
- `more_interference_leaky`:
  - `legacy_transient_focus_probe_v4 = 7`
  - `legacy_stage2 = 0`
  - `tie = 1`
  - `not_applicable = 2`
- `better_retention_minus_leak`:
  - `legacy_transient_focus_probe_v4 = 1`
  - `legacy_stage2 = 3`
  - `tie = 1`
  - `not_applicable = 5`

解码后均值：

- `legacy_stage2`
  - `target_capture_db = -12.578`
  - `interference_capture_db = -45.209`
  - `retention_minus_leak_db = 27.905`
  - `residual_output_share = 0.661`
- `legacy_transient_focus_probe_v4`
  - `target_capture_db = -9.779`
  - `interference_capture_db = -41.562`
  - `retention_minus_leak_db = 26.665`
  - `residual_output_share = 0.627`

当前理解：

1. `v4` 也不是“单纯减少伪影”的分支；
2. 它在 near-real 上同样体现为：
   - 更高 target retention
   - 更高 interference leak
3. 而且从这个新脚本看，`v4` 的 trade-off 甚至比 `v2` 更偏 leakage 一侧：
   - `better_source_retention`: `2 < 4`
   - `more_interference_leaky`: `7 > 4`
   - `better_retention_minus_leak`: `1 < 2`

### 关键样本对应关系

`near_real_0005 / 0007`：

- `v2` 与 `v4` 都会明显提升 `target_capture_db`；
- 但也都会同步抬高 `interference_capture_db`；
- 这和之前人听里“保得更多，但也漏得更多”的描述是一致的。

`near_real_0004 / 0006`：

- 更像是 leak 增加得比 target retention 收益更明显；
- 因此 `retention_minus_leak` 反而仍偏向 `legacy_stage2`。

### 最终更新结论

到这一步，transient-loss 线的判断已经更清楚了：

1. `v2` 和 `v4` 都不是“纯修电话音”的分支，而是典型的 retention-up / leak-up 分支。
2. `v4` 在 synthetic 上比 `v2` 更平衡，但在 near-real 的新 trade-off 诊断里，反而没有显示出比 `v2` 更好的 retention-vs-leak 平衡。
3. 因此在没有新一轮人耳听评条件时，当前不值得继续只围绕：
   - 更窄的 transient selector
   - 或更密的 transient weight 邻点
   做重复扫描。
4. 当前更合理的下一步应切到：
   - 显式 `interference leak` guardrail
   - 或直接面向 `retention_minus_leak` 的约束设计
   - 而不是继续假设“只要把 transient loss 局部化，trade-off 就会自动变好”。
