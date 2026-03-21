# 踩坑记录 历史归档 31-40

- 源文档：
  - `docs/02_pitfalls_log.md`
- 条目范围：
  - `31-40`

## 2026-03-16

### 31. 即使 recipe 配额相同，focused manifest 的 temporal pattern 分布变化也足以显著改变结果

现象：

- 当前 `regression_focus_v1` 与 `recipe_focus_v2` 的 recipe 总配额都为 `364` 条，且各 recipe 数量对齐。
- 但两者的 temporal pattern 分布并不相同。
- 在保持相同 warm-start 和训练预算的前提下，`ft2` 相对 `ft1` 的表现出现了明显变化：
  - overall `sisdr_db` 更好
  - `clean_plus_music` 更好
  - `hard_speech` 副作用更小

影响：

- 说明 focused 实验里，不能把“recipe 配比”当成唯一主变量。
- 即使 recipe 数量完全一样，sample 级别的时序结构分布不同，也会把结果推到另一边。

处理：

- 已把 `recipe_focus_v2` 和对应 `ft2` 结果登记为正式日报与总览。

后续要求：

1. 以后描述 focused manifest 时，至少同时记录：
   - recipe 分布
   - temporal pattern 分布
2. 不要只写“这是 clean_plus_music focus”，否则信息不够，容易误判实验变量。

### 32. 到了近邻微调后期，只看均值小涨就继续开新分支，很容易进入“平台区假进步”

现象：

- 在 `ft2` 之后，又做了一轮更保守的 `ft3`。
- `ft3` 的整体均值确实比 `ft2` 略好：
  - `sisdr_db`: `-7.947635 -> -7.926801`
- 但逐样本对比只有：
  - improved: `114`
  - regressed: `105`

影响：

- 这类结果说明模型可能已经进入平台区附近。
- 如果继续只因为“均值又涨了一点点”就往下开 `ft4 / ft5`，很容易把实验树越开越长，但结论并不变硬。

处理：

- 已把 `ft3` 记录为可保留但不主推的近邻点。

后续要求：

1. 近邻微调若没有形成更明显的分布支配关系，应优先停下来，转向听感验证。
2. 不要把“均值略涨”自动等同于“值得继续往下滚很多版”。

### 33. blind 听评如果没有结构化标签，后续很难把主观反馈和模型问题类型对齐

现象：

- 早期 blind 包中的 `listening_sheet.csv` 更偏自由备注。
- 这样虽然能记录主观看法，但很容易出现：
  - 描述词不统一
  - 同一问题被不同说法重复表述
  - 后续难以统计“到底是源保留差，还是干扰泄漏高，还是伪影重”

影响：

- 主观反馈会变得零散，难以和后续模型迭代形成闭环。

处理：

- 已把 blind 听评标准改成：
  - `better_output`
  - `source_retention`
  - `interference_leak`
  - `volume_fluctuation`
  - `artifact`
  - `decision_tags`
- 并同步更新了导出脚本。

后续要求：

1. 后面新的 blind 包，统一使用这套结构化表。
2. 若旧包还需要继续听，建议也优先重新导出成新格式，避免混用两套记录口径。

### 34. blind 包里其实已经带有真实模型标签，GUI 若直接读 `summary.json` 会破坏盲测

现象：

- 当前 blind listening pack 虽然把音频文件导出成了 `candidate_a.wav / candidate_b.wav`。
- 但同目录下的 `summary.json` 仍然记录了：
  - `label_a`
  - `label_b`
  - checkpoint 路径
  - 每条样本的真实 comparison 字段

影响：

- 如果后续写 GUI 或其他辅助工具时，直接把 `summary.json` 当作主界面数据源，就会在 blind 听评时意外看到真实身份。
- 这样看起来“文件名是盲的”，实际上流程已经不盲了。

处理：

- 本轮新增的 `scripts/eval/listening_pack_gui.py` 默认只读取：
  - `listening_sheet.csv`
  - `listening_rubric.json`
  - 样本目录中的音频文件
- 不把 `summary.json` 的真实标签直接展示到界面里。

后续要求：

1. 后面凡是 blind 包消费工具，都优先走 `listening_sheet.csv` 这条盲态入口。
2. 若确实需要解盲，应显式点击或单独走解盲流程，不要和评分界面混在一起。

