from __future__ import annotations
from dataclasses import dataclass
from contract_admission import admit
@dataclass(frozen=True)
class ContractCandidate:
 provider:str;model:str;allowed_paths:tuple[str,...];verification_argv:tuple[str,...];reasoning:str=""
class PlanningProviderError(RuntimeError):pass
class PlanningPool:
 def __init__(self,providers):self.providers=list(providers)
 def plan(self,*,repo,work,project_context):
  attempts=[]
  for p in self.providers:
   name=getattr(p,"name",type(p).__name__)
   try:
    c=p.plan(work=work,project_context=project_context);contract=admit(repo,work,{"allowed_paths":list(c.allowed_paths),"verification_argv":list(c.verification_argv)})
    attempts.append({"provider":name,"state":"SUCCEEDED"});return contract,{"attempts":attempts}
   except Exception as e:attempts.append({"provider":name,"state":"FAILED","reason":type(e).__name__+":"+str(e)})
  raise PlanningProviderError("ALL_PLANNERS_FAILED:"+str(attempts))
