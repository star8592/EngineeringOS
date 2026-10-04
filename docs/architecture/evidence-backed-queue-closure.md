# Evidence-Backed Queue Closure

EngineeringOS work items are not resolved merely because a finding disappears from the latest scan.

The durable queue uses a two-step closure model:

1. the manager stops emitting a condition, so the item becomes `PENDING_RESOLUTION`;
2. an evidence reconciler verifies that the underlying condition is actually satisfied and calls the queue `resolve()` contract with immutable evidence references.

This keeps discovery, disappearance, and closure as separate semantics.

## Supported authoritative closures

### Current-head qualification

Applies to:

- `RESOLVE_MAIN_QUALIFICATION`
- `RESTORE_MAIN_QUALIFICATION`

Closure requires a completed successful `DevControl 3 CI` run for the exact current `origin/main` SHA.

Evidence refs:

- `github-actions:<run-url>`
- `source-sha:<full-sha>`

Ancestor CI evidence is not accepted.

### Live production qualification

Applies to:

- `RESOLVE_LIVE_PRODUCTION_QUALIFICATION`

Closure requires `live_production_qualification=PASS` plus a durable release evidence file and resolved release/source identity.

Evidence refs include:

- `file:<release-evidence-path>#sha256:<digest>`
- `production-release:<release-id>`
- `source-sha:<full-sha>`

The file reference is content-addressed at reconciliation time.

### Deployment identity

Applies to:

- `CLOSE_DEPLOYMENT_IDENTITY_GAP`

Closure requires `deployment_identity=RESOLVED` and complete source/release/server/Agent binding evidence.

Evidence refs include:

- `production-release:<release-id>`
- `source-sha:<full-sha>`
- `deployment-binding-sha256:<digest>`
- `server-tree-sha256:<digest>`
- `agent-tree-sha256:<digest>`

## Explicit non-closure

`CLOSE_ARTIFACT_IDENTITY_GAP` is not closed by deployed-tree evidence.

Deployment identity proves which bytes are installed. Build artifact identity is a different claim about the staged/released artifact before deployment. It remains open until the producer persists an immutable build/staging manifest or equivalent artifact digest.

## Outcome-ledger compatibility

Existing `FALSE_POSITIVE` and `SEMANTIC_CORRECTION` outcomes remain valid closure sources.

Outcome-ledger closure and authoritative-evidence closure share the same queue `resolve()` function. No alternate resolved state exists.

## Safety

- only `PENDING_RESOLUTION` items may be auto-closed;
- empty or incomplete evidence produces no closure;
- evidence refs are deduplicated by the queue model;
- queue IDs remain stable across repeated observations;
- no target mutation is performed by reconciliation.
