# 目标3 机制地图（31_GOAL3_MECHANISM_MAP）— 三国（3K）观看 AI 内战（加载 + 旁观）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 主题：真正在战役中加载 AI 部队之间的战斗（观看 AI 内战），本地玩家自动旁观。
> 本文件 = 目标3 的机制链地图（唯一现状依据）：只收录当前成立结论，按游戏机制链组织。
> 修订/证伪历史单独收录 `32_GOAL3_LOGBOOK.md`（待建）——本文件不含任何修订文本。
> 路线视野（还有哪些路能走、哪条在挖/封死）见 `33_GOAL3_EXPLORATION_MAP.md`。
> 认知源：shogun2 目标3 已达成（b9=1 单字节直写 → 人类加载链 → 自动旁观）+ S1 复刻可行性报告（71 报告）。
> 最后更新：2026-08（§2.6 静态审查 + §2.7 分叉判定定位：ready 状态机 0x14193BFA3 + 0x28 元素表写者全集 + §2.8 MODIFY/QUERY 接口裁决）

---

## 0. 目标与成功判据

- **目标**：3K 战役中 AI 内战（AI vs AI）触发后，引擎加载出战斗场景（而非自动结算/闪退/卡死），本地玩家自动旁观（IsSpectator 等价身份）。
- **复刻机制（shogun2 已达成，迁移源）**：`AI 内战 pending + [pending+0xb9]=1 单字节直写（分叉输入）→ fork 0 → 状态 4 → env 接口链 → battle_mgr 创建 → 本地玩家不在参战名单 → setup 自动旁观（IsSpectator=1）→ 观看 AI 内战`。加载钥匙 = 人类分支；最小伪造 = 分叉输入字段（非登记门控/投票/人类在场）。
- **官方边界（已确证，勿重探，S1 71 报告）**：
  - 官方 pending battle 脚本面 = **纯查询**（lib_campaign_pending_battle_cache.lua 693 行零操控，无 setter/投票注入/强制加载）→ 不能「把 AI 内战送入人类加载链」。
  - 无强制加载/旁观 API：`spectat/drop_in/force_load` 0 命中；`SPECTATOR` 串全在 MP lobby；`auto_resolve_all_battles` 方向是「全结算」不是「全加载」。
  - **唯一官方翻盘点** = 引擎接口名 `get_modify_pending_battle`（★地址修正：@0x346C7C8，原记 @0x346BBC8 实为 EVENT_FEED 串）——官方脚本 0 使用；**✅ 2026-08 已裁决：返回空接口（0 方法），官方通道死**（g3t_pending_interface_verdict §1）。
- **引擎锚点（已确证命中，b9 等价物搜索区）**：`PRE_BATTLE_VOTING_SYSTEM::FACTION_VOTE`/`VOTING_SYSTEM_BLOCK`（@0x34980A2/@0x34980D8）、`FACTION_READY_TO_FIGHT`/`FACTIONS_READY_TO_FIGHT`（@0x3492208）、`PENDING_BATTLES::PENDING_BATTLE` RTTI（@0x3492028）、`BATTLE_ENV::BATTLE_ENV` ctor（@0x34E0E19）、`BattleCompleted` 事件名（71 报告 §2）。
- **成功判据**：AI 内战加载出战斗场景（battle_mgr 等价全局指针非 0）+ 本地玩家旁观身份（3K IsSpectator 等价物）+ 用户视觉确认纯 AI 互战。
- **失败判据**：自动结算（无加载）/ 静默退出 / 卡死 / 无旁观身份（滑向目标1 语义）。

---

## 0.1 机制链总览（★2026-08-20 更新：BATTLE_ENV 加载链已静态闭合，见 g3_battle_env_load_static）

```
pending 层      [占位] 3K pending battle 对象（PENDING_BATTLES::PENDING_BATTLE RTTI @0x3492028）+ 状态机
   ▼
投票/就绪层     [占位] ★b9 等价物候选：VOTING_SYSTEM_BLOCK / FACTION_READY_TO_FIGHT（@0x34980D8/@0x3492208）
   ▼
分叉判定层      [占位] 分叉函数（读投票/就绪标志 → 人类加载链 or AI 自动结算链；shogun2 FUN_105caa60 等价物）⬜ 未定位
   ▼
加载链          ✅ BATTLE_ENV 装配（静态闭合，g3_battle_env_load_static §1-§2）：
                六装配族 0x1403069D8/0x140308D04/0x140309AA9/0x14030B177/0x14030C3B2/0x14030C755
                + env 工厂三胞胎 0x141FF7230/0x141FF7550/0x141FF7350（.sbss 派发表 @0x1434DFA08，3×24B）
                → new(0x647C0) → BATTLE_ENV ctor @0x141FB6180（★真实入口；0x141FB6C76=vtable 写入中段点，
                  env vtable @0x1434E19A8 8 vfunc；BATTLE_MODEL 2MB @0x141FB812C + 嵌套 env）
                → finalize 0x141FF7030
                ⬜ 上游（装配族/派发表的调用者 = 分叉→加载 头部）静态未闭合；battle_mgr 单全局指针未发现
   ▼
旁观判定        [占位] 本地玩家不在参战名单 → 自动旁观；SP 侧字段候选 = env+0x64750（ctor 0x141FB6951，
                查询 id 0x79）/ PLAYER_SETUP 人类位（env+0x340 向量 64B/项）/ is_human 脚本方法 ID 0x19
                （注册 @0x140AAD203）；IsLocalPlayerSpectating @0x37D5DC0 已确证 = MP lobby 脚本方法名
```

## 1. 官方通道性质（已确证，迁移资产）

| 通道 | 3K 现状 | 判定 | 证据 |
|---|---|---|---|
| pending battle 脚本面 | 纯查询 + 快照缓存（693 行）| 零操控 | 71 报告 §1 |
| 强制加载 AI 战斗 | `force_battle` 仅战斗内胜利命令 | 不存在 | 71 报告 §3 |
| 旁观 API | `SPECTATOR` 全在 MP lobby | 无单人旁观入口 | 71 报告 §3 |
| `get_modify_pending_battle` | 引擎接口名存在（@0x346C7C8 修正；原记 @0x346BBC8 是 EVENT_FEED 串），官方脚本 0 使用 | ✅ 已裁决：**返回空接口（0 方法），通道死** | g3t_pending_interface_verdict §1 |

## 1.1 AI 内战素材来源（已确证 2026-08-19，g3_material_static §1）

- **AI 内战 = 引擎 CAI 决策直接创建 pending battle**，脚本层**无任何创建通道**（`create_pending_battle`/`force_pending_battle` 全脚本树 0 命中）——与 shogun2 同构。
- **★命名误解修正**：`3k_campaign_interventions.lua` 的 "intervention" = **顾问建议（advisor）系统**（4,961 行全为 `intervention:new` 建议对象 + `play_advice_for_intervention`），**不是战斗生成系统**；其对 pending 的使用仅为玩家侧顾问判据查询（:1173/:2473/:3464）。
- **产生路径图**（g3_material_static §1.4）：引擎 CAI 决策（强弱→攻/撤，battle 创建前）→ AI 军队冲突 → pending 创建（PENDING_BATTLE RTTI @0x3492028）→ ▶A PendingBattle 事件派发（@0x34A0378，对 AI 触发 ⬜）→ 投票/就绪（纯 AI → ready=0）→ 分叉判定（人类 → BATTLE_ENV 加载链 @0x34E0E19；AI → autoresolve 结算链 @0x3492028 区）→ ▶B BattleCompleted 事件（cdir_events_data.lua:253-302 → `ai_only_battle_events` :462，**官方显式处理 AI-only 战斗**）。
- **观测判定点**：A（发现）→ `human_involved()==false` 且攻防齐全（AI 内战确认）→ B（结算确认）——官方零成本。

## 2. 观测通道（★2026-08-19 修正：假设待裁决，非"官方零成本已确证"）

> ⚠️ **复盘修正（用户质疑）**：~~"AI 内战自动结算的检测 = 官方零成本"~~ 是**推断**——cdir 脚本 `ai_only_battle_events` 分支存在 ≠ 事件会派发（可能是防御代码）；**shogun2 先例：AI 内战快速结算全程引擎内完成、不经过脚本事件系统**。3K 大概率同理。**两场景待实机裁决**：
> - **场景 A（假设成立）**：BattleCompleted 对 AI-only 战斗派发 → 官方零成本观测通道成立
> - **场景 B（假设证伪，shogun2 式）**：AI 内战结算不派发脚本事件 → 观测转外部挂钩（frida 读 pending / hook 结算链），官方脚本仅覆盖玩家场景
> 裁决判据：AI 内战发生（视觉/存档证据）但无任何事件日志 → 场景 B 实锤。
- `PendingBattle` 事件（pending 创建/变更通知）+ `query_model:pending_battle()` 查询（`human_involved()==false` 且攻防齐全 = 纯 AI 内战）——**对 AI 触发 ⬜ 待裁决**。
- `BattleCompleted` 事件（结算通知）——判据 `has_been_fought() and (has_attacker() or has_defender())` 无人类过滤；cdir 有 `ai_only_battle_events` 分支（:253-302/462）——**是否对 AI-only 派发 ⬜ 待裁决**。
- **观测脚本 4 个完善点**（g3_material_static §2.2）：① null 检查 ② 显式 AI 内战判定 ③ attacker_is_stronger/is_active ④ 触发裁决。
- **b9 直写时机**：pending 生命周期瞬态（🔶）→ 直写窗口在引擎层——首选 hook PendingBattle 事件派发点（若场景 A 成立则事件驱动；场景 B 则纯引擎 hook）；轮询兜底；脚本侧只能观测不能直写。

## 2.5 ★★关键节点敲定（2026-08-20 目标3 敲定轮）：CCQ_SET_PENDING_BATTLE_READY_TO_START = 战役侧 ready 入口（与 b9 等价候选同表）

