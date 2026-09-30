# 指挥层报告（60_COMMAND_REPORT）— 三国/战锤3 资料库现状 + 幕府2 成果迁移评估

> 面向指挥层（决策/派工用）。依据：shogun2 目标3 已达成（2026-08-19，`[pending+0xb9]=1` 直写 → AI 内战加载+旁观）+ 本资料库（tw3k_wh3_databank）首轮勘察（pack 全解/脚本 API/PE 实证/引擎字符串扫描）+ shogun2 `51_3K_MIGRATION_PLAN.md`（三国迁移蓝图）。
> 日期：2026-08-19。

---

## 0. 一句话总判断

> **幕府2 目标3 的迁移资产是"机制认知 + b9 最小伪造思路 + 验证方法论"，不是注入代码。3K/WH3 均能迁移此路线，且入口比幕府2 当年好找（官方脚本查询层全开 + WH3 引擎符号明文）；唯一硬成本 = 64 位引擎层字段重新定位（160-178MB 代码体量下的定向逆向）。目标1/2 三库都走官方通道、周内可成；目标3 三库都无官方强制加载（已实证）→ 必须引擎层，按 b9 思路迁移。**

---

## 1. 幕府2 目标3 达成机制（迁移的源）

| 环节 | 机制（shogun2 已破译） |
|---|---|
| 加载钥匙 | **人类分支**：pending 状态 4（人类等待态）→ fork 0 → env 接口链 → battle_mgr 创建 |
| 最小伪造 | **`[pending+0xb9]=1` 单字节直写**（非登记门控/投票/人类在场）→ 引擎走人类加载链 |
| 自动旁观 | 本地玩家不在参战名单 → `0x5cf168` 自动旁观（IsSpectator=1）→ 纯 AI 互战可视 |
| 三判据 | 加载 + 旁观身份 + 纯 AI 无玩家（用户视觉确认） |
| 工具 | re_b9_forge.py（patch 自动写）+ 观测探针 |

**可迁移**：pending/人类判定/加载链/旁观判定 = **机制概念**（3K/WH3 同属 Rome2 系引擎，概念同源）；b9 思路 = "找分叉输入的最小字段伪造"。
**不可迁移**：全部地址/字段（32 位）、注入工具链（64 位差异）。

---

## 2. 三国（3K）现状 — 资料库已实证

| 层 | 状态 | 关键事实 |
|---|---|---|
| 数据层 | ✅ 全打通 | pack 44,189 路径/脚本 1,454/DB 1,503 表（99.9% 解码）/中文 loc 19.5MB/esfpy 实测可读 startpos |
| 脚本 API | ✅ 15 库取证 | pending_battle 查询、human_involved、script_ai_planner、相机——**官方 API 直出** |
| 官方能力边界 | ✅ grep 实证 | **无"派系切 CAI"、无"强制加载 AI 战斗"、无旁观 API**（switch_to_cai_control/spectat/force_load 0 命中）→ **目标2/3 达成需引擎层** |
| 逆向现状 | ⚠️ 体量障碍 | 178MB 可执行（.xcode），Ghidra 全量分析不可行 → 定向分析策略；引擎字符串待扫描（同 WH3 流程） |
| 参考 | — | shogun2 `51_3K_MIGRATION_PLAN.md`（三国迁移蓝图已拟） |

**迁移评估（三目标）**：
| 目标 | 难度 | 路径 | shogun2 成果如何帮 |
|---|---|---|---|
| 目标1（交军原生 AI） | 🟢 低 | 官方 script_ai_planner + 下目标（避"显傻"）| 身份替换认知 = 原生 AI 质量唯一路径 |
| 目标2（看海） | 🟢 低 | 官方 cm: API + startpos.esf + FakeObserverMode 先例 | faction 标志 + manager 认知直接映射 |
| 目标3（观战 AI 内战） | 🟡 中 | **无官方通道（已实证）→ b9 思路迁移**：找 pending 分叉字段最小伪造 → 64 位直写 | 加载链完整认知 = 现成路线图 |

---

## 3. 战锤3（WH3）现状 — 资料库已实证

| 层 | 状态 | 关键事实 |
|---|---|---|
| 数据层 | ✅ 全打通（含格式逆向） | **pack 新格式（zstd）自研破解**；脚本 5,787/DB 1,521 表（99.9%）/简中文案 39.6MB |
| 脚本 API | ✅ 43 库取证 | 与 3K 同族；pending battle = `cm:pending_battle_cache_*`（60 方法） |
| 官方能力边界 | ✅ grep 实证 | 同 3K：无派系切 CAI、无强制加载 AI 战斗 API（handover 仅区域移交事件）→ 目标2/3 达成需引擎层 |
| 官方工具 | ✅ | **Assembly Kit 已发布**（2022-06）——比 3K 更全的 mod 通道 |
| 逆向现状 | ✅ 静态实证 | **引擎符号明文**：`BCQ_`×249/`CCQ_`×369/`AI_SCRIPT_CONTROLLER`×7（BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_MOVE_TO_POSITION 等）/`FactionIsHuman`/`FULL_MANAGER`/`IsSpectator`×19/`CAI_`×720；RTTI 838 类；160MB 可执行（.shared）→ 定向分析 |
| 版本风险 | ⚠️ | 迭代快（8.1.1 现行），地址随更新漂移；patch_8_1 分支字符串可定位 |

