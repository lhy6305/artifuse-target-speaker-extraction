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

## 归档说明

- 本文档当前只保留 `209` 及之后的活跃记录，便于接班和日常维护。
- 更早的历史记录已拆分归档到 `docs/archive/project_overview/`。
- 归档总索引见 `docs/archive/project_overview/README.md`。

## 当前活跃记录

209. 已把“第二条 branch-local protect selector” 的工程入口补齐；当前可直接把 `target_full` 与 `0004-like speech leak` 拆成两条独立 protect 信号，不需要再改 plumbing：
  - 集中日报：
    - `reports/daily/2026-03-20_branch_protect_guard_plumbing.md`
  - 工程补充：
    - `src/tse_prefix/pipeline/baseline_train.py`
      新增：
      - `branch_protect_guard_sisdr_loss`
      - `branch_protect_sample_weights`
      - `branch_protect_guard_sisdr_weight`
    - `scripts/train/train_stft_mask_baseline.py`
      新增：
      - `--loss-branch-protect-guard-sisdr-weight`
      - `--loss-branch-protect-*`
      - train / val summary 中的
        `branch_protect_guard_sisdr_loss`
        与 `branch_protect` selector metrics
    - `scripts/eval/eval_stft_mask_baseline.py`
      同步补：
      - eval summary / pattern / recipe / ratio bucket
        中的 `branch_protect_guard_sisdr_loss`
  - 1-step smoke：
    - 输出目录：
      - `tmp/smoke_branch_protect_guard_sisdr`
    - eval：
      - `tmp/smoke_branch_protect_guard_sisdr_eval`
    - 已确认：
      - `branch_protect` selector
        train `4 / 7`
        val `1 / 3`
      - 新指标已正常进入
        train / eval summary
  - 当前解释应更新为：
    - 下一条默认已可直接测试：
      - `target_full`-only `base-align`
      - `+`
      - `0004-like branch_protect guard`
    - 当前不再缺“双 protect selector”
      的工程底座
210. 已完成本轮阶段性状态重置；当前正式口径更新为“默认主线冻结、研究分支停扩、下一条方案只保留书面规格”，不再把后续 dual-head 分支误写成即将替换主线的连续版本：
  - 集中日报：
    - `reports/daily/2026-03-20_project_state_reset_after_review.md`
  - 当前正式状态板：
    - 默认主线：
      - `legacy stage2`
      - status: `mainline_keep`
    - 研究基座：
      - `v19`
      - `v32`
      - `proxy_v7`
      - dual-head / branch-local decoder
      - status: `research_base_keep`
    - 当前 `v36+`
      默认解释为：
      - 研究排雷分支
      - 不是主线替换候选序列
    - 当前分支标签：
      - `v57 / v58 = closed_but_evidence_keep`
      - `v54 / v55 / v59 / v60 = closed_failed`
  - 当前正式停止继续扫的内容：
    - `proxy_v7` 微幅 waveform / stft 小变体
    - prefix-freeze 小组合
    - simple adapter 小参数与容量变体
    - dual-head 上已证伪或已进入平台区的 primitive 近邻值：
      - `interference_extra residual_projection_ratio`
      - exact-family `SI-SDR guard`
      - `base-align`
      - `base-delta-interference projection`
    - 回到 `proxy_v6`
    - 旧 absent reconstruction carve-out 族
211. 当前下一条方案只保留为书面规格，不执行训练；若后续重新开启实验，默认候选定义为 `v63 = target_full-only base-align + 0004-like branch_protect guard`：
  - 集中日报：
    - `reports/daily/2026-03-20_project_state_reset_after_review.md`
  - `v63` 书面规格：
    - 保留：
      - `target_full`-only `base-align`
    - 额外补：
      - `0004-like branch_protect guard`
  - 当前建议的第二条 protect selector
    采用：
    - `exact_all - exact_targetfull_all`
  - 本轮已正式物化为：
    - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_nontargetfull_all.txt`
  - 当前已确认的补集 ids：
    - `train_000405`
    - `train_001279`
    - `train_001491`
    - `val_000096`
    - `val_000297`
  - 当前执行约束：
    - 本次不启动新训练
    - 本次不生成新 checkpoint
    - 本次不生成新 compare / gate
  - 单独启动清单：
    - `reports/daily/2026-03-20_v63_written_spec_no_run.md`
212. 已完成 `v63 = dual-head + proxy_v7 reconstruction + target_full-only base-align + branch_protect guard`；结果说明 dual-protect plumbing 是通的，但把第二条 selector 直接定义成 `exact_all - exact_targetfull_all` 是错误建模，它主要选中的不是 `0004-like speech leak`，而是 `absent-like nonfull` 子集：
  - 集中日报：
    - `reports/daily/2026-03-20_v63_dualdecoder_targetfull_basealign_branchprotect_followup.md`
  - `v63` 定义：
    - checkpoint：
      - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v63_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect0002_ft1`
    - protect A：
      - `interference_extra_base_align_weight = 0.02`
      - `focus = exact_targetfull_all`
    - protect B：
      - `branch_protect_guard_sisdr_weight = 0.0002`
      - `focus = exact_nontargetfull_all`
  - selector 命中：
    - `interference_extra`
      - train `4 / 129`
      - val `1 / 37`
    - `branch_protect`
      - train `3 / 129`
      - val `2 / 37`
  - relative to `v19`：
    - default `+0.133461 dB`
    - exact `target_full = -0.145699 dB`
    - near-real speech probe overall `-0.100990 dB`
    - near-real `speech_leak_like (0004) = -0.072646 dB`
    - `guodegang_anchor_120s = -0.311379 dB`
    - `guodegang_absent_480s = -0.114641 dB`
    - `proxy_v7 = +1.460838 dB`
  - relative to `v32` 的 `friend_speech_leak_followup_gate`：
    - `overall_judgement = fail`
    - pass：
      - `default_stage2_delta_floor`
      - `exact_target_full_gain_floor`
    - near-tie：
      - `speech_probe_overall_floor`
    - clear fail：
      - `speech_leak_like_gain_floor`
      - `guodegang_anchor_floor`
      - `guodegang_absent_floor`
  - 额外 metadata 复盘已确认：
    - `exact_nontargetfull`
      这 5 个 ids
      基本全是：
      - `target_clean_speech`
      - `target_absent_head / target_absent_tail`
    - 它不应再被解释成：
      - `0004-like speech leak`
      的保守补集
  - 当前结论：
    - `v63` 不保留
    - `target_full`-only `base-align`
      仍成立
    - 但第二条 protect selector
      不能继续用：
      - `exact_all - exact_targetfull_all`
    - 下一步若继续这条线，
      应先重建真正对应
      `speech_leak_like (0004)`
      的 selector / proxy，
      而不是直接起 `v64`
      扫现有 guard weight
