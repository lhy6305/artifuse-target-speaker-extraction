# 踩坑记录

## 2026-03-16

### 1. 上下文恢复入口存在缺失文件

现象：

- `docs/00_context_bootstrap.md` 明确要求读取：
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `initial_design_judg.md`
- 但这些文件在本次整理前并不存在。

影响：

- 新会话无法按规范完整恢复上下文。
- 关键阶段信息容易只存在对话里，不落盘。

处理：

- 已补齐上述文件并写入首版内容。

后续要求：

- 以后新增引用文件时，必须同步创建并登记用途。

### 2. `segment_manifest.jsonl` 中存在历史绝对路径

现象：

- `data_in/source_segments/segment_manifest.jsonl` 中的 `path` 字段指向旧路径：
  - `F:/proj_dev/tmp/workdir4/...`
- 当前工作目录为：
  - `F:/proj_dev/tmp/workdir-4-1/...`

影响：

- 直接依赖该字段读取音频时，极可能找不到文件。
- 后续脚本若照搬历史绝对路径，数据管线会直接失败。

处理建议：

1. 后续正式 manifest 一律重建到 `data/manifests/`。
2. 新 manifest 优先保存相对路径，避免工作目录变更导致失效。
3. 若必须保留历史 manifest，需明确标注为“仅供参考，不可直接消费”。

当前状态：

- 已记录问题，尚未重写该 manifest。

### 3. `data_in/` 数据量很大，且类型混杂

现象：

- `data_in/genshin_voice_extract/` 文件规模很大。
- 同时存在 `wav` 与 `lab` 等不同类型文件。
- `friend_dataset_fuhuo_raw_concat.wav` 仍是长音频，不适合直接做数据桶。

影响：

- 如果不先做 manifest 和过滤，后续脚本会很慢，也容易把错误文件类型混进去。
- hard negative 池目前还不能直接使用。

处理建议：

1. 先做文件清单，而不是直接递归全目录跑训练。
2. clean interference 只收可消费音频格式。
3. hard negative 先切片再入池，不直接拿长音频训练。

当前状态：

- 已在结构文档中登记，等待下一阶段处理。

### 4. 数据整理脚本依赖 `ffmpeg` / `ffprobe`

现象：

- `scripts/data/prepare_curated_pools.py` 在生成音乐池时调用 `ffprobe`。
- 在切分 `friend_dataset_fuhuo_raw_concat.wav` 时调用 `ffmpeg` 与 `silencedetect`。

影响：

- 如果本机环境没有把 `ffmpeg` 和 `ffprobe` 放进 PATH，脚本会直接失败。
- 问题不在 Python 代码本身，而在外部工具前提没满足。

处理建议：

1. 后续凡是依赖音频切分、探测时长、混音的脚本，都在文档中明确写出 `ffmpeg` / `ffprobe` 前置要求。
2. 真正开始 synthetic mixture 生成前，先把这项依赖登记到脚本说明或 README。

当前状态：

- 本机当前环境已满足，`prepare_curated_pools.py` 已成功跑通。

### 5. `target_reference_pool` 不能简单取排序后前若干条

现象：

- 若把符合时长条件的 target 切片排序后直接取前 64 条作为 reference，reference 池会明显偏向时间上更靠前的一段录音。

影响：

- reference 分布不均匀，容易和整体 target 池产生不必要的时间段偏置。
- 后续若某些录音阶段的底噪或说话状态更固定，可能放大 reference 池的偏采样问题。

处理：

- 已将 `scripts/data/prepare_curated_pools.py` 的 reference 抽样逻辑改为在候选中均匀抽样。

后续要求：

1. 后面如果补充更细的 source 分组信息，优先按 session / 文件来源做更严格的隔离抽样。
2. 当前“均匀抽样”只是比“直接取前几条”更稳，不等于最终最优方案。

### 6. 首版 synthetic 生成器的时序覆盖仍然不完整

现象：

- 当前 `scripts/data/build_synthetic_dataset.py` 已能生成最小样本。
- 但当前样本仍以“目标全程存在 + 干扰可带起始偏移”为主。
- 设计稿中提到的 `target intermittent`、`target absent tail`、更复杂的 partial overlap 还没有全部落地。

影响：

- 现阶段更适合先验证数据链路和基础可用性。
- 若直接拿这版数据做正式训练，模型对“目标缺席”类场景的学习会不足。

处理建议：

1. 先保留这版作为 MVP 数据链路验证器。
2. 在进入正式 baseline 训练前，补 richer temporal patterns。
3. 补充人工抽听，确认简单 offset overlap 的听感是否自然。

当前状态：

- 已记录为下一步优先事项，尚未扩充到完整设计目标。

### 7. 当前磁盘不支持 hardlink 方案

现象：

- 在执行 `scripts/data/materialize_genshin_clean_subset.py` 时，`--mode hardlink` 失败。
- 当前存储环境对 `os.link(...)` 不可用，无法用“零额外内容占用”的硬链接方式保留子集。

影响：

- 若仍想把散选子集单独落盘，就只能使用：
  - `move`
  - 或 `copy`
- 其中 `copy` 会暂时增加额外占用，不适合磁盘紧张时优先采用。

处理：

- 已改用 `--mode move` 成功完成迁移。

后续要求：

1. 在当前环境下，默认把 `move` 视作更稳的节省空间方案。
2. 若后续迁移到支持硬链接的 NTFS 盘，再考虑恢复 `hardlink` 方案。

### 8. 原神 clean 子集迁移后，不能再把 `data_in/genshin_voice_extract/` 当作唯一真源

现象：

- `speech_interference_clean_pool` 的 768 条已选样本，已经从完整原神包中迁移到了 `data/curated/genshin_clean_subset/`。
- 原始 `data_in/genshin_voice_extract/` 现在仍是大包，但其中已不再包含这批被迁走的已选样本。

影响：

- 若后续无脑重跑 `prepare_curated_pools.py`，可能重新从不完整的原目录里挑出另一批样本，破坏当前 clean pool 的稳定性。

处理：

- 已在 `prepare_curated_pools.py` 中增加保护逻辑：
  - 如果发现现有 clean manifest 的 `source` 已指向 `data/curated/genshin_clean_subset`
  - 则直接保留当前 manifest，不再重建 clean pool

后续要求：

1. 当前 clean pool 的正式真源应视为：
   - `data/manifests/speech_interference_clean_pool.jsonl`
   - `data/curated/` 下当前激活的 clean 子集目录
2. `data_in/genshin_voice_extract/` 之后更适合被视作“上游残余原始包”，而不是当前 clean pool 的正式消费入口。

### 9. “覆盖全面”不等于“已做完整声学内容评估”

现象：

- 当前新版 clean pool 已经从“顺序截断”升级为 coverage-weighted sampling。
- 覆盖维度包括：
  - 说话人文件夹递归类别
  - 时长桶
  - 文本长度桶
  - 句式/标点特征
  - 去重倾向
- 并已确认所有纳入说话人的顶层类别都至少保留了 1 条样本。

影响：

- 这已经比旧版“前 24 条”强很多，能显著减少训练冗余。
- 但它仍不是：
  - 基于声学 embedding 的聚类抽样
  - 基于韵律/音素/能量轮廓的完整内容评估

处理建议：

1. 当前版本先作为 clean pool 的正式覆盖版使用。
2. 若后续训练仍表现出重复度过高，再补一轮声学嵌入聚类式下采样。

当前状态：

- 已完成 coverage-weighted v1。
- 尚未进入 embedding-level 去冗余阶段。

### 10. 当前环境足够做一轮无安装版声学 embedding 聚类

现象：

- 仓库自带 `python.exe` 当前可直接导入：
  - `numpy`
  - `scipy`
  - `sklearn`
  - `torch`
  - `torchaudio`
  - `librosa`
  - `soundfile`
- 当前未安装：
  - `speechbrain`
  - `wespeaker`

影响：

- 可以直接做一轮基于手工声学特征的 embedding 聚类下采样，无需新增装包。
- 若后续想做更强的“说话人表征”级聚类，则可能需要额外安装上述库并准备权重。

当前状态：

- 本轮已在不新增安装包的前提下完成 embedding-pruned v1。

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

### 21. reference conditioning 变强，不等于当前主指标一定同步变好

现象：

- 本轮把 baseline 的 reference conditioning 从 `legacy_bias` 升级到了 `ref_film`。
- 在与 legacy stage2 同预算的正式对照里，`ref_film` 的：
  - `loss` 更低
  - `stft_l1` 更低
- 但整体 `sisdr_db` 反而略差。

影响：

- 说明当前结构更擅长优化频谱重建，并不自动等于更好的分离质量。
- 如果只看 val loss 或 STFT 项，很容易误把它当成“新默认结构”，但这在当前主指标上站不住。

处理：

- 已完成正式对照并保留产物。
- 当前默认主线不切换到 `ref_film`，仍保持 `legacy_bias + stage2 default`。

后续要求：

1. 后续模型升级必须至少同时看：
   - 总 loss
   - `stft_l1`
   - `sisdr_db`
   - 必要的分组指标
2. 若某个新结构只改善频谱重建，不改善分离主指标，应优先考虑：
   - 调损失配比
   - 或继续改结构
   而不是直接替换主线。

### 22. 训练目标若和主评估指标错位，模型会学出“看起来更像”但“不一定分得更开”的结果

现象：

- `ref_film` 在不改损失的情况下，能改善：
  - `loss`
  - `stft_l1`
- 但 `sisdr_db` 反而略差。

影响：

- 说明当前 baseline 只靠波形 L1 + STFT L1 时，更容易朝“重建更像 target”走，不一定朝“分离得更开”走。
- 如果继续只追重建项，后面很可能一直出现“频谱指标更好，但分离主指标不涨”的错觉。

处理：

- 已在训练损失中加入可配置的轻量 `SI-SDR loss`。
- 并且保留了 eval 口径兼容，避免历史 `sisdr_db` 失去可比性。

后续要求：

1. 训练目标发生变化时，要明确区分：
   - 训练用的优化目标
   - eval 用的历史可比指标
2. 如果两者口径不同，必须在报告里写清楚，不能混着解读。

### 23. “loss 有效”与“结构有效”需要做隔离对照，不能一起改完直接宣布胜利

现象：

- 本轮先看到 `ref_film + sisdr001` 的 `sisdr_db` 明显提升。
- 但如果不补 `legacy_bias + sisdr001` 的对照，就无法知道收益到底来自：
  - 新损失
  - 还是新结构

影响：

- 如果不做隔离，很容易把“只是 SI-SDR loss 起作用”误判成“结构升级成功”。
- 后面继续迭代时，会失去对真正有效因素的判断能力。

处理：

