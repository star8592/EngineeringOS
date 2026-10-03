# EXP-004 Initial Findings

Date: 2026-10-03

The first Evidence Plane joins Git identity with GitHub Actions evidence without inferring deployment state that is not explicitly proven.

## Current authoritative remote head

- `origin/main`: `13e3b5c567bdafda50a7d443d19974ac38efb7f4`
- version at that SHA: `3.1.16`
- DevControl 3 CI for that exact SHA: `FAILURE`
- Production Smoke for that exact SHA: `UNKNOWN` (no matching run found in the sampled evidence)
- External Spec Drift for that exact SHA: `UNKNOWN`
- artifact identity: `UNKNOWN`
- deployment identity: `UNKNOWN`

A successful Production Smoke exists for older SHA `f6550f90...`, and that SHA is an ancestor of current `origin/main`. This proves historical smoke evidence exists; it does **not** prove current main is deployed or production-verified.

## Important consequence

A repository can be ahead of its last proven production state. EngineeringOS must model at least four distinct identities instead of one vague "current version": source head, qualified head, released artifact identity, and deployed/production-verified identity.

The GitHub Release API currently provides no release records for this repository, so release identity cannot be reconstructed from GitHub Releases alone.

## Next step

EXP-005 will model identity/provenance explicitly and investigate DevControl's release/deploy scripts and production endpoints to find durable artifact/deployment identifiers. The goal is evidence linkage, not triggering a deployment.