213. 接班恢复时，已确认 `v64 / v65` 并不是“未执行的设想”，而是磁盘上已经实际跑完、评估完、但此前没有补日报和主文档的两条 dual-protect follow-up；当前已完成事实回填：
  - 集中恢复日报：
    - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`
  - `v64`：
    - checkpoint：
      - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v64_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_v23minus0002_ft1`
    - 第二 selector：
      - `sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_all.txt`
    - branch_protect 命中偏稀：
      - train `1 / 129`
      - val `0 / 37`
    - relative to `v19`：
      - default `+0.079474 dB`
      - near-real speech probe overall `-0.038093 dB`
      - exact `target_full = -0.212114 dB`
      - near-real `speech_leak_like (0004) = -0.055069 dB`
      - `guodegang_anchor_120s = +0.048336 dB`
      - `guodegang_absent_480s = +0.019495 dB`
    - relative to `v32` 的 `friend_speech_leak_followup_gate`：
      - `overall_judgement = near_tie`
      - 唯一未过规则：
        - `speech_leak_like_gain_floor`
    - 当前定位：
      - `closed_but_evidence_keep`
      - 说明直接面向 `exact minus target_full` 的 selector
        比 `exact_nontargetfull`
        更接近真实 `0004-like`
        症状，
        但当前命中太稀，
        还不足以形成 keep 候选
  - `v65`：
    - checkpoint：
      - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v65_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_v23minus_union0002_ft1`
    - train / val manifest：
      - `data/synthetic/train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
      - `data/synthetic/val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
    - branch_protect 命中已补足到：
      - train `7 / 135`
      - val `2 / 39`
    - relative to `v19`：
      - default `+0.106078 dB`
      - near-real speech probe overall `-0.070686 dB`
      - exact `target_full = +0.031807 dB`
      - near-real `speech_leak_like (0004) = -0.067371 dB`
      - `guodegang_anchor_120s = -0.147071 dB`
      - `guodegang_absent_480s = -0.057623 dB`
    - relative to `v32` 的 `friend_speech_leak_followup_gate`：
      - `overall_judgement = fail`
      - near-tie：
        - `speech_leak_like_gain_floor`
      - clear fail：
        - `guodegang_anchor_floor`
        - `guodegang_absent_floor`
    - 当前定位：
      - `closed_failed`
      - 说明把 `v23minus` rows
        真正并入 manifest 后，
        仍然没有把 `0004-like`
        拉到正向，
        反而会重新打坏
        `guodegang` guardrail
  - 当前更新后的结论：
    - `v64` 可保留为“selector 语义更对、但命中太稀”的证据轮次
    - `v65` 证明“单纯把这批 rows union 进训练集”不是 keep 方向
    - 若后续继续 dual-protect，
      默认前置动作改为：
      - 先正式重建真正对应
        `speech_leak_like (0004)`
        的 selector / proxy
      - 不直接重跑 `v64`
      - 不直接放大 `v65`
      - 不继续扫现有
        `branch_protect_guard_sisdr_weight`
214. 已把 `v64 / v65` 这条 `0004-like speech_leak` selector 资产的生成过程正式脚本化，当前后续不再需要手工维护 sample-id 文本与 union manifest：
  - 新增脚本：
    - `scripts/data/build_branch_protect_selector_assets.py`
  - 作用：
    - 从 focused proxy manifest 生成：
      - `*_train.txt`
      - `*_val.txt`
      - `*_all.txt`
        三份 branch-protect selector
    - 可选把筛出的 rows
      union 回指定 base train / val manifest
    - 同时输出 overlap / recipe / temporal pattern 摘要
  - 已用该脚本实际重建并核对：
    - `sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_{train,val,all}.txt`
    - `train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
    - `val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
  - 实际核对结果：
    - `v23minus` 当前稳定为：
      - train `7`
      - val `2`
      - all `9`
    - 被减掉的 `target_full` overlap 恰好是：
      - train `4`
      - val `1`
    - `v65` merged manifest 当前稳定为：
      - train `135`
      - val `39`
  - 当前意义：
    - `v64 / v65` 不再只是“目录里存在的历史产物”
    - 而是已经有正式的可复现资产入口
    - 后续若继续重建真正对应 `speech_leak_like (0004)` 的 selector / proxy，
      应优先复用该脚本，
      改 proxy manifest 语义本身，
      而不是再手工拼 sample-id 文件
215. 已为 `0004-like speech_leak` 正式补出统一 shared-sample 搜索底座，并完成第一轮 common-manifest compare：
  - 新公共搜索 manifest：
    - `data/synthetic/val_manifest_friend_speech_leak_search_v1.jsonl = 50`
  - 过滤条件：
    - `target_clean_speech`
    - `target_full`
    - `target_present_ratio >= 0.95`
    - `overlap >= 0.75`
    - `speech_interference_clean_pool`
  - 这一步不是直接定义：
    - `0004` 真 proxy
  - 而是先保证：
    - 多 checkpoint compare
      来自严格同一批 `sample_id`
  - 已在该公共 manifest 上重跑：
    - `v19 vs v20 / v24 / v25 / v29 / v30 / v32 / v35 / v64 / v65`
  - 相对 `v19` 的平均 SI-SDR delta 当前为：
    - `v35 = +0.246194 dB`
    - `v65 = +0.197365 dB`
    - `v25 = +0.162377 dB`
    - `v24 = +0.073098 dB`
    - `v64 = +0.053230 dB`
    - `v29 = -0.005659 dB`
    - `v32 = -0.083233 dB`
    - `v30 = -0.098669 dB`
    - `v20 = -0.255740 dB`
  - 当前含义：
    - 这 50 条公共 rows
      里确实已经有一批更像
      `speech_leak_like`
      的候选样本
    - 但它们并不自动复现
      near-real `0004`
      的完整旧排序，
      因而不能把这 50 条直接当成
      真 proxy
216. 基于上述公共搜索 manifest，已经找出第一条新的 `speech_leak` candidate family，并正式物化 train / val manifest：
  - strict samplewise order-pass 下，
    `v20 > v35 > v25 > v24`
    没有任何 shared row 通过；
  - 当前能站住的 working order 是：
    - `v35 > v25 > v24`
  - relaxed 搜索 top candidate filters 当前收敛为：
    - `target_clean_speech`
    - `target_full`
    - `target_present_ratio >= 0.95`
    - `overlap >= 0.9`
    - `speech_interference_clean_pool`
    - `interference_gain_db >= -2.9865000247955322`
    - `target_transient_presence_minus_mid_db_mean <= -10.191147327423096`
    - `interference_transient_presence_minus_mid_db_mean <= 4.159853935241699`
  - 已物化：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v1.jsonl = 12`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v1.jsonl = 3`
  - 当前 3 条 val ids 为：
    - `val_000182`
    - `val_000331`
    - `val_000430`
  - 与旧 exact family 的 overlap：
    - train vs `v23 speech_leak exact`：
      - `2`
    - train vs `v30 exact`：
      - `1`
    - val vs `v23 / v30`：
      - `0`
  - 当前应把它解释为：
    - 一组新的 `0004-like speech_leak` candidate family
    - 不是已经确认的真 proxy
  - 下一步若继续搜索，
    默认应在这份 shared search 底座上继续加负约束，
    尤其要避免：
    - `v65` 仍显著占优
    - `v20` 仍明显落后
217. 已继续把负约束正式接入 `speech_leak` 搜索器，并完成第一轮 `v65` guard candidate 物化：
  - `scripts/eval/search_synthetic_proxy_candidates.py`
    新增：
    - `--extra-order-constraint higher>lower`
  - 当前首个 guard 测试为：
    - 主顺序：
      - `v35 > v25 > v24`
    - 额外约束：
      - `v24 > v65`
  - 在 strict samplewise order-pass 模式下，
    top order-pass candidate 数为：
    - `0`
  - 说明当前那 8 条 strict pass rows
    只要再要求
    `v24 > v65`，
    现有候选会全部掉空
  - 在 relaxed 搜索下，
    已找到一条新的 guarded candidate：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v2_guardv65.jsonl = 13`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v2_guardv65.jsonl = 3`
  - 当前 filters 收敛为：
    - `target_clean_speech`
    - `target_full`
    - `target_present_ratio >= 0.95`
    - `overlap >= 0.9`
    - `speech_interference_clean_pool`
    - `target_transient_presence_minus_mid_db_mean <= -10.191147327423096`
    - `interference_transient_presence_minus_mid_db_mean <= 4.159853935241699`
    - `target_interference_logspec_cosine >= 0.611259937286377`
  - 当前 val ids 为：
    - `val_000331`
    - `val_000376`
    - `val_000430`
  - 与 `candidate_v1` 的关系：
    - train overlap：
      - `8`
    - val overlap：
      - `2`
    - `candidate_v1` 独有：
      - `val_000182`
    - `candidate_v2_guardv65` 独有：
      - `val_000376`
  - 当前应把这条 guarded candidate 解释为：
    - 比 `candidate_v1` 更干净
    - 但辨识度也更弱，
      因为它会把多模型差异压到 near-tie
  - 所以下一步默认不是直接拿它开训练，
    而是继续把：
    - “去掉 `v65` 伪阳性”
    - 和
    - “保住 `v20` 不再明显掉队”
    同时写进搜索约束
218. 已继续补 `v20` 回拉约束，并确认当前最可继续细化的 working candidate 是 `candidate_v3_guardv20`：
  - 两条 relaxed 搜索对照后，
    当前应保留的是：
    - `v35 > v25 > v24`
    - 且 `v20 > v24`
  - 不保留的是：
    - `v35 > v20 > v25`
      且 `v20 > v65`
    - 因为它会把 family 推回：
      - 高 gain
      - 高 transient
      方向，
      更像旧 strong-transient 家族
  - 进一步把：
    - `v20 > v24`
    - `v20 > v65`
    一起写入额外约束后，
    strict samplewise order-pass
    仍为：
    - `0`
    但 relaxed top candidate
    与 `v20 > v24` 路线一致
  - 已物化：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v3_guardv20.jsonl = 10`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v3_guardv20.jsonl = 3`
  - 当前 val ids 为：
    - `val_000165`
    - `val_000331`
    - `val_000430`
  - 当前 3 条 rows 上相对 `v19` 的均值为：
    - `v64 = +0.120518 dB`
    - `v35 = +0.106455 dB`
    - `v20 = +0.099642 dB`
    - `v30 = +0.086138 dB`
    - `v32 = +0.082334 dB`
    - `v29 = +0.079002 dB`
    - `v25 = +0.055091 dB`
    - `v65 = +0.050324 dB`
    - `v24 = +0.028833 dB`
  - 与旧 / 新 family 的关系：
    - train vs `v23` overlap：
      - `2`
    - train vs `v30` overlap：
      - `1`
    - val vs `v23` overlap：
      - `1`
      - `val_000165`
    - val vs `v30` overlap：
      - `0`
    - train vs `candidate_v1 / candidate_v2` overlap：
      - 都是 `6`
    - val vs `candidate_v1 / candidate_v2` overlap：
      - 都是 `2`
  - 当前三条 candidate 的优先级应写成：
    - `candidate_v3_guardv20 = current_working_candidate`
    - `candidate_v2_guardv65 = cleaner_but_too_weak`
    - `candidate_v1 = more_discriminative_but_v65_contaminated`
  - 但 `candidate_v3_guardv20`
    仍不能直接升格成训练入口，
    因为 strict samplewise order-pass
    仍然掉空
219. 已把 `candidate_v3_guardv20` 的 selector 资产也正式补齐，后续可直接接 `focus_sample_ids` 或 branch-protect：
  - 已生成：
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_train.txt`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_val.txt`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v3_guardv20_all.txt`
  - 实际规模：
    - train `10`
    - val `3`
    - all `13`
  - 当前含义：
    - 下一步若继续做
      `focus_sample_ids`
      或 branch-protect probe，
      不再需要从 manifest
      手动抽 ids
220. 已补齐 `v66` 相对 `candidate_v3_guardv20` 的 synthetic 方向诊断，当前可以明确区分：
  - 不是
    “训练完全没沿新 `candidate_v3` rows 走”
  - 而是
    “aggregate synthetic 方向已经吃到，
     但 row-level 仍不够硬，
     real `0004` 语义仍未闭环”
  - 本轮新增：
    - `scripts/eval/analyze_proxy_candidate_direction.py`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v3_guardv20_direction_analysis/summary.json`
  - 在 `candidate_v3_guardv20` 的 3 条 val rows 上，
    `v66` 当前 aggregate 排名为：
    - `v66 > v64 > v35 > v20 > v30 > v32 > v29 > v25 > v65 > v24 > v19`
  - 其中相对 `v32`：
    - `+0.051855 dB`
  - 且相对原 search 约束：
    - `v35 > v25 > v24`
    - `v20 > v24`
    - `v20 > v65`
    仍都成立
  - 但 row-level 仍明显不稳：
    - strict samplewise order-pass = `0 / 3`
    - `v66` 在三条 row 上的 rank 分别为：
      - `7 / 10 / 1`
    - 说明当前 gain 主要集中在：
      - `val_000430`
  - 因而当前更合理的结论应写成：
    - `candidate_v3_guardv20`
      已能把训练 aggregate 方向拉向想要的一侧
    - 但还不够说明
      real `speech_leak_like (0004)`
      已被正确代理
221. 已继续沿 `v64>v66` 方向细化 `0004-like speech_leak` 搜索，并确认新的更优 working candidate 是 `candidate_v4_guardv66_by_v64`：
  - 先补跑了三组 follow-up 搜索：
    - 保留原约束并新增：
      - `v64 > v66`
    - 放掉：
      - `v25 > v24`
    - 放掉：
      - `v20 > v65`
  - 结果区分很明确：
    - 若放掉
      `v25 > v24`，
      top family 会退回：
      - 高 gain
      - 高 target transient
      的旧 strong-transient 家族
      - 虽然 aggregate 上
        能形成 `v64 > v66`
      - 但 `v65`
        仍然很强，
        语义上不像要找的
        `0004-like` proxy
    - 若保留：
      - `v35 > v25 > v24`
      - `v20 > v24`
      - `v64 > v66`
      仅放掉：
      - `v20 > v65`
      则可得到一条新的 order-pass family
  - 已正式物化：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 33`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 10`
  - selector 资产也已补齐：
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_train.txt`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_val.txt`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64_all.txt`
  - 当前 val `10` 条 rows 的 aggregate 排名为：
    - `v64 > v66 > v65 > v20 > v30 > v32 > v35 > v29 > v25 > v24`
    - 其中：
      - `v64 - v66 = +0.003908 dB`
      - `v66 - v65 = +0.015052 dB`
    - 且保留约束：
      - `v35 > v25 > v24`
      - `v20 > v24`
      都成立
  - 当前 row-level 仍不够硬，
    但已比 `candidate_v3` 更像
    “直接用来区分 `v64 / v66`” 的 proxy：
    - strict samplewise order-pass = `2 / 10`
    - `v20 > v24` samplewise = `4 / 10`
    - `v66` rank mean = `3.7`
  - 与既有 family 的 overlap：
    - train vs `candidate_v3_guardv20`：
      - `4`
    - val vs `candidate_v3_guardv20`：
      - `1`
      - `val_000165`
    - train / val vs `candidate_v1 / candidate_v2`：
      - `0`
    - train vs `v23 speech_leak exact`：
      - `1`
      - `train_001404`
    - val vs `v23 speech_leak exact`：
      - `1`
      - `val_000165`
  - 因而当前更新后的判断应写成：
    - `candidate_v3_guardv20`
      更适合回答：
      - 训练有没有沿旧 working candidate
        把 aggregate 方向推正
    - `candidate_v4_guardv66_by_v64`
      则是当前更适合继续细化的
      下一条 search candidate
      - 但仍不是正式训练入口