### 35. 听评 GUI 里的“峰值统一拉伸”如果按单文件分别执行，会悄悄改掉 A/B 的真实相对差异

现象：

- 在 `scripts/eval/listening_pack_gui.py` 的早期实现中，播放选项里的归一化逻辑是：
  - 先读取当前单个文件
  - 再把这个文件自己的峰值单独拉到目标值
- 这和实际盲听想要的口径不一致。

影响：

- 同一样本中的：
  - `candidate_a`
  - `candidate_b`
  - `mixture`
  - `target`
  - `reference`
  之间，本来应该保留的相对响度和抑制强弱差异，会被单文件拉伸部分抹平。
- 这样更容易出现：
  - “A/B 听起来差不多”
  - 或“某条本来更安静但也更薄的输出，被拉高后显得没那么弱”

处理：

- 已将 GUI 修正为：
  - 同一样本目录内共用一个播放增益
  - 该增益按整组文件中的最大峰值计算
- 这与导包脚本里“同一样本共享导出增益”的思路保持一致。

后续要求：

1. 后面凡是再做关键样本复核，优先使用修正后的“同一样本共享增益”口径。
2. 对此前在旧口径下得到的主观结论，尤其是“谁更稳 / 谁泄漏更重 / 谁波动更明显”这类细判断，要保留一点谨慎。

### 36. 少量 synthetic 听评样本的 `target.wav` 本身可能带有门限式截断痕迹，会污染主观判断

现象：

- 在复核 `clean_plus_music` focused 包时，用户明确指出：
  - `val_000036`
  - `val_000454`
  的 `target.wav` 中间疑似存在门限截断和放开瞬间的明显跳变。

影响：

- 这类样本即使 A/B 本身没有明显差异，也会因为 target 真值本身不自然，降低整条样本的可判性。
- 若不单独标记，后续很容易把“样本本身难评”误判成“模型完全没差异”。

处理：

- 已将这两条样本视作“可参考但带评估噪声”的样本，不再把它们当作最干净的主观证据。

后续要求：

1. 后续若继续做关键样本复核，优先记录这类“样本本身有问题”的备注。
2. 若类似现象继续出现，应回查 synthetic 生成逻辑，而不是只盯模型输出。

### 37. Git 状态和磁盘文档如果不一起维护，很容易出现“仓库已变化但总览仍停在旧时点”

现象：

- 本轮恢复时，Git 真实状态已经存在提交历史，`HEAD` 也已有具体 commit。
- 但总览、踩坑和日报中的部分表述仍停留在：
  - “当前仓库尚无任何提交”
  - “当前仓库还没有任何提交历史”

影响：

- 下次接手的人如果只看文档，不看 Git 事实，很容易误判当前仓库阶段。
- 这种偏差虽然不影响训练代码本身，却会让“当前该做文档修正还是做新实验”这个判断顺序变乱。

处理：

- 已将核心文档中的 Git 事实更新为当前状态。
- 已明确补充协作边界：
  - Git 由用户手动维护提交记录；
  - 助手只把 Git 当作状态核对和恢复辅助工具。

后续要求：

1. 以后只要引用 Git 状态，尽量写成“当前观察事实”，不要把某一时刻的临时状态写成长期结论。
2. 每次恢复上下文时，除读文档外，至少补看一次：
   - `git status --short`
   - `git log --oneline -n 3`
3. 若文档中的 Git 表述已过期，应优先修正文档，再继续推进其他任务。

### 38. 客观上大幅领先的候选，不等于修正后 GUI 口径下也会被人耳稳定选中

现象：

- `ref_film + stft0.5 + sisdr0.0005` 在客观指标上曾一度收敛为当前最强候选。
- 但在 `legacy stage2 vs ref_film_sisdr0005` 的 blind A/B 主观复核里，解盲后结果为：
  - `legacy_stage2`: `7`
  - `ref_film_sisdr0005`: `1`
  - `tie`: `1`
  - `uncertain`: `3`

影响：

- 说明当前这类 synthetic 客观增益，还不能直接等价理解成“耳朵会更喜欢”。
- 如果只因为客观指标领先就替换默认主线，实际很可能把一个“更激进但不够稳”的模型推到前面。

