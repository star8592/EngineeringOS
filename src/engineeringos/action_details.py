from __future__ import annotations
import json,pathlib
from state_paths import runtime


def build_action_details(brief: dict, debt: dict, release: dict, evidence_plane: dict | None = None) -> dict:
    dims=debt.get('dimensions',{})
    details=[]
    for action in brief.get('actions',[]):
        kind=action.get('kind')
        evidence=[]; resolution=[]
        if kind in ('RESOLVE_MAIN_QUALIFICATION','RESTORE_MAIN_QUALIFICATION'):
            plane=evidence_plane or {}
            head=plane.get('current_head_evidence') or {}
            ci=head.get('ci_evidence') or {}
            evidence=[{
                'origin_main':plane.get('origin_main'),
                'qualification':(plane.get('interpretation') or {}).get('qualification'),
                'qualification_evidence_state':(plane.get('interpretation') or {}).get('qualification_evidence_state'),
                'qualification_reason':(plane.get('interpretation') or {}).get('qualification_reason'),
                'workflow_query':plane.get('workflow_query'),
                'ci_evidence':ci,
            }]
            state=(plane.get('interpretation') or {}).get('qualification_evidence_state')
            if state=='NO_RUN':
                resolution=['run the canonical DevControl 3 CI for the current origin/main head','do not substitute CI evidence from an ancestor commit']
            elif state=='RUNNING':
                resolution=['await the existing current-head CI run','do not start a duplicate qualification run']
            elif state=='QUERY_ERROR':
                resolution=['restore authoritative GitHub workflow evidence retrieval','do not infer CI absence from a failed query']
            elif state=='FAIL':
                resolution=['inspect the exact current-head CI run conclusion and evidence','restore current-head qualification before release/convergence actions']
            else:
                resolution=['reconcile current-head CI evidence through the canonical workflow source']
        elif kind=='TRIAGE_DIRTY_WORKSPACES':
            evidence=dims.get('dirty_workspace',{}).get('evidence',[])
            resolution=['identify the active owner/agent for each dirty workspace','preserve uncommitted work before any convergence decision','classify each workspace as active, stale, or ready for review']
        elif kind=='REVIEW_OVERLAPPING_LINES':
            evidence=dims.get('overlap',{}).get('evidence',[])
            resolution=['identify semantic ownership of shared files','avoid parallel edits to the same contract surface','select a convergence order before merge/rebase work']
        elif kind=='RECONCILE_DUPLICATE_STATE':
            evidence=dims.get('duplicate_state',{}).get('evidence',[])
            resolution=['determine which branch name is canonical for each identical head','mark aliases as superseded only after ownership/evidence review']
        elif kind=='REVIEW_DIVERGENT_DEVELOPMENT':
            evidence=dims.get('divergence',{}).get('evidence',[])
            resolution=['check whether each line is still active','compare unique commits with current main before deciding rebase/supersede']
        elif kind=='CLOSE_ARTIFACT_IDENTITY_GAP':
            dep=release.get('deployment_observation') or {}
            evidence=[{'artifact_identity_state':release.get('artifact_identity_state'),'release_evidence_file':release.get('release_evidence_file'),'production':release.get('production'),'deployment_binding_sha256':release.get('deployment_binding_sha256'),'server_tree_sha256':(dep.get('server') or {}).get('tree_sha256'),'agent_tree_sha256':(dep.get('agent') or {}).get('tree_sha256'),'reasoning':release.get('reasoning',{}).get('artifact_identity')}]
            resolution=['persist immutable build/staging artifact manifests in release evidence','bind future build artifact digests to the already observed deployed-tree identities']
        elif kind=='CLOSE_DEPLOYMENT_IDENTITY_GAP':
            dep=release.get('deployment_observation') or {}
            evidence=[{'deployment_identity_state':release.get('deployment_identity_state'),'full_source_sha':release.get('full_source_sha'),'production':release.get('production'),'deployment_binding_sha256':release.get('deployment_binding_sha256'),'server':dep.get('server'),'agent':dep.get('agent'),'binding_reasons':dep.get('reasons'),'reasoning':release.get('reasoning',{}).get('deployment_identity')}]
            resolution=['bind runtime release_id to full source SHA and both deployed-tree digests','resolve any server/agent current-release or tree-digest mismatch before closure']
        details.append({
            'item_id':action['item_id'],'kind':kind,'priority':action.get('priority'),
            'evidence_count':len(evidence),'evidence':evidence,'suggested_resolution':resolution,
            'target_mutation_authorized':False,
        })
    return {'schema_version':1,'mode':'G2_SHADOW','project':brief.get('project'),'snapshot_content_sha256':brief.get('snapshot_content_sha256'),'items':details,'target_mutation_authorized':False}


def main():
    brief=json.load(open(runtime('action-brief.json')))
    debt=json.load(open('artifacts/convergence-debt.json'))
    release=json.load(open('artifacts/devcontrol-release-evidence.json'))
    evidence_plane=json.load(open('artifacts/evidence-plane.json')) if pathlib.Path('artifacts/evidence-plane.json').exists() else {}
    out=build_action_details(brief,debt,release,evidence_plane)
    p=runtime('action-details.json');p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'items':len(out['items']),'evidence':sum(x['evidence_count'] for x in out['items'])},indent=2))
if __name__=='__main__':main()