222. 已继续验证 `candidate_v4_guardv66_by_v64` 是否还能被更强 aggregate 约束继续收紧，并核对其在当前 active split 里的真实覆盖率：
  - 直接把搜索目标改成：
    - `v64 > v66 > v65`
    - 并保留：
      - `v35 > v25`
      - `v25 > v24`
      - `v20 > v24`
    后，
    top order-pass family
    仍然完全回到
    `candidate_v4_guardv66_by_v64`
    这同一批 rows
  - strict samplewise 版本下，
    top order-pass candidate 仍是：
    - `0`
  - 当前结论因此应写成：
    - `candidate_v4`
      已经是这组
      aggregate 约束下的固定点
    - 当前缺的仍是
      row-level hardness，
      不是再补一个
      `candidate_v5`
  - 更关键的是，
    已直接核对它和当前
    `v42 / v66`
    active split 的 overlap：
    - vs `v42` base train：
      - `1 / 33`
    - vs `v42` base val：
      - `0 / 10`
    - vs `v65` union train：
      - `2 / 33`
    - vs `v65` union val：
      - `1 / 10`
  - 这说明：
    - 若未来只换
      `branch_protect_focus_sample_ids`
      而不换 train / val manifest，
      `candidate_v4`
      实际几乎不会被训练命中
  - 因而本轮已直接补齐下一轮可用的 union split：
    - `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 161`
    - `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 47`
  - 当前更新后的默认前置动作应写成：
    - 若下一轮真要验证
      `candidate_v4`
      训练信号，
      默认先换到上述 union manifest，
      而不是只替换 selector
223. 已完成 `v67 = v66 recipe + candidate_v4 union manifest` 训练验证；结果说明 `candidate_v4` 的 coverage 问题已经排除，但当前 objective / proxy 方向仍不对：
  - checkpoint：
    - `baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v67_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_candv4union_0002_ft1`
  - train / val manifest：
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl`
  - `branch_protect` 命中已从 `v66`
    的稀命中变成：
    - train `33 / 161`
    - val `10 / 47`
  - 说明这轮不是：
    - “selector 还没打到真实 rows”
  - relative to `v19`：
    - default：
      - `+0.148614 dB`
    - exact `target_full`：
      - `-0.287388 dB`
    - near-real speech overall：
      - `-0.106822 dB`
    - near-real `speech_leak_like (0004)`：
      - `-0.116563 dB`
    - `guodegang_anchor_120s`：
      - `+0.004550 dB`
    - `guodegang_absent_480s`：
      - `-0.068236 dB`
    - `proxy_v7`：
      - `+0.835037 dB`
  - relative to `v32`
    的 `friend_speech_leak_followup_gate`：
    - `overall_judgement = fail`
    - pass：
      - `default_stage2_delta_floor`
      - `exact_target_full_gain_floor`
      - `guodegang_anchor_floor`
    - near-tie 但仍未过：
      - `speech_probe_overall_floor`
    - clear fail：
      - `speech_leak_like_gain_floor`
      - `guodegang_absent_floor`
  - 同时在
    `candidate_v4_guardv66_by_v64`
    这 `10` 条 val rows 上，
    aggregate 排名已退成：
    - `v64 > v66 > v65 > v67 > baseline > v20 > v30 > v32 > v35 > v29 > v25 > v24`
    - `v64 - v67 = +0.038179 dB`
    - `v65 - v67 = +0.019218 dB`
    - `v67` rank mean = `5.4`
    - `samplewise extra constraint pass = 0 / 10`
  - 这说明当前真正被证伪的是：
    - “只要把 `candidate_v4`
       union 进训练，
       real gate
       就会自然回正”
  - 当前更该怀疑的是：
    - `branch_protect` objective
      语义仍 partial / mismatch
    - 或 `candidate_v4`
      row-level
      仍不够 hard
  - 因而 `v67`
    应记为：
    - `closed_failed`
224. 已对 `candidate_v4_guardv66_by_v64` 做 subgroup 级 row-level 诊断；当前已可明确写成：`candidate_v4` 不是单语义 family，而是混入了一簇会系统性拖坏 `v67` 的高风险子族：
  - 新增脚本：
    - `scripts/eval/analyze_proxy_candidate_subgroups.py`
  - 新增输出：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_guardv66_by_v64_subgroup_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v4_guardv67_by_v64_subgroup_analysis/summary.json`
  - 当前最稳定的危险分界字段为：
    - `target_transient_presence_minus_mid_db_mean`
    - `interference_transient_presence_share_mean`
    - `target_interference_logspec_cosine`
  - 在 `v66`
    relative to `v64`
    的 `candidate_v4`
    这 `10` 条 val rows 上，
    虽然 overall 只剩：
    - `-0.003908 dB`
    但按 subgroup 拆开已明显分叉：
    - low target transient half：
      - `v66 - v64 = -0.015970 dB`
    - higher target transient half：
      - `v66 - v64 = +0.008154 dB`
    - high interference transient share half：
      - `v66 - v64 = +0.002971 dB`
      近 tie，
      但若改按更稳定的
      `target_transient_presence_minus_mid_db_mean`
      切，则负向会继续放大
  - 更关键的是 `v67`
    继续沿同一批 rows
    做 union training 后，
    当前回退主要集中在：
    - high interference transient share half：
      - `v67 - v66 = -0.086806 dB`
      - `v67 - v64 = -0.083835 dB`
      - improved count：
        - `0 / 5`
    - low target transient half：
      - `v67 - v66 = -0.072390 dB`
      - `v67 - v64 = -0.088359 dB`
  - 两条最稳定危险条件的交集当前为：
    - `target_transient_presence_minus_mid_db_mean <= median`
    - `interference_transient_presence_share_mean > median`
    - 对应 `4` 条 rows：
      - `val_000165`
      - `val_000223`
      - `val_000401`
      - `val_000469`
  - 在这 `4` 条上：
    - `v66 - v64 = -0.000723 dB`
      近 tie
    - `v67 - v66 = -0.094110 dB`
    - `v67 - v64 = -0.094832 dB`
  - 当前更新后的默认判断应改为：
    - `candidate_v4`
      现在更像：
      - 一簇可保留的 working rows
      - 加上一簇会把
        `branch_protect`
        objective
        推反的危险子族
    - 下一步若继续，
      默认优先做：
      - `candidate_v4`
        semantic split / hardness 提升
      - 尤其先排查：
        - low target transient
        - high interference transient share
          的 carve-out
      - 而不是直接再补 coverage
        或继续放大当前 guard weight
225. 已继续把 `v67 negative` top family 物化成新的诊断锚点 `candidate_v5_guardv67_negative`；当前它应解释为“稳定满足 `v64 > v66 > v65 > v67` 的收缩 negative family”，而不是 `candidate_v4` 的正式替代品：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v5_guardv67_negative_materialization.md`
  - 新资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 12`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 3`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative_{train,val,all}.txt`
    - `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 141`
    - `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 40`
  - 新 summary：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v5_guardv67_negative_direction_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v5_guardv67_negative_direction_analysis/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v5_guardv67_negative_on_friend_speech_leak_search_v1/materialized_candidate_v5_summary.json`
  - 这条 family 的 val `3` 条 rows 为：
    - `val_000076`
    - `val_000274`
    - `val_000469`
  - aggregate 上已明确形成：
    - `v64 > v35 > v66 > v20 > v29 > v65 > ... > v67`
    - 关键 gap：
      - `v66 - v64 = -0.039333 dB`
      - `v66 - v65 = +0.026017 dB`
      - `v66 - v67 = +0.056485 dB`
  - 更关键的新关系不是：
    - `candidate_v5 = candidate_v4 carve`
    - 或 `candidate_v5 = candidate_v4 pruned`
  - 而是：
    - val overlap with `candidate_v4 carve`：
      - `1 / 3`
      - `val_000469`
    - val overlap with `candidate_v4 pruned`：
      - `2 / 3`
      - `val_000076`
      - `val_000274`
  - 因而当前默认下一步应升级为：
    - 保留 `candidate_v4`
      作为 `v64 / v66`
      分界 working family
    - 新增保留 `candidate_v5_guardv67_negative`
      作为 `v67`
      负向锚点 family
    - 若后续继续，
      默认先做：
      - `candidate_v4`
        与 `candidate_v5`
        的交并分析
      - 尤其检查：
        - `candidate_v4 carve ∩ candidate_v5`
        - `candidate_v4 pruned ∩ candidate_v5`
      - 不直接启动新训练
226. 已继续把 `candidate_v4 / candidate_v5` 的交并关系正式拆到 subset 级；当前应明确写成：`candidate_v5` 在 val 上不是 `candidate_v4` 外部的新 family，而是 `candidate_v4` 的跨分区子集，且这 `3` 条 rows 本身也不是单语义：
  - 新脚本：
    - `scripts/eval/analyze_proxy_family_overlap.py`
  - 新 summary：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v4_v5_overlap_analysis.md`
  - 当前 val 上四类 rows 已可直接固定为：
    - `v4 carve only`：
      - `val_000165`
      - `val_000223`
      - `val_000401`
    - `v4 carve ∩ v5`：
      - `val_000469`
    - `v4 pruned only`：
      - `val_000034`
      - `val_000041`
      - `val_000202`
      - `val_000365`
    - `v4 pruned ∩ v5`：
      - `val_000076`
      - `val_000274`
  - 其中最关键的新事实不是：
    - `candidate_v5`
      只是“横跨两边”
  - 而是：
    - `v4 carve only`
      这 `3` 条
      更像纯
      `v67` negative rows：
      - `v66 - v64 = +0.007515 dB`
      - `v67 - v66 = -0.068223 dB`
    - `v4 carve ∩ v5`
      当前只有
      `val_000469`
      一条，
      但它是最硬的双信号 anchor：
      - `v66 - v64 = -0.025435 dB`
      - `v67 - v66 = -0.171768 dB`
      - `v66 - v65 = +0.313288 dB`
    - `v4 pruned ∩ v5`
      的
      `val_000076 / 000274`
      更像
      `v64 > v66`
      的 boundary-negative tail，
      不是稳定的
      `v67 negative` core：
      - aggregate
        `v66 - v64 = -0.046281 dB`
      - aggregate
        `v67 - v66 = +0.001157 dB`
    - `v4 pruned only`
      这 `4` 条
      当前最像 keep rows：
      - `v66 - v64 = +0.014094 dB`
      - `v67 - v66 = +0.007854 dB`
  - 因而当前默认下一步应进一步收窄为：
    - 继续保留
      `candidate_v4`
      作为大框架；
    - 但若后续继续做 proxy，
      默认优先考虑：
      - `v4 carve only`
        作为更纯的
        `v67` negative rows
      - `val_000469`
        作为单独的
        硬双信号 anchor
      - 不把
        `v4 pruned ∩ v5`
        直接当成
        `v67 negative` 核心
    - 仍不直接启动新训练
