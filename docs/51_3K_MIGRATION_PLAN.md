# 51_3K_MIGRATION_PLAN — 三国全面战争（3K）迁移方案：环境/工具准备 + 三目标执行层拟化

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 定位：**三国项目启动蓝图**——基于 shogun2 项目的全部成果（机制认知 + 验证方法论 + 工具链），评估三目标能否迅速攻破，并给出环境/工具准备清单与执行层拟化。
> 依据：shogun2 目标3 已达成（b9=1 单字节直写 → 纯 AI 内战加载+旁观）；`work/3k_extract/README.md`（三国官方脚本勘察）+ `work/ws_mods/README.md`（三国 workshop mod 实证）+ `../../shogun2_ai_battle/research/ENGINE_FAMILY_SURVEY.md`（引擎族谱）。
> 最后更新：2026-08-19（总指挥拟定）。
> ⚠️ **v2 勘误（2026-08-19 总指挥 + 用户纠正，详见 52_MIGRATION_COMMAND_REPORT.md）**：
> ① 本文件目标1"官方 script_ai_planner = 🟢 低"有偏差——**脚本 AI ≠ 原生 AI**（只 release 会显傻，3k_extract 附节实证），原生质量需引擎层身份替换（🟡）；
> ② 本文件目标2"startpos.esf + cm: API = 🟢 低"有偏差——**看海不是通过 startpos 实现**（shogun2 已宣告：真看海 = 运行时直写 faction+0x6a0=0 + manager=FULL_MANAGER；startpos 只调 personality），真看海需引擎层运行时字段（🟡）。
> ③ 目标3"先查官方能力边界"已实证：**3K/WH3 均无官方强制加载**（tw3k_wh3_databank 60 报告 grep 实证）→ 必须引擎层 b9 思路迁移。
> **本文件环境/工具清单仍有效；目标难度评估以 52 报告 §4 矩阵为准。**

---

## 0. 核心判断（一句话）

**三国三目标 = 走官方通道为主、逆向兜底；shogun2 的最大迁移资产是"引擎判定是否加载战斗的完整认知 + b9 最小伪造思路 + 验证方法论"，不是注入代码本身。攻破难度远低于 shogun2（官方接口全开），预计目标1/2 周内可成、目标3 需先确认官方能力边界。**

---

## 1. 环境事实（已勘察，勿重验）

| 项 | 三国（3K） | shogun2（对照） |
|---|---|---|
| 位数 | **64 位**（Three_Kingdoms.exe 243MB，主逻辑内嵌，无独立引擎 DLL）| 32 位（Empire.Retail.dll）|
| DRM | 无 Denuvo 迹象（steam_api64 + EOSSDK = 联机服务）| Steam API |
| 官方脚本 | **script/_lib/*.lua 全套**（包内，可 mod 覆盖）| 无 script/ 目录（实证 0 条，需逆向）|
| 战役脚本入口 | script/campaign/mod/*.lua（mod 目录，无需覆盖）+ cm: API | campaigns/*/scripting.lua（覆盖式）|
| 战斗脚本 | **script/battle/campaign_battle/battle_start.lua 每场战役战斗加载** | 无每战钩子 |
| 存档 | ESF 格式（startpos_historical/romance.esf，与幕府2 同族）| ESF |
| 工具链 | RPFM v4.3.7 原生支持（-g three_kingdoms，44,191 条路径）| RPFM 支持 |

**★结论**：三国 = 官方 Lua 脚本体系完整开放（pending_battle 查询、script_ai_planner、battle_manager 相机、cm: 战役 API 全在）——**AGENTS §0 通道优先级可直接走通道 1（官方 API/脚本），逆向为最后手段**。

---

## 2. 环境与工具准备清单

### 2.1 环境准备（启动前）

| # | 项 | 说明 | 状态 |
|---|---|---|---|
| 1 | Steam 安装三国（appid 779340）+ 启动一次验证 | 用户早年已装（ws_mods 有 779340 内容）| 待确认 |
| 2 | RPFM v4.3.7 读 3K data.pack | 本仓 work/tools/rpfm-v4.3.7 已支持（-g three_kingdoms）| ✅ 就绪 |
| 3 | 三国 Assembly Kit（官方工具）| Steam Tools 下载；含 TEd/脚本调试 | 待下载 |
| 4 | 存档 ESF 解析 | esfpy（本仓 work/esf_faction_dump.py 同族可复用）| ✅ 就绪 |
| 5 | 64 位逆向工具（兜底用）| Ghidra（本仓 tools/ghidra_bridge 可复用）+ x64dbg（新装，若需引擎层）| 待装 x64dbg |
| 6 | 三国脚本调试通道 | 官方脚本日志 / 控制台（验证 lua.log 是否可用）| 待验证 |

