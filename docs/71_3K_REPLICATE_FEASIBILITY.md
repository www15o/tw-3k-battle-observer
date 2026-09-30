# 71_3K_REPLICATE_FEASIBILITY — 三国（3K v1.7.1, 64 位）复刻 shogun2 目标3（观看 AI 内战）静态可行性评估

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 任务：纯静态评估 3K 能否直接复刻 shogun2 目标3（AI 内战 → 强制进入人类加载链 → 本地玩家自动旁观）。
> 方法：只读文档/官方 Lua 脚本/引擎字符串扫描产物（`re/3k_out/engine_scan.txt` + 本任务新增 `re/3k_out/engine_scan_extra.txt`），**不实机运行游戏**。
> 日期：2026-08。置信度标注：✅ 已确证（源码/扫描字节级实证）／🔶 推断／⬜ 未核实（需实机或 Ghidra 反编译确认）。
> 迁移源：shogun2 目标3 已达成——`[pending+0xb9]=1` 单字节直写 → fork 0 → 状态 4 → env 接口链 → battle_mgr 创建 → 本地玩家不在参战名单 → setup 0x5cf168 自动旁观（IsSpectator=1）→ 观看 AI 内战（40_GOAL3_MECHANISM_MAP §0/§3.4/§7；Goal_3_LogBook 2026-08-19）。
> 📌 路径基准（2026-08-19 迁移后）：`re/3k_out/...`、`extract/3k/...` 相对路径基准 = 本项目根 `tw3k_ai_battle/`；`40_RE_TOOLCHAIN_UPGRADE` 指 `tw3k_wh3_databank/docs/40_RE_TOOLCHAIN_UPGRADE.md`（共享参考）。

---

## 0. 结论速览（六问一句答）

1. **Q1（官方 API 能力边界）**：3K 官方 pending battle 脚本面 = **纯查询 + 快照缓存**（`lib_campaign_pending_battle_cache.lua` 全部 693 行无任何 setter/投票注入/强制加载方法）→ **不能**"强制把 AI 内战送入人类加载链"。✅ 已确证（脚本源码）。⚠️ 新发现：**3K exe 引擎字符串表存在 `get_modify_pending_battle` 接口名**（@0x346BBC8，与 `get_modify_unit`/`get_modify_campaign_ai` 同表）——官方脚本 0 处使用，能力未知（字段写？流程触发？），需引擎层反编译确认。
2. **Q2（引擎符号对照）**：3K 引擎与 shogun2 加载链**概念同源且类型名同族**：`PENDING_BATTLES::PENDING_BATTLE`（@0x3492028）、`PRE_BATTLE_VOTING_SYSTEM::FACTION_VOTE` / `VOTING_SYSTEM_BLOCK`（@0x34980A2/0x34980D8）、`FACTION_READY_TO_FIGHT` / `FACTIONS_READY_TO_FIGHT`（@0x3492208）、`BATTLE_ENV::BATTLE_ENV` 构造器（@0x34E0E19）、`EMPIREBATTLE::BATTLE_SETUP`（@0x3464C0F）、`BattleCompleted` 事件名 + `AUTORESOLVER_BAT…`（@0x3492028）。**b9 等价物候选 = 投票/就绪块（VOTING_SYSTEM_BLOCK / FACTION_READY_TO_FIGHT）**。✅ 已确证（字符串命中）；字段布局 ⬜ 未核实。
3. **Q3（官方强制加载/旁观通道）**：**无**。脚本层 `spectat/drop_in/force_load/switch_to_cai` 0 命中（仅 battle 内 `force_battle_victory()` 与 autoresolve 按钮 UI advice）；引擎串 `spectate_battles_allowed`/`remote_drop_in_battles_enabled`/`auto_resolve_all_battles` 全是**设置键**，且方向是"全自动结算"不是"全强制加载"；`SPECTATOR` 串全在 **MP lobby**（`OPEN SLOT (spectator)` 等）——与 shogun2 的"观战入口只在 MP 槽/加载后 setup"同构。→ 官方脚本层面**不能达成**目标3。✅ 已确证（grep + 扫描）。
4. **Q4（直接复刻判定）**：**今天不动引擎、纯官方通道（脚本 + startpos.esf + pack mod）不能复刻目标3**。加载钥匙 = 人类分支（引擎判定），官方无任何脚本能把 AI 内战扳进人类加载链；startpos 是战役初始状态（pending battle 是运行时瞬态对象），pack mod 只能改脚本/数据不改引擎判定。**b9 等价物定位路径（具体静态下一步）见 §4.2**——入口 = 投票块字符串 xref → 分叉判定函数 → 最小伪造字段；工具 = Ghidra x64 + CE AOB + Frida。
5. **Q5（观测通道）**：**官方脚本层可搭**——`PendingBattle` 事件（创建通知）+ `BattleCompleted` 事件（结算通知，判据 `pb:has_been_fought() and (pb:has_attacker() or pb:has_defender())` **无人类过滤**，官方 cdir 事件管理器对 AI-only 战斗有显式分支 `ai_only_battle_events`，`3k_campaign_cdir_events_data.lua:253-302/462`）→ **AI 内战被自动结算的检测 = 官方零成本通道**（对应 shogun2 验证闭环的观测层）。✅ 已确证（事件判据源码）；⚠️ `PendingBattle` 事件对 AI-vs-AI 是否触发需实机 1 轮确认。
6. **Q6（三档判定）**：
   - **(a) 官方通道直接复刻：不成立**（当前证据面）；唯一翻盘点 = `get_modify_pending_battle` 被证实暴露"写投票就绪/触发加载"能力（⬜ 未核实，可能性低——TW modify 接口族 = 字段写非流程触发，且官方脚本 0 使用）。
   - **(b) 引擎层 b9 思路迁移：可行（工作量中-高）**。入口 = `PRE_BATTLE_VOTING_SYSTEM`/`FACTION_READY_TO_FIGHT` 字符串锚 → PENDING_BATTLE 对象结构 → 分叉判定函数 → 最小伪造字段（大概率也是 1 字节就绪/投票标志）。第一步 = 建 3K Ghidra 工程 + 字符串 xref（详见 §4.2 六步）。
   - **(c) 先补静态资产**：① 3K Ghidra 工程（`re/run_ghidra_3k.ps1` 已备未跑）② 引擎字符串全量导出 ③ PENDING_BATTLE/投票块反编译 ④ `get_modify_pending_battle` 方法集反编译 ⑤ 社区 CE 表指针链参考 ⑥ 实机观测基线（需实机，超出本静态任务）。

