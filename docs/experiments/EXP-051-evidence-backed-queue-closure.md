# EXP-051: Evidence-backed closure for recovered DevControl debt

Date: 2026-10-04

## Problem

EngineeringOS intentionally moves a work item to `PENDING_RESOLUTION` when the finding disappears. This avoids false auto-closure, but the authoritative evidence reconciler only knew how to close one class: `RESOLVE_MAIN_QUALIFICATION` with a successful DevControl CI run.

After EXP-050, live production qualification and deployment identity became provably resolved, yet their historical queue items remained pending forever.

## Decision

Queue closure is now typed by debt class.

### Main qualification

`RESOLVE_MAIN_QUALIFICATION` and `RESTORE_MAIN_QUALIFICATION` may close only with:

- a completed successful **DevControl 3 CI** run;
- exact current `origin/main` head SHA;
- the GitHub Actions run URL.

### Live production qualification

`RESOLVE_LIVE_PRODUCTION_QUALIFICATION` may close only when the evidence plane says live production qualification is PASS and release evidence contains:

- resolved release qualification;
- resolved source identity;
- durable release-evidence file;
- production release id;
- full source SHA.

If available, the deployment binding is included as additional closure evidence.

### Deployment identity

`CLOSE_DEPLOYMENT_IDENTITY_GAP` may close only when deployment identity is RESOLVED and evidence contains:

- production release id;
- full source SHA;
- deployment binding SHA-256;
- production server tree SHA-256;
- local Agent tree SHA-256;
- server and Agent observations both RESOLVED.

## Non-substitution rule

Evidence is not interchangeable across debt classes. CI success cannot close deployment identity. Deployment digests cannot close source CI. Live release qualification cannot close artifact identity.

`CLOSE_ARTIFACT_IDENTITY_GAP` remains open while build/staging artifact identity is PARTIAL.

## Expected runtime effect

With the current DevControl 3.1.21 evidence set, the reconciler should resolve the historical pending items for:

- main CI recovery;
- live production qualification;
- deployment identity.

It must leave artifact identity and convergence-debt review items untouched.
