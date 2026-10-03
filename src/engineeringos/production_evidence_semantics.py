from __future__ import annotations

def interpret(*, source_ci, source_head_smoke, release_evidence):
    live_qualified=(release_evidence or {}).get('qualification_state')=='RESOLVED'
    source_resolved=(release_evidence or {}).get('source_identity_state')=='RESOLVED'
    return {
      'qualification':'FAIL' if source_ci=='FAILURE' else ('PASS' if source_ci=='SUCCESS' else 'UNKNOWN'),
      'source_head_production_verification':'PASS' if source_head_smoke=='SUCCESS' else 'UNKNOWN',
      'live_production_qualification':'PASS' if live_qualified and source_resolved else 'UNKNOWN',
      'deployment_identity':(release_evidence or {}).get('deployment_identity_state','UNKNOWN'),
      'artifact_identity':(release_evidence or {}).get('artifact_identity_state','UNKNOWN'),
    }
