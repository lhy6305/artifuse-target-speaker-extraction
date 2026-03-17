# 2026-03-16 Genshin Clean Pool Cover V1

## 目标

把原先“每个说话人取前 24 条、只取 32 个说话人”的 MVP 方案，升级成更能代表整个原神 clean 数据集的覆盖抽样版本。

重点不是继续无脑保留更多数据，而是：

- 覆盖更多说话人；
- 不漏掉说话人目录下的特殊语音子文件夹；
- 在每个说话人内部尽量覆盖短句、长句、不同文本边界；
- 降低纯顺序截断带来的冗余偏置。

## 本次新增脚本

- `scripts/data/rebuild_genshin_clean_pool.py`

## 当前抽样逻辑

对候选样本按以下维度做 coverage-weighted sampling：

- 说话人目录递归类别
  - 例如 `__root__`
  - `战斗语音 - Battle`
  - `怪物语音 - Monster`
  - `其它语音 - Others`
  - `带变量语音 - Placeholder`
- 时长桶
  - 1-2 秒
  - 2-4 秒
  - 4-7 秒
  - 7-12 秒
- 文本长度桶
- 句子子句数
- 起始/结尾字符类别
- 标点类别
  - 问句
  - 感叹
  - 省略
  - 停顿
  - 引号
  - 终止标点

并采用以下原则：

1. 先保证每个说话人的目录类别至少覆盖 1 条。
2. 再保证时长桶、文本长度桶、标点桶尽量都被覆盖。
3. 再用带稀有特征加权的贪心选择补齐剩余名额。
4. 对重复文本做明显惩罚，减少近重复句的堆积。

## 本次结果

- 新 clean pool 说话人数：838
- 新 clean pool 样本数：23657
- 新子集目录：
  - `data/curated/genshin_clean_subset_cover_v1/`
- 新 manifest：
  - `data/manifests/speech_interference_clean_pool.jsonl`
- 旧 manifest 备份：
  - `data/manifests/speech_interference_clean_pool.pre_cover_v1_backup.jsonl`
- 抽样报告：
  - `data/manifests/speech_interference_clean_pool.cover_v1_report.json`

## 覆盖结论

- 对于已经纳入 clean pool 的 838 个说话人：
  - 目录类别覆盖率为 100%
  - 即候选集中出现过的顶层类别，选样中都至少保留了 1 条

额外观察：

- 选中样本中，每个说话人平均覆盖约 3.634 个时长桶
- 每个说话人平均覆盖约 4.076 个文本长度桶

## 仍然没做到的事

这版虽然已经明显优于旧版，但仍不是完整声学评估版。当前还没有做：

- 声学 embedding 聚类抽样
- 韵律相似度去冗余
- 音素覆盖建模
- 基于能量轮廓或静音比的专门分层

## 当前结论

这版可以视为 clean interference pool 的正式覆盖抽样 V1。

如果后续训练仍显示出冗余过高，再在这版基础上做更重的 embedding-level 去冗余，而不是回退到旧的顺序截断方案。
