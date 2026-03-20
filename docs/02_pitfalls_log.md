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

### 74. Windows PowerShell 5 的 `Set-Content -Encoding utf8` 默认会写 UTF-8 BOM；对当前 JSONL 读取器来说，这会直接把新 manifest 写坏

现象：

- 本轮在物化：
  - `train_manifest_v13_anchor_absent_proxy_v1.jsonl`
  - `val_manifest_v13_anchor_absent_proxy_v1.jsonl`
  时，先用 `Set-Content -Encoding utf8` 写盘；
- 随后训练入口在读取第一行 JSONL 时直接报错：
  - `Unexpected UTF-8 BOM (decode using utf-8-sig)`

影响：

- 当前训练数据读取链默认按普通 `utf-8` 解码；
- 只要 manifest 带 BOM，就会在首行 `json.loads(...)` 直接失败；
- 这类问题看起来像“JSON 内容坏了”，实际上是编码前缀问题。

处理：

- 本轮已改用 `.NET UTF8Encoding(false)` 将两份 manifest 重写为：
  - UTF-8 无 BOM

后续要求：

1. 后面凡是新写 JSON / JSONL / Markdown，如果走 PowerShell 落盘，默认不要用会写 BOM 的旧口径。
2. 若必须用 PowerShell 原生命令生成文本，写完后至少再核对一次是否带 BOM。
3. 当前仓库的“统一 UTF-8 无 BOM”不是口头约定；它会直接影响训练脚本能不能读文件。

### 75. 把 `anchor_proxy` 和 `absent_proxy` 直接做 one-shot 并集，再从 `v12` warm-start 微调，并不会自然形成“保 anchor、补 absent”的折中；`v13` 证明它会把训练信号继续推向 friend 侧，却仍修不好真正想补的 `absent_480s`

现象：

- 本轮 `v13 = legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1`：
  - 使用：
    - `guodegang_anchor_proxy_v1`
    - `guodegang_absent_proxy_v2_speechonly`
    的去重并集
  - 从 `v12` warm-start
- 结果相对 `v8`：
  - near-real speech probe overall：
    - `+0.264425 dB`
  - `near_real_0003`：
    - `+0.311168 dB`
  - `near_real_0004`：
    - `+0.418977 dB`
  - 但 `near_real_0006`：
    - `-0.037517 dB`
  - 且 clip 级仍是：
    - `guodegang_anchor_120s = +0.107729 dB`
    - `guodegang_absent_480s = -0.182764 dB`
- 结果相对 `v12` 还进一步变成：
  - `guodegang_anchor_120s = -0.159074 dB`
  - `guodegang_absent_480s = -0.066398 dB`

影响：

- 这说明当前 one-shot union 训练不是“把两条目标自然平衡起来”；
- 它更像：
  - 继续强化了 `friend_raw / 0003 / 0004`
  - 却没有把真正要补的 `absent_480s` 拉回来
  - 还顺带把 `v12` 的 anchor 收益也一起回吐

处理：

- 本轮已将 `v13` 记录为：
  - 不保留
- 当前默认口径更新为：
  - 不继续沿这条 one-shot `anchor+absent` 并集路线扩大训练

后续要求：

1. 以后不要把“proxy 数量从 1 条加到 2 条”误读成“目标自然会更平衡”。
2. 若下一步还要补 `absent`，应先重做：
   - `absent` objective proxy
   - 或 `clip` 级 floor / gate
3. 在没有新 proxy 证据前，不要再直接把现有 `absent_proxy_v2_speechonly` 拼进 `v12` 做训练。

### 76. 新重建出来的 `absent` proxy 如果本身是 `target_full`，那就不能再想当然地以为“现有 absent-loss 配置会自动在这条 proxy 上生效”；`v14` 证明当前 selector 下它根本没有触发

现象：

- 本轮按真实排序 `v8 > v12 > v13` 重建出的新 proxy：
  - `guodegang_absent_proxy_v3_strict`
  - `guodegang_absent_proxy_v4_broad`
- 它们都稳定收敛到：
  - `target_hard_speech`
  - `target_full`
  - `target_present_ratio >= 0.95`
  - `high-overlap`
- 随后开的 `v14 = legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1` 训练日志里：
  - `train_absent_interval_l1 = 0.0`
  - `val_absent_interval_l1 = 0.0`
  且三轮都如此

原因：

- 当前训练参数仍把 absent loss 限定在：
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
- 但这轮新 proxy 全是：
  - `target_full`

影响：

- 名字叫 “absent proxy follow-up”，不代表它真的走了 explicit absent-loss；
- 在当前 selector 下，它其实只是：
  - 一次基于新 proxy 的 `target_full / hard speech` focused fine-tune
- 如果忽略这点，就会把训练结果误读成：
  - “absent loss 没有效果”
  - 但实际更准确的说法是：
    - 这轮根本没触发到 absent loss

处理：

- 本轮已在：
  - `reports/daily/2026-03-18_v14_v12_absent_proxy_v3_strict_ft1.md`
  - `docs/01_project_overview_and_plan.md`
  显式补记该事实

后续要求：

1. 以后只要新 proxy 是 `target_full` 主导，就必须先核对：
   - 当前 loss selector 是否真的会在它上面触发
2. 不要把：
   - “proxy 名字是 absent”
   自动等价成：
   - “训练里一定有 absent-loss 信号”
3. 若后续真要把这条新 proxy 接进 objective，先决定的是：
   - 改 selector
   - 还是承认它只是新的 focused fine-tune subset

### 77. 能复现真实排序的 synthetic proxy，不等于直接拿它从当前候选 warm-start 微调，就会把真实指标往正确方向推；`v14` 证明了“proxy 可搜索”与“proxy 可训练”是两件事

现象：

- 本轮新重建的 `guodegang_absent_proxy_v3_strict / v4_broad` 已经能稳定复现：
  - `v8 > v12 > v13`
- 但基于主候选 `v3_strict` 开出的：
  - `v14 = legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1`
  结果却变成：
  - 相对 `v12`
    - default val：
      - `-0.098198 dB`
    - near-real speech probe overall：
      - `-0.210393 dB`
    - `near_real_0006`：
      - `-0.750831 dB`
    - `guodegang_anchor_120s`：
      - `-1.099112 dB`
    - `guodegang_absent_480s`：
      - `-0.402550 dB`
    - `guodegang_absent_proxy_v3_strict`：
      - `-0.284848 dB`
- 也就是说：
  - 它不但没把真实 `absent` 拉回去；
  - 连这轮新建的主 proxy 自己也没保住

影响：

- 这说明：
  - “找到能复现真实排序的 synthetic 子集”
  - 只是解决了：
    - proxy 定义问题
  - 还没有解决：
    - 当前 warm-start / 预算 / objective / 约束下是否可训练
- 如果跳过这层区分，很容易把后续每次失败都误归因成：
  - proxy 还不够准
  而不是：
  - 训练路径本身不适合

处理：

- 本轮已将 `v14` 记录为：
  - 不保留
- 当前默认口径更新为：
  - `v3_strict / v4_broad` 保留为 absent-side synthetic eval / guardrail
  - 但不再直接当作 `v12` 的 single-route warm-start fine-tune objective

后续要求：

1. 以后先把这两件事分开判断：
   - proxy 是否真实对齐
   - 在当前训练路径下是否可训练
2. 若下一步还要继续补 `absent`，优先考虑的是：
   - 联立 `anchor` floor
   - 或更小预算的 nudging
   - 或先把新 proxy 只当 gate / eval，而不是直接拿来训练
3. 在没有新证据前，不要再把：
   - “proxy 搜索通过”
   直接写成：
   - “这条 focused fine-tune 路线可继续加预算”

### 78. 把 `anchor_proxy_v1` 与新 `absent_proxy_v3_strict` 做极轻量并集 nudging，确实能把 `anchor_120s` 拉回安全区附近，但它仍不会自然把 `absent_480s` 拉到 `v12` 之上；`v15` 说明这条路线本质上还是在强化 `anchor`，而不是在修真正的 `absent`

现象：

- 本轮 `v15 = legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1`：
  - 从 `v12` warm-start
  - 训练集是：
    - `guodegang_anchor_proxy_v1`
    - `guodegang_absent_proxy_v3_strict`
    的去重并集
  - 但预算极小：
    - `1 epoch`
    - `lr = 1e-5`
    - `34 steps`
- 结果相对 `v8`：
  - `guodegang_anchor_120s = +0.049097 dB`
  - `guodegang_absent_480s = -0.186798 dB`
- 结果相对 `v12`：
  - `guodegang_anchor_120s = -0.217707 dB`
  - `guodegang_absent_480s = -0.070432 dB`
  - `guodegang_anchor_proxy_v1 = +0.322262 dB`
  - `guodegang_absent_proxy_v3_strict = -0.126638 dB`

影响：

- 这说明轻量双路 nudging 的真实作用更像：
  - 保住甚至继续加强 `anchor` 方向
  - 但并没有把目标中的 `absent` 一侧往前推进
- 如果忽略这点，很容易把它误读成：
  - “已经很接近，只要再把步长调小一点就行”
- 但从当前证据看，更准确的说法是：
  - 这条路线的优化向量本身就偏向 `anchor`
  - 它不是当前 `absent_480s` 的有效修复入口

处理：

- 本轮已将 `v15` 记录为：
  - 不保留
- 当前默认口径更新为：
  - 不继续沿这条 warm-start 小步长搜索路线加预算

后续要求：

1. 以后不要因为某个版本“重新通过了 `clip__guodegang_anchor_120s`”就误判它正在修 `absent`。
2. 对这类双路 nudging，至少同时汇报：
   - `anchor_proxy` 变化
   - `absent_proxy` 变化
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
3. 如果结果表现出：
   - `anchor` 继续增强
   - `absent` 继续不动或回退
   就应直接停止，而不是继续扫更小 learning rate / 更小 step 数。

### 79. 如果训练摘要里不显式记录 selector 命中统计，就很容易把“loss 权重开着但 selector 实际 0 命中”的情况误读成“这项 loss 效果不好”；`v14` 暴露的是 selector 没打中，不只是数值弱

现象：

- `v14` 文档已经确认：
  - `absent_weight = 2.0`
  - 但 `train_absent_interval_l1 = 0.0`
  - 且新 proxy 样本本身都是：
    - `target_full`
- 如果只看旧版 `train_summary.json`：
  - 能看到 loss 数值为 `0.0`
  - 但看不到：
    - selector 到底有没有选中样本
- 这种情况下，很容易把结论写成：
  - “absent loss 开了但没有效果”
  - 而不是更准确的：
    - “当前 selector 配置根本没有命中这批样本”

处理：

- 本轮已在当前工作树补上：
  - dataset 侧 selector 元数据：
    - `overlap_ratio`
    - `interference_gain_db`
    - `interference_pool`
    - `interference_speaker_name`
  - 统一的：
    - `loss_selectors.py`
  - train summary 中的：
    - `train_selector_metrics`
    - `val_selector_metrics`
- 并已用 `tmp/selector_metrics_smoke_v14_style` 做 1-step smoke 验证：
  - `absent.selected_fraction = 0.0`

后续要求：

1. 以后任何 focused fine-tune 只要开了 selector，就必须同时看：
   - loss 数值
   - selector `selected_count / selected_fraction`
2. 如果某项 selector `active = true` 但：
   - `selected_count = 0`
   应先修 selector 或修 proxy 定义，而不是继续解释 loss 曲线。
3. 后续文档汇报里，不要再只写：
   - `absent_interval_l1 = 0.0`
   还要补一句：
   - 是因为命中为零
   - 还是命中了但优化失败。

