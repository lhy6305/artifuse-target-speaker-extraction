# 2026-03-20 `branch_protect` selector asset builder

## 背景

`v64 / v65` 已经说明：

- `exact_nontargetfull`
  不是对题的第二 selector；
- 直接来自
  `v23 speech_leak exact`
  并减掉
  `v30 target_full`
  overlap 的 selector，
  语义上更接近真实
  `0004-like speech_leak`；
- 但这套资产在恢复前
  只有结果文件，
  没有正式生成脚本。

这会带来一个直接问题：

- 下次若继续重建
  `0004-like speech_leak`
  selector / proxy，
  很容易又回到
  手工做集合差、
  手工 union manifest，
  最后连“这次到底测的是哪条语义”
  都会开始漂。

因此本轮先不新开训练，
只把这层资产生成过程
正式脚本化。

## 新增脚本

- `scripts/data/build_branch_protect_selector_assets.py`

### 作用

从 focused proxy manifest 出发，
一次性完成下面几件事：

1. 读取 train / val focused manifest
2. 可选减去一份已存在 selector
3. 输出：
   - `*_train.txt`
   - `*_val.txt`
   - `*_all.txt`
   三份 sample-id selector
4. 可选把筛出的 rows
   union 回 base train / val manifest
5. 输出：
   - overlap
   - recipe / temporal pattern
   - merged split 规模
   的摘要

### 当前对应的问题语义

当前脚本不是为了泛化所有 selector，
而是先把这条恢复链里
最容易丢失定义的资产写死：

- `v23 speech_leak exact`
  minus
  `v30 exact target_full`

也就是：

- 当前 `v64 / v65`
  用到的
  `speech_leak_exact_minus_targetfull`
  资产定义

## 实跑重建

本轮已用仓库自带 `python.exe`
实际重建以下资产：

- sample-id selector：
  - `data/synthetic/sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_train.txt`
  - `data/synthetic/sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_val.txt`
  - `data/synthetic/sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull_all.txt`
- merged manifest：
  - `data/synthetic/train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`
  - `data/synthetic/val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl`

对应命令为：

```powershell
.\python.exe scripts/data/build_branch_protect_selector_assets.py `
  --focus-train-manifest data/synthetic/train_manifest_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact.jsonl `
  --focus-val-manifest data/synthetic/val_manifest_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact.jsonl `
  --output-sample-ids-prefix data/synthetic/sample_ids_v23_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull `
  --subtract-sample-ids-file data/synthetic/sample_ids_v30_friend_reverse_guardrail_proxy_v8_similarity_lowtransient_lowinttrans_exact_targetfull_all.txt `
  --base-train-manifest data/synthetic/train_manifest_v42_v30_plus_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl `
  --base-val-manifest data/synthetic/val_manifest_v42_v30_plus_guodegang_absent_proxy_v7_highoverlap_lowtargettransient_lowinttrans.jsonl `
  --output-train-manifest data/synthetic/train_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl `
  --output-val-manifest data/synthetic/val_manifest_v65_v42_plus_friend_reverse_guardrail_proxy_v4_speech_leak_exact_minus_targetfull.jsonl `
  --summary-json tmp/branch_protect_selector_assets_v23minus_summary.json
```

## 重建结果

脚本输出与当前磁盘历史产物一致：

- focused source：
  - `v23 speech_leak exact`
    - train `11`
    - val `3`
- subtract overlap：
  - train `4`
    - `train_000001`
    - `train_000432`
    - `train_001225`
    - `train_001610`
  - val `1`
    - `val_000075`
- 最终 `v23minus`：
  - train `7`
  - val `2`
  - all `9`
- `v23minus` 当前全部都是：
  - `target_clean_speech`
  - `target_full`
- `v65` merged split：
  - train `135`
  - val `39`

这说明：

- `v64 / v65`
  现在不再只是“当时跑出来的目录”
- 而是已经有了
  正式可复现的生成入口

## 当前意义

这一步还不是
“已经找到新的 `0004-like` 真 selector”。

它解决的是更基础的问题：

- 后续如果继续重建
  `speech_leak_like (0004)`
  的 selector / proxy，
  现在已经有正式 builder
  可以承接；
- 因而下一步可以直接改：
  - focused proxy manifest 的语义定义
  - subtract selector 的定义
  - 或 union 的 base manifest
- 而不需要再手工维护
  sample-id 文件和 merged manifest。

## 当前更新

从这一步开始，
当前 dual-protect 线的默认入口应改成：

1. 用
   `scripts/data/build_branch_protect_selector_assets.py`
   重建 selector 资产；
2. 再决定新的
   `speech_leak_like (0004)`
   proxy manifest
   应该从：
   - `v23` 类 exact family
   - `v29 / v30` 类相似度 family
   - 或新的 near-real 锚点映射
   哪一条继续；
3. 不再手工维护：
   - `v23minus` sample-id
   - `v65` merged manifest。
