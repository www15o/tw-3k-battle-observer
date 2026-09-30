# 23_GOAL2_EXPLORATION_MAP — 目标2 指挥地图（分层：目标 → 路线 → 技术路径 → 证据/行动）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 定位：**指挥地图**（不是标记清单）——把目标拆成路线，路线拆成技术路径，技术路径拆成证据+行动，每层明确分割。
> 前线指挥官开工先看本图**认领一条技术路径**；卡住回来看本图**换路径**；总指挥按本图**派工与验收**。
> 机制事实以 21 为准；证伪历史以 22 为准。
> 认知源：shogun2 目标2 看海闭环（26_HANDOFF：faction+0x6a0=0 + manager=FULL_MANAGER）+ `51_3K_MIGRATION_PLAN.md` §目标2（含 v2 勘误：看海非 startpos 实现）。
> 最后更新：2026-08-19（★静态补足轮：CAIMT 枚举/管理器名表已定案，3-2/3-3 技术路径更新）。

---

## 0. 目标层（终点）

**目标2 = 3K 战役中玩家派系交给 CAI 自主发展（看海），玩家只观察，回合自动推进，可恢复人控。**

- **成功判据**：玩家派系被 CAI 托管、自主行动（招募/进军/外交），回合自动推进，战斗可发生；恢复人控合法不崩。
- **已确证边界（勿重探）**：官方无「派系切 CAI」API（70 报告 §6 铁证：switch_to_cai/handover/grant_faction 0 命中；is_human 只读；无 hotseat）→ 真看海需引擎层运行时字段。
- **★不是目标的部分（附加）**：CAI 行为质量调优（进攻欲望/扩张倾向等 personality）= 附加项，不参与路线判定。
- **失败形态**：玩家派系卡回合 / 无行动（只过回合缺行动，shogun2 疑缺 manager 控制器教训）/ 反向操作崩（AI 改人类，shogun2 P40/P42）。

---

## 1. 地图分层方法论（怎么读这张图）

| 层 | 是什么 | 回答什么问题 | 谁用 |
|---|---|---|---|
| **目标层**（§0） | 最终验收 | 我们要到哪 | 总指挥/全体 |
| **路线层**（§2） | 达成方式的逻辑分法 | 走哪条大路（互斥） | 总指挥定方向 |
| **技术路径层**（§3） | 每条路线下的具体方案 | 这条路怎么走、通不通 | 前线指挥官认领 |
| **证据/行动层**（每路径内） | 已确证什么 + 下一步做什么 | 现在手里有什么、最小下一步是什么 | 执行者 |

**每条技术路径固定四段**：**原理** → **证据**（✅ 实机 / 🔶 静态 / ⬜ 无）→ **行动**（最小可行实验）→ **判据**（可证伪）。

---

## 2. 路线层（互斥路线——达成方式的逻辑）

> 目标2 的两条路线回答同一个问题：**「让玩家派系被 CAI 托管」靠什么达成？**——靠官方存档/脚本旁路，还是靠引擎层人类标志 + CAI manager？

### 路线1：官方通道旁路（cm: API + startpos + FakeObserverMode）
- **逻辑依据**：工坊 FakeObserverMode 先例（附庸 + 观察员传送）+ startpos personality 调整 + cm: 战役 API。
- **现状**：⚠️ **51 蓝图 v2 勘误定案**——startpos 只调 personality，**不是真看海**；FakeObserverMode = 伪观察者（附庸+传送），非「玩家派系 CAI 化」；官方无派系切 CAI API（70 报告 §6）。
- **剩余价值**：低成本「伪看海」体验（观察 AI 世界），可作目标2 达成的过渡/观测形态。
- **手段家族**（占位）：[占位] startpos.esf personality 编辑 / FakeObserverMode 迁移 / cm: 事件观测

