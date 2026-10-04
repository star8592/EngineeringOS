from __future__ import annotations
import subprocess,os
from autopilot_admission import admit,make_command
from self_hosting_execution import execute_verified_check

def run_verification(item:dict,dispatch:dict,*,argv:list[str],cwd:str,owner:str="engineeringos-autopilot",verifier:str="deterministic-runner",subject_sha:str|None=None,timeout:int=120)->dict:
 gate=admit(item,dispatch,action_kind="RUN_VERIFICATION")
 if gate["decision"]!="ALLOW": return {"gate":gate,"executed":False}
 cmd=make_command(item,action_kind="RUN_VERIFICATION",subject_sha=subject_sha)
 try:
  p=subprocess.run(argv,cwd=cwd,text=True,capture_output=True,timeout=timeout,env={**os.environ,"CI":"1"})
  passed=p.returncode==0;evidence=f'command:{cmd.command_id}:exit-{p.returncode}:sha-{subject_sha or "unknown"}'
  closed=execute_verified_check(item,owner=owner,verifier=verifier,check_name=" ".join(argv),check_passed=passed,evidence_ref=evidence)
  return {"gate":gate,"executed":True,"command_id":cmd.command_id,"idempotency_key":cmd.idempotency_key,
          "exit_code":p.returncode,"stdout_tail":p.stdout[-4000:],"stderr_tail":p.stderr[-4000:],
          "evidence_ref":evidence,"closure":closed}
 except subprocess.TimeoutExpired as exc:
  return {"gate":gate,"executed":True,"command_id":cmd.command_id,"timed_out":True,"closure":None,
          "stdout_tail":(exc.stdout or "")[-4000:] if isinstance(exc.stdout,str) else "",
          "stderr_tail":(exc.stderr or "")[-4000:] if isinstance(exc.stderr,str) else ""}
