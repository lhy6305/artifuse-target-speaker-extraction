# 任务分支图

## 1. 文档目的

这份文档专门用来管理当前阶段的任务分支，防止出现下面几种常见失忆：

- 忘记当前真正的基座 checkpoint 是哪个；
- 忘记某条分支为什么被判死；
- 忘记某条 follow-up 到底是“新 coverage”还是“旧样本重路由”；
- 忘记下一条准备推进的候选分支具体入口文件在哪里。

大白话讲，这就是“当前这堆分支到底谁还活着、谁已经死了、下一步该接哪条”的总地图。

## 2. 当前裁决口径

### 参考基座

- 长期参考基线：
  - `v19`
  - checkpoint:
    - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v19_v12_absent_proxy_v3_reverse_guardrail_v1_int_up_ft1`

### 当前 friend-side 工作基座

- 当前 absent / friend-side follow-up 的直接比较基座：
  - `v32`
  - checkpoint:
    - `experiments/checkpoints/baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v32_v19_friend_reverse_guardrail_proxy_v8_basepred_extraresidual_ft1`

### 默认 keep / drop gate

- friend-side 主 gate：
  - `scripts/eval/gate_friend_speech_leak_followup.py`
- 当前最关键的 stop condition：
  - `exact_target_full_gain_floor`
  - `speech_leak_like_gain_floor`
  - `guodegang_anchor_floor`
  - `guodegang_absent_floor`
- 当前裁决解释采用三档：
  - `pass`
  - `near_tie`
    - 默认指低于 floor 不超过 `0.03 dB`
    - 只改变解释，不改变 `overall_pass`
  - `clear_fail`
- 因而：
  - `overall_pass`
    仍保持严格；
  - 但文档表述不再把所有 failed rule
    都混写成同一级别失败

## 3. 历史分支归档

- 原 `## 3. 已判死分支` 已迁移到：
  - `docs/archive/task_branch_map/sections_03_dead_branches.md`
- 原 `## 4. 当前分支状态` 已迁移到：
  - `docs/archive/task_branch_map/sections_04_branch_state_history.md`
- 主文档当前只保留：
  - 当前裁决口径
  - 下一条默认执行分支
  - 当前活跃记录
  - 忘线检查表
- 需要回溯某条旧分支的失败原因或阶段状态时，先看上面两份归档。

## 4. 当前维护口径

- `docs/05_task_branch_map.md` 用于记录当前仍可能影响下一步决策的活跃事实。
- 已终止或只具备历史参考价值的长记录，不再继续堆叠回主文档。
- 条目级历史分卷见 `docs/archive/task_branch_map/README.md`。

## 5. 下一条默认执行分支

如果下一轮没有新用户决策，默认暂停，不启动新实验。

即：

## 归档说明

- 本文档当前只保留 `31` 及之后的活跃记录，便于接班和日常维护。
- 更早的历史记录已拆分归档到 `docs/archive/task_branch_map/`。
- 归档总索引见 `docs/archive/task_branch_map/README.md`。

## 当前活跃记录

31. 当前更关键的新事实是：
    - `candidate_v4_guardv66_by_v64`
      与当前 `v42 / v66`
      active split
      几乎不重叠：
      - vs `v42` base train：
        - `1 / 33`
      - vs `v42` base val：
        - `0 / 10`
    - 因而若后续继续训练，
      默认不能只换 selector
32. 本轮已为后续训练准备好 union split：
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 161`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v4_guardv66_by_v64.jsonl = 47`
    - 这对 manifest
      才是后续若继续验证
      `candidate_v4`
      训练信号时的默认入口
33. 已继续把
    `candidate_v4_guardv66_by_v64`
    真正 union
    进 active split，
    并按 `v66`
    原 recipe
    启动：
    - `v67 = baseline_stft_mask_stage2_legacy_transient_leakguard_probe_v67_v32_absent_dualdecoder_v7_wave_targetfullbasealign_branchprotect_candv4union_0002_ft1`
34. `v67`
    已把 coverage 问题排除：
    - `branch_protect`
      命中变成：
      - train `33 / 161`
      - val `10 / 47`
    - 说明这轮不是
      selector 没命中
35. 但 `v67`
    结果明确失败：
    - relative to `v32`
      的 `friend_speech_leak_followup_gate`：
      - `overall_judgement = fail`
      - clear fail：
        - `speech_leak_like_gain_floor`
        - `guodegang_absent_floor`
      - near-tie 但未过：
        - `speech_probe_overall_floor`
    - 且在
      `candidate_v4`
      那 `10` 条 val rows 上，
      aggregate 变成：
      - `v64 > v66 > v65 > v67`
    - 说明当前更该怀疑的是：
      - objective / proxy
        语义仍错，
      - 而不是 manifest coverage
36. `v67`
    之后已补 subgroup 级诊断，
    当前对 `candidate_v4_guardv66_by_v64`
    的正确解释应升级为：
    - 不是单语义 family
    - 而是混入了一簇
      低 target transient /
      高 interference transient share
      的危险子族
    - 新入口：
      - `scripts/eval/analyze_proxy_candidate_subgroups.py`
      - `reports/daily/2026-03-21_candidate_v4_subgroup_diagnosis.md`
    - 核心事实：
      - 对 `v66`
        而言，
        `candidate_v4`
        在：
        - higher-target-transient half
          上相对 `v64`
          仍是小正向
        - low-target-transient half
          上则已转负
      - 对 `v67`
        而言，
        当前最明显的系统性回退落在：
        - high interference transient share half
          relative to `v66`：
          - `-0.086806 dB`
          - improved count `0 / 5`
        - low target transient half
          relative to `v66`：
          - `-0.072390 dB`
      - 两条危险条件交集
        当前为 `4` 条 rows：
        - `val_000165`
        - `val_000223`
        - `val_000401`
        - `val_000469`
        - 在这 `4` 条上：
          - `v66 - v64 = -0.000723 dB`
          - `v67 - v66 = -0.094110 dB`
    - 当前默认下一步因此改为：
      - 先做
        `candidate_v4`
        semantic split / carve-out
      - 不直接继续沿
        现有整包 `candidate_v4`
        再放大 branch_protect
37. 本轮已进一步把
    `v67 negative`
    top family
    物化为：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 12`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 3`
    - `sample_ids_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 141`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v5_guardv67_negative.jsonl = 40`
    - 入口：
      - `reports/daily/2026-03-21_candidate_v5_guardv67_negative_materialization.md`
  - 这条 `candidate_v5_guardv67_negative`
    当前性质应固定为：
    - `v67`
      负向锚点 family
    - 不是
      `candidate_v4`
      的正式替代品
  - val `3` 条 rows 为：
    - `val_000076`
    - `val_000274`
    - `val_000469`
  - aggregate 上明确形成：
    - `v64 > v35 > v66 > v20 > v29 > v65 > ... > v67`
    - `v66 - v64 = -0.039333 dB`
    - `v66 - v65 = +0.026017 dB`
    - `v66 - v67 = +0.056485 dB`
  - 更关键的是：
    - 它并不等于
      `candidate_v4 carve`
      或 `candidate_v4 pruned`
    - 而是横跨了两边：
      - val vs `candidate_v4 carve`：
        - `1 / 3`
        - `val_000469`
      - val vs `candidate_v4 pruned`：
        - `2 / 3`
        - `val_000076`
        - `val_000274`
  - 因而当前默认下一步
    不再只是：
    - `candidate_v4`
      单边 carve-out
  - 而是：
    - 同时保留
      `candidate_v4`
      作为 `v64 / v66`
      分界 working family
    - 保留
      `candidate_v5_guardv67_negative`
      作为 `v67`
      负向锚点 family
    - 若后续继续，
      默认先做：
      - `candidate_v4`
        与 `candidate_v5`
        的交并分析
      - 尤其聚焦：
        - `candidate_v4 carve ∩ candidate_v5`
        - `candidate_v4 pruned ∩ candidate_v5`
      - 不直接启动新训练
38. 已继续把
    `candidate_v4 / candidate_v5`
    交并关系
    拆到 subset 级；
    当前默认解释必须升级为：
    - `candidate_v5`
      在 val 上
      不是独立新族，
      而是
      `candidate_v4`
      的真子集，
      且内部也不是单语义
    - 入口：
      - `scripts/eval/analyze_proxy_family_overlap.py`
      - `reports/daily/2026-03-21_candidate_v4_v5_overlap_analysis.md`
      - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
      - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v4_v5_overlap_analysis/summary.json`
  - 当前 val 上已固定成四类：
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
  - 这四类当前应分别解释为：
    - `v4 carve only`
      = 纯 `v67` negative rows
      - `v66 - v64 = +0.007515 dB`
      - `v67 - v66 = -0.068223 dB`
    - `v4 carve ∩ v5`
      = 硬双信号 anchor
      - 当前只有：
        - `val_000469`
      - `v66 - v64 = -0.025435 dB`
      - `v67 - v66 = -0.171768 dB`
      - `v66 - v65 = +0.313288 dB`
    - `v4 pruned only`
      = 当前最像 keep rows
      - `v66 - v64 = +0.014094 dB`
      - `v67 - v66 = +0.007854 dB`
    - `v4 pruned ∩ v5`
      = `v64 > v66`
        boundary-negative tail，
        不是稳定
        `v67 negative` core
      - `v66 - v64 = -0.046281 dB`
      - `v67 - v66 = +0.001157 dB`
  - 因而当前默认下一步
    已进一步收窄为：
    - 保留
      `candidate_v4`
      大框架
    - 若后续继续做 proxy，
      默认优先考虑：
      - `v4 carve only`
        作为更纯的
        `v67` negative rows
      - `val_000469`
        作为单独的
        硬双信号 anchor
    - 不把整包
        `candidate_v5`
        或
        `v4 pruned ∩ v5`
        直接当成
        新核心 negative family
    - 仍不启动新训练
