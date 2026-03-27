# hard-present artifact proxy `v1` materialization

## 本轮目标

`v81 vs v103` blind 听审已经确认：

- `v103` 四条样本全部因 artifact 更重而落败；
- 不能再继续做 `v103+` 小步 sweep；
- 下一步必须先把 `near_real_0007` 风格风险物化成固定 synthetic proxy。

因此本轮不启动新训练，先完成两件事：

1. 给 metadata-focused manifest 脚本补上 `interference_profile / interference_layer_count / has_*_interference` 级过滤。
2. 物化并校准 `hard_present_artifact_proxy_v1`，再用它回放 `v81 / v102 / v103`。

## 代码补丁

文件：

- `scripts/data/build_metadata_focused_manifest.py`

新增能力：

- `--interference-profiles`
- `--min-interference-layer-count`
- `--max-interference-layer-count`
- `--require-speech-interference`
- `--forbid-speech-interference`
- `--require-music-interference`
- `--forbid-music-interference`
- `--require-other-interference`
- `--forbid-other-interference`

同时 summary 里新增：

- `interference_profile_counts`
- `interference_layer_count_counts`

这样后续 manifest 物化可以直接和训练 selector 使用同一套 profile/layer 语义，不再只能靠 recipe 间接代理。

## 新增资产

### `hard_present_artifact_proxy_v1`

文件：

- `data/synthetic/train_manifest_hard_present_artifact_proxy_v1.jsonl`
- `data/synthetic/val_manifest_hard_present_artifact_proxy_v1.jsonl`
- `data/synthetic/sample_ids_hard_present_artifact_proxy_v1_train.txt`
- `data/synthetic/sample_ids_hard_present_artifact_proxy_v1_val.txt`
- `reports/data/selector_hard_present_artifact_proxy_v1_train_summary.json`
- `reports/data/selector_hard_present_artifact_proxy_v1_val_summary.json`

过滤口径：

- `recipe in {target_clean_plus_music, target_hard_plus_music}`
- `temporal_pattern = target_full`
- `interference_profile = speech_plus_music`
- `interference_layer_count = 2`
- `require_speech_interference = true`
- `require_music_interference = true`
- `overlap_ratio >= 0.6`
- `0.04 <= target_energy_ratio <= 0.20`
- `0.02 <= target_transient_presence_share_mean <= 0.10`
- `-17.0 <= target_transient_presence_minus_mid_db_mean <= -9.0`

规模：

- train `33`
  - `target_clean_plus_music = 27`
  - `target_hard_plus_music = 6`
- val `7`
  - `target_clean_plus_music = 6`
  - `target_hard_plus_music = 1`

## 校准结论

`near_real_0007` 的关键点不是“极低 transient”本身，而是：

- 弱目标
- `speech_plus_music` 双层干扰
- `target_full` hard-present overlap
- target transient share 落在中高区间，而不是 `0006` 那类近乎零 transient share

所以这条 proxy 不再沿用旧的

- `target_transient_presence_share_mean <= 0.05`

式 hard-present keep 逻辑，而是显式要求：

- `speech_plus_music`
- `layer_count = 2`
- `target_transient_presence_share_mean` 在 `[0.02, 0.10]`

目的是把 `0007` 型 artifact risk 和 `0006` 型 speech-only keep case 分开。

## 回放验证

评测输出：

- `reports/eval/rank_hard_present_artifact_proxy_v1_v81_v102_v103_train/summary.json`
- `reports/eval/rank_hard_present_artifact_proxy_v1_v81_v102_v103_val/summary.json`

基线：

- `v81`

候选：

- `v102`
- `v103`

结果有两个层次。

### 1. 只看 retention-minus-leak，`v103` 仍会被排前

- train `combined_top = v103`
- val `combined_top = v103`

这和此前 automatic 观察一致：

- `v103` 仍会把 suppression 指标继续往前推。

### 2. 一加 present guardrail，`v103` 立刻掉到最后

- train
  - `v81` violation `0`
  - `v102` violation `1`
  - `v103` violation `2`
- val
  - `v81` violation `0`
  - `v102` violation `0`
  - `v103` violation `2`

`v103` 的 val 违规样本：

- `val_000437`
- `val_000495`

两条都表现为：

- relative `v81` 的 target capture 下滑超过 `2 dB`
- 但 retention-minus-leak 总分仍可能更高

这正符合本轮听审暴露的问题模式：

- suppression 指标会继续把 `v103` 往前排；
- 但一旦加上 hard-present artifact/backstop 视角，`v103` 会被重新打回去。

## 本轮裁决

1. `hard_present_artifact_proxy_v1` 成立，可作为新的固定 artifact-first 诊断资产。
2. `v103` 的问题现在不再只是 `near_real_0007` 单点 anecdote，而是已经能在 synthetic proxy 上复现成 present guardrail regression。
3. 下一步应基于 `v81` 重开新的 artifact-aware 子题，而不是继续 `v103+` sweep。

## 下一步

下一轮训练前，默认同时保留五条验收：

- `real_eval_manifest_residual_speech_leak_floor_v1`
- `same_gender_present_keep_guardrail_v1`
- `hard_present_gate_keep_guardrail_v1`
- `hard_present_artifact_proxy_v1`
- `overlap_abstention_proxy_v4_audibility_v1`

训练方向改为：

- 基于 `v81`
- 保留 localized speech-leak 视角
- 新增显式 artifact-aware backstop
- 优先限制 `speech_plus_music hard-present` 上的 target-capture regression