- 已补做 `legacy_bias + sisdr001` 的 stage2 同预算对照。
- 结果表明：
  - 单加 SI-SDR loss 确实有帮助；
  - 但 `ref_film + sisdr001` 明显优于 `legacy_bias + sisdr001`；
  - 说明当前收益来自“结构 + 损失”的组合，而不是其中任意一个单独就够。

后续要求：

1. 后面再改模型或损失时，优先一次只动一个主变量。
2. 如果必须同时改两个变量，随后一定补隔离对照，不然结论不够硬。

### 24. 直觉上“更重视 STFT”不等于真能把 STFT 指标救回来

现象：

- 在 `ref_film + SI-SDR loss` 已经有明显提升后，尝试把 `stft_weight` 从 `0.5` 提到 `0.6`。
- 结果两组对照都不是“STFT 稍好一点、其他略波动”，而是四项主指标一起明显变差。

影响：

- 说明当前训练动态不是简单线性关系。
- 不能用“某个指标差了一点，就把对应 loss 权重再加大”这种直觉，替代真实实验。

处理：

- 已完成 `stft=0.6` 的两组正式对照。
- 当前结论是先排除这条方向，不再继续在它上面消耗算力。

后续要求：

1. 以后做权重扫描，优先小步扫，不要一次跨得太大。
2. 若某个方向已经在 1-2 个点上明显整体退化，就及时止损，不继续做同类扩展。

### 25. 小范围权重扫描里，出现“一个候选同时支配另一个候选”时，应尽快收敛主线

现象：

- 在本轮扫描中，`ref_film + sisdr0005` 相对 `ref_film + sisdr001`：
  - `loss` 更低
  - `waveform_l1` 更低
  - `stft_l1` 更低
  - `sisdr_db` 更高

影响：

- 这不是“不同指标各有胜负”的平手状态，而是明确的支配关系。
- 如果此时还继续把两个点都当成同级候选，会让后续主线判断变得拖沓。

处理：

- 已把当前最优平衡点更新为 `ref_film + stft0.5 + sisdr0.0005`。

后续要求：

1. 以后若再次出现这种“一个点支配另一个点”的情况，优先收敛主线，不反复犹豫。
2. 后续新扫描应围绕新最优点做更小范围微调，而不是继续在明显更差的点附近浪费实验预算。

### 26. 有些超参最优点不是“平缓平台”，而是相当尖的局部最优

现象：

- 在 `ref_film + stft0.5` 下，对 `sisdr_weight` 做窄范围复扫后发现：
  - `0.0005` 明显优于 `0.0004`
  - `0.0003` 和 `0.0006` 都明显更差

影响：

- 说明当前最优点附近不是一大片都差不多的平缓区间，而是相对尖的局部最优。
- 如果误以为“差不多都一样”，后续很容易随手换一个邻近值，结果把模型性能 quietly 拉低。

处理：

- 已把 `ref_film + stft0.5 + sisdr0.0005` 确认为当前稳定主候选。

后续要求：

1. 当前阶段不要再随意把 `sisdr_weight` 从 `0.0005` 改开，除非有明确的新实验目的。
2. 如果后面再做微调，应有明确假设，不再做无方向的“顺手试几个邻近值”。

### 27. 在没有真实验证集 manifest 之前，不能把“准备听感验证”误说成“已经做完真实验证”

现象：

- 当前仓库已经有足够的代码和 checkpoint，可导出 A/B 试听包。
- 但还没有正式整理好的真实或近真实验证集 manifest。

影响：

- 如果表述不严谨，容易把“已经把试听包准备好”说成“已经完成真实验证”。
- 这会让阶段结论看起来比实际更靠前。

处理：

- 已新增 A/B 导出脚本并产出 synthetic hard-case 试听包。
- 当前文档明确把这一步表述为：
  - 听感验证准备完成
  - 真实验证尚未完成

后续要求：

1. 后面汇报时，要明确区分：
   - 试听包是否已导出
   - 真实验证集是否已建立
   - 人工听感是否已完成
2. 这三步不要混成一句“已经验证过了”。

### 28. focused fine-tune 若只留下派生 manifest，不记录生成规则，下次几乎无法严谨复刻

现象：

- 当前仓库中已存在：
  - `data/synthetic/train_manifest_clean_plus_music_regression_focus_v1.jsonl`
- 并且已经基于它完成了：
  - `baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_focus_ft1`
- 但当前没有同步找到该 focused manifest 的正式生成脚本或生成说明。

影响：

- 下次即使看到实验产物，也不容易确认这个 manifest 是怎么从默认 train manifest 派生出来的。
- 若想做 `v2`、做更公平对照，或让其他人接手复现，容易直接卡住。

处理：

- 已在日报中补记当前 manifest 的样本规模和分布统计。
- 已把该问题登记为当前接班风险。

后续要求：

1. 以后只要新增派生 manifest，必须同步落一份：
   - 生成脚本
   - 或最少可复现的生成规则说明
2. 不要只留下 `.jsonl` 产物本身。

### 29. 实验产物一旦多起来，目录存在不等于上下文可恢复

现象：

- 当前新增了：
  - `baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_focus_ft1`
  - 对应 eval 目录
  - 对应 focused blind A/B 试听包
- 如果不立即写进总览和日报，下次接手的人只能看到目录名，无法知道：
  - 它是不是主线
  - 它为什么产生
  - 它与上一轮听感反馈是什么关系

影响：

- 目录越多，越容易把“当前候选分支”和“历史残留试验”混在一起。
- 后续判断下一步该做什么时，会浪费时间重新考古。

处理：

- 已补写 focused fine-tune 专题日报。
- 已把该实验和试听包入口登记到 `docs/01_project_overview_and_plan.md`。

后续要求：

1. 新实验一旦确认有信息量，当轮就登记到总览文档。
2. 不要等“以后再补”，否则上下文恢复成本会迅速上升。

### 30. 没有试听条件时，最容易犯的错是继续盲堆新分支，而不先压缩客观不确定性

现象：

- 当前 `cpm_focus_ft1` 相对 `ref_film_sisdr0005` 在平均指标上略有提升。
- 但自动对比显示，它仍然是明显的“有赢有输”分支：
  - 全验证集 improved: `142`
  - regressed: `149`
  - near tie: `221`

影响：

- 如果在这种状态下继续连续堆很多 `ft2 / ft3 / ft4`，很容易让实验树快速膨胀。
- 但因为没有试听，主观层面的判断仍然缺口很大，最后会出现“分支越来越多，结论却没有变硬”的情况。

处理：

- 已补双 checkpoint 自动对比脚本：
  - `scripts/eval/compare_checkpoints_on_manifest.py`
- 并已实际产出：
  - `reports/eval/compare_ref_film_sisdr0005_vs_cpm_focus_ft1/`
  - `reports/eval/compare_ref_film_sisdr0005_vs_cpm_focus_ft1_clean_plus_music/`

后续要求：

1. 没有试听条件时，优先补客观分组对比和可复现 manifest，而不是快速增加新训练分支。
2. 若新分支没有形成更强的客观支配关系，就不要轻易继续扩展更多近邻实验。

### 31. 即使 recipe 配额相同，focused manifest 的 temporal pattern 分布变化也足以显著改变结果

现象：

- 当前 `regression_focus_v1` 与 `recipe_focus_v2` 的 recipe 总配额都为 `364` 条，且各 recipe 数量对齐。
- 但两者的 temporal pattern 分布并不相同。
- 在保持相同 warm-start 和训练预算的前提下，`ft2` 相对 `ft1` 的表现出现了明显变化：
  - overall `sisdr_db` 更好
  - `clean_plus_music` 更好
  - `hard_speech` 副作用更小

影响：

- 说明 focused 实验里，不能把“recipe 配比”当成唯一主变量。
- 即使 recipe 数量完全一样，sample 级别的时序结构分布不同，也会把结果推到另一边。

处理：

- 已把 `recipe_focus_v2` 和对应 `ft2` 结果登记为正式日报与总览。

后续要求：

1. 以后描述 focused manifest 时，至少同时记录：
   - recipe 分布
   - temporal pattern 分布
2. 不要只写“这是 clean_plus_music focus”，否则信息不够，容易误判实验变量。

### 32. 到了近邻微调后期，只看均值小涨就继续开新分支，很容易进入“平台区假进步”

现象：

- 在 `ft2` 之后，又做了一轮更保守的 `ft3`。
- `ft3` 的整体均值确实比 `ft2` 略好：
  - `sisdr_db`: `-7.947635 -> -7.926801`
- 但逐样本对比只有：
  - improved: `114`
  - regressed: `105`

影响：

- 这类结果说明模型可能已经进入平台区附近。
- 如果继续只因为“均值又涨了一点点”就往下开 `ft4 / ft5`，很容易把实验树越开越长，但结论并不变硬。

处理：

- 已把 `ft3` 记录为可保留但不主推的近邻点。

后续要求：

1. 近邻微调若没有形成更明显的分布支配关系，应优先停下来，转向听感验证。
2. 不要把“均值略涨”自动等同于“值得继续往下滚很多版”。

### 33. blind 听评如果没有结构化标签，后续很难把主观反馈和模型问题类型对齐

现象：

- 早期 blind 包中的 `listening_sheet.csv` 更偏自由备注。
- 这样虽然能记录主观看法，但很容易出现：
  - 描述词不统一
  - 同一问题被不同说法重复表述
  - 后续难以统计“到底是源保留差，还是干扰泄漏高，还是伪影重”

影响：

- 主观反馈会变得零散，难以和后续模型迭代形成闭环。

处理：

- 已把 blind 听评标准改成：
  - `better_output`
  - `source_retention`
  - `interference_leak`
  - `volume_fluctuation`
  - `artifact`
  - `decision_tags`
- 并同步更新了导出脚本。

后续要求：

1. 后面新的 blind 包，统一使用这套结构化表。
2. 若旧包还需要继续听，建议也优先重新导出成新格式，避免混用两套记录口径。

### 34. blind 包里其实已经带有真实模型标签，GUI 若直接读 `summary.json` 会破坏盲测

现象：

- 当前 blind listening pack 虽然把音频文件导出成了 `candidate_a.wav / candidate_b.wav`。
- 但同目录下的 `summary.json` 仍然记录了：
  - `label_a`
  - `label_b`
  - checkpoint 路径
  - 每条样本的真实 comparison 字段

影响：

- 如果后续写 GUI 或其他辅助工具时，直接把 `summary.json` 当作主界面数据源，就会在 blind 听评时意外看到真实身份。
- 这样看起来“文件名是盲的”，实际上流程已经不盲了。

处理：

- 本轮新增的 `scripts/eval/listening_pack_gui.py` 默认只读取：
  - `listening_sheet.csv`
  - `listening_rubric.json`
  - 样本目录中的音频文件
