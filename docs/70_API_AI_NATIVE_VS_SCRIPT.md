# 70_API_AI_NATIVE_VS_SCRIPT — 3K / WH3 官方脚本 API「AI 托管」能力铁证级判定

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 任务：判定全面战争：三国（3K v1.7.1）与战锤3（WH3）官方脚本 API 的「AI 托管/看海/AI 指挥」能力，是**原生型 AI**（引擎原生战斗 AI / CAI 直接接管、身份替换）还是**脚本型 AI**（Lua 脚本自己发号施令，≠ 引擎原生 AI）。
> 方法：纯静态源码取证（read/grep 官方提取脚本 + exe 字符串扫描 + 工坊 mod 实证），未实机运行。
> 结论分级：**已确证**（源码/注释/grep 直接证据）/ **推断**（命名+调用路径推导，未反编译验证）/ **未核实**（需实机验证）。
> 前置结论（已确证于本库 3k/50_REVERSE_ASSESSMENT.md §AI 操控质量缺口）：官方 script_ai_planner = 脚本接管（≈AI_Commanders 水平），≠ 原生 AI。本文把该结论从「用户论证」升级为「源码级实证」。
> 📌 路径基准（2026-09-13 整理后）：`extract/3k/...` 与 `re/3k_out/...` 相对路径基准 = 本项目根 `tw3k_ai_battle/`；`wh3/...` 基准 = `tw3k_wh3_databank/wh3/`；三国 Workshop 材料位于本项目 `work/ws_mods/`。

---

## 0. 结论速览

1. **官方 API 的「AI 托管」= 脚本型 AI，铁证成立**：所有高层决策（命令类型、目标选择、重发时机、巡逻编链、合并、监视条件）都在 Lua 层；引擎只提供一个「AI 脚本控制器」（`alliance:create_ai_unit_planner()`）作为**半自主执行器**，且其全部方法面只有 5 个（3K）/ 7 个（WH3）原语命令。
2. **不存在任何「把单位/军队交给引擎原生战斗 AI」的官方 API**：`ai_active / set_ai_control / ai_controlled / aiActiveSet / native_ai / battle_ai / scripted_ai / general_ai / give_to_ai` 在 3K 脚本全树 **0 命中**；两版 `_lib` 中唯一 AI 相关 API 就是 `create_ai_unit_planner()`。3K exe 字符串无 `FactionIsHuman`、无 `CAI_CONTROL`。
3. **`release_control_of_all_sunits()` 释放的是「脚本控制权」而非「激活原生 AI」**：官方注释明说脚本控制 = 「阻止 general AI 向这些单位发令」（lib_generated_battle.lua L3143）；释放 = 「交还 player/general AI」（L2673）。对**玩家军队**，释放后控制权回玩家（不建 planner 不下命令 = 呆立/仅反应式行为，工坊 AI_Commanders 实测「比敌人 AI 傻」）；对 **AI 军队**，释放后交还引擎一般战斗 AI（官方 quest battle 常规用法）。
4. **战役层看海：无「玩家派系切 CAI 控制」API**：`switch_to_cai / handover / grant_faction / cai_control / transfer_control / hotseat` 3K 0 命中；WH3 的 6 处 handover 全是**区域移交/UI 事件**（Nakai 区域移交函数、UI 标志、视野授予），非派系控制权移交。`is_human` 两版共 1262 处引用全为**只读查询**，无 setter。
5. **WH3 引擎符号 `BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_MOVE_TO_POSITION / RUSH_UNIT / ATTACK_UNIT` 驱动的是「脚本 AI 控制器」**（Lua planner 高层命令的引擎执行分发），不是 general battle AI 的军队级决策器（推断，置信度中-高）。
6. **分层最终判定**：战斗单位层 = 脚本控制（非 AI）；军队层 = 脚本型 AI（Lua 决策 + 引擎执行器）；战役派系层 = 无 API。shogun2 的 a270=0 直写字段「身份替换」在 3K/WH3 官方通道**无等价物**。
7. **「只 release 不建 planner」释放后单位交谁**：静态证据 → AI 军队交还引擎一般 AI（已确证语义）；玩家军队交还玩家、不构成原生 AI 托管（已确证语义 + 工坊实测）；「玩家军队 release 后引擎 battle AI 是否可能捡走」保留为**待实机验证项**（与 3k/50_REVERSE_ASSESSMENT.md 未核实项一致）。

