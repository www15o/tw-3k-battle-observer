"""CLI for the project-local 3K debugger."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .frida_bridge import FridaBridge, find_pid
from .pe import PEImage
from .profile import DEFAULT_PROFILE, executable_path, load_profile
from .report import markdown, read_events, summarize
from .trace import trace_goal4


def emit(value, as_json: bool = True):
    if as_json:
        print(json.dumps(value, ensure_ascii=False, indent=2))
    else:
        print(value)


def emit_jsonl(value):
    print(json.dumps(value, ensure_ascii=False), flush=True)


def cmd_status(args):
    profile = load_profile(args.profile)
    exe = executable_path(args.exe)
    result = {"profile": profile["version"], "profile_path": profile["_path"], "executable": str(exe)}
    if exe.exists():
        image = PEImage(exe)
        expected_hash = profile.get("sha256", "").upper()
        result["pe"] = image.summary()
        result["profile_hash_matches"] = not expected_hash or image.sha256() == expected_hash
        result["profile_base_matches"] = image.image_base == int(profile["image_base"], 0)
    else:
        result["error"] = "executable not found"
    try:
        result["pid"] = find_pid()
    except Exception as exc:
        result["pid_lookup_error"] = str(exc)
    emit(result, True)
    return 0 if "error" not in result else 2


def cmd_static_profile(args):
    profile = load_profile(args.profile)
    emit(profile, True)
    return 0


def cmd_static_verify(args):
    profile = load_profile(args.profile)
    image = PEImage(executable_path(args.exe))
    checks = []
    for name, pattern in profile.get("aobs", {}).items():
        rva = int(profile["functions"][name], 0)
        address = image.image_base + rva
        checks.append({"name": name, "address": f"0x{address:X}", "match": image.verify_aob(address, pattern)})
    result = {
        "profile": profile["version"],
        "sha256": image.sha256(),
        "hash_match": image.sha256() == profile.get("sha256", "").upper(),
        "image_base": f"0x{image.image_base:X}",
        "image_base_match": image.image_base == int(profile["image_base"], 0),
        "checks": checks,
        "ok": image.sha256() == profile.get("sha256", "").upper()
        and image.image_base == int(profile["image_base"], 0)
        and all(item["match"] for item in checks),
    }
    emit(result, True)
    return 0 if result["ok"] else 3


def cmd_static_xrefs(args):
    image = PEImage(executable_path(args.exe))
    target = int(args.target, 0)
    refs = image.call_xrefs(target)
    emit({"target": f"0x{target:X}", "refs": [f"0x{ref:X}" for ref in refs]}, True)
    return 0


def require_profile_image(profile, exe_arg=None):
    image = PEImage(executable_path(exe_arg))
    expected_hash = profile.get("sha256", "").upper()
    actual_hash = image.sha256().upper()
    if expected_hash and actual_hash != expected_hash:
        raise RuntimeError(f"profile hash mismatch: expected {expected_hash}, got {actual_hash}")
    expected_base = int(profile["image_base"], 0)
    if image.image_base != expected_base:
        raise RuntimeError(f"profile image base mismatch: expected 0x{expected_base:X}, got 0x{image.image_base:X}")
    failed = []
    for name, pattern in profile.get("aobs", {}).items():
        rva = int(profile["functions"][name], 0)
        if not image.verify_aob(image.image_base + rva, pattern):
            failed.append(name)
    if failed:
        raise RuntimeError("AOB verification failed: " + ", ".join(failed))
    return image


def cmd_attach(args):
    profile = load_profile(args.profile)
    image = require_profile_image(profile, args.exe)
    with FridaBridge(pid=args.pid) as bridge:
        info = bridge.load()
        emit({"attached": True, "profile": profile["version"], "image": image.summary(), "info": info}, True)
    return 0


def cmd_inspect(args):
    profile = load_profile(args.profile)
    image = require_profile_image(profile, args.exe)
    with FridaBridge(pid=args.pid) as bridge:
        bridge.load()
        value = bridge.script.exports_sync.readobject(args.object)
        emit({"profile": profile["version"], "image": image.summary(), "object": value}, True)
    return 0


def cmd_trace(args):
    profile = load_profile(args.profile_file)
    if args.profile_name != "goal4.grapple":
        raise SystemExit(f"unsupported trace profile: {args.profile_name}")
    require_profile_image(profile, args.exe)
    trace_goal4(profile, args.pid, args.duration, args.out, lambda event: print(json.dumps(event, ensure_ascii=False), flush=True))
    return 0


def cmd_session(args):
    """Keep one Frida attachment alive and serve small JSON-RPC requests on stdin."""
    profile = load_profile(args.profile)
    image = require_profile_image(profile, args.exe)
    with FridaBridge(pid=args.pid) as bridge:
        info = bridge.load()
        emit_jsonl({"event": "session_ready", "profile": profile["version"], "image": image.summary(), "info": info})
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                request = json.loads(line)
                op = request.get("op")
                if op == "info":
                    result = bridge.script.exports_sync.info()
                elif op == "inspect":
                    result = bridge.script.exports_sync.readobject(request["object"])
                elif op == "read_u8":
                    result = bridge.script.exports_sync.readu8(request["address"])
                elif op == "read_u32":
                    result = bridge.script.exports_sync.readu32(request["address"])
                elif op == "read_ptr":
                    result = bridge.script.exports_sync.readptr(request["address"])
                elif op == "close":
                    emit_jsonl({"ok": True, "closed": True})
                    break
                else:
                    raise ValueError(f"unsupported op: {op!r}")
                emit_jsonl({"ok": True, "result": result})
            except Exception as exc:
                emit_jsonl({"ok": False, "error": str(exc)})
            time.sleep(0.001)
    return 0


def cmd_report(args):
    result = summarize(read_events(args.input))
    if args.format == "markdown":
        print(markdown(result), end="")
    else:
        emit(result, True)
    return 0


def cmd_experiment(args):
    profile = load_profile(args.profile_file)
    if args.name != "goal4.reject_grapple":
        raise SystemExit(f"unsupported experiment: {args.name}")
    plan = {
        "experiment": args.name,
        "mode": args.mode,
        "profile": profile["version"],
        "write_targets": ["pocket_eligibility", "task_factory (unresolved)"],
        "forbidden_targets": ["CanClimbLadderAndStairPipes", "battle_entities", "generic pipe capability"],
        "status": "dry-run-ready" if args.mode == "dry-run" else "blocked-until-task-factory-and-fallback-are-proven",
        "reason": "No memory write is permitted before runtime object identity and fallback are verified.",
    }
    emit(plan, True)
    return 0 if args.mode == "dry-run" else 4


def build_parser():
    parser = argparse.ArgumentParser(prog="re3kdbg", description="Agent-callable 3K Goal4 debugger")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--exe")
    status.add_argument("--profile", default=str(DEFAULT_PROFILE))
    status.add_argument("--json", action="store_true", help="emit JSON (the default; compatibility flag)")
    status.set_defaults(func=cmd_status)

    static = sub.add_parser("static")
    static_sub = static.add_subparsers(dest="static_command", required=True)
    prof = static_sub.add_parser("profile")
    prof.add_argument("--profile", default=str(DEFAULT_PROFILE))
    prof.set_defaults(func=cmd_static_profile)
    verify = static_sub.add_parser("verify")
    verify.add_argument("--exe")
    verify.add_argument("--profile", default=str(DEFAULT_PROFILE))
    verify.set_defaults(func=cmd_static_verify)
    xrefs = static_sub.add_parser("xrefs")
    xrefs.add_argument("--target", required=True)
    xrefs.add_argument("--exe")
    xrefs.set_defaults(func=cmd_static_xrefs)

    attach = sub.add_parser("attach")
    attach.add_argument("--pid", type=int)
    attach.add_argument("--exe")
    attach.add_argument("--profile", default=str(DEFAULT_PROFILE))
    attach.set_defaults(func=cmd_attach)

    inspect = sub.add_parser("inspect")
    inspect.add_argument("--object", required=True)
    inspect.add_argument("--pid", type=int)
    inspect.add_argument("--exe")
    inspect.add_argument("--profile", default=str(DEFAULT_PROFILE))
    inspect.set_defaults(func=cmd_inspect)

    trace = sub.add_parser("trace")
    trace.add_argument("--profile-name", default="goal4.grapple")
    trace.add_argument("--profile-file", default=str(DEFAULT_PROFILE))
    trace.add_argument("--pid", type=int)
    trace.add_argument("--duration", type=float, default=0)
    trace.add_argument("--out")
    trace.add_argument("--exe")
    trace.add_argument("--jsonl", action="store_true", help="retain JSONL stdout; default output is already JSONL")
    trace.set_defaults(func=cmd_trace)

    session = sub.add_parser("session", help="persistent read-only JSON-RPC over stdin/stdout")
    session.add_argument("--pid", type=int)
    session.add_argument("--exe")
    session.add_argument("--profile", default=str(DEFAULT_PROFILE))
    session.set_defaults(func=cmd_session)

    report = sub.add_parser("report")
    report.add_argument("--input", required=True)
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    report.set_defaults(func=cmd_report)

    experiment = sub.add_parser("experiment")
    experiment.add_argument("name")
    experiment.add_argument("--mode", choices=("dry-run", "apply"), default="dry-run")
    experiment.add_argument("--profile-file", default=str(DEFAULT_PROFILE))
    experiment.set_defaults(func=cmd_experiment)
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