227. 已继续把最值得保留的两条 subset family 正式物化成可训练资产；当前默认不再把整包 `candidate_v5` 当下一条入口，而是改为保留一条“纯 `v67 negative` 子族”和一条“硬双信号 anchor”：
  - 新脚本：
    - `scripts/data/build_proxy_manifest_setops.py`
  - 新日报：
    - `reports/daily/2026-03-21_proxy_subfamily_materialization.md`
  - 当前新物化的两条子族为：
    - `v4carve_only_guardv67_negative`
      - train:
        - `data/synthetic/train_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 4`
      - val:
        - `data/synthetic/val_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 3`
      - val rows:
        - `val_000165`
        - `val_000223`
        - `val_000401`
      - union split:
        - train `133`
        - val `40`
      - focused direction:
        - `v66 - v64 = +0.007515 dB`
        - `v67 - v66 = -0.068223 dB`
      - 当前应解释为：
        - 更纯的
          `v67 negative`
          rows
    - `v4carve_v5_dualanchor`
      - train:
        - `data/synthetic/train_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 2`
      - val:
        - `data/synthetic/val_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 1`
      - val row:
        - `val_000469`
      - union split:
        - train `131`
        - val `38`
      - focused direction:
        - `v66 - v64 = -0.025435 dB`
        - `v67 - v66 = -0.171768 dB`
      - 当前应解释为：
        - 最硬的单点双信号 anchor
  - 因而当前默认下一步应继续收窄为：
    - 若仍停在 proxy 侧，
      默认优先围绕：
      - `v4carve_only_guardv67_negative`
      - `v4carve_v5_dualanchor`
      继续解释；
    - 若未来真要开训练，
      默认不再从
      全量 `candidate_v5`
      起步；
    - 本轮仍未启动新训练
228. 已继续沿 `v4carve_only` 和 `dualanchor` 两条线做 family expand 搜索；当前结果应写成：纯 `v67 negative` 这边已出现一条新的 aggregate 更干净的 working family `candidate_v6_v4carve_only_expand`，而 `dualanchor` 这边在 `min-count=3` 下没有新 family，top 结果直接塌回 `candidate_v5`：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v6_pure_negative_expand.md`
  - pure-negative expand 搜索：
    - `reports/eval/synthetic_proxy_search_candidate_v6_v4carve_only_expand_on_friend_speech_leak_search_v1/summary.json`
  - dualanchor expand 搜索：
    - `reports/eval/synthetic_proxy_search_candidate_v6_dualanchor_expand_on_friend_speech_leak_search_v1/summary.json`
  - 当前新物化的 `candidate_v6` 资产为：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 13`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 3`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand_{train,val,all}.txt`
    - `data/synthetic/train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 135`
    - `data/synthetic/val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 38`
  - 这条 family 的 val `3` 条 rows 为：
    - `val_000165`
    - `val_000331`
    - `val_000430`
  - focused direction 已明确形成：
    - `v66 - v64 = +0.013671 dB`
    - `v66 - v65 = +0.083866 dB`
    - `v66 - v67 = +0.038650 dB`
  - 它与旧 `v4carve_only` 不是同一条 family：
    - overlap val：
      - `1 / 3`
      - `val_000165`
    - overlap with dualanchor：
      - `0`
  - 当前更合理的解释应写成：
    - `candidate_v6`
      是新的 pure-negative expand family；
    - `val_000430`
      是其中最强核心；
    - `val_000331`
      是 partial-support row；
    - `val_000165`
      则更像旧 family 留下的 noisy carry-over
  - 另一边更关键的新事实是：
    - `dualanchor`
      在 `min-count=3`
      下没有新解；
    - top family
      仍然精确回到：
      - `val_000076`
      - `val_000274`
      - `val_000469`
      也就是旧
      `candidate_v5`
  - 因而当前默认下一步应继续收窄为：
    - 保留
      `candidate_v6_v4carve_only_expand`
      作为新的 pure-negative working family
    - 保留
      `val_000469`
      作为单独硬 anchor
    - 不继续把
      `dualanchor`
      扩成新的
      `3+ row`
      family
    - 本轮仍不启动新训练
229. 已补上真正的 samplewise 全约束 strict 搜索能力，并确认 `candidate_v6` 不能再被误写成 row-level strict core；当前更准确的状态应固定为“`candidate_v6` 仍是 aggregate pure-negative working family，而 row-level strict-all core 只有 `{val_000239, val_000430}` 两条”：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
  - 工程补强：
    - `scripts/eval/search_synthetic_proxy_candidates.py`
      新增：
      - `--require-samplewise-all-constraints-pass`
      - `num_samplewise_extra_constraint_pass_rows_before_optional_filter`
      - `num_samplewise_all_constraints_pass_rows_before_optional_filter`
    - 作用：
      - 不再只检查
        `ordered_aliases`
      - 而是可直接要求
        每条样本同时满足
        主顺序与全部
        `extra_order_constraints`
  - 回跑口径：
    - 主顺序：
      - `v66 > v64`
    - 额外约束：
      - `v66 > v65`
      - `v66 > v67`
      - `v64 > v67`
      - `v20 > v24`
    - 输出：
      - `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min3_on_friend_speech_leak_search_v1/summary.json`
      - `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min2_on_friend_speech_leak_search_v1/summary.json`
  - 关键结果：
    - samplewise 全约束过关的 shared rows
      只有：
      - `val_000239`
      - `val_000430`
    - `min-count = 3`
      直接掉空，
      说明当前不存在
      `3+ row`
      的 strict-all clean family
    - `min-count = 2`
      的 top strict-all family
      固定为：
      - `val_000239`
      - `val_000430`
    - aggregate gap：
      - `v66 - v64 = +0.010527 dB`
      - `v66 - v65 = +0.256205 dB`
      - `v66 - v67 = +0.110576 dB`
      - `v64 - v67 = +0.100049 dB`
      - `v20 - v24 = +0.060376 dB`
  - 与旧 `candidate_v6` 的关系：
    - `candidate_v6`
      val：
      - `val_000165`
      - `val_000331`
      - `val_000430`
    - strict-all core：
      - `val_000239`
      - `val_000430`
    - 因而当前应明确区分：
      - `candidate_v6`
        = aggregate working family
      - `{val_000239, val_000430}`
        = strict-all 诊断核心
    - `val_000430`
      被再次确认是真核心；
      `val_000165 / val_000331`
      被 strict-all 直接筛掉；
      `val_000239`
      则是此前未被 `candidate_v6`
      吸进来的新 strict core row
  - 当前解释应进一步收紧为：
    - `candidate_v6`
      还不能被写成
      row-level clean family；
    - 当前更该保留的三层结构是：
      - `candidate_v6`
        作为 aggregate pure-negative family
      - `{val_000239, val_000430}`
        作为 strict-all core
      - `val_000469`
        作为单独硬 anchor
  - 因而当前默认下一步应更新为：
    - 继续先做 proxy 解释，
      不回到训练；
    - 若要继续收窄，
      默认优先围绕：
      - strict-all core
        `{val_000239, val_000430}`
      - 单点硬 anchor
        `val_000469`
      继续解释；
    - 在出现新的
      `3+ row`
      strict-all family
      之前，
      不启动新训练
230. 已把 `candidate_v7` strict-core 资产与 overlap 关系正式物化，并确认当前不应把 strict core 继续写成 `candidate_v6` 那条 low-transient family 的继续收紧版；当前更合理的结构应改成“行为 core 与 metadata family 分开管理”：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
  - 新资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl = 0`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl = 2`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_{train,val,all}.txt`
    - `tmp/candidate_v7_strictall_core_val_ids.txt`
    - `tmp/candidate_v7_strictall_core_selector_assets_summary.json`
  - 新 overlap summary：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
  - 当前 union `5` 条 rows 已固定为：
    - `candidate_v6 only`
      - `val_000165`
      - `val_000331`
    - `strict_core only`
      - `val_000239`
    - `candidate_v6 ∩ strict_core`
      - `val_000430`
    - `dualanchor only`
      - `val_000469`
  - 当前更关键的新事实是：
    - `val_000430`
      继续是 strict core
      与 aggregate pure-negative
      的公共核心；
    - `val_000239`
      虽然行为上也严格满足：
      - `v66 > v64`
      - `v66 > v65`
      - `v66 > v67`
      - `v20 > v24`
      但它的元数据形态并不落在
      `candidate_v6`
      的 low-transient 模板里：
      - `target_transient_presence_minus_mid_db_mean = +0.631591`
      - `interference_transient_presence_minus_mid_db_mean = +1.396928`
    - 因而当前 strict core
      不是一个已经被单一 metadata family
      解释干净的集合
  - 当前解释应进一步更新为：
    - `candidate_v6`
      继续保留为 aggregate family；
    - `strict_core`
      保留为行为上干净的 row-level core；
    - `dualanchor`
      保留为边界锚点；
    - 这三者当前不能再混写成
      一条连续 family
  - 因而当前默认下一步应继续调整为：
    - 若继续做 proxy 搜索，
      默认优先围绕：
      - strict core
        `{val_000239, val_000430}`
        继续找新的行为同族；
      - `val_000469`
        继续保留为边界 anchor；
    - 不再默认只沿
      `candidate_v6`
      的 low-transient 语义
      去收紧阈值；
    - 在出现新的
      `3+ row`
      strict-all family
      之前，
      不启动新训练
231. 已继续把 strict-core 周围的 near-miss row 正式拆成按失败 guard 分组的两条 frontier，并确认当前默认优先前沿应改成 `guardv65_only`，而不是继续把所有 near-miss 混成一包：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
  - 新脚本：
    - `scripts/eval/analyze_proxy_strict_near_miss.py`
  - 为避免 near-miss 结果里派生特征为空，
    本轮先补了：
    - `data/synthetic/val_manifest_friend_speech_leak_search_v1_with_metrics.jsonl`
  - 新分析输出：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_nearmiss_analysis_with_metrics/summary.json`
  - 当前 shared `50` 条 rows 上，
    strict-all pass
    仍只有：
    - `val_000239`
    - `val_000430`
  - 但 single-fail frontier
    已明确拆成两条：
    - `guardv65_only`
      - `val_000376`
      - `val_000202`
      - aggregate：
        - `v66 - v64 = +0.011899 dB`
      - 唯一失败：
        - `v66 - v65 = -0.079787 dB`
      - 其中
        `val_000376`
        最接近 strict core：
        - `v66 - v65 = -0.004292 dB`
    - `guardv20_only`
      - `val_000223`
      - `val_000316`
      - aggregate：
        - `v66 - v64 = +0.020531 dB`
      - 唯一失败：
        - `v20 - v24 = -0.057057 dB`
  - 本轮已物化两条 single-fail 资产：
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65_{train,val,all}.txt`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20_{train,val,all}.txt`
  - 当前解释应进一步收紧为：
    - strict core
      的 near-miss
      不能再混成一包解释；
    - `guardv65_only`
      更像 strict core
      的直接扩张；
    - `guardv20_only`
      则更像与旧
      `v20`
      legacy guard
      解耦的第二分支；
    - `val_000469`
      继续是边界 anchor，
      不是 single-fail frontier
  - 因而当前默认下一步应更新为：
    - 若继续做 strict-core 扩张，
      默认第一优先围绕：
      - `guardv65_only`
      - 特别是
        `val_000376`
      继续找同向 rows；
    - `guardv20_only`
      继续保留，
      但作为第二优先分支；
    - `val_000469`
      继续单独保留为边界 anchor；
    - 仍不启动新训练
