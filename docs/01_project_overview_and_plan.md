# 项目总览与阶段计划

## 1. 项目定位

本项目是独立于现有 VC 主线的前置模块，目标是：

- 输入混合录音和目标说话人参考音频；
- 输出尽量只保留目标说话人的净化语音；
- 作为后续 VC 模型的更干净 `source` 输入。

当前阶段不做：

- 与 VC 主模型联合训练；
- 共享 VC 项目的实验体系；
- 直接追求大规模复杂训练。

## 2. 当前目录扫描事实

截至 2026-03-16，仓库当前已观察到的关键事实如下：

- 根目录原本只有 `initial_design.md`、`docs/00_context_bootstrap.md`、`data_in/` 和本地运行文件。
- `docs/00_context_bootstrap.md` 引用了 `docs/01_project_overview_and_plan.md`、`docs/02_pitfalls_log.md`、`initial_design_judg.md`，但这些文件原先不存在。
- `data_in/source_segments/segments/` 下当前可见 537 个切片文件，可作为首批目标说话人语音池候选。
- `data_in/genshin_voice_extract/` 下当前可见 214534 个文件，包含大量 `wav/lab`，可作为 clean speech interference 原始来源。
- `data_in/voice_music_dataset/normal/` 下当前可见 168 个文件。
- `data_in/voice_music_dataset/uvr_voice_only/` 下当前可见 121 个文件，可作为 singing vocal interference 原始来源。
- `data_in/pure_music_dataset/` 下当前可见 12 个文件，可作为首批音乐干扰来源。
- `data_in/friend_dataset_fuhuo_raw_concat.wav` 当前是单个长音频，尚未切片，不适合直接进入 hard negative 池。
- `scripts/data/prepare_curated_pools.py` 已于 2026-03-16 实际跑通，并在 `data/manifests/` 生成首批正式数据清单。
- `speech_interference_clean_pool` 已重建为 coverage-weighted 版本，当前正式子集保存在 `data/curated/genshin_clean_subset_cover_v1/`。
- 当前 clean pool 已进一步做过一轮声学 embedding 聚类下采样，正式子集现保存在 `data/curated/genshin_clean_subset_cover_embed_prune_v1/`。
- embedding 下采样前的可读 clean pool 为 836 个说话人 / 23170 条；下采样后为 836 个说话人 / 13667 条。
- 本轮 embedding 提取过程中识别出 487 条无法被 `soundfile`、`torchaudio`、`ffmpeg` 解码的坏文件，已跳过并写入报告。
- 新 embedding-pruned clean 子集当前文件数为 27334，体量约 7.00 GB。
- 顶层类别覆盖核对结果为：836 个说话人中，所有已纳入说话人的候选类别都至少保留了 1 条样本，类别覆盖率 100%。
- 项目根目录已初始化 Git 仓库，当前分支为 `main`，远端为 `https://github.com/lhy6305/artifuse-target-speaker-extraction.git`。
- 已补齐面向公开仓库的建仓文件：
  - `.gitignore`
  - `LICENSE`
  - `NOTICE`
  - 根目录 `README.md`
- 当前公开仓库策略已明确：
  - 只发布代码、配置、方案、评估、公开安全的模型或中间产物；
  - 不发布原始音频、游戏来源语音包、标注文本、合成音频数据及本地运行缓存。
- 当前 Git 仓库已有提交历史；截至 `2026-03-17 18:21:59 +0800`，`HEAD` 为 `2430e8d9b535f0c9daf3d82f2a48f32aaac09f1b`。
- Git 提交记录由用户手动维护；当前约定下，助手只使用 Git 做状态核对、差异检查和误操作恢复辅助。
- 根目录敏感文件 `ssh-key-private` 当前命中 `.gitignore` 规则，未被跟踪。
- 环境检查结果表明当前无需新增安装包即可完成这轮下采样；已实际使用：
  - `numpy`
  - `scipy`
  - `scikit-learn`
  - `torch`
  - `torchaudio`
  - `librosa`
  - `soundfile`
- `speechbrain` / `wespeaker` 当前环境中不存在，但这轮未使用它们。
- 当前已落地的首批清单规模为：
  - `target_speech_pool`: 219
  - `target_reference_pool`: 64
  - `speech_interference_clean_pool`: 13667
  - `speech_interference_hard_pool`: 140
  - `music_interference_pool`: 12
  - `singing_vocal_interference_pool`: 96
- `data/interim/friend_hard_negative_segments/` 已生成 140 个 hard negative 切片文件。

## 3. 现阶段数据桶映射

| 设计数据桶 | 当前对应来源 | 当前状态 | 备注 |
|---|---|---|---|
| `target_speech_pool` | `data_in/source_segments/segments/` | 可启动 | 后续需补 manifest 与质量过滤字段 |
| `target_reference_pool` | 从 `data_in/source_segments/segments/` 中二次拆分 | 待生成 | 必须与 target 采样隔离 |
| `speech_interference_clean_pool` | `data_in/genshin_voice_extract/` | 可启动 | 需先筛出可用 `wav`，忽略 `lab` |
| `speech_interference_hard_pool` | `data_in/friend_dataset_fuhuo_raw_concat.wav` | 待处理 | 需要先切片、过滤、写 manifest |
| `music_interference_pool` | `data_in/pure_music_dataset/` | 可启动 | 后续可补更系统的伴奏来源 |
| `singing_vocal_interference_pool` | `data_in/voice_music_dataset/uvr_voice_only/` | 可启动 | 建议单独控比使用 |
| `ambient_noise_pool` | 暂无正式目录 | 缺失 | 后续需要补采样或整理来源 |

## 4. 已建立的正式项目结构

### 顶层目录

- `configs/`
- `src/`
- `scripts/`
- `data/`
- `experiments/`
- `reports/`
- `docs/`
- `tmp/`

### 细分目录

- `src/tse_prefix/data/`
- `src/tse_prefix/models/`
- `src/tse_prefix/pipeline/`
- `src/tse_prefix/utils/`
- `scripts/data/`
- `scripts/train/`
- `scripts/eval/`
- `data/manifests/`
- `data/references/`
- `data/interim/`
- `data/synthetic/train/`
- `data/synthetic/val/`
- `data/synthetic/test/`
- `experiments/logs/`
- `experiments/checkpoints/`
- `reports/daily/`
- `reports/eval/`
- `docs/archive/`

## 5. 当前阶段目标

当前阶段定义为 Phase A 的 manifest 落地与 synthetic 前准备子阶段，目标是：

1. 保持清晰目录边界和可恢复文档链路。
2. 将设计稿中的数据桶真正落地为可消费的正式 manifest。
3. 为下一步 synthetic mixture 生成器和最小 baseline 闭环提供稳定输入。
4. 在进入训练前先把明显的数据组织风险记录清楚。

## 6. 当前阶段验收标准

当前阶段视为完成的最低标准：

1. 根目录不再把正式代码、实验、文档、临时文件混放。
2. `docs/00_context_bootstrap.md` 中引用的核心文档可被实际读取。
3. `data/manifests/` 中至少存在 target、reference、clean speech、hard speech、music、singing vocal 的正式清单。
4. 后续开发者能仅靠磁盘文档理解：
   - 项目目标是什么；
   - 当前有哪些数据；
   - 已经产出了哪些 manifest；
   - 下一步应该先做什么。

## 7. 当前进度

### 已完成

- 已阅读 `initial_design.md`。
- 已读取 `docs/00_context_bootstrap.md`。
- 已扫描当前目录与主要数据区。
- 已建立独立子项目的目录骨架。
- 已补齐项目总览、踩坑记录、结构说明与评审占位文档。
- 已实现并执行 `scripts/data/prepare_curated_pools.py`。
- 已生成首批正式 manifest 与 hard negative 切片中间产物。
- 已将 `target_reference_pool` 抽样逻辑改为在可用候选中均匀抽样，避免只取排序靠前样本。
- 已实现 `scripts/data/build_synthetic_dataset.py` 的首版。
- 已实际生成最小 synthetic 样本并验证 `mixture.wav`、`target.wav`、`reference.wav`、`metadata.json` 均可正常落盘。
- `scripts/data/build_synthetic_dataset.py` 已从“目标全程存在”的 MVP 版本扩展为 richer temporal patterns 版本。
- 当前已实际生成并验证的目标时序模式包括：
  - `target_full`
  - `target_absent_head`
  - `target_absent_tail`
  - `target_intermittent`
- 当前 synthetic metadata 已记录：
  - `temporal_pattern`
  - `target_present_ratio`
  - `target_segments`
  - `target_absent_intervals`
- 训练 / 评估管线现已消费 `target_absent_intervals`，并支持 `absent_interval_l1` loss / metric。
- 已验证 `target.wav` 与 `mixture.wav` 在这些模式下仍保持等长。
- 已实现并执行 `scripts/data/materialize_genshin_clean_subset.py`。
- 已实现并执行 `scripts/data/rebuild_genshin_clean_pool.py`。
- 已实现并执行 `scripts/data/downsample_genshin_clean_pool_with_acoustic_embeddings.py`。
- clean interference manifest 已改写为指向 `data/curated/genshin_clean_subset_cover_embed_prune_v1/`。
- 已给 `prepare_curated_pools.py` 加保护逻辑，避免重新扫描原神原目录后覆盖任意 `data/curated/` 下的正式 clean manifest。
- 已验证新的 clean manifest 仍可被 `prepare_curated_pools.py` 与 `build_synthetic_dataset.py` 正常消费。
- 已完成公开 GitHub 仓库的本地初始化与基础忽略规则设置。
- 已确认敏感根目录文件当前未进入 Git 跟踪与提交历史。
- 已实现最小 baseline 训练闭环：
  - `src/tse_prefix/data/synthetic_dataset.py`
  - `src/tse_prefix/models/stft_mask_baseline.py`
  - `src/tse_prefix/pipeline/baseline_train.py`
  - `scripts/train/train_stft_mask_baseline.py`
- 已完成 baseline smoke training，确认：
  - synthetic manifest 可被 DataLoader 正常读取
  - 模型前向和 loss 可正常反传
  - checkpoint 与 `train_summary.json` 可正常落盘
- 已实现 baseline 评估入口 `scripts/eval/eval_stft_mask_baseline.py`。
- 已能基于 checkpoint + synthetic val manifest 跑批量评估，并落盘：
  - 数值指标汇总 `eval_summary.json`
  - 少量样例的 `estimate.wav / target.wav / mixture.wav`
- 当前 smoke checkpoint 在 synthetic val 集上的首轮指标为：
  - `loss`: 0.046444
  - `waveform_l1`: 0.023725
  - `stft_l1`: 0.045437
  - `sisdr_db`: -26.484
- 已将 synthetic 集扩展到：
  - train: 512
  - val: 128
- 已完成 baseline stage1 小规模正式训练：
  - 5 epochs
  - batch size 8
  - global steps 320
  - best val loss 0.025460
- 已完成 stage1 checkpoint 的评估，当前 synthetic val 集指标为：
  - `loss`: 0.028332
  - `waveform_l1`: 0.014389
  - `stft_l1`: 0.027886
  - `sisdr_db`: -13.101
- 相比 smoke checkpoint，stage1 当前提升为：
  - `loss`: -0.018112
  - `waveform_l1`: -0.009336
  - `stft_l1`: -0.017551
  - `sisdr_db`: +13.383 dB
- 当前 smoke run 产物位于：
  - `experiments/checkpoints/baseline_stft_mask_smoke/latest.pt`
  - `experiments/checkpoints/baseline_stft_mask_smoke/best.pt`
  - `experiments/checkpoints/baseline_stft_mask_smoke/train_summary.json`
- 当前首轮 eval 产物位于：
  - `reports/eval/baseline_stft_mask_smoke_eval/eval_summary.json`
  - `reports/eval/baseline_stft_mask_smoke_eval/samples/`
- 当前 stage1 训练产物位于：
  - `experiments/checkpoints/baseline_stft_mask_stage1/latest.pt`
  - `experiments/checkpoints/baseline_stft_mask_stage1/best.pt`
  - `experiments/checkpoints/baseline_stft_mask_stage1/train_summary.json`
- 当前 stage1 eval 产物位于：
  - `reports/eval/baseline_stft_mask_stage1_eval/eval_summary.json`
  - `reports/eval/baseline_stft_mask_stage1_eval/samples/`
- 已将 synthetic 集进一步扩展到 stage2 规模：
  - train: 2048
  - val: 512
- 已完成 baseline stage2 训练：
  - 6 epochs
  - batch size 16
  - global steps 768
  - best val loss 0.020418
- 已完成 stage2 checkpoint 的评估，当前 synthetic val 集指标为：
  - `loss`: 0.024478
  - `waveform_l1`: 0.013034
  - `stft_l1`: 0.022888
  - `sisdr_db`: -10.324
- 相比 stage1，stage2 当前进一步提升为：
  - `loss`: -0.003855
  - `waveform_l1`: -0.001356
  - `stft_l1`: -0.004997
  - `sisdr_db`: +2.777 dB
- stage2 eval 已支持按以下维度分组统计：
  - `temporal_pattern`
  - `recipe`
  - `target_present_ratio` bucket
- 当前 stage2 中较难的 recipe 主要是：
  - `target_clean_plus_music`
  - `target_clean_speech`
- 当前 stage2 训练产物位于：
  - `experiments/checkpoints/baseline_stft_mask_stage2/latest.pt`
  - `experiments/checkpoints/baseline_stft_mask_stage2/best.pt`
  - `experiments/checkpoints/baseline_stft_mask_stage2/train_summary.json`
- 当前 stage2 eval 产物位于：
  - `reports/eval/baseline_stft_mask_stage2_eval/eval_summary.json`
  - `reports/eval/baseline_stft_mask_stage2_eval/samples/`
- 已完成一个与 stage2 同规模的 hard-recipe-focus 受控对照实验：
  - train: 2048
  - val: 512
  - train recipe profile: `hard_recipe_focus`
  - val recipe profile: `default`
- 该受控对照结果明显差于 stage2 默认配比：
  - `loss`: +0.005526
  - `waveform_l1`: +0.000980
  - `stft_l1`: +0.009092
  - `sisdr_db`: -8.976 dB
- 对照实验中，当前最难的两个 recipe 也没有被救回来，反而进一步恶化：
  - `target_clean_speech`: `sisdr_db` 再降约 9.127 dB
  - `target_clean_plus_music`: `sisdr_db` 再降约 10.182 dB
- 因此当前主线不采用 pure `hard_recipe_focus` 作为默认训练分布。
- 当前工作区 synthetic manifest 已恢复到 stage2 默认配比：
  - train: 2048 / default
  - val: 512 / default
- 已完成 baseline 模型侧的一轮 reference conditioning 升级：
  - 从 `legacy_bias` 版“reference 全局加性偏置”
  - 升级到 `ref_film` 版“reference attention pooling + FiLM gate + similarity feature”
- 训练 checkpoint 现已显式记录 `model_config`，评估脚本也已支持：
  - 新结构按 checkpoint 中的 `model_config` 复现
  - 旧 checkpoint 自动识别为 `legacy_bias` 并继续可评估
- 已完成 `ref_film` 结构的 smoke 训练与评估验证：
  - 训练：1 epoch / 6 steps
  - eval loss: `0.041898`
  - eval sisdr_db: `-21.665`
- 已验证旧的 stage2 checkpoint 仍可被新版 eval 脚本正确加载，指标与历史结果一致。
- 已完成 `ref_film` 与 `legacy_bias` 的同预算 stage2 正式对照：
  - synthetic 分布：2048 / 512 / default
  - 训练预算：6 epochs / batch size 16 / 768 steps
- `ref_film` 相对当前 legacy stage2：
  - `loss`: `-0.000904`
  - `stft_l1`: `-0.002323`
  - `waveform_l1`: `+0.000257`
  - `sisdr_db`: `-0.236 dB`
- 当前结论：
  - `ref_film` 已证明可稳定训练与评估
  - 但尚未证明整体优于 `legacy_bias`
  - 当前默认主线仍保持 `legacy_bias + stage2 default`
- 已完成训练损失扩展，当前 baseline 已支持可配置的 `SI-SDR loss`：
  - 训练脚本新增 `loss_config`
  - checkpoint / summary / eval 已同步记录
- 已完成两个同预算 stage2 损失对照：
  - `legacy_bias + sisdr001`
  - `ref_film + sisdr001`
- 当前观察到的关键结果：
  - `legacy_bias + sisdr001` 虽能提升 `sisdr_db`，但重建类指标退化较明显
  - `ref_film + sisdr001` 相对 legacy stage2：
    - `loss`: `+0.000931`
    - `waveform_l1`: `-0.000036`
    - `stft_l1`: `+0.001933`
    - `sisdr_db`: `+1.880 dB`
  - `ref_film + sisdr001` 相对 `legacy_bias + sisdr001`：
    - 四项指标全部更优
- 当前可把 `ref_film + sisdr001` 视为新的“分离导向候选主线”，但在没有听感验证前，仍保留 legacy stage2 作为回退对照。
- 已完成一轮小范围损失权重扫描，当前结论更新为：
  - `ref_film + stft0.5 + sisdr0.0005` 优于 `ref_film + sisdr0.001`
  - 相对 legacy stage2：
    - `loss`: `-0.000181`
    - `waveform_l1`: `-0.000276`
    - `stft_l1`: `+0.000190`
    - `sisdr_db`: `+2.231 dB`
  - 这说明当前最平衡的候选主线已经从 `sisdr001` 更新为 `sisdr0005`
- 已确认 `stft_weight=0.6` 的两组对照都明显更差，当前不再沿这个方向继续消耗算力。
- 已完成 `sisdr_weight` 的窄范围复扫：
  - 新增对照点：`0.0003 / 0.0004 / 0.0006`
  - 结果表明 `0.0005` 不是偶然点，而是当前窄区间内的明确最优点
  - `0.0005` 相对 `0.0004` 仍四项主指标全部更优
  - `0.0003` 与 `0.0006` 都明显退化
- 当前主线已可收敛到：
  - `ref_film + stft0.5 + sisdr0.0005`
  - 暂不继续扫描更远的 `sisdr_weight`
- 已完成听感验证准备侧的工程落地：
  - 新增双 checkpoint A/B 导出脚本 `scripts/eval/export_ab_listening_pack.py`
  - 已导出一套 synthetic hard-case 试听包：
    - `reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005/`
  - 已导出一套 blind A/B 试听包：
    - `reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005_blind/`
  - 已额外导出一套只聚焦 `target_clean_plus_music` 的 blind 试听包：
    - `reports/eval/ab_listening_pack_clean_plus_music_blind/`
  - 当前试听包对照的是：
    - `legacy stage2`
    - `ref_film + stft0.5 + sisdr0.0005`
  - 样本选择同时覆盖：
    - 明显收益样本
    - 明显退化样本
    - 接近平手样本
- 当前仓库仍缺少正式的真实验证集 manifest；因此本轮完成的是“听感验证准备”，不是“真实验证已完成”。
- 已收到第一批人工盲听反馈：
  - `val_000071`：用户主观更偏向新模型
  - `val_000089`、`val_000090`：用户主观更偏向旧模型
  - 当前已知的主观回退点主要落在 `target_clean_plus_music`
- 已完成一轮“主观反馈后的自动跟进分析”：
  - 当前确认 `clean_plus_music` 是最需要重点盯的回退 recipe
  - 已做轻量 hybrid probe：`legacy/new` 推理期线性融合
  - 当前 `alpha_new=0.75` 是客观上最值得保留的折中点，但暂未升级为主线
- 已完成修正后 GUI 口径下的主线 blind A/B 复核：
  - 听评包：`reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005_blind/`
  - 解盲后真实偏好：
    - `legacy_stage2`: `7`
    - `ref_film_sisdr0005`: `1`
    - `tie`: `1`
    - `uncertain`: `3`
  - 当前 `target_clean_plus_music` 上的主观偏好也仍明显更偏向旧主线：
    - `legacy_stage2`: `4`
    - `ref_film_sisdr0005`: `1`
    - `uncertain`: `1`
  - 因此当前不把 `ref_film + stft0.5 + sisdr0.0005` 升为新的默认主线。
  - 当前默认主线保持：
    - `legacy stage2`
