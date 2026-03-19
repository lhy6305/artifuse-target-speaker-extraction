# 2026-03-19 v36 anchor transient-extra / absent-union smoke

## 背景

上一轮已经把 friend-side follow-up 的 stop condition 收紧到两条 real / near-real floor：

- `guodegang_anchor_floor`
- `guodegang_absent_floor`

同时也确认了一个明确的工程阻塞点：

- `transient_extra / absent_extra` 在训练图里还没有真正独立的 branch-local weight

因此先补了 plumbing，再基于这套新 plumbing 开第一条最小 smoke：

- 保留 `v32` 的 friend-side speech-leak branch
- 额外挂：
  - `transient_extra = guodegang_anchor_proxy_v1`
  - `absent union = guodegang_absent_proxy_v3_strict`

目标不是立刻做大步升级，而是先验证：

- 把 `anchor` 保护项从 base transient 分支拆出来，是否能更稳地守住 real floor

## 训练配置

checkpoint：

- `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v36_v32_anchor_transientextra_absentunion_smoke_ft1`

初始化：

- `v32`

manifest：

- train:
  - `data/synthetic/train_manifest_v36_v30_plus_guodegang_anchor_proxy_v1_plus_absent_proxy_v3_strict.jsonl`
- val:
  - `data/synthetic/val_manifest_v36_v30_plus_guodegang_anchor_proxy_v1_plus_absent_proxy_v3_strict.jsonl`

loss 变化点：

- 保留 `v32` 的：
  - base transient
  - base interference
  - `interference_extra` exact speech-leak branch
- 新增：
  - `transient_extra_weight = 0.001`
  - `transient_extra_focus_sample_ids = sample_ids_guodegang_anchor_proxy_v1_all.txt`
- 未启用：
  - `absent_extra_weight`

原因：

- `guodegang_absent_proxy_v3_strict` 虽然被并进了 union manifest，
  但它的样本本质上仍是：
  - `target_full`
  - `target_absent_intervals = []`
- 所以它并不满足 `absent_extra_interval_l1` 的监督前提，
  当前这条 objective 实际上无法对它生效。

## 关键观察

### 1. `absent_proxy_v3_strict` 没有给 `absent_extra` 带来可训练监督

`v36` union manifest 的规模是：

- train `176`
- val `47`

和 `v35` 的 union 规模一致，没有新增样本。

同时统计可见：

- train manifest 中 `target_absent_intervals` 非空样本数：`0`
- val manifest 中 `target_absent_intervals` 非空样本数：`0`

因此：

- 这次 `v36` 虽然名字上是 `anchor + absent union`
- 但真正新加进去、且有独立损失权重的，只有 `anchor -> transient_extra`
- `absent_proxy_v3_strict` 仍缺一条匹配它语义的 objective path

### 2. `v36` 没有保住 real floor，且连 exact / `0004-like` 也一并回退

相对 `v19`：

- default：
  - `+0.042394 dB`
- exact speech-leak proxy：
  - `-0.038284 dB`
  - exact `target_full = -0.322388 dB`
- near-real speech probe overall：
  - `-0.092008 dB`
- near-real `speech_leak_like (0004)`：
  - `-0.042726 dB`
- near-real `guodegang_anchor_120s`：
  - `-0.300635 dB`
- near-real `guodegang_absent_480s`：
  - `-0.094534 dB`

相对 `v32` 的 friend-side follow-up gate：

- `overall_pass = false`
- failed rules：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`

说明：

- 这条 minimal smoke 不仅没解决 `guodegang` floor
- 甚至把 `exact target_full` 和 near-real `0004-like speech-leak` 也一起拉回去了

因此不能把这次失败解释成：

- “只差 absent side 没接上”

更准确的解释是：

- 仅把 `anchor_proxy_v1` 拆到 `transient_extra`，
  不是这条线的可保留方向；
- 当前 `guodegang_anchor_proxy_v1` 对 real `guodegang_anchor_120s` 仍是错配保护项；
- `guodegang_absent_proxy_v3_strict` 也仍缺能真正约束它的独立 objective。

## 工程坑补记

本轮还发现：

- `data/synthetic/sample_ids_guodegang_anchor_proxy_v1_{train,val,all}.txt`
  原先是 UTF-8 BOM 文件
- 旧的 sample-id loader 用 `encoding=\"utf-8\"` 读取时，
  会把首个样本读成：
  - `\\ufefftrain_000029`

已修复：

- `scripts/train/train_stft_mask_baseline.py`
- `scripts/data/build_metadata_focused_manifest.py`

现在都改为：

- `encoding=\"utf-8-sig\"`

同时已把上述 3 个 sample-id 文件重写为无 BOM UTF-8。

额外 smoke 已确认：

- 新产物 `tmp/smoke_sample_id_utf8sig/train_summary.json`
  中的 `transient_extra_focus_sample_ids[0] = \"train_000029\"`
- 不再出现 `\\ufefftrain_000029`

## 结论

`v36` 应直接判掉，不进入 keep 候选。

当前更准确的后续方向不是：

- 继续扫 `transient_extra_weight`
- 或继续把 `guodegang_anchor_proxy_v1` 往这条线里塞

而是：

1. 承认 `anchor transient-extra only` 不是可保留路径。
2. 承认 `guodegang_absent_proxy_v3_strict` 当前并没有可用的 `absent_extra_interval_l1` 监督。
3. 后续如果还做 `guodegang_absent` 保护，应优先补新的独立 objective / branch：
   - 更像 `interference_extra` 的全样本保护项
   - 或直接面向 real / near-real gate 的保护代理
4. 后续所有 friend-side 新 candidate 仍默认先过：
   - `scripts/eval/gate_friend_speech_leak_followup.py`
