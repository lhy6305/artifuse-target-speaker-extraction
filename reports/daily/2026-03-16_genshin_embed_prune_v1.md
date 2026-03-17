# 2026-03-16 Genshin Acoustic Embedding Prune V1

## 环境检查

本轮先检查了仓库自带 `python.exe` 的现有包环境。

已存在并可直接使用：

- `numpy`
- `scipy`
- `sklearn`
- `torch`
- `torchaudio`
- `librosa`
- `soundfile`

未安装：

- `speechbrain`
- `wespeaker`

结论：

- 当前无需额外装包，就可以做一轮无安装版声学 embedding 聚类下采样。
- 本轮不依赖预训练 speaker encoder，而是使用手工声学特征 embedding。

## 本次新增脚本

- `scripts/data/downsample_genshin_clean_pool_with_acoustic_embeddings.py`

## 本轮方法

输入：

- 当前 coverage 版本 clean pool manifest
  - `data/manifests/speech_interference_clean_pool.jsonl`

步骤：

1. 用 `soundfile` / `torchaudio` / `ffmpeg` 回退链尝试读取音频。
2. 提取手工声学 embedding，主要包括：
   - MFCC 均值/方差
   - Delta / Delta-Delta 均值/方差
   - RMS
   - ZCR
   - spectral centroid / bandwidth / rolloff / flatness
   - voiced ratio
   - duration
3. 对每个说话人先保留 coverage 锚点：
   - 目录类别
   - 时长桶
   - 文本长度桶
   - 标点边界桶
4. 再对剩余样本做说话人内聚类，保留每簇代表点。

## 运行结果

- 输入可读样本数：23170
- 下采样后样本数：13667
- 说话人数：836
- 平均每个说话人保留：16.348 条
- 平均保留比例：0.675
- 单说话人最少保留：8
- 单说话人最多保留：36

新正式子集目录：

- `data/curated/genshin_clean_subset_cover_embed_prune_v1/`

新 manifest：

- `data/manifests/speech_interference_clean_pool.jsonl`

manifest 备份：

- `data/manifests/speech_interference_clean_pool.pre_embed_prune_v1_backup.jsonl`

报告：

- `data/manifests/speech_interference_clean_pool.embed_prune_v1_report.json`

embedding 缓存：

- `data/interim/genshin_clean_cover_v1_acoustic_embeddings.npz`

## 覆盖结论

- 836 个保留说话人的目录类别覆盖率仍为 100%。
- 即：每个保留说话人候选集中出现过的 `coverage_category`，本轮下采样后仍至少保留 1 条。

## 坏文件情况

- embedding 提取阶段识别出 487 条坏文件。
- 这批文件不能被：
  - `soundfile`
  - `torchaudio`
  - `ffmpeg`
  正常解码。

处理方式：

- 已记入报告并在本轮下采样中跳过。
- 没有让整轮流程因为少量坏文件中断。

## 回归验证

已验证：

- `scripts/data/prepare_curated_pools.py`
- `scripts/data/build_synthetic_dataset.py`

都能继续消费本轮下采样后的 clean manifest。

## 当前边界

这仍然不是“预训练 speaker embedding 级”的最终版去冗余。

当前更准确的描述是：

- 已完成一轮基于手工声学 embedding 的聚类下采样；
- 已明显减少重复样本；
- 仍可在后续继续升级到更强的 speaker encoder 聚类。