---

## 1. Q1：3K 官方 pending battle API 能力边界

### 1.1 全部官方方法清单（✅ 已确证，脚本源码取证）

`extract/3k/script/_lib/lib_campaign_pending_battle_cache.lua`（693 行）**只做一件事**：把 `query_model:pending_battle()` 的查询结果**快照**成 Lua 表并序列化进存档（"store some data from a pending_battle, which can be saved and reaccessed later"，line 8）。**它不是引擎接口本身，是查询结果的缓存层。**

`query_model:pending_battle()`（引擎代码对象，脚本消费侧取证，30_SCRIPTING_API §2.3 + 脚本 grep 全量）：

| 方法 | 语义 | 证据 |
|---|---|---|
| `is_null_interface()` / `is_active()` | 存在性/活跃性 | lib line 52/140；`3k_campaign_cdir_global_events.lua:139-142` |
| `has_attacker()` / `attacker()` / `secondary_attackers()` | 攻方枚举（`attacker():military_force()`） | lib lines 84-101 |
| `has_defender()` / `defender()` / `secondary_defenders()` | 守方枚举 | lib lines 104-121 |
| `seige_battle()` / `ambush_battle()` / `naval_battle()` / `night_battle()` | 战斗类型判定 | lib lines 73-76 |
| `battle_type()` | **字符串**类型（"land_normal"/"settlement_unfortified"/"naval_normal"；`string.find(…,"settlement")` 用法见 interventions:2473）——**注意与 shogun2 pending+0x58 int 枚举不同编码** | lib line 78；engine_scan_extra @0x3277EB8 |
| `human_involved()` | 人类是否参战 | lib line 77 |
| `attacker_is_stronger()` | 攻方强度比较 | lib line 79；interventions:3464-3468 |
| `has_been_fought()` | 是否已结算 | `3k_dlc05_faction_ceos_titles.lua:458` |
| `attacker_battle_result()` / `defender_battle_result()` | 结算结果串（"decisive_victory" 等） | dlc05_titles:475-500；dlc07_yuan_shao:163-166 |
| `has_contested_garrison()` / `contested_garrison()` | 攻城守军 | dlc05_titles:505-509 |

缓存对象方法（全部只读）：`cache_last_pending_battle` / `get_pending_battle_cache` / `post_load_fixup` / `attacker_commander` / `defender_commander` / `num_attackers` / `num_defenders` / `num_*_units` / `num_*_unit_key` / `num_*_unit_class` / `num_*_unit_category` / `faction_was_involved/attacker/defender` / `was_character_*_in_battle`（lib lines 140-343）。

**结论（Q1a）**：官方脚本面 = **100% 查询/观测，零操控**。没有 `set_*`、没有"投票/就绪注入"、没有"强制结算/强制加载"、没有"把 AI 内战标记为人类"。**"强制把 AI 内战送入人类加载链"在官方 API 上不存在。** ✅ 已确证（脚本源码逐行）。

### 1.2 ⚠️ 新发现：引擎层存在 `get_modify_pending_battle` 接口名（🔶 需反编译确认）

补充扫描（`engine_scan_extra.txt`）命中：

