# 2026-03-28 split-selector head-only direct-apply `v138 / v139 / v140 / v141 / v142` follow-up

## Summary

- 在 `v136 / v137`
  已经证明
  `auxiliary_only` true-absent indirect path
  有局部正证据、
  但还不能转成 whole / listening 优势之后，
  这轮补了两件关键事：
  - 先把
    `overlap_cancel_waveform / target_projection`
    与
    `overlap_cancel_absent_mix`
    的 selector sample weights
    正式拆开，
    允许同一 head
    同时吃
    present-total 和 absent-local
    两套不同选择器；
  - 再沿着
    `head-only + bounded direct apply`
    这条更保守的路径，
    验证 `0007 total leak`
    能否在不打穿 guardrail
    的前提下继续推进
- 结果分五步：
  - `v138 = v126 + overlap-cancel total-leak 0007-like self-anchor blend05 v1`
    - safe / near-no-op
    - relative `v126`
      synthetic 与 near-real
      都接近全 tie
    - 只保留为
      “head-only bounded subtract path
      可以保持安全”
      的证据点
  - `v139 = v126 + split-selector auxcancel total-leak + absent-mix self-anchor v1`
    - split-selector 机制真实生效
    - `near_real_0009`
      absent local
      被强力打中
    - `near_real_0007 speech_only`
      local leak
      也出现局部改善
    - 但 whole `0003 / 0006 / 0007`
      全都更 leak，
      `0007 total leak`
      也更差，
      直接 reject
  - `v140 = v126 + head-only auxcancel hardlocaltotal absentmix self-anchor v1`
    - 训练不是 no-op，
      但推理是 exact no-op
    - relative `v126`
      四条 fixed synthetic checks
      全是 `0.0 dB`
    - 说明
      `head-only + auxiliary_only`
      在这条家族里
      没有任何输出路径
  - `v141 = v126 + head-only split-selector subtract blend05 absentmix v1`
    - 首个
      `head-only + bounded direct apply`
      且带 split selectors
      的真实 pilot
    - whole `0003 / 0006 / 0009`
      与 local `0007 total leak`
      都给出正证据
    - 但 `0007 speech_only`
      与 `0009 absent local`
      同时明显转坏，
      说明
      同一个 direct-apply cancel head
      不能同时承载
      present-total 与 absent-local
  - `v142 = v126 + head-only hardlocaltotal subtract blend05 v1`
    - 去掉 absent supervision 后，
      四条 fixed synthetic checks
      重新成为这轮最干净的一组正向结果
    - whole `0009` absent、
      whole/local `0006`、
      local `0007 total leak`
      都继续改善
    - 但 `0007 speech_only local leak`
      与 `0009 absent local`
      仍没解掉，
      所以仍不到 listening candidate
- 裁决：
  - `v138 = safe no-op reject`
  - `v139 = mechanism-positive but whole-regressive reject`
  - `v140 = structural inference no-op boundary`
  - `v141 = mixed mechanism-positive reject`
  - `v142 = current best continuation in head-only direct-apply subfamily, but still not promotable`
- 当前主结论更新为：
  - `v126`
    仍是全局最佳 automatic continuation
  - `v142`
    是
    `head-only bounded direct-apply`
    这条子线当前最好的 continuation
  - 下一步如果继续，
    不该再把 absent-local
    直接塞回同一个 direct-apply cancel head，
    而应改成更强解耦的 absent path

## Mechanism Materialization

- 这轮先补了一个必要接线：
  - `overlap_cancel_waveform / target_projection`
    继续走
    present-total selector
  - `overlap_cancel_absent_mix`
    改为可单独走
    absent selector
- 对应代码落点：
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
- 新边界：
  - 之后凡是做
    `split-selector overlap_cancel`
    实验，
    都必须区分：
    - present-total sample weights
    - absent-mix sample weights
  - 不能再把两类 loss
    共绑到同一个
    generic `overlap_cancel_sample_weights`

## `v138 = v126 + overlap-cancel total-leak 0007-like self-anchor blend05 v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v138_v126_overlapcancel_totalleak_0007like_selfanchor_blend05_v1_ft1`
- 关键机制：
  - `branch_overlap_cancel_apply_mode = subtract`
  - `branch_overlap_cancel_delta_blend_mode = complement`
  - `branch_overlap_cancel_max_blend = 0.5`
  - 聚焦 `0007-like total leak`
    的 bounded subtract probe

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.0061 dB`
  - `improved = 0`
  - `regressed = 0`
  - `near_tie = 8`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0027 dB`
  - `improved = 0`
  - `regressed = 0`
  - `near_tie = 11`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0047 dB`
  - `improved = 0`
  - `regressed = 0`
  - `near_tie = 16`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.0023 dB`
  - `improved = 0`
  - `regressed = 0`
  - `near_tie = 7`