39. 已继续把
    当前最值得保留的两条 subset family
    物化成标准资产；
    当前默认入口已不再是
    整包 `candidate_v5`
    而是：
    - `v4carve_only_guardv67_negative`
    - `v4carve_v5_dualanchor`
  - 入口：
    - `scripts/data/build_proxy_manifest_setops.py`
    - `reports/daily/2026-03-21_proxy_subfamily_materialization.md`
  - 新物化资产：
    - `train_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 4`
    - `val_manifest_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 3`
    - `sample_ids_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 133`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_only_guardv67_negative.jsonl = 40`
    - `train_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 2`
    - `val_manifest_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 1`
    - `sample_ids_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 131`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_subfamily_v4carve_v5_dualanchor.jsonl = 38`
  - focused direction summary：
    - pure negative：
      - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_only_guardv67_negative_direction_analysis/summary.json`
      - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_only_guardv67_negative_direction_analysis/summary.json`
      - 结论：
        - `v66 - v64 = +0.007515 dB`
        - `v67 - v66 = -0.068223 dB`
    - dual anchor：
      - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_v5_dualanchor_direction_analysis/summary.json`
      - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/proxy_subfamily_v4carve_v5_dualanchor_direction_analysis/summary.json`
      - 结论：
        - `v66 - v64 = -0.025435 dB`
        - `v67 - v66 = -0.171768 dB`
  - 因而当前分支图上的默认下一步
    应固定为：
    - 若继续停在 proxy 侧，
      优先围绕：
      - `v4carve_only_guardv67_negative`
      - `v4carve_v5_dualanchor`
      做后续 family 解释
    - 若未来真要开训练，
      默认不从
      全量 `candidate_v5`
      起步
    - 本轮仍不启动新训练
40. 已继续沿
    `v4carve_only`
    与
    `dualanchor`
    两条线做 family expand 搜索；
    当前结果应固定为：
    - pure-negative
      这边已出现一条新的
      working family
      `candidate_v6_v4carve_only_expand`
    - dualanchor
      这边在
      `min-count = 3`
      下没有新 family，
      top 结果直接回到
      `candidate_v5`
  - 入口：
    - `reports/daily/2026-03-21_candidate_v6_pure_negative_expand.md`
    - `reports/eval/synthetic_proxy_search_candidate_v6_v4carve_only_expand_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v6_dualanchor_expand_on_friend_speech_leak_search_v1/summary.json`
  - 新物化资产：
    - `train_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 13`
    - `val_manifest_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 3`
    - `sample_ids_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand_{train,val,all}.txt`
    - `train_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 135`
    - `val_manifest_v42_plus_friend_speech_leak_proxy_search_candidate_v6_v4carve_only_expand.jsonl = 38`
  - 这条 `candidate_v6`
    val rows 为：
    - `val_000165`
    - `val_000331`
    - `val_000430`
  - focused direction：
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v6_v4carve_only_expand_direction_analysis/summary.json`
    - 结论：
      - `v66 - v64 = +0.013671 dB`
      - `v66 - v65 = +0.083866 dB`
      - `v66 - v67 = +0.038650 dB`
  - 与旧 pure-negative 的关系：
    - overlap with
      `v4carve_only_guardv67_negative`
      val：
      - `1 / 3`
      - `val_000165`
    - overlap with
      `v4carve_v5_dualanchor`
      val：
      - `0`
  - 当前应解释为：
    - `candidate_v6`
      是新的 pure-negative expand family；
    - `val_000430`
      是最强核心；
    - `val_000331`
      是 partial-support row；
    - `val_000165`
      是旧 family
      留下的 noisy carry-over
  - 另一边更关键的新事实是：
    - dualanchor expand 搜索
      top family
      仍精确回到：
      - `val_000076`
      - `val_000274`
      - `val_000469`
      即旧
      `candidate_v5`
    - 因而当前不再默认继续追
      `469` 的
      `3+ row`
      扩展 family
  - 当前默认下一步
    已进一步固定为：
    - 保留
      `candidate_v6_v4carve_only_expand`
      作为新的 pure-negative working family
    - 保留
      `val_000469`
      作为单独硬 anchor
    - 不启动新训练
41. 已补上真正的
    samplewise 全约束 strict 搜索能力，
    并确认当前不存在
    `3+ row`
    的 strict-all clean family；
    当前更准确的两层状态应固定为：
    - `candidate_v6`
      = aggregate pure-negative working family
    - `{val_000239, val_000430}`
      = strict-all core
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
    - `scripts/eval/search_synthetic_proxy_candidates.py`
    - `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min3_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_v4carve_only_expand_strictall_min2_on_friend_speech_leak_search_v1/summary.json`
  - 本轮新增工程能力：
    - `--require-samplewise-all-constraints-pass`
    - `num_samplewise_extra_constraint_pass_rows_before_optional_filter`
    - `num_samplewise_all_constraints_pass_rows_before_optional_filter`
  - strict-all 搜索结果：
    - 在
      `v66 > v64`
      且额外满足：
      - `v66 > v65`
      - `v66 > v67`
      - `v64 > v67`
      - `v20 > v24`
      的口径下，
      真正逐条样本都过关的 shared rows
      只有：
      - `val_000239`
      - `val_000430`
    - `min-count = 3`
      直接掉空，
      说明当前没有
      `3+ row`
      strict-all family
  - 与旧 pure-negative 的关系：
    - `candidate_v6`
      val：
      - `val_000165`
      - `val_000331`
      - `val_000430`
    - strict-all core：
      - `val_000239`
      - `val_000430`
    - 因而当前不能再把
      `candidate_v6`
      误写成
      row-level strict core
  - 当前默认下一步
    应进一步收紧为：
    - 保留
      `candidate_v6`
      作为 aggregate working family
    - 保留
      `{val_000239, val_000430}`
      作为 strict-all 诊断核心
    - 继续保留
      `val_000469`
      作为单独硬 anchor
    - 在没有新的
      `3+ row`
      strict-all family
      之前，
      不启动新训练
42. 已把 strict-core 资产与 overlap 关系正式物化；
    当前更准确的三层结构应固定为：
    - `candidate_v6`
      = aggregate pure-negative working family
    - `strict_core`
      = row-level strict-all core
    - `dualanchor`
      = 单点边界锚点
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_strictall_core.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_strictall_core_{train,val,all}.txt`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
    - `reports/eval/compare_v19_vs_v67_on_friend_speech_leak_search_v1/candidate_v7_strictcore_v6_dualanchor_overlap_analysis/summary.json`
  - 当前正式 membership subset：
    - `candidate_v6 only`
      - `val_000165`
      - `val_000331`
    - `strict_core only`
      - `val_000239`
    - `candidate_v6 ∩ strict_core`
      - `val_000430`
    - `dualanchor only`
      - `val_000469`
  - 更关键的新事实：
    - `strict_core only`
      的
      `val_000239`
      行为上严格过关，
      但 metadata 语义
      并不落在
      `candidate_v6`
      的 low-transient 模板里；
    - 因而当前不能把
      strict core
      继续误写成：
      - `candidate_v6`
        的继续收紧版
  - 当前默认下一步
    应更新为：
    - 若继续做 proxy，
      默认改为：
      - 用 strict core
        `{val_000239, val_000430}`
        继续找新的行为同族
      - 同时保留
        `val_000469`
        作为边界 anchor
    - 不再默认只沿
      `candidate_v6`
      那套
      low-transient 语义
      继续缩阈值
    - 仍不启动新训练
