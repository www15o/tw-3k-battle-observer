# re3kdbg

说明：文中出现的 work/ 、testkit/ 、experiments/ 、outputs/ 、extract/ 、re/ 等路径指作者私有工作目录，未随本库公开。

项目专用的 Agent 可调用调试工具，面向 Total War: THREE KINGDOMS v1.7.1 Goal4。

## 安全边界

- 默认只读：PE 校验、Frida attach、对象检查、调用链追踪、JSONL 报告。
- 不修改 `CanClimbLadderAndStairPipes`、`battle_entities` 或通用 pipe 能力。
- `goal4.reject_grapple --mode apply` 当前会明确拒绝执行，直到吊绳 task factory、对象同一性和 fallback 被实机证明。
- 地址来自版本 profile，哈希/AOB 不匹配时拒绝继续。

## 常用命令

```powershell
python -m re3kdbg status --json
python -m re3kdbg static verify
python -m re3kdbg static xrefs --target 0x142601970
python -m re3kdbg attach --pid 1234
python -m re3kdbg inspect --object 0x... --pid 1234
python -m re3kdbg trace --profile-name goal4.grapple --duration 120 --out work/goal4_trace.jsonl
python -m re3kdbg report --input work/goal4_trace.jsonl --format markdown
python -m re3kdbg experiment goal4.reject_grapple --mode dry-run
```

`trace` 的 stdout 和 `--out` 文件均为 JSONL。`goal4.grapple` 除 Pocket Ladders/任务端点外，还观测 Wall Assault 高层编排、entry 目标清理，并记录线程号、调用者和原始参数；这些事件用于判断单位是否被释放和重新规划，不能单独证明 fallback。