### 80. 只看 `anchor_proxy_v1` 是否继续增强，无法判断候选是不是在修 `absent`；`v13 / v15` 都证明了“anchor 通过”与“absent 通过”是两回事，后续必须用 dual-proxy gate 同时看

现象：

- 本轮新增 synthetic dual-proxy gate 后，回放结果变得更明确：
  - `v13`
    - `anchor_proxy_v1 - v12 = +0.893597 dB`
    - 但：
      - `absent_proxy_v3_strict - v12 = -0.111381 dB`
      - `absent_proxy_v4_broad - v12 = -0.104639 dB`
  - `v15`
    - `anchor_proxy_v1 - v12 = +0.322262 dB`
    - 但：
      - `absent_proxy_v3_strict - v12 = -0.126638 dB`
      - `absent_proxy_v4_broad - v12 = -0.078349 dB`

影响：

- 如果只盯：
  - `anchor_proxy_v1`
  会很容易得出一种错误直觉：
  - “候选还在往对的方向走，只差一点 absent”
- 但 dual-proxy gate 已经说明：
  - 这些版本不是“差一点”；
  - 而是 synthetic absent-side 方向本身仍低于 `v12`。

处理：

- 本轮已新增：
  - `scripts/eval/gate_synthetic_dual_proxy.py`
- 当前默认规则应固定为：
  - `anchor_proxy_v1` 相对 `v12` 不回退
  - `guodegang_absent_proxy_v3_strict / v4_broad` 相对 `v12` 不变差

后续要求：

1. 以后任何 `v12+` absent follow-up，都不要再只汇报：
   - `anchor_proxy_v1`
   - 或单条 absent proxy
2. 至少同时看：
   - `anchor_proxy_v1`
   - `absent_proxy_v3_strict`
   - `absent_proxy_v4_broad`
3. 如果结果是：
   - anchor 通过
   - absent 双失败
   结论应直接写成：
   - 这条路线仍在强化 anchor，不是在修 absent。

### 81. 新增 reverse guardrail 并不等于可以靠简单下调 `absent_weight` 把 synthetic dual-proxy gate 的最后一点差距补过去；`v16 / v17` 证明这条路线的敏感点不在这里

现象：

- 本轮先构造了新的 reverse guardrail proxy：
  - `target_clean_speech`
  - `speech_interference_clean_pool`
  - 高 `interference_gain_db`
  - 高 `target_transient_presence_minus_mid_db_mean`
- 随后开的 `v16`：
  - `absent_proxy_v3_strict ∪ reverse_guardrail_proxy_v1`
  - 相对 `v12` 已经收敛到：
    - default = `-0.004540 dB`
    - `anchor_proxy_v1 = +0.298964 dB`
    - `absent_proxy_v3_strict = -0.007883 dB`
    - `absent_proxy_v4_broad = -0.001475 dB`
  - dual-proxy gate 只差：
    - absent 双项极小回退
- 但随后把：
  - `absent_weight = 1.0 -> 0.5`
  得到的 `v17` 反而变成：
  - default = `-0.038008 dB`
  - `anchor_proxy_v1 = -0.532572 dB`
  - `absent_proxy_v3_strict = -0.019250 dB`
  - `absent_proxy_v4_broad = -0.009301 dB`

影响：

- 这说明 `v16` 没过线的原因，不是“absent loss 稍微太重，降一点就会自然通过”；
- 更准确地说：
  - 这条路线已经接近 synthetic pre-screen；
  - 但真正还需要调的是：
    - full-pattern hard-speech 一侧的 transient / interference 路
    - 或整体预算分配
  - 不是继续把 absent side 越降越轻

处理：

- 本轮已将：
  - `v16`
  - `v17`
  都记录为：
  - 不保留
- 但同步保留一个更重要的中间结论：
  - `v16` 这条 objective 方向显著优于 `v13 / v14 / v15`

后续要求：

1. 以后若某条新路线已经接近 dual-proxy gate，只差极小 absent 回退，不要默认第一反应就是继续下调 `absent_weight`。
2. 对这类 near-miss，优先调整：
   - transient / interference selector
   - full-pattern 预算
   - 或总 step 分配
3. 如果一次降权重直接导致：
   - anchor floor 也丢
   - default 也回吐
   就应停止把“继续降 absent weight”当成默认搜索方向。

### 82. 对 `v16` 这条 reverse-guardrail 路线，把 transient / interference 一起减半并不会把 absent-side synthetic 缺口自动补回来；`v18` 说明“整体一起降预算”会先把 absent proxy 拉弱，而不是帮这条路线过线

现象：

- 本轮 `v18 = legacy_transient_leakguard_probe_v18_v12_absent_proxy_v3_reverse_guardrail_v1_ti_half_ft1`
  在 `v16` 同 manifest / 同 selector 下，仅把：
  - `transient_weight = 0.002 -> 0.001`
  - `interference_weight = 0.005 -> 0.0025`
- 结果相对 `v12`：
  - `anchor_proxy_v1 = +0.233116 dB`
  - 但：
    - `absent_proxy_v3_strict = -0.065609 dB`
    - `absent_proxy_v4_broad = -0.042189 dB`
- synthetic dual-proxy gate 仍然：
  - `FAIL`
  - failed：
    - `absent_proxy_v3_strict`
    - `absent_proxy_v4_broad`

影响：

- 这说明 `v16` 路线当前卡住的点，不是“transient / interference 总预算略高，降一点就自然过线”；
- 更准确地说：
  - 这两条 loss 在当前路线里仍提供了必要支撑；
  - 如果一起往下砍，先掉下去的反而是 absent-side synthetic 支配关系。

处理：

- 本轮已将 `v18` 记录为：
  - 不保留

后续要求：

1. 以后若某条 synthetic near-miss 路线还差 absent-side 最后一点，不要默认第一反应就是“把 transient / interference 一起减半”。
2. 优先改：
   - selector 形状
   - branch-local carve-out
   - 或单路预算
   而不是无差别整体减半。
3. 如果某条 follow-up 仍然表现为：
   - `anchor` 继续通过
   - absent 双失败
   就应明确写成：
   - 这版没有修掉真正的 absent 缺口。

### 83. 即使某个 absent follow-up 已经首次通过 synthetic dual-proxy gate，也不代表它可以直接晋升；`v19` 证明 synthetic 过线之后，broad near-real 仍可能卡在完全不同的 friend-side 锚点

现象：