- **★★命令链全闭合**：CCQ_SET_PENDING_BATTLE_READY_TO_START（CCQ 注册块 @0x140153480）→ handler **0x14181F6C0** → 0x1419DF1C0（跳板：
cx=[data+0x3B80]; jmp）→ 0x14186FD40（
cx+=0x188; jmp）→ **核心 0x141911900**
- **★★0x141911900 语义（已确证）**：定位 **0x28 步长元素表**（[obj+0x10] 数组、计数 [obj+0xC]、步长 0x28）→ 写 **元素+0x10 = dword（ready 状态 0-5，ebx 命令值）** + **元素+0x14 = byte**；特判 ebx==2（查全局 [rip+0x273E57D]/[obj+0x34]/[obj+0x30] → bpl）、ebx==3（0x14186E7C0）、ebx==5（0x14186ED00）；条件组合后 vcall 事件 [obj+0x1BD0]+0x10
- **★★★同表闭合**：READY_TO_START 写的元素布局（**0x28 步长、+0x10 dword、+0x14 byte**）与**投票元素完全一致**（b9 等价候选所在表，72f714cb 报告：+0x10 dword/+0x14/+0x15 byte/+0x18 double/+0x20 dword，步长 0x28）→ **战役侧「准备开始」写入的就是 b9 等价候选所在的 ready 元素表** = shogun2 「[pending+0xb9]=1」的 3K 战役侧同构入口
- **★相邻 pending 配置设置器族**（0x14186Fxxx，同源）：写 [obj+0x11C]/[obj+0x11D]/[obj+0x11E] 字节标志 + vcall 事件（[rax+0x2698]/[rax+0x26C0]+0x10）；0x14186FE00 写 [obj+0xA8] dword
- **★动态锚点（目标3 实机首选）**：hook 0x141911900（抓 ready 元素写入：元素指针 + 状态值）→ 观察 AI 内战 pending 的元素值变化；hook 0x14181F6C0 抓命令参数

## 2.6 ★★静态审查定案（2026-08 本轮，g3t_static_review）：两 hook 候选裁决 + 战斗侧分叉观察点

- **★0x14201D800 裁决（✅ 字节级实证）**：= 战斗记录树节点「控制标志传播+记录拷贝」**一次性初始化函数**（写 [node+0x1A0]=flag/[node+0x1C4]=!flag，递归子节点 0x2A8 步长），**不是战斗加载入口、不是每帧**。6 直接调用者全为设置期函数（PLAYER_SETUPS 容器 0x141FBE180/0x141FF2990 + 战斗 env 方法 0x142019AB0 + 自递归）。
- **★实机不触发根因（✅ 门控链闭合）**：上游 **0x142006340 = 战斗 env provider 工厂分发器**——入口门 `[r8+1]==1 && env+0x64565==1 && env+0x64566==1 && env+0x6461d==1` 才走 provider A 创建；[r8+2]/[r8+3] 非 0 才走「→ 0x142019AB0 → 0x14201D800」分支。**人类正常战斗门为 0 → 消费者链不触发**（目标1 值字节=1 时门满足 → 6 组调用）。其余分支产出 type 2/4/5/6。
- **★0x141FB6180 裁决（✅ 复核）**：确为 BATTLE_ENV 构造入口（0x4398 栈帧 + vtable@0x141FB6C76→0x1434E19A8）；但**实机人类战斗不触发** → env 不在每战加载路径上创建（🔶 持久单例/特定模式路径）；装配族/工厂/子类 ctor 调用者全 vtable 间接（0 直接引用，✅ 负面确证）。
- **★派发表布局修正（✅）**：@0x1434DFA08 区 = **三个类表**（每类 0x20B：{类 ctor 0x141FE0860/0x141FE0AE0/0x141FE0A60, env 工厂, vtable{0x1402DFF90, 0x142006310}}）；对象 vtable=0x1434DFA18/0x38/0x58，**工厂 = 类表第 2 项（vtable-0x8）**，经类型注册表间接调用。
- **★战斗侧分叉观察点（新增实机首选）**：hook **0x142006340**（provider 工厂分发器：log env+0x64565/0x64566/0x64598/0x64599/0x6459a/0x6461c/0x6461d + 参数块 [r8+0..3] + 返回 type）——**人类战斗 vs AI 内战的门控分支差异直接可见**；hook **0x142011F10**（battle AI setup vtable 方法，每次战斗设置必触发，取 env 指针）。

## 2.7 ★★分叉判定定位定案（2026-08 投票/就绪深挖轮，g3t_voting_fork）：ready 状态机 = shogun2 FUN_105caa60 等价物

- **★分叉判定宿主 = ready 状态机 0x14193BFA3（✅ 函数级确证）**：遍历 0x28 步长 ready 元素表（[容器+0xC] 计数/[+0x10] 数组）→ 类型判定族 0x14190F380/0xF630/0xFD10/0xF900（按 [env+0x34] + 0x141853a90 查询选状态 0-4）→ **0x141911900 写回 [elem+0x10]=状态 + [elem+0x14]=byte** → **`cmp [elem+0x10],5` 分叉：状态 5 → 0x141865C20（结算链）/ 非 5 → 0x141870000（战斗参战/加载链）**。0 直接调用者（vtable 方法，宿主 [rdi]+0x60 = 战役战斗管理器环境）。
- **★G：0x28 ready 元素表写者全集（✅）** = **0x141911900 唯一写入口**，调用者仅 2：① 0x14186FD47（CCQ_SET_PENDING_BATTLE_READY_TO_START 命令链 0x14181F6C0→…，玩家/脚本路径）② 0x14193C113（ready 状态机，**AI/引擎路径——AI 内战 ready 由引擎状态机直接写，不经 CCQ 命令**）。
- **★b9 等价物候选更新**：🥇 ready 元素 [elem+0x10] 状态值（0-5，分叉直接输入）🥈 [elem+0x14] byte（0x141870000 第 5 参）🥉 注册表就绪对象（脚本镜像）。投票块填充 0x14191EC10 = describe 查询镜像（非引擎决策写）。
- **字符串锚点复核（✅）**：投票串族消费方 = getter 存根 + describe 引擎（0 外部分叉消费）；READY_TO_FIGHT 串仅 getter 存根引用（0 外部调用者）——引擎真实 ready 维护在 0x28 元素表，不经注册表就绪对象。

## 2.8 ★★MODIFY/QUERY 接口裁决 + AI 内战观测点（2026-08 g3t_pending_interface_verdict，✅ 字节级实证）

- **★裁决：MODIFY_PENDING_BATTLE_SCRIPT_INTERFACE = 空接口（0 方法，无 getter 无 setter）——官方脚本通道死**。
  接口名串 @0x14346EC20 的 19 处 capstone 验证 lea 引用 0 处在方法注册；全部 = Lua userdata 类型注册（0x141565950）+
  Lua 元方法错误存根（__add/__sub/__mul/__div/__eq/__tostring/__gc，"Incompatible types passed to operator +" 等）+
  接口对象工厂（0x1415FD350，"%s missing metatable"）+ describe（0x14163D984，"%s (%s)"）。
  **方法注册面全枚举（✅ 闭合）**：0x1403B64F0 调用者 970 处 → 394 唯一方法名；0x14152DA10 调用者 50 处 → 35 个 bulk 注册函数
  （MODEL 25 / WORLD 25 / QUERY_PENDING_BATTLE 28 / QUERY_CHARACTER 68 / QUERY_FACTION 31 等）——两者均无 MODIFY_PENDING_BATTLE 方法块。
  get_modify_pending_battle 工厂（MODEL 块 handler 0x1415D5ED0）：读 [model+0x3B80]（pending 指针）→ 0x20B 包装
  {vtable 0x143466AE8, typeinfo 0x143466B18, pending_ptr+0x18} → 0x1415FD350 按名绑元表 → 元表仅 Lua 元方法。
  ★`get_modify_pending_battle` 串真实地址 @**0x14346C7C8**（31 §1 原记 @0x346BBC8 为 EVENT_FEED 串，已修正）。
- **QUERY_PENDING_BATTLE 复核（✅）**：28 方法全只读 getter（has_attacker..has_been_fought），bulk 块 0x14011DB60
  （接口上下文 0x143C0DFD8/DFE0，注册 0x14152DA10@0x14011E2B4），handler 族读 [包装+0x18]=pending 指针 → 战役侧 getter（0x14186AD90 等）。
- **★新增：pending battle 对象指针偏移 +0x3B80（战役战斗管理器）**——CCQ 链 [data+0x3B80] / 工厂 [model+0x3B80] /
  结算处理器 0x1419C6DA0 [this+0x3B80] 三源印证 = shogun2 [base+0x1bc8180] 等价物候选（31 §3 "battle_mgr 全局指针未发现" 部分解）。
- **★新增：结算链 0x141865C20 E8 调用者全集（4）**：0x14193C537/0x14193C6B0（ready 状态机状态 5）+ 0x1418196DE
  （CCQ 区 0x141819590）+ 0x1419C6F02（战役战斗管理器方法 0x1419C6DA0，读 [this+0x3B80]）。
  战斗链 0x141870000 调用者（1）：0x14193C612（状态 ≠5）。
- **AUTORESOLVER 裁决（✅）**：CDIR_CVN_AUTORESOLVER_MODIFIER_* = 战役平衡变量名（仅 0x140EDECxx 一处）；
  'auto_resolve' = 本地化/事件名；**结算引擎无独立 AUTORESOLVER 执行函数可指认——结算动作即 0x141865C20 链**。