43. 已继续把 strict-core 周围的 near-miss frontier 正式拆成按失败 guard 分组的两条前沿；
    当前更准确的扩张顺序应固定为：
    - 第一优先：
      `guardv65_only`
    - 第二优先：
      `guardv20_only`
    - 边界锚点：
      `val_000469`
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
    - `scripts/eval/analyze_proxy_strict_near_miss.py`
    - `data/synthetic/val_manifest_friend_speech_leak_search_v1_with_metrics.jsonl`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_strictcore_nearmiss_analysis_with_metrics/summary.json`
  - 当前两条 single-fail 前沿资产：
    - `guardv65_only`
      - `val_000202`
      - `val_000376`
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65.jsonl`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv65_{train,val,all}.txt`
    - `guardv20_only`
      - `val_000223`
      - `val_000316`
      - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20.jsonl`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_singlefail_guardv20_{train,val,all}.txt`
  - 当前判断：
    - `guardv65_only`
      是 strict core
      的默认主扩张前沿，
      因为它只差：
      - `v66 > v65`
      且保住其余四条 guards；
    - 其中
      `val_000376`
      目前最接近 strict core，
      仅差：
      - `v66 - v65 = -0.004292 dB`
    - `guardv20_only`
      则应解释为：
      - 与旧
        `v20`
        guard
        不再对齐的第二分支，
      不与第一优先前沿混写
  - 当前默认下一步
    已进一步更新为：
    - 若继续做 strict-core 扩张，
      默认先围绕：
      - `guardv65_only`
      - 特别是
        `val_000376`
      继续找同向 rows
    - `guardv20_only`
      保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
44. 已继续确认 `guardv65_only` 内部也要再拆一层；当前更准确的结构不是 `{202,376}` 并列前沿，而是一个 `4` 条 relaxed shell 加上一条 `{376,430}` bridge pair：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
    - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min3_on_friend_speech_leak_search_v1/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_guardv65_relaxed_min2_on_friend_speech_leak_search_v1/summary.json`
  - 当前 relaxed shell：
    - `val_000202`
    - `val_000239`
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_shell_{train,val,all}.txt`
  - 当前第一条稳定 bridge pair：
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge_{train,val,all}.txt`
  - 当前判断：
    - 放松
      `v66 > v65`
      后，
      `3+ row`
      搜索只会回到整包 relaxed shell，
      还 carve 不出更细 family；
    - 但 `2` 条口径下，
      第一条被 metadata
      稳定挑出来的 bridge
      不是：
      - `{202,239}`
      也不是
      - `{202,376}`
      而是：
      - `{376,430}`
    - 因此
      `val_000376`
      当前更像 strict core 里
      `430` 这一侧的外扩桥；
      `val_000202`
      则继续保留，
      但不再默认和
      `376`
      并写成同一条语义前沿
  - 当前默认下一步
    已再次更新为：
    - 若继续做 strict-core 扩张，
      默认先围绕：
      - `{val_000376, val_000430}`
      继续找同向 rows
    - `{202,239,376,430}`
      保留为 relaxed shell，
      作为 guardv65 放松后的诊断壳层
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
45. 已继续围绕 `{376,430}` 做 seed-anchored 扩张，并确认 `331` 是当前最近第三条 row；但它只能算 aggregate-only bridge extension，不能当成 row-level clean 第三成员：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
    - `scripts/eval/analyze_proxy_seed_expansion.py`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`
    - `reports/eval/synthetic_proxy_search_candidate_v7_bridgepair_aggregate_expand_min3_on_friend_speech_leak_search_v1/summary.json`
  - 当前 row-level bridge：
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_guardv65_relaxed_lowtransient_lowinttrans_bridge.jsonl`
  - 当前 aggregate-only bridge trio：
    - `val_000331`
    - `val_000376`
    - `val_000430`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331.jsonl`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_bridgepair_aggregate_plus331_{train,val,all}.txt`
  - 当前判断：
    - `val_000331`
      是 bridge pair
      最近的第三条 row，
      但它 row-level
      仍 fail：
      - `v66 > v65`
      - `v66 > v67`
      - `v64 > v67`
    - 只有并进 seed pair 后，
      `{331,376,430}`
      aggregate 才恢复为 full-pass；
    - 因而这条 trio
      当前只能解释为：
      - aggregate-only bridge extension
      不能写成：
      - row-level clean family
    - 同时 generic aggregate search
      仍会自动塌回旧：
      - `candidate_v6`
      语义；
      所以 bridge 语义
      必须靠 seed-anchored 诊断单独保住
  - 当前默认下一步
    已再次更新为：
    - row-level 扩张
      默认继续围绕：
      - `{val_000376, val_000430}`
    - `{val_000331, val_000376, val_000430}`
      保留为 aggregate-only bridge trio，
      不混写成 strict clean family
    - generic aggregate search
      若再次塌回旧 family，
      默认不覆盖
      上述 bridge 解释
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
46. 已进一步确认 `bridgepair seed+1` 的 aggregate-pass 候选榜本身也是混合前沿；当前若继续做第三条扩张，不能再按 aggregate 排名直接选，而要先按 candidate failed-signature 与 distance 拆开：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`
    - `scripts/eval/analyze_proxy_seed_expansion.py`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_seed_expansion_analysis/summary.json`
  - 新增工程视图：
    - `top_nearest_aggregate_pass_expansions_by_joint_distance`
    - `aggregate_pass_signature_summaries`
  - 当前 aggregate-pass 候选中已明确并存：
    - bridge-like 三失败签名：
      - `v66>v65 | v66>v67 | v64>v67`
      - nearest：
        - `val_000331`
        - distance `0.975332`
      - strongest aggregate：
        - `val_000235`
        - distance `6.092051`
    - `guardv20_only`：
      - `val_000223`
      - `val_000316`
    - `guardv65_only` 另一支：
      - `val_000202`
    - strict-core 自身：
      - `val_000239`
  - 当前判断：
    - top aggregate candidate
      `val_000223`
      实际属于：
      - `guardv20_only`
      并不是 bridge 第三条；
    - 在 bridge-like 同签名内部，
      也不能把：
      - aggregate 更强
      直接当成
      - bridge 更近；
      因为：
      - `val_000331`
        是最近第三条
      - `val_000235`
        虽 aggregate 更强，
        但明显是 washout row
  - 当前默认下一步
    已再次更新为：
    - 若继续做 bridge 第三条扩张，
      默认先在：
      - `v66>v65 | v66>v67 | v64>v67`
      这条 same-signature 里，
      按 distance 排，
      当前第一位仍是：
      - `val_000331`
    - `val_000235`
      及其它远距离 aggregate 强 row，
      只保留为 washout 诊断；
    - `val_000223 / val_000316 / val_000202 / val_000239`
      继续留在各自分支，
      不混进 bridge 第三条序列；
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
47. 已继续验证 `{331,376,430}` 能否作为 soft seed 往外长出第四条；结果当前应明确判成不能，trio 仍只是 aggregate-only bridge 结构，不是新的 family 中心：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`
    - `reports/eval/compare_v19_vs_v66_on_friend_speech_leak_search_v1/candidate_v7_bridgepair_trio_seed_expansion_analysis/summary.json`
  - 当前 soft seed：
    - `val_000331`
    - `val_000376`
    - `val_000430`
  - 当前更关键的新事实是：
    - 升成 soft seed 后，
      最近的 non-seed rows
      已经变成：
      - `val_000075`
      - `val_000305`
      - `val_000269`
      它们都不再属于原 bridge-like
      三失败签名；
    - 最近的 aggregate-pass rows
      也优先漂到别的前沿：
      - `val_000076`
      - `val_000316`
      - `val_000401`
      - `val_000223`
    - 真正仍在 bridge-like
      三失败签名里的下一条 row
      已经只剩：
      - `val_000022`
      - distance `2.854296`
      - aggregate min gap `+0.000087 dB`
  - 当前判断：
    - `{331,376,430}`
      不能再升级成：
      - quartet soft-seed family
    - 它的正式定位应保持为：
      - aggregate-only bridge trio
  - 当前默认下一步
    已再次收紧为：
    - row-level 扩张
      仍只围绕：
      - `{val_000376, val_000430}`
    - `val_000331`
      继续保留为唯一站得住的
      aggregate-only 第三条，
      但不升级成新的 seed 中心
    - 默认不再从 trio
      往外推第四条
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
48. 已把 `{376,430}` 的 metadata 邻域正式投影到当前 active split，并补出行为 compare；当前不能再把 active-neighbor top10 整包当成 bridge family，因为它在行为上会稳定裂成 `v66top / v67top_v66near / v65top_tail` 三层：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_neighbor_behavior_probe.md`
    - `scripts/eval/analyze_manifest_seed_neighbors.py`
    - `reports/eval/active_split_bridgepair_neighbor_analysis/summary.json`
    - `reports/eval/bridgepair_active_metadata_neighbor_top10_direction_analysis/summary.json`
  - 当前 active-neighbor top10：
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
    - top10 里：
      - `9` 条 train
      - `1` 条 val
      - 全部是 `target_clean_speech`
      - temporal pattern 为：
        - `target_full = 6`
        - `target_absent_head = 3`
        - `target_absent_tail = 1`
    - 其中：
      - `train_001279`
      已知属于 absent-like
      `exact_nontargetfull`
      旧资产
    - 行为 compare 后，
      aggregate 排序直接塌成：
      - `v67 > v65 > v66 > v64 > v20 > v24`
      - `v66 > v64 = +0.010333 dB`
      - `v66 > v65 = -0.033064 dB`
      - `samplewise_extra_constraint_pass = 0 / 10`
  - 当前行为分层资产已固定成：
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
  - 当前判断：
    - active split
      不是没有 bridge coverage，
      而是：
      - 有 metadata coverage
      - 但行为上是混合区
    - `val_000331`
      在 active split 投影里
      已明确落到：
      - `v65top_tail`
      不再属于：
      - `v66` 领先带
  - 当前默认下一步
    已再次收紧为：
    - row-level bridge
      仍只保留：
      - `{val_000376, val_000430}`
    - active-neighbor top10
      默认改记为：
      - behavior-mixed diagnostic buffer
      不作为新 proxy / 新训练入口
    - 若后续还要在 active split
      继续追 bridge 方向，
      默认优先看：
      - `v66top`
      这 `2` 条
      是否能与 row-level bridge
      建立更直接联系
    - `v67top_v66near`
      与
      `v65top_tail`
      继续保留为边界层与负向尾部；
      尤其：
      - `train_001279`
      - `val_000331`
      继续作为风险提示样本
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
49. 已继续把 active-neighbor 里的 `v66top` 两条向外拉宽成一个 active microbuffer，并确认这条线只有在先剥掉 nonfull / absent 污染后，才会恢复成 aggregate-pass 的 `v66` 小缓冲：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_targetfull_split.md`
    - `reports/eval/bridgepair_active_microbuffer_v66top_v1_direction_analysis/summary.json`
    - `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_direction_analysis/summary.json`
  - 当前宽版 `v66top_v1`
    过滤条件：
    - `recipe = target_clean_speech`
    - `target_transient_presence_share_mean <= 0.008`
    - `interference_transient_presence_minus_mid_db_mean <= -1.0`
  - 宽版资产：
    - train `7`
    - val `2`
    - all `9`
  - 当前更关键的新事实是：
    - 宽版一混入：
      - `target_absent_head`
      - `target_absent_tail`
      - `target_intermittent`
      aggregate 就塌成：
      - `v65 > v64 > v66`
      - `v66 > v64 = -0.049224 dB`
      - `v66 > v65 = -0.055437 dB`
    - 宽版里已直接混入：
      - `train_000405`
      - `train_001491`
      这类 absent-like
      `exact_nontargetfull`
      旧资产
  - 当前 `target_full` 收窄版固定为：
    - `train_000597`
    - `train_001599`
    - `train_001843`
    - `val_000430`
  - 当前 `target_full` 版 aggregate
    恢复成：
    - `v66 > v64 > v67 > v20 > v65`
    - 且 full extra constraints
      全部 aggregate pass
  - 但当前仍不能把它写成 row-level clean family，
    因为：
    - `samplewise extra pass = 1 / 4`
    - `train_001843`
      当前仍是 noisy carry-over
  - 当前判断：
    - 宽版 `v66top_v1`
      = contaminated active microbuffer
    - `target_full` 版
      = aggregate-pass `v66` microbuffer
      with noisy carry-over
  - 当前默认下一步
    已再次收紧为：
    - 若继续在 active split
      追 bridge 方向，
      默认只保留：
      - `target_full` 版 `v66` microbuffer
    - 宽版 `v66top_v1`
      只保留为：
      - nonfull / absent 污染会把 aggregate
        拉回 `v65`
        的反例资产
    - `train_001843`
      继续保留为 noisy carry-over，
      不和：
      - `train_000597`
      - `train_001599`
      - `val_000430`
      写成同纯度成员
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
50. 已继续把 `target_full` 微缓冲里的 noisy carry-over 拆掉；当前 active split 上最小可保留的 bridge-like train-side mirror 已进一步收窄为 core trio `{train_000597, train_001599, val_000430}`：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_core_trio.md`
    - `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`
  - 当前 core trio 资产：
    - train：
      - `train_000597`
      - `train_001599`
    - val：
      - `val_000430`
  - 当前更关键的新事实是：
    - 去掉：
      - `train_001843`
      之后，
      core trio aggregate
      继续保持：
      - `v66 > v64 > v67 > v20 > v24 > baseline > v65`
      且 full extra constraints
      全部 aggregate pass
    - 相比上一轮 `4` 条 target_full 微缓冲，
      当前：
      - `v66 > v64`
        从：
        - `+0.014670 dB`
        抬到：
        - `+0.030334 dB`
      - `v66 > v65`
        从：
        - `+0.114106 dB`
        抬到：
        - `+0.181224 dB`
      说明：
      - `train_001843`
        的确就是主要 carry-over
  - 当前 samplewise 状态：
    - `ordered pass = 3 / 3`
    - `extra pass = 1 / 3`
    - train 两条：
      - `train_000597`
      - `train_001599`
      仍共享同一条漏点：
      - `v64 > v67`
  - 当前判断：
    - core trio
      = aggregate-pass active microbuffer core
      with shared train-side
      `v64 > v67` leak
    - `train_001843`
      = target_full 微缓冲里的
      carry-over
  - 当前默认下一步
    已再次收紧为：
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
      这一个 shared leak
      去看；
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
51. 已把 `core trio` 投回 `active_targetfull_clean` 这 `88` 条全量 `target_full clean` workspace 继续核对；当前 train-side 外壳不能再写成单 `v64 > v67` 漏点，而应固定成更窄的 dual-leak shell，但它不能升级成新的 mirror core：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_targetfull_clean_dualleak_shell.md`
    - `reports/eval/active_targetfull_clean_strict_nearmiss_analysis/summary.json`
    - `reports/eval/bridgepair_active_targetfull_clean_core_dualleak_shell_direction_analysis/summary.json`
    - `reports/eval/active_targetfull_clean_core_trio_neighbor_analysis/summary.json`
  - 本轮脚本修正：
    - `scripts/eval/analyze_proxy_candidate_direction.py`
    - 当前 `order_pass(...)`
      与 `extra_constraints_pass(...)`
      已改成：
      - 记录全部 constraints
      - 再统一返回 overall pass / fail
    - 已重跑：
      - `reports/eval/bridgepair_active_microbuffer_v66top_v1_targetfull_core_direction_analysis/summary.json`
    - 当前 `train_000597`
      与
      `train_001599`
      都已明确不是：
      - 只差 `v64 > v67`
      而是同时差：
      - `v64 > v67`
      - `v20 > v24`
  - 当前更关键的新事实是：
    - 在 `88` 条 workspace 上，
      单-fail rows
      只有：
      - `v66>v65`
        - `3`
      - `v20>v24`
        - `1`
      - `v66>v64`
        - `1`
    - 并不存在：
      - 纯 `v64>v67`
        单漏 shell
    - 当前真正包住
      `597 / 1599`
      的最小 train shell 为：
      - `train_000597`
      - `train_001477`
      - `train_001599`
      - `train_000865`
      - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_all.txt`
  - 当前 focused direction：
    - aggregate 排序：
      - `v66 > v67 > v24 > v64 > baseline > v65 > v20`
    - 关键 gaps：
      - `v66 > v64 = +0.129529 dB`
      - `v66 > v65 = +0.175244 dB`
      - `v66 > v67 = +0.050005 dB`
      - `v64 > v67 = -0.079525 dB`
      - `v20 > v24 = -0.105507 dB`
    - `samplewise extra pass = 0 / 4`
  - metadata 邻域复盘：
    - 相对 `core trio`
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
    - 当前解释应固定为：
      - dual-leak shell
        是 behavior 同签名壳层，
        不是 metadata 紧邻镜像外环
      - 其它 all-pass rows
        属于别的 fully-pass frontier，
        不是 bridge 扩张入口
  - 当前默认下一步
    已再次收紧为：
    - `core trio`
      `{train_000597, train_001599, val_000430}`
      仍是当前唯一可保留的
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
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
52. 已继续验证 dual-leak shell 能否作为新的 seed 往外扩；结果当前应明确判成不能，它不是新的 family 中心，而只是 `core trio` 外侧一层 train-only diagnostic ring：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_dualleak_shell_neighbor_drift.md`
    - `reports/eval/active_targetfull_clean_dualleak_shell_neighbor_analysis/summary.json`
  - 本轮新增物化资产：
    - `data/synthetic/train_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell.jsonl = 4`
    - `data/synthetic/val_manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell.jsonl = 0`
    - `data/synthetic/manifest_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_all.jsonl = 4`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_core_dualleak_shell_{train,val,all}.txt`
  - 当前 dual-leak shell：
    - `train_000597`
    - `train_001477`
    - `train_001599`
    - `train_000865`
  - 当前更关键的新事实是：
    - 以这 `4` 条为 seed
      重排邻域后，
      最近邻 top10
      立刻变成：
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
  - 当前判断：
    - dual-leak shell
      不是可扩张 family；
    - 它更准确的定位应固定为：
      - `core trio`
        与外层 mixed frontier
        之间的一层
        train-only diagnostic ring
  - 当前默认下一步
    已再次收紧为：
    - active bridge
      仍只保留：
      - `core trio`
        `{train_000597, train_001599, val_000430}`
    - dual-leak shell
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
        会一起漏
      不再继续找
      shell 的外层扩张
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
53. 已把 `active_targetfull_clean` 上的 `v64>v67 / v20>v24` 组合正式切成四个标准桶并补齐 focused direction；结果当前应明确判成：pair bucketization 只是在全量 workspace 上把 `core trio / dual-leak shell / mixed frontier` 三层结构重新显影，并没有长出新的 bridge family：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_active_guardpair_bucketization.md`
    - `scripts/eval/analyze_proxy_constraint_pair_buckets.py`
    - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_bucket_analysis/summary.json`
  - 当前两条 guard：
    - A：
      - `v64 > v67`
    - B：
      - `v20 > v24`
  - 当前四桶数量：
    - `pass_both = 18`
    - `fail_a_only = 20`
    - `fail_b_only = 7`
    - `fail_both = 43`
  - 当前 focused direction：
    - `pass_both`
      - aggregate：
        - `v65 > v64 > v20 > v66`
      - `v66 > v64 = -0.037591 dB`
      - `v66 > v65 = -0.059018 dB`
    - `fail_a_only`
      - aggregate：
        - `v67 > v65 > v66 > v64`
      - `v66 > v67 = -0.169243 dB`
    - `fail_b_only`
      - aggregate：
        - `v64 > v66 > v67`
      - `v66 > v64 = -0.066802 dB`
    - `fail_both`
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
  - 当前更关键的新事实是：
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
    - 入口：
      - `reports/eval/active_targetfull_clean_guardpair_v64gtv67_v20gtv24_fail_both_top_alias_split/summary.json`
  - 当前判断：
    - `pass_both`
      不是更干净的 bridge 候选，
      而更像：
      - `v65 / v64`
        fully-pass frontier
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
      但其中唯一还能保持
      `v66-top`
      的，
      还是 dual-leak shell
  - 当前默认下一步
    已再次收紧为：
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
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
54. 已继续把 `fail_both` 大桶内部的 `v66-top` 小核与 `v67-top` 外层正式拆开；当前 active bridge 这条线的内外边界已经基本钉死：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_failboth_v66_vs_v67_split.md`
    - `reports/eval/active_targetfull_clean_failboth_topv66_vs_topv67_analysis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_subgroup_analysis/summary.json`
  - 当前 `v66-top 4`：
    - `train_000597`
    - `train_000865`
    - `train_001477`
    - `train_001599`
    - train `4`
    - val `0`
  - 当前 `v67-top 34`：
    - train `28`
    - val `6`
  - 当前更关键的新事实是：
    - `v66-top 4`
      aggregate：
      - `v66 > v67 > v24 > v64`
      - `v66 > v64 = +0.129529 dB`
      - `v66 > v67 = +0.050005 dB`
    - `v67-top 34`
      aggregate：
      - `v67 > v65 > v66 > v24 > baseline > v64 > v20`
      - `v66 > v64 = +0.187917 dB`
      - `v66 > v67 = -0.296784 dB`
    - 也就是：
      - 两边真正的分界
        不是：
        - `v66` 能不能压住
          `v64`
      - 而是：
        - `v67`
          有没有把
          `v66`
          彻底接管
  - 直接均值对照：
    - `v66-top 4`
      相对 `v67-top 34`
      当前固定更偏：
      - 更低的
        target transient / share
      - 更低的
        interference transient / share
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
  - subgroup split 当前进一步说明：
    - `fail_both`
      里 `v66-v67`
      的崩塌
      不是单一字段，
      而是一组：
      - target transient
      - target share
      - interference transient
      - interference share
      - cosine
      一起把 rows
      推向
      `v67-top`
      外层 frontier
  - 当前判断：
    - dual-leak shell
      应进一步固定写成：
      - `fail_both`
        大桶里唯一仍是
        `v66-top`
        的 train-only inner core
    - `v67-top 34`
      不是它的外环 family，
      而是：
      - `v67`
        主导的外层 mixed frontier
  - 当前默认下一步
    已再次收紧为：
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
        与
        `v67-top 34`
        在更细 metadata /
        音频案例上
        是否存在可解释的
        单一触发因子
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
55. 已继续把 dual-leak shell vs `v67-top 34` 做成单字段阈值扫描；当前这条线可以正式定性成多因子共驱动，不存在能一刀切开的单 trigger：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_failboth_single_trigger_scan.md`
    - `reports/eval/active_targetfull_clean_failboth_single_field_trigger_scan/summary.json`
  - 当前扫描字段：
    - `target_transient_presence_minus_mid_db_mean`
    - `target_transient_presence_share_mean`
    - `interference_transient_presence_minus_mid_db_mean`
    - `interference_transient_presence_share_mean`
    - `target_interference_logspec_cosine`
  - 当前更关键的新事实是：
    - 若要求：
      - dual-leak shell
        `4 / 4`
        全部保留
    - 最强单字段：
      - `interference_transient_presence_minus_mid_db_mean <= 2.428970`
      仍会误收：
      - `7`
        条 `v67-top`
    - 第二强单字段：
      - `target_interference_logspec_cosine >= 0.671519`
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
  - 当前判断：
    - dual-leak shell
      之所以还能保持：
      - `v66-top`
    - 不是因为某一个
      单字段阈值成立，
    - 而是：
      - 更低的
        target transient / share
      - 更低的
        interference transient / share
      - 更高的
        cosine
      这组条件
      共同把它留在：
      - train-only inner core
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
  - 当前默认下一步
    已再次收紧为：
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
    - `guardv20_only`
      继续保留为第二优先分支
    - `val_000469`
      继续单独保留为边界 anchor
    - 仍不启动新训练