## Near-Real relative `v126`

- 评估目录：
  - `reports/eval/ab_inference_residual_speech_leak_floor_v1_v126_vs_v138_all`
- whole summary：
  - `better_source_retention = tie:7, not_applicable:3`
  - `more_interference_leaky = tie:7, file_b:1, not_applicable:2`
  - `better_retention_minus_leak = tie:5, not_applicable:5`
- whole means：
  - `v126`
    - `target_capture_db = -11.9696`
    - `interference_capture_db = -50.0757`
    - `retention_minus_leak_db = 36.5219`
  - `v138`
    - `target_capture_db = -11.9694`
    - `interference_capture_db = -49.9453`
    - `retention_minus_leak_db = 36.6201`
- 仅有可见 whole 回退样本：
  - `near_real_0008`
    - `delta_interference_capture_db = +1.3024 dB`
- overlap-local summary：
  - `more_speech_interference_leaky = tie:4`
  - `more_total_interference_leaky = tie:4`
  - `better_retention_minus_speech_leak = tie:3, not_applicable:1`
  - `better_retention_minus_total_leak = tie:3, not_applicable:1`
- `near_real_0007 / 0009`
  的 local 数字
  虽有轻微错误方向，
  但都低于当前裁决阈值

结论：

- `v138`
  基本是 safe / near-no-op；
- 它不构成真实候选，
  但补出了一个重要安全边界：
  - `head-only bounded subtract path`
    可以做到
    基本不动主输出

## `v139 = v126 + split-selector auxcancel total-leak + absent-mix self-anchor v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v139_v126_splitselector_auxcancel_totalleak_absentmix_selfanchor_v1_ft1`
- 关键机制：
  - 保留
    `branch_overlap_cancel_apply_mode = auxiliary_only`
  - 对同一个
    `branch_overlap_cancel_head`
    拆两套 selector：
    - present-total：
      `0007-like total leak`
    - absent-local：
      true-absent mix target

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -0.0720 dB`
  - `improved = 2`
  - `regressed = 4`
  - `near_tie = 2`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.0702 dB`
  - `improved = 1`
  - `regressed = 3`
  - `near_tie = 7`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.0122 dB`
  - `improved = 3`
  - `regressed = 5`
  - `near_tie = 8`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = -0.0565 dB`
  - `improved = 3`
  - `regressed = 3`
  - `near_tie = 1`

结论：

- fixed synthetic checks
  是轻微负向，
  但还没到直接打穿 guardrail
  的程度；
- 因此继续补 near-real
  看 split-selector
  是否有实质局部价值

## Whole Near-Real relative `v126`

- 评估目录：
  - `reports/eval/ab_inference_residual_speech_leak_floor_v1_v126_vs_v139_all`
- 汇总：
  - `better_source_retention = tie:2, v139:1, n/a:1`
  - `more_interference_leaky = v139:4`
  - `better_retention_minus_leak = v126:3, n/a:1`
- means：
  - `v126`
    - `target_capture_db = -13.5673`
    - `interference_capture_db = -41.2502`
    - `retention_minus_leak_db = 28.8388`
  - `v139`
    - `target_capture_db = -13.3651`
    - `interference_capture_db = -38.4818`
    - `retention_minus_leak_db = 25.8326`
- 关键样本：
  - `near_real_0009`
    - `delta_interference_capture_db = +1.4486 dB`
  - `near_real_0007`
    - `delta_target_capture_db = +0.8483 dB`
    - `delta_interference_capture_db = +6.3064 dB`
    - `delta_retention_minus_leak_db = -5.4580 dB`
  - `near_real_0003`
    - `delta_interference_capture_db = +1.2475 dB`
    - `delta_retention_minus_leak_db = -1.5693 dB`
  - `near_real_0006`
    - `delta_interference_capture_db = +2.0712 dB`
    - `delta_retention_minus_leak_db = -1.9911 dB`

## Overlap-Local relative `v126`

- 汇总：
  - `more_speech_interference_leaky = v139:2, v126:2`
  - `more_total_interference_leaky = v139:3, v126:1`
  - `better_retention_minus_speech_leak = v126:2, v139:1, n/a:1`
  - `better_retention_minus_total_leak = v126:3, n/a:1`