- 本轮 `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
  首次同时通过：
  - `anchor_proxy_v1`
  - `absent_proxy_v3_strict`
  - `absent_proxy_v4_broad`
- 但补跑 near-real 后，相对 `v12` 仍然是：
  - speech probe overall = `-0.011926 dB`
  - `friend_raw = -0.039734 dB`
  - `near_real_0003 = -0.068178 dB`
  - `near_real_0004 = -0.011290 dB`
  - `near_real_0006 = +0.071497 dB`
- `speech_followup_gate_vs_v12`：
  - `FAIL`
  - failed：
    - `speech_probe_overall_floor`
    - `speech_probe_friend_raw_floor`
    - `anchor_0003_gain_floor`
    - `anchor_0004_gain_floor`
- 同时 `guodegang` 子 probe 虽已相对 `v8` 通过：
  - overall
  - `guodegang_anchor_120s`
  - `near_real_0006`
  但仍卡在：
  - `clip__guodegang_absent_480s`

影响：

- 这说明：
  - synthetic dual-proxy gate
  只负责证明 absent objective 方向终于可训练；
- 它不负责保证：
  - broad near-real `friend_raw / 0003 / 0004`
  不回退；
- 也不负责保证：
  - `guodegang_absent_480s`
  一定已经超过 `v8`。

处理：

- 本轮没有把 `v19` 直接升级成主候选；
- 当前口径改为：
  - `v19` 是新的 objective 基座
  - 但还需要 friend-side reverse guardrail / branch-local proxy

后续要求：

1. 以后任何 synthetic dual-proxy `PASS` 的 absent follow-up，都必须继续补：
   - `speech_followup_gate_vs_v12`
   - `probe_subset_guardrail_vs_v8_with_clips`
   再谈是否值得晋升。
2. 若结果表现为：
   - `0006` 继续变强
   - 但 `friend_raw / 0003 / 0004` 回退
   结论应改写成：
   - “objective 方向对了，但 broad real trade-off 还没闭环”
   而不是写成：
   - “这条线已经基本完成”。
3. 下一步若继续推进，优先补的是：
   - `v19 vs v12` 的 friend-side reverse guardrail
   - 或新的 branch-local synthetic proxy
   而不是继续只围绕 `absent_480s` 单边加力。

### 84. 如果把新加的 friend-side reverse guardrail 样本直接并进 `v19` warm-start，但它们没有命中任何专项 selector，那这轮训练本质上就不是“friend-side branch-local guardrail”，而只是一次 base-loss nudging；`v20` 证明这种做法会同时拖坏 broad real 和新增 proxy 本身

现象：

- 本轮 `v20 = legacy_transient_leakguard_probe_v20_v19_friend_reverse_guardrail_v1_ft1`
  相对 `v19` 只新增了：
  - train `21`
  - val `8`
  条样本；
- 且这些新增样本全部都是：
  - `target_clean_speech`
  - `target_full`
- 但 `v20` 的 selector 命中计数与 `v19` 完全相同：
  - train transient / interference / absent：
    - `51 / 51 / 24`
  - val transient / interference / absent：
    - `18 / 18 / 4`
- 唯一变化只是 total count：
  - train：
    - `90 -> 111`
  - val：
    - `27 -> 35`

影响：

- 这说明新增的 friend reverse guardrail 样本：
  - 没有进入 transient selector
  - 没有进入 interference selector
  - 也没有进入 absent selector
- 因而 `v20` 的真实形态不是：
  - “把 friend-side 风险正式接入 branch-local objective”
- 而更接近：
  - “在 `v19` 现有 objective 外，再额外并入一批只吃 base reconstruction loss 的 `target_clean_speech + target_full` 样本”
- 结果就是：
  - default val 相对 `v19 = -0.020962 dB`
  - `v20_v19_friend_reverse_guardrail_proxy_v1` 相对 `v19 = -0.131127 dB`
  - broad near-real speech probe overall 相对 `v19 = -0.051919 dB`
  - `near_real_guodegang_speech_probe` overall 相对 `v19 = -0.142566 dB`

处理：

- 本轮已把 `v20` 记录为：
  - 不保留
- 同时已把下一步要用的 selector plumbing 补到当前工作树：
  - `target_transient_presence_minus_mid_db_mean`
  - `target_transient_presence_share_mean`

后续要求：

1. 以后凡是新增 branch-local proxy 样本并入 warm-start 训练，必须同时核对：
   - total count 有没有变
   - `selected_count` 有没有同步增加
2. 如果只是：
   - total count 变多
   - `selected_count` 完全不变
   就不要把这轮训练写成：
   - “某个新 guardrail 已接入 objective”
   更准确的写法应是：
   - “只是一次无 selector 命中增量的 base-loss 并集 nudging”
3. 下一步若继续补 friend-side，不要再直接复制 `v20`；
   优先做的是：
   - 让 friend-side样本进入显式 selector
   - 或先重做能复现 friend-side 排序差异的 synthetic proxy

### 85. 即使把新增 friend-side proxy 真正接进了 selector，只要这批 proxy 样本本身没有提供比 `v19` 更正确的优化方向，训练仍然会回退；`v21` 说明“有 selector 命中”只是必要条件，不是充分条件

现象：

- 本轮 `v21 = legacy_transient_leakguard_probe_v21_v19_friend_reverse_guardrail_proxy_v2_transient_extra_ft1`
  在 `v20` 基础上进一步补了：
  - selector `extra` branch
  - 把新的 clean/full/high-transient friend proxy 显式挂进 `transient_extra`
- selector 命中数确实明显增加：
  - train transient：
    - `51 -> 76`
  - val transient：
    - `18 -> 30`
- 说明新增 branch 已经真实进入专项 loss，而不是 `v20` 那种零命中增量

影响：

- 但相对 `v19`，`v21` 仍然没有把目标方向推正：
  - default val：
    - `+0.008857 dB`
  - 新 proxy 自己：
    - `-0.076726 dB`
  - broad near-real speech probe overall：
    - `-0.042540 dB`
  - `near_real_guodegang_transient_probe_v1` overall：
    - `-0.122561 dB`
- stage2-relative 的关键 friend-side锚点也全部低于 `v19`：
  - `friend_raw`
  - `0003`
  - `0004`
  - `0006`
- `speech_followup_gate_vs_v19` 直接失败：
  - `speech_probe_overall_floor`
  - `speech_probe_friend_raw_floor`
  - `anchor_0003_gain_floor`
  - `anchor_0004_gain_floor`
  - `anchor_0006_regression_floor`
- 甚至 guodegang focused probe 相对 `v19` 也全线回退：
  - overall
  - family
  - `0006`
  - `anchor_120s`
  - `absent_480s`

处理：

- 本轮保留：
  - selector `extra` branch 这层基础设施
- 但不保留：
  - `v21` checkpoint

后续要求：

1. 以后凡是新 proxy 已经显式命中 selector，也仍然必须单独核对：
   - 该 proxy 相对当前基座是否真的转正
   - broad near-real 的关键锚点是否同步不回退
2. 如果出现：
   - selector 命中数明显增加
   - 但 proxy 自己和 near-real 关键锚点仍同时低于当前基座
   那问题就不再是“selector 没接上”，而应改判为：
   - “proxy 本身方向不够对，不能继续靠加预算硬推”
3. 下一步若继续补 friend-side，优先先重搜更窄、更贴近：
   - `0003 / 0004`
   的 proxy；
   不要先对这批 `v21` 样本继续扫权重、扫 epoch、扫 lr。

### 86. 如果一个 friend-side objective 在更严格的 exact samplewise-order-pass proxy 上仍然低于当前基座，那问题就不再是“proxy 太宽”，而是当前 objective / proxy 语义本身仍然不对；`v21` 在 `v22` exact full / nonfull proxy 上依然回退，说明继续缩窄同类 proxy 也不足以救活这条线

现象：

- 本轮把 friend-side proxy 搜索进一步收紧为：
  - 单样本先满足 `v12 > v19 > v8`
  - 再搜索 metadata 子集
- 对应地：
  - `val/default` shared speech rows 从 `237` 收缩到 `38`
  - `train/default` 也有 `176` 条 single-sample order-pass speech rows
- 基于这套 exact 搜索又落了两类 proxy：
  - exact full：
    - train `10`
    - val `4`
  - exact nonfull：
    - val `7`
- 但相对 `v19`：
  - `v21` 在 exact full 上仍是：
    - `-0.065412 dB`
  - `v21` 在 exact nonfull 上仍是：
    - `-0.156167 dB`

影响：

- 这说明 `v21` 的失败已经不能再归因于：
  - “proxy 还不够窄”
  - 或“proxy 里还混了太多单样本方向相反的行”
- 更准确的解释应改写为：
  - 当前 `transient_extra` 这条 friend-side objective
  - 即便只看 exact、single-sample order-pass 的 full / nonfull 子集
  - 也仍然没有把优化方向推到 `v19` 之上

处理：

- 本轮保留：
  - `samplewise-order-pass` exact proxy 搜索链
  - `sample_ids_file` manifest 构建链
- 但不保留：
  - 直接沿当前 `v21` 逻辑开 `v22` 训练

后续要求：

1. 以后若某条 friend-side objective 在 exact full / nonfull proxy 上仍低于当前基座，
   就不要再把下一步写成：
   - “继续缩窄 proxy 再试一次”
2. 这种情况下应直接把问题升级为：
   - objective / proxy 语义不匹配
   - 需要换 proxy 形态或换 loss 归属
3. 对当前这条线，下一步优先应改：
   - 更贴近 `0003 / 0004` 的 residual-transient / speech-leak 语义
   - 或不再继续只挂在 `transient_extra`
   而不是继续：
   - 同类 full/high-transient proxy 的宽窄扫描

### 87. `near_real_0004` 不能默认并入同一个 transient-only friend objective；本轮 semantic split 已显示它更像 `target_full + clean-pool + higher-gain + lower-transient` 的 speech-leak 语义，继续把 `0003 / 0004` 合并进单一 `transient_extra`，即使 exact proxy 也仍压不过 `v19`

现象：

- 本轮给 `search_synthetic_proxy_candidates.py` 补了 low-side bucket：
  - `gain_le_q50`
  - `transient_le_q50`
  - `transient_lt_q67`
- 然后把 friend-side exact proxy 明确拆成两族：
  - `0003-like residual-transient`：
    - train `10`
    - val `4`
  - `0004-like speech-leak`：
    - train `11`
    - val `3`
- 其中 `0004-like` 这族在当前 synthetic order-pass 行里并不落在：
  - `nonfull`
  - 或另一批 high-transient
  之上；
  它反而更像：
  - `target_full`
  - clean speech pool
  - higher-gain
  - lower-transient
- 但即便这样拆开后，`v21` 相对 `v19` 仍然：
  - residual-transient exact：`-0.065412 dB`
  - speech-leak exact：`-0.020621 dB`

影响：

- 这说明当前问题已经不能再描述成：
  - “只要把 `0004-like` 再收进同一个 transient 分支就会好”
- 更准确的描述应改成：
  - `0003 / 0004` 虽然都属于 friend-side speech overlap 回退
  - 但它们不是同一种 synthetic proxy 语义
  - 尤其 `0004-like` 不应默认按 transient-only 目标去吸收

处理：

- 本轮保留：
  - semantic-split exact proxy 搜索与 manifests
- 但不保留：
  - 继续把 `0003 / 0004` 合并成一个 single-branch friend objective 的写法

后续要求：

1. 以后若要继续补 friend-side `0003 / 0004`，至少先分两条语义：
   - residual-transient-like
   - speech-leak-like
2. 不要再把 `0004-like` 默认写成：
   - “另一批 transient proxy”
3. 新训练若要开，应优先考虑：
   - `0003-like` 仍挂 transient-adjacent 分支
   - `0004-like` 单独挂 interference / leak 侧归属
   而不是继续：
   - 两者并到同一个 `transient_extra`

### 88. 即使已经把 `0003-like` / `0004-like` 分别接到 `transient_extra` 和 `interference_extra`，one-shot semantic split 也不等于 friend-side objective 已经转正；`v24 / v25` 证明“语义拆开”只是开始，不是完成

现象：

- 本轮已把 friend-side 两条语义真正接进训练：
  - `v24`:
    - train transient `55 / 109`
    - train interference `51 / 109`
  - `v25`:
    - train transient `63 / 109`
    - train interference `62 / 109`
- 说明这批 friend-side proxy：
  - 不是 `v20` 那种零命中增量
  - 已真实进入 active selector
- 但相对 `v19`：
  - `v24 semantic-split proxy = -0.091072 dB`
  - `v25 semantic-split proxy = -0.152489 dB`
  - `v25 residual-transient exact = -0.176585 dB`
  - `v25 speech-leak exact = -0.120362 dB`
  - `v24 near_real_friend_speech_probe = -0.041770 dB`
  - `v25 near_real_friend_speech_probe = -0.037164 dB`

影响：

- 这说明当前问题已经不能再主要解释成：
  - selector 没接上
  - 或 `0003 / 0004` 还没有拆语义
- 更准确的说法应改成：
  - 当前 semantic split 的 objective / proxy 语义仍不够对
  - 即便已经分挂到不同 loss 归属
  - 也还没有把 friend-side 的 exact proxy 和 near-real bucket 一起推正

处理：

- 本轮保留：
  - semantic split 训练入口本身
  - `v24 / v25` 这批结果作为反例与边界
- 但不保留：
  - 把 `v24 / v25` 当成新候选继续放大预算

后续要求：

1. 以后即使已经把多个语义分挂到不同 selector，也不能默认写成：
   - “objective 已经对了”
2. 若 exact proxy 和 near-real friend bucket 仍同时低于当前基座，
   结论应直接升级为：
   - objective / proxy 语义本身仍需重做
3. 对当前这条线，不再优先做：
   - `v24 / v25` 的权重、epoch、lr 微扫

### 89. 把 `0003-like` 或 `0004-like` 单独 carve-out，也不等于至少能救回一半问题；`v26 / v27` 证明两侧 branch-local objective 当前都还不够稳

现象：

- `v26 residual-only` 相对 `v19`：
  - `residual-only proxy = -0.201198 dB`
  - `near_real_friend_speech_probe = -0.049491 dB`
  - `near_real_guodegang_speech_probe = +0.003146 dB`
- `v27 speech-leak-only` 相对 `v19`：
  - `speech-leak-only proxy = -0.144539 dB`
  - `near_real_friend_speech_probe = -0.044400 dB`
  - `near_real_guodegang_speech_probe = -0.004776 dB`

影响：

- 这说明：
  - `0003-like residual-transient`
    当前还不能被视为单独可保留的安全训练入口；
  - `0004-like speech-leak`
    当前也还没有形成稳定的 interference/leak-side 正收益；
  - 尤其后者已经开始把 `guodegang` 侧已有收益一起回吐

处理：

- 本轮不保留：
  - `v26`
  - `v27`
- 当前只把它们记为：
  - 单侧 carve-out 已验证过，但都未转正

后续要求：

1. 以后不要把“先单独 carve-out 一侧试一下”默认理解成：
   - 至少能保住另一侧不坏
2. 如果单侧 carve-out 仍然同时表现为：
   - 自己的 proxy 为负
   - friend-side near-real bucket 也为负
   结论应直接写成：
   - 这一侧的 branch-local objective 还不够对
3. 对当前这条线，下一步优先应继续改：
   - speech-leak / residual-transient 的 proxy 语义或 guardrail
   而不是继续沿当前 `v26 / v27` 直接放大预算

### 90. 如果 synthetic proxy 的正确边界已经依赖 exact `samplewise-order-pass` 子集，就不能再只用宽元数据 selector 近似；需要显式 sample-id selector，否则会把已排除的坏样本重新打回训练目标

现象：

- `v28` 已暴露：
  - metadata-only 宽集合即使长得像 speech-leak，
  - 也可能把 `v19 > v12 > v8` 的坏样本重新混进来；
- 本轮 `v29` 又进一步验证：
  - 即便 exact manifest 已经收成 `samplewise-order-pass`
  - 如果训练侧还只能靠 recipes / patterns / gain / transient 之类宽 selector 近似，
  - 实际 objective 仍然会偏回 “宽 region”，而不是 exact 子集本身。

处理：

- 本轮新增并保留：
  - `scripts/train/train_stft_mask_baseline.py`
    - `--loss-*-focus-sample-ids-file`
  - `src/tse_prefix/pipeline/loss_selectors.py`
    - `focus_sample_ids`
- 同时给 manifest 构建链补了：
  - `scripts/data/build_metadata_focused_manifest.py --include-derived-metrics`
  - 使 exact allowlist manifest 也能保留新的派生声学字段。

结果：

- `v29` 的 `interference_extra` 命中已精确对齐到：
  - train `+21`
  - val `+3`
- 这次可以排除：
  - selector 没接上
  - 宽 metadata 边界导致命中错样本
- 但结果仍然是：
  - default `-0.004999 dB`
  - exact speech-leak proxy `-0.142498 dB`

影响：

- 以后当 proxy 正确性已经依赖 exact samplewise 子集时，不能再写成：
  - “先用宽 metadata selector 近似一下，方向大概一样”
- 更严格的要求应改成：
  - 要么 selector 能直接命中 exact sample-id；
  - 要么就承认当前 objective 还没有真正对准 proxy。

后续要求：

1. 遇到 `samplewise-order-pass` 才能站住的 proxy 时，优先保留：
   - exact sample-id selector
   - exact manifest
2. 如果 exact sample-id selector 已经接通，但结果仍然不转正，
   结论应直接升级为：
   - objective / proxy 语义本身仍需重做
3. 不再把“宽 selector 近似失败”误归因成：
   - plumbing 问题
   - 或命中率还不够

### 91. 即使把 `0004-like speech-leak` 再重写成 `high similarity + low target transient + low interference transient` 的 mixed-pattern exact family，也不代表当前 interference-extra objective 已经足够；`v30` 证明 sample family 更像了，训练方向仍然可能不对

现象：

- 本轮在 `samplewise-order-pass` 搜索里新增：
  - `interference_transient_presence_minus_mid_db_mean`
  - `target_interference_logspec_cosine`
- 因而首次搜到一条不同于 `v23 / v29` 的新 family：
  - clean pool
  - higher gain
  - higher similarity
  - lower target transient
  - lower interference transient
  - `target_full + absent_head + absent_tail`
- 基于这条 family 落盘：
  - train exact `7`
  - val exact `3`
- 并开出：
  - `v30 = legacy_transient_leakguard_probe_v30_v19_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_ft1`

处理：

- 训练侧继续保留 `v19` 基座；
- 新 family 挂到：
  - `interference_extra_focus_sample_ids`
- 这次 selector 命中已明确增加到：
  - train interference `58 / 97`
  - val interference `21 / 29`

结果：

- 相对 `v19`：
  - default `+0.015689 dB`
  - `v30 exact proxy = -0.141952 dB`
  - near-real speech probe overall `-0.053396 dB`
  - near-real `speech_leak_like (0004) = -0.035911 dB`
- 新 exact family 的 full 行：
  - `val_000075`
  - 仍明显回退 `-0.340267 dB`

影响：

- 以后不能把：
  - “搜索结果终于更像 speech-leak 了”
  直接等价成：
  - “当前 objective 已经接近正确”
- `v30` 更准确的解释应写成：
  - sample family 的确比旧 `v23 / v29` 更换了一层语义；
  - 但当前 interference-extra objective / guardrail 形式仍不足以把这类样本训练成正收益。

后续要求：

1. 不继续围绕这条 `v30` family 扫权重、epoch、lr。
2. 后续若还要补 `0004-like speech-leak`，优先改：
   - objective 形式
   - leak-specific guardrail
   - 或更明确的 branch-local loss 归属
3. 不再把“又找到一条更像的 exact family”误写成：
   - objective 已基本闭环

### 92. 即使把 interference objective 从整段预测投影比改成残差投影比，也不代表 `0004-like speech-leak` 已经被补正；`v31` 证明这类 mode swap 只能部分缩小 exact proxy 回退，还可能把代价转移到 default 或其他锚点

现象：

- 本轮 `v31` 保持：
  - `v30` exact family
  - `v19` 基座
  - selector 命中边界
  全部不变；
- 唯一改动是：
  - `interference_loss_mode = residual_projection_ratio`
- 结果相对 `v19`：
  - default `-0.011286 dB`
  - exact proxy `-0.082113 dB`
  - near-real overall `-0.054149 dB`
- 结果相对 `v30`：
  - exact proxy `+0.059839 dB`
  - near-real overall `-0.000753 dB`

处理：

- 工程上保留：
  - `interference_projection_loss(..., mode=...)`
  - `--loss-interference-mode`
- 新增模式：
  - `residual_projection_ratio`
  只看 `prediction - target` 里的 interference-aligned 残差，而不再直接约束整段预测。

结果：

- `v31` 的确把 `v30` exact family 三条都往正方向推了一点；
- 但：
  - `v19` 基线仍未被超过；
  - `near_real_0004` 仍为负；
  - `guodegang / 0006` 还出现了新的回吐。

影响：

- 以后不能把：
  - “projection target 换对了”
  直接等价成：
  - “speech-leak objective 已经基本成形”
- 更准确的理解应写成：
  - residual-projection 只是一个更像样的 primitive；
  - 但若没有额外 leak-specific guardrail 或分侧保护，
  - 它仍可能只是把代价从 exact speech-leak proxy 挪到 default / 其他锚点。

后续要求：

1. 不继续围绕 `v31` 直接扫权重、epoch、lr。
2. 后续若继续补 `0004-like speech-leak`，优先试：
   - leak-specific guardrail
   - friend-side 与 `guodegang / 0006` 的解耦保护
   - 或只在 speech-leak exact family 上叠加更局部的 residual constraint
3. 不再把“objective mode 换成 residual projection 后 exact proxy 变好了一些”误写成：
   - 整条路线已经可保留

### 93. 即使把 residual objective 局部化到 `interference_extra`，也不代表 `0004-like speech-leak` 已经基本补正；`v32 / v33` 证明“全局替换过宽”只是问题的一部分，extra weight 也不是当前主瓶颈

现象：

- `v32` 首次把：
  - base interference
  - interference_extra
  做成了真正 branch-local 的不同 objective；
- 其中：
  - base interference 继续保留 `prediction_projection_ratio`
  - 只有 `interference_extra` exact speech-leak family 改成 `residual_projection_ratio`
- `v32` 相对 `v31` 已明显更稳：
  - default `+0.030320 dB`
  - near-real overall `+0.003684 dB`
- 但相对 `v19` 仍然：
  - exact proxy `-0.121204 dB`
  - near-real `speech_leak_like (0004) = -0.041680 dB`
- 后续 `v33` 再把：
  - `interference_extra_weight = 0.0075 -> 0.015`
  也没有带来新的结构性改善。

处理：

- 工程上保留：
  - branch-local selector weights
  - `interference_extra_weight`
  - `interference_extra_loss_mode`
  - `interference_extra_projection_ratio`
- 并通过 `v32 / v33` 明确验证：
  - localized residual extra
  - 以及更高 extra weight
  的真实边界。

结果：

- `v32` 证明：
  - “全局 residual 替换过宽”这件事确实存在；
  - 局部化后，default / near-real 稳定性明显优于 `v31`
- `v33` 又证明：
  - 当前瓶颈不在 extra branch 的 weight 还太小；
  - 至少在这一级额外放大下，exact / near-real 形态几乎不动。

影响：

- 以后不能把：
  - “把 residual objective 局部化到 exact family”
  直接等价成：
  - “speech-leak 这条线已经只差一点 weight”
- 更准确的理解应改写为：
  - 过宽的全局 interference objective 确实是问题之一；
  - 但即便修掉这点，`0004-like speech-leak` 仍需要更具体的 guardrail / 解耦约束；
  - 简单继续推 extra weight，大概率只是低价值重复试验。

后续要求：

1. 不继续围绕 `v32 / v33` 扫更多 extra weight。
2. 保留 branch-local interference-extra split 这套能力，作为后续实验底座。
3. 后续若继续补 `0004-like speech-leak`，优先试：
   - 只在 speech-leak exact family 上触发的 leak-specific guardrail
   - friend-side 与 `guodegang / 0006` 的显式解耦保护
   - 或更贴近“只压泄漏残差、不动目标保留”的局部约束

### 94. 即使 exact speech-leak family 已经被推到正增益，也不代表 near-real 就会一起转正；`v34` 证明 weighted SI-SDR guard 很容易把这条线推成 exact-family overfit

现象：

- `v34` 在 `v32` 基础上给 `interference_extra` exact family 叠加：
  - `interference_extra_guard_sisdr_weight = 0.0002`
- 结果相对 `v19`：
  - default `+0.058461 dB`
  - exact proxy `+0.026174 dB`
  - near-real overall `-0.071357 dB`
  - `guodegang / 0006 = -0.122081 dB`

处理：

- 工程上保留：
  - `weighted_sisdr_loss(...)`
  - `interference_extra_guard_sisdr_weight`
- 并只把这条 guardrail 作用于：
  - exact speech-leak family

结果：

- exact proxy 的确第一次转正；
- 但 near-real 同时更差，尤其：
  - `guodegang_anchor_120s`
  - `guodegang_absent_480s`
  都明显回退。

影响：

- 以后不能把：
  - “exact family 已转正”
  直接等价成：
  - “真实 speech-leak 已被修正”
- 更准确的理解应写成：
  - 当前这类 exact-family weighted guard 很容易把模型推向 synthetic exact overfit，
  - 而不是真正提升 near-real。

后续要求：

1. 不继续沿这条 exact-family sisdr guard 直接扫权重。
2. 后续若要继续保留这类 guard，必须同时通过：
   - near-real speech probe
   - 尤其 `guodegang / 0006` 子门

### 95. `guodegang_anchor_proxy_v1` 当前不能直接当作 friend-side speech-leak 线的 decoupling protection；`v35` 证明 synthetic anchor 更强，真实 `guodegang_anchor_120s` 反而可能更差

现象：

- 本轮 `v35` 把：
  - `guodegang_anchor_proxy_v1`
  并入 `v34` 的训练集，
  并通过：
  - `transient_extra_focus_sample_ids = guodegang_anchor_proxy_v1`
  试图给 `0006` 加一条显式保护。
- 结果相对 `v19`：
  - default `+0.061993 dB`
  - exact proxy `+0.152425 dB`
  - near-real overall `-0.078793 dB`
  - `near_real_guodegang_anchor_probe_v1 = -0.352486 dB`

处理：

- 生成了：
  - `sample_ids_guodegang_anchor_proxy_v1_{train,val,all}.txt`
  - `train/val_manifest_v35_v19_plus_friend_reverse_guardrail_proxy_v8_plus_guodegang_anchor_proxy_v1.jsonl`
- 并把它们真实并入训练，而不是只停留在文档假设里。

结果：

- synthetic friend-side exact proxy 继续变强；
- 但真实 `guodegang_anchor_120s` 不但没被保护住，
  反而比 `v34` 还更差。

影响：

- 以后不能把：
  - “某个 synthetic `guodegang_anchor_proxy` 在训练里被显式照顾了”
  直接等价成：
  - “真实 `guodegang_anchor_120s` 已有保护”
- 更准确的理解应写成：
  - 当前 `guodegang_anchor_proxy_v1` 对这条 friend-side speech-leak 线而言，
  - 仍是高风险的错配保护项。

后续要求：

1. 不继续并更多同类 synthetic `guodegang` proxy 充当保护项。
2. 下一步若还要做 decoupling protection，优先考虑：
   - real / near-real gate 优先
   - 或重新设计更贴近 `guodegang_anchor_120s` 的保护代理

### 96. 即使 exact target_full 与 near-real `speech_leak_like (0004)` 都变好，也不代表 friend-side speech-leak follow-up 已可保留；`friend_speech_leak_followup_gate` 证明真正卡口可能只剩 `guodegang_anchor / absent` 两条 real floor

现象：

- 本轮已把 friend-side follow-up gate 正式固化到：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- 对 `v35` 运行后可见：
  - relative to `v34`：
    - default `+0.003533 dB`
    - exact target_full `+0.102182 dB`
    - near-real `speech_leak_like (0004) = +0.022676 dB`
  - relative to `v32`：
    - exact target_full `+0.204893 dB`
    - near-real `speech_leak_like (0004) = +0.018996 dB`
- 但两种 reference 下都仍然：
  - `overall_pass = false`
  - failed rules 只剩：
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`

