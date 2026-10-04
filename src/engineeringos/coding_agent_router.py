from __future__ import annotations
from coding_agent_provider import CodingAgentError,TaskEnvelope,AgentCandidate,validate_candidate

class ProviderPool:
 def __init__(self,providers): self.providers=list(providers)
 def propose(self,*,task:TaskEnvelope,files:dict[str,str])->tuple[AgentCandidate,dict]:
  attempts=[]
  for provider in self.providers:
   name=getattr(provider,"name",type(provider).__name__)
   try:
    candidate=provider.propose(task=task,files=files);validate_candidate(task,candidate)
    attempts.append({"provider":name,"state":"SUCCEEDED"})
    return candidate,{"state":"SUCCEEDED","attempts":attempts,"needs_intent":False}
   except CodingAgentError as exc:
    attempts.append({"provider":name,"state":"FAILED","reason":str(exc)})
   except Exception as exc:
    attempts.append({"provider":name,"state":"FAILED","reason":"PROVIDER_EXCEPTION:"+type(exc).__name__})
  raise CodingAgentError("ALL_CODING_PROVIDERS_FAILED:"+str(attempts))

def classify_provider_failure(exc:Exception)->dict:
 return {"work_state":"REOPENED","reason":"WAITING_PROVIDER","needs_intent":False,"user_interruption":False,"detail":str(exc)}