- **实机观测点（AI 内战确认）**：★ready 状态机（函数头 **0x14193BFB0**，0x14193BFA3 为 int3 padding——实机 hook 错地址零触发，见 §3 修正）容器实机恒空——**按用户纠正：这不能推出「投票机制不存在」（玩家在 AI 内战附近可选加入/结算/拒绝 = 投票器存在）；正确解读 = 该状态机容器非投票表**（投票表载体 = pending battle 对象内部或另一容器，见 §2.10）。AI 内战观测优先走：
  ① 官方场景 A（PendingBattle 事件 + query_model():pending_battle()，§3 实锤）② 引擎侧 hook **0x1419C6DA0**（结算处理器，读 [this+0x3B80] pending battle → 0x141865C20；调用者 0x1419D48D8/0x1419D4ACA）——
  ★**AI 内战引擎路径（非 ready 表）观测首选**（当前核心缺口 §3 的候选答案之一）③ 0x141865C20（结算动作，各路径共用）④ 0x141870000（战斗参战动作）。
- **AI 内战素材 bonus**：脚本 `force_civil_war`（MODIFY 接口族，handler 0x141537490 → 0x1415CAC10）可脚本触发内战。

## 2.9 ★★shogun2 模板对照（2026-08-21 用户批评后定案：3K 按 shogun2 已达成机制平移，勿猜「投票器是否存在」）

> shogun2 目标3 已完整达成且机制全解（shogun2_ai_battle/docs/40_GOAL3_MECHANISM_MAP.md）。3K = Rome2 系 64 位同族引擎，机制概念直接平移。**用户批评**：shogun2 早研究透（b9 伪造位/分叉/登记/状态机），3K 应按模板找对应物而非从头猜。**投票器存在是铁证**（玩家可选加入/结算/拒绝 = shogun2 战前选择三路线界面），但**分叉决定性输入 = 玩家选择 → 登记（ready），不是人类在场本身**。

| shogun2 机制（已达成） | 地址/字段 | 3K 要找的对应物 | 3K 现状 |
|---|---|---|---|
| ★分叉输入 b9 | [pending+0xb9]=1 单字节直写 | **3K pending 的 b9 等价位** | ⬜ 子代理对照中 |
| 分叉判定 | FUN_105caa60：ready==0&&b9==0→1(结算) / b9==1→0(加载) | 3K 分叉函数 | ⬜ 候选 0x14193BFB0/0x1419C6DA0 |
| ready 字段 | pending+0x55 | 3K ready 字段 | ⬜ |
| 登记 | FUN_105c4700（human_flag\|\|faction+0x6a0→ready=1） | 3K 登记函数 | ⬜ |
| 状态机 | FUN_10604260：6→5→7→8→9→10（AI 结算）；状态 4=人类等待态→加载 | 3K pending 状态机 | ⬜ |
| 状态 4 | 人类等待态 → factory → envdisp → battle_mgr | 3K 状态 4 等价 | ⬜ |
| b9 持久性 | 构造后无覆盖者 → 外部写可持久 | 3K 同验证 | ⬜ |
| 三判据 | battle_mgr 创建 + 视觉确认 + IsSpectator=1 | 3K battle_mgr/旁观字段 | ⬜ |

**3K 已有锚**：pending 指针 = [model+0x3B80]（三源印证）；ready 状态机 0x14193BFB0；0x141911900（ready 写入口）；结算链 0x141865C20；战斗链 0x141870000；0x1419C6DA0（战役战斗管理器处理 pending）。
**★当前任务（子代理 1b0f55d3）**：按模板找 3K 的 b9 等价物 + 分叉函数 + 登记函数 + pending 状态机（dump pending 对象结构对照 shogun2 字段 +0x55/+0xb9/+0x50/+0x54/+0x60/+0x64）。

## 2.10 ★★VOTING_SYSTEM_BLOCK 消费裁决 + CCQ AUTORESOLVER 链 + ready 表宿主（2026-08 g3t_voting_ready_report，✅ 字节级实证）

- **VOTING_SYSTEM_BLOCK 消费 @0x1418F1BC0 = describe 格式化引擎（非投票器/非决策链，✅）**：
  读投票块容器 [+0xC]/[+0x10] 的 **0x28 步长元素表**（+0x10 dword / +0x14 byte / +0x15 byte / +0x18 double，与 ready 表同布局）
  → 0x1407E8D20/0x1403FF030 格式化字符串；0 直接 E8 调用者（vtable 间接）。★副产品：投票块与 ready 表**共用 0x28 元素结构族**。
- **★CCQ_SET_PENDING_BATTLE_AUTORESOLVER_BATTLE_STANCE 链（玩家「选自动结算」路径）**：串 @0x143490BE0 注册 @0x140153440
  → handler 0x14181F610 → `mov rcx,[命令数据+0x3B80]`（★+0x3B80 第 4 源印证）→ **0x140ACEB30 = mov [pending+0xE8],edx**
  （pending battle 对象 +0xE8 = autoresolve stance 字段）。CCQ pending 家族 8 命令 handler 连续 0x14181F610-0x14181F830
  （AUTORESOLVER_STANCE / CAPTIVES_OPTION / READY_TO_START / SIEGE_ACTION_OPTION / DISCONNECTION_RESET /
  SETUP_INFO_SYNCHRONISED / WALL_MOUNTED_ARTILLERY_OPTION / PLAYER_READY_TO_SAVE_GAME）。
- **★战役战斗管理器对象结构（0x141865xxx 簇）**：SETUP_SYNCHRONISED → 0x1419C68E0 → **0x1418654F0**
  （写 [mgr+0x138]=4「setup 已同步」+ 事件 [mgr+0x130]+0x10；[mgr+0x138]==0xE 特判）；{+0x130 事件子对象,
  +0x138 状态 dword, +0x140/+0x148 faction 数组, +0x3B80 pending 指针}。
- **★ready 元素表容器 = pending battle 对象 + 0x188（三链闭合）**：CCQ READY 链 0x1419DF1C0: `mov rcx,[rcx+0x3B80]` →
  0x14186FD40: `add rcx,0x188` → 0x141911900。表 {+0 回指, +0xC 计数, +0x10 数组 0x28 步长}；
  ready 状态机 0x14193BFB0 的 this = 表（[rdi]→pending → +0x60 → 0x141490980 → [vtable+0xD0] 环境）。
  0x141911900 = 更新 + 移除（count-- 左移压缩）；查找 0x1418CC720 调用者 22 处全为查询族（无 add）。
  add 函数 🔶 未定位（RTTI 0x143492C28 静态闭合失败；推断 = pending 创建/参与者注册路径直接填充）。
  ★对照 §2.9 模板：该 0x28 表 = 「ready 登记表」（容器 = pending+0x188），**非投票表**——投票表载体待找（pending 对象内其它 0x28 表候选）。
- **AI 内战观测点更新**：① 0x1419C6DA0（结算处理器，读 [this+0x3B80] → 0x141865C20）★★首选 ② 0x140ACEB30
  （pending+0xE8 stance 写）③ 0x141865C20（结算动作）④ 0x1418654F0（状态机 [mgr+0x138]=4）⑤ 0x141870000（战斗动作）
  ⑥ 0x14193BFB0（ready 状态机，玩家路径）⑦ 官方场景 A（PendingBattle 事件 + pending_battle() 查询，已实锤）。

## 2.11 ★★投票流重构：投票表载体 + 玩家投票选项字段 + 分叉判定（2026-08 g3t_vote_flow_report，✅ 字节级实证）

- **★投票表载体 = 0x28 步长元素表（投票块，与 ready 表同结构族）**：元素 {+0x10 dword 投票值/状态, +0x14 byte, +0x15 byte,
  +0x18 double, +0x20 dword}；VOTING_SYSTEM_BLOCK 消费（0x1418F1BC0，describe）+ 投票块填充（0x14191EC10，★0x28 表添加机制：
  读 FACTION_VOTE/PRE_BATTLE_VOTING_SYSTEM → 扩容 0x14066FC10 → 写元素 → count++）。
  数据源 = 注册表单例 **PRE_BATTLE_VOTING_SYSTEM（@0x144050CA8, hash 0x28f6f0f1）+ FACTION_VOTE（@0x144050C88, hash 0x7b248db6）**。
- **★玩家投票选项写入 = CCQ pending 家族（handler 连续 0x14181F610-0x14181F830）→ pending 对象字段**：
  加入/开始 READY_TO_START → pending+0x188 ready 表；自动结算 AUTORESOLVER_STANCE → **pending+0xE8**；
  攻城行动 → **faction 实体 +0x88**（0x14186FE60→0x141866250 查找→写）；俘虏 → **pending+0xA8**（0x14186FE00）；
  城墙火炮 → 0x1419DE200；setup 同步 → 0x1418654F0（写 [mgr+0x138]=4）。
- **★pending battle 对象字段地图（✅）**：+0xA8 俘虏 dword / +0xE8 autoresolve stance / +0x138 状态（0/0xE=激活,
  0x141844B60）/ +0x140/+0x148 faction 数组 / +0x188 ready 元素表 / faction 实体 +0x88 攻城行动。
- **★分叉判定（读投票结果处）**：
  - **AI 路径 = 0x1419C6DA0（★核心缺口答案，✅ 完整逻辑）**：检查 [pending+0x138]∈{0,0xE}（0x141844B60）→ faction
    CAI 标志 +0xCD0 检查 → 收集攻防双方（0x141BAC920，读 [r15+0x100]→[+0x3B80] pending）→ **直接 0x141865C20 结算**。
    **不读投票表**——AI 内战静默结算 = 该链（不经 ready 表/投票表）；调用者 0x1419D48D8/0x1419D4ACA。
  - 玩家路径 = ready 状态机 0x14193BFB0（[elem+0x10] 状态 5→结算 / 1-4→战斗）。
  - ★**投票表（FACTION_VOTE 注册对象）= 查询/描述镜像**（describe 引擎读它产字符串），**非分叉输入**；
    分叉输入 = 玩家 CCQ 选择写出的 pending 字段（+0xE8 stance / +0xA8 俘虏 / ready 表状态）。
