# 目标2 机制地图（21_GOAL2_MECHANISM_MAP）— 三国（3K）玩家派系 CAI 自主发展（看海）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 主题：让玩家派系在战役层由 CAI（Campaign AI）自主发展（看海），玩家只观察不操作。
> 本文件 = 目标2 的机制链地图（唯一现状依据）：只收录当前成立结论，按游戏机制链组织。
> 修订/证伪历史单独收录 `22_GOAL2_LOGBOOK.md`（待建）——本文件不含任何修订文本。
> 路线视野（还有哪些路能走、哪条在挖/封死）见 `23_GOAL2_EXPLORATION_MAP.md`。
> 认知源：shogun2 目标2 看海机制（faction+0x6a0=0 + manager=FULL_MANAGER = 真看海，26_HANDOFF）+ `51_3K_MIGRATION_PLAN.md` §目标2。
> 最后更新：2026-08-21（★FACTION_SWITCH 全链深钻：handler 名字匹配循环 + 切换动作 + [faction+0xCD0] 落点 + 475 消费点 + 复位链）。

---

## 0. 目标与成功判据

- **目标**：3K 战役中玩家派系交给 CAI 自主发展（招募/进军/外交），玩家只观察，回合自动推进，可恢复人控。
- **官方边界（已确证，勿重探）**：官方脚本**无**「玩家派系切 CAI 控制」API——`switch_to_cai_control/handover/grant_faction/cai_control/transfer_control/hotseat` 3K 全 0 命中；WH3 的 6 处 handover 全是区域移交/UI 事件；`is_human` 3K 340 处全只读无 setter。3K 无 hotseat 模式。→ **看海需引擎层**（shogun2 faction 人类标志 + CAI manager 的 3K 等价物，全部待逆向）。证据：docs/70_API_AI_NATIVE_VS_SCRIPT.md §6。
- **★注意（51 蓝图 v2 勘误）**：看海不是通过 startpos.esf 实现——startpos 只调 personality；shogun2 真看海 = 运行时直写 faction+0x6a0=0 + manager=FULL_MANAGER。
- **成功判据**：玩家派系被 CAI 托管、自主行动（招募/进军），回合自动推进，战斗可发生；可恢复人控且不崩。
- **失败判据**：玩家派系卡回合 / 无行动（只过回合缺行动）/ 反向操作崩（shogun2 P40/P42：AI 改人类崩）。

---

## 0.1 机制链总览（★2026-08-19 静态补足：CAIMT 枚举 + 管理器名表锚点）

```
人类标志层    [候选] 3K faction 人类标志字段（startpos CAMPAIGN_PLAYER_SETUP[2]，待实机交叉验证）
   ▼
Manager 层    ★CAIMT 枚举定案（表序=值）：FULL=0 MAINTAINANCE=1 REBELLION=2 END_TURN=3
   │          DO_NOTHING=4 OLD_...SHOGUN2_EUROPEAN_TRADERS=5 HUMAN=6 DB=7
   │          END_TURN_ALLOW_DIPLOMACY=8 NUM=9（与 shogun2 同源）
   │          ★管理器名指针表 @0x143C101A0（.didata 12 qword；纯动态锚点，静态 0 引用）
   ▼
调度层        ★CCQ_FACTION_SWITCH_HUMAN_TO_AI @0x1434B15F8 = 战役调试命令簇成员
   │          （同簇 CCQ_EXCHANGE_UNITS/FORCE_GAME_OVER/FIGHT_QUEST_BATTLE @0x34B09E0 区）
   │          = 引擎原生「人类→AI」切换命令名（哈希注册，消费方待动态）
   ▼
行动层        [占位] CAI 决策/行动循环（招募/进军/外交）
   ▼
副作用        [占位] 恢复人控合法性 / 存档兼容 / 与目标3（b9 观战）交互
```

## 1. 官方通道性质（已确证，迁移资产）

| 通道 | 3K 现状 | 判定 | 证据 |
|---|---|---|---|
| 派系切 CAI 控制 API | 0 命中（switch_to_cai/handover/grant_faction）| 不存在 | 70 报告 §6 |
| hotseat | 0 命中；引擎串 hotseat_mode_enabled 恒假 | 无旁路 | 70 报告 §6；71 报告 §3.2 |
| `is_human` | 340 处全只读查询，无 setter | 仅观测 | 70 报告 §6 |
| FakeObserverMode（工坊）| 附庸 + 观察员传送 | 伪观察者，非真 CAI 接管 | 51 蓝图 §目标2 |

