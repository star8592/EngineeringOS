#!/usr/bin/env python3
from __future__ import annotations
import json,pathlib,tempfile,os


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


def project():
    snap=atomic_copy_json('.engineeringos/shadow/latest.json','dashboard/runtime/snapshot.json')
    queue=atomic_copy_json('.engineeringos/work-queue.json','dashboard/runtime/queue.json')
    loop=atomic_copy_json('.engineeringos/control-loop/projection.json','dashboard/runtime/control-loop.json')
    return {'snapshot':snap['content_sha256'],'queue_items':len(queue['items']),'loop_items':len(loop['items'])}

if __name__=='__main__': print(json.dumps(project(),indent=2))