### 路线2：引擎层人类标志 + CAI manager（3K 版 faction+0x6a0 + FULL_MANAGER）
- **逻辑依据**：shogun2 真看海 = 运行时直写 faction+0x6a0=0 + manager=FULL_MANAGER（26_HANDOFF 织田 34 回合实证）；3K 同族引擎（Rome2 系 64 位）应有等价字段。
- **现状**：⬜ 未启动；入口候选 = 引擎串 `CAIMT_FULL_MANAGER`/`MAINTAINANCE_MANAGER`（@0x34B1BE0）+ `CCQ_FACTION_SWITCH_HUMAN_TO_AI`（目标2 引擎锚，= shogun2 FUN_10600c20 的 3K 命令名，71 报告 §2）。
- **手段家族**（占位）：[占位] faction 人类标志直写 / manager 表直写 / CCQ 命令注入
- **完成标准**：玩家派系 CAI 化且不崩、可恢复人控合法（对照 shogun2 判据）。

### 路线3（备选）：hotseat 类旁路
- **逻辑依据**：shogun2 系无 hotseat 的旁路思考；3K 引擎串 `hotseat_mode_enabled` 存在但恒假。
- **现状**：⬜ 未探（70/71 报告：3K 无 hotseat 模式）。
- **手段家族**（占位）：[占位]

---

## 3. 技术路径层（★2026-08-19 更新）

> 每条路径四段：**原理 / 证据 / 行动 / 判据**。骨架建立后由前线指挥官认领填充。

- **3-1** [占位→★2026-08-19 定案]：~~引擎字符串 xref 找 faction 人类标志字段~~ → **关闭**（哈希注册不可逆）。替代 = **动态锚定三通道**（g2 §Q3，work/probe_faction_scan.py 已备）：A. 国库值差分（Frida Memory.scan int32，对照 FACTION_ECONOMICS 存档值）B. faction key 字符串反查（"3k_main_liu_bei" 等 → x64 指针反查对象）C. vtable 扫描。
- **3-2** [占位→★更新]：**CAI manager 表定位已静态定案**——CAIMT 枚举（FULL=0...HUMAN=6,NUM=9，表序=值）+ 管理器名指针表 @0x143C101A0（.didata，纯动态锚点）。行动 = 实机 hook 字符串查找 0x1407DA9D0（抓 CAIMT 名查询时刻）或内存断点表地址 → 反查 manager 表运行时位置（对照 shogun2 manager 表 = {key, manager_id} 条目）。
- **3-3** [占位→★更新]：**CCQ_FACTION_SWITCH_HUMAN_TO_AI 命令分发**——静态 xref 不可行（哈希注册）；已定案为战役调试命令簇成员（@0x34B09E0 区）。动态 = ① 子代理钻 .didata CCQ 命令表（仿战斗表模式，钻链中）；② frida hook CCQ 命令入口（命令队列机制同 shogun2 BCQ/CCQ 族）或观察派系切换行为差分。
- **3-4** [占位→更新]：验证闭环——官方观测层现成（FactionTurnStart/End/WorldStartOfRoundEvent/PendingBattle + cm:query_faction 查询）；**可强制 AI 内战**（apply_automatic_diplomatic_deal 宣战条约，dlc07_imperial_intrigue L265-291）。
- **★执行层实机清单**（工具已就绪）：① Frida attach smoke ② probe_faction_scan 国库差分 → faction 锚定 ③ PLAYER_SETUP[2] ↔ 运行时人类标志交叉验证 ④ 看海观测基线（回合推进日志）⑤ hook 0x1407DA9D0 抓 CAIMT 查询。

## 4. 附加（非目标，不参与路线判定）

- [占位] CAI 行为质量项（进攻欲望/扩张倾向等，待攻坚后列）

## 5. 当前前沿（★2026-08-19 更新）

- [钻链中] 子代理 5cf46d44：CCQ 命令表 + CAI 设置注册消费函数（产出 work/g2_ccq_manager_static.md）
- [下一步] 实机动态：faction 锚定（国库差分）→ 人类标志字段差分 → manager 表反查