- 关键样本：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = -24.4329 dB`
    - `delta_total_interference_capture_db = -24.4329 dB`
  - `near_real_0007`
    - `delta_target_capture_db = +0.7372 dB`
    - `delta_speech_interference_capture_db = -1.1327 dB`
    - `delta_total_interference_capture_db = +3.0186 dB`
    - `delta_retention_minus_speech_leak_db = +1.8699 dB`
    - `delta_retention_minus_total_leak_db = -2.2814 dB`
  - `near_real_0006`
    - `delta_speech_interference_capture_db = +2.9425 dB`
    - `delta_retention_minus_speech_leak_db = -2.8611 dB`
  - `near_real_0003`
    - `delta_speech_interference_capture_db = +1.2258 dB`
    - `delta_retention_minus_speech_leak_db = -1.5476 dB`

结论：

- `v139`
  证明 split-selector 机制本身是真实的：
  - `0009 absent local`
    能被强力打中
  - `0007 speech_only`
    也能在 local 里改善
- 但它同时暴露了更强失败边界：
  - 只要这条 signal
    仍共享当前
    `mask-head transfer`
    路径，
    whole leak
    和 `0007 total leak`
    就会被推坏
- 因而 `v139`
  直接 reject，
  不导听审

## `v140 = v126 + head-only auxcancel hardlocaltotal absentmix self-anchor v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v140_v126_headonly_auxcancel_hardlocaltotal_absentmix_selfanchor_v1_ft1`
- 关键机制：
  - 只训练：
    - `branch_overlap_cancel_head`
  - 保留 split selectors：
    - `overlap_cancel`
      只吃
      `hard_present_artifact_local_proxy_v1_all`
    - `absent`
      只吃
      true-absent local windows
  - 但 apply
    仍是
    `branch_overlap_cancel_apply_mode = auxiliary_only`

## Training Signal

- 训练不是 no-op：
  - `overlap_cancel`
    selector 命中：
    - train `3 / 203`
    - val `3 / 63`
  - `absent`
    selector 命中：
    - train `95 / 203`
    - val `24 / 63`
  - 末轮：
    - `train_overlap_cancel_waveform_l1 = 0.0086242`
    - `val_overlap_cancel_waveform_l1 = 0.0281501`
    - `train_overlap_cancel_absent_mix_l1 = 0.0365149`
    - `val_overlap_cancel_absent_mix_l1 = 0.0522065`

## Fixed Checks relative `v126`

- 四条 fixed synthetic checks
  全是 exact tie：
  - abstention `+0.0000 dB`
  - same-gender keep `+0.0000 dB`
  - hard-present keep `+0.0000 dB`
  - artifact proxy `+0.0000 dB`

结论：

- `v140`
  的 loss-side training signal
  是真实存在的，
  但 inference side
  是结构性 no-op；
- 新边界明确为：
  - 在当前这条 family 里，
    `head-only + auxiliary_only`
    没有任何回写 final output
    的路径，
    因而不可能成为真实候选

## `v141 = v126 + head-only split-selector subtract blend05 absentmix v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v141_v126_headonly_splitselector_subtractblend05_absentmix_v1_ft1`
- 相对 `v140`
  只改一件事：
  - `branch_overlap_cancel_apply_mode = subtract`
  - `branch_overlap_cancel_delta_blend_mode = complement`
  - `branch_overlap_cancel_max_blend = 0.5`

## Training Signal

- selector 仍真实命中：
  - `overlap_cancel`
    - train `3 / 203`
    - val `3 / 63`
  - `absent`
    - train `95 / 203`
    - val `24 / 63`
- 末轮：
  - `train_overlap_cancel_waveform_l1 = 0.0086238`
  - `val_overlap_cancel_waveform_l1 = 0.0281501`
  - `train_overlap_cancel_absent_mix_l1 = 0.0365135`
  - `val_overlap_cancel_absent_mix_l1 = 0.0522065`

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.1037 dB`
  - `improved = 4`
  - `regressed = 0`
  - `near_tie = 4`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.1139 dB`
  - `improved = 4`
  - `regressed = 0`
  - `near_tie = 7`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0121 dB`
  - `improved = 4`
  - `regressed = 3`
  - `near_tie = 9`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.0178 dB`
  - `improved = 1`
  - `regressed = 0`
  - `near_tie = 6`

## Whole Near-Real relative `v126`

- 评估目录：
  - `reports/eval/ab_inference_residual_speech_leak_floor_v1_v126_vs_v141_all`
- 汇总：
  - `better_source_retention = tie:3, n/a:1`
  - `more_interference_leaky = v126:3, v141:1`
  - `better_retention_minus_leak = v141:2, v126:1, n/a:1`
- means：
  - `v126`
    - `target_capture_db = -13.5673`
    - `interference_capture_db = -41.2502`
    - `retention_minus_leak_db = 28.8388`
  - `v141`
    - `target_capture_db = -13.7060`
    - `interference_capture_db = -43.7342`
    - `retention_minus_leak_db = 24.7512`
- 关键样本：
  - `near_real_0009`
    - `delta_interference_capture_db = -21.7825 dB`
  - `near_real_0003`
    - `delta_interference_capture_db = -1.7272 dB`
    - `delta_retention_minus_leak_db = +1.7180 dB`
  - `near_real_0006`
    - `delta_interference_capture_db = -3.1749 dB`
    - `delta_retention_minus_leak_db = +3.1673 dB`
  - `near_real_0007`
    - `delta_target_capture_db = -0.3993 dB`
    - `delta_interference_capture_db = +16.7487 dB`
    - `delta_retention_minus_leak_db = -17.1479 dB`

## Overlap-Local relative `v126`

- 汇总：
  - `more_speech_interference_leaky = v126:2, v141:2`
  - `more_total_interference_leaky = v126:3, v141:1`
  - `better_retention_minus_speech_leak = tie:1, v141:1, v126:1, n/a:1`
  - `better_retention_minus_total_leak = tie:1, v141:2, n/a:1`
  - `more_artifact_proxy_heavy = tie:3, v126:1`
- 关键样本：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = +21.0921 dB`
    - `delta_total_interference_capture_db = +21.0921 dB`
  - `near_real_0007`
    - `delta_target_capture_db = -0.2323 dB`
    - `delta_speech_interference_capture_db = +13.4400 dB`
    - `delta_total_interference_capture_db = -19.5934 dB`
    - `delta_retention_minus_speech_leak_db = -13.6723 dB`
    - `delta_retention_minus_total_leak_db = +19.3612 dB`
  - `near_real_0006`
    - `delta_speech_interference_capture_db = -4.3632 dB`
    - `delta_total_interference_capture_db = -4.3632 dB`
    - `delta_retention_minus_speech_leak_db = +4.3557 dB`
  - `near_real_0003`
    - `delta_speech_interference_capture_db = -0.6221 dB`
    - `delta_total_interference_capture_db = -0.6221 dB`
    - `delta_retention_minus_speech_leak_db = +0.6129 dB`

