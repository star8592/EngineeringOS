# EXP-008: Fact Registry

## Goal

Represent engineering facts with enough semantics to reconcile code, documents, CI, release, deployment, production, and conversations safely.

## Proposed fact shape

- `subject`
- `predicate`
- `value`
- `scope` (repository, release, environment, host, tool surface, protocol, etc.)
- `valid_from` / `valid_until`
- `observed_at`
- `source_type`
- `source_identity`
- `authority`
- `confidence`
- `evidence_ref`

## Rule

A contradiction is only meaningful when facts refer to compatible subject/predicate/scope/time. EngineeringOS must not overwrite one source from another merely because strings differ.
