# 2026-03-27 phone artifact gate v1 follow-up

## 背景

- `v103` 与 `v107` 已分别在 blind `v81` A/B 听审里败给 `v81`；
- 共同失败模式不是 residual speech leak，而是更重的电话音式 artifact；
- 当前需要的不是继续同结构 sweep，而是先把这类 artifact 物化成可复用的自动 gate。

## 本轮目标

- 验证现有 `bandwidth_guardrail_v1` 是否足以解释最近几轮电话音失败；
- 如果纯 bandwidth 不够，就补一个能在已知失败 pack 上直接抓住 `v103 / v107` 的 phone-artifact gate。

## 本轮资产

- near-real manifest：
  - `data/references/real_eval_manifest_bandwidth_guardrail_v1.jsonl`
- 诊断脚本：
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
  - `scripts/eval/analyze_listening_pack_transients.py`
  - `scripts/eval/gate_near_real_phone_artifact.py`
- 回放 pack：
  - `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_v81_vs_v103`
  - `reports/eval/ab_listening_pack_real_eval_bandwidth_guardrail_v1_v81_vs_v107`

## 结果

### 1. 纯 bandwidth narrowing 不足以解释当前电话音失败

- `v81 vs v103`
  - `bandwidth_analysis/summary.json`
  - `narrower_candidate_counts = tie: 4`
- `v81 vs v107`
  - 对应 pack 的 bandwidth 结论同样没有 decisive narrowing

说明：

- 现有基于 `rolloff / upper_vs_mid / frame_upper_p90` 的纯 bandwidth 指标，
  没有把这两条已知主观失败候选从 `v81` 里分出来。

### 2. transient-presence loss 能稳定抓到已知失败候选

- `v81 vs v103`
  - `more_transient_lossy_candidate_counts = tie: 1, file_b: 3`
  - 被抓到的样本：
    - `near_real_0002`
    - `near_real_0006`
    - `near_real_0009`
- `v81 vs v107`
  - 结论同型：
    - `tie: 1, file_b: 3`
  - 同样是：
    - `near_real_0002`
    - `near_real_0006`
    - `near_real_0009`

说明：

- 当前这批“电话音”更接近：
  - 高频瞬态存在感丢失
  - 而不是单纯的频宽收窄。

### 3. 已物化 `phone_artifact_gate_v1`

新增脚本：

- `scripts/eval/gate_near_real_phone_artifact.py`

规则语义：

- `raw_target_only`
  - 不允许比 baseline 更窄；
  - 不允许比 baseline 更 transient-lossy。
- `target_present__speech`
  - 不允许比 baseline 更 transient-lossy。
- `target_absent__speech`
  - 不允许比 baseline 更窄；
  - 不允许比 baseline 更 transient-lossy。

验证结果：

- `v81 vs v103`
  - `phone_artifact_gate_summary.json`
  - `overall_pass = false`
  - `failed_buckets = [raw_target_only, target_present__speech, target_absent__speech]`
- `v81 vs v107`
  - `phone_artifact_gate_summary.json`
  - `overall_pass = false`
  - `failed_buckets = [raw_target_only, target_present__speech, target_absent__speech]`

共同失败模式：

- `raw_target_only`
  - 失败点在 `near_real_0002`
- `target_present__speech`
  - 失败点在 `near_real_0006`
- `target_absent__speech`
  - 失败点在 `near_real_0009`
- 两组 pack 都不是败在“更窄”，而是败在“更 transient-lossy”

## 结论

- 当前 frontier 上的电话音式 artifact，不能再只用纯 bandwidth guardrail 代理；
- 更可靠的自动信号是：
  - `bandwidth + transient-loss` 组合 gate；
- `phone_artifact_gate_v1` 已经能在两组已知主观失败 pack 上稳定抓住：
  - `v103`
  - `v107`

## 对主线的影响

- `v107` family 继续收口，不开 `v107+`；
- 后续任何沿 `local speech-leak proxy` 推进的新 pilot，
  在导听审前都应固定补过：
  - `real_eval_manifest_bandwidth_guardrail_v1`
  - `scripts/eval/gate_near_real_phone_artifact.py`
- 下一轮真正要补的，不再是“是否显式压 speech leak”，而是：
  - 显式 speech-leak suppression
  - 局部 preservation backstop
  - phone-artifact backstop
