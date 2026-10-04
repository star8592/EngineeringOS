# EXP-050: Resolve DevControl deployment identity from installed bytes

Date: 2026-10-04

## Problem

The live DevControl release could be mapped from runtime `release_id` to a unique source commit, and release qualification evidence was present, but EngineeringOS still reported:

- deployment identity = PARTIAL;
- artifact identity = UNKNOWN.

The previous implementation assumed that full source SHA and artifact digests had to be exposed directly by the runtime HTTP endpoint.

## Observation

DevControl's existing release pipeline already has stronger facts available outside the HTTP endpoint:

- production server `current` symlink identifies the installed server release;
- local Agent `current` symlink identifies the installed Agent release;
- both release directories contain the exact currently deployed bytes;
- staged packages already use SHA-256 manifests during release qualification.

However the original build/staging manifest is not durably stored in the release evidence record after a successful deploy.

## Experiment

EngineeringOS adds a read-only DevControl deployment observer that computes canonical deployed-tree digests for server and Agent and binds them to:

- live release id;
- unique full source SHA.

Deployment identity is resolved only if both current-release pointers and both deployed-tree digests agree.

Build artifact identity remains PARTIAL because deployed-tree identity is not the same claim as the original staged artifact identity.

## Expected effect

For a healthy live release with matching server/Agent current pointers:

- `deployment_identity_state` may become `RESOLVED`;
- `artifact_identity_state` becomes `PARTIAL` when deployed byte digests are known;
- the manager should retire `CLOSE_DEPLOYMENT_IDENTITY_GAP`;
- `CLOSE_ARTIFACT_IDENTITY_GAP` remains until the DevControl producer persists an immutable build manifest/tarball digest.

This narrows provenance debt without weakening proof semantics or modifying DevControl.
