# 81 — re_toolkit 通用逆向工具告知（2026-08-28）

> 通知：三项目通用逆向工具已整合到 `re_toolkit/`（独立仓库）。
> 请 3K 项目更新工具认知，并使用 re_toolkit 完成/维护本项目的索引。

## 1. 通用工具现状

| 工具 | 路径 | 说明 |
|---|---|---|
| Ghidra headless 运行器 | `re_toolkit\ghidra\run_headless.py` | `--project 3k` 已配置 |
| 索引导出脚本 | `re_toolkit\ghidra\ExportIndex.java` | 导出 callgraph/data_refs |
| 最小分析导出 | `re_toolkit\ghidra\MinimalAnalyze.java` | `-noanalysis` 导入后手动跑结构分析器并导出（避开 3K 全量自动分析卡死） |
| 索引构建器 | `re_toolkit\index\build_index.py` | 生成 SQLite 索引 |
| 检索 CLI | `re_toolkit\index\search.py` | string/caller/callee/field/command/related |
| 原生 Ghidra MCP | `re_toolkit\mcp\start_re_mcp_ghidra.ps1` | re-mcp-ghidra 已装并验证 |

## 2. 3K 应执行的索引流程

```powershell
# 方案 A（全量自动分析，3K 上已验证会卡在 DecompilerSwitch/OperandReference，不推荐）
python re_toolkit\ghidra\run_headless.py --project 3k --import
python re_toolkit\ghidra\run_headless.py --project 3k --reuse --script ExportIndex.java
python re_toolkit\index\build_index.py --project 3k

# 方案 B（推荐，2026-08-18 已跑通）：-noanalysis + MinimalAnalyze 手动结构分析
# 首次：先导入（不自动分析）
python re_toolkit\ghidra\run_headless.py --project 3k --no-analysis
# 之后：对已导入工程跑 MinimalAnalyze（含函数/字符串导出 + ExportIndex 导出）
python re_toolkit\ghidra\run_headless.py --project 3k --reuse --script MinimalAnalyze.java
# 构建索引
python re_toolkit\index\build_index.py --project 3k
```

## 3. 当前状态（2026-08-18 已建索引）

- ✅ `re\3k_out\functions.json` = **125,238 个函数**，首地址 `0x140001050`（3K 主 exe 正确基址）。
- ✅ `re\3k_out\strings.json` = **103,784 条字符串**。
- ✅ `re\index\3k_index.sqlite` 已构建；`search.py --project 3k --string ...` 可用。
- ⚠️ `callgraph.jsonl / str_refs.jsonl / data_refs.jsonl` 目前为 **0 字节**：MinimalAnalyze 只找到了 Function Start Search / ASCII Strings / Reference，未找到 Disassembler / Data / No Return 等分析器名；下一步需补跑反汇编以生成调用图/引用。
- ⚠️ 全量自动分析（`--import`）在 3K 255MB 上会卡死，勿再直接用。

## 4. 工具更新要求

- 通用脚本不要再复制到 3K 仓库维护；一律使用 `re_toolkit/`。
- 3K 专属工具（`re/3k_*.py`、Frida 探针等）保留在 `tw3k_ai_battle\re\`。
- 开工检索先用 `re_toolkit\index\search.py --project 3k ...`。
- 禁止把 SQLite/JSONL 全量读入上下文，只取 Top-N。
