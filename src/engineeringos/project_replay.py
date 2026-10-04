from __future__ import annotations
class ProjectReplayError(ValueError): pass
def replay_project(events):
 state={"schema_version":1,"project":None,"intents":{},"work_items":{},"last_seq":0}
 for e in events:
  if state["project"] is None: state["project"]=e["project"]
  if e["project"]!=state["project"]: raise ProjectReplayError("MIXED_PROJECT_STREAM")
  if e["seq"]!=state["last_seq"]+1: raise ProjectReplayError("SEQUENCE_GAP_OR_REORDER")
  state["last_seq"]=e["seq"]; typ=e["type"]; p=e.get("payload") or {}; key=e["key"]
  if typ in ("INTENT_RECORDED","INTENT_REVISED"):
   cur=dict(state["intents"].get(key,{}));cur.update(p);cur.update({"id":key,"generation":e.get("generation",0),"active":True});state["intents"][key]=cur
  elif typ=="INTENT_REVERSED":
   cur=dict(state["intents"].get(key,{}));cur.update(p);cur.update({"id":key,"generation":e.get("generation",0),"active":False});state["intents"][key]=cur
  elif typ=="WORK_DISCOVERED":
   if key in state["work_items"]: raise ProjectReplayError("WORK_ALREADY_EXISTS")
   state["work_items"][key]={**p,"id":key,"state":"DISCOVERED"}
  elif typ in ("WORK_REOPENED","WORK_WAITING_PROVIDER","WORK_WAITING_CONTRACT","WORK_PROTECTED","WORK_SUPERSEDED","WORK_COMMITTED","WORK_RESOLVED"):
   if key not in state["work_items"]: raise ProjectReplayError("WORK_NOT_CREATED")
   cur=dict(state["work_items"][key]);cur.update(p)
   cur["state"]={"WORK_REOPENED":"REOPENED","WORK_WAITING_PROVIDER":"REOPENED","WORK_WAITING_CONTRACT":"WAITING_CONTRACT","WORK_PROTECTED":"PROTECT","WORK_SUPERSEDED":"SUPERSEDED","WORK_COMMITTED":"COMMITTED","WORK_RESOLVED":"RESOLVED"}[typ]
   state["work_items"][key]=cur
  else: raise ProjectReplayError("UNKNOWN_EVENT_TYPE:"+typ)
 return state
