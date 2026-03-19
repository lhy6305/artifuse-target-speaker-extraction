# 2026-03-19 transient / absent extra branch plumbing

## 背景

上一轮 `v35` 已经把问题收敛得很明确：

- `guodegang_anchor_proxy_v1` 直接并进原有 transient 分支，不足以保护真实 `guodegang_anchor_120s`
- friend-side follow-up gate 最终卡住的，也不是 speech-leak side 本身，而是：
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

因此当前更具体的工程阻塞点不是：

- gate 还没写
- 或 synthetic proxy 还没搜

而是：

- 训练图里只有 `interference_extra` 是真正 branch-local 的独立权重；
- `transient_extra / absent_extra` 虽然能选中样本，但仍只能并进 base 分支同权计算。

大白话讲，就是：

- 现在可以单独给 speech-leak extra 分支上小权重；
- 但还不能同样单独给 `anchor` 或 `absent` 保护项上小权重。

## 本轮改动

### 1. `compute_losses(...)` 新增真正独立的 extra 通道

文件：

- `src/tse_prefix/pipeline/baseline_train.py`

新增：

- `transient_extra_sample_weights`
- `absent_extra_sample_weights`
- `transient_extra_weight`
- `absent_extra_weight`

`LossBreakdown` 新增：

- `transient_extra_presence_l1`
- `absent_extra_interval_l1`

当前训练图的含义变成：

- base transient：
  - `transient_presence_l1 * transient_weight`
- extra transient：
  - `transient_extra_presence_l1 * transient_extra_weight`
- base absent：
  - `absent_interval_l1 * absent_weight`
- extra absent：
  - `absent_extra_interval_l1 * absent_extra_weight`

因此后续终于可以把：

- `guodegang_anchor_proxy_v1`
- `guodegang_absent_proxy_v3_strict`

分别挂到：

- `transient_extra`
- `absent_extra`

而不是只能粗暴并回 base 分支。

### 2. train 脚本新增 CLI 与 summary 字段

文件：

- `scripts/train/train_stft_mask_baseline.py`

新增 CLI：

- `--loss-transient-extra-weight`
- `--loss-absent-extra-weight`

新增 selector 统计：

- `transient_extra`
- `absent_extra`

新增 train / val summary 字段：

- `train_transient_extra_presence_l1`
- `val_transient_extra_presence_l1`
- `train_absent_extra_interval_l1`
- `val_absent_extra_interval_l1`

### 3. eval 脚本新增 extra 指标落盘

文件：

- `scripts/eval/eval_stft_mask_baseline.py`

新增 summary / bucket / sample meta 字段：

- `transient_extra_presence_l1`
- `absent_extra_interval_l1`

这意味着后续做：

- `anchor` 保护
- `absent` 保护

不再只能看整体 transient / absent 指标，
而能单独看 extra 分支有没有被真正触发。

## Smoke 验证

### 训练 smoke

命令要点：

- manifest：
  - `train_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl`
  - `val_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl`
- 只跑：
  - `epochs = 1`
  - `max_steps = 1`
- 额外打开：
  - `loss_transient_extra_weight = 0.001`
  - `loss_absent_extra_weight = 0.001`
- 并分别用：
  - `target_clean_speech`
  - `target_hard_speech`
  作为一次最小 selector smoke

产物：

- `tmp/smoke_transient_absent_extra/train_summary.json`

关键结果：

- train:
  - `transient_extra_presence_l1 = 3.106702`
  - `absent_extra_interval_l1 = 0.0`
- val:
  - `transient_extra_presence_l1 = 2.233458`
  - `absent_extra_interval_l1 = 0.0`
- selector metrics:
  - `train_transient_extra = 3 / 4`
  - `train_absent_extra = 1 / 4`
  - `val_transient_extra = 22 / 40`
  - `val_absent_extra = 18 / 40`

说明：

- 新增的 extra branch 权重和 selector 统计已经真实接通；
- `absent_extra_interval_l1` 这次为 `0.0`，是因为这份 `v15` union manifest 本身没有显式 `target_absent_intervals`，这和 plumbing 是否接通是两回事。

### 评估 smoke

命令要点：

- checkpoint：
  - `tmp/smoke_transient_absent_extra/best.pt`
- manifest：
  - `val_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl`

产物：

- `tmp/smoke_transient_absent_extra_eval/eval_summary.json`

关键结果：

- `transient_extra_presence_l1 = 2.233458`
- `absent_extra_interval_l1 = 0.0`

说明 eval 侧 summary 也已经能正常落盘这些新增字段。

## 当前意义

这轮改动本身还不是新候选训练，
但它把下一步真正要做的 experiment 入口补齐了：

1. 可以把 `guodegang_anchor_proxy_v1` 只挂到 `transient_extra`
2. 可以把 `guodegang_absent_proxy_v3_strict` 只挂到 `absent_extra`
3. 可以给两侧不同的小权重
4. 可以再用 friend-side follow-up gate 判：
   - `guodegang_anchor_floor`
   - `guodegang_absent_floor`
   是否还在回退

## 下一步建议

若继续自动推进，下一条最小实验不应再是：

- 再扫 `interference_extra_guard_sisdr`
- 或继续并新的 synthetic `guodegang` proxy

而应优先是：

1. 以 `v19` 或 `v32` 为基座；
2. 保留现有 friend-side speech-leak branch；
3. 仅新增：
   - `transient_extra = guodegang_anchor_proxy_v1`
   - `absent_extra = guodegang_absent_proxy_v3_strict`
4. 先做一次：
   - 极轻量
   - 分侧
   - gate-first
   的 smoke / ft1；
5. 然后直接过：
   - `friend_speech_leak_followup_gate`
