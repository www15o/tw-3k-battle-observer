# 三国 mod 通道（40_MODDING）

> 本文件整理三国可用的 mod/修改通道（按成本排序）。总方法论见 `docs/10_TOOLCHAIN.md`。

## 通道清单

| 通道 | 成本 | 状态 | 说明 |
|---|---|---|---|
| pack mod | 低 | ✅ 可用 | `data/` 下放 .pack 覆盖（社区标准路线）；需遵循 pack 加载顺序 |
| 官方 Lua 脚本覆盖 | 低 | ✅ 可用（待验证加载机制） | mod 覆盖 `script/` 目录；**加载机制未实机验证** |
| DB 表编辑 | 中 | ⚠️ 工具就绪 | database.pack 已提取；schema_3k.ron 可解码；编辑后需重新打包 |
| ESF 存档修改 | 中 | ✅ 可用 | esfpy 读写（startpos/存档） |
| 引擎注入 | 高 | ⬜ 未启动 | 64 位直写字段/注入（见 50_REVERSE_ASSESSMENT） |

## 关键机制

- **无官方 Assembly Kit**（CA 未发布 3K 编辑器）→ 地图/模型 mod 受限，数据 mod 走 pack
- 加载优先级：pack 文件名排序靠后者覆盖前者（社区惯例，待实机确认）
- DB 表 raw 格式：`fd fe fc ff` 版本标记 + 表 GUID + 二进制数据行（与 Rome2 系同构）

## 社区资源（调研待补）

- Steam Workshop 3K 创意工坊
- 3DM/贴吧 三国 mod 社区
- RPFM（pack 编辑工具，v4.3.7 支持 3K）

## 未核实项

- script/ 覆盖加载机制（mod 是否真的能注入战役脚本）
- pack 加载顺序细节
- DB 表重新打包的校验（游戏是否验证签名）