---

## 1. 判定总表（逐层）

| 层 | shogun2（逆向基准） | 3K / WH3 官方 API | 判定 |
|---|---|---|---|
| 战斗单位层 | 单位 +0xea8/+0xc01 字段直写 = 引擎视为 AI 单位 | `UnitController:take_control()/release_control()` = 脚本控制开关；`release` 交还 player/general AI | **脚本型**（已确证） |
| 军队层 | 军队字段 a270=0/a28c=1/a290=1.0f/a294=-1 = **身份替换**，引擎认为「本来就是 AI 军队」→ 原生战斗 AI 全权指挥 | `generated_army:set_up_script_planner()` + `script_ai_planner` 高层命令（Lua 决策 + 引擎执行器）；无身份替换 API | **脚本型**（已确证） |
| 战役派系层 | faction+0x6a0=0 + manager=FULL_MANAGER = CAI 接管 | 无 API（handover 仅为区域移交/事件；is_human 只读） | **无 API**（已确证） |

---

## 2. Q1：`release_control_of_all_sunits()` 到底做了什么？释放后谁接管？

### 2.1 定义（已确证）

`extract/3k/script/_lib/lib_generated_battle.lua` L1894–1904：


**两步动作**：
1. 若该 generated_army 上挂着 script_ai_planner → `remove_sunits()`（内部调引擎 `self.planner:remove_units(unit)`，L322）并置 `script_ai_planner = nil`；
2. 对每个单位调 `script_units:release_control()` → `script_unit:release_control()`（lib_battle_script_unit.lua L905–907）→ **`self.uc:release_control()`**（引擎 unitcontroller 释放）。

`generated_army:release()`（L2326–2335）只是它的薄包装，debug 文案「releasing controlled units to the AI」。

### 2.2 引擎边界语义（官方注释，已确证）

| 证据 | 文件:行号 | 原文（关键句） |
|---|---|---|
| 脚本控制 = 摘出 general AI | lib_battle_script_unit.lua **L890–892**（3K）/ **L1053–1054**（WH3 逐字一致） | （官方原文不入库） |
| 取控制 = 阻止引擎 AI 发令 | lib_generated_battle.lua **L3142–3143**（take_control_on_message @desc） | （官方原文不入库） |
| 释放 = 交还 player/general AI | lib_generated_battle.lua **L2672–2673**（release_on_message @desc） | （官方原文不入库） |
| 释放（debug 文案） | lib_generated_battle.lua **L2695** | （官方原文不入库） |
| 释放（direct @desc） | lib_generated_battle.lua **L2326–2327**（release @desc） | （官方原文不入库） |

### 2.3 释放后谁接管（分层回答）

- **AI 方军队** → 交还**引擎一般战斗 AI（general AI）**。官方 quest battle 标准用法实证：red_cliff `ga_ai_settlement:release_on_message("start_enemy_behaviour")`（L224）、xiapi `ga_ai_main_01:release()`（L430）——脚本先把 AI 部队 hold 住（取控制防部署，L1863–1866），时机到再释放给引擎 AI 正常指挥。
- **玩家方军队** → 交还**玩家**。注释明说 "to the player"；不建 planner 不下命令 = 呆立/仅反应式行为（就近反击、fire-at-will 等 unit 级默认行为），**不会被引擎战斗 AI 捡走指挥**。
- 实机旁证（工坊 AI_Commanders，见 §7）：release + 建 planner 但 `attack_force/attack_unit/move_to_force/defend_position` 调用次数 = 0 → 玩家实测「比敌人 AI 傻」、单位各自为战——证明「释放 ≠ 原生 AI 激活」。

---

## 3. Q2：`set_up_script_planner()` 是什么？决策在 Lua 还是引擎？

### 3.1 定义（已确证）

lib_generated_battle.lua **L1871–1876**：