- 已补真实验证入口脚本与模板：
  - `scripts/eval/export_ab_inference_from_manifest.py`
  - `data/references/real_eval_manifest_template.jsonl`
  - 后续若整理出真实或近真实样本，只需填 manifest 即可直接导出双模型结果。
- 已为 baseline 训练脚本补充 warm-start 能力：
  - `scripts/train/train_stft_mask_baseline.py` 新增 `--init-checkpoint`
  - 当前支持从既有 checkpoint 加载模型权重后继续微调
- 已完成一轮 `clean_plus_music` 定向微调实验：
  - 实验名：`baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_focus_ft1`
  - 初始化自：`baseline_stft_mask_stage2_ref_film_sisdr0005`
  - focused train manifest：`data/synthetic/train_manifest_clean_plus_music_regression_focus_v1.jsonl`
  - 训练配置：3 epochs / batch size 16 / lr 3e-4
  - 当前整体 eval 相对 `ref_film + sisdr0005` 为：
    - `loss`: `-0.000158`
    - `waveform_l1`: `+0.000012`
    - `stft_l1`: `-0.000340`
    - `sisdr_db`: `+0.067887 dB`
  - 当前 `target_clean_plus_music` recipe 的 `sisdr_db` 改善为：
    - `+0.176268 dB`
- 已导出一套“原主候选 vs clean_plus_music 定向微调”的 blind A/B 试听包：
  - `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_focus_ft1_clean_plus_music_blind/`
  - 当前用于直接核对 focused fine-tune 是否真的救回主观回退点。
- 在暂无试听条件的前提下，已补一轮 purely objective follow-up：
  - 新增 focused manifest 生成脚本 `scripts/data/build_recipe_focused_manifest.py`
  - 新增双 checkpoint 自动对比脚本 `scripts/eval/compare_checkpoints_on_manifest.py`
- 已生成一个来源可复现的 focused manifest：
  - `data/synthetic/train_manifest_clean_plus_music_recipe_focus_v2.jsonl`
  - 当前总样本数 `364`，recipe 预算对齐旧 `v1`
- 已完成 `ref_film_sisdr0005` vs `cpm_focus_ft1` 的自动对比：
  - 全验证集：`avg_sisdr_delta_db = +0.062616`
  - `target_clean_plus_music`：`avg_sisdr_delta_db = +0.177162`
  - 但仍呈现明显“有赢有输”的分布，而非单边支配
- 已完成一轮受控 `ft2`，只替换为可复现 focused manifest：
  - 实验名：`baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_recipe_focus_v2_ft2`
  - train manifest：`data/synthetic/train_manifest_clean_plus_music_recipe_focus_v2.jsonl`
  - warm-start：`baseline_stft_mask_stage2_ref_film_sisdr0005`
  - 训练预算：3 epochs / batch size 16 / lr 3e-4
- `ft2` 当前已成为 focused 分支里的客观最优点：
  - 相对 `base`：
    - `loss`: `-0.000115`
    - `waveform_l1`: `-0.000036`
    - `stft_l1`: `-0.000158`
    - `sisdr_db`: `+0.145066 dB`
  - `target_clean_plus_music`：
    - `avg_sisdr_db`: `-10.319467 -> -10.033389`
    - `avg delta`: `+0.310862 dB`
  - `target_hard_speech` 的退化已较 `ft1` 明显收回：
    - `base`: `-7.002237`
    - `ft1`: `-7.093016`
    - `ft2`: `-7.016520`
- 已补 `base vs ft2` 的 blind A/B 试听包：
  - `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_clean_plus_music_blind/`
- 已完成一轮 very small `ft3`：
  - 实验名：`baseline_stft_mask_stage2_ref_film_sisdr0005_cpm_recipe_focus_v2_ft3`
  - init checkpoint：`cpm_recipe_focus_v2_ft2`
  - lr: `1e-4`
  - 当前只带来很小的客观增益，尚未形成足够强的新证据替代 `ft2`
- 已重构 blind 听评标准并同步到导出脚本：
  - `scripts/eval/export_ab_listening_pack.py`
  - `scripts/eval/export_ab_inference_from_manifest.py`
  - 当前听评表已改为：
    - `better_output`
    - `source_retention`
    - `interference_leak`
    - `volume_fluctuation`
    - `artifact`
    - `decision_tags`
- 已补一套 focused 分支的 guardrail blind pack：
  - `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_recipe_focus_v2_ft2_guardrail_blind/`
  - 当前用于试听 `clean_speech + hard_speech` 副作用边界
- 已补本地 blind listening pack GUI：
  - `scripts/eval/listening_pack_gui.py`
  - 当前支持：
    - blind 包文件夹加载
    - recipe / pattern / 状态筛选
    - `mixture/reference/file_a/file_b/target` 直接播放
    - 峰值统一拉伸开关
    - 结构化打分录入
    - 一键导出 `listening_sheet.csv` 与结果汇总
- 已完成一轮基于 GUI 的 focused 主观听评补回，当前结论更新为：
  - `cpm_focus_ft1` 相对 `ref_film_sisdr0005` 在 `clean_plus_music` 上几乎纯平手
  - `cpm_recipe_focus_v2_ft2` 相对 `ref_film_sisdr0005` 在 `clean_plus_music` 与 guardrail 包上都未形成稳定可听优势
  - 因此当前不把 focused fine-tune 分支升为新的主候选
- 已确认 GUI 早期“峰值统一拉伸”实现与听评原意不一致：
  - 旧实现是按单文件分别拉峰值
  - 现已修正为同一样本目录共享增益
  - 旧口径下的主观结果仍可参考，但在细粒度差异判断上需更谨慎解释
- 已修正仓库内路径的落盘口径：
  - `SyntheticTSEDataset` 下游传递的 `metadata_path`
  - A/B 听评导出、双 checkpoint 对比、baseline train/eval 汇总
  - 后续优先写仓库相对路径，减少工作目录改名导致的恢复偏差
- 已补第一版近真实验证资产：
  - 构建脚本：`scripts/data/build_near_real_eval_manifest.py`
  - manifest：`data/references/real_eval_manifest_near_real_v1.jsonl`
  - 样本目录：`data/references/real_eval_near_real_v1/`
  - blind A/B 包：`reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind/`
- `near_real_v1` 当前覆盖：
  - raw target only
  - target + friend speech
  - target + music
  - target + external speech
  - target absent
  - target absent + music
- 当前该资产明确定位为：
  - near-real eval
  - 不是最终真实现场验证集
- 已为 synthetic 生成器补入 `--output-tag`：
  - 可将 probe 数据写到独立的 `data/synthetic/*_{tag}` 目录与 manifest
  - 避免 side experiment 覆盖主线 `train_manifest.jsonl / val_manifest.jsonl`
- 已完成首轮 small reverb probe：
  - 实验名：`baseline_stft_mask_stage2_legacy_reverb_probe_v1`
  - synthetic tag：`legacy_reverb_probe_v1`
  - train / val：`256 / 64`
  - 轻混响配置：`target_reverb_prob=0.35`、`speech_reverb_prob=0.45`
  - warm-start 自：`baseline_stft_mask_stage2`
- `legacy_reverb_probe_v1` 当前结果为：
  - 默认 val 相对 `legacy stage2`：`sisdr_db -0.264 dB`、`waveform_l1 +0.000129`
  - probe val 相对 `legacy stage2`：`sisdr_db -0.194 dB`、`waveform_l1 +0.000113`
  - 当前不继续沿“target + speech 一起加轻混响”方向扩大训练
- 已完成第二轮 speech-only small reverb probe：
  - 实验名：`baseline_stft_mask_stage2_legacy_speechreverb_probe_v2`
  - synthetic tag：`legacy_speechreverb_probe_v2`
  - train / val：`256 / 64`
  - 轻混响配置：`target_reverb_prob=0.0`、`speech_reverb_prob=0.55`
  - warm-start 自：`baseline_stft_mask_stage2`
- `legacy_speechreverb_probe_v2` 当前结果为：
  - 默认 val 相对 `legacy stage2`：`sisdr_db -0.183 dB`、`waveform_l1 +0.000031`
  - probe val 相对 `legacy stage2`：`sisdr_db -0.195 dB`、`waveform_l1 +0.000034`
  - 在 probe 集上，`target_clean_speech` 与 `target_clean_plus_music` 仅出现 very small 平均改善，整体仍未转正
- 已导出两套 near-real blind A/B 包，用于核对 reverb probe 是否真能修正 near-real 暴露的问题：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_reverb_probe_v1_blind/`
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_speechreverb_probe_v2_blind/`
- `legacy_speechreverb_probe_v2` 的 near-real blind 听评已完成，当前结果为：
  - `legacy_stage2`: `1`
  - `legacy_speechreverb_probe_v2`: `0`
  - `tie`: `8`
  - `uncertain`: `1`
- 当前这轮人听暴露出的新增主观问题为：
  - 输出存在明显“电话音 / 降采样感”式的带宽收窄
  - 更像是某些频率被削掉，而不只是普通噪声或混响伪影
- 已补一版听评包频带诊断脚本：
  - `scripts/eval/analyze_listening_pack_bandwidth.py`
  - 当前可直接对 blind A/B 包输出逐样本带宽收窄指标与摘要
- 已补一版听评包瞬态诊断脚本：
  - `scripts/eval/analyze_listening_pack_transients.py`
  - 当前可直接对 blind A/B 包输出“高频瞬态相对中频是否被削掉”的逐样本指标
- 当前该脚本在 near-real 包上的首轮观察为：
  - `legacy_speechreverb_probe_v2` 没有表现成“全局统一低通”
  - 更像是局部频带 / 高频瞬态 / 清辅音边缘被削掉
  - `legacy_reverb_probe_v1` 的带宽收窄问题比 `v2` 更频繁、更明显
- 当前瞬态诊断的补充观察为：
  - `legacy_speechreverb_probe_v2` 在 `near_real_0005 / 0007 / 0010` 上仍会被标成更 transient-lossy
  - `legacy_reverb_probe_v1` 在 near-real 上的瞬态缺失问题整体比 `v2` 更重
- 已把“瞬态 / 清辅音保真”从纯诊断推进到可训练钩子：
  - `src/tse_prefix/pipeline/baseline_train.py` 新增 `transient_presence_l1_loss`
  - `scripts/train/train_stft_mask_baseline.py` 新增 `--loss-transient-weight`
  - checkpoint / train summary / eval summary 已同步记录 `transient_presence_l1`
- 已完成一轮 transient loss smoke 验证：
  - 训练产物：`experiments/checkpoints/baseline_stft_mask_transient_smoke/`
  - 评估产物：`reports/eval/baseline_stft_mask_transient_smoke_eval/`
  - 说明当前该 loss 已能实际参与 train / val / eval 流程，而不只是停留在诊断脚本层
- 已完成两轮基于 `legacy stage2` 的 small transient-loss warm-start probe：
  - `baseline_stft_mask_stage2_legacy_transient_probe_v1`
    - `transient_weight=0.005`
    - 默认 synthetic val 上 `avg_sisdr_delta_db = -0.412`
    - `transient_presence_l1: 0.7489 -> 0.5665`
  - `baseline_stft_mask_stage2_legacy_transient_probe_v2`
    - `transient_weight=0.002`
    - 默认 synthetic val 上 `avg_sisdr_delta_db = -0.314`
    - `transient_presence_l1: 0.7489 -> 0.5788`
- `legacy_transient_probe_v2` 当前在 focused synthetic recipe 上出现了第一批可保留信号：
  - `target_clean_speech + target_clean_plus_music` 合并后 `avg_sisdr_delta_db = +0.112`
  - 其中：
    - `target_clean_speech`: `+0.263 dB`
    - `target_clean_plus_music`: `-0.105 dB`
- 已导出一套 near-real blind A/B 包，用于直接核对 transient loss 是否真能减轻“电话音 / 瞬态缺失”：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/`
- 已对这套 near-real 包补跑自动诊断，并结合 `blind_key.json` 解码得到：
  - 带宽收窄 heuristic：`legacy_transient_probe_v2` 被标成更窄带 `4` 条，`legacy_stage2` 为 `0` 条，`tie = 6`
  - 瞬态缺失 heuristic：`legacy_transient_probe_v2` 被标成更 transient-lossy `7` 条，`legacy_stage2` 为 `1` 条，`tie = 2`
- `legacy_transient_probe_v2` 的 near-real blind 听评现已完成，当前真实偏好为：
  - `legacy_transient_probe_v2`: `2`
  - `legacy_stage2`: `0`
  - `tie`: `8`
  - `uncertain`: `0`
- 但这两次主观胜出都不算“干净强胜”：
  - `near_real_0005`：仅 very small 差异，主观更像略多保住一点 source retention
  - `near_real_0007`：source retention 更好，但同时带来更多 interference leak
- 当前主观补充观察为：
  - “电话音 / 伪影”主观上似乎有些许减轻
  - 但用户已明确要求这点不计入主结论，当前只作为弱观察保留
- 已完成一轮“更局部、更保守”的 transient-loss 选择器改造：
  - 训练脚本现支持：
    - `--loss-transient-focus-recipes`
    - `--loss-transient-focus-patterns`
    - `--loss-transient-min-target-ratio`
    - `--loss-transient-max-target-ratio`
  - 当前可把 transient loss 只施加到指定 recipe / pattern / ratio 子集，而不是全 batch 默认生效
- 已完成两轮 selector-based transient probe：
  - `legacy_transient_focus_probe_v3`
    - 选择器：`clean_speech + clean_plus_music`，排除 `intermittent`
    - 默认 synthetic val：`avg_sisdr_delta_db = -0.368`
    - 当前不保留
  - `legacy_transient_focus_probe_v4`
    - 选择器：仅 `target_clean_speech`，pattern 限于 `target_full / absent_head / absent_tail`
    - 默认 synthetic val：`avg_sisdr_delta_db = -0.228`
    - `target_clean_speech`: `+0.315 dB`
    - `target_clean_speech + target_clean_plus_music`: `+0.063 dB`
    - 相对全局 `legacy_transient_probe_v2`，当前是更平衡的局部候选
- 已导出 `legacy_transient_focus_probe_v4` 的 near-real blind 包：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_focus_probe_v4_blind/`
- 已对这套 near-real 包补跑自动诊断，并结合 `blind_key.json` 解码得到：
  - 带宽收窄 heuristic：`legacy_transient_focus_probe_v4` 被标成更窄带 `2` 条，`legacy_stage2` 为 `0` 条，`tie = 8`
  - 瞬态缺失 heuristic：`legacy_transient_focus_probe_v4` 被标成更 transient-lossy `7` 条，`legacy_stage2` 为 `1` 条，`tie = 2`
- 已基于 `legacy_transient_leakguard_probe_v1` 完成两轮更细的 leak-guardrail follow-up：
  - `legacy_transient_leakguard_probe_v2_musiconly`
    - 仅对 `target_music / target_clean_plus_music / target_hard_plus_music` 施加 interference selector
    - synthetic 默认 val 相对 `legacy stage2`：`avg_sisdr_delta_db = +0.665876`
    - `interference_projection_ratio = 0.0319`
    - 但相对 `legacy_transient_leakguard_probe_v1`：`avg_sisdr_delta_db = -0.183896`
    - 当前判断：过度向 music-like leakage 收缩，不保留为后续主候选
  - `legacy_transient_leakguard_probe_v3_w0005`
    - 保持全 interference selector，但将 `interference_weight` 从 `0.01` 下调到 `0.005`
    - synthetic 默认 val 相对 `legacy stage2`：`avg_sisdr_delta_db = +0.383818`
    - `waveform_l1` 基本持平，`interference_projection_ratio = 0.0560`
    - 但相对 `legacy_transient_leakguard_probe_v1`：`avg_sisdr_delta_db = -0.465955`
