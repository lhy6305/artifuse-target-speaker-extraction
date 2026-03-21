## 4. 当前分支状态

### 分支 `B1`: `v5 cleancarve` 内继续细粒度 carve-out

- 状态：
  - `closed / failed`
- 当前判断：
  - `v40` 已证明：
    单纯去掉 exact overlap
    还不足以把 absent-side real gate 拉回
- 已知事实：
  - `v40` relative to `v19`：
    - exact `target_full = -0.467909 dB`
    - `speech_leak_like (0004) = -0.086817 dB`
    - `guodegang_anchor_120s = -0.099242 dB`
    - `guodegang_absent_480s = -0.057473 dB`
    - `proxy_v6 = -0.424082 dB`

### 分支 `B2`: 更贴近 near-real `guodegang_absent` 的保护代理

- 状态：
  - `closed / failed`
- 当前判断：
  - `v41` 已证明当前
    `proxy_v6 currentsignal cleanonly`
    还不是可保留的 near-real absent 保护代理
- 已知事实：
  - `v41` relative to `v19`：
    - exact `target_full = -0.325134 dB`
    - `speech_leak_like (0004) = -0.062535 dB`
    - `guodegang_anchor_120s = -0.258474 dB`
    - `guodegang_absent_480s = -0.112892 dB`
    - `proxy_v6 = -0.627418 dB`
  - relative to `v32` 的 gate：
    - 额外 failed
      `speech_probe_overall_floor`

### 分支 `B3`: 重新定义 absent-side protection proxy / real-floor guardrail

- 状态：
  - `active / proxy found`
- 当前判断：
  - `B1 / B2` 当前这两条收紧版都已失败；
  - 但 `v42` 已说明：
    - 新的 `proxy_v7`
      不是旧 rows 重路由；
    - val 侧 `0` exact overlap；
    - 且能把
      `guodegang_anchor / absent`
      两条 real floor
      同时拉回正向
- 已知事实：
  - `v7` 物化后：
    - train `33`
    - val `8`
  - 与 `v32` base 的关系：
    - 新增 coverage：
      - train `32`
      - val `8`
  - `v42` relative to `v19`：
    - default `+0.077955 dB`
    - exact `target_full = -0.664459 dB`
    - `speech_leak_like (0004) = -0.113430 dB`
    - `guodegang_anchor_120s = +0.126568 dB`
    - `guodegang_absent_480s = +0.031863 dB`
    - `proxy_v7 = +0.444459 dB`
  - `v43` relative to `v19`：
    - default `+0.077610 dB`
    - exact `target_full = -0.663965 dB`
    - `speech_leak_like (0004) = -0.113233 dB`
    - `guodegang_anchor_120s = +0.125676 dB`
    - `guodegang_absent_480s = +0.031660 dB`
    - `proxy_v7 = +0.440865 dB`
  - `v44` relative to `v19`：
    - default `+0.072833 dB`
    - exact `target_full = -0.647221 dB`
    - `speech_leak_like (0004) = -0.110539 dB`
    - `guodegang_anchor_120s = +0.113703 dB`
    - `guodegang_absent_480s = +0.029381 dB`
    - `proxy_v7 = +0.359405 dB`
  - `v45` relative to `v19`：
    - default `+0.075720 dB`
    - exact `target_full = -0.653286 dB`
    - `speech_leak_like (0004) = -0.111924 dB`
    - `guodegang_anchor_120s = +0.119305 dB`
    - `guodegang_absent_480s = +0.029907 dB`
    - `proxy_v7 = +0.396169 dB`
  - `v46` relative to `v19`：
    - default `+0.077715 dB`
    - exact proxy overall `-0.315450 dB`
    - `speech_leak_like (0004) = -0.113260 dB`
    - `guodegang_anchor_120s = +0.126034 dB`
    - `guodegang_absent_480s = +0.031888 dB`
    - `proxy_v7 = +0.441273 dB`
  - `v47` relative to `v19`：
    - default `+0.018882 dB`
    - exact `target_full = -0.290016 dB`
    - `speech_leak_like (0004) = -0.042893 dB`
    - `guodegang_anchor_120s = -0.059132 dB`
    - `guodegang_absent_480s = -0.007238 dB`
    - `proxy_v7 = -0.858876 dB`
  - `v48` relative to `v19`：
    - default `+0.061926 dB`
    - exact `target_full = -0.347332 dB`
    - `speech_leak_like (0004) = -0.089823 dB`
    - `guodegang_anchor_120s = -0.014192 dB`
    - `guodegang_absent_480s = -0.017526 dB`
    - `proxy_v7 = -0.274633 dB`
  - `v49` relative to `v19`：
    - default `+0.004926 dB`
    - exact `target_full = -0.406366 dB`
    - `speech_leak_like (0004) = -0.048850 dB`
    - `guodegang_anchor_120s = -0.056997 dB`
    - `guodegang_absent_480s = -0.015182 dB`
    - `proxy_v7 = -1.542894 dB`
  - `v50` relative to `v19`：
    - default `+0.013945 dB`
    - exact `target_full = -0.323341 dB`
    - `speech_leak_like (0004) = -0.042961 dB`
    - `guodegang_anchor_120s = -0.064364 dB`
    - `guodegang_absent_480s = -0.013611 dB`
    - `proxy_v7 = -1.082981 dB`
  - `v51` relative to `v19`：
    - default `+0.015467 dB`
    - exact `target_full = -0.317694 dB`
    - `speech_leak_like (0004) = -0.042935 dB`
    - `guodegang_anchor_120s = -0.064897 dB`
    - `guodegang_absent_480s = -0.013696 dB`
    - `proxy_v7 = -1.016036 dB`
  - `v52` relative to `v19`：
    - default `+0.017187 dB`
    - exact `target_full = -0.310738 dB`
    - `speech_leak_like (0004) = -0.041941 dB`
    - `guodegang_anchor_120s = -0.065335 dB`
    - `guodegang_absent_480s = -0.013233 dB`
    - `proxy_v7 = -0.876078 dB`