## 2. 引擎层机制链（待攻坚填充）

> [占位] shogun2 已破译的看海机制链骨架如上（§0.1），3K 等价物全部待逆向定位：
> - 人类标志：faction 对象 + 人类标志字段（3K 命名体系 is_human/human_involved，勿按 shogun2 串名找）
> - Manager：CAIMT_* 类型串 xref → CAI manager 表
> - 命令：CCQ_FACTION_SWITCH_HUMAN_TO_AI xref → 切换命令分发函数
> - 完成形态：3K 版「faction 交 CAI」直写方案（对照 shogun2 26_HANDOFF）

## 2.1 startpos 派系结构（已确证 2026-08-19，g2_faction_anchor_static §Q2）

- **3K startpos 格式 = CAAB + LZMA1 压缩**：外层 `CAMPAIGN_STARTPOS` → `LZMA1 COMPRESSED_DATA` → 内层 `CAMPAIGN_ENV > CAMPAIGN_MODEL > WORLD > FACTION_ARRAY`（**272 派系**）。esfpy **不兼容**（0x26 类型截断）→ 自研 `work/esf_3k_parse.py` 完整打通（含 esfpy 3K 适配补丁）。
- FACTION 结构：`[0]=序号、[1]=key` + 子记录；**人类标志候选 = CAMPAIGN_PLAYER_SETUP[2]**（startpos 全 False，语义推断中-高，对照 shogun2 H48c 的 PLAYER_SETUP[2]）；国库在 FACTION_ECONOMICS（刘备 3500）。
- 主战役**仅 startpos_historical.esf**（演义/史实为运行时切换）。
- ★战略含义：**目标2 看海的"玩家派系→CAI"大概率不是改 startpos**（startpos 只调 personality，51 v2 勘误）——但 **PLAYER_SETUP[2] 是人类标志的存档侧证据**，可交叉验证运行时 faction 人类标志字段。

## 2.2 faction 对象运行时锚定（三通道，g2_faction_anchor_static §Q3）

| 通道 | 方法 | 工具 | 状态 |
|---|---|---|---|
| A. 国库值差分 | Frida Memory.scan 找 int32 国库值（FACTION_ECONOMICS 可读存档对照）| work/probe_faction_scan.py | ⬜ 实机 |
| B. faction key 字符串反查 | 内存搜 faction key（"3k_main_liu_bei" 等）→ x64 指针反查对象 | 同上 | ⬜ 实机 |
| C. vtable 扫描 | faction 对象 vtable 特征（Ghidra 后）| 待 Ghidra | ⬜ |

## 2.3 官方观测层 + 强制 AI 内战（已确证，g2_faction_anchor_static §Q1/Q5）

- 看海态官方可观测：`FactionTurnStart/End`、`WorldStartOfRoundEvent`、`PendingBattle` 事件 + `cm:query_faction():is_human/treasury/region_list` + `pending_battle:human_involved()`（引擎串 @0x3471468）。
- **★可强制 AI 内战**：`apply_automatic_diplomatic_deal` 宣战条约（dlc07_imperial_intrigue L265-291 实证）→ emergent faction 参战 → 目标3 素材（看海 mod 注册事件日志捕获）。
- **manager 类型族同源铁证**：`CAIMT_OLD...WAS_SHOGUN2_EUROPEAN_TRADER` 字符串（engine_scan_extra @0x34B1C70 区）= shogun2 manager 类型族直接对应；`CAI_FACTION_MANAGER_MANAGER` @0x34B4B64 + `CCQ_FACTION_SWITCH_HUMAN_TO_AI` @0x34B09E0 = 目标2 引擎入口。

## 2.4 ★CAIMT 枚举定案 + 管理器名指针表（已确证 2026-08-19，05_LOGBOOK 补足轮）