`script_ai_planner:new`（lib_battle_script_ai_planner.lua L82–133）核心 **L120**：


（WH3 同文件 L119 逐字一致。`alliance` = `bm:alliances()` 返回的引擎对象，见 lib_battle_script_unit.lua L124–137。）

### 3.2 planner 决策面（方法清单 = 决策面证据）

**引擎侧 `ai_planner` 方法面（grep 全树实证，唯一调用点）**：

| 引擎方法 | 3K 调用点 | WH3 调用点 |
|---|---|---|
| `add_units(unit)` | lib_battle_script_ai_planner.lua L246 | 同 L244 |
| `remove_units(unit)` | L322 | L334 |
| `move_to_position(pos)` | L489 | L514 |
| `defend_position(pos, radius)` | L769 | L794 |
| `attack_unit(unit)` | L922, L1023 | L988, L1029 |
| `rush_position(pos, radius)` | — | **L935（WH3 新增）** |
| `rush_unit(unit)` | — | **L1016, L1041（WH3 新增）** |

**共 5 个（3K）/ 7 个（WH3）原语命令 = 引擎执行器全部能力**：接收「去某地 / 守某地 / 打某单位」并半自主执行（寻路、阵型、接敌）。**没有任何目标选择、态势判断、时机决策暴露给脚本**。

**Lua 侧决策面（全部高层决策）**：

| Lua 决策 | 证据（lib_battle_script_ai_planner.lua） |
|---|---|
| 命令类型/参数选择 | `move_to_position` L461–477 / `defend_position` L732–754 / `attack_force` L933–1062 / `patrol` L1173–1261 / `merge_into` L1080–1116 / `release` L340–352 |
| 目标选择（最近敌人） | `attack_force` L951–981（可见性过滤 `is_visible` + 最近距离扫描）；`move_to_force` L621–645 |
| 重发/重定序 | 30s `reorder_interval` L492–502（move/defend）；15s `move_to_force_reorder_interval` L655–657 |
| 巡逻编链（多个 move 拼接成 patrol） | L1205–1207（逐 waypoint 摘取）、L1218（defend_position_action）、L1249–1260（抵达监视推进下一 waypoint） |
| 合并逻辑（120m 阈值移交单位） | L1119–1154 |
| 目标溃败/移动监视（bm:watch） | L546–555、L703–712、L830–852 |
| 敌人邻近测试（巡逻截击） | L1225–1246（`patrol_enemy_distance` 100m） |

### 3.3 官方头注释的自我定性（已确证）

lib_battle_script_ai_planner.lua **L8–11**（3K）/ **L9–11**（WH3 逐字一致）：

> （官方原文不入库）

- “in the past” 明确承认：玩家把部队交给 AI 的**历史功能**（旧作）→ 3K/WH3 的公开形态 = **脚本 AI 规划器**。
- “semi-autonomous” = 引擎执行器层面半自主（接敌/微操），**不是** general battle AI 的军队级自主。

**Q2 结论（已确证）**：`set_up_script_planner()` = 惰性创建 Lua `script_ai_planner`（内部包一个引擎 `create_ai_unit_planner()`）。**决策 100% 在 Lua 层，引擎 planner 只是执行器**。→ 脚本型 AI。

---

## 4. Q3：有没有官方 API 能把单位/军队交给「引擎原生战斗 AI」？

**答案：没有（已确证，全库 grep 实证）。**

