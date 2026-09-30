# 52_MIGRATION_COMMAND_REPORT — 三国/战锤3 迁移指挥报告（v2：吸收 60 报告 + 用户两点纠正）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 定位：**指挥层正式报告**——三库（shogun2 源 / 3K / WH3）迁移决策 + 执行层拟化。
> 依据：shogun2 目标3 达成（2026-08-19，b9=1 直写）+ 目标2 看海闭环 + 目标1 直写方案；`tw3k_wh3_databank/docs/60_COMMAND_REPORT.md`（对方资料库勘察）；本仓 `docs/51_3K_MIGRATION_PLAN.md`（三国蓝图 v1）；3k_extract/ws_mods 勘察。
> 版本：v2 = 在 v1/60 报告基础上落实**用户两点纠正**（①AI 指挥 mod ≠ 原生 AI 指挥 ②看海 ≠ startpos 实现）——这两点直接改变目标1/2 的难度评估。
> 日期：2026-08-19。总指挥拟定。

---

## 0. 一句话总判断（v2 修正版）

> **三库三目标的"官方通道"只能做到"脚本 AI / 伪看海 / 无法观战"三个下限；要达到 shogun2 同等的"原生 AI 指挥 / 真看海 / 观战 AI 内战"标准，目标1 需引擎层身份替换、目标2 需引擎层运行时字段（非 startpos）、目标3 必须引擎层（无官方强制加载，已实证）。迁移资产 = 机制认知 + b9 最小伪造思路 + 验证方法论 + 身份替换/看海机制的精确认知。执行顺序（2026-08-19 用户定案）：**先 3K（停更保值，先攻环境稳定库）后 WH3**——目标1/2 先官方下限达标 + 摸清能力，目标3 先 3K 打通 b9 等价物再横向迁移 WH3。**

---

## 1. shogun2 源成果的精确定义（什么可迁移、什么不可）

### 1.1 三目标达成机制（源）

| 目标 | shogun2 达成机制 | 性质 |
|---|---|---|
| 目标1 原生 AI 托管 | **直写 army 8 字段 + 单位 ea8/c01 = 身份替换**（引擎认为该军队本来就是 AI）→ 与正常敌人 AI 同等待遇（battle_ai 无注入实机）| 引擎层身份替换 |
| 目标2 看海 | **运行时直写 `faction+0x6a0=0` + `manager=FULL_MANAGER`** → 织田 AI 玩 34 回合；恢复人控合法 | 引擎层运行时字段 |
| 目标3 观战 | **`[pending+0xb9]=1` 单字节直写 → fork 0 → 状态 4 → env 链 → battle_mgr → 0x5cf168 自动旁观** | 引擎层分叉输入伪造 |

### 1.2 可迁移 / 不可迁移

- **✅ 可迁移（认知）**：pending/人类判定/加载链/旁观判定机制概念；b9 = "找分叉输入最小字段伪造"思路；**身份替换 = 原生 AI 质量唯一路径**；**看海 = 运行时标志 + manager 组合**；验证方法论（AGENTS §3）。
- **❌ 不可迁移（实现）**：全部 32 位地址/字段偏移；32 位注入工具链（远程线程等）；startpos 编辑当看海手段（★见 §3）。

---

## 2. ★用户纠正 1：3K/WH3 的 AI 指挥 mod ≠ 原生 AI 指挥（明确偏差）

### 2.1 shogun2 实证（勿重走弯路）

| 项 | shogun2 项目（s2_ai_ctl 直写） | 三国 AI_Commanders（script_ai_planner） |
|---|---|---|
| 手段 | 直写军队字段（a270=0/a28c=1/... + 单位 ea8/c01）| `release_control_of_all_sunits()` + `set_up_script_planner()` |
| 本质 | **身份替换**：引擎认为该军队本来就是 AI 军队 | **脚本接管**：script_ai_planner 由 Lua 发高层命令 |
| 决策者 | 引擎原生战斗 AI（与敌人 AI 同一路径）| **脚本自己**（目标选择等由 Lua 规则决定）|
| EOP 三态对应 | aiActiveSet=1（active = 原生 AI）| aiActiveSet=2（script controlled，独立档位）|
| 质量 | 与正常敌人 AI 完全同等待遇（实机）| **显傻**（attack_force 等目标调用=0 → 反应式默认，3k_extract 附节实证）|

### 2.2 对 3K/WH3 目标1 的评估修正