- **CAIMT 枚举（表序 = 值）**：`CAIMT_FULL_MANAGER`@0x1434B27E0 = **0**、`CAIMT_MAINTAINANCE_MANAGER`@0x1434B27F8 = 1、`CAIMT_REBELLION_MANAGER`@0x1434B2818 = 2、`CAIMT_END_TURN_MANAGER`@0x1434B2830 = 3、`CAIMT_DO_NOTHING_MANAGER`@0x1434B2848 = 4、`CAIMT_OLD_..._SHOGUN2_EUROPEAN_TRADERS_MANAGER`@0x1434B2870 = 5、**`CAIMT_HUMAN`@0x1434B28D0 = 6**、`CAIMT_DB`@0x1434B28E0 = 7、`CAIMT_END_TURN_ALLOW_DIPLOMACY`@0x1434B28F0 = 8、`CAIMT_NUM`@0x1434B2910 = 9。
  - 与 shogun2 对照：HUMAN 从 7 → 6（因插入 OLD/DB），枚举同源（CAIMT_OLD...SHOGUN2 串 = 铁证）。
- **管理器名指针表 @0x143C101A0**（.didata，12 个 qword：前 10 = CAIMT_* 名 VA，后 2 = CAI 设置串 0x1434B25C8/0x1434B25E8）：表基址的 qword/u32/lea 引用全 0 → **纯动态锚点**（实机 hook 字符串查找 0x1407DA9D0 或内存断点表地址）。
- **CCQ_FACTION_SWITCH_HUMAN_TO_AI@0x1434B15F8 = 战役调试命令簇成员**（同簇：CCQ_EXCHANGE_UNITS、CCQ_FORCE_GAME_OVER、CCQ_FIGHT_QUEST_BATTLE @0x34B09E0 区）——3K 引擎存在「人类→AI 切换」命令名（shogun2 FUN_10600c20 的 3K 对应名），哈希注册无静态消费方。
- **CAI 设置串簇**（off 0x34B19C0-0x34B1D30）：「描述串 + 设置名串」混排（CAI_STRENGTH_AUTORESOLVER_TEST / CAI_PERF_LOG_TURNS_PER_FILE / CAI_MEM_LOG_TURNS_PER_FILE / CAI_OUTPUT_FACTION_MAP / CAI_ENABLE_CAPTIVES_LOG + CAIMT 名）——设置系统名池模式。

## 2.5 ★CCQ 命令注册表全量提取 + FACTION_SWITCH handler（已确证 2026-08-19，本会话）

- **CCQ 注册器 = 0x141820B00**（191 注册块全提取，`work/g2_ccq_registry_all.txt`）；**注册块模式**（0x20B 步长）：`lea r9(handler) + xor r8d + lea rdx(命令名) + lea rcx + jmp 0x141820B00`。**★此前「CCQ_FACTION_SWITCH_HUMAN_TO_AI 引用者 = pendingbattle.cpp 假阳性」结论作废**（旧扫描器 lea 目标计算误差 + 后续"0 引用"结论因扫描器窗口回溯 bug 二次误报；22 LogBook L3/L4）。
- **★★★ CCQ_FACTION_SWITCH_HUMAN_TO_AI → handler 0x141B38A90**：命令存在且有实现！（注册块 @0x14015E320；handler 遍历 `[data+0x3B68]` 数组按名匹配 → 0x1419E66F0 = faction 惰性子对象创建）。**FACTION_SWITCH 切换动作 = handler 内名字匹配后的分支**（[data+0x3B68] 数组元素身份待动态确认）。
- **★CAI 管理器名/设置名注册块 + 编译期哈希（扫描器修复后重扫）**：CAI_FACTION_MANAGER_MANAGER@0x1434B5760 → 注册 @0x141B6F5FC（**哈希 0xEC05BF06**）、CAI_INTERFACE_MANAGERS@0x1434B5780 → @0x141B58F0D/+0x141BAACD9、CAI_FACTION_MANAGER@0x1434B5B58 → @0x141B594C2/+0x141B6821F、CAI_ACTIVE_FACTION@0x1434C5488 → @0x141DE0475/+0x141DEFB45、CAI_DESIGNATED_PLAYER_FACTION@0x1434BA768 → @0x1401609C1、CAI_LAST_FACTION_MANAGER@0x1434B5860 → @0x141B6FEBC、CAI_STRENGTH_AUTORESOLVER_TEST@0x1434B25E8 → @0x14015FBAF、CAI_OUTPUT_FACTION_MAP@0x1434B2700 → @0x14015F905、CAI_ENABLE_CAPTIVES_LOG@0x1434B27C8 → @0x14015F66F —— 全部经 0x1407DA9D0 注册（编译期哈希常数），**静态可达**（哈希 = 实机搜索键）。
- **其他目标3 相关 CCQ 命令**：`CCQ_SET_PENDING_BATTLE_READY_TO_START`→0x14181F6C0、`CCQ_PENDING_BATTLE_PLAYER_READY_TO_SAVE_GAME`→0x141B3A350、`CCQ_SET_PENDING_BATTLE_AUTORESOLVER_BATTLE_STANCE`→0x14181F610、`CCQ_SET_FIGHT_BATTLE_AT_NIGHT`→0x14181F420、`CCQ_SET_FIGHT_BATTLE_WITH_LARGE_ARMIES`→0x14181F4A0、`CCQ_SET_BATTLE_REINFORCEMENTS`→0x14181EFA0。
- **CAIMT 管理器名表 @0x143C101A0**：10 个 CAIMT 枚举名（表序=枚举值）+ 后 2 项 = 0x1432574C8/0x1432574E8（'camera position/target surface mode'，**修正**此前 0x1434B25C8/0x1434B25E8 的 hex 误读）；表本身静态 0 引用（纯动态锚点，hook 0x1407DA9D0 或内存断点）。