56. 已继续把 `5` 条 persistent borderline rows 做成 case-level split；当前应明确判成它们并不是同一种外层边界带，而是 `4` 条真正贴着 shell 的 train near-shell edge band 加 `1` 条 metadata-only val outlier：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_failboth_borderline_case_split.md`
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
    - 它们在 dual-leak shell seed
      的 joint-distance 排名里是：
      - `#1`
      - `#2`
      - `#3`
      - `#9`
    - 这 `4` 条 aggregate
      已可稳定写成：
      - `v67 > v66 > v64 > v65 > v24 > baseline > v20`
    - 也就是：
      - 仍保住 `v66 > v64`
      - 但已经稳定输给 `v67`
    - 所以它们当前最准确的身份应更新为：
      - train near-shell edge band
      不是：
      - dual-leak shell 扩张成员
  - `val_000182`
    当前必须单独处理：
    - 虽然它仍会在：
      - `4 / 5`
        单字段 full-recall 阈值下
        被误收
    - 但它在 dual-leak shell seed
      的 joint-distance 排名里
      已掉到：
      - `#39 / 39`
    - 更关键的是：
      - `constraint_distance_z = 14.799924`
      明显表明它不是
      near-shell 方向样本，
      而只是：
      - metadata-only borderline outlier
  - 当前默认下一步
    已继续收紧为：
    - 不再把这 `5` 条
      persistent borderline rows
      当成一个整体追
    - 若还继续推进，
      默认只围绕：
      - `train_001079`
      - `train_001494`
      - `train_000697`
      - `train_001589`
      做更细 case diagnosis
    - `val_000182`
      只单独保留为
      metadata-only outlier
    - active bridge
      主体解释更新为：
      - `core trio`
        = 唯一可保留 active core
      - dual-leak shell
        = train-only inner core
      - near-shell edge band `4`
        = 最靠近 shell 的 train 外层边界带
      - `val_000182`
        = metadata-only false shell
      - remaining `v67-top`
        = 更外层 mixed frontier
    - 仍不启动新训练
