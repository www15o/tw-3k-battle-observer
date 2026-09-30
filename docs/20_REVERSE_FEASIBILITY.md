# 逆向可行性评估（20_REVERSE_FEASIBILITY）— 对标 shogun2 项目

> 核心问题：三国（3K）与战锤3（WH3）能否像 shogun2 项目那样做逆向？关键逻辑点能否**简单确认**？
> 评估基准：shogun2_ai_battle 项目实际走过的路（32 位内存逆向 + Ghidra + 直写字段 + 注入）。
> 方法：本地安装实测（pack 解包/格式逆向/脚本提取）+ 公开资料调研。日期：2026-08。

## 0. 基准：shogun2 项目当时的情况

| 维度 | shogun2（基准） |
|---|---|
| 位数 | 32 位（shogun2.exe，Ghidra 可完整反编译） |
| pack | PFH4/PFH5 旧格式，RPFM 可读 |
| 官方脚本 | 部分（battle script 有限；无 script_ai_planner 概念） |
| 关键逻辑点 | **全部需要逆向**：pending battle 状态机（RVA 0x10604260）、人类标志（faction+0x6a0）、AI 激活字段（a270/a28c/a290）、加载判定（FUN_107034d0）、战斗管理器（[base+0x1bc8180]）……均为 Ghidra 逐函数破解 |
| 达成手段 | 内存直写字段（s2_ai_ctl）+ CreateRemoteThread/VEH/APC 注入 + esfpy 改存档 |
| 成本 | 数月、多轮实机、大量交接文档 |

**核心结论预置**：3K 与 WH3 都是 **Rome2 系 64 位引擎**——"像 shogun2 那样纯逆向"在工具层可行（Ghidra 支持 x64），但**大多数 shogun2 项目逆向数月才得到的关键逻辑点，在这两款游戏里是官方脚本 API**——无需逆向，直接可查可调。

## 1. 三国（3K v1.7.1）评估

### 1.1 数据层（pack/DB/存档）— ✅ 完全可行，已打通

| 项 | 证据 | 难度 |
|---|---|---|
| pack 读取 | RPFM v4.3.7 完整读取 data.pack（44,189 路径）+ database.pack（1,503 表）；自研 pfh5_extract.py 亦验证通过 | 零（工具现成） |
| DB 表 | schema_3k.ron（8.7MB）本地可用；database.pack 已全量提取 | 零 |
| 脚本 | script/ 1,454 文件全量提取（含 _lib 15 核心库） | 零 |
| 存档 | ESF 格式，esfpy 工具链可复用（与幕府2 同族） | 低 |

### 1.2 查询/观测层 — ✅ **官方 API 直出（注意：仅此层）**

> ⚠️ **边界声明**：本节只覆盖"读取/查询/观战"层。**AI 操控层（原生 AI 质量）官方 API 不给**——见 §1.3 与 `3k/research/00_3K_EXTRACT_RECORD.md`「AI 质量路径对比」表（用户已论证：3K 的 script_ai_planner 与 shogun2 直写字段是**两种根本不同的机制**）。

shogun2 逆向数月才得到的**查询/观测**逻辑点，3K 官方 Lua 直接暴露：

| shogun2 逆向成果（查询层） | 3K 官方 API（已提取验证） | 确认难度 |
|---|---|---|
| pending battle 状态机/加载判定 | `query_model:pending_battle()` + `pending_battle:human_involved()` + `attacker()/defender()/secondary_attackers()` | **脚本一行** |
| 人类参战判定（faction+0x6a0） | `pending_battle:human_involved()` | **脚本一行** |
| 观战相机 | `battle:camera():move_to()` + `enable_camera_movement()` | **脚本调用** |
| 单位级接管/释放（操控层） | UnitController `take_control()/release_control()`（⚠️ 脚本控制，非原生 AI） | **脚本调用** |

**含义（修正）**：三国项目的目标1/2/3 **探测/观测阶段不需要任何逆向**（读状态、判人类、查 pending battle、观战相机全是官方脚本）；**但"目标1 = 玩家部队交原生 AI 指挥"官方 API 达不到 shogun2 的质量**——见 §1.3。

### 1.3 AI 操控层（原生 AI 质量）— ⚠️ **官方 API 不给，唯一缺口**

> ★ 用户已论证（见 `3k/research/00_3K_EXTRACT_RECORD.md`「AI 质量路径对比」）：**3K 的 AI 操作方式与 shogun2 完全不一样**。

| | shogun2（s2_ai_ctl） | 3K 官方通道（script_ai_planner） |
|---|---|---|
| 手段 | 直写军队字段（a270=0/a28c=1/a290=1.0f/a294=-1 + 单位 +0xea8/+0xc01） | `release_control_of_all_sunits()` + `set_up_script_planner()` |
| 本质 | **身份替换**：引擎认为该军队"本来就是 AI 军队" | **脚本接管**：script_ai_planner 由脚本发高层命令 |
| 决策者 | 引擎原生战斗 AI（与友军/AI 敌人同一路径） | **脚本自己**（目标选择等由 Lua 逻辑决定） |
| 质量 | 原生 AI（=友军 AI 水平） | 脚本 AI（≈AI_Commanders，用户实测"比敌人 AI 傻"） |

