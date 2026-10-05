from __future__ import annotations
import hashlib,io,json,os,pathlib,re,shutil,subprocess,tarfile,tempfile,time

class ProtectedVerificationError(RuntimeError):pass

def _git(repo:pathlib.Path,*args:str,check=True)->str:
 p=subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if check and p.returncode:raise ProtectedVerificationError("GIT_"+args[0].upper().replace("-","_")+"_FAILED:"+p.stderr[-500:])
 return p.stdout.strip()

def _status_fingerprint(repo:pathlib.Path)->str:
 raw=subprocess.check_output(["git","-C",str(repo),"status","--porcelain=v1","-z","--branch"])
 return hashlib.sha256(raw).hexdigest()

def _inventory_fingerprint(inv:dict)->str:
 rows=[{"path":x.get("path"),"status":x.get("status"),"fingerprint":x.get("fingerprint"),"size":x.get("size")} for x in inv.get("paths",[])]
 raw=json.dumps({"head":inv.get("head"),"paths":rows},sort_keys=True,separators=(",",":")).encode()
 return hashlib.sha256(raw).hexdigest()

def _safe_extract_tar(data:bytes,dst:pathlib.Path)->None:
 with tarfile.open(fileobj=io.BytesIO(data),mode="r:") as tf:
  members=tf.getmembers()
  for m in members:
   p=pathlib.PurePosixPath(m.name)
   if p.is_absolute() or ".." in p.parts:raise ProtectedVerificationError("ARCHIVE_PATH_ESCAPE")
  tf.extractall(dst,members=members)

def _overlay(repo:pathlib.Path,workspace:pathlib.Path,inv:dict)->None:
 for row in inv.get("paths",[]):
  rel=row["path"]
  if row.get("sensitive"):raise ProtectedVerificationError("SENSITIVE_DIRTY_PATH_BLOCKED")
  src=repo/rel;dst=workspace/rel
  if not src.exists() and not src.is_symlink():
   if dst.is_dir():shutil.rmtree(dst)
   elif dst.exists() or dst.is_symlink():dst.unlink()
   continue
  dst.parent.mkdir(parents=True,exist_ok=True)
  if src.is_symlink():
   if dst.exists() or dst.is_symlink():dst.unlink()
   os.symlink(os.readlink(src),dst)
  elif src.is_file():
   shutil.copy2(src,dst)
  else:
   raise ProtectedVerificationError("UNSUPPORTED_DIRTY_PATH_TYPE:"+rel)

def _diagnostic_signature(stdout:str,stderr:str,workspace:pathlib.Path,exit_code:int)->dict|None:
 if exit_code==0:return None
 text=(stdout+"\n"+stderr).replace(str(workspace),"<workspace>")
 text=re.sub(r"/tmp/(?:tmp|engineeringos-protected-verify-)[^/\s]+","/tmp/<temp>",text)
 steps=re.findall(r"^==>\s+(.+)$",text,re.M)
 interesting=[]
 pattern=re.compile(r"(error|fail|✖|traceback|assertionerror|typeerror|syntaxerror)",re.I)
 for line in text.splitlines():
  line=" ".join(line.strip().split())
  if not line:continue
  if "<workspace>/" in line or pattern.search(line):
   interesting.append(line)
  if len(interesting)>=80:break
 payload={"failure_stage":steps[-1] if steps else None,"diagnostics":interesting}
 payload["sha256"]=hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":")).encode()).hexdigest()
 return payload

def verify(repo_path:str|pathlib.Path,inventory:dict,command:list[str],*,timeout_seconds:int=900,workspace_parent:str|pathlib.Path|None=None)->dict:
 repo=pathlib.Path(repo_path).resolve()
 if not command or any(not isinstance(x,str) or not x for x in command):raise ProtectedVerificationError("VERIFICATION_ARGV_REQUIRED")
 source_head_before=_git(repo,"rev-parse","HEAD");source_status_before=_status_fingerprint(repo)
 if inventory.get("head")!=source_head_before:raise ProtectedVerificationError("INVENTORY_SOURCE_SHA_DRIFT")
 if inventory.get("state")!="PROTECTED_EXISTING_WORK":raise ProtectedVerificationError("PROTECTED_INVENTORY_REQUIRED")
 inv_fp=_inventory_fingerprint(inventory)
 parent=pathlib.Path(workspace_parent) if workspace_parent else None
 started=time.monotonic()
 with tempfile.TemporaryDirectory(prefix="engineeringos-protected-verify-",dir=str(parent) if parent else None) as td:
  ws=pathlib.Path(td)
  archive=subprocess.check_output(["git","-C",str(repo),"archive","--format=tar",source_head_before])
  _safe_extract_tar(archive,ws)
  subprocess.run(["git","init","-q"],cwd=ws,check=True)
  subprocess.run(["git","config","user.email","engineeringos@local"],cwd=ws,check=True)
  subprocess.run(["git","config","user.name","EngineeringOS"],cwd=ws,check=True)
  subprocess.run(["git","add","-A"],cwd=ws,check=True)
  subprocess.run(["git","commit","-qm","protected verification base"],cwd=ws,check=True)
  _overlay(repo,ws,inventory)
  source_node_modules=repo/"node_modules"
  if source_node_modules.is_dir() and not (ws/"node_modules").exists():
   os.symlink(source_node_modules,ws/"node_modules",target_is_directory=True)
  proc=subprocess.run(command,cwd=ws,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout_seconds)
  diagnostic=_diagnostic_signature(proc.stdout,proc.stderr,ws,proc.returncode)
  changed=subprocess.check_output(["git","status","--porcelain=v1","-z","--untracked-files=all"],cwd=ws)
  changed_sha=hashlib.sha256(changed).hexdigest()
 elapsed_ms=round((time.monotonic()-started)*1000)
 source_head_after=_git(repo,"rev-parse","HEAD");source_status_after=_status_fingerprint(repo)
 source_unchanged=source_head_before==source_head_after and source_status_before==source_status_after
 state="PASS" if proc.returncode==0 and source_unchanged else ("SOURCE_CHANGED_DURING_VERIFY" if not source_unchanged else "FAIL")
 return {
  "schema_version":1,"state":state,"source_head":source_head_before,"source_unchanged":source_unchanged,
  "inventory_fingerprint":inv_fp,"command":command,"exit_code":proc.returncode,"elapsed_ms":elapsed_ms,
  "workspace_status_sha256":changed_sha,"diagnostic_signature":diagnostic,
  "stdout_tail":proc.stdout[-6000:],"stderr_tail":proc.stderr[-6000:],
  "authority":"ISOLATED_PROTECTED_WORK_VERIFICATION_ONLY","mutation_authorized":False,
 }