57. 已继续把 near-shell edge band `4` 深拆到 pure `v67` takeover 个例层；当前默认解释必须再收紧一层：真正代表第一层 `v67` 接管的只有 `3` 条 pure edge，而 `train_001589` 不能继续和它们并写：
  - 入口：
    - `reports/daily/2026-03-21_candidate_v7_failboth_nearshell_case_diagnosis.md`
    - `reports/daily/2026-03-21_candidate_v7_failboth_pure_v67_takeover_case_diagnosis.md`
    - `reports/eval/active_targetfull_clean_failboth_nearshell_case_diagnosis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_pure_v67_takeover_case_diagnosis/summary.json`
  - 当前 pure `v67` takeover edge `3`：
    - `train_001079`
    - `train_001494`
    - `train_000697`
  - 这 `3` 条当前共同签名已固定为：
    - 保住：
      - `v66 > v64`
      - `v66 > v65`
    - 失败：
      - `v66 > v67`
      - `v64 > v67`
      - `v20 > v24`
    - aggregate：
      - `v67 > v66 > v64 > v24 > v65 > baseline > v20`
  - 当前更关键的新事实是：
    - pure `3`
      相对 shell `4`
      不是：
      - 更高 interference transient
        的 takeover
    - 而更接近：
      - 更长一点的 target
      - 更弱的 interference gain
      - 更早的 interference start
      - 更低的 cosine
      共同把 rows
      推向：
      - pure `v67` takeover
    - `train_001589`
      则必须单独降格为：
      - `v67 + v65`
        takeover singleton
      因为它已经额外失败：
      - `v66 > v65`
  - 当前判断：
    - shell 外第一层稳定接管
      应固定写成：
      - pure `v67` takeover edge `3`
    - `train_001589`
      不再算：
      - pure edge 成员
    - `edge 4`
      的混合均值
      不能再直接当成：
      - pure takeover 机制
      的解释
  - 当前默认下一步
    已再次收紧为：
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
    - active bridge
      主体解释更新为：
      - `core trio`
        = 唯一可保留 active core
      - dual-leak shell
        = train-only inner core
      - pure `v67` takeover edge `3`
        = 第一层 `v67`
          takeover 过渡带
      - `train_001589`
        = `v67 + v65`
          drift singleton
      - remaining `v67-top`
        = 更外层 mixed frontier
    - 仍不启动新训练
58. 已把 pure `v67` takeover `3` 周围的 train-side 最近邻结构补成 metadata-rich 版本；当前分支图上的默认解释必须再收紧为“pure trio 周围不是单条外扩边，而是 shell-like / pure-signature / `v65` drift 三层 mixed ring”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_pure_v67_neighbor_diagnosis.md`
    - `reports/eval/active_targetfull_clean_failboth_pure_v67_neighbor_diagnosis/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_pure_v67_neighbor_diagnosis_train_only/summary.json`
    - `scripts/eval/analyze_proxy_case_neighbors.py`
  - 当前 train-only 最近邻
    已固定裂成：
    - shell-like `v66-top 3`
      - `train_001599`
      - `train_000597`
      - `train_000865`
    - pure-signature `v67-top 5`
      - `train_000799`
      - `train_001639`
      - `train_000216`
      - `train_000759`
      - `train_001006`
    - `v65` drift `v67-top 4`
      - `train_001745`
      - `train_001610`
      - `train_000266`
      - `train_001589`
  - 当前更关键的新事实是：
    - 若不先切 train-only，
      `val_000182`
      会重新混进：
      - pure trio 最近邻
      所以这条线
      不能再直接用
      train / val 混合 top-k
      下结论
    - shell-like `3`
      相对 pure trio
      共同更接近：
      - 更强 interference gain
      - 更高 cosine
      - `v66 > v67`
        仍为正
    - pure-signature `5`
      虽然已出现：
      - 更高 interference transient
      - 更高 interference share
      但仍保住：
      - `v66 > v64`
      - `v66 > v65`
    - `v65` drift `4`
      则共同出现：
      - `v66 > v64`
        接近 `0`
      - `v66 > v65`
        翻负
  - 当前判断：
    - pure `v67` takeover
      不应再被写成：
      - 低 transient 单层边界
    - 当前更准确的主解释应改成：
      - shell-like 回缩
      - pure-signature `v67-top`
      - `v65` drift
        三层 mixed ring
    - 因而当前分支图上的默认下一步
      应更新为：
      - 不再回到 shell 搜索
      - 不再混着 val 做近邻
      - 若还继续推进，
        默认只围绕：
        - pure-signature `v67-top 5`
        - `v65` drift `v67-top 4`
        做下一层 split
      - 下一条要解释的
        关键边界
        不是：
        - transient
          是否还低
        而是：
        - `v66 > v64`
          何时被磨平
        - `v66 > v65`
          何时一起翻掉
59. 已把 mixed ring 正式拆成 pure-signature `v67-top 5` 与 `v65` drift `4` 两组；当前分支图上的默认解释必须继续收紧为“分界不在 transient 本身，而在 `v66>v64` 保护带是否还保有正 margin”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_neighbor_ring_split.md`
    - `reports/eval/active_targetfull_clean_failboth_neighbor_ring_split/summary.json`
    - `scripts/eval/analyze_proxy_group_split.py`
  - 当前两组已固定为：
    - pure-signature `v67-top 5`
      - `train_000216`
      - `train_000759`
      - `train_000799`
      - `train_001006`
      - `train_001639`
    - `v65` drift `v67-top 4`
      - `train_000266`
      - `train_001589`
      - `train_001610`
      - `train_001745`
  - 当前更关键的新事实是：
    - 两组都已经有：
      - 高 interference transient
    - pure-signature `5`
      仍共同保住：
      - `v66 > v64`
      - `v66 > v65`
    - `v65` drift `4`
      则已掉到：
      - `v66 > v64`
        接近 `0`
      - `v66 > v65`
        翻负
    - 所以当前应固定写成：
      - `v65`
        不是因为 transient 第一次变高才进场
      - 而是因为
        `v66 > v64`
        这层保护带先塌平
  - 当前判断：
    - `train_001589`
      已正式并入：
      - `v65` drift
      不再保留为 pure edge 边缘样本
    - 当前分支图上的默认下一步
      应继续收紧为：
      - 不再反复判断
        `train_001589`
        身份
      - 若还继续推进，
        默认只围绕：
        - pure-signature `5`
        - `v65` drift `4`
        做保护带塌缩诊断
      - 下一条要解释的
        核心边界
        固定为：
        - `v66 > v64`
          的最后一层 buffer
        如何与：
        - target / reference length
        - gain / offset
        - cosine
        共变
60. 已把 mixed ring `9` 条样本继续压成 buffer-collapse 诊断；当前分支图上的默认解释必须再收紧为“这层 ring 里没有哪个单字段还能做 hard carve，真正最稳的下一条边界是 `v66>v64` 与 `v66>v65` 的联动塌缩”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_neighbor_buffer_collapse_diagnosis.md`
    - `reports/eval/active_targetfull_clean_failboth_neighbor_ring_buffer_collapse/summary.json`
  - 当前更关键的新事实是：
    - ring `9`
      内部：
      - `corr(v66>v64, v66>v65) = +0.5021`
      是最明显联动
    - 其余：
      - duration
      - gain
      - offset
      - cosine
      - transient
      与 `v66>v64`
      都只有弱相关
    - low-buffer `5`
      当前为：
      - `train_001745`
      - `train_001610`
      - `train_000266`
      - `train_001589`
      - `train_001006`
      其中：
      - `train_001006`
        已明确应写成
        pure-signature 组内的
        low-buffer edge
  - 当前判断：
    - mixed ring
      这一步不再适合继续做：
      - 单字段 carve
    - 当前更准确的主问题应固定为：
      - `v66 > v64`
        还剩多少
      - `v66 > v65`
        是否已经贴到 `0`
    - 因而当前分支图上的默认下一步
      应继续收紧为：
      - 不再继续扩大样本面
      - 若还继续推进，
        默认只围绕：
        - `train_001006`
        - `train_001589`
        - `train_001610`
        - `train_001745`
        做 case-to-case 对照
      - 下一条要解释的
        核心边界
        固定为：
        - pure-signature low-buffer edge
          为什么还能挂住
        - 而 drift ring
          为什么已经翻到
          `v66 <= v65`
61. 已把 `train_001006 / train_001589 / train_001610 / train_001745` 压成 reference-group positioning；当前分支图上的默认解释必须再收紧成“两轴并读：metadata position 还停在哪一圈，和 margin state 是否已经先掉进 `v65` drift，不再允许用单轴 nearest-group 贴标签”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_lowbuffer_edge_positioning.md`
    - `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_positioning/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_lowbuffer_edge_case_contrast/summary.json`
  - 当前更关键的新事实是：
    - `train_001006`
      对：
      - pure-signature
        的 total / metadata / margin
      三条距离都最近；
      因而它当前仍应固定写成：
      - pure-signature low-buffer edge
    - `train_001589`
      total 与 margin
      都已经最近：
      - `v65` drift
    - `train_001610`
      与 `train_001745`
      则都出现：
      - total / metadata
        仍更靠 pure-signature
      - 但 margin
        已更靠 `v65` drift
      说明这一步真正发生的是：
      - margin-first collapse
      而不是 metadata
        先整体迁移
  - 当前判断：
    - mixed ring
      这一步已不再适合继续问：
      - “它整体更像哪一组”
    - 当前更准确的主问题应固定为：
      - metadata position
        还停在哪一圈
      - `v66 > v64`
        与
        `v66 > v65`
        是否已经先塌
    - 因而当前分支图上的默认下一步
      应继续收紧为：
      - 不再继续扩大样本面
      - 若还继续推进，
        默认只围绕：
        - `train_001006`
        - `train_001610`
        - `train_001745`
        做 margin-first collapse
        对照
      - 下一条要解释的
        核心边界
        固定为：
        - 为什么
          `train_001610`
          `train_001745`
          在 metadata
          还靠 pure-signature
          时，
          已先掉进 drift margin
        - 以及
          `train_001006`
          为什么还能保住
          最后一层
          `v66 > v65`
          buffer