## 2.6 ★★FACTION_SWITCH 全链深钻（2026-08-21 本会话定案——静态最后一块补齐）

> 方法：注册块 → handler 全反汇编 → 切换动作调用者扫描（3k_call_xref）→ 落点字段全引擎字节模式扫描（work/g2_scan_cd0.py）。证据产物：work/g2_handler_disasm_tmp.txt / g2_switch_callers_tmp.txt / g2_cd0_access_tmp.txt。

### 2.6.1 handler 0x141B38A90 = 名字匹配循环（已确证，指令级）

```
CCQ_FACTION_SWITCH_HUMAN_TO_AI（参数 = faction key 字符串）
  → handler 0x141B38A90（注册块 @0x14015E320，参数解析 call 0x14261A7F0）
  → 检查 [cmd+8]==0（命令参数有效性）
  → 遍历 [data+0x3B68] 数组：计数 [rax+0x64]、数据 [rax+0x68]、步长 8B
  → 每元素 = faction 对象指针（★[data+0x3B68] 数组元素 = faction 对象，交叉确证）
  → 0x1419D5F10(faction) = 名字 getter：[faction+0xBF0] 懒指针 → +8 = 名字串指针
  → 0x140673800/0x140668340 = std::string length/c_str；0x142B82DD0 = 优化 memcmp
  → 名字精确匹配命中 → 0x1419E66F0(faction)
```

### 2.6.2 切换动作 0x1419E66F0（★全二进制唯一调用者 = 本 handler，已确证）

- **0x1419E66F0 全二进制仅 1 个调用者**（3k_call_xref：@0x141B38B6F）= FACTION_SWITCH 专用动作，非通用函数。
- 逻辑：`dl = !byte[faction+0xCD0]` → call `0x141453DD0(faction+0xCC0, dl)` → 若新状态==1 → 懒分配 `[faction+0xD18]`（0xD0B 对象，vtable 0x1433D7420/0x1433D7438 附近 + 3 个 DB 查询 [model+0x3B60]+0x6c/+0x70）+ `[faction+0xD10]`（0x200B 对象，26 子项循环 + 回指 [faction+0x288]）。
- **0x141453DD0 = 迷你 setter**（已确证）：`cmp [sub+0x10],dl; je ret; mov [sub+0x10],dl; mov [sub+0x48],1`；sub = faction+0xCC0 → **写 [faction+0xCD0] = dl + [faction+0xD08] = 1（脏标记）** → 即**翻转 [faction+0xCD0]**。
- **★faction 字段锚更新**：+0xBF0 名字懒指针、**+0xCC0 控制器子对象（+0x10 状态 / +0x48 脏标记）**、**+0xCD0 状态字节（= [0xCC0]+0x10）**、+0xD08 脏标记、+0xD10/+0xD18 懒分配子对象、+0x288 被引指针。