- 官方库查证：`generated_army` 只有 `set_up_script_planner`/`release_control_of_all_sunits`，**无军队级"原生 AI 激活"API**（无 ai_active/set_ai_control 类）
- 要**原生 AI 质量**只有两条候选：a) 验证"只 release 不建 planner"释放后单位交谁（待实测）；b) 引擎层直写字段（64 位逆向）
- 条件：64 位 exe（255MB，主逻辑内嵌）+ 无 Denuvo → **Ghidra 可分析，但地址/结构全部重新逆向**（幕府2 的经验不可直接搬，仅方法论可复用）
- 成本评估：中-高（64 位直写字段 + 注入的验证闭环需从零搭；但比 shogun2 少一个 32→64 的移植问题——本身就是 64 位）

### 1.4 官方脚本对三个目标的真实边界（2026-08 grep 实证）

> ★ 用户追问后逐条核验：**目标2（看海）、目标3（观战 AI 内战）官方脚本都不支持达成**——之前"看海/观战零成本"表述错误，此处修正。

对已提取的 3K 1,454 个与 WH3 5,787 个脚本文件全文 grep（`switch_to_cai_control/handover/grant_faction/spectat/drop_in/force_load/autoresolve` 等模式）：

| 目标 | 官方脚本能做到？ | 证据 |
|---|---|---|
| **目标1** 玩家部队交 AI 指挥 | ⚠️ 只能**脚本接管**（script_ai_planner，AI_Commanders 水平）；原生 AI 质量 ✗ | `generated_army` 无 ai_active 类 API（§1.3） |
| **目标2** 看海（玩家派系交 CAI 自主发展） | ✗ **无"玩家派系切 CAI 控制"API** | 3K `switch_to_cai_control/handover/grant_faction` **0 命中**；WH3 的 8 处 handover 全是 Nakai 区域移交脚本/传送网络事件（`handover_nakai_region()`），非派系托管 |
| **目标3** 观战 AI 内战实时战斗 | ✗ **无"强制加载 AI vs AI 战斗"API** | 3K/WH3 的 `spectat/drop_in/force_load` **0 命中**（WH3 的 spectat 仅 UI 覆写、battle_replay 仅回放脚本）；无人类参战 → 引擎自动结算（3K interventions 的 autoresolve 是结算检测，非强制加载） |

**官方脚本真实能做的**（有证据）：
1. **查询/检测**：pending battle 存在与状态、`human_involved()`、`is_human`（3K 11 处/WH3 131 处引用）、autoresolve 检测——让脚本"知道"AI 内战被结算了，但**不能**让它发生并观看
2. **单场脚本化战斗**：intro/任务战脚本可 `force_battle`/`skip_battle`（WH3 命中）——但这是脚本自己写死的流程，不是"原生 AI 指挥"，也不是"AI vs AI 内战加载"
3. **观战相机**：`battle:camera()`——**仅在战斗已被加载时**（含自定义/任务战）可用

**结论**：三个目标的**达成**（原生 AI 指挥 / 看海 / AI 内战实时观战）在 3K/WH3 **全部需要引擎层逆向**，与 shogun2 同级别难题——且 3K/WH3 **没有 hotseat 模式**（官方），看海少了一个 shogun2 系可用的旁路。官方脚本的价值 = 探测/检测/脚本战控制/已加载战斗的相机。

### 1.5 三国总体结论

> **分层看，三目标全部需要引擎层**：①**探测/查询层**官方脚本直出（零成本，用于验证闭环观测通道）；②**达成层**（目标1 原生 AI / 目标2 看海 / 目标3 观战 AI 内战）官方脚本**全部不支持**——目标1 只能脚本接管（质量差一档），目标2/3 连旁路都没有（无 hotseat、无强制加载）。**路线建议：官方脚本仅用于探测与观测通道；三个目标的达成都要走 64 位引擎层逆向（与 shogun2 同款难题，地址/结构全重新来）。**

### 1.6 WH3 同层结论

> WH3 与 3K 同属 Rome2 系 64 位分支，**同一边界适用**：查询/检测官方脚本直出（pending battle 已实证在 `cm:pending_battle_cache_*`）；目标1 只能脚本接管；目标2/3 无官方通道（无 hotseat、无强制加载 AI 战斗）→ 三目标达成均需引擎层逆向（64 位 + 版本漂移，成本高于 3K）。

## 2. 战锤3（WH3 v8.1.1）评估

### 2.1 数据层（pack/DB/脚本）— ✅ 已打通（含格式逆向）

