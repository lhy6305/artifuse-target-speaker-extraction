# 项目结构说明

## 1. 设计原则

目录结构遵循以下原则：

- 原始输入与正式产物分离；
- 代码、配置、实验、报告、临时文件分离；
- 尽量让“下一步脚本该写在哪、输出该落在哪”一眼可见；
- 不在根目录堆放一次性文件。

## 2. 当前目录职责

### `data_in/`

外部原始输入区。这里保留历史原始数据，不在结构整理阶段移动大文件。

当前主要内容：

- `source_segments/`：用户 source 切片与历史 manifest。
- `genshin_voice_extract/`：大量单说话人游戏语音。
- `voice_music_dataset/`：歌曲与 UVR 人声产物。
- `pure_music_dataset/`：纯音乐或伴奏候选。
- 根目录下若干长音频原件。

### `data/`

正式项目数据区，用于放可重复消费的数据索引和中间结果。

- `data/manifests/`：统一管理数据清单。
- `data/references/`：参考音频或筛选后的 enrollment 集。
- `data/interim/`：数据预处理的中间产物。
- `data/synthetic/`：合成训练、验证、测试样本。
- `data/curated/`：从大型原始包中正式散选并保留下来的长期可消费子集。

### `src/`

正式源码目录。

- `src/tse_prefix/data/`：数据集、manifest 读取、采样逻辑。
- `src/tse_prefix/models/`：模型封装。
- `src/tse_prefix/pipeline/`：训练、推理、串联流程。
- `src/tse_prefix/utils/`：通用工具函数。

### `scripts/`

命令行入口脚本目录。

- `scripts/data/`：扫描、切片、写 manifest、合成样本。
- `scripts/train/`：训练入口。
- `scripts/eval/`：评估、试听、指标汇总。

### `configs/`

配置文件目录。后续可按 `data/`、`model/`、`train/` 再拆。

### `experiments/`

实验运行产物。

- `experiments/logs/`：运行日志。
- `experiments/checkpoints/`：模型权重。

### `reports/`

阶段性结果和结论。

- `reports/daily/`：日常进度记录。
- `reports/eval/`：评估汇总、AB 听感结论。

### `docs/`

规范和长期说明文档。

### `tmp/`

一次性临时文件专用目录。临时内容不得长期散落到根目录。

## 3. 推荐后续文件落点

| 内容 | 推荐位置 |
|---|---|
| 用户语音池 manifest | `data/manifests/target_speech_pool.jsonl` |
| reference 池 manifest | `data/manifests/target_reference_pool.jsonl` |
| clean interference manifest | `data/manifests/speech_interference_clean_pool.jsonl` |
| 原神 clean 子集实体文件 | `data/curated/genshin_clean_subset_cover_embed_prune_v1/` |
| hard negative manifest | `data/manifests/speech_interference_hard_pool.jsonl` |
| 音乐干扰 manifest | `data/manifests/music_interference_pool.jsonl` |
| singing vocal manifest | `data/manifests/singing_vocal_interference_pool.jsonl` |
| 合成脚本 | `scripts/data/build_synthetic_dataset.py` |
| 数据集代码 | `src/tse_prefix/data/` |
| baseline 推理脚本 | `scripts/eval/` |
| 训练配置 | `configs/` |

## 4. 当前结构结论

当前已经完成“先把房间收拾出来”这一步。大白话讲，就是先把原始数据区、正式代码区、实验输出区和临时垃圾区分开，不然后面一旦开始写脚本、生成 manifest、跑实验，很快又会乱成一团。
