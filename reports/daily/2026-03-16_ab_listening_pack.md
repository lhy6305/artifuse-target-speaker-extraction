# 2026-03-16 A/B Listening Pack Preparation

## 本次目的

当前仓库已经有：

- 旧主线：`legacy stage2`
- 新主候选：`ref_film + stft0.5 + sisdr0.0005`

但还没有成型的“真实验证集 manifest”。

因此本轮不硬造一个假的真实集，而是先把“听感验证准备”做完：

1. 落一个可复用的双 checkpoint A/B 导出脚本
2. 直接导出一套难样本试听包
3. 让后续人工听感判断只需要进目录听，不需要手工拼结果

## 本次新增脚本

- `scripts/eval/export_ab_listening_pack.py`

## 脚本能力

该脚本可对同一个 manifest 上的两个 checkpoint 做 A/B 导出，并生成统一试听目录。

当前导出内容包括：

- `mixture.wav`
- `target.wav`
- `reference.wav`
- `model_a.wav`
- `model_b.wav`
- `sample_meta.json`
- 顶层 `summary.json`
- 顶层 `README.md`

样本选择逻辑：

- 先按 focus recipes 过滤
- 然后自动抽取：
  - 提升最大的样本
  - 退化最大的样本
  - 接近平手的样本

这样做的目的不是只看“新模型最强的样子”，而是同时保留：

- 明显收益样本
- 明显风险样本
- 边界样本

## 本次导出的试听包

命令：

```powershell
.\python.exe scripts\eval\export_ab_listening_pack.py --manifest data\synthetic\val_manifest.jsonl --checkpoint-a experiments\checkpoints\baseline_stft_mask_stage2\best.pt --checkpoint-b experiments\checkpoints\baseline_stft_mask_stage2_ref_film_sisdr0005\best.pt --label-a legacy_stage2 --label-b ref_film_sisdr0005 --focus-recipes target_clean_speech target_clean_plus_music target_hard_speech target_hard_plus_music --max-samples 12 --stable-count 4 --output-dir reports\eval\ab_listening_pack_stage2_vs_ref_film_sisdr0005
```

输出目录：

- `reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005/`

## 本次试听包样本构成

当前共从 focus recipes 中筛到候选样本：

- `397`

最终导出样本数：

- `12`

包含三类样本：

1. 提升最大的样本
2. 退化最大的样本
3. 接近平手的样本

当前已导出的样本 ID：

- `val_000365`
- `val_000325`
- `val_000145`
- `val_000398`
- `val_000186`
- `val_000071`
- `val_000096`
- `val_000466`
- `val_000147`
- `val_000404`
- `val_000089`
- `val_000090`

## 盲听版试听包

为了减少“文件名先暴露模型身份”带来的偏差，本轮又补导出了一份 blind A/B 版本：

- `reports/eval/ab_listening_pack_stage2_vs_ref_film_sisdr0005_blind/`

该目录中：

- 模型输出统一命名为：
  - `candidate_a.wav`
  - `candidate_b.wav`
- 可直接填写：
  - `listening_sheet.csv`
- 听完后再看：
  - `blind_key.json`

说明：

- 当前建议优先听 blind 版，再回看非 blind 版的 summary。

## 真实验证入口准备

本轮另外补了一个“任意 mixture/reference 清单”的 A/B 导出脚本：

- `scripts/eval/export_ab_inference_from_manifest.py`

并补了一个 manifest 模板：

- `data/references/real_eval_manifest_template.jsonl`

这样后面一旦整理出真实或近真实样本，只要按模板填 manifest，就可以直接导出双模型结果，而不用再改代码。

## 当前结论

这轮还不是“真实验证已经完成”，而是：

- 已把 A/B 听感验证所需的工程准备做完
- 已经有一套可直接开始听的试听包
- 后续即便换成新的 checkpoint，也可以复用同一个脚本继续导出

## 当前已收到的人工听感反馈

截至目前，已收到 3 个 blind 样本的人工反馈：

### 1. `val_000071`

用户结论：

- 选 `a`
- 描述：
  - 两者都削掉了不少细节
  - `a` 像输入数据的小声版
  - 干扰和目标都还能听到
  - 有少量电流声
  - `b` 几乎听不到目标声音

blind 解码：

- `candidate_a` = `ref_film_sisdr0005`
- `candidate_b` = `legacy_stage2`

结论：

- 在这个 `target_clean_speech + absent_head` 样本上，用户主观上更偏向新模型。

### 2. `val_000089`

用户结论：

- 选 `a`
- 描述：
  - `a` 明显同时存在干扰声音和目标声音
  - 整体较流畅
  - 干扰部分音量跳变较明显
  - 但干扰相比 `b` 更安静
  - `b` 在无干扰部分正常
  - 干扰部分保留了更多干扰音
  - 干扰部分音量跳变也明显

blind 解码：

- `candidate_a` = `legacy_stage2`
- `candidate_b` = `ref_film_sisdr0005`

结论：

- 在这个 `target_clean_plus_music + absent_tail` 样本上，用户主观上更偏向旧模型。

### 3. `val_000090`

用户结论：

- 选 `a`
- 描述：
  - `a` 音量跳变较明显
  - 但干扰压得比 `b` 更好
  - `b` 更多保留了干扰声音
  - 且有点毛刺感

blind 解码：

- `candidate_a` = `legacy_stage2`
- `candidate_b` = `ref_film_sisdr0005`

结论：

- 在这个 `target_clean_plus_music + full` 样本上，用户主观上也更偏向旧模型。

## 基于当前反馈的阶段判断

当前可以先得到一个很实在的判断：

1. 新模型不是“全面主观碾压”。
2. `target_clean_plus_music` 确实存在需要重点复核的回退样本。
3. 但这不等于新模型整体无效，因为：
   - 同一个试听包里也存在主观更偏向新模型的样本；
   - 客观平均指标上，`clean_plus_music` 与 `clean_speech` 仍整体显著优于旧模型。

因此当前更准确的状态是：

- 主线已经推进到“整体更强，但存在可听回退点”
- 下一步需要继续围绕这些回退点做更细的人工核对与针对性分析

## 下一步

1. 条件允许时，对该试听包做人工 A/B 听感判断。
2. 建议优先使用 blind 版试听包，并把结果记到 `listening_sheet.csv`。
3. 若后续补出真实或近真实 manifest，可直接复用新的 arbitrary-pair A/B 导出脚本导出真实试听包。
3. 在人工听感结论出来前，当前仍不把 synthetic 指标结论直接当作最终业务结论。