- **★目标3 伪造方向更新**：AI 内战走 0x1419C6DA0 → 结算。强制加载改写候选 = 0x1419C6F02 前插桩（改跳 0x141870000 等价战斗动作）
  或改 [pending+0x138] 状态触发另一分支（🔶 待实机确认 0x141BAC920 条件分叉）；CCQ READY_TO_START/AUTORESOLVER_STANCE 链 =
  引擎级「把 AI 内战送进人类就绪/结算表」开关候选。

## 2.12 ★★加载链静态深钻定案（2026-08-17 forkchain 轮，work/g3t_forkchain_2026-08-17.md，✅ 字节级实证）

- **★★pending 构造器定案（§2.10「add 未定位」闭环）**：**0x141837AA0**（AI 野战/攻击变体）/ **0x141838330**（攻城 type=6 / 攻击变体）；调用者 0x1419D4580/0x1419D4970/0x1419C02B0（AI 攻击创建链：release 旧 pending → `new(0x300)` → ctor（out-param=[manager+0x3B80] 赋值）→ 0x1419EC7E0 → 0x1418678B0 复位状态 1）。**对象大小 0x300；vftable=0x143491C50**（多继承基类 vftable @+0x20=0x143491C68/@+0x40=0x143491C80）；**ctor 写 [obj+0x138]=1（构造即状态 1）**；[+0x130]=事件子对象；[+0x188]=ready 表 ctor 0x1418DC010；[+0x178]=battle context 槽。
- **★★pending 状态机全定位**：状态字段 **+0x138**（合法性门 0x141844B60 ∈{1..0xD}，0/0xE 终态）；写状态族 = 共享 **0x14185B130** + 包装 0x141865420(→1)/0x141865320(→1 条件)/0x1418654F0(→4 setup 同步)/0x141865390(→5 战斗开始)；事件派发 = 0x14183CD00（[event+8]=状态，vcall +0xF50/+0x31B0 双事件于 0xE）。**tick = 0x141876280**（门 state==1：ready 状态机 + 参与者检查 + 建 +0x178 battle context(vtable 0x143491DD8，含 env 工厂槽 0x1402DFF90) + 事件 6/4/3 + army 收集）；每帧分发 = **0x141873190**（状态 2/1/7/0xC 转移可见）。状态全集观测：{0,1,2,4,5,7,0xC,0xE}。
- **★★对象同一性修正（§2.10「战役战斗管理器 0x141865xxx 簇」表述）**：0x141865C20/420/4F0/390 的 this = **[manager+0x3B80] 的 pending 对象本身**（0x1419C6F02 字节级证明）；{+0x130,+0x138,+0x140/+0x148,+0x188} 全部属 pending；「管理器」另有 +0x3B38/+0x3B68/+0x3B70/+0x3BA0/+0x2300 字段。
- **★★0x141870000 语义定案** = **faction ready 登记（战斗侧动作）**：0x141853A90 解析 faction → 遍历参与者表 [pending+0x154]/[0x158]（0x18 步长）0x14182B6F0 定位 → 写 [entry+0x10]=r8b、**[entry+0x11]=r9b（=ready 元素 [elem+0x14] 字节的流向）** + [pending+0x184]。
- **★b9 等价位细化**：🥇 ready 元素 [elem+0x14] byte（→ 参与者 +0x11）🥈 [faction+0xCD0] is_human（Fork A 输入）🥉 [pending+0x138] 状态。
- **★实机 hook 清单更新**：①0x1419C6DA0（Fork A，AI 内战首选）②0x141876280（tick，Fork B 观察）③0x141865C20（结算汇合）④0x141870000（战斗登记，改 [elem+0x14] 实验观测点）⑤0x141837AA0/0x141838330（ctor 生命周期）。
- **注入方向补充**：路线 B = 0x1419C6F02 前改跳 0x141870000（→ tick 链接管 → +0x178 battle context → env 工厂族）为与 shogun2「b9=1→状态4→加载」最接近的静态可行改写（🔶 待实机）；路线 C = 向 AI 内战 pending+0x188 注入元素置状态 1（走 Fork B 战斗侧）。

## 2.13 ★★pending ctor 级字段地图（增量：对象 0x300B + 完整布局 + b9 负面证据，2026-08 g3t_s2template_report，✅ 字节级实证）

- **★3K pending battle 对象 = 0x300B**，ctor = **0x1418363B0（主，+0x138 状态初始=1）/ 0x141836170（变体，初始=0）**
  （battle mgr ctor 0x141965680：`mov ecx,0x300; call new → call ctor → mov [mgr+0x3B80],rax`，写点 0x141967F7E/0x14196C08F 等 4 处）。
- **★ctor 字段地图（0x1418363B0 全函数反汇编）**：+0x00/+0x20/+0x40 多继承 vtable（0x143491C50/C68/C80）；
  **+0x60 = 攻侧对象指针 = [r8]（构造参数，shogun2 同偏移）**；+0x84=0x1010000；+0x8C/+0x90 float 初值；
  +0xA2 dword；+0xA8 起子对象（0x14183A1B0 ctor）；**+0xB0/+0xB4/+0xB8 = 向量 {cap,size,array}（登记容器等价物，0x141833FCC 拷贝）**；
  +0xC0..+0xCC 更多字段；**+0x130 = env 指针**；**+0x138 = 状态 dword（主=1；变更事件 [env+0xF50]+0x10，特判 0xE→[env+0x31B0]+0x10）**；
  **+0x140/+0x148 = 攻/守参与者数组**（new(0x28) + 0x141838AB0 条目 ctor + 0x14182FFF0 注册 r8d=0/2）；
  +0x150..+0x184 战场设置数据；**+0x188 = ready 表子对象（0x1418DC010 ctor）**；+0x1B8..+0x1E0 字段（+0x1CC=0xFFFFFFFF）；
  +0x1E8/+0x1F8/+0x228/+0x248 子对象（0x14197C9B0/0x141A0CD60/0x140744880/0x141723D10）。
- **★b9 原生写者负面证据（✅）**：0x14183-0x14188 区扫 [r+0xB9] 字节写 **0 命中**（+0xB8 是向量指针非 b9 位）——
  3K 无 shogun2 式 RNG 概率写 b9；b9 等价物候选（并发 §2.11：🥇[elem+0x14] 🥈[faction+0xCD0] 🥉[pending+0x138]）维持。
- **ctor 生命周期 hook 补充**：0x1418363B0/0x141836170（对象创建）+ 0x141838AB0（参与者条目 ctor）——
  冷启动挂 hook 可捕获 pending 创建参数（攻侧 [r8]、状态初值、btype 判定 0x1418442D0 结果）。

## 2.14 ★★链上选点展开：pending 创建/分叉/状态机（2026-08 g3t_fork_deep_report，✅ 字节级实证）

- **★pending 创建函数 = 0x1419D4580（attack creation）**：0x1419AC430 算 btype → new(0x300) → **0x141837AA0 ctor**
  （= 0x1418363B0 同族，栈参 {攻侧/守侧/btype/标志}）→ 存 [r15+0x3B80] → 初始化（0x1419EC7E0/0x1418678B0）。
- **★★分叉点 = 0x1419D48C6: `test r13,r13`**（r13 = 第 6 栈参 [rsp+0x110]）：**r13==0 → 0x1419C6DA0（结算链）；
  r13!=0 → 0x1414C8E70→0x1414C8700（另一链）** = shogun2 FUN_105caa60 分叉（ready/b9→0/1）的 3K 形态
  （★分叉输入 = 创建调用参数 r13，非 pending 字段；b9 等价物语义候选 = 「有参与对象=加载/无=结算」）。
- **★★pending 状态机 = 0x141865xxx 方法簇（每方法 = 状态切换器）**：0x141865420→状态 **1** / 0x141865390→状态 **5** /
  **0x1418654F0→状态 4（= shogun2 人类等待态 = 加载链入口！）** / 0x141865C20→结算。
  写模式：`cmp [pending+0x138],N; je; mov [pending+0x138],N; 事件 [env+0xF50]+0x10（旧值）; 特判 0xE→[env+0x31B0]+0x10`。
  **状态域 {0,1,4,5,0xE,0xF}**（无 shogun2 {6→5→7→8→9→10} 序列；切换器独立调用）。
- **★字段补充**：+0x118 状态字段 2（0x141865320 cmp 1）/ +0x178 battle context 指针（切换器检查清理）/
  +0x154/+0x158 参与者表 2（0x18 步长 [entry+0x10]/[+0x12]）/ +0x184 byte / +0x11C byte / +0xFC byte /
  +0x19F/+0x1A0 标志（0x1414C8F30/EA0 决策辅助置位，读 [obj+0x78]→[mgr+0x3B38/3B80] + 0x141861FC0）。
- **★实机 hook 点（链上可捕捉）**：① 0x1419D4580（pending 创建入口，log r13+btype）② **0x1419D48C6（分叉点，log r13）**
  ③ **0x1418654F0（状态=4 加载链入口）** ④ 0x141865390/0x141865420（状态 5/1）⑤ 0x141865C20（结算汇合）
  ⑥ 0x141837AA0（ctor 状态初值）。最小实验：玩家攻击 vs AI 内战跑两遍对比 r13 + 状态序列。

## 2.15 ★实机分叉点确认（2026-08-21 pid 9324，对 §2.14 的实机修正）

- **实机触发**：CREATE #1（r13=0x0）→ FORK #1（r13=0x0）——pending 创建走分叉点确认 ✅；但 **SETTLE（0x141865C20）零触发、状态 4/5 零触发**；CTOR（0x141837AA0）高频 10+ 次但 CREATE 仅 1 次（ctor 非专用 pending 创建链，别处大量调用）。
- **★分叉点反汇编修正（0x1419D48C6 上下文）**：
  ```
  test r13,r13 → jne 0x1419d48e1    ; r13!=0 → 0x1414C8E70
  call 0x1419C6DA0                  ; r13==0 → 结算处理器
  test al,al → jne 0x1419d490c      ; ★结算返回 true → 跳过
  → 0x1414C8E70                     ; ★结算返回 false → 也落 0x1414C8E70！
  ```
  **★0x1419C6DA0 不是「无条件结算」——返回 false 时仍落 0x1414C8E70**（原 §2.14「r13==0→结算」表述不完整）。
