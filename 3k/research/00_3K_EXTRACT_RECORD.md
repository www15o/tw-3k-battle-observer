# 三国全面战争 — 官方脚本勘察记录（迁移自 shogun2_ai_battle/work/3k_extract）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 原始出处：`work/3k_extract/README.md`（该文件原先误放于 `shogun2_ai_battle/work/3k_extract/`，2026-09-13 已迁入本库；2026-08-11 勘察），本文件补充后续勘察结论。
> 来源：`<Steam 库>\steamapps\common\Total War THREE KINGDOMS\data\data.pack`（6.1GB，RPFM `-g three_kingdoms` 可读；本库自研 `pfh5_extract.py` 亦可读）。
> 状态：只读勘察（未启动游戏、未改任何文件）。方法：RPFM/自研提取器提取包内 script/_lib/*.lua。

## 一句话结论

**三国官方战役/战斗脚本接口完整开放——幕府2 逆向到 RVA 级的概念（pending battle、人类判定、AI planner、相机），在三国全是官方 Lua 方法。三国路线应走官方通道（mod + 脚本），逆向为最后手段。**

## 环境事实

| 项 | 值 |
|---|---|
| 位数 | 64 位（Three_Kingdoms.exe 243MB，主逻辑内嵌，无独立引擎 DLL） |
| DRM | 无 Denuvo 迹象（steam_api64 + EOSSDK = 联机服务非 DRM） |
| 工具链 | RPFM v4.3.7 原生支持（-g three_kingdoms）；本库自研 pfh5_extract.py 亦完全可读 |
| 存档 | ESF 格式（startpos_historical/romance.esf，与幕府2 同族，esfpy 可复用） |
| 官方脚本 | script/_lib/*.lua 全套（包内，可 mod 覆盖候选），共 1,454 个 script/ 文件 |

## 关键 API 证据（提取自 data.pack script/）

### lib_campaign_pending_battle_cache.lua（19KB）
- `query_model:pending_battle()` —— **官方 pending battle 查询接口**
- `pending_battle:human_involved()` —— 人类参战判定（= 幕府2 逆向的 faction+0x6a0 人类检查）
- `pending_battle:attacker():military_force()` / `defender()` / `secondary_attackers():item_at(i)` —— 攻防军队官方枚举（= 幕府2 逆向的 entry[0x1c] 链表）
- `pending_battle:seige_battle()/ambush_battle()/naval_battle()/night_battle()/battle_type()/attacker_is_stronger()`

### lib_battle_script_ai_planner.lua（45KB，1322 行）
- `script_ai_planner:new(name, sunits, is_debug)` + `add_sunits/release/ensure_units_are_released`
- `move_to_position / move_to_force / defend_position / defend_force / attack_unit / attack_force / patrol` 全套
- = 幕府2 逆向的 AIObjectivePlanner 官方版（幕府2 里它是引擎内部概念，三国是官方脚本对象）

### lib_battle_manager.lua（134KB）
- `battle:camera():move_to(cam_pos, cam_targ, duration)` —— 官方相机控制
- `enable_camera_movement(value)` —— 观战相关相机锁
- `set_locatable_objective` —— 目标+镜头联动

## 三国路线建议（供三国项目启动时用；2026-08 追问修正版）

> ★ 修正：2026-08 对已提取 1,454 个脚本全文 grep 后确认——**目标2（看海）、目标3（观战 AI 内战）官方脚本无达成 API**（`switch_to_cai_control/handover/grant_faction/spectat/drop_in/force_load` 全 0 命中）；三目标达成均需引擎层逆向。官方脚本仅覆盖查询/检测与单场脚本战控制。

1. **官方通道盘点优先**：mod 覆盖 script/ 或 startpos 关联战役脚本的加载机制需先验证（Rome2 系战役脚本 = startpos.esf 引用 + script/ 目录）。
2. **探测/观测通道（零成本）**：pending_battle 查询 + `human_involved()` + `is_human` + autoresolve 检测 + 已加载战斗的相机（官方 API 直出）。
3. **目标1**（玩家部队交 AI）：script_ai_planner 官方 API 可用但=**脚本接管**（AI_Commanders 水平）；原生 AI 质量需引擎层直写字段。
4. **目标2**（看海）：~~startpos.esf + 战役脚本~~（修正：存档修改≠看海，shogun2 看海是运行期内存直写 faction 人类标志+manager）；**官方无派系切 CAI API、3K 无 hotseat → 引擎层**。
5. **目标3**（观战 AI 内战）：pending_battle 官方查询 + human_involved=false 可**检测** AI 内战；但**强制加载 AI 内战官方脚本无 API**（grep 实证）→ **引擎层**（shogun2 同款 battle_mgr 创建链难题）。
6. **未验证项**：三国战役脚本加载机制 / 引擎层 64 位注入可行性（三目标达成的共同前置）。

## AI 质量路径对比（2026-08-11 补充，回答"AI_Commanders 显得傻"）

> 用户观察：三国 AI_Commanders 实际用起来比敌人 AI 傻；幕府2 项目（s2_ai_ctl 直写字段）与友军 AI 水平一致。**不是错觉——两条路是根本不同的机制。**

| | 幕府2 项目（s2_ai_ctl） | 三国 AI_Commanders（script_ai_planner） |
|---|---|---|
| 手段 | 直写军队字段（a270=0/a28c=1/a290=1.0f/a294=-1 + 单位 +0xea8/+0xc01） | `release_control_of_all_sunits()` + `set_up_script_planner()` |
| 本质 | **身份替换**：引擎认为该军队"本来就是 AI 军队" | **脚本接管**：script_ai_planner 由脚本发高层命令 |
| 决策者 | 引擎原生战斗 AI（与友军/AI 敌人同一路径） | **脚本自己**（目标选择等由 Lua 逻辑决定） |
| EOP 三态对应 | aiActiveSet=1（active=原生 AI） | aiActiveSet=2（script controlled=脚本控制，独立档） |

**三国官方库查证（2026-08-11）**：`generated_army` 只有 `set_up_script_planner`/`release_control_of_all_sunits`，**无军队级"原生 AI 激活"API**（无 ai_active/set_ai_control 类）。`lib_battle_script_unit.lua` 有 UnitController `take_control()/release_control()`（与幕府2 battle script 相同）。

**含义**：
- 三国官方脚本通道的 AI 质量上限 = 脚本 AI（≈AI_Commanders 水平）
- 要"原生 AI 质量"只有两条候选：a) 验证"只 release 不建 planner"释放后单位交谁（待实测）；b) 引擎层直写字段（三国 64 位 + exe 内嵌，逆向成本高）
- 幕府2 逆向直写字段方案 = 唯一拿到原生 AI 质量的路（该项目核心价值之一）

## 迁移记录（2026-08）

- 原 5 个 lua 文件子集 → 已由全量提取取代（`../../extract/3k/script/`，1,454 文件）
- 本文件为迁移后的规范化版本；原始勘察文件与 Workshop 提取材料现均位于本项目 `work/` 下