处理：

- 已补跑并落盘：
  - `friend_speech_leak_followup_gate_vs_v34.json`
  - `friend_speech_leak_followup_gate_vs_v32.json`
- 同时保留：
  - `v34 vs v32` 的 gate 结果
  作为这条线的前序对照。

结果：

- `v34` 证明：
  - exact-family 推正并不等于能过 friend-side real gate；
- `v35` 又进一步证明：
  - 即使 `0004-like speech-leak` 也开始回升，
  - 只要 `guodegang_anchor / absent` 两条 real floor 还在回退，
  - 这条 candidate 仍应直接判掉。

影响：

- 以后不能把：
  - “speech-leak side 指标终于变好了”
  直接等价成：
  - “这条 follow-up 已经能保留”
- 更准确的 keep/drop 口径应写成：
  - 先过 friend-side follow-up gate；
  - 尤其先守住：
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`
  - 之后才有资格讨论 exact / `0004-like speech-leak` 的局部收益。

后续要求：

1. 后续这条线所有新 candidate 默认先跑 `friend_speech_leak_followup_gate`。
2. 不再把“`exact target_full` 或 `0004-like speech-leak` 转好”单独当作放行依据。
3. 若下一步继续推进，优先补的是：
   - 直接面向 `guodegang_anchor / absent` real floor 的 guardrail
   - 或更贴近真实锚点的保护代理，而不是继续并新的 synthetic `guodegang` proxy

### 97. 如果 `anchor` 或 `absent` 保护项仍只能并进 base transient / absent 分支同权计算，就很容易把“想保护某个 real floor”误做成“再次把 base branch 搅宽”；`v35` 暴露的不是只差一个新 proxy，而是缺真正的 branch-local extra weight 通道

现象：

- `v35` 虽然把：
  - `transient_extra_focus_sample_ids = guodegang_anchor_proxy_v1`
  接到了 selector；
- 但当时训练图里并没有：
  - `transient_extra_weight`
  - `absent_extra_weight`
  这类独立权重；
- 实际效果仍等价于：
  - 保护样本被并回 base transient / absent 分支一起算。

处理：

- 本轮已补齐：
  - `transient_extra_sample_weights`
  - `absent_extra_sample_weights`
  - `transient_extra_weight`
  - `absent_extra_weight`
- 并同步补齐：
  - train / eval summary
  - selector metrics
  - smoke 验证

结果：

- 现在已经可以真正做：
  - `anchor -> transient_extra`
  - `absent -> absent_extra`
  的分侧小权重保护；
- 不必再把：
  - `guodegang_anchor_proxy_v1`
  或
  - `guodegang_absent_proxy_v3_strict`
  粗暴并回 base 分支。

影响：

- 以后不能把：
  - “extra selector 已经命中了”
  直接等价成：
  - “这条保护项已经是独立可控的 branch-local guardrail”
- 更准确的判断应写成：
  - 只有当 extra selector 对应的 loss 也有独立 weight / 独立 summary / 独立 gate 观察位时，
  - 才算真正具备可控的 branch-local 保护能力。

后续要求：

1. 后续凡是涉及 `anchor / absent` 保护项的实验，默认优先走：
   - `transient_extra`
   - `absent_extra`
   这两条独立分支。
2. 不再把新的 `anchor / absent` proxy 直接并进 base transient / absent 分支，除非实验目标就是验证“宽分支是否故意更强”。
3. 下一步若继续推进，优先做：
   - 分侧轻量 protection smoke
   - 然后直接用 friend-side follow-up gate 裁决是否值得保留

### 98. 只把 `guodegang_anchor_proxy_v1` 拆到 `transient_extra`，并不能自然变成可保留的 real-floor 保护；`v36` 证明这条 `anchor transient-extra only` 路线会同时伤到 exact speech-leak side 与 `guodegang` real floor

现象：

- `v36` 是第一条真正使用新 plumbing 的分侧 smoke：
  - 基座是 `v32`
  - 保留现有 friend-side `interference_extra` exact speech-leak branch
  - 新增：
    - `transient_extra = guodegang_anchor_proxy_v1`
    - `transient_extra_weight = 0.001`
- 结果 relative to `v19`：
  - default `+0.042394 dB`
  - exact proxy overall `-0.038284 dB`
  - exact `target_full = -0.322388 dB`
  - near-real `speech_leak_like (0004) = -0.042726 dB`
  - near-real `guodegang_anchor_120s = -0.300635 dB`
  - near-real `guodegang_absent_480s = -0.094534 dB`
- relative to `v32` 的 `friend_speech_leak_followup_gate`：
  - `overall_pass = false`
  - failed rules：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`

