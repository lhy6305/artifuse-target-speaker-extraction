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
- `scripts/eval/analyze_proxy_case_neighbors.py`：基于 manifest 字段 + `metadata.json` 字段做 metadata-rich 近邻搜索，并可拼接 compare 结果一起看 top alias / failed constraints / alias gap。
- `scripts/eval/analyze_proxy_group_split.py`：对多个显式 sample-id group 做组均值、代表样本、aggregate 排序和 pairwise delta 对照，适合 frontier ring / subgroup split 诊断。
- `scripts/eval/analyze_proxy_case_positioning.py`：把单条 focus case 放到多个 reference group center 之间做位置诊断，支持 leave-one-out 距离、metadata / margin 分拆和 top 偏离字段解释。
- `scripts/eval/analyze_proxy_transition_axes.py`：基于 positioning summary 计算样本在 source-group 到 target-group 之间的 metadata / margin 双轴投影，适合判断 margin-first collapse 是否先于 metadata 迁移。
- `scripts/eval/analyze_proxy_margin_order_split.py`：基于 transition-axis summary 显式计算关键 margin 的 zero-cross threshold 与 case 进度，适合拆解 `v66 > v64` / `v66 > v65` 的先后塌缩次序。
- `scripts/eval/analyze_proxy_neighbor_signature_scan.py`：基于 neighbor summary 把近邻按 `focus-vs-reference` 与 `focus-vs-secondary` 的 gap 形态分桶，适合确认某个 singleton 签名在窄 ring 里有没有真正同型 row。
- `scripts/eval/analyze_proxy_branch_factor_contrast.py`：对 shared-shelf 基线、目标分支和对照分支做 factor residual 排序，适合判断某条 sink / pocket 分支里哪些字段是真正 branch-specific 而不是 shared package。
- `scripts/eval/analyze_proxy_factor_slice_support.py`：按 target-vs-baseline 中点把近邻切成 factor 的 target-side / shelf-side，并检查对照分支是否共享该侧，适合把 sink-specific 因子和 shared post-entry package 区分开。
- `scripts/eval/analyze_proxy_factor_pair_quadrants.py`：把两个 factor 的 target-side 切片做成交叉四象限，适合判断某条 sink / pocket 分支是单因子驱动还是需要 conjunction。
