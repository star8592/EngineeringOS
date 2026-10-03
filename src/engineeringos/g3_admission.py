from __future__ import annotations
import json

class AdmissionError(ValueError): pass

def load_policy(path):
    d=json.load(open(path))
    if d.get('schema_version')!=1: raise AdmissionError('UNSUPPORTED_POLICY_SCHEMA')
    return d

def assess(policy, *, action, backend, declared_annotations=None, runtime_contracts=()):
    """Machine gate for G3. Annotations classify; policy/contracts authorize."""
    if backend != policy.get('execution_backend'):
        return {'decision':'DENY','reason':'EXECUTION_BACKEND_DRIFT'}
    if policy.get('approval_authority') != 'HOST_PROTOCOL':
        return {'decision':'DENY','reason':'APPROVAL_AUTHORITY_DRIFT'}
    spec=(policy.get('actions') or {}).get(action)
    if spec is None:
        return {'decision':'DENY','reason':'UNKNOWN_ACTION'}
    if not spec.get('g3_allowed',False):
        return {'decision':'DENY','reason':'OUTSIDE_G3_BOUNDARY','approval_mode':spec.get('approval_mode')}
    # MCP/tool annotations are never authorization. If present, they must not contradict the project contract.
    ann=declared_annotations or {}
    if ann.get('destructive_hint') is False and spec.get('destructive') is True:
        return {'decision':'DENY','reason':'TOOL_METADATA_CONTRADICTION'}
    if ann.get('read_only_hint') is True and spec.get('side_effecting') is True:
        return {'decision':'DENY','reason':'TOOL_METADATA_CONTRADICTION'}
    required=set(spec.get('requires') or [])
    missing=sorted(required-set(runtime_contracts))
    if missing:
        return {'decision':'DENY','reason':'MISSING_RUNTIME_CONTRACTS','missing':missing}
    mode=spec.get('approval_mode','REQUIRE_HOST_APPROVAL')
    if mode == 'AUTO':
        # Automatic G3 actions must remain non-destructive; side effects require the durable command safety contract.
        if spec.get('destructive'):
            return {'decision':'DENY','reason':'DESTRUCTIVE_AUTO_NOT_ALLOWED'}
        return {'decision':'ALLOW','approval':'NOT_REQUIRED_BY_PROJECT_POLICY'}
    if mode == 'REQUIRE_HOST_APPROVAL':
        return {'decision':'REQUIRE_HOST_APPROVAL','approval':'HOST_PROTOCOL'}
    return {'decision':'DENY','reason':'UNKNOWN_APPROVAL_MODE'}
