from __future__ import annotations
import pathlib,subprocess

class DependencyMaterializationError(RuntimeError):pass

def materialize_node_modules(source_repo:pathlib.Path,workspace:pathlib.Path)->dict:
    src=source_repo/"node_modules";dst=workspace/"node_modules"
    if not src.is_dir():return {"state":"ABSENT","method":None}
    if dst.exists() or dst.is_symlink():raise DependencyMaterializationError("NODE_MODULES_DESTINATION_EXISTS")
    proc=subprocess.run(["cp","-a","--reflink=auto",str(src),str(dst)],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if proc.returncode:
        raise DependencyMaterializationError("NODE_MODULES_COPY_FAILED:"+proc.stderr[-800:])
    return {"state":"READY","method":"COPY_REFLINK_AUTO"}
