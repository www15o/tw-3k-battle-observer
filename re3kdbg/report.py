"""Deterministic JSONL-to-summary reporting for Agent consumption."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


def read_events(path: str | Path) -> list[dict[str, Any]]:
    events = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def summarize(events: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(event.get("hook", event.get("event", "unknown")) for event in events)
    entries = defaultdict(set)
    tasks = set()
    kinds = Counter()
    parent_kinds = defaultdict(set)
    empty_group_signals = 0
    retry_signals = 0
    repeated_entries = Counter()
    repeated_call_keys = Counter()
    orchestrator_counts = Counter()
    clear_target_events = 0
    for event in events:
        body = event.get("body", {})
        hook = event.get("hook", event.get("event", "unknown"))
        if hook.endswith(".enter") and any(
            hook.startswith(prefix)
            for prefix in (
                "wall_assault_orchestrator",
                "gate_group_factory",
                "alternate_group_factory_a",
                "dismount_group_factory",
                "alternate_group_factory_b",
            )
        ):
            orchestrator_counts[hook] += 1
        if hook == "entry_clear_target.leave":
            clear_target_events += 1
        for candidate in (body.get("entry"), body.get("entry_arg")):
            if isinstance(candidate, dict) and candidate.get("entry"):
                entries[candidate["entry"]].add(candidate.get("kind", "unknown"))
                kinds[candidate.get("kind", "unknown")] += 1
                repeated_entries[(hook, candidate["entry"])] += 1
        parent = body.get("parent")
        if isinstance(parent, dict) and parent.get("parent"):
            for candidate in parent.get("entries", []):
                if isinstance(candidate, dict):
                    parent_kinds[parent["parent"]].add(candidate.get("kind", "unknown"))
            if hook in ("plan_entry.enter", "wall_assault_postprocess.enter"):
                repeated_call_keys[(hook, parent["parent"])] += 1
        if body.get("entry_count") == 0:
            empty_group_signals += 1
        if isinstance(parent, dict) and parent.get("entry_count") == 0:
            empty_group_signals += 1
        task = body.get("task")
        if task:
            tasks.add(task)
            if hook == "throw_grapples.enter":
                repeated_call_keys[(hook, task)] += 1
    for (hook, _entry), count in repeated_entries.items():
        if hook in ("plan_entry.enter", "throw_grapples.enter") and count > 1:
            retry_signals += count - 1
    retry_candidates = [
        {"key": list(key), "count": count}
        for key, count in repeated_call_keys.items()
        if count > 1
    ]
    return {
        "event_count": len(events),
        "hook_counts": dict(counts),
        "entry_kinds": dict(kinds),
        "unique_entries": {key: sorted(value) for key, value in entries.items()},
        "unique_tasks": sorted(tasks),
        "grapple_execution_count": counts.get("throw_grapples.enter", 0),
        "empty_group_signals": empty_group_signals,
        "retry_signals": retry_signals,
        "retry_candidates": retry_candidates,
        "orchestrator_counts": dict(orchestrator_counts),
        "entry_clear_target_events": clear_target_events,
        "parents_with_multiple_entry_kinds": sum(1 for kinds_for_parent in parent_kinds.values() if len(kinds_for_parent) > 1),
        "fallback_proven": False,
        "warnings": [
            "This report proves observations only; it does not prove cross-entry fallback.",
            "Repeated calls are potential retries only; release/requeue and controller ownership are not yet observed.",
            "Capability +0xAC is diagnostic only and is never a patch target.",
        ],
    }


def markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# 3K Goal4 trace report",
        "",
        f"- Events: {summary['event_count']}",
        f"- Grapple executions: {summary['grapple_execution_count']}",
        f"- Empty-group signals: {summary['empty_group_signals']}",
        f"- Retry signals: {summary['retry_signals']}",
        f"- Entry target clears: {summary['entry_clear_target_events']}",
        f"- Parents with multiple entry kinds: {summary['parents_with_multiple_entry_kinds']}",
        f"- Fallback proven: {summary['fallback_proven']}",
        "",
        "## Hook counts",
        "",
    ]
    for key, value in summary["hook_counts"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "## Entry kinds", ""]
    for key, value in summary["entry_kinds"].items():
        lines.append(f"- `{key}`: {value}")
    lines += ["", "## Warnings", ""]
    lines += [f"- {warning}" for warning in summary["warnings"]]
    return "\n".join(lines) + "\n"
