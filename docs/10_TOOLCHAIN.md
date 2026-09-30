# 工具链与解包方法（10_TOOLCHAIN）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 本库的数据层方法论：RPFM 能读的用 RPFM，不能读的（WH3 新 pack 格式）用自研解析器。
> 全部工具与产物在 `extract/`；本文件记录方法与 WH3 格式逆向的完整证据链。

## 1. 环境事实

- 本机 pwsh **无外网**（curl/Invoke-WebRequest 均 HTTP 000）→ 无法下载新版 RPFM；web 知识仅 web_search 可用
- RPFM v4.3.7：`shogun2_ai_battle\work\tools\rpfm-v4.3.7\`（含 rpfm_cli.exe、rpfm_ui.exe、zstd.dll）
- RPFM schemas（schema_*.ron）：`shogun2_ai_battle\work\schemas\`（已拷贝 schema_3k/schema_wh3/patches/anim_ids 至 `extract\schemas\`）
- Python 3.14 可用

## 2. RPFM CLI 用法（3K 适用）

```powershell
# 列包内容
rpfm_cli.exe -g three_kingdoms pack list -p <pack路径>
# 提取整个文件夹（3K data.pack 的 script/）
rpfm_cli.exe -g three_kingdoms pack extract -p <pack> -F "script;<目标目录>"
# 提取单个文件
rpfm_cli.exe -g three_kingdoms pack extract -p <pack> -f "<包内路径>;<目标目录>"
# schema ron → json（原地转换，先拷贝副本）
rpfm_cli.exe -g three_kingdoms schemas to-json --schemas-path <schemas目录>
```

**限制**：RPFM v4.3.7 无法读取 WH3 的 db.pack/data.pack/data_script.pack/local_*.pack（报 "stream/file format not recognized"）；boot.pack（旧式）可读。

## 3. ★ WH3 新 pack 格式逆向（2026-08 本库完成）

### 3.1 现象

WH3 全部主要 pack 的 magic 均为 `PFH5`，但 rpfm v4.3.7 拒绝读取。头 64 字节对比（16 进制）：

```
3K data.pack:   PFH5 | 01 00 00 00 | 00 00 00 00 | 00 00 00 00 | 9D AC 00 00 (count=44189)
                | 5D D4 3A 00 (index_size=3855453) | D2 53 BD 63 (ts) | 08 00 00 00
WH3 db.pack:    PFH5 | 01 00 00 00 | 00 00 00 00 | 00 00 00 00 | F1 05 00 00 (count=1521)
                | F6 41 01 00 (index_size=82422) | 00 00 00 00 (ts=0) | BB 00 00 00
```

### 3.2 索引结构（自研解析实证，3K 与 WH3 通用）

```
header = 0x1C 字节:
  magic(4)="PFH5" | file_type(4)=1 | 0(4) | 0(4) | file_count(4)
  | file_index_size(4) | file_index_timestamp(4)

索引区（紧随 header，在文件头部）:
  u32 = file[0] 的大小                      ← 注意：不是版本号！
  每条目 i = [flags:1][name 以 \0 结尾][u32 = file[i+1] 的大小]

数据区（紧随索引区）:
  file[0..N-1] 按索引顺序连续存放
```

**证据**：3K data.pack 解析 44,189 条与索引字节数完全吻合；file[0]（assembly_kit_rules.bob）实际 8 字节 = 首尺寸字 8；条目 u32 与 rpfm 提取的实际大小逐条吻合（1261/1567/1475/1780/1885…）。

### 3.3 关键差异：压缩

| | 3K | WH3 |
|---|---|---|
| flags 字节 | 0x00（未压缩） | **0x01**（压缩） |
| 文件体 | 原始数据 | **[u32 解压大小][zstd 压缩帧]** |

**证据**：WH3 db.pack 表文件 `db\abilities_tables\data__` 头部 = `fd fe fc ff` + GUID（表版本+元数据）；WH3 data_script.pack 的 lua 文件体偏移 4 处为 zstd 魔数 `28 B5 2F FD`；用 RPFM 自带 zstd.dll 解压 lib_battle_manager.lua 得 218,862 字节有效 Lua 源码（含 `--- @set_environment battle` 等文档注释）。

### 3.4 为什么 rpfm v4.3.7 拒绝

推论（推断，未核实 RPFM 源码）：v4.3.7（2023 年初）的 PFH5 解析不识别 flags=0x01 的压缩条目与新的索引版本字段 → 整个 pack 判定为 "stream/file format not recognized"。社区公告确认 RPFM 曾为 WH3 更新（v4.4+ 时代）；本机无网无法获取新版。

### 3.5 自研工具

| 工具 | 用途 |
|---|---|
| `extract/tools/pfh5_extract.py` | 通用 PFH5 提取器：list / extract / extract-file；zstd 自动解压（ctypes 加载 rpfm 目录 zstd.dll） |
| `extract/tools/pack_index_probe.py` | 索引结构探测（研究用） |
| `extract/tools/zstd_decompress_probe.py` | zstd 解压验证 |

**验证闭环**：3K 用 rpfm 交叉校验（bob=8B、tiger01_attack_01=1261B 等逐条吻合）；WH3 用解压后 Lua 源码有效性验证（语法可读、含官方文档注释）。

## 4. DB 表解码（未完成）

- 已提取 raw 表文件：3K database.pack 1,503 表；WH3 db.pack 1,521 表（`db\<表名>\data__`）
- **raw 表格式（2026-08 解剖实证，WH3 abilities_tables）**：
  ```
  fd fe fc ff            ← 表版本标记（0xFFFFFFFC）
  GUID（UTF-16LE 字符串，带 $ 前缀，如 "$66e12b80-00ed-4f31-af7e-bc83867c6400"）
  fc fd fe ff            ← 第二标记
  u32 version（如 4）
  ...字符串表：u16 长度 + 字节（如 0B 00 "assist_army"）
  ```
- schema：`extract/schemas/schema_3k.ron`（8.7MB）、`schema_wh3.ron`（11MB）——RPFM 的 DB 表结构定义（字段名/类型/引用）
- **下一步**：写 DB 表解码器（ron schema → 二进制表解析），或在新版 RPFM 可用后用它导出 TSV
- 辅助工具：`extract/tools/decode_table_header.py`（表头部解剖）

## 5. 存档/ESF

- 3K：ESF 格式（startpos_historical/romance.esf）；esfpy（shogun2_ai_battle/tools/esfpy）可复用
- WH3：.save（ESF 家族，适配待验证）

## 6. 其他工具

- Ghidra（shogun2 项目已有，x64 分析引擎级逆向用）
- esfpy（ESF 读写）
- rpfm_ui（GUI 浏览 3K 包）
