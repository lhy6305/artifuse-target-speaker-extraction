# 2026-03-28 refine siblings on `v142`: `v143 / v144 / v145 / v146` follow-up

## Summary

- 上一轮已经把
  `v142`
  定位成：
  - `v126 + head-only hardlocaltotal subtract blend05 v1`
  - 当前
    `head-only bounded direct-apply`
    子线最佳 continuation
- 这轮的目标很明确：
  - 不碰 `v142`
    已经建立起来的
    `overlap_cancel` present-total path
  - 改为在 `v142`
    之上挂新的
    `overlap_refine` sibling，
    独立去打：
    - `0007 speech_only local leak`
    - 更广义的 local speech-leak proxy
- 一共做了四个 sibling：
  - `v143`
    - `branch_overlap_refine_present_head`
    - `0007-like` 稀疏 selector
    - teacher = `v142`
  - `v144`
    - `branch_overlap_refine_present_head`
    - broader `local_speech_leak_proxy_v1`
      selector
    - teacher = `v142`
  - `v145`
    - `branch_overlap_refine_head`
    - broader `local_speech_leak_proxy_v1`
      selector
    - teacher = `v142`
  - `v146`
    - 目标上想做
      `v145` 的 “no-teacher”
      版本
    - 但训练入口实际触发了
      `teacher_checkpoint`
      metadata fallback，
      最终继承到的是
      `v126`
      作为 teacher
- 裁决非常收敛：
  - `v143 = practical no-op reject`
  - `v144 = broader-selector still no-op reject`
  - `v145 = mechanism signal exists, but inference still near-no-op reject`
  - `v146 = exact no-op reject`
- 新边界因此很明确：
  - 在 `v142`
    已有 present-total direct path
    的前提下，
    继续叠
    `overlap_refine_present_head`
    或
    `overlap_refine_head`
    的 sibling，
    当前都推不出
    可观测输出变化
  - 如果后续还要继续这条方向，
    默认不该再扫：
    - `speech selector` 宽窄
    - `refine_present` vs `refine_base`
    - `teacher=self` 同构 rerun
  - 而应改成：
    - 新的输出 apply path
    - 或显式支持
      `disable teacher metadata fallback`
      后再验证真正的 no-teacher route

## `v143 = v142 + refine-present speech-only `0007-like` v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v143_v142_refinepresent_speechonly_0007like_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `v142`
- 仅训练：
  - `branch_overlap_refine_present_head`
- manifest：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_0007_like_plus_true_absent_anchor_bundle_v2.jsonl`
- selector：
  - speech-only：
    `sample_ids_local_speech_leak_0007_like_proxy_v1_all`
  - protect：
    `sample_ids_hard_present_artifact_local_proxy_v1_all`

## Training Signal

- selector 命中极稀：
  - speech-only
    - train `3 / 203`
    - val `3 / 63`
  - teacher protect
    - train `3 / 203`
    - val `3 / 63`
- 末轮：
  - `train_branch_protect_teacher_overlap_l1 = 0.0000047`
  - `val_branch_protect_teacher_overlap_l1 = 0.0000042`
  - `train_overlap_interference_extra_projection_ratio = 0.0000213`
  - `val_overlap_interference_extra_projection_ratio = 0.0000150`

## Fixed Checks relative `v142`

- abstention `-0.0030 dB`
- same-gender keep `+0.0080 dB`
- hard-present keep `+0.0086 dB`
- artifact proxy `+0.0006 dB`
- 四条 fixed checks
  全是 near-tie：
  - `improved = 0`
  - `regressed = 0`

结论：

- `v143`
  是稀疏 selector
  下的 practical no-op；
- 原因不是 guardrail 打坏，
  而是：
  - selector 太稀
  - self-teacher 也太紧

## `v144 = v142 + refine-present broader speech-local-proxy v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v144_v142_refinepresent_speechlocalproxy_hardlocalbundle_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `v142`
- 仅训练：
  - `branch_overlap_refine_present_head`
- manifest：
  - `data/synthetic/train_manifest_local_speech_leak_artifact_paired_hardlocal_bundle_v1.jsonl`
  - `data/synthetic/val_manifest_local_speech_leak_artifact_paired_hardlocal_bundle_v1.jsonl`
- selector：
  - broader speech-local proxy：
    `sample_ids_local_speech_leak_proxy_v1_all`
  - teacher protect：
    `sample_ids_hard_present_artifact_local_proxy_v1_all`

## Training Signal

- selector 命中不再稀疏：
  - speech-local
    - train `33 / 99`
    - val `7 / 37`
  - teacher protect
    - train `3 / 99`
    - val `3 / 37`
- 末轮：
  - `train_branch_protect_teacher_overlap_l1 = 0.0000028`
  - `val_branch_protect_teacher_overlap_l1 = 0.0000050`
  - `train_overlap_interference_extra_projection_ratio = 0.0005707`
  - `val_overlap_interference_extra_projection_ratio = 0.0000282`

## Fixed Checks relative `v142`

