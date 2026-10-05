from __future__ import annotations
import datetime as dt,hashlib,json,os,pathlib,re,subprocess
from collections import defaultdict,deque

SENSITIVE_PARTS={"private","secret","secrets","credentials",".ssh"}
TEXT_SUFFIXES={".md",".txt",".json",".py",".ts",".tsx",".js",".jsx",".css",".scss",".yml",".yaml",".toml"}
MAX_HASH_BYTES=8*1024*1024
MAX_REFERENCE_BYTES=512*1024

class ProtectedWorkError(ValueError):pass

def _now()->str:return dt.datetime.now(dt.timezone.utc).isoformat()
def _seconds_since(iso:str,now_iso:str)->float:
 try:return max(0.0,(dt.datetime.fromisoformat(now_iso)-dt.datetime.fromisoformat(iso)).total_seconds())
 except Exception:return 0.0
def _run(repo:pathlib.Path,*args:str)->str:
 p=subprocess.run(["git","-C",str(repo),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 if p.returncode:raise ProtectedWorkError("GIT_"+args[0].upper().replace("-","_")+"_FAILED:"+p.stderr[-500:])
 return p.stdout

def _sensitive(rel:str)->bool:
 p=pathlib.PurePosixPath(rel)
 if any(part.casefold() in SENSITIVE_PARTS for part in p.parts):return True
 name=p.name.casefold()
 return name.startswith(".env") or any(x in name for x in ("credential","secret")) or p.suffix.casefold() in {".pem",".key",".p12",".pfx"}

def _fingerprint(path:pathlib.Path,rel:str)->tuple[str|None,str]:
 try:
  st=path.lstat()
 except FileNotFoundError:return None,"MISSING"
 if _sensitive(rel):return None,"SENSITIVE_METADATA_ONLY"
 if path.is_symlink():
  return hashlib.sha256(("symlink:"+os.readlink(path)).encode()).hexdigest(),"SHA256_SYMLINK"
 if not path.is_file():return None,"NON_FILE"
 if st.st_size>MAX_HASH_BYTES:
  raw=f"large:{st.st_size}:{st.st_mtime_ns}".encode()
  return hashlib.sha256(raw).hexdigest(),"METADATA_HASH_LARGE_FILE"
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest(),"SHA256_CONTENT"

def _parse_status(repo:pathlib.Path)->list[tuple[str,str]]:
 raw=subprocess.check_output(["git","-C",str(repo),"status","--porcelain=v1","-z","--untracked-files=all"])
 parts=raw.split(b"\0");rows=[]
 for chunk in parts:
  if not chunk:continue
  text=chunk.decode("utf-8","surrogateescape")
  if len(text)<4:continue
  status=text[:2];path=text[3:]
  # v1 rename/copy emits "old -> new" only in non-z mode; -z puts destination in first record.
  rows.append((status,path))
 return rows

def _resolve_import(src_rel:str,target:str,dirty:set[str])->str|None:
 src=pathlib.PurePosixPath(src_rel)
 candidates=[]
 if target.startswith("@/"):
  base=pathlib.PurePosixPath("src")/target[2:]
 elif target.startswith("./") or target.startswith("../"):
  base=src.parent/target
 else:return None
 b=str(base)
 for c in (b,b+".ts",b+".tsx",b+".js",b+".jsx",b+".css",b+".scss",b+"/index.ts",b+"/index.tsx",b+"/page.tsx"):
  norm=str(pathlib.PurePosixPath(c))
  if norm in dirty:candidates.append(norm)
 return candidates[0] if candidates else None

def _strong_edges(repo:pathlib.Path,paths:list[str])->list[dict]:
 dirty=set(paths);edges=set()
 for rel in paths:
  if _sensitive(rel):continue
  p=repo/rel
  try:
   st=p.stat()
   if not p.is_file() or st.st_size>MAX_REFERENCE_BYTES or p.suffix.casefold() not in TEXT_SUFFIXES:continue
   text=p.read_text(errors="ignore")
  except OSError:continue
  basename_counts={}
  for candidate in paths:
   basename_counts[pathlib.PurePosixPath(candidate).name]=basename_counts.get(pathlib.PurePosixPath(candidate).name,0)+1
  for other in paths:
   if other==rel:continue
   if other in text:
    edges.add(tuple(sorted((rel,other)))+("EXACT_PATH_REFERENCE",))
   else:
    base=pathlib.PurePosixPath(other).name
    if basename_counts.get(base)==1 and base in text:
     edges.add(tuple(sorted((rel,other)))+("BASENAME_REFERENCE",))
  for target in re.findall(r'(?:from\s+|import\s*)["\']([^"\']+)["\']',text):
   resolved=_resolve_import(rel,target,dirty)
   if resolved and resolved!=rel:edges.add(tuple(sorted((rel,resolved)))+("LOCAL_IMPORT",))
  for route in re.findall(r'["\'](/[^"\']+)["\']',text):
   route=route.split("?",1)[0].strip("/")
   if not route:continue
   candidate="src/app/"+route+"/page.tsx"
   if candidate in dirty and candidate!=rel:edges.add(tuple(sorted((rel,candidate)))+("APP_ROUTE_REFERENCE",))
 return [{"a":a,"b":b,"kind":kind,"authority":"STRUCTURAL_REFERENCE_ONLY"} for a,b,kind in sorted(edges)]

def _components(paths:list[str],edges:list[dict])->list[list[str]]:
 graph=defaultdict(set)
 for e in edges:graph[e["a"]].add(e["b"]);graph[e["b"]].add(e["a"])
 seen=set();out=[]
 for p in sorted(paths):
  if p in seen:continue
  q=deque([p]);seen.add(p);comp=[]
  while q:
   x=q.popleft();comp.append(x)
   for y in sorted(graph[x]):
    if y not in seen:seen.add(y);q.append(y)
  out.append(sorted(comp))
 return out

def inspect(repo_path:str|pathlib.Path,previous:dict|None=None,*,quiet_after_seconds:int=900)->dict:
 repo=pathlib.Path(repo_path)
 head=_run(repo,"rev-parse","HEAD").strip();branch=_run(repo,"branch","--show-current").strip() or "DETACHED"
 observed=_now();prev={x["path"]:x for x in (previous or {}).get("paths",[])}
 rows=[];dirty_paths=[]
 for status,rel in _parse_status(repo):
  dirty_paths.append(rel);p=repo/rel
  try:st=p.lstat();size=st.st_size;mtime_ns=st.st_mtime_ns
  except FileNotFoundError:size=None;mtime_ns=None
  fp,method=_fingerprint(p,rel)
  old=prev.get(rel);same=bool(old and old.get("fingerprint")==fp and old.get("status")==status and old.get("size")==size)
  first_seen=old.get("first_seen") if old else observed
  last_changed=old.get("last_changed") if same else observed
  stable_seconds=_seconds_since(last_changed,observed) if same else 0.0
  rows.append({"path":rel,"status":status,"tracked":status!="??","sensitive":_sensitive(rel),"size":size,"mtime_ns":mtime_ns,
               "fingerprint":fp,"fingerprint_method":method,"observation":"STABLE" if same else ("NEW" if not old else "CHANGED"),
               "stable_seconds":round(stable_seconds,3),
               "first_seen":first_seen,"last_changed":last_changed,"authority":"PROTECTED_EXISTING_WORK"})
 disappeared=sorted(set(prev)-set(dirty_paths))
 edges=_strong_edges(repo,dirty_paths)
 packages=[]
 for comp in _components(dirty_paths,edges):
  pid="protected-"+hashlib.sha256("\n".join(comp).encode()).hexdigest()[:12]
  package_rows=[next(x for x in rows if x["path"]==p) for p in comp]
  if any(x["observation"]!="STABLE" for x in package_rows):state="CHANGED"
  elif package_rows and min(x.get("stable_seconds",0.0) for x in package_rows)>=quiet_after_seconds:state="QUIET"
  else:state="STABLE_RECENT"
  packages.append({"id":pid,"paths":comp,"path_count":len(comp),"state":state,"quiet_after_seconds":quiet_after_seconds,"authority":"NON_AUTHORITATIVE_CANDIDATE_GROUP"})
 return {"schema_version":1,"observed_at":observed,"repo":str(repo.resolve()),"head":head,"branch":branch,
         "state":"PROTECTED_EXISTING_WORK" if rows else "CLEAN","dirty_path_count":len(rows),"paths":sorted(rows,key=lambda x:x["path"]),
         "disappeared_paths":disappeared,"structural_edges":edges,"candidate_packages":packages,
         "safety":{"mutation_authorized":False,"auto_commit":False,"auto_delete":False,"candidate_groups_authoritative":False}}