### 2.2 工具迁移评估（shogun2 → 三国）

| shogun2 工具 | 迁移性 | 说明 |
|---|---|---|
| **esfpy + esf_faction_dump.py** | ✅ 直接迁移 | 三国存档同为 ESF，faction 节点结构可对照 |
| **RPFM** | ✅ 直接迁移 | 已支持 3K |
| **Ghidra 桥**（run_analysis.sh + re_lib.py）| ✅ 方法论迁移 | 64 位需调整（PE 解析/架构），但工作流同 |
| **验证方法论**（AGENTS §3 闭环 + 观测探针 + 崩溃取证）| ✅ 100% 迁移 | 与位数无关 |
| **机制认知**（pending/human 判定/登记/加载链/b9 伪造思路）| ✅ 100% 迁移（概念同源）| 三国官方 API 直接对应（见 §3）|
| **b9 单字节直写方案** | 🔶 思路迁移 | 三国是 64 位 + 官方脚本——优先找官方等价（force 命令/投票注入），b9 思路作兜底 |
| **32 位注入工具**（_run_elev/远程线程等）| ❌ 不可平移 | 64 位架构差异 |

---

## 3. 三目标执行层拟化（基于 shogun2 成果对照）

### 目标1：玩家部队由原生 AI 指挥（三国 = 战斗中交军 AI）

**shogun2 成果对照**：直写字段（RE-B3）实机可用 = 身份替换（引擎认为该军队本来就是 AI）；**★关键认知 = "只 release_control 不建 planner = 显傻"**（3k_extract 附节实证：脚本 AI ≠ 原生 AI，EOP 三态 aiActiveSet=1 vs 2）。

**三国执行层拟化**：

| 步 | 行动 | 依据（shogun2 成果）| 判据 |
|---|---|---|---|
| 1 | **官方通道验证**：battle_start.lua 用 `pa:set_up_script_planner() + release_control_of_all_sunits()` 交军 AI | AI_Commanders mod 现成实现（ws_mods）| 玩家部队被 AI 指挥，行为可观察 |
| 2 | **★避坑：不能只 release**——需给 script_ai_planner 下目标（attack_force/defend_position），否则"显傻"（与敌人 AI 差异明显）| 3k_extract 附节：AI_Commanders 调用 attack_force 次数=0 → 反应式默认 | AI 行为与正常敌人 AI 相当 |
| 3 | **原生 AI 质量备选**：找引擎"整军原生 AI"路径（shogun2 的 a270=0 身份替换，三国是否有官方等价 / 64 位直写字段兜底）| shogun2 11 机制地图：身份替换 = 唯一原生 AI 质量路径 | 与敌人 AI 完全同等待遇 |
| 4 | **天气/战前 UI 差异检查**（shogun2 卡天气 UI 教训）| shogun2 11 §7.3 | 三国无同类黑屏 |

**难度评估**：🟢 **低**——官方 API 直接支持（AI_Commanders 现成），只需补"下目标"解决显傻 + 验证原生质量。

### 目标2：玩家派系 CAI 自主发展/看海（三国 = 战役层 AI 托管）

**shogun2 成果对照**：写 faction+0x6a0=0 + manager=FULL_MANAGER = 真看海（织田 34 回合）；恢复人控合法；**★伪人类路线崩（P42）**。

**三国执行层拟化**：

| 步 | 行动 | 依据（shogun2 成果）| 判据 |
|---|---|---|---|
| 1 | **官方通道验证**：cm: 战役 API + startpos.esf（faction manager 节点）→ 玩家派系交 CAI | 三国 startpos.esf 同族（ESF）；cm:modify_faction 等 API 已实证（ws_mods observer）| 玩家派系被 CAI 托管、自主行动 |
| 2 | **★用户早年 FakeObserverMode 先例复用**（附庸 + 观察员传送看 AI 打仗）| ws_mods obsever.lua（657 行）| 看海/观战体验 |
| 3 | **人类标志机制对照**：三国 human_involved/pending_battle 官方查询，找 CAI manager 等价字段 | shogun2 faction+0x6a0/manager 表认知 | 玩家派系 CAI 化且不崩 |
| 4 | **避坑**：shogun2 "AI 改人类崩"（P40/P42）——三国若需反向操作先验证状态集完整性 | shogun2 04 P40/P42 | 不崩 |

**难度评估**：🟢 **低**——官方 cm: API + startpos.esf + 现成 FakeObserverMode 先例；看海范式（WH3 Auto-Run）行为模板现成。