- abstention `+0.0067 dB`
- same-gender keep `+0.0025 dB`
- hard-present keep `+0.0019 dB`
- artifact proxy `+0.0054 dB`
- 四条 fixed checks
  全是 near-tie：
  - `improved = 0`
  - `regressed = 0`

## Targeted Local Proxy Check

- `val_manifest_local_speech_leak_proxy_v1`
  relative `v142`：
  - `avg_sisdr_delta_db = -0.0039 dB`
  - `improved = 0`
  - `regressed = 0`

结论：

- 把 selector
  从 `3 / 203`
  扩到 `33 / 99`
  并没有把
  `refine_present_head`
  从 no-op
  变成真实输出变化；
- `v144`
  直接 reject

## `v145 = v142 + refine-base broader speech-local-proxy v1`

## Setup

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v145_v142_refinebase_speechlocalproxy_hardlocalbundle_v1_ft1`
- 初始化：
  - `v142`
- teacher：
  - `v142`
- 仅训练：
  - `branch_overlap_refine_head`
- manifest / selector：
  - 与 `v144`
    相同

## Training Signal

- selector 命中：
  - speech-local
    - train `33 / 99`
    - val `7 / 37`
  - teacher protect
    - train `3 / 99`
    - val `3 / 37`
- 与 `v144`
  不同的是：
  - 这轮真正非零的是
    `overlap_interference_projection_ratio`
    而不是
    `overlap_interference_extra_projection_ratio`
- 末轮：
  - `train_branch_protect_teacher_overlap_l1 = 0.0000066`
  - `val_branch_protect_teacher_overlap_l1 = 0.0000310`
  - `train_overlap_interference_projection_ratio = 0.0022900`
  - `val_overlap_interference_projection_ratio = 0.0006825`

## Fixed Checks relative `v142`

- abstention `+0.0128 dB`
- same-gender keep `+0.0075 dB`
- hard-present keep `+0.0081 dB`
- artifact proxy `+0.0047 dB`
- 四条 fixed checks
  仍全部 near-tie：
  - `improved = 0`
  - `regressed = 0`

## Targeted Local Proxy Check

- `val_manifest_local_speech_leak_proxy_v1`
  relative `v142`：
  - `avg_sisdr_delta_db = -0.0064 dB`
  - `improved = 0`
  - `regressed = 0`

结论：

- `v145`
  相比 `v144`
  至少证明了一件事：
  - `refine_base`
    比 `refine_present`
    更能真实吃到
    speech-local target signal
- 但从 inference 结果看，
  它仍只是
  mechanism-on / output-off
  的 near-no-op；
- 因而不补 near-real

## `v146 = v142 + refine-base broader speech-local-proxy fallback-teacher v1`

## Setup Clarification

- checkpoint：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v146_v142_refinebase_speechlocalproxy_hardlocalbundle_noteacher_v1_ft1`
- 这轮原本的意图是：
  - 复刻 `v145`
  - 但不再显式传
    `teacher_checkpoint`
- 需要明确的是：
  - 训练入口当前会对
    `teacher_checkpoint`
    做 metadata fallback
  - 因此这轮并不是真正的
    no-teacher
  - 实际解析到的是：
    - `teacher_checkpoint = v126`
- 结构与 selector：
  - 其余均与 `v145`
    相同

## Training Signal

- speech-local selector
  仍命中：
  - train `33 / 99`
  - val `7 / 37`
- 末轮：
  - `train_overlap_interference_projection_ratio = 0.0018121`
  - `val_overlap_interference_projection_ratio = 0.0006825`
- 由于没有显式
  `branch_protect_teacher`
  selector，
  这一轮的
  `branch_protect_teacher`
  sample weights
  实际上是 inactive

## Fixed Checks relative `v142`

- abstention `+0.0000 dB`
- same-gender keep `+0.0000 dB`
- hard-present keep `+0.0000 dB`
- artifact proxy `+0.0000 dB`
- `val_manifest_local_speech_leak_proxy_v1`
  也精确 `+0.0000 dB`

结论：

- `v146`
  直接补出一个更硬的边界：
  - 即便把
    `v145`
    里的显式 self-teacher
    去掉，
    当前这条 route
    仍然会收敛成 exact no-op
- 但同时也暴露了一个重要实现边界：
  - “不传 `--teacher-checkpoint`”
    不等于
    “真的没有 teacher”
  - 当前会自动继承
    init checkpoint metadata
    里的 teacher path

## Final Verdict

- `v143 / v144 / v145 / v146`
  共同给出的结论是：
  - 在 `v142`
    已经建立 present-total direct path
    的前提下，
    继续叠
    `overlap_refine_present_head`
    或
    `overlap_refine_head`
    sibling，
    当前都推不出
    有意义的输出变化
- 这轮默认不再继续扫：
  - `refine_present` vs `refine_base`
  - `0007-like` vs broader speech-local selector
  - `teacher=self`
    同构 rerun
- 如果后续还要继续：
  - 要么新增真正不同的 output apply path
  - 要么先给训练入口补一个
    明确的
    `disable teacher metadata fallback`
    开关，
    再验证真正的 no-teacher branch