| 扫描面 | 关键词 | 结果 |
|---|---|---|
| 3K `script/` 全树 | `ai_active` / `set_ai_control` / `ai_controlled` / `aiActiveSet` / `native_ai` / `battle_ai` / `scripted_ai` / `general_ai` / `is_ai_controll` | **0 命中** |
| WH3 `script/` 全树 | 同上 | 仅 2 处：lib_generated_battle.lua L2641 注释 （官方原文不入库）（同一脚本规划器体系）；一个 quest battle 脚本文件名 |
| 3K / WH3 `_lib/` 全库 | `:ai_` / `ai_unit` / `unit_ai` / `give_to_ai` / `to_ai(` / `hand_to` | 各 1 命中 = **`alliance:create_ai_unit_planner()`**（即脚本规划器的引擎执行器） |
| 3K exe 字符串 | `FactionIsHuman` | **0 命中**（re/3k_out/engine_scan.txt L20） |
| 3K exe 字符串 | `CAI_CONTROL` | **0 命中**（engine_scan.txt L36） |
| 3K exe 字符串 | `AI_SCRIPT_CONTROLLER` | 仅 `CQ_CREATE_AI_SCRIPT_CONTROLLER` / `BCQ_DESTROY_AI_SCRIPT_CONTROLLER`（创建/销毁，@0x34E76C3，L17）——即脚本 planner 的引擎对象生命周期命令，**无任何“把军队标记为 AI 军队”的命令** |

**shogun2 对照**：目标1 靠直写军队字段（a270=0/a28c=1/a290=1.0f/a294=-1 + 单位 +0xea8/+0xc01）实现**身份替换**（引擎认为该军队“本来就是 AI 军队”→ 原生战斗 AI 指挥）。3K/WH3 官方脚本 API 无等价字段写入通道，也无任何 `ai_active` 类开关。

**Q3 结论（已确证）**：官方 API 不存在「交引擎原生战斗 AI」通道；唯一可用的“交给 AI” = `script_ai_planner`（脚本型）。

---

## 5. Q4：WH3 `BCQ_AI_SCRIPT_CONTROLLER_*` 引擎符号驱动什么？

### 5.1 证据

- WH3：`wh3/50_REVERSE_ASSESSMENT.md` L60 —— `AI_SCRIPT_CONTROLLER` 7 命中族：**`BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_MOVE_TO_POSITION / RUSH_UNIT / ATTACK_UNIT`**（@0x37AAF74）。另有 `WH3_STATIC_ANALYSIS.md` L24/L31 同款。
- 3K：`re/3k_out/engine_scan.txt` L17 —— `AI_SCRIPT_CONTROLLER x6 @0x34E76C3`，字符串为 `CQ_CREATE_AI_SCRIPT_CONTROLLER` / `BCQ_DESTROY_AI_SCRIPT_CONTROLLER`。

### 5.2 判定（推断，置信度中-高）

1. **`AI_SCRIPT_CONTROLLER` = 引擎侧「AI 脚本控制器」对象**，即 Lua `alliance:create_ai_unit_planner()` 对应的引擎实体：3K 的 `CQ_CREATE_AI_SCRIPT_CONTROLLER`（创建命令）与脚本创建调用一一对应，`BCQ_DESTROY_*` 对应释放/清理。
2. **三个 `SET_OBJECTIVE_*` 命令 = planner 高层命令的 BCQ 分发名**：`SET_OBJECTIVE_MOVE_TO_POSITION` ↔ Lua `planner:move_to_position(pos)`（3K L489 / WH3 L514）；`ATTACK_UNIT` ↔ `planner:attack_unit(unit)`（L922/1023，WH3 L988/1029）；`RUSH_UNIT` ↔ WH3 新增 `planner:rush_unit(unit)`（L1016/1041）。——命令集与 Lua 调用面**完全重合**，这是「引擎命令驱动脚本 AI 控制器」的强对应。
3. **性质**：这些是**引擎原生代码**的**命令分发层**（BCQ = battle command queue，引擎内脚本→战斗引擎的命令队列，shogun2 同机制），但**目标由 Lua 决定**：谁设目标（general battle AI 的军队级决策 vs Lua planner 决策）才是“原生 vs 脚本”的分水岭。经 `script_ai_planner` 路径发出的 SET_OBJECTIVE_* = **脚本决策的高层目标**，≠ general battle AI 自主决策。
4. 保留项：未做 Ghidra 反编译验证 BCQ 分发函数内部是否与 general battle AI 共用同一 unit 级目标执行体（很可能共用，但不影响判定——决策者仍是 Lua）。

**Q4 结论（推断）**：这些引擎命令驱动的是「脚本 AI 控制器」（脚本高层目标的引擎执行器），不是原生战斗 AI 的决策器。**脚本型路径的引擎半截**，恰好证明官方通道的“AI 托管”本质上是 Lua 决策 + 引擎执行。