- **★0x1414C8E70 反汇编**：跳板（`mov [rsp+0x30],al → jmp 0x1414C8700`）；0x1414C8700 下游 0x1414C8EA0/0x1414C8F30 =
  **「决策辅助」**：状态检查 [rbx+0x138]==0 → [rbx+0x78]→[rax+0x3B38]→[+0xD0]→+0x10→0x141430B80 → [rbx+0x78]→[rax+0x3B80]=pending→0x141861FC0 → **写 [rbx+0x1A0]=1 / [rbx+0x19F]=1 标志**——**非加载链，是标志决策辅助**（§2.14「+0x19F/+0x1A0 决策标志」实锤）。
- **★实机矛盾点**：r13=0 → 0x1419C6DA0 若返回 true 应结算 0x141865C20，但 SETTLE 零触发 → **C6DA0 返回 false**，落 0x1414C8E70 标志链。C6DA0 内部 0x141BAC920 后存在**非 0x141865C20 的条件分支**（🔶 待 8 点 hook 确认 C6DA0 触发 + 返回 + 分支）。
- **当前实机结论**：r13 分叉语义待闭环（C6DA0 触发情况）；0x1414C8700 链 = 决策标志辅助非加载链；**加载链入口仍 = 0x1418654F0（状态 4）**；8 点 hook（加 C6DA0 本体 onLeave 返回值 + 0x1414C8E70/0x1414C8700）实机验证中。

## 2.16 ★★C6DA0 完整逻辑实机定案 + SETTLE 零触发解释（2026-08-22 pid 9324，8 点 hook + 实机反汇编，✅ 字节级实证）

- **★C6DA0 符号 = frida 跳板**：0x1419C6DA0 前 5 字节 `e9 jmp 0x13fcd0608` 为 Interceptor.attach 写入（0x13fcd0608 = frida 中转区，NO-MODULE）；**真实函数体 = 0x1419c6da5 起**（disasm_c6da0/b 实证）。同理 0x141865C20 前 5 字节也有跳板 = hook 生效、零调用 ≠ hook 失效。
- **★C6DA0 真实逻辑（AI 攻击专用门 + 结算前置收集）**：
  ```
  0x141844B60([pending+0x138] 状态∈{0,0xE} → false 提前返回)     ← 状态合法性门
  → 攻方 faction 链：0x141a2af80(r8) → [rax+0x68] 链表首 → 0x141a52840 → faction
  → cmp [faction+0xCD0],0 ; jne 提前返回                        ← ★is_human!=0（玩家攻方）→ 拒绝
  → 0x141866C90(pending, 守方faction) / 0x141866B40 守方检查
  → 0x14177ADF0 收集 → env getter 0x141B76950([this+0x3BA0])
  → ★0x141BAC920(env, rdx, 攻方, ...) 收集攻防双方
  → true → 0x1419C6F02: call 0x141865C20（★SETTLE 结算）→ mov al,1 返回 1
  → false → 0x1419C6F2C 清理 → 返回 0
  ```
- **★★实机 32 次 C6DA0 调用（过回合一次：48dd 点 21 + 4acf 点 11）RET 低字节全部 0x00**（0x69951200→al=0）→ **mov al,1 从未执行 → SETTLE（0x141865C20）从未到达**，全部在 0x141BAC920 false（或更早检查）终止。
- **★★创建链调用点语义修正（0x1419D48DD）**：`test al,al; jne 0x1419d490c` —— **al==0（C6DA0 返回 0）才 call E870（0x1414C8E70 决策标志辅助 @0x1419D48FF）**；al!=0 跳 0x1419d490c（后续推进链 0x1419D9B00/0x141A5DE20）。4acf 点（0x1419D4ACF）= 检查路径不接 E870。§2.15「C6DA0 返回 false 仍落 0x1414C8E70」表述精确化 = **al==0 → E870**（实机全部如此）。
- **★0x141BAC920 前半反汇编**：`[env+0x100]→[+0x3B80]→pending→0x141848490→0x1418618A0/840 取攻/守 faction 列表（xmm 对拷）` → 0x141840080 计数 → 0x14066FC10 扩容 → 0x14183FCF0/0x14183FD60/0x14183FE30 遍历收集 faction 指针数组 → 0x141B75E10×2 → 虚调用 → **0x141E1E660 检查，false → 0x141BACD3B 返回 false**。
- **★待解（fork6c 逐步定位中）**：32 次调用卡在哪一步（0x141844B60 / is_human / 0x141866C90 / 0x141BAC920）；pending 攻方是否全为 AI；**为什么 0x141BAC920 全 false（= 未确认任何一场 AI 战斗结算）**——候选：pending 状态非 1（0x141BAC920 读 pending 时状态已变）或攻守列表收集条件不满足。

## 2.17 ★★战斗分支 + 加载链实机定案（2026-08-22 pid 9324，fork6e/f6 + disasm_fork/load，✅ 字节级实证 + 实机三路对照）

- **★战斗分支（shogun2 FUN_105caa60 等价物）实锤 = ready 状态机 0x14193BFB0 的 `[elem+0x10]==5` 判定**：
  ```
  CCQ READY_TO_START（caller 0x14181F728 = CCQ handler 区）→ 0x1419DF1C0 → 0x141911900（r8=状态值写入 ready 元素）
  → tick 0x141876280（caller 0x1418762DA）调 ready 状态机 0x14193BFB0
  → 分叉（@0x14193C5FB/0x14193C640）：cmp [elem+0x10],5
      ==5 → call 0x141865c20（SETTLE 结算）
      !=5 → mov r8b,1 → call 0x141870000（BATTLE-REG，r8=1）
  ```
  ★**实机三路对照**：自动结算 r8=5→e10=[5]→SETTLE；重新进攻 r8=2→e10=[2]→BATTLE-REG；手动战斗 r8=1→e10=[1]→BATTLE-REG。
  ⚠️ **vote 语义已被 §2.19 修正**：5=撤退→SETTLE；2=自动结算→BATTLE-REG（无加载）；1=参加→BATTLE-REG→env 工厂→加载。
  ready 元素状态域 {0（初始/跳过）,1,2（战斗）,5（结算）}；状态机头另读 **[elem+0x14] byte**（0x14193C05A 区）。
- **★★加载链实锤（手动战斗场景加载）**：MGR-CTOR 0x141965680（rcx=0x732a0160=战役战斗管理器）→ TICK 0x141876280 每帧
  （pending state==1 门）→ ready 状态机 BATTLE-REG 0x141870000（只登记：0x141853A90 解析 faction → 0x1419D5F10 检查 →
  遍历参与者表 [pending+0x154]/[0x158] → 写 [entry+0x10]=r8/[entry+0x11]=r9/[pending+0x184]）→
  **★env 工厂 0x141FF7230（caller=0x1412FAA6D）→ ★BATTLE_ENV ctor 0x141FB6180（caller=0x141FF7306=工厂+0x76）**。
  **STATE4（0x1418654F0）零触发 = 非加载链入口（§2.14 静态推断修正）**。
- **★tick 0x141876280 内部结构（头部反汇编）**：`cmp [pending+0x138],1; jne 退出`（门）→ 0x141872650×2（攻/守检查）→
  `lea rcx,[pending+0x188]; call 0x14193bfb0`（ready 状态机）→ 参与者表检查（[0x154]/[0x158]）→ 0x141862600 → 写
  [pending+0x128] → env getter 0x1414907d0 → 0x1417ead10 → 攻守深度检查（[+0x140]/[+0x148]→[+0xC8]）→ 0x141861A50 →
  事件虚调用（[env+0x26E8]）→ 写 [pending+0xA8] → **0x14185B130（共享状态写器）** → 0x14186AD90（QUERY getter）→
  0x1415BDBA0 → 0x1419BD020 → ...（factory 调用链 0x1412FAA6D 待深挖）。
- **★b9 等价物候选更新（实锤级）**：🥇 **ready 元素 [elem+0x10] 状态值（分叉输入，5→结算/1-2→战斗）**
  🥈 [elem+0x14] byte 🥉 [pending+0x138]。**目标3 伪造方向 = 向 AI 内战 pending 的 ready 表（[pending+0x188]）
  注入状态 1 元素 → 状态机 BATTLE-REG → env 工厂 → BATTLE_ENV → 加载场景**。
- **待解**：① env 工厂 caller 0x1412FAA6D 上游（tick 内哪步调 factory）② ready 元素 add 函数（0x141911900 = 更新+移除，
  add 未定位）③ **AI 内战 pending 的 ready 表是否空**（AI 内战不走 ready 链 = 伪造注入可行）④ 玩家战斗 SETTLE 后
  pending 清理/结果落地路径。

## 2.18 ★★3K 注入点全集对照表（shogun2 多注入点模板，2026-08-22 用户提示「注入点不止 b9」后梳理）

