# 踩坑记录 历史归档 111-118

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `111-118`

## 2026-03-16

### 111. 单纯在 pure ref-conditioning freeze 上额外放开一个 shared `mask_head`，虽然会把 default 与 absent proxy 拉回一点，但仍不足以同时保住 friend-side 两条与 absent proxy 本体；这说明真正需要的是更强的 branch-local output isolation，而不是继续试 shared head 的解冻组合

现象：

- 本轮继续跑了：
  - `v48 = ref_encoder + condition_proj + mask_head`
- `v48`
  trainable parameter count：
  - `329,345 / 2,367,617`
  - `13.91%`
- relative to `v47`：
  - default：
    - `+0.018882 -> +0.061926 dB`
  - `proxy_v7`：
    - `-0.858876 -> -0.274633 dB`
- 但 relative to `v32` gate：
  - `exact_target_full_gain_floor = clear_fail`
  - `speech_leak_like_gain_floor = clear_fail`
  - `guodegang_absent_floor = near_tie`

处理：

- 已把 `v48`
  的训练、compare、gate 与裁决集中落盘到：
  - `reports/daily/2026-03-20_v47_v48_prefix_freeze_decoupling_followup.md`

结果：

- 现在可以明确写死：
  - `mask_head`
    这一级 shared output plasticity
    是有信号的；
  - 但它还不够独立，
    会在 `proxy_v7`
    还没回到正向之前，
    先把 friend-side 两条重新拖坏

影响：

1. 下一条若继续自动推进，
   默认不再扫：
   - `ref-conditioning + shared mask_head`
   这类 prefix-freeze 组合
2. 当前更合理的默认延伸应升级成：
   - absent-only residual adapter
   - 或独立 output branch / dual-head
3. 以后回看 `v47 / v48`
   时，要把它们记成：
   - “确定了需要 branch-local output plasticity”
   而不是：
   - “prefix freeze 方向已经足够接近 keep”。

### 112. 如果给 absent-side 只加一条 zero-init 的 simple residual `adapter_mask_head`，并让 `reconstruction_extra` 只更新这条专属输出分支，它仍然可能在 absent proxy 本体上明显反向；这说明“专属分支”这个方向是对的，但当前这条 simple output residual adapter 还不够表达

现象：

- 本轮补了：
  - `enable_adapter_mask_head`
  - `adapter_mask_max_delta`
  - `reconstruction_extra_prediction`
- 并跑了：
  - `v49 = adapter_mask_head only`
- `v49`
  只训练：
  - `adapter_mask_head`
  - trainable parameter count：
    - `197,377 / 2,564,994`
    - `7.70%`
- relative to `v19`：
  - `proxy_v7 = -1.542894 dB`
  - exact `target_full = -0.406366 dB`
  - `speech_leak_like (0004) = -0.048850 dB`
- relative to `v32` gate：
  - `exact_target_full_gain_floor = clear_fail`
  - `speech_leak_like_gain_floor = near_tie`
  - `guodegang_absent_floor = near_tie`

处理：

- 已把这轮 adapter branch 工程补充与 `v49`
  结果集中落盘到：
  - `reports/daily/2026-03-20_v49_v50_adaptermask_followup.md`

结果：

- 现在可以明确写死：
  - “给 absent-side 独立输出分支”
    这个大方向仍值得保留；
  - 但当前这种
    - shared encoded feature
      上直接叠一个 simple residual mask head
    还远远不够；
  - 不能把：
    - `v49`
      的结构方向成立
    误写成：
    - “这条 simple adapter 已经可继续微调到 keep”

影响：

1. 以后若继续沿 adapter 方向，
   默认要升级成：
   - adapter-specific conditioning
   - 或真正 dual-head
2. 不再把：
   - simple residual output head
   当作默认终局结构。

### 113. 当 simple residual adapter 的大残差会把 absent proxy 明显推反时，把 `max_delta` 压小确实能把 friend-side 拉回到 near-tie，但如果 absent proxy 本体仍明显负向，就不该继续扫这条 residual safety knob

