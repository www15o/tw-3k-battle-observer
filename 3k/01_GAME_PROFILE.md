# 全面战争：三国（3K）— 游戏档案（01_GAME_PROFILE）

> 勘察日期：2026-08。全部信息来自本地安装实测 + 公开资料。

## 基本信息

| 项 | 值 |
|---|---|
| 游戏 | Total War: THREE KINGDOMS（全面战争：三国） |
| Steam AppID | 779340 |
| 开发商 | The Creative Assembly |
| 本地版本 | **1.7.1**（exe FileVersion 1.7.1.0） |
| Steam buildid | 20435474 |
| 安装目录 | 随本机 Steam 库而定，形如 `<Steam 库>\steamapps\common\Total War THREE KINGDOMS` |
| 主程序 | Three_Kingdoms.exe（255,088,776 字节 ≈ 243MB） |
| 位数 | 64 位 |
| DRM | 无 Denuvo 迹象（仅 steam_api64.dll + EOSSDK-Win64-Shipping.dll，联机服务非 DRM） |
| 引擎 | Warscape（Rome2 系同源，64 位分支；主逻辑内嵌 exe，无独立引擎 DLL） |

## 首发与 DLC 时间线（公开资料）

- 2019-05-23 发售
- DLC：黄巾之乱（首发）、八王之乱（2019-08）、受命于天 Mandate of Heaven（2020-01）、弃叛之世 A World Betrayed（2020-03）、南蛮 The Furious Wild（2020-09）、命运分歧 Fates Divided（2021-03）、士别三年/官渡？——最终版更新 v1.7（2021-05 后）
- v1.7.1 为最终版本（CA 2021 年宣布停止 3K 后续内容支持）
- 简体中文为官方首发语言之一（本地 local_zh.pack 仅 0.2GB，主文本在 data.pack 内嵌中英双语）

## 安装内容（data 目录，36 个 pack，共 56.1GB）

关键 pack：

| pack | 大小 | 内容 |
|---|---|---|
| data.pack | 5.73 GB | 主包：44,189 文件（ui 24,761 / animations 13,479 / script 1,454 / prefabs 2,695 / shaders 450 等） |
| database.pack | 60 MB | **DB 表**（1,503 表，本库已提取至 ../extract/3k/db_raw） |
| boot.pack | ~0 | boot 资源 |
| fast.pack | 0.82 GB | 快速加载资源 |
| data_dlc06.pack / data_mh.pack | ~0 | DLC 数据（data_mh = 南蛮 Meng Huo） |
| local_zh.pack | 0.2 GB | 简体中文（text/localisation__.loc 19.5MB 合并文案 + 字体；已提取至 ../extract/3k/local_zh/） |
| local_en.pack 等 | 各 0.26-2.5 GB | 其他语言 |
| audio/models/movies/terrain/variants/vegetation | 合计 ~46 GB | 资产 |

## pack 格式勘察（2026-08 实测）

- 格式：**PFH5**（magic `50 46 48 35`），RPFM v4.3.7 可完整读取 ✓
- 布局（自研解析实证）：header 0x1C 字节 + 文件索引（头部，非尾部）+ 数据区
  - 索引：`u32 file[0]大小` + 每条目 `[flags:1][name\0][u32=下一个文件大小]`
  - 3K flags 恒为 0x00（**未压缩**）；WH3 flags=0x01（zstd 压缩，见 wh3 档案）
- 详见 `../docs/10_TOOLCHAIN.md` 与 `../extract/tools/pfh5_extract.py`

## 存档格式

- 战役存档 / startpos：**ESF 格式**（已实证：`campaigns/3k_main_campaign_map/startpos_historical.esf` + `startpos_romance.esf` 位于 data.pack 内；DLC 各自有 startpos，如 3k_dlc04/05/07_start_pos；8p_start_pos 为多人）
- **esfpy 兼容性已实测**：esfpy（shogun2_ai_battle/tools/esfpy）成功解析 3K startpos_historical.esf（3.3MB，魔数 CA AB 与幕府2 一致）
- 战斗回放：Battle Replay（ESF 树结构，与幕府2 同机制家族，具体路径待勘察）

## 官方 mod 通道

| 通道 | 状态 |
|---|---|
| pack mod（data/ 下 .pack） | ✓ 原生支持（社区标准路线） |
| 官方 Lua 脚本覆盖（script/） | ✓ 官方脚本库全量暴露（见 30_SCRIPTING_API） |
| Assembly Kit（官方编辑器） | ✗ **未发布**（CA 未给 3K 出官方 mod 工具包；与 WH3 不同） |
| 存档修改（ESF） | ✓ esfpy 可读写 |
| 引擎注入（内存层） | 64 位，可行但成本高（见 50_REVERSE_ASSESSMENT） |

## 关键事实速查

- 三国 = Rome2 系引擎 64 位分支；幕府2 = 32 位旧分支 → **逆向工具链不可直接复用**（Ghidra 可分析 x64，但地址/结构全不同）
- 官方脚本 API 覆盖了幕府2 项目逆向数月才得到的核心概念 → 优先走官方通道