处理：

- 已将 `v36` 作为明确失败样本落盘，不进入 keep 候选。

结果：

- 这次失败不只是：
  - `guodegang_anchor / absent` 还没守住；
- 而是连：
  - exact `target_full`
  - near-real `0004-like speech-leak`
  也一并回退。

影响：

- 以后不能把：
  - “把某个 `anchor proxy` 从 base transient 拆到 `transient_extra`”
  直接等价成：
  - “real floor 保护会更稳”
- 更准确的理解应写成：
  - `guodegang_anchor_proxy_v1` 对 real `guodegang_anchor_120s`
    仍然是高风险错配保护项；
  - `anchor transient-extra only`
    不是这条 friend-side follow-up 的 keep 路径。

后续要求：

1. 不继续扫 `guodegang_anchor_proxy_v1` 的 `transient_extra_weight`。
2. 后续若还做 `guodegang` 保护，优先补：
   - 新 objective / branch
   - 或更贴近 real / near-real gate 的保护代理
3. 所有新 candidate 仍默认先过 `friend_speech_leak_followup_gate`。

### 99. 只要 sample-id 列表文件可能来自 Windows / PowerShell 落盘，就不能假设它一定是不带 BOM 的 UTF-8；否则 selector 首个样本会 silently 失配

现象：

- `sample_ids_guodegang_anchor_proxy_v1_{train,val,all}.txt`
  原先带有 UTF-8 BOM；
- 旧的 sample-id loader 使用 `encoding=\"utf-8\"` 读取时，
  会把首个样本读成：
  - `\\ufefftrain_000029`
- 这会导致：
  - selector 看起来“已命中 sample-id 文件”
  - 但第一条样本实际上不会匹配到 manifest 中的 `train_000029`

处理：

- 已把：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/data/build_metadata_focused_manifest.py`
  的 sample-id 读取改为 `encoding=\"utf-8-sig\"`
- 同时已将：
  - `sample_ids_guodegang_anchor_proxy_v1_train.txt`
  - `sample_ids_guodegang_anchor_proxy_v1_val.txt`
  - `sample_ids_guodegang_anchor_proxy_v1_all.txt`
  重写为无 BOM UTF-8
- 额外 smoke 已确认：
  - 新 summary 中的首个 sample_id 已恢复为 `train_000029`

结果：

- 后续 selector / manifest builder 即使遇到 BOM 文件，也不会再把首个样本读脏。

影响：

- 以后不能把：
  - “sample-id 文件行内容肉眼看起来正常”
  直接等价成：
  - “训练时 selector 一定能命中”
- 更准确的检查方式应写成：
  - sample-id loader 默认对 BOM 容错
  - 并在 summary / smoke 中确认首个样本没有 `\\ufeff`

后续要求：

1. 所有 newline-delimited sample-id 文件默认按 `utf-8-sig` 容错读取。
2. 新生成的 sample-id 文件优先写成无 BOM UTF-8。
3. 遇到 selector 命中率异常时，先排查 BOM / 编码问题，再判断是语义筛选失败。

### 100. 如果一个 proxy family 在 base manifest 中本来就已经完整存在，再去重建“union manifest”很容易让人误以为问题出在 coverage；但像 `v37` 这种 follow-up，真正变化的其实只是 objective routing

现象：

- 本轮为 `guodegang_absent_proxy_v3_strict` 做 `v37` 时，
  曾额外构造：
  - `train_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
  - `val_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
- 但随后核对发现：
  - train 相对 `v32` base manifest：
    - `97 vs 97`
    - `same_order = true`
    - `same_set = true`
  - val 相对 `v32` base manifest：
    - `29 vs 29`
    - `same_order = true`
    - `same_set = true`

处理：

- 已把这条事实明确写入 `v37` 日报和总览：
  - `guodegang_absent_proxy_v3_strict`
    并不是“新并入的样本族”；
  - 它实际上早已完整存在于 `v32` 的 base manifest 中。
- 同时补了新的 branch-local objective：
  - `reconstruction`
  - `reconstruction_extra`
  用来显式表达：
  - 对一组 hard `target_full` 行的 target reconstruction 拉力
  而不是继续误用 `absent_interval_l1`

结果：

- `v37` 的变化来源现在可以被准确表述为：
  - objective re-routing
  - 而不是 manifest coverage 扩充
- 这也解释了为什么：
  - `v37` 能把 `guodegang_anchor / absent` real floor
    从 `v36` 的更差位置往回拉一点；
  - 但同时又会伤到：
    - exact `target_full`
    - near-real `0004-like speech-leak`

影响：

- 以后不能把：
  - “又做了一份 plus / union manifest”
  直接等价成：
  - “这条 follow-up 终于给模型喂到了之前没有的样本”
- 更准确的检查顺序应写成：
  - 先核对新 manifest 与当前 base manifest
    是否真有新增 sample-id
  - 如果没有，
    就把实验解释聚焦到：
    - objective routing
    - branch-local weighting
    - selector coverage

后续要求：

1. 后续所有 plus / union manifest，在起正式训练前都先核对：
   - `same_set`
   - `same_order`
   相对当前基座是否真的有变化。
2. 若 manifest 完全等价，就不要再把实验命名或结论写成“扩样 follow-up”。
3. 像 `guodegang_absent_proxy_v3_strict` 这种早已存在于基座的 hard `target_full` 行，优先从 objective routing / branch-local objective 角度设计 follow-up。

### 101. 如果 absent-side objective 直接作用在与 friend-side exact branch 共用的 hard `target_full` 行上，单纯继续加大 `interference_extra_weight` 并不能把 speech-leak side 拉回；`v38` 证明这不是一个“再平衡权重不够大”的简单问题

现象：

- `v37` 已说明：
  - `guodegang_absent_proxy_v3_strict`
    接到 `reconstruction_extra`
    会把 `guodegang` 两条 real floor 往回拉一点；
  - 但同时会伤到：
    - exact `target_full`
    - near-real `speech_leak_like (0004)`
- 因此本轮又做了 `v38`：
  - 把 absent-side 改成更轻的 `waveform-only reconstruction_extra`
  - 同时把：
    - `interference_extra_weight = 0.0075 -> 0.03`

处理：

- `v38` 继续从 `v32` 起步，
  直接用 `v32` base manifest，
  避免 manifest coverage 因素混入解释。
- 然后只改变：
  - `reconstruction_extra` 的形式与强度
  - `interference_extra_weight`

结果：

- `v38` 相对 `v37`：
  - default 更好
  - `guodegang_anchor / absent` 也都略有回升
- 但：
  - exact `target_full` 更差
  - near-real `speech_leak_like (0004)` 也更差
- 相对 `v32` 的 friend-side follow-up gate 仍然：
  - `overall_pass = false`
  - failed：
    - `exact_target_full_gain_floor`
    - `speech_leak_like_gain_floor`
    - `guodegang_anchor_floor`
    - `guodegang_absent_floor`

影响：

- 以后不能把：
  - “absent-side objective 已经更轻了”
  - “friend-side exact branch 也已经提权了”
  直接等价成：
  - “这条 trade-off 接下来只差继续扫一下 weight”