```
[OK] get_modify_pending_battle x1 @0x346BBC8
  ..rde_details.get_modify_unit.get_modify_pending_battle.......get_modify_campaign_ai..get_modify_family_member..
```

上下文是一个 **scripting 接口方法名表**（同表：`get_modify_world` / `get_modify_faction` / `get_modify_character` / `get_modify_region_manager` / `get_modify_mission` / `get_modify_faction_ceo_management`…@0x346BA38/0x346C3B8/0x346C4B8）。这证明 **3K 引擎的 MODIFY_MODEL 接口绑定了 `pending_battle()` 访问器**（TW 惯例：`get_modify_X` 返回 MODIFY_X 可写接口对象）。

但：**官方脚本 0 处调用**（grep `get_modify_pending_battle|modify_pending_battle` 全 3K 脚本 0 命中）；WH3 同族脚本（`lib_campaign_manager.lua` 803KB，`pending_battle_cache_*` 63 个函数）同样 0 处调用 modify 接口，且 WH3 的 63 个函数**全部是查询**（get_/num_/is_/faction_was_…，无 setter）。→ **接口在引擎里存在 ≠ 对 Lua 开放 ≠ 有能力强制加载**。可能性评估：TW modify 接口族是"字段写"（如 modify_faction 写国库/外交），不是"流程触发"（启动一场战斗）；即使开放，最乐观也仅支持改 pending 的查询值。**判定：不能作为官方通道达成目标3 的依据；其真实方法集 = 引擎层反编译任务（列入 §4.2 ③）。**

### 1.3 3K 无独立 `lib_campaign_manager.lua`（结构差异）

glob 证实 `extract/3k/script/_lib/` 下**无** `lib_campaign_manager.lua`（WH3 才有，803KB）——3K 的 `cm:` 全局经 `lib_header.lua` 装配，pending battle 查询集中在 `lib_campaign_pending_battle_cache.lua`；脚本里 `cm:pending_battle_cache_*` 调用（如 `3k_campaign_interventions.lua:2477-2534`）是 cache 的便捷透传。✅ 已确证。

---

## 2. Q2：3K 引擎字符串扫描命中 vs shogun2 加载链符号对照

来源：`re/3k_out/engine_scan.txt`（首扫，固定 KEYS 表）+ `re/3k_out/engine_scan_extra.txt`（本任务新增，补充 40+ 模式）。exe = Three_Kingdoms.exe 243MB，ImageBase 0x140000000，0xCC 函数边界块 10,336 处（正常非混淆）。