结论：

- `v141`
  首次证明：
  - `head-only bounded direct-apply`
    可以真实改善
    whole `0003 / 0006 / 0009`
  - 同时也能把
    `0007 total leak`
    往正确方向拉
- 但它更明确地证明了另一条边界：
  - 同一个 direct-apply cancel head
    不能同时承载
    `present-total`
    和
    `absent-local`
  - 一旦 absent supervision
    也灌进来，
    `0009 absent local`
    与 `0007 speech_only`
    会一起翻坏
- 因而 `v141`
  是 mixed mechanism-positive reject，
  不导听审

## `v142 = v126 + head-only hardlocaltotal subtract blend05 v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v142_v126_headonly_hardlocaltotal_subtractblend05_v1_ft1`
- 相对 `v141`
  移除：
  - `loss_overlap_cancel_absent_mix_weight`
  - 所有 absent selectors
- 保留：
  - `branch_overlap_cancel_apply_mode = subtract`
  - `branch_overlap_cancel_delta_blend_mode = complement`
  - `branch_overlap_cancel_max_blend = 0.5`
  - `hard_present_artifact_local_proxy_v1_all`
    作为 present-total selector

## Training Signal

- `overlap_cancel`
  selector 命中：
  - train `3 / 203`
  - val `3 / 63`
- absent 侧已彻底移除：
  - `train_overlap_cancel_absent_mix_l1 = 0.0`
  - `val_overlap_cancel_absent_mix_l1 = 0.0`
