from __future__ import annotations
import os,pathlib

def _ancestors(pid:int,proc_root:pathlib.Path)->set[int]:
 out=set()
 while pid>1 and pid not in out:
  out.add(pid)
  try:
   fields=(proc_root/str(pid)/"stat").read_text().split()
   pid=int(fields[3])
  except Exception:break
 return out

def _inside(path:str,root:pathlib.Path)->bool:
 try:
  p=pathlib.Path(path).resolve()
  return p==root or root in p.parents
 except Exception:return False

def probe(repo_path:str|pathlib.Path,*,proc_root:str|pathlib.Path="/proc",self_pid:int|None=None)->dict:
 repo=pathlib.Path(repo_path).resolve();pr=pathlib.Path(proc_root);me=os.getpid() if self_pid is None else int(self_pid);skip=_ancestors(me,pr)
 refs=[]
 for entry in pr.iterdir():
  if not entry.name.isdigit():continue
  pid=int(entry.name)
  if pid in skip:continue
  reasons=[]
  try:
   cwd=os.readlink(entry/"cwd")
   if _inside(cwd,repo):reasons.append("CWD_INSIDE_REPO")
  except Exception:pass
  try:
   raw=(entry/"cmdline").read_bytes().replace(b"\0",b" ").decode(errors="ignore")
   if str(repo) in raw:reasons.append("CMDLINE_REFERENCES_REPO")
  except Exception:pass
  try:
   fd_dir=entry/"fd"
   for fd in fd_dir.iterdir():
    try:
     target=os.readlink(fd)
     if not _inside(target,repo):continue
     info=(entry/"fdinfo"/fd.name).read_text()
     flag_line=next((x for x in info.splitlines() if x.startswith("flags:")),None)
     if not flag_line:continue
     flags=int(flag_line.split()[1],8)
     if flags & 3 in (1,2):
      reasons.append("OPEN_WRITABLE_FD_INSIDE_REPO");break
    except Exception:continue
  except Exception:pass
  if reasons:refs.append({"pid":pid,"reasons":sorted(set(reasons))})
 return {"schema_version":1,"repo":str(repo),"state":"ACTIVE_REFERENCES" if refs else "QUIET","active_reference_count":len(refs),"references":refs}
