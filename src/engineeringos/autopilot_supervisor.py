from __future__ import annotations
import pathlib,subprocess
from coding_agent_provider import TaskEnvelope,CodingAgentError,to_mutation_proposal
from coding_agent_router import ProviderPool,classify_provider_failure
from mutation_proposal import execute_proposal
from convergence_gate import converge
from commit_receipt import commit_converged,CommitReceiptError

def _head(repo): return subprocess.check_output(["git","-C",repo,"rev-parse","HEAD"],text=True).strip()

def mutation_contract(item:dict)->dict|None:
 paths=item.get("allowed_paths"); argv=item.get("verification_argv")
 if not paths or not argv: return None
 if not isinstance(paths,list) or not all(isinstance(x,str) and x for x in paths): return None
 if not isinstance(argv,list) or not all(isinstance(x,str) and x for x in argv): return None
 return {"allowed_paths":paths,"verification_argv":argv}

def execute_work_item(repo:str,item:dict,providers,*,workspace_root:str,verification_timeout:int=120)->dict:
 contract=mutation_contract(item)
 if not contract:
  return {"item_id":item["id"],"state":"WAITING_CONTRACT","needs_intent":False,"user_interruption":False}
 source_sha=item.get("source_sha") or _head(repo)
 if source_sha!=_head(repo):
  return {"item_id":item["id"],"state":"REOPENED","reason":"SOURCE_SHA_DRIFT","needs_intent":False,"user_interruption":False}
 task=TaskEnvelope(item["project"],item["id"],source_sha,item.get("expected_outcome") or item.get("goal") or item["id"],tuple(contract["allowed_paths"]),tuple(contract["verification_argv"]),item.get("agent_context",{}))
 files={p:(pathlib.Path(repo)/p).read_text() for p in task.allowed_paths}
 try:
  candidate,routing=ProviderPool(providers).propose(task=task,files=files)
 except CodingAgentError as exc:
  return {"item_id":item["id"],"state":"REOPENED",**classify_provider_failure(exc),"routing":{"state":"FAILED"}}
 proposal=to_mutation_proposal(task,candidate)
 verified=execute_proposal(repo,proposal,workspace_root=workspace_root,timeout=verification_timeout,keep_workspace=True)
 if verified["state"]!="READY_FOR_CONVERGENCE":
  return {"item_id":item["id"],"state":"REOPENED","reason":"VERIFICATION_FAILED","needs_intent":False,"user_interruption":False,"routing":routing,"proposal":proposal,"verification_result":verified}
 conv=converge(repo,proposal,verified)
 if not conv.get("applied"):
  return {"item_id":item["id"],"state":"REOPENED","reason":conv.get("reason") or conv.get("gate",{}).get("reason","CONVERGENCE_DENIED"),"needs_intent":False,"user_interruption":False,"routing":routing,"proposal":proposal,"verification_result":verified,"convergence":conv}
 try:
  receipt=commit_converged(repo,item_id=item["id"],source_sha=source_sha,changed_paths=verified["changed_paths"],message=item.get("commit_message") or ("autopilot: "+item["id"]))
 except CommitReceiptError as exc:
  return {"item_id":item["id"],"state":"REOPENED","reason":str(exc),"needs_intent":False,"user_interruption":False,"routing":routing,"proposal":proposal,"verification_result":verified,"convergence":conv}
 return {"item_id":item["id"],"state":"COMMITTED","needs_intent":False,"user_interruption":False,"routing":routing,"proposal":proposal,"verification_result":verified,"convergence":conv,"commit_receipt":receipt,"capability_evidence":receipt["evidence_refs"]}

def supervisor_tick(repo:str,items:list[dict],dispatch:list[dict],providers,*,workspace_root:str,verification_timeout:int=120)->dict:
 by={x["id"]:x for x in items}; results=[]
 for row in dispatch:
  if row.get("schedule_state")!="DISPATCHABLE": continue
  item=by.get(row["id"])
  if not item: continue
  results.append(execute_work_item(repo,item,providers,workspace_root=workspace_root,verification_timeout=verification_timeout))
  if results[-1]["state"]=="COMMITTED": break
 return {"schema_version":1,"results":results,"needs_intent":any(x.get("needs_intent") for x in results),"user_interruptions":[x for x in results if x.get("user_interruption")]}
