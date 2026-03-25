# 2026-03-25 same_gender reverb proxy v2 materialization

## 背景

focused GUI 听审结束后，
当前默认结论已经收敛成：

1. `v32`
   仍可保留为研究基座；
2. 但现有 focused near-real 证据
   还不足以直接放行新训练；
3. 若要继续补
   `same_gender + near-f0 + near-resonance + mild-reverb`
   这条窄线，
   需要把 synthetic pre-screen
   从
   `guodegang_proxy_v1`
   再往“同类男声 + 轻混响”方向推进一步。

因此本轮不直接起训练，
而是先把：

- male-only clean speech pool
- speech-reverb-only synthetic seed
- `same_gender_reverb_proxy_v2`

这三层资产正式物化。

## 新增脚本与输入

本轮新增：

- `scripts/data/filter_manifest_by_speaker_allowlist.py`
  - 作用：
    - 从现有 clean speech manifest
      按 `speaker_id` allowlist
      稳定切出子池
- `data/references/genshin_same_gender_male_speaker_ids_v1.txt`
  - 作用：
    - 作为 first-pass
      male speaker allowlist

同时补强了现有脚本：

- `scripts/data/build_synthetic_dataset.py`
  - 新增：
    - `clean_speech_only`
      recipe profile
    - `target_full_only`
      temporal profile
    - `--pool-manifest-override`
- `scripts/data/build_metadata_focused_manifest.py`
  - 新增：
    - `--require-interference-reverb`
    - `--forbid-interference-reverb`
    - `--require-target-reverb`
    - `--forbid-target-reverb`

另外，
`build_synthetic_dataset.py`
现在会把 interference
的显式 `speaker_id`
写进 `metadata.json`，
避免后续 speaker 统计
再被
`战斗语音 / Placeholder / Others`
这类子目录名污染。

## 物化出的新资产

### 1. male-only clean pool

命令：

```powershell
.\python.exe scripts/data/filter_manifest_by_speaker_allowlist.py `
  --input-manifest data/manifests/speech_interference_clean_pool.jsonl `
  --allowlist-file data/references/genshin_same_gender_male_speaker_ids_v1.txt `
  --output-manifest data/manifests/speech_interference_clean_pool_same_gender_male_v1.jsonl `
  --summary-json data/manifests/speech_interference_clean_pool_same_gender_male_v1_summary.json
```

输出：

- `data/manifests/speech_interference_clean_pool_same_gender_male_v1.jsonl`
- `data/manifests/speech_interference_clean_pool_same_gender_male_v1_summary.json`

当前规模：

- rows：
  - `1175`
- speakers：
  - `38`
- allowlist：
  - `39`
  - 其中仅
    `云叔`
    当前未命中

### 2. male-only speech-reverb seed

命令：

```powershell
.\python.exe scripts/data/build_synthetic_dataset.py `
  --train-count 512 `
  --val-count 256 `
  --train-recipe-profile clean_speech_only `
  --val-recipe-profile clean_speech_only `
  --train-temporal-pattern-profile target_full_only `
  --val-temporal-pattern-profile target_full_only `
  --target-reverb-prob 0.0 `
  --speech-reverb-prob 0.55 `
  --output-tag same_gender_reverb_proxy_v2_seed `
  --pool-manifest-override speech_interference_clean_pool=data/manifests/speech_interference_clean_pool_same_gender_male_v1.jsonl
```

输出：

- `data/synthetic/train_manifest_same_gender_reverb_proxy_v2_seed.jsonl`
- `data/synthetic/val_manifest_same_gender_reverb_proxy_v2_seed.jsonl`
- `data/synthetic/summary_same_gender_reverb_proxy_v2_seed.json`

当前配置固定成：

- interference：
  - male-only clean speech
- recipe：
  - `target_clean_speech`
- temporal pattern：
  - `target_full`
- reverb：
  - `speech_reverb_prob = 0.55`
  - `target_reverb_prob = 0.0`

### 3. focused proxy manifest

命令：

```powershell
.\python.exe scripts/data/build_metadata_focused_manifest.py `
  --input-manifest data/synthetic/train_manifest_same_gender_reverb_proxy_v2_seed.jsonl `
  --output-manifest data/synthetic/train_manifest_same_gender_reverb_proxy_v2.jsonl `
  --recipes target_clean_speech `
  --temporal-patterns target_full `
  --min-target-ratio 0.95 `
  --min-overlap-ratio 0.75 `
  --interference-pools speech_interference_clean_pool `
  --require-interference-reverb `
  --forbid-target-reverb
```

同法生成：

- `data/synthetic/val_manifest_same_gender_reverb_proxy_v2.jsonl`

当前规模：

- train：
  - `190`
- val：
  - `100`

当前 focused manifest 的固定约束：

1. `target_clean_speech`
2. `target_full`
3. `target_present_ratio >= 0.95`
4. `overlap >= 0.75`
5. `speech_interference_clean_pool`
6. interference 必带 reverb
7. target 不带 reverb

## objective baseline

本轮已对新 proxy
直接重跑：

- `legacy_stage2 vs v32`

命令：

```powershell
.\python.exe scripts/eval/compare_checkpoints_on_manifest.py `
  --manifest data/synthetic/val_manifest_same_gender_reverb_proxy_v2.jsonl `
  --checkpoint-a experiments/checkpoints/baseline_stft_mask_stage2/best.pt `
  --checkpoint-b experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt `
  --label-a legacy_stage2 `
  --label-b v32 `
  --output-dir reports/eval/compare_stage2_vs_v32_on_same_gender_reverb_proxy_v2
```

输出：

- `reports/eval/compare_stage2_vs_v32_on_same_gender_reverb_proxy_v2/summary.json`

当前结果：

- `num_samples = 100`
- `avg_sisdr_delta_db = +0.670015`
- `improved_count = 55`
- `regressed_count = 37`
- `near_tie_count = 8`

## 当前结论

1. `same_gender_reverb_proxy_v2`
   已正式物化完成，
   不再只是一个口头预案。
2. 相比旧的
   `guodegang_proxy_v1`，
   它更贴近：
   - same-gender
   - clean speech
   - target present
   - speech-side light reverb
3. 在这个新 proxy 上，
   `v32`
   对
   `legacy_stage2`
   仍是 objective 正向，
   所以这条 proxy
   可以保留为新的 focused pre-screen 入口。
4. 但它当前不是单边碾压：
   - `55` 改善
   - `37` 回退
   - `8` 近平手
   因此它只能作为：
   - keep / drop 的 synthetic pre-screen
   不能单独替代：
   - near-real target-present same-gender 听审

## 后续建议

若下一步继续推进，
默认顺序应是：

1. 保留
   `guodegang_proxy_v1`
   作为旧 seed baseline
2. 新增
   `same_gender_reverb_proxy_v2`
   作为更贴近问题家族的 synthetic pre-screen
3. 只有当候选在：
   - `guodegang_proxy_v1`
   - `same_gender_reverb_proxy_v2`
   - bandwidth guardrail
   上都不出现明显回退时，
   才允许进入下一轮 near-real / 听审 gate
