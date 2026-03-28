# 2026-03-28 true-absent aux-cancel indirect `v136 / v137` follow-up

## Summary

- 在 `v133 / v134 / v135` 收口了
  `gate-head-only absent veto / keep`
  之后，
  这轮转向更强解耦的
  `auxiliary_only` true-absent indirect path：
  - 不直接监督 final output
  - 不经 `gate_controller`
    回灌 global gate
  - 改为只训练：
    - `branch_decoder_mask_head`
    - `branch_overlap_cancel_head`
  - 用真实 absent-local 窗口
    监督 auxiliary
    `overlap_cancel_prediction`
    去拟合 `mixture`
- 结果分两步：
  - `v136 = v126 + true-absent auxiliary-only overlap-cancel absent-mix 0.02`
    - 不是 no-op：
      - `overlap_cancel` selector
        命中
        `95 / 203` train、
        `24 / 63` val
      - `overlap_cancel_absent_mix_l1`
        全程显著非零
    - relative `v126`
      四条 fixed synthetic checks
      仅轻微负向，
      没有出现
      `v127 / v131 / v132 / v134 / v135`
      那种直接打穿 guardrail 的情形
    - near-real / overlap-local
      也第一次给出了
      真正可用的局部正证据：
      - `near_real_0009`
        absent local leak
        明显下降
      - `near_real_0007`
        `speech_only` local leak
        也明显下降
    - 但 whole near-real
      仍然失败：
      `0003 / 0006 / 0007`
      都更 leak，
      `retention_minus_leak`
      也整体回退，
      所以不升格、不出听审
  - `v137 = v136 + overlap_cancel_absent_mix_weight 0.01`
    - 训练 selector
      和 absent-mix loss
      仍然真实生效，
      不是 no-op
    - 但 relative `v126`
      四条 fixed synthetic checks
      比 `v136` 全部更差
    - 因而直接 reject，
      不补 near-real
- 裁决：
  - `v136 = mechanism-positive but not promotable`
  - `v137 = reject`
  - 当前默认不再继续扫：
    - `overlap_cancel_absent_mix_weight`
    - `auxcancel absent-mix` 的同构 reweight
  - `v126`
    继续保持全局最佳 automatic continuation；
    如果后续还要继续 true-absent indirect path，
    默认应改成更局部的
    `monitor-only / local-window-only`
    或只打
    `0007 total leak`
    的 apply 机制

## `v136 = v126 + true-absent auxiliary-only overlap-cancel absent-mix 0.02`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v136_v126_trueabsent_auxcancel_absentmix002_maskheadtransfer_v1_ft1`
- 初始化：
  - `v126`
- teacher：
  - `v109`
- trainable：
  - `branch_decoder_mask_head`
  - `branch_overlap_cancel_head`
- 训练资产：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
- 关键机制：
  - `branch_overlap_cancel_apply_mode = auxiliary_only`
  - `branch_overlap_cancel_source_mode = residual`
  - `branch_overlap_cancel_gate_mode = complement`
  - `branch_overlap_cancel_ratio_mode = complex`
- 新增 loss：
  - `overlap_cancel_absent_mix_weight = 0.02`
  - 监督对象：
    - 在
      `target_absent_head / target_absent_tail`
      且
      `speech interference`
      命中的局部窗口里，
      把 auxiliary
      `overlap_cancel_prediction`
      拉向 `mixture`

## Training Signal

- 这轮不是 no-op：
  - `overlap_cancel`
    selector 命中：
    - train `95 / 203`
    - val `24 / 63`
  - `train_overlap_cancel_absent_mix_l1`
    末轮为：
    - `0.0382519`
  - `val_overlap_cancel_absent_mix_l1`
    末轮为：
    - `0.0522144`

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -0.1477 dB`
  - `improved = 1`
  - `regressed = 3`
  - `near_tie = 4`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.0324 dB`
  - `improved = 3`
  - `regressed = 3`
  - `near_tie = 5`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.0211 dB`
  - `improved = 4`
  - `regressed = 4`
  - `near_tie = 8`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = -0.1126 dB`
  - `improved = 1`
  - `regressed = 1`
  - `near_tie = 5`

结论：

- `v136`
  没有像此前的
  true-absent 直连分支那样
  直接击穿 fixed guardrails；
- 但它也没有相对 `v126`
  转正，
  只能带着 near-tie
  继续进 near-real
  看机制是否真有局部价值。

## Whole Near-Real relative `v126`

- 评估目录：
  - `reports/eval/ab_inference_residual_speech_leak_floor_v1_v126_vs_v136_all`
- 汇总：
  - `num_samples = 4`
  - `better_source_retention`
    - `v126: 1`
    - `tie: 2`
    - `n/a: 1`
  - `more_interference_leaky`
    - `v136: 3`
    - `tie: 1`
  - `better_retention_minus_leak`
    - `v126: 3`
    - `n/a: 1`
