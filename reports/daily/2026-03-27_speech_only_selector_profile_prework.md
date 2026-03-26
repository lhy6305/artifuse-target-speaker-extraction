# speech-only selector profile prework

## 本轮目的

在不开新训练的前提下，先补齐一个必要前置条件：

- 让训练 selector 能可靠区分：
  - `speech_only`
  - `speech_plus_music`
- 避免 `target_hard_plus_music` 因为“第一层是 speech”而被错误选进 `speech-only overlap` 子域。

## 代码改动

- `src/tse_prefix/data/synthetic_dataset.py`
  - 保留原有 `interference_pool` / `interference_speaker_name` 兼容字段；
  - 新增派生元数据：
    - `interference_layer_count`
    - `interference_profile`
    - `has_speech_interference`
    - `has_music_interference`
    - `has_other_interference`
    - `interference_pools_all`
    - `interference_speaker_names_all`
- `src/tse_prefix/pipeline/loss_selectors.py`
  - 新增 selector 键：
    - `focus_interference_profiles`
    - `require_speech_interference`
    - `require_music_interference`
    - `require_other_interference`
    - `min_interference_layer_count`
    - `max_interference_layer_count`
- `scripts/train/train_stft_mask_baseline.py`
  - 训练 CLI 暴露上述 selector 参数；
  - 布尔 selector 采用显式 `true|false|1|0|yes|no` 解析，保留 `None` 三态语义。

## 自检

自检 manifest：

- `data/synthetic/train_manifest_abstention_gate_bundle_v2.jsonl`

统计结果：

- `target_clean_speech = 34`
  - 全部为 `speech_only`
- `target_hard_speech = 17`
  - 全部为 `speech_only`
- `target_clean_plus_music = 30`
  - 全部为 `speech_plus_music`
- `target_hard_plus_music = 21`
  - 全部为 `speech_plus_music`

selector 自检条件：

```text
focus_interference_profiles = speech_only
require_speech_interference = true
require_music_interference = false
```

selector 命中结果：

- 共选中 `51` 条
- 命中 recipe：
  - `target_clean_speech = 34`
  - `target_hard_speech = 17`
- 误选 `plus_music = 0`

## 结论

- 现在已经不需要额外重做一套“speech-only manifest”；
- 只靠现有 synthetic manifest + 新 selector，就能稳定定义纯 speech overlap 子域；
- 下一步可以直接开：
  - 基于 `v81`
  - 面向 `speech_only overlap` 的 local residual suppressor pilot
  - 同时保留 hard-present artifact guardrail。

## pilot 配置约束

首个 pilot 至少应带上这组 selector：

```text
--loss-overlap-interference-focus-interference-profiles speech_only
--loss-overlap-interference-require-speech-interference true
--loss-overlap-interference-require-music-interference false
--loss-overlap-interference-min-interference-layer-count 1
--loss-overlap-interference-max-interference-layer-count 1
```

基座 checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v81_v79_audibility_gate_target_v1_ft1/best.pt`

## 未做

- 本轮还没有启动新的训练；
- 也还没有决定首个 pilot 最终挂在哪个 branch/head 家族上；
- 当前只完成了“纯 speech overlap 子域可被稳定筛选”的前置工作。
