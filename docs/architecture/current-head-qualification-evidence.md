# Current-Head Qualification Evidence Semantics

EngineeringOS must distinguish the state of an authoritative CI workflow from the transport used to retrieve that state.

For the current source head, a workflow evidence classifier emits exactly one qualification state:

- `NO_RUN` — the authoritative workflow query succeeded and no matching workflow run exists for the current source SHA;
- `RUNNING` — a matching current-head run exists but has not completed;
- `PASS` — the latest matching current-head run completed successfully;
- `FAIL` — the latest matching current-head run completed without success.

A GitHub/API query failure is **not** reclassified as `NO_RUN`. Query transport is recorded separately as `workflow_query.state=ERROR`, and the qualification interpretation becomes `QUERY_ERROR`.

## Why this matters

The old `UNKNOWN` state collapsed materially different situations:

- CI never ran;
- CI is currently running;
- CI retrieval failed;
- an unsupported/legacy status was observed.

Those states require different operator actions and retry behavior.

## Compatibility

The evidence plane retains the old string fields such as `current_head_evidence.ci` during migration. New consumers must use `current_head_evidence.ci_evidence.state` and `interpretation.qualification_evidence_state`.

The stable queue kind remains `RESOLVE_MAIN_QUALIFICATION` for non-terminal qualification gaps. Root cause is carried by:

- `evidence_state`;
- `reason_code`;
- explicit action-detail evidence.

A completed non-success run continues to use `RESTORE_MAIN_QUALIFICATION` and blocks qualification-dependent work.

## Safety

`NO_RUN` is evidence absence, not CI failure and not permission to proceed.

`RUNNING` must not cause EngineeringOS to launch a duplicate qualification run.

`QUERY_ERROR` must not be interpreted as evidence that no run exists.

Ancestor CI evidence is not substituted for current-head CI evidence.