| shogun2 注入点（40 §7） | 3K 对应 | 状态 |
|---|---|---|
| ★b9（AI 自动参战位，[pending+0xb9]=1） | **无**（3 构造器无条件字节写，扫描已证） | ✅ 已证无 |
| ★ready（+0x55 玩家登记） | **ready 元素 [elem+0x10] 状态值**（1=战斗/2=自动算/5=SETTLE）⚠️ 语义见 §2.19：5=撤退/2=自动结算/1=参加 | ★实锤（L13/L16） |
| ★登记 FUN_105c4700（human_flag 门控） | **0x141870000（BATTLE-REG）**：faction ready 登记（写 [entry+0x10]/[0x11]/[pending+0x184]） | ★实锤 |
| 登记门控 6a0/798/7a0（人类足迹伪造） | ?（3K「玩家足迹」字段，未找） | ⬜ |
| ★offer 链 M1/M2（援军/观察者，battle-offer 事件 0x133） | **预填 ready = 玩家参与检测**（引擎检测玩家援军 → 预填 ready → 投票 UI） | ⬜ add 未定位 |
| 状态 4 → factory → envdisp → battle_mgr | **BATTLE-REG → env 工厂 0x141FF7230 → BATTLE_ENV ctor 0x141FB6180** | ★实锤（L14/L16） |
| IsSpectator（0x5cf168 分支：本地玩家不在名单 → 旁观） | 旁观身份字段（未找） | ⬜ |

**★结论**：3K 与 shogun2 同构——**分叉输入 = 「玩家参与」表示（shogun2 ready/b9；3K ready 元素预填）**；3K 无 b9 位，
**AI 内战加载唯一入口 = 「玩家参与」路径（预填 ready → 投票 → BATTLE-REG → 加载）**。
伪造候选：~~① ready 元素注入（类型 6 + "rebels"串 + 状态 1，静态已验证字段安全，待实机）~~（①已废弃：L23，"rebels" 是撤退路径叛军转换，非注入模板）② 预填 add 伪造（未定位）
③ 玩家足迹字段（登记门控等价，未找）。分叉实体链与注入方向更新见 §2.19。

## 2.19 ★★★单链分叉实体定案（2026-08-22 用户纠正 + 全链静态，取代 §2.17/§2.18 的 vote 语义）

> ⚠️ 本节取代 §2.17「实机三路对照」与 §2.18「ready 元素状态值」的旧语义（5≠自动结算，SETTLE=撤退）。

- **★单链（唯一路径）**：卷入登记（ready 预填 state=0）→ 玩家投票（CCQ 0x14181F728→0x1419DF1C0→0x14186FD40→0x141911900，
  写 [elem+0x10]=vote）→ 状态机 0x14193BFB0（loop2 算 any-auto 标志 → loop4 分叉）→ BATTLE-REG → tick 全就绪门 → 战斗开始路径
  → [env+0xf50] 处理器分叉 → 自动结算计算 or env 工厂→加载。
- **★vote 语义（实锤）**：`1=参加战斗`（→BATTLE-REG→env 工厂 0x141FF7230（vtable 分发，data 0x1434dfa20）→ENV ctor 0x141FB6180→加载）/
  `2=自动结算`（→BATTLE-REG，无加载，战斗实际发生但引擎结算）/ `5=撤退`（→SETTLE 0x141865C20：写 [pending+0x180]=0x101、部队 [obj+0x49]=1、
  状态转移 0xa/0xe）。
- **★分叉实体**：状态机 loop4 对 state≠5 元素调 `BATTLE-REG(0x141870000)`，参数 `r9=[rsp+0x80]=「任一元素 state==2」` → 写参与表2
  `entry+0x10=1`（就绪）+ `entry+0x11=r9`（any-auto）+ `[pending+0x184]`。tick 0x141876280 扫 entry+0x10：全就绪→战斗开始路径
  （0x14187632B+）；有未就绪→跳过。**auto-vs-load 分叉 = env+0xf50 子对象 vtable+0x10 处理器**（地址待 fork6n 运行时读出）。
- **★结构定案**：pending ctor 0x141837AA0：`[pending+0x130]=env 对象指针`（0x1414907d0(attacker+0xe0)）、`[pending+0x138]=1`；
  状态转移器 0x14183CD00：写 [pending+0x138] + vtable 分发 [env+0xf50]+0x10（state==0xe 再 [env+0x31b0]+0x10）。
  READY-W(0x141911900)：写 [elem+0x10]/[elem+0x14]；r8==2 特殊分支（全局旗标 0x273e57d + [subobj+0x30/0x34]）；[elem+0x15]!=0 才移除元素。
- **★"rebels"(0x143348B2C) = 撤退（state==5）路径的叛军类型转换**（0x14193C36E lea rdx→串）——与 ready 注入模板无关，§2.18 伪造候选①废弃。
- **★ready 本身非关键**：自动结算（vote=2）也有 ready 预填（fork6h：SM cnt 0→1、e10=[0] 等投票、投票 r8=2）。ready=卷入登记，分叉在投票值+any-auto。
- **待解（fork6n 目标）**：① env+0xf50 处理器地址与 auto-vs-load 分叉指令 ② ready 元素 add（预填=offer 链，向上溯源）③ 战前部署界面创建点。

## 2.20 ★★★加载/自动结算分叉实机闭环（2026-08-22 fork6n 全链路捕获 + 0x141861A50 静态）

> 本节取代 §2.19「分叉在 env+0xf50 处理器层」的待定位状态——分叉已在 tick 状态选择层实锤。

- **★最终分叉链（实机 + 静态双证）**：
  ```
  投票 → ready 元素 state（1=手动/2=自动）
  → 状态机 loop2 any-auto 标志 → BATTLE-REG 写参与表2 entry+0x11=any-auto
  → tick 0x141876280 调 0x141861A50 → [pending+0xa8] = entry[0].+0x11（全表一致时）
  → tick 分支： [pending+0xa8]==0 → 状态 3/4（按 [pending+0x184]）→ ENV-FACTORY 0x141FF7230 → ENV-CTOR 0x141FB6180 → 加载
              [pending+0xa8]!=0 → 状态 6 → 11→13 → 自动结算（无加载；AI 内战同此）
  ```
- **★实机四路对照（fork6n 一轮）**：
  | 场景 | READY-W | SM anyAuto | BATTLE-REG r9 | 状态转移 | 结果 |
  |---|---|---|---|---|---|
  | ①手动 | r8=1 | anyAuto=0 allDecided=1 | r9=0 | 1→4 | ENV-CTOR 加载 |
  | ②自动 | r8=2 | anyAuto=1 allDecided=1 | r9=1 | 1→6→11→13 | 无加载 |
  | AI 内战×4 | 无 | 无 | 无 | 1→6→11→13 | 静默结算 |
- **★0x141861A50 结构**：读 [pending+0xa9]/[0xaa]/[env+0x3c50] 快捷路径；主路径扫参与表2（[0x154]/[0x158]，0x18 步长）全表 +0x11 一致 → 返回 entry[0].+0x11；不一致 → [env+0x3b38]→[+0x34]（混合场景）。
- **★0x141440910 = 状态变更观察者通知器**（[env+0xf50] vtable+0x10），遍历观察者数组逐个通知，非分叉本身。
- **⚠️ 注入点已修正（§2.21）**：🥇 参与表2 `entry+0x11=0` **不适用 AI 内战**（[pending+0x158]=0，直写 AV）；实际注入 = 强制 0x141861A50 返回 0。
- **关键地址**：0x141861A50（any-auto getter，★注入点）、0x1418764A8（tick 分叉 cmp）、0x141440910（状态通知器）、0x141FF7230（env 工厂）、0x141FB6180（ENV ctor）。
- **★2026-09-01 多 tick 结构静态确证（capstone，work/static_a50_mtick_20260901.py）**：
  - `0x141876280`（tick）在 `[pending+0x138]==1` 时**每帧对同一 pending 调用 `0x141861A50` 两次**：第一次 `0x1418763D9`（准备/广播），第二次 `0x141876401`（结果写入 `[pending+0xa8]`，随后 `0x14185b130` 状态写）。
  - tick 在调用 A50 前后都读取攻/守 alliance 链（`[+0x140]/[+0x148] → [+0x10] → [0] → [+0x18] → [0] → [0] → [+0xc8]`），并在 A50 后调用 `0x14186ad90/0x14186add0 → 0x1415bdba0 → 0x1419bd020`（官方单位数查询）。
  - **结论：3K 具备“多 tick 继承”入口**——同一 pending 在 state 1 会反复经过 A50，直到状态切换；若 force 单位容器在后续 tick 才填充，可以在 A50 内推迟/卡 tick 等到就绪，移植幕府2 Goal3.1 的 host-mediated 阻塞思路。
  - 待实机：`work/probe_a50_mtick_20260901.py` 对同一 pending 每次 A50 记录 `units/status/state/force`，验证 units 是否从 0/unknown 变为非 0。

## 2.21 ★★★★目标3达成：AI 内战加载注入实机成功（2026-08-22 fork6o v2，孙坚战斗）

> ✅ **目标3「观看 AI 内战（加载）」攻破**——强制 0x141861A50 返回 0 使 AI 内战 pending 走 state 4 → ENV 工厂 → 战场加载。

- **★注入方案（3K b9 等价 = 0x141861A50 返回值）**：对「非玩家卷入」pending（无 READY-W/SM cnt>0），在 0x141861A50 onLeave 强制 `retval.replace(0)`。
  效果：`[pending+0xa8]=0` → tick 走 state 4（加载）而非 state 6（自动结算）。
- **★成功序列（log 实锤）**：`C6DA0 → INJECT(a50 1->forced=0) → STATE 1->4 → TICK-A8 a8=0 → ENV-CTOR(LOAD)`。
- **★为何 v1（entry+0x11=0）失败**：AI 内战 `[pending+0x158]=0`（参与表2 空），且 0x141861A50 在 `a9=0 && aa=0` 时走快捷路径 `mov al,1; ret`（不读表）——AI 内战默认自动结算，表根本不在路径上。
- **★玩家战斗保护**：READY-W/SM cnt>0 的 pending 记为 seen，不注入（玩家手动/自动不受影响）。
- **遗留**：① 加载后玩家观战身份（IsSpectator 3K 等价，自动进入观战 UI）② 注入工具化（hook vs 持久补丁）③ 撤退场景演示。

