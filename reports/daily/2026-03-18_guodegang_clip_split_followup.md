# 2026-03-18 guodegang clip split follow-up

## 背景

上一轮 `v11` 已经把问题进一步收紧到一句话：

- `0003 / 0004` 继续变强
- 但真实 `guodegang / 0006` 相对 `v8` 继续明显回退

同时 `v11` 的 clip 级 summary 还暴露出一个更细的信号：

- `guodegang_absent_480s` 相对 `legacy_stage2` 仍是正增益
- `guodegang_anchor_120s` 相对 `legacy_stage2` 已变成负增益

因此本轮目标不是继续开训练，而是先确认：

- `0006` 是不是已经拆成两个不同子问题
- synthetic proxy 是否也必须跟着拆成两条

## 本轮新增

### 1. `0006` clip 级子 probe

基于：

- `data/probes/near_real_guodegang_transient_probe_v1_manifest.jsonl`

物化出两条更细子 probe：

- `data/probes/near_real_guodegang_anchor_probe_v1_manifest.jsonl = 3`
  - 全部为 `guodegang_anchor_120s`
- `data/probes/near_real_guodegang_absent_probe_v1_manifest.jsonl = 3`
  - 全部为 `guodegang_absent_480s`

### 2. `clip-tag` 级 focused guardrail

已扩展：

- `scripts/eval/gate_probe_subset_guardrail.py`

新增参数：

- `--clip-tags`

现在同一条 focused guardrail 可以同时检查：

- overall
- family
- anchor
- `speech_clip_tag`

## near-real clip 级排序

### A. `guodegang_anchor_120s`

相对 `legacy_stage2`：

- `v7 = +0.386009 dB`
- `v8 = -0.015205 dB`
- `v10 = -0.292184 dB`
- `v11 = -0.412207 dB`

当前排序：

- `v7 > v8 > v10 > v11`

解释：

- `anchor_120s` 这条线里，`v7` 其实是当前最佳版本
- `v8` 只是不像 `v10 / v11` 那么差
- 所以把 `v8` 当成 `0006` 全问题的统一基座，本身已经有损失

### B. `guodegang_absent_480s`

相对 `legacy_stage2`：

- `v8 = +2.135139 dB`
- `v7 = +1.932071 dB`
- `v10 = +1.576052 dB`
- `v11 = +1.228311 dB`

当前排序：

- `v8 > v7 > v10 > v11`

解释：

- `absent_480s` 与 `anchor_120s` 的排序是反过来的
- 也就是说，真实 `0006` 已经不是单一 objective target

## 对 `v8` 的 clip 级 guardrail

### `v7` 相对 `v8`

- 输出：
  - `reports/eval/compare_stage2_vs_legacy_transient_leakguard_probe_v7_v3_speech_absentguard_w2_ft1_on_near_real_guodegang_transient_probe_v1/near_real_speech_probe_analysis/probe_subset_guardrail_vs_v8_with_clips.json`

结果：

- `FAIL`

唯一失败项：

- `clip__guodegang_absent_480s`

解释：

- `v7` 并不是“整体输给 `v8`”
- 它只输在：
  - `absent_480s`
- 同时它仍保住了：
  - `guodegang_anchor_120s`

### `v10` / `v11` 相对 `v8`

输出：

- `.../probe_subset_guardrail_vs_v8_with_clips.json`

结果都为：

- `FAIL`

失败项包括：

- `overall_floor`
- `family__guodegang_raw`
- `anchor__near_real_0006`
- `clip__guodegang_anchor_120s`
- `clip__guodegang_absent_480s`

解释：

- `v10 / v11` 不是只在某一个 clip 上偏了
- 它们是两个 clip 都一起输给 `v8`

## synthetic proxy 搜索

### A. `anchor` 方向

搜索目标：

- `v7 > v8 > v10 > v11`

输出：

- `reports/eval/synthetic_proxy_search_guodegang_anchor_v7_v8_v10_v11_on_default/summary.json`

当前最稳定的 order-pass 子集集中在：

- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`

更强、更干净的可解释子集是：

- `target_clean_speech`
- `speech_interference_clean_pool`
- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`

已物化为：

- `data/synthetic/train_manifest_guodegang_anchor_proxy_v1.jsonl = 84`
- `data/synthetic/val_manifest_guodegang_anchor_proxy_v1.jsonl = 22`

并已确认在 compare 上复现：

- `v7 > v8 > v10 > v11`

### B. `absent` 方向

搜索目标：

- `v8 > v7 > v10 > v11`

输出：

- `reports/eval/synthetic_proxy_search_guodegang_absent_v8_v7_v10_v11_on_default/summary.json`

当前只有很少的 order-pass 子集，核心共性是：

- `target_full`
- `target_present_ratio >= 0.95`
- `overlap >= 0.9`
- `target_transient_presence_minus_mid_db_mean >= q50`
- 仍然限定在 speech rows

先前如果直接把这条 proxy 广义物化成：

- 包含 `music / singing`

则排序会立刻偏回：

- `v7 > v8 > v10 > v11`

说明这个 absent proxy 的 `speech-only` 边界是硬要求，不是可选项。

因此最终保留的是：

- `data/synthetic/train_manifest_guodegang_absent_proxy_v2_speechonly.jsonl = 76`
- `data/synthetic/val_manifest_guodegang_absent_proxy_v2_speechonly.jsonl = 20`

它已成功复现：

- `v8 > v7 > v10 > v11`

## 当前结论

1. `near_real_0006` 现在应被视为两个子问题，而不是一条统一 guardrail：
   - `guodegang_anchor_120s`
   - `guodegang_absent_480s`
2. 这两个子问题的真实排序已经明确冲突：
   - `anchor` 更像 `v7`
   - `absent` 更像 `v8`
3. 因而任何继续声称“我在补 `0006`”的后续版本，都必须至少同时说明：
   - 它更接近哪一条 clip 级排序
   - 它是否在另一条 clip 上付出了代价
4. synthetic 侧也必须跟着拆成两条 proxy：
   - `guodegang_anchor_proxy_v1`
   - `guodegang_absent_proxy_v2_speechonly`
5. `absent` proxy 的一个新坑已经被确认：
   - 一旦把 `music / singing` 混进来，排序就会漂掉
   - 所以这条 proxy 必须保持 speech-only 边界

## 对下一步的影响

1. 当前不要继续把 `0006` 当成单条 proxy 做统一 focused 微调。
2. 若继续自动推进，下一步更合理的入口应是：
   - 以 `v8` 为 broad speech 基座
   - 明确加一个 `anchor_120s` 方向的独立 guardrail
   - 而不是再做更宽的 `guodegang` 混合微调
3. 更直白地说：
   - 现在不是“再找一个更像 `0006` 的总 proxy”
   - 而是要先承认 `0006` 本身已经分裂成两种互相拉扯的优化目标

## 验证

- 已生成：
  - `near_real_guodegang_anchor_probe_v1_manifest.jsonl`
  - `near_real_guodegang_absent_probe_v1_manifest.jsonl`
  - `train/val_manifest_guodegang_anchor_proxy_v1.jsonl`
  - `train/val_manifest_guodegang_absent_proxy_v2_speechonly.jsonl`
- 已完成 compare：
  - `stage2 vs v7/v8/v10/v11` on anchor sub-probe
  - `stage2 vs v7/v8/v10/v11` on absent sub-probe
  - `stage2 vs v7/v8/v10/v11` on anchor/absent synthetic proxies
- 已完成：
  - `gate_probe_subset_guardrail.py` with `--clip-tags`
  - `search_synthetic_proxy_candidates.py` for anchor / absent split
