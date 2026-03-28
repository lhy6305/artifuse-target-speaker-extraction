# 2026-03-28 仓库健康度与规范性自检

## Summary

- 已完成覆盖扫描：
  - `docs/`
  - `configs/`
  - `src/`
  - `scripts/`
  - `reports/`
  - `experiments/`
  - `data/manifests/`
  - 根目录
- 当前结论：
  - 扫描开始时，tracked 工作区干净；
  - 核心 Python 文件可通过 `.\python.exe -m py_compile`；
  - 但仓库仍存在数个会影响长期维护或污染评估结论的风险点。

## Scan method

- 文档入口：
  - 按规范先读 `docs/00_context_bootstrap.md`
  - 再补 `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `docs/03_project_structure.md`
  - `docs/05_task_branch_map.md`
- Git / 目录检查：
  - `git status --short`
  - `git status --short --ignored`
  - `git ls-files`
  - 根目录与各主目录子项扫描
- 规模检查：
  - 统计主文档、主脚本行数与体量
  - 查看大文件与正式目录中的临时产物
- 代码检查：
  - 阅读 `src/` 核心模块
  - 阅读 `scripts/train/`、`scripts/eval/`、`scripts/data/` 关键入口
  - 对关键文件做 `py_compile`
  - 交叉核对训练与评估口径是否一致

## High-risk findings

### 1. 评估主流程与训练链的 dual / teacher 口径未完全对齐

位置：

- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

事实：

- 训练链已完整维护：
  - `branch_protect_teacher_overlap_l1`
  - `overlap_dual_mix_consistency_l1`
  - `overlap_dual_residual_target_projection_ratio`
  - 对应 selector hit summary
- 但评估主脚本 `main()` 落盘的总表、分组表和 `sample_meta.json`
  里没有把这套字段完整写出；
- 同时主流程 `compute_losses(...)` 也没有把 `overlap_dual_sample_weights`
  传进去。

影响：

- dual-controller / dual-decoder / teacher-veto 类 checkpoint
  的 `summary.json` 与 `eval_summary.json`
  可能丢失关键 loss 维度；
- 当这类 loss 被用于放行或拒绝某条研究线时，
  评估摘要会和真实训练约束不一致；
- 这属于会污染实验结论的问题，不只是“报表不够漂亮”。

建议：

- 把训练与评估共用的 loss / selector / summary 字段抽成统一 registry；
- 让 `eval_stft_mask_baseline.py` 的主流程复用同一套字段表；
- 修正后，对依赖 dual / teacher loss 的 checkpoint 重新导出评估摘要。

### 2. `focus_interference_pools / speaker_names` 仍只看第一层干扰

位置：

- `src/tse_prefix/data/synthetic_dataset.py`
- `src/tse_prefix/pipeline/loss_selectors.py`

事实：

- dataset 已同时产出：
  - `interference_pool`
  - `interference_speaker_name`
  - `interference_pools_all`
  - `interference_speaker_names_all`
- 但 selector 实现当前仍只匹配：
  - `batch["interference_pools"]`
  - `batch["interference_speaker_names"]`
  也就是第一层干扰；
- 仓库历史配置已经真实使用了：
  - `focus_interference_pools`
  - `focus_interference_speaker_names`
  例如：
  - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v24_v19_friend_reverse_guardrail_proxy_v4_semantic_split_ft1/train_summary.json`

影响：

- 对 `speech + music`
  或多层 speech 的样本，selector 命中集会偏离设计口径；
- 会导致 targeted loss 命中率、selector summary、后续实验解释同时偏掉；
- 这是静默型逻辑问题，最危险的地方就在于不报错。

建议：

- `focus_interference_pools` 和 `focus_interference_speaker_names`
  改成显式按 `_all` 字段做 `any-match`；
- 修正后重跑相关 selector summary，
  特别是历史上依赖 pool / speaker 聚焦的分支。

## Medium-risk findings

### 3. 训练 / 评估主指标默认按 batch 平均，不是按 sample 平均

位置：

- `scripts/train/train_stft_mask_baseline.py`
- `scripts/eval/eval_stft_mask_baseline.py`

事实：

- 多数总指标都先按 batch 累加，再除以：
  - `batch_count`
  - 或 `step_count`
- 这意味着最后一个短 batch 与满 batch 权重相同。

影响：

- 当 batch size 不整除样本数，或后续改成动态 batch 时，
  epoch / eval 总指标会出现系统性偏差；
