# EXP-034: Source-head verification vs live-production qualification

Date: 2026-10-03

G2 dogfood exposed a false-positive in the original manager semantics: absence of a Production Smoke run for the current `origin/main` SHA was reported as unresolved production verification.

That conflated two different questions:

1. Is current source HEAD deployed/production-smoke verified?
2. Is the currently live production release qualified and source-resolved?

The evidence model now separates:
- `qualification`
- `source_head_production_verification`
- `live_production_qualification`
- `deployment_identity`
- `artifact_identity`

At the observed state, current source qualification is PASS, current source-head production verification is UNKNOWN, live production qualification is PASS, deployment identity is PARTIAL, and artifact identity is UNKNOWN.

The manager no longer creates `RESOLVE_PRODUCTION_VERIFICATION` merely because current source HEAD is not deployed. It creates explicit identity-gap work instead.

This is a concrete G2 outcome label: the prior P1 finding was a semantic false-positive, corrected by splitting evidence predicates rather than weakening policy.