62. 已把 `train_001006 / train_001610 / train_001745` 压成 pure-signature -> `v65` drift 的双轴 transition 投影；当前分支图上的默认解释必须再收紧成“这条路径是 margin-first collapse，不是 metadata 先整体迁移”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_margin_first_transition_axes.md`
    - `reports/eval/active_targetfull_clean_failboth_margin_first_transition_axes/summary.json`
  - 当前更关键的新事实是：
    - `train_001006`
      - metadata ratio
        = `-1.581300`
      - margin ratio
        = `+0.051259`
      说明它两条轴
      都仍停在 pure 侧
    - `train_001610`
      - metadata ratio
        = `+0.004083`
      - margin ratio
        = `+1.240782`
      说明它几乎还停在
      pure metadata center，
      但 margin
      已经超过 drift center
    - `train_001745`
      - metadata ratio
        = `+0.349352`
      - margin ratio
        = `+1.046646`
      说明它 metadata
      只部分迁移，
      margin
      已基本走完
  - 当前判断：
    - mixed ring
      这一步不再适合继续问：
      - 哪些 metadata
        先把 row
        整体推向 drift
    - 当前更准确的主问题应固定为：
      - `v66 > v64`
      - `v66 > v65`
        哪条先塌
      - 哪条决定
        `train_001610`
        与
        `train_001745`
        的分叉深度
    - 因而当前分支图上的默认下一步
      应继续收紧为：
      - 不再继续扩大样本面
      - 若还继续推进，
        默认只围绕：
        - `train_001006`
        - `train_001610`
        - `train_001745`
        做 margin-order split
      - 下一条要解释的
        核心边界
        固定为：
        - `v66 > v64`
          是否先于
          `v66 > v65`
          决定 drift 进入
        - `train_001745`
          为什么会进一步走到：
          - `v66 < v64`
          - `v66 ≈ v65`
        - `train_001006`
          为什么还能保住：
          - `v66 > v65 > 0`
63. 已把 `train_001006 / train_001610 / train_001745` 的两条关键 gap 压成 zero-cross 次序拆分；当前分支图上的默认解释必须再收紧成“`v66 > v65` 先越零，`v66 > v64` 先近零、后翻负”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_margin_order_split.md`
    - `reports/eval/active_targetfull_clean_failboth_margin_order_split/summary.json`
  - 当前更关键的新事实是：
    - `v66 > v64`
      的 zero-cross threshold
      = `1.123493`
    - `v66 > v65`
      的 zero-cross threshold
      = `0.818051`
      因而：
      - `v66 > v65`
        更早越零
    - `train_001006`
      当前仍是：
      - pre-entry lowbuffer edge
      因为两条 gap
      都只走到越零路径的
      约三分之一
    - `train_001610`
      当前是：
      - `hinge_entry_v65_crossed_first`
      因为：
      - `v66 > v65`
        已越零
      - `v66 > v64`
        仍只差最后一小步
    - `train_001745`
      当前是：
      - `post_entry_v64_deeper_than_v65`
      因为：
      - 两条 gap
        都已越零
      - 但
        `v66 > v64`
        明显更深
  - 当前判断：
    - mixed ring
      这一步不再适合继续问：
      - drift
        是否已经进入
    - 当前更准确的主问题应固定为：
      - 为什么
        `train_001745`
        会比
        `train_001610`
        多走出：
        - `v66 < v64`
    - 因而当前分支图上的默认下一步
      应继续收紧为：
      - 不再继续扩大样本面
      - 若还继续推进，
        默认只围绕：
        - `train_001610`
        - `train_001745`
        做 post-entry depth split
      - 下一条要解释的
        核心边界
        固定为：
        - `v66 > v64`
          在 `train_001745`
          上为什么会单边继续崩塌
        - 以及
          `v66 > v65`
          为什么在它身上
          只刚刚越零
          没有同步深崩
64. 已把 `train_001610 / train_001745` 压成 post-entry depth split；当前分支图上的默认解释必须再收紧成“更深阶段不是 `v65` 继续 takeover，而是 `v64` 剩余 buffer 被继续单边打穿”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_post_entry_depth_split.md`
    - `reports/eval/active_targetfull_clean_failboth_post_entry_depth_split/summary.json`
  - 当前更关键的新事实是：
    - 相比 `train_001610`，
      `train_001745`
      的：
      - `v66 - v64`
        继续下掉
        `0.028624 dB`
      - 但
        `v66 - v65`
        反而回升
        `0.049313 dB`
      因而它更深
      的主轴不是：
      - `v65`
        更强 takeover
      而是：
      - `v64`
        buffer
        被继续打穿
    - ranking
      也因此改写成：
      - `v67 > v64 > v65 > v66`
      而不再是：
      - `v67 > v65 > v66 > v64`
    - 在这对样本里，
      与更深 `v64` collapse
      同步出现的是：
      - 更早 overlap
      - 更长 reference
      - 更高 target / interference transient
      - 更弱 gain
      - cosine 略更高
  - 当前判断：
    - post-entry
      这一步不再适合继续问：
      - `v65`
        是否继续 takeover
    - 当前更准确的主问题应固定为：
      - `v64`
        为什么失去最后 buffer
    - 因而当前分支图上的默认下一步
      应继续收紧为：
      - 不再继续扩大样本面
      - 若还继续推进，
        默认只围绕：
        - `train_001745`
        的
        `v64`
        single-sided collapse
        做同型 row
        复核
      - 下一条要解释的
        核心边界
        固定为：
        - 这组更早 overlap /
          更长 reference /
          更高双侧 transient /
          更弱 gain
          的组合
          是否构成
          可复用 post-entry signature
65. 已把 `train_001745` 周围的窄 ring train-side 近邻压成 signature scan；当前分支图上的默认解释必须再收紧成“这层 ring 里没有第二条 `both-crossed + v64-deeper` row，`train_001745` 仍是 rare singleton pocket”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_post_entry_v64_collapse_neighbor_scan.md`
    - `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_neighbor_scan_all/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_post_entry_v64_collapse_signature_scan/summary.json`
  - 当前更关键的新事实是：
    - 扫描
      `27`
      条 train-side `topv67`
      近邻后，
      bucket
      结构为：
      - `pre_entry_or_pure = 20`
      - `hinge_secondary_crossed_first = 4`
      - `post_entry_both_crossed_secondary_deeper_or_equal = 1`
      - `reference_only_crossed_unexpected = 2`
      - `post_entry_both_crossed_reference_deeper = 0`
    - 离得最近的
      post-entry row
      是：
      - `train_001543`
      但它属于：
      - `both-crossed + v65-deeper`
      不是：
      - `both-crossed + v64-deeper`
    - 两条
      `v64-only crossed`
      row：
      - `train_000664`
      - `train_000210`
      也不是
      `train_001745`
      的 mirror；
      它们仍保有：
      - `v66 > v65`
  - 当前判断：
    - `train_001745`
      在当前窄 ring
      里没有
      local mirror；
      它的更深 `v64`
      collapse
      仍应视作：
      - rare conditional singleton
    - 因而当前分支图上的默认问题
      不再是：
      - 还能不能再找一个
        一模一样的 row
      而应改成：
      - 为什么最像它的
        假近邻
        会分流到：
        - `v65` deeper
        - `v64-only crossed`
        两条异型支路
  - 当前默认下一步：
    - 不再外扩 ring
    - 若继续推进，
      默认只对比：
      - `train_001745`
      - `train_001543`
      - `train_000664`
      解释：
      - 为什么三者都碰到
        `v64`
        边界
        却只剩
        `train_001745`
        落在
        `both-crossed + v64-deeper`
        pocket
66. 已把 `train_001745 / train_001543 / train_000664` 压成 post-entry branch divergence split；当前分支图上的默认解释必须再收紧成“它们不是单线深度序列，而是从同一个 `v64 crossed` shelf 分叉成 `v65 sink` 和 `v64 pocket` 两支”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_post_entry_branch_divergence_split.md`
    - `reports/eval/active_targetfull_clean_failboth_post_entry_branch_divergence_split/summary.json`
  - 当前更关键的新事实是：
    - `train_001543`
      相对
      `train_000664`
      的：
      - `v66 - v64`
        只差
        `+0.000345 dB`
      - `v66 - v65`
        却额外下掉
        `0.118462 dB`
      所以它最干净地代表：
      - `v65 sink`
    - `train_001745`
      相对
      `train_000664`
      的：
      - `v66 - v64`
        再下掉
        `0.018296 dB`
      - `v66 - v65`
        只再下掉
        `0.006385 dB`
      所以它代表的是：
      - `v64`
        已更深翻负
      - `v65`
        只刚好越零
    - `train_001745`
      相对
      `train_001543`
      的：
      - `v66 - v64`
        更负
        `0.018641 dB`
      - 但
        `v66 - v65`
        反而更高
        `0.112077 dB`
      所以两者不是
      单轴深浅关系，
      而是：
      - `v65 sink`
      - `v64 pocket`
        的 branch identity
  - 当前判断：
    - `train_000664`
      应视为当前：
      - `v64 crossed`
        shared shelf
      的主锚点
    - `train_001543`
      应视为：
      - `v65 sink`
        主锚点
    - `train_001745`
      应视为：
      - `v64 pocket`
        主锚点
  - 当前默认下一步：
    - 不再外扩 ring
    - 若继续推进，
      默认只对比：
      - `train_001543`
      - `train_000664`
      去隔离：
      - 什么因素
        会把
        `v66 > v65`
        从刚好为正
        推成显著为负，
        同时几乎不改写
        `v66 > v64`
67. 已把 `train_001543 / train_000664` 压成 `v65 sink` isolation；当前分支图上的默认解释必须再收紧成“这对样本几乎固定住了 `v66 > v64`，真正单边翻的是 `v66 > v65`”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_isolation.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_isolation/summary.json`
  - 当前更关键的新事实是：
    - `train_001543`
      相对
      `train_000664`
      的：
      - `v66 - v64`
        只变化
        `+0.000345 dB`
      - 但
        `v66 - v65`
        额外下掉
        `0.118462 dB`
      所以这对
      可以正式当作：
      - `v65 sink`
        isolation pair
    - 与这一步同步出现的
      组合信号
      是：
      - 更短 reference
      - 更早 overlap
      - 更弱 gain
      - 更高双侧 transient
      - 更低 cosine
  - 当前判断：
    - 如果要继续隔离：
      - 谁在推动
        `v66 > v65`
        单边翻负
      不应再把：
      - `train_001745`
        的
        `v64 pocket`
      混回同一条线
    - 当前这条分支
      应固定成：
      - `train_001543`
        = `v65 sink`
          主锚点
      - `train_000664`
        = `pre-sink shared shelf`
          主锚点
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认优先检查：
      - 更短 reference
      - 更弱 gain
      - 更低 cosine
      在当前
      `v65 sink`
      里，
      哪一项
      更接近
      真正主导因子
