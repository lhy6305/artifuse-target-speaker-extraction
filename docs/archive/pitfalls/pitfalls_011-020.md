# 踩坑记录 历史归档 11-20

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `11-20`

## 2026-03-16

### 11. clean pool 中存在少量无法解码的坏音频

现象：

- 在做声学 embedding 提取时发现，当前 clean pool 中有 487 条音频既不能被 `soundfile` 读取，也不能被 `torchaudio` 和 `ffmpeg` 正常解码。

影响：

- 若不做容错，整轮 embedding 提取会被这些坏文件直接打断。
- 这些文件不适合进入后续训练或聚类流程。

处理：

- 已在 `scripts/data/downsample_genshin_clean_pool_with_acoustic_embeddings.py` 中将其记录到报告并跳过。
- 本轮下采样以 23170 条可读样本为输入完成。

后续要求：

1. 后面若继续清洗原神语音，优先把这批坏文件从上游候选集中剔除。
2. 若需要，可以再单独输出一个坏文件清单做人工或脚本级删除。

### 12. 公开仓库初始化后，Git 规则本身也需要视为正式项目状态

现象：

- 本项目已开始准备同步到公开 GitHub 仓库，用于实时备份开发进度。
- 这意味着 `.gitignore`、`LICENSE`、`NOTICE`、根目录 `README.md` 不再只是附属文件，而是正式仓库边界的一部分。

影响：

- 后续哪些文件应公开、哪些文件必须留在本地，不能只靠临时记忆判断。
- 若忽略规则漂移，容易在首次提交或后续提交时把不应公开的本地内容一起带上。

处理：

- 已初始化 Git 仓库并配置远端。
- 已将原始音频、标注文本、合成音频数据、local runtime 产物、`python.exe`、本地工具和敏感根目录文件纳入忽略边界。

后续要求：

1. 每次准备提交公开仓库前，都先看一次 `git status --short --ignored`。
2. 如果某类本地文件本应长期不公开，应优先通过 `.gitignore` 固化，而不是靠人工记忆避开。
3. 若新增中间模型或评估产物准备公开，先判断是否公开安全，再决定是否调整 ignore 规则。

### 13. 已确认存在根目录敏感凭证文件，当前未被跟踪

现象：

- 根目录当前存在敏感文件 `ssh-key-private`。
- 当前 `.gitignore` 已通过 `ssh-*` 规则命中它。
- 本地 Git 仓库当前还没有任何已跟踪文件，也没有任何提交。

影响：

- 当前状态下，该敏感文件未进入 Git 历史。
- 后续只要不绕过 ignore 规则，它就不会被正常纳入公开仓库。

处理：

- 已使用 `git status --short --ignored`、`git ls-files`、`git check-ignore -v ssh-key-private` 实际核对。

后续要求：

1. 把“先检查是否命中 ignore 再提交”视为固定动作。
2. 任何新增的本地敏感文件，优先补到 `.gitignore` 的模式规则里。

### 14. synthetic 时序模式若只停留在“目标全程存在”，会把训练分布喂偏

现象：

- 首版 `scripts/data/build_synthetic_dataset.py` 虽然已能生成最小样本，但目标语音默认全程存在。
- 这种分布会让模型过度习惯“输入里总能找到目标人”，不利于学习目标缺席或中断场景。

影响：

- 进入正式训练后，模型对 `target absent`、`target intermittent` 场景的抑制能力会偏弱。
- metadata 虽然可以事后补字段，但如果 `target.wav` 本身没有按时序留出静音区，监督目标仍然是不对的。

处理：

- 已把 synthetic 生成逻辑改成按 `TargetPattern` 实际渲染 `target.wav`。
- 当前已支持并实际验证：
  - `target_full`
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
- metadata 已同步记录 `target_segments` 和 `target_absent_intervals`，不再只是写一个空描述字段。

后续要求：

1. 若继续增强 realism，优先补更复杂的 intermittent 和 overlap 结构。
2. 在真正开训前，至少抽听一批包含各时序模式的样本，确认空窗段没有被错误填音。

### 15. baseline 最小训练闭环打通前，模型实现细节比“效果好坏”更容易先出边界错误

现象：

- 在首轮 baseline smoke training 中，先后遇到了两个典型工程问题：
  - `istft` 按真实长度返回后，batch 内不同样本长度不能直接 `stack`
  - `istft` 与 target 在个别 batch 中出现 1 个采样点的边界偏差

影响：

- 如果不先解决这些边界对齐问题，训练会在非常早的阶段直接崩掉，根本进不到“效果评估”。

处理：

- 已将模型输出改为 batch 内补齐。
- 已在 loss 里按预测与 target 的公共最短长度对齐，避免单点边界误差中断训练。