- 当前影响通常不致命，但会持续污染横向比较的精度。

建议：

- 改成显式按 sample 数聚合；
- 或至少把“当前是 batch-average”写进 summary 元数据。

### 4. 根目录仍有敏感文件与不直观杂项

事实：

- 根目录存在：
  - `ssh-key-private`
  - `codex_perm_cleanup_static.exe`
  - `git-push.bat`
  - `git-push.sh`
- 其中 `ssh-key-private`
  虽未被 Git 跟踪，但仍位于仓库根目录。

影响：

- 安全边界与项目边界混在一起；
- 一旦后续脚本或人工操作失误，误打包、误外传或误引用风险都偏高；
- 也会破坏“根目录一眼看懂项目结构”的直觉。

建议：

- 秘钥移出仓库工作树；
- 推送辅助脚本、清理工具等本地工具
  统一挪到明确的本地工具目录或用户私有目录。

### 5. 正式目录里混入临时产物

事实：

- `reports/tmp_metric.wav`
  仍位于正式报告目录根下；
- `scripts/`、`src/` 下也存在多处 `__pycache__/`。

影响：

- 与仓库自己的目录纪律冲突；
- 会降低正式报告目录的可读性；
- 长期看会继续鼓励“先丢到正式目录再说”的习惯。

建议：

- `tmp_metric.wav`
  迁移到 `tmp/` 或判定后删除；
- 清理 `__pycache__/`，
  并在运行脚本时避免把缓存长期留在源码树里。

## Maintainability findings

### 6. 活跃文档与主入口脚本已经明显偏大

当前体量：

- `docs/01_project_overview_and_plan.md`
  - `1382` 行
- `docs/02_pitfalls_log.md`
  - `1960` 行
- `docs/05_task_branch_map.md`
  - `1941` 行
- `scripts/train/train_stft_mask_baseline.py`
  - `1860` 行
- `scripts/eval/eval_stft_mask_baseline.py`
  - `1279` 行
- `scripts/eval/listening_pack_gui.py`
  - `1227` 行

结论：

- 这些文件都已经到达“继续增长会显著增加维护成本”的区间；
- 文档侧虽然已有 archive 机制，但活跃摘要仍偏长；
- 代码侧则已经出现：
  - 参数解析
  - selector 组装
  - loss plumbing
  - summary 落盘
  - GUI 状态管理
  全部堆在单文件里的情况。

建议拆分：

- `scripts/train/train_stft_mask_baseline.py`
  - `args`
  - `checkpoint_io`
  - `selector_plumbing`
  - `epoch_runner`
- `scripts/eval/eval_stft_mask_baseline.py`
  - `checkpoint_io`
  - `loss_summary_registry`
  - `per_sample_export`
  - `aggregate_report`
- `scripts/eval/listening_pack_gui.py`
  - `csv_io`
  - `rubric_model`
  - `tk views`
  - `summary_export`
- `docs/01 / 02 / 05`
  - 继续压缩成短摘要
  - 把详细历史推进到 `docs/archive/` 与 `reports/daily/`

## Positive observations

- `.gitignore` 的大方向是对的：
  - 重资产、音频、checkpoint 主要留在 ignore 边界内；
  - 小型恢复元数据保留了可跟踪出口；
- `data/ / src/ / scripts/ / reports/ / experiments/ / tmp/`
  的一级职责整体清晰；
- README 与文档入口关系基本可追；
- 核心代码使用 `UTF-8` 读写的意识比较统一；
- 核心训练 / 评估 / 数据脚本可通过语法编译检查。

## Verification notes

- 已执行：
  - `.\python.exe -m py_compile`
    覆盖核心 `src/` 与主入口 `scripts/`
- 未执行：
  - 真实训练
  - 真实评估
  - 音频级回放
- 原因：
  - 本轮目标是一次性仓库健康度与规范性自检；
  - 重点在全仓静态扫描、口径一致性核对与目录规范审计。

## Next cleanup order

1. 先修 `scripts/eval/eval_stft_mask_baseline.py` 的 dual / teacher / selector 汇总口径。
2. 再修 `loss_selectors.py` 对 pool / speaker 的全层匹配语义。
3. 清理根目录敏感文件和 `reports/tmp_metric.wav` 的落点问题。
4. 启动主入口脚本与活跃文档拆分，优先拆训练入口和评估入口。