232. 已进一步确认 `guardv65_only` 自身也不是单语义 frontier；放松 `v66 > v65` 后，当前更准确的结构应改成“一个 `4` 条 relaxed shell，加上一条真正稳定的 `{376,430}` bridge pair”，而不是继续把 `{202,376}` 并写成同一条扩张线：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
  - 新搜索输出：
    - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min3_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min2_on_friend_speech_leak_search_v1/summary.json`
  - 当前只要求 samplewise 保住其余四条 guards：
    - `v66 > v64`
    - `v66 > v67`
    - `v64 > v67`
    - `v20 > v24`
    放松：
    - `v66 > v65`
  - 对应当前唯一 relaxed shell：
    - `val_000202`
    - `val_000239`
    - `val_000376`
    - `val_000430`
    - aggregate：
      - `v66 - v64 = +0.011213 dB`
      - `v66 - v65 = +0.088209 dB`
      - `v66 - v67 = +0.071365 dB`
      - `v64 - v67 = +0.060153 dB`
      - `v20 - v24 = +0.120831 dB`
  - 但 `min-count = 3`
    下，
    搜索不会再 carve 出
    更细 metadata family，
    只会反复回到这 `4` 条 shell；
    所以它目前仍只能算：
    - relaxed diagnostic shell
  - 当前第一条真正被 metadata
    稳定挑出来的 bridge pair
    是：
    - `val_000376`
    - `val_000430`
    - 典型 filters：
      - `max_target_transient_presence_minus_mid_db_mean <= -8.670663`
      - `max_interference_transient_presence_minus_mid_db_mean <= 1.206818`
    - aggregate：
      - `v66 - v64 = +0.012678 dB`
      - `v66 - v65 = +0.229887 dB`
      - `v66 - v67 = +0.070054 dB`
      - `v64 - v67 = +0.057376 dB`
      - `v20 - v24 = +0.061743 dB`
  - 反过来：
    - `{val_000202, val_000239}`
      这对 aggregate
      仍是：
      - `v66 - v65 = -0.053469 dB`
    - 所以 `guardv65_only`
      这条线
      不能继续简单写成：
      - `202 / 376`
        两条一起向外扩
  - 本轮已物化两层资产：
    - relaxed shell：
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell.jsonl`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell_{train,val,all}.txt`
    - bridge pair：
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_{train,val,all}.txt`
  - 因而当前默认下一步应继续更新为：
    - 若继续做 strict-core 扩张，
      默认优先围绕：
      - `{val_000376, val_000430}`
      继续找同向 rows；
    - `{val_000202, val_000239, val_000376, val_000430}`
      保留为 relaxed shell，
      但只作为诊断壳层；
    - `val_000202`
      继续保留，
      不再默认和
      `val_000376`
      并写成同一条语义前沿；
    - 仍不启动新训练
233. 已继续围绕 `{val_000376, val_000430}` 做 seed-anchored 扩张诊断，并确认当前最接近的第三条 row 是 `val_000331`；但它只能算 aggregate-only bridge extension，不能当成 row-level clean 第三成员：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
  - 新脚本：
    - `scripts/eval/analyze_proxy_seed_expansion.py`
  - 新诊断输出：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`
  - 用 bridge pair
    `{val_000376, val_000430}`
    做 seed 时，
    当前最近的非 seed row
    是：
    - `val_000331`
    - joint distance：
      - `0.975332`
  - 但 `val_000331`
    row-level 仍 fail：
    - `v66 > v65`
    - `v66 > v67`
    - `v64 > v67`
  - 只是当它与 bridge pair
    并成 `3` 条 aggregate 时，
    会恢复成全约束过关：
    - `{val_000331, val_000376, val_000430}`
    - `v66 - v64 = +0.016071 dB`
    - `v66 - v65 = +0.120962 dB`
    - `v66 - v67 = +0.024827 dB`
    - `v64 - v67 = +0.008756 dB`
    - `v20 - v24 = +0.046605 dB`
  - 反过来，
    `val_000202`
    虽也能形成 seed+1 aggregate pass，
    但它到 bridge center
    的 distance 明显更远：
    - `3.448653`
    所以当前不应再视作
    bridge pair 的第一第三条候选
  - 为验证 generic aggregate search
    会不会自动找回同一条线，
    本轮又补跑了：
    - `reports/eval/synthetic_proxy_search_candidate_v7_bridgepair_aggregate_expand_min3_on_friend_speech_leak_search_v1/summary.json`
    结果 top family
    仍塌回旧：
    - `val_000165`
    - `val_000331`
    - `val_000430`
    说明 bridge 语义
    不能靠 generic aggregate search
    自动保住
  - 本轮已物化 aggregate-only
    bridge trio：
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331_{train,val,all}.txt`
  - 因而当前默认下一步应继续更新为：
    - row-level 扩张
      默认仍围绕：
      - `{val_000376, val_000430}`
    - `{val_000331, val_000376, val_000430}`
      只作为 aggregate-only bridge trio
      单独管理；
    - generic aggregate search
      若再次塌回旧 family，
      默认不覆盖
      bridge-pair 的 seed-anchored 解释；
    - 仍不启动新训练
234. 已进一步把 `bridgepair seed+1` 候选正式拆成按 candidate failed-signature 分组的多条前沿；当前不能再把所有 aggregate-pass 候选看成同一条 bridge 扩张线：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`
  - 工程更新：
    - `scripts/eval/analyze_proxy_seed_expansion.py`
      新增：
      - `top_nearest_aggregate_pass_expansions_by_joint_distance`
      - `aggregate_pass_signature_summaries`
  - 更新后的分析输出：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`
  - 当前 aggregate-pass 候选里已确认至少并存：
    - bridge-like 三失败签名：
      - `v66>v65 | v66>v67 | v64>v67`
      - count `6`
      - nearest：
        - `val_000331`
        - joint distance `0.975332`
      - strongest aggregate：
        - `val_000235`
        - joint distance `6.092051`
    - `guardv20_only`：
      - `val_000223`
      - `val_000316`
    - `guardv65_only` 另一支：
      - `val_000202`
    - strict-core 自身：
      - `val_000239`
  - 当前更关键的新事实是：
    - `seed+1`
      aggregate 排名最高的
      `val_000223`
      实际属于：
      - `guardv20_only`
      并不是 bridge 第三条；
    - 在 bridge-like
      同签名内部，
      `aggregate 更强`
      也不等于
      `bridge 更近`：
      - `val_000331`
        是最近第三条
      - `val_000235`
        虽 aggregate 更强，
        但明显是远距离 washout row
  - 因而当前默认下一步应继续收紧为：
    - 若继续围绕 bridge pair
      找第三条，
      默认先在：
      - `v66>v65 | v66>v67 | v64>v67`
      这条 same-signature 里，
      按 distance 排，
      当前仍以：
      - `val_000331`
      为第一候选；
    - `val_000235`
      及其它远距离但 aggregate 强的 row，
      只保留为 washout 诊断样本；
    - `val_000223 / val_000316 / val_000202 / val_000239`
      继续留在各自前沿，
      不并入 bridge 第三条序列；
    - 仍不启动新训练
235. 已继续验证 `{val_000331, val_000376, val_000430}` 能否作为 soft seed 往外长出第四条；结果是否定的，当前这条 trio 仍只能算 aggregate-only bridge trio，而不是正在成形的新 family：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`
  - 新分析输出：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_trio_seed_expansion_analysis/summary.json`
  - seed 改为：
    - `val_000331`
    - `val_000376`
    - `val_000430`
  - 当前更关键的新事实是：
    - 一旦把 `331`
      升成 soft seed，
      最近的 non-seed rows
      已经变成：
      - `val_000075`
      - `val_000305`
      - `val_000269`
      它们都不再落在原 bridge-like
      三失败签名里；
    - 最近的 aggregate-pass rows
      也会优先塌到别的前沿：
      - `val_000076`
      - `val_000316`
      - `val_000401`
      - `val_000223`
    - 真正仍属于 bridge-like
      三失败签名的下一条 row
      已经变成：
      - `val_000022`
      - distance `2.854296`
      - aggregate min gap `+0.000087 dB`
      几乎贴着 `0 dB`
      过线
  - 当前结论应进一步更新为：
    - `{331,376,430}`
      不能再解释成：
      - 正在长成 quartet 的 soft-seed family
    - 它更准确的定位仍是：
      - aggregate-only bridge trio
  - 因而当前默认下一步应继续收紧为：
    - row-level 扩张
      仍只围绕：
      - `{val_000376, val_000430}`
    - `val_000331`
      继续保留为唯一站得住的
      aggregate-only 第三条，
      但不升级成新的 seed 中心；
    - 默认不再从 trio soft-seed
      往外推第四条；
    - 仍不启动新训练
