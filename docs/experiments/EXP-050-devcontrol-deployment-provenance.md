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

## Live result

Validated against production DevControl 3.1.21 / release `e3b88b47`:

- full source SHA: `e3b88b47ccce96409eb929fd56ff8ff6e4cc68de`;
- production server current: `releases/e3b88b47`;
- local Agent current: `releases/e3b88b47`;
- server deployed-tree SHA-256: `0f142877483c086108942ad67b377c033913c2540204967de051ae52d1acd665`;
- Agent deployed-tree SHA-256: `ad3438fd1bb4e865be2f5ee4cbf791fcdf02638a1dbf4a937c67f60b3400fa85`;
- deployment binding SHA-256: `0234f95ce39d2995500bc6433616af6fd57cdbb775f7f57f93bb12f9f8d9bc09`.

Both deployed trees resolved to the live release id and contained non-empty byte sets.

Result:

- `deployment_identity_state = RESOLVED`;
- `artifact_identity_state = PARTIAL`;
- Manager automatically removed `CLOSE_DEPLOYMENT_IDENTITY_GAP`;
- `CLOSE_ARTIFACT_IDENTITY_GAP` remained.

The experiment also exposed two EngineeringOS runtime defects during clean-worktree validation: artifact output directories were assumed to pre-exist, and the first SSH implementation mishandled multiline `python -c` quoting. Both were fixed with explicit output-directory bootstrap and a quoted/base64 remote observer command.

This narrows provenance debt without weakening proof semantics or modifying DevControl.