| shogun2 加载链概念 | 3K 引擎字符串命中 | 地址 | 对照意义 |
|---|---|---|---|
| pending battle 对象（vtable 0x115fa8a4） | `PENDING_BATTLES::PENDING_BATTLE`（与 `BattleCompleted` 事件名同区）、`PendingBattle` ×4（RTTI 区） | 0x3492028 / 0x34A0378 / 0x3464BDC | **对象存在，RTTI 锚点现成** |
| 攻/守侧对象 + BATTLE_SETUP | `PENDING_BATTLES::PENDING_BATTLE_ALLIANCE attacker/defender/opponent`、`EMPIREBATTLE::BATTLE_SETUP battle_info`、`BATTLE_SETUP_INFO`/`CcoBattleSetupInfo` | 0x3464BDC-0x3464C0F / 0x37E6033 / 0x3272130 | 结构序列化描述串，Ghidra 结构恢复锚点 |
| **分叉输入（b9/ready/投票）** | **`PRE_BATTLE_VOTING_SYSTEM::FACTION_VOTE` / `PENDING_BATTLE::PRE_BATTLE_VOTING_SYSTEM` / `VOTING_SYSTEM_BLOCK` / `FACTION_READY_TO_FIGHT` / `FACTIONS_READY_TO_FIGHT`** | 0x34980A2 / 0x34980C8 / 0x34980D8 / 0x3492208 | **★b9 等价物头号候选区**（与 shogun2 同名同族投票容器） |
| 自动结算链 | `AUTORESOLVER_BAT…`（与 PENDING_BATTLE/BattleCompleted 同区）、`autoresolve` ×125、`auto_resolve_all_battles`、`use_auto_resolve_for_tiebreak` | 0x3492028 / 0x3254286 / 0x346DF38 / 0x346DFD4 | 结算路径锚点 |
| battle env（shogun2 env ctor 0x2470f0） | **`BATTLE_ENV::BATTLE_ENV (battle setup checksum)` / `(battle map definitio…`** | 0x34E0E19/0x34E0E7C | **env 构造器字符串 = 加载链锚点** |
| battle_mgr 创建链 | `battle_manager`/`battle_mgr`/`BattleManager` **0 命中**（与 shogun2 一致：battle_mgr 无字符串，靠 env 链定位）；`empire_battle` / `EMPIREBATTLE` 类名 | — / 0x3464C0F / 0x3805F70 | 需经 env/BCQ 链找 battle_mgr |
| 人类标志（faction+0x6a0） | `human_involved` ×1、`is_human` ×2、`FactionIsHuman` **0 命中**（3K 命名体系 = human_involved/is_human） | 0x3471468 / 0x331E0E8 | 人类判定查询接口名 |
| 旁观身份（env+0x281e8 IsSpectator） | `IsLocalPlayerSpectating` ×1、`IsLocalPlayerHost`/`IsLocalPlayerReady`/`ReadyButtonState`/`ToggleReady`、`SPECTATOR %S`/`OPEN SLOT (spectator)`/`(spectators %d/%d)`/`mp_ready_error_spectator` | 0x37D5DC0 / 0x359AAAA-0x359AB00 | **旁观概念 = MP lobby 层**（同 shogun2：观战入口=MP 槽/加载后 setup） |
| 命令队列（BCQ/CCQ） | `BCQ_` ×182、`CCQ_` ×191、`BCQ_FORCE_BATTLE_VICTORY`、`BCQ_FORCE_BATTLE_END`、`BCQ_FORCE_TICK`、`BCQ_CHANGE_ARMY_FACTION`、`CCQ_FACTION_SWITCH_HUMAN_TO_AI`（★看海机制同源命令）、`CCQ_FIGHT_QUEST_BATTLE` | 0x34E5450 / 0x348F6B8 / 0x34EADC0 / 0x34B09E0 | 引擎命令族完整；**CCQ_FACTION_SWITCH_HUMAN_TO_AI = shogun2 FUN_10600c20 的 3K 对应命令名**（目标2 引擎锚） |
| CAI manager（看海 manager 表） | `CAIMT_FULL_MANAGER`/`MAINTAINANCE_MANAGER`/`REBELLION_MANAGER`/`END_TURN_MANAGER`/`DO_NOTHING_MANAGER`、`CAI_FACTION_MANAGER_MANAGER`、`CAI_INTERFACE_MANAGERS`、`CAIMT_OLD_MANAGER_TYPE…WAS_SHOGUN2_EUROPEAN_TRADER` | 0x34B1BE0-0x34B1C70 / 0x34B4B64 | 与 shogun2 看海机制同源 |
| fork 概念 | `fork` ×2 = **pitchfork/rifle_butt（武器名），无分叉概念串**；`FORK`/`BattleFork` 0 命中 | 0x333C215 | shogun2 也无 fork 字符串（分叉是代码逻辑非命名）→ 分叉函数靠投票块字符串 xref 定位 |
| hotseat | `hotseat_mode_enabled` ×1（设置/查询键） | 0x346E0D8 | 3K 无 hotseat 模式（查询键恒假，60 报告已证） |
| 回放（旁路候选） | `BATTLE_HANDLER_REPLAY_START/LOAD/SAVE`、`CAMPAIGN_BATTLE_REPLAY`/`BATTLE_REPLAY_BLOCK`、`CAMPAIGN_REPLAY` | 0x3256EDF / 0x34761B9 | 回放机制存在（shogun2 H48c 旁路在 3K 有同族载体） |

**Q2 直接回答**：
- 命中 shogun2 加载链对应符号：**是，全部概念级命中**（PendingBattle / BATTLE_ENV / BATTLE_SETUP / 投票就绪 / BattleCompleted / autoresolve）。
- **"分叉输入/就绪标志"候选字符串：有**——`VOTING_SYSTEM_BLOCK`、`FACTION_READY_TO_FIGHT`、`FACTIONS_READY_TO_FIGHT`、`PRE_BATTLE_VOTING_SYSTEM::FACTION_VOTE`（@0x3498080-0x34980D8, @0x3492208）。**这就是 3K 的 b9 等价物搜索区**（shogun2 的 b9 语义 = ready==0 时让分叉判定返回 0；3K 对应判定大概率读投票块的就绪标志）。
- 引擎没有显式 `PendingBattleManager`/`BattleManager` 字符串（0 命中）——对象名与 shogun2 一样不在字符串层，靠 RTTI/类型描述串（PENDING_BATTLES 命名空间）定位。

---

## 3. Q3：官方"强制加载 AI vs AI 战斗 / 旁观"通道判定

### 3.1 脚本层（✅ 已确证，全量 grep）

对 3K 全部 1,454 脚本文件 grep `force_battle|drop_in|force_load|switch_to_cai|spectat|FACTION_SWITCH_HUMAN|spectate_battles_allowed|auto_resolve_all_battles`：

- **`force_battle` 仅 1 命中且是战斗内胜利命令**：`lib_generated_battle.lua:3112` `self.bm:alliances():item(...):force_battle_victory()`——对应 shogun2 `BCQ_FORCE_BATTLE_VICTORY`（战斗内，非战役层加载）。
- **`spectat` 仅 autoresolve 按钮 UI advice**：`3k_campaign_interventions.lua:1413-1471`（战前部署界面的"自动结算按钮"建议——玩家参战时的 UI 提示，非旁观通道）。
- **`drop_in` / `force_load` / `switch_to_cai` / `FACTION_SWITCH_HUMAN` / `spectate_battles_allowed` / `auto_resolve_all_battles`：脚本层 0 命中**。

