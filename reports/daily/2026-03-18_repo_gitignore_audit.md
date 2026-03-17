# 2026-03-18 Repo And Gitignore Audit

## 本次目的

从“意外丢失后最大可恢复目标”的角度，审一次当前仓库工作树里的版本控制边界：

- `.gitignore` 是否过宽
- 哪些文件虽然是生成物，但其实应该保留为可跟踪恢复元数据
- 哪些文件即使有恢复价值，也仍应因为敏感/版权/体积原因留在本地

本次结论只针对工作树里的规则与文档，不讨论 `.git/` 内部配置。

## 主要结论

原规则不够合理，原因不是“泄露风险太高”，而是“恢复边界太粗”：

1. `experiments/*` 会把 `train_summary.json` 一起挡掉。
2. `reports/eval/` 会把：
   - `eval_summary.json`
   - compare `summary.json`
   - blind pack `README.md`
   - `blind_key.json`
   - `sample_meta.json`
   一起挡掉。
3. 上述文件都很小，而且正是恢复实验配置、比较结果、blind pack 组成时最有价值的元数据。

因此当前 `.gitignore` 已改成更细的边界：

- 继续忽略：
  - 原始音频与版权受限音频
  - synthetic 生成音频
  - checkpoint、`.pt/.pth/.ckpt`
  - 本地工具、缓存、临时文件
  - 指向本地/非公开资产路径的 manifest
- 重新保持可跟踪：
  - `experiments/**/train_summary.json`
  - `reports/eval/**/eval_summary.json`
  - `reports/eval/**/summary.json`
  - `reports/eval/**/README.md`
  - `reports/eval/**/blind_key.json`
  - `reports/eval/**/listening_results_summary.json`
  - `reports/eval/**/listening_rubric.json`
  - `reports/eval/**/sample_meta.json`

## 为什么 `data/manifests/` 这次没有放开

抽检后确认，`data/manifests/` 中不少文件直接写着：

- `data_in/...`
- 本地 source segment 路径
- 与非公开原料直接绑定的资产位置

这类 manifest 虽然对恢复有帮助，但当前还不是公开安全资产。

因此当前判断是：

1. 它们继续留在本地更合理。
2. 真要进入版本控制，应先做：
   - 脱敏
   - 公开安全副本
   - 或用脚本/文档复刻其生成逻辑

## 已落盘的规范

本次已同步更新：

- `docs/00_context_bootstrap.md`
  - 新增 `.gitignore` 与可恢复边界规则
- `docs/01_project_overview_and_plan.md`
  - 登记本轮仓库边界调整
- `docs/02_pitfalls_log.md`
  - 记录“整目录忽略会误伤恢复摘要”的踩坑
- `README.md`
  - 对外说明当前仓库保留哪些结构化摘要，哪些内容仍本地化

## 后续固定动作

1. 改 `.gitignore` 时，必须同时检查：
   - 公开边界
   - 可恢复边界
2. 目录中若同时有重资产和小摘要，优先保留摘要可跟踪。
3. 每次改完 ignore 规则，都至少补看一次：
   - `git status --short --ignored`