| 项 | 证据 | 难度 |
|---|---|---|
| pack 读取 | **RPFM v4.3.7 不识别**（新 PFH5 变体）→ **本库完成格式逆向**：索引结构 + zstd 文件体，自研 pfh5_extract.py 打通 | 中（已完成） |
| DB 表 | db.pack 1,521 表全量提取（`db\<表名>\data__`，raw 二进制需 schema 解码） | 低（已有 schema_wh3.ron） |
| 脚本 | data_script.pack 5,787 文件（833 Lua）全量提取；lib_battle_manager.lua 解压验证 218KB 有效源码 | 零（已打通） |
| 存档 | .save（ESF 家族，esfpy 适配待验证） | 待勘察 |
| 官方工具 | **Assembly Kit 已发布**（2022-06）——比 3K 更完整的官方 mod 通道 | — |

### 2.2 关键逻辑点确认 — ✅ **大概率可简单确认（脚本同族）**

- WH3 脚本与 3K 同族：data_script.pack 已提取 `script/_lib` 43 个核心库，其中 `lib_battle_manager.lua`、`lib_battle_script_ai_planner.lua`、`lib_battle_script_unit.lua`、`lib_generated_battle.lua` 与 3K 同名
- **差异**：WH3 无独立的 `lib_campaign_pending_battle_cache.lua`——pending battle 功能并入 **`lib_campaign_manager.lua`（785KB）**，API 为 `campaign_manager:pending_battle_cache_*` 家族（`is_pending_battle_active`/`cache_pending_battle`/`get_attacker`/`get_defender`/`faction_is_attacker` 等，已 grep 实证 371 处引用）
- 与 3K 相同的核心概念（pending battle 查询、AI planner、相机）均以官方 API 暴露 → **确认难度：低**（函数名已部分实证）
- 差异点：WH3 是 CA 当前主力运营游戏，脚本 API 面更大（战役机制多：魔法之风/裂隙/腐化/灵魂之战/混沌魔域等）

### 2.3 引擎层 — ⚠️ 可行未启动

- 64 位 + clockwork 跨平台框架（比 3K 更新的构建管线）；无 Denuvo
- Ghidra 可分析；但 WH3 版本迭代快（buildid 24237342 为 2026 最新），**地址随更新漂移**，逆向成果保值期短
- 官方通道（Assembly Kit + 脚本）覆盖度比 3K 更高 → 引擎层逆向优先级更低

### 2.4 战锤3 总体结论

> **贴合 shogun2 的情况，且数据访问已由本库打通**：pack 格式逆向完成（zstd 变体），脚本全量可读；关键逻辑点预期可通过官方脚本简单确认（待验证）。引擎层逆向可行但优先级最低——**官方通道覆盖更全，先走官方**。

## 3. 能力矩阵对比

| 能力 | shogun2（基准） | 3K | WH3 |
|---|---|---|---|
| pack 读取 | ✅ RPFM | ✅ RPFM+自研 | ✅ **自研（新格式逆向）** |
| DB 表 | ✅ | ✅ 1,503 表 | ✅ 1,521 表 |
| 官方脚本库 | 部分 | ✅ 1,454 文件 | ✅ 5,787 文件（43 _lib 库） |
| 关键逻辑点确认 | ❌ 全部逆向 | ✅ **官方 API** | ✅ 预期官方 API |
| 引擎层逆向 | ✅（32 位） | ⚠️ 可行（64 位，成本高） | ⚠️ 可行（64 位，版本漂移） |
| 官方工具链 | 无 | 无 Assembly Kit | ✅ **Assembly Kit** |
| 存档修改 | ✅ esfpy | ✅ **esfpy 实测可读 3K startpos**（CA AB 同幕府2） | ⚠️ startpos 已证 ESF（CB AB），.save 待验证 |

## 4. 关键结论（回答"能否逆向 + 能否简单确认关键逻辑点"）

1. **能逆向**：两款游戏均无 Denuvo、64 位 exe 可用 Ghidra 分析，pack/数据层已全部打通（WH3 的 pack 新格式已由本库逆向完成）。
2. **关键逻辑点能简单确认**：3K 已实锤（pending battle / 人类判定 / AI planner / 相机 = 官方脚本 API，一行代码可查）；WH3 脚本同族，预期同样简单（待验证）。
3. **与 shogun2 的本质差别**：shogun2 是"不得不逆向"（逻辑点藏在引擎里）；3K/WH3 是"官方已暴露，逆向只是补缺"（引擎级原生 AI 质量、强制加载 AI 内战等官方未开放的能力）。
4. **路线建议**：官方脚本通道优先（零成本探测）→ Assembly Kit（WH3）/pack mod → 引擎层逆向仅当官方通道不达目标时启用。

## 5. 未核实项（诚实标注）

- WH3 关键脚本 API 与 3K 的完整差异对照（pending battle 已实证在 lib_campaign_manager.lua；其余待核对）
- WH3 .save 战役存档 esfpy 兼容性（startpos.esf 已证 ESF 魔数 CB AB）
- 3K 战役脚本加载机制（mod 覆盖 script/ 是否生效）
- 两款游戏引擎级注入的实际可行性（仅静态评估，未实机）