→ 官方脚本**没有**：强制加载 AI 战斗、旁观/观战、派系切 CAI 的任何 API。与 20_REVERSE_FEASIBILITY §1.4、60_COMMAND_REPORT §2 的既有 grep 实证一致。

### 3.2 引擎字符串层（✅ 已确证，扫描）

- `spectate_battles_allowed`（@0x346DFB0）、`remote_drop_in_battles_enabled`（@0x346E04F）、`fight_human_vs_human_battles_allowed`（@0x346DF38）、`auto_resolve_all_battles`（@0x346DF38）——**全部是设置/查询键**（与 `hotseat_mode_enabled`、`use_auto_resolve_for_tiebreak` 同表区 0x346DF38-0x346E0D8）。
- **方向性关键点**：`auto_resolve_all_battles` 是把战斗**全推去自动结算**（与目标3 相反方向）；没有任何"force_load_all_battles / load_ai_battles"类键。
- `SPECTATOR` 串（@0x359AAAA-0x359AB00）全在 **MP lobby**：`OPEN SLOT (spectator)` / `SPECTATOR %S` / `(spectators %d/%d)` / `mp_ready_error_spectator` / `IsLocalPlayerSpectating`（@0x37D5DC0，与 `ReadyButtonState`/`ToggleReady` 同 lobby 界面区）——**旁观概念 = 多人联机观战槽**，与 shogun2"观战入口=MP 槽/加载后 setup 继承"完全同构：单人战役没有独立旁观入口。
- `hotseat_mode_enabled` 存在但 3K 无 hotseat 模式（60 报告已证）→ 看海/观战的 hotseat 旁路在 3K 不存在。

### 3.3 结论（Q3）

**官方脚本层面不能达成目标3**：不能强制加载（无 API）、不能旁观（无单人旁观入口）、无 hotseat 旁路。官方能做的只有**观测**（§5）与**已加载战斗内的相机操控**（battle_manager，需战斗先被加载）。✅ 已确证。

---

## 4. Q4：直接复刻判定 + b9 等价物定位路径

### 4.1 直接复刻判定：**不能**（纯官方通道，证据链）

1. **加载钥匙 = 人类分支，官方够不到**：shogun2 达成路径的关键认知 = "battle_mgr 创建链只在人类分支可达；AI 内战默认无人类参战方 → 引擎从不进加载链，直接自动结算"（40 §1/§5）。3K 同族引擎（§2 符号全命中），且官方脚本对 pending battle 只有查询（§1）——没有任何"把一个 AI 参战方标记为人类 / 注入就绪投票"的官方调用。
2. **无强制加载/旁观 API**（§3）：`force_battle` 仅战斗内胜利命令；`spectat` 仅 MP lobby；`auto_resolve_all_battles` 方向相反。
3. **startpos.esf 不是加载钥匙**：startpos = 战役**初始**状态（派系/人物/部队/外交）。pending battle 是运行时**瞬态**对象（生成→状态机→结算/加载，一个 tick 内流转，shogun2 观测到状态 6→10 极快）。即便在存档里塞一个 pending，引擎读档后只会把它当普通数据走原状态机（shogun2 从未用 startpos 达成目标3，b9 是**运行时**直写）。无任何证据表明 startpos 有"强制加载 AI 战斗"标志。🔶（startpos 结构可读 = ✅ esfpy 实证；"存档塞 pending 无效" = 🔶 推断，机理与 shogun2 同族）
4. **pack mod 只改资源/脚本/DB**，不改引擎加载判定（AGENTS 通道优先级 §0 也在说"官方可行才放弃逆向"——此处官方不可行）。
5. **引擎层是唯一通路（且已现锚点）**：§2 命中证明 3K 引擎的 pending/投票/env 机制**与 shogun2 同源同族**，b9 思路（找分叉输入最小字段伪造）可平移；只是 64 位字段布局全需重新定位。

**一句话**：3K 的"b9"在引擎里（大概率在 VOTING_SYSTEM_BLOCK/FACTION_READY_TO_FIGHT 投票块），不在官方 API/存档/mod 里。

### 4.2 b9 等价物定位路径（具体静态下一步）

**第 0 步（地基，0.5-1 天）**：建 3K Ghidra 工程——`re/run_ghidra_3k.ps1` 已备（对照 WH3 流程），导入 Three_Kingdoms.exe（243MB，x64，ImageBase 0x140000000，无 CFG/ASLR 未请求 → RVA 直用预期）；复用 `ghidra_scripts/ExportProject.java` 导出 functions/strings。

