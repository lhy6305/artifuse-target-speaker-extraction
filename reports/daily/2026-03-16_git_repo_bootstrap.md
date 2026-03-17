# 2026-03-16 Git Repo Bootstrap

## 本次目的

为项目建立可公开同步到 GitHub 的本地仓库基础设施，用于实时备份开发进度。

本次目标不是整理对外教程，而是把仓库边界先定住：

- 哪些内容可以公开
- 哪些内容必须留在本地
- 本地敏感文件当前是否安全

## 本次完成

- 在根目录初始化了 Git 仓库：
  - 分支：`main`
- 配置了远端：
  - `origin = https://github.com/lhy6305/artifuse-target-speaker-extraction.git`
- 新增了：
  - `.gitignore`
  - `LICENSE`
  - `NOTICE`
- 更新了根目录 `README.md`，改成面向公开仓库首页的最小描述。

## 当前公开仓库边界

计划公开：

- 代码
- 脚本
- 配置
- 方案文档
- 阶段报告
- 评估结论
- 公开安全的模型或中间产物

默认不公开：

- `data_in/`
- 音频文件
- `lab` 标注文件
- `data/curated/`
- `data/interim/`
- `data/references/`
- `data/synthetic/`
- `data/manifests/`
- 本地运行工具与 runtime 噪声

## 本次核对结果

已执行：

- `git status --short --ignored`
- `git ls-files`
- `git log --oneline --decorate --graph --all`
- `git check-ignore -v ssh-key-private`

结论：

- 当时仓库还没有任何已跟踪文件。
- 当时仓库还没有任何提交历史。
- 根目录敏感文件 `ssh-key-private` 已命中 `.gitignore` 中的 `ssh-*` 规则。
- 因此它当前未被跟踪，也未进入 Git 历史。

补充更新（`2026-03-17`）：

- 仓库此后已产生提交历史，这份日报里的“还没有提交历史”只代表 `2026-03-16` 建仓当时的状态。
- 后续关于 Git 的当前事实，应以最新 `git log` 和总览文档为准。

## 后续规范

1. 首次公开推送前，再人工核对一次 `git status`。
2. 本地不应公开的内容，优先通过 `.gitignore` 固化。
3. 若未来要公开模型或评估产物，先确认其可公开性，再决定是否放开 ignore 规则。
4. 开发文档仍以项目内部恢复和接班为主，不以对外 onboarding 为目标。
