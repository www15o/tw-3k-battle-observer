"""Predefined Goal4 read-only tracing profile."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Callable

from .frida_bridge import FridaBridge


TRACE_JS_TEMPLATE = r"""
'use strict';
const main = Process.enumerateModules().filter(m => m.name.toLowerCase() === 'three_kingdoms.exe')[0]
    || Process.enumerateModules()[0];
const BASE = ptr(main.base);
const A_RVA = %s;
const A = {};
Object.keys(A_RVA).forEach(k => A[k] = BASE.add(A_RVA[k]));
const V_RVA = %s;
const POCKET = BASE.add(V_RVA.pocket_ladders);
const SIEGE = BASE.add(V_RVA.siege_vehicle);
let seq=0; const seen={};
function hex(p){try{return ptr(p).toString();}catch(_){return 'null';}}
function rp(p){try{return ptr(p).readPointer();}catch(_){return NULL;}}
function u8(p){try{return ptr(p).readU8();}catch(_){return null;}}
function u32(p){try{return ptr(p).readU32();}catch(_){return null;}}
function pn(p){try{return ptr(p);}catch(_){return NULL;}}
function callMeta(ctx){return {thread_id:Process.getCurrentThreadId(),caller:hex(ctx.returnAddress)};}
function rawArgs(a,count){const out=[];for(let i=0;i<count;i++)out.push(hex(a[i]));return out;}
function outRef(p){const q=pn(p);if(q.isNull())return null;return {slot:hex(q),value:hex(rp(q)),value2:hex(rp(q.add(8))),u32:u32(q)};}
function recordInfo(p){const q=pn(p);if(q.isNull())return null;return {record:hex(q),q0:hex(rp(q)),q8:hex(rp(q.add(8))),u32_8:u32(q.add(8)),u32_c:u32(q.add(0xc)),u32_10:u32(q.add(0x10)),u32_14:u32(q.add(0x14)),u32_30:u32(q.add(0x30))};}
function entry(e){const p=pn(e);if(p.isNull())return null;const v=rp(p);return {entry:hex(p),vtable:hex(v),kind:v.equals(POCKET)?'Pocket Ladders':(v.equals(SIEGE)?'Siege Vehicle':'other'),target:hex(rp(p.add(0x30))),group:hex(rp(p.add(0x40))),ready:u8(p.add(0x100))};}
function cap(o){const p=pn(o);if(p.isNull())return {object:'null',capability:'null',capability_ac:null};const c=rp(p.add(0x3cd8));return {object:hex(p),capability:hex(c),capability_ac:c.isNull()?null:u8(c.add(0xac))};}
function parent(p){const o=pn(p);if(o.isNull())return {parent:'null'};const n=u32(o.add(0x1b4)),a=rp(o.add(0x1b8)),es=[];if(!a.isNull()&&n!==null&&n<128)for(let i=0;i<n;i++)es.push(entry(a.add(i*8)));return {parent:hex(o),entry_count:n,entries:es};}
function emit(h,b){seen[h]=(seen[h]||0)+1;if(seen[h]<=1000)send({seq:++seq,ts:new Date().toISOString(),hook:h,body:b});}
function hook(name,enter,leave){Interceptor.attach(A[name],{onEnter(args){this.ctx=enter?enter.call(this,args):null;},onLeave(ret){if(leave)leave.call(this,ret);}});}
send({event:'ready',module:main.name,base:hex(BASE),addresses:A});
hook('create_entries',a=>emit('create_entries.enter',parent(a[0])));
hook('maintain_entries',a=>emit('maintain_entries.enter',parent(a[0])));
hook('plan_entry',a=>{const b=parent(a[0]);b.entry_arg=entry(a[1]);emit('plan_entry.enter',b);},r=>emit('plan_entry.leave',{ret:r.toString()}));
hook('select_wall',a=>emit('select_wall.enter',{parent:parent(a[0]),entry_arg:entry(a[1]),candidates:hex(a[2]),candidate_count:u32(pn(a[2]).add(4))}),r=>emit('select_wall.leave',{ret:r.toString()}));
hook('capability_predicate',function(a){return {call:callMeta(this),capability:cap(a[0])};},function(r){emit('capability_predicate.leave',{context:this.ctx,ret:r.toString()});});
hook('pocket_eligibility',function(a){return {call:callMeta(this),owner:hex(a[0]),entry:entry(a[1]),capability:cap(a[1])};},function(r){emit('pocket_eligibility.leave',{context:this.ctx,ret:r.toString()});});
hook('task_adapter',function(a){emit('task_adapter.enter',{call:callMeta(this),args:rawArgs(a,3),state_obj_candidate:hex(pn(a[1]).sub(0x30))});});
hook('throw_grapples',function(a){emit('throw_grapples.enter',{call:callMeta(this),task:hex(a[0]),task_vtable:hex(rp(a[0])),task_state_count:u32(pn(a[0]).add(0x7c))});});
hook('wall_assault_callback',function(a){emit('wall_assault_callback.enter',{call:callMeta(this),args:rawArgs(a,4)});});
hook('wall_assault_postprocess',function(a){emit('wall_assault_postprocess.enter',{call:callMeta(this),args:rawArgs(a,4)});});
hook('task_record_builder',function(a){return {call:callMeta(this),args:rawArgs(a,5),record_arg:recordInfo(a[0])};},function(r){emit('task_record_builder.leave',{context:this.ctx,ret:hex(r),record:recordInfo(this.ctx&&this.ctx.record_arg&&this.ctx.record_arg.record)});});
hook('postprocess_unit_eligibility',function(a){return {call:callMeta(this),args:rawArgs(a,3),object:recordInfo(a[0])};},function(r){emit('postprocess_unit_eligibility.leave',{context:this.ctx,ret:r.toString()});});
hook('wall_assault_orchestrator',function(a){emit('wall_assault_orchestrator.enter',{call:callMeta(this),stack_pointer:hex(this.context.sp),args:rawArgs(a,4)});},function(r){emit('wall_assault_orchestrator.leave',{ret:r.toString()});});
hook('gate_group_factory',function(a){this.factory_args=a;return {call:callMeta(this),args:rawArgs(a,4),out_refs:[outRef(a[1]),outRef(a[2]),outRef(a[3])]};},function(r){emit('gate_group_factory.call',{context:this.ctx,ret:r.toString(),out_refs:[outRef(this.factory_args[1]),outRef(this.factory_args[2]),outRef(this.factory_args[3])]});});
hook('alternate_group_factory_a',function(a){this.factory_args=a;return {call:callMeta(this),args:rawArgs(a,4),out_refs:[outRef(a[1]),outRef(a[2]),outRef(a[3])]};},function(r){emit('alternate_group_factory_a.call',{context:this.ctx,ret:r.toString(),out_refs:[outRef(this.factory_args[1]),outRef(this.factory_args[2]),outRef(this.factory_args[3])]});});
hook('dismount_group_factory',function(a){this.factory_args=a;return {call:callMeta(this),args:rawArgs(a,4),out_refs:[outRef(a[1]),outRef(a[2]),outRef(a[3])]};},function(r){emit('dismount_group_factory.call',{context:this.ctx,ret:r.toString(),out_refs:[outRef(this.factory_args[1]),outRef(this.factory_args[2]),outRef(this.factory_args[3])]});});
hook('alternate_group_factory_b',function(a){this.factory_args=a;return {call:callMeta(this),args:rawArgs(a,4),out_refs:[outRef(a[1]),outRef(a[2]),outRef(a[3])]};},function(r){emit('alternate_group_factory_b.call',{context:this.ctx,ret:r.toString(),out_refs:[outRef(this.factory_args[1]),outRef(this.factory_args[2]),outRef(this.factory_args[3])]});});
hook('entry_clear_target',function(a){return {call:callMeta(this),entry:entry(a[0]),target_arg:hex(a[1])};},function(r){emit('entry_clear_target.leave',{context:this.ctx,ret:r.toString()});});
"""


def _rva_map(profile: dict[str, Any]) -> dict[str, int]:
    """Pass RVAs to Frida; the script relocates them from the live module base."""
    return {name: int(value, 0) for name, value in profile["functions"].items()}


def trace_goal4(profile: dict[str, Any], pid: int | None, duration: float, output: str | None, emit: Callable[[dict], None]):
    events: list[dict] = []

    def receive(event: dict):
        event.setdefault("profile", f"{profile['game']}-{profile['version']}")
        events.append(event)
        emit(event)

    with FridaBridge(pid=pid) as bridge:
        vtable_rvas = {
            name: int(value, 0) if isinstance(value, str) else int(value)
            for name, value in profile["vtables"].items()
            if name in ("pocket_ladders", "siege_vehicle")
        }
        info = bridge.load(
            TRACE_JS_TEMPLATE % (json.dumps(_rva_map(profile)), json.dumps(vtable_rvas)),
            receive,
        )
        receive({"event": "bridge_info", "info": info})
        started = time.monotonic()
        try:
            while duration <= 0 or time.monotonic() - started < duration:
                time.sleep(0.25)
        except KeyboardInterrupt:
            pass
    if output:
        path = Path(output)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    return events
