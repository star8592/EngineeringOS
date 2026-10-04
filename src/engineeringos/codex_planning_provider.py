from __future__ import annotations
import json,pathlib,tempfile,subprocess,os,signal
from contract_planner import ContractCandidate,PlanningProviderError
class CodexPlanningProvider:
 name="codex-cli-planner-readonly"
 def __init__(self,*,binary="codex",model=None,timeout=60):self.binary=binary;self.model=model;self.timeout=timeout
 def plan(self,*,work,project_context):
  schema={"type":"object","properties":{"allowed_paths":{"type":"array","items":{"type":"string"},"minItems":1},"verification_argv":{"type":"array","items":{"type":"string"},"minItems":1},"reasoning":{"type":"string"}},"required":["allowed_paths","verification_argv","reasoning"],"additionalProperties":False}
  prompt=("You are a read-only software planning worker, not an execution authority. Propose the smallest mutation contract for this work. "
          "Do not modify files or run commands. Paths must be repository-relative. Verification must be a direct argv using ordinary project test/build entrypoints; never shell wrappers.\nWork:\n"+
          json.dumps(work,ensure_ascii=False)+"\nProject context:\n"+json.dumps(project_context,ensure_ascii=False))
  with tempfile.TemporaryDirectory(prefix="engineeringos-codex-planner-") as td:
   sp=pathlib.Path(td)/"schema.json";op=pathlib.Path(td)/"out.json";sp.write_text(json.dumps(schema))
   argv=[self.binary,"exec","--ephemeral","--sandbox","read-only","--output-schema",str(sp),"-o",str(op)]
   if self.model:argv+=["--model",self.model]
   argv+=["-"];proc=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
   try:stdout,stderr=proc.communicate(prompt,timeout=self.timeout)
   except subprocess.TimeoutExpired as exc:
    try:os.killpg(proc.pid,signal.SIGKILL)
    except ProcessLookupError:pass
    try:proc.wait(timeout=5)
    except subprocess.TimeoutExpired:proc.kill()
    raise PlanningProviderError("CODEX_PLANNER_TIMEOUT") from exc
   if proc.returncode:raise PlanningProviderError("CODEX_PLANNER_FAILED:"+stderr[-1000:])
   try:body=json.loads(op.read_text())
   except Exception as exc:raise PlanningProviderError("CODEX_PLANNER_OUTPUT_INVALID") from exc
  return ContractCandidate(self.name,self.model or "configured-default",tuple(body["allowed_paths"]),tuple(body["verification_argv"]),body["reasoning"])
