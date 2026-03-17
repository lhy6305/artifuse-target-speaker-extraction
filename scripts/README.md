# scripts

脚本入口目录。

建议约定：

- `scripts/data/`：数据扫描、切片、manifest、合成
- `scripts/train/`：训练入口
- `scripts/eval/`：评估与试听辅助

当前已实现的关键脚本：

- `scripts/data/prepare_curated_pools.py`：从 `data_in/` 生成正式数据池 manifest，并切出 hard negative 中间片段。
- `scripts/data/build_synthetic_dataset.py`：基于正式 manifest 生成最小 synthetic train/val 样本。
- `scripts/data/materialize_genshin_clean_subset.py`：把原神 clean interference 已选样本散着迁移到 `data/curated/`，并改写 clean manifest。
- `scripts/data/rebuild_genshin_clean_pool.py`：基于递归目录类别、时长、文本长度、标点边界等特征，对原神 clean pool 做 coverage-weighted 重抽样并生成新的正式子集。
- `scripts/data/downsample_genshin_clean_pool_with_acoustic_embeddings.py`：基于当前 coverage 版 clean pool 提取声学 embedding，并按说话人做“覆盖锚点 + 聚类代表点”下采样。
- `scripts/train/train_stft_mask_baseline.py`：训练最小 STFT mask conditional baseline。
- `scripts/eval/eval_stft_mask_baseline.py`：评估 baseline checkpoint，输出总指标、分组指标和少量样例音频。
- `scripts/eval/listening_pack_gui.py`：本地 blind listening pack GUI，支持样本筛选、音频播放、结构化打分和一键导出结果。
