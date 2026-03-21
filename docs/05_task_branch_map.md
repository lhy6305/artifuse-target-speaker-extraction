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

## 6. 忘线检查表

每次恢复上下文前，先看这 5 个入口：

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. 本文档 `docs/05_task_branch_map.md`
5. 当前活跃分支日报：
   - 现在补到：
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
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_trio_softseed_probe.md`
   - 上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seedplusone_signature_split.md`
   - 再上一条主停点日报：
     - `reports/daily/2026-03-21_candidate_v7_bridgepair_seed_expansion.md`
   - 更早一条主停点日报：
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
