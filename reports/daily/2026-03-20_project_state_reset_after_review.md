# 2026-03-20 项目状态重置与后续计划修正

## 背景

本轮已额外阅读：

- 根目录 `1.md`
- 根目录 `2.md`

两份文档都在提醒同一件事：

- 当前项目需要把
  - 默认主线
  - 研究排雷
  这两层重新分开；
- 并且当前不应继续沿
  “还能试什么就继续试什么”
  的自动实验节奏往前滚。

本次复核后的正式裁决如下。

## 正式裁决

### 1. 接受的部分

- 接受“当前已经不在主线切换阶段，而在研究排雷阶段”这一主判断。
- 接受“默认主线继续保持 `legacy stage2`”。
- 接受“`v19 / v32 / proxy_v7 / dual-head` 应被视为研究基座，而不是主线替换候选”。
- 接受“停止继续扫已证伪或已进入平台区的 primitive 近邻值”。
- 接受“项目级默认下一步应从自动开新实验，改成先停下来做状态管理与高层决策”。

### 2. 只部分接受的部分

- 不把“忘记初心”写成完全失控式表述；
  更准确的正式口径应是：
  - 目标锚点并没有丢；
  - 但执行节奏已经明显偏向 objective / gate 驱动，
    需要收回来。
- 不把所有失败分支都混成同一种归档；
  当前应区分：
  - `closed_failed`
  - `closed_but_evidence_keep`

例如：

- `v57 / v58`
  不应写成“无价值失败”，
  而应写成：
  - primitive 有信号，
  - 但“继续扫同一条 weight”
    这条线已关闭。

## 当前正式状态板

### 默认主线

- `legacy stage2`

### 当前主线结论

- `ref_film + stft0.5 + sisdr0.0005`
  不升主线；
- focused `ft2 / ft3`
  不升主候选；
- 后续 `v36+`
  默认解释为研究排雷分支，
  不是“即将替换主线”的连续版本。

### 当前研究基座

- absent-side 研究基座：
  - `v19`
- friend-side / branch-local 工程基座：
  - `v32`
- 有效 absent proxy：
  - `proxy_v7`
- 仍保留的结构方向：
  - dual-head / branch-local decoder

### 当前明确停止继续扫的内容

- `proxy_v7` 的微幅 waveform / stft 小变体
- prefix-freeze 小组合
- simple adapter 小参数 / 条件化 / temporal 变体
- dual-head 上已证伪 primitive 的近邻值：
  - `interference_extra residual_projection_ratio`
  - exact-family `SI-SDR guard`
  - `base-align` 近邻值
  - `base-delta-interference projection` 近邻值
- 回到 `proxy_v6`
- 旧 absent reconstruction carve-out 族

## 方案修正

### 1. 立即生效的执行修正

- 从现在开始：
  - 默认不再自动起新实验；
  - 若无用户明确指示，
    当前状态保持冻结。

### 2. 仍保留的下一条书面规格

下一条允许被重新激活的候选方案，
当前只保留为书面规格，
不执行训练：

- `v63 = dual-head`
  - 保留：
    - `target_full`-only `base-align`
  - 额外补：
    - `0004-like branch_protect guard`

当前建议的第二条 protect selector
采用：

- `exact_all - exact_targetfull_all`

对应当前已确认的补集 ids：

- `train_000405`
- `train_001279`
- `train_001491`
- `val_000096`
- `val_000297`

这条方案当前只做规格保留，
不写新的 checkpoint，
不跑训练，
不生成 compare / gate 产物。

### 3. 重新启动实验前的前置条件

若后续要重新开启训练，
应先满足：

1. 用户明确允许开启新实验。
2. 新实验必须明确服务于哪个真实问题：
   - `target_full`
   - `speech_leak_like (0004)`
   - `target absent`
   - 或其它 near-real 症状
3. 新实验不得只是已证伪 primitive 的近邻值重扫。

## 当前动作

本次仅做：

- 结论落盘
- 文档口径修正
- 默认计划冻结

本次不做：

- 新训练
- 新 compare
- 新 gate
- 新 checkpoint