**第 1 步（对象定位，1-2 天）**：字符串 xref 三条锚线：
- ① `0x34980A2 PRE_BATTLE_VOTING_SYSTEM` / `0x34980C8 PENDING_BATTLE::PRE_BATTLE_VOTING_SYSTEM` / `0x34980D8 VOTING_SYSTEM_BLOCK` → RTTI/类型描述符 → **投票块 vtable**；
- ② `0x3492208 FACTION_READY_TO_FIGHT` / `FACTIONS_READY_TO_FIGHT` → **就绪容器 vtable**（shogun2 的 FACTION_READY_TO_FIGHT 容器 = 投票写入目标）；
- ③ `0x3492028 PENDING_BATTLES::PENDING_BATTLE` + `BattleCompleted` + `AUTORESOLVER_BAT…` 同区 → **pending 对象 RTTI + 结算发射点**（`BattleCompleted` 事件名 xref 找结算/自动结算完成代码，对应 shogun2 结算执行器链）。

**第 2 步（分叉函数定位，1-2 天）**：在 pending 对象结构内找**分叉判定函数**（shogun2 对应物 = FUN_105caa60：读 ready/b9/投票条目 → 返回 0=人类加载链 / 1=AI 结算链）。方法：以投票块字段的消费点为 xref 反向收拢；目标函数特征 = "读多个投票/就绪标志 + 分支到（a）env/battle 加载链（BATTLE_ENV::BATTLE_ENV ctor @0x34E0E19 的调用者）或（b）autoresolve 链"。**b9 等价物 = 该函数输入集的某个就绪/投票位**（shogun2 是 pending+0xb9 单字节——3K 大概率是 VOTING_SYSTEM_BLOCK 内一个字节/标志，需反编译确证）。

**第 3 步（可写接口核查，0.5 天）**：`0x346BBC8 get_modify_pending_battle` xref → 反编译 MODIFY_PENDING_BATTLE 方法集 → 回答"引擎层/脚本层能否通过该接口写就绪标志"（若可写 = 官方通道翻盘点；若只读字段 = 关闭）。

**第 4 步（加载链确认，1 天）**：`BATTLE_ENV::BATTLE_ENV` ctor 串 xref → env 装配链 → battle_mgr 创建链（shogun2：FUN_101ebfa0 → wrapper → FUN_110d22f0 → 写 [base+0x1bc8180]；3K 需重定位 battle_mgr 全局指针）→ 判定"本地玩家不在参战名单 → 自动旁观"的 3K 等价逻辑（shogun2 setup 0x5cf168；3K 候选 = `IsLocalPlayerSpectating` @0x37D5DC0 的 SP 侧消费点——注意该串在 lobby 界面区，SP 侧观察身份字段另找）。

**第 5 步（动态入口，与静态并行）**：64 位下工具链已备（40_RE_TOOLCHAIN_UPGRADE §3）：**Frida 17.17.0 已装已验**（attach/Interceptor 替代手写注入，治 shogun2 注入三连败）；CE 社区有 **3K v1.7.1 CE 表**（指针链方法可参考）；x64dbg 待装（断点级验证）。ASLR 未请求 → 预期固定基址 0x140000000，静态 RVA 直用。

**第 6 步（验证闭环，实机）**：官方 `PendingBattle`/`BattleCompleted` 事件搭观测基线（§5，零成本）→ 先录"AI 内战自动结算"基线 → 校准环路（无害已知改动）→ 再写最小伪造字段。⚠️ 本任务纯静态，实机部分留待项目启动。

---

## 5. Q5：官方脚本层 pending 状态/加载判定的可见度（观测通道）

**结论：观测通道 = 官方可搭（零逆向）**，且比 shogun2 当年（全逆向 + 外部轮询探针）便宜一个量级。

### 5.1 事件钩子（✅ 已确证，源码取证）

- **`PendingBattle` 事件**（pending battle 创建/变更通知）：
  - `3k_campaign_tutorial.lua:640-644/674-678`（`sm:state_change_listener(…, "PendingBattle", function() return true end)`）；
  - `3k_campaign_interventions.lua:1170-1179`（触发条件里直接 `context:query_model():pending_battle():defender():military_force():active_stance()`——**事件 context 带完整 pending battle 查询**）；
  - `3k_dlc05_faction_ceos_titles.lua:801`（`core:add_listener("TitlePendingBattleUnitCount", "PendingBattle", …)`）。
- **`BattleCompleted` 事件**（战斗结算通知，**含 AI-only 分支**）——`3k_campaign_cdir_events_data.lua:253-302`：
  ```lua
  core:add_listener("cdir_events_manager_battle_completed", "BattleCompleted",
    function(context)
      local pb = context:query_model():pending_battle();
      return pb:has_been_fought() and (pb:has_attacker() or pb:has_defender());  -- ★无 is_human 过滤
    end,
    function(context)
      ...
      if player_involved_in_battle(pb) then
        -- 玩家事件
      elseif pb:has_attacker() and pb:has_defender() then
        self:ai_only_battle_events(pb, attacker, defender);  -- ★AI-only 战斗显式分支
      end
    end, true);
  ```
  `ai_only_battle_events(pb, attacker, defender)` 定义于 line 462，内部用 `cm:get_human_factions()`（464）/ `faction_involved_in_battle(pb, faction_key)`（475）——**官方脚本已经显式区分并处理"无人类参战的战斗"**。→ **AI 内战被自动结算的检测 = 官方事件 + 官方查询，零成本**。