- 更准确的理解应写成：
  - 一旦 absent-side objective
    直接改写了 shared hard `target_full` 区域的优化方向，
  - friend-side `interference_extra`
    就未必能通过单纯加权把它抵回来

后续要求：

1. 不继续围绕 `v37 / v38` 这族配置扫：
   - `interference_extra_weight`
   - 或当前 `reconstruction_extra` 配比
2. 后续若仍做 absent-side protection，优先做：
   - 更细粒度的 absent proxy carve-out
   - 或避免直接作用于 shared hard `target_full` 行的 objective
3. 所有“再平衡”实验都应先问清：
   - 当前冲突是 branch weight 不够，
   - 还是 objective 本身已经在改写共享区域

### 102. 即使把 absent-side 从 shared rows 改成更窄的 metadata carve-out，也不能把 synthetic carve-out 局部转正直接当成 real gate 已被修好；`v39` 证明这类 clean absent proxy 只够说明“方向更干净”，还不够说明“真实门已过”

现象：

- `v39` 没再直接复用 `guodegang_absent_proxy_v3_strict` 整族 shared hard `target_full` 行；
- 而是切到一批更窄的 metadata carve-out：
  - `target_clean_speech`
  - `target_full`
  - `speech_interference_clean_pool`
  - `target_present_ratio >= 0.95`
  - `target_transient_presence_minus_mid_db_mean <= -9.231693`
  - `interference_transient_presence_minus_mid_db_mean <= 5.840138`
- 这批 `v5 cleancarve` 子集相对 `v19` 的 synthetic summary 为：
  - `+0.181394 dB`
- 但同一 checkpoint 在 real / near-real 侧仍然：
  - exact `target_full = -0.467426 dB`
  - `speech_leak_like (0004) = -0.086908 dB`
  - `guodegang_anchor_120s = -0.099820 dB`
  - `guodegang_absent_480s = -0.057543 dB`
- 相对 `v32` 的 `friend_speech_leak_followup_gate` 仍：
  - `overall_pass = false`

处理：

- 已补写 `v39` 日报与 gate 结果：
  - `reports/daily/2026-03-19_v39_absent_recon_cleancarve_followup.md`
  - `reports/eval/compare_v19_vs_v39_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`

结果：

- 当前可以确认：
  - 更窄的 clean absent metadata carve-out 确实比直接作用 shared rows 更“干净”；
  - 但它的 synthetic proxy 局部转正，并不会自动迁移成：
    - friend-side exact speech-leak 转正
    - 或 `guodegang anchor / absent` 两条 real floor 守住

影响：

- 以后不能把：
  - “某个 absent carve-out 在 synthetic 自定义 proxy 上转正了”
  直接等价成：
  - “这条 absent-side 保护已经可保留”
- 更准确的解释应写成：
  - synthetic carve-out 只说明 selector / 代理方向可能更贴近目标；
  - 是否值得保留，仍必须回到：
    - exact `target_full`
    - `speech_leak_like (0004)`
    - `guodegang_anchor`
    - `guodegang_absent`
    这几条 gate 来裁决

后续要求：

1. 后续所有 absent-side metadata carve-out，都必须同步跑 real / near-real gate，不能只看自定义 proxy summary。
2. 不继续围绕当前 `v39` 的 metadata 上界或权重做低价值细扫。
3. 下一步若还做 absent-side follow-up，优先：
   - 继续排查 `v5 cleancarve` 内与 friend-side exact 冲突的子集；
   - 或补更贴近 near-real `guodegang_absent` 的保护代理；
   - 或改成不直接改写 target reconstruction 方向的 objective。

### 103. metadata carve-out 即使表面上和 friend-side exact family 不是同一条分支，也可能在 selector 交叉后重新命中 exact 样本；`v39 -> v40` 预备说明必须显式核对 overlap，而不能只看“这次没有直接传 exact sample-id”

现象：

- `v39` 的 absent-side `reconstruction_extra`
  没有直接使用 friend-side exact 的 sample-id 文件；
- 但按真实 selector 口径回放后发现，
  它仍然命中了：
  - train：
    - `train_000001`
    - `train_000432`
    - `train_001225`
    - `train_001610`
  - val：
    - `val_000075`
- 其中 `val_000075`
  正是 `v39` 在 exact `target_full` summary 里的主要回退点：
  - `sisdr_delta_db = -0.467426 dB`

处理：

- 已生成一组去 overlap 的 `v40` 预备 allowlist：
  - `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_train.txt`
  - `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_val.txt`
  - `data/synthetic/sample_ids_v40_absent_reconstructionextra_v6_cleancarve_noexactoverlap_all.txt`
- 并补写预备日报：
  - `reports/daily/2026-03-19_v40_absent_cleancarve_noexactoverlap_prep.md`

结果：

- 当前已经能把“metadata carve-out 大方向没问题”和“selector 交叉后误撞 exact family”这两类问题拆开；
- 下一条最直接可测的 follow-up
  就是不改 loss 图，
  先把 overlap 显式剔掉。

影响：

- 以后不能把：
  - “这次 absent-side 没直接传 exact sample-id 文件”
  直接等价成：
  - “它一定没有碰到 friend-side exact family”
- 更准确的检查顺序应写成：
  - 先回放真实 selector 命中集合；
  - 再和当前所有关键 sample-id family 做交集；
  - 最后再判断这条 carve-out 是方向不对，还是只是 selector crossfire。

后续要求：

1. 只要新分支同时存在：
   - metadata selector
   - 与其他 branch 的 sample-id family
   就必须显式核对 overlap。
2. 后续所有 absent-side carve-out 预备，都至少落一份：
   - kept ids
   - excluded overlap ids
   的摘要。
3. 若下一条 `v40` 仍失败，再把解释收紧到：
   - selector crossfire 不是主因，
   - 问题更可能在代理本身与 real gate 的语义错配。

### 104. 不要把“新 absent proxy family 看起来更贴近 current signal”自动等价成“real absent floor 会更好”；`v40 / v41` 证明必须把 proxy 本体分数和 real gate 关键值一起落盘，否则很容易只记住 gate failed，却忘了代理自己也在反向

现象：

- `v40` 已经把 `v39` 的 exact overlap 显式剔掉；
- 但 relative to `v19`，
  它仍然是：
  - exact `target_full = -0.467909 dB`
  - near-real `speech_leak_like (0004) = -0.086817 dB`
  - near-real `guodegang_anchor_120s = -0.099242 dB`
  - near-real `guodegang_absent_480s = -0.057473 dB`
  - `guodegang_absent_proxy_v6_currentsignal_cleanonly = -0.424082 dB`
- `v41` 进一步把 absent-side 直接换成
  `proxy_v6 currentsignal cleanonly allowlist`
  后，
  relative to `v19` 变成：
  - exact proxy overall `+0.036695 dB`
  - 但 exact `target_full = -0.325134 dB`
  - near-real speech probe overall `-0.109792 dB`
  - near-real `speech_leak_like (0004) = -0.062535 dB`
  - near-real `guodegang_anchor_120s = -0.258474 dB`
  - near-real `guodegang_absent_480s = -0.112892 dB`
  - `guodegang_absent_proxy_v6_currentsignal_cleanonly = -0.627418 dB`
- relative to `v32` 的 gate，
  `v41` 还额外 failed：
  - `speech_probe_overall_floor`

处理：

- 已把 `v40 / v41` 的裁决证据集中落盘到：
  - `reports/daily/2026-03-19_v40_v41_absent_followup_results.md`
- 并同步回写：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`

结果：

- 现在可以明确写死：
  - `proxy_v6` 本体 relative to `v19`
    不是边走边好，
    而是一路更差：
    - `v32 = -0.172916 dB`
    - `v39 = -0.424309 dB`
    - `v40 = -0.424082 dB`
    - `v41 = -0.627418 dB`
- 这说明当前 `currentsignal cleanonly v6`
  不是“更贴近 real absent 的代理还差一点点”，
  而更像是：
  - 代理本体就还在反向；
  - exact overall 即使局部转正，
    也不能推出关键的 exact `target_full`
    和 `guodegang` real floor 已被守住。

影响：

- 以后不能把：
  - `default` 还在正增益
  - 或 exact proxy overall 变正
  - 或代理名字看起来更像 current signal
  直接等价成：
  - absent-side 方向已经接近 keep
- absent-side candidate 的最小裁决证据必须至少同时写 5 个数：
  - exact `target_full`
  - `speech_leak_like (0004)`
  - `guodegang_anchor_120s`
  - `guodegang_absent_480s`
  - proxy 本体 summary

后续要求：

1. 后续每条 absent-side candidate 默认同时落盘这 5 个数值。
2. 若 proxy 本体 relative to `v19` 已明显为负，
   不再把它简单归因成：
   - “只是 gate 太严”
3. 下一条 absent-side proxy 设计，
   必须先说明它与当前 `proxy_v6 currentsignal cleanonly`
   的语义差异；
   否则默认视为同类失败重试。

### 105. 不要把“新 absent proxy candidate 仍没过 friend gate”自动等价成“proxy 本体也失败了”；`v42` 证明新的 `proxy_v7` 已能把 `guodegang_anchor / absent` 两条 real floor 拉回正向，真正失败的是当前 `reconstruction_extra` routing 仍会伤到 friend-side `exact target_full / speech_leak_like`

现象：

- 本轮把 `B3` 的新 absent proxy 正式落成：
  - `guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans`
  - train `33`
  - val `8`
- 它与 friend-side exact family 的 overlap 已明显更干净：
  - train `1`
    - `train_001225`
  - val `0`
- 且它不是旧 rows 重路由：
  - 相对 `v32` base manifest
    新增 coverage：
    - train `32`
    - val `8`
- 在这条 `proxy_v7` 上，
  旧 checkpoint relative to `v19` 已经是：
  - `v32 = -0.788730 dB`
  - `v40 = +0.537238 dB`
  - `v41 = +1.267294 dB`
- 进一步训练得到：
  - `v42 = v32 + reconstruction_extra(proxy_v7)`
- `v42` relative to `v19`：
  - default `+0.077955 dB`
  - exact `target_full = -0.664459 dB`
  - `speech_leak_like (0004) = -0.113430 dB`
  - `guodegang_anchor_120s = +0.126568 dB`
  - `guodegang_absent_480s = +0.031863 dB`
  - `proxy_v7 = +0.444459 dB`
- relative to `v32` 的 gate，
  `v42` 只 failed：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

处理：

- 已把这轮 `proxy_v7` 定义、coverage、训练与裁决结果集中落盘到：
  - `reports/daily/2026-03-19_v42_absent_proxy_v7_followup.md`
- 并同步回写：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`

结果：

- 现在可以明确拆开两层结论：
  - `proxy_v7` 本体是有效的：
    - 本体 summary 为正；
    - `guodegang_anchor / absent`
      两条 real floor
      也第一次同时转正；
  - 失败的是当前
    `reconstruction_extra(proxy_v7)`
    这条 routing：
    - 它仍会把 friend-side
      `exact target_full`
      与 `speech_leak_like`
      一起拖坏
- 所以：
  - `v42` 不能 keep；
  - 但不能因此退回写成：
    - “`proxy_v7` 也像 `proxy_v6` 一样无效”

影响：

1. 以后若新 absent proxy candidate 已满足：
   - 本体为正
   - real `guodegang_anchor / absent`
     同时转正
   但仍 failed 于 friend gate，
   默认先怀疑：
   - objective routing / decoupling
   而不是立刻把 proxy 本体判死。
2. `proxy_v6` 与 `proxy_v7`
   必须分开记：
   - `proxy_v6` 是本体反向；
   - `proxy_v7` 是本体成立、routing 失败。
3. 下一条 absent-side follow-up，
   默认不再重搜 proxy；
   而是围绕：
   - exact `target_full`
   - `speech_leak_like (0004)`
   的保护与解耦继续做。

