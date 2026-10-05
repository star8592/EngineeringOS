from __future__ import annotations
import hashlib,json
from conversation_ingest import ingest,_state,ConversationCommandError
from project_router import route
from durable_run import arm_run,read_run

PROCESS_CONTROL={"继续","继续推进","接着做","接着","往下做","继续往前推进","继续开发"}

def _normalized(text:str)->str:
    return "".join((text or "").split()).casefold()

def _recent_intent_for_conversation(state:dict,conversation_id:str)->str|None:
    for turn in reversed(state.get("conversation_turns",[])):
        if turn.get("conversation_id")==conversation_id and turn.get("intent_id"):
            return turn["intent_id"]
    return None

def submit(registry_path,runtime_root,*,command_id:str,conversation_id:str,text:str,kind:str|None=None,intent_id:str|None=None,current_project:str|None=None,artifact_ref:str|None=None,affects_task:bool=True,required_capabilities:list[str]|None=None)->dict:
    routed=route(registry_path,runtime_root,text=text,conversation_id=conversation_id,current_project=current_project)
    if routed.get("state")!="ROUTED":
        return {"state":routed.get("state"),"routing":routed,"durable_write":False}
    project=routed["project"]
    if _normalized(text) in {_normalized(x) for x in PROCESS_CONTROL}:
        return {"state":"CONTINUE_EXISTING_WORK","project":project,"routing":routed,"durable_write":False,"intent_changed":False,"run":read_run(runtime_root,project)}
    if not kind:
        raise ConversationCommandError("TURN_KIND_REQUIRED")
    state=_state(runtime_root,project)
    if not intent_id and kind in {"CORRECTION","REVERSAL","FEEDBACK","APPROVAL"}:
        intent_id=_recent_intent_for_conversation(state,conversation_id)
        if not intent_id:
            return {"state":"NEEDS_INTENT_SELECTION","project":project,"routing":routed,"durable_write":False}
    if not intent_id and kind=="DESIRE":
        raw=f"{project}|{conversation_id}|{command_id}"
        intent_id="intent-"+hashlib.sha256(raw.encode()).hexdigest()[:12]
    caps=required_capabilities
    if kind=="DESIRE" and caps is None:
        caps=[text.strip()]
    new_state=ingest(runtime_root,project=project,command_id=command_id,conversation_id=conversation_id,kind=kind,text=text,intent_id=intent_id,artifact_ref=artifact_ref,affects_task=affects_task,required_capabilities=caps)
    run=arm_run(runtime_root,project,intent_id=intent_id,conversation_id=conversation_id,command_id=command_id) if kind in {"DESIRE","CORRECTION","REVERSAL"} else read_run(runtime_root,project)
    return {"state":"ACCEPTED","project":project,"display_name":routed.get("display_name"),"routing":routed,"intent_id":intent_id,"durable_write":True,"project_state":new_state,"run":run}