- 玩家专属事件（观察"AI 内战"不适用，仅列备）：`ScriptEventPlayerBattleCompletedSP` / `ScriptEventPlayerWinsBattleSP` / `ScriptEventPreBattlePanelOpenedSP*`（interventions:1113-3507 区）。

### 5.2 查询钩子（✅ 已确证）

`query_model:pending_battle()` 全方法见 §1.1；`cm:get_human_factions()` / `cm:query_faction(k):is_human()`（cdir_events_data:464-467）；`cm:query_model():is_player_turn()`（interventions:1176）。

### 5.3 战斗已加载后的观测（✅ 已确证，但仅覆盖已加载战斗）

`script/battle/campaign_battle/battle_start.lua:3-4`：每场战役战斗加载时执行 `bm = battle_manager:new(empire_battle:new())` → battle_manager 全家桶（相机 `enable_camera_movement`/`cache_camera`、阶段回调 `register_phase_change_callback`、watch/定时器）——**这是"战斗已加载"侧的唯一脚本钩子**（对应 shogun2 的 battle script 钩子，3K 是官方开放的）。它不解决"让 AI 内战加载"，但解决"加载后怎么看/怎么记录"。

### 5.4 结论（Q5）

**观测层（对应 shogun2 验证闭环的"造观测通道"）官方可直接搭建**：`PendingBattle`（发现 AI 内战）→ 轮询/查询（`human_involved()==false` 且攻防双方齐全 = 纯 AI 内战）→ `BattleCompleted`（确认被自动结算 + 结算结果）→ 日志/incident。⚠️ 未核实项：`PendingBattle` 事件对 **AI-vs-AI** 战斗是否触发（官方脚本只在玩家相关场景用过它；`BattleCompleted` 的 AI-only 分支是静态铁证，但 pending 创建事件需实机 1 轮确认）。

---

## 6. Q6：复刻可行性三档判定

### (a) 官方通道直接复刻 —— ❌ 不成立（当前证据面）

- 条件（若成立）：官方存在"强制加载 AI 战斗"或"旁观"API——**grep/扫描全否定**（§3）；或 `get_modify_pending_battle` 被证实暴露"写就绪投票/触发加载"——**⬜ 未核实且可能性低**（TW modify 接口族 = 字段写非流程触发；官方脚本 0 使用；WH3 同族 63 个 pending 方法全查询）。
- 判定：**在 get_modify_pending_battle 能力被反编译证实之前，官方通道按"不可行"处理**；一旦证实可写就绪标志且引擎接受，升级为可行（届时 b9 等价物 = 官方 API 一行，目标3 直接达成，AGENTS §0 通道优先级生效）。

### (b) 引擎层 b9 思路迁移 —— ✅ 可行（工作量：中-高；入口已现成）

- **为什么可行**：3K = Rome2 系 64 位分支，与 shogun2 的 pending/投票/env/battle 加载机制**概念同源、类型名同族**（§2 全命中）；shogun2 达成的"加载链完整认知 + 分叉输入最小伪造 + 自动旁观" = 现成路线图（60_COMMAND_REPORT §1 已定论）。3K 停更（v1.7.1 最终版）→ 逆向成果不漂移。
- **工作量分解**：Ghidra 工程（0.5-1 天）→ 对象/分叉函数定位（§4.2 第 1-2 步，2-4 天）→ 字段验证 + 最小伪造实验（实机，数天）→ 筛选/常驻化（对照 shogun2 E1/E2 精进清单）。比 shogun2 当年（数月、全逆向）**省掉概念破译层**，只剩 64 位字段重定位。
- **第一步**（可立即开工）：`run_ghidra_3k.ps1` 导入 exe + xref 三锚线（0x34980A2 投票系统 / 0x3492208 READY_TO_FIGHT / 0x3492028 PENDING_BATTLE RTTI）→ 找分叉判定函数 → 反编译 `get_modify_pending_battle`。
- **风险**：255MB 二进制体量（全量分析不可行，需定向）；`FactionIsHuman` 0 命中（3K 用 is_human/human_involved 命名，别按 shogun2 串名找）；battle_mgr 无字符串（走 BATTLE_ENV/env 链）。

### (c) 先补的静态资产（按优先级）

