# 目标1 机制地图（11_GOAL1_MECHANISM_MAP）— 三国（3K）原生战斗 AI 托管

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 主题：让玩家部队在战役战斗中成为真正的 AI 部队（目标1：玩家部队由**原生**战斗 AI 指挥，战术等价于正常敌人 AI）。
> 本文件 = 目标1 的机制链地图（唯一现状依据）：只收录当前成立结论，按游戏机制链组织。
> 修订/证伪历史单独收录 `12_GOAL1_LOGBOOK.md`（待建）——本文件不含任何修订文本。
> 路线视野（还有哪些路能走、哪条在挖/封死）见 `13_GOAL1_EXPLORATION_MAP.md`。
> 认知源：shogun2 `docs/11_GOAL1_BATTLE_AI_MAP.md`（32 位机制链全破译，本文件为其 3K 迁移版骨架）。
> 最后更新：2026-08-19（目标1 静态补足轮：battle_ai 钻链 3K 版成形——战斗脚本方法表 + BCQ 命令块机制 + 计划类型枚举）。

---

## 0. 目标与成功判据

- **目标**：3K 战役战斗中，玩家部队由**引擎原生战斗 AI**（与敌人 AI 同一决策路径）指挥，而非官方 script_ai_planner 的**脚本型 AI**。
- **官方边界（已确证，勿重探）**：官方 API 只有脚本型——`alliance:create_ai_unit_planner()` 引擎执行器仅 5 原语（3K），决策 100% 在 Lua；无 ai_active/set_ai_control 类身份替换 API；`release_control_of_all_sunits()` 释放的是脚本控制权（玩家军队→交还玩家，不建 planner = 呆立/反应式）。→ **原生 AI 质量必须引擎层 64 位字段直写**（shogun2 a270=0/a28c=1/a290=1.0f/a294=-1 + 单位 +0xea8/+0xc01 的 3K 等价物，全部待逆向）。证据：docs/70_API_AI_NATIVE_VS_SCRIPT.md §2-§4。
- **成功判据**：玩家不操作（或最小操作），部队由引擎 AI 指挥链驱动（计划链 + 命令落地 + 单位 tick），能看完整场战斗，行为与正常敌人 AI 等价。
- **失败判据**：脚本型接管（行为劣化「显傻」）/ 呆立无命令 / 静默退出 / 黑屏。

---

## 0.1 机制链总览（★2026-08-19 静态补足：battle_ai 钻链 3K 版）

```
Lua 战斗脚本 (battle_start.lua / script_ai_planner)
   ▼ 脚本面命令名池 @0x1434ECAE0：force_ai_plan_type_attack/defend、force_snap_ai_to_hint_lines、
   │  create_ai_unit_planner、force_battle_victory、rout_position（官方 5 原语同源）
   ▼ ★战斗脚本方法表 @0x143C13180（.didata，16B 步长 {方法名指针, handler}）
   │  handler 全在 0x142037xxx 连续簇（create_ai_unit_planner→0x142037DF0 等）
   ▼ 命令块构造 {执行函数指针, target=[script_obj+8], value}（attack=0/defend=1 = 计划类型枚举）
   ▼ ★BCQ 入队 0x142044150(rcx=[全局@0x143CCF430]+0x468, rdx=块)
   │  查使能位(0x14200ACF0) → 取缓冲(0x14200ACB0) → 执行块头函数 → 序列化到 [buffer+0x5000]
   ▼ 执行函数族 0x142096390（force_ai_plan_type：写 [target+0x28] + 计划类型值）/ 0x1420963D0（序列化器）
   ▼ [待钻] BCQ 命令注册表 → army/unit「原生 AI 激活」字段（shogun2 a270 等价物，子代理钻链中）
```

## 1. 官方通道性质（已确证，迁移资产）