---

## 6. Q5：战役层看海——有无「玩家派系切 CAI 控制」API？

**答案：没有（已确证）。**

| 扫描面 | 关键词 | 结果 |
|---|---|---|
| 3K `script/` 全树 | `switch_to_cai` / `handover` / `grant_faction` / `cai_control` / `transfer_control` / `hotseat` | **0 命中** |
| WH3 `script/` 全树 | 同上 | 6 命中，**全部与派系控制权无关**（见下） |
| 3K + WH3 `_lib/` | `handover` | 0 命中 |
| 3K `script/` | `is_human` | 340 处，**全为只读查询**（`faction:is_human()` / `cm:is_human_faction()`），无 setter |
| WH3 `script/` | `is_human` | 922 处，**全为只读查询** |

WH3 的 6 处 handover 类命中逐条定性（已确证）：

| 位置 | 内容 | 性质 |
|---|---|---|
| `wh_campaign_setup.lua` L803/832/837 | `handover_nakai_region()` 本地函数 | Nakai 特殊战役**区域移交**给属国（战役经济事件） |
| `wh_campaign_scripted_tours.lua` L5931 | `"holder_transfer_controls"` | 食人魔肉类转移 UI 组件名 |
| `wh3_realm_common.lua` L220 | `context:flag_for_script_handover()` | UI/上下文标志（界域 UI 流程） |
| `wh3_realm_common.lua` L2999 | `cm:grant_faction_additional_vision(faction, region)` | **授予视野**，非控制权 |

**与 50_REVERSE_ASSESSMENT 核对**：wh3/50_REVERSE_ASSESSMENT.md L44–45（（官方原文不入库））与 3k/50_REVERSE_ASSESSMENT.md L45（（官方原文不入库））**源码级复核成立**。

**补充**：3K/WH3 均无 hotseat（0 命中）；战役层看海的官方可行为 = 工坊 FakeObserverMode 先例（附庸 + 观察员传送，`work/ws_mods/README.md`）——是**伪观察者**，非真 CAI 接管。

**Q5 结论（已确证）**：战役层无「玩家派系切 CAI 控制」API；WH3 的 handover 仅为区域移交/事件。

---

## 7. Q6：3K 官方 battle_start.lua 及同族脚本的「交 AI」范例

### 7.1 官方 `battle_start.lua` 本体（已确证）

`extract/3k/script/battle/campaign_battle/battle_start.lua`（56 行，全文已读）：
- L3–4：`load_script_libraries(); bm = battle_manager:new(empire_battle:new());`
- L26–56：按 `BattleTypeState` + 教程历史判断是否 `force_require("3k_campaign_battle_tutorial")` 或加载顾问。

**battle_start.lua 本身不含任何交 AI 代码**——它只是战役战斗脚本入口分发器。真正的官方交 AI 范式在同族史实战斗/任务战脚本中。

### 7.2 官方史实战斗的交 AI 范式（已确证，red_cliff）

`extract/3k/script/battle/historical_battle/historical_battle_red_cliff/battle_script.lua`：


- **玩家军队**：`release()` 只在过场后**交还玩家控制**（注释明说 （官方原文不入库）），从不交给引擎 AI。
- **AI 军队**：`release_on_message()` 交还引擎一般 AI；`defend_on_message()` 则走 **script_ai_planner 脚本防御命令**（generated_army:defend → L2322 `self.script_ai_planner:defend_position(v(x,y), radius)`）。
- 同族：jing_province_romance L134 `ga_ai_main_01:take_control_on_message("battle_started")`（战斗中重新夺回脚本控制）；xiapi L430 `ga_ai_main_01:release()`。

### 7.3 工坊实证：AI_Commanders（三国版「目标1」官方通道实现）

`work/ws_mods/README.md`（L22–34 引其战役版 battle_start.lua）：