68. 已把 `train_001543` 的 `v65 sink` 分支对 `train_000664 / train_001745` 做成 factor contrast；当前分支图上的默认解释必须再收紧成“`reference` 最强，`overlap` 第二，`gain` 第三，`cosine` 应降级”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_factor_contrast.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_factor_contrast/summary.json`
  - 当前更关键的新事实是：
    - sink-specific residual
      排名前三位为：
      - `reference_duration_sec = 2.0673 z`
      - `interference_layers.0.start_offset_sec = 1.5845 z`
      - `interference_layers.0.gain_db = 1.2125 z`
    - `target_interference_logspec_cosine`
      只有：
      - `0.2609 z`
      应降格成：
      - 弱辅助信号
    - 双侧 transient share
      也更像：
      - post-entry shared package
      不是：
      - `v65 sink`
        主导 identity
  - 当前判断：
    - 若继续隔离
      `v65 sink`
      真主导，
      默认不再优先看：
      - `cosine`
    - 当前主候选
      应固定为：
      - `reference`
      - `overlap`
      - `gain`
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只拆：
      - `reference`
      - `start_offset`
      谁更接近
      `v65 sink`
      真主导；
      `gain`
      作为第三候选保留
69. 已把 `reference / overlap / gain` 在当前窄 ring 做成 target-side slice support；当前分支图上的默认解释必须再收紧成“真正把 `v65 sink` 与 `v64 pocket` 分开的不是 `overlap`，而是 `reference`，`gain` 次之”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_factor_slice_support.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_factor_slice_support/summary.json`
  - 当前更关键的新事实是：
    - `reference`
      的：
      - `contrast_on_target_side = false`
      说明
      `train_001745`
      没有和
      `train_001543`
      落到同一 sink-side；
      它是当前最干净的
      sink-vs-pocket
      分界
    - `start_offset`
      的：
      - `contrast_on_target_side = true`
      说明
      `train_001745`
      也会一起落到
      更早 overlap
      那一侧；
      它更像：
      - shared post-entry package
      不是：
      - 主分界
    - `gain`
      的：
      - `contrast_on_target_side = false`
      所以仍保留
      sink-specific
      区分力，
      但当前排位
      仍在
      `reference`
      之后
  - 当前判断：
    - `reference`
      应固定为当前：
      - `v65 sink`
        主分界
    - `gain`
      为第二候选
    - `overlap`
      退回：
      - shared post-entry package
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只拆：
      - `reference`
      - `gain`
      谁更接近
      `v65 sink`
      真主导
70. 已把 `v65 sink` 对 `reference+gain both` 象限里的唯一 hinge `train_000266` 做成局部 split；当前分支图上的默认解释必须再收紧成“`reference + gain` 更像 entry gate，而 hinge -> sink 的最后半步更像 `reference` 再缩短并叠加 target-side transient 抬升”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_reference_gain_hinge_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_vs_reference_gain_hinge/summary.json`
  - 当前更关键的新事实是：
    - `train_001543`
      相对
      `train_000266`
      的：
      - `gain = +0.059`
      基本不变，
      说明：
      - 弱 gain
        已更像
        entry gate
    - `reference = -0.27`
      继续更短；
      且：
      - `v66 - v64`
        额外下掉
        `0.024817 dB`
      - `v66 - v65`
        额外下掉
        `0.074139 dB`
    - `start_offset = +0.049`
      overlap
      反而略更晚，
      说明：
      - 更早 overlap
        不是当前
        hinge -> sink
        的最后主导步
    - 当前新增的
      更强局部信号
      是：
      - target transient
        明显抬升
  - 当前判断：
    - `reference + gain`
      应固定为：
      - `v65 sink`
        entry gate
    - `reference`
      再缩短
      + `target transient`
      抬升
      应固定为：
      - hinge -> sink
        当前最优候选
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只拆：
      - `reference`
      - `target transient`
      谁更接近
      `v65 sink`
      的最终主导
71. 已把 `reference+gain both` 象限继续拆成 sink / hinge / pre，并补出 `reference+gain` 四象限；当前分支图上的默认解释必须再收紧成“`reference+gain` 是 conjunction entry gate，而 gate 内更稳定的 final push 已经更偏向 `target transient`”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_reference_vs_target_transient_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_gain_quadrants/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_reference_vs_target_transient_split/summary.json`
  - 当前更关键的新事实是：
    - `train_001543`
      在：
      - `reference+gain both`
      而
      `train_001745`
      与
      `train_000664`
      都在：
      - `neither`
      说明：
      - `reference+gain`
        是当前
        conjunction gate
    - gate 内部，
      `sink - both_pre`
      与
      `sink - both_nonsink`
      都显示：
      - `reference`
        只小幅继续变化
      - 但
        `target transient`
        仍稳定上升
      说明：
      - `target transient`
        更像
        gate 内 final push
    - `reference`
      仍然能解释：
      - `hinge -> sink`
      这一条局部边界，
      但不再适合写成：
      - gate 内
        统一第一分界
  - 当前判断：
    - `reference+gain`
      应固定为：
      - `v65 sink`
        conjunction entry gate
    - `target transient`
      应固定为：
      - gate 内
        更稳定的
        final push
    - `reference`
      退回：
      - hinge -> sink
        局部补刀
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只拆：
      - `target transient mean`
      - `target transient share`
      谁更接近
      `v65 sink`
      的最终主导
72. 已把 gate 内的 `target transient` 再拆成 `mean` vs `share`；当前分支图上的默认解释必须再收紧成“`mean` 已正式超过 `share`，成为当前 `v65 sink` 的最终主导候选”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_target_transient_mean_vs_share.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_factor_contrast/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_slice_support/summary.json`
  - 当前更关键的新事实是：
    - gate 内 factor contrast
      排序为：
      - `target_transient_mean = 1.2788 z`
      - `target_transient_share = 1.0665 z`
      说明：
      - `mean`
        已超过
        `share`
    - slice support
      里：
      - `mean`
        和
        `share`
        都能挡住
        hinge anchor
        `train_000266`
      - 但
        `share`
        会额外吸进：
        - `train_000210`
          这条
          `v64_only`
          旁支
      - `mean`
        没有这层污染
  - 当前判断：
    - `target transient mean`
      应固定为当前：
      - `v65 sink`
        final push
        主导候选
    - `target transient share`
      退回：
      - 辅助项
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只围绕：
      - `target transient mean`
      做更细支持复核
73. 已把 gate 内 `target transient mean` 与 `share` 的 slice support 正式核到当前窄 ring；当前分支图上的默认解释必须再收紧成“`mean` 不仅更强，而且更干净，`share` 会额外误吸 `v64_only` 旁支”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_target_transient_mean_vs_share.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_factor_contrast/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_target_transient_slice_support/summary.json`
  - 当前更关键的新事实是：
    - `target transient mean`
      的：
      - residual z = 1.2788
      高于
      `share = 1.0665`
    - `mean`
      与
      `share`
      都能挡住
      hinge anchor
      `train_000266`
    - 但
      `share`
      会额外吸进：
      - `train_000210`
        这条
        `v64_only`
        旁支；
      `mean`
      没有这层污染
  - 当前判断：
    - `target transient mean`
      应固定为当前：
      - `v65 sink`
        final push
        主导候选
    - `target transient share`
      退回：
      - 辅助项
      且带有
      旁支污染风险
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只围绕：
      - `target transient mean`
      做更细支持结构复核