### 106. 不能把所有 gate failed rule 都按同一级别解释；当前 absent / friend-side 裁决至少要区分 `near_tie` 和 `clear_fail`，否则会把“局部接近但总体仍失败”和“方向明显错误”混成同一种失败记忆

现象：

- 用户提醒后回看当前主 gate，
  发现它之前虽然已有：
  - default `0.1 dB` 容差
  - speech overall `0.05 dB` 容差
- 但输出层面仍只有：
  - `pass / fail`
- 这会把两类情况混写成同一种失败：
  - 只低于 floor `0.01 ~ 0.02 dB`
  - 明显低于 floor `0.1 ~ 0.3 dB`
- 用新口径回看后，
  `v41` 就是典型例子：
  - `speech_probe_overall_floor = near_tie`
    - `-0.009327 dB` below floor
  - `exact_target_full_gain_floor = near_tie`
    - `-0.021816 dB`
  - `speech_leak_like_gain_floor = near_tie`
    - `-0.020855 dB`
  - 但：
    - `guodegang_anchor_floor = clear_fail`
      - `-0.192590 dB`
    - `guodegang_absent_floor = clear_fail`
      - `-0.099666 dB`

处理：

- 已更新：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- 当前默认解释规范变成：
  - `pass`
  - `near_tie`
    - 低于 floor 不超过 `0.03 dB`
    - 只改变解释，不放宽 `overall_pass`
  - `clear_fail`
    - 低于 floor 超过 `0.03 dB`
- 输出里新增：
  - `candidate_minus_floor`
  - `judgement`
  - `overall_judgement`
  - `near_tie_rules`
  - `clear_fail_rules`

结果：

- `v39` / `v40`
  仍是 clear fail；
- `v41`
  更准确应写成：
  - 局部 near-tie
  - 但 real floor clear fail；
- `v42`
  仍是 clear fail，
  且 clear fail 已只剩：
  - exact `target_full`
  - `speech_leak_like (0004)`

影响：

1. 以后不能再把：
   - “局部 near-tie 但总体 failed”
   误写成：
   - “整条分支方向都错”
2. 也不能反过来把：
   - 某几条 near-tie
   误写成：
   - 这条分支可能其实应当 keep
3. 当前规范下，
   `near_tie`
   的作用是：
   - 防止失真记忆；
   - 不是放宽 keep gate。

### 107. 如果一条 follow-up 从 `v42` 到 `v43` 只做微幅 waveform weight rescale，而 default / exact / near-real / `guodegang` / proxy 本体几乎完全不动，就不该继续扫同类小数点级权重；这类缩放在当前 `proxy_v7` 路线上基本是 no-op

现象：

- `v43 = v42`
  只把：
  - `reconstruction_extra_waveform_weight`
    从 `0.005`
    改到 `0.0025`
- 其余：
  - `proxy_v7`
  - merged manifest
  - friend-side exact branch
  - base transient / interference / absent
  全都不变
- 结果 relative to `v19` 几乎和 `v42` 完全重合：
  - default：
    - `+0.077955 -> +0.077610`
  - exact `target_full`：
    - `-0.664459 -> -0.663965`
  - `speech_leak_like (0004)`：
    - `-0.113430 -> -0.113233`
  - `guodegang_anchor_120s`：
    - `+0.126568 -> +0.125676`
  - `guodegang_absent_480s`：
    - `+0.031863 -> +0.031660`
  - `proxy_v7`：
    - `+0.444459 -> +0.440865`

处理：

- 已把这轮验证集中落盘到：
  - `reports/daily/2026-03-19_gate_margin_reassessment_and_v43_followup.md`

结果：

- 现在可以明确写死：
  - 当前 `proxy_v7`
    路线上的微幅 waveform weight rescale
    基本是 no-op；
  - `v43`
    仍 failed 于：
    - exact `target_full`
    - `speech_leak_like (0004)`
  - 但并没有带来新的可解释 trade-off。

影响：

1. 不继续扫：
   - `0.005 -> 0.0025 -> 0.001`
   这类小数点级 waveform-only rescale。
2. 下一条若继续沿 `proxy_v7`，
   默认应改：
   - routing mode
   - 或 branch-level decoupling
   而不是继续扫同类微幅权重。

### 108. 当 `proxy_v7` 已证明本体成立时，单纯把 `reconstruction_extra` 从 `waveform_only` 切成 `stft_only` 只会带来很小的 friend-side 回收，同时削弱 default / proxy 本体 / `guodegang` 收益；这说明问题不只是损失域选错，而是需要更本质的 branch-level decoupling

现象：

- 在 `v42 / v43` 之后，
  本轮继续做了第一条真正的 routing mode 变化：
  - `v44 = reconstruction_extra_stft_only(proxy_v7)`
  - `reconstruction_extra_waveform_weight = 0.0`
  - `reconstruction_extra_stft_weight = 0.01`
- `v44` relative to `v19`：
  - default `+0.072833 dB`
  - exact `target_full = -0.647221 dB`
  - `speech_leak_like (0004) = -0.110539 dB`
  - `guodegang_anchor_120s = +0.113703 dB`
  - `guodegang_absent_480s = +0.029381 dB`
  - `proxy_v7 = +0.359405 dB`
- 相比 `v42`：
  - friend-side 两条是有小幅回收：
    - exact `target_full`
      `-0.664459 -> -0.647221`
    - `speech_leak_like (0004)`
      `-0.113430 -> -0.110539`
  - 但代价也同时出现：
    - default：
      `+0.077955 -> +0.072833`
    - `proxy_v7`：
      `+0.444459 -> +0.359405`
    - `guodegang_anchor_120s`：
      `+0.126568 -> +0.113703`
    - `guodegang_absent_480s`：
      `+0.031863 -> +0.029381`
- relative to `v32` gate，
  仍 clear fail 于：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

处理：

- 已把这轮结果集中落盘到：
  - `reports/daily/2026-03-19_v44_proxy_v7_stft_followup.md`

结果：

- 现在可以明确写死：
  - `stft_only`
    比微幅 wave weight 缩放更有信号；
  - 但它不是这条线的解法；
  - 当前问题不只是：
    - “选 waveform 还是 STFT”
    而更像是：
    - 这条 absent-side routing
      还没有和 friend-side speech-leak
      真正解耦

影响：

1. 不继续把
   `waveform_only <-> stft_only`
   当成默认主推进方向。
2. 下一条若继续沿 `proxy_v7`，
   优先考虑：
   - 更本质的 branch-level decoupling
   - 或更细的 routing 重写
3. 文档里以后应把 `v44`
   记成：
   - “mode 有信号”
   - 但“signal 还不足以形成 keep 候选”。

### 109. 当 `proxy_v7` 已经被证明本体有效时，把它内部的 `full` 与 `nonfull` 行拆开做不同 reconstruction routing，会比单一路由更平衡，但若 friend-side 两条仍 clear fail，就应把它记成“更好的 decoupling primitive”，而不是误记成已经接近 keep

现象：

- 本轮继续把 `proxy_v7` 内部拆成：
  - full：
    - train `17`
    - val `5`
  - nonfull：
    - train `16`
    - val `3`
- 训练了：
  - `v45 = nonfull waveform + full stft`
- `v45` relative to `v19`：
  - default `+0.075720 dB`
  - exact `target_full = -0.653286 dB`
  - `speech_leak_like (0004) = -0.111924 dB`
  - `guodegang_anchor_120s = +0.119305 dB`
  - `guodegang_absent_480s = +0.029907 dB`
  - `proxy_v7 = +0.396169 dB`
- 相比 `v44`：
  - default 更强
  - `proxy_v7` 更强
  - `guodegang_anchor / absent`
    也更强