**质量缺口归因（README §补充，用户实测 + 源码 diff 三方印证）**：
1. `attack_force/attack_unit/move_to_force/defend_position` 调用次数 = **0**——释放后**无任何高层目标**，只有引擎“反应式”默认行为；真正敌人军队由引擎 AI 调度器完整驱动（推进/包抄/编组/地形）。
2. 将军被移出 planner → 军队无指挥核心，单位各自为战。
3. 结论：只 release ≠ 原生 AI；必须给 planner 下目标（= 脚本 AI），或引擎层直写字段（= shogun2 路径）。

**Q6 结论（已确证）**：官方「交 AI」范例分两类——AI 军队交还引擎一般 AI（release 系）；玩家军队只能交给**脚本 AI**（script_ai_planner 命令）或**交还玩家**。没有「玩家军队 → 引擎原生战斗 AI」的官方范例（因为 API 不存在）。

---

## 8. Q7：最终判定（逐层）

### 8.1 分层判定

| 层 | 判定 | 依据（本节证据链） |
|---|---|---|
| 战斗单位层 | **脚本型**（非 AI） | unitcontroller take/release = 控制权开关；注释明说脚本控制「阻止 general AI 发令」（lib_battle_script_unit.lua L890–892；lib_generated_battle.lua L3143） |
| 军队层 | **脚本型 AI** | script_ai_planner：Lua 决策（目标/命令/重发/巡逻/合并全在 Lua）+ 引擎执行器（5/7 个原语）；引擎 planner ≠ general battle AI（§3） |
| 战役派系层 | **无 API** | 无 switch_to_cai/handover（控制权）/hotseat；is_human 只读；FactionIsHuman 3K exe 0 命中（§6） |

### 8.2 「只 release 不建 planner」释放后单位交谁

| 场景 | 静态判定 | 证据 | 状态 |
|---|---|---|---|
| AI 军队 release | 交还**引擎一般战斗 AI**（恢复原状，AI 军队本来就是 AI 管的） | lib_generated_battle.lua L2673/L2695/L2326；red_cliff L224 官方用法 | **已确证**（文档语义） |
| 玩家军队 release（不建 planner） | 交还**玩家**；玩家不下令 = 呆立/反应式行为；**不会**被引擎战斗 AI 捡走 | lib_generated_battle.lua L2673（（官方原文不入库））；工坊 AI_Commanders 实测（无目标 → “比敌人 AI 傻”） | **已确证**（语义）+ **实机旁证**（工坊实测） |
| 玩家军队 release 后引擎 battle AI 是否可能捡走 | 静态文档指向“不捡”（回玩家）；无身份替换 API 佐证 | §3/§4/§7 | **待实机验证**（保留项，与 3k/50_REVERSE_ASSESSMENT.md 未核实项一致） |

### 8.3 一句话判定

> **3K/WH3 官方脚本 API 的「AI 托管」= 脚本型 AI（Lua 决策 + 引擎 AI 脚本控制器执行），绝不是原生型 AI；不存在 shogun2 a270=0 式的「身份替换」官方通道。** 官方唯一能“把玩家部队交给 AI 动起来”的机制是 script_ai_planner（决策在 Lua，质量受脚本水平限制）；要达成 shogun2 目标1 的「原生战斗 AI 托管玩家部队」，3K/WH3 均需引擎层（64 位逆向直写字段，如 3k/50_REVERSE_ASSESSMENT.md §引擎级逆向所述）。

---

## 9. 证据表汇总（文件:行号 → 结论）