当前状态：

- baseline smoke training 已跑通。
- 当前更适合继续扩大训练与补 inference，而不是重新讨论模型结构细节。

### 16. eval 侧的 checkpoint 兼容性与训练侧并不完全一致

现象：

- 训练脚本保存的 checkpoint 中包含 `pathlib.WindowsPath` 等对象。
- 评估脚本如果强制用 `torch.load(..., weights_only=True)`，会因为这些对象不在默认 allowlist 中而失败。

影响：

- 如果不处理，eval 虽然逻辑正确，但在加载 checkpoint 时会被 PyTorch 的安全收紧策略卡住。

处理：

- 已将 `scripts/eval/eval_stft_mask_baseline.py` 改成：
  - 先尝试 `weights_only=True`
  - 若遇到 `pickle.UnpicklingError`，再自动回退到普通加载

当前状态：

- eval 脚本已稳定跑通。

### 17. smoke run 跑通不等于 baseline 已经有业务结论

现象：

- smoke run 的主要价值是验证训练和评估链路能完整执行。
- 即便 stage1 相比 smoke 指标已有明显提升，也仍然只是在 synthetic val 集上改善。

影响：

- 当前结果说明“这条基线在合成集上能学到东西”，但还不能直接推出真实场景已经可用。

处理建议：

1. 继续扩大 synthetic 训练规模，看指标是否继续稳定改善。
2. 后续尽量补更细粒度统计，例如按 recipe、时序模式、目标占空比拆看。
3. 待具备试听条件后，再补听感验证，不把当前数值当成最终业务结论。

当前状态：

- baseline stage1 已完成。
- 当前已从“链路能跑”进入“synthetic 指标开始改善”的阶段。

### 18. 总指标改善后，分组统计仍然必要

现象：

- stage2 相比 stage1，总体指标继续改善。
- 但按 recipe 分组后可以看到，不同干扰组合的难度差异仍然明显。
- 当前 stage2 中更难的 recipe 主要集中在：
  - `target_clean_plus_music`
  - `target_clean_speech`

影响：

- 如果只看总体平均值，容易误以为各类场景都在同步改善。
- 实际上不同干扰组合可能需要不同的数据配比或模型增强方向。

处理：

- 已在 eval 脚本中加入：
  - `recipe_metrics`
  - `target_present_ratio_bucket_metrics`

后续要求：

1. 后面若继续做 stage3，优先盯难 recipe，而不是只追总 loss。
2. 若某一类 recipe 持续偏难，可回到 synthetic 配比或 target pattern 设计上做针对性补样。

### 19. “更偏向难样本”不等于“整体上更好的训练分布”

现象：

- 在 stage2 之后，针对难 recipe 做了一个受控对照实验：
  - 保持与 stage2 相同的数据规模
  - 只把 train recipe profile 从 `default` 改成 `hard_recipe_focus`
- 结果该对照实验整体明显差于 stage2 默认配比。

影响：

- 说明当前 baseline 结构下，纯 hard-focus 会破坏整体学习分布。
- 不能简单认为“把难样本比例拉高”就会自动提升难场景表现。

处理：

- 已完成对照训练与评估。
- 当前 synthetic 工作集已恢复到 stage2 默认配比，保持主线状态稳定。

后续要求：

1. 如果还想继续动数据配比，优先尝试更温和的混合比例，而不是极端偏置。
2. 也可以直接把精力转向模型侧增强，而不是继续硬推数据分布。

### 20. 模型结构一旦演进，checkpoint 必须携带足够的复现信息

现象：

- baseline 从 `legacy_bias` 版 reference conditioning 演进到 `ref_film` 后，模型参数名和张量形状都发生了变化。
- 如果 checkpoint 不记录结构配置，评估脚本就无法知道该实例化旧结构还是新结构。

影响：

- 旧实验结果可能在脚本升级后“看起来还在”，但实际上已经无法稳定复现。
- 这类问题不是训练效果问题，而是实验资产管理问题；一旦放过，后面做 A/B 对照会很乱。

处理：

- 训练脚本保存 checkpoint 时，现已显式写入 `model_config`。
- 评估脚本加载 checkpoint 时：
  - 新 checkpoint 按 `model_config` 还原；
  - 旧 checkpoint 若检测到 `condition_proj.weight`，则自动按 `legacy_bias` 兼容加载。
- 已实际验证旧的 stage2 checkpoint 在新版 eval 脚本下仍能复现原指标。

后续要求：

1. 以后只要模型结构有演进，都必须同步更新 checkpoint 内的结构描述字段。
2. 做结构 A/B 时，优先让 eval 从 checkpoint 自带配置恢复，不依赖“当前代码默认值刚好一致”这种侥幸。