74. 已把 gate 内 `target transient mean` 再对 `reference` 与 `gain` 做成局部 partner split；当前分支图上的默认解释必须再收紧成“`mean+gain` 才是当前窄 ring 里最干净的 sink carve，而 `reference` 退回上游 entry 描述”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_mean_gate_partner_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_reference_quadrants/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_gain_quadrants/summary.json`
  - 当前更关键的新事实是：
    - `mean + reference`
      的
      `both`
      桶里仍有：
      - `1` 条 sink
      - `5` 条 pre
      说明：
      - `reference`
        还不能把
        当前窄 ring
        切干净
    - `mean + gain`
      的
      `both`
      桶则只剩：
      - `train_001543`
      本人；
      而：
      - `train_000266`
        仍在
        `factor_b_only`
      说明：
      - `weak gain`
        单独不够，
        但和
        `mean`
        合在一起
        已经形成
        sink-only carve
  - 当前判断：
    - `reference+gain`
      继续保留为：
      - 上游
        entry gate
    - 但当前最窄的
      局部 carve
      应改写成：
      - `target transient mean + weak gain`
    - `reference`
      不再写成：
      - 和 `gain`
        对
        `mean`
        同级有效的
        本地 partner
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只看：
      - `train_000266 / train_001589 / train_001543`
      解释为什么它们都已经落到
      `weak gain`
      一侧，
      但只有
      `train_001543`
      还能再被
      `mean`
      推成 sink

75. 已把 `train_000266 / train_001589 / train_001543` 压成 weak-gain 壳内 split；当前分支图上的默认解释必须再收紧成“在 weak-gain 壳内，`gain` 已经只是外壳，真正把 hinge 推成 sink 的第一主轴仍是 `target transient mean`”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_weak_gain_hinge_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_weak_gain_hinge_split/summary.json`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_hinge_train.txt`
  - 当前更关键的新事实是：
    - `v65_sink - weak_gain_hinge`
      的：
      - `gain = +0.083`
      - `start_offset = +0.090 sec`
      说明：
      - sink
        既不是靠
        更弱 gain
      - 也不是靠
        更早 overlap
        才进入 sink
    - 壳内最大的
      target-side
      变化是：
      - `target transient mean = +4.6522`
      - `target transient share = +0.05677`
    - 与此同时，
      margin
      也继续塌成：
      - `v66-v64 = -0.0364 dB`
      - `v66-v65 = -0.0673 dB`
      说明：
      - weak-gain hinge
        已经先有
        `v66 < v65`
      - 但只有
        `mean`
        继续抬升，
        才会把
        `v66 > v64`
        一起拖负
    - `train_001589`
      当前应固定写成：
      - weak-gain shell
        内部
        `partial mean rise`
        的 hinge
  - 当前判断：
    - `gain`
      在 weak-gain 壳内
      已经不能再写成
      final push
    - 当前壳内主导
      应固定为：
      - `target transient mean`
    - `train_000266`
      更像：
      - weak-gain hinge
        floor
    - `train_001589`
      更像：
      - weak-gain hinge
        near-sink step
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只看：
      - `train_001589`
      - `train_001543`
      解释为什么
      `001589`
      已经出现
      partial mean rise，
      却还没跨过
      最后那条
      sink 边界

76. 已把 `train_001589 / train_001543` 压成 partial-mean hinge one-to-one split；当前分支图上的默认解释必须再收紧成“`001589` 已经在壳内，但它仍是带着长 duration / 高 cosine 的 near-sink hinge，最后没跨过去的边界不再是 gain，而是 `mean` 对 `duration/cosine` 的竞态”：
  - 入口：
    - `reports/daily/2026-03-23_candidate_v7_v65_sink_partial_mean_hinge_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_vs_partial_mean_hinge/summary.json`
    - `data/synthetic/sample_ids_friend_speech_leak_proxy_search_candidate_v7_active_targetfull_clean_failboth_weak_gain_partial_mean_hinge_train.txt`
  - 当前更关键的新事实是：
    - `v65_sink - weak_gain_partial_mean_hinge`
      的：
      - `target transient mean = +3.3921`
      - `target transient share = +0.056997`
      说明：
      - `001589`
        已是
        partial mean rise
        hinge
      - 但还没到
        sink
        那一档
    - 同时：
      - `gain = +0.107`
      - `start_offset = +0.131 sec`
      仍说明：
      - 这一步
        不是
        更弱 gain
      - 也不是
        更早 overlap
        在主导
    - `v66-v64`
      还需要再掉：
      - `0.0480 dB`
      才会从
      `+0.0392`
      变成
      `-0.0088`
    - 而且
      `001589`
      仍带着：
      - 更长 target/reference
      - 更高 cosine
        的 near-sink hinge 壳
  - 当前判断：
    - `train_001589`
      不再写成：
      - 壳外 hinge
    - 应固定写成：
      - weak-gain shell
        内部
        partial mean rise
        near-sink hinge
    - 当前最后那条边界
      应改写成：
      - `mean`
        还没抬够
      与
      - duration / cosine
        壳
        谁在托住
        `v64 buffer`
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只拆：
      - `mean`
      对
      - `duration / cosine`
      看
      `001589`
      为什么没跨进
      sink

77. 已把 `001589 -> 001543` 的最后边界继续拆成 `mean / duration / cosine`；当前分支图上的默认解释必须再收紧成“near-sink 最后托住 `001589` 的更像 duration shell，cosine 次之，而不是再把问题写回单纯 `mean` 不够”：
  - 入口：
    - `reports/daily/2026-03-24_candidate_v7_v65_sink_partial_mean_duration_cosine_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_hinge_ladder_split/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_partial_mean_edge_factor_contrast/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_partial_mean_edge_slice_support/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_targetduration_quadrants/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_mean_cosine_quadrants/summary.json`
  - 当前更关键的新事实是：
    - 按当前窄 ring
      标准化 residual，
      `001543 - 001589`
      这一步里：
      - `reference_duration = 3.3076 z`
      - `target_duration = 2.2258 z`
      - `cosine = 1.6606 z`
      - `mean = 0.7337 z`
    - 但：
      - `reference`
        的
        `contrast_on_target_side = true`
      说明：
      - `000266`
        已经落在
        短 reference
        那一侧
      所以它不是
      最后边界
    - `target_duration`
      与
      `cosine`
      都满足：
      - `contrast_on_target_side = false`
      说明：
      - 这两项
        还在真正挡住
        floor hinge
    - 两组 quadrants
      进一步说明：
      - `mean + target_duration`
        和
        `mean + cosine`
        都能把
        `001589`
        与
        `000266`
        留在
        `neither`
      - 但两者的
        `both`
        桶仍混着
        大量 pre
      所以：
      - `target_duration`
        更强
      - `cosine`
        更干净
      - 但都不是
        独立 hard gate
  - 当前判断：
    - `train_001589`
      最后没跨进 sink，
      当前更像：
      - 长 target duration
        壳
      辅以：
      - 高 cosine
        约束
    - `mean`
      继续保留为：
      - 必要条件
      但不再单独承担
      最后边界主语
    - `reference`
      不再抬回
      最后主语
  - 当前默认下一步：
    - 不再扩样本面
    - 若继续推进，
      默认只拆：
      - `target_duration`
      对
      - `cosine`
      看哪一项更接近
      `001589`
      没跨进 sink
      的最终主导

78. 已把 `target_duration` 对 `cosine` 正式压成 focused split；当前分支图上的默认解释必须再收紧成“`duration` 仍是 near-sink 主 blocker，`cosine` 退回 duration shell 上的 secondary trim，不再把两者并列成同级主语”：
  - 入口：
    - `reports/daily/2026-03-24_candidate_v7_v65_sink_duration_vs_cosine_split.md`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_slice_support/summary.json`
    - `reports/eval/active_targetfull_clean_failboth_v65_sink_duration_cosine_quadrants/summary.json`
  - 当前更关键的新事实是：
    - `target_duration`
      的 target-side
      为：
      - `1` 条 sink
      - `2` 条 hinge
      - `2` 条 `v64_only`
      - `17` 条 pre
    - `cosine`
      的 target-side
      为：
      - `1` 条 sink
      - `2` 条 hinge
      - `2` 条 `v64_only`
      - `13` 条 pre
      说明：
      - `cosine`
        确实更干净，
        但两者保住的
        boundary-support rows
        是同一批
    - 真正更能把
      `001589`
      与
      `000266`
      拉开的，
      仍是：
      - `duration`
      因为：
      - `target_duration`
        midpoint
        为 `1.71 sec`
      - `001589`
        离 target-side
        还差：
        - `0.57 sec`
      - `000266`
        只差：
        - `0.03 sec`
      - gap 差为：
        - `0.54 sec`
      而：
      - `cosine`
        这组
        只有：
        - `0.053765`
        对
        - `0.041001`
        的窄差
    - quadrants
      进一步说明：
      - `both = 1 sink + 2 hinge + 2 v64_only + 11 pre`
      - `duration-only = 6 pre`
      - `cosine-only = 2 pre`
      - `neither = 2 hinge + 1 pre`
      也就是：
      - 真正贴边的 rows
        没有任何一条
        落在
        `duration-only`
        或
        `cosine-only`
  - 当前判断：
    - `target_duration`
      应固定为：
      - 当前 near-sink
        主 blocker
    - `cosine`
      应固定为：
      - duration shell
        上的
        secondary trim
    - `duration + cosine`
      应固定为：
      - boundary-support shell
      但还不是
      final hard gate
  - 当前默认下一步：
    - 不再扩样本面
    - 不再继续问：
      - `duration`
      还是
      - `cosine`
    - 若继续推进，
      默认只看：
      - `duration + cosine both`
        这层 shell
        内部
        为什么还残留
        大量 pre
      - 也就是
        回到：
        - `mean`
        作为 shell 内
        final push

## 6. 忘线检查表

每次恢复上下文前，先看这 5 个入口：

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. 本文档 `docs/05_task_branch_map.md`
5. 当前活跃分支日报：
   - 现在补到：
     - `reports/daily/2026-03-21_candidate_v7_failboth_pure_v67_takeover_case_diagnosis.md`
     - `reports/daily/2026-03-21_candidate_v7_failboth_nearshell_case_diagnosis.md`
     - `reports/daily/2026-03-21_candidate_v7_failboth_borderline_case_split.md`
     - `reports/daily/2026-03-21_candidate_v7_failboth_single_trigger_scan.md`
     - `reports/daily/2026-03-21_candidate_v7_failboth_v66_vs_v67_split.md`
     - `reports/daily/2026-03-21_candidate_v7_active_guardpair_bucketization.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_dualleak_shell_neighbor_drift.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_targetfull_clean_dualleak_shell.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_core_trio.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_targetfull_split.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_neighbor_behavior_probe.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
     - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
     - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
     - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
     - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
     - `reports/daily/2026-03-21_candidate_v6_pure_negative_expand.md`
     - `reports/daily/2026-03-21_proxy_subfamily_materialization.md`
     - `reports/daily/2026-03-21_candidate_v4_v5_overlap_analysis.md`
     - `reports/daily/2026-03-21_candidate_v5_guardv67_negative_materialization.md`
     - `reports/daily/2026-03-21_candidate_v4_subgroup_diagnosis.md`
   - 当前主停点日报已更新为：
     - `reports/daily/2026-03-24_candidate_v7_v65_sink_duration_vs_cosine_split.md`
   - 上一条主停点日报：
     - `reports/daily/2026-03-24_candidate_v7_v65_sink_partial_mean_duration_cosine_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_post_entry_depth_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_margin_order_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_margin_first_transition_axes.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_lowbuffer_edge_positioning.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_neighbor_buffer_collapse_diagnosis.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_neighbor_ring_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-23_candidate_v7_pure_v67_neighbor_diagnosis.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_failboth_pure_v67_takeover_case_diagnosis.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_failboth_nearshell_case_diagnosis.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_failboth_borderline_case_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_failboth_single_trigger_scan.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_failboth_v66_vs_v67_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_active_guardpair_bucketization.md`
   - 更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_dualleak_shell_neighbor_drift.md`
   - 更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_targetfull_clean_dualleak_shell.md`
   - 更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_core_trio.md`
   - 更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_microbuffer_targetfull_split.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_active_neighbor_behavior_probe.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`
   - 更更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_guardv65_relaxed_bridge_search.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_strictcore_nearmiss_frontier.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_strictcore_asset_and_overlap.md`
   - 更更更早一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_strictall_core_search.md`
   - 更更早一条主停点日报：
     - `reports/daily/2026-03-21_v67_candidate_v4_union_followup.md`
   - 上一条 `candidate_v4` 搜索日报：
     - `reports/daily/2026-03-21_candidate_v4_guardv66_by_v64_search_followup.md`
   - 上一条 `v66` 定向诊断日报：
     - `reports/daily/2026-03-20_v66_candidate_v3_direction_diagnosis.md`
   - `candidate_v3` 搜索日报：
     - `reports/daily/2026-03-20_friend_speech_leak_search_manifest_v1.md`
   - 上一条 `branch_protect` 资产日报：
     - `reports/daily/2026-03-20_branch_protect_selector_asset_builder.md`
   - `v64 / v65` 恢复日报：
     - `reports/daily/2026-03-20_v64_v65_dualprotect_recovery.md`
   - `v63` 主日报：
     - `reports/daily/2026-03-20_v63_dualdecoder_targetfull_basealign_branchprotect_followup.md`
   - `v63` 旧启动清单：
     - `reports/daily/2026-03-20_v63_written_spec_no_run.md`

每次准备开新分支前，至少回答：

1. 这条分支是新 coverage，还是旧 rows 重路由？
2. 会不会再次误命中 `interference_extra` exact family？
3. 计划跑完后用哪份 gate 判 keep / drop？
