# 2026-03-20 `branch_protect` guard selector plumbing

## 背景

`v61 / v62` 已把当前 dual-head protect 线的结论收紧到：

- `target_full`-only selector
  是对的；
- 但继续只扫同一条
  `base-align` weight
  不是正确延伸；
- 下一条更合理的方向应是：
  - 保留 `target_full` 保护；
  - 再显式补一条
    更直接面向
    `speech_leak_like (0004)`
    的 branch-local protect signal。

当前工程缺口不在模型结论，
而在训练脚本此前只有一条
`interference_extra`
protect selector：

- 这意味着：
  - `target_full`-only `base-align`
  - 和 `0004-like` guard
  还不能各自挂在不同 selector 上。

## 本轮工程补充

已新增一条独立的 `branch_protect` selector / loss 通道，
用于给 branch-local output
单独挂第二条 protect objective，
而不复用现有 `interference_extra` selector。

### 代码改动

- `src/tse_prefix/pipeline/baseline_train.py`
  - `LossBreakdown` 新增：
    - `branch_protect_guard_sisdr_loss`
  - `compute_losses(...)` 新增：
    - `branch_protect_sample_weights`
    - `branch_protect_guard_sisdr_weight`
  - 语义：
    - 对 `extra_prediction`
      在独立 selector 命中的样本上，
      单独计算一条 `SI-SDR guard`
- `src/tse_prefix/pipeline/loss_selectors.py`
  - `selector_config_keys(...)`
    纳入：
    - `branch_protect`
- `scripts/train/train_stft_mask_baseline.py`
  - 新增权重参数：
    - `--loss-branch-protect-guard-sisdr-weight`
  - 新增 selector 参数族：
    - `--loss-branch-protect-*`
  - 训练 / 验证 summary
    新增：
    - `branch_protect_guard_sisdr_loss`
    - `branch_protect` selector metrics
  - 顺手修正：
    - selector CLI flag
      对带下划线前缀
      统一转成连字符写法，
      避免出现
      `--loss-branch_protect-*`
      这种难记参数
- `scripts/eval/eval_stft_mask_baseline.py`
  - eval summary / pattern / recipe / ratio bucket
    新增：
    - `branch_protect_guard_sisdr_loss`

## 1-step smoke

### 命令目标

不是验证模型效果，
只验证：

- 新 selector 能命中；
- 新 loss 能进入 train/eval summary；
- train / eval 两侧都不崩。

### smoke 设置

- train manifest：
  - `data/synthetic/train_manifest_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
- val manifest：
  - `data/synthetic/val_manifest_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
- init：
  - `v32`
- output：
  - `tmp/smoke_branch_protect_guard_sisdr`
- dual-head：
  - `enable_branch_decoder_head = true`
- 仅训练：
  - `branch_decoder_temporal_model`
  - `branch_decoder_mask_head`
- 新 protect：
  - `--loss-branch-protect-guard-sisdr-weight 0.0002`
  - selector：
    - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt`
- 预算：
  - `epochs = 1`
  - `max_steps = 1`

### smoke 结果

训练侧：

- `branch_protect` selector 命中：
  - train `4 / 7`
  - val `1 / 3`
- step log 已出现：
  - `branch_protect_guard_sisdr_loss = 6.596457`

验证侧：

- `tmp/smoke_branch_protect_guard_sisdr_eval/eval_summary.json`
  已正常落盘
- overall metrics 中已出现：
  - `branch_protect_guard_sisdr_loss = 16.299091`

结论：

- 新的 `branch_protect`
  selector / loss plumbing
  已接通；
- 下一条若要做：
  - `target_full`-only `base-align`
  - 加上
    `0004-like` 独立 guard
  已不再缺工程入口。

## 当前更新

当前默认下一步可以直接进入：

- `v63 = target_full-only base-align`
  `+`
  `0004-like branch_protect guard`

而不需要再补额外 plumbing。
