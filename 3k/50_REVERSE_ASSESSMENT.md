# 三国逆向可行性评估（50_REVERSE_ASSESSMENT）

> 总评估见 `../docs/20_REVERSE_FEASIBILITY.md`；本文件为三国专项细化。

## 结论速览

- **数据层**：✅ 完全打通（RPFM + 自研提取器；44,189 路径 / 1,454 脚本 / 1,503 表 / ESF 存档）
- **查询/观测层**：✅ 官方脚本 API 直出（pending battle / 人类判定 / 相机），无需逆向
- **AI 操控层**：⚠️ **官方 API 与 shogun2 机制根本不同**（身份替换 vs 脚本接管）——script_ai_planner 只能给脚本 AI（≈AI_Commanders 水平）；**原生 AI 质量必须引擎层直写字段**（64 位逆向）

## 可简单确认的关键逻辑点（官方 API 对照表）

> ⚠️ 下表分两类：**查询/观测类**（官方 API 直出 ✓）与 **操控类**（官方 API 是脚本接管，≠ 原生 AI；用户已论证与 shogun2 完全不同的机制）。

| 逻辑点（shogun2 逆向成果） | 3K 官方 API | 类型 | 来源文件 |
|---|---|---|---|
| pending battle 存在性/状态 | `query_model:pending_battle()` | 查询 ✓ | lib_campaign_pending_battle_cache.lua |
| 人类参战判定 | `pending_battle:human_involved()` | 查询 ✓ | 同上 |
| 攻防军队枚举 | `attacker()/defender()/secondary_attackers():item_at(i)` | 查询 ✓ | 同上 |
| 战斗类型 | `seige_battle()/ambush_battle()/naval_battle()/night_battle()/battle_type()` | 查询 ✓ | 同上 |
| 观战相机 | `battle:camera():move_to()/enable_camera_movement()` | 查询 ✓ | lib_battle_manager.lua |
| AI 目标规划 | `script_ai_planner:new()/move_to_position/.../attack_force/patrol` | ⚠️ 操控（**脚本 AI**，非原生） | lib_battle_script_ai_planner.lua |
| 军队脚本接管/释放 | `generated_army:set_up_script_planner()/release_control_of_all_sunits()` | ⚠️ 操控（**脚本 AI**，非原生） | lib_generated_battle.lua |
| 单位级接管 | `UnitController:take_control()/release_control()` | ⚠️ 操控（**脚本控制**） | lib_battle_script_unit.lua |

## AI 操控质量缺口（用户已论证，勿混为一谈）

| | shogun2（s2_ai_ctl） | 3K 官方通道（script_ai_planner） |
|---|---|---|
| 手段 | 直写军队字段（a270=0/a28c=1/a290=1.0f/a294=-1 + 单位 +0xea8/+0xc01） | `release_control_of_all_sunits()` + `set_up_script_planner()` |
| 本质 | **身份替换**：引擎认为该军队"本来就是 AI 军队" | **脚本接管**：script_ai_planner 由脚本发高层命令 |
| 决策者 | 引擎原生战斗 AI（与友军/AI 敌人同一路径） | **脚本自己**（目标选择等由 Lua 逻辑决定） |
| 质量 | 原生 AI（=友军 AI 水平） | 脚本 AI（≈AI_Commanders，用户实测"比敌人 AI 傻"） |

## 引擎级逆向（获得原生 AI 质量的唯一通道）

- 目标：军队级"原生 AI 激活"字段（3K 官方无 ai_active 类 API；幕府2 是 a270=0/a28c=1/a290=1.0f/a294=-1）
- 候选前置验证："只 release 不建 planner"释放后单位交谁（待实测）
- 条件：Three_Kingdoms.exe 255MB、64 位、主逻辑内嵌（无独立引擎 DLL）、无 Denuvo
- 方法：Ghidra x64 分析 + 内存字段定位（幕府2 方法论可复用，地址/结构全部重新逆向）
- 难度：中-高；验证闭环（实机观测通道）需从零搭建

## 路线建议（按目标，修正版）

> ★ 用户追问后核验：**目标2（看海）、目标3（观战 AI 内战）官方脚本无 API**（grep 实证：`switch_to_cai_control/handover/grant_faction/spectat/force_load` 在 3K 脚本全 0 命中；WH3 的 handover 均为区域移交/传送网络事件）。三目标**达成**全部需引擎层。

1. **探测/观测通道**（零成本）：官方脚本——pending battle 查询、`human_involved()`、`is_human`、autoresolve 检测、已加载战斗的相机
2. **目标1**：官方脚本只能脚本接管（AI_Commanders 水平）；**原生 AI 质量 = 引擎层直写字段**（候选前置：验证"只 release 不建 planner"）
3. **目标2（看海）**：官方脚本 ✗（无派系切 CAI API；3K 无 hotseat）→ **引擎层**：参考 shogun2 的 faction 人类标志 + manager 写法（3K 需重新定位字段）
4. **目标3（观战 AI 内战）**：官方脚本 ✗（无强制加载 API；无人类参战 → 引擎自动结算）→ **引擎层**：shogun2 同款 battle_mgr 创建链难题（3K 64 位重新逆向）
5. pack mod + ESF 存档修改——低成本辅助通道

## 未核实项

- 战役脚本加载机制（mod 覆盖 script/ 是否生效——需实机验证）
- "只 release 不建 planner"释放后单位交谁（原生 AI？）
- Rome2 系是否有官方"强制加载 AI 内战/旁观"命令
- 引擎级注入实机可行性
