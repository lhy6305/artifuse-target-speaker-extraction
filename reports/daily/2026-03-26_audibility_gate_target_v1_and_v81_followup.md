# 2026-03-26 audibility-conditioned gate target `v1` and `v81` follow-up

## 本轮目标

上一轮 `v80` 已经说明：

- 只把 keep 样本从 `same_gender_present_keep_guardrail_v1` 扩成 `keep_union_v2`
- 并不能阻止 gate 继续滑向 over-silence。

所以本轮不再继续做同结构 sweep，而是直接把 gate supervision 从二元 `0 / 1` 改成连续 target：

- 弱目标样本不再一律推到 `0`
- keep 样本也不再只用硬 `1`
- 改成按 audibility 指标生成连续 gate target

## 代码改动

修改：

- `src/tse_prefix/pipeline/baseline_train.py`
- `scripts/train/train_stft_mask_baseline.py`

新增机制：

- `gate_target_l1`
- `--loss-gate-target-weight`
- `--loss-gate-target-mode audibility`
- audibility target 由三类 metadata 生成：
  - `target_energy_ratio`
  - `target_transient_presence_share_mean`
  - `target_transient_presence_minus_mid_db_mean`

当前 `v1` 公式是 sigmoid 组合：

- energy
  - center `0.13`
  - scale `0.035`
  - weight `0.75`
- transient share
  - center `0.01`
  - scale `0.006`
  - weight `0.15`
- transient dB
  - center `-13`
  - scale `2.5`
  - weight `0.10`

典型 target 值 smoke：

- 弱样本约 `0.08`
- 中等样本约 `0.58`
- 强样本约 `0.96`

## 新训练

### `v81 = v79 + audibility gate target v1`

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v81_v79_audibility_gate_target_v1_ft1`

训练口径：

- init：`v79`
- 只训：
  - `branch_decoder_gate_head`
- train / val：
  - `abstention_gate_bundle_v2`
- reconstruction / branch protect 仍保持：
  - `sample_ids_gate_keep_union_v2_train`
- 关闭旧二元 gate loss：
  - `gate_abstain_weight = 0`
  - `gate_keep_weight = 0`
- 新开连续 gate loss：
  - `gate_target_weight = 0.10`

训练期信号：

- train `gate_target_l1`
  - epoch1 `0.294`
  - epoch4 `0.259`
- val `gate_target_l1`
  - `0.255 -> 0.242`

说明：

- 新连续 supervision 不是 no-op；
- gate 明确学到了更平滑的目标。

## 结果

### A. abstention proxy：`v81` 把 `v79` 拉回更 balanced 区间

- `reports/eval/compare_v79_vs_v81_on_overlap_abstention_proxy_v4_audibility_v1/summary.json`
  - `avg_sisdr_delta_db = +1.9569`
  - `7` improve / `1` regress

解释：

- 和 `v80` 不同，`v81` 没有继续在 abstention proxy 上整体崩掉；
- 它是第一条同时保住 abstention synthetic 方向的 audibility-conditioned gate pilot。

### B. same-gender keep guardrail：明显回拉，但仍未完全清零

- `reports/eval/rank_same_gender_present_keep_guardrail_v1_v54_v78_v79_v80_v81/summary.json`
  - `present_guardrail_violation_count`
    - `v79 = 11`
    - `v80 = 11`
    - `v81 = 4`
  - `present_mean_target_capture_db`
    - `v79 = -23.696`
    - `v80 = -25.266`
    - `v81 = -20.500`

解释：

- `v81` 没有回到 `v54 / v78` 的完全安全；
- 但相对 `v79 / v80` 已经是大幅修复。

### C. hard-present keep guardrail：同样明显回拉

- `reports/eval/rank_hard_present_gate_keep_guardrail_v1_v54_v78_v79_v80_v81/summary.json`
  - `present_guardrail_violation_count`
    - `v79 = 16`
    - `v80 = 16`
    - `v81 = 12`
  - `present_mean_target_capture_db`
    - `v79 = -25.727`
    - `v80 = -27.820`
    - `v81 = -20.376`

解释：

- `v81` 仍然没达到 fully safe；
- 但第一次证明：
  - 问题并不是 gate 机制天然会压坏 hard-present；
  - 连续 target 语义确实能把 hard-present regression 往回拉。

### D. near-real residual leak floor：第一次重新回到 `0` violation

- `reports/eval/rank_residual_speech_leak_floor_v1_v54_v78_v79_v80_v81/summary.json`
  - `present_guardrail_violation_count`
    - `v54 = 0`
    - `v78 = 0`
    - `v79 = 1`
    - `v80 = 1`
    - `v81 = 0`
  - `absent_mean_interference_capture_db`
    - `v54 = -33.385`
    - `v79 = -36.617`
    - `v81 = -34.050`

逐样本：

- `near_real_0003`
  - `target_capture_db`
    - `v54 = -11.464`
    - `v79 = -11.512`
    - `v81 = -11.474`
  - 基本回到安全区
- `near_real_0006`
  - `interference_capture_db`
    - `v54 = -30.495`
    - `v79 = -36.393`
    - `v81 = -31.249`
  - 仍比 `v54` 更静，但不再像 `v79 / v80` 那么激进
- `near_real_0007`
  - `target_capture_db`
    - `v79 = -22.369`
    - `v80 = -26.456`
    - `v81 = -17.715`
  - 已明显拉回
- `near_real_0009`
  - `interference_capture_db`
    - `v54 = -33.385`
    - `v79 = -36.617`
    - `v81 = -34.050`
  - 仍略优于 `v54`

解释：

- `v81` 是第一条真正把：
  - `0007` hard-present regression
  - 和 `0006 / 0009` 的 silence-over-leak 收益
  重新拉回可接受 tradeoff 的 gate pilot。

## 本轮裁决

1. `audibility-conditioned gate target v1` 是有效方向。
   - 它不是纯理论修辞，而是已经把 `v79 / v80` 的主要失败模式往回拉。
2. `v81` 是当前 gate 机制线里最有希望的 checkpoint。
   - 它还不能直接放行为默认线；
   - 但已经值得进入 focused 听审关。
3. 当前还不能宣称问题完全解决。
   - synthetic keep guardrail 仍有残余 violation：
     - same-gender `4`
     - hard-present `12`

## 下一步

当前默认下一步不再是继续大 sweep，而是：

1. 先导一个小型 focused 听审关：
   - 主比较 `v54 vs v81`
   - 必听 `near_real_0003 / 0006 / 0007 / 0009`
2. 若听感确认 `v81`：
   - `0006 / 0009` 确实更干净
   - `0007` 不再出现 `v79 / v80` 那种明显误伤
   则把 `v81` 升格为新的 gate 研究基座
3. 只有在听审确认之后，才值得做：
   - `audibility gate target v2`
   - 围绕 target curve 形状做更小的 follow-up