- **60 报告"目标1 🟢 官方通道"需降级为"🟢 脚本 AI 下限 / 🟡 原生 AI 质量需引擎层"**：
  - 官方通道（script_ai_planner）可拿"被脚本指挥的 AI"，但**质量上限 = 脚本 AI**（≈AI_Commanders 水平，比敌人 AI 显傻）；
  - 要"原生 AI 质量"= 引擎层身份替换（shogun2 a270=0 等价物在 64 位定位：找军队/单位 AI 标志字段直写）。
- **WH3 AI General 3 "uses the game's own AI Planner"** = 引擎 AI Planner（脚本层高层命令器），**仍非引擎原生战斗 AI 完整决策树**——不可视为原生 AI 等价。
- **行动修正**：目标1 = ①官方通道先跑通"下限达标"（交军可动）→ ②引擎层身份替换达成"原生质量"（对照 shogun2 直写 8 字段思路，64 位定位军队 AI 标志字段）。

---

## 3. ★用户纠正 2：看海不是通过 startpos 实现的（shogun2 已宣告）

### 3.1 shogun2 实证（26_HANDOFF 闭环）

- **真看海 = 运行时内存直写**：`faction+0x6a0=0`（FactionIsHuman 清除）+ `manager=FULL_MANAGER` → 织田 AI 自主玩到 34 回合（招募/进军）；恢复人控 = 反向写回（manager→7 + 0x6a0→1）合法。
- **startpos.esf 里的 manager 节点 ≠ 运行时开关**：它是 **CAI personality（行动倾向）** 的存档层描述（TWC《All about the CAI》：manager 按派系写在 startpos.esf）——**改 startpos 只改倾向，不改"谁控制这个派系"**。
- **P32 教训**：manager 表直写 FULL_MANAGER **单独 ≠ 人类控制开关**（必须 + faction 人类标志组合）。

### 3.2 对 3K/WH3 目标2 的评估修正

- **60 报告"目标2 🟢 官方 cm: + startpos.esf"需修正**：startpos.esf 只能调 personality（倾向），**不能实现"玩家派系交 CAI 自主行动"**——与 shogun2 实证一致。
- **cm: 战役 API 查询有，但"切换控制权"官方 API 已 grep 实证不存在**（switch_to_cai_control 0 命中）→ **目标2 真看海 = 引擎层运行时字段**（找 faction 人类标志 + manager 等价物，64 位定位）。
- **FakeObserverMode（用户早年 3K mod）是"附庸 + 观察员传送"的战役层伪看海**（把玩家变附庸、传观察员看 AI），**不是真看海**（玩家派系未被 CAI 托管）——可作"伪看海"体验参考，非达成路径。
- **行动修正**：目标2 = ①官方通道跑通"伪看海下限"（FakeObserver 迁移，体验可看）→ ②引擎层 faction 人类标志 + manager 等价字段定位（对照 shogun2 26_HANDOFF 组合写）→ 真看海达成。

---

## 4. 三库 × 三目标 × 双标准矩阵（v2 修正版）

> 双标准 = 官方通道能到的"下限" vs 与 shogun2 同等的"达成标准"。**判定"达成"一律按后者**（原生 AI 质量 / 真看海 / 观战 AI 内战）。

| 目标 | 3K 官方通道（下限）| 3K 达成（引擎层）| WH3 官方通道（下限）| WH3 达成（引擎层）|
|---|---|---|---|---|
| **目标1** 原生 AI 托管 | 🟢 脚本 AI（显傻上限）| 🟡 身份替换字段定位（178MB 定向）| 🟢 脚本 AI（AI General 3 先例）| 🟡 身份替换字段定位（160MB + 引擎符号明文 xref 易）|
| **目标2** 看海 | 🟢 伪看海（FakeObserver 迁移，非真）| 🟡 faction 标志+manager 字段（非 startpos）| 🟢 伪看海（Assembly Kit 更全）| 🟡 同 3K |
| **目标3** 观战 AI 内战 | ❌ 无官方强制加载（grep 实证）| 🟡 b9 思路迁移 + 分叉字段定位 | ❌ 无官方强制加载（grep 实证）| 🟡 b9 思路迁移（**引擎符号明文入口更易**）|

**★关键修正（vs 60 报告）**：
1. 目标1 不再是"纯官方 🟢 周内可成"——官方只达下限；**原生质量需引擎层**（难度 🟢→🟡）；
2. 目标2 不再是"startpos 🟢"——**startpos ≠ 看海**（shogun2 已宣告）；真看海需引擎层运行时字段（🟢→🟡）；
3. 目标3 维持 🟡（无官方通道已实证 → 引擎层 b9 思路）。

