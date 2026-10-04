from __future__ import annotations
import json,os,tempfile,pathlib
from dataclasses import asdict
from conversation_intent import IntentTurn
from autopilot_control_loop import tick
from state_paths import runtime

def _atomic(path:pathlib.Path,obj:dict):
 path.parent.mkdir(parents=True,exist_ok=True)
 fd,tmp=tempfile.mkstemp(prefix=path.name+".",suffix=".tmp",dir=path.parent)
 try:
  with os.fdopen(fd,"w") as f:
   json.dump(obj,f,ensure_ascii=False,indent=2);f.write("\n");f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)

def run_durable_tick(*,project:str,turns:list[IntentTurn],intent_id:str,required_capabilities:list[str],capabilities:list,work_items:list[dict],state_path=None)->dict:
 out=tick(project=project,turns=turns,intent_id=intent_id,required_capabilities=required_capabilities,capabilities=capabilities,work_items=work_items)
 path=pathlib.Path(state_path) if state_path else runtime("autopilot",project,intent_id+".json")
 projection={"schema_version":1,"project":project,"intent_id":intent_id,"turn_ids":[t.id for t in turns],
             "intent_state":out["intent_state"],"status":out["status"],"work_items":out["plan"].get("work_items",[]),
             "dispatch":out["plan"].get("dispatch",[]),"human_interruptions":out["plan"].get("human_interruptions",[])}
 _atomic(path,projection)
 return {"projection_path":str(path),"projection":projection,"tick":out}

def load_projection(path)->dict:
 return json.loads(pathlib.Path(path).read_text())