**迁移评估（三目标）**：
| 目标 | 难度 | 路径 | 对比 3K |
|---|---|---|---|
| 目标1 | 🟢 低 | 官方 script_ai_planner（AI General 3 工坊 mod 现成先例）| 同 |
| 目标2 | 🟢 低 | Assembly Kit + cm: API + startpos.esf（已证 ESF）| 官方工具更全 |
| 目标3 | 🟡 中 | **无官方通道（已实证）→ b9 思路迁移 + 引擎符号入口（BCQ_AI_SCRIPT_CONTROLLER/FactionIsHuman 明文 xref）** | **引擎符号明文 = 比 3K 更好找入口** |

---

## 4. 迁移评估汇总（指挥层决策表）

| 维度 | 3K | WH3 |
|---|---|---|
| 目标1 官方通道 | ✅ 有（需补"下目标"避显傻）| ✅ 有（AI General 3 先例）|
| 目标2 官方通道 | ✅ cm: + startpos + FakeObserver 先例 | ✅ Assembly Kit + cm: |
| 目标3 官方强制加载 | ❌ 无（grep 实证）| ❌ 无（grep 实证）|
| 目标3 引擎层入口 | ⬜ 待扫描字符串 | ✅ 已定位（BCQ_AI_SCRIPT_CONTROLLER/FactionIsHuman/IsSpectator）|
| 体量障碍 | 178MB | 160MB |
| 版本漂移风险 | 低（停更 v1.7.1）| 高（8.1.1 活跃迭代）|
| 启动成本 | 环境 2-3 天 + 能力边界验证 | 同 + pack 工具链已就绪 |

**★结论**：
1. **目标1/2 三库均走官方通道，周内可成**——51 蓝图 + 本库脚本 API 文档直接可执行
2. **目标3 三库均无官方强制加载**（本库 grep 实证回答了 51 的待确认事项 1）→ **必须引擎层**，b9 思路迁移 + 64 位字段定位
3. **优先攻 WH3 目标3**：引擎符号入口已定位（比 3K 快），但版本漂移风险高（成果保值期短）；**3K 目标3 更稳**（停更，逆向成果不漂移）——决策点：先 WH3（入口现成）还是先 3K（成果保值）？
4. **迁移执行顺序建议**：目标1/2（官方，三库并行低风险）→ 目标3（先在一库打通 b9 等价物，再横向迁移）

---

## 5. 下一步行动（可派工）

| # | 行动 | 负责人建议 | 产出 |
|---|---|---|---|
| 1 | 3K 引擎字符串扫描（复用 wh3_quick_scan.py）| 资料库 | 3K 目标3 引擎入口表 |
| 2 | 3K/WH3 目标1 官方通道实机（battle_start.lua 交军 + 下目标）| 3K/WH3 项目 | 目标1 达成判定 |
| 3 | 3K/WH3 目标2 官方看海（cm: API + startpos + FakeObserver 迁移）| 同上 | 目标2 达成判定 |
| 4 | WH3 目标3：BCQ_AI_SCRIPT_CONTROLLER xref → Ghidra 定向反编译（-Reuse -Targets）| 逆向组 | 命令分发函数 + 分叉字段候选 |
| 5 | 3K/WH3 pending 对象结构（64 位）定位——对应 shogun2 pending+0xb9 | 逆向组 | 分叉输入字段表 |
| 6 | 版本漂移对策：CE/脚本按版本重建（WH3）| 工具组 | 快速重定位流程 |

## 6. 文档引用

| 用途 | 文档 |
|---|---|
| 三国迁移蓝图（总指挥拟定）| shogun2 docs/51_3K_MIGRATION_PLAN.md |
| 幕府2 目标3 机制地图/达成 | shogun2 docs/40_GOAL3_MECHANISM_MAP.md §0/§7 + Goal_3_LogBook 08-19 |
| 3K 档案/脚本 API/逆向评估 | 本库 3k/01_GAME_PROFILE + 30_SCRIPTING_API + 50_REVERSE_ASSESSMENT |
| WH3 档案/静态实证/逆向评估 | 本库 wh3/01_GAME_PROFILE + WH3_STATIC_ANALYSIS + 50_REVERSE_ASSESSMENT |
| 三目标官方能力边界（grep 实证）| 本库 docs/20_REVERSE_FEASIBILITY §1.4 |
| 64 位逆向工具升级路线 | 本库 docs/40_RE_TOOLCHAIN_UPGRADE |
| 逆向工程现场 | 本库 re/（Ghidra 工程 + wh3_quick_scan.py + run_ghidra_*.ps1）|