- 当前缺口：
  - 现在不再缺 absent proxy 本体；
  - 当前真正缺的是：
    - 如何在保留 `proxy_v7`
      的同时，
      不再同步拖坏
      `exact target_full`
      与 `speech_leak_like (0004)`
  - 同时已知：
    - 微幅 waveform weight 缩放
      基本不改变这条结论
    - 单纯切成 `stft_only`
      虽然比 wave-only 更有信号，
      但仍不足以越过 friend-side 两条 clear fail
    - `full / nonfull` split routing
      比单一路由更像正确方向，
      但当前仍未把两条 clear fail
      拉回 near-tie
    - 即便把 `full`
      完全退出 absent reconstruction，
      friend-side 两条仍几乎不回收；
      问题更像共享参数层面的全局耦合
    - 纯 ref-conditioning freeze
      虽能把 friend-side
      拉回 `near_tie / pass`，
      但会让 `proxy_v7`
      与 real `guodegang`
      一起塌掉
    - 再放开 shared `mask_head`
      虽可恢复一部分 default / proxy，
      但还没等 `proxy_v7`
      回到正向，
      friend-side 两条就先重新坏掉了
    - simple output residual adapter
      已证明：
      - 大残差会把 absent proxy 明显推反
      - 小残差只能把 friend-side
        拉回 near-tie，
        但仍带不回 absent proxy 本体
    - 继续给 adapter branch
      增加：
      - reference conditioning
      - 或自己的 temporal model
      也仍然只能把结果压到 near-tie，
      拉不回 absent proxy 本体
    - `dual-head / branch-local decoder`
      的工程底座现已补齐：
      - `enable_branch_decoder_head`
      - `reset_branch_decoder_from_base()`
      - `--model-enable-branch-decoder-head`
      - `v32 -> tmp/smoke_branch_decoder_v53`
        已跑通 1-step smoke
    - 因而当前默认下一条
      已不再是“继续补 plumbing”，
      而是：
      - 直接跑第一条正式 dual-head follow-up
    - `v53`
      已证明：
      - dual-head 本身不是没方向；
      - `proxy_v7 / guodegang`
        可被明显拉强；
      - 但若 friend-side extra guardrail
        没真正回流到 branch decoder，
        它就会变成单边 absent 训练
    - `v54`
      已证明：
      - 把现有 friend-side
        `interference_extra residual_projection_ratio`
        真接到 branch decoder，
        也不会把它拉向 keep；
      - 反而会把
        `proxy_v7 / guodegang`
        与 friend-side clear fail
        一起放大
    - `v55`
      已证明：
      - exact-family `SI-SDR guard`
        在 dual-head 上
        仍是 overfit 型 protect；
      - 不能把
        exact / `proxy_v7`
        变强
        直接等价成：
        friend-side protect 已成立
    - `v56`
      记为：
      - invalid plumbing round；
      - 不纳入模型结论
    - `v57`
      已证明：
      - `base-align`
        是有信号的 protect primitive；
      - 它能把 dual-head
        拉到非常接近 gate；
      - 但强版本会直接压塌
        `proxy_v7`
    - `v58`
      已证明：
      - 把 `base-align`
        放轻后，
        `proxy_v7 / guodegang`
        能回来；
      - 但 `speech_leak_like (0004)`
        又重新 clear fail
      - 因而当前缺的
        不是同一条 `base-align` weight
        的再细扫，
        而是更直接面向
        `speech_leak_like (0004)`
        的 protect objective
    - `v59 / v60`
      已证明：
      - `base-delta-interference projection`
        不是没接上；
      - 但它在当前 exact ids 上
        的实际 loss 量级几乎为 `0`
      - 所以会继续允许：
        - `proxy_v7 / guodegang`
          很强
        - friend-side
          `target_full / 0004`
          继续 clear fail
      - 因而这条 primitive
        当前也不值得继续扫权重
    - `v61`
      已证明：
      - 把 protect selector
        收窄到 `target_full` 子集
        是有效修正；
      - 这不是 trivial 摆动，
        而是把：
        - exact `target_full`
        - `0004`
        - `guodegang`
        三者同时拉回到更平衡的区间
    - `v62`
      已证明：
      - 在这个更细 selector 上，
        继续把同一条 `base-align`
        weight 往上推，
        不是 closing gap 的正确方向；
      - 当前缺的已不是：
        - 同一 primitive 的更强档
      - 而是：
        - 面向 `0004-like speech leak`
          的第二条显式 protect 信号
    - 当前已补好第二条 protect selector
      的工程入口：
      - `branch_protect`
      - `--loss-branch-protect-guard-sisdr-weight`
      - `--loss-branch-protect-*`
      - `tmp/smoke_branch_protect_guard_sisdr`
        已完成 1-step smoke
      - 已确认：
        - selector 命中
        - train / eval summary
          新指标落盘
      - 因而下一条已不再缺：
        - 双 protect selector
          的 plumbing
    - `v63`
      已实际执行并失败：
      - `target_full`
        确实继续收回；
      - 但 `0004-like`
        没有被真正拉正；
      - `guodegang_anchor / absent`
        反而一起转负；
      - 额外 metadata 复盘已确认：
        - `exact_nontargetfull`
          并不是
          `0004-like`
          的保守近似，
          而几乎全是
          `target_absent_head / tail`
          子集
      - 因而：
        - `exact_all - exact_targetfull_all`
          不再保留为
          第二 protect selector
          的默认定义
    - `v64`
      已实际执行并回收：
      - 第二 selector
        改成直接的
        `v23 friend speech_leak exact minus target_full`
      - 但仍直接跑在默认
        `v42` split 上，
        `branch_protect`
        实际命中只有：
        - train `1 / 129`
        - val `0 / 37`
      - gate 结果为：
        - 只剩
          `speech_leak_like_gain_floor`
          一个 `near_tie`
      - 因而：
        - 这条 selector
          语义上
          比 `exact_nontargetfull`
          更像对题；
        - 但当前 hit 太稀，
          不能直接记成 keep
    - `v65`
      已实际执行并回收：
      - 把上述 `v23minus`
        rows 真正 union
        进 train / val manifest
      - `branch_protect`
        命中补到：
        - train `7 / 135`
        - val `2 / 39`
      - `target_full`
        进一步转正到：
        - `+0.031807 dB`
      - 但：
        - `speech_leak_like (0004)`
          仍未转正；
        - `guodegang_anchor / absent`
          明显转负
      - 因而：
        - 单纯 union
          这批 rows
          不是 keep 方向；
        - 当前不应再直接沿
          `v65`
          放大训练预算

