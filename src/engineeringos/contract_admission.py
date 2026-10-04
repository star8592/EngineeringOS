from __future__ import annotations
import pathlib
class ContractAdmissionError(ValueError):pass
SAFE_COMMAND_PREFIXES={("python3",),("python",),("pytest",),("cargo","test"),("npm","test"),("npm","run","test"),("npm","run","build")}
def admit(repo:str,work:dict,proposal:dict)->dict:
 if work.get("required_assurance","A1") not in ("A1","A2"):raise ContractAdmissionError("ASSURANCE_EXCEEDS_SAFE_PLANNING")
 paths=proposal.get("allowed_paths");argv=proposal.get("verification_argv")
 if not isinstance(paths,list) or not paths or not isinstance(argv,list) or not argv:raise ContractAdmissionError("CONTRACT_FIELDS_REQUIRED")
 root=pathlib.Path(repo).resolve();clean=[]
 for raw in paths:
  p=pathlib.Path(raw)
  if p.is_absolute() or ".." in p.parts:raise ContractAdmissionError("PATH_ESCAPE")
  target=(root/p).resolve()
  if root not in target.parents and target!=root:raise ContractAdmissionError("PATH_ESCAPE")
  clean.append(str(p))
 av=tuple(str(x) for x in argv)
 if not any(av[:len(prefix)]==prefix for prefix in SAFE_COMMAND_PREFIXES):raise ContractAdmissionError("VERIFICATION_COMMAND_NOT_ALLOWLISTED")
 return {"allowed_paths":clean,"verification_argv":list(av),"admission":"SAFE_A2_CONTRACT"}