处理：

- 已将默认主线保持为 `legacy stage2`。
- `ref_film_sisdr0005` 当前改回：
  - 客观候选分支
  - 听评和真实验证对照分支

后续要求：

1. 后面凡是“客观上更强但主观未过关”的候选，都不要直接升默认主线。
2. 若想继续推进这类候选，优先补：
   - 更真实样本
   - 或更聚焦的不确定样本复核
3. 结论里要明确区分：
   - 客观最优候选
   - 当前默认主线

### 39. 评估与听评导出若把仓库内路径写成绝对路径，工作目录一改名就会产生恢复噪声

现象：

- 当前恢复时发现，多份导出产物仍写着旧工作目录：
  - `reports/eval/*/listening_results_summary.json` 的 `pack_dir`
  - `reports/eval/compare_*/summary.json`
  - `reports/eval/compare_*/per_sample_metrics.jsonl` 的 `metadata_path`
- 这些文件本身还在，但文本里记录的路径已经漂到旧目录名 `workdir-4-1`。

影响：

- 下次接手的人如果只看报告 JSON，很容易误以为当前产物放在旧目录，增加恢复噪声。
- 这类问题和代码逻辑无关，但会直接削弱“看报告就能恢复上下文”的可靠性。

处理：

- 已将后续默认口径改为：
  - 仓库内路径优先写仓库相对路径
  - 仅在仓库外路径无法相对化时，才回退为绝对路径
- 已修正：
  - `SyntheticTSEDataset`
  - `scripts/eval/listening_pack_gui.py`
  - `scripts/eval/compare_checkpoints_on_manifest.py`
  - `scripts/eval/export_ab_listening_pack.py`
  - `scripts/eval/export_ab_inference_from_manifest.py`
  - `scripts/eval/eval_stft_mask_baseline.py`
  - `scripts/train/train_stft_mask_baseline.py`
  - `scripts/data/build_recipe_focused_manifest.py`

后续要求：

1. 以后新增报告 JSON 时，仓库内路径默认不要直接写 `str(path.resolve())`。
2. 若历史产物里仍保留旧绝对路径，应把它视为“历史记录字段”，不要当作当前真实路径来源。

### 40. 当前训练分布仍缺少混响 / RIR realism，near-real 一上轻微混响就更容易暴露“伪影像目标”的问题

现象：

- 设计稿里早就把：
  - 轻混响
  - RIR 卷积
  写成了后续 realism 增强项。
- 但当前代码实现中，还没有真正落地这类增强。
- 在 `near_real_v1` blind 听评里，用户新给出的主观判断是：
  - 对输入的混响处理存在问题；
  - 有可能将处理中间过程产生的伪影误当作目标音频。
- 这条判断在样本级上也有支撑：
  - `near_real_0008`
  - `near_real_0010`
  的 target absent 场景中，A/B 都出现了目标样瞬态；
  - `near_real_0009` 的轻微混响说话素材中，两边都出现了泄漏和较强伪影。

影响：

- 当前问题已经不只是“整体客观指标是否更高”，而是：
  - 模型对混响尾音、拖尾和房间染色不够稳；
  - target absent 时可能会吐出一点像目标的东西；
  - 处理中间伪影可能被误保留成“像目标的成分”。
- 如果不先补这类 realism，继续只在 dry synthetic 上扫近邻 checkpoint，主观问题大概率还会反复出现。

处理：

- 已将 near-real 听评结果和这一判断补记到日报：
  - `reports/daily/2026-03-17_near_real_listening_review.md`
- 已把下一阶段优先级更新为：
  - 先补混响 / 尾音拖尾 realism
  - 再重点看 target absent guardrail

后续要求：

1. 下一轮若继续改数据，优先加轻混响 / RIR / 拖尾类增强，而不是先扫更多近邻 loss 权重。
2. 下一轮若继续做主观验证，必须单独保留：
   - raw target only
   - target absent
   - 轻微混响 speech interference
   这三类样本，避免又被总体均值盖掉。
3. 当前已在 synthetic 生成器里补了可选轻混响入口，但默认仍关闭；真正开始用它前，应先做小规模 probe，避免直接破坏历史主线的可比性。
