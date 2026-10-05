from __future__ import annotations
import pathlib,re
from project_registry import load
from project_journal import events

class ProjectRoutingError(ValueError):
    pass

def _norm(text:str)->str:
    return re.sub(r"\s+","",text or "").casefold()

def _terms(cfg:dict)->list[str]:
    vals=[cfg.get("name"),cfg.get("display_name"),*(cfg.get("aliases") or [])]
    return sorted({x.strip() for x in vals if isinstance(x,str) and x.strip()},key=len,reverse=True)

def _conversation_projects(registry:dict,runtime_root,conversation_id:str)->list[str]:
    if not conversation_id:return []
    hits=[]
    for cfg in registry.get("projects",[]):
        jp=pathlib.Path(runtime_root)/"projects"/cfg["name"]/"journal.jsonl"
        if not jp.exists():continue
        for e in reversed(events(jp)):
            if e.get("type")=="CONVERSATION_TURN" and e.get("payload",{}).get("conversation_id")==conversation_id:
                hits.append(cfg["name"]);break
    return hits

def route(registry_path,runtime_root,*,text:str,conversation_id:str,current_project:str|None=None)->dict:
    registry=load(registry_path);projects=registry.get("projects",[])
    if not projects:return {"state":"NO_PROJECTS","needs_intent":False}
    hay=_norm(text)
    matches=[]
    for cfg in projects:
        matched=[t for t in _terms(cfg) if _norm(t) and _norm(t) in hay]
        if matched:matches.append((cfg,max(matched,key=len)))
    if len(matches)==1:
        cfg,term=matches[0]
        return {"state":"ROUTED","project":cfg["name"],"display_name":cfg.get("display_name") or cfg["name"],"evidence":"EXPLICIT_PROJECT_MENTION","matched_term":term,"needs_intent":False}
    if len(matches)>1:
        return {"state":"NEEDS_PROJECT_SELECTION","candidates":[{"project":c["name"],"display_name":c.get("display_name") or c["name"]} for c,_ in matches],"reason":"MULTIPLE_PROJECT_MENTIONS","needs_intent":True}
    if current_project:
        candidates=[x for x in projects if x["name"]==current_project]
        if len(candidates)==1:
            cfg=candidates[0]
            return {"state":"ROUTED","project":cfg["name"],"display_name":cfg.get("display_name") or cfg["name"],"evidence":"EXPLICIT_CURRENT_PROJECT","needs_intent":False}
        raise ProjectRoutingError("UNKNOWN_CURRENT_PROJECT")
    bound=_conversation_projects(registry,runtime_root,conversation_id)
    if len(bound)==1:
        cfg=next(x for x in projects if x["name"]==bound[0])
        return {"state":"ROUTED","project":cfg["name"],"display_name":cfg.get("display_name") or cfg["name"],"evidence":"DURABLE_CONVERSATION_BINDING","needs_intent":False}
    if len(bound)>1:
        return {"state":"NEEDS_PROJECT_SELECTION","candidates":[{"project":x["name"],"display_name":x.get("display_name") or x["name"]} for x in projects if x["name"] in bound],"reason":"MULTIPLE_CONVERSATION_PROJECTS","needs_intent":True}
    if len(projects)==1:
        cfg=projects[0]
        return {"state":"ROUTED","project":cfg["name"],"display_name":cfg.get("display_name") or cfg["name"],"evidence":"SINGLE_REGISTERED_PROJECT","needs_intent":False}
    return {"state":"NEEDS_PROJECT_SELECTION","candidates":[{"project":x["name"],"display_name":x.get("display_name") or x["name"]} for x in projects],"reason":"NO_PROJECT_CONTEXT","needs_intent":True}