| # | 资产 | 现状 | 产出 |
|---|---|---|---|
| 1 | **3K Ghidra 工程** | ⬜ 未建（`re/run_ghidra_3k.ps1` 已备；wh3.rep 已有先例）| functions/strings 全量导出 → xref 能力 |
| 2 | **引擎字符串全量导出 + 反汇编** | 🟡 已有 2 轮定向扫描（本报告）；缺 Ghidra 侧 xref | PENDING_BATTLE/投票块/结算链函数地址表 |
| 3 | **PENDING_BATTLE 对象 + VOTING_SYSTEM_BLOCK 反编译** | ⬜ | 对象布局 + 分叉输入字段（b9 等价物候选）|
| 4 | **`get_modify_pending_battle` 方法集反编译** | ⬜ | 官方通道翻盘点裁决（(a) 档唯一悬念）|
| 5 | **battle_mgr 创建链（BATTLE_ENV ctor → 全局指针）** | ⬜ | 加载判据（对照 shogun2 [base+0x1bc8180]）|
| 6 | **社区 CE 表指针链参考**（fearlessrevolution 3K v1.7.1）| 🔶 资料已列（40_RE_TOOLCHAIN_UPGRADE §3.3）| 动态定位捷径 |
| 7 | **实机观测基线**（PendingBattle/BattleCompleted 事件实录）| ⬜ 需实机（超出本静态任务）| 确认 AI-vs-AI 事件触发 + 校准环路 |

---

## 7. 证据清单与置信度汇总

| 结论 | 置信度 | 证据 |
|---|---|---|
| 3K 官方 pending battle 脚本面 = 纯查询/缓存，无操控 | ✅ 已确证 | `lib_campaign_pending_battle_cache.lua` 全文 693 行逐方法；30_SCRIPTING_API §2.3 |
| `get_modify_pending_battle` 接口名存在于 3K exe | ✅ 已确证（存在性） | `engine_scan_extra.txt` @0x346BBC8 |
| `get_modify_pending_battle` 可写能力/脚本可用性 | ⬜ 未核实（可能性低） | 官方脚本 0 使用；WH3 同族 63 方法全查询 |
| 3K 引擎含 PENDING_BATTLE/投票系统/BATTLE_ENV 等 shogun2 同族符号 | ✅ 已确证 | `engine_scan.txt` + `engine_scan_extra.txt` 命中表（§2）|
| b9 等价物候选 = 投票/就绪块 | 🔶 推断 | 类型名同族 + shogun2 机制认知平移；字段布局待 Ghidra |
| 无官方强制加载/旁观/派系切 CAI API | ✅ 已确证 | 全量脚本 grep（force_battle 仅 battle 内；spectat 仅 UI advice；其余 0）；引擎设置键方向相反 |
| 旁观概念在 3K = MP lobby | ✅ 已确证 | SPECTATOR/OPEN SLOT (spectator)/IsLocalPlayerSpectating 串区 |
| 纯官方通道不能复刻目标3 | ✅ 已确证（组合判定） | §1+§3+§4.1 证据链 |
| startpos.esf 不能承载"强制加载" | 🔶 推断 | ESF 可读写 ✅（esfpy 实证）；pending 瞬态性 + 同族机理推断 |
| 观测通道官方可搭（含 AI-only 结算检测）| ✅ 已确证 | `3k_campaign_cdir_events_data.lua:253-302`（判据无人类过滤）+ line 462 `ai_only_battle_events` |
| `PendingBattle` 事件对 AI-vs-AI 触发 | ⬜ 未核实 | 官方脚本只在玩家场景使用；需实机 1 轮 |
| 引擎层 b9 迁移可行、3K 成果保值 | 🔶 推断（方向强） | Rome2 系同源（30_ENGINE_FAMILY）+ 3K 停更 + 符号锚点现成 |

---

## 8. 未核实项（诚实标注）

1. `get_modify_pending_battle` 的完整方法集与脚本可调性（唯一官方通道翻盘点）。
2. 3K pending 对象字段布局 / VOTING_SYSTEM_BLOCK 结构 / 分叉判定函数地址（Ghidra 反编译）。
3. 3K battle_mgr 全局指针位置（shogun2 [base+0x1bc8180] 的 3K 对应物）。
4. `PendingBattle` 事件对纯 AI 战斗是否触发（观测闭环前提）。
5. exe 运行时基址是否恒 0x140000000（ASLR 未请求 ≠ 一定固定，Exploit Protection 可强制）、CET 运行时状态（40_RE_TOOLCHAIN_UPGRADE §7）。
6. 引擎层注入（Frida attach 3K）实机可行性——工具已备未对 3K 实机。
7. 战役脚本 mod 覆盖 `script/` 是否生效（pack mod 通道的前提，50_REVERSE_ASSESSMENT 未核实项）。
8. 本报告所有结论基于纯静态（文档/脚本/字符串扫描）；实机验证属下一阶段。

---

*附件：本任务新增扫描脚本 `re/3k_extra_scan.py`、产物 `re/3k_out/engine_scan_extra.txt`；既有首扫产物 `re/3k_out/engine_scan.txt`。*
