# EXP-017: First G2 DevControl Shadow Run

Date: 2026-10-03

The first complete G2 shadow observation completed successfully with no target-project mutation authorization.

Observed DevControl source HEAD: `277448d3d04383c395ff733ed0bea4dbf836605a` (source version 3.1.17).

Manager state:
- qualification: PASS
- production verification: UNKNOWN
- source/production policy: ACCEPTABLE_DRIFT
- work items: 5
- dispatchable: 5
- execution authorized: false

Convergence debt:
- duplicate-state groups: 3
- divergent development lines: 17
- high-overlap pairs: 4
- dirty workspaces: 10
- role debt: 0
- verification debt: UNKNOWN

Production runtime remains internally consistent at version 3.1.14 / release `3a51151`; that release uniquely resolves to full source SHA `3a51151b8ae2dd56bfabcad680d7c23df19a5e0c` and is an ancestor of current origin/main.

## Important result

The source advanced from the previous observation while the durable work-item identities remained stable. Only observation timestamps changed in the queue. This is desired: work identity is not tied to a chat turn or source HEAD.

## Gap exposed by dogfood

Production verification, deployment identity, and artifact identity remain UNKNOWN. These are now evidence-contract work rather than reasons to guess deployment state.
