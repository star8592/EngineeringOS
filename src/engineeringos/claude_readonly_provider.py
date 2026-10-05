from __future__ import annotations
import json,subprocess,os,signal
from coding_agent_provider import AgentCandidate,CodingAgentError
class ClaudeReadonlyProvider:
 name="claude-cli-readonly"
 def __init__(self,*,binary="claude",model=None,timeout=60):self.binary=binary;self.model=model;self.timeout=timeout
 def propose(self,task,files):
  props={p:{"type":"string"} for p in task.allowed_paths}
  schema={"type":"object","properties":{"changes":{"type":"object","properties":props,"required":list(task.allowed_paths),"additionalProperties":False},"rationale":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1}},"required":["changes","rationale","confidence"],"additionalProperties":False}
  prompt=("You are an implementation worker, not an authority. Return a candidate only. Do not run commands, use tools, broaden scope, or modify files. Return full replacement text for every allowed path and no others.\nTask:\n"+json.dumps({"goal":task.goal,"allowed_paths":task.allowed_paths,"verification_argv":task.verification_argv,"context":task.context},ensure_ascii=False)+"\nCurrent files:\n"+json.dumps(files,ensure_ascii=False))
  argv=[self.binary,"-p","--no-session-persistence","--tools","","--output-format","json","--json-schema",json.dumps(schema)]
  if self.model:argv+=["--model",self.model]
  proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  try:stdout,stderr=proc.communicate(prompt,timeout=self.timeout)
  except subprocess.TimeoutExpired as exc:
   try:os.killpg(proc.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   try:proc.wait(timeout=5)
   except subprocess.TimeoutExpired:proc.kill()
   raise CodingAgentError("CLAUDE_TIMEOUT") from exc
  try: outer=json.loads(stdout)
  except Exception: outer=None
  if isinstance(outer,dict) and outer.get("is_error"):
   msg=str(outer.get("result",""))
   if "Not logged in" in msg: raise CodingAgentError("CLAUDE_NOT_AUTHENTICATED")
   raise CodingAgentError("CLAUDE_REMOTE_ERROR:"+msg[:500])
  if proc.returncode:raise CodingAgentError("CLAUDE_FAILED:"+stderr[-1000:])
  try:
   if outer is None: outer=json.loads(stdout)
   body=outer.get("structured_output")
   if body is None:
    raw=outer.get("result",stdout);body=json.loads(raw) if isinstance(raw,str) else raw
   return AgentCandidate(self.name,self.model or "configured-default",body["changes"],body["rationale"],float(body["confidence"]))
  except Exception as exc:raise CodingAgentError("CLAUDE_OUTPUT_INVALID") from exc
