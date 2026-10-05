from __future__ import annotations
import pathlib,subprocess
from contract_planner import PlanningPool,PlanningProviderError
from durable_supervisor_runtime import recover,admit_work_contract

def project_context(repo:str)->dict:
 root=pathlib.Path(repo)
 files=[]
 for p in root.rglob("*"):
  if len(files)>=500:break
  if p.is_file() and ".git" not in p.parts:
   try:files.append(str(p.relative_to(root)))
   except ValueError:pass
 hints={}
 for rel in sorted(x for x in files if x.startswith("tests/") and x.endswith(".py"))[:40]:
  try:
   text=(root/rel).read_text()
   hints[rel]="unittest" if ("unittest.TestCase" in text or "TestCase)" in text) else ("direct-python-invariant-script" if ("assert " in text or "raise AssertionError" in text) else "unknown-python-test-style")
  except (OSError,UnicodeDecodeError):pass
 return {"files":sorted(files),"file_count_capped":len(files),"verification_hints":hints}
def plan_one(repo,runtime_root,project,providers)->dict:
 state=recover(runtime_root,project)
 candidates=[x for x in state["work_items"].values() if x.get("kind")=="CAPABILITY_PLANNING" and x.get("state") in ("DISCOVERED","REOPENED","WAITING_CONTRACT") and not x.get("allowed_paths")]
 if not candidates:return {"state":"NO_PLANNING_WORK"}
 item=sorted(candidates,key=lambda x:x["id"])[0]
 try:contract,routing=PlanningPool(providers).plan(repo=repo,work=item,project_context=project_context(repo))
 except PlanningProviderError as exc:return {"state":"PLANNER_FAILED","item_id":item["id"],"reason":str(exc)}
 evidence="planner:"+routing["attempts"][-1]["provider"]+":admitted"
 source_sha=subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()
 admit_work_contract(runtime_root,project,item["id"],contract,planner_evidence=evidence,source_sha=source_sha)
 return {"state":"CONTRACT_ADMITTED","item_id":item["id"],"contract":contract,"routing":routing}
