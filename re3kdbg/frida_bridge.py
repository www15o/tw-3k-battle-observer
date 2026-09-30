"""Frida lifecycle and a deliberately read-only JS memory facade."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Callable


def import_frida():
    candidates = [
        Path(__file__).resolve().parents[1] / "extract" / "tools" / "pyfrida",
        Path(__file__).resolve().parents[2] / "tw3k_wh3_databank" / "extract" / "tools" / "pyfrida",
    ]
    for candidate in candidates:
        if candidate.is_dir() and str(candidate) not in sys.path:
            sys.path.insert(0, str(candidate))
    import frida  # type: ignore

    return frida


def find_pid(target: str = "Three_Kingdoms.exe") -> int | None:
    frida = import_frida()
    for process in frida.get_local_device().enumerate_processes():
        if process.name.lower() == target.lower():
            return process.pid
    return None


JS_READONLY = r"""
'use strict';
const main = Process.enumerateModules().filter(m => m.name.toLowerCase() === 'three_kingdoms.exe')[0]
    || Process.enumerateModules()[0];
const BASE = ptr(main.base);
function hex(p) { try { return ptr(p).toString(); } catch (_) { return 'null'; } }
function readPtr(p) { try { return ptr(p).readPointer(); } catch (_) { return NULL; } }
function readU8(p) { try { return ptr(p).readU8(); } catch (_) { return null; } }
function readU32(p) { try { return ptr(p).readU32(); } catch (_) { return null; } }
function ptrOrNull(p) { try { return ptr(p); } catch (_) { return NULL; } }
function entryInfo(e, pocket, siege) {
  const p = ptrOrNull(e);
  if (p.isNull()) return null;
  const vt = readPtr(p);
  return {entry:hex(p), vtable:hex(vt),
    kind:vt.equals(pocket)?'Pocket Ladders':(vt.equals(siege)?'Siege Vehicle':'other'),
    target:hex(readPtr(p.add(0x30))), group:hex(readPtr(p.add(0x40))), ready:readU8(p.add(0x100))};
}
function capabilityInfo(obj) {
  const p = ptrOrNull(obj);
  if (p.isNull()) return {object:'null', capability:'null', capability_ac:null};
  const cap = readPtr(p.add(0x3cd8));
  return {object:hex(p), object_vtable:hex(readPtr(p)), capability:hex(cap),
    capability_ac:cap.isNull()?null:readU8(cap.add(0xac))};
}
rpc.exports = {
  info() { return {pid:Process.id, arch:Process.arch, module:main.name,
    base:hex(BASE), size:main.size, path:main.path}; },
  readu8(address) { return ptr(address).readU8(); },
  readu32(address) { return ptr(address).readU32(); },
  readptr(address) { return ptr(address).readPointer().toString(); },
  readobject(address) {
    const p=ptr(address); return {address:p.toString(), vtable:readPtr(p).toString(),
      plus30:hex(readPtr(p.add(0x30))), plus40:hex(readPtr(p.add(0x40))),
      plus100:readU8(p.add(0x100)), plus1b4:readU32(p.add(0x1b4)),
      plus1b8:hex(readPtr(p.add(0x1b8))), capability:capabilityInfo(p)};
  }
};
"""


class FridaBridge:
    def __init__(self, pid: int | None = None, target: str = "Three_Kingdoms.exe"):
        self.frida = import_frida()
        self.device = self.frida.get_local_device()
        self.pid = pid or find_pid(target)
        if not self.pid:
            raise RuntimeError(f"{target} is not running")
        self.session = self.device.attach(self.pid)
        self.script = None

    def load(self, source: str = JS_READONLY, on_event: Callable[[dict[str, Any]], None] | None = None):
        self.script = self.session.create_script(source)
        if on_event:
            def on_message(message, _data):
                if message.get("type") == "send":
                    on_event(message["payload"])
                elif message.get("type") == "error":
                    on_event({"event": "frida_error", "error": message.get("stack") or message.get("description")})
            self.script.on("message", on_message)
        self.script.load()
        return self.script.exports_sync.info()

    def close(self):
        if self.session:
            self.session.detach()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc, _tb):
        self.close()