- 末轮：
  - `train_overlap_cancel_waveform_l1 = 0.0088271`
  - `val_overlap_cancel_waveform_l1 = 0.0290104`

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = +0.1949 dB`
  - `improved = 4`
  - `regressed = 0`
  - `near_tie = 4`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0894 dB`
  - `improved = 2`
  - `regressed = 0`
  - `near_tie = 9`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = +0.0848 dB`
  - `improved = 5`
  - `regressed = 1`
  - `near_tie = 10`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = +0.0696 dB`
  - `improved = 2`
  - `regressed = 0`
  - `near_tie = 5`

## Whole Near-Real relative `v126`

- 评估目录：
  - `reports/eval/ab_inference_residual_speech_leak_floor_v1_v126_vs_v142_all`
- 汇总：
  - `better_source_retention = tie:3, n/a:1`
  - `more_interference_leaky = tie:1, v126:2, v142:1`
  - `better_retention_minus_leak = tie:1, v142:1, v126:1, n/a:1`
- means：
  - `v126`
    - `target_capture_db = -13.5673`
    - `interference_capture_db = -41.2502`
    - `retention_minus_leak_db = 28.8388`
  - `v142`
    - `target_capture_db = -13.6155`
    - `interference_capture_db = -42.0525`
    - `retention_minus_leak_db = 28.1440`
- 关键样本：
  - `near_real_0009`
    - `delta_interference_capture_db = -5.1486 dB`
  - `near_real_0006`
    - `delta_interference_capture_db = -1.1233 dB`
    - `delta_retention_minus_leak_db = +1.1203 dB`
  - `near_real_0003`
    - `delta_interference_capture_db = -0.4307 dB`
    - `delta_retention_minus_leak_db = +0.4275 dB`
  - `near_real_0007`
    - `delta_target_capture_db = -0.1384 dB`
    - `delta_interference_capture_db = +3.4937 dB`
    - `delta_retention_minus_leak_db = -3.6321 dB`

## Overlap-Local relative `v126`

- 汇总：
  - `more_speech_interference_leaky = tie:1, v126:1, v142:2`
  - `more_total_interference_leaky = tie:1, v126:2, v142:1`
  - `better_retention_minus_speech_leak = tie:1, v142:1, v126:1, n/a:1`
  - `better_retention_minus_total_leak = tie:1, v142:2, n/a:1`
  - `more_artifact_proxy_heavy = tie:3, v126:1`
- 关键样本：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = +14.5135 dB`
    - `delta_total_interference_capture_db = +14.5135 dB`
  - `near_real_0007`
    - `delta_target_capture_db = -0.0806 dB`
    - `delta_speech_interference_capture_db = +6.4977 dB`
    - `delta_total_interference_capture_db = -3.2201 dB`
    - `delta_retention_minus_speech_leak_db = -6.5784 dB`
    - `delta_retention_minus_total_leak_db = +3.1394 dB`
  - `near_real_0006`
    - `delta_speech_interference_capture_db = -1.4526 dB`
    - `delta_total_interference_capture_db = -1.4526 dB`
    - `delta_retention_minus_speech_leak_db = +1.4496 dB`
  - `near_real_0003`
    - `delta_speech_interference_capture_db = -0.1702 dB`
    - `delta_total_interference_capture_db = -0.1702 dB`
    - `delta_retention_minus_speech_leak_db = +0.1670 dB`

结论：

- `v142`
  证明：
  - present-total bounded direct path
    本身是有效且相对安全的
  - 它可以同时改善：
    - fixed synthetic guardrails
    - whole `0009` absent
    - whole/local `0006`
    - local `0007 total leak`
- 但它也明确保留了两个 blocker：
  - `0007 speech_only local leak`
    仍明显更差
  - `0009 absent local`
    仍明显更差
- 因而当前结论是：
  - `v142`
    接替 `v141`
    成为这条
    `head-only bounded direct-apply`
    子线的最佳 continuation
  - 但它仍不是 listening candidate，
    也不能替代 `v126`

## Final Verdict

- 全局主线结论不变：
  - `v126`
    仍是当前最佳 automatic continuation
- 子线结论新增：
  - `v142`
    是
    `head-only bounded direct-apply`
    的最佳 continuation
  - `v138`
    是安全 no-op 边界
  - `v140`
    是结构性 inference no-op 边界
  - `v141`
    证明同一个 direct-apply cancel head
    不能同时承载
    present-total 与 absent-local
- 下一步如果继续：
  - 不再扫
    `absent_mix weight`
    或同构的同头混训
  - 应改做：
    - 更强解耦的 absent path
    - 或只保留 `v142`
      这条 present-total direct path，
      另找独立机制处理
      `0007 speech_only`
      与 `0009 absent local`