- label-level means：
  - `v126`
    - `target_capture_db = -13.5673`
    - `interference_capture_db = -41.2502`
    - `retention_minus_leak_db = 28.8388`
  - `v136`
    - `target_capture_db = -13.6853`
    - `interference_capture_db = -39.4449`
    - `retention_minus_leak_db = 26.4448`

按样本看：

- `near_real_0003`
  - `delta_interference_capture_db = +1.8214 dB`
  - `delta_retention_minus_leak_db = -2.6093 dB`
- `near_real_0006`
  - `delta_interference_capture_db = +1.0095 dB`
  - `delta_retention_minus_leak_db = -1.0239 dB`
- `near_real_0007`
  - `delta_target_capture_db = +0.4483 dB`
  - `delta_interference_capture_db = +3.9969 dB`
  - `delta_retention_minus_leak_db = -3.5486 dB`
- `near_real_0009`
  - `delta_interference_capture_db = +0.3934 dB`

结论：

- `v136`
  虽然在局部窗口里
  能做出正确方向的 absent-like 动作，
  但 whole utterance
  仍然会把 present 样本
  推向更 leak 的方向；
- 因而 still not promotable。

## Overlap-Local relative `v126`

- 汇总：
  - `more_speech_interference_leaky`
    - `v136: 2`
    - `v126: 2`
  - `more_total_interference_leaky`
    - `v136: 3`
    - `v126: 1`
  - `better_retention_minus_speech_leak`
    - `v126: 2`
    - `v136: 1`
    - `n/a: 1`
  - `better_retention_minus_total_leak`
    - `v126: 3`
    - `n/a: 1`
- 关键样本：
  - `near_real_0009`
    - `delta_speech_interference_capture_db = -13.5689 dB`
    - `delta_total_interference_capture_db = -13.5689 dB`
  - `near_real_0007`
    - `delta_target_capture_db = +0.3216 dB`
    - `delta_speech_interference_capture_db = -1.7290 dB`
    - `delta_total_interference_capture_db = +1.6095 dB`
    - `delta_retention_minus_speech_leak_db = +2.0506 dB`
    - `delta_retention_minus_total_leak_db = -1.2879 dB`

结论：

- `v136`
  是这条机制第一次给出的可信正证据：
  - `0009` absent local
    明显更干净
  - `0007 speech_only`
    local leak
    也确实在变好
- 但它同时明确暴露了新的失败模式：
  - `0007 speech_only`
    能改善，
    不代表
    `0007 total leak`
    也会改善
  - 更不代表
    whole near-real
    就能过关

## `v137 = v136 + overlap_cancel_absent_mix_weight 0.01`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v137_v136_trueabsent_auxcancel_absentmix001_maskheadtransfer_v1_ft1`
- 改动只一处：
  - `overlap_cancel_absent_mix_weight`
    从 `0.02`
    降到 `0.01`
- 其余 teacher / trainable / selector / model config
  与 `v136` 相同

## Training Signal

- 仍然不是 no-op：
  - `overlap_cancel`
    selector 命中不变：
    - train `95 / 203`
    - val `24 / 63`
  - `train_overlap_cancel_absent_mix_l1`
    末轮为：
    - `0.0382143`
  - `val_overlap_cancel_absent_mix_l1`
    末轮为：
    - `0.0521895`

## Fixed Checks relative `v126`

- `overlap_abstention_proxy_v4_audibility_v1`
  - `avg_sisdr_delta_db = -0.1718 dB`
  - `improved = 1`
  - `regressed = 3`
- `same_gender_present_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.0715 dB`
  - `improved = 4`
  - `regressed = 4`
- `hard_present_gate_keep_guardrail_v1`
  - `avg_sisdr_delta_db = -0.0347 dB`
  - `improved = 3`
  - `regressed = 8`
- `hard_present_artifact_proxy_v1`
  - `avg_sisdr_delta_db = -0.2080 dB`
  - `improved = 2`
  - `regressed = 2`

对照 `v136`：

- 四条 fixed checks
  全都更差；
- 说明这条
  `auxcancel absent-mix`
  路径的问题
  不是简单的
  `0.02` 偏大，
  而是当前
  broad absent-local mixture target
  本身还会拖坏
  whole tradeoff。

裁决：

- `v137 = reject`
- 不补 near-real
- 不再继续扫
  `overlap_cancel_absent_mix_weight`

## Final Decision

- 保留：
  - `v126`
    继续作为全局最佳 automatic continuation
  - `v129`
    继续作为 decoupled true-absent routing 支线最佳 continuation
  - `v136`
    保留为
    `auxiliary_only` true-absent indirect path
    的首个 credible evidence point
- 收口：
  - `v137`
  - `overlap_cancel_absent_mix_weight` sweep
- 下一步默认方向：
  - 不再做 broad absent-local mixture target
    的简单 reweight
  - 如果继续这条线，
    默认改做：
    - `monitor-only`
      或
      `local-window-only`
      的更局部 apply
    - 只打
      `near_real_0007 total leak`
      而不是只看
      `speech_only leak`