## 2.22 ★★ESC 攻城不占城静态取证（2026-08-22 纯静态轮，work/esc_spectator_static_forensic.md）

> 现象：强制加载 AI 攻城战后，玩家 ESC「结束战斗」被视作平局（两败俱伤），城池不占。
> 结论速览：3K 存在 SP 旁观 UI 状态；ESC 走玩家战斗结束路径；AI 自动结算提交点用 result-side=-1；draw = `battle_result_types...draw`。
> **2026-08-18 实机三连复现（黄巾攻城全不占城）**：ESC 实际触发 `BCQ_FACTION_QUIT_BATTLE`；结果方槽被 QUIT_SETTLE 从 -1 改成 **1**；BATTLE_END_RESULT 有 result-side=1 但仍**判不出胜方**（两 army 的 `[+0x1bb]` 均为 0）；RESULT_SUBMIT 收到的结果方 = 1（非 -1）。根因从「无结果方」修正为「有结果方但胜负判定失败」。

- **ESC 命令族（✅ BCQ 注册表 + 反汇编）**：
  - `BCQ_FACTION_QUIT_BATTLE` @0x142077D70 → 0x141FCE6C0（构造 quit 记录）→ 0x1421E5850 → **QUIT_SETTLE 0x14213BF30**。
  - `BCQ_FORCE_BATTLE_END` @0x1420784D0 → **0x142145880**：设结果方槽 `[battle+0x1ac4]`（BCQ 参数）→ phase 0xC/0xE（PHASE_SETTER 0x1421698B0）→ 尾调 **BATTLE_END_RESULT 0x142136BD0**。
  - `BCQ_FORCE_BATTLE_VICTORY` @0x142078540 → 0x1420038C0 = 写 `[obj+0xbf]=1` 标志（非结算本身）。
- **★BATTLE_END_RESULT 0x142136BD0（胜负判定，✅）**：按战斗内存活部队判胜方（标记 `[army+0x18]→[+8]→[+0x1bb]=1`）；开头 `sete r10b` 显式处理 **result-side=-1 = 由战斗推算**。调用者仅 0x14213BF84（QUIT 路径）+ 0x142174616（正常战斗结束流）。
- **★RESULT_SUBMIT 0x1422598C0（战役回写，✅）**：调 0x141FD8120 → 0x14223EF60 / 0x14222F170 构建结果记录。调用者 3 = **0x1418474C0（AI 自动结算）** / 0x142112726（正常战斗流）/ 0x14213C013（QUIT 路径）。
- **★★AI 自动结算对照（✅ 0x1418474C0）**：pending 结算提交时 **result-side 传 -1（0xffffffff）**，由战役上下文推算胜负 → 攻城回写正常；-1 是引擎设计支持的「由战斗推算」哨兵。
- **★QUIT_SETTLE 0x14213BF30 流程（✅）**：`[battle+0x1ac4]==-1` → 结果方 = getter **0x141FEB4A0**（`[battle+0x14]` → `[[battle+8]+idx*8+4]`）→ BATTLE_END_RESULT → RESULT_SUBMIT（结果方参数 = `[battle+0x1ac4]`）→ phase 0xD。
- **★「两败俱伤」= draw（✅ 本地化）**：`battle_result_types_result_screen_name_draw` = 平局；另有 `shortcut_localisation_onscreen_battle_both_withdraw` = 后撤（双方退出形态）。
- **★SP 旁观 UI 证据（✅）**：`spectate_icon` tooltip（放弃指挥权→旁观）、`blocker_spectator`（你是观众，无法调节战斗速度）、`spectate_button_active`（观看战斗）、`spectator_parent`（观众）。exe 内仅组件名 `spectate_icon`@0x1437ED0C0 / `button_spectate`@0x1437ED0A0 / `button_spectate_battle`@0x14381BEB8（0 直接 lea 引用，哈希注册）。
- **根因链（🔶 推断 → 2026-08-18 实机部分修正）**：
  - 旧推断：本地玩家无参战方 → 结果方槽无有效值 → draw。**已被实机部分推翻**：强制加载后 `PLAYER_SETUPS.cnt=2`、`env+0x64750=1`，QUIT_SETTLE 成功把 `[battle+0x1ac4]` 从 -1 改成 **1**。
  - 新推断（✅ 实机确认到“判不出胜方”为止）：ESC → QUIT_SETTLE → 结果方=1 → BATTLE_END_RESULT 有 result-side=1 但两个 army 的胜方标记 `[+0x1bb]` 均为 0 → 无胜方 → 提交 draw → 攻城不回写。
  - **★实机根因确认（2026-08-18 第二轮，work/live_out/esc_ai_siege_army_20260818.log）**：两个 army 的 `unitCnt=1`、`unitArr` 有效，但 unit entry 的 `[+0x184]=0`、`[+0x188]=0`（unit 对象指针全 0）→ BATTLE_END_RESULT 内层 `test eax,eax; je` 直接跳过所有 unit → 永远无 side 匹配 → 无胜方 → draw。**H3 实锤：强制加载态 army 存在但 unit 对象链未填充。**
- **修复方向（2026-08-19 v1/v2 实机失败后更新）**：
  - ①保底 v1（仅把 `[battle+0x1ac4]=-1`）：**失败**——QUIT_SETTLE 内两个前置检查（0x14217E6A0/0x142154E30）返回 false，RESULT_SUBMIT 被跳过 → 仍平局不占城。
  - ②保底 v2（-1 + 强制放行两个前置检查）：**触发 RESULT_SUBMIT 但随后游戏卡死/闪退**——QUIT 路径的 RESULT_SUBMIT 用 -1 时上下文/结果对象可能不匹配，不能简单硬放行。
  - ③★静态已打通（2026-08-19，work/esc_settle_chain_static.md）：QUIT_SETTLE 调 RESULT_SUBMIT 时 `[rsp+0x40]=0` → RESULT_SUBMIT 是 **no-op**；AI 自动结算 `[rsp+0x40]=1` → 走 **0x14223EF60** 真正回写。v3 保底 = -1 + 强制前置检查 + **把 RESULT_SUBMIT 入口 `sp+0x48` 字节写 1**（=调用方 [rsp+0x40]=1），复用 AI 同款提交构建器。
  - ③b ★★★v3 实机验证成功（2026-08-19，work/live_out/esc_fix_v3_20260819_003358.log）：用户战后显示「酣畅大胜」、城池正常占、不闪退。日志证据：`FIX-SUB #1`（+213c018 写 sp+0x48=1）→ `RESULT_SUBMIT #1` `st48` 低字节=1（调用方 `[rsp+0x40]=1`）→ 走 0x14223EF60；随后 AI 自动结算 `RESULT_SUBMIT #2`（+18474c5）正常。**ESC 保底已确证可用，已移植 GUI v4（dist_v4）真实开关（修复+日志）。**
  - ④根治：强制加载时补齐 unit 对象链，或让 ESC 完全改走 AI 自动结算路径。

## 2.23 ★★战斗捕捉过滤数据源（2026-08-19 静态，work/battle_filter_static.md）

> 目标：只强制加载“大规模/指定派系”的 AI 战斗，小规模/无关战斗保持自动结算。
> 实现位置：目标3 注入点 0x141861A50（rcx = pending battle 对象）onEnter 判定，不满足则不注入。

- **攻/守参与集合（✅ 字节级，2026-08-22 对象同一性纠错）**：`[pending+0x140]` / `[pending+0x148]` 指向 0x28B 的战斗参与集合（getter 0x141848490）；集合 `+0x0C=count`、`+0x10=8B 指针数组`。数组元素**不是 campaign army/military_force**，而是按 `FACTIONS` 生成的 0x158B faction participant-group。
- **participant-group 布局（✅ 构造/清理双证）**：`0x141839420` 写 `group+0x08=faction`；`group+0x14` = `PARTICIPANTS` 子记录数，`group+0x18` = 0xA0B participant 指针数组。旧文档/代码把 `group+0x14` 称作“兵牌数”是对象层级错误，已撤回；participant 的精确域类型仍未闭合，不能擅称将领数或军团数。
- **强度聚合（✅）**：`float 0x14186A4E0(collection*, flag)` 遍历 `group+0x18`，累加每条 participant `+0x64` 的 float 强度；所以 participant_count=1 与 total_strength=5169 完全相容。
- **派系归属（✅ 字节级）**：`group+0x08=faction` 由构造器明确写入；faction key 扫描逻辑因此可用，但这不证明 group 本身是 army/force。
- **GUI v4 已实现（2026-08-19，待实机验证）**：启用过滤 + 最低总强度 + 最低军团数 + 指定派系（逗号分隔）；日志 `FILTER-HIT/FILTER-SKIP`。
- **强度观测模式（2026-08-19；2026-08-22 纠错）**：`STRENGTH-OBSERVE` 可记录总强度、既有集合计数与攻守派系；不得再把 `group+0x14` 输出为兵牌数。
- **扫描免开派系窗口（2026-08-21 实机修正）**：faction 容器 = `[env+0x3B68]` 指针指向的容器（计数 +0x64/数据 +0x68），**不是 `[world+0x3B68]`**；env 未拿到时自动按 BATTLE_ENV vtable 0x1434E19A8 扫内存定位 env 再枚举。
- **待实机**：AI 内战 pending 在 a50 触发时攻/守容器是否已填充；强度量纲是否与官方 `pending_battle():attacker_strength()` 一致；过滤后小规模不再 `INJECT/LOAD`。

## 2.24 ★★战斗开始前单位数静态纠错 + 战斗类型现状（2026-08-22，work/unit_count_static_correction_20260822.md）

> 读取时机统一在目标3注入点 `0x141861A50` 的 `onEnter(args[0]=pending)`，早于强制返回 0 与战场加载。