现象：

- 本轮继续跑了：
  - `v50 = same adapter, adapter_mask_max_delta = 0.05`
- relative to `v49`：
  - exact `target_full`
    - `-0.406366 -> -0.323341 dB`
  - `speech_leak_like (0004)`
    - `-0.048850 -> -0.042961 dB`
  - `proxy_v7`
    - `-1.542894 -> -1.082981 dB`
- relative to `v32` gate：
  - `overall_judgement = near_tie`
  - `clear_fail_rules = []`
  - 但仍 failed：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_absent_floor`
    全部只到 `near_tie`

处理：

- 已把 `v50`
  的训练、compare、gate 与裁决集中落盘到：
  - `reports/daily/2026-03-20_v49_v50_adaptermask_followup.md`

结果：

- 现在可以明确写死：
  - `v49`
    的严重反向，
    部分确实来自 residual step 太大；
  - 但即便把 residual 幅度压小，
    simple adapter branch
    仍然拉不回 absent proxy 本体；
  - 当前问题不再是：
    - `max_delta`
      该调到多少
    而是：
    - 结构表达力本身不够

影响：

1. 下一条若继续自动推进，
   默认不再扫：
   - `adapter_mask_max_delta`
   - 或 simple residual adapter 的小数点参数
2. 当前更合理的默认延伸应升级成：
   - adapter-specific conditioning
   - 或真正 dual-head / branch-local output branch
3. 回看 `v49 / v50`
   时，要把它们记成：
   - “确认 simple adapter 不够”
   而不是：
   - “只是还没调到合适幅度”。

### 114. 如果 simple adapter 已经证明“看 reference 不够”，那么继续给这条 residual branch 补 `ref_film` 条件化，只能把它维持在 near-tie，不会自然把 absent proxy 本体拉回；这说明当前缺口不只是 adapter 没看到 reference

现象：

- 本轮继续给 adapter 分支新增：
  - `adapter_conditioning_mode`
  - `none / ref_bias / ref_film`
- 并跑了：
  - `v51 = adapter ref_film conditioning`
- `v51`
  仅训练：
  - `adapter_condition_scale`
  - `adapter_condition_shift`
  - `adapter_mask_head`
- relative to `v19`：
  - `proxy_v7 = -1.016036 dB`
  - exact `target_full = -0.317694 dB`
  - `speech_leak_like (0004) = -0.042935 dB`
- relative to `v32` gate：
  - `overall_judgement = near_tie`
  - near-tie：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_absent_floor`

处理：

- 已把 `v51`
  的训练、compare、gate 与裁决集中落盘到：
  - `reports/daily/2026-03-20_v51_v52_adapter_conditioning_and_temporal_followup.md`

结果：

- 现在可以明确写死：
  - 当前问题不只是：
    - adapter 分支没看到 reference
  - 因为即便 adapter 已经吃到自己的 `ref_film` 条件，
    `proxy_v7`
    仍然明显负向

影响：

1. 以后若继续沿 branch-local adapter，
   默认不再把：
   - “再给它多一层 reference conditioning”
   当成主要缺口
2. 当前更合理的默认方向应升级成：
   - 更强的 branch-local decoder / dual-head
   而不是继续堆 adapter conditioning。

### 115. 如果 adapter 分支已经有自己的时序模型，结果仍然只是 near-tie 而 `proxy_v7` 继续负向，就该把“shared path 上叠 residual branch”这条大类结构判为基本到头，而不是继续加深 adapter 容量

现象：

- 本轮继续新增：
  - `enable_adapter_temporal_model`
  - `adapter_gru_layers`
- 并跑了：
  - `v52 = adapter_temporal_model + adapter_mask_head`
- `v52`
  仅训练：
  - `adapter_temporal_model`
  - `adapter_mask_head`
  - trainable parameter count：
    - `986,881 / 3,354,498`
    - `29.42%`