- 不把 `summary.json` 的真实标签直接展示到界面里。

后续要求：

1. 后面凡是 blind 包消费工具，都优先走 `listening_sheet.csv` 这条盲态入口。
2. 若确实需要解盲，应显式点击或单独走解盲流程，不要和评分界面混在一起。

### 35. 听评 GUI 里的“峰值统一拉伸”如果按单文件分别执行，会悄悄改掉 A/B 的真实相对差异

现象：

- 在 `scripts/eval/listening_pack_gui.py` 的早期实现中，播放选项里的归一化逻辑是：
  - 先读取当前单个文件
  - 再把这个文件自己的峰值单独拉到目标值
- 这和实际盲听想要的口径不一致。

影响：

- 同一样本中的：
  - `candidate_a`
  - `candidate_b`
  - `mixture`
  - `target`
  - `reference`
  之间，本来应该保留的相对响度和抑制强弱差异，会被单文件拉伸部分抹平。
- 这样更容易出现：
  - “A/B 听起来差不多”
  - 或“某条本来更安静但也更薄的输出，被拉高后显得没那么弱”

处理：

- 已将 GUI 修正为：
  - 同一样本目录内共用一个播放增益
  - 该增益按整组文件中的最大峰值计算
- 这与导包脚本里“同一样本共享导出增益”的思路保持一致。

后续要求：

1. 后面凡是再做关键样本复核，优先使用修正后的“同一样本共享增益”口径。
2. 对此前在旧口径下得到的主观结论，尤其是“谁更稳 / 谁泄漏更重 / 谁波动更明显”这类细判断，要保留一点谨慎。

### 36. 少量 synthetic 听评样本的 `target.wav` 本身可能带有门限式截断痕迹，会污染主观判断

现象：

- 在复核 `clean_plus_music` focused 包时，用户明确指出：
  - `val_000036`
  - `val_000454`
  的 `target.wav` 中间疑似存在门限截断和放开瞬间的明显跳变。

影响：

- 这类样本即使 A/B 本身没有明显差异，也会因为 target 真值本身不自然，降低整条样本的可判性。
- 若不单独标记，后续很容易把“样本本身难评”误判成“模型完全没差异”。

处理：

- 已将这两条样本视作“可参考但带评估噪声”的样本，不再把它们当作最干净的主观证据。

后续要求：

1. 后续若继续做关键样本复核，优先记录这类“样本本身有问题”的备注。
2. 若类似现象继续出现，应回查 synthetic 生成逻辑，而不是只盯模型输出。

### 37. Git 状态和磁盘文档如果不一起维护，很容易出现“仓库已变化但总览仍停在旧时点”

现象：

- 本轮恢复时，Git 真实状态已经存在提交历史，`HEAD` 也已有具体 commit。
- 但总览、踩坑和日报中的部分表述仍停留在：
  - “当前仓库尚无任何提交”
  - “当前仓库还没有任何提交历史”

影响：

- 下次接手的人如果只看文档，不看 Git 事实，很容易误判当前仓库阶段。
- 这种偏差虽然不影响训练代码本身，却会让“当前该做文档修正还是做新实验”这个判断顺序变乱。

处理：

- 已将核心文档中的 Git 事实更新为当前状态。
- 已明确补充协作边界：
  - Git 由用户手动维护提交记录；
  - 助手只把 Git 当作状态核对和恢复辅助工具。

后续要求：

1. 以后只要引用 Git 状态，尽量写成“当前观察事实”，不要把某一时刻的临时状态写成长期结论。
2. 每次恢复上下文时，除读文档外，至少补看一次：
   - `git status --short`
   - `git log --oneline -n 3`
3. 若文档中的 Git 表述已过期，应优先修正文档，再继续推进其他任务。

### 38. 客观上大幅领先的候选，不等于修正后 GUI 口径下也会被人耳稳定选中

现象：

- `ref_film + stft0.5 + sisdr0.0005` 在客观指标上曾一度收敛为当前最强候选。
- 但在 `legacy stage2 vs ref_film_sisdr0005` 的 blind A/B 主观复核里，解盲后结果为：
  - `legacy_stage2`: `7`
  - `ref_film_sisdr0005`: `1`
  - `tie`: `1`
  - `uncertain`: `3`

影响：

- 说明当前这类 synthetic 客观增益，还不能直接等价理解成“耳朵会更喜欢”。
- 如果只因为客观指标领先就替换默认主线，实际很可能把一个“更激进但不够稳”的模型推到前面。

处理：

- 已将默认主线保持为 `legacy stage2`。
- `ref_film_sisdr0005` 当前改回：
  - 客观候选分支
  - 听评和真实验证对照分支

后续要求：

1. 后面凡是“客观上更强但主观未过关”的候选，都不要直接升默认主线。
2. 若想继续推进这类候选，优先补：
   - 更真实样本
   - 或更聚焦的不确定样本复核
3. 结论里要明确区分：
   - 客观最优候选
   - 当前默认主线

### 39. 评估与听评导出若把仓库内路径写成绝对路径，工作目录一改名就会产生恢复噪声

现象：

- 当前恢复时发现，多份导出产物仍写着旧工作目录：
  - `reports/eval/*/listening_results_summary.json` 的 `pack_dir`
  - `reports/eval/compare_*/summary.json`
  - `reports/eval/compare_*/per_sample_metrics.jsonl` 的 `metadata_path`
- 这些文件本身还在，但文本里记录的路径已经漂到旧目录名 `workdir-4-1`。

影响：

- 下次接手的人如果只看报告 JSON，很容易误以为当前产物放在旧目录，增加恢复噪声。
- 这类问题和代码逻辑无关，但会直接削弱“看报告就能恢复上下文”的可靠性。

处理：

- 已将后续默认口径改为：
  - 仓库内路径优先写仓库相对路径
  - 仅在仓库外路径无法相对化时，才回退为绝对路径
- 已修正：
  - `SyntheticTSEDataset`
  - `scripts/eval/listening_pack_gui.py`
  - `scripts/eval/compare_checkpoints_on_manifest.py`
  - `scripts/eval/export_ab_listening_pack.py`
  - `scripts/eval/export_ab_inference_from_manifest.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/data/build_recipe_focused_manifest.py`

后续要求：

1. 以后新增报告 JSON 时，仓库内路径默认不要直接写 `str(path.resolve())`。
2. 若历史产物里仍保留旧绝对路径，应把它视为“历史记录字段”，不要当作当前真实路径来源。

### 40. 当前训练分布仍缺少混响 / RIR realism，near-real 一上轻微混响就更容易暴露“伪影像目标”的问题

现象：

- 设计稿里早就把：
  - 轻混响
  - RIR 卷积
  写成了后续 realism 增强项。
- 但当前代码实现中，还没有真正落地这类增强。
- 在 `near_real_v1` blind 听评里，用户新给出的主观判断是：
  - 对输入的混响处理存在问题；
  - 有可能将处理中间过程产生的伪影误当作目标音频。
- 这条判断在样本级上也有支撑：
  - `near_real_0008`
  - `near_real_0010`
  的 target absent 场景中，A/B 都出现了目标样瞬态；
  - `near_real_0009` 的轻微混响说话素材中，两边都出现了泄漏和较强伪影。

影响：

- 当前问题已经不只是“整体客观指标是否更高”，而是：
  - 模型对混响尾音、拖尾和房间染色不够稳；
  - target absent 时可能会吐出一点像目标的东西；
  - 处理中间伪影可能被误保留成“像目标的成分”。
- 如果不先补这类 realism，继续只在 dry synthetic 上扫近邻 checkpoint，主观问题大概率还会反复出现。

处理：

- 已将 near-real 听评结果和这一判断补记到日报：
  - `reports/daily/2026-03-17_near_real_listening_review.md`
- 已把下一阶段优先级更新为：
  - 先补混响 / 尾音拖尾 realism
  - 再重点看 target absent guardrail

后续要求：

1. 下一轮若继续改数据，优先加轻混响 / RIR / 拖尾类增强，而不是先扫更多近邻 loss 权重。
2. 下一轮若继续做主观验证，必须单独保留：
   - raw target only
   - target absent
   - 轻微混响 speech interference
   这三类样本，避免又被总体均值盖掉。
3. 当前已在 synthetic 生成器里补了可选轻混响入口，但默认仍关闭；真正开始用它前，应先做小规模 probe，避免直接破坏历史主线的可比性。

### 41. reverb probe 若直接复用默认 synthetic 输出路径，会污染主线数据集边界

现象：

- 当前主线 synthetic 数据固定使用：
  - `data/synthetic/train_manifest.jsonl`
  - `data/synthetic/val_manifest.jsonl`
- reverb probe 若也直接写这两个默认文件，会把 side experiment 的数据静默覆盖到主线入口上。

影响：

- 后续训练、评估或 compare 脚本可能在不知情的情况下吃到 probe 数据，而不是默认主线数据。
- 这类错误不会像崩溃那样立刻暴露，但会让实验结论和目录名逐渐对不上。

处理：

- 已在 `scripts/data/build_synthetic_dataset.py` 中补入 `--output-tag`。
- 当前 probe 数据改为写到：
  - `data/synthetic/*_{tag}/`
  - `data/synthetic/*_manifest_{tag}.jsonl`
  - `data/synthetic/summary_{tag}.json`

后续要求：

1. 任何非主线 synthetic 数据都必须使用 `--output-tag` 隔离落盘。
2. 主线默认 manifest 只保留给当前默认数据分布，不拿来承载 side experiment。

### 42. 把 target 与 speech 干扰同时做轻混响，不等于更接近 near-real；首轮 joint reverb probe 反而几乎全面回退

现象：

- 首轮 small probe `legacy_reverb_probe_v1` 使用：
  - `target_reverb_prob=0.35`
  - `speech_reverb_prob=0.45`
  - train / val：`256 / 64`
- 结果相对 `legacy stage2` 为：
  - 默认 val：`avg_sisdr_delta_db = -0.264`
  - probe val：`avg_sisdr_delta_db = -0.194`
- 且回退不是只集中在一两个角落，而是大多数 recipe / pattern 都没有占优。

影响：

- 说明“target 和 speech 一起加轻混响”这条最直观的 realism 改法，当前更像是在伤害 dry target 保真，而不是稳定修正 near-real 暴露的问题。
- 如果不先止损，后面继续沿这条线加规模，只会把算力花在已知不稳的方向上。

处理：

- 已保留 `legacy_reverb_probe_v1` 的训练、评估和 near-real blind 包产物，作为反例参考。
- 当前不再沿这条 joint reverb 方向继续放大训练规模。

后续要求：

1. 若继续做 reverb realism，优先先隔离 speech-like interference 侧，而不是再次一起改 target。
2. `legacy_reverb_probe_v1` 当前只保留为反例和回看材料，不再视作积极候选。

