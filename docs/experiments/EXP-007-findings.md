# EXP-007 Initial Findings: Memory Convergence

Date: 2026-10-03

A first conservative checker compared a small set of machine-readable DevControl facts with claims in durable architecture memory.

## Canonical machine facts observed

- repository `VERSION`: `3.1.13`
- `origin/main`: `790772c8fc0203794ff1c32ad1414dc72be0c897`
- canonical modern MCP protocol in the current architecture: `2026-07-28`

## First drift candidate

`docs/architecture/APPROVAL_SEMANTICS_AND_TOOL_SURFACE_PLAN.md` states that production health reports `version=3.1.14`, while the repository's canonical `VERSION` currently reports `3.1.13`.

This is intentionally classified as `VERSION_CLAIM_DRIFT`, not automatically as a documentation bug. There are at least three possible realities: the document is stale, the repository version is stale, or production is intentionally ahead/behind source. Resolving the conflict requires live production identity evidence.

## Key design lesson

Memory convergence must detect contradictions, not "fix documentation" by guessing which side is right. A contradiction becomes an evidence-resolution task. Historical and incident documents are also allowed to preserve old facts; only claims presented as current/canonical should participate in automatic drift checks.

## Next step

EXP-008 will introduce a Fact Registry with provenance, scope, temporal validity, authority, and confidence. Memory checks will compare compatible facts rather than regexing arbitrary prose as if every sentence had the same semantics.