### `v64`

- 定义：
  - `v63`
    之后的第一条恢复验证轮次
  - `target_full`-only `base-align`
    保持不变
  - 第二 protect selector
    改为：
    - `sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_all.txt`
- 结论：
  - `NOT keep`
  - `closed_but_evidence_keep`
- 主要原因：
  - 相对 `v32` gate
    只剩：
    - `speech_leak_like_gain_floor`
      一个 `near_tie`
  - `guodegang_anchor / absent`
    继续保持正向
  - 但 `branch_protect`
    在当前 split
    实际命中过稀，
    还不足以形成可保留候选
- 解释：
  - `v64`
    不应记成：
    - “又一次普通 fail”
  - 它真正写死的是：
    - 直接对准
      `exact minus target_full`
      的 selector
      语义上更对；
    - 但若这批 rows
      没有真实并入
      当前 manifest，
      证据强度仍然不够
- 入口：
  - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`

### `v65`

- 定义：
  - `v64`
    的 union-manifest follow-up
  - 将：
    - `train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
    - `val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
    作为新的 train / val split
- 结论：
  - `FAIL as keep candidate`
- 主要原因：
  - `target_full`
    虽明显更强，
    甚至转正；
  - 但 `speech_leak_like (0004)`
    仍未过线；
  - 同时：
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`
      都变成 `clear_fail`
- 解释：
  - `v65`
    证明当前问题
    不是简单的
    “让第二 selector
    多命中一点”
  - 一旦真的补足 coverage，
    这条线仍会把
    `guodegang`
    保护项重新打坏
- 入口：
  - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`