| 通道 | 3K 现状 | 判定 | 证据 |
|---|---|---|---|
| `script_ai_planner` / `set_up_script_planner()` | Lua 决策 + 引擎执行器（5 原语）| **脚本型，非原生** | 70 报告 §3 |
| `release_control_of_all_sunits()` | 释放脚本控制权；玩家军队→交还玩家 | 不构成原生托管 | 70 报告 §2 |
| `ai_active` / `set_ai_control` 类 API | 3K 脚本全树 0 命中 | 不存在 | 70 报告 §4 |
| UnitController `take_control/release_control` | 控制权开关（非 AI）| 脚本控制 | 70 报告 §2 |

## 2. 引擎层机制链（★2026-08-19 静态资产，钻链缺口已派工）

### 2.1 战斗命令体系（已确证 2026-08-19，05_LOGBOOK「目标1/2 静态补足轮」）

- **命名语义**：BCQ_ = 战斗命令队列 / CCQ_ = 战役命令队列（引擎串族确证）。
- **AI 脚本控制器命令名池**（.sbss，全 0 直接 xref = 哈希注册）：`BCQ_CREATE_AI_SCRIPT_CONTROLLER`@0x1434E82B8、`BCQ_DESTROY_AI_SCRIPT_CONTROLLER`@0x1434E82D8、`BCQ_ADD_UNIT_TO_AI_SCRIPT_CONTROLLER`@0x1434E8300、`BCQ_REMOVE_UNIT_FROM_AI_SCRIPT_CONTROLLER`@0x1434E8328、`BCQ_SCRIPT_CONTROLLER_CLEAR_OBJECTIVE`@0x1434E8358、`BCQ_SCRIPT_CONTROLLER_SET_OBJECTIVE_DEFEND_POSITION`@0x1434E8380、`BCQ_SCRIPT_CONTROLLER_SET_OBJECTIVE_CAPTURE_SETTLEMENT`@0x1434E83B8、`BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_ATTACK_UNIT`@0x1434E83F0、`BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_MOVE_TO`（0x1434E8428 截断）、`BCQ_FORCE_ALLIANCE_BATTLE_PLAN`@0x1434E8298 —— 即官方 script_ai_planner 5 原语的引擎执行器命令名。
- **★战斗脚本方法表 @0x143C13180**（.didata，16B 步长 {方法名指针, handler}）：命令 → handler：
  | 方法名 | handler |
  |---|---|
  | create_ai_unit_planner | 0x142037DF0 |
  | force_ai_plan_type_attack | 0x142037C50 |
  | force_ai_plan_type_defend | 0x142037CE0 |
  | force_snap_ai_to_hint_lines | 0x142037D70 |
  | force_battle_victory | 0x142037EB0 |
  | rout_position | 0x142037F30 |
  同表还含 armies/units 查询方法（load/play3D/is_moving/is_idle/number_of_men_alive 等，handler 0x142037xxx 连续簇）。