### 2.6.3 落点字段 [faction+0xCD0] = 核心控制标志（475 个全引擎访问点，已确证）

- 扫描（work/g2_scan_cd0.py，6 类字节模式 capstone 验证）：**475 个访问点**遍布战役/回合/外交/战斗准备区——`cmp [r+0xCD0],0` 为主 + 少量 `cmp ...,1` + `movzx` 读取 + `cmp ...,r8b` 寄存器比较。
- 抽查消费点：影响数值符号（0x141941F01 取负）、条件分支（0x1419C4E4E `cmp 1`）、vcall 选择（0x1404847C1）——**贯穿全引擎的核心布尔状态**，非一次性缓存。
- 0x1419E5D80 上下文：[战役管理器] 读 [0x3B68 容器+0x48] 对象（活跃 faction?）的 [0xCD0]==1 → 分支。

### 2.6.4 复位链（已确证）——世界装配时默认 0

- 0x1419DDFD0 = **全 faction [0xCD0] 清 0**（遍历同一 [data+0x3B68] 数组，dl=0 调 0x141453DD0）。
- 唯一调用者 @0x14146EC3B = 世界装配巨型 ctor（0x14146E160：0x5010/0x40/0xe0/0x10 多对象分配 + faction 数组处理 0x1419C2AE0 + [obj+0x3BA0] 装配 0x141B88770/0x141B8AC40 + stub 0x1402E0520）→ **世界加载时全部 faction 默认 0**。

### 2.6.5 语义定性（★2026-08-21 修正：is_human 人类标志；manager 落点未闭合）

- **★[faction+0xCD0] = is_human 人类标志（1=human）——已确证**：is_human 方法名注册块（@0x14011B94B）紧跟 handler **0x1415DC110** = 脚本布尔 getter（0x140364410/0x14075C220/0x14035F670 包装），**直接读 [faction+0xCD0] 返回** → 官方 `faction:is_human()` 引擎实现。
- **★切换动作语义修正**：0x1419E66F0 翻转 [faction+0xCD0]；新值==1（human）时懒分配 [faction+0xD10]（=关系/阵营列表容器，0x1415DC400 遍历）+ [faction+0xD18]（=human 数据对象，挂 [model+0x1D10]）——**子对象是 human 控制数据，非 CAI manager**；FACTION_SWITCH = 调试用「人类↔AI 标志翻转」，**单独执行大概率不足看海**（无 manager 同步）。
- **★Manager 落点未闭合（静态边界）**：CAIMT 枚举（FULL_MANAGER=0..HUMAN=6..NUM=9）的实际消费字段静态未找到——CAI 名注册哈希单向、CAIMT 表纯动态锚点、值 6 扫描太泛；**剩余路径 = 实机动态差分**（faction 锚定后 diff player vs AI faction，找存 0-9 小整数的字段 / 对比 [faction+0xCC0] 控制器对象内部）。详见 22 LogBook L5（尝试路径全记录）。
- **看海达成（shogun2 语义对照）**：大概率需要 **人类标志 [faction+0xCD0]=0 + manager 字段=FULL_MANAGER(0) 双写**——3K manager 字段位置是目标2 实机的首要动态任务。

### 2.6.6 目标2 实机验证序列（★压缩后开工用）

1. **faction 锚定**（probe_faction_scan.py 已修 NativePointer 兼容）：国库差分 / key 指针反查
2. **方向验证**：读 player faction vs AI faction 的 [0xCD0]（预期不同）
3. **hook 0x141B38A90**：抓 FACTION_SWITCH 触发（参数 = faction key）
4. **直写翻转 [faction+0xCD0]**（对照 battle_ai 值字节注入模式）→ 观测回合行为（FactionTurnStart/End + PendingBattle 事件，官方零成本）
5. **恢复**：反向翻转 [0xCD0] → 观测是否安全回人控（对照 shogun2 P40/P42 反向崩风险）

## 2.7 ★★实机成果（2026-08-21 实机轮，全部动态验证；堆地址重启后失效）

> 工具：work/goal2_live.py（锚定/差分/写/hook）+ live_probe_*.py + live_mgr*.py + esf_3k_parse.py（已修 SAVE_GAME 根解压）。

