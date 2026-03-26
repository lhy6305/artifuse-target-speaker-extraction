# 2026-03-26 present-overlap residual purify `v1` and `v82` follow-up

## 本轮目标

上一轮 `v54 vs v81` 听审已经确认：

- `v81` 虽然把 gate calibration 和 near-real guardrail 拉回健康；
- 但 `0003 / 0006 / 0007 / 0009` 的可听残余泄漏没有形成主观改善。

所以本轮不再继续做 gate target sweep，而是直接开新的机制子题：

- `present_overlap_residual_leak_purification`

目标不是让 gate 更会闭嘴，而是：

- 在 `target present + overlap` 区间内；
- 直接压低 residual speech leak；
- 同时尽量不把 keep case 再次压坏。

## 代码改动

修改：

- `src/tse_prefix/data/synthetic_dataset.py`
- `src/tse_prefix/pipeline/loss_selectors.py`
- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

新增机制：

### 1. `target_overlap_intervals`

现在 dataset 会从 metadata 里显式产出：

- `target_overlap_intervals`

生成规则：

- 优先用 `target_segments`
  - 与 interference 开始后的区间做交集
- 若没有 `target_segments`
  - 则从整体 overlap 区间中减去 `target_absent_intervals`

这保证 intermittent target 不会把 absent gap 误算进 overlap loss。

### 2. `overlap_interval_interference_projection_loss`

在 `baseline_train.py` 新增：

- `overlap_interval_interference_projection_loss()`

作用：

- 只在 `target_overlap_intervals` 内部计算 interference projection；
- 不再把全局静音误当成主要优化方向；
- 直接针对“重叠段 residual leak”本身施压。

Loss breakdown 也新增：

- `overlap_interference_projection_ratio`
- `overlap_interference_extra_projection_ratio`

### 3. 新 CLI / selector 入口

训练脚本新增：

- `--loss-overlap-interference-weight`
- `--loss-overlap-interference-extra-weight`
- `--loss-overlap-interference-mode`
- `--loss-overlap-interference-extra-mode`

并新增独立 selector 前缀：

- `overlap_interference`

这意味着后续可以单独筛：

- high-overlap
- speech-only interference
- weak / medium target audibility

而不会污染已有 `interference` selector。

## 新训练

### `v82 = v81 + overlap residual purify v1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v82_v81_overlap_purify_v1_ft1`

训练口径：

- init：
  - `v81`
- 只训：
  - `branch_decoder_mask_head`
- 保留：
  - `reconstruction_extra`
  - `branch_protect`
  两条 keep 约束
- 新开：
  - `overlap_interference_extra_weight = 0.03`
  - `overlap_interference_extra_mode = residual_projection_ratio`

新 overlap selector：

- `target_full`
- `interference_pool in {speech_interference_clean_pool, speech_interference_hard_pool}`
- `overlap_ratio >= 0.6`
- `0.05 <= target_energy_ratio <= 0.22`
- `target_transient_presence_share_mean <= 0.04`

解释：

- 只把新 loss 压到“重叠明显、目标偏弱但仍存在、且干扰是语音”的子集上；
- 不主动去推 absent case；
- 也不碰 music-only overlap。

训练期信号：

- train `overlap_interference_extra_projection_ratio`
  - epoch1 `0.0187`
  - epoch4 `0.0181`
- val `overlap_interference_extra_projection_ratio`
  - `0.01209 -> 0.01130`

说明：

- 新 overlap loss 确实被激活；
- 而且不是纯 no-op。

## 结果

### A. overlap abstention proxy：`v82` 没有牺牲弱目标静音

- `reports/eval/compare_v81_vs_v82_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = +2.8258`
  - `7` improve / `1` regress

解释：

- `v82` 不是那种“为了 keep 把 abstention 又拉回去”的假改进；
- 它在弱目标 overlap proxy 上反而更强。

### B. same-gender keep guardrail：`v82` 全量正收益

- `reports/eval/compare_v81_vs_v82_on_same_gender_present_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +1.2533`
  - `11` improve / `0` regress

解释：

- 新 overlap residual loss 没有把 same-gender keep 再次压坏；
- 相反，这条 guardrail 是全量改善。

### C. hard-present keep guardrail：也整体改善

- `reports/eval/compare_v81_vs_v82_on_hard_present_gate_keep_guardrail_v1/summary.json`
  - `avg_sisdr_delta_db = +1.0219`
  - `13` improve / `2` regress / `1` near tie

解释：

- 这说明 `v82` 不是简单的 over-silence 回退；
- 它在 hard-present synthetic 上也整体更强。

### D. near-real residual leak floor：`0003 / 0006 / 0009` 更好，但 `0007` 重新黄灯

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v81_v82/summary.json`

关键结果：

- `combined_rank`
  - `v82 > v81 > v54`
- 但 `guardrail_filtered_rank`
  - `v81 > v54 > v82`

原因：

- `v82 present_guardrail_violation_count = 1`
- `target_capture_regression_sample_ids = [near_real_0007]`

逐样本相对 `v81`：

- `near_real_0003`
  - `target_capture_db = -1.155 dB`
  - `interference_capture_db = -2.249 dB`
- `near_real_0006`
  - `target_capture_db = -0.976 dB`
  - `interference_capture_db = -1.857 dB`
- `near_real_0007`
  - `target_capture_db = -1.449 dB`
  - `interference_capture_db = -1.240 dB`
  - 因为相对 `v54` 的 capture 回退超过阈值，形成 `1` 条 guardrail violation
- `near_real_0009`
  - `interference_capture_db = -0.186 dB`

解释：

- `v82` 的方向是对的：
  - `0003 / 0006 / 0009` 都更静
  - 而且泄漏降低幅度大于或接近 target capture 的损失
- 但它还没有安全到可以直接放行；
  - `0007` 这条 hard-present 重新被压过线了。

## 本轮裁决

1. `present_overlap_residual_leak_purification` 是有效方向。
   - 这不是新的伪 proxy。
   - 第一轮 `v82` 已经证明：直接打 overlap residual leak，可以同时推高 abstention proxy、same-gender keep、hard-present keep 三条 synthetic 线。

2. `v82` 是当前第一条真正碰到“残余泄漏本体”的 pilot。
   - 相对 `v81`，它不是纯 calibration 改动；
   - objective 改善也不是单边的。

3. `v82` 还不能自动升格。
   - near-real 上 `0007` 重新出现 `1` 条 present guardrail violation；
   - 所以当前不能仅凭 objective / combined rank 放行。

## 下一步

当前默认下一步不是继续扫 `v82 / v83` 权重，而是先做 focused 听审确认这条新 tradeoff 是否值得继续。

我已经导出：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v82_blind`

并已通过资产审计：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v82_blind/asset_audit_summary.json`
  - `all_mono = true`
  - `all_have_target = true`

默认听审重点：

- `near_real_0003`
  - 泄漏是否真的更少，且没更空
- `near_real_0006`
  - 重叠段是否终于更干净
- `near_real_0007`
  - `v82` 是否出现可听的误伤
- `near_real_0009`
  - absent 是否至少没回退

如果听审确认：

- `0003 / 0006` 有可听改善；
- `0007` 的回退不可感知或可接受；

则下一步才值得做：

- `v83`
  - 在 `v82` 基础上专门补 `0007` 风格 hard-present keep 回拉

如果听审确认：

- `0007` 的误伤已经可听；
- 而 `0003 / 0006` 仍没有可听提升；

则应收口当前 `v82` 配方，不再继续沿同一 selector 放大。