- **★BCQ 命令块机制**（handler 反汇编确证）：块 = {执行函数指针, target=[script_obj+8], value}；入队函数 0x142044150（rcx = [全局@0x143CCF430]+0x468，rdx = 块）：查使能位（0x14200ACF0，[rax+0x10]/[rax+0x11]）→ 0x14200ACB0 取字节缓冲 → 写头（全局 [rip+0x209C56D]/[rip+0x209C548]）→ `call [rdi]` 执行块头 → 序列化到 [buffer+0x5000]（计数器 +0x5000 / 起始 +0x5008）。
- **★计划类型枚举**：force_ai_plan_type_attack 块值 = 0、defend = 1（[rsp+0x30] 实证）；执行函数 **0x142096390** 写 [target+0x28] 与块值（经 0x14261B540）；块序列化器 **0x1420963D0**。
- **create_ai_unit_planner 执行链**：分配 0x20B 对象（0x14066FC10）→ **vtable@0x1434ED4E0**（首 vfunc 0x1420659B0）→ [+0x18]=[target+0x28]、[+0x1C]=全局 id → 块 {0x1434ECE18 处值 0x142096390, target, id} → 入队 0x1420432B0。
- **原生战斗 AI 模块线索**：`ai\localplanner\` 源码路径 ×19（ailp ×120）= 原生战斗 AI 本地规划器；`battle_ai`×11 全为 DB 表名（battle_ai_properties/parameters/personalities_table）；`BATTLE_AI_*`×40 全为设置串（BATTLE_AI_DEBUG_DISPLAY_*、BATTLE_AI_EXCLUSIVE/INVERT）。

### 2.2 ★BCQ 命令注册表全量提取（已确证 2026-08-19，本会话）

- **★双注册器定案**：`0x141820B00` = **CCQ（战役命令）注册器**（191 块）；`0x1420B0CD0` = **BCQ（战斗命令）注册器**（129 块）。注册块模式（0x20B 步长）：`lea r9(handler) + xor r8d + lea rdx(命令名) + lea rcx + jmp 注册器`——**此前「CCQ_FACTION_SWITCH_HUMAN_TO_AI 假阳性」结论作废**（旧扫描器 lea 计算误差；真注册块 @0x14015E320）。工具：`re/3k_regblocks_all.py`（全量提取）；产物：`work/g2_ccq_registry_all.txt`（191 条）+ `work/g1_bcq_registry_all.txt`（129 条）。
- **★AI 脚本控制器命令族 handler（BCQ 注册器）**：
  | 命令 | handler |
  |---|---|
  | BCQ_CREATE_AI_SCRIPT_CONTROLLER | 0x142076DB0 |
  | BCQ_DESTROY_AI_SCRIPT_CONTROLLER | 0x1420770D0 |
  | BCQ_ADD_UNIT_TO_AI_SCRIPT_CONTROLLER | 0x142075360 |
  | BCQ_REMOVE_UNIT_FROM_AI_SCRIPT_CONTROLLER | 0x14207C200 |
  | BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_ATTACK_UNIT | 0x1420753F0 |
  | BCQ_AI_SCRIPT_CONTROLLER_SET_OBJECTIVE_MOVE_TO_POSITION | 0x142075480 |
  | BCQ_FORCE_ALLIANCE_BATTLE_PLAN | 0x142078460 → **0x1402E0520 = `ret 0` 空壳（stub no-op）** |
  | BCQ_CHANGE_ARMY_FACTION | 0x1420768D0 → 0x1402E0520（同 stub） |
  | BCQ_FORCE_SNAP_AI_TO_HINT_LINES | 0x142078590 |
- **★army 对象查找链（BCQ handler 通用）**：命令 data → `[data+0x150]` → `[+0x150]` 数组 → `[idx*8]` → `[+0x20]` = **army 对象**（CREATE/DESTROY/FORCE_ALLIANCE_BATTLE_PLAN 同款）。
- **★★★ AI 脚本控制器附着点 = army 对象链表（0x1424E8880/0x1424F3850 反汇编确证）**：
  - **army+0x820 = 控制器计数（u32）**；**army+0x828 = 链表头哨兵**；**army+0x830 = 链表尾**；节点 0x20B = {next, prev, 控制器id(u32), 控制器对象ptr}
  - 控制器对象 0x48B：vtable **@0x143567BA0**（vfunc0=0x1424CE9C0 析构）、+8/+0x10 = 拷贝 [army+0x20]、+0x18 = 指向 army+0x20
  - create = 0x1424E8880(army, id)：new 0x48 控制器 + new 0x20 节点 + 链表尾插 + 计数++；destroy = 0x1424F3850(army, id)：按 id 遍历 [army+0x830] 尾链、调 [控制器]vtable[0] 析构、摘链、计数--
- **★动态锚点建议**：army 对象查找链（hook BCQ_CREATE handler 0x142076DB0 抓 army 指针）→ 直接读/写 [army+0x820/0x828]；「原生 AI 激活」字段（a270 等价物）= army 对象锚定后 player vs AI 军字段差分（对照 shogun2 RE-B3）。
- **BCQ 系统语义补全（子代理 22da1667 报告 g1_bcq_commands_static.md，2026-08-19）**：
  - BCQ = **命令日志系统**：入队 0x142044150（~130 个命令专用变体）→ 查使能位 `battle_env 子对象 +0x360/+0x361`（0x14200ACF0，写者静态不可达）→ 取缓冲 **battle_env+0x644A0**（vtable@0x1434733F8，数据区 +8/计数器 +0x5008/容量 0x5000）→ 序列化记录头 {2B 长度 + 4B 命令 id BE + 1B dword} → **立即调块头执行函数**（0x142096xxx 簇 91 个 {执行+序列化} 对）→ 参数 marker 字节（0x04/0x0B/0x29）流入记录
  - 命令 id = **名字哈希**（0x14261A4F0，CA 32 位哈希）；注册表 = TLS 单例哈希表（0x141F46DE0，条目 {key@+0x10, name@+0x18, dword@+0x28, **handler@+0x30**}）
  - 129 条 BCQ/BNCQ 全枚举清单 `work/bcq_stubs.txt`；**army+0x28 = army 索引/id**（planner 与命令消费端经 [ctx+0x150]→[+0x150] 句柄数组→[+0x20] 回查 army）
  - 报告 §4 有 8 条 frida hook 点清单（搁置层参考）

## 2.3 ★★3K battle_ai 等价物定案（2026-08-19 方向修正轮，shogun2 同构铁证）

> ★用户指示：官方接口（BCQ/CCQ/脚本命令）不连通引擎功能实现，**照 shogun2 成功路线图**重新调查（03_DISCOVERIES：tweaker 命令族 battle_ai → Command 对象值字节 → 消费者 0x1adf50 → army+0x12c；直写 8 字段 a270=0 等）。

- **★★BATTLE_AI_EXCLUSIVE**（value=**0xd9**，desc='AI versus AI (no manual player control)' 与 shogun2 逐字一致，display='Battle AI Exclusive'，source=empirebattlesetup.cpp）
- **★★注册器 = 0x14034BB80**（tweaker 8 参注册：rcx=Command 对象 + rdx=name + r8b=temp + r9d + 栈参 UPPERNAME/desc/display/value/source）
- **Command 对象布局（3K tweaker）**：+0x00 vtable（≈0x14352AA00）、+0x08 dword、+0x10/+0x20/+0x30 字符串（UPPERNAME/desc/display）、+0x40 **value**、+0x44 dword、+0x48 name 串、+0x58 temp byte、+0x59 set 标志（对照 shogun2 Command +0x5c 值字节——64 位重排）
- **值字节全局 [0x1440DC640]**（注册时置 0）；Command 对象区 0x1440DC5E0（.didata）
- 家族：BATTLE_AI_INVERT（value=0xda）、FORCE_REALISM_MODE（value=0xdb），注册函数 0x140184E00/0x140184F50/0x140189FD0 同构
- **★★消费者 = 0x14201D800（子代理 8ad327b7 定案，与 shogun2 0x1adf50 完全同构）**：
  - **4 门判定**：EXCLUSIVE 值字节[0x1440DC640] / env dword[0x1440DA610]（BATTLE_ENV ctor @0x141FB6B45 写 [env+0x4318]）/ byte[0x1440D9399]（无静态写者，推断=另一命令值字节）/ INVERT 值字节[0x1440DA840]（对象 0x1440DA7E0+0x60）
  - 逻辑：**EXCLUSIVE≠0 → flag=0**（玩家控制关）；INVERT≠0 → 翻转；否则 flag=param[0]——平行 shogun2（battle_ai==0 && test_ai_build==0 → local_35=*param_2；任一非 0 → local_35=0）
  - 写：**节点 [node+0x1A0]=flag + [node+0x1C4]=!flag**，递归子节点（步长 0x2A8）——平行 shogun2 army+0x12c=0/+0x148=1
  - 调用链：0x142011F10 → 0x142006340（battle AI setup）→ 0x142019AB0（battle_env 方法，读 +0x64560..0x64567 构造 param）→ 0x14201D800；另有容器处理器 0x141FBE180 / 0x141FF2990
- **setter（值字节=1 运行时通道）**：Command vtable vfunc+0x18 = **0x1402E0080** → 0x140711BE0 写 [this+0x60] + 置 +0x59=1（经 vtable，无静态 xref）
- **★注入方案（对照 shogun2 R2，实机首选）**：运行时写 **0x1440DC640=1** → 全部战斗记录 [node+0x1a0]=0/+0x1c4=1 = AI-versus-AI（no manual player control）；或静态补丁 0x14201D81E `80 3D 1B EE 0B 02 00` imm 0→1
- **★动态验证清单**：hook 0x140711BE0（值字节写者观测）→ hook 0x14201D800（4 门+flag 验证）→ 内存断点 0x1440DC640（找置 1 路径）→ hook 0x141FB6B45（门2 来源）
- **✅✅ 实机成功（2026-08-19 自定义战斗，shogun2 R2 复刻）**：写值字节 0x1440DC640=1（frida，回读确认；Command 对象 value=0xD9 实机验证）→ 进自定义战斗 → **消费者 0x14201D800 调用 6 组（0x2A8 步长递归命中静态预测）** → **部队自动部署 + 自主行动（AI 接管玩家部队达成）**；值字节跨战斗保持 1
  - **副作用（shogun2 P25 同款）**：速度不可调整（变速锁——引擎设计约束「玩家军队 AI 托管 + 玩家变速」不可兼得）；天气问题未确认（推断战役层进攻战会有 shogun2 同款卡天气选择，待战役测试）
  - 工具：work/battle_ai_live_test.py（--read/--hook/--write/--clear）；frida 17.17.0 为裁剪运行时（Memory 仅 alloc/dup/patchCode/scan，读写须 NativePointer 方法）
  - 恢复人控：--clear（值字节写 0）
- **★注入目标（对照 shogun2 R2）**：写 BATTLE_AI_EXCLUSIVE 值字节 = 1 → 引擎 AI vs AI 模式（预期：军队自动部署+自主行动+自动跳结算；副作用待实机确认——shogun2 有天气 UI/变速锁）
- **★直写目标（对照 shogun2 R3，最终形态）**：3K 版 a270 等价字段 = army 锚定后玩家军 vs AI 军差分（army 锚定捷径 = hook 0x142076DB0 抓 army 指针）
- **★★单位级控制权字段（子代理 22da1667 补轮，884e404；= shogun2 单位 +0xea8/+0xc01 的 3K 等价候选）**：
  - **battle_unit+0x3C40 = 控制权 dword**：BCQ_UNIT_CHANGE_CONTROL_STATUS handler 0x14207CD90 写（`mov [unit+0x3C40], eax`）；全 EXEC **82 处访问**，绝大多数 `cmp byte [..+0x3C40], imm` 门控——低字节非 0 判定"受控"【推断，语义 0/1/任意值待动态确认】
  - **unit+0x339C = 伴随字节标志**；**接管路径 0x1424D0F60**（遍历 [army+0x830] 控制器链表按 id 匹配 → 写 unit+0x339C=1 + unit+0x3C40=1，controller+0x2C/+0x30 = 受控 unit 计数/数组）；**释放 0x142512CD3**（同字段置 0）
  - is_controllable（方法表+0x330，handler 0x142039750）经 [unit+0x20] battle unit 对象 vfunc1 查询
  - 战斗脚本方法表 128 条全 dump → `work/method_table.txt`；无 set_control_status 类写方法（控制权写面仅 BCQ 命令 + 引擎内部路径）
  - **★动态验证方案（报告 §7.6）**：hook 0x14207CD90 / 0x1424D0F60 / 0x142512CD3 记录 (unit, 值) 对比玩家军 vs AI 军 +0x3C40/+0x339C 差异与变化时机；CE diff ±0x200 找其他激活位；对玩家军 unit 直写 +0x3C40（0↔1↔2）观察原生 AI 是否接管

## 2.5 Goal4 交叉引用：攻城 AI 钩索直登控制

- 攻城 AI 的攻墙方式选择已独立为 **Goal4**，不再作为 Goal1 行为质量附项维护。
- Goal1 只保留边界：`BATTLE_AI_EXCLUSIVE` 是否影响 settlement tactic 初始化尚无直接因果证据。
- 当前机制、修订和路线分别见 `docs/41_GOAL4_MECHANISM_MAP.md`、`42_GOAL4_LOGBOOK.md`、`43_GOAL4_EXPLORATION_MAP.md`。

## 2.4 待钻缺口（子代理 8ad327b7 battle_ai 消费者钻链中）

- ★battle_ai 值字节 [0x1440DC640] 消费者（= 3K 版 0x1adf50 决策函数；预期写 army/unit 控制字段——可能与 unit+0x3C40 汇合）
- create_ai_unit_planner 的 target（[script_obj+8]）对象类型 + planner 附着到 army/unit 的偏移
- 「原生 AI 激活」根开关字段（army 级，对照 shogun2 a270）——unit+0x3C40 是单位级候选，army 级待动态差分
- Goal4 交叉项：只有发现 `BATTLE_AI_EXCLUSIVE` 与 Wall Assault 初始化共享字段/条件分支时，才回写 Goal1。

## 2.3 ★战略定案（2026-08-19）：静态 xref 路线关闭，字段定位走动态（shogun2 同款）

- **3K 引擎字符串 → 函数关联静态不可逆**（哈希/ID 注册）：外部 lea/mov 全 REX 扫描 0 命中、luaL_Reg 表 0、方法名池纯字符串、.link 无符号（00_INDEX 战略节，证据链完整）。
- **目标1 的含义**：军队「原生 AI 激活」字段（a270 等价物）**不能靠字符串 xref 静态猜**——必须动态定位：战斗加载 → 锚定 army 对象（军队名字符串反查 / 单位数差分 / vtable 扫描）→ 字段差分实验（对照 shogun2 RE-B3：直写候选字段观察 AI 行为变化）。
- 引擎侧已知锚点（仅作动态比对用）：`AI_SCRIPT_CONTROLLER` 族（BCQ_CREATE/DESTROY @0x34E76C3）、`BCQ_`×182/`CCQ_`×191 命令族。
- 脚本侧观测（官方零成本）：`battle_start.lua:4` 的 `battle_manager:new(empire_battle:new())` 钩子 + 相机/阶段 API（30_SCRIPTING_API §2.1）——战斗加载后的行为观测通道现成。

## 3. 当前前沿疑点（★2026-08-19 更新）

- [钻链中] 3K 军队对象 a270 等价字段（64 位布局，BCQ 命令注册表 → 执行函数 → 附着点）
- [钻链中] create_ai_unit_planner 的 target 对象类型（[script_obj+8]）与 planner 附着偏移
- [未核实] 「只 release 不建 planner」玩家军队释放后引擎 battle AI 是否可能捡走（待实机，70 报告保留项）
- [未核实] 原生接管与旁观身份（目标3 复用）的交互
- [转 Goal4] 攻城 AI 钩索/墙攻方式选择见 41-43；Goal1 不再重复维护其地址清单。
- [已确证] 脚本面命令执行链全貌（战斗脚本方法表 → 命令块 → BCQ 入队 → 执行函数）——见 §2.1
