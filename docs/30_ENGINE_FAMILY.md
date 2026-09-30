# 全战引擎族谱（30_ENGINE_FAMILY）

> 两款游戏在 Warscape 引擎家族中的位置；说明为什么 shogun2 的逆向成果不可直接复用、方法论可复用。

## 族谱简表

```
Warscape 引擎
├── 32 位分支（早期）
│   ├── Empire (2009) / Napoleon (2010)
│   ├── Shogun 2 (2011)          ← shogun2_ai_battle 项目（逆向对象）
│   └── Rome 2 (2013) 早期
├── 64 位分支（Rome2 系，2013+）
│   ├── Rome 2 (2013) / Attila (2015)
│   ├── Warhammer (2016) / Warhammer 2 (2017) / Thrones of Britannia (2018)
│   ├── Three Kingdoms (2019)    ← 本库 3K
│   ├── Troy (2020)
│   └── Warhammer 3 (2022)       ← 本库 WH3（含 clockwork 跨平台框架）
└── 独立分支
    └── Pharaoh Dynasties (2023-2024，新引擎方向)
```

## 关键结论

1. **3K 与 WH3 同属 Rome2 系 64 位分支** → 脚本 API 同族（lib_* 库结构一致，已实证）；pack 结构同族但 WH3 工具链换代（zstd）
2. **shogun2（32 位旧分支）逆向成果不可直接复用**：地址/结构/字段完全不同；但方法论（验证闭环、字段定位法、esfpy 存档法）100% 可迁移
3. **3K 是 Rome2 系 64 位的"停更版"**（v1.7.1 后 CA 停止支持）→ 逆向成果保值期长
4. **WH3 是 Rome2 系 64 位的最新运营版**（2026 仍在更新）→ 逆向成果保值期短（版本漂移）
5. **Pharaoh Dynasties**（本机也有安装）是独立新方向，暂不在本库范围

## 引擎层差异速查

| 项 | shogun2 | 3K | WH3 |
|---|---|---|---|
| 位数 | 32 | 64 | 64 |
| 独立引擎 DLL | 有 | 无（exe 内嵌） | 无（exe 内嵌）+ clockwork 框架 |
| pack | PFH4/PFH5 | PFH5（未压缩） | PFH5 变体（zstd） |
| 官方脚本 | 有限 | 完整 | 完整 + Assembly Kit |
| 存档 | ESF | ESF | .save（ESF 家族待验证） |