236. 已把 `{val_000376, val_000430}` 的 metadata 邻域正式投影到当前 active split，并补出行为 compare；结果说明 active split 里不是没有 bridge coverage，而是这簇近邻会行为上裂成 `v66top / v67top_v66near / v65top_tail` 三层混合区，不能整包当 bridge family：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_neighbor_behavior_probe.md`
  - 新脚本：
    - `scripts/eval/analyze_manifest_seed_neighbors.py`
  - 新输出：
    - `reports/eval/active_split_bridgepair_neighbor_analysis/summary.json`
    - `reports/eval/bridgepair_active_metadata_neighbor_top10_direction_analysis/summary.json`
  - 本轮新物化资产：
    - active-neighbor top10：
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10_{train,val,all}.txt`
      - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10.jsonl`
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10.jsonl`
      - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_metadata_neighbor_top10_all.jsonl`
    - 行为分层子集：
      - `..._v66top_*`
      - `..._v67top_v66near_*`
      - `..._v65top_tail_*`
  - 当前 active-neighbor top10
    最近邻为：
    - `train_000597`
    - `train_001978`
    - `train_001279`
    - `train_001599`
    - `train_001219`
    - `train_001991`
    - `train_000737`
    - `train_000432`
    - `train_001079`
    - `val_000331`
  - 当前更关键的新事实是：
    - top10 里有：
      - `9` 条 train
      - `1` 条 val
      - 全部是 `target_clean_speech`
      - temporal pattern 为：
        - `target_full = 6`
        - `target_absent_head = 3`
        - `target_absent_tail = 1`
    - 其中：
      - `train_001279`
      命中此前已知的
      `exact_nontargetfull`
      absent-like 旧资产；
      说明 metadata-near
      不能直接当成语义对题
    - 在 top10 上实际 compare 后，
      aggregate 排序塌成：
      - `v67 > v65 > v66 > v64 > v20 > v24`
      - `v66 > v64 = +0.010333 dB`
      - `v66 > v65 = -0.033064 dB`
      - `samplewise_extra_constraint_pass = 0 / 10`
    - 行为分层当前稳定拆成：
      - `v66top`：
        - `train_000597`
        - `train_001599`
      - `v67top_v66near`：
        - `train_001978`
        - `train_001991`
        - `train_000737`
        - `train_001079`
      - `v65top_tail`：
        - `train_001279`
        - `train_001219`
        - `train_000432`
        - `val_000331`
  - 当前解释应进一步更新为：
    - active split 对 bridge pair
      不是没有 coverage，
      而是：
      - 有 metadata coverage
      - 但行为上是混合区
    - `val_000331`
      虽仍可保留为 shared-val 上的
      aggregate-only 第三条，
      但在 active split 投影里
      已明确落到：
      - `v65top_tail`
      不再属于：
      - `v66` 领先带
  - 因而当前默认下一步应继续收紧为：
    - 若继续做 bridge 方向扩张，
      默认只保留：
      - `{val_000376, val_000430}`
      为 row-level bridge
    - active-neighbor top10
      默认改记为：
      - behavior-mixed diagnostic buffer
      不作为新 proxy / 新训练入口
    - 若还要在 active split
      继续追这条线，
      默认优先看：
      - `v66top`
      这 `2` 条
      是否能和 row-level bridge
      建立更直接联系；
      不继续沿：
      - `val_000331`
      或整包 top10
      往外推
    - 仍不启动新训练
237. 已继续把 active split 里 `v66top` 两条向外拉成一个更宽的 active microbuffer，并确认这条线只有在先剥掉 nonfull / absent 污染后，才会恢复成 aggregate-pass 的 `v66` 小缓冲：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_targetfull_split.md`
  - 本轮新增宽版资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1.jsonl = 7`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1.jsonl = 2`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_all.jsonl = 9`
  - 宽版过滤条件：
    - `recipe = target_clean_speech`
    - `target_transient_presence_share_mean <= 0.008`
    - `interference_transient_presence_minus_mid_db_mean <= -1.0`
  - 当前更关键的新事实是：
    - 宽版 `v66top_v1`
      一混入：
      - `target_absent_head`
      - `target_absent_tail`
      - `target_intermittent`
      就会整体塌成：
      - `v65 > v64 > v66`
      - `v66 > v64 = -0.049224 dB`
      - `v66 > v65 = -0.055437 dB`
    - 宽版里已直接混入：
      - `train_000405`
      - `train_001491`
      这类 absent-like
      `exact_nontargetfull`
      旧资产
  - 当前 target_full-only
    收窄版资产为：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull.jsonl = 3`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull.jsonl = 1`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_{train,val,all}.txt`
  - target_full-only
    当前固定为：
    - `train_000597`
    - `train_001599`
    - `train_001843`
    - `val_000430`
  - 当前 target_full-only
    aggregate 排序恢复成：
    - `v66 > v64 > v67 > v20 > v65`
    - 并且 full extra constraints
      全部 aggregate pass：
      - `v66 > v65 = +0.114106 dB`
      - `v66 > v67 = +0.062182 dB`
      - `v64 > v67 = +0.047513 dB`
      - `v20 > v24 = +0.036113 dB`
  - 但当前仍不能把它误写成 row-level clean family，
    因为：
    - `samplewise extra pass = 1 / 4`
    - `train_001843`
      当前仍是 noisy carry-over
  - 因而当前解释应继续收紧为：
    - 宽版 `v66top_v1`
      = contaminated active microbuffer
    - `target_full` 版
      = aggregate-pass `v66` microbuffer
      with noisy carry-over
  - 当前默认下一步应继续更新为：
    - 若继续在 active split
      追 bridge 方向，
      默认只保留：
      - `target_full` 版 `v66` microbuffer
      作为可讨论的小缓冲；
    - 宽版 `v66top_v1`
      只保留为：
      - nonfull / absent 污染会把 aggregate
        拉回 `v65`
        的反例资产；
    - `train_001843`
      继续保留为 noisy carry-over，
      不和：
      - `train_000597`
      - `train_001599`
      - `val_000430`
      写成同纯度成员；
    - 仍不启动新训练
238. 已继续把 `target_full` 微缓冲里的 noisy carry-over 拆掉；当前 active split 上最小可保留的 bridge-like core 已进一步收窄为 `{train_000597, train_001599, val_000430}`：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_core_trio.md`
  - 新 core 资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core.jsonl = 2`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core.jsonl = 1`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core_all.jsonl = 3`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_active_microbuffer_v66top_v1_targetfull_core_{train,val,all}.txt`
  - 新方向汇总：
    - `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`
  - 当前更关键的新事实是：
    - 去掉 `train_001843`
      之后，
      core trio aggregate
      继续保持：
      - `v66 > v64 > v67 > v20 > v24 > baseline > v65`
      且 full extra constraints
      全部 aggregate pass：
      - `v66 > v64 = +0.030334 dB`
      - `v66 > v65 = +0.181224 dB`
      - `v66 > v67 = +0.052351 dB`
      - `v64 > v67 = +0.022017 dB`
      - `v20 > v24 = +0.009617 dB`
    - 相比上一轮 `4` 条 target_full 微缓冲，
      当前：
      - `v66 > v64`
        从 `+0.014670`
        抬到：
        - `+0.030334 dB`
      - `v66 > v65`
        从 `+0.114106`
        抬到：
        - `+0.181224 dB`
      说明：
      - `train_001843`
        的确就是主要 noisy carry-over
  - 当前 samplewise 状态为：
    - `ordered pass = 3 / 3`
    - `extra pass = 1 / 3`
    - train 侧两条：
      - `train_000597`
      - `train_001599`
      当前都只差同一条：
      - `v64 > v67`
  - 当前解释应继续收紧为：
    - core trio
      = aggregate-pass active microbuffer core
      with shared train-side
      `v64 > v67` leak
    - `train_001843`
      = target_full 微缓冲里的
      noisy carry-over
  - 因而当前默认下一步应继续更新为：
    - 若继续在 active split
      保留 bridge 方向资产，
      默认核心改成：
      - `{train_000597, train_001599, val_000430}`
    - `train_001843`
      继续单独保留为 carry-over，
      不再并入 core
    - 后续若还要继续追 train-side 镜像，
      默认优先围绕：
      - 为什么两条 train row
        都只差：
        - `v64 > v67`
      这一条 shared leak
      去看；
    - 仍不启动新训练
239. 已在 `active_targetfull_clean` 这 `88` 条 `target_full clean` workspace 上把 `core trio` 的 shared leak 重新核对到全约束口径；当前必须把 train-side 外壳正式修正为更窄的 dual-leak shell，而不是继续写成单 `v64 > v67` 漏点：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_targetfull_clean_dualleak_shell.md`
  - 本轮脚本修正：
    - `scripts/eval/analyze_proxy_candidate_direction.py`
    - 当前 `order_pass(...)`
      与 `extra_constraints_pass(...)`
      已改为：
      - 先记录全部 constraint gaps
      - 再统一返回 overall pass / fail
    - 已重跑：
      - `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`
    - 当前两条 train rows
      不再被 summary 误写成：
      - 只差 `v64 > v67`
      而是明确同时差：
      - `v64 > v67`
      - `v20 > v24`
  - 当前 `active_targetfull_clean strict-near-miss`
    更关键的新事实是：
    - 当前单-fail rows
      只有：
      - `v66>v65`
        - `3`
      - `v20>v24`
        - `1`
      - `v66>v64`
        - `1`
    - 并不存在
      - 纯 `v64>v67`
        单漏 shell
  - 当前真正包住：
    - `train_000597`
    - `train_001599`
    的最小 train-side 壳层为：
    - `train_000597`
    - `train_001477`
    - `train_001599`
    - `train_000865`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_all.txt`
  - focused direction：
    - `reports/eval/bridgepair_active_targetfull_clean_core_dualleak_shell_direction_analysis/summary.json`
    - aggregate 排序：
      - `v66 > v67 > v24 > v64 > baseline > v65 > v20`
    - 关键 gaps：
      - `v66 > v64 = +0.129529 dB`
      - `v66 > v65 = +0.175244 dB`
      - `v66 > v67 = +0.050005 dB`
      - `v64 > v67 = -0.079525 dB`
      - `v20 > v24 = -0.105507 dB`
    - samplewise：
      - `candidate rank = 1`
        在 `4 / 4`
      - `extra pass = 0 / 4`
  - metadata 邻域复盘：
    - `reports/eval/active_targetfull_clean_core_trio_neighbor_analysis/summary.json`
    - 在相对 `core trio`
      的最近邻排序里：
      - `train_000865`
        rank `8`
      - `train_001477`
        rank `34`
      - `train_001827`
        rank `67`
      - `val_000239`
        rank `69`
      - `train_000588`
        rank `79`
    - 当前解释应更新为：
      - dual-leak shell
        是 behavior 同签名 train shell，
        不是 metadata 紧邻的 mirror 外环
      - 其它 all-pass rows
        属于别的 fully-pass frontier，
        不是 bridge 扩张入口
  - 因而当前默认下一步应继续收紧为：
    - `core trio`
      `{train_000597, train_001599, val_000430}`
      仍是当前最小可保留的
      bridge-like active core
    - `{train_000597, train_001477, train_001599, train_000865}`
      只保留为：
      - train-only dual-leak shell
      不升级成：
      - 新的 active microbuffer
      - 或 train-side mirror core
    - 后续若还继续追 train-side 漏点，
      默认优先围绕：
      - 为什么
        `v64 > v67`
        与
        `v20 > v24`
        会一起漏
      去看；
      不再把问题缩写成：
      - 单 `v64 > v67` leak
    - 仍不启动新训练
240. 已继续验证 dual-leak shell 能否作为新的 train-side seed 往外扩；结果当前应明确判成不能，它不是可扩张 family，而是 `core trio` 外侧一层 train-only diagnostic ring：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_dualleak_shell_neighbor_drift.md`
  - 本轮新增物化资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell.jsonl = 4`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell.jsonl = 0`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_all.jsonl = 4`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_{train,val,all}.txt`
  - dual-leak shell 当前固定为：
    - `train_000597`
    - `train_001477`
    - `train_001599`
    - `train_000865`
  - 邻域分析输出：
    - `reports/eval/active_targetfull_clean_dualleak_shell_neighbor_analysis/summary.json`
  - 当前更关键的新事实是：
    - 以 dual-leak shell 为 seed
      重排 `active_targetfull_clean`
      metadata 邻域后，
      最近邻 top10 立刻变成：
      - `val_000376`
      - `val_000305`
      - `train_001181`
      - `val_000075`
      - `train_001494`
      - `train_001589`
      - `train_001079`
      - `train_000432`
      - `train_001219`
      - `train_001404`
    - 也就是：
      - 最近邻前 `4`
        已有 `3` 条 val
      - 但没有任何一条
        继续停在：
        - `v64>v67 | v20>v24`
        这条同签名上
  - 当前最近邻 failed-signature
    已明确裂成三种更坏方向：
    - bridge / guardv65：
      - `val_000376`
        只 fail：
        - `v66 > v65`
    - `v67` 插队：
      - `train_001494`
      - `train_001079`
      - `train_001589`
      都会额外 fail：
      - `v66 > v67`
    - `v64 / v65` 回顶：
      - `train_001181`
      - `val_000075`
      - `train_000432`
      会直接连：
      - `v66 > v64`
      或：
      - `v66 > v65`
      一起丢掉
  - 当前 metadata / signature
    的更准确解释是：
    - `core trio`
      是最干净的 active core
    - dual-leak shell
      是：
      - `core trio`
        外侧一层
        train-only 中间带
    - 再往外一层，
      就会迅速滑成：
      - bridge / guardv65
      - `v67`
      - `v64 / v65`
      混合前沿
  - 因而当前默认下一步应继续收紧为：
    - `core trio`
      `{train_000597, train_001599, val_000430}`
      仍是唯一可保留的
      bridge-like active core
    - dual-leak shell
      只保留为：
      - train-only diagnostic ring
      不再作为：
      - 新 family seed
      - 新 mirror core
      - 新 active microbuffer
    - 后续若还继续追 train-side 漏点，
      默认只看：
      - 为什么
        `v64 > v67`
        与
        `v20 > v24`
        会在这层 train rows
        一起漏
      不再继续找
      shell 的外层扩张
    - 仍不启动新训练