### 43. 即使把轻混响限制到 speech-like interference，small probe 也不会自动转正；仍需 near-real 人听把关

现象：

- 第二轮 `legacy_speechreverb_probe_v2` 改为：
  - `target_reverb_prob=0.0`
  - `speech_reverb_prob=0.55`
  - train / val：`256 / 64`
- 它相对 `legacy_reverb_probe_v1` 明显更稳，但相对 `legacy stage2` 仍为：
  - 默认 val：`avg_sisdr_delta_db = -0.183`
  - probe val：`avg_sisdr_delta_db = -0.195`
- probe 集上虽有一些方向性改善：
  - `target_clean_speech`: `+0.015 dB`
  - `target_clean_plus_music`: `+0.033 dB`
  但整体平均仍未转正。

影响：

- 说明“只给 speech 干扰加轻混响”更接近当前问题，但仍不足以仅凭 synthetic 指标就宣布有效。
- 如果这时直接扩到更大规模训练，仍有较大概率把一个“方向更对但证据还不硬”的分支提前放大。

处理：

- 已导出：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`
- 当前把它视作唯一保留的 reverb realism 候选，等待 near-real 人工听评。

后续要求：

1. 下一步人工优先听 `legacy stage2 vs legacy_speechreverb_probe_v2` 这包 near-real blind A/B。
2. 若 near-real 仍不占优，则先停止继续加大 reverb 训练预算，回到更细的 realism / guardrail 方案设计。

### 44. 只给 speech-like interference 加轻混响，可能不会变成“更稳的 near-real”，而会先冒出“电话音 / 带宽缺失感”

现象：

- `legacy_speechreverb_probe_v2` 的 near-real blind 听评现已完成。
- 解盲后的真实偏好为：
  - `legacy_stage2`: `1`
  - `legacy_speechreverb_probe_v2`: `0`
  - `tie`: `8`
  - `uncertain`: `1`
- 用户新增的关键主观判断是：
  - 这轮伪影更像“丢失了某些频率”
  - 听感接近“降低采样率”或“电话机里那种感觉”

影响：

- 这说明当前问题不只是：
  - 混响没处理好
  - 或单纯有残余泄漏
- 还包括一种更像“频带被削窄 / 高频或某些共振段被吃掉”的失真。
- 这类失真很容易在均值型 synthetic 指标里只表现成“小退步”或“看起来差不多”，但人耳会明显觉得不自然。

处理：

- 已把这轮主观结果补记到：
  - `reports/daily/2026-03-17_reverb_probe_followup.md`
- 当前不继续沿 `legacy_speechreverb_probe_v2` 直接放大训练规模。

后续要求：

1. 若后续继续做 realism 方向，优先补“频带缺失 / 电话音”诊断，而不是先继续抬 reverb 概率。
2. 后续客观分析不应只看 SI-SDR / L1；应增加更能暴露频带收窄的频谱侧检查。

### 45. “电话音 / 降采样感”未必表现成简单的全局高频均值塌陷，更可能是局部频带或清辅音瞬态被削掉

现象：

- 针对 near-real blind 包，已补一版诊断脚本：
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
- 首轮分析表明：
  - `legacy_speechreverb_probe_v2` 并没有稳定表现成“所有样本都更低的全局高频占比”
  - 但在 `near_real_0005`、`near_real_0007` 等样本上，仍能看到：
    - `upper_vs_mid` 明显下降
    - `frame_upper_share_p90` 明显下降
- 这与人耳听到的“电话音”并不矛盾，因为它更像：
  - 局部频带被削窄
  - 清辅音、吹气声或高频边缘瞬态被压掉

影响：

- 如果后续只盯“全局高频能量均值”或简单 rolloff，很可能漏掉最接近人耳感受的那部分失真。
- 这类失真在主观上很明显，但在均值型指标里容易只表现成“小变化”。

处理：

- 已把诊断脚本加入仓库，并实际跑在：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/`

后续要求：

1. 后续若继续做这类诊断，优先同时看：
   - `rolloff`
   - `upper_vs_mid`
   - `frame_upper_share_p90`
2. 不要把“没有明显全局低通”误判成“没有电话音式失真”。

### 46. “电话音”里最伤耳朵的部分，常常是高频瞬态相对中频被削掉；只看全局频带仍然不够

现象：

- 已新增：
  - `scripts/eval/analyze_listening_pack_transients.py`
- 该脚本以 mixture 的高频瞬态帧为锚点，对比 candidate 在这些帧上的：
  - `presence` 频段保留
  - 相对 `mid` 频段的保留差
- 首轮结果表明：
  - `legacy_speechreverb_probe_v2` 在 `near_real_0005 / 0007 / 0010` 上仍会被标成更 transient-lossy
  - `legacy_reverb_probe_v1` 的瞬态缺失问题更广、更重

影响：

- 这进一步说明，人耳听到的“电话音”很可能不是纯带宽问题，而是：
  - 清辅音
  - 吹气声
  - 高频边缘瞬态
  在相对中频的保留上被削弱了。
- 如果后续只做带宽均值检查，仍然可能漏掉这类最接近主观听感的问题。

处理：

- 已将该脚本实际跑在两套 near-real blind 包上。
- 当前这类瞬态缺失诊断，已成为后续 realism 方向的固定辅助检查项。

后续要求：

1. 后续若继续做 candidate 对比，至少同时跑：
   - `analyze_listening_pack_bandwidth.py`
   - `analyze_listening_pack_transients.py`
2. 若两者都指向同一侧“更窄带 / 更 transient-lossy”，再把它视作更强的客观证据。

### 47. 把“电话音 / 瞬态缺失”从诊断推进到训练钩子时，`sample_rate` 不能再靠 loss 内部写死

现象：

- 本轮已在 baseline loss 中新增：
  - `transient_presence_l1_loss`
  - 以及训练脚本入口 `--loss-transient-weight`
- 该 loss 需要把 `3k-8k`、`0.8k-3k` 这类频带边界映射到 STFT bin。
- 如果直接在 loss 里写死 `16000 Hz`，短期虽然和当前主线数据一致，但会把“当前数据约束”偷偷变成“代码永久假设”。

影响：

- 当前项目主数据确实是 `16k`，所以问题不会立刻炸出来。
- 但一旦后续 near-real 资产或其他评估入口改采样率，loss 里的频带解释就会静默漂移，变成很难察觉的错位。

处理：

- 已把 `sample_rate` 显式写入 `loss_config`，并由：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  传到 `compute_losses(...) / transient_presence_l1_loss(...)`
- 已实际跑通：
  - `max_steps=1` transient smoke training
  - smoke checkpoint eval

后续要求：

1. 以后凡是涉及“Hz 到 bin”的损失或诊断，都优先从配置或数据入口显式传 `sample_rate`。
2. 不要因为当前主线全是 `16k`，就把采样率约束偷偷散落成多个硬编码常量。

### 48. default 全分布上直接加 transient loss，很容易先伤 guardrail，再换来局部场景收益

现象：

- 本轮基于 `legacy stage2` 做了两轮 warm-start transient probe：
  - `transient_weight=0.005`
  - `transient_weight=0.002`
- 两轮都会明显压低 synthetic val 上的 `transient_presence_l1`：
  - `0.7489 -> 0.5665`
  - `0.7489 -> 0.5788`
- 但在默认全分布 compare 上，`SI-SDR` 仍分别回退：
  - `-0.412 dB`
  - `-0.314 dB`

影响：

- 这说明“更像在保高频瞬态”不等于默认主线就更稳。
- 当前默认分布里，transient loss 更容易先伤：
  - `target_only`
  - `target_hard_speech`
  - `target_hard_plus_music`
- 而局部收益更集中在：
  - `target_clean_speech`
  - 以及部分 `target_absent_head / absent_tail`

处理：

- 已把较保守的 `legacy_transient_probe_v2 (0.002)` 保留下来。
- 但当前不把“直接在默认分布上加 transient loss”视为安全主线升级。

后续要求：

1. 若继续推进 transient loss，优先把它当作候选分支，而不是默认主线改动。
2. 判断是否值得继续，必须同时看：
   - focused recipe 收益
   - `target_only / hard_speech` guardrail 代价
   - near-real blind 听评

### 49. blind 包诊断脚本里的 `file_a / file_b` 计数是候选文件计数，不是模型标签计数；必须结合 `blind_key.json` 解码

现象：

- `analyze_listening_pack_bandwidth.py` 和 `analyze_listening_pack_transients.py` 的 summary 默认输出：
  - `file_a`
  - `file_b`
  - `tie`
- 但 blind 包里 `candidate_a / candidate_b` 与真实模型标签的对应关系会按样本随机打乱。

影响：

- 如果直接把：
  - `file_a: 4`
  - `file_b: 4`
  这种 summary 当作“两个模型各输 4 次”，结论可能是错的。
- 本轮 `legacy_transient_probe_v2` 的 near-real 包就是这样：
  - summary 表面上只是 `file_a: 4 / file_b: 4 / tie: 2`
  - 但结合 `blind_key.json` 解码后，真实结果是：
    - `legacy_transient_probe_v2` 被标成更 transient-lossy `7` 条
    - `legacy_stage2` 仅 `1` 条

处理：

- 当前这轮分析已补做解码，并把真实标签结论写入日报与总览。

后续要求：

1. 以后凡是 blind 包自动诊断，默认先看 summary，再必须结合 `blind_key.json` 解码成真实标签统计。
2. 没做解码前，不要直接用 `file_a / file_b` 计数下模型级结论。

### 50. 听评表里的空白字段不一定代表“无问题”；如果这轮打分策略是“只在差异明显时才填写”，就不能把空白直接当 `none`

现象：

- 本轮 `legacy_transient_probe_v2` 的 near-real 听评里，用户明确采用的是：
  - 只有存在明显差异时，才填写主要差异来源；
  - 其余字段保持未填。
- 因此 `listening_sheet.csv` 中大量空白字段，语义上更接近：
  - “未特别标注”
  - 而不是“明确没有问题”。

影响：

- 如果后续把这些空白字段直接按：
  - `none`
  - 或“没有 artifact / 没有 leak”
  去统计，就会高估这轮结构化标签的确定性。

处理：

- 本轮对结果解读时，已只把：
  - `better_output`
  - 明确填写的 `source_retention / interference_leak / artifact`
  - 以及自由备注
  当作有效证据。

后续要求：

1. 以后汇总这类 listening sheet 时，必须先确认“空白”的语义是：
   - 未评
   - 还是等价于 `none`
2. 如果口径是“只标明显差异”，最终结论里应优先写成：
   - “明确标出的差异是什么”
   - 而不是把未填项也硬转成负面或正面统计。