- 但 relative to `v32` gate，
  仍 clear fail：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`

处理：

- 已把这轮 split-routing 结果集中落盘到：
  - `reports/daily/2026-03-19_v45_proxy_v7_splitrouting_followup.md`

结果：

- 现在可以明确写死：
  - `proxy_v7 full`
    与
    `proxy_v7 nonfull`
    不应继续共用同一种 reconstruction routing；
  - 这类 split routing
    的确比单一路由更平衡；
  - 但当前这一级 split
    还没有把 friend-side 两条 clear fail
    拉回 near-tie，
    所以不能误记成：
    - “这条线已经接近 keep”

影响：

1. 以后若继续沿 `proxy_v7`，
   默认优先继续做：
   - 更细的内部语义拆分
   - 或更本质的 branch-level decoupling
2. 不再把：
   - 单一路由
   当成默认基线思路；
   当前更合理的默认 primitive
   已经是：
   - `full / nonfull` split routing
3. 但也不把当前 `v45`
   误写成：
   - 已接近通过 gate 的准 keep 分支。

### 110. 如果把 absent-side follow-up 的可训练范围压到纯 reference-conditioning，friend-side 两条确实可能被拉回到 `near_tie / pass`，但 absent proxy 本体会直接塌掉；这说明当前缺的不是“更少更新”本身，而是“给 absent-side 一点专属 output plasticity，同时别改写共享主干”

现象：

- 本轮新增了：
  - `scripts/train/train_stft_mask_baseline.py`
    的 `--trainable-module-prefixes`
- 并跑了：
  - `v47 = proxy_v7 all ids + ref_encoder + condition_proj only`
- `v47`
  trainable parameter count：
  - `131,968 / 2,367,617`
  - `5.57%`
- relative to `v32` gate：
  - `overall_judgement = near_tie`
  - `exact_target_full_gain_floor = pass`
  - `speech_leak_like_gain_floor = near_tie`
- 但 relative to `v19`：
  - `proxy_v7 = -0.858876 dB`
  - `guodegang_anchor_120s = -0.059132 dB`
  - `guodegang_absent_480s = -0.007238 dB`

处理：

- 已把这轮 prefix-freeze 工程补充与 `v47`
  结果集中落盘到：
  - `reports/daily/2026-03-20_v47_v48_prefix_freeze_decoupling_followup.md`

结果：

- 现在可以明确写死：
  - 纯 ref-conditioning freeze
    的确能保护 friend-side；
  - 但它对 absent-side
    过于保守，
    连 `proxy_v7`
    本体都带不起来；
  - 所以不能把：
    - `v47` 的 gate 近似通过
    误写成：
    - “这条线已经接近 keep”

影响：

1. 以后若继续沿 branch-level decoupling，
   不要把：
   - “继续减少 trainable 参数”
   当成默认方向
2. 当前更合理的默认目标应改写成：
   - 给 absent-side
     一点专属 output-side 可塑性；
   - 但不要再改写共享时序主干
3. 因此下一条默认不再扫：
   - 纯 prefix freeze 的更窄组合。

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

### 119. 对 dual-head 来说，exact-family `SI-SDR guard` 依然很容易把训练推成 exact overfit；`v55` 证明“exact 更好”并不等于 near-real protect 真成立

现象：

- 本轮在 dual-head 上测试了：
  - `v55 = dual-head + proxy_v7 reconstruction + exact SI-SDR guard`
- relative to `v19`：
  - default `+0.126371 dB`
  - exact proxy overall `+0.394224 dB`
  - `proxy_v7 = +1.859823 dB`
- 但 near-real 明显转负：
  - speech probe overall `-0.140416 dB`
  - `guodegang_anchor = -0.494584 dB`
  - `guodegang_absent = -0.157483 dB`

影响：

- 如果只看到：
  - exact family 变正
  - `proxy_v7` 继续变强
  很容易误以为 dual-head protect objective 已经更接近 keep。
- 实际上这更像：
  - exact-family overfit
  - 而不是 friend-side / near-real protect 真正成立。

处理：

- 已把 `v55`
  的训练、compare、gate 与解释集中落盘到：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

后续要求：

1. 后续 dual-head protect objective 不能把 exact-family 变正自动当作放行理由。
2. 若某条 protect objective 把 exact / `proxy_v7` 一起推强，但 `guodegang` 或 near-real speech 明显转负，应直接判成 overfit 型失败。
3. 对这条线，默认不再继续扫 exact `SI-SDR guard` 的小权重变体。

### 120. 新增 extra-only protect weight 时，如果 selector 激活逻辑没把它算进 `extra_weight_keys`，实验会静默失效；`v56` 就属于这种无效轮次

现象：

- 首次跑 dual-head `base-align` 版本时，
  训练命令已经传了：
  - `--loss-interference-extra-base-align-weight`
  - `--loss-interference-extra-focus-sample-ids-file`
- 但当时
  `resolve_selector_sample_weights(...)`
  里，
  `interference_extra`
  的激活条件还没把：
  - `interference_extra_base_align_weight`
  算进去。
- 结果：
  - `v56`
    实际上 `interference_extra = inactive`
  - exact ids 并没有真正命中这条 protect objective。

影响：

- 这类问题不会像 shape error 那样直接崩；
  训练能跑完，
  但实验结论是假的。
- 如果不单独标记，
  后续很容易把这类无效轮次误当成：
  - objective 无效
  - 或 dual-head 本身没信号。

处理：

- 已在：
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  把：
  - `interference_extra_base_align_weight`
  加入 `interference` 分支的 `extra_weight_keys`。
- 并把：
  - `v56`
    明确记为无效 plumbing 轮次；
  - 有效结论从 `v57`
    开始算。

后续要求：

1. 以后每新增一个 extra-only loss weight，都要同步检查 selector 激活条件是否已纳入它。
2. 新 protect primitive 首轮若结果异常平，应先核对 selector 命中，再下模型结论。
3. 无效轮次要明确写成 invalid / plumbing issue，不能混进模型比较序列。

### 121. dual-head 的 `base-align` protect primitive 有信号，但继续扫同一条 weight 已进入平台区；`v57 / v58` 说明当前缺的不是“小数点再调一下”

现象：

- 本轮在 dual-head 上新增：
  - `interference_extra_base_align_l1`
  - 语义是：
    - exact ids 上约束 branch output 不要偏离 frozen base output
- `v57`（weight `0.02`）relative to `v19`：
  - `speech_leak_like (0004) = -0.047720 dB`
  - `guodegang_absent = -0.000021 dB`
  - `proxy_v7 = -1.498264 dB`
  - relative to `v32 gate`：
    - `overall_judgement = near_tie`
    - 唯一 near-tie rule：
      - `speech_leak_like_gain_floor`
- `v58`（weight `0.005`）relative to `v19`：
  - `speech_leak_like (0004) = -0.076592 dB`
  - `guodegang_anchor = +0.061275 dB`
  - `guodegang_absent = +0.027740 dB`
  - `proxy_v7 = +0.042581 dB`
  - relative to `v32 gate`：
    - 唯一 clear fail：
      - `speech_leak_like_gain_floor`

影响：

- `base-align`
  说明 protect primitive 方向是对题的；
  它确实能把 dual-head 拉近 gate。
- 但当前 trade-off 已经很清楚：
  - 保护重了，
    `proxy_v7` 会被压塌；
  - 放轻一点，
    `speech_leak_like (0004)` 又重新 clear fail。
- 如果继续只扫这同一条 weight，
  很容易进入：
  - 实验很多，
  - 但结论不再变硬
  的平台区。

处理：

- 已把：
  - `v57`
  - `v58`
  的结果与解释集中落盘到：
  - `reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`

后续要求：

1. 当前默认不再继续扫 `interference_extra_base_align_weight` 的近邻小变体。
2. 下一条 dual-head protect objective 应更直接面向：
   - `speech_leak_like (0004)`
   - 而不是继续只做 exact-family base 对齐。
3. 同时继续保留：
   - dual-head plumbing
   - `proxy_v7`
   - `v32` frozen base anchor
   这三项资产，作为下一条新 protect objective 的底座。

### 122. 即使 protect primitive 看起来更“局部更聪明”，如果它在 exact ids 上的实际 loss 量级几乎为 `0`，继续扫权重也不会自动变成有效约束；`v59 / v60` 证明 `base-delta-interference projection` 当前就属于这种情况

现象：

- 本轮新增并正式测试了：
  - `interference_extra_base_delta_projection_weight`
- selector 已真实命中：
  - train `7 / 129`
  - val `3 / 37`
- 但 `v59 / v60`
  的 train summary 里，
  新 protect 项量级都极小：
  - `v59`
    - train `2.0131949656154081e-07`
    - val `1.8925945539649546e-07`
  - `v60`
    - train `1.9598214456009678e-07`
    - val `1.7825688871653256e-07`
- 同时：
  - `proxy_v7 / guodegang`
    仍明显变强
  - 但 friend-side
    `exact target_full / speech_leak_like (0004)`
    仍 clear fail

影响：

- 如果只看：
  - “这是更局部的 protect primitive”
  很容易主观上觉得它比 `base-align`
  更有希望。
- 但当实际 loss 量级已经接近 `0` 时，
  继续把权重从：
  - `0.005`
  调到：
  - `0.02`
  往往也只会得到近乎同形态结果，
  不是新的结构性结论。

处理：

- 已完成：
  - `v59`
  - `v60`
  两个正式点；
- 并把训练、compare、gate 与结论集中落盘到：
  - `reports/daily/2026-03-20_v59_v60_dualdecoder_basedeltaproj_followup.md`

后续要求：

1. 对任何新 protect primitive，不能只看 selector 是否命中；还要看该项 loss 的实际量级。
2. 如果在有效命中样本上，该项 loss 长期只有 `~1e-7` 这种接近零的量级，就不要继续扫近邻权重。
3. 这类结果应直接判成：
   - primitive 没真正碰到当前坏掉的行为语义，
   而不是：
   - “再多试两档 weight 也许就行”。

### 123. 如果 protect selector 仍把多类 exact-family 行为绑在一起，可能会把本来对题的 protect primitive 误判成“方向不对”；`v61` 说明 `base-align` 真正的问题之一是 selector 过粗，而不是 primitive 本身失效

现象：

- `v57 / v58`
  已说明 dual-head 上的 `base-align`
  primitive 有信号；
- 但当时 protect selector
  仍挂在整组
  `v30 exact 10 ids`
  上，
  会同时混入：
  - `target_full`
  - `speech_leak_like (0004)`
  - 以及其它 exact-family 行为；
- 本轮把 selector 收窄到：
  - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt`
  后，
  `v61`
  相对 `v19`：
  - exact `target_full`
    从前一轮同类失败点
    `-0.95 / -0.98 dB`
    回收到：
    - `-0.369736 dB`
  - `speech_leak_like (0004)`
    也回收到：
    - `-0.071034 dB`
    并在 relative to `v32` gate
    中只剩：
    - `near_tie`
  - 同时：
    - `guodegang_anchor = +0.069889 dB`
    - `guodegang_absent = +0.043306 dB`
    都没有塌。

影响：

- 如果只看早一轮粗 selector 下的表现，
  很容易把：
  - `base-align`
    误写成：
    - primitive 本身不对题
- 但 `v61`
  说明更准确的解释是：
  - protect primitive 可能是对的；
  - 真正坏的是 selector 语义过粗，
    把不同坏行为绑成同一条约束。

处理：

- 已把 `v61 / v62`
  的结果集中落盘到：
  - `reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`

后续要求：

1. 以后评估 protect objective 时，不能只问“primitive 是什么”，还要问“selector 语义是不是过粗”。
2. 如果一个 protect primitive 在粗 selector 下表现摇摆，但在更细 selector 下出现实质回收，应先把问题归因到 selector，再决定是否放弃 primitive。
3. 当前 dual-head protect 线里，`target_full` 应视为一个独立保护子问题，不再默认和整组 exact-family 绑死。

### 124. 当更细 selector 已证明方向成立后，继续单纯把同一条 protect weight 往上推，可能只会把 trade-off 再次推回去；`v62` 说明下一步该补的是第二条行为约束，而不是同一 primitive 的更强档

现象：

- `v61`
  已证明：
  - `target_full`-only selector
    是对的；
- 本轮继续把同一条
  `interference_extra_base_align_weight`
  从：
  - `0.02`
  加到：
  - `0.05`
  得到 `v62`；
- `v62`
  相对 `v61`：
  - `speech_leak_like (0004)`
    只小幅改善：
    - `-0.071034 -> -0.063768 dB`
  - 但 exact `target_full`
    明显变差：
    - `-0.369736 -> -0.586134 dB`
  - 同时：
    - `proxy_v7`
      从：
      - `-0.029114 dB`
      变成：
      - `+0.861507 dB`
    - `guodegang_anchor`
      也进一步转强。

影响：

- 这说明当前缺的
  已不是：
  - “同一条 protect primitive
     的 weight 还没调到位”
- 而是：
  - `target_full`
  - 与 `0004-like speech leak`
    其实是两类不同的保护行为，
    需要拆开约束。

处理：

- 已把这条结论同步写入：
  - `docs/01_project_overview_and_plan.md`
  - `docs/05_task_branch_map.md`
  - `reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`

后续要求：

1. 当前默认不再继续扫 `target_full`-only `base-align` 的近邻更强档。
2. 下一条 dual-head protect objective，应在保留 `target_full` 保护的前提下，再补一条更直接面向 `speech_leak_like (0004)` 的 branch-local protect signal。
3. 以后遇到“更强权重把一个子问题略微拉好、却把另一个关键子问题重新推坏”的情况，应优先考虑拆目标，而不是继续扫同一条 weight。

### 125. 当主线是否切换其实已经有稳定主观结论后，项目如果继续默认沿 objective / gate 自动扩实验树，就会让“研究排雷”和“主线决策”混层；这时需要项目级 stop rule，而不是继续靠局部 gate 自己滚

现象：

- 当前项目早已得到：
  - `ref_film + stft0.5 + sisdr0.0005`
    不升主线；
  - focused `ft2 / ft3`
    也不升主候选；
- 但后续推进仍然持续长出了：
  - `v36+`
    大量 absent / friend-side / dual-head
    objective 研究分支；
- 这些分支的价值主要是：
  - 排雷
  - 定位冲突
  - 写清哪些 primitive / routing / selector
    不值得再扫；
  - 而不是：
    - 已经接近替换默认主线。

影响：

- 如果不显式把：
  - 默认主线
  - 研究基座
  - 已关闭分支
  这三层拆开，
  项目会自然滑向：
  - 还有什么能试就继续试什么；
- 这会让：
  - objective / gate
    成为实际节奏驱动，
  - 而不是：
    - 主观结论
    - 真实症状
    - 项目级停止条件。

处理：

- 已新增：
  - `reports/daily/2026-03-20_project_state_reset_after_review.md`
- 并把正式口径更新为：
  - 默认主线：
    - `legacy stage2`
  - 当前 `v36+`
    解释为：
    - 研究排雷分支
  - 默认下一步：
    - 暂停等待用户指示，
      不自动起新实验

后续要求：

1. 以后必须把“主线是否切换”与“研究是否继续”分成两套决策，不再混用同一条默认推进逻辑。
2. 当主线结论已锁定而研究仍在继续时，默认计划应写成：
   - `paused / pending instruction`
   而不是：
   - `continue training`
3. 若后续重新启动实验，新分支必须先写明：
   - 服务的真实问题症状是什么；
   - 为什么不是旧 primitive 的近邻重扫；
   - 对应哪条人耳或 near-real 复核入口。
