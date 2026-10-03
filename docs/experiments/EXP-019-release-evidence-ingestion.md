# EXP-019: DevControl Release Evidence Ingestion

Date: 2026-10-03

EngineeringOS now ingests the existing DevControl release-evidence store instead of treating production verification as a single undifferentiated UNKNOWN.

For live production release `3a51151`:
- runtime release identity is observed from `/readyz`;
- release evidence file `~/.local/state/devcontrol3/release-evidence/3a51151.json` exists;
- qualification includes `release_gate_all` and `post_deploy` plus OAuth/browser/Agent/hygiene gates;
- release ID uniquely maps to full source SHA `3a51151b8ae2dd56bfabcad680d7c23df19a5e0c`.

Therefore source provenance and release qualification are resolved for this release.

Artifact identity remains UNKNOWN because the durable qualification record does not bind immutable server/Agent artifact digests. Deployment identity is PARTIAL: runtime exposes release ID and version, but not full source SHA or artifact digest.

## Required producer-side evidence contract

DevControl should eventually emit a release manifest containing at least full source SHA, product version, release ID, server artifact digest, Agent artifact digest, qualification evidence identity, and deployment/runtime binding. EngineeringOS should consume this contract rather than infer missing edges.