### 51. 把 interference selector 缩到 music-only，容易出现“局部 metric 更漂亮，但整体比上一版更差”的过拟合假象

现象：

- `legacy_transient_leakguard_probe_v2_musiconly` 只对：
  - `target_music`
  - `target_clean_plus_music`
  - `target_hard_plus_music`
  施加 interference selector。
- 它在默认 synthetic val 上相对 `legacy stage2` 仍有：
  - `avg_sisdr_delta_db = +0.665876`
- 同时 `interference_projection_ratio` 进一步压到：
  - `0.0319`
- 但相对上一版 `legacy_transient_leakguard_probe_v1` 却变成：
  - `avg_sisdr_delta_db = -0.183896`
  - 并在 `target_only / hard_speech / clean_speech` 等非 music 主体上大面积回退。

影响：

- 这说明“leak metric 更低”不等于“当前 candidate 更稳”。
- 当 selector 缩得过窄时，模型会更像在针对某一类干扰专门收缩，而不是整体 trade-off 更好。

处理：

- 当前已明确不保留 `legacy_transient_leakguard_probe_v2_musiconly` 作为后续主候选。

后续要求：

1. 后面只要改 selector 范围，默认必须同时看：
   - 相对 `legacy stage2`
   - 相对上一版 objective-only 最强候选
2. 不能只因为某个 focused metric 更好，就把更窄 selector 当成自然升级。

### 52. 单纯下调 interference loss 权重，虽然能减 residual-heavy，但不等于 near-real 风险就同步转正

现象：

- `legacy_transient_leakguard_probe_v3_w0005` 将 `interference_weight` 从：
  - `0.01 -> 0.005`
- 相对 `legacy_transient_leakguard_probe_v1`，它在 near-real trade-off 上确实收回了一部分 residual-heavy 问题：
  - `more_residual_heavy` 从 `6` 条降到 `1` 条
  - `residual_output_share` 均值从 `0.679 -> 0.654`
- 但同时它也带来：
  - `retention_minus_leak_db` 从 `28.938 -> 28.585`
  - 带宽收窄计数从 `2 -> 3`
  - `more_interference_leaky` 仍是 `5` 条

影响：

- 这说明“把 loss 调轻一点”更像是在移动 trade-off，而不是自动修复根因。
- 如果没有同时盯 leakage、带宽和 retention-minus-leak，只看 residual share，很容易误判 `v3` 已经更稳。

处理：

- 当前已把 `legacy_transient_leakguard_probe_v3_w0005` 记录为“更保守的参考分支”，但不替代 `v1`。

后续要求：

1. 后续若继续调 interference 权重，必须把以下指标成组看：
   - `interference_projection_ratio`
   - `residual_output_share`
   - `retention_minus_leak_db`
   - near-real 带宽 / 瞬态诊断
2. 不要把“residual 更轻”单独当作升级依据。

### 53. 把 leak-guardrail 的 interference selector 收窄到 speech-only recipes，不等于 speech-only near-real 回退就会自动修好

现象：

- 本轮新增 `legacy_transient_leakguard_probe_v4_speechfocus_ft1`：
  - 从 `legacy_transient_leakguard_probe_v1` warm-start；
  - 保留 `interference_weight = 0.01`；
  - 但把 `interference_focus_recipes` 从全 interference recipe 收窄到：
    - `target_clean_speech`
    - `target_hard_speech`
- 它在 synthetic 默认 val 上相对 `legacy stage2` 反而更强：
  - `avg_sisdr_delta_db = +0.969665`
- 相对 `legacy_transient_leakguard_probe_v1` 也仍是正增益：
  - `avg_sisdr_delta_db = +0.119893`

影响：

- 如果只看 synthetic 总体均值，很容易误判成：
  - “既然 speech-focused 更强，那 speech-only near-real 应该也更稳”
- 但实际 near-real 自动诊断并没有这么走：
  - `more_interference_leaky` 仍是 `5` 条；
  - `better_retention_minus_leak` 仍是 `2` 条，落后 `legacy stage2` 的 `3` 条；
  - `near_real_0003 / 0004` 这两条 speech-only 回退点仍未修正；
  - `target_only / target_singing_vocal` 相对 `v1` 还开始出现 guardrail 回退。

处理：

- 已将该分支正式记录为：
  - `reports/daily/2026-03-17_speech_only_leakguard_followup.md`
- 当前把它定位为：
  - 有价值的诊断性 follow-up
  - 但不升级为新的主候选，也不排到 `v3_w0005` 前面

后续要求：

1. 后续若继续围绕 speech-only 问题做实验，不能只靠“把 selector 再收窄一点”作为默认思路。
2. 必须继续同时看：
   - `near_real_0003 / 0004` 这类关键 speech-only 样本；
   - `more_interference_leaky`
   - `better_retention_minus_leak`
   - `target_only / singing` guardrail 代价
3. 若目标真的是修 speech-only near-real 回退，下一步更应该考虑：
   - 更贴近 residual / leak 机制的约束
   - 或 target absent / speech absent guardrail
   - 而不是继续单改 selector 覆盖范围。

### 54. 直接把 target-absent guardrail 权重拉高，虽然能明显压低 absent leakage，但很容易把模型推成 residual-heavy / over-suppressed

现象：

- 本轮已把 `target_absent_intervals` 正式接入训练 / 评估管线，并新增：
  - `absent_interval_l1`
- 基于这条入口，新增 `legacy_transient_leakguard_probe_v5_absentguard_ft1`：
  - 从 `legacy_transient_leakguard_probe_v1` warm-start；
  - 保留 `transient_weight = 0.002` 与 `interference_weight = 0.01`；
  - 新增 `absent_weight = 20`；
  - focused 在：
    - `target_clean_speech`
    - `target_hard_speech`
    - `target_clean_plus_music`
    - `target_hard_plus_music`
  - pattern 限于：
    - `target_absent_head`
    - `target_absent_tail`
    - `target_intermittent`
- 它在 synthetic 上确实把 absent leakage 压得很明显：
  - `absent_interval_l1: 0.00010835 -> 0.00001870`
- 但同时：
  - 默认 val 相对 `legacy_transient_leakguard_probe_v1` 变成 `avg_sisdr_delta_db = -0.662080`
  - focused absent-guard recipes 上也仍为 `avg_sisdr_delta_db = -0.894569`

影响：

- 如果只看 `absent_interval_l1`，很容易误判成：
  - “target-absent guardrail 已经修好了”
- 但 near-real 自动诊断给出的实际信号是：
  - `better_source_retention = legacy_stage2 7`
  - `more_interference_leaky = legacy_stage2 8`
  - `more_residual_heavy = legacy_transient_leakguard_probe_v5_absentguard_ft1 7`
- 也就是：
  - 干扰确实压得更狠；
  - 但 target capture 也一起被压掉；
  - 最终变成更明显的 residual-heavy / over-suppressed 版本。
- 关键回退样本包括：
  - `near_real_0003`
  - `near_real_0005`
  - `near_real_0007`
  - `near_real_0010`

处理：

- 已将该分支正式记录为：
  - `reports/daily/2026-03-18_absent_guardrail_probe.md`
- 当前把它定位为：
  - 有价值的机制探针
  - 但不升级为新的 objective-only 候选

后续要求：

1. 以后若继续做 target-absent guardrail，不能只盯 `absent_interval_l1` 单指标。
2. 必须继续同时看：
   - 默认 val 相对 `v1` 的退化
   - near-real `better_source_retention`
   - near-real `more_residual_heavy`
   - `near_real_0003 / 0004 / 0005 / 0007 / 0010`
3. 当前这条线只允许做更保守的小步 follow-up：
   - 更低 absent weight
   - 更窄 selector
   - 不再直接沿 `absent_weight = 20` 扩训。

### 55. `.gitignore` 如果按目录整块屏蔽生成产物，容易把恢复关键摘要一起挡掉

现象：

- 当前公开仓库最初的 ignore 规则更偏“公开边界安全”，但对“误删后最大可恢复目标”还不够细：
  - `experiments/*`
  - `reports/eval/`
  这类整块忽略会把以下小文件一起挡掉：
  - `train_summary.json`
  - `eval_summary.json`
  - compare `summary.json`
  - blind pack `README.md`
  - `blind_key.json`
  - `sample_meta.json`

影响：

- 这些文件虽然是生成物，但通常：
  - 体积很小
  - 不含音频本体
  - 正是恢复实验配置、评估结论和 blind pack 组成的关键元数据
- 如果把它们和 checkpoint / wav 一起整体忽略，仓库会丢掉一整层可恢复信息。

处理：

- 已把 `.gitignore` 调整为“重资产继续本地，结构化摘要恢复可跟踪”：
  - `experiments/**/train_summary.json` 重新保持可跟踪
  - `reports/eval/**` 下的 `eval_summary.json`、`summary.json`、`README.md`、`blind_key.json`、`sample_meta.json` 重新保持可跟踪
- 仍继续留本地的内容包括：
  - 音频本体
  - checkpoint / `.pt`
  - synthetic 生成音频
  - 指向本地/非公开资产的 manifest

后续要求：

1. 以后审 ignore 规则时，不能只问“会不会泄露”，还要同时问“删盘后还能恢复到什么程度”。
2. 目录里若同时存在大文件和关键摘要，应优先用“忽略重资产 + 反向放行摘要”的写法，而不是整目录屏蔽。
3. 每次改完 `.gitignore`，至少补看一次 `git status --short --ignored`，确认：
   - 摘要文件没有被误伤
   - 重资产仍留在本地边界内

### 56. near-real trade-off 只看整包均值，很容易把“某个桶明显更好、另一个桶明显更差”的候选误判成中庸或稳定

现象：

- `analyze_listening_pack_tradeoff.py` 早期 summary 主要给：
  - 整包计数
  - 整包 decoded means
- 这足以看大方向，但不够直接回答：
  - `speech-only near-real` 是不是修好了
  - `target absent` 的收益到底落在哪个桶
  - 某个 candidate 的正收益是不是只是被 `music` 或 mixed bucket 拉起来

影响：

- 如果只看整包均值，很容易把：
  - `legacy_transient_leakguard_probe_v1`
  - `legacy_transient_leakguard_probe_v3_w0005`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1`
  这些分支之间真正的症状差异压平。
- 结果就是：
  - 某些“只在 music 桶更好”的版本会看起来像整体候选；
  - 某些“只在 target-absent speech 桶更强，但会压坏 raw-only”的版本，也会被误读成只是“整体更 residual-heavy”。

处理：

- 已给 `scripts/eval/analyze_listening_pack_tradeoff.py` 增加：
  - `scenario_groups`
  - `target_status_groups`
  - `interference_profile_groups`
  - `target_interference_bucket_groups`
- 已实际在 `v1 / v3_w0005 / v4_speechfocus_ft1 / v5_absentguard_ft1` 的 near-real blind 包上重跑。

当前新增结论：

1. `legacy_transient_leakguard_probe_v1` 的主要收益集中在：
   - `target_present__music`
   - `target_present__music_plus_speech`
2. 当前真正没修好的主缺口更明确地落在：
   - `target_present__speech`
   - `target_present__none`
3. `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 没有修好 `target_present__speech`
4. `legacy_transient_leakguard_probe_v5_absentguard_ft1` 的收益主要落在：
   - `target_absent__speech`
   但代价分散到：
   - `target_present__none`
   - `target_present__music`
   - `target_present__music_plus_speech`

