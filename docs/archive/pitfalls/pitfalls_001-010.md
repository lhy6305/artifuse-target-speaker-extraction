# 踩坑记录 历史归档 1-10

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `1-10`

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