241. 已把 `active_targetfull_clean` 上的 `v64>v67 / v20>v24` 组合正式切成四个标准桶并补齐 focused direction；结果当前应明确判成：guard-pair bucketization 只是在全量 workspace 上重现了 `core trio / dual-leak shell / mixed frontier` 三层结构，并没有长出新的 bridge family：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_active_guardpair_bucketization.md`
  - 新增脚本：
    - `scripts/eval/analyze_proxy_constraint_pair_buckets.py`
  - 新 summary：
    - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_bucket_analysis/summary.json`
  - 当前两条 guard：
    - A：
      - `v64 > v67`
    - B：
      - `v20 > v24`
  - 当前四桶数量为：
    - `pass_both = 18`
    - `fail_a_only = 20`
    - `fail_b_only = 7`
    - `fail_both = 43`
  - 当前 focused direction：
    - `pass_both`：
      - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_pass_both_direction_analysis/summary.json`
      - aggregate：
        - `v65 > v64 > v20 > v66`
      - `v66 > v64 = -0.037591 dB`
      - `v66 > v65 = -0.059018 dB`
    - `fail_a_only`：
      - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_a_only_direction_analysis/summary.json`
      - aggregate：
        - `v67 > v65 > v66 > v64`
      - `v66 > v67 = -0.169243 dB`
    - `fail_b_only`：
      - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_b_only_direction_analysis/summary.json`
      - aggregate：
        - `v64 > v66 > v67`
      - `v66 > v64 = -0.066802 dB`
    - `fail_both`：
      - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_direction_analysis/summary.json`
      - aggregate：
        - `v67 > v65 > v66 > v24 > baseline > v64 > v20`
      - `v66 > v64 = +0.162575 dB`
      - `v66 > v67 = -0.233290 dB`
      - `v64 > v67 = -0.395865 dB`
      - `v20 > v24 = -0.426840 dB`
  - 当前 overlap 事实：
    - `core trio`
      只有：
      - `val_000430`
      落在：
      - `pass_both`
    - `train_000597`
      与
      `train_001599`
      落在：
      - `fail_both`
    - dual-leak shell
      `4` 条
      也全部落在：
      - `fail_both`
  - 更关键的新事实是：
    - `fail_both`
      这 `43` 条
      再按 top alias
      拆开后：
      - `v67` top：
        - `34`
      - `v65` top：
        - `4`
      - `v66` top：
        - `4`
      - `v24` top：
        - `1`
    - 而唯一这 `4` 条
      `v66-top`
      rows，
      恰好就是：
      - `train_000597`
      - `train_001477`
      - `train_001599`
      - `train_000865`
      即当前 dual-leak shell 本身
    - 对应 summary：
      - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_top_alias_split/summary.json`
  - 当前解释应更新为：
    - `pass_both`
      不能再被误写成
      更干净的 bridge 候选；
      它整体更像：
      - `v65 / v64`
        一侧的别的 fully-pass frontier
    - `fail_a_only`
      更像：
      - `v67` 插队层
    - `fail_b_only`
      更像：
      - legacy `guardv20`
        分支
    - 真正包住 train-side bridge
      诊断层的，
      只有：
      - `fail_both`
      这一大桶；
      但它内部唯一仍然
      `v66-top`
      的，
      还是当前
      dual-leak shell
  - 因而当前默认下一步应继续收紧为：
    - active bridge
      仍只保留：
      - `core trio`
      - dual-leak shell
    - 不再继续从四个 guard-pair buckets
      直接找新 family
    - 若还继续推进，
      默认优先看：
      - 为什么
        `fail_both`
        里只有这 `4` 条
        还能保持 `v66-top`
      - 以及它们和
        那 `34` 条
        `v67-top`
        rows
        的差异
    - 仍不启动新训练
242. 已继续把 `fail_both` 大桶内部真正的 `v66-top` 小核和外层 `v67-top` 大层正式拆开；当前 bridge active 这条线的内外边界已经基本钉死：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_failboth_v66_vs_v67_split.md`
  - 本轮新增资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66.jsonl = 4`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66.jsonl = 0`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66_all.jsonl = 4`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv66_{train,val,all}.txt`
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67.jsonl = 28`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67.jsonl = 6`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67_all.jsonl = 34`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_topv67_{train,val,all}.txt`
  - 当前 `v66-top 4`：
    - `train_000597`
    - `train_000865`
    - `train_001477`
    - `train_001599`
  - focused direction：
    - `reports/eval/active_targetfull_clean_failboth_topv66_direction_analysis/summary.json`
    - aggregate：
      - `v66 > v67 > v24 > v64 > baseline > v65 > v20`
    - `v66 > v64 = +0.129529 dB`
    - `v66 > v67 = +0.050005 dB`
  - 当前 `v67-top 34`
    focused direction：
    - `reports/eval/active_targetfull_clean_failboth_topv67_direction_analysis/summary.json`
    - aggregate：
      - `v67 > v65 > v66 > v24 > baseline > v64 > v20`
    - `v66 > v64 = +0.187917 dB`
    - `v66 > v67 = -0.296784 dB`
  - 当前更关键的新事实是：
    - 两边真正的分界
      不是：
      - `v66` 能不能压住
        `v64`
    - 而是：
      - `v67`
        有没有把
        `v66`
        彻底反超
    - `v67-top 34`
      的
      `v66 > v64`
      反而更强正，
      但排序已经整体切换成：
      - `v67`
        主导
  - 直接均值对照：
    - `reports/eval/active_targetfull_clean_failboth_topv66_vs_topv67_analysis/summary.json`
    - `v66-top 4`
      相对 `v67-top 34`
      当前固定更偏：
      - 更低的
        `target_transient_presence_minus_mid_db_mean`
      - 更低的
        `target_transient_presence_share_mean`
      - 更低的
        `interference_transient_presence_minus_mid_db_mean`
      - 更低的
        `interference_transient_presence_share_mean`
      - 更高的
        `target_interference_logspec_cosine`
    - 当前均值差
      `v66-top - v67-top`
      为：
      - `target_transient_presence_minus_mid_db_mean = -1.626303`
      - `target_transient_presence_share_mean = -0.033455`
      - `interference_transient_presence_minus_mid_db_mean = -4.366413`
      - `interference_transient_presence_share_mean = -0.107130`
      - `target_interference_logspec_cosine = +0.119815`
  - subgroup split：
    - `reports/eval/active_targetfull_clean_failboth_subgroup_analysis/summary.json`
    - 当前进一步说明：
      - 在 `fail_both`
        大桶内部，
        `v66-v67`
        的崩塌不是由单一字段决定，
        而是一组：
        - target transient
        - target share
        - interference transient
        - interference share
        - cosine
        共同把 rows
        推向更外层
        `v67-top`
        frontier
  - 当前解释应进一步更新为：
    - dual-leak shell
      不只是：
      - `train-only diagnostic ring`
    - 还应固定写成：
      - `fail_both`
        大桶里唯一仍是
        `v66-top`
        的 train-only inner core
    - `v67-top 34`
      不是它的外环 family，
      而是：
      - `v67`
        主导的外层 mixed frontier
  - 因而当前默认下一步应继续收紧为：
    - active bridge
      当前只保留：
      - `core trio`
      - dual-leak shell
    - 不再把：
      - `v67-top 34`
      写成：
      - bridge family 外环
    - 若还继续推进，
      默认优先看：
      - dual-leak shell
        和
        `v67-top 34`
        在更细 metadata /
        音频案例上
        是否存在可解释的
        单一触发因子
    - 仍不启动新训练
243. 已继续把 `dual-leak shell` vs `v67-top 34` 做成单字段阈值扫描；当前这条线可以正式定性成多因子共驱动，不存在能一刀切开的单 trigger：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_failboth_single_trigger_scan.md`
  - 新 summary：
    - `reports/eval/active_targetfull_clean_failboth_single_field_trigger_scan/summary.json`
  - 当前扫描字段：
    - `target_transient_presence_minus_mid_db_mean`
    - `target_transient_presence_share_mean`
    - `interference_transient_presence_minus_mid_db_mean`
    - `interference_transient_presence_share_mean`
    - `target_interference_logspec_cosine`
  - 当前更关键的新事实是：
    - 若要求：
      - `4 / 4`
        dual-leak shell
        全部保留
    - 最强单字段
      `interference_transient_presence_minus_mid_db_mean <= 2.428970`
      仍会误收：
      - `7`
        条 `v67-top`
    - 第二强单字段
      `target_interference_logspec_cosine >= 0.671519`
      仍会误收：
      - `8`
        条 `v67-top`
    - 其余字段更差：
      - `interference_transient_presence_share_mean`
        误收 `12`
      - `target_transient_presence_share_mean`
        误收 `20`
      - `target_transient_presence_minus_mid_db_mean`
        误收 `24`
  - 当前解释应正式更新为：
    - dual-leak shell
      之所以还能保持：
      - `v66-top`
    - 不是因为某一个
      单字段阈值成立，
    - 而是因为：
      - 更低的
        target transient / share
      - 更低的
        interference transient / share
      - 更高的
        cosine
      这组条件
      共同把它留在
      train-only inner core
  - 当前 persistent borderline rows
    也已固定出来：
    - `train_001079`
      命中：
      - `5 / 5`
        单字段 full-recall 阈值
    - `train_001494`
      命中：
      - `5 / 5`
    - `train_000697`
      命中：
      - `4 / 5`
    - `train_001589`
      命中：
      - `4 / 5`
    - `val_000182`
      命中：
      - `4 / 5`
    - 当前应把它们记成：
      - 外层近内核边界样本
      不回写成
      dual-leak shell 成员
  - 因而当前默认下一步应继续收紧为：
    - 不再继续找：
      - 单 trigger threshold
    - 若还继续推进，
      默认优先围绕：
      - `train_001079`
      - `train_001494`
      - `train_000697`
      - `train_001589`
      - `val_000182`
      做更细的个例诊断
    - active bridge
      主体解释继续保持：
      - `core trio`
        = 唯一可保留 active core
      - dual-leak shell
        = `fail_both` 大桶里
          唯一仍是 `v66-top`
          的 train-only inner core
      - `v67-top 34`
        = 外层 mixed frontier
    - 仍不启动新训练
244. 已继续把 `5` 条 persistent borderline rows 做成个例拆分；当前应明确判成它们并不是同一种“外层近内核边界带”，而是已经裂成 `4` 条真正贴着 shell 的 train near-shell edge band 和 `1` 条 metadata-only val outlier：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_failboth_borderline_case_split.md`
  - 新 summary：
    - `reports/eval/active_targetfull_clean_failboth_topv67_vs_dualleak_seed_expansion/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_persistent_borderline_case_analysis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_persistent_borderline_nearshell_direction_analysis/summary.json`
  - 新物化资产：
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_persistent_borderline_nearshell_all.txt`
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_persistent_borderline_nearshell.jsonl`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_persistent_borderline_nearshell_all.jsonl`
  - 当前更关键的新事实是：
    - 真正贴着 dual-leak shell 的
      只有：
      - `train_001494`
      - `train_001079`
      - `train_001589`
      - `train_000697`
    - 它们在 dual-leak shell seed 的
      joint-distance 排名里分别是：
      - `#1`
      - `#2`
      - `#3`
      - `#9`
    - 这 `4` 条 aggregate
      已可稳定写成：
      - `v67 > v66 > v64 > v65 > v24 > baseline > v20`
    - 并且仍保住：
      - `v66 > v64 = +0.070637`
      - `v66 > v65 = +0.093171`
    - 但已经稳定输给：
      - `v67`
        即：
        - `v66 > v67 = -0.095303`
    - 所以它们当前最准确的身份应更新为：
      - train-side near-shell edge band
      不是：
      - dual-leak shell 扩张成员
  - `val_000182`
    当前则必须单独处理：
    - 虽然它在单字段 full-recall 阈值里
      仍会被误收：
      - `4 / 5`
    - 但它在 dual-leak shell seed 的
      joint-distance 排名里
      已直接掉到：
      - `#39 / 39`
    - 关键原因不是 metadata 完全脱靶，
      而是：
      - `constraint_distance_z = 14.799924`
        远高于
        metadata distance
    - 当前更准确的身份应写成：
      - metadata-only borderline outlier
      不再和 train near-shell edge band
      混写
  - 因而 active bridge
    这条线当前应进一步收紧为：
    - `core trio`
      = 唯一可保留 active core
    - dual-leak shell
      = train-only inner core
    - near-shell edge band `4`
      = 最靠近 shell 的外层 train 边界带
    - `val_000182`
      = metadata-only false shell
    - remaining `v67-top`
      = 更外层 mixed frontier
  - 当前默认下一步
    已再次收紧为：
    - 不再把 `5` 条 persistent borderline rows
      当成一个整体追
    - 若还继续推进，
      默认只围绕：
      - `train_001079`
      - `train_001494`
      - `train_000697`
      - `train_001589`
      做更细个例诊断
    - `val_000182`
      只保留为 metadata-only outlier
    - 仍不启动新训练
