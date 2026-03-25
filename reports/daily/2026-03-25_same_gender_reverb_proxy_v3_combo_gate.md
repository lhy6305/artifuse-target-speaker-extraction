# 2026-03-25 same_gender reverb proxy v3 combo gate

## 背景

你在 `same_gender_reverb_proxy_v2` target-present GUI 听审里给出的主观反馈是：

- 有时像是把目标声也加了混响
- `speech-only reverb` 这一类 synthetic gate 不足以解释真实听感

同时，刚完成的 v2 听审解盲结果对 `v32` 不利：

- `legacy_stage2 = 6`
- `tie = 2`
- `uncertain = 2`
- `v32 = 0`

因此下一步不再只看 `speech-only reverb`，而是把混响拆成四个可直接听审的组合：

1. 都不加
2. 只给目标加
3. 只给干扰加
4. 目标和干扰都加

## 组合 seed 与 objective 分桶

本轮先物化了一个 mixed-reverb seed：

- `data/synthetic/train_manifest_same_gender_reverb_proxy_v3_combo_seed.jsonl`
- `data/synthetic/val_manifest_same_gender_reverb_proxy_v3_combo_seed.jsonl`
- `data/synthetic/summary_same_gender_reverb_proxy_v3_combo_seed.json`

构造方式：

```powershell
.\python.exe scripts/data/build_synthetic_dataset.py `
  --train-count 512 `
  --val-count 256 `
  --train-recipe-profile clean_speech_only `
  --val-recipe-profile clean_speech_only `
  --train-temporal-pattern-profile target_full_only `
  --val-temporal-pattern-profile target_full_only `
  --target-reverb-prob 0.5 `
  --speech-reverb-prob 0.5 `
  --output-tag same_gender_reverb_proxy_v3_combo_seed `
  --pool-manifest-override speech_interference_clean_pool=data/manifests/speech_interference_clean_pool_same_gender_male_v1.jsonl
```

然后把 val 侧切成四个严格组合：

- `data/synthetic/val_manifest_same_gender_reverb_proxy_v3_none.jsonl`
- `data/synthetic/val_manifest_same_gender_reverb_proxy_v3_target_only.jsonl`
- `data/synthetic/val_manifest_same_gender_reverb_proxy_v3_speech_only.jsonl`
- `data/synthetic/val_manifest_same_gender_reverb_proxy_v3_both.jsonl`

`legacy_stage2 vs v32` 的 objective 分桶结果：

- `none`: `51` 条，`avg_sisdr_delta_db = +1.1064`
- `target_only`: `41` 条，`avg_sisdr_delta_db = +1.0708`
- `speech_only`: `46` 条，`avg_sisdr_delta_db = +0.9484`
- `both`: `57` 条，`avg_sisdr_delta_db = +1.0905`

结论非常明确：

- 四个组合在 objective 上都仍然偏向 `v32`
- 但上一包人耳听审却明显偏向 `legacy_stage2`
- 所以当前 objective 指标还没有抓住“目标被加混响 / 目标更假”的真实感知失败模式

## 新导出的 combo gate

当前已导出 blind GUI 包：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v3_combo_gate_stage2_vs_v32_blind`

导包命令：

```powershell
.\python.exe scripts/eval/export_ab_listening_pack.py `
  --manifest data/synthetic/val_manifest_same_gender_reverb_proxy_v3_combo_gate.jsonl `
  --checkpoint-a experiments/checkpoints/baseline_stft_mask_stage2/best.pt `
  --checkpoint-b experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1/best.pt `
  --label-a legacy_stage2 `
  --label-b v32 `
  --focus-recipes target_clean_speech `
  --max-samples 12 `
  --stable-count 4 `
  --blind `
  --output-dir reports/eval/ab_listening_pack_same_gender_reverb_proxy_v3_combo_gate_stage2_vs_v32_blind
```

当前这包不是随机抽样，而是每个组合各取三条：

- 一条 objective 最强改善
- 一条 objective 最强回退
- 一条 objective 近平手

样本级组合摘要已落盘：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v3_combo_gate_stage2_vs_v32_blind/combo_gate_selection_summary.json`

分层覆盖如下：

- `none`: `val_000019`, `val_000150`, `val_000039`
- `target_only`: `val_000252`, `val_000035`, `val_000229`
- `speech_only`: `val_000045`, `val_000043`, `val_000197`
- `both`: `val_000062`, `val_000212`, `val_000183`

## 资产审计与 bandwidth 预分析

资产审计已通过：

- `all_mono = true`
- `all_have_target = true`
- `missing_target_count = 0`
- `non_mono_file_count = 0`

落盘：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v3_combo_gate_stage2_vs_v32_blind/asset_audit_summary.json`

bandwidth 预分析结果：

- `num_samples = 12`
- `narrower_candidate_counts.tie = 5`
- `narrower_candidate_counts.file_b = 5`
- `narrower_candidate_counts.file_a = 2`

其中最需要额外盯听的样本：

- `val_000252`，`target_only`，当前 heuristic 指向 `v32` 更窄带
- `val_000035`，`target_only`，当前 heuristic 指向 `v32` 更窄带
- `val_000062`，`both`，当前 heuristic 指向 `v32` 更窄带
- `val_000183`，`both`，当前 heuristic 指向 `v32` 更窄带

落盘：

- `reports/eval/ab_listening_pack_same_gender_reverb_proxy_v3_combo_gate_stage2_vs_v32_blind/bandwidth_analysis/summary.json`

## 当前裁决口径

到这一步为止，最重要的结论不是“哪种混响组合已经证实是根因”，而是：

1. 只做 `speech-only reverb` gate 不够，会误导决策。
2. 不能再把 objective 正收益当成放行训练的充分条件。
3. 下一步必须做这包 combo-stratified GUI 听审，判断失败感知到底集中在哪个组合。

如果听审显示问题主要集中在：

- `target_only`
  - 就说明“目标侧混响”是高优先级风险轴
- `speech_only`
  - 说明旧判断并没错，问题主要还是干扰侧空间化
- `both`
  - 说明 joint reverb 交互项才是真正破坏点
- `none`
  - 说明混响不是主因，问题要回到别的声学轴

## 下一步

直接用 GUI 听这包：

```powershell
.\python.exe scripts/eval/listening_pack_gui.py --pack-dir reports/eval/ab_listening_pack_same_gender_reverb_proxy_v3_combo_gate_stage2_vs_v32_blind
```

听的时候优先判断：

1. 目标人声是否被“空间化”得更假、更远、更空
2. 抑制变强时，是否伴随目标高频被削薄
3. `target_only` 与 `both` 组是否比另外两组更容易触发这个问题
4. objective 强改善样本里，主观是否真的改善，还是只是“压得更多”
