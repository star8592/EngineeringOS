from __future__ import annotations
import json,pathlib,subprocess,tempfile
from coding_agent_provider import AgentCandidate,CodingAgentError,TaskEnvelope

class CodexReadOnlyProvider:
 name="codex-cli-readonly"
 def __init__(self, *, binary:str="codex", model:str|None=None, timeout:int=180):
  self.binary=binary;self.model=model;self.timeout=timeout
 def propose(self, *, task:TaskEnvelope, files:dict[str,str])->AgentCandidate:
  schema={"type":"object","properties":{"changes":{"type":"object","properties":{path:{"type":"string"} for path in task.allowed_paths},"required":list(task.allowed_paths),"additionalProperties":False},"rationale":{"type":"string"},"confidence":{"type":"number","minimum":0,"maximum":1}},"required":["changes","rationale","confidence"],"additionalProperties":False}
  prompt=("You are a coding implementation worker, not an authority. Return a candidate implementation only. "
          "Do not request permissions, do not modify files, do not run commands, and do not broaden scope. "
          f"Goal: {task.goal}\nExact allowed paths: {list(task.allowed_paths)}\n"
          "Return full replacement text for every allowed path in changes, and no other paths.\n"
          "Current file contents:\n"+json.dumps(files,ensure_ascii=False))
  with tempfile.TemporaryDirectory(prefix="engineeringos-codex-provider-") as td:
   sp=pathlib.Path(td)/"schema.json";op=pathlib.Path(td)/"out.json";sp.write_text(json.dumps(schema))
   argv=[self.binary,"exec","--ephemeral","--sandbox","read-only","--output-schema",str(sp),"-o",str(op)]
   if self.model: argv+=["--model",self.model]
   argv+=["-"]
   try: proc=subprocess.run(argv,input=prompt,text=True,capture_output=True,timeout=self.timeout)
   except subprocess.TimeoutExpired as exc: raise CodingAgentError("CODEX_TIMEOUT") from exc
   if proc.returncode!=0: raise CodingAgentError("CODEX_FAILED:"+proc.stderr[-1000:])
   try: body=json.loads(op.read_text())
   except Exception as exc: raise CodingAgentError("CODEX_OUTPUT_INVALID") from exc
  return AgentCandidate(self.name,self.model or "configured-default",body["changes"],body["rationale"],float(body["confidence"]))
