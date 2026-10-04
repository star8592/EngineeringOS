from __future__ import annotations
import pathlib,subprocess,hashlib
from isolated_mutation_lane import validate_paths,MutationLaneError

class ConvergenceError(ValueError): pass
def _git(repo,*a): return subprocess.check_output(["git","-C",repo,*a],text=True).strip()

def assess(repo:str, proposal:dict, result:dict)->dict:
 if result.get("state")!="READY_FOR_CONVERGENCE": return {"decision":"DENY","reason":"PROPOSAL_NOT_VERIFIED"}
 if result.get("main_mutated") is not False: return {"decision":"DENY","reason":"MUTATION_BOUNDARY_VIOLATED"}
 if _git(repo,"status","--porcelain"): return {"decision":"DENY","reason":"MAIN_DIRTY"}
 if _git(repo,"rev-parse","HEAD")!=proposal["source_sha"]: return {"decision":"DENY","reason":"SOURCE_SHA_DRIFT"}
 if sorted(result.get("changed_paths",[]))!=sorted(proposal["allowed_paths"]): return {"decision":"DENY","reason":"CHANGE_SURFACE_DRIFT"}
 return {"decision":"ALLOW","reason":"VERIFIED_ISOLATED_PATCH"}

def converge(repo:str,proposal:dict,result:dict)->dict:
 gate=assess(repo,proposal,result)
 if gate["decision"]!="ALLOW": return {"gate":gate,"applied":False}
 ws=result["workspace_path"];patch=subprocess.check_output(["git","-C",ws,"diff","--binary","--",*proposal["allowed_paths"]])
 if hashlib.sha256(patch).hexdigest()!=result["diff_sha256"]: raise ConvergenceError("DIFF_EVIDENCE_DRIFT")
 proc=subprocess.run(["git","-C",repo,"apply","--index","--whitespace=error-all","-"],input=patch,capture_output=True)
 if proc.returncode: raise ConvergenceError("PATCH_APPLY_FAILED:"+proc.stderr.decode(errors="replace")[-1000:])
 verify=subprocess.run(proposal["verification_argv"],cwd=repo,text=True,capture_output=True,env={**__import__("os").environ,"CI":"1"})
 if verify.returncode:
  subprocess.run(["git","-C",repo,"reset","--hard",proposal["source_sha"]],check=True,capture_output=True)
  return {"gate":gate,"applied":False,"reason":"POST_CONVERGENCE_VERIFICATION_FAILED","exit_code":verify.returncode}
 return {"gate":gate,"applied":True,"state":"CONVERGED_UNCOMMITTED","changed_paths":result["changed_paths"],"post_verification_exit_code":0}
