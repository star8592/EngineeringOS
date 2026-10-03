#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib,tempfile,os
from state_paths import runtime

def atomic_copy_json(src,dst):
    obj=json.load(open(src));p=pathlib.Path(dst);p.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode()
    fd,tmp=tempfile.mkstemp(prefix=p.name+'.',suffix='.tmp',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.replace(tmp,p)
        dfd=os.open(p.parent,os.O_DIRECTORY)
        try:os.fsync(dfd)
        finally:os.close(dfd)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return obj

def optional_copy_json(src,dst):
    if not pathlib.Path(src).exists(): return None
    return atomic_copy_json(src,dst)

def project():
    snap=atomic_copy_json(runtime('shadow/latest.json'),'dashboard/runtime/snapshot.json')
    queue=atomic_copy_json(runtime('work-queue.json'),'dashboard/runtime/queue.json')
    loop=atomic_copy_json(runtime('control-loop/projection.json'),'dashboard/runtime/control-loop.json')
    status=optional_copy_json(runtime('supervisor/status.json'),'dashboard/runtime/supervisor.json')
    brief=optional_copy_json(runtime('action-brief.json'),'dashboard/runtime/action-brief.json')
    details=optional_copy_json(runtime('action-details.json'),'dashboard/runtime/action-details.json')
    history=optional_copy_json(runtime('time-series-summary.json'),'dashboard/runtime/time-series.json')
    g3=optional_copy_json(runtime('g3/controller.json'),'dashboard/runtime/g3-controller.json')
    g3exec=optional_copy_json(runtime('g3/projection.json'),'dashboard/runtime/g3-execution.json')
    system_one=optional_copy_json(runtime('system-one/projection.json'),'dashboard/runtime/system-one.json')
    system_one_admission=optional_copy_json(runtime('system-one/admission.json'),'dashboard/runtime/system-one-admission.json')
    system_one_observations=optional_copy_json(runtime('system-one/observation-summary.json'),'dashboard/runtime/system-one-observations.json')
    return {'snapshot':snap['content_sha256'],'queue_items':len(queue['items']),'loop_items':len(loop['items']),'supervisor_health':status['health'] if status else 'STARTING','action_count':len(brief['actions']) if brief else 0,'detail_count':len(details['items']) if details else 0,'observations':history['observations'] if history else 0,'g3_decisions':len(g3['decisions']) if g3 else 0,'g3_check_result':g3exec.get('check_result') if g3exec else None,'system_one_status':system_one.get('status') if system_one else None,'system_one_items':len(system_one.get('items',[])) if system_one else 0,'system_one_admission':system_one_admission.get('state') if system_one_admission else None,'system_one_observations':system_one_observations.get('observations') if system_one_observations else 0}

if __name__=='__main__': print(json.dumps(project(),indent=2))