### 2.7.1 faction 锚定通道（实机确证）
- **hook 0x1419D5F10（faction 名字 getter）= 自动枚举 faction 表**（51+ 对象，is_human=1 的唯一 = 玩家）。实机：曹操 = 0x22A7B9D0（is_human=1）、其余 50 AI = 0。
- faction 对象：vtable = 0x14349BAD8（所有 faction 相同）；+0x18 = 0x14349BAE0（静态函数表）；**+0xCC0 = 内联 dword（非对象指针，如曹操 0x17）**；+0xCD0 = is_human 字节；+0xD08 脏标记；+0xD10 关系容器；+0xD18 human 数据；+0xE58 = mgr_mgr（faction 专属，dump 为共享对象容器非 manager 表）；+0xD28 = 哈希容器。

### 2.7.2 is_human 实机铁证 + 存档侧同步
- **写 [曹操+0xCD0]=0 → 回合自动过**（引擎不再等玩家输入）——is_human 语义实机确认；但**无 CAI 自主行动**（空转）。
- **存档侧同步**：自动存档解析（esf_3k_parse.py 修 CAMPAIGN_SAVE_GAME 根后解压成功）——曹操 CAMPAIGN_PLAYER_SETUP **[2]=False（跟随内存写入同步保存）、[3]=True（玩家标志，唯一）**。
- **★manager 表不在存档**（shogun2 同源：NewGame 构建、读档不重建——26/31_HANDOFF 已证）→ 存档无法直接给 manager。

### 2.7.3 ★3K manager 架构（实机破解）
- **全局 CAI 管理器管理器 = 0x22A61800**（hook 0x1419C2BE0 的 rcx 恒为它；含 vtable 0x1434A03E8 + 内嵌 '3k_main_dummy_army' 字符串 + 记录区指针）。
- **记录 = 40B 池块**（hook 0x1419C2BE0 onLeave 抓 rec 实读）：+0x00 对象指针、**+0x08 = CAIMT 类型**（0 FULL/4 DO_NOTHING/5 OLD 实测）、+0x18 计数、+0x20 池链指针、+0x28 回指对象；记录区 0x7FF4EA13xxxx（大堆段）。
- **查找链**：0x1419E50C0(mgr) → 0x1419C2BE0(mgr, key) 三级哈希查找（一级[+0x4C]/[+0x50] → 二级 → 三级 96B 步长）→ **无记录返回 0x0 → 默认 6(HUMAN)**。key = faction key 字符串对象（0x385Bxxxx 区，内嵌反转存储字符串）。
- **★实验判定（2 次均无自主行动）**：
  1. 只 is_human=0 → 自动过回合空转
  2. **伪造记录返回 FULL**（hook 0x1419C2BE0 onLeave 替换 6878 次）→ 仍无行动 → **记录池返回 FULL 不是激活条件**（或伪造缺 +0x20 池链/+0x28 回指）
- **CAIMT 名注册链（静态新发现）**：CAIMT_NUM@0x1434B2910 → 引用 @0x14015FD3A → **0x14015FD20 = CAIMT 名 tweaker 注册**（**0x14034BB80 = 通用 8 参 tweaker 注册器**（battle_ai 同款！）+ 名串 → 全局 **0x143C103E0**，静态 0 引用=纯动态锚点）。

### 2.7.4 ★WH3 对照（wh3 docs/21 已静态全闭合，本目标借鉴）
- WH3 manager 表 = [mgr+0x30] 0x10 步长条目（{对象,id}）；**名→id 比对 0x142A510CC（FULL_MANAGER 12B）→ 写表 0x142A59A44**；切 AI 链尾部有**投票管理器注册 0x142574BC4**。
- WH3 3K 对照提示：名注册 lea rdx,"HUMAN"/"FULL_MANAGER" + intern + 表写入特征扫——3K 已命中「名注册」（0x14015FD20 → 0x143C103E0）。
- **★3K 下一步关键**：找「名→id + 写表」= 0x143C103E0 的消费方（hook 0x14034BB80 抓注册结构 或 搜写 [记录池+8] 代码）；验证投票管理器注册是否切 AI 必需（WH3 尾部动作）。