- 已导出并补跑 `legacy stage2 vs legacy_transient_leakguard_probe_v3_w0005` 的 near-real blind 自动诊断包：
  - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v3_w0005_blind/`
- `legacy_transient_leakguard_probe_v3_w0005` 当前 near-real 自动结论为：
  - 带宽收窄 heuristic：`legacy_transient_leakguard_probe_v3_w0005 = 3`，`legacy_stage2 = 0`，`tie = 7`
  - 瞬态缺失 heuristic：`legacy_transient_leakguard_probe_v3_w0005 = 4`，`legacy_stage2 = 4`，`tie = 2`
  - trade-off 解码均值：
    - `target_capture_db`: `-12.578 -> -9.558`
    - `interference_capture_db`: `-45.209 -> -43.697`
    - `retention_minus_leak_db`: `27.905 -> 28.585`
    - `residual_output_share`: `0.661 -> 0.654`
- `legacy_transient_leakguard_probe_v3_w0005` 相对 `v1` 的当前定位为：
  - 更像“更保守、residual 更轻”的 follow-up
  - `more_residual_heavy` 已从 `v1` 的 `6` 条显著收回到 `1` 条
  - 但 `retention_minus_leak_db` 仍低于 `v1`：`28.938 -> 28.585`
  - 且带宽收窄计数从 `2` 条升到 `3` 条
  - 当前仍不足以替代 `legacy_transient_leakguard_probe_v1`

### 进行中

- synthetic 生成器已具备 richer temporal patterns 版本，但仍未覆盖更复杂的多段真实重叠场景。
- clean pool 已完成一轮基于手工声学 embedding 的聚类式去冗余，但尚未上更强的预训练 speaker embedding。
- 公开仓库边界已定义，但首次实际公开提交前仍需人工核对一遍将被纳入的文件集合。
- 公开仓库的 ignore 策略已补过一次“恢复性收口”：
  - checkpoint、音频、synthetic 数据、指向本地资产的 manifest 继续留本地
  - `experiments/**/train_summary.json` 与 `reports/eval/**` 下的小型结构化摘要重新保持可跟踪
- baseline 已进入 stage2，小规模正式训练和分组评估已完成。
- recipe profile 的受控对照已完成，当前已知最佳主线仍是 stage2 默认配比。
- 新的 `ref_film` conditioning 结构与轻量 `SI-SDR loss` 组合已完成 stage2 正式对照与小范围权重扫描，客观上最强候选仍是 `ref_film + stft0.5 + sisdr0.0005`。
- 但该候选已完成修正后 GUI 口径下的主观主线复核，当前未能替代 `legacy stage2`。
- A/B 听感导出流程已落地，后续若补出真实或近真实 manifest，可直接复用同一脚本导出双模型对照结果。
- 已完成一轮 `clean_plus_music` 定向微调试探，但当前仍处于“客观略有改善、主观尚待确认”的状态。
- `clean_plus_music` focused fine-tune 所用 manifest 已存在，但其生成过程尚未正式登记为脚本或文档，当前仍有可恢复性风险。
- 该可恢复性风险已部分缓解：后续 focused manifest 已有正式生成脚本和可复现的 `recipe_focus_v2` 版本。
- 但历史 `regression_focus_v1` 仍不是严格可复刻资产，当前应逐步退出主工作流。
- `recipe_focus_v2` 已经过一轮受控 `ft2` 验证，当前比历史 `v1 + ft1` 分支更值得保留。
- 听评执行环境已从“纯文件夹手动点击”升级为本地 GUI，并已补回 focused 分支的首轮主观结果。
- 当前若还要继续做主观判断，优先改成：
  - 修正后 GUI 口径下的少量关键样本复核
  - 而不是继续整包扩听
- 当前默认优先级已进一步收敛为：
  - 先基于现有主观结果收敛主线判断
  - 暂不继续新增训练分支
- 当前已从“只有真实验证模板”推进到“已有 near-real blind 包待听”的状态。
- 但 `near_real_v1` 仍不是现场真实混合录音集；后续若有更真实素材，仍需继续扩成正式 real eval。
- `near_real_v1` 的 blind 听评已完成，当前结果为：
  - `legacy_stage2`: `6`
  - `ref_film_sisdr0005`: `1`
  - `tie`: `2`
  - `uncertain`: `1`
- 当前 near-real 听评暴露出的新问题聚焦为：
  - 混响输入处理不稳
  - target absent 时出现目标样瞬态
  - 处理中间伪影可能被误当作目标相关成分
- 已在 `scripts/data/build_synthetic_dataset.py` 中补入可选轻混响增强入口：
  - `--target-reverb-prob`
  - `--speech-reverb-prob`
  - 当前默认仍为 `0.0`，用于保持历史主线可复现性
- 当前已完成两轮 small reverb probe：
  - `legacy_reverb_probe_v1` 客观上明显差于 `legacy stage2`
  - `legacy_speechreverb_probe_v2` 明显优于 `v1`，但相对 `legacy stage2` 仍整体小幅回退
- 两套 reverb probe 的 near-real blind 包已导出，但当前尚未完成听评：
  - 当前人工优先级更高的是 `legacy_speechreverb_probe_v2`
- `legacy_speechreverb_probe_v2` 的 near-real blind 听评现已完成：
  - 结果没有形成主观优势
  - 当前更像“多数平手，但更容易带出带宽缺失感”
- 当前已具备一版可复跑的带宽收窄诊断：
  - 可直接复盘听评包里的 `candidate_a / candidate_b`
  - 但阈值和特征仍是第一版，后续还可继续细化
- 当前已具备一版可复跑的瞬态缺失诊断：
  - 可直接把“电话音 / 清辅音被削”拆成 frame-level presence-vs-mid retention 指标
  - 但当前仍是 heuristic 诊断，不作为单独判定主线优劣的唯一依据
- 当前已具备一版可配置的 transient-presence 训练损失钩子：
  - 可作为后续“瞬态 / 辅音保真”候选实验的最小实现基础
  - 但尚未开始正式 budget 下的对照训练
- transient-loss 对照现已完成第一轮 small-budget 试探：
  - 说明它在 synthetic 上能明显压低 `transient_presence_l1`
  - 但默认全分布上仍有较高概率伤到 `target_only / hard_speech / hard_plus_music`
  - 当前还不能把它直接视为“减电话音”的安全主线方案
- transient-loss 候选现已补完 near-real 听评：
  - 没有出现主观负偏好
  - 但也没有形成足够强、足够干净的可听优势
  - 当前更像“多数平手，少量样本上 source retention 有弱收益，但伴随泄漏风险”
- transient-loss 的 selector-based 局部版本现已完成第一轮客观试探：
  - `v3` 证明“选得太宽”并不会自动变稳
  - `v4` 证明“只打 `target_clean_speech`”能把默认全分布代价继续收窄
  - 但自动 near-real 瞬态诊断仍未比全局 `v2` 更明显转正
- leak-guardrail 分支已继续向下做过 `v2_musiconly / v3_w0005` 两轮 follow-up：
  - `v2_musiconly` 已证实为过窄 selector，不再保留
  - `v3_w0005` 已证实“减 residual-heavy”可做到，但还不足以替代 `v1`
- 已完成 `legacy_transient_leakguard_probe_v4_speechfocus_ft1` follow-up：
  - 从 `legacy_transient_leakguard_probe_v1` warm-start
  - 将 `interference selector` 收窄到 `target_clean_speech / target_hard_speech`
  - synthetic 默认 val 相对 `legacy stage2` 为：`avg_sisdr_delta_db = +0.969665`
  - 相对 `legacy_transient_leakguard_probe_v1` 仍有：`avg_sisdr_delta_db = +0.119893`
- 但 `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 的 near-real 自动结论仍未放行：
  - 带宽收窄 heuristic：`legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 3`，`legacy_stage2 = 1`，`tie = 6`
  - 瞬态缺失 heuristic：`legacy_transient_leakguard_probe_v4_speechfocus_ft1 = 7`，`legacy_stage2 = 1`，`tie = 2`
  - trade-off 解码后：`more_interference_leaky = 5`，`better_retention_minus_leak = 2`
  - `near_real_0003 / 0004` 这两条 speech-only 回退点仍未修正
- `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 当前更像：
  - synthetic speech-like recipe 的继续提分版本
  - 以及“只收窄到 speech-only selector 并不会自动修好 speech-only near-real 回退”的诊断性反例
- 已完成 `legacy_transient_leakguard_probe_v5_absentguard_ft1`：
  - 从 `legacy_transient_leakguard_probe_v1` warm-start
  - 新增 `target_absent_intervals -> absent_interval_l1` guardrail
  - `absent_weight = 20`
  - focused 在 `target_clean_speech / target_hard_speech / target_clean_plus_music / target_hard_plus_music`
  - pattern 限于 `target_absent_head / target_absent_tail / target_intermittent`
- `legacy_transient_leakguard_probe_v5_absentguard_ft1` 的 synthetic 结论是：
  - `absent_interval_l1` 相对 `v1` 从 `0.00010835` 降到 `0.00001870`
  - 但默认 val 相对 `legacy stage2` 只剩：`avg_sisdr_delta_db = +0.187692`
  - 相对 `legacy_transient_leakguard_probe_v1` 变成：`avg_sisdr_delta_db = -0.662080`
  - 在 focused absent-guard recipes 上也仍为：`avg_sisdr_delta_db = -0.894569`
- `legacy_transient_leakguard_probe_v5_absentguard_ft1` 的 near-real 自动结论也不放行：
  - 带宽收窄 heuristic：`tie = 9`，`legacy_transient_leakguard_probe_v5_absentguard_ft1 = 1`
  - 瞬态缺失 heuristic：`tie = 2`，`legacy_stage2 = 4`，`legacy_transient_leakguard_probe_v5_absentguard_ft1 = 4`
  - trade-off 解码后：`better_source_retention = legacy_stage2 7`
  - `more_interference_leaky = legacy_stage2 8`
  - `more_residual_heavy = legacy_transient_leakguard_probe_v5_absentguard_ft1 7`
  - `near_real_0003 / 0005 / 0007 / 0010` 仍存在明显过抑制或 transient-lossy 回退
- `legacy_transient_leakguard_probe_v5_absentguard_ft1` 当前更像：
  - 证明 absent leakage 可被显式压低的机制探针
  - 但也是“高权重 target-absent guardrail 会把模型推向 residual-heavy / over-suppressed”的反例
- 已补一个更保守的 quick gate：`legacy_transient_leakguard_probe_v6_absentguard_w5_ft1`
  - 只把 `absent_weight` 从 `20` 收到 `5`
  - `absent_interval_l1` 回到 `0.00004554`
  - 相对 `legacy stage2` 仍有：`avg_sisdr_delta_db = +0.493601`
  - 但相对 `legacy_transient_leakguard_probe_v1` 仍为：`avg_sisdr_delta_db = -0.356172`
  - focused absent-guard recipes 上也仍为：`avg_sisdr_delta_db = -0.501773`
  - 因而未继续导出 near-real blind 包，直接止损
- 当前 objective-only 候选层级已更新为：
  - 第一保留：`legacy_transient_leakguard_probe_v1`
  - 第二保留：`legacy_transient_leakguard_probe_v3_w0005`
  - 诊断参考：`legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - 诊断参考：`legacy_transient_leakguard_probe_v5_absentguard_ft1`
  - 不保留：`legacy_transient_leakguard_probe_v2_musiconly`
- 已为 `scripts/eval/analyze_listening_pack_tradeoff.py` 补充 near-real 场景分桶汇总：
  - `scenario_groups`
  - `target_status_groups`
  - `interference_profile_groups`
  - `target_interference_bucket_groups`
- 已在以下 near-real blind 包上重跑新的 bucketized trade-off 分析：
  - `legacy_transient_leakguard_probe_v1`
  - `legacy_transient_leakguard_probe_v3_w0005`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1`
- 已新增 near-real hard gate 脚本：
  - `scripts/eval/gate_near_real_tradeoff.py`
- 已在以下分支上实际跑出 `gate_summary.json`：
  - `legacy_transient_leakguard_probe_v1`
  - `legacy_transient_leakguard_probe_v3_w0005`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1`
- 当前 hard gate 结果进一步收敛为：
  - `v1` 卡在：
    - `target_present__speech`
    - `target_present__none`
  - `v3_w0005` 只卡在：
    - `target_present__speech`
  - `v4_speechfocus_ft1` 只卡在：
    - `target_present__speech`
  - `v5_absentguard_ft1` 卡在：
    - `target_present__speech`
    - `target_present__none`
- 因此当前 objective-only 小步 follow-up 的真正 gate 已可明确写成：
  - 必须修掉 `target_present__speech`
  - 不能再伤 `target_present__none`
  - 同时不能丢 `target_absent__speech`
- 当前 bucketized 结论进一步收敛为：
  - `legacy_transient_leakguard_probe_v1` 的主收益集中在带 `music` 的桶；
  - 真正还没修好的 near-real 主缺口更明确地落在：
    - `target_present__speech`
    - `target_present__none`
  - `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 没有修好 `target_present__speech`
  - `legacy_transient_leakguard_probe_v5_absentguard_ft1` 虽然修到了 `target_absent__speech`，但把：
    - `target_present__none`
    - `target_present__music`
    - `target_present__music_plus_speech`
    一起推向更 residual-heavy / over-suppressed

### 未开始

- 更真实验证集评估与后续模型结构升级。
- focused fine-tune 在修正后 GUI 口径下，是否还需要做最后一轮小样本复核。
- 在无试听条件下，基于 `recipe_focus_v2` 的下一轮 focused fine-tune 是否值得继续推进。
- 后续是否需要在 `ft2` 基础上继续做更保守的小步 `ft3`。
- `legacy stage2` 与 `ref_film_sisdr0005` 是否还需要仅围绕少量 `uncertain` 样本补最后一轮复核。
- 若后续还要继续做 realism 方向实验，需要先决定是否专门围绕“频带缺失 / 电话音”建立更贴症状的诊断和指标，而不是直接再扩 mixed reverb 训练规模。

## 8. 下一阶段任务

建议按以下顺序推进：

1. 生成 `data/manifests/target_speech_pool.jsonl`。
2. 基于同源切片拆出 `target_reference_pool.jsonl`，保证与 target 采样隔离。
3. 为 `genshin_voice_extract` 建立只含可用 `wav` 的 clean interference manifest。
4. 对 `friend_dataset_fuhuo_raw_concat.wav` 做切片与初筛，形成 hard negative manifest。
5. 为音乐与 singing vocal 建立最小 manifest。
6. 编写首版合成样本生成脚本和元数据格式。

上述 1-6 已完成。当前优先补充：

7. 扩展 synthetic 时序模式，加入 `target intermittent`、`target absent tail` 等场景。
8. 生成一小批更系统的 train/val 样本做人工抽检和抽听。
9. 若 clean pool 还需继续去冗余，可在当前 embedding-pruned 版本基础上补更强的预训练 speaker embedding 聚类。
10. 再决定 baseline 是先做纯 inference 验证，还是直接最小训练闭环。
11. 首次对外推送前，再人工核对一次 `git status` 与将被纳入的文件集合，确保仓库只含公开安全内容。

上述第 7 步已部分完成。当前优先改为：

12. 若继续增强 synthetic realism，可补三段式 intermittent、更多 partial overlap 和 target absent 尾段干扰增强。
13. 在现有 temporal patterns 基础上挑一批样本人工抽听。
14. 在当前 stage1 基础上扩大 synthetic 规模，进入 stage2 训练。
15. 基于现有 eval 入口，补按 recipe、目标占空比、干扰类型的更细粒度统计。
16. 在没有试听环境的前提下，继续以指标和样例导出为主；待有试听条件后再补听感判断。

上述 14-15 已完成。当前优先改为：

17. 基于 stage2 分组指标，针对较难 recipe 补更有针对性的 synthetic 配比或模型改进。
18. 若继续推 baseline，可进入 stage3：
   - 更大 synthetic 规模
   - 更长训练
   - 或更强条件建模结构
19. 条件允许后补听感验证，核对数值改善是否对应真实可听改善。

当前对第 17 点的结论更新为：

20. 不采用 pure `hard_recipe_focus` 作为默认配比；后续若继续调数据分布，应尝试更温和的混合方案或直接转向模型改进。

当前对模型主线的推进补充为：

21. `ref_film` 已完成 stage2 同预算 A/B，对总 loss / STFT 指标有改善，但整体 `sisdr_db` 略退化；当前不升为默认结构。
22. 轻量 `SI-SDR loss` 已验证能有效补齐分离主指标，但收益依赖于与 `ref_film` 结构配合。
23. 小范围权重扫描已完成，当前最佳平衡点为 `sisdr_weight=0.0005`。
24. `sisdr_weight 0.0003 ~ 0.0006` 的窄范围复扫已完成，`0.0005` 仍为当前明确最优点。
25. “继续扫权重”已阶段性停止；当前优先任务改为保留双基线并推进更真实验证或听感验证。
26. 当前主听感对照应固定为：
   - legacy stage2
   - `ref_film + stft0.5 + sisdr0.0005`
27. 在没有正式真实验证 manifest 的前提下，先使用已导出的 synthetic hard-case blind A/B 试听包做人工听感核对。
28. 若后续补出真实样本，优先按 `data/references/real_eval_manifest_template.jsonl` 建清单，再用 arbitrary-pair A/B 导出脚本直接生成真实试听包。
29. 当前人工听感已显示新模型存在 `clean_plus_music` 回退点；后续分析与试听应优先盯这类样本，而不是只看整体平均指标。
30. 若后续听感继续显示“旧模型更稳、新模型更激进”，可把推理期 hybrid 作为低成本退路继续推进。
31. 当前已完成 `clean_plus_music` focused fine-tune 试探；下一步优先听：
   - `reports/eval/ab_listening_pack_ref_film_sisdr0005_vs_cpm_focus_ft1_clean_plus_music_blind/`
32. 在 focused fine-tune 的人工听感出来前，不把 `cpm_focus_ft1` 升为新主线，只把它视作待验证分支。
33. 若后续继续做 focused manifest 实验，必须先把 manifest 的生成规则或脚本正式落盘，避免实验可重复性断掉。
34. 该生成规则已经开始正式化；后续 focused manifest 优先改用：
   - `scripts/data/build_recipe_focused_manifest.py`
   - `data/synthetic/train_manifest_clean_plus_music_recipe_focus_v2.jsonl`
35. 在暂无试听条件时，继续推进的原则改为：
   - 控制实验数量
   - 强制做双 checkpoint 自动对比
   - 同时盯 `clean_plus_music` 收益和 `hard_speech` 侧向代价
36. 当前 focused 客观最优分支已从 `cpm_focus_ft1` 更新为：
   - `cpm_recipe_focus_v2_ft2`
37. 在没有试听条件的前提下，当前不再继续开很多近邻分支；优先保留：
   - `base`
   - `cpm_recipe_focus_v2_ft2`
   作为下一轮真正需要听的对照。
38. `ft3` 已完成，但当前只表现为 very small gain；在没有更强证据前，不把它替换 `ft2` 的位置。
39. 下一步试听范围收敛为两包：
   - 主包：`base vs ft2` / `target_clean_plus_music`
   - guardrail 包：`base vs ft2` / `target_clean_speech + target_hard_speech`
40. 后续盲测填写规则统一改成：
   - 先填 `better_output`
   - 再填四类标签强度
   - 最后补自由备注
41. 当前已具备 GUI 听评入口，下一步不再需要手工逐目录点开 wav；优先直接用 GUI 补回主观结果。
42. 当前阶段若继续推进，默认顺序改为：
   - 先保持 `legacy stage2` 作为默认主线
   - 再决定是否还需要补听 `base vs ft2`
43. 当前 Git 只用于核对改动和恢复，不作为助手自动维护提交记录的工具链环节。
44. 当前已补第一版 near-real blind 包；后续主线听评的第一优先级改为：
   - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_ref_film_sisdr0005_blind/`
45. 若这包 near-real 听评仍偏向 `legacy stage2`，则当前更不应把 `ref_film_sisdr0005` 升为默认主线。
46. 当前这包 near-real 已实际听完，结果继续偏向 `legacy stage2`；主线不切换。
47. 当前下一阶段优先改为：
   - 先补混响 / 尾音拖尾 realism
   - 再专门盯 target absent 下的目标样瞬态与伪影误保留
48. 该 realism 入口已完成第一步工程落地，但尚未正式重建训练集和重训；下一步应先做小规模 reverb probe，再决定是否扩到 stage2 规模。
49. small reverb probe 的当前结论已初步收敛：
   - `legacy_reverb_probe_v1` 不继续扩大
   - `legacy_speechreverb_probe_v2` 暂列为唯一保留的 realism 候选
50. `legacy_speechreverb_probe_v2` 的 near-real blind 听评现已完成：
   - 未形成主观优势
   - 并新增暴露出“电话音 / 带宽收窄感”问题
51. 因此当前不继续加大 mixed reverb 训练预算，优先转回：
   - 梳理更贴近问题类型的 realism 方案
   - 单独加强 `raw target only` 与 `target absent` guardrail
52. 若后续继续推进这条线，优先补：
   - 面向频带缺失的客观诊断
   - 而不是先继续堆新的 reverb 概率或更长训练
53. 上述诊断已进一步落到训练入口：当前可直接基于 `--loss-transient-weight` 开第一轮小预算对照，优先验证“减电话音感”是否能在不明显伤害主线 guardrail 的前提下成立。
54. 这轮小预算对照已完成；当前更接近可保留候选的是 `legacy_transient_probe_v2 (transient_weight=0.002)`，但是否真能减轻 near-real 的“电话音 / 瞬态缺失感”，仍必须以 blind 听评为准。
55. 这包 blind 听评现已完成；当前结论更新为：
   - `legacy_transient_probe_v2` 值得保留，但还不足以升成新主线
   - 若继续推进，优先改成更局部、更保守的 recipe / pattern 约束，而不是直接在默认全分布上扩大 transient loss 预算
56. 上述更局部的 recipe / pattern 约束现已完成第一轮实现与客观试探；训练侧 / synthetic 侧当前最平衡的 selector-based 候选仍是：
   - `legacy_transient_focus_probe_v4`
57. 但 near-real 新增 `tradeoff_analysis` 之后，当前判断已更新为：
   - `legacy_transient_probe_v2` 与 `legacy_transient_focus_probe_v4` 都更像“多保一点目标、也多漏一点干扰”的分支
   - 其中 `legacy_transient_focus_probe_v4` 在新脚本里的 `retention_minus_leak` 表现还不如 `legacy_transient_probe_v2`
58. 上述 leak-guardrail follow-up 现已完成第一轮小预算验证；当前新候选为：
   - `legacy_transient_leakguard_probe_v1`
   - 其 synthetic 默认 val 相对 `legacy_stage2` 已转为明显正增益：
     - `avg_sisdr_delta_db = +0.849772`
   - 且 `interference_projection_ratio` 从：
     - `legacy_stage2: 0.0713`
     - `legacy_transient_focus_probe_v4: 0.0801`
     - 收敛到 `legacy_transient_leakguard_probe_v1: 0.0444`
59. 但 near-real 自动诊断仍未完全放行：
   - 带宽收窄：`legacy_transient_leakguard_probe_v1 = 2`, `legacy_stage2 = 0`, `tie = 8`
   - 瞬态缺失：`legacy_transient_leakguard_probe_v1 = 7`, `legacy_stage2 = 1`, `tie = 2`
   - trade-off 的 `better_retention_minus_leak` 仍是：
     - `legacy_transient_leakguard_probe_v1 = 2`
     - `legacy_stage2 = 3`
60. 因此当前无新增人耳听评条件下，下一步优先级更新为：
   - 以 `legacy_transient_leakguard_probe_v1` 作为当前最佳 objective-only 候选保留
   - 不再单扫更窄的 transient selector
   - 转向修 speech-only near-real 回退点的更细 leak / residual guardrail
61. 本轮新增的 near-real trade-off 自动诊断入口为：
   - `scripts/eval/analyze_listening_pack_tradeoff.py`
   - 已实跑：
     - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_probe_v2_blind/tradeoff_analysis/`
     - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_focus_probe_v4_blind/tradeoff_analysis/`
     - `reports/eval/ab_listening_pack_real_eval_near_real_v1_stage2_vs_legacy_transient_leakguard_probe_v1_blind/tradeoff_analysis/`
62. leak-guardrail follow-up 的更窄 interference selector 已完成第一轮验证：
   - `legacy_transient_leakguard_probe_v2_musiconly`
   - 虽然相对 `legacy stage2` 仍有 `+0.665876 dB` 的 synthetic 默认 val 增益
   - 但相对 `legacy_transient_leakguard_probe_v1` 已出现大面积回退，不再保留
63. 更保守的权重回收版也已完成：
   - `legacy_transient_leakguard_probe_v3_w0005`
   - 当前说明“降低 `interference_weight`”能明显收回 residual-heavy 副作用
   - 但仍未把 near-real 的 leakage / 窄带化风险一起压到足够安全
64. 因此当前 objective-only 候选顺位进一步收敛为：
   - 第一保留：`legacy_transient_leakguard_probe_v1`
   - 第二保留：`legacy_transient_leakguard_probe_v3_w0005`
   - 诊断参考：`legacy_transient_leakguard_probe_v4_speechfocus_ft1`
65. `legacy_transient_leakguard_probe_v4_speechfocus_ft1` 已完成：
   - synthetic 上相对 `legacy stage2` 更强
   - 相对 `v1` 也有小幅正增益
   - 但它没有修正 `near_real_0003 / 0004` 这类 speech-only 回退点
   - 且 `more_interference_leaky` 仍为 `5` 条，`better_retention_minus_leak` 仍落后 `legacy stage2`
66. 因此当前对 `v4_speechfocus_ft1` 的判断是：
   - 可保留为诊断性 follow-up
   - 但不把它抬到 `v1` 或 `v3_w0005` 之前
67. 若继续推进，优先围绕 speech-only near-real 回退点做更细 residual / leak guardrail 或 target-absent guardrail，而不是继续扫 music-only selector、speech-only selector 或单纯降权重
68. `target_absent_intervals` 现已正式接入训练 / 评估管线，当前可直接用 `absent_interval_l1` 同时做 loss 与 metric，不需要再重复补基础工程。
69. 基于这条入口完成的 `legacy_transient_leakguard_probe_v5_absentguard_ft1` 已证明：
   - absent leakage 可以显著下降
   - 但高权重 absent guardrail 会把模型明显推向更强 over-suppression / residual-heavy
   - 因而它不能替代 `v1`，也不进入当前保留候选顺位
70. 进一步补的保守版 `legacy_transient_leakguard_probe_v6_absentguard_w5_ft1` 也未回到 `v1`：
   - 虽然比 `v5` 更温和
   - 但默认全分布与 focused absent-guard recipes 仍都系统性落后于 `v1`
   - 因而当前不再为这条线继续消耗 near-real 诊断预算
71. 若后续继续沿 target-absent guardrail 往下走，只应做更保守的小步版本，并继续同时盯：
   - `absent_interval_l1`
   - 默认 val 相对 `v1` 的回退
   - near-real `more_residual_heavy`
   - near-real `better_source_retention`
   - `near_real_0003 / 0004 / 0005 / 0007 / 0010`
72. 当前公开仓库的 `.gitignore` 策略已按“最大可恢复目标”重新审过一轮：
   - 原始/敏感/重资产继续留本地
   - 但 `train_summary.json`、`eval_summary.json`、compare `summary.json`、blind pack `README.md / blind_key.json / sample_meta.json` 不再被整类忽略
73. 对仍指向本地/非公开资产的 manifest，当前保持本地策略，不直接纳入版本控制；后续若要公开，必须先做脱敏或生成公开安全副本。
74. near-real `tradeoff_analysis` 现已支持按场景家族自动分桶；后续 objective-only 候选默认至少同时看：
   - `target_present__speech`
   - `target_present__none`
   - `target_absent__speech`
75. 当前 bucketized 结果进一步说明：
   - `speech-only selector` 不是当前主问题的根因解；
   - `high-weight absent guardrail` 也不是可直接晋升的主候选解；
   - 若继续小步 follow-up，更适合：
     - 以 `legacy_transient_leakguard_probe_v1` 为主基座
     - 以 `legacy_transient_leakguard_probe_v3_w0005` 为副作用锚点
     - 明确按上述三类桶做 gate，而不是只看整包均值
76. 上述三类桶现已进一步固化为可执行 hard gate；后续 near-real objective-only 候选默认至少要通过：
   - `target_present__speech`
   - `target_present__none`
   - `target_absent__speech`
   的 `gate_near_real_tradeoff.py` 检查，再谈是否值得继续保留
77. 基于上述 gate 的第一条保守 follow-up 已完成：
   - `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
   - 其训练基座为：
     - `legacy_transient_leakguard_probe_v3_w0005`
   - 关键增量为：
     - `absent_weight = 2.0`
     - `absent_focus_recipes = target_clean_speech / target_hard_speech`
     - `absent_focus_patterns = target_absent_head / target_absent_tail / target_intermittent`
78. `v7` 在 synthetic 默认 val 上相对：
   - `legacy_stage2` 仍为正增益：
     - `avg_sisdr_delta_db = +0.461595`
   - `legacy_transient_leakguard_probe_v3_w0005` 也是小幅正增益：
     - `avg_sisdr_delta_db = +0.077777`
   - 因而它更像“`v3` 的保守升级版”，不是新的大步近邻分支
79. `v7` 的 near-real hard gate 结果进一步把它的定位压实为：
   - 相对 `legacy_stage2`：
     - 仍 fail `target_present__speech`
     - 但已 pass：
       - `target_present__none`
       - `target_absent__speech`
   - 相对 `legacy_transient_leakguard_probe_v3_w0005`：
     - 已通过三类关键桶 hard gate
   - 因而它可以替换 `v3_w0005` 成为新的第二保留候选，但还不能替换 `legacy_stage2` 或 `v1`
80. 当前 objective-only 保留顺位更新为：
   - 第一保留：`legacy_transient_leakguard_probe_v1`
   - 第二保留：`legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
   - 第三保留：`legacy_transient_leakguard_probe_v3_w0005`
   - 诊断参考：
     - `legacy_transient_leakguard_probe_v4_speechfocus_ft1`
     - `legacy_transient_leakguard_probe_v5_absentguard_ft1`
81. 因此当前若继续 objective-only 小步推进，默认问题表述应更新为：
   - 不是“再找一个能替代 `v3` 的版本”
   - 而是“以 `v1` 为主基座、以 `v7` 为保守升级锚点，继续修掉 `target_present__speech`，同时不丢 `target_present__none` 与 `target_absent__speech`”
82. 上述 `target_present__speech` 现已进一步落到样本级诊断；当前这个失败桶实际上只包含：
   - `near_real_0003`
   - `near_real_0004`
   - `near_real_0006`
   三条样本，不是一个大样本池的平均性问题
83. 样本级诊断工具现已补齐：
   - `scripts/eval/diagnose_near_real_bucket_failures.py`
   - 当前默认把：
     - tradeoff
     - bandwidth
     - transient
     三路证据统一到 `baseline / candidate` 方向后再看 bucket 内 failure signature
84. 当前 `target_present__speech` 的失败机制已明确拆成三类：
   - `near_real_0003`：
     - 以 over-suppression / residual-heavy + transient loss 为主
   - `near_real_0004`：
     - 以 speech leak trade-off 为主
   - `near_real_0006`：
     - 以 transient loss 为主
85. 因此当前最有价值的无听审推进，不再是继续扫“统一的 loss / selector 小改动”，而是先把这三种失败形态映射回 synthetic / objective 训练可控项；否则单一 follow-up 很容易在：
   - `0003`
   - `0004`
   - `0006`
   之间互相打架
86. 若只允许继续推进 1 条 objective-only follow-up，当前更合理的出发点应改为：
   - 以 `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1` 为基座
   - 优先修 `near_real_0006` 这类 transient-only 回退
   - 同时避免把 `near_real_0004` 再推回 speech leak
   而不是继续做更泛化的 absent guard 或 speech-only selector 扫描
87. 当前已补一套 synthetic-compatible 的 near-real 微型 probe：
   - `scripts/data/build_near_real_speech_probe_manifest.py`
   - manifest:
     - `data/probes/near_real_speech_probe_v1_manifest.jsonl`
   - 样本锚点只覆盖：
     - `near_real_0003`
     - `near_real_0004`
     - `near_real_0006`
   - 并只使用：
     - `friend_raw`
     - `guodegang_raw`
     这两类真实近源语音干扰族
88. 上述 probe 当前共 24 条样本，核心作用不是替代 near-real hard gate，而是作为未来 objective-only 小步 follow-up 的预筛：
   - 先判断 candidate 是否更接近当前 near-real speech bucket 的真实排序
   - 再决定是否值得消耗 near-real blind 包诊断预算
89. 当前已新增配套汇总入口：
   - `scripts/eval/analyze_near_real_speech_probe.py`
   - 并已实跑：
     - `legacy_stage2 vs legacy_transient_leakguard_probe_v1`
     - `legacy_stage2 vs legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
     - `legacy_transient_leakguard_probe_v1 vs legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
90. 这个微型 probe 给出的排序与先前 broad synthetic speech proxy 不同，而且更贴近 near-real 诊断：
   - 相对 `legacy_stage2`
     - `v1`：`avg_sisdr_delta_db = -1.559718`
     - `v7`：`avg_sisdr_delta_db = -0.629166`
   - 相对 `v1`
     - `v7`：`avg_sisdr_delta_db = +0.930552`
     - `improved_count = 24 / 24`
91. 当前这一结果进一步压实了 `v7` 作为 speech-only near-real follow-up 基座的定位：
   - `v7` 虽仍未整体超过 `legacy_stage2`
   - 但它在这套更近真实的 speech probe 上，已经比 `v1` 更稳
   - 因而后续若继续 objective-only，小步修正应默认从 `v7` 出发，而不是重新回到 `v1` 主导
92. 该 probe 还把下一步问题进一步收窄为：
   - `near_real_0006` 型的 `guodegang_raw / transient_like` 子问题，`v7` 已相对 `legacy_stage2` 转正
   - 当前剩余主缺口主要集中在：
     - `near_real_0003` 型 `friend_raw / residual_transient_like`
     - `near_real_0004` 型 `friend_raw / speech_leak_like`
93. 因而当前若继续自动推进，最合理的下一个实验设计目标应更新为：
   - 以 `v7` 为基座
   - 只针对 `friend_raw` 的 `0003 / 0004` 型 speech overlap 回退做更保守修正
   - 同时把 `near_real_0006` 型已拿回的 transient-like 收益当成 guardrail，不允许再回吐
94. 上述方向现已完成第一条 very small focused fine-tune：
   - `legacy_transient_leakguard_probe_v8_friend_overlap_focus_ft1`
   - warm-start:
     - `legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1`
   - focused train manifest:
     - `data/synthetic/train_manifest_friend_overlap_focus_v1_combo.jsonl`
   - focused val manifest:
     - `data/synthetic/val_manifest_friend_overlap_focus_v1_combo.jsonl`
95. 这条 focused manifest 不是重造 synthetic 数据，而是从现有 default split 里筛出更接近 `0003 / 0004` 的样本：
   - `target_hard_speech + target_full + overlap >= 0.9`
   - 加上一批 `target_clean_speech + target_full + overlap >= 0.9 + gain in [-6, -3.5]`
   - 当前规模为：
     - train `72`
     - val `26`
   - 新增筛选脚本：
     - `scripts/data/build_metadata_focused_manifest.py`
96. `v8` 相对 `v7` 的 default synthetic val 出现可接受但不可忽略的回退：
   - `avg_sisdr_delta_db = -0.191305`
   - 因而它不是“无代价升级”
97. 但 `v8` 在 near-real speech micro probe 上相对 `v7` 已形成明确正增益：
   - overall:
     - `avg_sisdr_delta_db = +0.392748`
   - `friend_raw`:
     - `avg_sisdr_delta_db = +0.556688`
   - 锚点：
     - `near_real_0003 = +0.421242`
     - `near_real_0004 = +0.692135`
   - 代价主要是：
     - `near_real_0006 = -0.099073`
98. `v8` 相对 `legacy_stage2` 的 direct micro-probe 表现也继续优于 `v7`：
   - overall:
     - `avg_sisdr_delta_db = -0.236418`
   - 相比 `v7` 的 `-0.629166` 明显更接近放行
   - 分锚点为：
     - `near_real_0003 = -1.116950`
     - `near_real_0004 = -0.220142`
     - `near_real_0006 = +1.059967`
99. `v8` 已进一步经过真实 near-real 自动诊断链验证：
   - hard gate 仍然 `FAIL`
   - 但仍然只 fail：
     - `target_present__speech`
   - `target_present__none`
   - `target_absent__speech`
   继续保持 `PASS`
100. `v8` 当前在真实 near-real `target_present__speech` bucket 内的 failure signature 已比旧 `v7` 更收敛：
   - 不再出现 `more_residual_heavy`
   - 当前主要剩：
     - `near_real_0003`: `lost_retention_minus_leak + more_transient_lossy`
     - `near_real_0004`: `lost_retention_minus_leak + more_interference_leaky`
     - `near_real_0006`: `more_transient_lossy`
101. 因而当前对 `v8` 的定位应写成：
   - 它是当前 speech-bucket-focused follow-up 线上最值得保留的新候选
   - 已经比 `v7` 更接近修正 `friend_raw` 的 `0003 / 0004`
   - 但仍未通过真实 near-real hard gate
   - 也不能替代 `legacy_stage2`
102. 若下一步继续自动推进，默认问题应再进一步收窄为：
   - 保住 `v8` 对 `friend_raw / 0003 / 0004` 的改善
   - 同时把 `guodegang_raw / 0006` 的 transient-like回退重新拉回至少 `v7` 水平
   - 并避免 default synthetic val 再继续显著回吐
103. 本轮已新增 `scripts/eval/gate_speech_probe_followup.py`，把 speech-focused follow-up 的 branch-local keep/drop 规则正式脚本化：
   - 共用 `stage2` 基线
   - 检查 default val 总体增益是否只在容忍范围内回吐
   - 检查 near-real speech micro probe 的 `0003 / 0004` 是否继续改善
   - 检查 `0006` 是否只在允许阈值内轻微回退
   - 检查真实 near-real hard gate 的 fail bucket 不得扩张
104. 这套 gate 的默认阈值当前固定为：
   - `max_default_regression_db = 0.2`
   - `min_anchor_0003_gain_db = 0.0`
   - `min_anchor_0004_gain_db = 0.0`
   - `max_anchor_0006_regression_db = 0.1`
105. 用这套 gate 回放 `v7 -> v8` 的结果为 `PASS`：
   - `v8` 相对 `v7` 的 default val 回吐为 `-0.191305 dB`
   - 仍在 `0.2 dB` 容忍线内
   - `0003 = +0.421242 dB`
   - `0004 = +0.692135 dB`
   - `0006 = -0.099073 dB`
   - fail bucket 仍只剩 `target_present__speech`
106. 同一套 gate 回放 `v1 -> v7` 的结果为 `FAIL`：
   - 唯一失败项是 `default_stage2_delta_floor`
   - 说明 `v7` 虽然是更好的 speech-bucket branch-local follow-up
   - 但还不能把它当成相对 `v1` 的 broad objective-only 升级版
107. 因而当前自动推进口径应再明确一层：
   - `v8` 现在是 speech-focused 分支的默认基座
   - 未来 `v9+` 应先过 `gate_speech_probe_followup.py`
   - 再决定是否值得继续跑完整 near-real 自动诊断链或进入听审候选
108. 本轮已把 `scripts/data/build_metadata_focused_manifest.py` 升级为支持 target transient 指标过滤：
   - `target_transient_presence_minus_mid_db_mean`
   - `target_transient_presence_share_mean`
   - `transient_filter_mode = all | any`
109. 基于这个入口，本轮构造了 `v9` 的 `hard transient` 双焦点数据：
   - 新 hard 子集：
     - `train_manifest_hard_transient_focus_v1_any.jsonl = 21`
     - `val_manifest_hard_transient_focus_v1_any.jsonl = 5`
   - 再把它叠加到 `v8` 的 friend-focused combo 上，形成：
     - `train_manifest_v9_dualfocus_v1.jsonl = 93`
     - `val_manifest_v9_dualfocus_v1.jsonl = 31`
110. `v9 = legacy_transient_leakguard_probe_v9_v8_dualfocus_hardtransient_ft1` 已完成训练与预筛：
   - init:
     - `v8`
   - budget:
     - `72` steps
   - default 相对 `stage2`：
     - `+0.224121 dB`
   - default 相对 `v8`：
     - `-0.046169 dB`
111. 但 `v9` 在 near-real speech micro probe 上未通过 branch-local gate：
   - 相对 `stage2` overall:
     - `-0.252293 dB`
   - 相对 `v8` overall:
     - `-0.015875 dB`
   - fail rules:
     - `speech_probe_overall_floor`
     - `anchor_0006_regression_floor`
112. `v9` 的失败形态很明确：
   - 它对 `friend_raw` 其实略有改善：
     - `v8 -> v9 friend_raw = +0.073949 dB`
     - `0003 = +0.064120 dB`
     - `0004 = +0.083778 dB`
   - 但对真正想补的 `guodegang_raw / 0006` 是系统性回退：
     - `v8 -> v9 0006 = -0.285347 dB`
     - `guodegang_raw = -0.285347 dB`
     - `6 / 6` 样本全部 regression
113. 因而当前应把结论明确更新为：
   - `v9` 不是保留候选
   - 当前 synthetic `hard/full-overlap/transient` proxy 不能作为 `0006` 的可靠训练代用
   - 下一步最有价值的工作，应从“继续开小微调”切回到“重做 `0006` 的 objective proxy / guardrail”
114. 本轮已把 near-real speech probe v1 正式拆成两个可复用子 probe：
   - `data/probes/near_real_friend_speech_probe_v1_manifest.jsonl = 18`
   - `data/probes/near_real_guodegang_transient_probe_v1_manifest.jsonl = 6`
115. 同时新增两个基础工具：
   - `scripts/data/build_probe_subset_manifest.py`
   - `scripts/eval/gate_probe_subset_guardrail.py`
   它们用于从现有 probe manifest 生成 anchor/family 子集，并把 focused probe 的 keep/drop 规则脚本化。
116. `near_real_guodegang_transient_probe_v1` 已经把 `0006` 的客观排序固定下来：
   - `v7 = +1.159040 dB`
   - `v8 = +1.059967 dB`
   - `v9 = +0.774620 dB`
   - 当前是单调 `v7 > v8 > v9`
117. 这条子 probe 也证实了 `v9` 的失败不是噪声，而是系统性回退：
   - `v8 -> v9 = -0.285347 dB`
   - `guodegang_raw = -0.285347 dB`
   - `near_real_0006 = -0.285347 dB`
   - `6 / 6` 样本全部 regression
118. 因而从本轮起，`near_real_guodegang_transient_probe_v1` 应被视为 `v10+` 的前置硬门槛：
   - 任何声称“在补 `0006`”的 follow-up
   - 都应先在这条子 probe 上至少不弱于当前参考版本
   - 否则不值得继续投入更重的训练或 near-real 自动链
119. 本轮已把“重做 `0006` objective proxy”进一步落到可执行搜索：
   - 新启用：
     - `scripts/eval/search_synthetic_proxy_candidates.py`
   - 输出：
     - `reports/eval/synthetic_proxy_search_v7_v8_v9_on_default/summary.json`
   - 搜索目标是：
     - 在 default synthetic speech rows 上找能复现
       - `v7 > v8 > v9`
       排序的 metadata-defined 子集
120. 这次搜索给出的 top order-pass 结果非常一致，当前最接近 `guodegang / 0006` 排序的 synthetic proxy 不是：
   - `target_hard_speech + target_full + high-overlap + transient-rich`
   而是更偏：
   - `target_clean_speech`
   - `target_full`
   - `target_present_ratio >= 0.95`
   - `overlap >= 0.75`
   - `speech_interference_clean_pool`
   - `target_transient_presence_minus_mid_db_mean >= -11.5350723`
121. 基于上述搜索结果，本轮已正式物化：
   - `data/synthetic/train_manifest_guodegang_proxy_v1.jsonl = 85`
   - `data/synthetic/val_manifest_guodegang_proxy_v1.jsonl = 31`
   它们现在可以作为：
   - `v10+` 的 synthetic 预筛 / focused fine-tune 入口
   - 以及 future branch-local compare 的固定锚点
122. 本轮已在 `val_manifest_guodegang_proxy_v1.jsonl` 上重跑 checkpoint compare，并确认它能独立复现 near-real `0006` guardrail 的正确排序：
   - 相对 `legacy_stage2`：
     - `v7 = +1.916698 dB`
     - `v8 = +1.032723 dB`
     - `v9 = +0.866308 dB`
   - branch-local：
     - `v7 -> v8 = -0.883974 dB`
     - `v8 -> v9 = -0.166415 dB`
123. 因而当前对下一步的默认口径应更新为：
   - 若继续自动推进，不再从 `hard_transient_focus_v1_any` 出发
   - 而是把 `guodegang_proxy_v1` 当作新的 synthetic 预筛入口
   - 同时继续保留：
     - `near_real_guodegang_transient_probe_v1`
     作为不可跳过的真实侧 guardrail
124. 基于上述入口，本轮已实际执行一条 very small focused fine-tune：
   - `legacy_transient_leakguard_probe_v10_v8_guodegang_proxy_ft1`
   - warm-start:
     - `v8`
   - focused train/val:
     - `train_manifest_guodegang_proxy_v1.jsonl`
     - `val_manifest_guodegang_proxy_v1.jsonl`
125. `v10` 在 synthetic 侧并不是空转：
   - 相对 `v8`
     - default: `-0.031839 dB`
     - `guodegang_proxy_v1`: `+0.480623 dB`
   - 相对 `v8` 的 broad near-real speech probe：
     - overall: `+0.080006 dB`
     - `0003 = +0.280721 dB`
     - `0004 = +0.211316 dB`
126. 但 `v10` 仍然明确失败在真正关键的 `guodegang / 0006` 上：
   - 相对 `v8` 的 `near_real_guodegang_transient_probe_v1`：
     - overall: `-0.418033 dB`
     - `6 / 6` 样本全部 regression
   - 对应 gate 结果：
     - `gate_speech_probe_followup.py`: `FAIL`
       - failed:
         - `anchor_0006_regression_floor`
     - `gate_probe_subset_guardrail.py`: `FAIL`
       - failed:
         - `overall_floor`
         - `family__guodegang_raw`
         - `anchor__near_real_0006`
127. 这说明当前判断还要再收窄一步：
   - `guodegang_proxy_v1` 比旧 proxy 更像，但还不够像
   - 单边 `guodegang` focused 微调会继续把分支推向：
     - 更强 `friend_raw / 0003 / 0004`
     - 更弱 `guodegang_raw / 0006`
128. 本轮进一步补的失败面搜索：
   - `reports/eval/synthetic_proxy_search_v8_v10_on_default/summary.json`
   显示当前最稳定支持 `v8 > v10` 的 synthetic 子集集中在：
   - `target_hard_speech`
   - `target_full`
   - `overlap >= 0.9`
   - `speech_interference_hard_pool`
   - `friend_hard_negative_segments`
129. 因而当前下一步若继续自动推进，最合理的问题表述应更新为：
   - 不是再做“单边 `guodegang_proxy_v1` 微调”
   - 而是做一条双锚点平衡 follow-up：
     - 用 `guodegang_proxy_v1` 做正向 focused 信号
     - 用 `friend_hard_negative_segments / hard full-overlap` 做反向 guardrail
   - 同时继续要求通过：
     - `near_real_guodegang_transient_probe_v1`
130. 上述双锚点入口现已实际执行为：
   - `legacy_transient_leakguard_probe_v11_v8_dualanchor_ft1`
   - `train_manifest_v11_dualanchor_v1.jsonl = 136`
   - `val_manifest_v11_dualanchor_v1.jsonl = 49`
   - 其中保留：
     - `guodegang_proxy_v1` train/val `85 / 31`
   - 新增：
     - `target_hard_speech + target_full + speech_interference_hard_pool(friend_hard_negative_segments)` train/val `51 / 18`
131. `v11` 在 synthetic 侧继续放大了 dual-anchor 的“看起来像成功”信号：
   - 相对 `legacy_stage2`
     - default: `+0.190317 dB`
     - `guodegang_proxy_v1`: `+1.828146 dB`
   - 相对 `v8`
     - default: `-0.079973 dB`
     - `guodegang_proxy_v1`: `+0.795423 dB`
132. 但 `v11` 的 broad near-real speech micro probe 相对 `v8` 仍然是典型的“一边继续变强、一边继续被推坏”：
   - overall: `+0.025061 dB`
   - `near_real_0003 = +0.260091 dB`
   - `near_real_0004 = +0.241347 dB`
   - `near_real_0006 = -0.651915 dB`
   - `friend_raw = +0.250719 dB`
   - `guodegang_raw = -0.651915 dB`
133. `v11` 在 focused `near_real_guodegang_transient_probe_v1` 上也未通过保留线：
   - 相对 `legacy_stage2`: `+0.408052 dB`
   - 相对 `v8`: `-0.651915 dB`
   - `6 / 6` 样本全部 regression
   - clip 级别拆开后：
     - `guodegang_absent_480s = +1.228311 dB`
     - `guodegang_anchor_120s = -0.412207 dB`
134. 两套 gate 对 `v11` 的结论已统一：
   - `gate_speech_probe_followup.py`: `FAIL`
     - failed:
       - `anchor_0006_regression_floor`
   - `gate_probe_subset_guardrail.py`: `FAIL`
     - failed:
       - `overall_floor`
       - `family__guodegang_raw`
       - `anchor__near_real_0006`
135. 因而当前结论应继续收紧为：
   - `v11` 不是保留候选
   - “`guodegang_proxy_v1` 正向 focused 信号 + friend hard/full-overlap 反向 guardrail”的 one-shot 双锚点拼法仍然不够
   - 相对同一参考 `v8`，它对真实 `0006` 的回退还比 `v10` 更重：
     - `v10 = -0.418033 dB`
     - `v11 = -0.651915 dB`
136. 当前下一步若继续自动推进，问题表述应再收窄为：
   - 暂不继续沿 `v11` 同配方扩大训练
   - 优先拆开：
     - `guodegang_anchor_120s`
     - `guodegang_absent_480s`
   - 先确认究竟是哪类 `0006` 子问题在被 friend-side guardrail 挤压
   - 在真实 `0006` guardrail 没过之前，不把：
     - `guodegang_proxy_v1` 更强
     - `0003 / 0004` 更强
     当成继续放行理由
137. 上述拆分现已实际落到两条 clip 级子 probe：
   - `data/probes/near_real_guodegang_anchor_probe_v1_manifest.jsonl = 3`
   - `data/probes/near_real_guodegang_absent_probe_v1_manifest.jsonl = 3`
138. `guodegang_anchor_120s` 与 `guodegang_absent_480s` 的真实排序现已确认冲突：
   - `anchor`:
     - `v7 = +0.386009 dB`
     - `v8 = -0.015205 dB`
     - `v10 = -0.292184 dB`
     - `v11 = -0.412207 dB`
     - 排序：`v7 > v8 > v10 > v11`
   - `absent`:
     - `v8 = +2.135139 dB`
     - `v7 = +1.932071 dB`
     - `v10 = +1.576052 dB`
     - `v11 = +1.228311 dB`
     - 排序：`v8 > v7 > v10 > v11`
139. 这说明当前 `near_real_0006` 不能再被视为单一 objective target，而应拆成：
   - `anchor_120s` 子问题，当前更像 `v7`
   - `absent_480s` 子问题，当前更像 `v8`
140. `gate_probe_subset_guardrail.py` 现已支持 `--clip-tags`，因此 clip 级保留线也已正式脚本化：
   - `v7` 相对 `v8` 只 fail：
     - `clip__guodegang_absent_480s`
   - `v10 / v11` 相对 `v8` 则两个 clip 都 fail
141. synthetic proxy 侧也已跟着拆成两条：
   - `guodegang_anchor_proxy_v1`
     - `train = 84`
     - `val = 22`
     - 过滤口径：
       - `target_clean_speech`
       - `target_full`
       - `target_present_ratio >= 0.95`
       - `overlap >= 0.9`
     - 已复现：
       - `v7 > v8 > v10 > v11`
   - `guodegang_absent_proxy_v2_speechonly`
     - `train = 76`
     - `val = 20`
     - 过滤口径：
       - `target_clean_speech / target_hard_speech`
       - `target_full`
       - `target_present_ratio >= 0.95`
       - `overlap >= 0.9`
       - `target_transient_presence_minus_mid_db_mean >= q50`
     - 已复现：
       - `v8 > v7 > v10 > v11`
142. 同时已确认一个新的 proxy 边界：
   - `absent` proxy 若把 `music / singing` 混进来，排序会漂回 `v7 > v8 > v10 > v11`
   - 因而这条 proxy 必须保持 speech-only 边界
143. 因而当前下一步若继续自动推进，默认口径应再更新为：
   - 不再寻找“统一的 `0006` 总 proxy”
   - 而是把：
     - `anchor_120s`
     - `absent_480s`
     当成两条独立 guardrail / proxy 目标
   - 未来任何 `v12+` 都必须同时说明：
     - 更接近哪一条 clip 级排序
     - 是否在另一条 clip 上付出代价
144. 已完成 `legacy_transient_leakguard_probe_v12_v8_anchor_proxy_ft1`：
   - 基座：
     - `v8`
   - focused manifest：
     - `train_manifest_guodegang_anchor_proxy_v1.jsonl = 84`
     - `val_manifest_guodegang_anchor_proxy_v1.jsonl = 22`
   - 相对 `legacy_stage2`：
     - default val：`+0.171113 dB`
     - `near_real_guodegang_transient_probe_v1` overall：`+1.135186 dB`
     - `guodegang_anchor_proxy_v1`：`+1.890848 dB`
     - `guodegang_absent_proxy_v2_speechonly`：`+3.652780 dB`
   - 相对 `v8`：
     - default val：`-0.099178 dB`
     - `near_real_guodegang_transient_probe_v1` overall：`+0.075219 dB`
     - `guodegang_anchor_120s`：`+0.266803 dB`
     - `guodegang_absent_480s`：`-0.116366 dB`
   - `speech_followup_gate` 已通过；
   - 但 clip 级 guardrail 相对 `v8` 仍因 `clip__guodegang_absent_480s` 单项失败而未完全放行。
145. 因而当前默认接班口径应进一步更新为：
   - `v8` 继续保留为 broad speech 参考基座
   - `v12` 作为当前 anchor-focused 第二候选保留
   - 下一步若继续自动推进，问题不再是“再训更宽的 `guodegang` focused 版本”
   - 而是：
     - 如何在不回吐 `v12` 的 `anchor_120s` 收益前提下
     - 给 `guodegang_absent_480s` 增加显式 floor / guardrail
146. 已完成 `legacy_transient_leakguard_probe_v13_v12_anchor_absent_proxy_ft1`：
   - 基座：
     - `v12`
   - focused manifest：
     - `train_manifest_v13_anchor_absent_proxy_v1.jsonl = 114`
     - `val_manifest_v13_anchor_absent_proxy_v1.jsonl = 29`
     - 由 `guodegang_anchor_proxy_v1 ∪ guodegang_absent_proxy_v2_speechonly` 去重并集得到
   - 相对 `legacy_stage2`：
     - default val：`+0.195532 dB`
     - near-real speech probe overall：`+0.028007 dB`
     - `near_real_0003`：`-0.805782 dB`
     - `near_real_0004`：`+0.198835 dB`
     - `near_real_0006`：`+1.022450 dB`
     - `guodegang_anchor_120s`：`+0.092524 dB`
     - `guodegang_absent_480s`：`+1.952375 dB`
   - 相对 `v8`：
     - default val：`-0.074758 dB`
     - near-real speech probe overall：`+0.264425 dB`
     - `near_real_0003`：`+0.311168 dB`
     - `near_real_0004`：`+0.418977 dB`
     - `near_real_0006`：`-0.037517 dB`
     - `guodegang_anchor_120s`：`+0.107729 dB`
     - `guodegang_absent_480s`：`-0.182764 dB`
   - 相对 `v12`：
     - default val：`+0.024419 dB`
     - `near_real_guodegang_transient_probe_v1` overall：`-0.112736 dB`
     - `guodegang_anchor_120s`：`-0.159074 dB`
     - `guodegang_absent_480s`：`-0.066398 dB`
   - `speech_followup_gate_vs_v12` 当前失败项为：
     - `anchor_0006_regression_floor`
   - `probe_subset_guardrail_vs_v8_with_clips` 当前失败项为：
     - `overall_floor`
     - `family__guodegang_raw`
     - `anchor__near_real_0006`
     - `clip__guodegang_absent_480s`
147. 因而当前默认接班口径应再次收紧为：
   - `v13` 不保留
   - 不继续沿 one-shot `anchor + absent` 并集微调路线加预算
   - `v8` 继续保留为 broad speech 参考基座
   - `v12` 继续保留为当前 anchor-focused 第二候选
   - 下一步若继续自动推进，应先重做 `absent` objective proxy / floor
   - 而不是再直接把现有 `absent_proxy_v2_speechonly` 拼进 `v12` 做训练
148. 已完成当前真实排序 `v8 > v12 > v13` 下的 `absent` objective proxy 重建：
   - 搜索输入：
     - `stage2 vs v8 / v12 / v13` on `default` synthetic speech rows
   - 新搜索输出：
     - `reports/eval/synthetic_proxy_search_guodegang_absent_v8_v12_v13_on_default/summary.json`
   - 当前稳定 order-pass 的两条候选为：
     - `guodegang_absent_proxy_v3_strict`
       - `recipe = target_hard_speech`
       - `pattern = target_full`
       - `target_ratio >= 0.95`
       - `overlap >= 0.9`
       - `val = 18`
       - `train = 51`
       - stage2-relative：
         - `v8 = +0.240256 dB`
         - `v12 = +0.088626 dB`
         - `v13 = -0.022755 dB`
     - `guodegang_absent_proxy_v4_broad`
       - 同上，但 `overlap >= 0.75`
       - `val = 39`
       - `train = 122`
       - stage2-relative：
         - `v8 = +0.256340 dB`
         - `v12 = +0.155148 dB`
         - `v13 = +0.050509 dB`
   - 这说明当前 `absent` proxy 已不再落在旧的：
     - `pattern_nonfull`
     - `target_absent_head / tail / intermittent`
     方向上；
   - 而是更接近：
     - `hard speech + target_full + high-overlap`
149. 已完成 `legacy_transient_leakguard_probe_v14_v12_absent_proxy_v3_strict_ft1`：
   - 基座：
     - `v12`
   - focused manifest：
     - `train_manifest_guodegang_absent_proxy_v3_strict.jsonl = 51`
     - `val_manifest_guodegang_absent_proxy_v3_strict.jsonl = 18`
   - 训练摘要：
     - `best_val_loss = 0.023063`
     - `global_steps = 39`
   - 一个关键事实：
     - 当前这条新 proxy 全是 `target_full`
     - 现有 `absent_loss` selector 仍限定在：
       - `target_absent_head`
       - `target_absent_tail`
       - `target_intermittent`
     - 因而本轮 `absent_interval_l1` 自始至终都是：
       - `0.0`
   - 相对 `legacy_stage2`：
     - default val：
       - `+0.072915 dB`
     - near-real speech probe overall：
       - `-0.207776 dB`
     - `near_real_0003`：
       - `-0.923706 dB`
     - `near_real_0004`：
       - `+0.113401 dB`
     - `near_real_0006`：
       - `+0.384354 dB`
     - `guodegang_anchor_120s`：
       - `-0.847514 dB`
     - `guodegang_absent_480s`：
       - `+1.616223 dB`
     - `guodegang_anchor_proxy_v1`：
       - `+1.500173 dB`
     - `guodegang_absent_proxy_v3_strict`：
       - `-0.196222 dB`
   - 相对 `v8`：
     - default val：
       - `-0.197375 dB`
     - near-real speech probe overall：
       - `+0.028642 dB`
     - `near_real_guodegang_transient_probe_v1` overall：
       - `-0.675613 dB`
     - `guodegang_anchor_120s`：
       - `-0.832309 dB`
     - `guodegang_absent_480s`：
       - `-0.518916 dB`
   - 相对 `v12`：
     - default val：
       - `-0.098198 dB`
     - near-real speech probe overall：
       - `-0.210393 dB`
     - `friend_raw`：
       - `-0.030246 dB`
     - `near_real_0003`：
       - `-0.077958 dB`
     - `near_real_0004`：
       - `+0.017465 dB`
     - `near_real_0006`：
       - `-0.750831 dB`
     - `near_real_guodegang_transient_probe_v1` overall：
       - `-0.750831 dB`
     - `guodegang_anchor_120s`：
       - `-1.099112 dB`
     - `guodegang_absent_480s`：
       - `-0.402550 dB`
     - `guodegang_anchor_proxy_v1`：
       - `-0.390675 dB`
     - `guodegang_absent_proxy_v3_strict`：
       - `-0.284848 dB`
   - `speech_followup_gate_vs_v12` 当前失败项为：
     - `speech_probe_overall_floor`
     - `speech_probe_friend_raw_floor`
     - `anchor_0003_gain_floor`
     - `anchor_0006_regression_floor`
   - `probe_subset_guardrail_vs_v8_with_clips` 当前失败项为：
     - `overall_floor`
     - `family__guodegang_raw`
     - `anchor__near_real_0006`
     - `clip__guodegang_anchor_120s`
     - `clip__guodegang_absent_480s`
150. 因而当前默认接班口径应再次更新为：
   - `v14` 不保留
   - 新的 `guodegang_absent_proxy_v3_strict / v4_broad` 保留为 synthetic absent-side eval / guardrail
   - 但不要再把它们直接当作：
     - `v12` 的 single-route warm-start fine-tune objective
   - 因为本轮已经证明：
     - “proxy 排序能复现真实排序”
     - 不等于
     - “直接用该 proxy 微调就能朝真实目标前进”
   - `v8` 继续保留为 broad speech 参考基座
   - `v12` 继续保留为当前 anchor-focused 第二候选
151. 已完成 `legacy_transient_leakguard_probe_v15_v12_anchor_absent_proxy_v3_nudge_ft1`：
   - 基座：
     - `v12`
   - focused manifest：
     - `train_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl = 135`
     - `val_manifest_v15_anchor_absent_proxy_v3_nudge.jsonl = 40`
     - 由：
       - `guodegang_anchor_proxy_v1`
       - `guodegang_absent_proxy_v3_strict`
       去重并集得到
   - 训练配置刻意压小：
     - `epochs = 1`
     - `lr = 1e-5`
     - `global_steps = 34`
     - `absent_weight = 0.0`
   - 相对 `legacy_stage2`：
     - default val：
       - `+0.142876 dB`
     - near-real speech probe overall：
       - `-0.023170 dB`
     - `near_real_0003`：
       - `-0.835371 dB`
     - `near_real_0004`：
       - `+0.112841 dB`
     - `near_real_0006`：
       - `+0.991116 dB`
     - `guodegang_anchor_120s`：
       - `+0.033892 dB`
     - `guodegang_absent_480s`：
       - `+1.948341 dB`
     - `guodegang_anchor_proxy_v1`：
       - `+2.213110 dB`
     - `guodegang_absent_proxy_v3_strict`：
       - `-0.038012 dB`
   - 相对 `v8`：
     - default val：
       - `-0.127415 dB`
     - near-real speech probe overall：
       - `+0.213248 dB`
     - `near_real_guodegang_transient_probe_v1` overall：
       - `-0.068851 dB`
     - `guodegang_anchor_120s`：
       - `+0.049097 dB`
     - `guodegang_absent_480s`：
       - `-0.186798 dB`
   - 相对 `v12`：
     - default val：
       - `-0.028237 dB`
     - near-real speech probe overall：
       - `-0.025787 dB`
     - `friend_raw`：
       - `+0.013641 dB`
     - `near_real_0003`：
       - `+0.010377 dB`
     - `near_real_0004`：
       - `+0.016905 dB`
     - `near_real_0006`：
       - `-0.144069 dB`
     - `near_real_guodegang_transient_probe_v1` overall：
       - `-0.144069 dB`
     - `guodegang_anchor_120s`：
       - `-0.217707 dB`
     - `guodegang_absent_480s`：
       - `-0.070432 dB`
     - `guodegang_anchor_proxy_v1`：
       - `+0.322262 dB`
     - `guodegang_absent_proxy_v3_strict`：
       - `-0.126638 dB`
   - `speech_followup_gate_vs_v12` 当前失败项已收缩为：
     - `speech_probe_overall_floor`
     - `anchor_0006_regression_floor`
   - `probe_subset_guardrail_vs_v8_with_clips` 当前失败项为：
     - `overall_floor`
     - `family__guodegang_raw`
     - `anchor__near_real_0006`
     - `clip__guodegang_absent_480s`
   - `clip__guodegang_anchor_120s` 已重新通过
152. 因而当前默认接班口径应再次收紧为：
   - `v15` 不保留
   - 这条轻量双路 `nudge` 已证明：
     - 可以把 `anchor_120s` 保回来
     - 但仍不会自然补好 `absent_480s`
   - 因而不要继续沿：
     - `v12 + anchor_proxy_v1 + absent_proxy_v3_strict`
     的 warm-start 路线做更小步长搜索
   - `v8` 继续保留为 broad speech 参考基座
   - `v12` 继续保留为当前 anchor-focused 第二候选
153. 已完成 selector 可观测性补强与 smoke 验证：
   - 当前工作树已把以下元数据接入 train / eval batch：
     - `overlap_ratio`
     - `interference_gain_db`
     - `interference_pool`
     - `interference_speaker_name`
   - 新增：
     - `src/tse_prefix/pipeline/loss_selectors.py`
   - `scripts/train/train_stft_mask_baseline.py` 现已支持：
     - 更细的 selector 条件
     - `train_selector_metrics`
     - `val_selector_metrics`
     - `train_summary.json` 内的 selector 命中统计落盘
   - 已用 `tmp/selector_metrics_smoke_v14_style` 做 1-step smoke：
     - `transient.selected_fraction = 1.0`
     - `interference.selected_fraction = 1.0`
     - `absent.selected_fraction = 0.0`
   - 这说明当前代码已经能直接暴露：
     - `v14` 这类“absent loss 名义开启，但 selector 实际 0 命中”的情况
   - 因而下一步若继续设计新的 `absent` objective / gate，应直接依赖这套 selector metrics，而不要再只靠最终 loss 数值反推
154. 已完成 synthetic dual-proxy gate 脚本化：
   - 新增：
     - `scripts/eval/gate_synthetic_dual_proxy.py`
   - 这条 gate 当前固定检查两类条件：
     - `anchor_proxy_v1` 相对 `v12` 不回退
     - `guodegang_absent_proxy_v3_strict / v4_broad` 相对 `v12` 不变差
   - `v12 -> v12` self-check：
     - `PASS`
   - 对已判死路线回放结果：
     - `v13`：
       - `anchor_proxy_v1` 通过
       - `absent_proxy_v3_strict / v4_broad` 双失败
     - `v14`：
       - `anchor_proxy_v1 / absent_proxy_v3_strict / v4_broad` 全失败
     - `v15`：
       - `anchor_proxy_v1` 通过
       - `absent_proxy_v3_strict / v4_broad` 双失败
   - 因而下一步若继续自动推进，应把这条 synthetic dual-proxy gate 当作：
     - 新 absent objective 的 pre-screen
   - 不再只因为：
     - `anchor_proxy_v1` 还在增强
     就误判候选正在修 `absent`
155. 已完成 `v12 > v15 > v13 > v14` 反向 carve-out 搜索与 `v16 / v17` synthetic pre-screen：
   - 新 reverse guardrail proxy：
     - `train_manifest_v16_v12_reverse_guardrail_proxy_v1.jsonl = 39`
     - `val_manifest_v16_v12_reverse_guardrail_proxy_v1.jsonl = 9`
   - 其 metadata 形态集中在：
     - `target_clean_speech`
     - `speech_interference_clean_pool`
     - 高 `interference_gain_db`
     - 高 `target_transient_presence_minus_mid_db_mean`
   - 新联集 manifest：
     - `absent_proxy_v3_strict ∪ reverse_guardrail_proxy_v1`
     - train = `90`
     - val = `27`
   - `v16 = legacy_transient_leakguard_probe_v16_v12_absent_proxy_v3_reverse_guardrail_v1_ft1`
     - selector 命中：
       - transient / interference = `51 / 90`
       - absent = `24 / 90`
     - 相对 `v12`：
       - default = `-0.004540 dB`
       - reverse guardrail proxy = `-0.076261 dB`
       - `anchor_proxy_v1 = +0.298964 dB`
       - `absent_proxy_v3_strict = -0.007883 dB`
       - `absent_proxy_v4_broad = -0.001475 dB`
     - synthetic dual-proxy gate：
       - `FAIL`
       - 仅剩：
         - `absent_proxy_v3_strict`
         - `absent_proxy_v4_broad`
   - `v17 = legacy_transient_leakguard_probe_v17_v12_absent_proxy_v3_reverse_guardrail_v1_absw05_ft1`
     - 仅把：
       - `absent_weight = 1.0 -> 0.5`
     - 相对 `v12`：
       - default = `-0.038008 dB`
       - `anchor_proxy_v1 = -0.532572 dB`
       - `absent_proxy_v3_strict = -0.019250 dB`
       - `absent_proxy_v4_broad = -0.009301 dB`
     - synthetic dual-proxy gate：
       - `FAIL`
       - `anchor + absent` 全回退
156. 因而当前默认接班口径应继续收紧为：
   - `v16` 不保留，也不扩到 near-real
   - `v17` 不保留
   - 但 `v16` 已证明：
     - `absent_proxy_v3_strict + reverse_guardrail_proxy_v1`
     这条 objective 方向显著比 `v13 / v14 / v15` 更接近 synthetic pre-screen
   - 下一步若继续自动推进，优先改的是：
     - `v16` 这条路线里的 transient / interference 预算或 selector
   - 而不是继续：
     - 下调 `absent_weight`
157. 已完成 `v18 / v19` reverse-guardrail follow-up：
   - 二者都固定沿用：
     - `absent_proxy_v3_strict ∪ reverse_guardrail_proxy_v1`
     - 与 `v16` 相同的 selector 命中
   - `v18 = legacy_transient_leakguard_probe_v18_v12_absent_proxy_v3_reverse_guardrail_v1_ti_half_ft1`
     - 仅把：
       - `transient_weight = 0.002 -> 0.001`
       - `interference_weight = 0.005 -> 0.0025`
     - 相对 `v12`：
       - default = `-0.016253 dB`
       - reverse guardrail proxy = `-0.069016 dB`
       - `anchor_proxy_v1 = +0.233116 dB`
       - `absent_proxy_v3_strict = -0.065609 dB`
       - `absent_proxy_v4_broad = -0.042189 dB`
     - synthetic dual-proxy gate：
       - `FAIL`
       - failed：
         - `absent_proxy_v3_strict`
         - `absent_proxy_v4_broad`
   - `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
     - 仅把：
       - `interference_weight = 0.005 -> 0.0075`
     - 相对 `v12`：
       - default = `+0.044902 dB`
       - reverse guardrail proxy = `-0.076964 dB`
       - `anchor_proxy_v1 = +0.346704 dB`
       - `absent_proxy_v3_strict = +0.053602 dB`
       - `absent_proxy_v4_broad = +0.040802 dB`
     - synthetic dual-proxy gate：
       - `PASS`
158. 已补 `v19` near-real 分析与 gate：
   - broad near-real speech probe 相对 `legacy_stage2`：
     - overall = `-0.009309 dB`
     - `friend_raw = -0.414640 dB`
     - `near_real_0003 = -0.913926 dB`
     - `near_real_0004 = +0.084646 dB`
     - `near_real_0006 = +1.206683 dB`
   - broad near-real speech probe 相对 `v12`：
     - overall = `-0.011926 dB`
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
   - `guodegang` probe 相对 `v8`：
     - overall = `+0.146716 dB`
     - `guodegang_anchor_120s = +0.370681 dB`
     - `guodegang_absent_480s = -0.077249 dB`
   - `probe_subset_guardrail_vs_v8_with_clips`：
     - `FAIL`
     - 仅剩：
       - `clip__guodegang_absent_480s`
159. 因而当前默认接班口径应再次更新为：
   - `v18` 不保留
   - `v19` 是当前第一条通过 synthetic dual-proxy gate 的 absent follow-up
   - 但 `v19` 仍不直接晋升主候选
   - 因为它目前的真实形态是：
     - `0006` 与 `guodegang_anchor_120s` 已继续改善
     - `guodegang` 总体也重新超过 `v8`
     - 但 `guodegang_absent_480s` 仍略低于 `v8`
     - broad `friend_raw / 0003 / 0004` 又相对 `v12` 回退
   - 下一步若继续自动推进，不再回到：
     - `v16 / v17 / v18`
   - 而应把问题改写成：
     - 如何以 `v19` 为基座补 friend-side reverse guardrail / branch-local proxy
     - 而不是继续只围绕 `0006 absent` 单边加力
160. 已完成 `v20 = legacy_transient_leakguard_probe_v20_v19_friend_reverse_guardrail_v1_ft1` 与 friend-side selector plumbing 补线：
   - 当前工作树已把以下元数据正式接入：
     - `target_transient_presence_minus_mid_db_mean`
     - `target_transient_presence_share_mean`
   - 并已补到：
     - `src/tse_prefix/data/synthetic_dataset.py`
     - `scripts/train/train_stft_mask_baseline.py`
     - `scripts/eval/eval_stft_mask_baseline.py`
     - `src/tse_prefix/pipeline/loss_selectors.py`
   - `v20` 基座：
     - `v19`
   - train / val manifest：
     - `train_manifest_v20_v19_plus_friend_reverse_guardrail_v1.jsonl = 111`
     - `val_manifest_v20_v19_friend_reverse_guardrail_proxy_v1.jsonl = 35`
   - 相对 `v19`，本轮只新增：
     - train `21`
     - val `8`
   - 这些新增样本全部都是：
     - `target_clean_speech`
     - `target_full`
   - 一个关键事实：
     - `v20` 的 selector 命中数与 `v19` 完全相同：
       - train transient / interference / absent：`51 / 51 / 24`
       - val transient / interference / absent：`18 / 18 / 4`
     - 只是 total count 变成了：
       - train `90 -> 111`
       - val `27 -> 35`
     - 这说明新增的 friend-side reverse guardrail 样本：
       - 没有进入任何专项 selector
       - 只是在现有 objective 外额外吃了 base reconstruction loss
   - 相对 `v19`：
     - default val：
       - `-0.020962 dB`
     - `target_clean_speech`：
       - `-0.104638 dB`
     - `v20_v19_friend_reverse_guardrail_proxy_v1`：
       - `-0.131127 dB`
     - broad near-real speech probe overall：
       - `-0.051919 dB`
     - `near_real_friend_speech_probe` overall：
       - `-0.021704 dB`
     - `near_real_guodegang_speech_probe` overall：
       - `-0.142566 dB`
   - `speech_followup_gate_vs_v12`：
     - `FAIL`
     - failed：
       - `speech_probe_overall_floor`
       - `speech_probe_friend_raw_floor`
       - `anchor_0003_gain_floor`
       - `anchor_0004_gain_floor`
   - `probe_subset_guardrail_vs_v8_with_clips`：
     - `FAIL`
     - 仍仅剩：
       - `clip__guodegang_absent_480s`
     - 但 clip 值进一步从：
       - `v19 = +2.135139 dB`
       - 回退到
       - `v20 = +1.991658 dB`
161. 因而当前默认接班口径应再次收紧为：
   - `v20` 不保留
   - 不继续沿：
     - `v19 + friend_reverse_guardrail_proxy_v1`
     - 这种“无 selector 命中增量的并集 warm-start”路线继续加预算
   - 当前更准确的解释应改写为：
     - `v20` 不是一次真正的 friend-side branch-local guardrail 训练
     - 而是一次只通过 base loss 拉扯 `v19` 的无选择器 nudging
   - 下一步若继续自动推进，应优先做的是：
     - 让 friend-side proxy 进入显式 selector
     - 或先重做能复现 `v12 > v19` friend-side 排序的 synthetic proxy
   - 而不是继续：
     - 复制 `v20` 这类直接并集微调
   - 当前主线应继续保持：
     - `v19` 作为 absent-side objective 基座
     - friend-side 仍待 branch-local proxy / selector 闭环
162. 已完成 `v21 = legacy_transient_leakguard_probe_v21_v19_friend_reverse_guardrail_proxy_v2_transient_extra_ft1`：
   - 本轮新增了 selector `extra` branch 能力：
     - 单个 loss prefix 现在可以同时保留：
       - 原有 selector branch
       - `extra` selector branch
     - 当前已补到：
       - `src/tse_prefix/pipeline/loss_selectors.py`
       - `scripts/train/train_stft_mask_baseline.py`
   - 新 friend-side proxy `v21_v19_friend_reverse_guardrail_proxy_v2` 条件为：
     - `target_clean_speech`
     - `target_full`
     - `target_present_ratio >= 0.95`
     - `overlap_ratio >= 0.9`
     - `speech_interference_clean_pool`
     - `target_transient_presence_minus_mid_db_mean >= -9.179057439168297`
   - proxy manifest：
     - `train_manifest_v21_v19_friend_reverse_guardrail_proxy_v2.jsonl = 25`
     - `val_manifest_v21_v19_friend_reverse_guardrail_proxy_v2.jsonl = 12`
   - 但相对 `v19` 基座去重后，真正新增的唯一样本仍然只有：
     - train `21`
     - val `8`
   - `v21` 训练时：
     - 保留 `v19` 原有 hard friend branch
     - 再把上述 clean/full/high-transient branch 挂到 `transient_extra`
   - selector 命中确实显式增加：
     - train transient / interference / absent：
       - `76 / 51 / 24` out of `111`
     - val transient / interference / absent：
       - `30 / 18 / 4` out of `35`
   - 这说明：
     - `v20` 的“零命中增量”问题已经被解决
     - 新 friend-side branch 确实进了专项 loss
   - 但相对 `v19`：
     - default val：
       - `+0.008857 dB`
     - `v21_v19_friend_reverse_guardrail_proxy_v2`：
       - `-0.076726 dB`
     - broad near-real speech probe overall：
       - `-0.042540 dB`
     - `near_real_guodegang_transient_probe_v1` overall：
       - `-0.122561 dB`
   - stage2-relative speech probe 关键锚点也都低于 `v19`：
     - `friend_raw`：
       - `v19 = -0.414640 dB`
       - `v21 = -0.430507 dB`
     - `0003`：
       - `v19 = -0.913926 dB`
       - `v21 = -0.938342 dB`
     - `0004`：
       - `v19 = +0.084646 dB`
       - `v21 = +0.077329 dB`
     - `0006 / guodegang`：
       - `v19 = +1.206683 dB`
       - `v21 = +1.084122 dB`
   - `speech_followup_gate_vs_v19`：
     - `FAIL`
     - failed：
       - `speech_probe_overall_floor`
       - `speech_probe_friend_raw_floor`
       - `anchor_0003_gain_floor`
       - `anchor_0004_gain_floor`
       - `anchor_0006_regression_floor`
   - `probe_subset_guardrail_vs_v19_with_clips`：
     - `FAIL`
     - failed：
       - `overall_floor`
       - `family__guodegang_raw`
       - `anchor__near_real_0006`
       - `clip__guodegang_anchor_120s`
       - `clip__guodegang_absent_480s`
   - `synthetic_dual_proxy_gate_vs_v12`：
     - `PASS`
     - 但三项 synthetic proxy 仍都低于 `v19`：
       - `anchor_proxy_v1 = +2.026994 dB < v19 +2.237552 dB`
       - `absent_proxy_v3_strict = +0.110022 dB < v19 +0.142228 dB`
       - `absent_proxy_v4_broad = +0.187115 dB < v19 +0.195950 dB`
163. 当前默认接班口径应继续收紧为：
   - `v21` 不保留
   - 但 selector `extra` branch 这层基础设施保留
   - 本轮已经证明：
     - 让 friend-side proxy 显式命中 selector 是必要条件
     - 但不是充分条件
   - 当前更准确的主线解释应改写为：
     - `v20` 失败在于新 branch 根本没进 objective
     - `v21` 则说明：
       - 即便显式进了 objective
       - 当前这批 clean/full/high-transient friend proxy 本身也没有提供足够正确的优化方向
   - 因而下一步若继续自动推进，应优先先做：
     - 更窄、更接近 `0003 / 0004` 的 friend-side proxy 重搜
     - 或更严格的 proxy 前置验证
   - 而不是继续：
     - 对现有 `v21` proxy 扫权重 / 扫 epoch / 扫 lr
164. 已完成 friend-side `samplewise-order-pass` exact proxy 重搜：
   - 本轮把 `scripts/eval/search_synthetic_proxy_candidates.py` 升级为支持：
     - `--require-samplewise-order-pass`
     - 在 top candidate 中落盘 exact `sample_ids`
   - 同时把 `scripts/data/build_metadata_focused_manifest.py` 升级为支持：
     - `--sample-ids-file`
     - 可直接把 exact `sample_id` allowlist 落成 manifest
   - `val/default` 上：
     - 原 shared speech rows = `237`
     - 加上单样本顺序约束 `v12 > v19 > v8` 后，只剩 `38`
   - `train/default` 上补跑 `stage2 vs v8 / v12 / v19` compare 后：
     - single-sample order-pass speech rows = `176`
   - 这说明：
     - 之前很多“均值上 order-pass”的 candidate
     - 实际内部混有大量单样本反向行
165. 上述 exact proxy 重搜已经把下一步结论继续收紧：
   - train 侧 top full candidate exact manifest：
     - `train_manifest_v22_friend_reverse_guardrail_proxy_v3_full_exact.jsonl = 10`
   - val 侧 exact full candidate：
     - `val_manifest_v22_friend_reverse_guardrail_proxy_v3_full_exact.jsonl = 4`
     - ids：
       - `val_000033`
       - `val_000200`
       - `val_000446`
       - `val_000496`
   - val 侧 exact nonfull candidate：
     - `val_manifest_v22_friend_reverse_guardrail_proxy_v3_nonfull_exact.jsonl = 7`
   - 但相对 `v19`：
     - `v21` 在 exact full proxy 上：
       - `-0.065412 dB`
     - `v21` 在 exact nonfull proxy 上：
       - `-0.156167 dB`
   - 也就是说：
     - `v21` 失败不是因为 proxy 只是“太宽”
     - 即便改成 exact、single-sample order-pass 的 full / nonfull 子集
       当前 `v21 transient_extra` objective 仍然低于 `v19`
   - 当前默认接班口径因此再次收紧为：
     - 不直接起 `v22` 训练
     - 不继续对 `v21` 现有 objective 扫更多权重 / epoch / lr
    - 下一步若继续自动推进，应优先改：
      - proxy 语义本身
      - 或 loss 归属
    - 而不是只继续改：
      - proxy 的宽窄
166. 本轮进一步把 friend-side proxy 语义拆成了两个 exact family：
  - `0003-like = residual_transient_like`
    - `train_manifest_v23_friend_reverse_guardrail_proxy_v4_residual_transient_exact.jsonl = 10`
    - `val_manifest_v23_friend_reverse_guardrail_proxy_v4_residual_transient_exact.jsonl = 4`
  - `0004-like = speech_leak_like`
    - `train_manifest_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact.jsonl = 11`
    - `val_manifest_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact.jsonl = 3`
  - 这一步同时确认：
    - `0004-like` 在当前 synthetic order-pass 行里并不更像 `nonfull`
    - 而更像：
      - `target_full`
      - clean pool
      - higher-gain
      - lower-transient
167. 在这两族 exact val proxy 上，`v21 transient_extra` 仍都没有超过 `v19`：
  - residual-transient exact：
    - `compare_v19_vs_v21_on_v23_friend_reverse_guardrail_proxy_v4_residual_transient_exact = -0.065412 dB`
  - speech-leak exact：
    - `compare_v19_vs_v21_on_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact = -0.020621 dB`
  - 因此当前默认接班口径继续收紧为：
    - 不再把 `0003 / 0004` 合并成一个 friend-side proxy
    - 不继续把 `0004-like` 默认并入单一 `transient_extra`
    - 下一步若开新训练，应至少拆成两条 branch-local 语义：
      - `0003-like residual-transient`
      - `0004-like speech-leak`
    - 其中后者更像需要 interference / leak 侧独立归属，而不是继续放在 transient-only 目标里
168. 已完成第一轮 semantic-split 训练侧落地与 follow-up：
  - `v24 = legacy_transient_leakguard_probe_v24_v19_friend_reverse_guardrail_proxy_v4_semantic_split_ft1`
  - `v25 = legacy_transient_leakguard_probe_v25_v19_friend_reverse_guardrail_proxy_v4_semantic_split_ft1`
  - `v26 = legacy_transient_leakguard_probe_v26_v19_friend_reverse_guardrail_proxy_v4_residual_only_ft1`
  - `v27 = legacy_transient_leakguard_probe_v27_v19_friend_reverse_guardrail_proxy_v4_speech_leak_only_ft1`
  - 当前这 4 条 follow-up 的共同点是：
    - friend-side 样本已真实接入 active selector
    - 不再是 `v20` 那种“total count 增了、selected_count 不变”的 base-loss nudging
169. 但 `v24 / v25` 这两版 one-shot semantic split 仍都没有把 friend-side 方向推到 `v19` 之上：
  - `v24` 相对 `v19`：
    - `default = +0.021078 dB`
    - `v24 semantic-split proxy = -0.091072 dB`
    - `near_real_friend_speech_probe = -0.041770 dB`
    - `near_real_guodegang_speech_probe = +0.060570 dB`
  - `v25` 相对 `v19`：
    - `default = +0.028038 dB`
    - `v25 semantic-split proxy = -0.152489 dB`
    - `v25 residual-transient exact = -0.176585 dB`
    - `v25 speech-leak exact = -0.120362 dB`
    - `near_real_friend_speech_probe = -0.037164 dB`
    - `near_real_guodegang_speech_probe = +0.088547 dB`
  - 因而当前不能把：
    - “已经按 `0003 / 0004` semantic split”
    - 误写成：
    - “friend-side objective 已基本闭环”
170. 单侧 carve-out 也没有转正：
  - `v26 residual-only` 相对 `v19`：
    - `default = +0.045235 dB`
    - `residual-only proxy = -0.201198 dB`
    - `near_real_friend_speech_probe = -0.049491 dB`
    - `near_real_guodegang_speech_probe = +0.003146 dB`
  - `v27 speech-leak-only` 相对 `v19`：
    - `default = +0.037512 dB`
    - `speech-leak-only proxy = -0.144539 dB`
    - `near_real_friend_speech_probe = -0.044400 dB`
    - `near_real_guodegang_speech_probe = -0.004776 dB`
  - 因而当前不能把：
    - `0003-like residual-transient`
    - 或 `0004-like speech-leak`
    - 视为已经找到单侧可稳定保留的训练入口
171. 当前默认接班口径应继续收紧为：
  - `v24-v27` 全部不保留为新的主候选
  - `v25` 只能记为：
    - 在这组 follow-up 里 broad overall 代价最小的一版
    - 但仍未通过 exact proxy 与 near-real friend bucket
  - 当前 friend-side 问题已不能再主要归因于：
    - selector 没接上
    - 或两条语义还没拆开
  - 更准确的解释应改写为：
    - 当前 `0003-like / 0004-like` 的 objective-proxy 语义仍不够对
  - 下一步若继续自动推进，不再优先做：
    - `v24-v27` 的权重 / epoch / lr 微扫
  - 而应优先改：
    - `0004-like speech-leak` 的 proxy / objective 语义
    - 或更明确的 branch-local 归属与 guardrail
  - 当前基座继续保持：
    - `v19 = legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`
172. 已完成 `v29 = legacy_transient_leakguard_probe_v29_v19_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact_ft1`，把 `0004-like speech-leak` 首次收紧到 exact sample-id selector：
  - 工程补充：
    - `scripts/data/build_metadata_focused_manifest.py` 新增 `--include-derived-metrics`
    - `scripts/train/train_stft_mask_baseline.py` 新增 `--loss-*-focus-sample-ids-file`
    - `src/tse_prefix/pipeline/loss_selectors.py` 新增 `focus_sample_ids`
  - exact proxy：
    - `train_manifest_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 21`
    - `val_manifest_v29_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 3`
    - plus manifests：
      - `train_manifest_v29_v19_plus_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 111`
      - `val_manifest_v29_v19_plus_friend_reverse_guardrail_proxy_v7_speech_leak_similarity_exact.jsonl = 30`
  - selector 命中：
    - train transient / interference / absent = `51 / 72 / 24` out of `111`
    - val transient / interference / absent = `18 / 21 / 4` out of `30`
    - 其中 `interference_extra` 相对 `v19` 的新增命中正好是 train `+21`、val `+3`
  - 相对 `v19`：
    - default = `-0.004999 dB`
    - `v29 exact speech-leak proxy = -0.142498 dB`
  - 当前解释应进一步收紧为：
    - 即便把 `0004-like speech-leak` 的 selector 边界收成 exact sample-id，
    - 当前 objective / proxy 语义本身仍没有形成正收益
  - 因而：
    - `v29` 不保留为新候选
    - `focus_sample_ids` selector plumbing 保留
    - 下一步若继续自动推进，应优先重做 `0004-like speech-leak` objective / proxy 语义，而不是继续扫这条 exact selector 的权重、epoch、lr
173. 已完成 `v30 = legacy_transient_leakguard_probe_v30_v19_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_ft1`，把 `0004-like speech-leak` 再重写成 `high similarity + low target transient + low interference transient` 的 exact family：
  - 搜索刷新：
    - `search_synthetic_proxy_candidates.py` 新搜索已把：
      - `interference_transient_presence_minus_mid_db_mean`
      - `target_interference_logspec_cosine`
      纳入 `samplewise-order-pass` family 搜索
    - 首次搜出 train / val 都能落盘的 mixed-pattern family：
      - clean pool
      - higher gain
      - higher similarity
      - lower target transient
      - lower interference transient
      - `target_full + absent_head + absent_tail`
  - exact proxy：
    - `train_manifest_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 7`
    - `val_manifest_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 3`
    - plus manifests：
      - `train_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 97`
      - `val_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl = 29`
  - selector 命中：
    - train transient / interference / absent = `51 / 58 / 27` out of `97`
    - val transient / interference / absent = `18 / 21 / 5` out of `29`
    - 这说明新 exact family 已真实进入：
      - `interference_extra`
      - 且因为混入 nonfull 行，也改变了 absent 命中
  - 相对 `v19`：
    - default = `+0.015689 dB`
    - `v30 exact proxy = -0.141952 dB`
    - near-real speech probe overall = `-0.053396 dB`
    - near-real `speech_leak_like (0004) = -0.035911 dB`
  - 当前解释应继续收紧为：
    - 即便把 `0004-like speech-leak` 改写成：
      - `high similarity`
      - `low target transient`
      - `low interference transient`
      的新 exact family，
    - 当前 objective / branch-local guardrail 形式仍没有形成正收益
  - 因而：
    - `v30` 不保留为新候选
    - 不继续围绕这条 family 扫权重、epoch、lr
    - 下一步若继续自动推进，应优先改：
      - `0004-like speech-leak` 的 objective 形式
      - leak-specific guardrail
      - 或更明确的 branch-local loss 归属
174. 已完成 `v31 = legacy_transient_leakguard_probe_v31_v19_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_residualproj_ft1`，在保持 `v30` exact family 不变的前提下，把 interference objective 从 `prediction_projection_ratio` 改成 `residual_projection_ratio`：
  - 工程补充：
    - `src/tse_prefix/pipeline/baseline_train.py`
      - `interference_projection_loss(...)` 新增 `mode`
      - 支持：
        - `prediction_projection_ratio`
        - `residual_projection_ratio`
    - `scripts/train/train_stft_mask_baseline.py`
      - 新增 `--loss-interference-mode`
    - `scripts/eval/eval_stft_mask_baseline.py`
      - 按 checkpoint 自带 `interference_loss_mode` 复算 sample-level interference metric
  - 训练侧：
    - 继续使用 `v30` plus manifests
    - selector 命中与 `v30` 保持一致：
      - train transient / interference / absent = `51 / 58 / 27` out of `97`
      - val transient / interference / absent = `18 / 21 / 5` out of `29`
  - 相对 `v19`：
    - default = `-0.011286 dB`
    - `v30 exact proxy = -0.082113 dB`
    - near-real speech probe overall = `-0.054149 dB`
    - near-real `speech_leak_like (0004) = -0.041094 dB`
  - 相对 `v30`：
    - exact proxy = `+0.059839 dB`
    - near-real speech probe overall = `-0.000753 dB`
    - `friend_raw = +0.006956 dB`
    - `speech_leak_like (0004) = -0.005182 dB`
    - `transient_like (0006) = -0.023880 dB`
  - 当前解释应进一步收紧为：
    - 仅把 interference objective 从整段预测投影比切到残差投影比，
    - 的确能部分缩小 exact speech-leak proxy 的回退；
    - 但还不足以把 `v19` 之上的 default / near-real 一起拉正
  - 因而：
    - `v31` 不保留为新候选
    - `residual_projection_ratio` 可保留为后续 primitive
    - 下一步若继续自动推进，应优先补：
      - leak-specific guardrail
      - friend-side 提升与 `guodegang / 0006` 保护的解耦
      - 或更局部的 residual constraint，而不是继续扫这条 mode 的权重/epoch/lr
175. 已完成 `v32 = legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1`，在不改 `v30` exact family 的前提下，首次把 base interference 与 `interference_extra` 做成真正 branch-local 的不同 objective：
  - 工程补充：
    - `loss_selectors.py` 新增：
      - `build_branch_selector_sample_weights(...)`
      - `merge_selector_sample_weights(...)`
    - `compute_losses(...)` 新增：
      - `interference_extra_sample_weights`
      - `interference_extra_weight`
      - `interference_extra_loss_mode`
    - train / eval summary 新增：
      - `interference_extra_projection_ratio`
      - `interference_extra` selector metrics
  - branch-local interference 挂法：
    - base interference：
      - `weight = 0.0075`
      - `mode = prediction_projection_ratio`
    - interference_extra：
      - `weight = 0.0075`
      - `mode = residual_projection_ratio`
      - `focus_sample_ids = v30 exact 10 ids`
  - selector 命中：
    - train transient / interference / interference_extra / absent = `51 / 58 / 7 / 27` out of `97`
    - val transient / interference / interference_extra / absent = `18 / 21 / 3 / 5` out of `29`
  - 相对 `v19`：
    - default = `+0.019034 dB`
    - `v30 exact proxy = -0.121204 dB`
    - near-real speech probe overall = `-0.050465 dB`
    - near-real `speech_leak_like (0004) = -0.041680 dB`
  - 相对 `v31`：
    - default = `+0.030320 dB`
    - exact proxy = `-0.039091 dB`
    - near-real speech probe overall = `+0.003684 dB`
  - 当前解释应更新为：
    - `v31` 的问题确实部分来自“全局 residual 替换过宽”；
    - 只把 residual objective 局部化到 `interference_extra`，可以明显收回 default / near-real 稳定性；
    - 但 exact speech-leak family 仍未被推正
  - 因而：
    - `v32` 不保留为新候选
    - branch-local interference-extra split 能力保留
    - 下一步若继续自动推进，应优先补真正 leak-specific guardrail，而不是把“局部 residual extra 已接通”误写成“speech-leak objective 已闭环”
176. 已完成 `v33 = legacy_transient_leakguard_probe_v33_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_w015_ft1`，只把 `v32` 的 `interference_extra_weight` 从 `0.0075` 提到 `0.015`：
  - 相对 `v19`：
    - default = `+0.020266 dB`
    - `v30 exact proxy = -0.127022 dB`
    - near-real speech probe overall = `-0.050239 dB`
    - near-real `speech_leak_like (0004) = -0.041911 dB`
  - 当前解释应进一步收紧为：
    - branch-local extra residual 的瓶颈不在“weight 还不够大”；
    - 至少在这一档 extra weight 放大下，结构性结果几乎不变
  - 因而：
    - `v33` 不保留为新候选
    - 不继续围绕 `v32 / v33` 扫更多 extra weight
    - 下一步若继续自动推进，应优先做：
      - leak-specific guardrail
      - 或 friend-side / `guodegang` side 的显式解耦保护
177. 已完成 `v34 = legacy_transient_leakguard_probe_v34_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_sisdrguard0002_ft1`，在 `v32` 基础上给 `interference_extra` exact speech-leak family 叠加一条很轻的 weighted SI-SDR guardrail：
  - 工程补充：
    - `compute_losses(...)` 新增：
      - `interference_extra_guard_sisdr_weight`
    - train / eval summary 新增：
      - `interference_extra_guard_sisdr_loss`
  - 相对 `v19`：
    - default = `+0.058461 dB`
    - `v30 exact proxy = +0.026174 dB`
    - near-real speech probe overall = `-0.071357 dB`
    - near-real `speech_leak_like (0004) = -0.045359 dB`
    - near-real `transient_like (0006) = -0.122081 dB`
  - 相对 `v32`：
    - exact proxy = `+0.147378 dB`
    - near-real speech probe overall = `-0.020892 dB`
  - 当前解释应更新为：
    - weighted SI-SDR guard 确实能把 exact speech-leak family 推到整体正增益；
    - 但这并不等于 near-real 也会一起转正；
    - `v34` 更像 exact-family overfit，而不是可保留升级
  - 因而：
    - `v34` 不保留为新候选
    - 不继续沿这条 exact-family sisdr guard 直接扫权重
178. 已完成 `v35 = legacy_transient_leakguard_probe_v35_v19_friend_guard_sisdrplus_guodegang_anchor_guard_ft1`，尝试在 `v34` 的基础上把 `guodegang_anchor_proxy_v1` 当作 decoupling protection 并入训练：
  - 新增样本文件：
    - `sample_ids_guodegang_anchor_proxy_v1_train.txt = 84`
    - `sample_ids_guodegang_anchor_proxy_v1_val.txt = 22`
    - `sample_ids_guodegang_anchor_proxy_v1_all.txt = 106`
  - 新 union manifests：
    - `train_manifest_v35_v19_plus_friend_reverse_guardrail_proxy_v8_plus_guodegang_anchor_proxy_v1.jsonl = 176`
    - `val_manifest_v35_v19_plus_friend_reverse_guardrail_proxy_v8_plus_guodegang_anchor_proxy_v1.jsonl = 47`
  - 训练侧新增：
    - `transient_extra_focus_sample_ids = guodegang_anchor_proxy_v1`
  - 相对 `v19`：
    - default = `+0.061993 dB`
    - `v30 exact proxy = +0.152425 dB`
    - near-real speech probe overall = `-0.078793 dB`
    - near-real `speech_leak_like (0004) = -0.022684 dB`
    - near-real `transient_like (0006) = -0.240638 dB`
    - `near_real_guodegang_anchor_probe_v1 = -0.352486 dB`
  - 当前解释应进一步收紧为：
    - `guodegang_anchor_proxy_v1` 目前不能直接当作 friend-side speech-leak guard 的 decoupling protection；
    - 在这条组合线上，它对真实 `guodegang_anchor_120s` 反而是反向信号
  - 因而：
    - `v35` 不保留为新候选
    - 不继续并更多同类 synthetic `guodegang` proxy 充当保护项
    - 下一步若继续自动推进，应优先考虑：
      - real / near-real gate 优先
      - 或重新设计更贴近 `guodegang_anchor_120s` 的保护代理
179. 已把 friend-side speech-leak follow-up 的 keep/drop 逻辑正式固化成专门 gate，并补跑了 `v34 / v35` 的落盘结果：
  - 脚本：
    - `scripts/eval/gate_friend_speech_leak_followup.py`
  - 新 gate 产物：
    - `reports/eval/compare_v19_vs_v34_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`
    - `reports/eval/compare_v19_vs_v35_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v34.json`
    - `reports/eval/compare_v19_vs_v35_on_near_real_speech_probe_v1/near_real_speech_probe_analysis/friend_speech_leak_followup_gate_vs_v32.json`
  - `v34` relative to `v32`：
    - `overall_pass = false`
    - failed rules：
      - `speech_leak_like_gain_floor`
      - `guodegang_anchor_floor`
      - `guodegang_absent_floor`
  - `v35` relative to `v34`：
    - `overall_pass = false`
    - 虽然：
      - default `+0.003533 dB`
      - exact target_full `+0.102182 dB`
      - near-real `speech_leak_like (0004) = +0.022676 dB`
    - 但仍 failed：
      - `guodegang_anchor_floor = -0.168818 dB`
      - `guodegang_absent_floor = -0.068296 dB`
  - `v35` relative to `v32`：
    - `overall_pass = false`
    - 虽然：
      - exact target_full `+0.204893 dB`
      - near-real `speech_leak_like (0004) = +0.018996 dB`
    - 但仍 failed：
      - `guodegang_anchor_floor = -0.286603 dB`
      - `guodegang_absent_floor = -0.115565 dB`
  - 当前解释应再收紧为：
    - friend-side speech-leak 这条线的 keep/drop，不再由：
      - exact proxy 有没有转正
      - 或 `0004-like speech-leak` 有没有局部回升
      单独决定；
    - 真正的 stop condition 已经收敛到：
      - `guodegang_anchor_floor`
      - `guodegang_absent_floor`
      这两条 real / near-real protection floor
  - 因而：
    - 后续这条线所有新 candidate 默认都先过 friend-side follow-up gate，再讨论是否保留
    - 不再把“speech-leak side gain 变好”误写成“已可保留升级”
    - 下一步若继续自动推进，应优先：
      - 直接围绕 real / near-real gate 设计 guardrail
      - 或重做更贴近 `guodegang_anchor_120s` / `guodegang_absent` 的保护代理
180. 已补齐 `transient_extra / absent_extra` 的真正 branch-local 权重通道，避免后续 `anchor / absent` 保护项只能并回 base 分支同权计算：
  - 工程补充：
    - `src/tse_prefix/pipeline/baseline_train.py`
      - `compute_losses(...)` 新增：
        - `transient_extra_sample_weights`
        - `absent_extra_sample_weights`
        - `transient_extra_weight`
        - `absent_extra_weight`
      - `LossBreakdown` 新增：
        - `transient_extra_presence_l1`
        - `absent_extra_interval_l1`
    - `scripts/train/train_stft_mask_baseline.py`
      - 新增：
        - `--loss-transient-extra-weight`
        - `--loss-absent-extra-weight`
      - train / val summary 新增：
        - `transient_extra_presence_l1`
        - `absent_extra_interval_l1`
      - selector metrics 新增：
        - `transient_extra`
        - `absent_extra`
    - `scripts/eval/eval_stft_mask_baseline.py`
      - eval summary / bucket / sample meta 新增：
        - `transient_extra_presence_l1`
        - `absent_extra_interval_l1`
  - smoke 验证：
    - 训练 smoke：
      - `tmp/smoke_transient_absent_extra/train_summary.json`
      - 已确认：
        - `transient_extra_presence_l1`
        - `absent_extra_interval_l1`
        - `transient_extra / absent_extra` selector metrics
        都能正常落盘
    - 评估 smoke：
      - `tmp/smoke_transient_absent_extra_eval/eval_summary.json`
      - 已确认 eval summary 也会记录上述 extra 字段
  - 当前解释应更新为：
    - 之前 `v35` 的一个真实工程限制是：
      - `guodegang_anchor_proxy_v1` 只能并进原 transient 分支；
    - 现在至少已经具备：
      - `anchor -> transient_extra`
      - `absent -> absent_extra`
      这类分侧轻量保护实验的基础能力
  - 因而：
    - 下一步若继续自动推进，不再优先改老的 `interference_extra_guard_sisdr`
    - 而应优先开一条真正分侧的 protection smoke：
      - `transient_extra = guodegang_anchor_proxy_v1`
      - `absent_extra = guodegang_absent_proxy_v3_strict`
      - 以 friend-side follow-up gate 作为 keep/drop 裁决
181. 第一条真正分侧的 protection smoke `v36` 已完成，并可明确判掉；`anchor transient-extra only` 不是这条线的 keep 路径，`guodegang_absent_proxy_v3_strict` 也仍缺有效 objective：
  - 训练配置：
    - `v36 = v32 + transient_extra(guodegang_anchor_proxy_v1, weight=0.001) + 既有 interference_extra(exact speech-leak)`
    - `guodegang_absent_proxy_v3_strict` 虽被并进 union manifest，但未启用 `absent_extra_weight`
  - 关键工程事实：
    - `train_manifest_v36...` / `val_manifest_v36...` 的规模仍是：
      - train `176`
      - val `47`
      与 `v35` union 相同，没有新增样本；
    - 且这两份 manifest 中：
      - `target_absent_intervals` 非空样本数均为 `0`
    - 所以当前 `guodegang_absent_proxy_v3_strict` 并不能触发 `absent_extra_interval_l1`
  - `v36` relative to `v19`：
    - default `+0.042394 dB`
    - exact proxy overall `-0.038284 dB`
    - exact `target_full = -0.322388 dB`
    - near-real speech probe overall `-0.092008 dB`
    - near-real `speech_leak_like (0004) = -0.042726 dB`
    - near-real `guodegang_anchor_120s = -0.300635 dB`
    - near-real `guodegang_absent_480s = -0.094534 dB`
  - `v36` relative to `v32` 的 `friend_speech_leak_followup_gate`：
    - `overall_pass = false`
    - failed：
      - `exact_target_full_gain_floor`
      - `speech_leak_like_gain_floor`
      - `guodegang_anchor_floor`
      - `guodegang_absent_floor`
  - 当前解释应更新为：
    - 只把 `guodegang_anchor_proxy_v1` 拆到 `transient_extra`，
      不仅没有守住 `guodegang_anchor / absent` 两条 real floor，
      还会把 exact speech-leak side 一并拉回；
    - 所以 `anchor transient-extra only` 不是值得继续扫权重的方向；
    - 真正未解决的缺口仍是：
      - `guodegang_anchor_proxy_v1` 与 real `guodegang_anchor_120s` 的保护错配
      - `guodegang_absent_proxy_v3_strict` 缺少与其语义匹配的独立 objective / branch
  - 额外工程补记：
    - `sample_ids_guodegang_anchor_proxy_v1_{train,val,all}.txt` 原先带 UTF-8 BOM
    - 现已：
      - 将 sample-id loader 改为 `utf-8-sig`
      - 将这 3 个文件重写为无 BOM UTF-8
    - 后续 selector 类实验不应再出现 `\\ufefftrain_000029` 这类脏 sample_id
  - 因而：
    - 下一步不继续开 `guodegang_anchor_proxy_v1` 的 `transient_extra` 权重扫描
    - 若继续推进，应优先补：
      - 面向 `guodegang_absent_proxy_v3_strict` 的新 objective / branch
      - 或更贴近 real / near-real gate 的保护代理
182. 已补齐 `reconstruction / reconstruction_extra` branch-local objective，并完成第一条 absent-side follow-up `v37`；这条线的关键信息不是“又并进了新 manifest”，而是“把早已在 `v32` 基座中的 hard `target_full` 行重新路由到更匹配的 objective”，但 `v37` 仍明确 `FAIL`：
  - 工程补充：
    - `src/tse_prefix/pipeline/baseline_train.py`
      - 新增：
        - `weighted_waveform_l1_loss(...)`
        - `weighted_stft_l1_loss(...)`
      - `LossBreakdown` 新增：
        - `reconstruction_waveform_l1`
        - `reconstruction_stft_l1`
        - `reconstruction_extra_waveform_l1`
        - `reconstruction_extra_stft_l1`
      - `compute_losses(...)` 新增：
        - `reconstruction_sample_weights`
        - `reconstruction_extra_sample_weights`
        - `reconstruction_waveform_weight`
        - `reconstruction_stft_weight`
        - `reconstruction_extra_waveform_weight`
        - `reconstruction_extra_stft_weight`
    - `src/tse_prefix/pipeline/__init__.py`
      - 导出：
        - `weighted_waveform_l1_loss`
        - `weighted_stft_l1_loss`
    - `src/tse_prefix/pipeline/loss_selectors.py`
      - selector config 前缀新增：
        - `reconstruction`
    - `scripts/train/train_stft_mask_baseline.py`
      - 新增 CLI：
        - `--loss-reconstruction-waveform-weight`
        - `--loss-reconstruction-stft-weight`
        - `--loss-reconstruction-extra-waveform-weight`
        - `--loss-reconstruction-extra-stft-weight`
      - train / val summary 与 selector metrics 新增：
        - `reconstruction*` 4 个 loss 指标
        - `reconstruction`
        - `reconstruction_extra`
    - `scripts/eval/eval_stft_mask_baseline.py`
      - eval summary / sample meta / bucket 聚合也同步新增 `reconstruction*` 指标
  - smoke 验证：
    - `tmp/smoke_reconstruction_extra/train_summary.json`
    - `tmp/smoke_reconstruction_extra_eval/eval_summary.json`
    - 已确认 train / eval 两侧都能正常落盘：
      - `reconstruction_extra_waveform_l1`
      - `reconstruction_extra_stft_l1`
      - `reconstruction / reconstruction_extra` selector metrics
  - 一个关键工程事实：
    - `train_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
      与 `train_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
      是：
      - `same_order = true`
      - `same_set = true`
    - `val_manifest_v37_v30_plus_guodegang_absent_proxy_v3_strict.jsonl`
      与 `val_manifest_v30_v19_plus_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact.jsonl`
      也同样：
      - `same_order = true`
      - `same_set = true`
    - 这说明：
      - `guodegang_absent_proxy_v3_strict`
        实际早已完整包含在 `v32` 基座 manifest 中；
      - `v37` 的变化完全来自：
        - objective routing
        - 而不是 manifest coverage
  - `v37 = legacy_transient_leakguard_probe_v37_v32_absent_reconstructionextra_smoke_ft1`
    - 相对 `v19`：
      - default `+0.004330 dB`
      - exact proxy overall `-0.214515 dB`
      - exact `target_full = -0.553167 dB`
      - near-real speech probe overall `-0.093653 dB`
      - near-real `speech_leak_like (0004) = -0.077866 dB`
      - near-real `guodegang_anchor_120s = -0.122504 dB`
      - near-real `guodegang_absent_480s = -0.051134 dB`
    - relative to `v32` 的 `friend_speech_leak_followup_gate`：
      - `overall_pass = false`
      - failed：
        - `exact_target_full_gain_floor`
        - `speech_leak_like_gain_floor`
        - `guodegang_anchor_floor`
        - `guodegang_absent_floor`
  - 当前解释应升级为：
    - `guodegang_absent_proxy_v3_strict`
      当前真正缺的不是“并进 manifest”，
      而是一个语义匹配的独立 objective；
    - `reconstruction_extra`
      比旧 `absent_interval_l1` 更贴近这批 hard `target_full` 行，
      且相对 `v36` 确实把：
      - `guodegang_anchor_120s`
      - `guodegang_absent_480s`
      往回拉了一截；
    - 但 absent-side only 的 `v37`
      仍会把：
      - exact `target_full`
      - near-real `0004-like speech-leak`
      一并拉坏
  - 因而：
    - `v37` 不保留为新候选
    - 后续若继续推进，应优先做：
      - 更轻的 absent reconstruction
      - 与更强的 friend-side protection 联动的再平衡
      - 而不是继续放大 absent-only reconstruction 权重
183. 已完成第一条 `v37` 之后的再平衡 follow-up：`v38 = v32 + lighter waveform-only absent reconstruction + stronger friend-side exact branch`，结果仍明确 `FAIL`，因此这条线当前不值得继续扫配比：
  - 训练配置：
    - checkpoint：
      - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v38_v32_absentreconwave_friendextra_rebalance_ft1`
    - init：
      - `v32`
    - manifest：
      - 直接回到 `v32` base manifest
      - 不再沿用与其完全等价的 `v37` union manifest
    - 相对 `v37` 的变化：
      - `reconstruction_extra_waveform_weight = 0.01`
      - `reconstruction_extra_stft_weight = 0.0`
      - `interference_extra_weight = 0.03`
  - selector 命中：
    - train：
      - `reconstruction_extra = 51 / 97`
      - `interference_extra = 7 / 97`
    - val：
      - `reconstruction_extra = 18 / 29`
      - `interference_extra = 3 / 29`
    - 说明：
      - coverage 与 `v37 / v32` 一致
      - 这次变化只来自 loss 配比
  - `v38` relative to `v19`：
    - default `+0.017846 dB`
    - exact proxy overall `-0.238433 dB`
    - exact `target_full = -0.582605 dB`
    - near-real speech probe overall `-0.093675 dB`
    - near-real `speech_leak_like (0004) = -0.082113 dB`
    - near-real `guodegang_anchor_120s = -0.097188 dB`
    - near-real `guodegang_absent_480s = -0.045739 dB`
  - relative to `v32` 的 `friend_speech_leak_followup_gate`：
    - `overall_pass = false`
    - failed：
      - `exact_target_full_gain_floor`
      - `speech_leak_like_gain_floor`
      - `guodegang_anchor_floor`
      - `guodegang_absent_floor`
  - 与 `v37` 的对照：
    - `v38` 虽然把：
      - default
      - `guodegang_anchor_120s`
      - `guodegang_absent_480s`
      又回拉了一点；
    - 但：
      - exact `target_full`
      - near-real `speech_leak_like (0004)`
      反而比 `v37` 更差
  - 当前解释应进一步收紧为：
    - 一旦 `guodegang_absent_proxy_v3_strict`
      以当前这组 shared hard `target_full` 行的方式接到 `reconstruction_extra`，
      再单纯加大 friend-side `interference_extra_weight`
      也不能把 exact speech-leak side 拉回；
    - 所以当前冲突更像是：
      - absent reconstruction 本身就在改写 shared hard-speech region 的优化方向
      - 而不是 `interference_extra_weight` 还不够大
  - 因而：
    - `v38` 不保留为新候选
    - 下一步不继续扫：
      - `v37 / v38` 这族的 `interference_extra_weight`
      - 或当前 `reconstruction_extra` 配比
    - 若继续推进，应优先：
      - 更细粒度的 absent proxy carve-out
      - 更贴近 real gate 的保护代理
      - 或避免直接作用于 shared hard `target_full` 行的 absent-side objective

## 9. 文档入口

- 规范入口：`docs/00_context_bootstrap.md`
- 当前总览：`docs/01_project_overview_and_plan.md`
- 踩坑记录：`docs/02_pitfalls_log.md`
- 结构说明：`docs/03_project_structure.md`
- 人耳复核指南：`docs/04_human_listening_review_guide.md`
- 初始设计：`initial_design.md`
- 设计评审占位：`initial_design_judg.md`
- 本轮模型条件化升级记录：`reports/daily/2026-03-16_ref_conditioning_upgrade.md`
- 本轮损失对齐与隔离对照记录：`reports/daily/2026-03-16_sisdr_loss_alignment.md`
- 本轮损失权重扫描记录：`reports/daily/2026-03-16_loss_weight_sweep.md`
- 本轮窄范围权重复扫记录：`reports/daily/2026-03-16_loss_weight_narrow_sweep.md`
- 本轮 A/B 试听包准备记录：`reports/daily/2026-03-16_ab_listening_pack.md`
- 本轮主观反馈跟进与 hybrid probe：`reports/daily/2026-03-16_subjective_followup_and_hybrid_probe.md`
- 本轮 `clean_plus_music` 定向微调记录：`reports/daily/2026-03-16_clean_plus_music_focus_finetune.md`
- 本轮“无试听条件下”的客观跟进：`reports/daily/2026-03-16_objective_followup_without_listening.md`
- 本轮受控 `recipe_focus_v2 ft2` 记录：`reports/daily/2026-03-16_recipe_focus_v2_ft2.md`
- 本轮 `ft3` 与听评标准改造：`reports/daily/2026-03-16_ft3_and_listening_rubric.md`
- 本轮 GUI 听评工具记录：`reports/daily/2026-03-17_listening_gui.md`
- 本轮主线 blind A/B 听评结论：`reports/daily/2026-03-17_mainline_ab_listening_review.md`
- 本轮 near-real eval v1 记录：`reports/daily/2026-03-17_near_real_eval_v1.md`
- 本轮 near-real blind 听评结论：`reports/daily/2026-03-17_near_real_listening_review.md`
- 本轮 reverb probe 跟进记录：`reports/daily/2026-03-17_reverb_probe_followup.md`
- 本轮 `legacy_speechreverb_probe_v2` near-real 听评补记：`reports/daily/2026-03-17_reverb_probe_followup.md`
- 本轮 transient loss probe 记录：`reports/daily/2026-03-17_transient_loss_probe.md`
- 本轮 interference leak guardrail probe 记录：`reports/daily/2026-03-17_interference_leak_guardrail_probe.md`
- 本轮 speech-only leak guardrail follow-up：`reports/daily/2026-03-17_speech_only_leakguard_followup.md`
- 本轮 target-absent guardrail follow-up：`reports/daily/2026-03-18_absent_guardrail_probe.md`
- 本轮 near-real trade-off 分桶复盘：`reports/daily/2026-03-18_near_real_tradeoff_bucketization.md`
- 本轮 near-real hard gate 复盘：`reports/daily/2026-03-18_near_real_hard_gate.md`
- 本轮 `v7` 保守 absent-guard follow-up：`reports/daily/2026-03-18_v7_v3_speech_absentguard_w2_ft1.md`
- 本轮 `target_present__speech` 样本级诊断：`reports/daily/2026-03-18_target_present_speech_bucket_diagnosis.md`
- 本轮 near-real speech 微型 probe：`reports/daily/2026-03-18_near_real_speech_probe_v1.md`
- 本轮 `v8` friend-overlap focused follow-up：`reports/daily/2026-03-18_v8_friend_overlap_focus_ft1.md`
- 本轮 speech-focused follow-up gate：`reports/daily/2026-03-18_speech_followup_gate.md`
- 本轮 `v9` dual-focus hard-transient follow-up：`reports/daily/2026-03-18_v9_v8_dualfocus_hardtransient_ft1.md`
- 本轮 `guodegang/0006` 子 probe guardrail：`reports/daily/2026-03-18_guodegang_probe_guardrail.md`
- 本轮 `guodegang/0006` synthetic proxy 搜索：`reports/daily/2026-03-18_guodegang_proxy_search_v1.md`
- 本轮 `v10` guodegang-focused follow-up：`reports/daily/2026-03-18_v10_v8_guodegang_proxy_ft1.md`
- 本轮 `v11` dual-anchor follow-up：`reports/daily/2026-03-18_v11_v8_dualanchor_ft1.md`
- 本轮 `guodegang 0006` clip-split 跟进：`reports/daily/2026-03-18_guodegang_clip_split_followup.md`
- 本轮 `v12` anchor-proxy focused follow-up：`reports/daily/2026-03-18_v12_v8_anchor_proxy_ft1.md`
- 本轮 `v13` anchor+absent union follow-up：`reports/daily/2026-03-18_v13_v12_anchor_absent_proxy_ft1.md`
- 本轮 absent proxy 重建与 `v14` follow-up：`reports/daily/2026-03-18_v14_v12_absent_proxy_v3_strict_ft1.md`
- 本轮轻量 dual-proxy `v15` nudging：`reports/daily/2026-03-18_v15_v12_anchor_absent_proxy_v3_nudge_ft1.md`
- 本轮 synthetic dual-proxy gate：`reports/daily/2026-03-18_synthetic_dual_proxy_gate.md`
- 本轮 reverse guardrail carve-out 与 `v16 / v17` pre-screen：`reports/daily/2026-03-18_v16_v17_reverse_guardrail_probe.md`
- 本轮 `v18 / v19` reverse-guardrail follow-up：`reports/daily/2026-03-18_v18_v19_reverse_guardrail_followup.md`
- 本轮 `v20` friend reverse guardrail follow-up：`reports/daily/2026-03-18_v20_friend_reverse_guardrail_followup.md`
- 本轮 `v21` transient-extra friend reverse guardrail follow-up：`reports/daily/2026-03-18_v21_friend_reverse_guardrail_transient_extra_followup.md`
- 本轮 `v22` samplewise-order-pass friend proxy follow-up：`reports/daily/2026-03-18_v22_friend_proxy_samplewise_search_followup.md`
- 本轮 `v23` friend proxy semantic split follow-up：`reports/daily/2026-03-18_v23_friend_proxy_semantic_split_followup.md`
- 本轮 `v24-v27` friend proxy branch split follow-up：`reports/daily/2026-03-19_v24_v27_friend_proxy_branch_split_followup.md`
- 本轮 `v29` exact speech-leak sample-id selector follow-up：`reports/daily/2026-03-19_v29_exact_speech_leak_sampleid_selector_followup.md`
- 本轮 `v30` similarity + low-transient + low-interference-transient follow-up：`reports/daily/2026-03-19_v30_similarity_lowtransient_lowinttrans_followup.md`
- 本轮 `v31` residual-projection follow-up：`reports/daily/2026-03-19_v31_residual_projection_followup.md`
- 本轮 `v32 / v33` branch-local residual-extra follow-up：`reports/daily/2026-03-19_v32_v33_branch_local_residual_extra_followup.md`
- 本轮 `v34 / v35` guardrail follow-up：`reports/daily/2026-03-19_v34_v35_guardrail_followup.md`
- 本轮 `transient / absent extra` branch-local plumbing：`reports/daily/2026-03-19_transient_absent_extra_branch_plumbing.md`
- 本轮 `v36` anchor transient-extra / absent-union smoke：`reports/daily/2026-03-19_v36_anchor_transientextra_absentunion_smoke.md`
- 本轮 `reconstruction_extra` plumbing 与 `v37` absent follow-up：`reports/daily/2026-03-19_reconstruction_extra_branch_and_v37_absent_followup.md`
- 本轮 `v38` absent-recon-wave / friend-extra rebalance：`reports/daily/2026-03-19_v38_absentreconwave_friendextra_rebalance.md`
- 本轮仓库与 `.gitignore` 审计：`reports/daily/2026-03-18_repo_gitignore_audit.md`
- 本轮全仓库评估总结：`reports/daily/2026-03-17_repo_evaluation_summary.md`
