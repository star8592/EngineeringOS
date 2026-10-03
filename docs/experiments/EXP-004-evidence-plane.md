# EXP-004: Evidence Plane

## Goal

Join deterministic qualification and runtime evidence to the Engineering World Model.

## Sources

- GitHub Actions/check conclusions and required checks
- release/version/tag lineage
- build artifacts and release manifests where available
- deployment/production references
- production smoke results
- contract, MCP conformance, and spec-drift checks

## Invariant

`UNKNOWN` is a first-class state. Missing evidence must never be silently interpreted as PASS.

## Desired questions

For any integrated or released change: what checks proved it, what artifact contains it, where was it deployed, what production evidence verified it, and is that evidence still current?
