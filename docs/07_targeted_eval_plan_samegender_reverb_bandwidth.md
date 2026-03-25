# 下一阶段定向评估与推进方案

## 1. 当前新观察

本轮人耳复核后，
当前需要被单独建模的新事实已经收敛成三条：

1. `guodegang`
   不是一个孤立样本名问题，
   更像一类真实风险家族：
   - 同性别说话人
   - `f0` 接近
   - 共鸣方式接近
   - 带一定程度房间混响
2. 当前仍存在
   “电话音 / 频段被削掉”
   这类感知问题，
   它不一定只发生在
   reverb probe，
   更可能是一条独立 guardrail。
3. 听审链路里，
   声道口径和 `target.wav`
   必须先固定，
   否则人耳结果会掺进无关噪声。

大白话讲：

- 下一阶段不该再问
  “friend-side 大树还能不能继续扩”；
- 而该改问：
  - 对
    “像 `guodegang` 这种同性别、近 `f0`、近共鸣、带轻混响的人声”
    会不会系统性漏？
  - 对
    “电话音 / 频带缺失”
    会不会系统性更严重？

## 2. 已补好的工程前置

当前已经补好的工程底座：

1. `near_real_v1`
   样本目录现在已带：
   - `target.wav`
2. `data/references/real_eval_manifest_near_real_v1.jsonl`
   现在已带：
   - `target_audio_path`
3. `scripts/eval/export_ab_inference_from_manifest.py`
   现在会：
   - 优先导出 `target.wav`
   - 明确统一导出为单声道
4. 新增：
   - `scripts/eval/audit_listening_pack_assets.py`
   用来在听审前检查：
   - 是否全单声道
   - 是否缺 `target.wav`

当前已确认：

- `near_real_v1`
  基础样本本身是单声道；
- 旧的
  `decision_gate ... blind_v2`
  包虽然也是单声道，
  但确实缺了 `target.wav`；
- 之后的新导包链应先跑 audit，
  再做人耳。

## 3. 定向评估设计

### 3.1 听审资产 QA

目标：

- 先把“听审文件本身有没有失真因素”排干净。

固定执行：

```powershell
.\python.exe scripts\eval\audit_listening_pack_assets.py --pack-dir <pack_dir> --require-target
```

放行条件：

1. `all_mono = true`
2. `all_have_target = true`
3. `non_mono_file_count = 0`
4. `missing_target_count = 0`

这一步不过，
不进入正式听审。

### 3.2 `guodegang-like` 家族化 near-real 评估

目标：

- 不再把 `guodegang`
  当成单独人名样本，
  而是升级成一类症状家族。

建议新 family 定义：

- `same_gender_reverb_like_speech`

入选条件建议：

1. 说话人性别与目标一致
2. `f0` 中位数与目标接近
3. 共鸣 / 谱包络整体接近
4. 素材带轻到中度房间混响
5. 优先保留真实语音，
   不先做人为强处理

near-real 侧建议至少覆盖两类：

1. target present
   - `target + same_gender_reverb_like speech`
2. target absent
   - `same_gender_reverb_like speech only`

当前立即可保留的 seed：

- `near_real_0006`
- `near_real_0009`

若本地后续补到更多外部素材，
应把这类 family
 扩到至少：

- `6-12` 条 near-real 样本

判断口径：

- 不只看 overall，
  必须单独看：
  - target present family
  - target absent family

### 3.3 focused synthetic proxy

目标：

- 在开训练前，
  先用 synthetic 子集筛掉明显错方向的候选。

当前保留的 proxy 入口：

- `train_manifest_guodegang_proxy_v1.jsonl`
- `val_manifest_guodegang_proxy_v1.jsonl`

这组 proxy
 仍然有效，
 但下一阶段解释要改成：

- 它不是“只对应郭德纲本人”，
- 而是当前最接近
  `same_gender_reverb_like`
  风险的一条 seed proxy。

下一步建议不是重做大 proxy 搜索，
而是只做两件事：

1. 保留
   `guodegang_proxy_v1`
   作为 focused pre-screen
2. 后续若补到更多同类真实素材，
   再新增：
   - `same_gender_reverb_proxy_v2`

### 3.4 电话音 / 带宽缺失 guardrail

目标：

- 把
  “听起来像电话音”
  从主观吐槽，
  升级成固定 guardrail。

当前直接可复用的工具：

- `scripts/eval/analyze_listening_pack_bandwidth.py`

建议每次 near-real 导包后固定执行：

```powershell
.\python.exe scripts\eval\analyze_listening_pack_bandwidth.py --pack-dir <pack_dir>
```

重点盯的样本组：

1. raw target only
   - 看是否把目标本身削窄
2. `same_gender_reverb_like`
   target present
   - 看模型是否为了压干扰，
     先把高频 / 存在感一起削掉
3. target absent
   - 看 suppress 时
     是否出现异常窄带残留

下一阶段应把下面这条规则固定下来：

- **电话音问题不再混在“artifact”里口头描述，而是单独作为 bandwidth guardrail**

建议主判字段：

1. `rolloff_95_hz`
2. `upper_vs_mid_db`
3. `frame_upper_share_p90`

推荐判停逻辑：

- 若候选相对基座在
  raw-target-only
  或
  same_gender_reverb_like
  家族上，
  被标成更窄带，
  就直接记为 bandwidth regression。

## 4. 下一阶段的最小推进方案

### 4.1 不再做的事

1. 不继续
   `v64`
   独立 follow-up
2. 不继续
   `candidate_v7`
   旧 rows 路由细分
3. 不继续 broad union manifest 扩树
4. 不继续只围绕单一 loss weight 扫近邻

### 4.2 只保留的一条窄线

若继续，
下一阶段只保留：

- `v32` 基座上的
  `same_gender_reverb_like + bandwidth guardrail`
  focused follow-up

建议执行顺序：

1. 先补齐
   `same_gender_reverb_like`
   的 near-real family 样本
2. 再把听审链固定成：
   - mono
   - target present
   - asset audit 必过
3. 再用
   `guodegang_proxy_v1`
   做一轮小规模 synthetic pre-screen
4. 只有 pre-screen
   没明显回退时，
   才允许起一轮小训练

### 4.3 训练侧建议

如果真的起下一轮，
当前只建议：

1. init：
   - `v32`
2. 数据：
   - 保留当前主数据
   - 额外加一条轻量 focused objective
     对准
     `guodegang_proxy_v1`
     / `same_gender_reverb_like`
3. realism：
   - 只加 speech-like interference 侧的轻混响
   - 不再一起动 target 侧
4. 守门：
   - friend speech leakage
   - target absent
   - raw target only
   - bandwidth guardrail

## 5. 放行与停线条件

若重开，
建议把放行条件固定成：

1. 相对 `v32`，
   `same_gender_reverb_like`
   near-real family 必须形成稳定可听收益
2. `near_real_0006`
   不能更差
3. `near_real_0009`
   不能更差
4. friend speech leakage
   不能更差
5. raw target only
   不能更差
6. bandwidth analysis
   不能新增明确窄带回退

只要任一条不过：

- 直接停
- 不扩更多训练
- 不补更多 route 解释

## 6. 当前默认建议

当前默认建议是：

1. 先按当前阶段结题口径收尾
2. 把上面的定向评估方案作为下一阶段预案保留
3. 只有在你明确决定继续修：
   - 同性别近 `f0`
   - 近共鸣
   - 轻混响
   - 电话音
   这组真实痛点时，
   才按这份方案重开
