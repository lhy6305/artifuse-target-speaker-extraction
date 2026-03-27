# 2026-03-27 `v81 vs v109` focused blind listening review

blind pack：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v109_blind`

decoded summary：

- `reports/eval/ab_listening_pack_residual_speech_leak_floor_v1_v81_vs_v109_blind/listening_review_decoded_summary.json`

## 解盲结果

- `v81 = 1`
- `v109 = 0`
- `tie = 3`

分样本：

- `near_real_0003`
  - `tie`
- `near_real_0006`
  - `tie`
- `near_real_0007`
  - `v81`
  - 决策标签：
    - `less_artifact`
- `near_real_0009`
  - `tie`

## 听感结论

1. `v81` 与 `v109` 已经非常接近；
2. `v109` 没有像 `v103 / v107` 那样明显一边倒输在电话音伪影；
3. 但核心痛点 `near_real_0007` 仍未转正：
   - 唯一非 tie 样本仍判给 `v81`
   - 原因仍是 `v109` artifact 更重
4. 因此这轮不能把 `v109` 升格成新的研究前沿。

## 裁决

- `v109` 不升格
- `v81` 继续作为当前研究基座
- `v109` 这条 `0007-like backstop` 小步 sweep 先收口

## 启示

- `v109` 已证明：
  - 把 backstop 缩到 `0007-like` 子域，
  - 能避免 `v108` 式全局回缩，
  - 也能通过 `phone_artifact_gate_v1`
- 但这还不足以解决：
  - `0007` 的最终主观 artifact / retention 拉扯

当前更准确的判断应是：

- 这条 family 已经从“明显失败”走到“和 `v81` 很接近”；
- 但离“主观上解决核心痛点”还差最后一步，
  而这一步没有通过继续同构小步 sweep 自动出现。