245. 已继续把 near-shell edge band `4` 深拆到 pure `v67` takeover 个例层；当前应明确判成真正代表第一层 takeover 的其实只有 `3` 条 pure `v67` edge，而 `train_001589` 必须单独降格成 `v67 + v65` drift singleton：
  - 新日报：
    - `reports/daily/2026-03-21_candidate_v7_failboth_nearshell_case_diagnosis.md`
    - `reports/daily/2026-03-21_candidate_v7_failboth_pure_v67_takeover_case_diagnosis.md`
  - 新 summary：
    - `reports/eval/active_targetfull_clean_failboth_nearshell_case_diagnosis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_pure_v67_takeover_case_diagnosis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_edgeband_pure_v67_takeover_direction_analysis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_edgeband_v67_plus_v65_takeover_singleton_direction_analysis/summary.json`
  - 当前更关键的新事实是：
    - pure `v67` takeover edge `3`
      为：
      - `train_001079`
      - `train_001494`
      - `train_000697`
    - 它们共同保住：
      - `v66 > v64`
      - `v66 > v65`
    - 但共同失败：
      - `v66 > v67`
      - `v64 > v67`
      - `v20 > v24`
    - aggregate 已固定为：
      - `v67 > v66 > v64 > v24 > v65 > baseline > v20`
    - 相对 dual-leak shell `4`，
      pure `3`
      当前更偏：
      - 更长一点的 target
      - 更弱的 interference gain
      - 更早的 interference start
      - 更低的 `target_interference_logspec_cosine`
    - 但并不是：
      - 更高 interference transient
      的 takeover
    - `train_001589`
      则必须单列：
      - 它额外失败：
        - `v66 > v65`
      - 并且相对 pure `3`
        出现明显更高的
        `interference_transient_presence_minus_mid_db_mean`
      - 当前更准确的身份应写成：
        - `v67 + v65`
          takeover singleton
  - 当前解释应进一步更新为：
    - shell 外第一层真正稳定发生的
      是：
      - pure `v67` takeover
    - 不是：
      - `v67 / v65`
        同时进场
    - 因而 `edge 4`
      的混合均值
      不能再直接拿来解释
      pure takeover 的首发机制
  - 当前默认下一步
    已继续收紧为：
    - 若还继续推进，
      默认只围绕：
      - `train_001079`
      - `train_001494`
      - `train_000697`
      做更细 case diagnosis
    - `train_001589`
      只保留为：
      - edge-to-outer drift singleton
    - `val_000182`
      继续只保留为：
      - metadata-only outlier
    - 仍不启动新训练

## 9. 文档入口

- 规范入口：`docs/00_context_bootstrap.md`
- 当前总览：`docs/01_project_overview_and_plan.md`
- 踩坑记录：`docs/02_pitfalls_log.md`
- 结构说明：`docs/03_project_structure.md`
- 人耳复核指南：`docs/04_human_listening_review_guide.md`
- 任务分支图：`docs/05_task_branch_map.md`
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
- 本轮 `v39` absent-recon-wave / `v5 cleancarve` metadata carve-out follow-up：`reports/daily/2026-03-19_v39_absent_recon_cleancarve_followup.md`
- 本轮 `v40` absent cleancarve no-exact-overlap 预备：`reports/daily/2026-03-19_v40_absent_cleancarve_noexactoverlap_prep.md`
- 本轮 `v40 / v41` absent-side follow-up 结果：`reports/daily/2026-03-19_v40_v41_absent_followup_results.md`
- 本轮 `v49 / v50` adapter residual output follow-up：`reports/daily/2026-03-20_v49_v50_adaptermask_followup.md`
- 本轮 `v51 / v52` adapter conditioning and temporal follow-up：`reports/daily/2026-03-20_v51_v52_adapter_conditioning_and_temporal_followup.md`
- 本轮 `v53` dual-head / branch-local decoder plumbing：`reports/daily/2026-03-20_v53_dual_head_branch_decoder_plumbing.md`
- 本轮 `v53 / v54` dual-head follow-up：`reports/daily/2026-03-20_v53_v54_dualdecoder_followup.md`
- 本轮 `v55 - v58` dual-head protect-objective follow-up：`reports/daily/2026-03-20_v55_v58_dualdecoder_protect_objective_followup.md`
- 本轮 dual-head `base-delta-interference projection` smoke：`reports/daily/2026-03-20_dualdecoder_base_delta_projection_smoke.md`
- 本轮 `v59 / v60` dual-head `base-delta-interference projection` follow-up：`reports/daily/2026-03-20_v59_v60_dualdecoder_basedeltaproj_followup.md`
- 本轮 `v61 / v62` dual-head `target_full`-only `base-align` follow-up：`reports/daily/2026-03-20_v61_v62_dualdecoder_targetfull_basealign_followup.md`
- 本轮 `branch_protect` guard selector plumbing：`reports/daily/2026-03-20_branch_protect_guard_plumbing.md`
- 本轮项目状态重置与方案修正：`reports/daily/2026-03-20_project_state_reset_after_review.md`
- 本轮 `v63` dual-protect follow-up：`reports/daily/2026-03-20_v63_dualdecoder_targetfull_basealign_branchprotect_followup.md`
- 本轮 `v64 / v65` dual-protect 恢复补记：`reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`
- 本轮 `branch_protect` selector 资产脚本化：`reports/daily/2026-03-20_branch_protect_selector_asset_builder.md`
- 本轮 friend speech-leak 公共搜索 manifest v1：`reports/daily/2026-03-20_friend_speech_leak_search_manifest_v1.md`
- 本轮 `v66` candidate_v3 synthetic 方向诊断：`reports/daily/2026-03-20_v66_candidate_v3_direction_diagnosis.md`
- 本轮 `candidate_v4` subgroup 行级诊断：`reports/daily/2026-03-21_candidate_v4_subgroup_diagnosis.md`
- 本轮 `candidate_v4 / candidate_v5` 交并诊断：`reports/daily/2026-03-21_candidate_v4_v5_overlap_analysis.md`
- 本轮 proxy subset 物化：`reports/daily/2026-03-21_proxy_subfamily_materialization.md`
- 本轮 `candidate_v6` pure-negative 扩展：`reports/daily/2026-03-21_candidate_v6_pure_negative_expand.md`
- 本轮 `candidate_v7` strict-all core 搜索：`reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
- 本轮 `candidate_v7` strict-core 资产与 overlap：`reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
- 本轮 `candidate_v7` strict-core near-miss frontier：`reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
- 本轮 `candidate_v7` guardv65-relaxed bridge 搜索：`reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
- 本轮 `candidate_v7` bridgepair seed 扩张：`reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
- 本轮 `candidate_v7` bridgepair `seed+1` 签名拆分：`reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`
- 本轮 `candidate_v7` bridgepair trio soft-seed probe：`reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`
- 本轮 `candidate_v7` bridgepair active-neighbor behavior probe：`reports/daily/2026-03-21_candidate_v7_bridgepair_active_neighbor_behavior_probe.md`
- 本轮 `candidate_v7` bridgepair active microbuffer targetfull split：`reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_targetfull_split.md`
- 本轮 `candidate_v7` bridgepair active microbuffer core trio：`reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_core_trio.md`
- 本轮 `candidate_v7` bridgepair active targetfull clean dual-leak shell：`reports/daily/2026-03-21_candidate_v7_bridgepair_active_targetfull_clean_dualleak_shell.md`
- 本轮 `candidate_v7` bridgepair active dual-leak shell neighbor drift：`reports/daily/2026-03-21_candidate_v7_bridgepair_active_dualleak_shell_neighbor_drift.md`
- 本轮 `candidate_v7` active guard-pair bucketization：`reports/daily/2026-03-21_candidate_v7_active_guardpair_bucketization.md`
- 本轮 `candidate_v7` fail-both `v66` vs `v67` split：`reports/daily/2026-03-21_candidate_v7_failboth_v66_vs_v67_split.md`
- 本轮 `candidate_v7` fail-both borderline case split：`reports/daily/2026-03-21_candidate_v7_failboth_borderline_case_split.md`
- 本轮 `candidate_v7` fail-both single-trigger scan：`reports/daily/2026-03-21_candidate_v7_failboth_single_trigger_scan.md`
- 本轮 `candidate_v7` fail-both near-shell case diagnosis：`reports/daily/2026-03-21_candidate_v7_failboth_nearshell_case_diagnosis.md`
- 本轮 `candidate_v7` fail-both pure `v67` takeover case diagnosis：`reports/daily/2026-03-21_candidate_v7_failboth_pure_v67_takeover_case_diagnosis.md`
- 本轮仓库与 `.gitignore` 审计：`reports/daily/2026-03-18_repo_gitignore_audit.md`
- 本轮全仓库评估总结：`reports/daily/2026-03-17_repo_evaluation_summary.md`