### 2.7.5 ★压缩后继续实机序列（堆地址重锚定）
1. **重锚定**：hooknames 收集 faction 表 → is_human=1 定位曹操（新地址）；hook 0x1419C2BE0 抓 mgr（0x22A61800 也可能变）
2. **找记录池插入链**：hook 0x14034BB80（tweaker 注册器）抓 CAIMT 名注册 → 0x143C103E0 结构 → 名→id → 写表函数 → 给曹操插真 FULL 记录（含 +0x20 池链）
3. **验证**：插真记录后过回合观察；仍无效则测投票管理器注册（0x141911900 READY 链 / 0x1434DFA08 派发表）
4. 恢复人控验证（is_human=1 反向）

### 2.7.6 ★★★manager 机制静态全闭合（2026-08-21，22 L7 修正；推翻 §2.7.3 部分认知）
> 静态反汇编 + WH3 对照 + assembly_kit 官方 db 佐证。核心修正：**0x1419C2BE0 不是 manager 表查找**（伪造它 = 伪造错表，22 L6 实验 2 失败的根因）。

- **★manager 表 = 线性表**（非哈希）：`[表+0x30]` 条目数组（**0x10 步长 {key对象, id}**）+ `[表+0x2c]` 条目数 + `[表+0x28]` 容量——**与 WH3 [mgr+0x30] 0x10 步长完全同构**。
- **★CAIMT 名→id 函数 = 0x141B94A80**（WH3 0x142A510CC 等价物，按名字符串长度比对）——完整映射：
  | 名（长度） | id | | 名（长度） | id |
  |---|---|---|---|---|
  | FULL_MANAGER(12) | 0 | | HUMAN(5) | 6 |
  | MAINTAINANCE_MANAGER(20) | 1 | | DB(2) | 7 |
  | REBELLION_MANAGER(17) | 2 | | END_TURN_ALLOW_DIPLOMACY(24) | 8 |
  | END_TURN_MANAGER(16) | 3 | | 其它 | 9(NUM) |
  | DO_NOTHING_MANAGER(18) | 4 | | | |
  ★exe 中 HUMAN_MANAGER=0 处；**HUMAN 注册名 = "HUMAN"（5 字节）**；FULL_MANAGER 字符串 2 处（VA 0x1434B27E6/0x1434B5798），xref=0x141B94AA4。
- **写表函数 = 0x141BABE80**（rdi=表, rdx=key, r8d=id）：查 [表+0x30] 找 key → 命中改 [rax+8]=id / 未命中分配新条目写 {key,id} + inc [表+0x2c]。
- **写表封装 = 0x141BABE00**（rcx=表, rdx=?, r8=名字符串）：0x141B94A80 名→id → 0x1418A96E0 取 key → 0x141BABE80。
- **★玩家 faction manager 设置入口 = 0x1419C7454**（唯一调用 0x141BABE00）：`cmp byte ptr [faction+0xCD0], 0 → je skip`——**is_human=1 才执行**，名字 lea → **'HUMAN'**（VA 0x1434A39F0）；**is_human=0 → 跳过 → 无 HUMAN 记录**。manager 表 getter = **0x141B88770 = [rcx+0xa68]**。
- **AI 批量写表 = 0x141B8AC40 系**（0x141B8ACB7/0x141B8CE48/0x141BA84FE call 0x141BABE80）：遍历列表 → 按元素类型选 id（[rdi+0x38]/[0x3c]/[0x40] 预设）→ 直接写。
- **0x1419C2BE0 重新定性** = 通用 keyed 表查找（43 调用者），96B 条目三级哈希；实机查询 key = 改革/实体 key（_selling_of_titles、work_yan_henei 等），type = 改革状态等其它语义——**非 manager 表**。
- **官方 db 佐证（assembly_kit）**：`campaign_ai_managers_tables`（3K/WH3 db_raw data__ 均 99B、GUID $1e00d973、2 行）= **{EMPTY, default}**——非 CAIMT 源；CAIMT 枚举 = 引擎硬编码名注册。
- **★实机环境澄清（用户）**：压缩前才被输入过 is_human=0；**本轮新加载存档环境曹操 is_human 应为 1（正常玩家态）**——旧地址 0x22A7B9D0 的 cd0=0 为污染残留。游戏已关闭，未及验证。
- **★看海正确路径（替代 §2.7.5）**：
  1. 新档环境：曹操 is_human=1 → 初始化 0x1419C7454 已写 HUMAN 记录到曹操 manager 表
  2. **把曹操 manager 表（[[env]+0x3ba0]+0xa68）中 HUMAN 记录 id 改 0（FULL）**，或调 0x141BABE00(表, key, "FULL_MANAGER")
  3. is_human=0（清人类标志）→ 过回合观察 CAI 自主行动
  4. 仍无效 → 投票管理器注册（WH3 0x142574BC4 等价物：0x141911900 READY / 0x1434DFA08）

