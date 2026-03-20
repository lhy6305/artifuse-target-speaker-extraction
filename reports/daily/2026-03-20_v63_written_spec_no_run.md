# 2026-03-20 `v63` 书面启动规格（未执行）

## 后续状态

该书面规格后续已被实际执行。

执行结果见：

- `reports/daily/2026-03-20_v63_dualdecoder_targetfull_basealign_branchprotect_followup.md`

当前 `v63`
不再是 `written_only`，
而是已关闭实验。

## 目的

把当前唯一保留的下一条 dual-head follow-up
补成“可执行但未执行”的正式资产，
避免后续再次靠口头恢复：

- 明确第二条 protect selector 的正式文件路径；
- 明确 `v63` 的启动清单；
- 明确它当前仍处于
  `written_only / do_not_run`
  状态。

## 正式 selector 资产

### protect A: `target_full`-only `base-align`

- `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_train.txt`
- `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_val.txt`
- `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt`

### protect B: `exact_nontargetfull` (`exact_all - exact_targetfull_all`)

已正式物化：

- `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_nontargetfull_train.txt`
- `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_nontargetfull_val.txt`
- `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_nontargetfull_all.txt`

对应当前 ids：

- train
  - `train_000405`
  - `train_001279`
  - `train_001491`
- val
  - `val_000096`
  - `val_000297`

当前解释：

- 这不是“已经证明的最终 `0004-like` 真值集合”；
- 而是当前最保守、最可复现的第二 selector 候选；
- 它只表达：
  - `exact family` 内
  - 非 `target_full`
  的那一侧保护需求。

## `v63` 启动清单

### 训练定义

- 名义方案：
  - `v63 = dual-head + proxy_v7 reconstruction + target_full-only base-align + exact_nontargetfull branch_protect guard`
- warm-start：
  - `v32`
- 结构前提：
  - `enable_branch_decoder_head = true`
- protect A：
  - 沿用 `v61` 证明有效的
    `target_full`-only `base-align`
- protect B：
  - 使用独立 `branch_protect` selector
  - `focus_sample_ids_file`
    指向：
    - `data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_nontargetfull_all.txt`

### 评估与裁决口径

若后续获准启动，
仍必须按当前既有口径完整走：

- default eval
- exact eval
- near-real / speech probe
- `guodegang`
- `friend_speech_leak_followup_gate`

### 禁止事项

当前这份文档只提供启动规格，
不代表批准执行。

本次明确不做：

- 新训练
- 新 eval
- 新 compare
- 新 gate
- 新 checkpoint

## 当前状态标签

- `legacy stage2 = mainline_keep`
- `v19 / v32 / proxy_v7 = research_base_keep`
- `v57 / v58 = closed_but_evidence_keep`
- `v54 / v55 / v59 / v60 = closed_failed`
- `v63 = historical_spec_only; executed_later_and_closed_failed`
