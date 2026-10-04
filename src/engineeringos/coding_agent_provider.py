from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol

class CodingAgentError(RuntimeError): pass

@dataclass(frozen=True)
class TaskEnvelope:
 project:str
 item_id:str
 source_sha:str
 goal:str
 allowed_paths:tuple[str,...]
 verification_argv:tuple[str,...]
 context:dict

@dataclass(frozen=True)
class AgentCandidate:
 provider:str
 model:str
 changes:dict[str,str]
 rationale:str=""
 confidence:float|None=None

class CodingAgentProvider(Protocol):
 name:str
 def propose(self, *, task:TaskEnvelope, files:dict[str,str])->AgentCandidate: ...

def validate_candidate(task:TaskEnvelope,candidate:AgentCandidate)->None:
 if not candidate.provider or not candidate.model: raise CodingAgentError("AGENT_IDENTITY_REQUIRED")
 if not candidate.changes: raise CodingAgentError("EMPTY_AGENT_CANDIDATE")
 if set(candidate.changes)!=set(task.allowed_paths): raise CodingAgentError("AGENT_MUTATION_SURFACE_DRIFT")
 if not all(isinstance(v,str) for v in candidate.changes.values()): raise CodingAgentError("AGENT_CONTENT_MUST_BE_TEXT")
 if candidate.confidence is not None and not 0<=candidate.confidence<=1: raise CodingAgentError("AGENT_CONFIDENCE_INVALID")

def to_mutation_proposal(task:TaskEnvelope,candidate:AgentCandidate)->dict:
 validate_candidate(task,candidate)
 return {"schema_version":1,"project":task.project,"item_id":task.item_id,"source_sha":task.source_sha,
         "allowed_paths":list(task.allowed_paths),"changes":candidate.changes,"verification_argv":list(task.verification_argv),
         "agent_evidence":{"provider":candidate.provider,"model":candidate.model,"rationale":candidate.rationale,"confidence":candidate.confidence}}