后续要求：

1. 以后看 near-real trade-off，不能只盯整包均值。
2. objective-only 候选默认至少同时过这三类桶：
   - `target_present__speech`
   - `target_present__none`
   - `target_absent__speech`
3. 若某个版本只在 `music` 桶变强，但 `speech` 或 `raw-only` 桶继续输给 `legacy_stage2`，不能把它误判成“下一主候选”。

### 57. 即使已经按桶看 near-real，如果 gate 规则仍停留在自然语言里，后续还是会反复回到“这个候选整体看着还行”的模糊判断

现象：

- 在补了 `target_interference_bucket_groups` 之后，已经能更清楚地看见：
  - `v1` 的收益主要集中在带 `music` 的桶；
  - `v3 / v4` 主要卡在 `target_present__speech`；
  - `v5` 主要卡在 `target_present__speech` 与 `target_present__none`
- 但如果这些结论只写在日报里，后续仍很容易再次退回到：
  - 看整包 summary
  - 口头回忆“上次好像是这个桶有问题”
  - 再重新人工解释一次

影响：

- 同样的 near-real 放行条件会被反复人工重述。
- 很容易出现：
  - 某个分支已经明显卡在 `speech-only target-present`
  - 但因为整包上还有别的亮点，又被误当成“可以继续保留的主候选”

处理：

- 已新增：
  - `scripts/eval/gate_near_real_tradeoff.py`
- 当前已把以下三类桶正式固化为 hard gate：
  - `target_present__speech`
  - `target_present__none`
  - `target_absent__speech`
- 并已实际跑在：
  - `legacy_transient_leakguard_probe_v1`
  - `legacy_transient_leakguard_probe_v3_w0005`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1`

当前新增结论：

1. `v1`
   - fail:
     - `target_present__speech`
     - `target_present__none`
2. `v3_w0005`
   - fail:
     - `target_present__speech`
3. `v4_speechfocus_ft1`
   - fail:
     - `target_present__speech`
4. `v5_absentguard_ft1`
   - fail:
     - `target_present__speech`
     - `target_present__none`

后续要求：

1. 以后 near-real objective-only 候选，默认先过 `gate_near_real_tradeoff.py`，再谈是否值得继续保留。
2. 若一个候选已经明确 fail 某个关键桶，不能再只因为整包上某些局部亮点就把它当成“下一主候选”。
3. 后续若要改 gate，必须：
   - 先在文档里写清改动理由；
   - 再改脚本；
   - 不能只在对话里临时换标准。

### 58. 相对保守锚点通过 hard gate，不等于已经对主基线过关；`v7` 的正确定位是“替换 `v3`”，不是“替换 `stage2` 或 `v1`”

现象：

- 本轮新增 `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`。
- 它相对 `legacy_transient_leakguard_probe_v3_w0005` 已通过三类关键桶 hard gate：
  - `target_present__speech`
  - `target_present__none`
  - `target_absent__speech`
- 但相对 `legacy_stage2` 时，仍 fail：
  - `target_present__speech`

影响：

- 如果只看到：
  - “`v7` 已经通过 gate”
  而不区分它过的是谁的 gate，就很容易误判成：
  - `v7` 已经可以升成新主候选
  - 或者已经能替换 `legacy_stage2 / v1`
- 这会把“相对保守锚点的改进”误读成“相对主基线的放行”。

处理：

- 当前已把 `v7` 的定位明确写回日报与总览：
  - 它可以替换 `v3_w0005` 成为新的第二保留候选；
  - 但它还不能替换 `legacy_stage2`；
  - 也还不能替换 `legacy_transient_leakguard_probe_v1`。

后续要求：

1. 以后凡是说“某个 candidate 通过 gate”，必须同时写清：
   - baseline 是谁；
   - candidate 替换的是哪一层候选。
2. 若 candidate 只对“保守锚点”过关，但仍对主基线失守，就只能升级它在保守分支里的顺位，不能直接升成新的主候选。
3. 后续汇报候选顺位时，至少明确区分：
   - 默认主线
   - 当前 objective-only 最强候选
   - 保守升级锚点 / 副作用回收锚点

### 59. 同一个 listening-pack 输出目录，不能把 `export_ab_inference_from_manifest.py` 和下游分析脚本并行跑

现象：

- 本轮在导出 near-real blind 包时，曾把：
  - `scripts/eval/export_ab_inference_from_manifest.py`
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
  - `scripts/eval/analyze_listening_pack_transients.py`
  - `scripts/eval/analyze_listening_pack_tradeoff.py`
  - `scripts/eval/gate_near_real_tradeoff.py`
  针对同一个输出目录并行启动。
- 结果分析脚本在 export 还没写完样本目录和 `sample_meta.json` 时就开始读盘，出现过：
  - `num_samples = 0`
  - `summary.json` 缺失或不完整
  - gate 读取到半成品 summary

影响：

- 这类失败不是模型结论本身有问题，而是执行顺序错了。
- 如果不追根因，后续很容易把：
  - “分析结果为空”
  - “某脚本突然报缺文件”
  误判成数据包本身损坏或脚本逻辑回归。

处理：

- 当前已确认正确顺序应为：
  1. 先完整执行 export；
  2. 确认 blind 包样本与元数据已落盘；
  3. 再跑 bandwidth / transient / tradeoff / gate 分析。

后续要求：

1. 同一输出 pack 目录上，`export` 与下游分析默认串行，不并行。
2. 只有在 export 完成之后，多个纯分析脚本之间才允许并行。
3. 若再次看到：
   - `num_samples = 0`
   - 缺 `summary.json`
   - gate 读到空目录
   先检查是否是 export 和 analysis 抢同一个目录，而不是先怀疑模型或数据本身。

### 60. 即使已经把 near-real 失败压到单个 bucket，bucket 内也可能仍是几种互相冲突的子问题；`target_present__speech` 当前就是 3 条样本、3 种失败机制

现象：

- 在 hard gate 层面，当前 objective-only 主缺口已经收敛成：
  - `target_present__speech`
- 但进一步做样本级诊断后发现，这个 bucket 实际上只包含：
  - `near_real_0003`
  - `near_real_0004`
  - `near_real_0006`
- 且三条样本的失败主因并不一样：
  1. `near_real_0003`
     - 更像 over-suppression / residual-heavy + transient loss
  2. `near_real_0004`
     - 更像 speech leak trade-off
  3. `near_real_0006`
     - 更像 transient loss

影响：

- 如果只看到：
  - “当前只剩 `target_present__speech` 没过”
  就继续开一条统一的 loss / selector follow-up，很容易出现：
  - 修 `0006` 时把 `0004` 推回 leak；
  - 压 `0004` 时又把 `0003` 压成更 residual-heavy；
  - 最终 bucket 级 summary 继续原地打转。

处理：

- 当前已新增：
  - `scripts/eval/diagnose_near_real_bucket_failures.py`
- 并已把 `target_present__speech` 的样本级 failure signature 写回日报与总览。

后续要求：

1. 以后即使某个 near-real bucket 已经很小，也不要默认把它当成“单一机制问题”。
2. 在继续开下一条 objective-only follow-up 前，至少先确认：
   - 这个 bucket 内是不是其实由几条不同症状的样本组成。
3. 若 bucket 内症状已明显分裂，优先先做样本级诊断或可控映射，再决定：
   - 修哪一类
   - 先不修哪一类
4. 当前 `target_present__speech` 下，若只允许推进 1 条 follow-up，应优先选最单一的：
   - transient-only 子问题
   而不是继续对整个 bucket 做统一加权扫点。

### 61. broad synthetic regrouping 可能会把 near-real speech-only 候选排错顺序；如果 proxy 没有把真实 source family 和失败锚点带进去，就可能继续偏爱 `v1` 这类“更强但不更近真实”的版本

现象：

- 在完成 `target_present__speech` 的样本级诊断后，已经明确：
  - `near_real_0003`
  - `near_real_0004`
  - `near_real_0006`
  才是当前真正卡住的 speech-only target-present 样本。
- 早一轮 broad synthetic speech proxy 分析里：
  - `v1` 在 `speech_full_overlap_like`
  - `speech_leak_risk_proxy`
  - `speech_transient_proxy`
  - `speech_compound_proxy`
  上都仍优于 `v7`
- 但新补的 near-real-aligned 微型 probe：
  - 直接锚定 `0003 / 0004 / 0006`
  - 只使用真实近源 `friend_raw / guodegang_raw` 语音族
  之后，排序反过来了：
  - 相对 `legacy_stage2`
    - `v1 = -1.559718 dB`
    - `v7 = -0.629166 dB`
  - 相对 `v1`
    - `v7 = +0.930552 dB`
    - `24 / 24` 样本全胜

影响：

- 这说明“按 synthetic 默认 metadata 重新分桶”还不够接近当前 near-real speech bucket 的真实难点。
- 如果继续只依赖 broad proxy 排序，很容易误判成：
  - `v1` 仍是 speech-only follow-up 的更好基座
- 但更近真实的 probe 已经表明：
  - `v7` 才是更稳、更接近 near-real 排序的起点。

处理：

- 已新增：
  - `scripts/data/build_near_real_speech_probe_manifest.py`
  - `scripts/eval/analyze_near_real_speech_probe.py`
- 已生成并实跑：
  - `data/probes/near_real_speech_probe_v1_manifest.jsonl`
  - `stage2 vs v1`
  - `stage2 vs v7`
  - `v1 vs v7`

后续要求：

1. 以后只要当前 near-real 主缺口已经收敛到少数真实锚点，优先先补“带真实 source family 的微型 probe”，不要只靠 broad synthetic regrouping 排下一步候选。
2. 若 broad proxy 与 near-real-aligned micro probe 排序冲突，默认以更接近真实锚点的 micro probe 为准。
3. 当前 speech-only objective follow-up 的默认基座应改成：
   - `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
   而不是回到 `v1`。
4. 下一步若继续开新实验，默认只修：
   - `friend_raw`
   - `near_real_0003 / 0004` 型
   同时把 `guodegang_raw / 0006` 型当前已拿回的收益当 guardrail。

