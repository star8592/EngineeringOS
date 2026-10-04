from __future__ import annotations
import hashlib
from execution_receipt import ExecutionReceipt,transition
from queue_model import claim,request_resolution,resolve

def execution_id(item:dict)->str:
 return "self-"+hashlib.sha256((item["project"]+"|"+item["id"]).encode()).hexdigest()[:16]

def execute_verified_check(item:dict, *, owner:str, verifier:str, check_name:str, check_passed:bool, evidence_ref:str|None)->dict:
 """Close one bounded self-hosting work item only from explicit verification evidence."""
 claim(item,owner)
 receipt=ExecutionReceipt(execution_id(item),f'self:{item["id"]}',"SELF_HOSTING_VERIFICATION",side_effecting=False)
 transition(receipt,"DISPATCHED"); transition(receipt,"ACCEPTED"); transition(receipt,"RUNNING")
 if not check_passed:
  transition(receipt,"FAILED")
  item["state"]="REOPENED"; item.pop("lease",None)
  return {"item":item,"receipt":receipt,"capability_state":"UNKNOWN"}
 if not evidence_ref:
  # No evidence means no success claim and no queue closure.
  item["state"]="REOPENED"; item.pop("lease",None)
  return {"item":item,"receipt":receipt,"capability_state":"UNKNOWN"}
 transition(receipt,"SUCCEEDED",[evidence_ref])
 pred=item.get("completion_predicate",{})
 if pred.get("type")!="CAPABILITY_EVIDENCE" or "VERIFIED" not in pred.get("accepted_states",[]):
  item["state"]="REOPENED"; item.pop("lease",None)
  return {"item":item,"receipt":receipt,"capability_state":"DISCOVERED"}
 request_resolution(item,owner,[evidence_ref])
 resolve(item,verifier,[f'verifier:{verifier}:{check_name}'])
 return {"item":item,"receipt":receipt,"capability_state":"VERIFIED"}