- relative to `v19`：
  - `proxy_v7 = -0.876078 dB`
  - exact `target_full = -0.310738 dB`
  - `speech_leak_like (0004) = -0.041941 dB`
- relative to `v32` gate：
  - `overall_judgement = near_tie`
  - near-tie：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_absent_floor`

处理：

- 已把 `v52`
  的训练、compare、gate 与裁决集中落盘到：
  - `reports/daily/2026-03-20_v51_v52_adapter_conditioning_and_temporal_followup.md`

结果：

- 现在可以明确写死：
  - 当前缺的已经不是：
    - adapter 分支更强一点的 conditioning
    - 或更大一点的 temporal capacity
  - 即便给 adapter branch
    自己的一层双向 GRU，
    仍然只能把结果压到 near-tie，
    拉不回 absent proxy 本体

影响：

1. 下一条若继续自动推进，
   默认不再扫：
   - adapter branch 的 conditioning 变体
   - adapter branch 的 temporal 容量
2. 当前更合理的默认方向应直接升级成：
   - 真正独立的 dual-head / branch-local decoder
   - 或训练图级别的更强语义解耦
3. 回看 `v51 / v52`
   时，要把它们记成：
   - “adapter line has been structurally pressure-tested”
   而不是：
   - “这条 adapter 再堆一点容量也许就够了”。

### 116. 真正的 dual-head / branch-local decoder 若从旧 checkpoint 起步，却不先复制 base decoder 权重，实验会被“随机新头”噪声污染

现象：

- 当前已正式补入：
  - `enable_branch_decoder_head`
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- 这条线的目标是：
  - 给 absent-side 一套真正独立的 decoder；
  - 不再只是 shared path 上叠 residual branch。
- 但如果直接从旧 checkpoint
  `strict=False` 加载后就开跑，
  新 branch decoder
  会保留随机初始化；
- 这样第一条 dual-head 实验
  就不再是：
  - “从 `v32` 等价起步，只让 branch-local decoder 学增量”；
  而会混进：
  - “随机新头本身带来的大幅 default / proxy 扰动”。

处理：

- 已在：
  - `src/tse_prefix/models/stft_mask_baseline.py`
    增加：
    - `reset_branch_decoder_from_base()`
- 已在：
  - `scripts/train/train_stft_mask_baseline.py`
    增加：
    - `--model-enable-branch-decoder-head`
    - 旧 checkpoint 初始化时允许缺失：
      - `branch_decoder_temporal_model.*`
      - `branch_decoder_mask_head.*`
    - 若缺失则自动：
      - `reset_branch_decoder_from_base()`
- 并已用：
  - `v32 -> tmp/smoke_branch_decoder_v53`
    跑过一轮 `max_steps = 1` smoke，
    确认旧 checkpoint 兼容、
    branch decoder 自举初始化、
    以及 `reconstruction_extra` 路由都正常。

结果：

- 现在第一条 dual-head follow-up
  可以默认解释成：
  - 与旧 base decoder 同起点；
  - 差异主要来自 branch-local decoder 的后续更新；
- 不再把“随机新头初始偏差”
  误读成：
  - dual-head 方向本身失败
  - 或 dual-head 一上来就明显伤 default。

影响：

1. 后续任何 `dual-head / branch-local decoder` 候选，
   若是从旧 checkpoint warm-start，
   都应显式确认：
   - branch decoder 是否已从 base decoder 自举复制。
2. 若某轮 dual-head 结果很差，
   先排除：
   - 是训练方向错了；
   还是：
   - 新头其实根本没按 base 权重起步。
3. `tmp/smoke_branch_decoder_v53/train_summary.json`
   应视为这条 plumbing 已接通的最低证据，
   后续不再重复怀疑：
   - “是不是工程根本没接好”。 

### 117. 对 dual-head 分支，如果 extra 类 loss 仍默认挂在 frozen base output 上，新分支就会只吃到 absent-side reconstruction，friend-side guardrail 根本不会真正回流

现象：

- 本轮第一条正式 dual-head 候选：
  - `v53 = dual-head + proxy_v7 reconstruction only`
- 训练配置表面上仍保留了：
  - `transient_weight`
  - `interference_weight`
  - `interference_extra_weight`
  - `absent_weight`
- 但在 `v53` 当时的训练图里：
  - base losses 继续看 frozen `estimated_waveform_base`
  - branch decoder 只通过：
    - `reconstruction_extra_prediction = estimated_waveform`
    收梯度
- 结果是：
  - `proxy_v7 = +1.465092 dB`
  - `guodegang_anchor = +0.296715 dB`
  - `guodegang_absent = +0.060516 dB`
  都明显增强；
  - 但 friend-side 仍 clear fail：
    - exact `target_full = -0.875034 dB`
    - `speech_leak_like (0004) = -0.104842 dB`

处理：

- 已在：
  - `src/tse_prefix/pipeline/baseline_train.py`
    新增：
    - `extra_prediction`
- 已在：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
    补入：
    - `resolve_branch_extra_prediction(outputs)`

结果：

- 现在可以明确区分：
  - `v53`
    是“friend-side extra guardrail 实际没接到 dual-head”
  - 而不是：
    - dual-head 本身完全没有方向

影响：

1. 以后只要 trainable prefixes
   只剩 branch-local decoder，
   就不能再默认认为：
   - base loss 配着 extra weight
     就已经在约束新分支。
2. 判断 dual-head 失败前，
   先核对：
   - 这条分支到底真正吃到了哪些 loss。
3. `v53`
   应记成：
   - “single-sided absent training on dual-head”
   而不是：
   - “dual-head fully tested and failed”。

### 118. 即使把现有 friend-side `interference_extra residual_projection_ratio` 真正接到 dual-head，上面的冲突也不会自动变成有效对冲；`v54` 说明它反而会把 absent-side 收益和 friend-side 回退一起放大

现象：

- 本轮在修好 routing 后继续跑了：
  - `v54 = dual-head + proxy_v7 reconstruction + friend exact interference_extra`
- 并确认：
  - `interference_extra`
    真正命中 branch decoder：
    - train `7 / 129`
    - val `3 / 37`
- 但相对 `v53`：
  - `proxy_v7`
    继续增强：
    - `+1.465092 -> +2.016788`
  - `guodegang_anchor`
    继续增强：
    - `+0.296715 -> +0.465969`
  - `guodegang_absent`
    继续增强：
    - `+0.060516 -> +0.097155`
  - 同时 friend-side 更差：
    - exact `target_full`
      `-0.875034 -> -1.349682`
    - `speech_leak_like (0004)`
      `-0.104842 -> -0.128521`

处理：

- 已把 `v53 / v54`
  的训练、compare、gate 与解释集中落盘到：
  - `reports/daily/2026-03-20_v53_v54_dualdecoder_followup.md`

结果：

- 当前 dual-head 的主要缺口
  已不再是：
  - extra routing 没接上
- 而是：
  - 现有这条 friend-side
    `residual_projection_ratio`
    objective
    即便接到 branch decoder，
    也不会形成 keep 方向的对冲；
  - 它和 absent-side `proxy_v7 reconstruction`
    在这条新分支上，
    更像同向强化，
    不是互相制衡。

影响：

1. 下一条 dual-head follow-up
   默认不再扫：
   - 同一条 `interference_extra residual_projection_ratio`
     的权重；
   - 或继续机械复用同一批 `v30 exact 10 ids`
     当 protect objective。
2. 后续若继续保留 dual-head，
   friend-side protect objective
   应改成更贴近：
   - `keep target_full`
   - `protect speech_leak_like`
   的 branch-local 约束，
   而不是再把当前 residual extra
   当默认答案。