| # | 证据 | 支持结论 | 置信度 |
|---|---|---|---|
| 1 | lib_generated_battle.lua L1896–1904 `release_control_of_all_sunits()` 定义 | Q1：两步（摘 planner + 逐单位 release_control） | 已确证 |
| 2 | lib_battle_script_unit.lua L890–892 / L1053–1054（WH3 同文） | Q1：脚本控制 = 摘出 player/general AI 控制 | 已确证 |
| 3 | lib_generated_battle.lua L3142–3143 `take_control_on_message` @desc | Q1：脚本控制阻止 general AI 发令 | 已确证 |
| 4 | lib_generated_battle.lua L2672–2673 / L2695 / L2326–2327 | Q1：释放 = 交还 player/general AI | 已确证 |
| 5 | lib_generated_battle.lua L1871–1876 `set_up_script_planner()` | Q2：惰性建 Lua planner | 已确证 |
| 6 | lib_battle_script_ai_planner.lua L120 / WH3 L119 `create_ai_unit_planner()` | Q2：引擎执行器创建 | 已确证 |
| 7 | planner 引擎方法面 grep：3K L246/322/489/769/922/1023；WH3 +L935/988/1016/1041 | Q2：引擎执行器仅 5/7 原语 | 已确证 |
| 8 | planner Lua 决策面（目标扫描 L621–645/L951–981、重发 L492–502/L655–657、巡逻 L1173–1261、合并 L1080–1154、watch L546–555 等） | Q2：决策全在 Lua | 已确证 |
| 9 | 3K script 全树 grep：ai_active/set_ai_control/ai_controlled/aiActiveSet/native_ai/battle_ai/scripted_ai/general_ai = 0 命中 | Q3：无原生 AI 接管 API | 已确证 |
| 10 | `_lib/` grep `:ai_` 等 = 仅 create_ai_unit_planner | Q3：唯一 AI 相关 API | 已确证 |
| 11 | engine_scan.txt L17/L20/L36：3K exe 仅 CREATE/DESTROY_AI_SCRIPT_CONTROLLER；FactionIsHuman 0；CAI_CONTROL 0 | Q3/Q5：引擎无身份替换字符串 | 已确证 |
| 12 | wh3/50_REVERSE_ASSESSMENT.md L60：BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_MOVE_TO_POSITION/RUSH_UNIT/ATTACK_UNIT @0x37AAF74 | Q4：命令名 ↔ planner 方法一一对应 | 推断（中-高） |
| 13 | 3K/WH3 script grep：switch_to_cai/handover/grant_faction/cai_control/transfer_control/hotseat（3K 0；WH3 6 处全为区域移交/UI） | Q5：战役层无切 CAI API | 已确证 |
| 14 | is_human：3K 340 / WH3 922 处全只读 | Q5：无人类标志 setter | 已确证 |
| 15 | battle_start.lua 全文 56 行 | Q6：官方入口无交 AI 代码 | 已确证 |
| 16 | red_cliff L205–233（release/release_on_message/defend_on_message） | Q6：官方交 AI 范式（AI 军队→引擎 AI；玩家军队→玩家） | 已确证 |
| 17 | ws_mods/README.md L22–67（AI_Commanders 源码 + 质量归因） | Q1/Q7：只 release = 反应式呆立；planner 无目标 = 变傻 | 已确证（工坊实证） |
| 18 | 3k/50_REVERSE_ASSESSMENT.md L26–33/L45/L56；wh3/50_REVERSE_ASSESSMENT.md L9/L25/L44 | 前置结论复核成立 | 已确证 |

---

## 10. 未核实项 / 待实机验证

1. **玩家军队 release（不建 planner）后，引擎 battle AI 是否绝对不捡走**——静态文档与工坊实测均指向「不捡（回玩家）」，但引擎侧无直证；保留为实机验证项（与 3k/50_REVERSE_ASSESSMENT.md §未核实项一致）。
2. **3K/WH3 引擎 BCQ 分发内部**：`BCQ_AI_SCRIPT_CONTROLLER_*` 命令的 dispatch 函数是否与 general battle AI 共用 unit 级目标执行体（可能共用，不影响「脚本 vs 原生」判定，判定只看决策者）。
3. **`AI_SCRIPT_CONTROLLER` 与 general battle AI 的关系**：引擎内部 battle AI 是否也创建自己的 AI_SCRIPT_CONTROLLER（3K exe 有 CREATE/DESTROY 命令但未见非脚本路径调用证据）。
4. 3K 引擎层是否存在 shogun2 式军队字段（a270 等）——需 64 位逆向（超出本文静态脚本范围，见 3k/50_REVERSE_ASSESSMENT.md §引擎级逆向）。

---

*生成：2026-08 静态分析（脚本源码 grep/read + exe 字符串扫描 + 工坊 mod 实证），无实机运行。*