- **❌ 旧兵牌公式已实机证伪并静态解释**：`sum(group+0x14)` 统计的是 faction group 内 `PARTICIPANTS` 子记录数，不是兵牌。实机 1/1 与强度 5169 的冲突正是对象同一性错误；最低兵牌过滤和参数链已禁用，日志改为 `*_invalid_candidate14`。
- **✅ 真正 campaign force 兵牌容器**：官方 `unit_list` handler `0x1416433B0 → 0x1419BC420` 与独立消费者 `0x141B988F0 → 0x1419BC420` 交叉验证：`military_force+0x5F0` 为 unit 子容器，`force+0x60C=count`，`force+0x610=unit handle array`，`*array[i]=unit`。
- **⚠️ 2026-08-31 桥已证伪（实机 2026-09-01）**：`0x14186ad90/0x14186add0 → 0x141a66d80` 返回的**不是 military_force**，而是 faction 相关对象（读 `+0x610` 得到 `1.0f`/小整数，不是 unit 数组）。该旧链不能用于 A50 兵牌过滤。
- **✅ 2026-09-01 广探针闭合（直接链）**：`participant` 记录（0xA0B）的 **`+0x0` 就是 military_force 指针**。A50 时直接读 `force+0x60C`（unit handle count）/ `force+0x610`（unit handle array）即可，不再需要 alliance/force 链。实机样本：攻 `cnt=3`、守 `cnt=21`。
- **⚠️ 语义范围（v11 已扩展）**：v11 起按侧遍历**全部外层 faction 分组 × 全部 PARTICIPANTS**，累加每个有效 `participant+0x0 → force+0x60C`；覆盖多派系/多部队联军。仍需与官方 `num_attacker_units/num_defender_units` 多场对照确认合计口径。
- **★v13 延迟判定**：实机存在防守方 force 第一次 A50 `no-force`、后续同一 pend 变 ok（21/21）的时序；`units=unknown` 先挂起，离开 state=1 仍 unknown 才 skip。
- **将领数/实际兵员人数仍未定位**。
- **战斗类型 raw 字段（✅ 字节级）**：QUERY_PENDING_BATTLE 的 `battle_type` 注册 @`0x14011E127` → handler `0x1415941F0` → getter `0x1418492B0`；getter 为 `movzx eax, word ptr [rcx+0x68]; ret`，故 **`[pending+0x68]` = u16 battle type raw**。
- **当前唯一闭合类别（✅）**：官方 `seige_battle` handler `0x141613560` 调同一 getter，并把 raw `6`、`9` 判为攻城相关；故当前仅确证 `6/9 → siege`。
- **完整枚举未闭合（⬜）**：raw→字符串函数 `0x140AACB30` 接收调用方提供的 C++ 字符串目标对象与 raw，返回该对象指针；并非安全的 `char*` getter，Frida 当前不直接调用。静态虽有 `battle_type_land/siege/siege_relief/ambush` 等串，尚不能把其余 raw 猜成野战或关隘。
- **代码止损（✅）**：GUI/Frida 已移除最低兵牌配置及 Python→Frida 参数链，不再输出 `atk_units/def_units/total_units`；强度、派系、类型实验项与玩家战斗保护保留。`dist_v5_unit_filter` 已写 `WITHDRAWN.txt`，构建脚本入口已阻止误重建。
- **★自定义战斗校准路线已关闭（2026-08-22 实机，FIELD_CUSTOM_01 / PASS_CUSTOM_01）**：普通野战从配置→部署→正式开战，`0x1418492B0` / `0x141613560` / 其余 campaign 类型消费点全程 0 命中；关隘战配置→部署同样不命中 pending 类型链。扩展战斗侧 hook `0x142011F10` / `0x142006340` 在关隘部署各命中 5 次，但参数并非可信 BATTLE_ENV（候选字段为代码字节/零值），`0x142019AB0` 0 命中，无法导出任何 field/pass 类型结论。**当前结论：自定义战斗绕过 campaign PendingBattle getter，不能用于校准 `[pending+0x68]` 枚举；类型过滤保持实验状态，默认全选。**
- **当前可交付能力（2026-08-31 更新）**：总强度、军团数、派系、**真实兵牌数（第一 force）** 可继续使用；field/pass 类型过滤仍不在可用范围。兵牌数读取失败/未就绪时按「拒绝加载」处理（不再 fail-open）。
- **撤回产物（2026-08-22）**：`work/dist_v5_unit_filter/ThreeKingdomsControl.exe` 不得继续使用或传播；撤回说明见 `work/UNIT_FILTER_TEST_README.md` 与同目录 `WITHDRAWN.txt`。

## 3. 当前前沿疑点（★2026-08-21 更新：BATTLE_ENV 链已闭合 3 项，见 g3_battle_env_load_static；2026-08 静态审查见 31 §2.6/§2.7 + work/g3t_static_review.md + work/g3t_voting_fork.md）

- ✅（已解）3K BATTLE_ENV 加载链：ctor 入口 @0x141FB6180（env 0x647C0）、env vtable @0x1434E19A8、工厂三胞胎 @0x141FF7230/7550/7350 + 类表 @0x1434DFA08（修正：工厂=vtable-0x8）、finalize @0x141FF7030、装配六族 @0x1403069D8 等
- ✅（已解）0x14201D800（battle_ai 消费者）= 门控初始化函数非加载入口；不触发根因 = 0x142006340 门控（env+0x64565/0x64566/0x6461d + 参数块字节），见 31 §2.6
- ✅（已解）分叉判定候选 = ready 状态机（**函数头 0x14193BFB0**，§2.7 写的 0x14193BFA3 是 int3 padding——实机 hook 错地址零触发，已修正）；0x28 ready 元素表写者全集 = 0x141911900（调用者：CCQ 链 0x14186FD36 区 + 状态机），见 31 §2.7
- ✅（2026-08-21 用户旧 mod 实证）★**场景 A 实锤：`PendingBattle` 事件对 AI 战斗触发** + `query_model():pending_battle()` 可读 AI 内战全数据（attacker/defender faction、坐标、实力、士气、battle_type、增援、attacker_strength/defender_strength）——用户旧 mod `@FakeObserverMode`（workshop 3433582189）`check_battle_pre` 函数实证（work/mods/fake_observer/script/campaign/mod/obsever.lua）；其旁观实现 = 官方脚本（玩家派系附庸/中立 + 侦察部队传送），非引擎旁观
- ✅（2026-08-21 实机负面，★2026-08-21 用户纠正后修正认知）ready 状态机（0x14193BFB0）**容器恒空**——**但不能推出「投票机制不存在」**：用户旧 mod 实证 AI 内战发生时玩家在附近可**选择加入战斗/自动结算/拒绝战斗** = 玩家投票 UI = **投票器绝对存在**。正确解读 = ready 状态机处理的容器**不是投票表**；投票表载体可能在 pending battle 对象（[model+0x3B80]）内部或另一容器。★「AI 内战不走 ready 投票机制」结论作废/降级为「该状态机容器非投票表」（子代理 1b0f55d3 深挖 VOTING_SYSTEM_BLOCK 消费入口 @0x1418F1BF8 + pending 对象投票字段中）
- ✅（2026-08-21 定案）MODIFY_PENDING_BATTLE 官方翻盘点**已关闭**（71 §1.2：脚本接口方法名表成员，官方 0 调用 + WH3 同族 63 方法全查询 → 字段写非流程触发）；子代理 1b0f55d3 转挖 VOTING_SYSTEM_BLOCK 消费入口 @0x1418F1BF8 + AI 内战必触发观测点
- ✅（2026-08-19 记录，2026-08-21 已裁决）★**VOTING_SYSTEM_BLOCK 真消费 @0x1418F1BF8** = describe 格式化引擎（读投票块 0x28 表 → 字符串，0 直接调用者，非投票器/非决策链），见 31 §2.10
- ✅（部分解）AI 内战引擎路径：★**0x1419C6DA0 完整逻辑 = AI 内战静默结算链**（检查 [pending+0x138] → faction 检查 → 收集 0x141BAC920 → 0x141865C20 结算，不读投票表）——核心缺口已闭环大半；剩余 = 0x141BAC920 内「结算 vs 加载」条件分叉确认（实机 hook 0x1419C6DA0 + 0x141865C20 + 0x141870000 三连观察），见 31 §2.11
- ✅（部分解）3K battle_mgr 全局指针（shogun2 [base+0x1bc8180] 等价物）——**pending battle 指针 = [manager+0x3B80]（5 源印证：CCQ 链 / get_modify 工厂 / 结算处理器 0x1419C6DA0 / AUTORESOLVER CCQ handler / 0x141BAC920）**；battle_mgr 本体全局仍 ⬜（等价物 = .sbss 类表 @0x1434DFA08 🔶）
- [占位] 3K 旁观身份字段（SP 侧）——候选：env+0x64750（ctor 查询 id 0x79）/ PLAYER_SETUP 人类位（env+0x340 向量）/ is_human 方法 ID 0x19 getter；**IsLocalPlayerSpectating @0x37D5DC0 已确证 = MP lobby 脚本方法名（3 上下文注册 0x140269402/0x14026AA72/0x14026B662），非 SP 侧**
- [占位] 3K 无人类参战自动结算链（AUTORESOLVER 族 xref）
- [占位] 旁观时 battle_manager 玩家语义方法（get_player_army 等）返回行为（实机确认）
- ⬜ 战斗类型完整 raw 枚举：当前只确证 6/9=siege；**自定义战斗校准路线已实机关闭**，field/pass/ambush 等只能用战役 `PendingBattle` 官方 `battle_type()` 与 A50 日志对照（§2.24）。
- ✅（2026-08-31）兵牌链：真实兵牌 count = `military_force+0x60C`；pending participant→force 桥已由官方 getter 链 `0x14186ad90/0x14186add0 → 0x141a66d80` 闭合。剩余：多 force/援军合计与官方 `num_attacker_units` 的实机对照；将领数、实际兵员人数仍未定位。
