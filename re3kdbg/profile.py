"""Versioned 3K debugger profiles and executable discovery."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_PROFILE = PACKAGE_DIR / "profiles" / "3k_1.7.1.json"
# 本仓库不附带任何游戏文件。exe 路径解析优先级：
#   TW3K_EXE（完整文件路径）→ TW3K_DIR（游戏根目录）→ Steam 安装位置自动探测
_EXE_NAME = "Three_Kingdoms.exe"
_GAME_SUBPATH = os.path.join("steamapps", "common", "Total War THREE KINGDOMS")


def _steam_roots():
    """列出本机 Steam 库根目录（注册表 + libraryfolders.vdf）；非 Windows / 失败返回空表。"""
    roots = []
    try:
        import winreg
    except ImportError:
        return roots
    steam = None
    for hive, key, name in (
        (winreg.HKEY_CURRENT_USER, r"Software\\Valve\\Steam", "SteamPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\WOW6432Node\\Valve\\Steam", "InstallPath"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Valve\\Steam", "InstallPath"),
    ):
        try:
            with winreg.OpenKey(hive, key) as k:
                steam = winreg.QueryValueEx(k, name)[0]
                break
        except OSError:
            continue
    if not steam:
        return roots
    steam = os.path.normpath(steam)
    roots.append(steam)
    vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
    try:
        with open(vdf, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if line.startswith(chr(34) + 'path' + chr(34)):
                    parts = line.split(chr(34))
                    if len(parts) >= 4:
                        p = parts[3].replace(chr(92) * 2, chr(92))
                        if os.path.isdir(p):
                            roots.append(os.path.normpath(p))
    except OSError:
        pass
    return roots


def find_executable():
    """定位游戏主程序；找不到返回 None（不猜路径）。"""
    env = os.environ.get("TW3K_EXE")
    if env and os.path.isfile(env):
        return Path(env)
    cands = []
    d = os.environ.get("TW3K_DIR")
    if d:
        cands.append(os.path.join(d, _EXE_NAME))
    for root in _steam_roots():
        cands.append(os.path.join(root, _GAME_SUBPATH, _EXE_NAME))
    for c in cands:
        if os.path.isfile(c):
            return Path(c)
    return None

DEFAULT_EXE = find_executable()


def load_profile(path: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    profile_path = Path(path) if path else DEFAULT_PROFILE
    with profile_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    data["_path"] = str(profile_path)
    return data


def executable_path(value: str | os.PathLike[str] | None = None) -> Path:
    if value:
        return Path(value)
    configured = os.environ.get("TW3K_EXE")
    if configured:
        return Path(configured)
    if DEFAULT_EXE:
        return DEFAULT_EXE
    raise RuntimeError(
        "未找到 Three_Kingdoms.exe：请设置 TW3K_EXE（完整文件路径）或 "
        "TW3K_DIR（游戏根目录）。本仓库不附带游戏文件。"
    )


def rva(profile: dict[str, Any], category: str, name: str) -> int:
    value = profile[category][name]
    return int(value, 0) if isinstance(value, str) else int(value)


def absolute(profile: dict[str, Any], category: str, name: str, base: int) -> int:
    return base + rva(profile, category, name)


def address_map(profile: dict[str, Any], base: int) -> dict[str, int]:
    result: dict[str, int] = {}
    for category in ("functions", "vtables", "strings"):
        for name in profile.get(category, {}):
            result[name] = absolute(profile, category, name, base)
    return result

