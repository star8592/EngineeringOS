#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/"src"/"engineeringos"))
from conversation_gateway import submit
from state_paths import RUNTIME_ROOT

def main()->int:
 p=argparse.ArgumentParser(description="Submit one frontend-neutral conversation command to EngineeringOS.")
 p.add_argument("--registry",default=str(RUNTIME_ROOT/"projects"/"registry.json"))
 p.add_argument("--runtime-root",default=str(RUNTIME_ROOT))
 p.add_argument("--command-id",required=True)
 p.add_argument("--conversation-id",required=True)
 p.add_argument("--text",required=True)
 p.add_argument("--kind")
 p.add_argument("--intent-id")
 p.add_argument("--current-project")
 p.add_argument("--artifact-ref")
 args=p.parse_args()
 result=submit(args.registry,args.runtime_root,command_id=args.command_id,conversation_id=args.conversation_id,text=args.text,kind=args.kind,intent_id=args.intent_id,current_project=args.current_project,artifact_ref=args.artifact_ref)
 public={k:v for k,v in result.items() if k!="project_state"}
 if "project_state" in result:
  st=result["project_state"]
  public["generation"]=st.get("intents",{}).get(result.get("intent_id"),{}).get("generation")
  public["active_work_items"]=sum(1 for x in st.get("work_items",{}).values() if x.get("state") not in {"RESOLVED","SUPERSEDED"})
 print(json.dumps(public,ensure_ascii=False,indent=2))
 return 0

if __name__=="__main__":
 raise SystemExit(main())