### 62. 只盯 `friend_raw / 0003 / 0004` 做 focused fine-tune，虽然能把 speech micro-probe 往前推，但很容易同步回吐 `guodegang / 0006` 和 broad default val；后续必须双侧设 guardrail

现象：

- 本轮基于：
  - `target_hard_speech + target_full + high-overlap`
  - `target_clean_speech + target_full + mid-gain + high-overlap`
  做了 very small focused fine-tune：
  - `legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1`
- 相对 `v7`，它在 near-real speech micro probe 上明显更好：
  - overall `+0.392748 dB`
  - `near_real_0003 = +0.421242`
  - `near_real_0004 = +0.692135`
- 但同时也出现了两类回吐：
  - default synthetic val 相对 `v7 = -0.191305 dB`
  - `near_real_0006` micro probe 相对 `v7 = -0.099073 dB`

影响：

- 这说明“对准 friend speech overlap 去修”是有效的，但它不会自动兼容：
  - `guodegang_raw / transient_like`
  - broad default synthetic coverage
- 如果后续继续只按 `0003 / 0004` 定向加力，很容易把：
  - `0006`
  - 或默认 val
  当作隐性代价慢慢吃掉。

处理：

- 当前已把 `v8` 记录为：
  - speech-bucket-focused 线上新的保留候选
- 但还未把它升成 broad objective-only 的无条件替代版。

后续要求：

1. 以后任何 `friend_raw` focused follow-up，至少同时看三层 guardrail：
   - `friend_raw / 0003 / 0004` 是否继续改善
   - `guodegang_raw / 0006` 是否回吐
   - default synthetic val 是否继续系统性回退
2. 不能只因为 speech micro-probe 更强，就直接把 focused 版本当成下一默认候选。
3. 当前下一条 follow-up 如果继续开，应优先做：
   - 在保住 `v8` 对 `0003 / 0004` 改善的前提下
   - 单独补 `0006` 的 transient-like guardrail
   而不是继续扩大 friend-only focused 训练预算。

### 63. `export_ab_inference_from_manifest.py` 的非 blind 导出文件命名，不兼容当前 near-real 自动分析脚本；要走 bandwidth / transient / tradeoff 链，仍应使用 blind 包

现象：

- 本轮尝试直接对 near-real manifest 做非 blind 导出：
  - `export_ab_inference_from_manifest.py`
- 导出目录内生成的是：
  - `legacy_stage2.wav`
  - `legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1.wav`
- 但现有自动分析脚本默认读取的是：
  - `candidate_a.wav`
  - `candidate_b.wav`

影响：

- 如果直接把非 blind 导出目录喂给：
  - `analyze_listening_pack_bandwidth.py`
  - `analyze_listening_pack_transients.py`
  - `analyze_listening_pack_tradeoff.py`
  会在读盘阶段直接报找不到或打不开 `candidate_a.wav / candidate_b.wav`。

处理：

- 本轮已改用：
  - `--blind`
  的导出方式重跑 near-real 包
- 随后 bandwidth / transient / tradeoff / gate / bucket diagnosis 链均恢复正常。

后续要求：

1. 只要目标是走现有 near-real 自动分析链，默认使用 blind 导出目录。
2. 如果未来需要支持非 blind 自动分析，应先统一命名约定或补兼容逻辑，不能假设现有分析脚本会自动识别 label-named wav。
3. 遇到这类“导出成功但分析读不到 wav”的问题，先检查文件命名约定，不要先怀疑音频本体损坏。

### 64. `speech-focused follow-up` 的 branch-local 进步，必须和 broad objective-only 升级分开判定；否则会把 `v7/v8` 这类局部修复线误当成总冠军

现象：

- `v7` 相对 `v1` 在 near-real speech micro-probe 上更强
- `v8` 相对 `v7` 在 `0003 / 0004` 也继续改善
- 但这两类“speech-focused 改进”并不自动等价于：
  - broad default synthetic val 也足够保住
  - 或 broad objective-only 排位已经完成替换

影响：

- 如果只盯着 micro-probe 或 `target_present__speech` 一条局部线索，会高估 branch-local follow-up 的全局价值。
- 这会导致：
  - 误把 `v7` 当成对 `v1` 的 broad keeper 升级
  - 或误把 `v8` 当成已经足够替代当前全部保留候选

处理：

- 本轮已新增：
  - `scripts/eval/gate_speech_probe_followup.py`
- 它明确要求：
  - 共享 `stage2` 基线
  - `0003 / 0004` 要继续改善
  - `0006` 只能在允许阈值内轻微回退
  - default val 不能回吐过多
  - near-real hard gate fail bucket 不能扩张

后续要求：

1. 以后所有 `v8` 之后的 speech-focused follow-up，先过这套 branch-local gate，再谈是否值得继续推进。
2. broad keeper 排位仍应单独判断，不能用 branch-local gate 结果直接替代。
3. “局部 speech 桶更强”和“全局更适合替主线”必须继续分开写结论。

### 65. 用 PowerShell `Set-Content` 或默认文本拼接 JSONL 时，容易写入 UTF-8 BOM，进而让 dataset 读盘直接报错

现象：

- 本轮在合并 focused manifest JSONL 时，最初直接用 PowerShell 文本写回。
- 生成文件头部带了 UTF-8 BOM。
- `SyntheticTSEDataset` 读这些 manifest 时，会在首行 JSON 解码阶段报：
  - `json.decoder.JSONDecodeError: Unexpected UTF-8 BOM`

影响：

- 表面上看像是某条 manifest 行坏了。
- 实际上是整个 JSONL 文件编码带 BOM，导致训练入口在最开始就失败。

处理：

- 本轮已改成显式使用无 BOM 的 UTF-8 写回组合 manifest。
- 问题随后消失，训练恢复正常。

后续要求：

1. 以后生成或拼接 JSONL manifest，默认使用 `utf-8` 无 BOM。
2. 遇到 `Unexpected UTF-8 BOM` 时，先查文件编码，不要先怀疑样本内容。
3. 若继续用 PowerShell 生成 JSONL，必须显式控制编码行为，不能依赖默认文本输出。

### 66. `hard/full-overlap/transient` synthetic proxy 目前会把 `friend` 侧修得更顺，却会系统性误伤真正想补的 `guodegang 0006`

现象：

- 本轮从 `v8` 出发，构造了一个看似合理的 `0006` 代理方向：
  - `target_hard_speech`
  - `target_full`
  - `overlap >= 0.9`
  - target transient 指标较高
- 再把这批样本叠加到 `v8` 的 friend-focused combo 上，训练出：
  - `v9`

影响：

- `v9` 在 synthetic default 上只小幅回吐：
  - `v8 -> v9 = -0.046169 dB`
- 但 near-real speech micro probe 上却出现反向结果：
  - `friend_raw = +0.073949 dB`
  - `0003 = +0.064120 dB`
  - `0004 = +0.083778 dB`
  - `guodegang_raw / 0006 = -0.285347 dB`
- 也就是这条 proxy 并没有把训练信号导向 `0006 recovery`，反而继续把模型往 friend 侧推。

处理：

- 本轮已用：
  - `scripts/eval/gate_speech_probe_followup.py --max-anchor-0006-regression-db 0.0`
  对 `v8 -> v9` 做严格预筛
- 结果直接 `FAIL`：
  - `speech_probe_overall_floor`
  - `anchor_0006_regression_floor`

后续要求：

1. 当前不要再沿这条 `hard/full-overlap/transient` synthetic proxy 继续开近邻训练。
2. 若要继续补 `0006`，应先重做 objective proxy，而不是再复用同类 manifest。
3. 以后所有声称“在补 `0006`”的 follow-up，都必须先看：
   - `guodegang_raw`
   - `near_real_0006`
   不能只看 broad speech proxy 是否转正。

### 67. `0006` 的 guardrail 不能继续混在 broad speech probe 里看整体均值；必须拆成独立 `guodegang` 子 probe，否则会被 `friend` 侧改善掩盖

现象：

- broad near-real speech probe v1 里：
  - `friend_raw = 18` 条
  - `guodegang_raw = 6` 条
- 当 follow-up 同时出现：
  - `friend` 侧略好
  - `guodegang 0006` 侧明显变差
  时，overall 只会表现成很小的正负波动。

影响：

- 如果只看 broad speech probe overall，很容易误判成：
  - “只是轻微波动，还能继续试”
- 实际上像 `v9` 这种情况，已经是：
  - `0006` 被系统性推坏
  - 但 `friend` 侧改善把整体均值部分抵消了

处理：

- 本轮已新增：
  - `data/probes/near_real_guodegang_transient_probe_v1_manifest.jsonl`
  - `scripts/eval/gate_probe_subset_guardrail.py`
- 并已确认：
  - `v8 -> v9` 在这条子 probe 上 `6 / 6` 全 regression

后续要求：

1. 今后所有“补 `0006`”的实验，必须单独看 `guodegang` 子 probe，不得只看 broad speech probe overall。
2. broad speech probe 继续保留，但它负责看 branch 的整体方向，不再承担 `0006` 专用 guardrail 职责。
3. 若 focused follow-up 在 `guodegang` 子 probe 上不过线，应直接止损，不再进入下一轮训练扩展。

### 68. `0006` 的 synthetic 代理若继续凭直觉往 `hard speech / friend overlap` 上靠，会把 proxy 重建方向带偏；当前最接近真实排序的反而是 `clean speech + high-target-transient`

现象：

- 在 `v9` 失败之后，本轮没有继续开训练，而是先用：
  - `scripts/eval/search_synthetic_proxy_candidates.py`
  在 default synthetic speech rows 上搜索能复现
  - `v7 > v8 > v9`
  的 metadata-defined 子集。
- 搜索得到的 top order-pass 候选，没有落在旧的：
  - `target_hard_speech`
  - `target_full`
  - `overlap >= 0.9`
  - transient-rich
  方向。
