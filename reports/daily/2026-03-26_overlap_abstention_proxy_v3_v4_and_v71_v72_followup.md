# 2026-03-26 overlap-abstention `proxy_v3 / proxy_v4` 与 `v71 / v72` follow-up

## 本轮目标

在 `v68 / v69 / v70` 已经证明 “overlap abstention 方向可训练、但 near-real 仍误杀 present case” 之后，继续回答两个更具体的问题：

1. 之前的 near-real 失败，是否主要由 `absent-style` selector 带来的时序静音偏置造成。
2. 如果把 selector 收窄到更贴近“真实可辨度弱”，能否把 `near_real_0006` 和 `near_real_0003` 分开。

## 新增代码与资产

### 1. `build_metadata_focused_manifest.py` 新增 audibility metric

文件：

- `scripts/data/build_metadata_focused_manifest.py`

本轮新增并持久化的 derived metrics：

- `target_energy_ratio`
  - 定义与 near-real ranking 保持一致：
    `energy(target) / energy(mixture)`
- `interference_energy_ratio`
- `target_to_interference_energy_ratio`
- `target_to_interference_energy_db`

新增过滤参数：

- `--min-target-energy-ratio`
- `--max-target-energy-ratio`

结论：

- 这一步不是 cosmetic patch。
- 它把 selector 从“只按 `target_present_ratio / transient share` 间接猜弱目标”
  推进到“可直接按目标在混音里的能量占比过滤”。

### 2. `proxy_v3 = weakfull`

文件：

- `data/synthetic/train_manifest_overlap_abstention_proxy_v3_weakfull_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_proxy_v3_weakfull_v1.jsonl`
- `data/synthetic/sample_ids_overlap_abstention_proxy_v3_weakfull_v1_{train,val,all}.txt`
- `reports/data/selector_overlap_abstention_proxy_v3_weakfull_v1_summary.json`

构造口径：

- 输入：`overlap_abstention_backstop_v1`
- `target_full`
- `target_transient_presence_share_mean <= 0.03`
- `target_transient_presence_minus_mid_db_mean <= -10`
- 清掉 `Battle / Placeholder` 污染条目

规模：

- train `49`
- val `17`

### 3. `proxy_v4 = weakfull + audibility`

文件：

- `data/synthetic/train_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`
- `data/synthetic/val_manifest_overlap_abstention_proxy_v4_audibility_v1.jsonl`
- `data/synthetic/sample_ids_overlap_abstention_proxy_v4_audibility_v1_{train,val,all}.txt`
- `reports/data/selector_overlap_abstention_proxy_v4_audibility_v1_summary.json`

构造口径：

- 在 `proxy_v3` 基础上再加：
  - `target_energy_ratio <= 0.2`
- 同样清掉 `Battle / Placeholder`

规模：

- train `35`
- val `8`

当前判断：

- `proxy_v4` 比 `proxy_v3` 更贴近 `near_real_0006 (target_energy_ratio ~= 0.18)`，
  明确远离 `near_real_0003 (target_energy_ratio ~= 0.59)`。

## 新训练

### 1. `v71 = 去掉 absent-style 推力，只保留 weakfull interference focus`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v71_v54_overlap_abstention_proxy_v3_weakfull_v1_ft1`

训练口径：

- init：`v54`
- manifest：`overlap_abstention_backstop_union_v1`
- focused interference selector：
  - `sample_ids_overlap_abstention_proxy_v3_weakfull_v1_all.txt`
- 保留：
  - `reconstruction_extra`
  - `branch_protect`
- 删除：
  - `absent_extra`

目的：

- 直接验证 “near-real 失败是否主要来自 absent-style selector”。

### 2. `v72 = audibility-aware weakfull pilot`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v72_v54_overlap_abstention_proxy_v4_audibility_v1_ft1`

训练口径：

- 与 `v71` 相同
- 唯一变化：
  - interference focus selector 改为
    `sample_ids_overlap_abstention_proxy_v4_audibility_v1_all.txt`

目的：

- 直接验证 `target_energy_ratio` 是否能把 `0006` 和 `0003` 进一步分开。

## Synthetic 结果

### `v71` 相对 `v54`

- `proxy_v3 weakfull`
  - `reports/eval/compare_v54_vs_v71_on_overlap_abstention_proxy_v3_weakfull_v1/summary.json`
  - `+2.966444 dB`
  - `16` improve / `1` regress
- `backstop_union_v1`
  - `reports/eval/compare_v54_vs_v71_on_overlap_abstention_backstop_union_v1/summary.json`
  - `+2.146660 dB`
  - `49` improve / `3` regress
- 旧 `proxy_v2`
  - `reports/eval/compare_v54_vs_v71_on_overlap_abstention_proxy_v2/summary.json`
  - `+1.666490 dB`
  - `10` improve / `0` regress