**体量与版本**：3K 178MB 停更（成果保值，入口待扫字符串）；WH3 160MB 活跃迭代 8.1.1（入口现成，版本漂移风险高）。

---

## 5. 执行顺序与派工（指挥决策）

### 5.1 执行顺序（总指挥裁决，2026-08-19 用户定案：**先 3K，WH3 后置**）

1. **阶段 A（并行，低风险）**：3K 目标1、目标2 的**官方通道下限验证**——跑通脚本 AI 交军（+ 下目标测试）与伪看海（FakeObserver 迁移），**同时量化"下限 vs 原生"差距**（为引擎层投入提供基线）；
2. **阶段 B（3K 目标3 攻坚，优先）**：3K 目标3 = **引擎字符串扫描（复用 wh3_quick_scan.py）** → 找 pending 分叉字段（b9 等价物）+ 加载链入口 → 64 位直写验证。**3K 停更（v1.7.1）→ 逆向成果保值，无版本漂移风险，先拿下**；
3. **阶段 C（WH3 迁移）**：WH3 = 把 3K 打通的方案**横向迁移** + 引擎符号明文（BCQ_AI_SCRIPT_CONTROLLER/FactionIsHuman/IsSpectator）xref 加速定位（WH3 活跃迭代 8.1.1，版本漂移风险高 → 方案验证后快速落地，成果保值期短是已知成本）；
4. **阶段 D（引擎层质量）**：目标1 身份替换字段 + 目标2 faction/manager 字段定位（先 3K 后 WH3）。

> **先 3K 的理由**：①停更 → 成果保值（WH3 8.1.1 活跃迭代，逆向成果可能随更新作废）；②先攻环境稳定的库，方案打磨成熟后再迁移 WH3（WH3 引擎符号明文可加速迁移）；③两库都要拿下，先难后易 / 先稳后快。

### 5.2 派工表（可立即派，3K 优先）

| # | 行动 | 项目 | 产出 | 状态 |
|---|---|---|---|---|
| 1 | **3K 引擎字符串扫描（复用 wh3_quick_scan.py）→ 目标3 引擎入口表** | **3K（P0）** | 3K 目标3 引擎入口表（pending 分叉字段候选）| 可派（资料库）|
| 2 | **3K 目标3：pending 对象结构（64 位）定位——对应 shogun2 pending+0xb9** | **3K（P0）** | 分叉输入字段表 | 可派（依赖 1）|
| 3 | 3K 目标1 官方下限验证（battle_start.lua 交军 + 下目标对照）| 3K | 下限 vs 原生差距量化 | 可派 |
| 4 | 3K 目标2 伪看海验证（FakeObserver 迁移）+ **startpos 反证记录** | 3K | 伪看海基线 + 反证（startpos ≠ 看海）| 可派 |
| 5 | WH3 目标3：BCQ_AI_SCRIPT_CONTROLLER/FactionIsHuman/IsSpectator xref → Ghidra 定向反编译（3K 方案验证后迁移加速用）| WH3（后置）| 命令分发函数 + 分叉字段候选 | 3K 阶段 B 后再派 |
| 6 | 版本漂移对策（WH3 8.1.1：CE/脚本按版本重建）| 工具组 | 快速重定位流程 | 3K 后再派 |

---

## 6. 文档引用

| 用途 | 文档 |
|---|---|
| 三国迁移蓝图 v1（本报告前身，含环境/工具清单）| shogun2 `docs/51_3K_MIGRATION_PLAN.md` |
| 幕府2 目标3 机制地图/达成 | shogun2 `docs/40_GOAL3_MECHANISM_MAP.md` §0/§7 + `Goal_3_LogBook.md` 08-19 |
| 幕府2 目标2 看海实证（**非 startpos**）| shogun2 00_INDEX 阶段状态（26_HANDOFF：faction+0x6a0=0 + manager=FULL_MANAGER）+ 04 P32 |
| 幕府2 目标1 身份替换实证 | shogun2 `docs/11_GOAL1_BATTLE_AI_MAP.md` §8 |
| **AI mod ≠ 原生 AI（显傻实证）** | `work/3k_extract/README.md` 附节 + `work/ws_mods/README.md` 附节 |
| 对方资料库勘察（pack 全解/脚本 API/引擎符号/能力边界 grep）| `tw3k_wh3_databank/docs/60_COMMAND_REPORT.md` |
| 跨游戏范式（AI General/Auto-Run/注入框架）| shogun2 `../../shogun2_ai_battle/research/ENGINE_FAMILY_SURVEY.md` |