- 当前最稳定复现 `guodegang / 0006` 排序的，反而是：
  - `target_clean_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `overlap >= 0.75`
  - `speech_interference_clean_pool`
  - `target_transient_presence_minus_mid_db_mean >= -11.5350723`

影响：

- 这说明“`0006` 更像 hard speech / friend-like overlap”是一个错误直觉。
- 如果后续还沿旧方向继续构造 focused manifest，很容易再次出现：
  - friend 侧看起来更顺
  - 但真正的 `guodegang / 0006` 继续回退
- 也就是说，问题不只是权重没调对，而是 proxy 映射本身就在把训练信号导向错误子空间。

处理：

- 本轮已物化：
  - `data/synthetic/train_manifest_guodegang_proxy_v1.jsonl`
  - `data/synthetic/val_manifest_guodegang_proxy_v1.jsonl`
- 并已确认它们在独立 compare 上可复现：
  - `v7 > v8 > v9`

后续要求：

1. 若继续做 `0006` 相关 objective-only follow-up，默认先从 `guodegang_proxy_v1` 出发，而不是回到 `hard_transient_focus_v1_any`。
2. 但 `guodegang_proxy_v1` 仍只是 synthetic 预筛，不替代：
   - `near_real_guodegang_transient_probe_v1`
3. 今后任何声称“补回了 `0006`”的版本，都至少要同时说明：
   - 在 `guodegang_proxy_v1` 上是否仍保持 `v7 > v8 > v9` 方向的一致性
   - 在 `near_real_guodegang_transient_probe_v1` 上是否真的不过线或转正

### 69. 即使 synthetic proxy 已经比旧方向更接近真实，也不代表它单独拿来做 focused fine-tune 就足够；`v10` 证明了“单边补 `guodegang`”仍会把真实 `0006` 推坏

现象：

- 本轮基于：
  - `train_manifest_guodegang_proxy_v1.jsonl`
  - `val_manifest_guodegang_proxy_v1.jsonl`
  从 `v8` warm-start 做了：
  - `legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1`
- `v10` 在 synthetic 上看起来并不差：
  - 相对 `v8`
    - default: `-0.031839 dB`
    - `guodegang_proxy_v1`: `+0.480623 dB`
- broad near-real speech probe 相对 `v8` 也仍是小幅正增益：
  - overall: `+0.080006 dB`
  - `0003 = +0.280721 dB`
  - `0004 = +0.211316 dB`

影响：

- 如果只看：
  - default
  - broad speech probe overall
  很容易误判成：
  - `v10` 基本可留
- 但真正关键的：
  - `near_real_guodegang_transient_probe_v1`
  上，`v10` 相对 `v8` 是：
  - `-0.418033 dB`
  - `6 / 6` 样本全部 regression
- 也就是：
  - 新 proxy 虽然比旧的更像
  - 但它单独拿来做 focused 训练，仍不足以约束真实 `0006`

处理：

- 本轮已确认：
  - `gate_speech_probe_followup.py` 失败项只剩：
    - `anchor_0006_regression_floor`
  - `gate_probe_subset_guardrail.py` 在 `guodegang` 子 probe 上直接全线失败
- 同时又补做了一次：
  - `v8 > v10`
  synthetic 搜索

后续要求：

1. 以后不要把“proxy 更接近真实”误解为“只用这条 proxy 单边微调就够了”。
2. 当前更合理的 follow-up 设计应改成双锚点：
   - `guodegang_proxy_v1` 作为正向 focused 信号
   - `friend_hard_negative_segments / hard full-overlap` 作为反向 guardrail
3. 在真实 `0006` guardrail 没过之前，不能因为：
   - default 没炸
   - `0003 / 0004` 更好
   就把候选继续往下推进。

### 70. 即使已经把“正向 `guodegang` proxy + 反向 friend hard-overlap guardrail”同时放进 one-shot dual-anchor manifest，也不代表真实 `0006` 就会自动被保住；`v11` 证明这种平衡会先继续偏向 friend 侧

现象：

- 本轮基于：
  - `guodegang_proxy_v1`
  - `target_hard_speech + target_full + speech_interference_hard_pool(friend_hard_negative_segments)`
  直接拼出：
  - `train_manifest_v11_dualanchor_v1.jsonl = 136`
  - `val_manifest_v11_dualanchor_v1.jsonl = 49`
- 再从 `v8` warm-start 训练出：
  - `legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1`
- `v11` 在 synthetic 上看起来比 `v10` 还更像成功：
  - 相对 `v8`
    - default: `-0.079973 dB`
    - `guodegang_proxy_v1`: `+0.795423 dB`
- broad near-real speech micro probe 相对 `v8` 也仍是小幅正增益：
  - overall: `+0.025061 dB`
  - `0003 = +0.260091 dB`
  - `0004 = +0.241347 dB`

影响：

- 如果只看：
  - default
  - synthetic `guodegang_proxy_v1`
  - broad speech probe overall
  会很容易误判成：
  - “dual-anchor 已经开始起效”
- 但真正关键的：
  - `near_real_guodegang_transient_probe_v1`
  上，`v11` 相对 `v8` 是：
  - `-0.651915 dB`
  - `6 / 6` 样本全部 regression
- 也就是：
  - friend 侧确实继续变好
  - 可真实 `0006` 仍被系统性挤压
- 更细看还会发现：
  - `guodegang_absent_480s` 相对 `legacy_stage2` 是正增益
  - `guodegang_anchor_120s` 却变成负增益
  说明当前 `0006` 内部可能已经不是单一子问题

处理：

- 本轮已确认：
  - `gate_speech_probe_followup.py` 失败项仍是：
    - `anchor_0006_regression_floor`
  - `gate_probe_subset_guardrail.py` 在 focused `guodegang` 子 probe 上仍直接失败：
    - `overall_floor`
    - `family__guodegang_raw`
    - `anchor__near_real_0006`
- 同时已把这一轮结论写回：
  - `reports/daily/2026-03-18_v11_v8_dualanchor_ft1.md`
  - `docs/01_project_overview_and_plan.md`

后续要求：

1. 以后不要把“正向 proxy 和反向 guardrail 都加进 manifest 了”误读成“真实双锚点已经被平衡住”。
2. 当前不要继续沿 `v11` 同配方扩大训练预算。
3. 若继续补 `0006`，默认先拆开看：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
   不要再把它们当成同一个 objective proxy 目标。
4. 在真实 `0006` guardrail 没过之前，不能因为：
   - `0003 / 0004` 更强
   - broad speech probe overall 仍为正
   就把 dual-anchor 分支继续往下推进。

### 71. `near_real_0006` 现在已经不是单一子问题；如果还把 `guodegang_anchor_120s` 和 `guodegang_absent_480s` 混成同一条 proxy 或同一条 gate，只会继续把训练信号互相抵消

现象：

- 本轮把 `near_real_guodegang_transient_probe_v1` 再拆成：
  - `near_real_guodegang_anchor_probe_v1`
  - `near_real_guodegang_absent_probe_v1`
- 结果发现两条 clip 的真实排序已经冲突：
  - `anchor`:
    - `v7 > v8 > v10 > v11`
  - `absent`:
    - `v8 > v7 > v10 > v11`

影响：

- 如果继续把两条 clip 混在同一条 `0006` guardrail 里看 overall：
  - 会看见一个折中的均值
  - 但看不出 candidate 到底是在修：
    - `anchor`
    - 还是 `absent`
- 这会导致：
  - 误把某个“只修好其中一条”的版本理解成“`0006` 已整体转正”
  - 或继续错误寻找一条“统一总 proxy”

处理：

- 本轮已把 clip 级 guardrail 正式脚本化：
  - `scripts/eval/gate_probe_subset_guardrail.py --clip-tags ...`
- 同时把 synthetic proxy 也拆成两条：
  - `guodegang_anchor_proxy_v1`
  - `guodegang_absent_proxy_v2_speechonly`

后续要求：

1. 今后凡是声称“补 `0006`”的版本，至少同时汇报：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
2. 若只看合并后的 `near_real_guodegang_transient_probe_v1` overall，不再视为足够。
3. 下一步默认不再寻找“统一 `0006` 总 proxy”，而是分别维护：
   - `anchor` proxy
   - `absent` proxy

### 72. `absent` proxy 一旦把 `music / singing` 一起混进来，排序会立刻漂掉；这条 proxy 必须保持 speech-only 边界

现象：

- 本轮先按较宽口径物化了：
  - `guodegang_absent_proxy_v1`
- 它包含：
  - `speech`
  - `music`
  - `singing`
  的 full-overlap 高 transient rows
- 结果在 synthetic compare 上，排序变成：
  - `v7 > v8 > v10 > v11`
  而不是 near-real `absent_480s` 想要的：
  - `v8 > v7 > v10 > v11`

影响：

- 这说明 `absent_480s` 的 proxy 不是“只要高 transient 就行”
- 一旦把 non-speech rows 混进来，就会把排序重新带偏
- 也就是：
  - `absent` proxy 的关键边界之一就是 speech-only

处理：

- 本轮已收回并改成：
  - `guodegang_absent_proxy_v2_speechonly`
- 过滤条件为：
  - `target_clean_speech / target_hard_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `overlap >= 0.9`
  - `target_transient_presence_minus_mid_db_mean >= q50`
- 新 manifest 已确认复现：
  - `v8 > v7 > v10 > v11`

后续要求：

1. 以后若继续构造 `absent_480s` proxy，默认保持 speech-only。
2. 不要因为某个 broad transient-rich manifest 看起来更“大更全”，就把 `music / singing` 一起混进来。
3. 若某条 `absent` proxy 没有先验证：
   - `v8 > v7 > v10 > v11`
   就不要把它当成新的 objective 入口。

### 73. broad speech gate 过线，不等于 clip 级 `anchor / absent` trade-off 已过线；`v12` 证明如果不同时看两条 clip，仍会把“有代价的成功”误读成“已可替代参考版本”

现象：

- 本轮 `v12 = legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1`：
  - 相对 `v8` 的 `speech_followup_gate_summary.json` 已经 `PASS`
  - `near_real_guodegang_transient_probe_v1` overall 也相对 `v8` 转成：
    - `+0.075219 dB`
- 但同一轮在 clip 级 `probe_subset_guardrail_vs_v8_with_clips.json` 里仍然：
  - `FAIL`
  - 唯一失败项是：
    - `clip__guodegang_absent_480s`
- 也就是说，`v12` 的真实形态是：
  - `guodegang_anchor_120s` 相对 `v8`：
    - `+0.266803 dB`
  - `guodegang_absent_480s` 相对 `v8`：
    - `-0.116366 dB`

影响：

- 如果只看：
  - broad speech follow-up gate
  - 或合并后的 `near_real_0006` overall
- 很容易误判成：
  - `v12` 已经无代价替代 `v8`
- 实际上它只是：
  - 成功修回了 `anchor`
  - 但仍在 `absent` 上付出小幅代价

处理：

- 本轮已把该结论同步写入：
  - `reports/daily/2026-03-18_v12_v8_anchor_proxy_ft1.md`
  - `docs/01_project_overview_and_plan.md`
- 当前默认口径更新为：
  - `v8` 保留为 broad speech 参考基座
  - `v12` 仅作为 anchor-focused 第二候选保留

后续要求：

1. 以后凡是 `v12+` 的 follow-up，至少同时汇报：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
2. 只要 clip 级 `absent` 仍明显回退，就不要把 broad gate 的 `PASS` 误写成“已可切主线”。
3. 下一步若继续推进，优先补的是：
   - `absent` 的显式 floor / guardrail
   而不是继续做更宽的 anchor-only 强化。