### 2.7.7 ★manager 表实机拿到 + 曹操 HUMAN 记录定位（2026-08-21 新档 pid 5188；随后游戏内存崩，堆地址失效）
> 工具：work/live_mgr20_envget.py（hook 0x1414907d0 onLeave 抓 env）。**L7 静态链实机全验证**。

- **env getter 0x1414907d0 需参数（rcx）**——无参 NativeFunction 调用会 AV；正确姿势 = **hook onLeave 抓返回值**。
- **实机解引用链**：env=0x108ba34d0 → `[env+0x3ba0]`=world=0x6cbd5f90 → `[world+0xa68]`=**mgr_table=0x6db075f0**。
- **表结构实机确认**：cap=512、**count=273**、条目数组 `[表+0x30]`=0x6dd66f90（0x10 步长 {key对象,id}）。
- **★曹操 HUMAN 记录 = entry[0]**：key=0x6cc3cfa0、**id=6(HUMAN)**（玩家 faction 初始化最先写入表头）；其余 272 条 = id=7(DB)（实体默认类型）。
- **待补**：AI 的 FULL/OLD_SHOGUN2 记录未见（dump 仅 80 条）——下次 dump 全表 + 类型分布；entry[0] key 字符串归属确认。
- **★崩溃警示**：apply 写 entry0=FULL + is_human=0 后进程消失（用户报告内存崩）——下次**先 dump 验证再写、写后立即读回**、观察崩点（疑 is_human 切换后引擎访问失效对象）。

## 3. 当前前沿疑点（★2026-08-21 更新）

- [已确证] CCQ 命令注册表 191 条全量（work/g2_ccq_registry_all.txt）；FACTION_SWITCH handler = 名字匹配循环（§2.6.1）
- [已确证] 切换动作 0x1419E66F0 唯一调用者 = handler；落点 = **is_human 人类标志 [faction+0xCD0]** 翻转（§2.6.5，0x1415DC110 铁证）；475 全引擎消费点（§2.6.3）；世界装配复位（§2.6.4）；[faction+0xD10]=关系容器、[faction+0xD18]=human 数据（22 L5）
- [已确证·静态] **★Manager 机制全闭合（22 L7 / §2.7.6）**：manager 表 = 线性 [表+0x30] {key,id}；名→id = 0x141B94A80；写表 = 0x141BABE80；玩家 HUMAN 设置 = 0x1419C7454（is_human=1 才执行）；表 getter = [obj+0xa68]
- [已确证·实机] **★manager 表拿到（22 L8 / §2.7.7）**：env(0x1414907d0 onLeave) → [env+0x3ba0] → [..+0xa68]=表（cap512/count273）；**曹操 HUMAN 记录 = entry[0]（id=6）**；其余 DB(7)；游戏随后崩（堆失效）
- [待动态] **★看海激活（核心缺口收窄为实机验证）**：新档曹操 is_human=1 → 改曹操 manager 表 HUMAN→FULL（id 0）→ 观察 CAI 自主行动；is_human 方向确认（应=1）；⚠️ apply 后崩溃风险（先 dump 再写）
- [待动态] AI 的 FULL/OLD_SHOGUN2 记录位置（本表未见，dump 全表 or 另一张表）
- [待动态] 投票管理器注册是否必需（WH3 0x142574BC4 等价物：0x141911900 / 0x1434DFA08）
- [未核实] 恢复人控合法性 / AI 改人类是否崩（shogun2 P40/P42 对照）
- [未核实] 看海态与目标3（b9 观战 AI 内战）组合可行性
