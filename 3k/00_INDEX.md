# 三国分库索引（00_INDEX）

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

> 全面战争：三国（Total War: THREE KINGDOMS，v1.7.1）资料库。
> 总库入口：`../README.md`；逆向总评估：`../docs/20_REVERSE_FEASIBILITY.md`。

## 文档

| 文档 | 内容 | 状态 |
|---|---|---|
| 01_GAME_PROFILE.md | 游戏档案（版本/构建/pack/存档/mod 通道） | ✅ |
| 10_FACTIONS.md | 派系（198 行：5 剧本 + 13 首发 + DLC 派系） | ✅ |
| 11_UNITS.md | 兵种体系 | ✅ |
| 12_CHARACTERS.md | 角色/武将 | ✅ |
| 20_MECHANICS.md | 战役/战斗机制 | ✅ |
| 30_SCRIPTING_API.md | 官方脚本 API | ✅（323 行，15 库逐库取证） |
| 40_MODDING.md | mod 通道 | 待写 |
| 50_REVERSE_ASSESSMENT.md | 逆向可行性评估 | ✅ |
| research/00_3K_EXTRACT_RECORD.md | 迁移勘察记录 | ✅ |

## 提取产物（extract/3k/）

- `script/` — data.pack script/ 全量 1,454 文件（_lib 15 核心库）
- `db_raw/` — database.pack 全量 1,503 表
- `pack_lists/data_pack_paths.txt` — 44,189 路径
- `pack_lists/database_pack_paths.txt` — DB 表路径

## 关键结论

1. pack 完全可读（RPFM v4.3.7 + 自研提取器交叉验证）
2. **官方脚本 API 覆盖 shogun2 逆向数月成果**（pending battle/人类判定/AI planner/相机）
3. 引擎级"原生 AI 激活"无官方 API → 唯一需要逆向的点
4. 无 Assembly Kit（与 WH3 不同）；ESF 存档 esfpy 可复用

## 待办

- [ ] 30_SCRIPTING_API 定稿（subagent 进行中）
- [ ] DB 表解码（schema_3k.ron → 表数据）
- [ ] 战役脚本加载机制实机验证（mod 覆盖 script/）
- [ ] 文字本地化定位（3K 中文本地化位置确认）