### 目标3：观看 AI 内战（三国 = 捕捉 AI vs AI 战斗并加载）

**shogun2 成果对照**：★★★ **已达成**——b9=1 单字节直写 → 纯 AI 内战加载 + 旁观（issp=1）；完整加载链认知（pending→fork→状态4→env→battle_mgr→旁观）+ **三路线真值表**（率阵厮杀/自动结算/拒绝）。

**三国执行层拟化**：

| 步 | 行动 | 依据（shogun2 成果）| 判据 |
|---|---|---|---|
| 1 | **★能力边界确认（第一优先）**：三国官方是否支持"强制加载 AI 内战/旁观"——查 Rome2 系 auto_autoresolve 族 / force 命令 / pending_battle API 是否有官方加载通道 | shogun2 结论：加载钥匙 = 人类分支；三国 pending_battle:human_involved() 官方可检测 AI 内战，但"强制加载"未知 | 官方能力边界定案（有/无）|
| 2 | **有官方通道** → 直接用（cm: 强制战斗 / pending 操作）| shogun2 若官方可行即放弃逆向（AGENTS §0）| 加载 AI 内战 + 旁观 |
| 3 | **无官方通道** → **b9 思路迁移**：三国找"分叉输入"等价字段（pending 对象投票/就绪标志），1 字节/最小伪造驱动人类加载链；64 位直写（CE/内核）兜底 | shogun2 b9=1 最小伪造方案 + 完整加载链认知 | 纯 AI 内战加载 + 本地玩家旁观 |
| 4 | **观战形态确认**：三国本地玩家不在参战名单 → 是否自动旁观（shogun2 setup 0x5cf168 等价物）| shogun2 达成判据③ IsSpectator=1 | 旁观身份确认 |
| 5 | **兜底**：回放路线（shogun2 H48c 改 PLAYER_SETUP[2]）——三国 ESF 同族可复用 | shogun2 回放路线判活 | 改造回放 → 旁观 |

**难度评估**：🟡 **中**（取决于官方能力边界）——若官方支持强制加载 = 低；若需逆向 = 中（64 位但概念已破译，b9 思路可直接映射）。

---

## 4. 攻破可行性综合评估

| 目标 | 难度 | 关键路径 | shogun2 成果如何帮 |
|---|---|---|---|
| 目标1 | 🟢 低 | 官方 script_ai_planner + 下目标 | **显傻认知**避免重走弯路（3k_extract 附节已写好结论）|
| 目标2 | 🟢 低 | cm: API + startpos.esf + FakeObserverMode | **看海机制认知**（faction 标志 + manager）直接映射 |
| 目标3 | 🟡 中 | 先查官方能力边界 → b9 思路迁移 | **加载链完整认知 + b9 最小伪造方案** = 现成路线图 |

**★总判断**：三国项目启动成本 = **环境准备（2-3 天）+ 官方能力边界验证（目标3 关键决策）**。shogun2 的最大价值 = **避免"从零摸黑"**：概念（pending/人类判定/加载链）在三国全是官方 API，把 shogun2 逆向结论当"翻译词典"即可。**目标1/2 周内可攻破，目标3 一周内可定官方能力边界并给出路线**。

---

## 5. 待确认事项（启动三国项目前）

1. **三国官方是否支持强制加载 AI 内战 / 旁观**（目标3 决策点，Rome2 系 auto_autoresolve 族 / force 命令）
2. 三国战役脚本加载机制验证（mod 覆盖 script/ 是否生效）
3. 三国 lua.log 脚本日志是否可用（shogun2 的 P3 教训）
4. 64 位引擎层兜底工具链（x64dbg/CE）是否需要

---

## 6. 迁移文档引用（shogun2 → 三国对照）

| shogun2 文档 | 三国用途 |
|---|---|
| docs/40_GOAL3_MECHANISM_MAP.md | 加载链机制认知源（pending/fork/env/battle_mgr）|
| docs/14_GOAL3_EXPLORATION_MAP.md | 达成路径 + b9 方案 + 精进清单 |
| docs/11_GOAL1_BATTLE_AI_MAP.md | 身份替换 = 原生 AI 质量路径（目标1 兜底）|
| ../../shogun2_ai_battle/research/ENGINE_FAMILY_SURVEY.md | 跨游戏范式（AI General/Auto-Run/注入框架）|
| work/3k_extract/README.md + ws_mods/README.md | 三国官方通道实证 |
| AGENTS.md | 验证方法论 + 文档纪律 + 通道优先级 |