结论：

- 去掉 `absent_extra` 后，synthetic 并没有塌。
- 这说明 `weakfull` 路径本身就是可训练的，不依赖 absent-style selector 才能成立。

### `v72` 相对 `v54`

- `proxy_v4 audibility`
  - `reports/eval/compare_v54_vs_v72_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `+4.317892 dB`
  - `7` improve / `1` regress
- `proxy_v3 weakfull`
  - `reports/eval/compare_v54_vs_v72_on_overlap_abstention_proxy_v3_weakfull_v1/summary.json`
  - `+2.976152 dB`
  - `16` improve / `1` regress
- `backstop_union_v1`
  - `reports/eval/compare_v54_vs_v72_on_overlap_abstention_backstop_union_v1/summary.json`
  - `+2.144486 dB`
  - `48` improve / `2` regress

结论：

- `target_energy_ratio` 版 selector 在 synthetic 上没有方向错误。
- 而且它在自己的 `proxy_v4` 切片上，比 `v71` 预期更对题。

## Near-real 结果

### `v71`

文件：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v71/summary.json`

真实结论：

- `combined_top = v71`
- `guardrail_filtered_top = v54`
- `present_guardrail_violation_count = 2`
- 违规样本：
  - `near_real_0003`
  - `near_real_0006`

样本级变化：

- `near_real_0009`
  - absent suppression：
    `-33.385 dB -> -34.406 dB`
- `near_real_0006`
  - interference capture：
    `-30.495 dB -> -34.942 dB`
  - 但 target capture：
    `-4.754 dB -> -8.945 dB`
- `near_real_0003`
  - interference capture：
    `-24.658 dB -> -34.287 dB`
  - 但 target capture：
    `-11.464 dB -> -19.601 dB`

裁决：

- 去掉 absent-style selector 后，
  `0007` 没再被拉进 violation，
  说明之前的失败不完全是“方向错”，但也不是“只有 absent_extra 在作怪”。
- `0003 / 0006` 仍然一起过静，说明仅靠 `weakfull interference push + branch protect`
  还不足以把“该闭嘴的弱目标”和“仍应保留的中等可辨目标”拆开。

### `v72`

文件：

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v71_v72/summary.json`

真实结论：

- `combined_top = v72`
- `guardrail_filtered_top = v54`
- `v72` 仍有 `present_guardrail_violation_count = 2`
- 违规样本仍然是：
  - `near_real_0003`
  - `near_real_0006`

与 `v71` 的差异：

- `near_real_0009`
  - `-34.406 dB -> -34.468 dB`
  - 稍好
- `near_real_0003`
  - target capture：
    `-19.601 dB -> -19.592 dB`
  - 基本不变
- `near_real_0006`
  - target capture：
    `-8.945 dB -> -8.941 dB`
  - 基本不变

裁决：

- `target_energy_ratio` selector 让 objective 继续朝对的方向走，
  但 near-real 主失败模式几乎没变。
- 这说明当前瓶颈已经不是 selector 还不够贴题，
  而是现有 loss 结构下，
  “更强的 overlap suppression”仍然会把 `0003` 和 `0006` 一起拖进过静区。

## 本轮总裁决

### 已确认成立的事

1. `weakfull` 路径本身可训练，不依赖 `absent_extra` 才能产生 synthetic 收益。
2. `target_energy_ratio` 是一个有价值的 selector metric，应该保留。
3. `v72` 相对 `v71` 在 combined objective 上略强，说明 audibility-aware selector 方向正确。

### 已确认不成立的事

1. “只要把 absent-style selector 去掉，near-real 就会自动修好”。
2. “只要再把 selector 从 transient 收窄到 audibility，`0003` 和 `0006` 就会自然分开”。

### 当前最准确的判断

当前真正的未解点已经从

- `selector 是否够准`

进一步收窄成

- `如何在保持 `0006` 更安静的同时，不把 `0003` 一起压坏`

也就是说，下一步如果继续，不该优先再做一轮更细 selector sweep，
而该考虑：

1. 给 `0003` 这一类中等可辨 target-present case
   单独补一条反向 keep guardrail；
2. 或者在 loss 上引入更直接的
   “只惩罚 residual leak，不鼓励整体静音”
   约束；
3. 否则继续加 overlap-abstention focused loss，
   大概率只会重复 `v71 / v72` 这种
   “combined score 更好，但 guardrail 仍不过”的模式。

## 当前默认下一步

如果继续推进，默认下一步应改成：

- 不再先训 `v73`
- 先设计一个
  `medium-audibility present keep guardrail`
  或等价的 focused backstop

目标非常明确：

- 继续允许模型在 `0006 / 0009` 一类弱目标上更愿意闭嘴
- 但必须显式阻止它把 `0003` 这种
  `target_energy_ratio ~= 0.59`
  的样本也一起压成过静

